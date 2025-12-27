# R9 清除离线模式调查报告

## 任务背景

从 R8 调查报告中发现存在"离线模式"，用户要求彻底清除该模式，所有权重都应从 project 加载 JSON 格式的权重数据，不依赖 TensorFlow。

## 1. 离线模式现状分析

### 1.1 当前实现位置

| 文件 | 行号 | 用途 |
|------|------|------|
| `visualization/wnet5_circuit_validator.py` | 34 | 读取 `offline_mode` 配置 |
| `visualization/wnet5_circuit_validator.py` | 36 | 读取 `precomputed_data` 配置 |
| `visualization/wnet5_circuit_validator.py` | 370-382 | 离线模式逻辑分支 |
| `core/config_validator.py` | 331-336 | Schema 定义 `offline_mode` 和 `precomputed_data` |

### 1.2 离线模式工作流程

```
config.json (offline_mode=true, precomputed_data={...})
         ↓
wnet5_circuit_validator.py:execute_validation()
         ↓
if self.offline_mode:
    svf_params = precomputed_data['svf_parameters']
    dense_weights = precomputed_data['dense_weights']
else:
    _load_model() → TensorFlow
    _extract_svf_parameters()
    _extract_dense_weights()
```

### 1.3 问题分析

| 问题 | 说明 |
|------|------|
| **手动编辑不可靠** | `precomputed_data` 需在 config.json 中手动编写权重数值 |
| **容易出错** | 手动复制粘贴的权重数值容易遗漏或错误 |
| **冗余数据** | 权重已在 `projects/{project}/data/best.weights.json` 中存在 |

## 2. Project 权重存储位置

### 2.1 JSON 权重文件

```
projects/WNET5q1h2u6l3/
├── data/
│   ├── best.weights.json      # 训练最佳权重 (Keras格式)
│   └── best_val.weights.json  # 验证最佳权重
```

### 2.2 JSON 文件格式

```json
[
    {
        "name": "simple_rnn/simple_rnn_cell/kernel:0",
        "shape": [6, 24],
        "value": [[...], [...], ...]
    },
    {
        "name": "simple_rnn/simple_rnn_cell/recurrent_kernel:0",
        "shape": [24, 24],
        "value": [[...], [...], ...]
    },
    {
        "name": "simple_rnn/simple_rnn_cell/bias:0",
        "shape": [24],
        "value": [...]
    }
]
```

### 2.3 Project 配置获取 SVF 参数

```json
projects/WNET5q1h2u6l3/config.json
{
    "model": {
        "model_subcfg": {
            "init_center_freqs": [10.0, 80.0],
            "init_quality_factors": [1.0, 1.0]
        }
    }
}
```

## 3. 清除离线模式的修改计划

### 3.1 修改文件清单

| 文件 | 修改类型 | 说明 |
|------|----------|------|
| `visualization/wnet5_circuit_validator.py` | 修改 | 移除离线模式，添加 JSON 加载方法 |
| `core/config_validator.py` | 修改 | 移除 `offline_mode` 和 `precomputed_data` 字段 |
| `ex_projects/wnet5-circuit-validation/layer1/config.json` | 删除 | 移除 `offline_mode` 和 `precomputed_data` |
| `ex_projects/wnet5-circuit-validation/layer2/config.json` | 删除 | 同上 |
| `ex_projects/wnet5-circuit-validation/layer3/config.json` | 删除 | 同上 |

### 3.2 详细修改计划

#### 修改 1: `visualization/wnet5_circuit_validator.py`

**位置**: 第 26-36 行 ( `__init__` 方法)

**原代码**:
```python
# 离线模式：使用预计算的数据，跳过TensorFlow模型加载
self.offline_mode = config.get('offline_mode', False)
# 预计算的数据（离线模式使用）
self.precomputed_data = config.get('precomputed_data', {})
```

**新代码** (删除):
```python
# 删除离线模式相关代码
```

