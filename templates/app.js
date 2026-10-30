/* 球员身价走势与阵型表现追踪 —— Vue 3 应用逻辑（由 index.html 抽离）
   依赖全局 Vue / echarts（CDN 引入），无需构建步骤。 */

const { createApp, ref, computed, onMounted, onUnmounted, nextTick, watch } = Vue;

// 后端数据来自静态文件，但 tooltip 会拼 HTML，统一转义以防将来接入用户输入时出现 XSS
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

createApp({
  setup() {
    // ---- 语言：zh / en，默认中文，选择持久化 ----
    const lang = ref("zh");
    try { if (localStorage.getItem("fv-lang") === "en") lang.value = "en"; } catch (e) {}
    const T = {
      zh: {
        docTitle: "球员身价走势与阵型表现追踪 · fclogo.top 风格",
        brand: "足球身价追踪",
        navAria: "数据视图",
        langBtn: "EN", langAria: "切换为 English",
        themeLight: "浅色", themeDark: "深色",
        themeAriaToLight: "切换到浅色模式", themeAriaToDark: "切换到深色模式",
        source: "数据来源：Transfermarkt · fclogo.top",
        viewDetail: "查看明细 ›",
        statPlayers: "追踪球员", statClubs: "收录俱乐部", statSignings: "近年引援", statFormations: "阵型对比",
        statPlayersAria: "查看 {n} 名追踪球员明细",
        statClubsAria: "查看 {n} 家收录俱乐部明细",
        statSigningsAria: "查看 {n} 笔近年引援明细",
        statFormationsAria: "查看 {n} 套阵型对比明细",
        loadingData: "正在加载球员与阵型数据…",
        retry: "重试",
        loadFailed: "数据加载失败：{e}",
        playerLoadFailed: "球员 {id} 的数据加载失败：{e}",
        formationLoadFailed: "阵型聚合数据加载失败：{e}",
        rosterTitle: "球员名册 · 每批 {n} 人",
        rosterPaused: "已选中球员 · 自动轮播已暂停，点「换一批」恢复",
        rosterAuto: "每 5 秒自动换一批 · 悬停暂停",
        searchHits: "搜索到 {n} 名球员",
        filterHits: "筛选后 {n} 名",
        searchPlaceholder: "搜索球员 / 俱乐部 / 位置…",
        searchAria: "搜索球员、俱乐部或位置",
        filterPosAria: "按位置筛选",
        allPositions: "全部位置",
        posFW: "前锋", posMF: "中场", posDF: "后卫", posGK: "门将",
        filterLeagueAria: "按联赛筛选",
        allLeagues: "全部联赛",
        sortAria: "排序方式",
        sortRandom: "随机展示", sortValue: "身价从高到低", sortAge: "年龄从小到大", sortName: "姓名 A-Z",
        clear: "清除", shuffle: "换一批",
        viewPlayerAria: "查看 {name} 的身价与生涯",
        noMore: "该筛选条件下暂无更多球员",
        emptyFiltered: "当前筛选条件下没有球员",
        noMatch: "没有匹配的球员",
        flipBack: "点击翻回",
        pos: "位置", age: "年龄", nationality: "国籍", foot: "惯用脚",
        currentValue: "当前身价", peakValue: "历史峰值",
        noFormationData: "⚠ 阵型数据待补充",
        currentView: "当前视图",
        trendTitle: "德转身价走势 · {name} ({n} 个采样点)",
        zoomHint: "滚轮缩放 · 拖动滑块",
        trendLegendX: "横轴：日期 (Transfermarkt 更新快照)",
        trendLegendY: "纵轴：市场估值 (€M)",
        trendLegendBand: "背景色块 = 当时所属俱乐部",
        trendLegendZoom: "横轴可滚轮缩放 / 拖动下方滑块拉伸时间轴",
        trendLegendEst: "灰点 = 回填估值（非当期快照）",
        dataAsOf: "数据截至",
        dataSourceSnapshot: "来源：Transfermarkt 身价快照（2021 年起为逐次更新记录，更早为关键节点抽样）",
        compareTitle: "多球员身价对比 (折线叠加)",
        careerTitle: "职业生涯经历 · 队徽标注 (fclogo.top)",
        thPeriod: "时期", thClub: "俱乐部", thLeague: "联赛",
        thApps: "出场", thGoals: "进球", thAssists: "助攻", thContribution: "场均造球",
        careerTrendTitle: "身价走势 · 单一曲线 (背景带标注所属俱乐部)",
        careerTimelineAria: "职业生涯俱乐部时间线",
        ctTitle: "生涯数据总览", ctApps: "总出场", ctClubs: "效力俱乐部", ctSpan: "生涯跨度", tlTitle: "俱乐部足迹",
        formationTitle: "不同阵型中的表现水平 · {name}",
        formationCard: "{f} 阵型",
        avgRating: "场均评分",
        formationCardMeta: "出场 {apps} · 进球 {goals} · 助攻 {assists}",
        pitchAria: "{f} 阵型站位图，高亮 {g} 位置",
        pitchLegend: "点上方阵型卡片切换站位 · 高亮 = 该球员所属的 {g} 位置组",
        formationNoteDisclaimer: "说明：四种阵型的出场与贡献数据为估算值（有生涯统计者按生涯总量分摊，其余按生涯跨度与位置基准推算）；门将用扑救/丢球、后卫用解围/拦截衡量。仅用于横向比较相对倾向，非逐场实录；场均评分按出场加权。",
        formationNoData: "该球员暂无按阵型拆分的统计数据（为避免误导，未对其做估算）；站位图仍可参考其位置组。",
        formationChartTitle: "各阵型进球 / 助攻 / 评分对比",
        efficiencyTitle: "阵型效率 (场均造球)",
        mapYearLabel: "引援起始年份",
        mapStat: "共 {clubs} 家俱乐部 · {signings} 笔近年引援 · 悬停看队徽 · 点击查看转会",
        rankSub: "共 {clubs} 家收录俱乐部 · {signings} 笔 {year} 年以来引援",
        signingsShort: "引援",
        mapTitle: "世界俱乐部分布与近年引援网络",
        mapLegendDot: "蓝点 = 俱乐部位置",
        mapLegendHover: "悬停蓝点 → 显示队徽 + 信息",
        mapLegendClick: "点击蓝点 → 查看转会详情",
        mapLegendBig: "大蓝点 = 有近年引援",
        selectedClubSignings: "选中俱乐部 · 近年引援",
        signingsCountInline: "引援 {n} 笔",
        mapEmpty: "悬停蓝点查看队徽",
        mapEmpty2: "点击蓝点查看该俱乐部近年引援详情",
        back: "← 返回", closeAria: "关闭详情页",
        backHome: "← 返回首页", backHomeAria: "关闭详情页，返回首页",
        backToTop: "回到顶部", backToTopAria: "回到页面顶部",
        dpKicker: "球员数据库", dpTitle: "追踪球员全库", dpMetric: "{n} 名",
        dpSub: "可按位置与联赛筛选、按身价/年龄/姓名排序；点击任意球员进入其详情页。",
        dcKicker: "俱乐部数据库", dcTitle: "收录俱乐部总览", dcMetric: "{n} 家",
        dcSub: "地理与联赛信息手工整理自维基百科与俱乐部官方资料；点击任意俱乐部跳到世界地图定位。",
        dsKicker: "转会台账", dsTitle: "近年引援明细", dsMetric: "{n} 笔",
        dsSub: "由球员生涯记录推导的转入记录（2020 年起，可在世界地图页切换起始年份）；点击可查看球员详情。",
        dfKicker: "阵型报告", dfTitle: "阵型对比总览", dfMetric: "{n} 套",
        dfSub: "四套主流阵型的估算/分摊累计数据聚合；点击阵型卡片查看参与球员明细。",
        dSearchPlaceholder: "搜索球员 / 俱乐部 / 国籍…",
        dSortValue: "按身价", dSortAge: "按年龄", dSortName: "按姓名",
        dCount: "命中 {a} / {b} 名",
        kAvgAge: "平均年龄", kValueSum: "身价合计", kTopValue: "最高身价", kLeagues: "覆盖联赛",
        ageUnit: "{n} 岁",
        dNoPlayers: "没有符合条件的球员，试试放宽筛选条件。",
        cSearchPlaceholder: "搜索俱乐部 / 城市 / 国家…",
        allCountries: "全部国家",
        cSortSignings: "按引援数", cSortName: "按名称",
        cCount: "命中 {a} / {b} 家",
        kCountries: "国家 / 地区", kWithSignings: "有近年引援", kAvgSignings: "平均引援", kMostSignings: "引援最多",
        clubCountUnit: "{n} 家", signingsCountUnit: "{n} 笔",
        mapView: "地图查看 ›",
        dNoClubs: "没有符合条件的俱乐部。",
        sSearchPlaceholder: "搜索球员 / 俱乐部…",
        allYears: "全部年份",
        yearFrom: "{y} 年起",
        sCount: "命中 {a} / {b} 笔",
        kTotalSignings: "引援总笔数", kClubsInvolved: "涉及俱乐部",
        kSigningValueSum: "引援球员身价合计", kTopSigning: "最高身价引援",
        thPlayer: "球员", thToClub: "转入俱乐部", thFromClub: "原俱乐部", thPosition: "位置", thCurrentValue: "当前身价",
        dNoSignings: "没有符合条件的引援记录。",
        kFormationCount: "阵型数量", kFormationPlayers: "有阵型数据的球员",
        kFormationApps: "阵型出场合计", kFormationContrib: "阵型造球合计",
        playerCountUnit: "{n} 名",
        fCardMeta: "{n} 名球员 · 场均评分 {r}",
        fApps: "出场", fGoals: "进球", fAssists: "助攻", fContrib: "造球",
        fOpen: "点击查看该阵型的参与球员 ›",
        formationLoading: "正在加载阵型聚合数据…",
        fContributors: "{f} 阵型 · 参与球员明细",
        viewInFormation: "在阵型页查看 ›",
        rating: "评分 {r}",
        appsUnit: "{n} 场",
        goalsAssists: "{g}球 / {a}助",
        formationDisclaimer: "说明：仅统计已录入阵型分摊数据的球员；从 Transfermarkt 新增的球员暂无阵型拆分数据，不计入合计。",
        chartPeak: "峰值", chartTrough: "谷值", chartValue: "身价", chartClubThen: "当时俱乐部",
        chartTransfer: "转会", chartValueAt: "该时点身价", chartEst: "（估值）",
        chartTransferInferred: "（按相邻身价快照推断）",
        chartNoFormation: "暂无阵型表现数据", chartNoEfficiency: "暂无阵型效率数据",
        chartGoalsAssistsAxis: "进球 / 助攻", chartAvgRatingAxis: "场均评分",
        chartGoals: "进球", chartAssists: "助攻", chartPer90: "场均造球",
        chartClubsSeries: "俱乐部", chartSigningsInline: "近年引援: {n} 笔",
        careerSeries: "身价走势",
        tabs: {
          trend: { label: "身价走势", kicker: "身价时间轴", headline: "身价起伏，一目了然", tagline: "德转身价历史曲线 · 背景色带标注当时所属俱乐部 · 横轴可缩放拖拽", desc: "德转身价历史曲线，背景色块标注当时所属俱乐部" },
          career: { label: "职业生涯", kicker: "生涯轨迹", headline: "逐站回看，每段旅程", tagline: "按俱乐部逐段梳理出场 / 进球 / 助攻 · 队徽标注转会节点 · 单一曲线看身价轨迹", desc: "逐俱乐部出场/进球/助攻，队徽标注转会节点" },
          formation: { label: "阵型表现", kicker: "战术适配", headline: "换阵型，换一种活法", tagline: "四套主流阵型下的赛季累计数据 · 场均评分与场均造球效率对比", desc: "四套战术下赛季累计数据与效率对比" },
          map: { label: "世界地图", kicker: "全球转会网络", headline: "球员流动，画在地图上", tagline: "俱乐部地理位置与近年引援网络 · 悬停看队徽 · 点击查看该队引援详情", desc: "俱乐部地理位置与近年引援网络，悬停看队徽、点查看转会" },
        },
      },
      en: {
        docTitle: "Player Market Value & Formation Performance Tracker · fclogo.top style",
        brand: "Football Value Tracker",
        navAria: "Data views",
        langBtn: "中文", langAria: "切换为中文",
        themeLight: "Light", themeDark: "Dark",
        themeAriaToLight: "Switch to light mode", themeAriaToDark: "Switch to dark mode",
        source: "Source: Transfermarkt · fclogo.top",
        viewDetail: "Details ›",
        statPlayers: "Tracked players", statClubs: "Clubs", statSignings: "Recent signings", statFormations: "Formations",
        statPlayersAria: "View details for {n} tracked players",
        statClubsAria: "View details for {n} clubs",
        statSigningsAria: "View details for {n} recent signings",
        statFormationsAria: "View details for {n} formations",
        loadingData: "Loading players and formations…",
        retry: "Retry",
        loadFailed: "Failed to load data: {e}",
        playerLoadFailed: "Failed to load player {id}: {e}",
        formationLoadFailed: "Failed to load formation summary: {e}",
        rosterTitle: "Player roster · {n} per batch",
        rosterPaused: "Player selected · autoplay paused. Click “Next batch” to resume.",
        rosterAuto: "New batch every 5s · pauses on hover",
        searchHits: "Found {n} players",
        filterHits: "{n} after filtering",
        searchPlaceholder: "Search player / club / position…",
        searchAria: "Search players, clubs or positions",
        filterPosAria: "Filter by position",
        allPositions: "All positions",
        posFW: "Forwards", posMF: "Midfielders", posDF: "Defenders", posGK: "Goalkeepers",
        filterLeagueAria: "Filter by league",
        allLeagues: "All leagues",
        sortAria: "Sort order",
        sortRandom: "Random", sortValue: "Value: high to low", sortAge: "Age: youngest first", sortName: "Name A-Z",
        clear: "Clear", shuffle: "Next batch",
        viewPlayerAria: "View {name}'s value and career",
        noMore: "No more players for this filter",
        emptyFiltered: "No players match the current filters",
        noMatch: "No matching players",
        flipBack: "Click to flip back",
        pos: "Position", age: "Age", nationality: "Nationality", foot: "Preferred foot",
        currentValue: "Current value", peakValue: "Career peak",
        noFormationData: "⚠ Formation data pending",
        currentView: "Current view",
        trendTitle: "Transfermarkt value history · {name} ({n} samples)",
        zoomHint: "Scroll to zoom · drag slider",
        trendLegendX: "X axis: date (Transfermarkt snapshots)",
        trendLegendY: "Y axis: market value (€M)",
        trendLegendBand: "Background band = club at the time",
        trendLegendZoom: "Scroll to zoom / drag the slider below to stretch the timeline",
        trendLegendEst: "Grey dots = back-filled estimates (not snapshots)",
        dataAsOf: "Data as of",
        dataSourceSnapshot: "Source: Transfermarkt value snapshots (per-update records from 2021; key snapshots for earlier years)",
        compareTitle: "Player value comparison (overlaid lines)",
        careerTitle: "Career history · club crests (fclogo.top)",
        thPeriod: "Period", thClub: "Club", thLeague: "League",
        thApps: "Apps", thGoals: "Goals", thAssists: "Assists", thContribution: "G+A / match",
        careerTrendTitle: "Value trajectory · single line (background bands mark clubs)",
        careerTimelineAria: "Career club timeline",
        ctTitle: "Career Overview", ctApps: "Total Apps", ctClubs: "Clubs", ctSpan: "Career Span", tlTitle: "Club Journey",
        formationTitle: "Performance by formation · {name}",
        formationCard: "{f} formation",
        avgRating: "Average rating",
        formationCardMeta: "Apps {apps} · Goals {goals} · Assists {assists}",
        pitchAria: "{f} formation layout, highlighting the {g} position",
        pitchLegend: "Tap a formation card above to switch layout · highlight = this player's {g} group",
        formationNoteDisclaimer: "Note: apps and contribution figures for the four formations are estimates (career totals apportioned where available; otherwise inferred from career span and positional baselines). Goalkeepers are measured by saves/conceded, defenders by clearances/interceptions. For relative comparison only, not match-by-match records; average rating is weighted by appearances.",
        formationNoData: "No formation-split statistics are available for this player (no estimate is shown to avoid misleading figures); the layout still reflects their position group.",
        formationChartTitle: "Goals / assists / rating by formation",
        efficiencyTitle: "Formation efficiency (goal contributions per game)",
        mapYearLabel: "Signings from",
        mapStat: "{clubs} clubs · {signings} recent signings · hover for crests · click for transfers",
        rankSub: "{clubs} clubs tracked · {signings} signings since {year}",
        signingsShort: "Signings",
        mapTitle: "Global club map and recent signing network",
        mapLegendDot: "Blue dot = club location",
        mapLegendHover: "Hover a dot → crest + info",
        mapLegendClick: "Click a dot → transfer details",
        mapLegendBig: "Larger dot = recent signings",
        selectedClubSignings: "Selected club · recent signings",
        signingsCountInline: "{n} signings",
        mapEmpty: "Hover a blue dot to see its crest",
        mapEmpty2: "Click a blue dot to see the club's recent signings",
        back: "← Back", closeAria: "Close details",
        backHome: "← Back to home", backHomeAria: "Close details and return home",
        backToTop: "Top", backToTopAria: "Back to top of page",
        dpKicker: "Player Database", dpTitle: "All tracked players", dpMetric: "{n} players",
        dpSub: "Filter by position and league, sort by value/age/name; click any player for their detail page.",
        dcKicker: "Club Database", dcTitle: "All clubs", dcMetric: "{n} clubs",
        dcSub: "Geography and league data curated from Wikipedia and official club sources; click a club to locate it on the world map.",
        dsKicker: "Transfer Ledger", dsTitle: "Recent signings", dsMetric: "{n} signings",
        dsSub: "Incoming transfers derived from career records (from 2020; change the start year on the World Map tab); click to open a player.",
        dfKicker: "Formation Report", dfTitle: "Formation overview", dfMetric: "{n} formations",
        dfSub: "Apportioned career totals across four mainstream formations; click a formation card to see contributing players.",
        dSearchPlaceholder: "Search player / club / nationality…",
        dSortValue: "By value", dSortAge: "By age", dSortName: "By name",
        dCount: "Showing {a} / {b} players",
        kAvgAge: "Average age", kValueSum: "Total value", kTopValue: "Most valuable", kLeagues: "Leagues covered",
        ageUnit: "{n} yrs",
        dNoPlayers: "No players match these filters. Try widening them.",
        cSearchPlaceholder: "Search club / city / country…",
        allCountries: "All countries",
        cSortSignings: "By signings", cSortName: "By name",
        cCount: "Showing {a} / {b} clubs",
        kCountries: "Countries / regions", kWithSignings: "With recent signings", kAvgSignings: "Average signings", kMostSignings: "Most signings",
        clubCountUnit: "{n} clubs", signingsCountUnit: "{n} signings",
        mapView: "View on map ›",
        dNoClubs: "No clubs match these filters.",
        sSearchPlaceholder: "Search player / club…",
        allYears: "All years",
        yearFrom: "From {y}",
        sCount: "Showing {a} / {b} signings",
        kTotalSignings: "Total signings", kClubsInvolved: "Clubs involved",
        kSigningValueSum: "Signings' current value", kTopSigning: "Most valuable signing",
        thPlayer: "Player", thToClub: "Joined", thFromClub: "From", thPosition: "Position", thCurrentValue: "Current value",
        dNoSignings: "No signings match these filters.",
        kFormationCount: "Formations", kFormationPlayers: "Players with data",
        kFormationApps: "Total appearances", kFormationContrib: "Total goal contributions",
        playerCountUnit: "{n} players",
        fCardMeta: "{n} players · avg rating {r}",
        fApps: "Apps", fGoals: "Goals", fAssists: "Assists", fContrib: "G+A",
        fOpen: "View the players in this formation ›",
        formationLoading: "Loading formation summary…",
        fContributors: "{f} formation · contributing players",
        viewInFormation: "Open in formations ›",
        rating: "Rating {r}",
        appsUnit: "{n} apps",
        goalsAssists: "{g}G / {a}A",
        formationDisclaimer: "Note: only players with apportioned formation data are counted; players added from Transfermarkt without formation splits are excluded from totals.",
        chartPeak: "Peak", chartTrough: "Low", chartValue: "Value", chartClubThen: "Club at the time",
        chartTransfer: "Transfer", chartValueAt: "Value at this point", chartEst: "(est.)",
        chartTransferInferred: "(inferred from adjacent value snapshots)",
        chartNoFormation: "No formation performance data", chartNoEfficiency: "No formation efficiency data",
        chartGoalsAssistsAxis: "Goals / assists", chartAvgRatingAxis: "Average rating",
        chartGoals: "Goals", chartAssists: "Assists", chartPer90: "Goal contributions per game",
        chartClubsSeries: "Clubs", chartSigningsInline: "Recent signings: {n}",
        careerSeries: "Value trajectory",
        tabs: {
          trend: { label: "Value Trend", kicker: "Market Value Timeline", headline: "Every rise and fall, at a glance", tagline: "Transfermarkt value history · background bands mark the club at the time · zoom and pan the time axis", desc: "Transfermarkt value history with club bands" },
          career: { label: "Career", kicker: "Career Path", headline: "Every stop, every chapter", tagline: "Club-by-club apps / goals / assists · crests mark transfer points · one line for the value trajectory", desc: "Apps/goals/assists per club, crests mark transfers" },
          formation: { label: "Formations", kicker: "Tactical Fit", headline: "Change shape, change the game", tagline: "Season totals across four mainstream formations · average rating and goal contribution per game", desc: "Season totals and efficiency across four formations" },
          map: { label: "World Map", kicker: "Global Transfer Network", headline: "Player movement, drawn on the map", tagline: "Club locations and recent signing networks · hover for crests · click for transfer details", desc: "Club locations and signing network · hover for crests, click for transfers" },
        },
      },
    };
    const L = computed(() => T[lang.value]);
    const tf = (s, vars) => String(s == null ? "" : s).replace(/\{(\w+)\}/g, (m, k) => (vars && vars[k] != null ? vars[k] : m));
    function applyLang() {
      document.documentElement.lang = lang.value === "zh" ? "zh-CN" : "en";
      document.title = T[lang.value].docTitle;
    }
    applyLang();
    function toggleLang() {
      lang.value = lang.value === "zh" ? "en" : "zh";
      try { localStorage.setItem("fv-lang", lang.value); } catch (e) {}
      applyLang();
      // ECharts 的文字在 canvas 内，必须重绘；HTML 时间线由 computed 自动更新
      nextTick(() => { renderAllCharts(); });
    }

    // 每个标签一套独立视觉主题：配色 / 渐变 / 图标 / 文案，切换时整页换色
    const baseTabs = [
      { key: "trend", icon: "↗", accent: "#4f46e5", shadow: "rgba(79,70,229,.32)", wash: "linear-gradient(180deg,#eef2ff 0%,#f7f8ff 420px,#ffffff 100%)", washStrong: "rgba(79,70,229,.11)", metric: "€M" },
      { key: "career", icon: "⌁", accent: "#0f766e", shadow: "rgba(15,118,110,.30)", wash: "linear-gradient(180deg,#ecfdf5 0%,#f4fdfa 420px,#ffffff 100%)", washStrong: "rgba(15,118,110,.11)", metric: "→" },
      { key: "formation", icon: "▦", accent: "#b45309", shadow: "rgba(180,83,9,.30)", wash: "linear-gradient(180deg,#fffbeb 0%,#fffdf5 420px,#ffffff 100%)", washStrong: "rgba(180,83,9,.12)", metric: "×4" },
      { key: "map", icon: "◉", accent: "#334155", shadow: "rgba(51,65,85,.30)", wash: "linear-gradient(180deg,#f1f5f9 0%,#f8fafc 420px,#ffffff 100%)", washStrong: "rgba(51,65,85,.12)", metric: "—" },
    ];
    const tabs = computed(() => baseTabs.map(t => ({ ...t, ...L.value.tabs[t.key] })));
    const activeTab = ref("trend");

    // ---- 深色模式：切换 <html data-theme>，组件与图表同步换色 ----
    const isDark = ref(false);
    try { isDark.value = localStorage.getItem("fv-theme") === "dark"; } catch (e) {}
    function applyTheme() { document.documentElement.dataset.theme = isDark.value ? "dark" : "light"; }
    applyTheme();
    const DARK_ACCENT = { trend: "#a5b4fc", career: "#5eead4", formation: "#fcd34d", map: "#cbd5e1" };
    const theme = computed(() => {
      const t = tabs.value.find(t => t.key === activeTab.value) || tabs.value[0];
      // 地图 Tab 的指标数 = 实际收录俱乐部数，避免硬编码过期值（未加载完成时显示占位符）
      const metric = t.key === "map" ? (clubs.value.length ? String(clubs.value.length) : "—") : t.metric;
      const base = { ...t, metric };
      if (!isDark.value) return base;
      return {
        ...base,
        accent: DARK_ACCENT[t.key] || t.accent,
        wash: "linear-gradient(180deg, rgba(255,255,255,.05) 0%, #0e1117 420px, #0e1117 100%)",
        washStrong: "rgba(255,255,255,.08)",
      };
    });
    // 图表通用的轴/文字/浮层配色（深色下网格与刻度用足对比度，避免"看不见的线"）
    const ink = () => isDark.value
      ? { axis: "#5b6577", label: "#b6bdc9", split: "#2b3444", text: "#e6e8ee", bg: "#151a22", border: "#3a4354" }
      : { axis: "#999999", label: "#666666", split: "#eeeeee", text: "#333333", bg: "#ffffff", border: "#cccccc" };
    function toggleTheme() {
      isDark.value = !isDark.value;
      try { localStorage.setItem("fv-theme", isDark.value ? "dark" : "light"); } catch (e) {}
      applyTheme();
      nextTick(() => { renderAllCharts(); });
    }

    const players = ref([]);
    const current = ref(null);
    const loading = ref(true);
    const loadError = ref("");
    const formations = ref([]);
    const formationNotes = ref({});
    const formationNotesEn = ref({});
    const formationPositions = ref({});
    const positionDuties = ref({});
    const positionDutiesEn = ref({});
    const pitchSelectedRole = ref("");
    const i18n = ref({ positions: {}, position_groups: {}, nations: {}, countries: {}, leagues: {}, feet: {} });
    // 中文名的拼音索引（/api/search-index）：支持 "mbp" / "mubapei" 这类输入
    const pyIndex = ref({});
    const pyFull = ref({});
    const currentFormation = ref("4-3-3");
    const compareIds = ref([]);

    // ---- 双语名称工具：zh 优先返回 *_zh，en 返回 Transfermarkt 原名 ----
    const playersById = computed(() => {
      const m = {};
      players.value.forEach(p => { m[p.id] = p; });
      return m;
    });
    function nm(p) {
      if (!p) return "";
      if (lang.value === "en") return p.name || "";
      const full = p.name_zh || (p.id && playersById.value[p.id] && playersById.value[p.id].name_zh);
      return full || p.name || "";
    }
    function playerName(s) {
      if (!s) return "";
      if (lang.value === "en") return s.player_name || "";
      const full = s.player_name_zh || (s.player_id && playersById.value[s.player_id] && playersById.value[s.player_id].name_zh);
      return full || s.player_name || "";
    }
    function clubNm(name, clubZh) {
      if (lang.value === "zh") return clubZh || name || "";
      const n = name || "";
      // 数据集里的青训标记在中文字段中是「(青训 / 学徒)」，英文模式需要本地化
      if (/^[（(]\s*青训/.test(n)) return "(Youth / Academy)";
      return n;
    }
    function posNm(raw, zh) { return lang.value === "zh" ? (zh || i18n.value.positions?.[raw] || raw || "") : (raw || ""); }
    function leagueNm(raw, zh) { return lang.value === "zh" ? (zh || i18n.value.leagues?.[raw] || raw || "") : (raw || ""); }
    function countryNm(raw, zh) { return lang.value === "zh" ? (zh || i18n.value.countries?.[raw] || raw || "") : (raw || ""); }
    function cityNm(raw, zh) { return lang.value === "zh" ? (zh || i18n.value.cities?.[raw] || raw || "") : (raw || ""); }
    function stadiumNm(raw) { return lang.value === "zh" ? (i18n.value.stadiums?.[raw] || raw || "") : (raw || ""); }
    function natNm(raw, zh) { return lang.value === "zh" ? (zh || i18n.value.nations?.[raw] || raw || "") : (raw || ""); }
    function footNm(raw, zh) { return lang.value === "zh" ? (zh || i18n.value.feet?.[raw] || raw || "") : (raw || ""); }
    function pgNm(raw, zh) { return lang.value === "zh" ? (zh || i18n.value.position_groups?.[raw] || raw || "") : (raw || ""); }
    function clubNmOfPlayer(p) {
      const src = (p && p.id && playersById.value[p.id]) || p || {};
      return clubNm(src.current_club, src.club_zh);
    }
    const currentName = computed(() => nm(current.value));
    watch(current, (p) => {
      if (!p) return;
      const rest = compareIds.value.filter(id => id !== p.id);
      compareIds.value = [p.id, ...rest].slice(0, 6);
    });

    // ---- 名册轮播：每批 8 人、俱乐部互不重复 ----
    const roster = ref([]);
    const batchSeq = ref(0);          // 每次换批 +1，用于让 8 张卡片重新挂载并播放淡入
    const cardState = ref({}); // { p01: 'idle-front' | 'idle-back' | 'flipping' | 'unflipping' }
    const flipToken = ref({});  // 每次翻转 +1，触发 rc-inner 重挂载让 animation 从头播放
    const rosterPaused = ref(false);
    const autoPaused = ref(false);   // 用户主动选中球员后暂停自动轮播
    const searchQuery = ref("");
    let rotorTimer = null;

    // ---- 名册筛选 / 排序 ----
    const filterPos = ref("");
    const filterLeague = ref("");
    const sortBy = ref("random");
    const leagueOptions = computed(() => [...new Set(players.value.map(p => p.league).filter(Boolean))].sort());
    const filteredPlayers = computed(() => {
      let arr = players.value.filter(p =>
        (!filterPos.value || p.position_group === filterPos.value) &&
        (!filterLeague.value || p.league === filterLeague.value));
      if (sortBy.value === "value") arr = [...arr].sort((a, b) => (b.current_value_m_eur || 0) - (a.current_value_m_eur || 0));
      else if (sortBy.value === "age") arr = [...arr].sort((a, b) => a.age - b.age);
      else if (sortBy.value === "name") arr = [...arr].sort((a, b) => a.name.localeCompare(b.name));
      return arr;
    });
    function onFilterChange() {
      autoPaused.value = false;
      shuffleRoster();
    }

    // ---- 导出：图表 PNG / 表格 CSV ----
    function renderAllCharts() {
      if (current.value) { renderTrend(); renderFormation(); renderEfficiency(); }
      renderCompare();
      if (activeTab.value === "career") renderClubBar();
      if (activeTab.value === "map" && clubs.value.length) renderMap();
    }
    // 文件名 slug：避免 é/ñ 等字符在部分浏览器下载时乱码
    function slugify(s) {
      // NFD 后去掉组合音符（U+0300–U+036F），再转连字符
      return (s || "chart").normalize("NFD").replace(/[̀-ͯ]/g, "")
        .replace(/[^a-zA-Z0-9]+/g, "-").replace(/^-+|-+$/g, "").toLowerCase() || "chart";
    }
    // 队徽加载失败兜底：换成首字母 SVG 占位，避免浏览器默认破图图标（CDN 失效时很显眼）
    function onLogoError(e, label) {
      const el = e.target;
      if (el.dataset.failed) return;
      el.dataset.failed = "1";
      const ch = ((label || "?").trim().charAt(0) || "?")
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">`
        + `<rect width="64" height="64" rx="14" fill="#e9edf2"/>`
        + `<text x="32" y="43" font-size="28" font-family="system-ui,sans-serif" font-weight="600"`
        + ` fill="#8b95a1" text-anchor="middle">${ch}</text></svg>`;
      el.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
    }
    function exportChart(key) {
      const c = instances[key];
      if (!c) return;
      const a = document.createElement("a");
      a.href = c.getDataURL({ type: "png", pixelRatio: 2, backgroundColor: ink().bg });
      a.download = `${slugify(current.value?.name)}-${key}.png`;
      a.click();
    }
    function exportCSV(kind) {
      if (!current.value) return;
      let header, rows;
      const mk = metricKeys();
      if (kind === "career") {
        header = ["period", "club", "league", "apps", mk.k1, mk.k2];
        rows = current.value.career_history.map(c => [c.period, c.club, c.league, c.apps, c[mk.k1], c[mk.k2]]);
      } else {
        header = ["formation", "apps", mk.k1, mk.k2, "avg_rating"];
        rows = formations.value.map(f => {
          const v = formationPerf(f) || {};
          return [f, v.apps || 0, v[mk.k1] || 0, v[mk.k2] || 0, v.avg_rating || ""];
        });
      }
      const csv = "﻿" + [header, ...rows]
        .map(r => r.map(v => `"${v == null ? "" : String(v).replace(/"/g, '""')}"`).join(","))
        .join("\r\n");
      const a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
      a.download = `${slugify(current.value.name)}-${kind}.csv`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    }

    // 每批卡片数：桌面 8（2 列 × 4 行），窄屏 4（单列，避免首屏被名册占满）
    function batchSize() { return window.innerWidth < 640 ? 4 : 8; }
    // 每个俱乐部随机取一名球员，再抽出一批不同俱乐部 → 保证同批不重复
    function pickBatch() {
      const pool = filteredPlayers.value;
      const size = batchSize();
      // 排序模式下取「排序后的前 N 家不同俱乐部」，让排序结果真正可见
      if (sortBy.value !== "random") {
        const seen = new Set(), out = [];
        for (const p of pool) {
          if (seen.has(p.current_club)) continue;
          seen.add(p.current_club); out.push(p);
          if (out.length === size) break;
        }
        return out;
      }
      const byClub = {};
      for (const p of pool) {
        (byClub[p.current_club] = byClub[p.current_club] || []).push(p);
      }
      const clubNames = Object.keys(byClub);
      for (let i = clubNames.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [clubNames[i], clubNames[j]] = [clubNames[j], clubNames[i]];
      }
      return clubNames.slice(0, size).map(c => {
        const arr = byClub[c];
        return arr[Math.floor(Math.random() * arr.length)];
      });
    }

    function shuffleRoster() {
      const size = batchSize();
      const next = pickBatch();
      // 尽量避开和上一批完全相同的球员
      const prevIds = new Set(roster.value.map(p => p.id));
      let batch = (next.length === size && next.every(p => prevIds.has(p.id)) && players.value.length > size * 2)
        ? pickBatch()
        : next;
      // 筛选结果不足一批时补占位卡，保持网格卡片数恒定、布局不塌（空结果交给 empty-state）
      while (batch.length && batch.length < size) batch = [...batch, { id: `__ph${batch.length}`, __placeholder: true }];
      roster.value = batch;
      cardState.value = {};
      flipToken.value = {};
      batchSeq.value++;
    }

    const searchResults = computed(() => {
      const q = searchQuery.value.trim().toLowerCase();
      if (!q) return [];
      // 拼音查询：q 里同时含中文与字母时按"文本命中即可"处理；纯字母时额外匹配首字母/全拼
      const latinOnly = /^[a-z]+$/.test(q);
      return players.value.filter(p => {
        const hitText = [p.name, p.name_zh, p.current_club, p.club_zh, p.position, p.position_zh,
         p.nationality, p.nationality_zh, p.league, p.league_zh]
          .some(v => (v || "").toLowerCase().includes(q));
        if (hitText) return true;
        if (!latinOnly) return false;
        const ini = pyIndex.value[p.id] || "";
        const full = pyFull.value[p.id] || "";
        // 首字母支持前缀（mbp）与子串（lm）两种习惯写法
        return ini.startsWith(q) || ini.includes(q) || (full && full.includes(q));
      });
    });

    // 搜索关键词高亮：先把文本整体转义，再把命中片段包进 <mark>（避免 XSS）
    function hl(text) {
      const raw = String(text == null ? "" : text);
      const q = searchQuery.value.trim();
      if (!q) return esc(raw);
      const idx = raw.toLowerCase().indexOf(q.toLowerCase());
      if (idx < 0) return esc(raw);
      return esc(raw.slice(0, idx)) + "<mark>" + esc(raw.slice(idx, idx + q.length)) + "</mark>" + esc(raw.slice(idx + q.length));
    }

    // 拼音命中时姓名里没有可直接高亮的片段 → 整段高亮，告诉用户"是按拼音搜到的"
    function hlName(p) {
      const raw = String(p.name_zh || p.name || "");
      const q = searchQuery.value.trim().toLowerCase();
      if (q && raw.toLowerCase().indexOf(q) < 0) {
        const ini = pyIndex.value[p.id] || "";
        const full = pyFull.value[p.id] || "";
        if (ini.includes(q) || (full && full.includes(q))) return "<mark>" + esc(raw) + "</mark>";
      }
      return hl(raw);
    }

    // world-map state
    const clubs = ref([]);
    const selectedClub = ref(null);
    // 跳转触发的一次性聚焦标志：仅当用户从列表点"地图查看"时置为目标 club_id，
    // renderMap 会据此强制飞到该点，渲染后立即清零，避免下次手动切 Tab 被重置视角
    const mapFocusId = ref(null);
    // 选中俱乐部变化时：
    //   - 若 watch 触发源是地图 click，flyMapTo 在实例已就绪后增量 setOption（不破坏漫游）
    //   - 若触发源是 openClub，此时 Tab 可能还没切过来、实例尚未 render，飞行交给 renderMap 初始视角处理
    watch(selectedClub, (club) => {
      if (activeTab.value === "map" && !mapFocusId.value) flyMapTo(club);
    });
    const mapYearFrom = ref(2020);
    const worldMap = ref(null);
    let worldMapRegistered = false;

    // chart refs
    const trendChart = ref(null);
    const compareChart = ref(null);
    const formationChart = ref(null);
    const efficiencyChart = ref(null);
    const clubBarChart = ref(null);
    let instances = {};
    // key 与 instances 的 key 保持一致，便于 ResizeObserver 反查并 resize 对应实例
    const chartRefs = {
      trend: trendChart, compare: compareChart,
      formation: formationChart, efficiency: efficiencyChart, worldMap: worldMap,
      clubBar: clubBarChart,
    };

    // 对比曲线配色：拉开色相/明度差，深色主题下也能分辨（避免相邻两条线撞色）
    const palette = ["#4f46e5", "#0ea5e9", "#16a34a", "#f59e0b", "#ef4444", "#a855f7", "#14b8a6", "#ec4899", "#64748b", "#f97316", "#84cc16", "#06b6d4"];

    // 请求取消：同一 key 的新请求会中断旧请求（切换球员时旧响应可能后到并覆盖新数据），
    // 组件卸载时统一中断所有未完成请求
    const aborters = new Map();
    const liveRequests = new Set();

    async function fetchJSON(url, key = null) {
      let ctrl = null;
      if (key) {
        const prev = aborters.get(key);
        if (prev) prev.abort();
        ctrl = new AbortController();
        aborters.set(key, ctrl);
        liveRequests.add(ctrl);
      }
      try {
        const r = await fetch(url, { cache: "no-store", signal: ctrl ? ctrl.signal : undefined });
        if (!r.ok) throw new Error(`${url} -> ${r.status}`);
        return await r.json();
      } finally {
        if (ctrl) {
          liveRequests.delete(ctrl);
          if (aborters.get(key) === ctrl) aborters.delete(key);
        }
      }
    }

    async function loadInitial() {
      loading.value = true;
      loadError.value = "";
      try {
        const [pres, fres, ires] = await Promise.all([
          fetchJSON("/api/players"),
          fetchJSON("/api/formations"),
          fetchJSON("/api/i18n"),
        ]);
        players.value = pres.players;
        formations.value = fres.formations;
        formationNotes.value = fres.notes || {};
        formationNotesEn.value = fres.notes_en || {};
        formationPositions.value = fres.positions || {};
        positionDuties.value = fres.position_duties || {};
        positionDutiesEn.value = fres.position_duties_en || {};
        i18n.value = ires;
        // 拼音索引用于搜索（失败不影响主流程，退化为纯文本匹配）
        try {
          const py = await fetchJSON("/api/search-index");
          pyIndex.value = py.initials || {};
          pyFull.value = py.full || {};
        } catch (e) {}
        // also preload clubs for stats display
        try { const cd = await fetchJSON("/api/clubs?year_from=2020"); clubs.value = cd.clubs; } catch(e) {}
        if (!roster.value.length) shuffleRoster();
        // 支持从分享链接恢复：#player/p01/trend
        const saved = readHash();
        const targetId = saved && players.value.some(p => p.id === saved.id)
          ? saved.id
          : (players.value[0] && players.value[0].id);
        if (saved) activeTab.value = saved.tab;
        if (targetId) await selectPlayer(targetId);
      } catch (e) {
        loadError.value = tf(L.value.loadFailed, { e: e.message || e });
      } finally {
        loading.value = false;
      }
    }

    function retryLoad() { loadInitial(); }

    async function selectPlayer(id) {
      try {
        const data = await fetchJSON(`/api/player?id=${id}`, "player");
        current.value = data;
        loadError.value = "";
      } catch (e) {
        if (e.name === "AbortError") return;   // 被后一次选人中断，静默丢弃
        loadError.value = tf(L.value.playerLoadFailed, { id, e: e.message || e });
        return;
      }
      syncHash();
      await nextTick();
      observeCharts();
      renderTrend();
      renderFormation();
      renderEfficiency();
      if (activeTab.value === "career") renderClubBar();
    }

    // 用户主动选人：暂停自动轮播，并写入可分享的 URL；同时翻转卡片显示队徽
    function pickPlayer(id) {
      autoPaused.value = true;
      selectPlayer(id);
    }
    // 卡片翻转动画：每条 keyframes 从头播放一次 → 翻过去用 flipForward，翻回来用 flipBackward
    // 配合 rc-inner 的 :key 绑定（每次 token+1 强制 Vue 重挂载），animation 从头触发
    function curState(id) { return cardState.value[id] || 'idle-front'; }
    function isFlipped(id) {
      const s = curState(id);
      return s === 'idle-back' || s === 'flipping' || s === 'unflipping';
    }
    function isUnflip(id) { return curState(id) === 'unflipping'; }
    function bumpToken(id) {
      const t = (flipToken.value[id] || 0) + 1;
      flipToken.value = { ...flipToken.value, [id]: t };
      return t;
    }
    function toggleFlip(id) {
      const s = curState(id);
      if (s === 'idle-front') {
        cardState.value = { ...cardState.value, [id]: 'flipping' };
        bumpToken(id);
      } else if (s === 'idle-back') {
        cardState.value = { ...cardState.value, [id]: 'unflipping' };
        bumpToken(id);
      }
    }
    function onFlipEnd(id) {
      const s = curState(id);
      if (s === 'flipping') {
        cardState.value = { ...cardState.value, [id]: 'idle-back' };
      } else if (s === 'unflipping') {
        cardState.value = { ...cardState.value, [id]: 'idle-front' };
      }
    }
    function onCardClick(id) {
      toggleFlip(id);
      pickPlayer(id);
    }
    function manualShuffle() {
      autoPaused.value = false;
      shuffleRoster();
    }

    function isSelected(id) { return current.value?.id === id; }

    // ---- URL 路由：/#player/p01/trend ----
    const TAB_KEYS = ["trend", "career", "formation", "map"];
    function readHash() {
      const m = (location.hash || "").match(/^#player\/(p\d{2,3})\/([a-z]+)$/);
      return m && TAB_KEYS.includes(m[2]) ? { id: m[1], tab: m[2] } : null;
    }
    function syncHash() {
      if (!current.value) return;
      const h = `#player/${current.value.id}/${activeTab.value}`;
      if (location.hash !== h) history.replaceState(null, "", h);
    }
    function onHashChange() {
      const s = readHash();
      if (!s) return;
      if (s.tab !== activeTab.value) switchTab(s.tab);
      if (!current.value || current.value.id !== s.id) selectPlayer(s.id);
    }

    function switchTab(key) {
      activeTab.value = key;
      syncHash();
      nextTick(() => {
        // 关键：selectPlayer 在页面加载时就渲染了所有图表，但隐藏 Tab(v-show) 的容器宽度为 0，
        // echarts.init 会按 0 宽建立坐标系。Tab 变为可见后必须先 resize() 到真实宽度再渲染，
        // 否则数据会被画在左侧一小条、canvas 被 CSS 拉伸（表现为"数据挤在左边、滑块很小"）。
        Object.values(instances).forEach(c => { if (c) c.resize(); });
        observeCharts();   // 容器若被 v-if 重建，重新挂上 ResizeObserver
        if (key === "trend") { renderTrend(); renderCompare(); }
        if (key === "career") { renderClubBar(); }
        if (key === "formation") { renderFormation(); renderEfficiency(); }
        if (key === "map") { loadClubs().then(renderMap).catch(e => console.warn("[map] loadClubs failed", e)); }
      });
    }

    function toggleCompare(id) {
      const i = compareIds.value.indexOf(id);
      if (i >= 0) compareIds.value.splice(i, 1);
      else if (compareIds.value.length < 6) compareIds.value.push(id);
      else compareIds.value = [...compareIds.value.slice(1), id];
      // 快速连续勾选时合并请求：180ms 内的多次点击只发一次
      clearTimeout(compareDebounce);
      compareDebounce = setTimeout(() => { compareDebounce = null; renderCompare(); }, 180);
    }

    const peakValue = computed(() => {
      if (!current.value) return 0;
      return Math.max(...current.value.market_value_history.map(m => m.value_m_eur));
    });

    const totalSignings = computed(() =>
      clubs.value.reduce((s, c) => s + c.signings_count, 0)
    );

    function formationPerf(f) { return current.value?.formation_performance?.[f]; }
    const hasFormationData = computed(() => !!current.value?.formation_performance);
    const formationKeysShown = computed(() => {
      const fp = current.value?.formation_performance;
      if (!fp) return [];
      return formations.value.filter(f => fp[f]);
    });
    const formationPerfVisible = computed(() =>
      hasFormationData.value && formationKeysShown.value.length > 0);
    const formationNoDataText = computed(() => L.value.formationNoData);
    const _bestFormation = computed(() => {
      if (!hasFormationData.value) return null;
      const entries = formationKeysShown.value.map(f => [f, formationPerf(f)]).filter(e => e[1]);
      if (!entries.length) return null;
      return entries.reduce((a, b) => ((b[1]?.avg_rating || 0) > (a[1]?.avg_rating || 0)) ? b : a);
    });
    const bestFormationKey = computed(() => _bestFormation.value ? _bestFormation.value[0] : '—');
    const bestFormationRating = computed(() => _bestFormation.value?.[1]?.avg_rating?.toFixed(2) || '—');
    const bestFormationApps = computed(() => _bestFormation.value?.[1]?.apps || 0);
    // 位置差异化：门将=扑救/丢球，后卫=解围/拦截，其余=进球/助攻
    const bestFormationPrimary = computed(() => {
      const cell = _bestFormation.value?.[1];
      if (!cell) return 0;
      return cell[metricKeys().k1] || 0;
    });
    const bestFormationSecondary = computed(() => {
      const cell = _bestFormation.value?.[1];
      if (!cell) return 0;
      return cell[metricKeys().k2] || 0;
    });

    // ---- 顶部四个指标框 → 详情页 ----
    const detail = ref(null);
    const detailPageEl = ref(null);
    const dQuery = ref(""), dPos = ref(""), dLeague = ref(""), dSort = ref("value");
    const cQuery = ref(""), cCountry = ref(""), cLeague = ref(""), cSort = ref("signings");
    const sQuery = ref(""), sYear = ref("");
    const formationSummary = ref([]);
    const formationLoading = ref(false);
    const formationCurrentKey = ref("");

    function formationNoteFor(f) {
      const zh = formationNotes.value || {};
      const en = formationNotesEn.value || {};
      return lang.value === "zh" ? (zh[f] || en[f] || "") : (en[f] || zh[f] || "");
    }
    const formationNoteText = computed(() => formationNoteFor(currentFormation.value));

    const detailMeta = computed(() => {
      const d = L.value;
      return ({
        players: {
          kicker: d.dpKicker, title: d.dpTitle,
          metric: tf(d.dpMetric, { n: players.value.length }),
          sub: d.dpSub,
        },
        clubs: {
          kicker: d.dcKicker, title: d.dcTitle,
          metric: tf(d.dcMetric, { n: clubs.value.length }),
          sub: d.dcSub,
        },
        signings: {
          kicker: d.dsKicker, title: d.dsTitle,
          metric: tf(d.dsMetric, { n: totalSignings.value }),
          sub: d.dsSub,
        },
        formations: {
          kicker: d.dfKicker, title: d.dfTitle,
          metric: tf(d.dfMetric, { n: formations.value.length }),
          sub: d.dfSub,
        },
      })[detail.value] || { kicker: "", title: "", metric: "", sub: "" };
    });

    function openDetail(kind) {
      detail.value = kind;
      document.body.style.overflow = "hidden";
      // 让详情页自身获得焦点，Esc 才能被其 keydown.esc 接收到
      nextTick(() => detailPageEl.value?.focus());
      if (kind === "formations") {
        if (!formationCurrentKey.value && formations.value.length) formationCurrentKey.value = formations.value[0];
        if (!formationSummary.value.length) loadFormationSummary();
      }
    }
    function closeDetail() {
      detail.value = null;
      document.body.style.overflow = "";
    }
    function onKeydown(e) { if (e.key === "Escape" && detail.value) closeDetail(); }

    async function loadFormationSummary() {
      formationLoading.value = true;
      try {
        const d = await fetchJSON("/api/formation-summary", "formation-summary");
        formationSummary.value = d.formations;
        if (!formationCurrentKey.value && d.formations.length) formationCurrentKey.value = d.formations[0].formation;
      } catch (e) {
        loadError.value = tf(L.value.formationLoadFailed, { e: e.message || e });
      } finally {
        formationLoading.value = false;
      }
    }

    // 详情页内的跳转：统一先关闭详情再切 Tab，避免遮罩残留
    function openPlayer(id) { closeDetail(); switchTab("trend"); pickPlayer(id); }
    function openClub(c) {
      closeDetail();
      mapFocusId.value = c.club_id;
      selectedClub.value = c;
      if (activeTab.value !== "map") {
        switchTab("map");
      } else {
        // 已在地图 tab，只飞过去 + 重新渲染散点高亮（不重新拉 clubs，避免覆盖 selectedClub）
        nextTick(() => { if (instances.worldMap) renderMap(); });
      }
    }
    function onMapYearChange() { selectedClub.value = null; loadClubs().then(renderMap); }
    function openFormationTab(f) { currentFormation.value = f; closeDetail(); switchTab("formation"); }

    // -------- players detail --------
    const dPlayers = computed(() => {
      const q = dQuery.value.trim().toLowerCase();
      let arr = players.value.filter(p =>
        (!dPos.value || p.position_group === dPos.value) &&
        (!dLeague.value || p.league === dLeague.value) &&
        (!q || [p.name, p.name_zh, p.current_club, p.club_zh, p.nationality, p.nationality_zh,
                p.position, p.position_zh, p.league, p.league_zh]
          .some(v => (v || "").toLowerCase().includes(q))));
      if (dSort.value === "value") arr = [...arr].sort((a, b) => (b.current_value_m_eur || 0) - (a.current_value_m_eur || 0));
      else if (dSort.value === "age") arr = [...arr].sort((a, b) => a.age - b.age);
      else arr = [...arr].sort((a, b) => a.name.localeCompare(b.name));
      return arr;
    });
    const dTopPlayer = computed(() => dPlayers.value.reduce(
      (best, p) => (!best || (p.current_value_m_eur || 0) > (best.current_value_m_eur || 0)) ? p : best, null));

    // -------- clubs detail --------
    const countryOptions = computed(() => [...new Set(clubs.value.map(c => c.country).filter(Boolean))].sort());
    const clubLeagueOptions = computed(() => [...new Set(clubs.value.map(c => c.league).filter(Boolean))].sort());
    const cClubs = computed(() => {
      const q = cQuery.value.trim().toLowerCase();
      let arr = clubs.value.filter(c =>
        (!cCountry.value || c.country === cCountry.value) &&
        (!cLeague.value || c.league === cLeague.value) &&
        (!q || [c.club, c.zh_name, c.en_name, c.city, c.country, c.league]
          .some(v => (v || "").toLowerCase().includes(q))));
      arr = [...arr].sort(cSort.value === "name"
        ? (a, b) => a.club.localeCompare(b.club)
        : (a, b) => b.signings_count - a.signings_count || a.club.localeCompare(b.club));
      return arr;
    });
    const cTopClub = computed(() => clubs.value.reduce(
      (best, c) => (!best || c.signings_count > best.signings_count) ? c : best, null));

    // -------- signings detail --------
    const allSignings = computed(() => {
      const out = [];
      clubs.value.forEach(c => (c.recent_signings || []).forEach(s => out.push({ ...s, club: c.club, clubZh: c.zh_name })));
      return out;
    });
    const signingYears = computed(() => [...new Set(
      allSignings.value.map(s => parseInt((s.period || "").slice(0, 4))).filter(y => y)
    )].sort((a, b) => b - a));
    const sSignings = computed(() => {
      const q = sQuery.value.trim().toLowerCase();
      const arr = allSignings.value.filter(s => {
        const y = parseInt((s.period || "").slice(0, 4)) || 0;
        return (!sYear.value || y >= Number(sYear.value)) &&
          (!q || [s.player_name, s.player_name_zh, s.club, s.clubZh, s.prev_club, s.prev_club_zh]
            .some(v => (v || "").toLowerCase().includes(q)));
      });
      return [...arr].sort((a, b) => (b.current_value_m_eur || 0) - (a.current_value_m_eur || 0));
    });
    const sTopSigning = computed(() => sSignings.value[0] || null);

    // -------- formations detail --------
    const formationDataPlayers = computed(() =>
      new Set(formationSummary.value.flatMap(f => f.contributors.map(c => c.id))).size);
    const formationTotals = computed(() => formationSummary.value.reduce(
      (a, f) => ({ apps: a.apps + f.apps, goal_contrib: a.goal_contrib + f.goal_contrib }),
      { apps: 0, goal_contrib: 0 }));
    const formationCurrent = computed(() =>
      formationSummary.value.find(f => f.formation === formationCurrentKey.value) || null);

    function posColor(g) { return { GK: "#1d70b8", DF: "#2e8b3d", MF: "#d29922", FW: "#c8102e" }[g] || "#888"; }

    // role 缩写 → position_group（用来给球场点上色 + 判断球员在该阵型里应该高亮哪些点）
    const ROLE_TO_GROUP = {
      GK: "GK", CB: "DF", LB: "DF", RB: "DF", LWB: "DF", RWB: "DF",
      CM: "MF", DM: "MF", CAM: "MF", LAM: "MF", RAM: "MF",
      LW: "FW", RW: "FW", ST: "FW",
    };
    function roleGroup(role) { return ROLE_TO_GROUP[role] || "MF"; }

    // 球场 SVG：给某个 role 的点上色（根据 role 所在组），如果 role 属于当前球员的组则高亮加粗
    function pitchDotFill(role) { return posColor(roleGroup(role)); }
    function pitchDotHighlight(role) {
      if (!current.value) return false;
      return roleGroup(role) === current.value.position_group;
    }
    function pitchSelectedDuty() {
      if (!pitchSelectedRole.value) return "";
      const dict = lang.value === "zh" ? positionDuties.value : positionDutiesEn.value;
      return dict[pitchSelectedRole.value] || positionDuties.value[pitchSelectedRole.value] || "";
    }

    // 界面文案的双语助手：中文界面只显示中文，英文界面只显示英文，不做中英混排
    function bi(zhText, enText) {
      return lang.value === "zh" ? zhText : enText;
    }

    // 位置缩写在中文界面里直接给中文名，避免球场上的英文缩写
    const ROLE_ZH = {
      GK: "门将", CB: "中卫", LB: "左后卫", RB: "右后卫",
      LWB: "左翼卫", RWB: "右翼卫", CM: "中场", DM: "后腰",
      CAM: "前腰", LAM: "左前卫", RAM: "右前卫",
      LW: "左边锋", RW: "右边锋", ST: "中锋",
    };
    function roleLabel(role) {
      if (!role) return "";
      return lang.value === "zh" ? (ROLE_ZH[role] || role) : role;
    }

    // 位置差异化指标标签：GK→扑救/丢球, DF→解围/拦截, MF/FW→进球/助攻
    // metricKeys 给出对应的数据字段名，metricLabels 给出展示文案 —— 两者必须成对使用
    function metricKeys() {
      const g = current.value?.position_group;
      if (g === "GK") return { k1: "saves", k2: "conceded" };
      if (g === "DF") return { k1: "clearances", k2: "interceptions" };
      return { k1: "goals", k2: "assists" };
    }

    // 对比列的第三个指标：门将=扑救、后卫=解围、其余=造球，统一按场均折算
    function careerRate(c) {
      if (!c || c.apps == null) return null;
      const { k1, k2 } = metricKeys();
      const g = current.value?.position_group;
      const numerator = (g === "GK" || g === "DF")
        ? (c[k1] || 0)
        : (c.goals || 0) + (c.assists || 0);
      return (numerator / Math.max(c.apps, 1)).toFixed(2);
    }

    // 图表/生涯表的"近几年"区块标题也要随位置切换（门将看扑救、后卫看解围）
    function recentAppsTitle() {
      const g = current.value?.position_group;
      const zh = lang.value === "zh";
      if (g === "GK") return zh ? "近几年上场与扑救" : "Recent Apps & Saves";
      if (g === "DF") return zh ? "近几年上场与解围" : "Recent Apps & Clearances";
      return zh ? "近几年上场与进球" : "Recent Appearances";
    }

    // 生涯总览：聚合 career_history 全量数据（指标随位置组切换）
    const careerTotals = computed(() => {
      const hist = current.value?.career_history || [];
      if (!hist.length) return null;
      const { k1, k2 } = metricKeys();
      const g = current.value?.position_group;
      let apps = 0, a = 0, b = 0;
      hist.forEach(c => { apps += c.apps || 0; a += c[k1] || 0; b += c[k2] || 0; });
      const rate = apps ? ((g === "GK" || g === "DF" ? a : a + b) / apps).toFixed(2) : "—";
      const m = (hist[0].period || "").match(/\d{4}/);
      return { apps, k1: a, k2: b, rate, clubs: hist.length, startYear: m ? m[0] : "" };
    });

    // 俱乐部对比柱状图标题：随位置组切换指标口径
    function clubBarTitle() {
      const g = current.value?.position_group;
      const zh = lang.value === "zh";
      if (g === "GK") return zh ? "各俱乐部扑救与丢球" : "Saves & Conceded by Club";
      if (g === "DF") return zh ? "各俱乐部解围与拦截" : "Clearances & Interceptions by Club";
      return zh ? "各俱乐部进球与助攻" : "Goals & Assists by Club";
    }

    // 阵型贡献者列表：按球员位置选指标（门将→扑救/丢球，后卫→解围/拦截，其余→进球/助攻）
    function contribMetric(p) {
      const g = p.position_group;
      const zh = lang.value === "zh";
      if (g === "GK") return zh ? `扑救 ${p.saves || 0} · 丢球 ${p.conceded || 0}`
        : `Saves ${p.saves || 0} · Conceded ${p.conceded || 0}`;
      if (g === "DF") return zh ? `解围 ${p.clearances || 0} · 拦截 ${p.interceptions || 0}`
        : `Clearances ${p.clearances || 0} · Int ${p.interceptions || 0}`;
      return zh ? `进球 ${p.goals || 0} · 助攻 ${p.assists || 0}`
        : `Goals ${p.goals || 0} · Assists ${p.assists || 0}`;
    }

    function metricLabels() {
      const g = current.value?.position_group;
      if (g === "GK") {
        return lang.value === "zh"
          ? { primary: "扑救", secondary: "丢球", axis: "扑救 / 丢球", eff: "场均扑救", gkHint: "门将位置主要展示扑救与丢球数据" }
          : { primary: "Saves", secondary: "Conceded", axis: "Saves / Conceded", eff: "Saves per game", gkHint: "Goalkeeper metrics focus on saves and conceded" };
      }
      if (g === "DF") {
        return lang.value === "zh"
          ? { primary: "解围", secondary: "拦截", axis: "解围 / 拦截", eff: "场均解围", gkHint: "后卫位置主要展示解围与拦截数据" }
          : { primary: "Clearances", secondary: "Interceptions", axis: "Clearances / Interceptions", eff: "Clearances per game", gkHint: "Defender metrics focus on clearances and interceptions" };
      }
      // MF / FW 默认
      return lang.value === "zh"
        ? { primary: "进球", secondary: "助攻", axis: "进球 / 助攻", eff: "场均造球", gkHint: "" }
        : { primary: "Goals", secondary: "Assists", axis: "Goals / Assists", eff: "G+A per game", gkHint: "" };
    }

    // 转会节点：相邻两个采样点俱乐部不同 → 视为一次转会（身价历史里没有转会费字段）
    function trendTransfers(hist) {
      const out = [];
      for (let i = 1; i < hist.length; i++) {
        if (hist[i].club !== hist[i - 1].club) {
          out.push({
            date: hist[i].date,
            from: hist[i - 1].club, fromZh: hist[i - 1].club_zh,
            to: hist[i].club, toZh: hist[i].club_zh,
            value: hist[i].value_m_eur, idx: i,
          });
        }
      }
      return out;
    }

    // 小屏上 dataZoom 的 inside 手势会跟页面纵向滚动抢事件（手指一滑图表就停住页面），
    // 因此窄屏只保留底部滑块；桌面端仍支持滚轮缩放。
    const narrowMedia = window.matchMedia("(max-width: 768px)");
    function isNarrow() { return narrowMedia.matches; }
    function zoomControls(k) {
      const slider = { type: "slider", xAxisIndex: 0, height: 16, bottom: 16, borderColor: k.border, fillerColor: theme.value.washStrong, handleStyle: { color: theme.value.accent }, textStyle: { color: k.label, fontSize: 10 } };
      return isNarrow() ? [slider] : [{ type: "inside", xAxisIndex: 0 }, slider];
    }

    // -------- render: trend --------
    function renderTrend() {
      if (!trendChart.value || !current.value) return;
      if (!instances.trend) instances.trend = echarts.init(trendChart.value);
      const c = instances.trend;
      const k = ink();
      const hist = current.value.market_value_history;
      const areas = [];
      for (let i = 0; i < hist.length; i++) {
        const start = hist[i].date;
        const end = i < hist.length - 1 ? hist[i+1].date : hist[i].date;
        areas.push([{ xAxis: start, itemStyle: { color: posColor(current.value.position_group), opacity: 0.06 } }, { xAxis: end }]);
      }
      const transfers = trendTransfers(hist);
      c.setOption({
        tooltip: { trigger: "axis", formatter: ps => {
          const lineParam = ps.find(p => p.seriesType === "line") || ps[0];
          const h = hist[lineParam.dataIndex];
          return `<b>${h.date}</b><br/>${L.value.chartValue}: <b style="color:${theme.value.accent}">€${h.value_m_eur}m</b>${h.estimated ? ` <span style="font-size:10px;opacity:.65">${L.value.chartEst}</span>` : ''}<br/>${L.value.chartClubThen}: ${esc(clubNm(h.club, h.club_zh))}`;
        }},
        // containLabel: 让 ECharts 按实际文字宽度预留轴空间，避免刻度/轴名互相压字
        grid: { left: 8, right: 20, top: 34, bottom: 68, containLabel: true },
        // 真实时间轴 + 可缩放：横轴长度 = 真实时间跨度，滚轮/拖动可拉伸查看细节
        xAxis: { type: "time", axisLine: { lineStyle: { color: k.axis } }, axisLabel: { color: k.label, fontSize: 10, hideOverlap: true } },
        yAxis: { type: "value", name: "€M", scale: true, splitNumber: 5, nameGap: 14, nameTextStyle: { color: k.label, align: "left" }, axisLine: { lineStyle: { color: k.axis } }, splitLine: { lineStyle: { color: k.split } }, axisLabel: { color: k.label, margin: 8 } },
        dataZoom: zoomControls(k),
        series: [{
          type: "line", smooth: true, symbol: "circle", symbolSize: 8,
          // 回填的估值点用小一号的灰点，跟真实快照点分开（线仍连续，不假装分段）
          data: hist.map(h => ({
            value: [h.date, h.value_m_eur],
            symbolSize: h.estimated ? 4 : 8,
            itemStyle: h.estimated ? { color: "#9ca3af", borderColor: "#9ca3af" } : { color: theme.value.accent },
          })),
          lineStyle: { color: theme.value.accent, width: 3 },
          itemStyle: { color: theme.value.accent },
          areaStyle: { color: { type: "linear", x:0,y:0,x2:0,y2:1, colorStops: [{ offset: 0, color: theme.value.accent + "40" }, { offset: 1, color: theme.value.accent + "00" }] } },
          markArea: { silent: true, data: areas },
          markPoint: { symbolSize: 40, data: [{ type: "max", name: L.value.chartPeak, symbolOffset: [0, -12] }, { type: "min", name: L.value.chartTrough, symbolOffset: [0, 12] }], itemStyle: { color: "#1d70b8" }, label: { color: "#fff", fontSize: 10 } },
        }, {
          name: L.value.chartTransfer, type: "scatter", symbol: "pin", symbolSize: 30, z: 6,
          data: transfers.map(t => ({ value: [t.date, t.value], transfer: t })),
          itemStyle: { color: "#c8102e" },
          tooltip: { trigger: "item", formatter: p => {
            const t = p.data.transfer;
            return `<b>${L.value.chartTransfer}</b> <span style="font-size:10px;opacity:.65">${L.value.chartTransferInferred}</span><br/>${esc(t.date)}<br/>${esc(clubNm(t.from, t.fromZh))} → <b>${esc(clubNm(t.to, t.toZh))}</b><br/>${L.value.chartValueAt} €${t.value}m`;
          } },
        }],
      }, true);
    }

    // -------- render: compare -------------
    // 同一个 ids 组合的结果缓存起来，并在请求飞行中复用同一个 Promise：
    // 来回勾选同一批球员时不再重复请求 /api/compare
    const compareCache = new Map();      // idsKey -> {series}
    const compareInflight = new Map();   // idsKey -> Promise
    let compareDebounce = null;
    const COMPARE_CACHE_MAX = 40;

    function compareData(ids) {
      const key = ids.join(",");
      if (compareCache.has(key)) return Promise.resolve(compareCache.get(key));
      if (compareInflight.has(key)) return compareInflight.get(key);
      const p = fetchJSON(`/api/compare?ids=${key}`).then(d => {
        compareCache.set(key, d);
        if (compareCache.size > COMPARE_CACHE_MAX) {
          compareCache.delete(compareCache.keys().next().value);
        }
        compareInflight.delete(key);
        return d;
      }, e => { compareInflight.delete(key); throw e; });
      compareInflight.set(key, p);
      return p;
    }

    async function renderCompare() {
      if (!compareChart.value) return;
      if (!instances.compare) instances.compare = echarts.init(compareChart.value);
      const c = instances.compare;
      const ids = [...compareIds.value];
      let data;
      try {
        data = await compareData(ids);
      } catch (e) {
        console.warn("[compare] request failed", e);
        return;   // 保留上一帧图表，避免整块白屏
      }
      // 期间用户又改了选择 → 丢弃这次过期响应
      if (ids.join(",") !== compareIds.value.join(",")) return;
      // 真实时间轴：各球员数据按各自真实日期落点，横轴长度 = 实际时间跨度
      const series = data.series.map((s, i) => ({
        name: (playersById.value[s.id] && nm(playersById.value[s.id])) || s.name,
        type: "line", smooth: true, symbol: "circle", symbolSize: 5,
        data: s.data.map(d => [d.date, d.value_m_eur]), connectNulls: true,
        lineStyle: { width: 3, color: palette[i % palette.length] },
        itemStyle: { color: palette[i % palette.length] },
        emphasis: { focus: "series", lineStyle: { width: 4 } },
      }));
      const k = ink();
      c.setOption({
        tooltip: { trigger: "axis", backgroundColor: k.bg, borderColor: k.border, textStyle: { color: k.text } }, legend: { type: "scroll", top: 0, textStyle: { color: k.text, fontSize: 11 } },
        grid: { left: 8, right: 20, top: 40, bottom: 68, containLabel: true },
        xAxis: { type: "time", axisLine: { lineStyle: { color: k.axis } }, axisLabel: { color: k.label, fontSize: 10, hideOverlap: true } },
        yAxis: { type: "value", name: "€M", scale: true, splitNumber: 5, nameGap: 14, nameTextStyle: { color: k.label, align: "left" }, axisLine: { lineStyle: { color: k.axis } }, splitLine: { lineStyle: { color: k.split } }, axisLabel: { color: k.label, margin: 8 } },
        dataZoom: zoomControls(k),
        series,
      }, true);
    }

    // -------- render: formation bars --------
    // v-if 会销毁图表容器，旧实例还绑在被移除的节点上 → 必须 dispose 后在当前节点重建
    function ensureChart(key, el) {
      const cur = instances[key];
      if (cur && cur.getDom() !== el) { cur.dispose(); instances[key] = null; }
      if (!instances[key]) instances[key] = echarts.init(el);
      return instances[key];
    }

    function renderFormation() {
      if (!formationChart.value || !current.value) return;
      const c = ensureChart("formation", formationChart.value);
      const k = ink();
      const fs = formationKeysShown.value;
      const fp = current.value.formation_performance;
      const ml = metricLabels();
      const mk = metricKeys();
      if (!fp || !fs.length) {
        c.setOption({ series: [], xAxis: { show: false }, yAxis: { show: false },
          graphic: [{ type: "text", left: "center", top: "middle",
            style: { text: L.value.chartNoFormation, fill: k.label, fontSize: 14 } }] }, true);
        return;
      }
      c.setOption({
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, backgroundColor: k.bg, borderColor: k.border, textStyle: { color: k.text } }, legend: { top: 0, textStyle: { color: k.text } },
        grid: { left: 8, right: 12, top: 48, bottom: 40, containLabel: true },
        xAxis: { type: "category", data: fs, axisLine: { lineStyle: { color: k.axis } }, axisTick: { alignWithLabel: true }, axisLabel: { color: k.label, fontSize: 12, fontWeight: 500 } },
        yAxis: [
          { type: "value", alignTicks: true, name: ml.axis, nameGap: 14, nameTextStyle: { color: k.label, align: "left" }, axisLine: { lineStyle: { color: k.axis } }, splitLine: { lineStyle: { color: k.split } }, axisLabel: { color: k.label, margin: 8 } },
          { type: "value", alignTicks: true, name: L.value.chartAvgRatingAxis, min: 6, max: 9, interval: 0.5, nameGap: 14, nameTextStyle: { color: k.label, align: "right" }, axisLine: { lineStyle: { color: k.axis } }, splitLine: { show: false }, axisLabel: { color: k.label, margin: 8 } },
        ],
        series: [
          { name: ml.primary, type: "bar", data: fs.map(f => formationPerf(f)?.[mk.k1] || 0), itemStyle: { color: "#4f46e5" } },
          { name: ml.secondary, type: "bar", data: fs.map(f => formationPerf(f)?.[mk.k2] || 0), itemStyle: { color: "#1d70b8" } },
          { name: L.value.chartAvgRatingAxis, type: "line", yAxisIndex: 1, data: fs.map(f => formationPerf(f)?.avg_rating || 0), lineStyle: { color: "#2e8b3d", width: 3 }, itemStyle: { color: "#2e8b3d" }, symbolSize: 8 },
        ],
      }, true);
    }

    // -------- render: efficiency --------
    function renderEfficiency() {
      if (!efficiencyChart.value || !current.value) return;
      const c = ensureChart("efficiency", efficiencyChart.value);
      const k = ink();
      const fs = formationKeysShown.value;
      const fp = current.value.formation_performance;
      const ml = metricLabels();
      const mk = metricKeys();
      const group = current.value.position_group;
      if (!fp || !fs.length) {
        c.setOption({ series: [], xAxis: { show: false }, yAxis: { show: false },
          graphic: [{ type: "text", left: "center", top: "middle",
            style: { text: L.value.chartNoEfficiency, fill: k.label, fontSize: 14 } }] }, true);
        return;
      }
      const eff = fs.map(f => {
        // 数据集没有真实出场分钟数，只能按场均折算：
        // 门将→场均扑救、后卫→场均解围、其余→场均造球（(进球+助攻)/出场数）。
        // 不能用 apps*90 冒充"每 90 分钟"——替补的场均时间远低于 90 分钟。
        const v = formationPerf(f) || {};
        const num = (group === "GK" || group === "DF")
          ? (v[mk.k1] || 0)
          : (v.goals || 0) + (v.assists || 0);
        return +(v.apps ? num / v.apps : 0).toFixed(2);
      });
      c.setOption({
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, backgroundColor: k.bg, borderColor: k.border, textStyle: { color: k.text } },
        grid: { left: 8, right: 16, top: 36, bottom: 40, containLabel: true },
        xAxis: { type: "category", data: fs, axisLine: { lineStyle: { color: k.axis } }, axisTick: { alignWithLabel: true }, axisLabel: { color: k.label, fontSize: 12, fontWeight: 500 } },
        // max 留 15% 顶部余量（向上取到 0.1），避免柱顶数值贴到轴名/被裁切
        yAxis: { type: "value", name: ml.eff, nameGap: 14, nameTextStyle: { color: k.label, align: "left" }, max: v => Math.max(0.4, Math.ceil(v.max * 1.15 * 10) / 10), axisLine: { lineStyle: { color: k.axis } }, splitLine: { lineStyle: { color: k.split } }, axisLabel: { color: k.label, margin: 8 } },
        series: [{ type: "bar", data: eff.map((v, i) => ({ value: v, itemStyle: { color: palette[i % palette.length] } })), label: { show: true, position: "top", color: k.text, fontSize: 11, distance: 6 }, barWidth: "38%" }],
      }, true);
    }

    // -------- render: club bar (career tab) --------
    function renderClubBar() {
      const el = clubBarChart.value;
      if (!el || !current.value) return;
      if (!el.offsetWidth) return;   // career tab 隐藏时容器宽 0，等 switchTab 的 nextTick 再画
      const hist = current.value.career_history || [];
      if (!hist.length) return;
      const c = ensureChart("clubBar", el);
      c.resize();
      const k = ink();
      const ml = metricLabels();
      const mk = metricKeys();
      const names = hist.map(h => lang.value === "zh" ? (h.club_zh || h.club) : h.club);
      c.setOption({
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, backgroundColor: k.bg, borderColor: k.border, textStyle: { color: k.text } },
        legend: { top: 0, textStyle: { color: k.text, fontSize: 11 } },
        grid: { left: 8, right: 12, top: 40, bottom: 40, containLabel: true },
        xAxis: { type: "category", data: names, axisLine: { lineStyle: { color: k.axis } }, axisTick: { alignWithLabel: true },
          axisLabel: { color: k.label, fontSize: 11, rotate: names.length > 5 ? 20 : 0, hideOverlap: true } },
        yAxis: { type: "value", name: ml.axis, nameGap: 14, nameTextStyle: { color: k.label, align: "left" }, axisLine: { lineStyle: { color: k.axis } }, splitLine: { lineStyle: { color: k.split } }, axisLabel: { color: k.label, margin: 8 } },
        series: [
          { name: ml.primary, type: "bar", data: hist.map(h => h[mk.k1] || 0), itemStyle: { color: theme.value.accent } },
          { name: ml.secondary, type: "bar", data: hist.map(h => h[mk.k2] || 0), itemStyle: { color: k.label } },
        ],
      }, true);
    }

    // ===== world map =====
    async function ensureWorldMap() {
      if (worldMapRegistered) return;
      // 优先本地自托管（避免 CDN 不可用 + echarts 4.9 地图与 5.x 本体的版本错位），失败再回退 CDN
      const urls = ["/world.json", "https://cdn.jsdelivr.net/gh/apache/echarts@4.9.0/map/json/world.json", "https://fastly.jsdelivr.net/gh/apache/echarts@4.9.0/map/json/world.json"];
      let json = null;
      for (const u of urls) { try { const r = await fetch(u); if (r.ok) { json = await r.json(); break; } } catch (e) {} }
      if (json) { echarts.registerMap("world", json); worldMapRegistered = true; }
    }

    async function loadClubs() {
      const data = await fetchJSON(`/api/clubs?year_from=${mapYearFrom.value}`, "clubs");
      clubs.value = data.clubs; return data;
    }

    function onSigningClick(playerId) { pickPlayer(playerId); switchTab("trend"); }

    // 地图俱乐部散点数据生成：根据 selectedClub 计算高亮样式（独立函数，供 renderMap / updateMapHighlight 复用）
    function buildMapClubData(clubList, selId) {
      const k = ink();
      return clubList.map(club => {
        const isSel = club.club_id === selId;
        return {
          id: club.club_id, name: clubNm(club.club, club.zh_name), value: [club.lng, club.lat], symbol: "circle",
          symbolSize: isSel
            ? (club.signings_count > 0 ? 22 : 18)
            : (club.signings_count > 0 ? 14 + Math.min(club.signings_count, 4) * 3 : 10),
          itemStyle: isSel
            ? { color: theme.value.accent, borderColor: k.bg, borderWidth: 2.5, shadowBlur: 16, shadowColor: theme.value.accent }
            : { color: "#1d70b8", borderColor: k.bg, borderWidth: 1.5, shadowBlur: club.signings_count > 0 ? 8 : 0, shadowColor: "rgba(29,112,184,0.6)" },
          clubData: club,
        };
      });
    }

    // 增量更新散点高亮（merge 模式 setOption，不动 geo，不破坏用户漫游）
    function updateMapHighlight() {
      const c = instances.worldMap; if (!c || !clubs.value.length) return;
      const data = buildMapClubData(clubs.value, selectedClub.value?.club_id);
      c.setOption({ series: [{ data }] });  // 默认 merge 模式
    }

    // 地图视角飞到指定俱乐部；增量 setOption 不破坏用户已有漫游
    function flyMapTo(club) {
      const c = instances.worldMap; if (!c) return;
      if (!club || club.lng == null || club.lat == null) {
        c.setOption({ geo: { center: [10, 35], zoom: 1.6 } });
        updateMapHighlight();
        return;
      }
      const zoom = club.signings_count > 0 ? 6 : 4;
      c.setOption({ geo: { center: [club.lng, club.lat], zoom } });
      updateMapHighlight();
    }

    // 容器尺寸为 0 时的重试计数（Tab 刚切过来、v-show 尚未完成布局）
    let mapRetry = 0;

    async function renderMap() {
      const el = worldMap.value;
      if (!el) { console.warn("[map] worldMap ref is null"); return; }
      await ensureWorldMap();
      if (!worldMapRegistered) console.warn("[map] registerMap failed, /world.json 未成功注册");
      // 容器必须已有真实尺寸再初始化，否则 ECharts 会以 0 宽/高建立坐标系，表现为整块空白
      if (!el.offsetWidth || !el.offsetHeight) {
        if (mapRetry < 20) {
          mapRetry++;
          setTimeout(() => { mapRetry = 0; renderMap(); }, 120);
        }
        return;
      }
      mapRetry = 0;
      // 复用旧实例：仅当容器节点被 Vue 替换时 ensureChart 才会 dispose 重建，
      // 避免每次切 Tab 都把整张世界地图销毁再初始化
      const c = ensureChart("worldMap", el);
      c.resize();   // Tab 隐藏期间窗口尺寸可能变过，重新量一次容器
      const k = ink();
      if (!clubs.value.length) { try { await loadClubs(); } catch (e) { console.warn("[map] loadClubs failed", e); } }
      const data = buildMapClubData(clubs.value, selectedClub.value?.club_id);
      // 视角策略：
      //   - 有 mapFocusId（从 openClub 跳过来）→ 强制飞到 selectedClub 位置
      //   - 手动切 Tab / renderAllCharts → undefined 字段保持当前 center/zoom（不破坏漫游）
      const s = selectedClub.value;
      const forceFly = mapFocusId.value && s && s.club_id === mapFocusId.value && s.lng != null && s.lat != null;
      const geoCenter = forceFly ? [s.lng, s.lat] : undefined;
      const geoZoom = forceFly ? (s.signings_count > 0 ? 6 : 4) : undefined;
      c.setOption({
        tooltip: { trigger: "item", renderMode: "html", confine: true, formatter: p => {
          const cd = p.data.clubData; if (!cd) return esc(p.name);
          const badge = cd.club_logo
            ? `<img src="${esc(cd.club_logo)}" style="width:48px;height:48px;object-fit:contain;vertical-align:middle;margin-right:8px;"/>`
            : `<span style="display:inline-block;width:48px;height:48px;line-height:48px;text-align:center;background:${k.split};border-radius:50%;font-weight:700;color:${k.label};margin-right:8px;">${esc(clubNm(cd.club, cd.zh_name).slice(0, 2))}</span>`;
          return `<div style="display:flex;align-items:center;">${badge}<div><div style="font-weight:700;font-size:13px;">${esc(clubNm(cd.club, cd.zh_name))}</div><div style="font-size:11px;color:${k.label};">${esc(cd.city)}, ${esc(countryNm(cd.country))} · ${esc(leagueNm(cd.league))}</div><div style="font-size:11px;">${esc(tf(L.value.chartSigningsInline, { n: Number(cd.signings_count) || 0 }))}</div></div></div>`;
        }, backgroundColor: k.bg, borderColor: "#1d70b8", borderWidth: 1, padding: 8, extraCssText: "box-shadow: 0 2px 8px rgba(0,0,0,0.15);" },
        geo: { map: worldMapRegistered ? "world" : "", roam: true, silent: false, itemStyle: { areaColor: k.split, borderColor: k.border, borderWidth: 0.5 }, emphasis: { itemStyle: { areaColor: isDark.value ? "#2f3644" : "#d4d4d4" }, label: { show: false } }, center: geoCenter, zoom: geoZoom },
        series: [{ name: L.value.chartClubsSeries, type: "scatter", coordinateSystem: "geo", data, label: { show: false }, emphasis: { scale: 1.6, itemStyle: { borderColor: theme.value.accent, borderWidth: 2 } }, zlevel: 2 }],
      }, true);
      // 渲染完成后清零一次性聚焦标志
      if (forceFly) mapFocusId.value = null;
      c.off("click");
      c.on("click", (params) => {
        if (params.componentType !== "series" || params.seriesType !== "scatter") return;
        const cd = params.data.clubData; if (!cd) return;
        selectedClub.value = cd;   // watch 会在 activeTab==map && !mapFocusId 时触发 flyMapTo + updateMapHighlight
      });
    }

    // 用 ResizeObserver 替代全局 resize 监听：只重算尺寸真正变化的图表，且可精确解绑
    let ro = null;
    // 已观察的节点集合（WeakSet）：v-if 重建容器后节点对象会变，需要重新 observe
    const observedNodes = new WeakSet();
    function observeCharts() {
      if (!ro) return;
      Object.entries(chartRefs).forEach(([key, el]) => {
        const node = el && el.value;
        if (!node || observedNodes.has(node)) return;
        node.dataset.chartKey = key;
        ro.observe(node);
        observedNodes.add(node);
      });
    }
    function watchCharts() {
      if (typeof ResizeObserver === "undefined") {
        window.addEventListener("resize", onWinResize);
        return;
      }
      ro = new ResizeObserver(entries => {
        for (const en of entries) {
          const key = en.target.dataset.chartKey;
          const c = key && instances[key];
          if (c) c.resize();
        }
      });
      observeCharts();
    }
    function onWinResize() { Object.values(instances).forEach(c => c && c.resize()); }

    // 长页面（阵型/地图 tab 内容很长）在手机上滚到深处时提供一个回到顶部的按钮
    const showTop = ref(false);
    function onScroll() { showTop.value = window.scrollY > 480; }
    function scrollTop() { window.scrollTo({ top: 0, behavior: "smooth" }); }

    onMounted(async () => {
      await loadInitial();
      await nextTick();
      renderTrend(); renderCompare();
      // 分享链接直接落在「世界地图」时不会经过 switchTab，需要主动渲染一次
      if (activeTab.value === "map") loadClubs().then(renderMap).catch(e => console.warn("[map] loadClubs failed", e));
      // 名册每 5 秒自动换一批；悬停、搜索、已选中球员或排序模式下暂停
      rotorTimer = setInterval(() => {
        if (!rosterPaused.value && !autoPaused.value && !searchQuery.value && sortBy.value === "random" && players.value.length) shuffleRoster();
      }, 5000);
      watchCharts();
      window.addEventListener("hashchange", onHashChange);
      document.addEventListener("keydown", onKeydown);
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    });

    onUnmounted(() => {
      if (rotorTimer) clearInterval(rotorTimer);
      window.removeEventListener("hashchange", onHashChange);
      document.removeEventListener("keydown", onKeydown);
      window.removeEventListener("scroll", onScroll);
      document.body.style.overflow = "";
      if (ro) { ro.disconnect(); ro = null; }
      else window.removeEventListener("resize", onWinResize);
      // 销毁所有 ECharts 实例，避免内存泄漏
      Object.keys(instances).forEach(k => {
        if (instances[k]) { instances[k].dispose(); instances[k] = null; }
      });
      // 中断所有仍在途的请求
      liveRequests.forEach(c => c.abort());
      liveRequests.clear();
      aborters.clear();
    });

    return {
      tabs, activeTab, theme, isDark, toggleTheme, players, current, currentName, formations, formationNotes,
      formationPositions, positionDuties,
      lang, L, tf, toggleLang, nm, playerName, clubNm, posNm, leagueNm, countryNm, cityNm, stadiumNm, natNm, footNm, pgNm,
      clubNmOfPlayer, batchSize, formationNoteFor, formationNoteText, i18n, hl, hlName,
      currentFormation, compareIds, peakValue, totalSignings,
      loading, loadError, retryLoad, autoPaused,
      trendChart, compareChart, formationChart, efficiencyChart, worldMap,
      clubs, selectedClub, mapYearFrom,
      roster, rosterPaused, batchSeq, searchQuery, searchResults, shuffleRoster,
      cardState, flipToken, isFlipped, isUnflip, onCardClick, onFlipEnd,
      selectPlayer, pickPlayer, manualShuffle, isSelected, switchTab, toggleCompare, formationPerf,
      hasFormationData,
      formationPerfVisible, formationNoDataText,
      formationKeysShown,
      bestFormationKey, bestFormationRating, bestFormationApps, bestFormationPrimary, bestFormationSecondary,
      pitchSelectedRole, roleGroup, pitchDotFill, pitchDotHighlight, pitchSelectedDuty, metricLabels,
      metricKeys, careerRate, recentAppsTitle, contribMetric, roleLabel, bi,
      careerTotals, clubBarChart, clubBarTitle,
      loadClubs, renderMap, onSigningClick,
      filterPos, filterLeague, sortBy, leagueOptions, filteredPlayers, onFilterChange,
      exportChart, exportCSV, onLogoError,
      // 指标框详情页
      detail, detailMeta, openDetail, closeDetail, detailPageEl,
      dQuery, dPos, dLeague, dSort, dPlayers, dTopPlayer,
      cQuery, cCountry, cLeague, cSort, cClubs, cTopClub,
      countryOptions, clubLeagueOptions,
      sQuery, sYear, allSignings, signingYears, sSignings, sTopSigning,
      formationSummary, formationLoading, formationCurrentKey, formationCurrent,
      formationDataPlayers, formationTotals,
      openPlayer, openClub, onMapYearChange, openFormationTab,
      showTop, scrollTop,
    };
  },
}).mount("#app");
