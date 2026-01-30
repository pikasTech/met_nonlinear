# 多震级频率响应对比可视化增强实施方案（修订版）

## 项目概述

基于 MET Nonlinear 项目现有的可视化基础设施，增强频率响应对比功能，支持左右图布局选项。扩展目标包括：
1. **单项目内的补偿前后对比**：左图补偿前，右图补偿后
2. **跨项目的补偿前对比**：左图项目A，右图项目B（都是补偿前数据）

目标是在不破坏现有功能的基础上，通过最小修改实现统一的左右布局可视化框架。

**调研时间**: 2025年1月15日  
**修订时间**: 2025年1月15日  
**调研范围**: `FR_for_comp_real_data` 函数、CLI 接口、配置驱动机制、多项目管理  
**目标功能**: 
- 支持左右布局的补偿前后对比图
- 支持左右布局的跨项目补偿前对比图  

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

### 现有参数结构

```python
def FR_for_comp_real_data(
    model,
    dataset: Dataset_COMP,
    freq_range=None,
    gain_range=None,
    use_debug=False,
    freq_start_skip=0,
    freq_end_skip=0,
    output_folder='results',
    use_linear_response=True,
    only_origin=False,
    config=None
):
```

### CLI 集成现状

- **任务类型**: 通过 `model_engine.predict_FR()` 间接调用
- **配置机制**: 支持项目级别的 `config.json` 文件
- **参数传递**: 通过 `ModelEngine` 和 `ProjectManager` 传递
- **多项目处理**: CLI 已支持 `project_names` 列表和通配符

## 实施方案

基于现有基础设施的复用能力和新增的跨项目对比需求，提供两种可靠的实施方案。

### 方案一：统一的对比可视化框架（推荐）

**核心思路**: 创建统一的左右布局框架，通过参数控制对比类型

#### 1.1 新增对比模式枚举

**新增文件**: `visualization/comparison_types.py`

```python
from enum import Enum

class ComparisonType(Enum):
    """对比类型枚举"""
    COMPENSATION_BEFORE_AFTER = "compensation_before_after"  # 单项目补偿前后对比
    PROJECT_BEFORE_BEFORE = "project_before_before"         # 跨项目补偿前对比
    PROJECT_AFTER_AFTER = "project_after_after"             # 跨项目补偿后对比 (未来扩展)

class LayoutMode(Enum):
    """布局模式枚举"""
    OVERLAY = "overlay"           # 叠加模式（现有模式）
    SIDE_BY_SIDE = "side_by_side" # 左右布局模式
```

#### 1.2 配置文件扩展

**修改文件**: `inference/tools/visualization/config.json`

```json
{
  "plots": {
    "overview": true,
    "layer_analysis": true,
    "channel_analysis": true,
    "distribution": true,
    "statistics": true,
    "rms_analysis": false,
    "frequency_response_layout": "overlay"
  },
  "figure": {
    "dpi": 300,
    "figsize": [10, 8],
    "figsize_dual": [16, 8],
    "font_size": 12,
    "style": "seaborn-v0_8-paper"
  },
  "frequency_response": {
    "layout_mode": "overlay",
    "comparison_type": "compensation_before_after",
    "share_axes": true,
    "subplot_titles": {
      "compensation_before_after": ["Compensation Before", "Compensation After"],
      "project_before_before": ["Project A (Before)", "Project B (Before)"]
    },
    "show_reference_line": true,
    "cross_project": {
      "normalize_magnitude_ranges": true,
      "align_frequency_ranges": true,
      "show_project_info": true
    }
  }
}
```

#### 1.3 统一的对比可视化函数

**新增文件**: `visualization/frequency_response_comparison.py`

