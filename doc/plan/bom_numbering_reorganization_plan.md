# BOM电阻编号重组实施计划

## 执行摘要

本计划详细规划了将BOM电阻编号从当前的顺序编号方式改为按功能分组的新编号体系。新体系将每个通道的14个电阻按照正负分组排列：R1(bias_pos) → R2-R7(input_pos) → R8(bias_neg) → R9-R14(input_neg)，提高PCB布局的逻辑性和可维护性。

## 背景与目标

### 当前编号方式的问题
1. **顺序混乱**：正负权重交替出现，不利于PCB布线
2. **差分对分散**：差分对的两个电阻编号相距较远（如R2和R10）
3. **偏置位置不固定**：偏置电阻在通道末尾，不便于识别

### 新编号体系的优势
1. **功能分组清晰**：正向权重集中在前半部分，负向权重集中在后半部分
2. **偏置优先**：偏置电阻固定在R1和R8位置，便于快速识别
3. **对应关系明确**：R2对应R9，R3对应R10...形成清晰的差分对关系
4. **PCB布局优化**：同极性电阻集中，有利于电源和地线布局

## 新编号规则详细定义

### 每通道14个电阻的固定位置
| 位置 | 编号 | 类型 | 索引 | 说明 |
|------|------|------|------|------|
| 1 | R1 | bias_pos | - | 正向偏置 |
| 2 | R2 | input_pos | 1 | 第1个输入正权重 |
| 3 | R3 | input_pos | 2 | 第2个输入正权重 |
| 4 | R4 | input_pos | 3 | 第3个输入正权重 |
| 5 | R5 | input_pos | 4 | 第4个输入正权重 |
| 6 | R6 | input_pos | 5 | 第5个输入正权重 |
| 7 | R7 | input_pos | 6 | 第6个输入正权重 |
| 8 | R8 | bias_neg | - | 负向偏置 |
| 9 | R9 | input_neg | 1 | 第1个输入负权重 |
| 10 | R10 | input_neg | 2 | 第2个输入负权重 |
| 11 | R11 | input_neg | 3 | 第3个输入负权重 |
| 12 | R12 | input_neg | 4 | 第4个输入负权重 |
| 13 | R13 | input_neg | 5 | 第5个输入负权重 |
| 14 | R14 | input_neg | 6 | 第6个输入负权重 |

### 全局编号计算公式
```
全局编号 = (层偏移 + 通道偏移) * 14 + 通道内位置
```

其中：
- 层偏移：Layer2=0, Layer3=6, Layer4=12, Layer5=13
- 通道偏移：Channel号-1（对于Layer4，始终为0）
- 通道内位置：1-14（按上表）

## 技术实施方案

### 1. 修改文件：`spice_simulator/weight_resistor_bom_generator.py`

#### 修改点1：添加排序模式配置（约第45行）
```python
def __init__(self, bom_config: Optional[Dict] = None):
    # 新增：排序模式配置
    self.numbering_mode = self.bom_config.get('numbering_mode', 'sequential')
    # 'sequential': 原有的顺序编号
    # 'grouped': 新的分组编号
```

#### 修改点2：实现分组排序函数（新增方法，约第55行后）
```python
def _reorder_by_groups(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    按新规则重新排序电阻：
    每通道内顺序：bias_pos → input_pos(1-6) → bias_neg → input_neg(1-6)
    """
    # 实现逻辑：
    # 1. 添加排序键：层号、通道号、组内顺序
    # 2. 定义排序优先级
    # 3. 重新排序DataFrame
    # 4. 返回排序后的结果
```

#### 修改点3：修改编号生成逻辑（约第115行）
```python
# 在筛选后，应用排序
if self.numbering_mode == 'grouped':
    weight_df = self._reorder_by_groups(weight_df)
    
# 重新编号（保持原有逻辑）
weight_df['Symbol'] = [f"{self.symbol_prefix}{i+1}" 
                      for i in range(len(weight_df))]
```

#### 修改点4：添加差分对关联信息（可选增强，约第135行）
```python
if self.numbering_mode == 'grouped' and self.bom_config.get('include_pair_info', False):
    # 添加差分对信息列
    weight_df['Differential_Pair'] = weight_df.apply(
        lambda row: self._get_pair_info(row), axis=1
    )
```

### 2. 修改文件：`projects/WNET5q1h2u6l3/config.json`

#### 修改点：扩展bom_config配置（约第25行）
```json
"bom_config": {
  "standardization_series": "E192",
  "package": "0805",
  "tolerance": "0.5%",
  "auto_standardize": true,
  "numbering_mode": "grouped",  // 新增：编号模式
  "include_pair_info": true      // 新增：是否包含差分对信息
}
```

