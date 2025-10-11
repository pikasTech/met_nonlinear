# CLI绘图任务工程化管理系统设计方案

## 调查目的

设计一个工程化的绘图任务管理系统，通过 `cli.py ep path/to/the/vis-project` 子命令和配置文件驱动的方式统一管理可视化任务，实现标准化的目录结构、配置管理和输出组织，提升可视化工作流的可维护性和可扩展性。

## 需求分析

### 核心需求
1. **子命令集成**: 通过 `cli.py ep` 子命令管理可视化项目
2. **路径驱动**: 支持多种路径格式，直接指定可视化项目路径
3. **配置驱动**: 通过JSON配置文件定义绘图任务，而非命令行参数
4. **标准化目录结构**: 统一的项目可视化目录组织方式
5. **任务隔离**: 不同类型的绘图任务独立管理，避免输出文件混乱
6. **向后兼容**: 保持现有CLI接口完全不变

### 新命令格式设计
```bash
# 基本格式
cli.py ep <vis-project-path> [OPTIONS]

# 使用示例
cli.py ep LSTMu32al_rs300_ex2/freq-response-compare/baseline-comparison --execute
cli.py ep projects/LSTMu32al_rs300_ex2/visualization/freq-response-compare/baseline-comparison --validate
cli.py ep LSTMu32al_rs300_ex2/baseline-comparison --create  # 自动检测任务类型
cli.py ep LSTMu32al_rs300_ex2 --list  # 列出所有任务
```

### 支持的路径格式
1. **完整路径**: `projects/{project}/visualization/{task-type}/{task-name}`
2. **相对路径**: `{project}/{task-type}/{task-name}`  
3. **简化路径**: `{project}/{task-name}` (自动检测任务类型)

### 目标目录结构
```
projects/
└── {project_name}/
    ├── config.json                    # 项目配置（现有）
    ├── data/                          # 项目数据（现有）
    │   └── linear_response.json
    └── visualization/                 # 新增：可视化配置和输出
        ├── freq-response-compare/     # 频率响应对比任务类型
        │   ├── {task_name}/          # 具体任务实例
        │   │   ├── config.json       # 任务配置文件
        │   │   └── data/            # 任务输出目录
        │   │       ├── *.png        # 生成的图片
        │   │       └── *.json       # 元数据
        │   └── baseline-comparison/  # 另一个任务实例
        │       ├── config.json
        │       └── data/
        ├── bias-visualization/        # 其他可视化任务类型
        └── waveform-analysis/
```

## 现有基础设施调研

### 1. 配置管理现状

#### 1.1 项目配置系统
- **文件**: `projects/{project_name}/config.json`
- **管理器**: 无专用配置管理器（bias_tuner有ConfigManager可参考）
- **加载方式**: 直接JSON读取

#### 1.2 CLI配置系统
- **文件**: `core/cli_defaults.yaml` 
- **类**: `CLIConfig` (dataclass)
- **支持**: 默认值配置，YAML格式

#### 1.3 可视化配置现状
- **现状**: 通过CLI参数传递，缺乏持久化配置
- **问题**: 复杂配置难以管理，无法版本控制

### 2. 任务分发系统

#### 2.1 现有架构
```python
# core/task_dispatcher.py
def dispatch_task(task_type, project_names, args):
    if freq_compare_sources:
        _handle_freq_response_compare_task(project_names, args)
```

#### 2.2 扩展点分析
- **任务检测**: 通过参数存在性判断
- **参数传递**: `_get_arg_value()` 兼容函数
- **扩展性**: 支持新增任务类型处理函数

### 3. 可视化模块现状

#### 3.1 频率响应对比模块
- **文件**: `visualization/frequency_response_json_comparator.py`
- **功能**: JSON数据加载，双源对比，布局支持
- **输出**: `projects/results/` 目录（不规范）

#### 3.2 其他可视化模块
- **偏置可视化**: `inference/visualization_manager.py`
- **波形可视化**: 分散在多个模块
- **模型分析**: `visualization/model_analysis.py`

## 技术方案设计