```python
from .comparison_types import ComparisonType, LayoutMode
from .model_analysis import FR_for_comp_real_data
import matplotlib.pyplot as plt
import numpy as np
import os

class FrequencyResponseComparator:
    """频率响应对比器 - 统一处理各种对比模式"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.default_config = {
            'frequency_response': {
                'layout_mode': 'overlay',
                'comparison_type': 'compensation_before_after',
                'share_axes': True,
                'show_reference_line': True
            },
            'figure': {
                'figsize': [10, 8],
                'figsize_dual': [16, 8],
                'dpi': 300
            }
        }
    
    def compare_compensation_before_after(self, model, dataset, output_folder, 
                                        layout_mode='side_by_side'):
        """
        单项目补偿前后对比
        
        Args:
            model: 模型对象
            dataset: 数据集对象
            output_folder: 输出目录
            layout_mode: 布局模式
        """
        if layout_mode == 'side_by_side':
            return self._generate_compensation_dual_layout(
                model, dataset, output_folder
            )
        else:
            # 使用原有的叠加模式
            return FR_for_comp_real_data(
                model, dataset, 
                output_folder=output_folder,
                use_linear_response=True,
                config=self.config
            )
    
    def compare_projects_before(self, project_data_list, output_folder, 
                              layout_mode='side_by_side'):
        """
        跨项目补偿前数据对比
        
        Args:
            project_data_list: 项目数据列表 [(project_name, model, dataset), ...]
            output_folder: 输出目录
            layout_mode: 布局模式
        """
        if len(project_data_list) != 2:
            raise ValueError("跨项目对比需要恰好两个项目")
        
        if layout_mode == 'side_by_side':
            return self._generate_cross_project_dual_layout(
                project_data_list, output_folder
            )
        else:
            # 叠加模式：在同一图上显示两个项目
            return self._generate_cross_project_overlay(
                project_data_list, output_folder
            )
    
    def _generate_compensation_dual_layout(self, model, dataset, output_folder):
        """生成补偿前后的左右布局对比图"""
        # 计算补偿前后的数据
        X_features = dataset.reshape2feature(dataset.output_ori)
        pre_features = model.predict(X_features, batch_size=10)
        pre_samples = dataset.reshape2sample(pre_features)
        
        # 计算系统响应
        gains_origin, gains_comped = self._calculate_system_responses(
            dataset, pre_samples
        )
        
        # 创建左右布局
        config = self._get_effective_config()
        fig = self._create_dual_layout_plot(
            gains_origin, gains_comped, 
            dataset.magn_list, dataset.freq_list,
            config, comparison_type=ComparisonType.COMPENSATION_BEFORE_AFTER
        )
        
        # 保存图像
        output_path = os.path.join(output_folder, 'frequency_response_compensation_dual.png')
        fig.savefig(output_path, dpi=config['figure']['dpi'], bbox_inches='tight')
        
        return {'output_path': output_path, 'figure': fig}
    
    def _generate_cross_project_dual_layout(self, project_data_list, output_folder):
        """生成跨项目的左右布局对比图"""
        project_gains = []
        project_magnitudes = []
        project_frequencies = []
        project_names = []
        
        for project_name, model, dataset in project_data_list:
            # 只使用原始数据（补偿前）
            gains_origin, _ = self._calculate_system_responses(dataset, None)
            project_gains.append(gains_origin)
            project_magnitudes.append(dataset.magn_list)
            project_frequencies.append(dataset.freq_list)
            project_names.append(project_name)
        
        # 统一频率和震级范围
        unified_freq, unified_magn = self._unify_data_ranges(
            project_frequencies, project_magnitudes
        )
        
        # 创建左右布局
        config = self._get_effective_config()
        fig = self._create_cross_project_dual_layout(
            project_gains, unified_magn, unified_freq,
            project_names, config
        )
        
        # 保存图像
        output_path = os.path.join(output_folder, 'frequency_response_cross_project_dual.png')
        fig.savefig(output_path, dpi=config['figure']['dpi'], bbox_inches='tight')
        
        return {'output_path': output_path, 'figure': fig, 'project_names': project_names}
    
    def _create_dual_layout_plot(self, gains_left, gains_right, magnitudes, 
                               frequencies, config, comparison_type):
        """创建通用的左右布局图"""
        figsize = config['figure']['figsize_dual']
        share_axes = config['frequency_response']['share_axes']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, 
                                      sharey=share_axes, sharex=share_axes)
        
        # 获取标题
        titles = config['frequency_response']['subplot_titles'][comparison_type.value]
        
        # 绘制左右图
        self._plot_frequency_response_data(ax1, gains_left, magnitudes, frequencies, 
                                         marker='o', title=titles[0])
        self._plot_frequency_response_data(ax2, gains_right, magnitudes, frequencies,
                                         marker='^', title=titles[1])
        
        # 统一坐标轴
        if share_axes:
            self._sync_axis_limits(ax1, ax2)
        
        # 添加理想响应线
        if config['frequency_response']['show_reference_line']:
            self._add_reference_lines([ax1, ax2], magnitudes)
        
        plt.tight_layout()
        return fig
    
    def _create_cross_project_dual_layout(self, project_gains, magnitudes, 
                                        frequencies, project_names, config):
        """创建跨项目的左右布局图"""
        figsize = config['figure']['figsize_dual']
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, sharey=True, sharex=True)
        
        # 绘制两个项目的数据
        self._plot_frequency_response_data(ax1, project_gains[0], magnitudes, frequencies,
                                         marker='o', title=f"{project_names[0]} (Before Compensation)")
        self._plot_frequency_response_data(ax2, project_gains[1], magnitudes, frequencies,
                                         marker='s', title=f"{project_names[1]} (Before Compensation)")
        
        # 统一坐标轴
        self._sync_axis_limits(ax1, ax2)
        
        # 添加理想响应线
        if config['frequency_response']['show_reference_line']:
            self._add_reference_lines([ax1, ax2], magnitudes)
        
        plt.tight_layout()
        return fig
    
    def _calculate_system_responses(self, dataset, pre_samples=None):
        """计算系统响应（复用原有逻辑）"""
        # 这里复用 FR_for_comp_real_data 中的计算逻辑
        # ... 省略具体实现 ...
        pass
    
    def _plot_frequency_response_data(self, ax, gains_data, magnitudes, frequencies, 
                                    marker='o', title=""):
        """在指定axes上绘制频率响应数据"""
        # 复用原有的绘图逻辑
        # ... 省略具体实现 ...
        pass
    
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
    
    def _unify_data_ranges(self, frequencies_list, magnitudes_list):
        """统一多个项目的频率和震级范围"""
        # 找到公共的频率范围
        common_freq = frequencies_list[0]  # 简化实现
        common_magn = magnitudes_list[0]   # 简化实现
        return common_freq, common_magn
    
    def _get_effective_config(self):
        """获取有效配置（合并默认配置和用户配置）"""
        effective_config = self.default_config.copy()
        if self.config:
            # 深度合并配置
            for key, value in self.config.items():
                if key in effective_config and isinstance(value, dict):
                    effective_config[key].update(value)
                else:
                    effective_config[key] = value
        return effective_config
```

