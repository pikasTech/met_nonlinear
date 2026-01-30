# R5: WNET5 电路验证层映射问题报告与解决方案

## 问题描述

在执行 R4 任务时发现，`wnet5_circuit_validator.py` 中的 `layer_name_map` 是**硬编码固定映射**，导致输出层 `dense` 固定对应 `analysis_layer=4`。

### 现象

对于 `WNET5_EFF2_A1_PS-5_360-07` 模型（只有 2 层 post_dense）：

| analysis_layer | 期望对应层 | 实际对应层 |
|---------------|-----------|-----------|
| 1 | post_dense_1 | post_dense_1 ✅ |
| 2 | post_dense_2 | post_dense_2 ✅ |
| 3 | dense（输出层） | post_dense_3 ❌（不存在） |
| 4 | - | dense ✅ |

当前代码中 `dense` 层固定映射到 `analysis_layer=4`，这意味着：
- 当模型只有 2 层 post_dense 时，`analysis_layer=3` 会失败（因为找不到 `post_dense_3`）
- 当模型有 3 层 post_dense 时，`analysis_layer=3` 对应 `post_dense_3`，`analysis_layer=4` 对应 `dense`

这种设计不够灵活，用户需要根据模型实际结构记住"输出层是 layer4"。

## 问题代码

`visualization/wnet5_circuit_validator.py:1569-1574`:

```python
layer_name_map = {
    1: ('post_dense_1', 'Dense_Layer_Model_1'),
    2: ('post_dense_2', 'Dense_Layer_Model_2'),
    3: ('post_dense_3', 'Dense_Layer_Model_3'),
    4: ('dense', 'Output_Layer_Model')  # 固定映射到 dense
}
```

问题：
1. 硬编码 3 层 post_dense + 1 层 dense 的假设
2. 不支持 2 层 post_dense + 1 层 dense 的模型
3. 用户需要手动记住 layer4 才是输出层，不符合直觉

## 解决方案

### 方案一：动态生成 layer_name_map（推荐）

修改 `_load_dense_weights_from_project` 方法，从权重 JSON 文件中动态检测实际存在的层，动态生成映射表。

**修改逻辑**：
1. 加载 `best.weights.json` 文件
2. 扫描所有 `post_dense_N/kernel:0` 名称，找到实际存在的 post_dense 层
3. 动态生成映射：
   - 第 1 个 post_dense → analysis_layer=1
   - 第 2 个 post_dense → analysis_layer=2
   - ...
   - 最后一个 post_dense 之后的 dense → analysis_layer=N+1

**优点**：
- 完全动态，适应任意层数
- 用户无需记忆固定映射
- 向后兼容现有配置

### 方案二：固定 layer3 为输出层

简单修改，将 `dense` 从 layer4 改为 layer3：

```python
layer_name_map = {
    1: ('post_dense_1', 'Dense_Layer_Model_1'),
    2: ('post_dense_2', 'Dense_Layer_Model_2'),
    3: ('post_dense_3', 'Dense_Layer_Model_3'),
    4: ('dense', 'Output_Layer_Model')  # 保持不变（不常用）
}
```

**问题**：
- 不解决根本问题
- 对于只有 2 层 post_dense 的模型，layer3 仍然会失败

### 方案三：参数化层数

在配置文件中添加 `post_dense_layers` 参数，指定实际层数。

**问题**：
- 需要修改配置文件
- 增加用户配置负担

## 推荐方案

**选择方案一**：动态生成 layer_name_map

### 实现步骤

1. 修改 `_load_dense_weights_from_project` 方法：
   - 添加 `_detect_post_dense_layers()` 方法，扫描权重文件
   - 动态生成 layer_name_map

2. 核心代码思路：

```python
def _detect_post_dense_layers(self, weights_data: List[Dict]) -> List[str]:
    """检测权重文件中实际存在的 post_dense 层"""
    post_dense_layers = []
    for entry in weights_data:
        name = entry.get('name', '')
        if name.startswith('post_dense_') and name.endswith('/kernel:0'):
            layer_num = name.split('/')[0].replace('post_dense_', '')
            post_dense_layers.append(int(layer_num))
    return sorted(post_dense_layers)

def _load_dense_weights_from_project(self, analysis_layer: int = 1) -> Dict[str, Any]:
    # 加载权重数据
    with open(weights_json_path, 'r', encoding='utf-8') as f:
        weights_data = json.load(f)

    # 动态检测 post_dense 层
    post_dense_nums = self._detect_post_dense_layers(weights_data)

    # 动态生成 layer_name_map
    layer_name_map = {}
    for i, layer_num in enumerate(post_dense_nums):
        layer_name_map[i + 1] = (f'post_dense_{layer_num}', f'Dense_Layer_Model_{i + 1}')
    # dense 始终是最后一层
    layer_name_map[len(post_dense_nums) + 1] = ('dense', 'Output_Layer_Model')
```

### 测试用例

1. **3 层 post_dense 模型**（如 WNET5_EFF2_A1）：
   - layer1 → post_dense_1
   - layer2 → post_dense_2
   - layer3 → post_dense_3
   - layer4 → dense

2. **2 层 post_dense 模型**（如 WNET5_EFF2_A1_PS-5_360-07）：
   - layer1 → post_dense_1
   - layer2 → post_dense_2
   - layer3 → dense

3. **其他层数模型**：自动适配

## 影响范围

- **需要修改的文件**: `visualization/wnet5_circuit_validator.py`
- **不需要修改的文件**: 配置文件、CLI 接口
- **向后兼容**: 是

## 后续任务

- **R5.1**: 实现动态层检测功能
- **R5.2**: 测试 3 层 post_dense 模型（WNET5_EFF2_A1）
- **R5.3**: 测试 2 层 post_dense 模型（WNET5_EFF2_A1_PS-5_360-07）