### 1. 配置文件格式设计

#### 1.1 任务配置结构
```json
{
  "task_info": {
    "task_type": "freq-response-compare",
    "task_name": "baseline-vs-optimized",
    "description": "对比基线模型与优化模型的频率响应",
    "created_time": "2025-09-15T10:30:00Z",
    "version": "1.0"
  },
  "visualization_config": {
    "method": "--vis-freq-response-compare",
    "layout": "side_by_side",
    "freq_range": [10, 200],
    "magnitude_range": [1.0, 6.0],
    "output_format": "png",
    "dpi": 300
  },
  "data_sources": [
    {
      "project": "LSTMu32al_rs300_ex2",
      "state": "origin",
      "label": "Baseline Model"
    },
    {
      "project": "LSTMu32al_rs300_ex2", 
      "state": "compensation",
      "label": "Optimized Model"
    }
  ],
  "output_config": {
    "save_raw_data": true,
    "generate_metadata": true,
    "export_formats": ["png", "svg"]
  }
}
```

#### 1.2 配置验证Schema
```python
TASK_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["task_info", "visualization_config", "data_sources"],
    "properties": {
        "task_info": {
            "type": "object",
            "required": ["task_type", "task_name"],
            "properties": {
                "task_type": {"type": "string", "enum": ["freq-response-compare", "bias-visualization", "waveform-analysis"]},
                "task_name": {"type": "string", "pattern": "^[a-zA-Z0-9_-]+$"}
            }
        }
    }
}
```

### 2. 目录管理系统

#### 2.1 目录管理器设计
```python
class VisualizationDirectoryManager:
    """可视化目录管理器"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_path = Path(f"projects/{project_name}")
        self.vis_root = self.project_path / "visualization"
    
    def create_task_directory(self, task_type: str, task_name: str) -> Path:
        """创建任务目录结构"""
        task_dir = self.vis_root / task_type / task_name
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "data").mkdir(exist_ok=True)
        return task_dir
    
    def get_task_config_path(self, task_type: str, task_name: str) -> Path:
        """获取任务配置文件路径"""
        return self.vis_root / task_type / task_name / "config.json"
    
    def get_task_output_dir(self, task_type: str, task_name: str) -> Path:
        """获取任务输出目录"""
        return self.vis_root / task_type / task_name / "data"
```

#### 2.2 配置管理器设计
```python
class VisualizationConfigManager:
    """可视化配置管理器"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.dir_manager = VisualizationDirectoryManager(project_name)
    
    def load_task_config(self, task_type: str, task_name: str) -> Dict[str, Any]:
        """加载任务配置"""
        config_path = self.dir_manager.get_task_config_path(task_type, task_name)
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.validate_config(config)
        return config
    
    def create_task_config(self, task_type: str, task_name: str, config: Dict[str, Any]) -> Path:
        """创建任务配置文件"""
        task_dir = self.dir_manager.create_task_directory(task_type, task_name)
        config_path = task_dir / "config.json"
        
        # 添加默认元数据
        config["task_info"]["created_time"] = datetime.now().isoformat()
        config["task_info"]["task_type"] = task_type
        config["task_info"]["task_name"] = task_name
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return config_path
```

### 3. CLI集成方案

#### 3.1 新增CLI参数
```python
# core/cli_parser.py 扩展
viz_group.add_argument('--vis-project', 
                      metavar='PROJECT',
                      help='指定可视化项目名称')
viz_group.add_argument('--vis-task', 
                      metavar='TASK_TYPE/TASK_NAME',
                      help='执行指定的可视化任务。格式: task_type/task_name')
viz_group.add_argument('--vis-list-tasks',
                      action='store_true', 
                      help='列出项目中的所有可视化任务')
viz_group.add_argument('--vis-create-task',
                      metavar='TASK_TYPE/TASK_NAME',
                      help='创建新的可视化任务配置模板')
```