#### 1.4 CLI 接口扩展

**修改文件**: `core/cli_parser.py`

```python
class TaskType(Enum):
    # ... 现有类型 ...
    FREQ_RESPONSE_DUAL = "freq_response_dual"      # 单项目补偿前后左右对比
    FREQ_RESPONSE_CROSS = "freq_response_cross"    # 跨项目补偿前左右对比

# 在任务组中添加新选项
task_group.add_argument('--freq-dual', action='store_const',
                       const=TaskType.FREQ_RESPONSE_DUAL, dest='task_type',
                       help='生成单项目补偿前后左右对比图')
task_group.add_argument('--freq-cross', action='store_const',
                       const=TaskType.FREQ_RESPONSE_CROSS, dest='task_type',
                       help='生成跨项目补偿前左右对比图（需要两个项目）')

# 在可视化参数组中添加新参数
viz_group.add_argument('--comparison-type', 
                      choices=['compensation', 'cross_project'],
                      help='对比类型: compensation(补偿前后) 或 cross_project(跨项目)')
viz_group.add_argument('--layout', 
                      choices=['overlay', 'side_by_side'],
                      default='side_by_side',
                      help='布局模式: overlay(叠加) 或 side_by_side(左右)')
```

#### 1.5 任务分发器扩展

**修改文件**: `core/task_dispatcher.py`

