# 贡献指南

感谢你愿意改进这个项目。以下是最小必要流程，麻烦照着走，能省掉很多来回。

## 环境搭建

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

浏览器打开 <http://127.0.0.1:5000>。依赖只有 Flask 与 flask-cors，前端零构建。

## 改动前的三个坑

1. **改完前端或数据必须重启 Flask**。`index.html` 里的 `?v=` 资源版本号在进程启动时按文件内容哈希算好，热改 `templates/app.js` / `styles.css` 不会生效。
2. **静态资源必须自托管**。不得在 `index.html` 里直接引第三方 CDN 脚本，Vue / ECharts 走 `templates/vendor/`，CI 会拦这类提交。
3. **双语不能漏**。所有界面文案都要在 `templates/app.js` 的 `T.zh` / `T.en` 两份字典里同时补齐；名称类文本走 `nm()` / `clubNm()` / `posNm()` 等助手，不要在模板里硬编码单语字符串。

## 数据改动

- 球员与俱乐部数据都在 `data/` 下，`data/processed/*.json` 是 ETL 产物，一并提交。
- 有完整生涯合计的球员，阵型拆分数据必须与生涯合计精确一致（`data` 导入时会做一致性校验，不一致会直接报错）。
- 阵型数据是**分摊 / 估算**值，任何公开文案都写「估算 / 分摊」，不得表述为逐场实录。

## 提交前自检

```bash
python -m compileall -q app.py data scripts
```

再跑一遍接口冒烟（或直接手动点四个 Tab：身价走势 / 职业生涯 / 阵型表现 / 世界地图）：

```bash
python -c "from app import app; c=app.test_client(); print(c.get('/api/players').status_code)"
```

确认以下几条：

- 浅色 / 深色主题都正常，图表不变形、不出现窄条；
- 中英切换无残留另一语言文字；
- 切 Tab 后图表能撑满容器宽度；
- 未提交 `node_modules/`、`__pycache__/`、根目录导出的 PNG / CSV。

## 提交与 PR

- 提交信息用一句话说清「为什么改」，例如 `fix: 阵型评分轴固定 0.5 刻度，避免出现长串小数`。
- 一个 PR 只做一件事，别把重构和数据补充混在一起。
- PR 描述请按 `.github/pull_request_template.md` 的自检清单勾选。

## 数据版权

身价与生涯数据整理自 Transfermarkt，队徽与头像来自第三方公开来源。新增数据请注明来源，不要引入需要授权的商业数据。本项目仅供学习与演示。
