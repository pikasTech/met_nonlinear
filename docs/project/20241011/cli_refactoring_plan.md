# CLI.py 重构计划

## 目标
将 cli.py 从当前的 511 行精简到 200 行以下，通过将功能委托到内部模块来实现。

## 当前状态分析

### 文件结构
- **总行数**: 511 行
- **主要组件**:
  1. 环境检查功能 (19-54行)
  2. ProjectManager 类 (73-289行，216行)
  3. 辅助函数 (290-302行)
  4. 主程序入口和参数解析 (304-511行，207行)

### 存在的问题
1. 违反单一职责原则：CLI 接口和业务逻辑混合
2. 代码过长，难以维护
3. 测试困难：所有功能耦合在一个文件中

## 重构方案

### 1. 模块划分

#### 1.1 utils/environment_checker.py
负责环境检查功能：
- `check_python_version()`: 检查 Python 版本
- `check_tensorflow_version()`: 检查 TensorFlow 版本  
- `check_environment()`: 主入口函数

#### 1.2 core/project_manager.py
移动整个 ProjectManager 类（当前 73-289 行）：
- 保持现有的所有方法
- 这是核心业务逻辑，不应该在 CLI 中

#### 1.3 core/cli_parser.py
负责命令行参数解析：
- `parse_arguments(argv)`: 解析命令行参数，返回参数字典
- `get_project_names(args)`: 根据参数解析项目名称
- 包含所有参数解析逻辑（task_type、force_mode、layers等）

#### 1.4 core/task_dispatcher.py
负责任务分发执行：
- `dispatch_task(task_type, project_names, args)`: 根据任务类型执行相应操作
- 包含当前 main 中的所有 if-elif 任务执行逻辑

#### 1.5 core/cli_helpers.py
辅助函数：
- `met_comp_with_project(project_path)`
- `get_all_project_dirs(base_path='projects')`

### 2. 重构后的 cli.py 结构

**关键要求：严格保持启动时序和多进程安全性**

```python
"""
cli.py - CLI 接口，仅作为内部功能的代理
严格控制启动时序，确保多进程安全
"""
import logging
import os
import sys
import shutil
from logger import setup_logging

# 第一阶段：日志配置（仅主进程，防止多进程时重复配置）
if __name__ == "__main__":
    setup_logging()

logger = logging.getLogger('cli')

# 第二阶段：环境检查（仅主进程，必须在TensorFlow导入前）
if __name__ == "__main__":
    from utils.environment_checker import check_environment
    check_environment()

# 第三阶段：依赖导入（环境检查通过后，保持原有导入顺序）
from models.base_models import ModelEvent, ModelEventType
import tensorflow as tf
from core.training import start_process, plot_process_start
from core.project_manager import ProjectManager
from core.cli_parser import parse_arguments, get_project_names
from core.task_dispatcher import dispatch_task

# TensorFlow 配置（必须在导入后立即执行）
tf.config.experimental.enable_tensor_float_32_execution(False)

# 主程序入口
if __name__ == '__main__':
    logger.info("cli.py start...")
    
    # 解析命令行参数
    args = parse_arguments(sys.argv)
    
    # 获取项目名称列表
    project_names = get_project_names(args)
    
    # 分发执行任务
    dispatch_task(args['task_type'], project_names, args)
```

预计行数：约 35-40 行

### 3. 实施步骤

1. **第一步**：创建 `utils/environment_checker.py`
   - 移动环境检查相关代码
   - 确保日志功能正常

2. **第二步**：创建 `core/project_manager.py`
   - 移动 ProjectManager 类
   - 处理导入依赖

3. **第三步**：创建 `core/cli_parser.py`
   - 提取参数解析逻辑
   - 定义清晰的参数数据结构

4. **第四步**：创建 `core/task_dispatcher.py`
   - 提取任务执行逻辑
   - 处理各种任务类型

5. **第五步**：创建 `core/cli_helpers.py`
   - 移动辅助函数

6. **第六步**：重构 `cli.py`
   - 删除已移动的代码
   - 添加模块导入和调用

### 4. 关键注意事项

#### 4.1 启动时序保证（最重要）
- **严格保持双重主进程检查机制**：
  - 第一次：`if __name__ == "__main__":` 用于日志配置
  - 第二次：`if __name__ == "__main__":` 用于环境检查
- **导入顺序不可改变**：
  - 日志配置 → 环境检查 → TensorFlow导入 → 业务逻辑导入
- **TensorFlow配置时机**：
  - 必须在 `import tensorflow as tf` 后立即执行
  - `tf.config.experimental.enable_tensor_float_32_execution(False)`

#### 4.2 多进程安全保证
- **日志配置只在主进程执行**：
  - 子进程继承父进程的日志配置
  - 避免多个进程同时创建日志文件
