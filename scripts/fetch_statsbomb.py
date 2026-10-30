"""StatsBomb open-data 阵型数据抓取 + 聚合（断点续传）。

数据源：StatsBomb open-data（jsDelivr 镜像 GitHub 仓库，raw.githubusercontent 兜底）。
为什么不用 FBref：FBref 整域 Cloudflare 403，无法稳定抓取；raw GitHub 直连也不稳定。

流程：
  1) fetch   —— 抓 competitions / matches / lineups / events，逐场解析出
                 「球员 × 阵型 × 进球/助攻/出场」的小文件，写入缓存。
                 已解析的场次直接跳过，中断后重跑即可续传。
  2) aggregate —— 扫描缓存里的逐场解析结果，按球员聚合，产出
                 data/processed/formation_real.json，供 data/etl.py 消费。

用法：
  python scripts/fetch_statsbomb.py                  # 抓取默认赛季集（可重复执行续传）
  python scripts/fetch_statsbomb.py --rebuild        # 不联网，只用本地缓存重算
  python scripts/fetch_statsbomb.py --list           # 列出可用联赛/赛季
  python scripts/fetch_statsbomb.py --season 2:27 --season 9:281
  python scripts/fetch_statsbomb.py --season 9:281 --max-matches 50
  python scripts/fetch_statsbomb.py --all            # 抓全部赛季（数据量极大）

缓存目录默认 %TEMP%/statsbomb-cache，可用环境变量 STATSBOMB_CACHE 覆盖。
缓存不写入仓库；仓库内只提交聚合产物 data/processed/formation_real.json。
"""

import argparse
import datetime
import json
import os
import re
import sys
import tempfile
import time
import unicodedata
from collections import defaultdict

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data.formations import FORMATIONS                     # noqa: E402
from data.periods import period_end, period_start          # noqa: E402

BASE_URLS = [
    # jsDelivr 镜像 GitHub 仓库：国内访问比 raw.githubusercontent.com 稳定得多
    "https://cdn.jsdelivr.net/gh/statsbomb/open-data@master/data",
    "https://fastly.jsdelivr.net/gh/statsbomb/open-data@master/data",
    "https://raw.githubusercontent.com/statsbomb/open-data/master/data",
]
CACHE_DIR = os.environ.get("STATSBOMB_CACHE") or os.path.join(
    tempfile.gettempdir(), "statsbomb-cache")
OUT_PATH = os.path.join(ROOT, "data", "processed", "formation_real.json")

FORMATION_BY_INT = {433: "4-3-3", 442: "4-4-2", 352: "3-5-2", 4231: "4-2-3-1"}

# 默认只抓规模和覆盖度都比较合适的赛季；--season 可覆盖，--all 抓全量。
DEFAULT_SEASONS = [
    ("Premier League", "2015/2016"),
    ("La Liga", "2019/2020"),
    ("1. Bundesliga", "2023/2024"),
    ("Serie A", "2015/2016"),
    ("Ligue 1", "2021/2022"),
    ("UEFA Champions League", "2018/2019"),
    ("FIFA World Cup", "2022"),
    ("UEFA Euro", "2024"),
    ("Copa America", "2024"),
]

