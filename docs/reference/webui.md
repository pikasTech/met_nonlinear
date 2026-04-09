# WebUI 可视化服务

## 概述

WebUI 是基于 React + TypeScript 的项目可视化平台，用于浏览、选择和横向对比 `projects/` 目录下的多个项目。

## 技术架构

```
src/webui/
├── server/              # TypeScript 后端服务
│   ├── src/
│   │   ├── index.ts    # Express 服务器入口
│   │   └── manager.py  # Python 服务管理脚本
│   └── package.json
└── src/                # React 前端
    ├── components/      # React 组件
    ├── api.ts          # API 调用层
    ├── types.ts        # TypeScript 类型定义
    └── App.tsx         # 主应用组件
```

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
python cli.py --metrics --all-projects --missing-only
```

该命令会递归扫描 `projects/` 下所有真实项目目录，并只补生成缺失的 `metrics.json`。

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
      "hasLinearityByFrequency": true,
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

对于新的汇总链路，前端优先读取：

- `metrics.json`：表格视图和部分摘要图表的统一指标来源
- `linearity_by_frequency.json`：R² 频点曲线和 improvement 图仍使用该文件

## 前端功能

### 项目浏览器
- 递归扫描 `projects/` 目录
- 按项目名称过滤
- 按模型类型筛选

### 多项目对比
- 支持多选项目进行横向对比
- **图表视图**：R² 曲线继续读取 `linearity_by_frequency.json`，评估指标和计算成本摘要优先读取 `metrics.json`
- **表格视图**：直接读取 `metrics.json`，支持筛选、排序（TanStack Table）

## 开发命令

```bash
# 安装依赖
cd src/webui/server && npm install
cd src/webui && npm install

# 开发模式
cd src/webui/server && npx tsx watch src/index.ts

# 构建前端
cd src/webui && npm run build
```

## 端口说明

- 服务器默认端口：`3000`
- 前端开发服务器端口：`3001`（代理 API 到 3000）
