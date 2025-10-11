# CLI.py 重构具体实施计划

## 概述
本文档详细描述将 cli.py 从 511 行精简到 200 行以内的具体实施步骤，包括每个文件的修改点和实施顺序。

## 文件修改清单

### 1. 新建文件列表

| 文件路径 | 源代码行数 | 功能描述 | 来源 |
|----------|------------|----------|------|
| `utils/environment_checker.py` | 19-54 | 环境检查功能 | cli.py |
| `core/project_manager.py` | 73-289 | 项目管理类 | cli.py |
| `core/cli_helpers.py` | 290-302 | 辅助函数 | cli.py |
| `core/cli_parser.py` | 304-402 | 参数解析 | cli.py |
| `core/task_dispatcher.py` | 403-511 | 任务分发 | cli.py |

### 2. 修改文件列表

| 文件路径 | 修改类型 | 修改内容 |
|----------|----------|----------|
| `cli.py` | 重构 | 保留启动时序，删除已移动代码，添加模块调用 |

## 详细实施步骤

### 步骤1：创建环境检查模块
**文件**: `utils/environment_checker.py`
**源代码**: cli.py 第 19-54 行

#### 修改点：
1. **函数移动**：
   - 移动 `check_environment()` 函数完整逻辑
   - 保持所有错误消息和格式化输出
   - 保持 `sys.exit(1)` 退出机制

2. **导入处理**：
   ```python
   import logging
   import sys
   
   logger = logging.getLogger(__name__)
   ```

3. **关键要求**：
   - 不能包含 `if __name__ == "__main__":` 逻辑
   - 保持原有的错误检查逻辑
   - 保持原有的日志输出格式

4. **测试验证**：
   - 测试正确的 Python 版本检查
   - 测试正确的 TensorFlow 版本检查
   - 测试错误环境的退出机制

### 步骤2：创建项目管理模块
**文件**: `core/project_manager.py`
**源代码**: cli.py 第 73-289 行

#### 修改点：
1. **类移动**：
   - 完整移动 `ProjectManager` 类
   - 保持所有方法和属性不变
   - 保持所有内部逻辑不变

2. **导入处理**：
   ```python
   import logging
   import os
   import traceback
   import sys
   import shutil
   from models.base_models import ModelEvent, ModelEventType
   from config import Config
   import config
   from core.model_engine import ModelEngine
   from core.training_log import TrainingLogger
   from core.training_state import TrainingStateManager
   from inference.manager import InferenceManager
   # ... 其他必要导入
   
   logger = logging.getLogger(__name__)
   ```

3. **关键要求**：
   - 保持 `__init__` 方法完全不变
   - 保持所有方法签名不变
   - 保持对 `InferenceManager` 的延迟创建机制

4. **测试验证**：
   - 测试 ProjectManager 实例化
   - 测试所有方法的正常调用
   - 测试与其他模块的交互

### 步骤3：创建辅助函数模块
**文件**: `core/cli_helpers.py`
**源代码**: cli.py 第 290-302 行

#### 修改点：
1. **函数移动**：
   - 移动 `met_comp_with_project()` 函数（290-299行）
   - 移动 `get_all_project_dirs()` 函数（301-302行）

2. **导入处理**：
   ```python
   import logging
   import os
   import sys
   import matplotlib.pyplot as plt
   from core.project_manager import ProjectManager
   from core.training import start_process, plot_process_start
   import config
   
   logger = logging.getLogger(__name__)
   ```

3. **关键要求**：
   - 保持 `met_comp_with_project()` 的多进程逻辑
   - 保持 Windows 平台的实时绘图功能
   - 保持 `get_all_project_dirs()` 的目录扫描逻辑

4. **测试验证**：
   - 测试项目处理功能
   - 测试目录扫描功能
   - 测试多进程场景（Windows）

### 步骤4：创建参数解析模块
**文件**: `core/cli_parser.py`
**源代码**: cli.py 第 304-402 行

#### 修改点：
1. **参数解析逻辑**：
   - 提取任务类型判断（308-323行）
   - 提取参数标志解析（324-359行）
   - 提取项目名称处理（376-402行）

