# CLI Parser 现代化改进计划

## 概述
本文档提出对 `core/cli_parser.py` 的现代化改进计划，目标是使其更加标准、稳健和易于维护。

## 当前状态分析

### 现有实现的问题

1. **手动参数解析**：
   - 使用原始的 `sys.argv` 手动解析参数
   - 大量的 `if-elif` 语句处理任务类型
   - 缺乏内置的参数验证和错误处理

2. **代码维护性差**：
   - 硬编码的参数处理逻辑
   - 新增参数需要修改多个地方
   - 缺乏统一的参数管理

3. **类型安全性不足**：
   - 没有类型提示
   - 返回原始字典，缺乏结构化数据
   - 运行时错误风险高

4. **错误处理不优雅**：
   - 直接使用 `sys.exit(1)` 退出
   - 错误信息不够友好
   - 缺乏参数验证的统一机制

5. **可扩展性有限**：
   - 添加新参数需要修改多处代码
   - 缺乏插件化的参数支持
   - 没有配置文件支持

6. **用户体验不佳**：
   - 没有内置的 `--help` 支持
   - 参数文档分散在代码中
   - 缺乏参数自动补全支持

## 改进目标

### 现代化标准
- 使用 Python 标准库 `argparse` 进行参数解析
- 采用 `dataclass` 定义结构化的参数数据
- 添加完整的类型提示支持
- 遵循 PEP 8 和现代 Python 编码规范

### 稳健性要求
- 统一的参数验证机制
- 优雅的错误处理和用户友好的错误信息
- 全面的单元测试覆盖
- 边界条件和异常情况的处理

### 易维护性
- 清晰的代码结构和职责分离
- 完整的文档和类型注解
- 易于扩展的参数定义机制
- 向后兼容性保证

## 技术方案设计

### 1. 核心架构改进

#### 使用 argparse 替代手动解析
```python
import argparse
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum

class TaskType(Enum):
    TRAIN = "train"
    EVALUATE = "evaluate"
    CLEAN = "clean"
    MODEL_INFO = "model_info"
    LUT = "lut"
    INFERENCE = "inference"
    ANALYZE = "analyze"
    WAVE = "wave"
    BIAS_VISUALIZATION = "bias_visualization"

@dataclass
class CLIArgs:
    """结构化的CLI参数数据类"""
    task_type: TaskType
    project_names: List[str]
    force_mode: bool = False
    quick_inference: bool = False
    layers_param: Optional[int] = None
    bias_method: str = "auto"
    bias_params: Dict[str, Any] = None
    baseline_dir: Optional[str] = None
    compensated_dir: Optional[str] = None
    vis_output_dir: Optional[str] = None
    vis_config_path: Optional[str] = None
    
    def __post_init__(self):
        if self.bias_params is None:
            self.bias_params = {}
```