# StatsBomb 球队名 -> 本仓库 clubs.py 的 key（只列名字对不上的）
TEAM_ALIASES = {
    "FC Bayern München": "Bayern Munich",
    "Bayern München": "Bayern Munich",
    "Borussia Dortmund": "Dortmund",
    "Bayer 04 Leverkusen": "Bayer Leverkusen",
    "VfL Wolfsburg": "Wolfsburg",
    "SV Werder Bremen": "Werder Bremen",
    "Paris Saint-Germain": "PSG",
    "Manchester United": "Manchester Utd",
    "Tottenham Hotspur": "Tottenham",
    "Newcastle United": "Newcastle",
    "Atlético Madrid": "Atletico Madrid",
    "FC Barcelona": "Barcelona",
    "Real Madrid": "Real Madrid",
    "Villarreal CF": "Villarreal",
    "FC Internazionale Milano": "Inter Milan",
    "Inter": "Inter Milan",
    "SSC Napoli": "Napoli",
    "AS Roma": "AS Roma",
    "Juventus": "Juventus",
    "AC Milan": "AC Milan",
    "SL Benfica": "Benfica",
    "FC Porto": "Porto",
    "Sporting CP": "Sporting CP",
    "LOSC Lille": "Lille",
    "Olympique Lyonnais": "Lyon",
    "Stade Rennais": "Rennes",
    "Stade de Reims": "Reims",
    "AS Saint-Étienne": "Saint-Etienne",
    "Eintracht Frankfurt": "Eintracht Frankfurt",
    "RB Leipzig": "RB Leipzig",
    "AFC Ajax": "Ajax",
    "AS Monaco": "AS Monaco",
    "Real Sociedad": "Real Sociedad",
    "Aston Villa": "Aston Villa",
    "Crystal Palace": "Crystal Palace",
    "Brighton & Hove Albion": "Brighton",
    "Wolverhampton Wanderers": "Wolves",
    "Brentford": "Brentford",
    "AFC Bournemouth": "Bournemouth",
    "Leicester City": "Leicester",
    "West Ham United": "West Ham",
    "Everton": "Everton",
    "Fulham": "Fulham",
    "Nottingham Forest": "Nottingham Forest",
    "Leeds United": "Leeds",
    "Burnley": "Burnley",
    "Sheffield United": "Sheffield Utd",
    "Luton Town": "Luton",
    "Watford": "Watford",
    "Norwich City": "Norwich",
    "West Bromwich Albion": "West Brom",
    "Stoke City": "Stoke",
    "Swansea City": "Swansea",
    "Hull City": "Hull",
    "Sunderland": "Sunderland",
    "Middlesbrough": "Middlesbrough",
    "Reading": "Reading",
    "Birmingham City": "Birmingham City",
    "Southampton": "Southampton",
    "Celtic": "Celtic",
}

# StatsBomb 球员名 -> 本仓库 players.py 的 name（只列缩写/全名对不上的）
PLAYER_ALIASES = {
    "Erling Braut Haaland": "Erling Haaland",
    "Rodrigo Hernández": "Rodri",
    "Rodrigo Hernandez": "Rodri",
    "Rodrigo Hernández Cascante": "Rodri",
    "Rodrigo Hernandez Cascante": "Rodri",
    "Pedro González López": "Pedri",
    "Pedro Gonzalez Lopez": "Pedri",
    "Alisson Ramsés Becker": "Alisson Becker",
    "Alisson Ramos Becker": "Alisson Becker",
    "Ederson Santana de Moraes": "Ederson",
    "David Raya Martín": "David Raya",
    "Gabriel dos Santos Magalhães": "Gabriel",
    "Gabriel dos Santos Magalhaes": "Gabriel",
    "Raphael Dias Belloli": "Raphinha",
    "Rodrygo Silva de Goes": "Rodrygo",
    "Vinícius José Paixão de Oliveira Júnior": "Vinícius Júnior",
    "Vinicius Jose Paixao de Oliveira Junior": "Vinícius Júnior",
    "Marc-André ter Stegen": "Marc-André ter Stegen",
    "Gianluigi Donnarumma": "Gianluigi Donnarumma",
    "Yann Sommer": "Yann Sommer",
    "Yassine Bounou": "Yassine Bounou",
    "Emiliano Martínez": "Emiliano Martínez",
    "Emiliano Martinez": "Emiliano Martínez",
    # StatsBomb 使用本名/全名，与德转常用名不同（缺失会导致国家队比赛无法命中）
    "Kylian Mbappé Lottin": "Kylian Mbappé",
    "Kylian Mbappe Lottin": "Kylian Mbappé",
    "Lautaro Javier Martínez": "Lautaro Martínez",
    "Lautaro Javier Martinez": "Lautaro Martínez",
    "Damián Emiliano Martínez": "Emiliano Martínez",
    "Damian Emiliano Martinez": "Emiliano Martínez",
    "Lamine Yamal Nasraoui Ebana": "Lamine Yamal",
    "Philip Foden": "Phil Foden",
    "Rúben Santos Gato Alves Dias": "Rúben Dias",
    "Ruben Santos Gato Alves Dias": "Rúben Dias",
    "Bernardo Mota Veiga de Carvalho e Silva": "Bernardo Silva",
    "Dayotchanculle Upamecano": "Dayot Upamecano",
    "Aurélien Djani Tchouaméni": "Aurélien Tchouaméni",
    "Aurelien Djani Tchouameni": "Aurélien Tchouaméni",
    "Pedro Lomba Neto": "Pedro Neto",
    "Cody Mathès Gakpo": "Cody Gakpo",
    "Cody Mathes Gakpo": "Cody Gakpo",
    "Rafael Alexandre Conceição Leão": "Rafael Leão",
    "Rafael Alexandre Conceicao Leao": "Rafael Leão",
    "Piero Martín Hincapié Reyna": "Piero Hincapié",
    "Piero Martin Hincapie Reyna": "Piero Hincapié",
    "Matheus Luiz Nunes": "Matheus Nunes",
    "Marc Cucurella Saseta": "Marc Cucurella",
    "Ferrán Torres García": "Ferran Torres",
    "Ferran Torres Garcia": "Ferran Torres",
    "Alejandro Balde Martínez": "Alejandro Balde",
    "Alejandro Balde Martinez": "Alejandro Balde",
    "Darwin Gabriel Núñez Ribeiro": "Darwin Núñez",
    "Darwin Gabriel Nunez Ribeiro": "Darwin Núñez",
    "Diogo Meireles Costa": "Diogo Costa",
    "Anatolii Trubin": "Anatoliy Trubin",
    "Fermin Lopez Marin": "Fermín López",
    "Moisés Isaac Caicedo Corozo": "Moisés Caicedo",
    "Moises Isaac Caicedo Corozo": "Moisés Caicedo",
    "Federico Santiago Valverde Dipetta": "Federico Valverde",
    "Achraf Hakimi Mouh": "Achraf Hakimi",
    "Willian Joel Pacho Tenorio": "Willian Pacho",
    "Martín Zubimendi Ibáñez": "Martín Zubimendi",
    "Martin Zubimendi Ibanez": "Martín Zubimendi",
    "Luis Fernando Díaz Marulanda": "Luis Díaz",
    "Luis Fernando Diaz Marulanda": "Luis Díaz",
    "Bruno Guimarães Rodriguez Moura": "Bruno Guimarães",
    "Bruno Guimaraes Rodriguez Moura": "Bruno Guimarães",
    "Daniel Olmo Carvajal": "Dani Olmo",
}


