"""数据集组装。

优先加载离线 ETL 产物 data/processed/players.json（由 scripts/process_data.py 生成）；
产物缺失或比原始数据旧时，现场执行一次 ETL 并给出提示，保证开发时不至于跑不起来。
"""

import json
import os

from . import etl
from .i18n import PLAYER_NAMES_ZH
from .players import PLAYERS as RAW_PLAYERS

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(HERE, "players.py")
PROCESSED_PATH = os.path.join(HERE, "processed", "players.json")


def _is_fresh():
    if not os.path.exists(PROCESSED_PATH):
        return False
    newest = os.path.getmtime(RAW_PATH)
    # 真实阵型聚合产物更新后也要重新生成，否则新抓到的数据不会生效
    if os.path.exists(etl.REAL_PERF_PATH):
        newest = max(newest, os.path.getmtime(etl.REAL_PERF_PATH))
    return os.path.getmtime(PROCESSED_PATH) >= newest


def _load():
    if _is_fresh():
        with open(PROCESSED_PATH, encoding="utf-8") as f:
            return json.load(f)
    print("[data] processed/players.json 缺失或过期，现场执行 ETL；"
          "建议运行 python scripts/process_data.py 生成离线数据集")
    players = json.loads(json.dumps(RAW_PLAYERS))  # 深拷贝，避免污染原始字面量
    etl.run_all(players)
    return players


PLAYERS = _load()

# 中文名回填（原 data.py 里写在 i18n 段落末尾，改为加载后统一执行）
for _p in PLAYERS:
    _p["name_zh"] = PLAYER_NAMES_ZH.get(_p["id"], _p["name"])
