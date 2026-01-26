# 网表存储统一到data/目录详细实施计划

## 1. 执行摘要

### 1.1 背景问题
当前网表文件存储存在严重的路径不一致问题：
- **网表生成**: 保存到 `temp/spice_output/`
- **验证系统**: 查找 `projects/{project}/data/spice_netlists/`
- **结果**: 验证系统完全失效，依赖手动数据填充

### 1.2 目标
将所有SPICE网表文件统一存储到项目的 `data/spice_netlists/` 目录，彻底解决路径不一致问题。

### 1.3 核心原则
- **统一性**: 所有网表一律存储在 `data/spice_netlists/`
- **简洁性**: 移除时间戳版本等复杂机制
- **兼容性**: 保持API向后兼容
- **可验证性**: 确保验证系统能正确工作

## 2. 修改文件清单

### 2.1 核心文件修改（必须）

#### **File 1: `inference/wavenet5_spice_backend.py`**
**当前问题**: 默认输出到 `./temp/spice_output`
**修改内容**:
```python
# Line 26 - 修改默认输出路径
- def __init__(self, model=None, output_folder='./temp/spice_output', ngspice_path=None, inference_config=None):
+ def __init__(self, model=None, output_folder=None, ngspice_path=None, inference_config=None):
    
    # 新增智能路径处理
    if output_folder is None:
        # 尝试从模型获取项目路径
        if hasattr(model, 'project_path'):
            output_folder = os.path.join(model.project_path, 'data', 'spice_netlists')
        else:
            # 使用当前项目的默认路径
            output_folder = os.path.join('data', 'spice_netlists')
    
    # 确保目录存在
    os.makedirs(output_folder, exist_ok=True)
    self.output_folder = output_folder
```

#### **File 2: `inference/backends/spice/backend.py`**
**当前问题**: 默认输出到 `./temp`
**修改内容**:
```python
# Line 31 - 修改默认输出路径
- def __init__(self, model=None, output_folder='./temp', ngspice_path=None, inference_config=None):
+ def __init__(self, model=None, output_folder=None, ngspice_path=None, inference_config=None):
    
    # 与WaveNet5SPICEBackend保持一致
    if output_folder is None:
        if hasattr(model, 'project_path'):
            output_folder = os.path.join(model.project_path, 'data', 'spice_netlists')
        else:
            output_folder = os.path.join('data', 'spice_netlists')
    
    os.makedirs(output_folder, exist_ok=True)
    self.output_folder = output_folder
```

#### **File 3: `inference/processing/backend_manager.py`**
**当前问题**: 已有路径生成逻辑但默认仍使用temp
**修改内容**:
```python
# Line 195 - 修改默认fallback路径
def _generate_spice_output_path(self) -> str:
    if self.project_path:
        spice_netlists_dir = os.path.join(self.project_path, 'data', 'spice_netlists')
        logger.info(f"使用项目特定的SPICE网表目录: {spice_netlists_dir}")
        return spice_netlists_dir
    else:
-       logger.info("项目路径未指定，使用temp目录")
-       return os.path.join('temp', 'spice_output')
+       # 使用相对于当前工作目录的data目录
+       logger.info("项目路径未指定，使用默认data目录")
+       return os.path.join('data', 'spice_netlists')
```

#### **File 4: `spice_simulator/spice_path_manager.py`**
**当前问题**: clean_temp_files仍然指向temp目录
**修改内容**:
```python
# Line 50-55 - 更新清理函数
def clean_temp_files(self):
-   """清理临时文件（从temp目录）"""
-   temp_dir = os.path.join('temp', 'spice_output')
-   if os.path.exists(temp_dir):
-       import shutil
-       shutil.rmtree(temp_dir)
+   """清理临时网表文件（保留功能但不再需要）"""
+   # 网表文件现在存储在项目data目录，不需要清理
+   logger.debug("网表文件现已持久化存储，无需清理")
+   pass
```

### 2.2 CLI和推理相关修改

