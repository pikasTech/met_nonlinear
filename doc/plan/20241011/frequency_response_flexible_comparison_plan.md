# 灵活频率响应对比可视化CLI实施方案

## 项目概述

基于 MET Nonlinear 项目现有的可视化基础设施，新增一个通用的频率响应对比CLI接口，支持任意两个数据源的灵活对比。核心特性：

1. **任意组合对比**：支持 `project1@origin vs project2@origin`、`project1@origin vs project1@compensation` 等任意组合
2. **灵活布局选择**：通过 `--layout` 参数选择 `overlay` 或 `side_by_side` 布局方式
3. **默认行为保持**：默认行为为 `project@origin vs project@compensation`，保持向后兼容
4. **统一CLI接口**：一个命令解决所有对比需求，简化用户体验

目标是通过新增专门的CLI命令，实现最灵活的频率响应对比可视化功能。

**调研时间**: 2025年1月15日  
**设计时间**: 2025年1月15日  
**调研范围**: `FR_for_comp_real_data` 函数、CLI 接口、配置驱动机制、多项目管理  
**目标功能**: 
- 支持任意两个数据源的对比（project@state语法）
- 支持overlay和side_by_side两种布局模式
- 保持现有功能的向后兼容性

## 现有功能分析

### 核心可视化函数

现有的 `FR_for_comp_real_data` 函数位于 `visualization/model_analysis.py`，具有以下特点：

1. **绘图策略**: 在同一张图上绘制补偿前后的数据
2. **颜色区分**: 使用不同的标记和颜色区分补偿前后
3. **配置驱动**: 支持 `config` 参数传入配置
4. **输出格式**: 生成 JSON 数据和 PNG 图像

### 多项目处理现状

通过调研发现项目已具备多项目处理能力：
- **CLI 支持**: 支持通配符和多项目名称列表
- **任务分发**: `dispatch_task` 函数循环处理 `project_names` 列表
- **项目管理**: `ProjectManager` 类管理单个项目的生命周期
- **可视化复用**: `figure_paper.py` 中已有跨项目比较的先例

## 新CLI接口设计

### 命令语法设计

```bash
# 基本语法
python cli.py --freq-compare [SOURCE1] [SOURCE2] [OPTIONS]

# 示例用法
# 1. 默认行为（项目内补偿前后对比）
python cli.py --freq-compare project1

# 2. 跨项目补偿前对比
python cli.py --freq-compare project1@origin project2@origin

# 3. 项目内补偿前后对比（显式指定）
python cli.py --freq-compare project1@origin project1@compensation

# 4. 指定布局模式
python cli.py --freq-compare project1@origin project2@origin --layout side_by_side

# 5. 使用默认叠加布局
python cli.py --freq-compare project1@origin project2@origin --layout overlay
```

### 参数规范

```python
class DataSourceSpec:
    """数据源规范定义"""
    def __init__(self, project_name: str, state: str = "origin"):
        self.project_name = project_name
        self.state = state  # "origin" | "compensation"
    
    @classmethod
    def parse(cls, source_str: str):
        """解析 project@state 格式的字符串"""
        if '@' in source_str:
            project, state = source_str.split('@', 1)
            return cls(project, state)
        else:
            return cls(source_str, "origin")

class LayoutMode(Enum):
    OVERLAY = "overlay"           # 叠加在同一图上
    SIDE_BY_SIDE = "side_by_side"  # 左右分布子图
```

### CLI参数定义

```python
# 在 core/cli_parser.py 中添加
parser.add_argument('--freq-compare', 
                   nargs='*',  # 支持1-2个参数
                   metavar='PROJECT[@STATE]',
                   help='频率响应对比。格式: PROJECT[@STATE]。'
                        '1个参数: 项目内补偿前后对比；'
                        '2个参数: 任意两个数据源对比。'
                        'STATE可以是origin或compensation，默认为origin')

parser.add_argument('--layout',
                   choices=['overlay', 'side_by_side'],
                   default='overlay',
                   help='布局模式: overlay(叠加) 或 side_by_side(左右分布)，默认overlay')
```

## 核心实现架构

### 1. 数据源管理器