### 3. 修改文件：`core/cli_parser.py`

#### 修改点：添加命令行参数（约第280行）
```python
resistance_group.add_argument(
    '--bom-numbering', 
    type=str, 
    choices=['sequential', 'grouped'],
    default='sequential',
    help='BOM编号模式：sequential(顺序) 或 grouped(分组)'
)
```

### 4. 修改文件：`core/tasks/resistance_task.py`

#### 修改点：传递编号模式参数（约第200行）
```python
# 在调用BOM生成器前，添加编号模式到配置
if bom_config is None:
    bom_config = {}
    
# 从CLI参数或配置文件获取编号模式
numbering_mode = kwargs.get('bom_numbering') or \
                 bom_config.get('numbering_mode', 'sequential')
bom_config['numbering_mode'] = numbering_mode
```

## 详细排序算法

### 排序键生成逻辑
```python
def _get_sort_key(row):
    """生成排序键：(层优先级, 通道号, 类型优先级, 索引)"""
    layer_priority = {
        'layer2': 0,
        'layer3': 1, 
        'layer4': 2,
        'layer5': 3
    }
    
    type_priority = {
        'bias_pos': 0,    # R1
        'input_pos': 1,   # R2-R7
        'bias_neg': 2,    # R8
        'input_neg': 3    # R9-R14
    }
    
    # 处理索引（bias没有索引，设为0）
    index = row.get('index', 0) if not pd.isna(row.get('index')) else 0
    
    return (
        layer_priority.get(row['layer'], 999),
        row['channel'],
        type_priority.get(row['type'], 999),
        index
    )
```

### 差分对映射关系
```python
def _get_pair_info(row):
    """获取差分对信息"""
    if row['type'] == 'bias_pos':
        return 'R8'  # 对应bias_neg
    elif row['type'] == 'bias_neg':
        return 'R1'  # 对应bias_pos
    elif row['type'] == 'input_pos':
        # R2-R7对应R9-R14
        offset = int(row['index']) if not pd.isna(row['index']) else 0
        return f'R{8 + offset}'
    elif row['type'] == 'input_neg':
        # R9-R14对应R2-R7
        offset = int(row['index']) if not pd.isna(row['index']) else 0
        return f'R{1 + offset}'
    return ''
```

## 测试验证方案

### 1. 单元测试
- 测试排序算法的正确性
- 验证每个通道确实有14个电阻
- 检查编号连续性

### 2. 对比测试
- 生成两种模式的BOM，对比电阻数量一致性
- 验证相同的电阻只是编号不同

### 3. 验证要点
- Layer2 Channel1：R1-R14
- Layer2 Channel2：R15-R28
- Layer4（特殊）：只有R169-R182
- 总数仍为266个

## 实施步骤

### 第一阶段：核心功能实现（3小时）
1. 实现`_reorder_by_groups`排序函数
2. 添加排序模式配置支持
3. 单元测试排序逻辑

### 第二阶段：系统集成（2小时）
1. 修改CLI参数支持
2. 更新配置文件处理
3. 集成测试

### 第三阶段：增强功能（1小时）
1. 添加差分对信息列（可选）
2. 优化日志输出
3. 更新文档

### 第四阶段：测试与验证（2小时）
1. 完整的端到端测试
2. 生成对比报告
3. 性能测试

## 风险评估与缓解

### 风险1：向后兼容性
- **风险**：现有用户依赖当前编号
- **缓解**：默认保持`sequential`模式，新模式需显式启用

### 风险2：索引缺失
- **风险**：某些电阻可能没有index字段
- **缓解**：对缺失索引的情况设置默认值0

### 风险3：特殊层处理
- **风险**：Layer4只有1个通道，可能影响计算
- **缓解**：特殊处理Layer4的偏移计算

## 预期成果

### 1. 改进的BOM可读性
- 偏置电阻位置固定，一目了然
- 正负权重分组清晰，便于理解

### 2. 优化的PCB设计流程
- 差分对关系明确，布线更合理
- 同极性电阻集中，电源布局优化

### 3. 提升的可维护性
- 编号规则统一，便于自动化处理
- 故障诊断更快速，通过编号直接定位功能

## 总结

本计划通过重新设计BOM电阻编号体系，将混乱的顺序编号改为清晰的功能分组编号。新体系不仅提高了BOM的可读性，还为PCB设计和制造提供了更好的支持。实施过程保持向后兼容，风险可控，预计总工时8小时。建议在下一个项目版本中启用新编号模式，充分测试后再全面推广。