- **环境检查只在主进程执行**：
  - 子进程无需重复检查环境
  - 确保环境检查在依赖导入前完成

#### 4.3 模块设计要求
- **utils/environment_checker.py**：
  - 不能有 `if __name__ == "__main__":` 逻辑
  - 只提供 `check_environment()` 函数
  - 错误时使用 `sys.exit(1)` 退出
- **core/project_manager.py**：
  - 完整移动 ProjectManager 类
  - 保持所有方法和属性不变
  - 添加适当的日志记录

#### 4.4 导入依赖处理
- **延迟导入策略**：
  - 环境检查模块在主进程检查时导入
  - TensorFlow 相关模块在环境检查后导入
  - 业务逻辑模块可以正常导入
- **循环依赖预防**：
  - core 模块之间避免循环导入
  - 使用类型注解时用字符串形式

#### 4.5 向后兼容性
- **CLI 接口完全不变**：
  - 所有命令行参数保持一致
  - 所有任务类型行为保持一致
- **多进程行为保持一致**：
  - Windows 平台实时绘图功能正常
  - 训练进程重启机制正常

### 5. 测试计划

#### 5.1 启动时序测试
1. **日志配置测试**：
   - 验证日志文件正确创建
   - 验证多进程环境下无重复配置
   - 验证子进程日志正常输出

2. **环境检查测试**：
   - 测试正确的Python版本（3.9）
   - 测试正确的TensorFlow版本（2.6.x）
   - 测试错误环境的退出机制

3. **导入顺序测试**：
   - 验证TensorFlow在环境检查后导入
   - 验证TensorFlow配置正确执行
   - 验证所有业务模块正常导入

#### 5.2 多进程功能测试
1. **Windows平台实时绘图**：
   - 验证 `plot_process_start()` 正常工作
   - 验证 `start_process()` 正常工作
   - 验证进程间通信正常

2. **训练进程重启机制**：
   - 验证训练进程异常退出时的重启
   - 验证正常结束时的退出机制
   - 验证进程健康监控功能

#### 5.3 业务功能测试
1. **所有任务类型测试**：
   - train, evaluate, clean, model_info, lut
   - inference, analyze, wave, bias_visualization
   - 验证所有参数和行为一致

2. **错误处理测试**：
   - 验证各种错误场景的处理
   - 验证日志记录正确
   - 验证进程清理正确

### 6. 预期收益

1. **代码可维护性**：模块化设计，职责清晰
2. **可测试性**：每个模块可独立测试
3. **可扩展性**：易于添加新功能
4. **代码复用**：其他工具可以复用这些模块

### 7. 风险评估

- **低风险**：重构不改变功能，只是代码组织
- **中风险**：可能出现导入问题，需要仔细测试

### 8. 实施检查清单

#### 8.1 启动时序检查
- [ ] 保持第一个 `if __name__ == "__main__":` 仅用于日志配置
- [ ] 保持第二个 `if __name__ == "__main__":` 仅用于环境检查
- [ ] 保持 TensorFlow 导入在环境检查后
- [ ] 保持 TensorFlow 配置在导入后立即执行
- [ ] 验证多进程环境下日志配置不重复

#### 8.2 模块实现检查
- [ ] `utils/environment_checker.py` 无主程序逻辑
- [ ] `core/project_manager.py` 完整移动 ProjectManager 类
- [ ] `core/cli_parser.py` 处理所有参数解析逻辑
- [ ] `core/task_dispatcher.py` 处理所有任务分发逻辑
- [ ] `core/cli_helpers.py` 包含辅助函数

#### 8.3 功能兼容性检查
- [ ] 所有命令行参数保持一致
- [ ] 所有任务类型行为保持一致
- [ ] Windows 平台实时绘图功能正常
- [ ] 训练进程重启机制正常
- [ ] 错误处理和退出机制正常

#### 8.4 测试验证检查
- [ ] 单进程环境测试通过
- [ ] 多进程环境测试通过
- [ ] 所有任务类型测试通过
- [ ] 错误场景测试通过
- [ ] 性能影响测试通过

### 9. 时间估算

- 环境检查模块：1 小时（包含多进程安全验证）
- ProjectManager 移动：1.5 小时（包含导入处理）
- CLI 解析器：1 小时
- 任务分发器：1 小时
- 启动时序集成：1 小时（关键步骤）
- 测试和调试：3 小时（重点测试多进程）
- **总计**：约 8.5 小时

### 10. 风险缓解措施

1. **备份当前 cli.py**：在重构前创建完整备份
2. **分阶段实施**：一次只移动一个模块，逐步验证
3. **多环境测试**：在 Windows 和 Linux 环境下都要测试
4. **回滚计划**：准备快速回滚到原始版本的方案