```python
# 新增文件: core/data_source_manager.py

class DataSourceManager:
    """管理多个项目的数据源访问"""
    
    def __init__(self, project_base_path: str):
        self.project_base_path = project_base_path
        self._loaded_projects = {}  # 缓存已加载的项目
    
    def load_data_source(self, source_spec: DataSourceSpec):
        """加载指定的数据源"""
        project_key = source_spec.project_name
        
        # 懒加载项目
        if project_key not in self._loaded_projects:
            project_path = os.path.join(self.project_base_path, project_key)
            project = ProjectManager(project_path)
            
            # 加载模型和数据集
            model_engine = ModelEngine(project)
            model_engine.load_model()
            model_engine.load_dataset()
            
            self._loaded_projects[project_key] = {
                'project': project,
                'model_engine': model_engine,
                'model': model_engine.model_comp,
                'dataset': model_engine.dataset_test
            }
        
        project_data = self._loaded_projects[project_key]
        
        # 根据状态返回相应的数据
        if source_spec.state == "origin":
            return self._extract_origin_data(project_data)
        elif source_spec.state == "compensation":
            return self._extract_compensation_data(project_data)
        else:
            raise ValueError(f"Unknown state: {source_spec.state}")
    
    def _extract_origin_data(self, project_data):
        """提取补偿前数据"""
        # 复用 FR_for_comp_real_data 中的数据提取逻辑
        model = project_data['model']
        dataset = project_data['dataset']
        
        # 计算原始响应
        gains_origin, magnitudes, frequencies = self._compute_frequency_response(
            model, dataset, compensated=False
        )
        
        return {
            'gains': gains_origin,
            'magnitudes': magnitudes,
            'frequencies': frequencies,
            'label': f"{project_data['project'].project_name}@origin"
        }
    
    def _extract_compensation_data(self, project_data):
        """提取补偿后数据"""
        model = project_data['model']
        dataset = project_data['dataset']
        
        # 计算补偿后响应
        gains_comped, magnitudes, frequencies = self._compute_frequency_response(
            model, dataset, compensated=True
        )
        
        return {
            'gains': gains_comped,
            'magnitudes': magnitudes,
            'frequencies': frequencies,
            'label': f"{project_data['project'].project_name}@compensation"
        }
    
    def _compute_frequency_response(self, model, dataset, compensated=False):
        """计算频率响应数据（复用现有逻辑）"""
        # 从 FR_for_comp_real_data 中提取的核心计算逻辑
        # ... 具体实现 ...
        pass
```

### 2. 通用对比可视化器