#### 创建参数解析器
```python
def create_parser(config: CLIConfig = None) -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    if config is None:
        config = load_config()
    
    parser = argparse.ArgumentParser(
        description='MET Nonlinear Model Training and Inference CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
任务类型说明：
  train         训练模型
  evaluate      评估模型性能
  clean         清理项目数据
  model_info    显示模型信息
  lut           生成查找表
  inference     运行推理
  analyze       分析错误
  wave          生成波形数据
  bias_viz      偏置可视化

示例用法：
  python cli.py train PROJECT_NAME
  python cli.py evaluate PROJECT_NAME
  python cli.py inference PROJECT_NAME --layers 5
  python cli.py analyze PROJECT_NAME --bias-method auto

配置文件：
  可以在以下位置创建 cli_config.yaml 文件来设置默认值：
  - 项目根目录: cli_config.yaml
  - 核心模块目录: core/cli_defaults.yaml
  - 用户目录: ~/.met_nonlinear/cli_defaults.yaml
        """
    )
    
    # 任务类型（互斥组）
    task_group = parser.add_mutually_exclusive_group(required=True)
    task_group.add_argument('-t', '--train', action='store_const', 
                           const=TaskType.TRAIN, dest='task_type',
                           help='训练模型')
    task_group.add_argument('-e', '--evaluate', action='store_const',
                           const=TaskType.EVALUATE, dest='task_type',
                           help='评估模型')
    task_group.add_argument('-c', '--clean', action='store_const',
                           const=TaskType.CLEAN, dest='task_type',
                           help='清理项目数据')
    task_group.add_argument('-m', '--model-info', action='store_const',
                           const=TaskType.MODEL_INFO, dest='task_type',
                           help='显示模型信息')
    task_group.add_argument('-l', '--lut', action='store_const',
                           const=TaskType.LUT, dest='task_type',
                           help='生成查找表')
    task_group.add_argument('-i', '--inference', action='store_const',
                           const=TaskType.INFERENCE, dest='task_type',
                           help='运行推理')
    task_group.add_argument('-a', '--analyze', action='store_const',
                           const=TaskType.ANALYZE, dest='task_type',
                           help='分析错误')
    task_group.add_argument('-w', '--wave', action='store_const',
                           const=TaskType.WAVE, dest='task_type',
                           help='生成波形数据')
    task_group.add_argument('--bias-viz', '--bias-visualization', 
                           action='store_const',
                           const=TaskType.BIAS_VISUALIZATION, dest='task_type',
                           help='偏置可视化')
    
    # 项目名称
    parser.add_argument('project_name', nargs='?', 
                       default=config.default_project,
                       help=f'项目名称（支持通配符），默认: {config.default_project}')
    parser.add_argument('-all', '--all-projects', action='store_true',
                       help='处理所有项目')
    
    # 通用标志
    parser.add_argument('-f', '--force', action='store_true',
                       default=config.default_force_mode,
                       help=f'强制模式，默认: {config.default_force_mode}')
    parser.add_argument('-q', '--quick', action='store_true',
                       default=config.default_quick_inference,
                       help=f'快速推理模式，默认: {config.default_quick_inference}')
    
    # 推理相关参数
    inference_group = parser.add_argument_group('推理参数')
    inference_group.add_argument('--layers', type=int, metavar='N',
                                default=config.default_layers,
                                help=f'推理层数（必须为正整数），默认: {config.default_layers}')
    
    # 偏置分析参数
    bias_group = parser.add_argument_group('偏置分析参数')
    bias_group.add_argument('--bias-method', 
                           choices=['auto', 'steady_state', 'frequency_domain'],
                           default=config.default_bias_method,
                           help=f'偏置分析方法，默认: {config.default_bias_method}')
    bias_group.add_argument('--bias-params', type=json.loads,
                           metavar='JSON',
                           help='偏置分析参数（JSON格式）')
    
    # 可视化参数
    viz_group = parser.add_argument_group('可视化参数')
    viz_group.add_argument('--baseline', metavar='DIR',
                          default=config.default_baseline_dir,
                          help=f'基线数据目录，默认: {config.default_baseline_dir}')
    viz_group.add_argument('--compensated', metavar='DIR',
                          default=config.default_compensated_dir,
                          help=f'补偿数据目录，默认: {config.default_compensated_dir}')
    viz_group.add_argument('--vis-output', metavar='DIR',
                          default=config.default_vis_output_dir,
                          help=f'可视化输出目录，默认: {config.default_vis_output_dir}')
    viz_group.add_argument('--vis-config', metavar='FILE',
                          help='可视化配置文件')
    
    return parser
```

### 2. 参数验证器

```python
class ArgumentValidator:
    """参数验证器"""
    
    @staticmethod
    def validate_layers(layers: Optional[int]) -> None:
        """验证层数参数"""
        if layers is not None and layers <= 0:
            raise argparse.ArgumentTypeError("--layers 参数必须是正整数")
    
    @staticmethod
    def validate_bias_params(bias_params: Optional[str]) -> Dict[str, Any]:
        """验证偏置参数"""
        if bias_params is None:
            return {}
        try:
            return json.loads(bias_params)
        except json.JSONDecodeError as e:
            raise argparse.ArgumentTypeError(f"无效的偏置参数JSON: {e}")
    
    @staticmethod
    def validate_project_name(project_name: str) -> List[str]:
        """验证并解析项目名称"""
        if '*' in project_name:
            project_names = get_all_project_dirs()
            project_names = fnmatch.filter(project_names, project_name)
            if not project_names:
                raise argparse.ArgumentTypeError(f"没有找到匹配的项目: {project_name}")
            return project_names
        return [project_name]
```

### 3. 新的解析接口

