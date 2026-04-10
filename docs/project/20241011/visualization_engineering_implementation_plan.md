# CLI拓展项目工程化实施计划

## 实施概述

本文档详细规划了CLI拓展项目工程化系统的具体实施步骤，以支持新的 `cli.py ep path/to/the/ep-project` 子命令格式，包括文件创建、代码修改和测试验证的完整流程。

## 新命令格式设计

### 命令结构
```bash
# 基本格式
cli.py ep <ep-project-path> [OPTIONS]

# 使用示例（统一工程路径）
cli.py ep ep_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3
cli.py ep LSTMu32al_rs300_ex2/freq-response-compare/baseline-comparison
cli.py ep LSTMu32al_rs300_ex2/baseline-comparison
```

### 子命令参数设计
```bash
# 简化设计：直接执行，无额外参数
cli.py ep <ep-project-path>
```

**设计理念**:
- 简洁性优先：一个命令直接执行，无需额外参数
- 智能化处理：自动检测配置文件是否存在，不存在则创建模板
- 默认行为：直接执行可视化任务并生成输出

## 目标架构

### 新增文件结构（EP）
```
core/
├── external_cli_handler.py          # EP 命令处理与任务分发
├── external_path_parser.py          # EP 路径解析
├── config_validator.py              # 配置验证器（复用）
└── ...（各任务执行器分散在对应子模块，如 visualization/ 下）

ep_projects/
└── {domain}/
    └── {task_type}/
        └── {task_name}/
            ├── config.json         # 任务配置
            └── data/               # 输出目录（统一命名）
               ├── numerics/        # 数值产物（JSON/NPZ等）
               ├── plots/           # 图表
               └── reports/         # 报告
```

### 配置文件示例
```json
{
  "task_info": {
    "task_type": "freq-response-compare",
    "task_name": "baseline-comparison",
    "description": "补偿前后频率响应对比",
    "version": "1.0"
  },
  "visualization_config": {
    "method": "freq-response-compare",
    "layout": "side_by_side",
    "freq_range": [10, 200],
    "output_format": "png",
    "dpi": 300
  },
  "data_sources": [
    {
      "project": "LSTMu32al_rs300_ex2",
      "state": "origin",
      "label": "补偿前"
    },
    {
      "project": "LSTMu32al_rs300_ex2",
      "state": "compensation", 
      "label": "补偿后"
    }
  ]
}
```

### 路径解析设计

EP 项目路径解析器将支持以下路径格式：

1. **完整路径格式**:
   ```
    ep_projects/{domain}/{task_type}/{task_name}
    例: ep_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3
   ```

2. **相对路径格式**:
   ```
    {project_name}/{task_type}/{task_name}
    例: LSTMu32al_rs300_ex2/freq-response-compare/baseline-comparison
   ```

3. **简化格式**:
   ```
    {project_name}/{task_name}  (自动检测task_type)
    例: LSTMu32al_rs300_ex2/baseline-comparison
   ```

## 阶段1: 基础架构搭建

### 1.1 创建路径解析模块

**文件**: `core/external_path_parser.py`

**功能**:
- 解析可视化项目路径格式
- 支持多种路径表示方式
- 路径验证和标准化

**关键类**:
- `ExternalPathParser`: 路径解析器主类
- `ExternalPath`: 路径数据结构
- 支持路径解析、验证、标准化

### 1.2 修改CLI解析器 - 添加子命令支持

**文件**: `core/cli_parser.py`

**重大修改**:
1. 在 `create_parser()` 函数中添加子命令支持：
   ```python
   # 创建子命令解析器
   subparsers = parser.add_subparsers(dest='command', help='可用命令')
   
   # 原有的主命令保持不变（向后兼容）
   # ... 现有的所有参数 ...
   
    # 新增 ep 子命令（简化设计）
    ep_parser = subparsers.add_parser('ep', help='拓展项目管理 (External Project)')
    ep_parser.add_argument('ep_project_path', help='拓展项目路径，格式: project/task-type/task-name 或统一路径')
   # 无额外参数，直接执行
   ```

2. 修改 `CLIArgs` 数据类添加子命令字段：
   ```python
   @dataclass
   class CLIArgs:
       # 现有字段...
       
    # 新增子命令字段（简化）
    command: Optional[str] = None
    ep_project_path: Optional[str] = None
   ```

### 1.3 修改主CLI入口

**文件**: `cli.py`