```python
# 新增文件: visualization/frequency_response_comparator.py

class FrequencyResponseComparator:
    """通用的频率响应对比可视化器"""
    
    def __init__(self, layout_mode: LayoutMode = LayoutMode.OVERLAY):
        self.layout_mode = layout_mode
    
    def compare_data_sources(self, source1_data, source2_data, output_folder='results'):
        """对比两个数据源并生成可视化"""
        
        if self.layout_mode == LayoutMode.OVERLAY:
            return self._create_overlay_plot(source1_data, source2_data, output_folder)
        elif self.layout_mode == LayoutMode.SIDE_BY_SIDE:
            return self._create_side_by_side_plot(source1_data, source2_data, output_folder)
    
    def _create_overlay_plot(self, source1_data, source2_data, output_folder):
        """创建叠加布局的对比图"""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        
        # 绘制数据源1
        self._plot_data_on_axis(ax, source1_data, marker='o', linestyle='-')
        
        # 绘制数据源2
        self._plot_data_on_axis(ax, source2_data, marker='^', linestyle='--')
        
        # 设置图例和标签
        ax.set_xlabel('Magnitude (m/s^2)')
        ax.set_ylabel('Amplitude (Normalized)')
        ax.set_title(f'Frequency Response Comparison: {source1_data["label"]} vs {source2_data["label"]}')
        ax.grid(True)
        ax.legend()
        
        # 保存图像
        output_path = os.path.join(output_folder, 'frequency_response_overlay_comparison.png')
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        
        return fig, output_path
    
    def _create_side_by_side_plot(self, source1_data, source2_data, output_folder):
        """创建左右分布的对比图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), sharey=True, sharex=True)
        
        # 绘制左图（数据源1）
        self._plot_data_on_axis(ax1, source1_data, marker='o')
        ax1.set_title(source1_data['label'])
        ax1.set_xlabel('Magnitude (m/s^2)')
        ax1.set_ylabel('Amplitude (Normalized)')
        ax1.grid(True)
        ax1.legend()
        
        # 绘制右图（数据源2）
        self._plot_data_on_axis(ax2, source2_data, marker='^')
        ax2.set_title(source2_data['label'])
        ax2.set_xlabel('Magnitude (m/s^2)')
        ax2.grid(True)
        ax2.legend()
        
        # 同步坐标轴范围
        self._sync_axis_limits(ax1, ax2)
        
        plt.tight_layout()
        
        # 保存图像
        output_path = os.path.join(output_folder, 'frequency_response_side_by_side_comparison.png')
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        
        return fig, output_path
    
    def _plot_data_on_axis(self, ax, data, marker='o', linestyle='-'):
        """在指定的轴上绘制频率响应数据"""
        gains = data['gains']
        magnitudes = data['magnitudes']
        frequencies = data['frequencies']
        
        color_map = plt.cm.get_cmap("tab20", len(frequencies))
        
        for i, freq in enumerate(frequencies):
            color = color_map(i)
            gain_data = [gains[k][i] for k in range(len(gains))]
            linearity = [gain / gain_data[0] for gain in gain_data]
            outputs_std = [linearity[k] * magnitudes[k] for k in range(len(gain_data))]
            
            ax.plot(magnitudes, outputs_std,
                   label=f'{freq} Hz', linestyle=linestyle, marker=marker,
                   markersize=3, color=color)
    
    def _sync_axis_limits(self, ax1, ax2):
        """同步两个subplot的坐标轴范围"""
        xlim1, ylim1 = ax1.get_xlim(), ax1.get_ylim()
        xlim2, ylim2 = ax2.get_xlim(), ax2.get_ylim()
        
        unified_xlim = (min(xlim1[0], xlim2[0]), max(xlim1[1], xlim2[1]))
        unified_ylim = (min(ylim1[0], ylim2[0]), max(ylim1[1], ylim2[1]))
        
        ax1.set_xlim(unified_xlim)
        ax1.set_ylim(unified_ylim)
        ax2.set_xlim(unified_xlim)
        ax2.set_ylim(unified_ylim)
```

### 3. CLI任务处理器

```python
# 修改文件: core/task_dispatcher.py

def dispatch_task(task_type, project_names, args):
    # ... 现有分发逻辑 ...
    elif hasattr(args, 'freq_compare') and args.freq_compare is not None:
        _handle_freq_compare_task(project_path, args)

def _handle_freq_compare_task(project_path: str, args):
    """处理频率响应对比任务"""
    from core.data_source_manager import DataSourceManager, DataSourceSpec
    from visualization.frequency_response_comparator import FrequencyResponseComparator, LayoutMode
    
    freq_compare_args = args.freq_compare
    layout_mode = LayoutMode(args.layout)
    
    # 解析数据源规范
    if len(freq_compare_args) == 1:
        # 默认行为：项目内补偿前后对比
        project_name = freq_compare_args[0]
        source1_spec = DataSourceSpec(project_name, "origin")
        source2_spec = DataSourceSpec(project_name, "compensation")
        logger.info(f"对比项目 {project_name} 的补偿前后数据")
    elif len(freq_compare_args) == 2:
        # 任意两个数据源对比
        source1_spec = DataSourceSpec.parse(freq_compare_args[0])
        source2_spec = DataSourceSpec.parse(freq_compare_args[1])
        logger.info(f"对比数据源: {source1_spec.project_name}@{source1_spec.state} vs {source2_spec.project_name}@{source2_spec.state}")
    else:
        raise ValueError("--freq-compare 参数数量错误，应为1-2个")
    
    # 加载数据源
    data_manager = DataSourceManager(project_path)
    source1_data = data_manager.load_data_source(source1_spec)
    source2_data = data_manager.load_data_source(source2_spec)
    
    # 创建对比可视化
    comparator = FrequencyResponseComparator(layout_mode)
    fig, output_path = comparator.compare_data_sources(
        source1_data, source2_data, 
        output_folder=os.path.join(project_path, 'results')
    )
    
    logger.info(f"频率响应对比图已生成: {output_path}")
    plt.show()  # 可选：显示图形
```

