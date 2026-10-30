﻿// 生成按需引入的 ECharts 浏览器包（IIFE，全局变量 echarts），体积从 1MB 降到 ~300KB。
// 用法：cd tools/echarts-bundle && npm install && npm run build
import { build } from "esbuild";
import { fileURLToPath } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const outfile = path.resolve(here, "../../templates/vendor/echarts.custom.min.js");

// 入口：显式注册本项目实际用到的图表 / 组件 / 渲染器
// 图表：line（身价走势、对比、评分折线）、bar（阵型进球/助攻、场均造球）、scatter（转会节点、地图俱乐部点）
// 组件：grid、tooltip、legend（含 scroll）、dataZoom（slider + inside）、markPoint、graphic（空态文案）、geo（世界地图）
// 渲染器：只用 canvas（getDataURL 导出 PNG 也依赖它）
const entry = `
import * as echarts from "echarts/core";
import { LineChart, BarChart, ScatterChart } from "echarts/charts";
import {
  GridComponent, TooltipComponent, LegendComponent, DataZoomComponent,
  MarkPointComponent, GraphicComponent, GeoComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  LineChart, BarChart, ScatterChart,
  GridComponent, TooltipComponent, LegendComponent, DataZoomComponent,
  MarkPointComponent, GraphicComponent, GeoComponent,
  CanvasRenderer,
]);

// 只把运行时真正用到的 API 挂到 window.echarts（init / registerMap），
// 避免 export * 把 core 里未使用的工具一并留在包里
export { init, registerMap } from "echarts/core";
`;

await build({
  stdin: { contents: entry, resolveDir: here, sourcefile: "echarts-entry.js" },
  bundle: true,
  minify: true,
  format: "iife",
  globalName: "echarts",
  target: ["es2018"],
  legalComments: "none",
  outfile,
});

console.log("built:", outfile);

