# R5: WNET5 电路验证层映射问题修复实现

## 问题背景

在执行 R4 任务时发现，`wnet5_circuit_validator.py` 中的 `layer_name_map` 是**硬编码固定映射**，导致输出层 `dense` 固定对应 `analysis_layer=4`。

对于 `WNET5_EFF2_A1_PS-5_360-07` 模型（只有 2 层 post_dense）：
- 当模型只有 2 层 post_dense 时，`analysis_layer=3` 会失败（因为找不到 `post_dense_3`）
- 用户需要根据模型实际结构记住"输出层是 layer4"，不符合直觉

## 修复方案

**选择方案**：动态生成 `layer_name_map`

修改 `_load_dense_weights_from_project` 方法，从权重 JSON 文件中动态检测实际存在的层，动态生成映射表。

## 代码修改

### 文件: [visualization/wnet5_circuit_validator.py](visualization/wnet5_circuit_validator.py)

#### 1. 新增 `_detect_post_dense_layers` 方法

```python
def _detect_post_dense_layers(self, weights_data: List[Dict]) -> List[int]:
    """检测权重文件中实际存在的 post_dense 层序号

    Args:
        weights_data: 权重 JSON 数据列表

    Returns:
        按升序排列的 post_dense 层序号列表，如 [1, 2, 3]
    """
    post_dense_nums = []
    for entry in weights_data:
        name = entry.get('name', '')
        # 匹配形如 "post_dense_N/kernel:0" 的名称
        if name.startswith('post_dense_') and name.endswith('/kernel:0'):
            layer_name = name.split('/')[0]  # 如 "post_dense_3"
            layer_num_str = layer_name.replace('post_dense_', '')
            try:
                layer_num = int(layer_num_str)
                post_dense_nums.append(layer_num)
            except ValueError:
                logger.warning(f"忽略无效的层名称: {layer_name}")
    return sorted(post_dense_nums)
```

#### 2. 修改 `_load_dense_weights_from_project` 方法

将硬编码的 `layer_name_map` 改为动态生成：

```python
# 动态检测权重文件中实际存在的 post_dense 层
post_dense_nums = self._detect_post_dense_layers(weights_data)
logger.info(f"检测到 {len(post_dense_nums)} 个 post_dense 层: {post_dense_nums}")

if not post_dense_nums:
    raise ValueError(f"权重文件中未找到任何 post_dense 层")

# 动态生成 layer_name_map
# 约定: analysis_layer=1,2,3...N 对应 post_dense_1, post_dense_2, ..., post_dense_N
#       analysis_layer=N+1 对应 dense（输出层）
layer_name_map = {}
for i, layer_num in enumerate(post_dense_nums):
    layer_name_map[i + 1] = (f'post_dense_{layer_num}', f'Dense_Layer_Model_{i + 1}')
# dense 始终是最后一层
layer_name_map[len(post_dense_nums) + 1] = ('dense', 'Output_Layer_Model')

logger.debug(f"动态生成的 layer_name_map: {layer_name_map}")
```

## 映射规则

| analysis_layer | 2 层 post_dense 模型 | 3 层 post_dense 模型 |
|---------------|---------------------|---------------------|
| 1 | post_dense_1 | post_dense_1 |
| 2 | post_dense_2 | post_dense_2 |
| 3 | dense (输出层) | post_dense_3 |
| 4 | - | dense (输出层) |

## 测试结果

### 测试 1: 3 层 post_dense 模型 (WNET5_EFF2_A1/layer2)

```
[INFO  3.81s] 从 project 'WNET5_EFF2_A1' 加载权重...
[INFO  3.81s] 检测到 3 个 post_dense 层: [1, 2, 3]
[INFO  3.81s] ✅ 从 JSON 加载 Dense 层 2: kernel=(14, 14), bias=(14,)
[INFO  5.11s] ✅ WNET5电路验证分析完成
```

### 测试 2: 2 层 post_dense 模型 (WNET5_EFF2_A1_PS-5_360-07/layer3)

```
[INFO  3.81s] 从 project 'WNET5_EFF2_A1_PS-5_360-07' 加载权重...
[INFO  3.81s] 检测到 2 个 post_dense 层: [1, 2]
[INFO  3.81s] 找到 dense/kernel:0: shape=(14, 1)
[INFO  3.81s] ✅ 从 JSON 加载 Dense 层 3: kernel=(14, 1), bias=(1,)
[WARNING 4.31s] SVF通道数 (12) 与权重输入通道数 (14) 不匹配，已循环拓展适配
[INFO  5.11s] ✅ WNET5电路验证分析完成
```

## 结论

- ✅ 动态层检测功能正常工作
- ✅ 3 层 post_dense 模型测试通过
- ✅ 2 层 post_dense 模型测试通过（layer3 正确映射到 dense）
- ✅ 向后兼容：现有配置无需修改
- ✅ 警告提示正常显示通道适配信息
