# 根目录整理计划

## 概述
本计划旨在重新组织项目根目录，将相关文件归类到合适的子目录中，提高项目的可维护性和清晰度。

## 目录结构规划

### 1. 保留在根目录的文件
这些是项目的核心入口点和配置文件：
- `ui.py` - GUI主程序入口
- `cli.py` - CLI主程序入口  
- `training.py` - 训练脚本入口
- `config.py` - 核心配置模块
- `metnl.py` - 核心工具库
- `requirements.txt` - 依赖列表
- `pytest.ini` - 测试配置
- `README.md` - 项目说明
- `CLAUDE.md` - AI助手指南
- `.gitignore`, `.gitmodules` - Git配置文件
- `run_tests.py` - 测试运行器

### 2. 新建目录结构

#### `/core/` - 核心功能模块
移入文件：
- `model_engine.py` - 模型训练引擎
- `data_processing.py` - 数据处理核心
- `loss_functions.py` - 损失函数定义
- `training_state.py` - 训练状态管理
- `training_log.py` - 训练日志系统

#### `/inference/` - 推理和导出工具
移入文件：
- `inference.py` - 推理处理器
- `inference_backends.py` - 推理后端实现
- `export_svf_to_spice.py` - SVF到SPICE导出
- `lstm2c.py` - LSTM到C代码导出

#### `/visualization/` - 可视化和分析工具
移入文件：
- `data_viewer.py` - 数据查看器
- `figure_paper.py` - 论文图表生成
- `model_analysis.py` - 模型分析工具
- `image_data_process.py` - 图像数据处理

#### `/utils/` - 通用工具函数
移入文件：
- `sample_list.py` - 列表采样工具
- `grid_log.py` - 网格生成工具
- `test_config.py` - 测试配置

#### `/simulation/` - 仿真相关工具
移入文件：
- `simu_sweep.py` - 扫频仿真
- `simu_svf_sweep.py` - SVF扫频仿真
- `analyze_tanh_bias_feasibility.py` - tanh偏置分析

#### `/experimental/` - 实验性和特殊功能
移入文件：
- `kan_lut.py` - KAN查找表实现
- `mimoiir.py` - MIMO IIR滤波器
- `analyze_imports.py` - 导入分析工具
- `verify_report_data.py` - 报告数据验证

### 3. 需要更新的导入路径

#### 核心模块导入更新
```python
# 原始导入
import model_engine
import data_processing
import training_state
import training_log
import loss_functions

# 更新后
from core import model_engine
from core import data_processing
from core import training_state
from core import training_log
from core import loss_functions
```

#### 推理模块导入更新
```python
# 原始导入
import inference
import inference_backends

# 更新后
from inference import inference
from inference import inference_backends
```

#### 可视化模块导入更新
```python
# 原始导入
import data_viewer
import figure_paper
import model_analysis

# 更新后
from visualization import data_viewer
from visualization import figure_paper
from visualization import model_analysis
```

### 4. 需要修改导入的文件列表

#### 高优先级（核心功能，多处引用）
1. **`cli.py`**
   - 导入：`model_engine`, `training`, `training_log`, `training_state`
   
2. **`ui.py`**
   - 导入：`data_viewer`
   
3. **`training.py`**
   - 导入：`training_state`, `training_log`

#### 中优先级（功能模块间引用）
4. **`core/model_engine.py`** (移动后)
   - 导入：`data_processing`, `model_analysis`, `loss_functions`, `training`, `training_state`, `training_log`
   
5. **`inference/inference.py`** (移动后)
   - 导入：`model_engine`
   
6. **`inference/inference_backends.py`** (移动后)
   - 内部引用需要调整

7. **`visualization/figure_paper.py`** (移动后)
   - 导入：`training_log`

#### 低优先级（独立工具）
8. **`simulation/simu_sweep.py`** (移动后)
   - 已通过sys.path添加路径，可能需要调整
   
9. **`simulation/simu_svf_sweep.py`** (移动后)
   - 同上

### 5. 实施步骤

1. **创建新目录结构**
   ```bash
   mkdir -p core inference visualization utils simulation experimental
   ```

2. **在各目录创建 __init__.py**
   ```bash
   touch core/__init__.py inference/__init__.py visualization/__init__.py 
   touch utils/__init__.py simulation/__init__.py experimental/__init__.py
   ```

3. **批量移动文件**（见下方脚本）

4. **更新导入语句**（按优先级逐个文件修改）

5. **运行测试验证**
   ```bash
   python run_tests.py
   ```

### 6. 移动脚本

```bash
#!/bin/bash
# 核心模块
mv model_engine.py core/
mv data_processing.py core/
mv loss_functions.py core/
mv training_state.py core/
mv training_log.py core/

# 推理模块
mv inference.py inference/
mv inference_backends.py inference/
mv export_svf_to_spice.py inference/
mv lstm2c.py inference/

# 可视化模块
mv data_viewer.py visualization/
mv figure_paper.py visualization/
mv model_analysis.py visualization/
mv image_data_process.py visualization/

# 工具模块
mv sample_list.py utils/
mv grid_log.py utils/
mv test_config.py utils/

# 仿真模块
mv simu_sweep.py simulation/
mv simu_svf_sweep.py simulation/
mv analyze_tanh_bias_feasibility.py simulation/

# 实验性模块
mv kan_lut.py experimental/
mv mimoiir.py experimental/
mv analyze_imports.py experimental/
mv verify_report_data.py experimental/
```

### 7. 风险和注意事项

1. **动态路径添加**：一些文件使用 `sys.path.append()` 添加路径，需要检查并更新
2. **相对导入**：确保所有相对导入在新结构中仍然有效
3. **外部依赖**：`calibration_analyzer` 等外部模块的导入不受影响
4. **测试覆盖**：确保所有测试在重组后仍能正常运行
5. **版本控制**：建议在单独的分支上进行重组，确保可以回滚

### 8. 额外建议

1. **创建 setup.py**：使项目可以作为包安装，简化导入
2. **统一导入风格**：建议使用绝对导入而非相对导入
3. **文档更新**：更新 README.md 和 CLAUDE.md 中的文件路径引用
4. **CI/CD 更新**：如果有自动化流程，需要更新相关配置

## 预期效果

重组后的项目结构将：
- ✅ 更清晰的模块划分
- ✅ 更容易找到相关功能
- ✅ 减少根目录的混乱
- ✅ 便于新开发者理解项目结构
- ✅ 支持未来的模块化扩展