## 向后兼容性保证

### 1. 现有功能保持不变

- 所有现有的CLI命令和参数完全不受影响
- `FR_for_comp_real_data` 函数保持原有接口和行为
- 现有的配置文件和输出格式保持兼容

### 2. 默认行为保持一致

```python
# 这些调用方式的行为完全一致
python cli.py -e MyProject  # 现有方式
python cli.py --freq-compare MyProject  # 新方式，默认行为相同
```

### 3. 渐进式迁移

用户可以根据需要选择使用新的CLI接口，现有脚本无需修改。

## 使用示例

### 1. 基本对比场景

```bash
# 项目内补偿前后对比（默认overlay布局）
python cli.py --freq-compare MyProject

# 项目内补偿前后对比（side_by_side布局）
python cli.py --freq-compare MyProject --layout side_by_side
```

### 2. 跨项目对比场景

```bash
# 跨项目补偿前数据对比
python cli.py --freq-compare Project1@origin Project2@origin --layout side_by_side

# 跨项目补偿后数据对比
python cli.py --freq-compare Project1@compensation Project2@compensation --layout overlay
```

### 3. 混合对比场景

```bash
# 项目1补偿前 vs 项目2补偿后
python cli.py --freq-compare Project1@origin Project2@compensation --layout side_by_side

# 显式指定项目内对比
python cli.py --freq-compare Project1@origin Project1@compensation --layout overlay
```

## 实施计划和时间估算

### 阶段1：核心架构实现（2天）

1. **DataSourceManager 实现**
   - 项目加载和缓存机制
   - 数据提取逻辑（复用现有FR函数）
   - 状态管理（origin/compensation）

2. **FrequencyResponseComparator 实现**
   - 叠加布局绘图逻辑
   - 左右分布布局绘图逻辑
   - 坐标轴同步和美化

### 阶段2：CLI集成（1天）

1. **参数解析扩展**
   - 添加 `--freq-compare` 参数
   - 添加 `--layout` 参数
   - 参数验证逻辑

2. **任务分发器集成**
   - 添加新的任务处理函数
   - 错误处理和日志记录

### 阶段3：测试和优化（1天）

1. **单元测试**
   - DataSourceSpec 解析测试
   - 数据加载测试
   - 可视化生成测试

2. **集成测试**
   - 完整CLI流程测试
   - 各种参数组合测试
   - 向后兼容性验证

**总计**: 4个工作日

## 质量保证和风险评估

### 风险评估

1. **低风险** 🟢
   - 完全独立的新功能，不修改现有代码
   - 清晰的接口设计和模块化架构
   - 充分复用现有的成熟组件

2. **潜在问题和解决方案**
   - **内存使用**: 多项目同时加载可能占用较多内存
     - 解决方案: 实现懒加载和LRU缓存
   - **参数复杂性**: 新的参数语法可能让用户困惑
     - 解决方案: 提供详细的帮助文档和错误提示

### 测试策略

```python
# 示例测试用例
def test_data_source_spec_parsing():
    # 测试基本解析
    spec1 = DataSourceSpec.parse("Project1")
    assert spec1.project_name == "Project1"
    assert spec1.state == "origin"
    
    # 测试完整解析
    spec2 = DataSourceSpec.parse("Project2@compensation")
    assert spec2.project_name == "Project2"
    assert spec2.state == "compensation"

def test_comparison_workflow():
    # 测试完整的对比工作流
    # ... 集成测试逻辑 ...
```

## 总结

这个新的灵活对比CLI设计具有以下核心优势：

1. **最大灵活性**: 支持任意两个数据源的对比组合，满足所有可能的对比需求
2. **统一接口**: 一个命令解决所有对比场景，用户体验简洁明了
3. **向后兼容**: 完全不影响现有功能，现有用户无需改变使用习惯
4. **可扩展性**: 模块化设计使得未来添加新的数据状态和布局模式变得容易
5. **低风险实施**: 通过新增独立模块实现，风险可控，开发周期短

该方案将在4个工作日内完成，为用户提供强大而直观的频率响应对比可视化能力。

---

**文档版本**: v2.0  
**设计时间**: 2025年1月15日  
**预计实施时间**: 4 个工作日  
**风险评级**: 低风险  
**向后兼容性**: 完全兼容