**修改点**:
1. 在主程序中添加子命令检测（延迟加载重依赖，仅非 ep 流程加载）：
   ```python
   if __name__ == '__main__':
       logger.info("cli.py start...")
       
       # 解析命令行参数
       args = parse_arguments()
       
       # 检查是否为子命令
       if args.command == 'ep':
           from core.external_cli_handler import handle_ep_command
           handle_ep_command(args)
       else:
           # 原有的主命令处理逻辑
           project_names = args.project_names
           dispatch_task(args.task_type.value, project_names, args)
   ```

### 1.4 创建 EP CLI 处理器

**文件**: `core/external_cli_handler.py`

**功能**:
- 处理 ep 子命令的所有操作
- 路径解析和验证
- 任务执行分发

**关键函数**:
- `handle_ep_command(args: CLIArgs)`: 主处理函数
- `parse_ep_project_path(path: str)`: 路径解析
- `execute_external_task_auto(parsed_path)`: 智能执行任务（自动处理配置创建和任务执行）

### 1.5 目录管理策略

目录由 `external_path_parser` 与 `external_cli_handler` 协同创建标准结构：

**输出结构（统一为 data，内部数值为 numerics）**:
```
{ep_project_root}/
├─ config.json
└─ data/
    ├─ numerics/      # 计算产物（JSON/NPZ 等）
    ├─ plots/         # 图表
    └─ reports/       # 报告
```

**关键类**:
- `VisualizationDirectoryManager`: 目录管理器主类
- 支持任务目录创建、路径查询、目录验证

### 1.6 配置管理模块

（沿用现有验证器 `core/config_validator.py`，在 EP 下使用）

**功能**:
- JSON配置文件的加载和验证
- 配置模板生成
- 配置Schema验证

**关键类**:
- `VisualizationConfigManager`: 配置管理器主类
- `ConfigValidator`: 配置验证器
- `ConfigTemplate`: 配置模板生成器

### 1.7 任务执行器

任务由各领域执行器实现（如 `visualization/wnet5_circuit_validator.py`）。

**功能**:
- 统一的可视化任务执行入口
- 任务分发和生命周期管理
- 集成目录和配置管理

**示例**:
- `WNET5CircuitValidator`：WNET5 电路验证执行器

## 阶段2: 频率响应任务适配

### 2.1 适配频率响应对比器

**文件**: `visualization/frequency_response_json_comparator.py`

**修改策略**:
1. 保持现有接口不变（向后兼容）
2. 新增配置驱动的执行方法
3. 支持自定义输出目录

**关键修改**:
- 新增 `from_config()` 类方法支持配置驱动
- 修改输出路径逻辑，支持指定输出目录
- 增强标签自定义能力

### 2.2 创建任务执行器

**文件**: `core/visualization_engine.py` (扩展)

**实现**:
- `FreqResponseTaskExecutor` 类
- 配置解析和参数转换
- 元数据生成和保存

### 2.3 配置模板创建

**文件**: `core/visualization_templates.py`

**模板类型**:
1. **项目内对比模板**: 补偿前后对比
2. **跨项目对比模板**: 不同项目间对比
3. **自定义对比模板**: 用户定义数据源

## 阶段3: 测试与验证

### 3.1 单元测试

**测试文件**: `tests/test_external_cli.py`

**测试覆盖**:
- 目录管理器功能测试
- 配置管理器功能测试
- 任务执行器功能测试
- 错误处理测试

### 3.2 集成测试

**测试场景**:
1. **端到端工作流测试**:
   ```bash
   # 简化的命令格式 - 直接执行
   conda run -n tf26 python cli.py ep LSTMu32al_rs300_ex2/freq-response-compare/test-comparison
   conda run -n tf26 python cli.py ep LSTMu32al_rs300_ex2/baseline-comparison
   conda run -n tf26 python cli.py ep projects/LSTMu32al_rs300_ex2/external/freq-response-compare/test-comparison
   ```

2. **模板创建测试**: 验证必须通过 `python cli.py ep create ...` 显式创建模板
3. **路径解析测试**: 验证各种路径格式的正确解析（完整路径、相对路径、简化路径）  
4. **缺配置报错测试**: 验证直接运行 `python cli.py ep ...` 且配置缺失时立即报错退出
5. **重复执行测试**: 验证配置存在时直接执行任务

### 3.3 向后兼容性测试

**验证点**:
- 原有 `--vis-freq-response-compare` 命令仍然工作
- 现有项目结构不受影响
- 现有输出路径保持不变（在非工程化模式下）
- 原有的所有CLI参数和功能保持不变