#### **File 5: `inference/cli.py`**
**当前问题**: comparison_dir默认指向temp
**修改内容**:
```python
# Line 21 - 修改默认对比目录
- parser.add_argument('--comparison_dir', type=str, default='inference/temp/spice_comparison', help='SPICE对比数据目录路径')
+ parser.add_argument('--comparison_dir', type=str, default='data/spice_comparison', help='SPICE对比数据目录路径')

# 确保InferenceProcessor获得正确的项目路径
# Line 30 附近
inference_processor = InferenceProcessor(model_path)
# 确保project_path被正确传递
```

#### **File 6: `inference/spice_analysis.py`**
**当前问题**: 默认输出到temp目录
**修改内容**:
```python
# Line 53 - 修改默认输出目录
- def generate_spice_comparison_data(self, input_wave_path: str, output_dir: str='temp/spice_comparison', use_scaler: bool=False):
+ def generate_spice_comparison_data(self, input_wave_path: str, output_dir: str='data/spice_comparison', use_scaler: bool=False):
```

#### **File 7: `inference/processing/inference_processor.py`**
**当前问题**: 默认comparison_dir使用temp
**修改内容**:
```python
# Line 160 - 修改默认输出目录
- output_dir: str = 'temp/spice_comparison'
+ output_dir: str = 'data/spice_comparison'
```

### 2.3 验证系统修复

#### **File 8: `core/tasks/resistance_task.py`**
**当前问题**: 验证系统查找项目目录但网表在temp
**修改内容**:
```python
# Line 401-419 - 加强验证逻辑
def _validate_csv_with_netlists(self, csv_path: str) -> Dict:
    validation_results = {
        'passed': True,
        'layers_validated': [],
        'errors': [],
        'warnings': []
    }
    
    # 查找所有网表文件
    netlist_dir = self.path_manager.netlist_dir
    if not os.path.exists(netlist_dir):
-       logger.warning(f"Netlist directory not found: {netlist_dir}")
-       validation_results['warnings'].append(
-           f"Netlist directory not found: {netlist_dir} - netlists may not be generated yet"
-       )
-       return validation_results
+       # 创建目录并抛出错误
+       os.makedirs(netlist_dir, exist_ok=True)
+       raise FileNotFoundError(
+           f"网表目录不存在且无法创建: {netlist_dir}\n"
+           f"请先运行推理生成网表文件"
+       )
    
    netlist_files = glob.glob(os.path.join(netlist_dir, '*.cir'))
    
    if not netlist_files:
-       logger.warning(f"No netlist files found in {netlist_dir}")
-       validation_results['warnings'].append(
-           f"No netlist files found for validation - netlists may not be generated yet"
-       )
-       return validation_results
+       raise FileNotFoundError(
+           f"网表目录中没有找到.cir文件: {netlist_dir}\n"
+           f"请先运行推理生成网表文件"
+       )
```

### 2.4 测试文件更新

#### **File 9: `spice_simulator/tests/test_simulation.py`**
**修改内容**:
```python
# Line 58
- def __init__(self, output_folder='./temp', ngspice_path=None, max_workers=16, clean_temp_files=True):
+ def __init__(self, output_folder='./data/test_spice_netlists', ngspice_path=None, max_workers=16, clean_temp_files=False):
```

### 2.5 Legacy代码更新（可选但建议）

#### **File 10: `spice_simulator/legacy/simulation_adapter.py`**
```python
# Line 106 - 更新日志路径
- command = [self.sim.ngspice_path, "-b", "-o", f"{temp_dir}/ngspice.log", netlist_file]
+ command = [self.sim.ngspice_path, "-b", "-o", f"{self.output_folder}/ngspice.log", netlist_file]
```

#### **File 11: `spice_simulator/legacy/ngspice_opamp_adder.py`**
```python
# Line 16
- def __init__(self, output_folder='./temp', ngspice_path=None):
+ def __init__(self, output_folder='./data/spice_netlists', ngspice_path=None):
```

#### **File 12: `spice_simulator/legacy/multi_channel_opamp_adder.py`**
```python
# Line 282
- def __init__(self, output_folder='./temp', ngspice_path=None, max_workers=None):
+ def __init__(self, output_folder='./data/spice_netlists', ngspice_path=None, max_workers=None):
```

