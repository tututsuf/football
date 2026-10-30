"""对外查询接口：球员摘要/完整记录、阵型汇总、球员-俱乐部关联。"""

import os

from .clubs import CLUBS, club_id_for, league_for, logo_for
from .dataset import PLAYERS
from .formations import FORMATIONS, FORMATION_NOTES
from .i18n import (CLUB_NAME_ZH, FOOT_ZH, LEAGUE_ZH, NATION_ZH,
                   POSITION_GROUP_ZH, POSITION_ZH)
from .periods import period_end, period_start

# ----------------------------------------------------------------------
# 球员头像
#   TM_PLAYER_IDS   Transfermarkt player id（头像来源标识，人工核对）
#   头像图源说明     Transfermarkt 图片 CDN（img.transfermarkt.technology）
#                   在本机网络环境下整域返回 403（空响应体、无 server 头，
#                   UA / Referer / Sec-Fetch / Chrome TLS 指纹伪装均无效），
#                   因此头像字节改从 FotMob 官方图床下载并缓存到
#                   templates/photos/{player_id}.png，只引用本地文件。
#                   TM id 保留作为来源映射，换网络时可直接切回 TM CDN：
#                   https://img.transfermarkt.technology/portrait/header/{id}.jpg
# ----------------------------------------------------------------------

TM_PLAYER_IDS = {
    "p01": 325807, "p02": 418560, "p03": 581678, "p04": 371998, "p05": 88755,
    "p06": 148455, "p07": 139208, "p08": 357565, "p09": 433177, "p10": 314353,
    "p11": 598577, "p12": 406625, "p13": 937958, "p14": 38253, "p15": 132098,
    "p16": 406635, "p17": 412363, "p18": 86202, "p19": 568177, "p20": 315779,
    "p21": 349066, "p22": 502670, "p23": 258004, "p24": 241641, "p25": 108390,
    "p26": 566723, "p27": 683840, "p28": 670681, "p29": 487469, "p30": 914562,
    "p31": 357662, "p32": 576024, "p33": 495666, "p34": 288230, "p35": 636703,
    "p36": 451276, "p37": 401923, "p38": 580195, "p39": 687626, "p40": 1390649,
    "p41": 792380, "p42": 369081, "p43": 503743, "p44": 861410, "p45": 607223,
    "p46": 648195, "p47": 810092, "p48": 583255, "p49": 709726, "p50": 397033,
    "p51": 616341, "p52": 398073, "p53": 962110, "p54": 626724, "p55": 661171,
    "p56": 948294, "p57": 478573, "p58": 1056993, "p59": 486049, "p60": 435338,
    "p61": 423440, "p62": 517894, "p63": 413039, "p64": 627442, "p65": 845654,
    "p67": 567576, "p68": 344695, "p69": 480692, "p70": 708265, "p71": 520624,
    "p72": 475959, "p73": 534033, "p74": 820374, "p75": 743413, "p76": 744149,
    "p77": 392757, "p78": 955357, "p79": 429014, "p80": 420243, "p81": 411295,
    "p82": 413112, "p83": 315853, "p84": 479999, "p85": 503733, "p86": 739443,
    "p87": 325443, "p88": 316264, "p89": 1075147, "p90": 892160, "p91": 610442,
    "p92": 472423, "p93": 487465, "p94": 1012564, "p95": 434675, "p96": 293385,
    "p97": 411975, "p98": 890290, "p99": 388198, "p100": 1004301, "p101": 532826,
    "p102": 502821, "p103": 623570, "p104": 973085, "p105": 309400, "p106": 455661,
    "p107": 775605, "p108": 927353, "p109": 406640, "p110": 618472, "p111": 198116,
    "p112": 318528, "p113": 441986, "p114": 255942, "p115": 357164, "p116": 624690,
    "p117": 1097139, "p118": 745200, "p119": 543499, "p120": 880245, "p121": 503987,
    "p122": 557459, "p123": 659813, "p124": 763079, "p125": 855256, "p126": 601883,
    "p127": 614258, "p128": 923831, "p129": 284857, "p130": 1005649, "p131": 460939,
    "p132": 445939, "p133": 434224, "p134": 733576, "p135": 811778, "p136": 398184,
    "p137": 640428, "p138": 636688, "p139": 443710, "p140": 554903, "p141": 546543,
}

PHOTO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "templates", "photos")


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def player_by_id(pid):
    for p in PLAYERS:
        if p["id"] == pid:
            return p
    return None


def photo_for(p):
    """本地缓存的球员头像 URL；无文件时返回 None（前端回退首字母）。"""
    if os.path.exists(os.path.join(PHOTO_DIR, p["id"] + ".png")):
        return "/photos/" + p["id"] + ".png"
    return None


def player_summary(p):
    """Compact summary used in player list / select widgets."""
    latest = p["market_value_history"][-1] if p["market_value_history"] else {}
    club_meta = CLUBS.get(p["current_club"], {})
    league = club_meta.get("league")
    return {
        "id": p["id"],
        "name": p["name"],
        "name_zh": p.get("name_zh") or p["name"],
        "position": p["position"],
        "position_zh": POSITION_ZH.get(p["position"], p["position"]),
        "position_group": p["position_group"],
        "position_group_zh": POSITION_GROUP_ZH.get(p["position_group"], p["position_group"]),
        "age": p["age"],
        "current_club": p["current_club"],
        "club_zh": club_meta.get("zh_name") or p["current_club"],
        "club_id": club_id_for(p["current_club"]),
        "current_value_m_eur": latest.get("value_m_eur"),
        "club_logo": logo_for(p["current_club"]),
        "photo_url": photo_for(p),
        "nationality": p["nationality"],
        "nationality_zh": NATION_ZH.get(p["nationality"], p["nationality"]),
        "league": league,
        "league_zh": LEAGUE_ZH.get(league, league),
    }