**测试命令**:
```bash
# 确保原有命令格式仍然工作
conda run -n tf26 python cli.py --vis-freq-response-compare LSTMu32al_rs300_ex2 --layout side_by_side
conda run -n tf26 python cli.py -e LSTMu32al_rs300_ex2
conda run -n tf26 python cli.py -t LSTMu32al_rs300_ex2
```

## 阶段4: 文档和用户指导

### 4.1 用户文档

**文件**: `doc/user_guide/ep_engineering.md`

**内容**:
- 工程化可视化系统使用指南
- 配置文件编写指导
- 常见问题和解决方案

### 4.2 开发者文档

**文件**: `doc/dev_guide/ep_architecture.md`

**内容**:
- 可视化系统架构说明
- 新增任务类型的开发指南
- API参考文档

## 实施时间线

### 第1天: 基础架构
- [ ] 创建 `external_path_parser.py`
- [ ] 创建 `external_cli_handler.py`
- [ ] 修改 `cli_parser.py` 添加子命令支持
- [ ] 修改 `cli.py` 添加子命令检测
- [ ] 输出目录标准化（data/numerics, plots, reports）
- [ ] 创建 `visualization_config.py`

### 第2天: 引擎和模板
- [ ] 实现任务执行器（按任务类型放置于对应子模块）
- [ ] 适配 `frequency_response_json_comparator.py`

### 第3天: 测试和验证
- [ ] 编写单元测试
- [ ] 执行集成测试
- [ ] 向后兼容性验证
- [ ] 路径解析测试

### 第4天: 文档和完善
- [ ] 编写用户文档
- [ ] 编写开发者文档
- [ ] 错误处理完善
- [ ] 命令行帮助文档

## 关键实施细节

### 1. 子命令集成设计（EP）

```python
# 在 core/cli_parser.py 中的实现
def create_parser(config: Optional[CLIConfig] = None) -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='MET Nonlinear 多功能工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 主命令（保持原有功能，向后兼容）
    main_parser = subparsers.add_parser('main', parents=[_create_main_parser(config)], 
                                       add_help=False, help='主要功能命令')
    
    # ep 子命令（简化设计）
    ep_parser = subparsers.add_parser('ep', help='拓展项目管理 (External Project)')
    ep_parser.add_argument('ep_project_path', 
                           help='拓展项目路径，格式: project/task-type/task-name 或统一路径')
    # 无额外参数，直接执行任务
    
    return parser

def _create_main_parser(config: CLIConfig) -> argparse.ArgumentParser:
    """创建主命令解析器（原有的所有功能）"""
    parser = argparse.ArgumentParser(add_help=False)
    # ... 原有的所有参数定义 ...
    return parser
```

### 2. 路径解析器设计

```python
# core/external_path_parser.py
@dataclass
class ExternalPath:
    """EP 路径数据结构"""
    project_name: str
    task_type: str
    task_name: str
    full_path: Path
    config_path: Path
    output_path: Path

class ExternalPathParser:
    """EP 路径解析器"""
    
    SUPPORTED_TASK_TYPES = [
        'freq-response-compare',
        'bias-visualization', 
        'waveform-analysis'
    ]
    
    def parse(self, path_str: str) -> ExternalPath:
        """解析 EP 项目路径"""
        # 规范化路径
        path_str = path_str.replace('\\', '/').strip('/')
        
        # 尝试不同的解析模式
        if self._is_full_path(path_str):
            return self._parse_full_path(path_str)
        elif self._is_relative_path(path_str):
            return self._parse_relative_path(path_str)
        elif self._is_simple_path(path_str):
            return self._parse_simple_path(path_str)
        else:
            raise ValueError(f"无法解析路径格式: {path_str}")
    
    def _parse_full_path(self, path_str: str) -> ExternalPath:
        """解析完整路径: projects/project/visualization/task-type/task-name"""
        parts = path_str.split('/')
        if len(parts) >= 5 and parts[0] == 'projects' and parts[2] == 'visualization':
            project_name = parts[1]
            task_type = parts[3]
            task_name = parts[4]
            return self._build_path_object(project_name, task_type, task_name)
        raise ValueError(f"完整路径格式错误: {path_str}")
    
    def _parse_relative_path(self, path_str: str) -> ExternalPath:
        """解析相对路径: project/task-type/task-name"""
        parts = path_str.split('/')
        if len(parts) == 3:
            project_name, task_type, task_name = parts
            return self._build_path_object(project_name, task_type, task_name)
        raise ValueError(f"相对路径格式错误: {path_str}")
    
    def _parse_simple_path(self, path_str: str) -> ExternalPath:
        """解析简化路径: project/task-name (自动检测task-type)"""
        parts = path_str.split('/')
        if len(parts) == 2:
            project_name, task_name = parts
            task_type = self._detect_task_type(project_name, task_name)
            return self._build_path_object(project_name, task_type, task_name)
        raise ValueError(f"简化路径格式错误: {path_str}")
```

