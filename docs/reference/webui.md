# WebUI 可视化服务

## 概述

WebUI 是基于 React + TypeScript 的项目可视化平台，用于浏览、选择和横向对比 `projects/` 目录下的多个项目。

当前对比页只保留两个主视图：

- `Loss Curves`：基于训练日志交互查看 loss 曲线
- `Table`：基于统一指标文件查看横向对比表格

其中 loss 曲线视图已经不再保留旧的指标图标签页，也不再显示底部缩略 rangeslider。

Figure Studio 页面用于调整论文图。它不维护硬编码图清单，后端递归扫描 `ex_projects/plot/**/config.json`，把每个 `paper_figure` 配置暴露给前端；渲染结果读取对应 ex_project 的 `data/` 目录。

## 技术架构

```
src/webui/
├── server/              # TypeScript 后端服务
│   ├── src/
│   │   ├── index.ts    # Express 服务器入口
│   │   └── manager.py  # Python 服务管理脚本
│   └── package.json
├── src/                # React 前端
│   ├── components/      # React 组件
│   ├── clientApi.ts    # API 调用层
│   ├── types.ts        # TypeScript 类型定义
│   └── App.tsx         # 主应用组件
└── dist/               # 构建产物（由 vite 生成）
```

**注意**：项目根目录不允许有 `package.json`、`package-lock.json`、`node_modules` 等 npm 相关文件，这些只允许存在于 `src/webui/` 目录下。

### Paper Editor 约束

- 前端 API 封装文件应保持为 `src/webui/src/clientApi.ts` 这类不与 `/api` 代理前缀冲突的命名，避免 Vite 开发代理把模块路径误判为接口路径。
- Markdown 与数学公式渲染必须复用成熟第三方链路，例如 `react-markdown`、`remark-*`、`rehype-*`、`KaTeX`；不要在项目内重复实现新的 Markdown/LaTeX 解析器。
- Outline 的 HTML 定位必须基于最终渲染 HTML 中的 heading `id` 反查，而不能仅依赖通用 `latex -> html` 线性插值；否则文档前段标题会被压到同一 HTML 行号，导致滚动映射失真。
- Paper Editor 的行号链路必须坚持 `view line -> raw latex -> markdown -> html` 的单向构建与严格反向映射；不要跳过中间层做插值回推。
- 当 Paper Editor 后端契约新增 `sourceView`、`viewColumns` 一类字段时，验收应直接请求 `/api/paper-editor/document?entry=main.tex&viewColumns=80`，确认响应中存在 `sourceView`；若缺失，优先怀疑服务端启动了陈旧产物，而不是先改前端。

## 启动服务

```bash
python cli.py server start
```

服务启动后访问 `http://localhost:3000`

推荐在启动前先为目标项目准备好评估与指标汇总产物：

```bash
python cli.py -e PROJECT_NAME
python cli.py --metrics PROJECT_NAME
python cli.py server start
```

如果要给仓库里的旧项目批量补齐指标文件，推荐先执行：

```bash
python cli.py --metrics --all-projects
```

该命令会递归扫描 `projects/` 下所有真实项目目录，并全量重算 `metrics.json`。

## 服务管理命令

| 命令 | 说明 |
|------|------|
| `python cli.py server start` | 启动服务器 |
| `python cli.py server stop` | 停止服务器 |
| `python cli.py server status` | 查看运行状态 |
| `python cli.py server logs` | 查看日志 |

## API 接口

### 项目列表

```
GET /api/projects
```

返回所有包含 `config.json` 的项目，支持递归扫描子目录。

响应示例：
```json
{
  "projects": [
    {
      "name": "FRIKANh8u6l6",
      "path": "FRIKANh8u6l6",
      "config": { "use_model": "FRIKAN", ... },
      "hasTrainingInfo": true,
      "hasLinearResponse": true,
      "hasModelInfo": true,
      "hasComputeAnalysis": true,
      "hasMetricsSummary": true
    }
  ],
  "total": 100
}
```

### 项目数据

```
GET /api/projects/{name}/data/{filename}
```

获取指定项目的 `data/` 目录下的 JSON 文件，如 `training_info.json`、`model_info.json` 等。

对于统一指标链路，前端只读取：

- `metrics.json`：表格视图和摘要指标的统一来源

### 训练日志

```
GET /api/projects/*/training-log
```

读取指定项目 `data/training_log.jsonl`，并按 JSONL 行解析为前端可直接消费的结构。