# ----------------------------------------------------------------------
# 基础工具
# ----------------------------------------------------------------------

def _norm(text):
    """去重音、去标点、小写、压缩空白，用于人名/队名比对。"""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


_NORM_PLAYER_ALIASES = {_norm(k): _norm(v) for k, v in PLAYER_ALIASES.items()}


def _load_cache_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _write_json_atomic(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, path)


def _cache_path(*parts):
    return os.path.join(CACHE_DIR, *parts)


def _ensure_json(session, rel_path, path, timeout=90, retries=2):
    """读缓存；缺失/损坏则依次尝试各镜像下载。返回解析后的对象，失败返回 None。"""
    cached = _load_cache_json(path)
    if cached is not None:
        return cached
    last_error = None
    for base in BASE_URLS:
        url = f"{base}/{rel_path}"
        for attempt in range(1, retries + 1):
            try:
                started = time.time()
                resp = session.get(url, timeout=timeout)
                if resp.status_code != 200:
                    raise RuntimeError(f"HTTP {resp.status_code}")
                data = resp.json()
                _write_json_atomic(path, data)
                print(f"  [get] {os.path.relpath(path, CACHE_DIR)} "
                      f"{len(resp.content) // 1024} KB {time.time() - started:.1f}s "
                      f"via {url.split('/')[2]}")
                return data
            except Exception as exc:          # noqa: BLE001 —— 网络异常一律重试
                last_error = exc
                if attempt < retries:
                    wait = attempt * 2
                    print(f"  [retry {attempt}/{retries}] {exc}；{wait}s 后重试")
                    time.sleep(wait)
        print(f"  [mirror-fail] {url.split('/')[2]} -> {last_error}")
    print(f"  [fail] {rel_path} -> {last_error}")
    return None


# ----------------------------------------------------------------------
# 逐场解析：lineups 提供名单，events 提供阵型/出场/进球/助攻
# ----------------------------------------------------------------------

