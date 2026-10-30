"""数据加工（ETL）：补齐缺失身价点、合成阵型表现、校验完整性。

由 scripts/process_data.py 离线执行；Web 服务只读产出物。
"""

import datetime
import json
import os
import random

from .formations import FORMATIONS
from .periods import period_end, period_start

# StatsBomb 真实阵型聚合产物（由 scripts/fetch_statsbomb.py 生成）。
# 文件缺失时整条管线回退到纯估算，不影响开发与构建。
REAL_PERF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "processed", "formation_real.json")


# ----------------------------------------------------------------------
# Data reconciliation（离线 ETL，由 scripts/process_data.py 执行）
# 1) Backfill market_value_history: every career_history club gets at least
#    one value point. Synthesized points are flagged "estimated": True and
#    rendered as "估值" in frontend tooltips. career_history itself is NEVER
#    modified — estimates must not be presented as career facts.
# 2) Synthesize formation_performance for players that lack it. These players
#    (Transfermarkt CSV import) have no career totals to split, so totals are
#    derived from career span × position benchmarks instead.
# 3) Validate dataset integrity (fail in the offline step, not at request time).
# ----------------------------------------------------------------------

def _reconcile_market_value_gaps(players):
    """Insert estimated value points for career clubs missing from MV history.

    Insert date = June 30 of the stint's end year (transfer-window boundary);
    value = linear interpolation between neighbouring points, or 55% of the
    next point when the gap is at the start of the recorded history.
    Points are re-sorted after each insertion so earlier inserts anchor
    later gaps (e.g. Salah: Basel + Chelsea both missing).
    """
    for p in players:
        hist = p.get("market_value_history") or []
        career = p.get("career_history") or []
        if not hist or not career:
            continue
        hist.sort(key=lambda m: m["date"])
        for c in career:
            if c["club"] in {m["club"] for m in hist}:
                continue
            end = period_end(c["period"])
            if end is None:  # single-year ("2019") or open ("2024-") period
                end = period_start(c["period"])
            cand = datetime.date(end, 6, 30)
            existing = {m["date"] for m in hist}
            while cand.isoformat() in existing:
                cand -= datetime.timedelta(days=1)
            iso = cand.isoformat()
            prev = next((m for m in reversed(hist) if m["date"] < iso), None)
            nxt = next((m for m in hist if m["date"] > iso), None)
            if prev and nxt:
                d0 = datetime.date.fromisoformat(prev["date"])
                d1 = datetime.date.fromisoformat(nxt["date"])
                frac = (cand - d0).total_seconds() / max((d1 - d0).total_seconds(), 1)
                frac = min(max(frac, 0.0), 1.0)
                value = prev["value_m_eur"] + frac * (nxt["value_m_eur"] - prev["value_m_eur"])
            elif nxt:
                value = nxt["value_m_eur"] * 0.55
            elif prev:
                value = prev["value_m_eur"]
            else:
                continue
            value = max(0.5, value)
            value = round(value) if value >= 10 else int(value * 2 + 0.5) / 2
            hist.append({"date": iso, "value_m_eur": value,
                         "club": c["club"], "estimated": True})
            hist.sort(key=lambda m: m["date"])


# Split weights per position group, in FORMATIONS order (4-3-3, 4-4-2, 3-5-2, 4-2-3-1)
_FORMATION_WEIGHTS = {
    "GK": [0.34, 0.20, 0.16, 0.30],
    "DF": [0.30, 0.24, 0.24, 0.22],
    "MF": [0.34, 0.20, 0.16, 0.30],
    "FW": [0.40, 0.18, 0.16, 0.26],
}
# (goals/app, assists/app) benchmarks per position group
_FORMATION_RATES = {
    "GK": (0.0, 0.0),
    "DF": (0.035, 0.07),
    "MF": (0.11, 0.20),
    "FW": (0.42, 0.20),
}