响应示例：

```json
{
  "projectPath": "01_LR_STUDY/LSTMTransformeru6_e1k_1",
  "projectName": "LSTMTransformeru6_e1k_1",
  "total": 1000,
  "availableMetrics": ["loss", "val_loss", "lr"],
  "entries": [
    {
      "epoch": 1,
      "loss": 0.0012,
      "val_loss": 0.0015,
      "lr": 0.0005
    }
  ]
}
```

说明：

- `Loss Curves` 视图优先读取该接口，而不是从 `training_info.json` 推断整条曲线
- 接口只负责把 `training_log.jsonl` 解析成结构化数据，不会补算缺失训练日志

### 论文图 Studio

```
GET /api/paper-figures/catalog
PUT /api/paper-figures/config/{figure_id}
POST /api/paper-figures/render
GET /api/paper-figures/render/{job_id}
```

说明：

- Catalog 来源是 `ex_projects/plot/**/config.json` 的递归扫描结果，不再读取 `docs/paper/config.json` 中的静态 figure 清单。
- Preview URL 指向 `/paper-plot-assets/.../data/<output_name>`，也就是每个 figure ex_project 的 canonical 输出。
- 保存配置时只写回该 figure ex_project 的 `config.json`。
- 重绘时后端调用 `python -m src.visualization.paper_figure_projects run-ids --figure-id <id>`；标准人工入口仍是 `python cli.py ep ex_projects/plot/.../<figure_project>`。
- 拼图和子图跳转关系来自 `paper_figure.subfigures[].project_path` 以及扫描阶段反向推导出的 parent montage。

## 前端功能

### 项目浏览器
- 递归扫描 `projects/` 目录
- 按项目名称过滤
- 按模型类型筛选

### 多项目对比
- 支持多选项目进行横向对比
- **Loss Curves 视图**：通过 `training-log` 接口读取 `training_log.jsonl`，使用 Plotly 渲染交互曲线
- **表格视图**：直接读取 `metrics.json`，支持筛选、排序（TanStack Table）

### Figure Studio

- 递归扫描 `ex_projects/plot/` 下所有带 `paper_figure` 的 `config.json`，自动区分 single 与 montage。
- 右侧 inspector 编辑的是当前 ex_project 的 `paper_figure.figure_config`，保存后写回原 config。
- 所有绘图输出进入对应 ex_project 的 `data/` 目录；Studio 不把新图写入 `docs/paper/figures/`。
- Montage 不显示 Legend adjuster；子图和拼图之间通过配置中的 project path 互相跳转。
- 正在重绘时，旧图固定在左侧，新图区域显示 spinner；渲染完成后进入左右对比。
- **配置持久化**：单图/montage tab 与具体 figure id 都写入 localStorage；页面刷新后优先恢复保存的 figure id，只有该 id 不在当前 tab 的扫描结果中时才回退到当前 tab 的首个 figure。
- **状态恢复约束**：catalog 异步加载完成前不得把恢复出的 `selectedFigureId` 清成 `null`，也不得让持久化 effect 把这个临时空值写回 localStorage；兜底选择只能在 `figures.length > 0` 且当前 id 已确认不在当前 tab pool 中时执行。
- **持久化验收**：修改 Figure Studio 选择逻辑后必须用 Playwright 覆盖刷新恢复场景，至少验证 single 与 montage 各自保存一个非首个 figure 后刷新，目标 tab、左侧 thumb、右侧 stage 标题和 localStorage 中的 `{ figureId, kind }` 都保持一致。

### Loss Curves 视图
- 当前只展示 `loss` 与 `val_loss`，**合并在同一张图中**
- 同一个 project 的 loss 和 val_loss 保持**同一种颜色**，loss 为实线，val_loss 为虚线，便于横向对应
- 工具栏按钮：`X: Linear/Log`、`Y: Linear/Log`、`Normalize`（归一化）、`Show All`、`Hide All`、`Reset Axes`
- **归一化**：按每个 project 的 `max(loss, val_loss)` 归一化到 1，便于跨项目对比收敛速度
- 支持 Plotly 原生缩放、滚轮缩放、双击重置和手动输入 X/Y 轴范围
- legend 固定放在主图下方外部，并预留额外底部边距避免与 `Epoch` 标签重叠
- 不再显示主图下方的小缩略图 rangeslider，避免压缩主图排版