```python
def dispatch_task(task_type, project_names, args):
    # ... 现有分发逻辑 ...
    elif task_type == 'freq_response_dual':
        _handle_freq_response_dual_task(project_names, args)
    elif task_type == 'freq_response_cross':
        _handle_freq_response_cross_task(project_names, args)

def _handle_freq_response_dual_task(project_names, args):
    """处理单项目补偿前后左右对比任务"""
    if len(project_names) != 1:
        logger.error("单项目对比需要恰好一个项目名称")
        return
    
    project_name = project_names[0]
    project_path = f'projects/{project_name}'
    
    logger.info(f"开始为项目 {project_name} 生成补偿前后左右对比图")
    
    from visualization.frequency_response_comparison import FrequencyResponseComparator
    from core.project_manager import ProjectManager
    from core.model_engine import ModelEngine
    
    # 准备项目数据
    project = ProjectManager(project_path)
    model_engine = ModelEngine(project)
    model_engine.load_model()
    model_engine.load_dataset()
    
    # 创建对比器
    config = _load_visualization_config(args)
    comparator = FrequencyResponseComparator(config)
    
    # 执行对比
    result = comparator.compare_compensation_before_after(
        model_engine.model_comp,
        model_engine.dataset_test,
        project.checkpoint_dir,
        layout_mode='side_by_side'
    )
    
    logger.info(f"✅ 补偿前后左右对比图生成完成")
    logger.info(f"   输出文件: {result['output_path']}")

def _handle_freq_response_cross_task(project_names, args):
    """处理跨项目补偿前左右对比任务"""
    if len(project_names) != 2:
        logger.error("跨项目对比需要恰好两个项目名称")
        return
    
    logger.info(f"开始生成项目 {project_names[0]} 和 {project_names[1]} 的跨项目对比图")
    
    from visualization.frequency_response_comparison import FrequencyResponseComparator
    from core.project_manager import ProjectManager
    from core.model_engine import ModelEngine
    
    # 准备两个项目的数据
    project_data_list = []
    for project_name in project_names:
        project_path = f'projects/{project_name}'
        project = ProjectManager(project_path)
        model_engine = ModelEngine(project)
        model_engine.load_model()
        model_engine.load_dataset()
        
        project_data_list.append((project_name, model_engine.model_comp, model_engine.dataset_test))
    
    # 创建对比器
    config = _load_visualization_config(args)
    comparator = FrequencyResponseComparator(config)
    
    # 执行跨项目对比
    output_folder = f'results/cross_project_comparison_{project_names[0]}_vs_{project_names[1]}'
    os.makedirs(output_folder, exist_ok=True)
    
    result = comparator.compare_projects_before(
        project_data_list,
        output_folder,
        layout_mode='side_by_side'
    )
    
    logger.info(f"✅ 跨项目左右对比图生成完成")
    logger.info(f"   对比项目: {' vs '.join(result['project_names'])}")
    logger.info(f"   输出文件: {result['output_path']}")

def _load_visualization_config(args):
    """加载可视化配置"""
    config_path = _get_arg_value(args, 'vis_config_path', None)
    if config_path and os.path.exists(config_path):
        import json
        with open(config_path, 'r') as f:
            return json.load(f)
    
    # 返回默认配置
    return {
        'frequency_response': {
            'layout_mode': _get_arg_value(args, 'layout', 'side_by_side'),
            'comparison_type': _get_arg_value(args, 'comparison_type', 'compensation'),
            'share_axes': True,
            'show_reference_line': True
        },
        'figure': {
            'figsize_dual': [16, 8],
            'dpi': 300
        }
    }
```

### 方案二：渐进式功能扩展

**核心思路**: 分步实现，先支持单项目补偿前后对比，再扩展跨项目对比

#### 2.1 第一阶段：扩展现有函数

**修改文件**: `visualization/model_analysis.py`

直接在 `FR_for_comp_real_data` 函数中添加左右布局支持，保持最小修改。

#### 2.2 第二阶段：新增跨项目任务

**新增文件**: `visualization/cross_project_comparison.py`