## 3. 实施步骤

### Phase 1: 核心路径修改（2小时）
1. 修改 `wavenet5_spice_backend.py` 和 `backend.py` 的默认路径
2. 更新 `backend_manager.py` 的fallback逻辑
3. 测试基本推理功能确保网表生成到正确位置

### Phase 2: 验证系统加固（1小时）
1. 修改 `resistance_task.py` 的验证逻辑
2. 移除"礼貌失败"机制，改为严格错误
3. 测试验证功能确保能正确找到网表

### Phase 3: CLI和工具更新（1小时）
1. 更新 `cli.py` 的默认路径
2. 修改 `spice_analysis.py` 和 `inference_processor.py`
3. 清理 `spice_path_manager.py` 的temp相关代码

### Phase 4: 测试和验证（2小时）
1. 运行完整的推理测试
2. 验证网表生成位置
3. 测试CSV-网表一致性验证
4. 检查BOM生成功能

### Phase 5: 文档更新（30分钟）
1. 更新所有文档中的路径引用
2. 更新summary.md记录改动
3. 创建迁移指南

## 4. 测试计划

### 4.1 单元测试
```bash
# 测试网表生成到正确位置
python cli.py --project WNET5q1h2u6l3 --backend spice --quick
ls projects/WNET5q1h2u6l3/data/spice_netlists/*.cir

# 测试验证系统
python cli.py --project WNET5q1h2u6l3 --task export-resistance --validate
```

### 4.2 集成测试
```bash
# 完整推理流程
python cli.py --project WNET5q1h2u6l3 --backend spice --input test.wav

# BOM生成
python cli.py --project WNET5q1h2u6l3 --task export-resistance --bom --bom-mode grouped
```

### 4.3 验证检查清单
- [ ] 网表文件生成到 `data/spice_netlists/`
- [ ] 不再生成到 `temp/spice_output/`
- [ ] 验证系统能找到网表文件
- [ ] 验证失败时抛出明确错误
- [ ] BOM生成功能正常
- [ ] 向后兼容性保持

## 5. 风险评估

### 5.1 主要风险
1. **路径硬编码**: 某些地方可能有硬编码的temp路径
2. **权限问题**: data目录可能需要创建权限
3. **向后兼容**: 旧项目可能依赖temp目录

### 5.2 缓解措施
1. **全面搜索**: 使用grep搜索所有temp/spice相关引用
2. **目录创建**: 使用 `os.makedirs(exist_ok=True)`
3. **迁移脚本**: 提供脚本将旧的temp文件迁移到data

## 6. 回滚计划

如果出现问题，可以通过以下步骤回滚：
1. Git revert相关提交
2. 手动将网表从data目录复制回temp
3. 临时修改验证系统查找两个位置

## 7. 预期收益

### 7.1 立即收益
- **验证系统恢复**: 自动化验证正常工作
- **路径一致性**: 消除路径混乱
- **可维护性提升**: 代码更清晰

### 7.2 长期收益
- **可靠性增强**: 减少隐藏问题
- **开发效率**: 减少调试时间
- **用户信任**: 真实的验证保障

## 8. 实施时间表

| 阶段 | 任务 | 预计时间 | 责任人 |
|-----|------|---------|-------|
| Phase 1 | 核心路径修改 | 2小时 | 开发 |
| Phase 2 | 验证系统加固 | 1小时 | 开发 |
| Phase 3 | CLI工具更新 | 1小时 | 开发 |
| Phase 4 | 测试验证 | 2小时 | QA |
| Phase 5 | 文档更新 | 30分钟 | 文档 |
| **总计** | | **6.5小时** | |

## 9. 成功标准

实施成功的标志：
1. ✅ 所有网表文件生成到 `data/spice_netlists/`
2. ✅ 验证系统能自动找到并验证网表
3. ✅ 没有任何temp/spice_output引用
4. ✅ 所有测试通过
5. ✅ 文档更新完成

---

**创建日期**: 2025-08-21  
**作者**: Claude  
**状态**: 待执行  
**优先级**: 高（修复关键验证问题）