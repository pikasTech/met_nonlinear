# AGENTS.md - Agentic Coding Guidelines

## 项目概述

**MET Nonlinear** - 电化学非线性矫正项目。核心模块: `models/`, `tfkan/`, `analysis/`, `visualization/`, `calibration_analyzer/`

---

## CLI 命令 (cli.py)

### 主命令

```bash
# 训练模型
python cli.py -t PROJECT_NAME

# 评估模型
python cli.py -e PROJECT_NAME

# 运行推理
python cli.py -i PROJECT_NAME --layers 5

# 分析误差
python cli.py -a PROJECT_NAME --bias-method auto

# 清理项目数据
python cli.py -c PROJECT_NAME

# 波形生成
python cli.py -w PROJECT_NAME

# 偏置可视化
python cli.py --bias-viz PROJECT_NAME

# 导出电阻值
python cli.py -r PROJECT_NAME

# 标准化电阻
python cli.py -s PROJECT_NAME --series E96 E24

# 绘制loss曲线
python cli.py --loss-plot PROJECT_NAME
```

### ep 子命令 (外部项目)

```bash
# 频率响应对比
python cli.py ep "PROJECT/task-type/task-name"

# WNET5电路验证
python cli.py ep "PROJECT/wnet5-circuit-validation/layer2"

# 补偿器频率响应
python cli.py ep "PROJECT/freq-response-compensator/test"
```

### ep 路径格式

| 格式 | 示例 |
|------|------|
| 外部项目 | `external/projects/freq-response-compare/PS-5-190_vs_PS-5-360` |
| 训练项目 | `LSTMu32al_rs300/freq-response-compare/baseline-comparison` |
| 简化格式 | `PROJECT/task-name` (自动检测任务类型) |

### 测试命令

```bash
# 运行单元测试
python cli.py --test

# 指定测试路径
python cli.py --test --test-path src/logger/tests

# 并行测试配置
python cli.py --test --test-workers 4 --test-timeout 300
```

---

## 代码风格

### 格式化

- **Formatter**: `autopep8` (VS Code配置)
- **Python Language Server**: Jedi
- **缩进**: 4空格
- **行长**: PEP 8标准（最大79字符）

### 导入顺序

```python
# 1. 标准库
import os, sys, json, logging
from typing import Tuple, List, Any, Union, Callable, Optional, Dict
from enum import Enum
from dataclasses import dataclass, field

# 2. 第三方库
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

# 3. 本地项目导入
from .ops.spline import calc_spline_values
from ..layers.base import LayerKAN
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 类 | CamelCase | `PiecewiseActivationLayer`, `CLIArgs`, `TaskType` |
| 函数/方法 | snake_case | `calc_spline_output`, `validate_bias_config` |
| 变量 | snake_case | `spline_kernel`, `layer_idx` |
| 常量 | UPPER_SNAKE | `FREQ_LIST`, `GRID_SIZE` |
| 枚举值 | UPPER_SNAKE | `TaskType.TRAIN`, `LayoutMode.OVERLAY` |
| 私有成员 | _前缀 | `_progress_monitor`, `_src_dir` |

### CLI 参数类模式

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any

class TaskType(Enum):
    TRAIN = "train"
    EVALUATE = "evaluate"
    INFERENCE = "inference"

@dataclass
class CLIArgs:
    task_type: TaskType
    project_names: List[str]
    force_mode: bool = False
    layers_param: Optional[int] = None
    bias_params: Dict[str, Any] = field(default_factory=dict)
    # ...
```

### 错误处理

```python
# 使用具体异常类型
raise ValueError("xn and yn must have the same length.")
raise ArgumentParsingError("参数解析错误")
raise NotImplementedError("Subclasses must implement update_grid_from_samples.")

# 捕获并重新抛出（保留上下文）
try:
    config.validate_bias_compensation_config(model=None)
except Exception as e:
    logger.warning(f"偏置补偿配置验证警告: {e}")
```

### Keras/TensorFlow模式

```python
class PiecewiseActivationLayer(tf.keras.layers.Layer):
    def __init__(self, xn, yn, **kwargs):
        super(PiecewiseActivationLayer, self).__init__(**kwargs)
    
    def call(self, inputs):
        return self.piecewise_activation(inputs)
    
    def get_config(self):
        config = super().get_config()
        config.update({"xn": self.xn, "yn": self.yn})
        return config
```

---

## 项目结构

```
src/
├── core/                  # 核心模块
│   ├── cli_parser.py      # CLI参数解析
│   ├── task_dispatcher.py # 任务分发
│   ├── external_cli_handler.py  # ep子命令处理
│   ├── training.py        # 训练逻辑
│   └── project_manager.py # 项目管理
├── models/               # 神经网络模型
├── tfkan/                # TensorFlow KAN实现
├── visualization/        # 可视化
├── calibration_analyzer/ # 校准分析
├── utils/                # 工具函数
└── logger/               # 日志工具
```

---

## CLI 启动时序 (cli.py)

1. **第一阶段**: 日志配置 `setup_logging()` (仅主进程)
2. **轻量导入**: `cli_parser.parse_arguments()` (不加载TensorFlow)
3. **ep子命令**: 直接调用 `external_cli_handler.handle_ep_command()`
4. **测试命令**: 调用 `_run_test_command()` (不加载重型依赖)
5. **主命令**: `_run_main_commands()` 加载重型依赖后执行

---

## 关键依赖

```
tensorflow==2.6, keras==2.6, numpy==1.19.5, matplotlib==3.6.3
pandas, plotly, scikit-learn, tqdm, scipy
pytest>=7.0.0, pytest-cov, pytest-timeout
```

---

## 测试命令 (pytest)

```bash
# 运行所有测试
pytest

# 单个测试文件/函数
pytest src/analysis/tests/test_analysis_comprehensive.py::TestAliasSuppression::test_module_import -v

# 关键字匹配
pytest -k "test_module_import"
```