```python
def compare_projects_frequency_response(project_names, output_folder, config=None):
    """
    跨项目频率响应对比
    
    Args:
        project_names: 项目名称列表（需要恰好两个）
        output_folder: 输出目录
        config: 配置参数
    """
    if len(project_names) != 2:
        raise ValueError("跨项目对比需要恰好两个项目")
    
    # 加载两个项目的数据
    project_data = []
    for project_name in project_names:
        project_path = f'projects/{project_name}'
        project = ProjectManager(project_path)
        model_engine = ModelEngine(project)
        model_engine.load_model()
        model_engine.load_dataset()
        
        # 只使用原始数据（补偿前）
        gains_origin = extract_origin_gains(model_engine.dataset_test)
        project_data.append({
            'name': project_name,
            'gains': gains_origin,
            'magnitudes': model_engine.dataset_test.magn_list,
            'frequencies': model_engine.dataset_test.freq_list
        })
    
    # 生成对比图
    fig = create_cross_project_comparison_plot(project_data, config)
    
    # 保存图像
    output_path = os.path.join(output_folder, f'cross_project_comparison_{project_names[0]}_vs_{project_names[1]}.png')
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    
    return {'output_path': output_path, 'project_names': project_names}
```

#### 2.3 CLI 任务扩展

**修改文件**: `core/cli_parser.py`

```python
class TaskType(Enum):
    # ... 现有类型 ...
    FREQ_CROSS_PROJECT = "freq_cross_project"  # 跨项目频率响应对比

task_group.add_argument('--freq-cross', action='store_const',
                       const=TaskType.FREQ_CROSS_PROJECT, dest='task_type',
                       help='生成跨项目频率响应对比图（需要两个项目）')
```

#### 2.4 任务分发器扩展

**修改文件**: `core/task_dispatcher.py`

```python
def dispatch_task(task_type, project_names, args):
    # ... 现有分发逻辑 ...
    elif task_type == 'freq_cross_project':
        _handle_cross_project_freq_task(project_names, args)

def _handle_cross_project_freq_task(project_names, args):
    """处理跨项目频率响应对比任务"""
    if len(project_names) != 2:
        logger.error("跨项目对比需要恰好两个项目名称")
        return
    
    from visualization.cross_project_comparison import compare_projects_frequency_response
    
    output_folder = f'results/cross_project_{project_names[0]}_vs_{project_names[1]}'
    os.makedirs(output_folder, exist_ok=True)
    
    result = compare_projects_frequency_response(project_names, output_folder)
    
    logger.info(f"✅ 跨项目对比完成: {' vs '.join(result['project_names'])}")
    logger.info(f"   输出文件: {result['output_path']}")
```

## 实施优先级和风险评估

### 方案一（推荐）- 统一对比框架

**优势**:
- ✅ 统一的架构设计，支持多种对比模式
- ✅ 完全向后兼容，不影响现有功能
- ✅ 符合项目的配置驱动设计哲学
- ✅ 易于扩展其他对比类型（如补偿后的跨项目对比）
- ✅ 复用现有的基础设施最充分
- ✅ 支持跨项目对比的高级功能

**风险评估**:
- 🟡 **低风险**: 主要是功能扩展，核心逻辑保持独立
- 🟡 **配置复杂性**: 增加了配置项，但有合理的默认值和类型系统
- 🟢 **测试风险**: 可以独立测试新功能，不影响现有测试
- 🟡 **跨项目复杂性**: 需要处理数据范围统一和项目间兼容性

**实施估时**: 4-5 天（包含跨项目对比功能）

### 方案二 - 渐进式扩展

**优势**:
- ✅ 分步实现，风险可控
- ✅ 可以先实现单项目对比，快速验证效果
- ✅ 每个阶段都有独立的价值

**风险评估**:
- 🟡 **中等风险**: 需要分多个阶段协调开发
- 🟠 **代码重复**: 可能导致部分逻辑重复
- 🟠 **维护成本**: 需要维护多个相似的功能模块

**实施估时**: 3-4 天（第一阶段）+ 2-3 天（第二阶段）

### 新需求带来的技术挑战

#### 跨项目数据兼容性

**挑战**:
- 不同项目的频率范围可能不同
- 震级范围可能不一致
- 数据集结构可能有差异

