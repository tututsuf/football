# ⚽ 球员身价走势与阵型表现追踪 (Football Value Tracker)

一个自包含的足球球员数据可视化网站：追踪 **160 名球员** 的德转身价走势、职业生涯经历与阵型表现，覆盖 **156 家俱乐部**（含队徽与世界地图分布）。

中文 / English 双语界面 · 明暗双主题 · 无需构建步骤，Flask 直接跑。

## ✨ 功能特性

- **身价走势**：Transfermarkt 身价历史曲线，背景色带标注当时所属俱乐部，支持滚轮缩放与拖动时间轴；多球员折线叠加对比。
- **职业生涯**：逐俱乐部出场 / 进球 / 助攻明细，队徽标注转会节点；生涯数据总览、各俱乐部数据对比柱状图、俱乐部足迹时间线。
- **阵型表现**：四套主流阵型（4-3-3 / 4-4-2 / 4-2-3-1 / 3-5-2）下的出场、贡献与场均评分；SVG 球场站位图，点击阵型卡片查看球员位置与职责说明。
- **位置差异化指标**：门将按扑救 / 丢球统计，后卫按解围 / 拦截统计，其余位置按进球 / 助攻统计。
- **世界地图**：俱乐部地理分布与近年引援网络，悬停看队徽、点击查看转会详情，可按起始年份筛选。
- **数据明细页**：球员库 / 俱乐部库 / 引援台账 / 阵型报告四个全库明细页，支持搜索、筛选、排序。

## 🛠 技术栈

- **后端**：Python 3.10+ · Flask（单文件 `app.py`，数据经 ETL 预处理为静态结构）
- **前端**：Vue 3（CDN，无构建）· ECharts（自托管 + SRI 校验）· 原生 CSS 变量主题
- **数据**：`data/` 目录内手工整理 + ETL 处理的 Python 数据集

## 🚀 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/tututsuf/football.git
cd football

# 2. 安装依赖（建议先建虚拟环境）
pip install -r requirements.txt

# 3. 启动
python app.py
```

浏览器打开 <http://127.0.0.1:5000> 即可。

## 📁 项目结构

```
football/
├── app.py              # Flask 入口 + 全部 API 路由
├── requirements.txt    # 仅 flask / flask-cors
├── data/               # 数据集与访问层
│   ├── players.py      # 球员主数据（身价历史、生涯经历）
│   ├── clubs.py        # 俱乐部元数据（地理、联赛、队徽）
│   ├── formations.py   # 阵型定义与站位坐标
│   ├── accessors.py    # 数据访问与序列化
│   └── etl.py          # 原始数据 → 静态结构的 ETL
├── templates/          # 前端三件套（index.html / app.js / styles.css）
│   └── vendor/         # 自托管的 Vue / ECharts（含 SRI）
└── scripts/, tools/    # 数据补全与校验脚本
```

## ⚠️ 数据来源与免责声明

- 身价与生涯数据整理自 [Transfermarkt](https://www.transfermarkt.com)，队徽图片来自第三方公开 CDN（SportsAPI Pro / Transfermarkt / fclogo.top）。
- 阵型拆分数据为**估算值**（按生涯总量分摊或按位置基准推算），仅用于横向比较相对倾向，非逐场实录。
- 本项目**仅供学习与演示用途**，数据版权归原始来源方所有，请勿用于商业用途。如涉侵权请联系删除。

## 📄 License

代码部分以 [MIT License](LICENSE) 开源；数据与队徽图片的版权见上方免责声明。