### 预设持久化
- **自动保存**：选择项目、筛选、排序等操作会自动保存到 `cache/webui/state.json`
- **手动保存**：点击 "Presets" 按钮可保存/加载预设到 `cache/webui/presets/` 目录
- **预设保存内容**：选中项目、全局筛选、列筛选、排序、列可见性、展开文件夹状态
- **Loss Curves 状态**：归一化开关、X/Y 对数刻度会被保存；缩放范围（range）和曲线隐藏状态为本地状态，不持久化
- **加载容错**：加载预设时，会自动过滤掉当前项目列表中不存在的项目路径，并显示提示；若部分项目未找到，会显示"Preset loaded (N project(s) not found)"
- **更新预设**：已保存的预设支持点击"↻"按钮用当前配置覆盖更新

## 开发命令

> **npm 路径说明**：Windows 环境下若 `npm` 命令未在 PATH 中，需使用完整路径调用，如 `D:/Program Files/nodejs/npm.cmd` 或 `npm.cmd`。

```bash
# 安装依赖
cd src/webui/server && npm install
cd src/webui && npm install

# 开发模式
cd src/webui/server && npx tsx watch src/index.ts

# 构建前端（构建产物输出到 src/webui/dist/）
cd src/webui && npm run build
# Windows PATH 未配置时：
# D:/Program Files/nodejs/npm.cmd run build
```

前端静态资源说明：

- `python cli.py server start` 直接从 `src/webui/dist/` 提供静态文件
- `python cli.py server start` 不应盲目固定执行 `src/webui/server/dist/index.js`；如果 `src/webui/server/src/` 比 server dist 更新，应优先使用较新的源码入口或先重建 server dist，否则 Paper Editor 接口可能继续返回旧 schema。
- 修改 `src/webui/src/` 前端源码后，必须重新执行 `npm run build`，否则浏览器仍会加载旧的 dist 产物

## 端口说明

- 服务器默认端口：`3000`
- 前端开发服务器端口：`3001`（代理 API 到 3000）

## 技术经验与教训

### Plotly 组件重渲染导致 zoom 状态丢失

**问题描述**：当父组件重新渲染时，即使传给 Plotly 的数据相同，zoom 状态也会丢失，图表闪一下后回到初始状态。

**根本原因**：
- 每次渲染时 `new Set(...)` 创建新的 Set 对象引用
- 回调函数 `() => {...}` 每次渲染创建新的函数引用
- React 认为 prop 变化，触发 Plotly 组件重渲染，内部状态丢失

**解决方案**：
- 使用 `useMemo` 稳定对象引用：`const hiddenTracesSet = useMemo(() => new Set(lcState.hiddenTraces), [lcState.hiddenTraces])`
- 使用 `useCallback` 稳定回调函数引用

### auto-saving 触发重渲染问题

**问题描述**：auto-saving 触发后，图表 zoom 状态丢失。

**根本原因**：auto-saving 导致父组件状态更新，进而导致子组件 prop 引用变化，触发 Plotly 重渲染。

**经验教训**：
- **只将必要的状态放入持久化 state**：如 `normalize`、`xLogScale`、`yLogScale` 等设置开关
- **显示控制状态（range、hiddenTraces）应保留为组件本地状态**，不放入 state.json
- auto-saving 应该是无副作用的操作，父组件状态更新不应触发 Plotly 组件重渲染

### normalize 模式下 range 被锁死

**问题描述**：开启归一化后，Y 轴范围被锁死在 0-1.05，无法缩放。

**根本原因**：错误的代码逻辑同时设置了 `range: [0, 1.05]` 和 `autorange: false`，Plotly 忽略用户拖动产生的 zoom 操作。

**正确做法**：归一化只是对数据做了缩放，range 应由 Plotly 的 autorange 自动计算，不应手动锁死。

```typescript
// 错误：normalize=true 时锁死 range
range: normalize ? [0, 1.05] : toPlotRange(yRange, yLogScale),
autorange: normalize ? false : yRange == null,

// 正确：range 只受用户手动设置控制，与 normalize 无关
range: yRange != null ? toPlotRange(yRange, yLogScale) : undefined,
autorange: yRange == null,
```

### 状态设计原则

1. **持久化状态 vs 本地状态**：需要保存到 state.json/presets 的才放入全局状态；仅用于显示控制的应作为组件本地状态
2. **避免 prop 引用漂移**：传递给子组件的对象/函数应使用 `useMemo`/`useCallback` 稳定引用
3. **auto-saving 应无副作用**：状态保存操作不应触发不必要的重新渲染