#### 3.2 使用示例
```bash
# 列出项目的可视化任务
conda run -n tf26 python cli.py --vis-project LSTMu32al_rs300_ex2 --vis-list-tasks

# 执行特定可视化任务
conda run -n tf26 python cli.py --vis-project LSTMu32al_rs300_ex2 --vis-task freq-response-compare/baseline-vs-optimized

# 创建新任务配置模板
conda run -n tf26 python cli.py --vis-project LSTMu32al_rs300_ex2 --vis-create-task freq-response-compare/new-comparison
```

### 4. 任务执行引擎

#### 4.1 可视化任务执行器
```python
class VisualizationTaskExecutor:
    """可视化任务执行器"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.config_manager = VisualizationConfigManager(project_name)
        self.dir_manager = VisualizationDirectoryManager(project_name)
    
    def execute_task(self, task_type: str, task_name: str) -> Path:
        """执行可视化任务"""
        # 1. 加载配置
        config = self.config_manager.load_task_config(task_type, task_name)
        
        # 2. 获取输出目录
        output_dir = self.dir_manager.get_task_output_dir(task_type, task_name)
        
        # 3. 根据任务类型分发执行
        if task_type == "freq-response-compare":
            return self._execute_freq_response_compare(config, output_dir)
        elif task_type == "bias-visualization":
            return self._execute_bias_visualization(config, output_dir)
        else:
            raise ValueError(f"不支持的任务类型: {task_type}")
    
    def _execute_freq_response_compare(self, config: Dict[str, Any], output_dir: Path) -> Path:
        """执行频率响应对比任务"""
        from visualization.frequency_response_json_comparator import (
            FrequencyResponseComparator, LinearResponseDataLoader, 
            DataSourceSpec, LayoutMode, DataState
        )
        
        # 解析配置
        vis_config = config["visualization_config"]
        data_sources = config["data_sources"]
        
        # 创建数据源规范
        source_specs = []
        for source in data_sources:
            spec = DataSourceSpec(
                project_name=source["project"],
                state=DataState(source["state"])
            )
            source_specs.append(spec)
        
        # 执行对比
        data_loader = LinearResponseDataLoader("projects")
        source1_data = data_loader.extract_data_source(source_specs[0])
        source2_data = data_loader.extract_data_source(source_specs[1])
        
        # 应用配置中的标签
        source1_data["label"] = data_sources[0].get("label", source1_data["label"])
        source2_data["label"] = data_sources[1].get("label", source2_data["label"])
        
        # 创建对比器
        layout_mode = LayoutMode(vis_config["layout"])
        comparator = FrequencyResponseComparator(layout_mode)
        
        # 生成图像
        fig, output_path = comparator.compare_sources(
            source1_data, source2_data, 
            str(output_dir), show_plot=False
        )
        
        # 生成元数据
        metadata = {
            "task_info": config["task_info"],
            "execution_time": datetime.now().isoformat(),
            "output_files": [output_path],
            "config_used": config
        }
        
        metadata_path = output_dir / "execution_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return Path(output_path)
```

### 5. 任务分发器集成

#### 5.1 修改task_dispatcher.py
```python
def dispatch_task(task_type, project_names, args):
    """任务分发器主函数"""
    
    # 检查是否为工程化可视化任务
    vis_project = _get_arg_value(args, 'vis_project', None)
    vis_task = _get_arg_value(args, 'vis_task', None)
    vis_list_tasks = _get_arg_value(args, 'vis_list_tasks', False)
    vis_create_task = _get_arg_value(args, 'vis_create_task', None)
    
    if vis_project:
        _handle_visualization_project_task(vis_project, vis_task, vis_list_tasks, vis_create_task, args)
        return
    
    # 原有的任务分发逻辑...
    freq_compare_sources = _get_arg_value(args, 'freq_compare_sources', None)
    if freq_compare_sources:
        _handle_freq_response_compare_task(project_names, args)
        return
```

