# BOM格式标准化改造计划（简化版）

## 执行概要
- **计划日期**: 2025-08-21
- **目标**: 将当前BOM输出格式改为标准PCB制造格式
- **核心改动**: 仅修改列名并添加Quantity列（固定值1）
- **预计耗时**: 15-30分钟
- **影响范围**: 仅影响BOM CSV输出格式，不影响其他功能

## 1. 背景与动机

### 1.1 当前状态
当前BOM生成功能输出格式：
```csv
Symbol,Package,Value
R1,R0805,52.300kΩ ±0.1%
R2,R0805,1000MΩ ±0.1%
```

### 1.2 目标格式
标准PCB制造BOM格式：
```csv
Designator,Footprint,Quantity,Value
R1,R0805,1,52.300kΩ ±0.1%
R2,R0805,1,1000MΩ ±0.1%
```

### 1.3 改造必要性
1. **行业标准兼容性** - 新格式符合KiCad、Altium等主流EDA工具的BOM标准
2. **制造流程集成** - 便于直接导入SMT贴片机和采购系统
3. **数量字段必需** - 即使固定为1，Quantity列是标准BOM格式的必需字段
4. **术语规范化** - Designator/Footprint是PCB行业标准术语

### 1.4 重要说明
- **不做值合并**: 每个电阻保持独立一行，Quantity始终为1
- **保持现有编号**: 继续支持sequential和grouped两种编号模式
- **grouped含义澄清**: grouped指按功能分组编号（bias→input），不是指相同值合并

## 2. 技术分析

### 2.1 当前实现架构

```
cli.py 
  ↓
task_dispatcher.py (_handle_export_resistance_task)
  ↓
resistance_task.py (export_resistances with generate_bom=True)
  ↓
weight_resistor_bom_generator.py (WeightResistorBOMGenerator)
  ↓
CSV输出 (Symbol, Package, Value)
```

### 2.2 核心修改点

**主文件**: `spice_simulator/weight_resistor_bom_generator.py`

**关键代码位置**:
- 第126-127行: 符号列生成 (`weight_df['Symbol']`)
- 第130行: 封装列生成 (`weight_df['Package']`)
- 第134-136行: 值列生成 (`weight_df['Value']`)
- 第139行: 输出列定义 (`bom_columns = ['Symbol', 'Package', 'Value']`)
- 第154行: BOM DataFrame创建 (`bom_df = weight_df[bom_columns]`)

### 2.3 格式对比分析

| 当前列名 | 新列名 | 数据变化 | 实现难度 |
|---------|--------|----------|----------|
| Symbol | Designator | 仅列名变化 | 简单 |
| Package | Footprint | 仅列名变化 | 简单 |
| - | Quantity | 新增列，固定值"1" | 简单 |
| Value | Value | 无变化 | 无 |

### 2.4 简化后的实施方案

**单一格式方案**：
- 每个电阻保持独立一行
- Quantity列固定为1
- 仅修改列名映射
- 不涉及任何合并逻辑

**与现有功能的关系**：
- **numbering_mode='sequential'**: 按原始顺序编号（默认）
- **numbering_mode='grouped'**: 按功能分组编号（bias→input顺序）
- 两种编号模式都输出相同的BOM格式，只是R编号顺序不同

## 3. 实施方案（极简版）

### 3.1 核心改动

**修改文件**: `spice_simulator/weight_resistor_bom_generator.py`

**具体修改位置和内容**：

#### 修改点1：第126-127行（列名变更）
```python
# 原代码：
weight_df['Symbol'] = [f"{self.symbol_prefix}{i+1}" 
                      for i in range(len(weight_df))]

# 改为：
weight_df['Designator'] = [f"{self.symbol_prefix}{i+1}" 
                           for i in range(len(weight_df))]
```

#### 修改点2：第130行（列名变更）
```python
# 原代码：
weight_df['Package'] = f"R{self.package}" if not self.package.startswith('R') else self.package

# 改为：
weight_df['Footprint'] = f"R{self.package}" if not self.package.startswith('R') else self.package
```

