# 权重电阻BOM导出功能实现计划

## 背景和目标

### 背景说明
当前系统已实现统一电阻计算架构，可以导出所有层的完整电阻值到CSV文件。电阻记录包含多种类型：
- `weight`：权重电阻（神经网络权重矩阵对应的电阻）
- `bias`：偏置电阻
- 其他类型：高通滤波器电阻等

在实际PCB制造中，权重电阻是主要的BOM（物料清单）组成部分，需要单独导出用于采购和贴装。

### 功能目标
1. **权重电阻筛选**：从完整CSV中提取`type='weight'`的电阻
2. **BOM格式化**：生成符合制造要求的BOM格式CSV，包含：
   - 重新编号的符号（R1, R2, R3...）
   - 封装规格（如0805）
   - 阻值
   - 精度规格（如0.1%）
3. **可配置性**：封装和精度通过配置文件或命令行参数指定
4. **向后兼容**：不改变现有导出流程，作为后处理步骤

## 技术方案

### 1. 系统架构设计

#### 1.1 核心组件
```
ResistanceTaskHandler (现有)
    ├── export_resistances() (现有完整导出)
    └── export_weight_resistor_bom() (新增BOM导出)
            └── WeightResistorBOMGenerator (新增类)
                    ├── filter_weight_resistors()
                    ├── renumber_symbols()
                    ├── add_bom_fields()
                    └── save_bom_csv()
```

#### 1.2 数据流程
```
1. 完整CSV生成（现有流程）
   UnifiedResistanceCalculator → ResistanceExtractor → CSV文件

2. BOM后处理（新增流程）
   CSV文件 → WeightResistorBOMGenerator → 权重电阻BOM CSV
```

### 2. 详细设计

#### 2.1 WeightResistorBOMGenerator类
```python
class WeightResistorBOMGenerator:
    """权重电阻BOM生成器"""
    
    def __init__(self, bom_config=None):
        """
        Args:
            bom_config: BOM配置字典
                - package: 封装规格（默认"0805"）
                - tolerance: 精度规格（默认"0.1%"）
                - symbol_prefix: 符号前缀（默认"R"）
        """
        self.package = bom_config.get('package', '0805')
        self.tolerance = bom_config.get('tolerance', '0.1%')
        self.symbol_prefix = bom_config.get('symbol_prefix', 'R')
    
    def generate_bom_from_csv(self, input_csv_path, output_csv_path):
        """从完整CSV生成权重电阻BOM"""
        # 1. 读取完整CSV
        df = pd.read_csv(input_csv_path)
        
        # 2. 筛选权重电阻
        weight_df = df[df['type'] == 'weight'].copy()
        
        # 3. 重新编号
        weight_df['symbol'] = [f"{self.symbol_prefix}{i+1}" 
                               for i in range(len(weight_df))]
        
        # 4. 添加BOM字段
        weight_df['package'] = self.package
        weight_df['tolerance'] = self.tolerance
        
        # 5. 选择BOM所需列
        bom_df = weight_df[['symbol', 'package', 'value', 'tolerance']]
        bom_df.columns = ['Symbol', 'Package', 'Value(Ω)', 'Tolerance']
        
        # 6. 保存BOM CSV
        bom_df.to_csv(output_csv_path, index=False)
        
        return len(bom_df)
```

#### 2.2 配置结构
```json
// inference_config.json中添加
{
    "bom_config": {
        "enabled": true,
        "package": "0805",        // 封装规格
        "tolerance": "0.1%",       // 精度规格
        "symbol_prefix": "R",      // 符号前缀
        "export_path": "weight_resistor_bom.csv"  // 输出文件名
    }
}
```

#### 2.3 CLI参数扩展
```python
# core/cli_parser.py 添加
resistance_group.add_argument('--bom', action='store_true',
                             help='同时生成权重电阻BOM')
resistance_group.add_argument('--bom-package', type=str, default='0805',
                             help='BOM封装规格（默认: 0805）')
resistance_group.add_argument('--bom-tolerance', type=str, default='0.1%',
                             help='BOM精度规格（默认: 0.1%）')
```

### 3. 实现步骤

#### 阶段1：核心功能实现（2小时）
1. 创建`spice_simulator/weight_resistor_bom_generator.py`
2. 实现WeightResistorBOMGenerator类
3. 单元测试