**位置**: 第 364-410 行 ( `execute_validation` 方法)

**原代码**:
```python
# 检查是否使用离线模式
if self.offline_mode:
    logger.info("使用离线模式，跳过TensorFlow模型加载")
    # 离线模式：使用预计算的数据
    svf_params = self.precomputed_data['svf_parameters']
    dense_weights = self.precomputed_data['dense_weights']

    # 转换列表为numpy数组（离线模式）
    if isinstance(dense_weights['weights'], list):
        dense_weights['weights'] = np.array(dense_weights['weights'], dtype=np.float32)
    if isinstance(dense_weights['bias'], list):
        dense_weights['bias'] = np.array(dense_weights['bias'], dtype=np.float32)

    dense_weights['analysis_layer'] = self.analysis_layer
else:
    # 在线模式：加载模型和提取参数
    model = self._load_model()
    svf_params = self._extract_svf_parameters(model)
    dense_weights = self._extract_dense_weights(model, self.analysis_layer)
```

**新代码**:
```python
# 统一从 project 加载权重（纯 JSON，无 TensorFlow 依赖）
logger.info(f"从 project '{self.model_project_name}' 加载权重...")
svf_params = self._load_svf_parameters_from_project()
dense_weights = self._load_dense_weights_from_project(self.analysis_layer)
```

**新增方法**: 放在 `_load_model` 方法之前

```python
def _load_svf_parameters_from_project(self) -> Dict[str, Any]:
    """从 project 的 config.json 加载 SVF 参数（纯 JSON，无 TensorFlow）"""
    project_cfg_path = Path('projects') / self.model_project_name / 'config.json'
    if not project_cfg_path.exists():
        raise FileNotFoundError(f"项目配置不存在: {project_cfg_path}")

    with open(project_cfg_path, 'r', encoding='utf-8') as f:
        project_cfg = json.load(f)

    # 兼容不同配置结构
    model_cfg = project_cfg.get('model', {})
    subcfg = model_cfg.get('model_subcfg', {}) or model_cfg.get('model_subcfg', {})

    center_freqs = subcfg.get('init_center_freqs', [])
    quality_factors = subcfg.get('init_quality_factors', [])

    if not center_freqs or not quality_factors:
        raise ValueError(f"项目 {self.model_project_name} 缺少 SVF 参数")

    return {
        'center_freqs': [float(f) for f in center_freqs],
        'quality_factors': [float(q) for q in quality_factors]
    }

def _load_dense_weights_from_project(self, analysis_layer: int = 1) -> Dict[str, Any]:
    """从 project 的 best.weights.json 加载指定 Dense 层权重（纯 JSON）"""
    weights_json_path = Path('projects') / self.model_project_name / 'data' / 'best.weights.json'
    if not weights_json_path.exists():
        raise FileNotFoundError(f"权重文件不存在: {weights_json_path}")

    with open(weights_json_path, 'r', encoding='utf-8') as f:
        weights_data = json.load(f)

    # 查找指定层的 Dense 权重
    # WNET5 结构: layer_to_layer_models[0]=SVF, [1]=Dense1, [2]=Dense2, [3]=Dense3
    # analysis_layer=1 -> Dense_Layer_Model_1 -> 权重名称包含 'layer_with_kernel-1'
    target_idx = analysis_layer  # Dense 层索引

    # 根据层号映射到权重名称
    layer_name_map = {
        1: 'layer_with_kernel-1',  # Dense_Layer_Model_1
        2: 'layer_with_kernel-2',  # Dense_Layer_Model_2
        3: 'layer_with_kernel-3',  # Dense_Layer_Model_3
        4: 'output_layer'          # Output_Layer_Model
    }

    kernel_key = layer_name_map.get(analysis_layer)
    if not kernel_key:
        raise ValueError(f"无效的 analysis_layer: {analysis_layer}")

    # 查找 kernel 和 bias
    kernel = None
    bias = None
    layer_name = None

    for entry in weights_data:
        name = entry.get('name', '')
        if kernel_key in name and 'kernel' in name:
            kernel = np.array(entry['value'], dtype=np.float32)
            layer_name = name.split('/')[0] if '/' in name else kernel_key
        elif kernel_key in name and 'bias' in name:
            bias = np.array(entry['value'], dtype=np.float32)

    if kernel is None:
        raise ValueError(f"未找到层 {analysis_layer} ({kernel_key}) 的权重")

    # 如果没有 bias，使用零向量
    if bias is None:
        bias = np.zeros(kernel.shape[1], dtype=np.float32)

    # 归一化 kernel 形状
    if kernel.ndim == 3:
        if kernel.shape[0] != 1:
            raise ValueError(f"期望 kernel_size=1，实际 {kernel.shape[0]}")
        kernel = kernel[0]

    logger.info(f"✅ 从 JSON 加载 Dense 层 {analysis_layer}: kernel={kernel.shape}, bias={bias.shape}")

    return {
        'layer_name': f"Dense_Layer_Model_{analysis_layer}",
        'weights': kernel,
        'bias': bias,
        'analysis_layer': analysis_layer
    }
```