```python
def parse_arguments(argv: Optional[List[str]] = None) -> CLIArgs:
    """
    解析命令行参数
    
    Args:
        argv: 命令行参数列表，为None时使用sys.argv
        
    Returns:
        CLIArgs: 结构化的参数对象
        
    Raises:
        ArgumentParsingError: 参数解析错误
    """
    # 加载配置文件中的默认值
    config = load_config()
    parser = create_parser(config)
    
    try:
        args = parser.parse_args(argv)
        
        # 解析项目名称
        if args.all_projects:
            project_names = get_all_project_dirs(config.projects_dir)
        else:
            project_names = ArgumentValidator.validate_project_name(args.project_name)
        
        # 验证参数
        ArgumentValidator.validate_layers(args.layers)
        
        # 构建结果对象
        return CLIArgs(
            task_type=args.task_type,
            project_names=project_names,
            force_mode=args.force,
            quick_inference=args.quick,
            layers_param=args.layers,
            bias_method=args.bias_method,
            bias_params=args.bias_params or {},
            baseline_dir=args.baseline,
            compensated_dir=args.compensated,
            vis_output_dir=args.vis_output,
            vis_config_path=args.vis_config
        )
        
    except argparse.ArgumentError as e:
        raise ArgumentParsingError(f"参数解析错误: {e}")
```

### 4. 默认值配置文件支持

```python
@dataclass
class CLIConfig:
    """CLI默认值配置类"""
    default_project: str = "WNET5q1h2u6l3"
    projects_dir: str = "projects"
    default_bias_method: str = "auto"
    default_layers: Optional[int] = None
    default_force_mode: bool = False
    default_quick_inference: bool = False
    
    # 可视化默认配置
    default_baseline_dir: Optional[str] = None
    default_compensated_dir: Optional[str] = None
    default_vis_output_dir: Optional[str] = None
    
    @classmethod
    def from_file(cls, config_path: str) -> 'CLIConfig':
        """从配置文件加载默认值"""
        import yaml
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
            return cls(**{k: v for k, v in config_data.items() if hasattr(cls, k)})
        except (FileNotFoundError, yaml.YAMLError) as e:
            logger.warning(f"配置文件加载失败: {e}，使用默认配置")
            return cls()

def load_config() -> CLIConfig:
    """加载配置文件中的默认值"""
    config_paths = [
        'cli_config.yaml',                                       # 项目根目录
        'core/cli_defaults.yaml',                               # 核心模块目录
        os.path.expanduser('~/.met_nonlinear/cli_defaults.yaml')  # 用户目录
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            logger.info(f"加载配置文件: {config_path}")
            return CLIConfig.from_file(config_path)
    
    logger.info("未找到配置文件，使用内置默认值")
    return CLIConfig()
```

#### 配置文件示例 (`cli_config.yaml`)
```yaml
# CLI 默认值配置文件
# 此文件用于设置命令行参数的默认值，不支持环境变量

# 项目设置
default_project: "WNET5q1h2u6l3"
projects_dir: "projects"

# 分析设置
default_bias_method: "auto"
default_layers: null  # 不设置默认层数

# 模式设置
default_force_mode: false
default_quick_inference: false

# 可视化设置
default_baseline_dir: null
default_compensated_dir: null
default_vis_output_dir: "visualization_output"

# 其他默认设置可以在这里添加
```

## 实施步骤

### 第一阶段：基础重构（2小时）
1. **创建新的数据结构**：
   - 定义 `TaskType` 枚举
   - 创建 `CLIArgs` 数据类
   - 实现 `ArgumentValidator` 类

2. **实现 argparse 解析器**：
   - 创建 `create_parser()` 函数
   - 定义所有参数组和选项
   - 添加完整的帮助文档

### 第二阶段：兼容性保证（1小时）
1. **保持现有接口**：
   - 创建兼容性适配器
   - 确保现有调用方式继续工作
   - 添加弃用警告

2. **测试兼容性**：
   - 验证所有现有功能
   - 确保参数解析结果一致

### 第三阶段：增强功能（1.5小时）
1. **添加配置文件支持**：
   - 实现配置文件加载
   - 支持多层级配置查找
   - YAML格式的默认值配置

2. **改进错误处理**：
   - 自定义异常类
   - 用户友好的错误信息
   - 参数验证增强

### 第四阶段：测试和文档（1小时）
1. **编写单元测试**：
   - 参数解析测试
   - 错误处理测试
   - 边界条件测试

2. **更新文档**：
   - API文档更新
   - 使用示例更新
   - 迁移指南

## 向后兼容性