#### 修改点3：第131行后（新增Quantity列）
```python
# 在第131行后新增：
weight_df['Quantity'] = 1  # 每个电阻数量固定为1
```

#### 修改点4：第139行（输出列更新）
```python
# 原代码：
bom_columns = ['Symbol', 'Package', 'Value']

# 改为：
bom_columns = ['Designator', 'Footprint', 'Quantity', 'Value']
```

#### 修改点5：第142-145行（可选列名更新）
```python
# 如果include_original_name为True，调整列顺序
if self.include_original_name:
    weight_df['Original_Name'] = weight_df['name']
    bom_columns = ['Designator', 'Footprint', 'Quantity', 'Value', 'Original_Name']
```

### 3.2 为什么不需要复杂方案

用户明确要求：
- **不做相同值合并**
- **Quantity始终为1**
- **每个电阻独立一行**

因此删除了所有关于合并的复杂逻辑，仅保留最简单的列名修改方案。

## 4. 实施步骤

### 实施步骤（总计15分钟）
1. [ ] 备份`weight_resistor_bom_generator.py`（1分钟）
2. [ ] 执行5个修改点（5分钟）
3. [ ] 运行测试命令验证（5分钟）
4. [ ] 检查输出格式（2分钟）
5. [ ] 提交代码（2分钟）

### 文档更新（5分钟）
1. ✅ 更新用户使用说明
2. ✅ 记录格式变更
3. ✅ 更新示例输出

## 5. 测试验证

### 5.1 功能测试
```bash
# 生成新格式BOM
python cli.py -r WNET5q1h2u6l3 --bom

# 验证输出格式
head projects/WNET5q1h2u6l3/data/resistance_tables/all_layers_resistances_bom.csv
```

### 5.2 预期输出验证
```csv
Designator,Footprint,Quantity,Value
R1,R0805,1,52.300kΩ ±0.1%
R2,R0805,1,1000MΩ ±0.1%
R3,R0805,1,1000MΩ ±0.1%
...
```

### 5.3 兼容性测试
- [ ] KiCad导入测试
- [ ] Excel打开测试
- [ ] 数值精度保持测试
- [ ] 特殊字符处理测试

## 6. 风险评估

### 6.1 极低风险
- **改动最小化** - 仅修改4个字符串（列名）和添加1列
- **数据不变** - 电阻值、编号逻辑完全不变
- **功能不变** - sequential/grouped编号模式继续正常工作

### 6.2 无风险点
- **无合并逻辑** - 不涉及复杂的数据处理
- **无配置变更** - 不需要修改配置文件
- **无CLI变更** - 不需要修改命令行参数

## 7. 回滚方案

如需回滚：
1. 恢复`weight_resistor_bom_generator.py`备份
2. 删除新生成的BOM文件
3. 重新运行BOM生成命令

## 8. 简化后的总结

### 8.1 实际改动内容
仅需修改`weight_resistor_bom_generator.py`中的5处：
1. `Symbol` → `Designator`（第126行）
2. `Package` → `Footprint`（第130行）
3. 添加 `weight_df['Quantity'] = 1`（第131行后）
4. 更新 `bom_columns` 列表（第139行）
5. 调整可选列处理（第142-145行，如果使用）

### 8.2 不涉及的内容
- 不修改编号逻辑（sequential/grouped保持不变）
- 不做数据合并
- 不添加新配置
- 不修改CLI参数

## 9. 执行清单

- [x] 技术调研完成
- [x] 方案设计完成
- [ ] 代码修改
- [ ] 功能测试
- [ ] 文档更新
- [ ] 用户通知

## 10. 结论

本次BOM格式改造已**极度简化**：
- **改动极小** - 仅修改5处字符串和添加1行代码
- **风险极低** - 不涉及任何复杂逻辑
- **立即可用** - 15分钟内完成全部改造
- **完全满足需求** - Designator/Footprint/Quantity/Value格式，Quantity固定为1

**核心要点**：
- `numbering_mode='grouped'` 是指按功能分组编号（bias→input），不是值合并
- 新格式每个电阻保持独立一行，不做任何合并
- 仅改列名和添加Quantity=1，其他一切保持不变