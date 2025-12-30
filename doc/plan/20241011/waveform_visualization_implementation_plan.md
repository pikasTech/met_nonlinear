# Origin/Target波形可视化功能实施计划

## 实施日期
2025年9月10日

## 功能需求概述
设计并实现一个CLI集成的波形可视化功能，能够：
1. 绘制Origin和Target波形的对比图
2. 按不同频率和震级分别保存PNG文件
3. 集成到cli.py中作为新的命令行任务
4. 输出到projects/xxx/data/visualizations目录

## 深入基础设施调研结果

### 1. CLI架构分析
**现有CLI结构** (`cli.py` + `core/task_dispatcher.py`):
- CLI使用现代化的参数解析器 (`core/c### 3. 模块化设计
- **独立模块**: WaveformVisualizer可独立测试和维护
- **清晰接口**: 通过ProjectManager解耦数据加载逻辑
- **扩展性**: 易于添加新的可视化类型（频域、相位等）
- **目录组织**: visualizations/{type}/结构为不同可视化类型提供清晰分类arser.py`)
- 任务分发通过 `task_dispatcher.py` 统一管理
- 支持多种任务类型：`train`, `evaluate`, `inference`, `analyze`, `wave`, `bias_visualization`等
- 每个任务都有独立的处理函数，遵循 `_handle_xxx_task()` 命名规范

### 2. 数据处理基础设施分析
**Dataset_COMP类体系**:
- **核心基类**: `Dataset_COMP` - 提供标准的数据结构 `(magn_num, freq_num, points_num)`
- **具体实现**: 
  - `Dataset_COMP_MET` - 真实测量数据
  - `Dataset_COMP_Alias` - 混叠失真数据  
  - `Dataset_COMP_PE` - 压电传感器仿真数据

**关键数据属性**:
```python
self.inputs: np.ndarray      # 输入波形 (magn_num, freq_num, points_num)
self.output_ori: np.ndarray  # 原始输出 (magn_num, freq_num, points_num) 
self.output_tar: np.ndarray  # 目标输出 (magn_num, freq_num, points_num)
self.magn_list: List[float]  # 震级列表 [0.72, 1.2, 6.0, ...]
self.freq_list: List[float]  # 频率列表 [20, 40, 100, ...]
self.fs: int                 # 采样频率 2000Hz
```

### 3. 项目目录结构分析
**标准项目路径**: `projects/{project_name}/data/`
- 现有子目录: `wave_output/`, `spice_netlists/`, `temp/`, `scalers/`
- 推荐新增: `visualizations/waveforms/` - 专门存放波形可视化输出
- 预留扩展: `visualizations/frequency/`, `visualizations/phase/` 等其他绘图类型

### 4. 可视化基础设施分析
**TimeSeries绘图能力**:
- `TimeSeries.plot()` - 基础时域绘图功能
- 支持matplotlib集成，包含标签、网格、图例等
- 已在多个测试函数中使用 (`test_timeseries_generate()`)

**现有可视化参考**:
- `visualization/figure_paper.py` - 复杂学术图表生成
- `calibration_analyzer/dataplot.py` - 数据分析绘图
- `paper/fig_process/plot_predict.py` - 预测结果对比绘图

### 5. 项目配置加载分析
**ProjectManager机制**:
- 通过 `ProjectManager(project_path)` 加载项目配置
- 自动检测数据集类型并实例化对应的Dataset类
- 集成数据加载、缓存、验证等完整流程

## 技术实施方案

### 架构设计原则
1. **最大化复用**: 利用现有Dataset_COMP数据加载逻辑
2. **最小化修改**: 在现有CLI框架基础上扩展
3. **模块化设计**: 独立的可视化模块，便于测试和维护
4. **一致性保证**: 遵循现有代码规范和目录结构

### 核心实施策略

#### 1. 新建可视化模块
**文件**: `core/waveform_visualizer.py`
**功能**: 专门处理Origin/Target波形可视化逻辑

#### 2. 扩展CLI任务类型
在现有 `TaskType` 枚举中添加 `WAVEFORM_VIS` 任务类型

#### 3. 集成项目管理器
复用 `ProjectManager` 的数据集加载能力，避免重复实现

## 详细修改计划

### 修改点1: 扩展CLI参数解析器
**文件**: `core/cli_parser.py`
**位置**: TaskType枚举定义处
**修改内容**:
```python
class TaskType(Enum):
    # ... 现有任务类型 ...
    WAVEFORM_VIS = "waveform_vis"  # 新增波形可视化任务
```

**位置**: 参数解析器创建函数
**修改内容**:
```python
task_group.add_argument('--vis', '--waveform-vis', action='store_const',
                       const=TaskType.WAVEFORM_VIS, dest='task_type',
                       help='生成Origin/Target波形可视化图')
```

