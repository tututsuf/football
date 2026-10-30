"""Football player dataset — 公共 API。

数据流：players.py（原始字面量）→ etl.py（加工）→ dataset.py（加载）→ accessors.py（查询）
Sources: Transfermarkt 身价历史 / 生涯记录；队徽来自 fclogo.top 与 Transfermarkt CDN。
"""

from .accessors import (formation_summary, photo_for, player_by_id,
                        player_club_associations, player_full, player_summary)
from .clubs import (CLUBS, LOGOS, club_by_id, club_id_for,
                    clubs_with_geo_and_signings, logo_for,
                    recent_signings_by_club)
from .dataset import PLAYERS
from .formations import (FORMATION_NOTES, FORMATION_POSITIONS,
                          FORMATIONS, POSITION_DUTIES, POSITION_DUTIES_EN)
from .i18n import (CITY_ZH, COUNTRY_ZH, FOOT_ZH, FORMATION_NOTES_EN, LEAGUE_ZH,
                   NATION_ZH, PLAYER_NAMES_ZH, POSITION_GROUP_ZH, POSITION_ZH,
                   STADIUM_ZH)
from .pinyin import PINYIN_FULL, PINYIN_INITIALS

__all__ = [
    "PLAYERS", "FORMATIONS", "FORMATION_NOTES", "FORMATION_NOTES_EN", "LOGOS",
    "CLUBS", "PLAYER_NAMES_ZH", "POSITION_ZH", "POSITION_GROUP_ZH", "NATION_ZH",
    "COUNTRY_ZH", "LEAGUE_ZH", "FOOT_ZH", "CITY_ZH", "STADIUM_ZH", "PINYIN_INITIALS", "PINYIN_FULL",
    "logo_for", "club_by_id", "club_id_for", "recent_signings_by_club",
    "clubs_with_geo_and_signings", "player_by_id", "photo_for",
    "player_summary", "player_full", "formation_summary",
    "player_club_associations",
]
