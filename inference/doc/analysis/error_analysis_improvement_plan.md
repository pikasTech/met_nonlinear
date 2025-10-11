# 误差分析功能改进实施计划

## 需求概述

1. **代码组织优化**：将误差分析逻辑从 `cli.py` 转移到独立模块，保持顶级入口文件的简洁性
2. **双重误差分析**：增加 NN-NumPy 和 NN-SPICE 两种误差分析，生成独立的误差目录

## 实施阶段

### 第一阶段：误差分析逻辑迁移

#### 目标
将 `analyze_errors` 的实现逻辑完全迁移到 `InferenceManager`，`cli.py` 仅保留简单调用。

#### 当前状态
- `cli.py` 的 `analyze_errors` 方法已经委托给 `InferenceManager`
- 但 `InferenceManager` 中的 `_analyze_inference_errors` 仍然只支持单一的 NN-SPICE 对比

#### 修改文件清单

1. **inference/manager.py**
   - 无需修改，现有代码结构已经满足需求
   - `analyze_errors()` 已经是完整的误差分析入口
   - `_analyze_inference_errors()` 已经包含所有误差分析逻辑

2. **cli.py**
   - 无需修改，已经是简单的委托调用：
     ```python
     def analyze_errors(self):
         """委托给推理管理器"""
         self.inference_manager.analyze_errors()
     ```

#### 测试步骤
```bash
# 确认误差分析功能正常工作
python cli.py -a WNET5q0.5h2u6l3

# 检查输出目录结构
ls -la projects/WNET5q0.5h2u6l3/data/inference/
# 应该看到：error_layers/
```

### 第二阶段：实现双重误差分析

#### 目标
支持 NN-NumPy 和 NN-SPICE 两种误差分析，生成独立的误差目录。

#### 修改文件清单

1. **inference/manager.py**
   
   **修改点1：`_check_existing_inference_data` 方法**
   - 增加对 numpy_layers 目录的检查逻辑
   - 返回更详细的状态信息（哪些层类型存在）

   **修改点2：`_analyze_inference_errors` 方法（主要修改）**
   - 重构以支持多种对比类型
   - 创建两个误差目录：`nn_spice_error_layers/` 和 `nn_numpy_error_layers/`
   - 分别计算 NN-SPICE 和 NN-NumPy 的误差（如果 numpy_layers 存在）
   - 更新返回的 analysis_results 结构，包含两种误差分析

   **修改点3：`_generate_analysis_report` 方法**
   - 扩展报告生成逻辑，分别显示两种误差分析的结果
   - 添加对比表格，展示两种误差的差异

2. **新增辅助方法（在 inference/manager.py 中）**
   
   **新增方法：`_compute_layer_errors`**
   ```python
   def _compute_layer_errors(self, reference_dir, comparison_dir, error_dir_name, comparison_type):
       """
       计算两个推理结果之间的逐层误差
       
       参数:
           reference_dir: 参考数据目录（通常是 nn_layers）
           comparison_dir: 对比数据目录（spice_layers 或 numpy_layers）
           error_dir_name: 误差输出目录名
           comparison_type: 对比类型字符串（用于描述）
       
       返回:
           layer_errors: 包含逐层误差统计的列表
       """
   ```

3. **数据结构更新**
   
   **analysis_results 结构扩展**：
   ```python
   {
       "project_name": "...",
       "timestamp": "...",
       "nn_spice_analysis": {
           "layer_analysis": [...],
           "validation_info": {...}
       },
       "nn_numpy_analysis": {
           "layer_analysis": [...],
           "validation_info": {...}
       },
       "comparison_summary": {
           "has_numpy": True/False,
           "comparison_types": ["nn_spice", "nn_numpy"]
       }
   }
   ```

#### 实现细节

1. **目录结构变更**
   ```
   inference/
   ├── nn_layers/
   ├── spice_layers/
   ├── numpy_layers/
   ├── nn_spice_error_layers/    # 新增
   │   └── layer_1.wave ... layer_5.wave
   ├── nn_numpy_error_layers/    # 新增（如果有numpy_layers）
   │   └── layer_1.wave ... layer_5.wave
   └── error_analysis.json       # 更新格式
   ```

2. **兼容性考虑**
   - 如果没有 numpy_layers，只生成 nn_spice_error_layers
   - 保持向后兼容，旧的推理数据仍能正常分析
   - error_analysis.json 采用新格式，但包含足够信息供旧代码解析

3. **性能优化**
   - 重用文件加载逻辑，避免重复读取相同的 nn_layers 数据
   - 并行处理两种误差分析（如果需要）

#### 测试步骤

```bash
# 1. 清理旧的推理数据
rm -rf projects/WNET5q0.5h2u6l3/data/inference/

# 2. 生成新的推理数据（包含numpy_layers）
python cli.py -i WNET5q0.5h2u6l3

# 3. 执行误差分析
python cli.py -a WNET5q0.5h2u6l3

# 4. 验证输出
ls -la projects/WNET5q0.5h2u6l3/data/inference/
# 应该看到：
# - nn_spice_error_layers/
# - nn_numpy_error_layers/（如果有numpy仿真）
# - error_analysis.json（新格式）
```

## 代码量估计

### 第一阶段
- 无需修改代码，仅需测试验证

### 第二阶段
- 修改 `_analyze_inference_errors`: 约150行代码重构
- 新增 `_compute_layer_errors`: 约80行新代码
- 修改 `_generate_analysis_report`: 约30行代码修改
- 总计：约260行代码变更

## 风险评估

1. **低风险**：第一阶段无需修改，仅验证
2. **中等风险**：第二阶段需要重构核心误差分析逻辑
3. **缓解措施**：
   - 保持原有API不变
   - 充分测试各种场景（有/无numpy_layers）
   - 保留详细的错误日志

## 时间安排

1. 第一阶段：立即执行测试验证（5分钟）
2. 第一阶段提交：确认测试通过后提交
3. 第二阶段：实现双重误差分析（30-45分钟）
4. 第二阶段测试：全面测试（15分钟）
5. 第二阶段提交：测试通过后提交

## 成功标准

1. **第一阶段**：
   - `python cli.py -a` 正常工作
   - 生成 error_layers 目录和 error_analysis.json

2. **第二阶段**：
   - 生成两个独立的误差目录
   - error_analysis.json 包含两种误差分析结果
   - 向后兼容旧的推理数据
   - 清晰的误差对比报告