**解决方案**:
```python
def _unify_data_ranges(self, project_data_list):
    """统一多个项目的数据范围"""
    # 找到公共频率范围
    freq_ranges = [data['frequencies'] for data in project_data_list]
    common_freq = self._find_common_frequency_range(freq_ranges)
    
    # 找到公共震级范围
    magn_ranges = [data['magnitudes'] for data in project_data_list]
    common_magn = self._find_common_magnitude_range(magn_ranges)
    
    # 插值和标准化数据
    unified_data = []
    for data in project_data_list:
        unified_gains = self._interpolate_to_common_range(
            data['gains'], data['frequencies'], data['magnitudes'],
            common_freq, common_magn
        )
        unified_data.append({
            'name': data['name'],
            'gains': unified_gains,
            'frequencies': common_freq,
            'magnitudes': common_magn
        })
    
    return unified_data, common_freq, common_magn
```

#### CLI 参数复杂性

**挑战**: 需要支持单项目和多项目两种模式

**解决方案**:
```bash
# 单项目补偿前后对比
python cli.py --freq-dual PROJECT_A

# 跨项目补偿前对比
python cli.py --freq-cross PROJECT_A PROJECT_B

# 带配置的对比
python cli.py --freq-dual PROJECT_A --layout side_by_side --vis-config custom_config.json
```

## 技术细节和关键实现点

### 坐标轴同步机制

```python
def _sync_axis_limits(ax1, ax2):
    """同步两个subplot的坐标轴范围"""
    # 获取两个图的数据范围
    xlim1, ylim1 = ax1.get_xlim(), ax1.get_ylim()
    xlim2, ylim2 = ax2.get_xlim(), ax2.get_ylim()
    
    # 计算统一的范围
    unified_xlim = (min(xlim1[0], xlim2[0]), max(xlim1[1], xlim2[1]))
    unified_ylim = (min(ylim1[0], ylim2[0]), max(ylim1[1], ylim2[1]))
    
    # 应用统一范围
    ax1.set_xlim(unified_xlim)
    ax1.set_ylim(unified_ylim)
    ax2.set_xlim(unified_xlim)
    ax2.set_ylim(unified_ylim)
```

### 配置优先级机制

```python
def _resolve_layout_config(explicit_param, config_dict, default='overlay'):
    """解析布局配置的优先级：CLI参数 > 配置文件 > 默认值"""
    if explicit_param is not None:
        return explicit_param
    if config_dict and 'frequency_response' in config_dict:
        return config_dict['frequency_response'].get('layout_mode', default)
    return default
```

### 向后兼容性保证

- 现有的调用方式完全不变
- 新参数都有合理的默认值
- 配置文件是可选的
- 现有的输出文件格式保持不变

## 使用示例

### 单项目补偿前后对比

#### 配置文件驱动（方案一）

```bash
# 修改项目配置文件
echo '{"frequency_response": {"layout_mode": "side_by_side", "comparison_type": "compensation_before_after"}}' > projects/MyProject/vis_config.json

# 运行评估（将自动使用左右布局）
python cli.py -e MyProject --vis-config projects/MyProject/vis_config.json
```

#### CLI 参数驱动（方案一）

```bash
# 直接通过命令行指定布局
python cli.py --freq-dual MyProject --layout side_by_side
```

#### 独立任务驱动（方案二）

```bash
# 使用专门的任务类型
python cli.py --freq-dual MyProject
```

### 跨项目补偿前对比

#### 基础跨项目对比（方案一）

```bash
# 对比两个项目的补偿前数据
python cli.py --freq-cross PROJECT_A PROJECT_B --layout side_by_side
```

#### 带配置的跨项目对比

```bash
# 使用自定义配置进行跨项目对比
python cli.py --freq-cross PROJECT_A PROJECT_B \
  --vis-config cross_project_config.json \
  --vis-output results/cross_comparison
```

**配置文件示例** (`cross_project_config.json`):
```json
{
  "frequency_response": {
    "layout_mode": "side_by_side",
    "comparison_type": "project_before_before",
    "share_axes": true,
    "subplot_titles": {
      "project_before_before": ["WNET5 Model", "LSTM Model"]
    },
    "cross_project": {
      "normalize_magnitude_ranges": true,
      "align_frequency_ranges": true,
      "show_project_info": true
    }
  },
  "figure": {
    "figsize_dual": [18, 8],
    "dpi": 300
  }
}
```

### 高级使用场景

#### 批量项目对比