def _derive_match(match, lineups, events):
    """lineups 提供球员名单；阵型只存在于 events 的 Starting XI（tactics.formation）。"""
    player_team = {}         # statsbomb player_id -> 球队名
    player_name = {}         # statsbomb player_id -> 球员名

    for team in lineups or []:
        team_name = team.get("team_name")
        for entry in team.get("lineup") or []:
            pid = entry.get("player_id")
            if pid is None:
                continue
            player_team[pid] = team_name
            player_name[pid] = entry.get("player_name")

    formations = {}          # 球队名 -> 首发阵型
    played = set()
    goals = defaultdict(int)
    assists = defaultdict(int)

    for event in events or []:
        etype = (event.get("type") or {}).get("name")
        team_name = (event.get("team") or {}).get("name")

        if etype == "Starting XI":
            formation = FORMATION_BY_INT.get((event.get("tactics") or {}).get("formation"))
            if team_name and formation and team_name not in formations:
                formations[team_name] = formation
            for slot in (event.get("tactics") or {}).get("lineup") or []:
                pid = (slot.get("player") or {}).get("id")
                if pid is not None:
                    played.add(pid)
        elif etype == "Substitution":
            off = event.get("player") or {}
            on = (event.get("substitution") or {}).get("replacement") or {}
            for person in (off, on):
                pid = person.get("id")
                if pid is None:
                    continue
                played.add(pid)
                player_name.setdefault(pid, person.get("name"))
                if team_name:
                    player_team.setdefault(pid, team_name)
        elif etype == "Shot":
            if (event.get("shot") or {}).get("outcome", {}).get("name") == "Goal":
                person = event.get("player") or {}
                pid = person.get("id")
                if pid is not None:
                    goals[pid] += 1
                    player_name.setdefault(pid, person.get("name"))
                    if team_name:
                        player_team.setdefault(pid, team_name)
        elif etype == "Pass":
            if (event.get("pass") or {}).get("goal_assist"):
                person = event.get("player") or {}
                pid = person.get("id")
                if pid is not None:
                    assists[pid] += 1
                    player_name.setdefault(pid, person.get("name"))
                    if team_name:
                        player_team.setdefault(pid, team_name)

    season_name = (match.get("season") or {}).get("season_name") or ""
    year = re.search(r"(\d{4})", season_name)
    records = []
    for pid in sorted(played):
        team_name = player_team.get(pid)
        formation = formations.get(team_name)
        if not formation:
            continue           # 阵型不在四种之内（如 4-1-4-1），不计数
        records.append({
            "player_id": pid,
            "name": player_name.get(pid),
            "team": team_name,
            "formation": formation,
            "goals": goals.get(pid, 0),
            "assists": assists.get(pid, 0),
        })

    return {
        "match_id": match.get("match_id"),
        "date": match.get("match_date"),
        "competition": (match.get("competition") or {}).get("competition_name"),
        "season": season_name,
        "season_start": int(year.group(1)) if year else 0,
        "players": records,
    }


def _fetch_season(session, comp_id, season_id, comp_name, season_name,
                  max_matches, keep_raw):
    """抓一个赛季的逐场数据；已解析的场次直接跳过。"""
    print(f"[season] {comp_name} {season_name} (comp={comp_id} season={season_id})")
    matches = _ensure_json(session, f"matches/{comp_id}/{season_id}.json",
                           _cache_path("matches", f"{comp_id}-{season_id}.json"))
    if matches is None:
        return False
    if max_matches and max_matches > 0:
        matches = matches[:max_matches]

    total = len(matches)
    parsed = skipped = failed = 0
    for index, match in enumerate(matches, 1):
        match_id = match.get("match_id")
        derived_path = _cache_path("derived", f"{match_id}.json")
        if _load_cache_json(derived_path) is not None:
            skipped += 1
            continue

        lineup_path = _cache_path("lineups", f"{match_id}.json")
        events_path = _cache_path("events", f"{match_id}.json")
        lineups = _ensure_json(session, f"lineups/{match_id}.json", lineup_path)
        if lineups is None:
            failed += 1
            print(f"  [{index}/{total}] match {match_id} 阵容抓取失败，跳过")
            continue
        events = _ensure_json(session, f"events/{match_id}.json", events_path)
        if events is None:
            failed += 1
            print(f"  [{index}/{total}] match {match_id} 事件抓取失败，跳过")
            continue

        _write_json_atomic(derived_path, _derive_match(match, lineups, events))
        parsed += 1
        if not keep_raw:
            # 逐场解析结果已落盘，原始大文件删除以节省磁盘；
            # 需要原始数据时用 --keep-raw。
            for path in (lineup_path, events_path):
                try:
                    os.remove(path)
                except OSError:
                    pass
        print(f"  [{index}/{total}] match {match_id} 已解析")

    print(f"[season] 完成：新解析 {parsed}，缓存命中 {skipped}，失败 {failed}")
    return failed == 0


# ----------------------------------------------------------------------
# 聚合：逐场结果 -> 每球员每阵型 apps/goals/assists
# ----------------------------------------------------------------------

