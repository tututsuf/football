"""生成球员中文名的拼音首字母索引（供前端拼音搜索用）。

用法：python scripts/build_pinyin_index.py
产出：data/pinyin.py（静态字典，运行时不依赖 pypinyin）
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pypinyin import Style, lazy_pinyin  # noqa: E402

from data.i18n import PLAYER_NAMES_ZH  # noqa: E402

OUT_PATH = os.path.join(ROOT, "data", "pinyin.py")

HEADER = '''"""球员中文名的拼音索引（由 scripts/build_pinyin_index.py 生成，请勿手改）。

两种键：
  initials  —— 每个字的首字母（"基利安·姆巴佩" -> "jlambp"），用于首字母快搜
  full      —— 完整拼音（"jilianmubaipei"），用于全拼匹配
"""

'''


def build():
    initials, full = {}, {}
    for pid, name in PLAYER_NAMES_ZH.items():
        # 分隔符（·、空格）不参与拼音，直接剔除，避免生成 "jla·mbp"
        chunks = [c for c in lazy_pinyin(name, style=Style.NORMAL) if c.strip(" ·")]
        full[pid] = "".join(chunks).lower()
        initials[pid] = "".join(c[0] for c in chunks).lower()
    return initials, full


def main():
    initials, full = build()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(HEADER)
        f.write("PINYIN_INITIALS = ")
        f.write(json.dumps(initials, ensure_ascii=False, indent=4))
        f.write("\n\nPINYIN_FULL = ")
        f.write(json.dumps(full, ensure_ascii=False, indent=4))
        f.write("\n")
    print(f"players             : {len(initials)}")
    print(f"sample p01          : {initials.get('p01')} / {full.get('p01')}")
    print(f"written             : {OUT_PATH}")


if __name__ == "__main__":
    main()