#### 阶段2：集成到ResistanceTaskHandler（1小时）
1. 修改`core/tasks/resistance_task.py`
2. 添加`export_weight_resistor_bom()`方法
3. 在`export_resistances()`中可选调用

#### 阶段3：CLI集成（1小时）
1. 修改`core/cli_parser.py`添加BOM相关参数
2. 修改`cli.py`处理BOM导出逻辑
3. 更新帮助文档

#### 阶段4：测试和调试（2小时）
1. 功能测试：验证BOM生成正确性
2. 边界测试：空数据、大数据集
3. 配置测试：不同封装和精度组合
4. 集成测试：与现有流程兼容性

#### 阶段5：文档和报告（1小时）
1. 更新使用文档
2. 编写测试报告
3. 更新summary.md

### 4. 文件修改清单

#### 新增文件
1. `spice_simulator/weight_resistor_bom_generator.py` - BOM生成器核心类

#### 修改文件
1. `core/tasks/resistance_task.py` - 添加BOM导出方法
2. `core/cli_parser.py` - 添加BOM相关CLI参数
3. `cli.py` - 集成BOM导出逻辑
4. `core/task_dispatcher.py` - 处理BOM导出任务

### 5. 测试计划

#### 5.1 功能测试
```bash
# 基础导出测试
python cli.py -r WNET5q1h2u6l3

# 带BOM导出测试
python cli.py -r WNET5q1h2u6l3 --bom

# 自定义配置测试
python cli.py -r WNET5q1h2u6l3 --bom --bom-package 0603 --bom-tolerance 1%
```

#### 5.2 验证要点
- [ ] 权重电阻数量正确
- [ ] 符号编号连续（R1, R2, ...）
- [ ] 封装和精度字段正确
- [ ] CSV格式符合BOM标准
- [ ] 文件路径和命名正确

#### 5.3 性能要求
- 10000个电阻：< 1秒
- 50000个电阻：< 5秒
- 内存占用：< 100MB

### 6. 风险和缓解

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| 电阻类型识别错误 | BOM不完整或包含错误项 | 添加类型验证和日志 |
| 大数据集性能问题 | 处理缓慢 | 使用DataFrame优化操作 |
| 配置冲突 | 参数覆盖问题 | 明确优先级：CLI > 配置文件 > 默认值 |

### 7. 扩展考虑

#### 未来可能的扩展
1. **多封装支持**：不同阻值范围使用不同封装
2. **成本优化**：根据标准系列和价格优化选型
3. **供应商信息**：添加制造商和料号
4. **分组导出**：按层或通道分组导出
5. **Excel格式**：支持直接导出到Excel

#### 保留接口
- BOMGenerator基类，便于扩展其他类型BOM
- 配置字典结构，便于添加新字段
- 插件式处理流程，便于添加预处理/后处理步骤

### 8. 实施时间表

| 任务 | 预计时间 | 实际时间 | 状态 |
|-----|---------|---------|------|
| 核心功能实现 | 2小时 | - | 待开始 |
| 系统集成 | 1小时 | - | 待开始 |
| CLI集成 | 1小时 | - | 待开始 |
| 测试调试 | 2小时 | - | 待开始 |
| 文档更新 | 1小时 | - | 待开始 |
| **总计** | **7小时** | - | - |

### 9. 成功标准

1. ✅ 能够从完整CSV中准确提取所有权重电阻
2. ✅ BOM格式符合制造要求，包含必要字段
3. ✅ 支持通过配置和CLI参数自定义封装和精度
4. ✅ 不影响现有导出功能，完全向后兼容
5. ✅ 性能满足要求，处理50000个电阻<5秒
6. ✅ 通过所有测试用例，无回归问题

## 附录：示例输出

### 输入CSV示例（部分）
```csv
layer,channel,type,index,name,value,unit
layer2,1,weight,1,layer2_ch1_R_weight1,1234.5,Ω
layer2,1,weight,2,layer2_ch1_R_weight2,2345.6,Ω
layer2,1,bias,1,layer2_ch1_R_bias,10000,Ω
...
```

### 输出BOM CSV示例
```csv
Symbol,Package,Value(Ω),Tolerance
R1,0805,1234.5,0.1%
R2,0805,2345.6,0.1%
R3,0805,3456.7,0.1%
...
```

---
*文档版本：1.0*  
*创建日期：2025-08-20*  
*作者：Claude*