def _build_team_index():
    from data.clubs import CLUBS
    index = {}
    for key, meta in CLUBS.items():
        index[_norm(key)] = key
        if meta.get("en_name"):
            index[_norm(meta["en_name"])] = key
    for raw, key in TEAM_ALIASES.items():
        index[_norm(raw)] = key
    return index


def _build_player_index():
    from data.players import PLAYERS
    full_name, last_name, spans = {}, {}, {}
    for player in PLAYERS:
        pid = player["id"]
        name = _norm(player["name"])
        full_name.setdefault(name, set()).add(pid)
        tokens = name.split()
        if tokens:
            last_name.setdefault(tokens[-1], set()).add(pid)
        career = []
        for stint in player.get("career_history") or []:
            start = period_start(stint["period"])
            end = period_end(stint["period"]) or 2026
            career.append((stint["club"], start, end))
        spans[pid] = career
    return full_name, last_name, spans


def _match_player(name, team, season_start, indexes, team_index):
    full_name, last_name, spans = indexes
    if not name:
        return None
    normed = _norm(name)
    normed = _NORM_PLAYER_ALIASES.get(normed, normed)
    club = team_index.get(_norm(team)) if team else None

    def in_career(pid):
        if club is None:
            return True
        return any(cname == club and start <= season_start <= end
                   for cname, start, end in spans.get(pid, []))

    candidates = full_name.get(normed) or set()
    if candidates:
        qualified = [pid for pid in candidates if in_career(pid)]
        if len(qualified) == 1:
            return qualified[0]
        if len(qualified) > 1:
            return None
        if club is None and len(candidates) == 1:
            return next(iter(candidates))
        return None

    tokens = normed.split()
    # 仅姓氏匹配风险高（如 "… da Silva Junior" 撞上 Vinícius Júnior），
    # 必须能确定球队且落在该球员生涯区间内才接受。
    if tokens and club is not None:
        qualified = [pid for pid in (last_name.get(tokens[-1]) or set())
                     if in_career(pid)]
        if len(qualified) == 1:
            return qualified[0]
    return None


def aggregate():
    """扫描缓存中的逐场结果，产出 formation_real.json。"""
    derived_dir = _cache_path("derived")
    paths = []
    if os.path.isdir(derived_dir):
        paths = sorted(
            (os.path.join(derived_dir, n) for n in os.listdir(derived_dir)
             if n.endswith(".json")),
            key=lambda p: os.path.getmtime(p))

    if not paths:
        print(f"[aggregate] 缓存中没有逐场结果（{derived_dir}）。"
              f"请先联网运行抓取，或用 STATSBOMB_CACHE 指向已有缓存。")
        return None

    indexes = _build_player_index()
    team_index = _build_team_index()
    stats = defaultdict(lambda: defaultdict(lambda: {"apps": 0, "goals": 0, "assists": 0}))
    unmatched = []
    matched_records = unmatched_records = 0
    seasons = set()
    matches = 0

    for path in paths:
        data = _load_cache_json(path)
        if not data:
            continue
        matches += 1
        seasons.add(f"{data.get('competition')} {data.get('season')}".strip())
        for record in data.get("players") or []:
            pid = _match_player(record.get("name"), record.get("team"),
                                data.get("season_start") or 0, indexes, team_index)
            if pid is None:
                unmatched_records += 1
                unmatched.append({**record, "match_id": data.get("match_id"),
                                  "season": data.get("season")})
                continue
            matched_records += 1
            cell = stats[pid][record["formation"]]
            cell["apps"] += 1
            cell["goals"] += record.get("goals") or 0
            cell["assists"] += record.get("assists") or 0

    players = {}
    for pid in sorted(stats):
        entry = {}
        for formation in FORMATIONS:
            cell = stats[pid].get(formation)
            if cell and cell["apps"]:
                entry[formation] = cell
        if entry:
            players[pid] = entry

    out = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "source": "StatsBomb open-data (github.com/statsbomb/open-data)",
        "matches": matches,
        "seasons": sorted(seasons),
        "coverage": {
            "records_matched": matched_records,
            "records_unmatched": unmatched_records,
            "players_matched": len(players),
        },
        "players": players,
    }
    _write_json_atomic(OUT_PATH, out)
    _write_json_atomic(_cache_path("unmatched.json"), unmatched)

    print(f"[aggregate] 场次 {matches}，命中记录 {matched_records}，"
          f"未匹配 {unmatched_records}，球员 {len(players)}")
    print(f"[aggregate] 已写入 {OUT_PATH}")
    if unmatched:
        print("[aggregate] 未匹配示例（完整清单见缓存 unmatched.json）：")
        seen = set()
        for record in unmatched:
            key = (record.get("name"), record.get("team"))
            if key in seen:
                continue
            seen.add(key)
            print(f"  - {record.get('name')} ({record.get('team')})")
            if len(seen) >= 10:
                break
    return out