#### 5.2 可视化项目任务处理器
```python
def _handle_visualization_project_task(project_name: str, vis_task: str, 
                                     list_tasks: bool, create_task: str, args):
    """处理工程化可视化任务"""
    from core.visualization_engine import VisualizationEngine
    
    engine = VisualizationEngine(project_name)
    
    if list_tasks:
        tasks = engine.list_tasks()
        logger.info(f"项目 {project_name} 的可视化任务:")
        for task_type, task_list in tasks.items():
            logger.info(f"  {task_type}:")
            for task_name in task_list:
                logger.info(f"    - {task_name}")
    
    elif create_task:
        task_type, task_name = create_task.split('/', 1)
        template_path = engine.create_task_template(task_type, task_name)
        logger.info(f"已创建任务配置模板: {template_path}")
        logger.info("请编辑配置文件后重新执行任务")
    
    elif vis_task:
        task_type, task_name = vis_task.split('/', 1)
        output_path = engine.execute_task(task_type, task_name)
        logger.info(f"✅ 可视化任务执行完成: {output_path}")
    
    else:
        logger.error("必须指定 --vis-task, --vis-list-tasks 或 --vis-create-task 参数")
```

## 实施计划

### 阶段1: 基础架构搭建（1-2天）
1. **创建核心模块**
   - `core/visualization_engine.py` - 可视化引擎
   - `core/visualization_config.py` - 配置管理
   - `core/visualization_directory.py` - 目录管理

2. **扩展CLI解析器**
   - 在 `core/cli_parser.py` 中添加新参数
   - 更新 `CLIArgs` 数据类

3. **修改任务分发器**
   - 在 `core/task_dispatcher.py` 中集成可视化任务处理

### 阶段2: 频率响应任务适配（1天）
1. **适配现有模块**
   - 修改 `frequency_response_json_comparator.py` 支持配置驱动
   - 实现标准化输出路径

2. **创建配置模板**
   - 频率响应对比任务配置模板
   - 配置验证Schema

### 阶段3: 测试与完善（1天）
1. **单元测试**
   - 配置管理器测试
   - 目录管理器测试
   - 任务执行器测试

2. **集成测试**
   - 端到端工作流测试
   - 错误处理测试

### 阶段4: 扩展支持（后续）
1. **其他可视化任务类型**
   - 偏置可视化任务
   - 波形分析任务

2. **高级功能**
   - 任务批量执行
   - 配置版本管理
   - 任务依赖关系

## 技术风险评估

### 高风险
1. **配置文件复杂性**: JSON配置可能过于复杂，影响用户体验
   - **缓解方案**: 提供配置模板和向导工具

2. **向后兼容性**: 可能影响现有CLI使用方式
   - **缓解方案**: 保持原有CLI接口，新功能作为扩展

### 中风险
1. **目录结构变更**: 新增目录结构可能影响现有工作流
   - **缓解方案**: 逐步迁移，提供迁移工具

2. **性能影响**: 配置文件解析可能增加启动时间
   - **缓解方案**: 配置缓存和延迟加载

### 低风险
1. **配置验证错误**: 配置格式错误导致任务失败
   - **缓解方案**: 完善的配置验证和错误提示

## 收益分析

### 直接收益
1. **标准化管理**: 统一的可视化任务组织方式
2. **配置复用**: 复杂配置可以保存和版本控制
3. **输出组织**: 清晰的输出目录结构，便于管理
4. **可扩展性**: 易于添加新的可视化任务类型

### 间接收益
1. **团队协作**: 配置文件可以共享和协作
2. **自动化**: 支持批量任务和CI/CD集成
3. **质量提升**: 标准化流程减少人为错误
4. **维护性**: 清晰的架构便于长期维护

## 总结

该方案通过引入配置驱动的可视化任务管理系统，实现了从命令行参数驱动到工程化配置管理的转变。核心特点包括：

1. **分层架构**: 配置层、管理层、执行层清晰分离
2. **标准化**: 统一的目录结构和配置格式
3. **可扩展**: 支持多种可视化任务类型
4. **向后兼容**: 保持现有CLI接口不变

通过该系统，用户可以通过简单的JSON配置文件定义复杂的可视化任务，实现可重现、可版本控制的可视化工作流，显著提升工程化水平。

---

**文档版本**: v1.0  
**编写时间**: 2025年9月15日  
**下一步**: 实施阶段1的基础架构搭建