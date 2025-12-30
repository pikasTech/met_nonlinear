# R10 清除离线模式 - 修改报告

## 任务概述

按照 R9 调查计划的修改方案，清除 WNET5 电路验证功能中的"离线模式"，所有权重统一从 project 目录的 JSON 文件加载，不再依赖 TensorFlow。

## 修改内容

### 1. `visualization/wnet5_circuit_validator.py`

#### 1.1 删除离线模式配置 (第 31-36 行)

**删除内容**:
```python
# 可选: 实验对比数据 (Excel) - 旧的单文件对比配置（向后兼容）
self.experiment_path = config.get('compare_with_experiment')
# 离线模式：使用预计算的数据，跳过TensorFlow模型加载
self.offline_mode = config.get('offline_mode', False)
# 预计算的数据（离线模式使用）
self.precomputed_data = config.get('precomputed_data', {})
```

**修改后**:
```python
# 可选: 实验对比数据 (Excel) - 旧的单文件对比配置（向后兼容）
self.experiment_path = config.get('compare_with_experiment')
```

#### 1.2 修改 `execute_validation` 方法 (第 360-368 行)

**原代码**:
```python
def execute_validation(self) -> bool:
    """执行WNET5电路验证流程"""
    try:
        logger.info("开始WNET5电路验证分析...")

        # 检查是否使用离线模式
        if self.offline_mode:
            logger.info("使用离线模式，跳过TensorFlow模型加载")
            # 离线模式：使用预计算的数据
            svf_params = self.precomputed_data['svf_parameters']
            dense_weights = self.precomputed_data['dense_weights']
            ...
        else:
            # 在线模式：加载模型和提取参数
            model = self._load_model()
            svf_params = self._extract_svf_parameters(model)
            dense_weights = self._extract_dense_weights(model, self.analysis_layer)
```

**新代码**:
```python
def execute_validation(self) -> bool:
    """执行WNET5电路验证流程"""
    try:
        logger.info("开始WNET5电路验证分析...")

        # 统一从 project 加载权重（纯 JSON，无 TensorFlow 依赖）
        logger.info(f"从 project '{self.model_project_name}' 加载权重...")
        svf_params = self._load_svf_parameters_from_project()
        dense_weights = self._load_dense_weights_from_project(self.analysis_layer)
```

#### 1.3 新增 `_load_svf_parameters_from_project` 方法 (第 408-419 行)

```python
def _load_svf_parameters_from_project(self) -> Dict[str, Any]:
    """从 project 的 config.json 加载 SVF 参数（纯 JSON，无 TensorFlow）"""
    project_cfg_path = Path('projects') / self.model_project_name / 'config.json'
    if not project_cfg_path.exists():
        raise FileNotFoundError(f"项目配置不存在: {project_cfg_path}")

    with open(project_cfg_path, 'r', encoding='utf-8') as f:
        project_cfg = json.load(f)

    # 兼容不同配置结构
    # 情况1: model.model_subcfg.init_center_freqs (嵌套结构)
    # 情况2: model_subcfg.init_center_freqs (扁平结构)
    if 'model' in project_cfg and 'model_subcfg' in project_cfg['model']:
        subcfg = project_cfg['model']['model_subcfg']
    else:
        subcfg = project_cfg.get('model_subcfg', {})

    center_freqs = subcfg.get('init_center_freqs', [])
    quality_factors = subcfg.get('init_quality_factors', [])

    if not center_freqs or not quality_factors:
        raise ValueError(f"项目 {self.model_project_name} 缺少 SVF 参数")

    return {
        'center_freqs': [float(f) for f in center_freqs],
        'quality_factors': [float(q) for q in quality_factors]
    }
```

#### 1.4 新增 `_load_dense_weights_from_project` 方法 (第 421-481 行)

