"""离线执行数据加工（ETL），产出 data/processed/players.json。

用法：python scripts/process_data.py

Web 服务只读该产物；重新生成后无需改代码，重启进程即可生效。
产物比 players.py 旧时，服务端会自动回退到现场加工并打印提示。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data import etl            # noqa: E402
from data.players import PLAYERS as RAW_PLAYERS  # noqa: E402

OUT_DIR = os.path.join(ROOT, "data", "processed")
OUT_PATH = os.path.join(OUT_DIR, "players.json")


def main():
    # 深拷贝：不污染 players.py 里的原始字面量
    players = json.loads(json.dumps(RAW_PLAYERS))
    etl.run_all(players)   # 校验失败会在这里抛出，而不是拖到 Web 请求期

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, separators=(",", ":"))

    estimated_points = sum(
        1 for p in players
        for m in p.get("market_value_history") or [] if m.get("estimated"))
    synthesized = sum(
        1 for p in players
        if p.get("formation_performance")
        and not all((c.get("apps") is not None) for c in p.get("career_history") or []))
    # 从真实产物里读覆盖情况（ETL 已把真实值合并进 apps/goals/assists，
    # 不再单独暴露来源标记，这里只做统计给人看）
    real_file = etl.REAL_PERF_PATH
    try:
        with open(real_file, encoding="utf-8") as f:
            real_data = json.load(f)
        cov = real_data.get("coverage", {})
        players_matched = cov.get("players_matched", 0)
        records_matched = cov.get("records_matched", 0)
        matches = real_data.get("matches", 0)
    except (OSError, ValueError):
        players_matched = records_matched = matches = 0
    print(f"players           : {len(players)}")
    print(f"estimated MV points: {estimated_points}")
    print(f"synthesized perf   : {synthesized} players")
    print(f"real formation perf: StatsBomb {matches} 场，"
          f"{players_matched} 人命中，{records_matched} 条实录混入合并值")
    print(f"written            : {OUT_PATH} "
          f"({os.path.getsize(OUT_PATH) // 1024} KB)")


if __name__ == "__main__":
    main()