2. **核心函数**：
   ```python
   def parse_arguments(argv):
       """解析命令行参数，返回参数字典"""
       # 解析任务类型
       task_type = parse_task_type(argv)
       
       # 解析标志参数
       flags = parse_flags(argv)
       
       # 解析特殊参数
       special_params = parse_special_params(argv)
       
       return {
           'task_type': task_type,
           'flags': flags,
           'special_params': special_params
       }
   
   def get_project_names(args, argv):
       """根据参数获取项目名称列表"""
       # 处理项目名称解析逻辑
       pass
   ```

3. **导入处理**：
   ```python
   import logging
   import sys
   import json
   import fnmatch
   from core.cli_helpers import get_all_project_dirs
   
   logger = logging.getLogger(__name__)
   ```

4. **关键要求**：
   - 保持所有参数的解析逻辑
   - 保持默认值和参数验证
   - 保持项目名称通配符匹配

5. **测试验证**：
   - 测试所有任务类型的解析
   - 测试所有参数标志的解析
   - 测试项目名称匹配逻辑

### 步骤5：创建任务分发模块
**文件**: `core/task_dispatcher.py`
**源代码**: cli.py 第 403-511 行

#### 修改点：
1. **任务分发逻辑**：
   - 移动主要的 if-elif 任务分发逻辑（403-511行）
   - 保持所有任务类型的处理逻辑
   - 保持错误处理和异常捕获

2. **核心函数**：
   ```python
   def dispatch_task(task_type, project_names, args):
       """根据任务类型分发执行"""
       for project_name in project_names:
           project_path = f'projects/{project_name}'
           logger.info(f'Project path: {project_path}')
           
           try:
               if task_type == 'train':
                   handle_train_task(project_path)
               elif task_type == 'evaluate':
                   handle_evaluate_task(project_path, args)
               # ... 其他任务类型
           except Exception as e:
               logger.error(f"Error in {task_type} task for {project_name}: {e}")
               continue
   ```

3. **导入处理**：
   ```python
   import logging
   import traceback
   import shutil
   import matplotlib.pyplot as plt
   from core.project_manager import ProjectManager
   from core.cli_helpers import met_comp_with_project
   
   logger = logging.getLogger(__name__)
   ```

4. **关键要求**：
   - 保持所有任务类型的完整逻辑
   - 保持错误处理和日志记录
   - 保持多项目处理的循环逻辑

5. **测试验证**：
   - 测试所有任务类型的执行
   - 测试错误处理机制
   - 测试多项目批处理

### 步骤6：重构主文件
**文件**: `cli.py`
**修改**: 从 511 行精简到约 35-40 行

#### 修改点：
1. **保持启动时序**：
   ```python
   # 第一阶段：日志配置（仅主进程）
   if __name__ == "__main__":
       setup_logging()
   
   logger = logging.getLogger('cli')
   
   # 第二阶段：环境检查（仅主进程）
   if __name__ == "__main__":
       from utils.environment_checker import check_environment
       check_environment()
   
   # 第三阶段：依赖导入（环境检查后）
   from models.base_models import ModelEvent, ModelEventType
   import tensorflow as tf
   from core.training import start_process, plot_process_start
   from core.project_manager import ProjectManager
   from core.cli_parser import parse_arguments, get_project_names
   from core.task_dispatcher import dispatch_task
   
   # TensorFlow 配置
   tf.config.experimental.enable_tensor_float_32_execution(False)
   ```

2. **删除已移动代码**：
   - 删除 `check_environment()` 函数定义
   - 删除 `ProjectManager` 类定义
   - 删除辅助函数定义
   - 删除参数解析和任务分发逻辑

3. **添加模块调用**：
   ```python
   if __name__ == '__main__':
       logger.info("cli.py start...")
       
       # 解析命令行参数
       args = parse_arguments(sys.argv)
       
       # 获取项目名称列表
       project_names = get_project_names(args, sys.argv)
       
       # 分发执行任务
       dispatch_task(args['task_type'], project_names, args)
   ```

4. **关键要求**：
   - 严格保持双重主进程检查
   - 保持导入顺序不变
   - 保持多进程安全性

