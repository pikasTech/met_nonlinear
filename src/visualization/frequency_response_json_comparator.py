"""
基于JSON数据的频率响应对比可视化模块

此模块直接从 linear_response.json 文件读取数据进行对比，
无需加载模型或数据集，实现轻量级、高性能的频率响应对比可视化。
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Tuple, Optional, Union
import os
import json
import matplotlib.pyplot as plt
import numpy as np
import logging

# 配置日志
logger = logging.getLogger(__name__)

class DataState(Enum):
    """数据状态枚举"""
    ORIGIN = "origin"          # 补偿前数据
    COMPENSATION = "compensation"  # 补偿后数据

class LayoutMode(Enum):
    """布局模式枚举"""
    OVERLAY = "overlay"
    SIDE_BY_SIDE = "side_by_side"
    SEPARATE = "separate"

@dataclass
class DataSourceSpec:
    """数据源规范定义"""
    project_name: str
    state: DataState = DataState.ORIGIN
    
    @classmethod
    def parse(cls, source_str: str) -> 'DataSourceSpec':
        """解析 project@state 格式的字符串"""
        if '@' in source_str:
            project, state_str = source_str.split('@', 1)
            state = DataState.COMPENSATION if state_str == "compensation" else DataState.ORIGIN
            return cls(project, state)
        else:
            return cls(source_str, DataState.ORIGIN)
    
    def __str__(self) -> str:
        return f"{self.project_name}@{self.state.value}"

class LinearResponseDataLoader:
    """轻量级线性响应数据加载器"""
    
    def __init__(self, projects_root: str = "projects"):
        self.projects_root = projects_root
        self._cache = {}  # 缓存已加载的JSON数据
    
    def load_project_data(self, project_name: str) -> Dict[str, Any]:
        """加载项目的线性响应数据"""
        if project_name in self._cache:
            logger.debug(f"从缓存加载项目数据: {project_name}")
            return self._cache[project_name]
        
        json_path = os.path.join(self.projects_root, project_name, "data", "linear_response.json")
        
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Linear response data not found: {json_path}")
        
        logger.info(f"加载线性响应数据: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 验证数据完整性
        required_fields = ['gains_origin', 'gains_comped', 'magnitudes', 'frequencies']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields in {json_path}: {missing_fields}")
        
        logger.debug(f"数据验证通过，震级数: {len(data['magnitudes'])}, 频率数: {len(data['frequencies'])}")
        self._cache[project_name] = data
        return data
    
    def extract_data_source(self, spec: DataSourceSpec) -> Dict[str, Any]:
        """根据数据源规范提取对应的数据"""
        project_data = self.load_project_data(spec.project_name)
        
        # 选择对应状态的数据
        gains_key = "gains_comped" if spec.state == DataState.COMPENSATION else "gains_origin"
        
        safe_project_name = spec.project_name.replace('/', '_').replace('\\', '_')
        
        return {
            'gains': project_data[gains_key],
            'magnitudes': project_data['magnitudes'],
            'frequencies': project_data['frequencies'],
            'project_name': safe_project_name,
            'state': spec.state.value,
            'label': str(spec)
        }

class FrequencyResponseComparator:
    """基于JSON数据的频率响应对比可视化器"""
    
    def __init__(self, layout_mode: LayoutMode = LayoutMode.OVERLAY):
        self.layout_mode = layout_mode
    
    def compare_sources(self, source1_data: Dict[str, Any], source2_data: Dict[str, Any], 
                       output_folder: str = 'results', show_plot: bool = True,
                       freq_range: List[float] = None, gain_range: List[float] = None,
                       figsize: List[int] = None, dpi: int = 300, title: str = None,
                       source1_freq_range: List[float] = None,
                       source2_freq_range: List[float] = None,
                       source1_gain_range: List[float] = None,
                       source2_gain_range: List[float] = None,
                       source1_split_magnitudes: bool = False,
                       source2_split_magnitudes: bool = False
                       ) -> Tuple[Union[plt.Figure, List[plt.Figure]], Union[str, List[str]]]:
        """对比两个数据源并生成可视化"""
        
        # 创建输出目录
        os.makedirs(output_folder, exist_ok=True)
        
        logger.info(f"创建 {self.layout_mode.value} 布局的频率响应对比图")
        logger.info(f"数据源1: {source1_data['label']}")
        logger.info(f"数据源2: {source2_data['label']}")
        
        if self.layout_mode == LayoutMode.OVERLAY:
            return self._create_overlay_plot(source1_data, source2_data, output_folder, show_plot,
                                            freq_range, gain_range, figsize, dpi, title)
        elif self.layout_mode == LayoutMode.SIDE_BY_SIDE:
            return self._create_side_by_side_plot(source1_data, source2_data, output_folder, show_plot,
                                                freq_range, gain_range, figsize, dpi, title)
        elif self.layout_mode == LayoutMode.SEPARATE:
            return self._create_separate_plots(
                source1_data, source2_data, output_folder, show_plot,
                freq_range, gain_range, figsize, dpi, title,
                source1_freq_range, source2_freq_range,
                source1_gain_range, source2_gain_range,
                source1_split_magnitudes, source2_split_magnitudes
            )
    
    def _create_overlay_plot(self, source1_data: Dict, source2_data: Dict, 
                           output_folder: str, show_plot: bool,
                           freq_range: List[float] = None, gain_range: List[float] = None,
                           figsize: List[int] = None, dpi: int = 300, title: str = None) -> Tuple[plt.Figure, str]:
        """创建叠加布局的对比图"""
        # 设置图像尺寸
        if figsize is None:
            figsize = [12, 8]
        
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        
        # 绘制数据源1
        self._plot_data_on_axis(ax, source1_data, marker='o', linestyle='-', alpha=0.7, freq_range=freq_range)
        
        # 绘制数据源2  
        self._plot_data_on_axis(ax, source2_data, marker='^', linestyle='--', alpha=0.7, freq_range=freq_range)
        
        # 设置图例和标签
        ax.set_xlabel('Frequency (Hz)', fontsize=12)
        ax.set_ylabel('Amplitude', fontsize=12)
        
        # 设置标题
        if title is None:
            title = f'Frequency Response Comparison (Bode Plot)\n{source1_data["label"]} vs {source2_data["label"]}'
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        ax.grid(True, alpha=0.3, which="both", ls="--")
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 设置频率范围
        if freq_range is not None and len(freq_range) == 2:
            ax.set_xlim(freq_range[0], freq_range[1])
        
        # 设置增益范围
        if gain_range is not None and len(gain_range) == 2:
            ax.set_ylim(gain_range[0], gain_range[1])
        
        # 保存图像
        filename = 'bode_plot_overlay.png'
        output_path = os.path.join(output_folder, filename)
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        
        logger.info(f"叠加布局图像已保存: {output_path}")
        
        if show_plot:
            plt.show()
        
        return fig, output_path

    def _create_separate_plots(self, source1_data: Dict, source2_data: Dict,
                               output_folder: str, show_plot: bool,
                               freq_range: List[float] = None, gain_range: List[float] = None,
                               figsize: List[int] = None, dpi: int = 300, title: str = None,
                               source1_freq_range: List[float] = None,
                               source2_freq_range: List[float] = None,
                               source1_gain_range: List[float] = None,
                               source2_gain_range: List[float] = None,
                               source1_split_magnitudes: bool = False,
                               source2_split_magnitudes: bool = False
                               ) -> Tuple[List[plt.Figure], List[str]]:
        """为两个数据源分别创建独立坐标轴的幅频响应图。"""
        if figsize is None:
            figsize = [8, 6]

        figures = []
        output_paths = []
        sources = []
        sources.extend(
            self._build_separate_source_specs(
                source1_data,
                source1_freq_range or freq_range,
                source1_gain_range or gain_range,
                'o',
                source1_split_magnitudes
            )
        )
        sources.extend(
            self._build_separate_source_specs(
                source2_data,
                source2_freq_range or freq_range,
                source2_gain_range or gain_range,
                '^',
                source2_split_magnitudes
            )
        )

        for index, source_spec in enumerate(sources, start=1):
            source_data = source_spec['source_data']
            local_freq_range = source_spec['freq_range']
            local_gain_range = source_spec['gain_range']
            marker = source_spec['marker']
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111)
            self._plot_data_on_axis(
                ax,
                source_data,
                marker=marker,
                linestyle='-',
                alpha=0.85,
                freq_range=local_freq_range
            )
            ax.set_xlabel('Frequency (Hz)', fontsize=12)
            ax.set_ylabel('Amplitude', fontsize=12)
            ax.set_title(source_spec['title'], fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, which="both", ls="--")
            ax.legend(fontsize=10)

            if local_freq_range is not None and len(local_freq_range) == 2:
                ax.set_xlim(local_freq_range[0], local_freq_range[1])
            if local_gain_range is not None and len(local_gain_range) == 2:
                ax.set_ylim(local_gain_range[0], local_gain_range[1])

            fig.tight_layout()

            safe_name = self._safe_filename(
                f"bode_plot_separate_{index}_{source_data['project_name']}_{source_data['state']}{source_spec['filename_suffix']}.png"
            )
            output_path = os.path.join(output_folder, safe_name)
            fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
            logger.info(f"独立频率响应图像已保存: {output_path}")

            figures.append(fig)
            output_paths.append(output_path)

        if show_plot:
            plt.show()

        return figures, output_paths

    def _build_separate_source_specs(self, source_data: Dict[str, Any],
                                     freq_range: Optional[List[float]],
                                     gain_range: Optional[List[float]],
                                     marker: str,
                                     split_magnitudes: bool) -> List[Dict[str, Any]]:
        """将一个数据源展开成 separate 布局所需的一个或多个绘图规格。"""
        if not split_magnitudes:
            return [{
                'source_data': source_data,
                'freq_range': freq_range,
                'gain_range': gain_range,
                'marker': marker,
                'title': source_data['label'],
                'filename_suffix': ''
            }]

        specs = []
        for magnitude in source_data['magnitudes']:
            filtered_source = _filter_source_magnitudes(source_data, [float(magnitude)])
            mag_text = self._format_magnitude_for_filename(float(magnitude))
            specs.append({
                'source_data': filtered_source,
                'freq_range': freq_range,
                'gain_range': gain_range,
                'marker': marker,
                'title': f"{source_data['label']} @ {float(magnitude):.1f} m/s²",
                'filename_suffix': f"_mag_{mag_text}"
            })
        return specs
    
    def _create_side_by_side_plot(self, source1_data: Dict, source2_data: Dict,
                                output_folder: str, show_plot: bool,
                                freq_range: List[float] = None, gain_range: List[float] = None,
                                figsize: List[int] = None, dpi: int = 300, title: str = None) -> Tuple[plt.Figure, str]:
        """创建左右分布的对比图"""
        # 设置图像尺寸
        if figsize is None:
            figsize = [16, 8]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, sharey=True, sharex=True)
        
        # 绘制左图（数据源1）
        self._plot_data_on_axis(ax1, source1_data, marker='o', alpha=0.8, freq_range=freq_range)
        ax1.set_title(source1_data['label'], fontsize=14, fontweight='bold')
        ax1.set_xlabel('Frequency (Hz)', fontsize=12)
        ax1.set_ylabel('Amplitude', fontsize=12)
        ax1.grid(True, alpha=0.3, which="both", ls="--")
        ax1.legend(fontsize=10)
        
        # 绘制右图（数据源2）
        self._plot_data_on_axis(ax2, source2_data, marker='^', alpha=0.8, freq_range=freq_range)
        ax2.set_title(source2_data['label'], fontsize=14, fontweight='bold')
        ax2.set_xlabel('Frequency (Hz)', fontsize=12)
        ax2.grid(True, alpha=0.3, which="both", ls="--")
        ax2.legend(fontsize=10)
        
        # 设置频率范围
        if freq_range is not None and len(freq_range) == 2:
            ax1.set_xlim(freq_range[0], freq_range[1])
            ax2.set_xlim(freq_range[0], freq_range[1])
        
        # 设置增益范围
        if gain_range is not None and len(gain_range) == 2:
            ax1.set_ylim(gain_range[0], gain_range[1])
            ax2.set_ylim(gain_range[0], gain_range[1])
        
        # 同步坐标轴范围（如果没有手动设置增益范围）
        if gain_range is None:
            self._sync_axis_limits(ax1, ax2)
        
        plt.tight_layout()
        
        # 保存图像
        filename = 'bode_plot_sidebyside.png'
        output_path = os.path.join(output_folder, filename)
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        
        logger.info(f"左右布局图像已保存: {output_path}")
        
        if show_plot:
            plt.show()
        
        return fig, output_path
    
    def _plot_data_on_axis(self, ax, data: Dict, marker: str = 'o', 
                          linestyle: str = '-', alpha: float = 0.7, 
                          freq_range: List[float] = None) -> None:
        """在指定的轴上绘制真正的幅频特性曲线 (Bode Plot)"""
        gains = data['gains']
        magnitudes = data['magnitudes']
        frequencies = data['frequencies']
        
        # 为每个震级绘制一条幅频特性曲线
        color_map = plt.cm.get_cmap("viridis", len(magnitudes))
        
        for mag_idx, magnitude in enumerate(magnitudes):
            color = color_map(mag_idx)
            
            # 提取该震级下所有频率的幅度响应
            amplitudes = gains[mag_idx]  # gains[mag_idx] 包含该震级的所有频率响应
            
            # 过滤掉无效值 (零值或负值会导致 loglog 绘制错误)
            valid_indices = [i for i in range(len(amplitudes)) 
                           if amplitudes[i] > 0 and frequencies[i] > 0]
            
            # 如果设置了频率范围，进一步过滤
            if freq_range is not None and len(freq_range) == 2:
                min_freq, max_freq = freq_range
                valid_indices = [i for i in valid_indices 
                               if min_freq <= frequencies[i] <= max_freq]
            
            if valid_indices:
                valid_freqs = [frequencies[i] for i in valid_indices]
                valid_amps = [amplitudes[i] for i in valid_indices]
                
                # 绘制幅频特性曲线 (Bode Plot)
                # X轴: 频率 (Hz), Y轴: 幅度响应 (线性值) - 双对数刻度
                ax.loglog(valid_freqs, valid_amps,
                         label=f'{data["label"]} @ {magnitude:.1f} m/s²', 
                         linestyle=linestyle, marker=marker,
                         markersize=3, color=color, alpha=alpha, linewidth=1.5)

    @staticmethod
    def _safe_filename(filename: str) -> str:
        """将项目名中的路径分隔符替换为适合文件名的字符。"""
        return filename.replace('/', '_').replace('\\', '_').replace(':', '_')

    @staticmethod
    def _format_magnitude_for_filename(magnitude: float) -> str:
        """将震级数值转换为稳定文件名片段。"""
        mag_text = f"{magnitude:.3f}".rstrip('0').rstrip('.')
        return mag_text.replace('.', 'p')
    
    def _sync_axis_limits(self, ax1, ax2) -> None:
        """同步两个subplot的坐标轴范围"""
        xlim1, ylim1 = ax1.get_xlim(), ax1.get_ylim()
        xlim2, ylim2 = ax2.get_xlim(), ax2.get_ylim()
        
        unified_xlim = (min(xlim1[0], xlim2[0]), max(xlim1[1], xlim2[1]))
        unified_ylim = (min(ylim1[0], ylim2[0]), max(ylim1[1], ylim2[1]))
        
        ax1.set_xlim(unified_xlim)
        ax1.set_ylim(unified_ylim)
        ax2.set_xlim(unified_xlim)
        ax2.set_ylim(unified_ylim)

# 便利函数：快速对比
def quick_compare(project1: str, project2: str = None, 
                 state1: str = "origin", state2: str = "compensation",
                 layout: str = "overlay", output_dir: str = "results",
                 projects_root: str = "projects", freq_range: List[float] = None,
                 gain_range: List[float] = None, figsize: List[int] = None, 
                 dpi: int = 300, title: str = None,
                 label1: str = None, label2: str = None,
                 magnitudes1: List[float] = None, magnitudes2: List[float] = None,
                 source1_freq_range: List[float] = None,
                 source2_freq_range: List[float] = None,
                 source1_gain_range: List[float] = None,
                 source2_gain_range: List[float] = None,
                 split_magnitudes1: bool = False,
                 split_magnitudes2: bool = False) -> Union[str, List[str]]:
    """
    便利函数：快速进行频率响应对比
    
    Args:
        project1: 第一个项目名称
        project2: 第二个项目名称（如果为None，则与project1相同）
        state1: 第一个数据状态 ("origin" | "compensation")
        state2: 第二个数据状态 ("origin" | "compensation")
        layout: 布局模式 ("overlay" | "side_by_side")
        output_dir: 输出目录
        projects_root: 项目根目录
        freq_range: 频率范围限制 [min_freq, max_freq]
        gain_range: 增益范围限制 [min_gain, max_gain]
        figsize: 图像尺寸 [width, height]
        dpi: 图像分辨率
        title: 图像标题
        label1: 第一个数据源的显示标签
        label2: 第二个数据源的显示标签
        magnitudes1: 第一个数据源要绘制的震级列表；None 表示全部
        magnitudes2: 第二个数据源要绘制的震级列表；None 表示全部
        source1_freq_range: 第一个数据源的独立频率范围，仅 separate 布局使用
        source2_freq_range: 第二个数据源的独立频率范围，仅 separate 布局使用
        source1_gain_range: 第一个数据源的独立增益范围，仅 separate 布局使用
        source2_gain_range: 第二个数据源的独立增益范围，仅 separate 布局使用
        split_magnitudes1: 是否将第一个数据源按震级拆分成多张图
        split_magnitudes2: 是否将第二个数据源按震级拆分成多张图
    
    Returns:
        生成的图像文件路径
    """
    
    # 设置默认值
    if project2 is None:
        project2 = project1
    
    # 创建数据源规范
    source1_spec = DataSourceSpec(project1, DataState(state1))
    source2_spec = DataSourceSpec(project2, DataState(state2))
    
    # 加载数据
    data_loader = LinearResponseDataLoader(projects_root)
    source1_data = data_loader.extract_data_source(source1_spec)
    source2_data = data_loader.extract_data_source(source2_spec)
    if label1:
        source1_data['label'] = label1
    if label2:
        source2_data['label'] = label2
    source1_data = _filter_source_magnitudes(source1_data, magnitudes1)
    source2_data = _filter_source_magnitudes(source2_data, magnitudes2)
    
    # 创建对比图
    layout_aliases = {
        "overlaid": "overlay",
    }
    normalized_layout = layout_aliases.get(layout, layout)
    comparator = FrequencyResponseComparator(LayoutMode(normalized_layout))
    fig_or_figs, output_path = comparator.compare_sources(
        source1_data, source2_data, output_dir, show_plot=False,
        freq_range=freq_range, gain_range=gain_range, figsize=figsize, 
        dpi=dpi, title=title,
        source1_freq_range=source1_freq_range,
        source2_freq_range=source2_freq_range,
        source1_gain_range=source1_gain_range,
        source2_gain_range=source2_gain_range,
        source1_split_magnitudes=split_magnitudes1,
        source2_split_magnitudes=split_magnitudes2
    )
    
    if isinstance(fig_or_figs, list):
        for fig in fig_or_figs:
            plt.close(fig)
    else:
        plt.close(fig_or_figs)  # 释放内存
    return output_path


def _filter_source_magnitudes(source_data: Dict[str, Any],
                              requested_magnitudes: Optional[List[float]] = None) -> Dict[str, Any]:
    """按震级筛选数据源曲线，保持原有数据结构。"""
    if not requested_magnitudes:
        return source_data

    magnitudes = np.asarray(source_data['magnitudes'], dtype=float)
    gains = np.asarray(source_data['gains'], dtype=float)
    if gains.ndim == 1:
        gains = gains.reshape(1, -1)
    if gains.shape[0] != magnitudes.shape[0]:
        raise ValueError(
            f"Magnitude count mismatch for {source_data['label']}: "
            f"{magnitudes.shape[0]} magnitudes vs {gains.shape[0]} gain rows"
        )

    selected_indices = []
    for requested in requested_magnitudes:
        matches = np.where(np.isclose(magnitudes, float(requested), rtol=1e-7, atol=1e-9))[0]
        if len(matches) == 0:
            raise ValueError(
                f"Magnitude {requested} not found in {source_data['label']}; "
                f"available magnitudes: {magnitudes.tolist()}"
            )
        match_index = int(matches[0])
        if match_index not in selected_indices:
            selected_indices.append(match_index)

    filtered = dict(source_data)
    filtered['magnitudes'] = magnitudes[selected_indices].tolist()
    filtered['gains'] = gains[selected_indices, :].tolist()
    return filtered

if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 测试内部对比
    print("测试内部对比...")
    output1 = quick_compare(
        "LSTMu32al_rs300_PS-5_160-200Hz_inverse_ex2",
        layout="side_by_side"
    )
    print(f"内部对比完成: {output1}")
    
    # 测试跨项目对比
    print("测试跨项目对比...")
    output2 = quick_compare(
        "LSTMu32al_rs300", "LSTMu32al_rs300_PS-5",
        state1="origin", state2="origin",
        layout="overlay"
    )
    print(f"跨项目对比完成: {output2}")
