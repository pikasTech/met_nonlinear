# 旧格式和兼容代码清理清单

## 高优先级清理项目

### 1. `/inference/management/report_generator.py`
**需要清理的内容：**
- [ ] 删除 `_print_bias_matrix_summary` 函数（第336-357行）- 旧格式兼容
- [ ] 删除兼容模式处理（第55-58行）- 旧格式结果处理
- [ ] 删除 `_format_bias_matrix_report` 中的旧格式引用（第390-391行）
- [ ] 更新所有对 'statistics' 的引用为 'global_statistics'（第345行）

### 2. `/tests/inference/test_bias_analyzer.py`
**需要清理的内容：**
- [ ] 更新测试以使用新格式而非旧的 'matrix_shape'（第429, 433-434行）
- [ ] 更新对 'statistics' 的引用为 'global_statistics'（第430行）
- [ ] 删除所有旧格式验证逻辑

## 中优先级清理项目

### 3. `/tests/test_bias_analyzer_fix.py`
**需要清理的内容：**
- [ ] 更新中文注释，移除"规则"相关术语（第104行）
- [ ] 重命名不规则相关的变量名称

### 4. `/inference/wavenet5_spice_backend.py`
**需要清理的内容：**
- [ ] 更新中文注释，移除"规则"相关术语（第113行）

### 5. `/inference/backends/spice/phase_correction.py`
**需要清理的内容：**
- [ ] 更新中文注释中的"修正规则"为更合适的术语（第78行）

## 低优先级清理项目

### 6. `/scripts/validate_refactor_results.py`
**需要清理的内容：**
- [ ] 更新以处理新格式（如果需要）（第54行）

### 7. `/archive/legacy/obs_data.py`
**注意：** 这是归档文件，可能不需要修改

## 清理原则

1. **完全移除旧格式支持**
   - 删除所有 `matrix_shape` 相关代码
   - 删除所有 `n_layers`, `n_channels` 的旧格式引用
   - 使用新的 `layer_count`, `channels_per_layer` 格式

2. **更新数据结构引用**
   - 将 'statistics' 改为 'global_statistics'
   - 确保使用嵌套列表格式而非规则矩阵

3. **清理中文术语**
   - 移除"规则"/"不规则"相关术语
   - 使用"每层通道数"等更准确的描述

4. **保持接口一致性**
   - 确保所有清理不破坏现有功能
   - 运行测试验证功能完整性

## 验证步骤

每次清理后运行以下命令验证：
```bash
# 运行偏置分析
conda run -n tf26 python cli.py -a

# 运行相关测试
conda run -n tf26 pytest tests/test_bias_analyzer_fix.py -v
conda run -n tf26 pytest tests/inference/test_bias_analyzer.py -v
```