```python
def _load_dense_weights_from_project(self, analysis_layer: int = 1) -> Dict[str, Any]:
    """从 project 的 best.weights.json 加载指定 Dense 层权重（纯 JSON）"""
    weights_json_path = Path('projects') / self.model_project_name / 'data' / 'best.weights.json'
    if not weights_json_path.exists():
        raise FileNotFoundError(f"权重文件不存在: {weights_json_path}")

    with open(weights_json_path, 'r', encoding='utf-8') as f:
        weights_data = json.load(f)

    # WNET5 结构: layer_to_layer_models[0]=SVF, [1]=Dense1, [2]=Dense2, [3]=Dense3
    # best.weights.json 中的命名:
    # - analysis_layer=1 -> "dense/kernel:0", "dense/bias:0"
    # - analysis_layer=2 -> "post_dense_1/kernel:0", "post_dense_1/bias:0"
    # - analysis_layer=3 -> "post_dense_2/kernel:0", "post_dense_2/bias:0"
    # - analysis_layer=4 -> "post_dense_3/kernel:0", "post_dense_3/bias:0"

    # 根据层号映射到权重名称
    layer_name_map = {
        1: ('dense', 'Dense_Layer_Model_1'),
        2: ('post_dense_1', 'Dense_Layer_Model_2'),
        3: ('post_dense_2', 'Dense_Layer_Model_3'),
        4: ('post_dense_3', 'Output_Layer_Model')
    }

    if analysis_layer not in layer_name_map:
        raise ValueError(f"无效的 analysis_layer: {analysis_layer}")

    layer_prefix, layer_name = layer_name_map[analysis_layer]

    # 查找 kernel 和 bias
    kernel = None
    bias = None

    for entry in weights_data:
        name = entry.get('name', '')
        if name == f"{layer_prefix}/kernel:0":
            kernel = np.array(entry['value'], dtype=np.float32)
        elif name == f"{layer_prefix}/bias:0":
            bias = np.array(entry['value'], dtype=np.float32)

    if kernel is None:
        raise ValueError(f"未找到层 {analysis_layer} ({layer_prefix}/kernel:0) 的权重")

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
        'layer_name': layer_name,
        'weights': kernel,
        'bias': bias,
        'analysis_layer': analysis_layer
    }
```

### 2. `core/config_validator.py`

#### 2.1 移除 schema 中的离线模式字段 (第 327-336 行)

**删除内容**:
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

### 3. `ex_projects/wnet5-circuit-validation/layer1/config.json`

**删除字段**:
- `offline_mode`
- `precomputed_data` (包含 svf_parameters 和 dense_weights)

### 4. `ex_projects/wnet5-circuit-validation/layer2/config.json`

同上，删除 `offline_mode` 和 `precomputed_data`

### 5. `ex_projects/wnet5-circuit-validation/layer3/config.json`

同上，删除 `offline_mode` 和 `precomputed_data`

## 验证测试

### 测试命令

```bash
python cli.py ep ex_projects/wnet5-circuit-validation/layer1
```

### 测试结果

```
[INFO  2.51s] 开始WNET5电路验证分析...
[INFO  2.51s] 从 project 'WNET5q1h2u6l3' 加载权重...
[INFO  2.51s] ✅ 从 JSON 加载 Dense 层 1: kernel=(6, 1), bias=(1,)
[INFO  3.17s] 计算SVF传递函数...
[INFO  3.17s] 计算组合传递函数...
[INFO  3.17s] 计算频率响应...
[INFO  3.19s] 生成幅频响应图...
[INFO  3.19s] 使用单文件对比模式...
[INFO  4.87s] 读取实验数据sheet: layer1
[INFO  4.87s] 匹配实验列: ['D1_1']
[INFO  5.69s] 对比图已保存: F:\...\layer1\data\plots\frequency_response_comparison.png
[INFO  6.41s] 误差比值图已保存: F:\...\layer1\data\plots\frequency_response_error_ratio.png
[INFO  6.41s] 误差分析数据已保存: F:\...\layer1\data\numerics\error_analysis.json
[INFO  6.41s] 生成分析报告...
[INFO  6.41s] 分析报告已保存: F:\...\layer1\data\reports\analysis_report.json
[INFO  6.41s] 保存计算结果 (results.json)...
[INFO  6.44s] 误差分析数据已添加到results.json
[INFO  6.45s] 结果已保存: results.json
[INFO  6.45s] ✅ WNET5电路验证分析完成
```

**测试状态**: ✅ 成功

## 优势对比

| 方面 | 离线模式（修改前） | Project 加载（修改后） |
|------|-------------------|----------------------|
| **配置复杂度** | 高（需手动编辑大量数值） | 低（只需 project 名称） |
| **可靠性** | 低（手动复制易出错） | 高（自动从权威源加载） |
| **依赖** | 可选 TensorFlow | 纯 JSON，无 TensorFlow |
| **维护性** | 差（权重变更需同步更新） | 好（单一数据源） |
| **可验证性** | 差（无法自动校验） | 好（JSON 格式可读） |

## 生成的文件

- `ex_projects/wnet5-circuit-validation/layer1/data/plots/frequency_response_comparison.png`
- `ex_projects/wnet5-circuit-validation/layer1/data/plots/frequency_response_error_ratio.png`
- `ex_projects/wnet5-circuit-validation/layer1/data/numerics/error_analysis.json`
- `ex_projects/wnet5-circuit-validation/layer1/data/reports/analysis_report.json`
- `ex_projects/wnet5-circuit-validation/layer1/data/results.json`

## 总结

成功清除离线模式，所有权重现在从 project 目录的 JSON 文件加载：
- SVF 参数从 `projects/{project}/config.json` 加载
- Dense 权重从 `projects/{project}/data/best.weights.json` 加载

验证测试通过，代码无需 TensorFlow 即可正常运行。