### 3. CLI 处理器设计（EP）

```python
# core/external_cli_handler.py
def handle_ep_command(args: CLIArgs) -> None:
    """处理 ep 子命令（简化版本）"""
    try:
        # 解析路径
    parser = ExternalPathParser()
    ep_path = parser.parse(args.ep_project_path)
        
        # 智能执行：检查配置文件，不存在则创建，然后执行任务
    execute_external_task_auto(ep_path)
            
    except Exception as e:
    logger.error(f"ep 命令执行失败: {e}")
        sys.exit(1)

def execute_external_task_auto(ep_path: ExternalPath) -> None:
    """智能执行 EP 任务"""
    logger.info(f"� 开始处理 EP 任务: {ep_path.task_name}")
    logger.info(f"  - 项目: {ep_path.project_name}")
    logger.info(f"  - 类型: {ep_path.task_type}")
    
    # 检查配置文件是否存在
    if not ep_path.config_path.exists():
        logger.info(f"配置文件不存在，创建模板: {ep_path.config_path}")
        create_ep_template(ep_path)
        logger.info("✅ 配置模板已创建，请编辑后重新运行")
        return
    
    # 执行任务
    logger.info(f"执行 EP 任务...")
    # 实际任务由对应执行器完成，例如 WNET5CircuitValidator
    result = _execute_task(ep_path)
    logger.info(f"✅ 任务执行完成: {result}")
```

```python
FREQ_RESPONSE_TASK_SCHEMA = {
    "type": "object",
    "required": ["task_info", "visualization_config", "data_sources"],
    "properties": {
        "task_info": {
            "type": "object",
            "required": ["task_type", "task_name"],
            "properties": {
                "task_type": {"const": "freq-response-compare"},
                "task_name": {"type": "string", "pattern": "^[a-zA-Z0-9_-]+$"},
                "description": {"type": "string"},
                "version": {"type": "string", "default": "1.0"}
            }
        },
        "visualization_config": {
            "type": "object",
            "properties": {
                "layout": {"enum": ["overlay", "side_by_side"], "default": "overlay"},
                "freq_range": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                "output_format": {"enum": ["png", "svg", "pdf"], "default": "png"},
                "dpi": {"type": "integer", "minimum": 100, "maximum": 600, "default": 300}
            }
        },
        "data_sources": {
            "type": "array",
            "minItems": 1,
            "maxItems": 2,
            "items": {
                "type": "object",
                "required": ["project", "state"],
                "properties": {
                    "project": {"type": "string"},
                    "state": {"enum": ["origin", "compensation"]},
                    "label": {"type": "string"}
                }
            }
        }
    }
}
```

### 4. 配置Schema设计

```python
FREQ_RESPONSE_TASK_SCHEMA = {
    "type": "object",
    "required": ["task_info", "visualization_config", "data_sources"],
    "properties": {
        "task_info": {
            "type": "object",
            "required": ["task_type", "task_name"],
            "properties": {
                "task_type": {"const": "freq-response-compare"},
                "task_name": {"type": "string", "pattern": "^[a-zA-Z0-9_-]+$"},
                "description": {"type": "string"},
                "version": {"type": "string", "default": "1.0"}
            }
        },
        "visualization_config": {
            "type": "object",
            "properties": {
                "layout": {"enum": ["overlay", "side_by_side"], "default": "overlay"},
                "freq_range": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                "output_format": {"enum": ["png", "svg", "pdf"], "default": "png"},
                "dpi": {"type": "integer", "minimum": 100, "maximum": 600, "default": 300}
            }
        },
        "data_sources": {
            "type": "array",
            "minItems": 1,
            "maxItems": 2,
            "items": {
                "type": "object",
                "required": ["project", "state"],
                "properties": {
                    "project": {"type": "string"},
                    "state": {"enum": ["origin", "compensation"]},
                    "label": {"type": "string"}
                }
            }
        }
    }
}
```

