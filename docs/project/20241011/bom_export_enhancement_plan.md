# BOM导出功能增强改进计划

**创建时间**: 2025-08-21  
**状态**: 待实施  
**目标**: 改进权重电阻BOM导出功能，修复格式问题并支持配置化标准化

## 改进需求

### 1. 封装格式修正
- **问题**: 当前封装显示为"0805"，但生成的CSV中变成了"805"
- **要求**: 改为"R0805"格式
- **原因**: 符合电子行业标准命名规范

### 2. 精度格式优化
- **问题**: 
  - 精度显示有两个%%（"0.1%%"）
  - 精度与阻值分开显示在不同列
- **要求**: 精度应该和阻值写在一起，如"100K ±0.1%"
- **原因**: 符合BOM表格标准格式，便于制造商理解

### 3. 配置化标准化支持
- **需求**: 支持在config.json的inference_config中配置BOM导出时的标准化系列
- **功能**: 
  - 在inference_config中添加bom_standardization配置项
  - 支持E6/E12/E24/E96/E192标准系列
  - BOM导出前自动将电阻值标准化到指定系列
- **原因**: 实际制造时需要使用标准电阻值

## 技术分析

### 当前架构
```
CLI参数 → task_dispatcher → ResistanceTaskHandler → WeightResistorBOMGenerator
                                    ↓
                          ResistanceStandardizer (标准化)
```

### 配置传递路径
```
config.json → Config类 → task_dispatcher → ResistanceTaskHandler → BOM生成
```

## 详细修改方案

### 1. 修改文件清单

#### 需要修改的文件（7个）

1. **spice_simulator/weight_resistor_bom_generator.py**
   - 修改封装格式处理
   - 改进阻值和精度的组合显示
   - 支持标准化后的值输入

2. **core/tasks/resistance_task.py**
   - 增加标准化预处理逻辑
   - 从config中读取BOM标准化配置
   - 在BOM生成前应用标准化

3. **core/task_dispatcher.py**
   - 传递inference_config中的BOM配置
   - 处理标准化参数

4. **core/cli_parser.py**
   - 修复--bom-tolerance参数的%%问题
   - 添加--bom-standardize参数（可选）

5. **spice_simulator/resistance_standardizer.py**
   - 添加E192系列支持（如需要）
   - 优化标准化算法

6. **projects/WNET5q1h2u6l3/config.json**
   - 添加BOM标准化配置示例

7. **core/config.py**
   - 确保新配置项的正确加载和验证

### 2. 具体修改点

#### 2.1 weight_resistor_bom_generator.py
```python
# 修改点1: 封装格式处理（第120行附近）
# 原代码:
weight_df['Package'] = self.package

# 修改为:
weight_df['Package'] = f"R{self.package}" if not self.package.startswith('R') else self.package

# 修改点2: 合并阻值和精度显示（第124-127行）
# 原代码:
weight_df['Value(Ω)'] = weight_df['value'].apply(self._format_resistance_value)
bom_columns = ['Symbol', 'Package', 'Value(Ω)', 'Tolerance']

# 修改为:
weight_df['Value'] = weight_df['value'].apply(
    lambda v: self._format_resistance_with_tolerance(v, self.tolerance)
)
bom_columns = ['Symbol', 'Package', 'Value']

# 修改点3: 新增格式化方法
def _format_resistance_with_tolerance(self, value: float, tolerance: str) -> str:
    """格式化电阻值，包含精度"""
    # 先格式化阻值
    formatted_value = self._format_resistance_value(value)
    # 修复双%%问题并组合
    tolerance_clean = tolerance.replace('%%', '%')
    return f"{formatted_value} ±{tolerance_clean}"
```

#### 2.2 resistance_task.py
```python
# 修改点1: 在export_resistances方法中添加标准化逻辑（第148行前）
# 在生成BOM前检查是否需要标准化
if generate_bom:
    # 检查config中的BOM标准化配置
    bom_standardization = None
    if self.config and self.config.get('inference_config'):
        bom_config_from_json = self.config['inference_config'].get('bom_config', {})
        bom_standardization = bom_config_from_json.get('standardization_series')
    
    # 如果配置了标准化，先对CSV进行标准化
    if bom_standardization:
        logger.info(f"Applying {bom_standardization} standardization before BOM generation")
        # 读取刚保存的CSV
        df = pd.read_csv(output_path)
        # 应用标准化
        df_standardized = self.standardizer.standardize_dataframe(
            df, 
            series_list=[bom_standardization]
        )
        # 将标准化值替换原始值
        df['value'] = df_standardized[f'Standardized_{bom_standardization}']
        # 重新保存（或使用临时文件）
        standardized_csv_path = output_path.replace('.csv', f'_{bom_standardization}.csv')
        df.to_csv(standardized_csv_path, index=False)
        # 更新BOM生成的输入路径
        bom_input_path = standardized_csv_path
    else:
        bom_input_path = output_path
```