# 位置专属指标（每场）：(saves, conceded, clearances, interceptions)
# 门将用扑救/丢球衡量，后卫用解围/拦截衡量 —— 进球助攻对这两类位置没有解释力。
_POSITION_METRICS = {
    "GK": (2.55, 1.10, 0.0, 0.0),
    "DF": (0.0, 0.0, 4.30, 1.55),
    "MF": (0.0, 0.0, 1.35, 1.10),
    "FW": (0.0, 0.0, 0.45, 0.45),
}

# 位置专属指标字段：career_history 与 formation_performance 共用
METRIC_KEYS = ("saves", "conceded", "clearances", "interceptions")


def _split_total(total, weights):
    """Largest-remainder split of an integer total across weights (sums stay exact)."""
    raw = [total * w for w in weights]
    out = [int(x) for x in raw]
    rem = total - sum(out)
    order = sorted(range(len(weights)), key=lambda i: -(raw[i] - out[i]))
    for i in order[:rem]:
        out[i] += 1
    return out


def _fit_total(values, total):
    """把整数序列按比例缩到 total；未超出时原样返回（真实数据优先保持原值）。"""
    current = sum(values)
    if current <= total:
        return list(values)
    return _split_total(total, [v / current for v in values])


def _distribute(total, weights):
    """按权重把整数 total 分到各桶；权重全为 0 时返回全 0（不硬塞给某一个桶）。"""
    if total <= 0 or not weights:
        return [0] * len(weights)
    wsum = sum(weights)
    if wsum <= 0:
        return [0] * len(weights)
    return _split_total(total, [w / wsum for w in weights])


def _stint_years(period):
    start = period_start(period)
    end = period_end(period)
    if end is None:
        end = 2026 if period.endswith("-") else start
    return max(1, end - start + 1)


def _estimate_career_totals(group, value, career, rng):
    """无公开来源时按「生涯年数 × 位置基准」估算生涯合计。"""
    seasons = sum(_stint_years(c["period"]) for c in career)
    base = (44 if value >= 100 else 40 if value >= 60 else
            36 if value >= 30 else 30 if value >= 10 else 26)
    apps = max(1, round(seasons * base * rng.uniform(0.85, 1.15)))
    g_rate, a_rate = _FORMATION_RATES.get(group, _FORMATION_RATES["MF"])
    quality = 0.7 + min(1.0, value / 150) + rng.uniform(0, 0.2)
    return {
        "apps": apps,
        "goals": round(apps * g_rate * quality),
        "assists": round(apps * a_rate * quality),
    }


def _reconcile_career_metrics(players):
    """补齐 career_history 缺少的出场/进球/助攻。

    转会数据源的口径差异让一部分球员（尤以后卫、门将为主）缺少生涯合计，
    没有合计就无从拆分阵型数据，整块页面会是空的。补齐规则：
      1. 已有生涯合计 —— 保持原值，不做任何改写；
      2. 球员自带手工核定的阵型数据 —— 以阵型合计反推生涯合计
         （反推方向保证两边合计一致，不会把核定值改小或改大）；
      3. 两边都没有 —— 按「生涯年数 × 位置基准」估算。
    """
    for p in players:
        career = p.get("career_history") or []
        if not career or any(c.get("apps") is not None for c in career):
            continue
        group = p.get("position_group", "MF")
        fp = p.get("formation_performance")
        if fp:
            totals = {
                key: sum((fp.get(f) or {}).get(key, 0) for f in FORMATIONS)
                for key in ("apps", "goals", "assists")
            }
        else:
            hist = p.get("market_value_history") or []
            value = (hist[-1].get("value_m_eur") if hist else 5) or 5
            totals = _estimate_career_totals(
                group, value, career, random.Random(f"career:{p['id']}"))
        weights = [_stint_years(c["period"]) for c in career]
        chunks = {k: _distribute(totals[k], weights) for k in ("apps", "goals", "assists")}
        for i, c in enumerate(career):
            c["apps"] = chunks["apps"][i]
            c["goals"] = chunks["goals"][i]
            c["assists"] = chunks["assists"][i]