#### 修改 2: `core/config_validator.py`

**位置**: 第 327-337 行 ( `WNET5_CIRCUIT_VALIDATION_SCHEMA` )

**删除字段**:
```python
"weights_path": {
    "type": "string",
    "minLength": 1
},
"offline_mode": {
    "type": "boolean"
},
"precomputed_data": {
    "type": "object"
}
```

**保留字段**:
```python
# 只保留必要的配置
"model_project_name": {
    "type": "string",
    "minLength": 1
},
"analysis_layer": {
    "type": "integer",
    "minimum": 1,
    "maximum": 10
},
"frequency_range": {...},
"compare_with_experiment": {...},
"experiment_comparison": {...}
```

#### 修改 3: 清理 config.json 文件

**删除以下字段**:
- `offline_mode`
- `precomputed_data`
- `weights_path` (如果存在)

**保留**:
- `model_project_name` (用于定位 project 目录)
- `analysis_layer`
- `frequency_range`
- `compare_with_experiment` / `experiment_comparison`

### 3.3 修改后的工作流程

```
config.json (只需 model_project_name + analysis_layer)
         ↓
wnet5_circuit_validator.py:execute_validation()
         ↓
_load_svf_parameters_from_project()  # 从 projects/{name}/config.json 读取
_load_dense_weights_from_project()   # 从 projects/{name}/data/best.weights.json 读取
         ↓
计算频率响应 (纯 numpy + sympy，无需 TensorFlow)
```

## 4. 优势分析

| 方面 | 离线模式（修改前） | Project 加载（修改后） |
|------|-------------------|----------------------|
| **配置复杂度** | 高（需手动编辑大量数值） | 低（只需 project 名称） |
| **可靠性** | 低（手动复制易出错） | 高（自动从权威源加载） |
| **依赖** | 可选 TensorFlow | 纯 JSON，无 TensorFlow |
| **维护性** | 差（权重变更需同步更新） | 好（单一数据源） |
| **可验证性** | 差（无法自动校验） | 好（JSON 格式可读） |

## 5. 风险与应对

| 风险 | 等级 | 应对措施 |
|------|------|----------|
| JSON 格式变更 | 中 | 添加版本检查和回退机制 |
| 权重文件缺失 | 高 | 添加清晰的错误信息 |
| 层号映射错误 | 中 | 添加详细日志和验证 |
| 配置不一致 | 低 | Schema 验证确保必需字段 |

## 6. 验证步骤

1. 运行 `ex_projects/wnet5-circuit-validation/layer1/config.json` 验证
2. 对比修改前后的输出结果是否一致
3. 检查日志中的权重加载信息是否正确
4. 验证所有三个 layer 配置都能正常工作