```bash
# 对比多个项目组合
for project_a in WNET5_* ; do
  for project_b in LSTM_* ; do
    python cli.py --freq-cross $project_a $project_b \
      --vis-output results/batch_comparison/$project_a\_vs_$project_b
  done
done
```

#### 与现有功能结合

```bash
# 先生成传统的叠加图，再生成左右对比图
python cli.py -e MyProject                    # 生成传统叠加图
python cli.py --freq-dual MyProject          # 生成左右对比图

# 同时生成两种格式
python cli.py -e MyProject --freq-layout overlay     # 叠加模式
python cli.py -e MyProject --freq-layout side_by_side # 左右模式
```

## 质量保证和测试策略

### 单元测试

- 测试新的绘图函数
- 测试配置解析逻辑
- 测试坐标轴同步机制

### 集成测试

- 测试 CLI 到可视化的完整流程
- 测试向后兼容性
- 测试不同配置组合的效果

### 回归测试

- 确保现有功能不受影响
- 验证默认行为保持不变
- 检查输出格式兼容性

## 总结

基于 MET Nonlinear 项目强大的基础设施和配置驱动架构，以及新增的跨项目对比需求，推荐采用**方案一（统一的对比可视化框架）**。该方案具有以下核心优势：

### 🏆 推荐方案的核心价值

1. **统一的架构设计**: 通过 `FrequencyResponseComparator` 类统一处理单项目和跨项目对比
2. **最大兼容性**: 完全保持现有功能不变，提供渐进式升级路径
3. **最佳扩展性**: 为未来添加更多对比模式（如补偿后的跨项目对比、三项目对比等）提供了坚实基础
4. **配置驱动**: 继承项目的配置驱动哲学，支持灵活的自定义配置

### 🚀 功能矩阵

| 功能特性 | 方案一 | 方案二 | 说明 |
|---------|--------|--------|------|
| 单项目补偿前后对比 | ✅ | ✅ | 两种方案都支持 |
| 跨项目补偿前对比 | ✅ | ⚠️  | 方案一原生支持，方案二需要额外开发 |
| 配置驱动 | ✅ | ⚠️  | 方案一统一配置，方案二分散配置 |
| CLI 集成 | ✅ | ✅ | 两种方案都有良好的CLI支持 |
| 向后兼容 | ✅ | ✅ | 完全兼容现有功能 |
| 代码复用 | ✅ | ⚠️  | 方案一复用度更高 |
| 维护成本 | 低 | 中 | 方案一统一架构，维护成本更低 |

### 📊 实施路线图

#### 第一阶段（2-3天）：核心框架
- 创建 `FrequencyResponseComparator` 类
- 实现单项目补偿前后对比的左右布局
- CLI 接口和配置系统集成

#### 第二阶段（1-2天）：跨项目支持  
- 实现跨项目数据兼容性处理
- 添加跨项目对比的CLI命令
- 数据范围统一和插值算法

#### 第三阶段（1天）：测试和优化
- 单元测试和集成测试
- 性能优化和错误处理
- 文档和使用示例完善

### 🎯 技术亮点

1. **智能数据统一**: 自动处理不同项目间的频率和震级范围差异
2. **坐标轴同步**: 确保左右图具有一致的视觉比较基准
3. **配置层次化**: 支持全局配置、项目配置、CLI参数的优先级机制
4. **可扩展架构**: 为未来功能扩展（如3D可视化、动态对比等）预留接口

### 💡 投资回报分析

- **开发投入**: 4-5天（包含完整的跨项目对比功能）
- **维护成本**: 低（统一架构，配置驱动）
- **用户价值**: 高（支持多种科学研究场景的可视化需求）
- **技术债务**: 无（完全基于现有架构扩展）

该方案将通过约 400-500 行新增代码，在4-5天内完成实施，为用户提供强大而灵活的频率响应对比可视化能力，同时为项目的长期发展奠定坚实基础。

---

**文档版本**: v2.0（修订版）  
**编写时间**: 2025年1月15日  
**修订时间**: 2025年1月15日  
**预计实施时间**: 4-5 个工作日  
**风险评级**: 低风险  
**向后兼容性**: 完全兼容  
**新增功能**: 跨项目对比支持