### 兼容性适配器
```python
def parse_arguments_legacy(argv: List[str]) -> Dict[str, Any]:
    """
    保持向后兼容的参数解析接口
    
    Args:
        argv: 命令行参数列表
        
    Returns:
        dict: 原有格式的参数字典
        
    Deprecated:
        使用新的 parse_arguments() 函数替代
    """
    warnings.warn(
        "parse_arguments_legacy() is deprecated. Use parse_arguments() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    cli_args = parse_arguments(argv)
    
    # 转换为旧格式
    return {
        'task_type': cli_args.task_type.value,
        'force_mode': cli_args.force_mode,
        'quick_inference': cli_args.quick_inference,
        'bias_method': cli_args.bias_method,
        'bias_params': cli_args.bias_params,
        'baseline_dir': cli_args.baseline_dir,
        'compensated_dir': cli_args.compensated_dir,
        'vis_output_dir': cli_args.vis_output_dir,
        'vis_config_path': cli_args.vis_config_path,
        'layers_param': cli_args.layers_param,
        'default_project_name': cli_args.project_names[0] if cli_args.project_names else "WNET5q1h2u6l3"
    }
```

## 测试策略

### 单元测试覆盖
1. **参数解析测试**：
   - 所有任务类型的解析
   - 参数组合测试
   - 默认值测试

2. **错误处理测试**：
   - 无效参数测试
   - 缺失参数测试
   - 参数冲突测试

3. **边界条件测试**：
   - 空参数列表
   - 极端参数值
   - 特殊字符处理

### 集成测试
1. **端到端测试**：
   - 完整的CLI调用链
   - 与task_dispatcher的集成
   - 多项目处理测试

2. **性能测试**：
   - 启动时间测试
   - 内存使用测试
   - 大量项目处理测试

## 风险评估与缓解

### 风险分析
1. **兼容性风险**：
   - 现有脚本可能依赖特定的参数格式
   - 缓解：提供兼容性适配器和过渡期

2. **性能风险**：
   - argparse可能比手动解析稍慢
   - 缓解：CLI启动时间影响可忽略

3. **依赖风险**：
   - 增加对YAML库的依赖
   - 缓解：PyYAML是常见依赖，仅用于配置文件加载

4. **学习成本**：
   - 团队需要学习新的参数结构
   - 缓解：详细文档和示例代码

### 缓解措施
1. **渐进式迁移**：
   - 保持旧接口可用
   - 逐步迁移调用代码
   - 提供迁移工具

2. **充分测试**：
   - 完整的测试覆盖
   - 自动化测试流程
   - 性能基准测试

3. **文档支持**：
   - 详细的迁移指南
   - 代码示例和最佳实践
   - FAQ和常见问题解答

## 预期收益

### 代码质量提升
1. **类型安全**：
   - 完整的类型提示
   - 编译时错误检查
   - IDE智能提示支持

2. **可维护性**：
   - 清晰的代码结构
   - 统一的参数管理
   - 易于扩展的设计

3. **稳健性**：
   - 统一的错误处理
   - 全面的参数验证
   - 边界条件处理

### 用户体验改善
1. **更好的帮助信息**：
   - 内置的 `--help` 支持
   - 详细的参数说明
   - 使用示例

2. **友好的错误提示**：
   - 清晰的错误信息
   - 解决方案建议
   - 参数格式提示

3. **功能增强**：
   - 配置文件支持（YAML格式）
   - 参数自动补全

### 开发效率提升
1. **新功能开发**：
   - 简化参数添加流程
   - 标准化的验证机制
   - 自动化的文档生成

2. **测试和调试**：
   - 更容易的单元测试
   - 清晰的错误跟踪
   - 模块化的组件

3. **维护和扩展**：
   - 代码重用性提升
   - 插件化架构支持
   - 配置文件驱动的默认值

## 实施时间表

| 阶段 | 时间 | 主要任务 | 交付物 |
|------|------|----------|---------|
| 第一阶段 | 2小时 | 基础重构 | 新的数据结构和解析器 |
| 第二阶段 | 1小时 | 兼容性保证 | 兼容性适配器和测试 |
| 第三阶段 | 1.5小时 | 增强功能 | 配置文件支持和错误处理 |
| 第四阶段 | 1小时 | 测试和文档 | 单元测试和用户文档 |
| **总计** | **5.5小时** | **完整现代化** | **现代化的CLI解析器** |

## 结论

通过这次现代化改进，`core/cli_parser.py` 将从一个手工编写的参数解析器升级为一个标准、稳健、易维护的现代化CLI解析模块。这不仅提升了代码质量，还为未来的功能扩展和维护奠定了坚实的基础。

改进后的解析器将提供：
- 更好的类型安全性
- 更友好的用户体验
- 更高的开发效率
- 更强的可扩展性

这个改进是值得投入的，将显著提升项目的整体质量和开发体验。