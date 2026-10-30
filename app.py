"""Flask backend for the Football Player Value Tracker.

Focus pivot (per latest spec):
  - Player market-value trajectory over recent years (Transfermarkt data)
  - Career history annotated with fclogo.top team badges
  - Per-formation performance comparison

Endpoints:
    GET  /                            -> SPA index
    GET  /api/players                  -> player summary list
    GET  /api/player?id=pXX            -> full player record (history + career + formations)
    GET  /api/compare?ids=p01,p02,...  -> market value series for multiple players (overlay)
    GET  /api/formations               -> formation list + notes
    GET  /api/search-index             -> pinyin initials/full spellings for fuzzy search
    GET  /api/logos                    -> fclogo.top URL map (for debugging/UI)

Run with:  python app.py    (then open http://127.0.0.1:5000)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import lru_cache
import gzip
import hashlib
import os
import re

from data import (
    PLAYERS, FORMATIONS, FORMATION_NOTES, FORMATION_POSITIONS, POSITION_DUTIES, POSITION_DUTIES_EN, LOGOS,
    POSITION_ZH, POSITION_GROUP_ZH, NATION_ZH, COUNTRY_ZH, LEAGUE_ZH, FOOT_ZH, CITY_ZH, STADIUM_ZH,
    FORMATION_NOTES_EN, PINYIN_INITIALS, PINYIN_FULL,
    logo_for, player_by_id, player_full, player_summary,
    player_club_associations, clubs_with_geo_and_signings, formation_summary,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "templates"), static_url_path="")
# 静态资源（CSS/JS/头像/世界地图）可以放心长缓存：CSS/JS 通过 ?v=内容哈希 破缓存，
# 头像与 world.json 本身不随发版变化
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 24 * 3600
# 生产环境用 CORS_ORIGINS 收紧来源；未配置时仅放行本机常用端口（同源请求本就不受 CORS 限制）
_PORT = os.environ.get("PORT", "5000")
_DEFAULT_ORIGINS = f"http://127.0.0.1:{_PORT},http://localhost:{_PORT}"
_origins = os.environ.get("CORS_ORIGINS", "").strip() or _DEFAULT_ORIGINS
CORS(app, resources={r"/api/*": {"origins": [o.strip() for o in _origins.split(",") if o.strip()]}})

PLAYER_ID_RE = re.compile(r"^p\d{2,3}$")


# 静态资源版本号：CSS/JS 内容哈希，用于 index.html 里的 ?v= 破缓存
def _asset_version():
    h = hashlib.md5()
    for name in ("styles.css", "app.js"):
        with open(os.path.join(app.static_folder, name), "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:10]


ASSET_V = _asset_version()
_index_cache = {"mtime": None, "html": None}


def _render_index():
    """读取 index.html 并把 __ASSET_V__ 占位符换成资源哈希（带 mtime 缓存）。

    这里不用 render_template：index.html 是一份 Vue 模板，满篇 {{ }} 会被 Jinja 吃掉。
    """
    path = os.path.join(app.static_folder, "index.html")
    mtime = os.path.getmtime(path)
    if _index_cache["mtime"] != mtime:
        with open(path, encoding="utf-8") as f:
            _index_cache["html"] = f.read().replace("__ASSET_V__", ASSET_V)
        _index_cache["mtime"] = mtime
    return _index_cache["html"]


@app.route("/")
def index():
    # 禁用缓存：Flask 默认给静态文件 max-age，会导致浏览器一直用旧版 HTML
    resp = app.response_class(_render_index(), mimetype="text/html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@app.after_request
def _no_store(resp):
    # 所有 API 响应禁止缓存，避免浏览器继续使用旧版球员/俱乐部数据
    if resp.mimetype == "application/json":
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
    return resp


@app.after_request
def _security_headers(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    # Vue 浏览器版需要 unsafe-eval 做模板编译；Vue/ECharts 已自托管到 templates/vendor（带 SRI 校验），
    # 因此 script-src 不再放行第三方 CDN
    resp.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://cdn.jsdelivr.net https://fastly.jsdelivr.net; "
        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
    )
    return resp


_gzip_cache = {}


def _gzip_static(resp):
    """静态文件响应（send_file 的 direct_passthrough）压缩：直接从文件句柄读原始字节。

    压缩结果按 (路径, mtime, 大小) 缓存，避免每次请求都重新压 1MB 的 ECharts/world.json。
    """
    f = getattr(resp.response, "file", None)
    if f is None:
        return None
    try:
        st = os.fstat(f.fileno())
        key = (getattr(f, "name", ""), st.st_mtime_ns, st.st_size)
    except (OSError, ValueError):
        return None
    body = _gzip_cache.get(key)
    if body is None:
        try:
            f.seek(0)
            body = gzip.compress(f.read(), compresslevel=6)
        except (OSError, ValueError):
            return None
        if len(_gzip_cache) > 16:
            _gzip_cache.clear()
        _gzip_cache[key] = body
    return body


@app.after_request
def _compress(resp):
    """对文本类响应做 gzip（JSON/CSS/JS 体积可压掉 60%+），静态文件同样适用。"""
    if resp.status_code != 200 or resp.headers.get("Content-Encoding"):
        return resp
    if "gzip" not in request.headers.get("Accept-Encoding", "").lower():
        return resp
    if resp.mimetype not in ("application/json", "text/html", "text/css",
                             "application/javascript", "text/javascript",
                             "image/svg+xml"):
        return resp
    if resp.direct_passthrough:
        body = _gzip_static(resp)
        if body is None:
            return resp
        resp.direct_passthrough = False
    else:
        data = resp.get_data()
        if len(data) < 500:   # 太小的响应压缩反而变大
            return resp
        body = gzip.compress(data, compresslevel=6)
    resp.set_data(body)
    resp.headers["Content-Encoding"] = "gzip"
    resp.headers["Content-Length"] = str(len(body))
    resp.headers["Vary"] = "Accept-Encoding"
    return resp


@app.route("/api/search-index")
def api_search_index():
    """中文名的拼音索引：首字母（jlambp）与全拼（jilianmubapei），供前端拼音搜索。"""
    return jsonify({"initials": PINYIN_INITIALS, "full": PINYIN_FULL})


@app.route("/api/players")
def api_players():
    return jsonify({"players": [player_summary(p) for p in PLAYERS]})


@app.route("/api/player")
def api_player():
    pid = (request.args.get("id") or "").strip()
    if not PLAYER_ID_RE.match(pid):
        return jsonify({"error": "invalid player id", "id": pid}), 400
    p = player_by_id(pid)
    if p is None:
        return jsonify({"error": "player not found", "id": pid}), 404
    return jsonify(player_full(p))


@app.route("/api/compare")
def api_compare():
    ids_arg = request.args.get("ids", "")
    ids = [s.strip() for s in ids_arg.split(",") if s.strip()][:10]  # 最多 10 名，避免超大请求
    series = []
    for pid in ids:
        p = player_by_id(pid)
        if not p:
            continue
        series.append({
            "id": p["id"],
            "name": p["name"],
            "current_club": p["current_club"],
            "club_logo": logo_for(p["current_club"]),
            "position_group": p["position_group"],
            "data": [
                {"date": m["date"], "value_m_eur": m["value_m_eur"], "club": m["club"]}
                for m in p["market_value_history"]
            ],
        })
    return jsonify({"series": series})


@app.route("/api/formations")
def api_formations():
    return jsonify({
        "formations": FORMATIONS,
        "notes": FORMATION_NOTES,
        "notes_en": FORMATION_NOTES_EN,
        "positions": FORMATION_POSITIONS,
        "position_duties": POSITION_DUTIES,
        "position_duties_en": POSITION_DUTIES_EN,
    })


@app.route("/api/i18n")
def api_i18n():
    """Static label dictionaries for the bilingual UI (zh / en)."""
    return jsonify({
        "positions": POSITION_ZH,
        "position_groups": POSITION_GROUP_ZH,
        "nations": NATION_ZH,
        "countries": COUNTRY_ZH,
        "leagues": LEAGUE_ZH,
        "feet": FOOT_ZH,
        "cities": CITY_ZH,
        "stadiums": STADIUM_ZH,
    })


@app.route("/api/formation-summary")
def api_formation_summary():
    """阵型详情页：聚合各球员的 formation_performance（生涯总量的分摊估算，无数据的球员不计入）。"""
    return jsonify({"formations": formation_summary()})


@app.route("/api/logos")
def api_logos():
    return jsonify({"logos": LOGOS})


@lru_cache(maxsize=16)
def _clubs_cached(year_from):
    """俱乐部+引援的派生计算较贵，按 year_from 缓存（data.py 只在启动时加载一次）。"""
    return tuple(clubs_with_geo_and_signings(year_from=year_from))


@app.route("/api/clubs")
def api_clubs():
    """World-map data: every catalogued club's coordinates + recent signings
    (transfers with start year >= year_from)."""
    try:
        year_from = int(request.args.get("year_from", "2020"))
    except ValueError:
        return jsonify({"error": "year_from must be an integer"}), 400
    return jsonify({
        "clubs": list(_clubs_cached(year_from)),
        "year_from": year_from,
    })


@app.route("/api/associations")
def api_associations():
    """Table B: player-club association records (joined via club_id)."""
    return jsonify({"associations": player_club_associations()})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # 默认关闭 debug，需要热重载时显式 FLASK_DEBUG=1
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="127.0.0.1", port=port, debug=debug)