### 修改点2: 创建核心可视化模块
**文件**: `core/waveform_visualizer.py`
**功能**: 波形可视化核心逻辑
**实现内容**:
```python
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 无GUI后端
import numpy as np
from typing import Optional, Dict, List, Tuple
import logging
from calibration_analyzer.exam_class import TimeSeries

logger = logging.getLogger(__name__)

class WaveformVisualizer:
    """Origin/Target波形可视化器"""
    
    def __init__(self, project_manager):
        self.project_manager = project_manager
        self.output_dir = os.path.join(
            project_manager.checkpoint_dir, 
            'visualizations',
            'waveforms'  # 专门的波形子目录
        )
        os.makedirs(self.output_dir, exist_ok=True)
    
    def visualize_dataset(self, force: bool = False) -> Dict[str, List[str]]:
        """
        生成数据集的所有波形可视化图
        
        Returns:
            Dict: 包含生成的文件路径信息
        """
        # 1. 加载数据集
        dataset = self._load_dataset()
        
        # 2. 生成所有组合的可视化图
        generated_files = []
        
        for mag_idx, magnitude in enumerate(dataset.magn_list):
            for freq_idx, frequency in enumerate(dataset.freq_list):
                # 检查现有文件
                output_path = self._get_output_path(magnitude, frequency)
                if os.path.exists(output_path) and not force:
                    logger.info(f"跳过已存在的文件: {output_path}")
                    continue
                
                # 生成单个波形图
                self._plot_single_waveform(
                    dataset, mag_idx, freq_idx, magnitude, frequency, output_path
                )
                generated_files.append(output_path)
                
        return {
            'generated_files': generated_files,
            'output_directory': self.output_dir,
            'total_combinations': len(dataset.magn_list) * len(dataset.freq_list)
        }
    
    def _load_dataset(self):
        """加载项目数据集"""
        # 复用ProjectManager的数据集加载逻辑
        return self.project_manager.load_dataset()
    
    def _get_output_path(self, magnitude: float, frequency: float) -> str:
        """生成输出文件路径"""
        filename = f"waveform_mag{magnitude:.2f}_freq{frequency:.1f}Hz.png"
        return os.path.join(self.output_dir, filename)
    
    def _plot_single_waveform(self, dataset, mag_idx: int, freq_idx: int, 
                            magnitude: float, frequency: float, output_path: str):
        """绘制单个频率/震级组合的波形图"""
        # 提取数据
        origin_data = dataset.output_ori[mag_idx, freq_idx, :]
        target_data = dataset.output_tar[mag_idx, freq_idx, :]
        
        # 创建TimeSeries对象
        origin_ts = TimeSeries(samples=origin_data, fs=dataset.fs)
        target_ts = TimeSeries(samples=target_data, fs=dataset.fs)
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 绘制波形
        ax.plot(origin_ts.time, origin_ts.samples, 
               label=f'Origin (Mag={magnitude:.2f})', 
               color='blue', alpha=0.7, linewidth=1.5)
        ax.plot(target_ts.time, target_ts.samples, 
               label=f'Target (Mag={magnitude:.2f})', 
               color='red', alpha=0.7, linewidth=1.5)
        
        # 设置图形属性
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.set_title(f'Origin vs Target Waveforms\n'
                    f'Frequency: {frequency:.1f} Hz, Magnitude: {magnitude:.2f}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 保存图形
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"已生成波形图: {output_path}")
```

### 修改点3: 扩展任务分发器
**文件**: `core/task_dispatcher.py`
**位置**: dispatch_task函数中的任务分发逻辑
**修改内容**:
```python
def dispatch_task(task_type, project_names, args):
    """根据任务类型分发执行任务"""
    for project_name in project_names:
        # ... 现有代码 ...
        
        try:
            # ... 现有任务类型处理 ...
            elif task_type == 'waveform_vis':
                _handle_waveform_vis_task(project_path, project_name, args)
            # ... 其他任务类型 ...
```

**新增任务处理函数**:
```python
def _handle_waveform_vis_task(project_path: str, project_name: str, args):
    """处理波形可视化任务"""
    from core.waveform_visualizer import WaveformVisualizer
    
    logger.info(f"开始为项目 {project_name} 生成波形可视化")
    
    # 创建项目管理器
    project = ProjectManager(project_path)
    
    # 创建可视化器
    visualizer = WaveformVisualizer(project)
    
    # 执行可视化
    force = _get_arg_value(args, 'force_mode', False)
    result = visualizer.visualize_dataset(force=force)
    
    # 输出结果
    logger.info(f"可视化完成:")
    logger.info(f"  - 输出目录: {result['output_directory']}")
    logger.info(f"  - 波形文件: visualizations/waveforms/")
    logger.info(f"  - 生成文件数: {len(result['generated_files'])}")
    logger.info(f"  - 总组合数: {result['total_combinations']}")
    
    if result['generated_files']:
        logger.info("生成的文件列表:")
        for file_path in result['generated_files']:
            logger.info(f"  - {os.path.basename(file_path)}")
```