def _apply_position_metrics(players):
    """给生涯与阵型数据补上位置专属指标：门将→扑救/丢球，后卫→解围/拦截。

    这两类位置用进球助攻衡量没有解释力，因此单独统计。生涯合计按各段出场数
    分配、阵型合计按各阵型出场数分配，两者总和恒等于生涯总量。
    """
    for p in players:
        group = p.get("position_group", "MF")
        rates = _POSITION_METRICS.get(group, _POSITION_METRICS["MF"])
        career = p.get("career_history") or []
        fp = p.get("formation_performance") or {}
        apps_total = sum((c.get("apps") or 0) for c in career)
        if not apps_total:
            continue
        quality = random.Random(f"metrics:{p['id']}").uniform(0.92, 1.08)
        totals = {key: (int(round(apps_total * rate * quality)) if rate else 0)
                  for key, rate in zip(METRIC_KEYS, rates)}

        chunks = {k: _distribute(totals[k], [c.get("apps") or 0 for c in career])
                  for k in METRIC_KEYS}
        for i, c in enumerate(career):
            for k in METRIC_KEYS:
                c[k] = chunks[k][i]

        if fp:
            fweights = [(fp.get(f) or {}).get("apps") or 0 for f in FORMATIONS]
            fchunks = {k: _distribute(totals[k], fweights) for k in METRIC_KEYS}
            for i, f in enumerate(FORMATIONS):
                cell = fp.get(f)
                if not cell:
                    continue
                for k in METRIC_KEYS:
                    cell[k] = fchunks[k][i]


def _rating_base(value):
    return 6.85 + min(0.85, (value or 5) / 160)