# ----------------------------------------------------------------------
# 赛季选择
# ----------------------------------------------------------------------

def _load_competitions(session, allow_network=True):
    path = _cache_path("competitions.json")
    if not allow_network:
        return _load_cache_json(path)
    return _ensure_json(session, "competitions.json", path)


def _resolve_targets(competitions, wanted):
    resolved, seen = [], set()
    for comp_name, season_name in wanted:
        comp_norm = _norm(comp_name)
        comp_hits = [c for c in competitions if _norm(c.get("competition_name")) == comp_norm]
        if not comp_hits:
            comp_hits = [c for c in competitions if comp_norm in _norm(c.get("competition_name"))]
        season_norm = _norm(season_name)
        hits = [c for c in comp_hits if _norm(c.get("season_name")) == season_norm]
        if not hits:
            print(f"[warn] 未找到：{comp_name} {season_name}")
            continue
        for comp in hits:
            key = (int(comp["competition_id"]), int(comp["season_id"]))
            if key in seen:
                continue
            seen.add(key)
            resolved.append((key[0], key[1],
                             comp.get("competition_name"), comp.get("season_name")))
    return resolved


def _list_competitions(competitions):
    grouped = defaultdict(list)
    for comp in competitions:
        grouped[comp.get("competition_name")].append(comp.get("season_name"))
    for name in sorted(grouped):
        seasons = sorted(set(grouped[name]))
        print(f"{name}: {', '.join(seasons)}")


def main():
    parser = argparse.ArgumentParser(description="StatsBomb 阵型数据抓取 + 聚合（断点续传）")
    parser.add_argument("--rebuild", action="store_true", help="不联网，只用本地缓存重算")
    parser.add_argument("--list", action="store_true", help="列出可用联赛/赛季")
    parser.add_argument("--all", action="store_true", help="抓取 competitions.json 中全部赛季")
    parser.add_argument("--season", action="append", default=[],
                        metavar="COMP:SEASON", help="显式指定 comp_id:season_id，可重复")
    parser.add_argument("--max-matches", type=int, default=80,
                        help="每赛季最多解析多少场（0 表示全部，默认 80）")
    parser.add_argument("--keep-raw", action="store_true",
                        help="解析后保留 lineups/events 原始缓存（默认删除以省磁盘）")
    parser.add_argument("--timeout", type=int, default=90, help="单文件下载超时秒数")
    args = parser.parse_args()

    session = requests.Session()
    session.headers["User-Agent"] = "football-etl/1.0 (+statsbomb open-data)"

    if args.rebuild:
        aggregate()
        return

    competitions = _load_competitions(session)
    if competitions is None:
        print("[error] 无法获取 competitions.json，且缓存为空。")
        return

    if args.list:
        _list_competitions(competitions)
        return

    if args.all:
        targets = [(int(c["competition_id"]), int(c["season_id"]),
                    c.get("competition_name"), c.get("season_name"))
                   for c in competitions]
    elif args.season:
        targets = []
        for token in args.season:
            try:
                comp_id, season_id = (int(part) for part in token.split(":", 1))
            except ValueError:
                print(f"[warn] 忽略非法赛季参数：{token}（应为 comp:season）")
                continue
            targets.append((comp_id, season_id, "", ""))
    else:
        targets = _resolve_targets(competitions, DEFAULT_SEASONS)

    if not targets:
        print("[error] 没有可抓取的赛季。用 --list 查看可用赛季，或 --season 指定。")
        return

    print(f"[plan] 目标赛季 {len(targets)} 个，缓存目录 {CACHE_DIR}，"
          f"每赛季上限 {args.max_matches or '全部'} 场")
    failures = 0
    for comp_id, season_id, comp_name, season_name in targets:
        ok = _fetch_season(session, comp_id, season_id, comp_name or str(comp_id),
                           season_name or str(season_id), args.max_matches,
                           args.keep_raw)
        failures += 0 if ok else 1

    aggregate()
    if failures:
        print(f"[done] {failures} 个赛季存在失败场次；重跑本命令即可续传缺失部分。")


if __name__ == "__main__":
    main()