5. **测试验证**：
   - 测试启动时序正确
   - 测试多进程环境安全
   - 测试所有功能完整

## 实施顺序和时间安排

### 阶段1：基础模块创建（2小时）
1. **步骤1**: 创建 `utils/environment_checker.py` (30分钟)
2. **步骤2**: 创建 `core/project_manager.py` (90分钟)

### 阶段2：功能模块创建（2小时）
3. **步骤3**: 创建 `core/cli_helpers.py` (30分钟)
4. **步骤4**: 创建 `core/cli_parser.py` (90分钟)

### 阶段3：集成完成（2小时）
5. **步骤5**: 创建 `core/task_dispatcher.py` (60分钟)
6. **步骤6**: 重构 `cli.py` (60分钟)

### 阶段4：测试验证（2.5小时）
7. **单元测试**: 每个模块单独测试 (90分钟)
8. **集成测试**: 完整功能测试 (60分钟)

**总计**: 8.5小时

## 测试策略

### 测试检查点
1. **每个模块完成后**：立即进行单元测试
2. **集成完成后**：完整功能测试
3. **部署前**：多环境回归测试

### 测试内容
- 启动时序测试
- 多进程安全测试
- 所有任务类型功能测试
- 错误处理测试
- 性能影响测试

### 测试命令
```bash
# 基本功能测试
python cli.py WNET5q1h2u6l3
python cli.py WNET5q1h2u6l3 -e
python cli.py WNET5q1h2u6l3 -i

# 多进程测试（Windows）
python cli.py WNET5q1h2u6l3  # 测试实时绘图

# 参数测试
python cli.py WNET5q1h2u6l3 -i --layers 5
python cli.py WNET5q1h2u6l3 -a --bias-method auto
```

## 回滚计划

### 备份策略
1. **完整备份**: 在开始前备份当前 cli.py
2. **增量备份**: 每个阶段完成后创建checkpoint
3. **测试环境**: 在测试环境先完成所有步骤

### 回滚触发条件
- 任何阶段测试失败
- 多进程功能异常
- 性能显著下降
- 无法在规定时间内完成

### 回滚步骤
1. 停止当前修改
2. 恢复最近的可工作版本
3. 分析失败原因
4. 调整计划后重新开始

## 验收标准

### 功能完整性
- [ ] 所有命令行参数正常工作
- [ ] 所有任务类型正常执行
- [ ] 多进程环境正常工作
- [ ] 错误处理机制正常

### 代码质量
- [ ] cli.py 行数少于 200 行
- [ ] 代码结构清晰，职责明确
- [ ] 所有模块有适当的文档
- [ ] 遵循项目编码规范

### 性能要求
- [ ] 启动时间无明显增加
- [ ] 内存使用无明显增加
- [ ] 多进程性能保持一致

### 测试覆盖
- [ ] 所有新模块通过单元测试
- [ ] 集成测试覆盖所有功能
- [ ] 回归测试确认无功能退化

## 风险控制

### 高风险操作
1. **修改启动时序**: 可能影响多进程安全
2. **移动 ProjectManager**: 可能影响核心功能
3. **重构参数解析**: 可能影响CLI兼容性

### 风险缓解
1. **分阶段实施**: 每次只修改一个模块
2. **充分测试**: 每个阶段完成后立即测试
3. **保持备份**: 随时可以快速回滚
4. **文档记录**: 详细记录每个修改点

## 完成检查清单

### 开发完成
- [ ] 所有6个步骤完成
- [ ] 所有新文件创建完成
- [ ] cli.py 重构完成
- [ ] 所有导入和调用正确

### 测试完成
- [ ] 单元测试全部通过
- [ ] 集成测试全部通过
- [ ] 多进程测试通过
- [ ] 性能测试通过

### 文档完成
- [ ] 所有新模块添加文档
- [ ] 更新相关技术文档
- [ ] 记录重构过程和注意事项

### 部署准备
- [ ] 代码审查完成
- [ ] 版本控制提交
- [ ] 部署文档准备
- [ ] 监控和回滚方案就绪