def load_real_performance():
    """读取 StatsBomb 真实阵型聚合结果；缺失或损坏时返回空字典。"""
    try:
        with open(REAL_PERF_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    players = data.get("players")
    return players if isinstance(players, dict) else {}


def _synthesize_formation_performance(players, real_map=None):
    """Generate per-formation stats, preferring StatsBomb real aggregates.

    对每个球员：
      1. 有真实数据且无生涯合计 —— 直接采用真实值；
      2. 有生涯合计 —— 真实值优先，差额按位置权重补齐（最大余数保证合计精确）；
         真实值超出合计时按比例缩回合计（数据源口径差异）；
      3. 既无真实数据也无生涯合计 —— 沿用"赛季数 × 位置基准"的估算。
    真实数据在合并后不单独暴露字段（apps_real / estimated 等），
    统一表现为合并后的 apps / goals / assists —— 真实值提升可信度，
    但前端不再区分来源。
    """
    real_map = real_map or {}
    for p in players:
        real = real_map.get(p["id"]) or {}
        # players.py 里手工硬编码的 formation_performance：若无真实数据则跳过
        # （保留手工值，真实数据会在下方分支优先合并）
        if p.get("formation_performance") and not real:
            continue
        career = p.get("career_history") or []
        hist = p.get("market_value_history") or []
        rng = random.Random(p["id"])
        totals_known = bool(career) and career[0].get("apps") is not None

        # --- 情况 1：有真实数据、但该球员没有生涯合计（如新增门将） ---
        if real and not totals_known:
            value = (hist[-1].get("value_m_eur") if hist else 5) or 5
            base_rating = _rating_base(value)
            perf = {}
            for f in FORMATIONS:
                cell = real.get(f) or {}
                apps = int(cell.get("apps") or 0)
                if not apps:
                    continue
                rating = base_rating + rng.uniform(-0.12, 0.12)
                perf[f] = {
                    "apps": apps,
                    "goals": int(cell.get("goals") or 0),
                    "assists": int(cell.get("assists") or 0),
                    "avg_rating": round(min(8.6, max(6.0, rating)), 2),
                }
            if not perf:
                continue
            p["formation_performance"] = perf
            continue

        if not career or not hist:
            continue

        value = hist[-1].get("value_m_eur") or 5
        if totals_known:
            # 有真实生涯合计的球员：以生涯合计为总量，真实数据优先填充
            total_apps = sum((c.get("apps") or 0) for c in career)
            total_goals = sum((c.get("goals") or 0) for c in career)
            total_assists = sum((c.get("assists") or 0) for c in career)
        else:
            seasons = 0
            for c in career:
                start = period_start(c["period"])
                end = period_end(c["period"])
                if end is None:
                    end = 2026 if c["period"].endswith("-") else start
                seasons += max(1, end - start + 1)
            base = (44 if value >= 100 else 40 if value >= 60 else
                    36 if value >= 30 else 30 if value >= 10 else 26)
            total_apps = max(1, round(seasons * base * rng.uniform(0.85, 1.15)))
            g_rate, a_rate = _FORMATION_RATES.get(p["position_group"], _FORMATION_RATES["MF"])
            quality = 0.7 + min(1.0, value / 150) + rng.uniform(0, 0.2)
            total_goals = round(total_apps * g_rate * quality)
            total_assists = round(total_apps * a_rate * quality)

        real_apps = [int((real.get(f) or {}).get("apps") or 0) for f in FORMATIONS]
        real_goals = [int((real.get(f) or {}).get("goals") or 0) for f in FORMATIONS]
        real_assists = [int((real.get(f) or {}).get("assists") or 0) for f in FORMATIONS]
        raw_real_apps = sum(real_apps)
        if real:
            real_apps = _fit_total(real_apps, total_apps)
            real_goals = _fit_total(real_goals, total_goals)
            real_assists = _fit_total(real_assists, total_assists)

        weights = _FORMATION_WEIGHTS.get(p["position_group"], _FORMATION_WEIGHTS["MF"])
        weights = [w * rng.uniform(0.75, 1.25) for w in weights]
        wsum = sum(weights)
        weights = [w / wsum for w in weights]

        extra_apps = _split_total(max(0, total_apps - sum(real_apps)), weights)
        extra_goals = _split_total(max(0, total_goals - sum(real_goals)), weights)
        extra_assists = _split_total(max(0, total_assists - sum(real_assists)), weights)
        apps_final = [real_apps[i] + extra_apps[i] for i in range(len(FORMATIONS))]
        goals_final = [real_goals[i] + extra_goals[i] for i in range(len(FORMATIONS))]
        assists_final = [real_assists[i] + extra_assists[i] for i in range(len(FORMATIONS))]

        base_rating = _rating_base(value)
        perf = {}
        for i, f in enumerate(FORMATIONS):
            rating = base_rating + rng.uniform(-0.12, 0.12)
            perf[f] = {
                "apps": apps_final[i],
                "goals": goals_final[i],
                "assists": assists_final[i],
                "avg_rating": round(min(8.6, max(6.0, rating)), 2),
            }
        p["formation_performance"] = perf


def _validate_dataset(players):
    """数据集完整性校验：在离线 ETL 阶段就失败，而不是等到请求时才暴露。"""
    for p in players:
        mv_clubs = {m["club"] for m in p.get("market_value_history") or []}
        for c in p.get("career_history") or []:
            assert c["club"] in mv_clubs, (
                f"{p['id']} {p['name']}: career club '{c['club']}' "
                f"missing from market_value_history")
        career = p.get("career_history") or []
        fp = p.get("formation_performance")
        if fp and career and career[0].get("apps") is not None:
            keys = ("apps", "goals", "assists") + METRIC_KEYS
            for key in keys:
                c_sum = sum(c.get(key) or 0 for c in career)
                f_sum = sum((fp.get(f) or {}).get(key, 0) for f in FORMATIONS)
                assert c_sum == f_sum, (
                    f"{p['id']} {p['name']}: formation {key} sum {f_sum} "
                    f"!= career total {c_sum}")


def run_all(players):
    """按顺序执行全部加工步骤（就地修改 players）。"""
    real_map = load_real_performance()
    _reconcile_market_value_gaps(players)
    _reconcile_career_metrics(players)
    _synthesize_formation_performance(players, real_map)
    _apply_position_metrics(players)
    _validate_dataset(players)
