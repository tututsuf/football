"""生涯区间字符串解析（如 "2020-2023" / "2024-"）。"""

import re


def period_start(period):
    """Parse start year from period strings like '2020-2023' or '2024-'."""
    m = re.match(r"(\d{4})", period)
    return int(m.group(1)) if m else 0


def period_end(period):
    """Parse end year from '2020-2023' (->2023); return None for '2024-' (still active)."""
    m = re.match(r"\d{4}-(\d{4})", period)
    return int(m.group(1)) if m else None
