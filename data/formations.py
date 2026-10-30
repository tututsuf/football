"""四套阵型的定义与中文注记。"""

# ----------------------------------------------------------------------
# Formation definitions (4 tactical shapes) — for the 阵型表现 view
# Each player has aggregate season stats per formation where they actually played.
# ----------------------------------------------------------------------
FORMATIONS = ["4-3-3", "4-4-2", "3-5-2", "4-2-3-1"]

FORMATION_NOTES = {
    "4-3-3":   "强调边路宽度与高压逼抢，适合有内切型边锋 + 控球型中场的球队。",
    "4-4-2":   "经典双链阵型，防守紧凑、反击直接，依赖双中锋抢点与边前卫套边。",
    "3-5-2":   "三中卫 + 翼卫前插提供宽度，中场中路密度大，适合控球与挤压对手。",
    "4-2-3-1": "双后腰保护 + 三前腰制造中路 overload，单前锋做支点，依赖前腰创造力。",
}

# 场上位置说明（每个位置缩写对应的职责一句话）
POSITION_DUTIES = {
    "GK":  "门将：唯一能在禁区内用手处理球的位置，是整条防线的最后一道屏障。",
    "CB":  "中后卫：防线的核心，负责盯人、出球和高空球争夺。",
    "LB":  "左后卫：既可防守也可压上助攻，是边路攻防转换的关键。",
    "RB":  "右后卫：同左后卫，负责右路攻防平衡。",
    "LWB": "左翼卫：比传统后卫更靠前、更靠近边线，兼具防守硬度和助攻能力。",
    "RWB": "右翼卫：同左翼卫，负责右路上下飞奔。",
    "CM":  "中路中场：攻防转换枢纽，需要覆盖面积大、技术全面。",
    "DM":  "后腰：专职防守的中场，在防线前建立一道屏障，也负责组织进攻。",
    "CAM": "前腰：埋伏在前锋身后创造机会，是球队进攻的灵感之源。",
    "LAM": "左边前腰：在左肋部活动，兼具前插和边路内切能力。",
    "RAM": "右边前腰：在右肋部活动，兼具前插和边路内切能力。",
    "LW":  "左边锋：主要活动在左路禁区前沿，擅长内切打门或传中。",
    "RW":  "右边锋：主要活动在右路禁区前沿，擅长内切打门或传中。",
    "ST":  "中锋：最接近对方球门的位置，承担进球的主要责任，也需要做支点。",
}

# 英文界面的位置职责说明（与 POSITION_DUTIES 一一对应）
POSITION_DUTIES_EN = {
    "GK":  "Goalkeeper: the only player allowed to handle the ball inside the box, and the last line of the defence.",
    "CB":  "Centre-back: the anchor of the back line, handling marking, distribution and aerial duels.",
    "LB":  "Left-back: defends the flank and overlaps to support attacks, key to transitions on the left.",
    "RB":  "Right-back: mirrors the left-back, balancing defence and attack down the right.",
    "LWB": "Left wing-back: pushed higher and wider than a full-back, combining defensive grit with delivery.",
    "RWB": "Right wing-back: same brief as the left wing-back, running the right touchline box to box.",
    "CM":  "Central midfielder: the engine of transition, covering ground with a well-rounded skill set.",
    "DM":  "Defensive midfielder: shields the back line and starts attacks from deep.",
    "CAM": "Attacking midfielder: operates behind the striker to create chances.",
    "LAM": "Left attacking midfielder: works the left half-space, arriving late or cutting inside.",
    "RAM": "Right attacking midfielder: works the right half-space, arriving late or cutting inside.",
    "LW":  "Left winger: lives near the left corner of the box, cutting inside to shoot or crossing.",
    "RW":  "Right winger: lives near the right corner of the box, cutting inside to shoot or crossing.",
    "ST":  "Striker: closest to goal, shouldering the scoring burden and linking play as a target.",
}