### 5. 向后兼容性处理

```python
# 在 cli.py 中的兼容性处理
if __name__ == '__main__':
    logger.info("cli.py start...")
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 检查是否为子命令
    if hasattr(args, 'command') and args.command == 'ep':
        from core.external_cli_handler import handle_ep_command
        handle_ep_command(args)
    else:
        # 原有的主命令处理逻辑（完全保持不变）
        project_names = args.project_names
        dispatch_task(args.task_type.value, project_names, args)
```

### 6. 错误处理策略

**路径解析错误**:
- 提供清晰的路径格式说明
- 给出正确的路径示例
- 支持路径格式建议

**配置错误**:
- 详细的验证错误信息
- 建议修复方案
- 配置模板推荐

**执行错误**:
- 清晰的错误日志
- 部分失败的恢复机制
- 临时文件清理

**文件系统错误**:
- 权限检查和提示
- 目录自动创建
- 路径规范化

### 7. 性能考虑

**配置缓存**:
- 避免重复解析配置文件
- 配置变更检测

**延迟加载**:
- 按需导入可视化模块
- 数据源懒加载

**并发支持**:
- 多任务并行执行能力
- 资源锁定机制

## 验收标准

### 功能性验收
1. **基本功能**:
   - ✅ 能够解析各种格式的可视化项目路径
   - ✅ 能够智能处理配置文件（不存在时自动创建，存在时直接执行）
   - ✅ 能够执行配置驱动的可视化任务
   - ✅ 生成正确的目录结构和输出文件

2. **命令格式**:
   - ✅ `cli.py ep project/task-type/task-name` 正常工作
   - ✅ `cli.py ep path/to/full/vis-project` 正常工作
   - ✅ `cli.py ep project/task-name` 自动检测任务类型
   - ✅ 错误的路径格式给出明确提示

3. **智能行为**:
   - ✅ 首次运行自动创建配置模板并提示用户编辑
   - ✅ 配置存在时直接执行任务
   - ✅ 错误配置给出明确提示和修复建议

4. **兼容性**:
   - ✅ 原有CLI命令完全保持工作 (如 `cli.py -e project`, `cli.py --vis-freq-response-compare`)
   - ✅ 现有项目结构不受影响
   - ✅ 现有可视化功能正常运行

### 质量验收
1. **代码质量**:
   - ✅ 单元测试覆盖率 > 80%
   - ✅ 通过代码静态检查
   - ✅ 符合项目编码规范

2. **文档质量**:
   - ✅ 用户文档完整清晰
   - ✅ 开发者文档准确详细
   - ✅ 示例代码可运行

3. **性能指标**:
   - ✅ 配置解析时间 < 100ms
   - ✅ 任务执行时间无明显增加
   - ✅ 内存使用无明显增长

## 后续扩展计划

### 短期扩展（1-2周）
1. **其他可视化任务类型**:
   - 偏置可视化任务工程化
   - 波形分析任务工程化

2. **高级功能**:
   - 任务批量执行
   - 任务依赖关系管理

### 中期扩展（1个月）
1. **Web界面**:
   - 基于Web的任务管理界面
   - 可视化配置编辑器

2. **自动化集成**:
   - CI/CD流水线集成
   - 定时任务执行

### 长期扩展（3个月）
1. **分布式执行**:
   - 多机器并行执行
   - 云计算资源集成

2. **智能化**:
   - 任务推荐系统
   - 自动参数优化

## 总结

本实现计划描述了一个简化但强大的可视化工程化解决方案：

### 核心优势
1. **简洁的用户界面**: 单一的 `cli.py ep <path>` 命令，无需记忆复杂参数
2. **智能化行为**: 自动检测配置文件，首次运行创建模板，后续直接执行
3. **强大的路径解析**: 支持多种路径格式，自动识别项目结构
4. **完全向后兼容**: 不影响现有CLI功能和工作流程
5. **工程化管理**: 标准化目录结构、配置管理、任务执行

### 设计哲学
- **简单性优于功能性**: 选择最直观的用户体验
- **约定优于配置**: 通过智能默认行为减少用户配置负担
- **渐进式增强**: 从简单开始，根据需要逐步扩展

---

**文档版本**: v2.0 (简化版)  
**编写时间**: 2025年1月10日  
**责任人**: AI Assistant  
**预计完成时间**: 4个工作日