#### 2.3 task_dispatcher.py
```python
# 修改点1: 从config中读取BOM配置（第203行附近）
if generate_bom:
    bom_config = {
        'package': _get_arg_value(args, 'bom_package', '0805'),
        'tolerance': _get_arg_value(args, 'bom_tolerance', '0.1%')
    }
    
    # 从项目config中读取BOM标准化配置
    config = handler.config  # 假设handler有config属性
    if config and config.get('inference_config'):
        inference_config = config['inference_config']
        if 'bom_config' in inference_config:
            # 合并配置，CLI参数优先
            bom_config.update(inference_config['bom_config'])
```

#### 2.4 cli_parser.py
```python
# 修改点1: 修复双%%问题（第290行）
# 原代码:
resistance_group.add_argument('--bom-tolerance', type=str, default='0.1%%',
                             help='BOM精度规格（默认: 0.1%%）')

# 修改为:
resistance_group.add_argument('--bom-tolerance', type=str, default='0.1%',
                             help='BOM精度规格（默认: 0.1%）')

# 修改点2: 添加标准化参数（可选）
resistance_group.add_argument('--bom-standardize', type=str,
                             choices=['E6', 'E12', 'E24', 'E96', 'E192'],
                             help='BOM导出时使用的标准化系列')
```

#### 2.5 resistance_standardizer.py
```python
# 修改点1: 添加E192系列支持（第18行后）
# E192系列（0.5%精度）- 192个值
E192_VALUES = [
    1.00, 1.01, 1.02, 1.04, 1.05, 1.06, 1.07, 1.09, 1.10, 1.11, 1.13, 1.14,
    # ... 完整的192个值
]

# 修改点2: 更新SERIES字典（第34行）
SERIES = {
    'E6': E6_VALUES,
    'E12': E12_VALUES,
    'E24': E24_VALUES,
    'E96': E96_VALUES,
    'E192': E192_VALUES  # 新增
}
```

#### 2.6 config.json示例
```json
{
  "inference_config": {
    "power_supply": {
      "vcc": 8.0,
      "vee": -8.0
    },
    "bom_config": {
      "standardization_series": "E96",
      "package": "0805",
      "tolerance": "0.1%",
      "auto_standardize": true
    },
    // ... 其他配置
  }
}
```

## 实施步骤

### 第一阶段：格式修复（2小时）
1. 修复封装格式（0805→R0805）
2. 修复精度双%%问题
3. 合并阻值和精度显示
4. 测试验证格式输出

### 第二阶段：标准化集成（3小时）
1. 实现BOM生成前的标准化预处理
2. 添加E192系列支持（如需要）
3. 优化标准化性能
4. 测试标准化功能

### 第三阶段：配置化支持（2小时）
1. 扩展config.json结构
2. 实现配置加载和验证
3. 集成CLI参数与配置文件
4. 测试配置优先级

### 第四阶段：测试与文档（1小时）
1. 端到端测试所有改进
2. 更新用户文档
3. 更新代码注释
4. 创建使用示例

## 预期效果

### 改进前
```csv
Symbol,Package,Value(Ω),Tolerance
R1,0805,1000M,0.1%%
R2,0805,484.09,0.1%%
```

### 改进后
```csv
Symbol,Package,Value
R1,R0805,1000M ±0.1%
R2,R0805,487 ±0.1%  # 如果启用E96标准化
```

## 配置示例

### config.json配置
```json
"bom_config": {
  "standardization_series": "E96",
  "package": "0805",
  "tolerance": "0.1%",
  "auto_standardize": true
}
```

### CLI命令示例
```bash
# 使用默认配置
python cli.py -r WNET5q1h2u6l3 --bom

# 覆盖配置
python cli.py -r WNET5q1h2u6l3 --bom --bom-standardize E24 --bom-package 0603

# 不使用标准化
python cli.py -r WNET5q1h2u6l3 --bom --no-standardize
```

## 风险评估

1. **兼容性风险**: 修改BOM格式可能影响下游工具
   - 缓解措施: 提供格式选项开关

2. **标准化误差**: 标准化可能改变电路性能
   - 缓解措施: 记录标准化误差，提供误差报告

3. **配置复杂性**: 增加配置选项可能使用户困惑
   - 缓解措施: 提供合理默认值，详细文档

## 总结

本改进计划将：
1. 修复现有格式问题，提升BOM质量
2. 支持配置化标准化，满足制造需求
3. 保持向后兼容，提供灵活选项

预计总工时：8小时（1个工作日）