# 四套阵型的场上位置坐标（SVG-friendly）。
# 足球场纵向：门将在底部 (y 小)，前锋在顶部 (y 大)。
# x 从左到右 0-100，y 从底到顶 0-100。
FORMATION_POSITIONS = {
    "4-3-3": [
        {"id": "GK",  "x": 50, "y":  5, "role": "GK"},
        {"id": "LB",  "x": 18, "y": 25, "role": "LB"},
        {"id": "CB1", "x": 38, "y": 25, "role": "CB"},
        {"id": "CB2", "x": 62, "y": 25, "role": "CB"},
        {"id": "RB",  "x": 82, "y": 25, "role": "RB"},
        {"id": "CM1", "x": 30, "y": 60, "role": "CM"},
        {"id": "CM2", "x": 50, "y": 60, "role": "CM"},
        {"id": "CM3", "x": 70, "y": 60, "role": "CM"},
        {"id": "LW",  "x": 20, "y": 90, "role": "LW"},
        {"id": "ST",  "x": 50, "y": 92, "role": "ST"},
        {"id": "RW",  "x": 80, "y": 90, "role": "RW"},
    ],
    "4-4-2": [
        {"id": "GK",  "x": 50, "y":  5, "role": "GK"},
        {"id": "LB",  "x": 18, "y": 25, "role": "LB"},
        {"id": "CB1", "x": 38, "y": 25, "role": "CB"},
        {"id": "CB2", "x": 62, "y": 25, "role": "CB"},
        {"id": "RB",  "x": 82, "y": 25, "role": "RB"},
        {"id": "LW",  "x": 22, "y": 60, "role": "LW"},
        {"id": "CM1", "x": 40, "y": 60, "role": "CM"},
        {"id": "CM2", "x": 60, "y": 60, "role": "CM"},
        {"id": "RW",  "x": 78, "y": 60, "role": "RW"},
        {"id": "ST1", "x": 38, "y": 92, "role": "ST"},
        {"id": "ST2", "x": 62, "y": 92, "role": "ST"},
    ],
    "3-5-2": [
        {"id": "GK",  "x": 50, "y":  5, "role": "GK"},
        {"id": "CB1", "x": 30, "y": 25, "role": "CB"},
        {"id": "CB2", "x": 50, "y": 25, "role": "CB"},
        {"id": "CB3", "x": 70, "y": 25, "role": "CB"},
        {"id": "LWB", "x": 12, "y": 55, "role": "LWB"},
        {"id": "CM1", "x": 32, "y": 55, "role": "CM"},
        {"id": "CM2", "x": 50, "y": 55, "role": "CM"},
        {"id": "CM3", "x": 68, "y": 55, "role": "CM"},
        {"id": "RWB", "x": 88, "y": 55, "role": "RWB"},
        {"id": "ST1", "x": 38, "y": 92, "role": "ST"},
        {"id": "ST2", "x": 62, "y": 92, "role": "ST"},
    ],
    "4-2-3-1": [
        {"id": "GK",  "x": 50, "y":  5, "role": "GK"},
        {"id": "LB",  "x": 18, "y": 22, "role": "LB"},
        {"id": "CB1", "x": 38, "y": 22, "role": "CB"},
        {"id": "CB2", "x": 62, "y": 22, "role": "CB"},
        {"id": "RB",  "x": 82, "y": 22, "role": "RB"},
        {"id": "DM1", "x": 38, "y": 44, "role": "DM"},
        {"id": "DM2", "x": 62, "y": 44, "role": "DM"},
        {"id": "LAM", "x": 22, "y": 68, "role": "LAM"},
        {"id": "CAM", "x": 50, "y": 72, "role": "CAM"},
        {"id": "RAM", "x": 78, "y": 68, "role": "RAM"},
        {"id": "ST",  "x": 50, "y": 94, "role": "ST"},
    ],
}