def formation_summary():
    """Aggregate per-formation stats across all players.

    Per-formation figures are estimates: for players with career totals they
    are a split of those totals (sums match exactly); for players without,
    they are synthesized from career span × position benchmarks at import.
    Used for relative comparison only — not per-match records.
    avg_rating is weighted by apps for a more representative figure.
    apps_real / coverage report how much of the apps figure is backed by
    StatsBomb per-match data (see scripts/fetch_statsbomb.py).
    """
    out = []
    for f in FORMATIONS:
        apps = goals = assists = 0
        apps_real = 0
        real_players = 0
        rating_weighted = 0.0
        rating_apps = 0
        contributors = []
        for p in PLAYERS:
            v = (p.get("formation_performance") or {}).get(f)
            if not v:
                continue
            f_apps = v.get("apps") or 0
            apps += f_apps
            goals += v.get("goals") or 0
            assists += v.get("assists") or 0
            f_real = min(v.get("apps_real") or 0, f_apps)
            apps_real += f_real
            if f_real:
                real_players += 1
            if v.get("avg_rating"):
                rating_weighted += v["avg_rating"] * f_apps
                rating_apps += f_apps
            contributors.append({
                "id": p["id"], "name": p["name"],
                "current_club": p["current_club"],
                "club_logo": logo_for(p["current_club"]),
                "position_group": p["position_group"],
                "apps": f_apps,
                "goals": v.get("goals") or 0,
                "assists": v.get("assists") or 0,
                # 位置专属指标：门将看扑救/丢球，后卫看解围/拦截
                "saves": v.get("saves") or 0,
                "conceded": v.get("conceded") or 0,
                "clearances": v.get("clearances") or 0,
                "interceptions": v.get("interceptions") or 0,
                "avg_rating": v.get("avg_rating"),
                "apps_real": f_real,
                "estimated": bool(v.get("estimated")),
            })
        contributors.sort(key=lambda x: -(x["apps"] or 0))
        out.append({
            "formation": f,
            "note": FORMATION_NOTES.get(f, ""),
            "players": len(contributors),
            "apps": apps,
            "goals": goals,
            "assists": assists,
            "goal_contrib": goals + assists,
            "apps_real": apps_real,
            "real_players": real_players,
            "coverage": round(apps_real / apps, 3) if apps else 0.0,
            "avg_rating": round(rating_weighted / rating_apps, 2) if rating_apps else None,
            "contributors": contributors,
        })
    return out


def _career_row(c):
    """单条生涯记录：补 club_id / 队徽 / 中文名，并在 league 为空时回退到俱乐部主表或补充表。"""
    club = c["club"]
    league = league_for(club, c.get("league"))
    return {**c,
            "club_id": club_id_for(club), "logo_url": logo_for(club),
            "club_zh": CLUBS.get(club, {}).get("zh_name") or CLUB_NAME_ZH.get(club) or club,
            "league": league, "league_zh": LEAGUE_ZH.get(league, league)}


def player_full(p):
    """Full player record with club_id + logo URLs attached to career history."""
    out = dict(p)
    club_meta = CLUBS.get(p["current_club"], {})
    out["club_id"] = club_id_for(p["current_club"])
    out["club_logo"] = logo_for(p["current_club"])
    out["photo_url"] = photo_for(p)
    out["club_zh"] = club_meta.get("zh_name") or p["current_club"]
    out["position_zh"] = POSITION_ZH.get(p["position"], p["position"])
    out["position_group_zh"] = POSITION_GROUP_ZH.get(p["position_group"], p["position_group"])
    out["nationality_zh"] = NATION_ZH.get(p["nationality"], p["nationality"])
    out["foot_zh"] = FOOT_ZH.get(p["foot"], p["foot"])
    out["career_history"] = [_career_row(c) for c in p["career_history"]]
    out["market_value_history"] = [
        {**m, "club_id": club_id_for(m["club"]), "club_logo": logo_for(m["club"]),
         "club_zh": CLUBS.get(m["club"], {}).get("zh_name") or CLUB_NAME_ZH.get(m["club"]) or m["club"]}
        for m in p["market_value_history"]
    ]
    return out


def player_club_associations():
    """Build Table B: player-club association records derived from career_history.

    Each record: {player_id, player_name, club_id, club_name, period_from,
    period_to, was_starter, apps, goals, assists}.
    was_starter is a best-effort flag: True when apps-per-season >= ~15.
    This is what lets market value, geography and logos be joined via club_id.
    """
    out = []
    for p in PLAYERS:
        for c in p["career_history"]:
            pf = period_start(c["period"])
            pt = period_end(c["period"])
            seasons = (pt - pf + 1) if pt else (2026 - pf + 1)
            # 新增球员的出场/进球/助攻为 None（仅保留真实字段，不做估算）
            if c["apps"] is None:
                apps_per_season = 0
                was_starter = None
            else:
                apps_per_season = c["apps"] / seasons if seasons > 0 else c["apps"]
                was_starter = apps_per_season >= 15
            out.append({
                "player_id": p["id"],
                "player_name": p["name"],
                "club_id": club_id_for(c["club"]),
                "club_name": c["club"],
                "period_from": pf,
                "period_to": pt,
                "was_starter": was_starter,
                "apps": c["apps"],
                "goals": c["goals"],
                "assists": c["assists"],
            })
    return out
