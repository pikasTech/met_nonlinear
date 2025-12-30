# R8 问题调查报告：wnet5-circuit-validation 权重手动编辑问题

## 问题描述

**R8**: 我发现 `ex_projects\wnet5-circuit-validation\layer1\config.json` 里面的权重竟然是手动编辑的，这相当不可靠，我认为应当指定 project 来支持加载，例如 `WNET5q1h2u6l3` 这种 project 来加载权重。

## 调查结果

### 1. 当前配置分析

**文件位置**: `ex_projects\wnet5-circuit-validation\layer1\config.json`

```json
{
  "task_info": {
    "task_type": "wnet5-circuit-validation",
    "description": "WNET5电路频率响应理论验证 - Layer1"
  },
  "model_project_name": "WNET5q1h2u6l3",
  "analysis_layer": 1,
  "frequency_range": {...},
  "compare_with_experiment": "...",
  "offline_mode": true,
  "precomputed_data": {
    "svf_parameters": {...},
    "dense_weights": {
      "layer_name": "Dense_Layer_Model_1",
      "weights": [[-2.0467..., -1.2283..., ...], ...],
      "bias": [0.1549..., -0.0135..., ...]
    }
  }
}
```

### 2. 问题核心

| 字段 | 用途 | 问题 |
|------|------|------|
| `model_project_name` | 指定项目名称 | 已存在，指向 `WNET5q1h2u6l3` |
| `precomputed_data.dense_weights` | 手动硬编码的权重数值 | **不可靠**：手动编辑容易出错 |
| `offline_mode` | 离线模式开关 | 当前为 `true`，使用手动权重 |

### 3. 代码执行逻辑

**文件**: `visualization/wnet5_circuit_validator.py`

```python
# 第 370-374 行：当 offline_mode=True 时
if self.offline_mode:
    # 使用手动编辑的 precomputed_data
    svf_params = self.precomputed_data['svf_parameters']
    dense_weights = self.precomputed_data['dense_weights']

# 第 412-458 行：当 offline_mode=False 且 TF 可用时
def _load_model(self):
    weights_path = Path('projects') / self.model_project_name / 'data' / 'best.weights.h5'
    model = WaveNet5(model_subcfg=model_subcfg)
    model.load_weights(str(weights_path))  # 从 project 加载
```

### 4. 现有项目结构

**WNET5q1h2u6l3 项目已存在于**: `projects/WNET5q1h2u6l3/`

```
projects/WNET5q1h2u6l3/
├── config.json
└── data/
    ├── best.weights.h5          # 训练最佳权重
    ├── best_val.weights.h5      # 验证最佳权重
    ├── best.weights.json        # JSON 格式权重（可读）
    ├── best_val.weights.json
    └── ...
```

**权重 JSON 文件示例** (`data/best_val.weights.json`):
```json
{
  "Dense_Layer_Model_1": {
    "weights": [[...], [...], ...],
    "bias": [...]
  }
}
```

### 5. 冗余与不一致风险

当前配置存在两个数据源：

```
                    ┌─────────────────────┐
                    │  model_project_name │
                    │  "WNET5q1h2u6l3"    │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────────┐   ┌───────────────────┐
│ 从 project    │    │   冗余字段        │   │  手动编辑字段     │
│ 加载权重      │    │  (未被使用)       │   │  (当前正在使用)   │
│ (TF 模式)     │    │                   │   │                   │
└───────────────┘    └───────────────────┘   └───────────────────┘
```

## 问题根因

1. **`model_project_name` 字段存在但未被离线模式使用**：代码只在 `offline_mode=False` 时使用 `model_project_name` 加载权重。

2. **手动编辑的 `dense_weights` 不可靠**：
   - 数值容易输错
   - 与实际训练结果可能不一致
   - 每次训练都需要手动更新

3. **配置语义不清晰**：`offline_mode` 的含义是"跳过 TensorFlow 加载"，但不应该意味着"手动提供权重"。

## 建议解决方案

### 方案 A：修改代码支持从 project 加载（推荐）

修改 `wnet5_circuit_validator.py`，让离线模式也能从 project 加载预导出的 JSON 权重：

```python
def _load_dense_weights_from_project(self):
    """从 project 目录加载 dense_weights.json"""
    weights_json_path = Path('projects') / self.model_project_name / 'data' / 'best_val.weights.json'
    if weights_json_path.exists():
        with open(weights_json_path, 'r') as f:
            weights_data = json.load(f)
        # 根据 analysis_layer 提取对应的权重
        target_layer = f"Dense_Layer_Model_{self.analysis_layer}"
        return weights_data.get(target_layer, {})
    raise FileNotFoundError(f"未找到权重文件: {weights_json_path}")
```

### 方案 B：统一配置结构

修改配置，只保留 `model_project_name`，删除 `precomputed_data`：

```json
{
  "task_type": "wnet5-circuit-validation",
  "model_project_name": "WNET5q1h2u6l3",
  "analysis_layer": 1,
  "frequency_range": {...},
  "compare_with_experiment": "..."
}
```

### 方案 C：添加自动导出功能

在 project 训练完成后，自动导出各层的 dense_weights 到 JSON 文件，供离线模式使用。

## 实施步骤

1. **修改代码**：在 `_load_model()` 或新增方法中，当 `offline_mode=True` 时，从 `projects/{model_project_name}/data/best_val.weights.json` 加载。

2. **清理配置**：从 `layer1/layer2/layer3/config.json` 中删除 `precomputed_data` 字段，只保留 `model_project_name`。

3. **验证**：确保离线模式能正确加载权重，与 TensorFlow 模式结果一致。

## 结论

R8 指出的问题确实存在。当前架构设计已经支持通过 `model_project_name` 指定项目，但离线模式没有利用这一机制，而是依赖手动编辑的权重。建议修改代码使离线模式也能自动从 project 加载权重，消除手动编辑的风险。

---

**调查完成**: 2025-12-27
**调查范围**: `ex_projects/wnet5-circuit-validation/`、`visualization/wnet5_circuit_validator.py`、`projects/WNET5q1h2u6l3/`