### 修改点4: 确保ProjectManager支持数据集加载
**文件**: `core/project_manager.py`
**验证**: 确认现有的load_dataset方法能正确加载Dataset_COMP类实例
**如需修改**: 添加专门的数据集加载方法
```python
def load_dataset(self):
    """加载项目数据集用于可视化"""
    # 检查现有实现，确保返回Dataset_COMP实例
    # 如果需要，添加适配代码
    pass
```

### 修改点5: CLI使用说明更新
**文件**: CLI帮助文档和README
**添加使用示例**:
```bash
# 生成单个项目的波形可视化
python cli.py --vis PROJECT_NAME

# 强制重新生成（覆盖已存在文件）
python cli.py --vis PROJECT_NAME -f

# 批量生成多个项目
python cli.py --vis PROJECT_PATTERN*
```

## 输出文件组织结构

### 目录结构
```
projects/
└── {project_name}/
    └── data/
        └── visualizations/              # 可视化根目录
            └── waveforms/               # 波形可视化子目录
                ├── waveform_mag0.72_freq20.0Hz.png
                ├── waveform_mag0.72_freq40.0Hz.png
                ├── waveform_mag1.20_freq20.0Hz.png
                ├── waveform_mag1.20_freq40.0Hz.png
                └── ... (按震级×频率组合)
            # 预留其他可视化类型目录：
            # ├── frequency/               # 频域分析图
            # ├── phase/                   # 相位分析图
            # ├── nonlinearity/            # 非线性度分析图
            # └── comparison/              # 对比分析图
```

### 文件命名规范
- 格式: `waveform_mag{magnitude:.2f}_freq{frequency:.1f}Hz.png`
- 示例: `waveform_mag1.20_freq40.0Hz.png`
- 确保文件名在不同操作系统下兼容

## 技术优势

### 1. 最大化基础设施复用
- **数据加载**: 直接使用ProjectManager和Dataset_COMP体系
- **时域绘图**: 利用TimeSeries.plot()的成熟实现
- **项目管理**: 集成现有的项目路径和配置管理

### 2. 模块化设计
- **独立模块**: WaveformVisualizer可独立测试和维护
- **清晰接口**: 通过ProjectManager解耦数据加载逻辑
- **扩展性**: 易于添加新的可视化类型（频域、相位等）

### 3. CLI集成度高
- **一致体验**: 遵循现有CLI的参数和输出风格
- **批量处理**: 支持多项目并行处理
- **错误处理**: 集成现有的日志和异常处理机制

## 实施风险评估

### 技术风险
1. **数据集兼容性**: 不同类型数据集的形状可能不一致
   - **缓解**: 在WaveformVisualizer中添加数据验证
2. **内存占用**: 大数据集可能导致内存问题
   - **缓解**: 逐个处理频率/震级组合，及时释放内存
3. **图形质量**: 高分辨率输出可能影响性能
   - **缓解**: 可配置的DPI设置

### 兼容性风险
1. **matplotlib后端**: 服务器环境可能无GUI支持
   - **缓解**: 使用Agg后端，确保无GUI环境兼容
2. **文件权限**: 输出目录权限不足
   - **缓解**: 添加权限检查和友好错误提示

## 测试策略

### 单元测试
1. **WaveformVisualizer类测试**
   - 数据集加载测试
   - 单个波形绘制测试
   - 文件路径生成测试

### 集成测试
1. **端到端测试**
   - 不同类型项目的可视化测试
   - 批量项目处理测试
   - 强制覆盖模式测试

### 回归测试
1. **CLI兼容性测试**
   - 确保新任务不影响现有功能
   - 参数解析正确性验证

## 部署计划

### 阶段1: 核心模块开发（1天）
1. 实现WaveformVisualizer类
2. 基础的单波形绘制功能
3. 输出目录管理

### 阶段2: CLI集成（0.5天）
1. 扩展参数解析器
2. 添加任务分发逻辑
3. 实现任务处理函数

### 阶段3: 测试验证（0.5天）
1. 单元测试和集成测试
2. 在测试项目中验证功能
3. 性能和兼容性测试

### 阶段4: 文档完善（0.3天）
1. 更新CLI使用文档
2. 添加代码注释和示例
3. 更新项目README

## 验收标准
1. ✅ CLI能正确解析--vis参数
2. ✅ 能成功加载不同类型的数据集
3. ✅ 按频率×震级组合生成PNG文件
4. ✅ 图形包含Origin和Target两条波形曲线
5. ✅ 文件保存到正确的项目目录
6. ✅ 支持强制覆盖模式
7. ✅ 错误处理和日志输出正常
8. ✅ 不影响现有CLI功能

## 总结
这个实施计划通过最大化复用现有基础设施，在现有CLI框架中添加波形可视化功能。设计遵循模块化原则，确保代码质量和可维护性。预计2天内完成开发和测试，能够为所有支持的数据集类型生成高质量的Origin/Target波形对比图。
