#!/usr/bin/env python3
"""
权重E96量化对比可视化工具

生成权重E96量化前后的对比图表，包括：
1. 原始权重矩阵热力图
2. 电阻（浮点数）热力图
3. 电阻（E96量化）热力图
4. E96量化相对误差热力图
5. 统计表格
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

# 直接导入绘图辅助函数（避免导入整个inference包导致的tensorflow依赖问题）
sys.path.insert(0, str(Path(__file__).parent / 'utils'))
from plot_helpers import setup_academic_style, save_plot_data

# 定义最大电阻值（开路电阻）
MAX_RESISTANCE = 1e9


class WeightE96QuantizationPlotter:
    """
    权重E96量化对比可视化器
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化可视化器

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.output_dir = self.config.get('output_dir', 'inference/results/e96_quantization_analysis')

    def _ensure_native_types(self, obj):
        """
        递归将numpy类型转换为Python原生类型

        修复 'can only convert an array of size 1 to a Python scalar' 错误
        """
        if isinstance(obj, np.ndarray):
            return [self._ensure_native_types(item) for item in obj.tolist()]
        elif isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, dict):
            return {key: self._ensure_native_types(val) for key, val in obj.items()}
        elif isinstance(obj, list):
            return [self._ensure_native_types(item) for item in obj]
        else:
            return obj

    def plot_quantization_comparison(self,
                                     comparison_data: Dict[str, Any],
                                     output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        生成完整的E96量化对比可视化图表

        Args:
            comparison_data: 量化对比数据（来自DenseCircuit.generate_quantization_comparison_data）
            output_dir: 输出目录

        Returns:
            Dict: 生成的文件路径
        """
        if output_dir:
            self.output_dir = output_dir

        # 创建输出目录
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 转换所有numpy类型为Python原生类型（修复序列化错误）
        comparison_data = self._ensure_native_types(comparison_data)

        setup_academic_style(self.config)

        generated_files = {}

        # 1. 绘制权重矩阵热力图对比
        try:
            files = self._plot_weight_matrices(comparison_data, output_path)
            generated_files.update(files)
            print("DEBUG: _plot_weight_matrices succeeded")
        except Exception as e:
            print(f"DEBUG: _plot_weight_matrices FAILED: {e}")
            import traceback
            traceback.print_exc()

        # 2. 绘制电阻值热力图对比
        try:
            files = self._plot_resistor_values(comparison_data, output_path)
            generated_files.update(files)
            print("DEBUG: _plot_resistor_values succeeded")
        except Exception as e:
            print(f"DEBUG: _plot_resistor_values FAILED: {e}")
            import traceback
            traceback.print_exc()

        # 3. 绘制5子图综合表格热力图（表格+热力图形式）
        try:
            files = self._plot_five_panel_heatmap(comparison_data, output_path)
            generated_files.update(files)
            print("DEBUG: _plot_five_panel_heatmap succeeded")
        except Exception as e:
            print(f"DEBUG: _plot_five_panel_heatmap FAILED: {e}")
            import traceback
            traceback.print_exc()

        # 4. 绘制量化误差热力图（原始版本，保留兼容性）
        try:
            files = self._plot_quantization_error_heatmap(comparison_data, output_path)
            generated_files.update(files)
            print("DEBUG: _plot_quantization_error_heatmap succeeded")
        except Exception as e:
            print(f"DEBUG: _plot_quantization_error_heatmap FAILED: {e}")
            import traceback
            traceback.print_exc()

        # 5. 绘制误差分布直方图
        try:
            files = self._plot_error_distribution(comparison_data, output_path)
            generated_files.update(files)
            print("DEBUG: _plot_error_distribution succeeded")
        except Exception as e:
            print(f"DEBUG: _plot_error_distribution FAILED: {e}")
            import traceback
            traceback.print_exc()

        # 6. 生成统计表格
        try:
            files = self._generate_statistics_table(comparison_data, output_path)
            generated_files.update(files)
            print("DEBUG: _generate_statistics_table succeeded")
        except Exception as e:
            print(f"DEBUG: _generate_statistics_table FAILED: {e}")
            import traceback
            traceback.print_exc()

        # 7. 生成综合对比大图
        try:
            files = self._plot_comprehensive_comparison(comparison_data, output_path)
            generated_files.update(files)
            print("DEBUG: _plot_comprehensive_comparison succeeded")
        except Exception as e:
            print(f"DEBUG: _plot_comprehensive_comparison FAILED: {e}")
            import traceback
            traceback.print_exc()

        return generated_files

    def _plot_weight_matrices(self,
                              comparison_data: Dict[str, Any],
                              output_path: Path) -> Dict[str, str]:
        """绘制权重矩阵热力图对比"""
        try:
            # 确保 weight_matrix 是纯 Python 类型
            weight_matrix_data = comparison_data['weight_matrix']
            weight_matrix = np.array(weight_matrix_data, dtype=np.float64)

            fig, axes = plt.subplots(1, 2, figsize=(14, 6))

            # 原始权重
            im1 = axes[0].imshow(weight_matrix, cmap='viridis', aspect='auto')
            axes[0].set_title('Original Weight Matrix', fontsize=14, fontweight='bold')
            axes[0].set_xlabel('Input Channels')
            axes[0].set_ylabel('Output Channels')

            # 添加数值标注
            weight_mean = float(np.mean(weight_matrix))
            for i in range(weight_matrix.shape[0]):
                for j in range(weight_matrix.shape[1]):
                    val = float(weight_matrix[i, j])
                    text_color = 'white' if abs(val) > weight_mean else 'black'
                    axes[0].text(j, i, f'{val:.2f}', ha='center', va='center',
                               color=text_color, fontsize=8)

            # 量化后的等效权重（从E96电阻反推）
            weight_error = comparison_data.get('weight_error', {})
            weight_e96_matrix = np.zeros_like(weight_matrix, dtype=np.float64)
            for key, error_data in weight_error.items():
                # 解析key格式: "layer_X_channel_Y_type_Z"
                parts = key.split('_')
                if len(parts) >= 6:
                    ch = int(parts[3]) if parts[3].isdigit() else 0
                    output_idx = int(parts[1]) if parts[1].isdigit() else 0
                    if 0 <= output_idx < weight_matrix.shape[0] and 0 <= ch < weight_matrix.shape[1]:
                        w_e96 = error_data.get('weight_e96', 0)
                        # 确保是 Python 原生类型
                        if hasattr(w_e96, 'item'):
                            w_e96 = w_e96.item()
                        weight_e96_matrix[output_idx, ch] = float(w_e96)

            im2 = axes[1].imshow(weight_e96_matrix, cmap='viridis', aspect='auto')
            axes[1].set_title('E96 Quantized Weight Matrix', fontsize=14, fontweight='bold')
            axes[1].set_xlabel('Input Channels')
            axes[1].set_ylabel('Output Channels')

            # 添加数值标注
            e96_mean = float(np.mean(weight_e96_matrix))
            for i in range(weight_e96_matrix.shape[0]):
                for j in range(weight_e96_matrix.shape[1]):
                    val = float(weight_e96_matrix[i, j])
                    if val > 0:
                        text_color = 'white' if abs(val) > e96_mean else 'black'
                        axes[1].text(j, i, f'{val:.2f}', ha='center', va='center',
                                   color=text_color, fontsize=8)

            # 共享颜色条
            fig.colorbar(im1, ax=axes, shrink=0.6, label='Weight Value')

            plt.tight_layout()

            plot_name = 'weight_matrices_comparison'
            fig_path = output_path / f'{plot_name}.png'
            plt.savefig(fig_path, dpi=300, bbox_inches='tight')
            plt.close()

            # 保存原始数据
            save_plot_data({
                'plot_type': 'weight_matrices_comparison',
                'data': {
                    'weight_matrix': comparison_data['weight_matrix'],
                    'weight_e96_matrix': weight_e96_matrix.tolist()
                }
            }, str(output_path), plot_name)

            return {plot_name: str(fig_path)}
        except Exception as e:
            import traceback
            print(f"Error in _plot_weight_matrices: {e}")
            traceback.print_exc()
            return {}

    def _plot_resistor_values(self,
                              comparison_data: Dict[str, Any],
                              output_path: Path) -> Dict[str, str]:
        """绘制电阻值热力图对比"""
        resistor_raw = comparison_data.get('resistor_raw', {})
        resistor_e96 = comparison_data.get('resistor_e96', {})

        # 构建电阻矩阵（简化展示，选取代表性通道）
        channels = ['input_pos_0', 'input_pos_1', 'input_pos_2',
                   'input_neg_0', 'input_neg_1', 'input_neg_2']

        raw_values = []
        e96_values = []
        labels = []

        for ch in channels:
            if ch in resistor_raw:
                raw_values.append(resistor_raw[ch])
                e96_values.append(resistor_e96.get(ch, resistor_raw[ch]))
                labels.append(ch)

        fig, axes = plt.subplots(2, 1, figsize=(12, 8))

        # 原始电阻值
        if raw_values:
            y_pos = np.arange(len(labels))
            bars1 = axes[0].barh(y_pos, raw_values, color='#3498DB', alpha=0.8, label='Raw Resistor')
            axes[0].set_yticks(y_pos)
            axes[0].set_yticklabels(labels)
            axes[0].set_xlabel('Resistance (Ohm)')
            axes[0].set_title('Raw Float-point Resistance', fontsize=14, fontweight='bold')
            axes[0].xaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: f'{x/1e3:.1f}k' if x >= 1000 else f'{x:.0f}'))

            # 添加数值标注
            for bar, val in zip(bars1, raw_values):
                axes[0].text(val + max(raw_values)*0.01, bar.get_y() + bar.get_height()/2,
                           f'{val:.2f}Ohm', va='center', fontsize=9)

        # E96量化电阻值
        if e96_values:
            y_pos = np.arange(len(labels))
            bars2 = axes[1].barh(y_pos, e96_values, color='#E74C3C', alpha=0.8, label='E96 Quantized Resistor')
            axes[1].set_yticks(y_pos)
            axes[1].set_yticklabels(labels)
            axes[1].set_xlabel('Resistance (Ohm)')
            axes[1].set_title('E96 Quantized Resistance', fontsize=14, fontweight='bold')
            axes[1].xaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: f'{x/1e3:.1f}k' if x >= 1000 else f'{x:.0f}'))

            # 添加数值标注
            for bar, val in zip(bars2, e96_values):
                axes[1].text(val + max(e96_values)*0.01, bar.get_y() + bar.get_height()/2,
                           f'{val:.2f}Ohm', va='center', fontsize=9)

        plt.tight_layout()

        plot_name = 'resistor_values_comparison'
        fig_path = output_path / f'{plot_name}.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()

        # 保存原始数据
        save_plot_data({
            'plot_type': 'resistor_values_comparison',
            'data': {
                'channels': labels,
                'resistor_raw': raw_values,
                'resistor_e96': e96_values
            }
        }, str(output_path), plot_name)

        return {plot_name: str(fig_path)}

    def _plot_table_heatmap(self, matrix, title, ax, cmap='viridis', fmt='.2f', text_color_threshold=None):
        """
        绘制带数值的表格热力图

        Args:
            matrix: 2D numpy array
            title: 子图标题
            ax: matplotlib axes
            cmap: 颜色映射
            fmt: 数值格式
            text_color_threshold: 文字颜色阈值（基于数据均值）
        """
        im = ax.imshow(matrix, cmap=cmap, aspect='auto')

        # 计算阈值用于文字颜色
        if text_color_threshold is None:
            text_color_threshold = np.mean(matrix)

        # 添加数值标注
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                val = float(matrix[i, j])
                # 跳过零值和无效值
                if val == 0 or val >= 1e8:
                    ax.text(j, i, '-', ha='center', va='center',
                           color='gray', fontsize=7)
                else:
                    # 根据数值大小选择文字颜色
                    text_color = 'white' if abs(val) > text_color_threshold * 0.5 else 'black'
                    ax.text(j, i, f'{val:{fmt}}', ha='center', va='center',
                           color=text_color, fontsize=7, fontweight='bold')

        ax.set_title(title, fontsize=11, fontweight='bold', pad=8)
        ax.set_xlabel('Input Channel' if matrix.shape[1] > 1 else 'Channel Type')
        ax.set_ylabel('Output Channel' if matrix.shape[0] > 1 else 'Layer')

        return im

    def _build_resistor_matrix(self, resistor_dict, layer_idx, resistor_type):
        """
        构建指定层和类型的电阻矩阵

        Args:
            resistor_dict: 电阻字典 {key: value}
            layer_idx: 层索引
            resistor_type: 电阻类型 (pos, neg, R1, R2, bias_pos, bias_neg)

        Returns:
            2D numpy array (outputs x inputs)
        """
        n_outputs = 6  # WNET5 layer1 有6个输出
        n_inputs = 6   # 有6个输入

        matrix = np.zeros((n_outputs, n_inputs))

        for key, value in resistor_dict.items():
            if value >= 1e8:  # 开路电阻，跳过
                continue

            parts = key.split('_')
            if len(parts) < 6:
                continue

            try:
                key_layer = int(parts[1])
                key_channel = int(parts[3])
                key_type = parts[5]

                if key_layer != layer_idx:
                    continue

                # 映射类型到矩阵位置
                if resistor_type == 'input':
                    # 输入电阻 (pos/neg) - 每个channel都有
                    if key_type == 'pos' or key_type == 'neg':
                        output_idx = 0  # 所有输入电阻归类到第一行（为了简化）
                        input_idx = key_channel
                        matrix[output_idx, input_idx] = value
                elif resistor_type == key_type:
                    # 特定类型
                    output_idx = 0
                    input_idx = key_channel
                    matrix[output_idx, input_idx] = value
            except (ValueError, IndexError):
                continue

        return matrix

    def _plot_five_panel_heatmap(self,
                                  comparison_data: Dict[str, Any],
                                  output_path: Path) -> Dict[str, str]:
        """
        绘制5子图综合热力图（表格热力图）

        子图内容：
        1. 原始权重矩阵热力图
        2. 电阻（浮点数）热力图
        3. 电阻（E96量化）热力图
        4. 计算带E96量化误差的权重热力图
        5. 量化前后的E96引入的相对误差热力图

        每个子图都是带数值的热力图（表格热力图）
        """
        import matplotlib.colors as mcolors

        weight_matrix = np.array(comparison_data['weight_matrix'])
        resistor_raw = comparison_data.get('resistor_raw', {})
        resistor_e96 = comparison_data.get('resistor_e96', {})
        weight_error = comparison_data.get('weight_error', {})
        relative_error = comparison_data.get('relative_error_percent', {})

        # 构建权重误差矩阵（从weight_error字典构建）
        weight_e96_matrix = np.zeros_like(weight_matrix, dtype=np.float64)
        error_matrix = np.zeros_like(weight_matrix, dtype=np.float64)

        R_base = 1000  # 基准电阻

        for key, error_data in weight_error.items():
            try:
                parts = key.split('_')
                if len(parts) >= 6:
                    layer = int(parts[1])
                    channel = int(parts[3])
                    r_type = parts[5]

                    # 只处理 pos 和 neg 类型（与电阻矩阵保持一致）
                    if r_type not in ['pos', 'neg']:
                        continue

                    if layer < weight_matrix.shape[0] and channel < weight_matrix.shape[1]:
                        # weight_e96 直接使用 weight_original + (weight_e96 - weight_original)
                        # 即从电阻反推的权重应该接近原始权重（考虑量化误差）
                        weight_original = float(weight_matrix[layer, channel])
                        w_e96 = error_data.get('weight_e96', weight_original)

                        # 只更新有效数据点（非零权重）
                        if abs(weight_original) > 1e-6:
                            weight_e96_matrix[layer, channel] = w_e96

                            # 使用电阻的相对误差，而不是权重的相对误差
                            # E96量化的误差应该在1-2%左右，这才是用户关心的
                            r_raw_val = resistor_raw.get(key, 0)
                            r_e96_val = resistor_e96.get(key, r_raw_val)

                            if r_raw_val > 0 and r_raw_val < MAX_RESISTANCE:
                                # 电阻相对误差（这是 E96 量化的真实误差）
                                r_rel_error = abs(r_e96_val - r_raw_val) / r_raw_val * 100
                                error_matrix[layer, channel] = r_rel_error
                            else:
                                error_matrix[layer, channel] = 0.0
            except (ValueError, IndexError):
                continue

        # 创建5子图
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))

        # 子图1: 原始权重矩阵
        ax1 = axes[0, 0]
        # 计算统一的颜色范围（用于子图1和子图4的可比性）
        all_weights = np.concatenate([weight_matrix.flatten(), weight_e96_matrix.flatten()])
        valid_weights = all_weights[(all_weights > 0) & (all_weights < 1e8)]
        if len(valid_weights) > 0:
            vmin = float(np.min(valid_weights))
            vmax = float(np.max(valid_weights))
        else:
            vmin = float(np.min(weight_matrix))
            vmax = float(np.max(weight_matrix))
        # 使用相同的colormap和刻度范围，使子图1和子图4可比
        im1 = ax1.imshow(weight_matrix, cmap='RdBu_r', aspect='auto', vmin=vmin, vmax=vmax)
        weight_mean = float(np.mean(np.abs(weight_matrix)))
        for i in range(weight_matrix.shape[0]):
            for j in range(weight_matrix.shape[1]):
                val = float(weight_matrix[i, j])
                text_color = 'white' if abs(val) > weight_mean else 'black'
                ax1.text(j, i, f'{val:.2f}', ha='center', va='center',
                        color=text_color, fontsize=8, fontweight='bold')
        ax1.set_title('1. Original Weight Matrix', fontsize=12, fontweight='bold', pad=10)
        ax1.set_xlabel('Input Channel')
        ax1.set_ylabel('Output Channel')
        plt.colorbar(im1, ax=ax1, shrink=0.8)

        # 子图2: 电阻（浮点数）- 6x6矩阵
        ax2 = axes[0, 1]
        # 构建6x6电阻矩阵
        resistor_raw_matrix = np.zeros((6, 6))
        resistor_e96_matrix = np.zeros((6, 6))

        for key, r_raw in resistor_raw.items():
            if r_raw >= 1e8:  # 跳过开路
                continue
            parts = key.split('_')
            if len(parts) >= 6:
                try:
                    layer = int(parts[1])
                    channel = int(parts[3])
                    key_type = parts[5]
                    if key_type in ['pos', 'neg']:
                        if layer < 6 and channel < 6:
                            resistor_raw_matrix[layer, channel] = r_raw
                            resistor_e96_matrix[layer, channel] = resistor_e96.get(key, r_raw)
                except (ValueError, IndexError):
                    continue

        # 如果没有有效数据，填入NaN用于显示
        if np.all(resistor_raw_matrix == 0):
            resistor_raw_matrix = np.full((6, 6), np.nan)

        # 使用masked array处理NaN值
        resistor_raw_masked = np.ma.masked_invalid(resistor_raw_matrix)

        im2 = ax2.imshow(resistor_raw_masked, cmap='YlOrRd', aspect='auto')
        resistor_mean = float(np.nanmean(resistor_raw_matrix))

        for i in range(6):
            for j in range(6):
                val = float(resistor_raw_matrix[i, j])
                if not np.isnan(val) and val > 0:
                    text_color = 'white' if val > resistor_mean else 'black'
                    ax2.text(j, i, f'{val:.0f}', ha='center', va='center',
                            color=text_color, fontsize=8, fontweight='bold')
                elif not np.isnan(val):
                    ax2.text(j, i, '-', ha='center', va='center',
                            color='gray', fontsize=8)

        ax2.set_title('2. Resistor Values (Float)', fontsize=12, fontweight='bold', pad=10)
        ax2.set_xlabel('Input Channel')
        ax2.set_ylabel('Output Channel')
        plt.colorbar(im2, ax=ax2, shrink=0.8, label='Resistance (Ω)')

        # 子图3: 电阻（E96量化）- 6x6矩阵
        ax3 = axes[0, 2]
        # 使用之前构建的resistor_e96_matrix（6x6）
        resistor_e96_masked = np.ma.masked_invalid(resistor_e96_matrix)

        im3 = ax3.imshow(resistor_e96_masked, cmap='YlGnBu', aspect='auto')
        e96_mean = float(np.nanmean(resistor_e96_matrix))

        for i in range(6):
            for j in range(6):
                val = float(resistor_e96_matrix[i, j])
                if not np.isnan(val) and val > 0:
                    text_color = 'white' if val > e96_mean else 'black'
                    ax3.text(j, i, f'{val:.0f}', ha='center', va='center',
                            color=text_color, fontsize=8, fontweight='bold')
                elif not np.isnan(val):
                    ax3.text(j, i, '-', ha='center', va='center',
                            color='gray', fontsize=8)

        ax3.set_title('3. Resistor Values (E96)', fontsize=12, fontweight='bold', pad=10)
        ax3.set_xlabel('Input Channel')
        ax3.set_ylabel('Output Channel')
        plt.colorbar(im3, ax=ax3, shrink=0.8, label='Resistance (Ω)')

        # 子图4: 计算带E96量化误差的权重热力图
        ax4 = axes[1, 0]
        # 使用与子图1相同的colormap和刻度范围，确保视觉可比性
        im4 = ax4.imshow(weight_e96_matrix, cmap='RdBu_r', aspect='auto', vmin=vmin, vmax=vmax)
        w_e96_mean = float(np.mean(weight_e96_matrix[weight_e96_matrix > 0])) if np.any(weight_e96_matrix > 0) else 0

        for i in range(weight_e96_matrix.shape[0]):
            for j in range(weight_e96_matrix.shape[1]):
                val = float(weight_e96_matrix[i, j])
                if val > 0:
                    ax4.text(j, i, f'{val:.3f}', ha='center', va='center',
                            color='white' if val > w_e96_mean else 'black',
                            fontsize=8, fontweight='bold')

        ax4.set_title('4. Weight with E96 Quantization Error', fontsize=12, fontweight='bold', pad=10)
        ax4.set_xlabel('Input Channel')
        ax4.set_ylabel('Output Channel')
        plt.colorbar(im4, ax=ax4, shrink=0.8)

        # 子图5: 量化前后的E96引入的相对误差热力图
        ax5 = axes[1, 1]
        im5 = ax5.imshow(error_matrix, cmap='RdYlGn_r', aspect='auto',
                        vmin=0, vmax=max(2.0, float(np.max(error_matrix))))
        err_mean = float(np.mean(error_matrix[error_matrix > 0])) if np.any(error_matrix > 0) else 0

        for i in range(error_matrix.shape[0]):
            for j in range(error_matrix.shape[1]):
                val = float(error_matrix[i, j])
                if val > 0:
                    ax5.text(j, i, f'{val:.2f}%', ha='center', va='center',
                            color='white' if val > err_mean * 0.7 else 'black',
                            fontsize=8, fontweight='bold')

        ax5.set_title('5. E96 Relative Error (%)', fontsize=12, fontweight='bold', pad=10)
        ax5.set_xlabel('Input Channel')
        ax5.set_ylabel('Output Channel')
        plt.colorbar(im5, ax=ax5, shrink=0.8, label='Error (%)')

        # 子图6: 统计信息表格
        ax6 = axes[1, 2]
        ax6.axis('off')

        stats = comparison_data.get('statistics', {})

        # 表格数据
        table_data = [
            ['Statistic', 'Value'],
            ['Total Resistors', str(stats.get('total_count', 0))],
            ['Mean Error', f"{stats.get('mean_relative_error', 0):.3f}%"],
            ['Max Error', f"{stats.get('max_relative_error', 0):.3f}%"],
            ['Min Error', f"{stats.get('min_relative_error', 0):.3f}%"],
            ['Within 1%', f"{stats.get('within_1pct', 0):.1f}%"],
            ['Within 5%', f"{stats.get('within_5pct', 0):.1f}%"],
        ]

        table = ax6.table(cellText=table_data[1:], colLabels=table_data[0],
                         cellLoc='center', loc='center',
                         colColours=['#4A90D9', '#4A90D9'])
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 2)

        for i in range(2):
            table[(0, i)].set_text_props(color='white', weight='bold')

        for i in range(1, len(table_data)):
            for j in range(2):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#E8F4FC')
                else:
                    table[(i, j)].set_facecolor('#FFFFFF')

        ax6.set_title('6. Statistics Summary', fontsize=12, fontweight='bold', pad=10)

        # 总标题
        fig.suptitle('E96 Quantization Error Analysis - 5-Panel Table Heatmap',
                    fontsize=16, fontweight='bold', y=0.98)

        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # 保存图片
        plot_name = 'e96_table_heatmap'
        fig_path = output_path / f'{plot_name}.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        # 保存JSON数据
        save_data = {
            'plot_type': 'e96_table_heatmap',
            'data': {
                'weight_matrix': comparison_data['weight_matrix'],
                'weight_e96_matrix': weight_e96_matrix.tolist(),
                'error_matrix': error_matrix.tolist(),
                'resistor_raw_matrix': resistor_raw_matrix.tolist(),
                'resistor_e96_matrix': resistor_e96_matrix.tolist(),
                'statistics': stats
            }
        }
        save_plot_data(save_data, str(output_path), plot_name)

        return {plot_name: str(fig_path)}

    def _plot_quantization_error_heatmap(self,
                                         comparison_data: Dict[str, Any],
                                         output_path: Path) -> Dict[str, str]:
        """绘制量化误差热力图"""
        relative_errors = comparison_data.get('relative_error_percent', {})

        # 构建误差矩阵
        error_matrix = []
        error_labels = []

        for key, error in relative_errors.items():
            if error > 0:  # 排除零误差（开路等）
                parts = key.split('_')
                label = f"Ch{parts[3]}_{parts[5]}" if len(parts) >= 6 else key
                error_labels.append(label)
                error_matrix.append(error)

        if not error_matrix:
            return {}

        error_array = np.array(error_matrix).reshape(1, -1)
        # 确保 max 返回 Python 原生类型
        max_error = float(np.max(error_array))

        fig, ax = plt.subplots(figsize=(14, 4))

        # 使用热力图展示误差分布
        im = ax.imshow(error_array, cmap='RdYlGn_r', aspect='auto',
                      vmin=0, vmax=max_error * 1.2)

        # 添加数值标注
        half_max = max_error * 0.5
        for i in range(error_array.shape[1]):
            val = float(error_array[0, i])
            text_color = 'white' if val > half_max else 'black'
            ax.text(i, 0, f'{val:.2f}%', ha='center', va='center',
                   color=text_color, fontsize=9, fontweight='bold')

        ax.set_yticks([0])
        ax.set_yticklabels(['E96 Quantization Error'])
        ax.set_xlabel('Resistor Channel')
        ax.set_xticks(range(len(error_labels)))
        ax.set_xticklabels(error_labels, rotation=45, ha='right')

        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Relative Error (%)', fontsize=12)

        ax.set_title('E96 Quantization Relative Error Distribution', fontsize=14, fontweight='bold')

        plt.tight_layout()

        plot_name = 'e96_quantization_error_heatmap'
        fig_path = output_path / f'{plot_name}.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()

        # 保存原始数据
        save_plot_data({
            'plot_type': 'e96_quantization_error_heatmap',
            'data': {
                'channels': error_labels,
                'relative_errors': error_matrix
            }
        }, str(output_path), plot_name)

        return {plot_name: str(fig_path)}

    def _plot_error_distribution(self,
                                 comparison_data: Dict[str, Any],
                                 output_path: Path) -> Dict[str, str]:
        """绘制误差分布直方图"""
        relative_errors = comparison_data.get('relative_error_percent', {})
        errors = [e for e in relative_errors.values() if e > 0]

        if not errors:
            return {}

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # 直方图
        axes[0].hist(errors, bins=20, color='#3498DB', alpha=0.7, edgecolor='black')
        axes[0].set_xlabel('Relative Error (%)')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title('E96 Quantization Error Histogram', fontsize=14, fontweight='bold')

        # 添加统计线
        mean_error = np.mean(errors)
        max_error = np.max(errors)
        axes[0].axvline(mean_error, color='red', linestyle='--', linewidth=2,
                       label=f'Mean: {mean_error:.2f}%')
        axes[0].legend()

        # 箱线图
        bp = axes[1].boxplot(errors, vert=True, patch_artist=True)
        bp['boxes'][0].set_facecolor('#3498DB')
        bp['boxes'][0].set_alpha(0.7)
        axes[1].set_ylabel('Relative Error (%)')
        axes[1].set_title('E96 Quantization Error Boxplot', fontsize=14, fontweight='bold')
        axes[1].set_xticklabels(['E96 Quantization Error'])

        # 添加统计标注
        stats_text = f'Mean: {mean_error:.2f}%\nMax: {max_error:.2f}%\nMedian: {np.median(errors):.2f}%'
        axes[1].text(1.2, mean_error, stats_text, fontsize=10, verticalalignment='center')

        plt.tight_layout()

        plot_name = 'e96_error_distribution'
        fig_path = output_path / f'{plot_name}.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()

        # 保存原始数据
        save_plot_data({
            'plot_type': 'e96_error_distribution',
            'data': {
                'relative_errors': errors,
                'mean': mean_error,
                'max': max_error,
                'median': float(np.median(errors))
            }
        }, str(output_path), plot_name)

        return {plot_name: str(fig_path)}

    def _generate_statistics_table(self,
                                   comparison_data: Dict[str, Any],
                                   output_path: Path) -> Dict[str, str]:
        """生成统计表格"""
        stats = comparison_data.get('statistics', {})

        setup_academic_style(self.config)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('off')

        # 创建表格数据
        table_data = [
            ['Statistic', 'Value'],
            ['Total Resistors', str(stats.get('total_count', 0))],
            ['Mean Relative Error', f"{stats.get('mean_relative_error', 0):.4f}%"],
            ['Max Relative Error', f"{stats.get('max_relative_error', 0):.4f}%"],
            ['Min Relative Error', f"{stats.get('min_relative_error', 0):.4f}%"],
            ['Error < 1% Ratio', f"{stats.get('within_1pct', 0):.1f}%"],
            ['Error < 5% Ratio', f"{stats.get('within_5pct', 0):.1f}%"]
        ]

        # 创建表格
        table = ax.table(cellText=table_data[1:], colLabels=table_data[0],
                        cellLoc='center', loc='center',
                        colColours=['#E0E0E0', '#E0E0E0'])

        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.5, 2)

        # 设置表头样式
        for i in range(2):
            table[(0, i)].set_text_props(weight='bold')

        # 交替行颜色
        for i in range(1, len(table_data)):
            for j in range(2):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#F5F5F5')

        ax.set_title('E96 Quantization Error Statistics Summary', fontsize=16, fontweight='bold', pad=20)

        plot_name = 'e96_quantization_statistics'
        fig_path = output_path / f'{plot_name}.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()

        # 保存JSON数据
        stats_path = output_path / f'{plot_name}.json'
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        return {plot_name: str(fig_path)}

    def _plot_comprehensive_comparison(self,
                                       comparison_data: Dict[str, Any],
                                       output_path: Path) -> Dict[str, str]:
        """生成综合对比大图（包含所有可视化元素）"""
        weight_matrix = np.array(comparison_data['weight_matrix'])
        relative_errors = comparison_data.get('relative_error_percent', {})
        errors = [e for e in relative_errors.values() if e > 0]

        fig = plt.figure(figsize=(18, 12))

        # 创建子图布局
        gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)

        # 1. 权重矩阵热力图
        ax1 = fig.add_subplot(gs[0, 0])
        im1 = ax1.imshow(weight_matrix, cmap='viridis', aspect='auto')
        ax1.set_title('Original Weight Matrix', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Input')
        ax1.set_ylabel('Output')
        plt.colorbar(im1, ax=ax1, shrink=0.8)

        # 2. 误差直方图
        ax2 = fig.add_subplot(gs[0, 1])
        if errors:
            ax2.hist(errors, bins=15, color='#3498DB', alpha=0.7, edgecolor='black')
            ax2.axvline(np.mean(errors), color='red', linestyle='--', linewidth=2,
                       label=f'Mean: {np.mean(errors):.2f}%')
            ax2.legend()
        ax2.set_title('Error Distribution', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Relative Error (%)')
        ax2.set_ylabel('Frequency')

        # 3. 统计表格
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.axis('off')
        stats = comparison_data.get('statistics', {})
        table_data = [
            ['Mean Error', f"{stats.get('mean_relative_error', 0):.3f}%"],
            ['Max Error', f"{stats.get('max_relative_error', 0):.3f}%"],
            ['<1% Ratio', f"{stats.get('within_1pct', 0):.1f}%"],
            ['<5% Ratio', f"{stats.get('within_5pct', 0):.1f}%"],
            ['Total', str(stats.get('total_count', 0))]
        ]
        table = ax3.table(cellText=table_data, loc='center', cellLoc='center',
                         colColours=['#E0E0E0', '#E0E0E0'])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        ax3.set_title('Statistics Summary', fontsize=12, fontweight='bold')

        # 4. 误差热力图
        ax4 = fig.add_subplot(gs[1, :2])
        if errors:
            error_array = np.array(errors).reshape(1, -1)
            im4 = ax4.imshow(error_array, cmap='RdYlGn_r', aspect='auto',
                           vmin=0, vmax=max(errors) * 1.2)
            for i, e in enumerate(errors):
                text_color = 'white' if e > max(errors) * 0.5 else 'black'
                ax4.text(i, 0, f'{e:.2f}%', ha='center', va='center',
                        color=text_color, fontsize=8)
            plt.colorbar(im4, ax=ax4, shrink=0.8, label='Error (%)')
        ax4.set_title('E96 Quantization Relative Error', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Resistor Index')
        ax4.set_yticks([])

        # 5. 箱线图
        ax5 = fig.add_subplot(gs[1, 2])
        if errors:
            bp = ax5.boxplot(errors, vert=True, patch_artist=True)
            bp['boxes'][0].set_facecolor('#3498DB')
            bp['boxes'][0].set_alpha(0.7)
        ax5.set_title('Error Boxplot', fontsize=12, fontweight='bold')
        ax5.set_ylabel('Relative Error (%)')

        # 6. 权重误差vs电阻误差散点图
        ax6 = fig.add_subplot(gs[2, :])
        weight_errors = comparison_data.get('weight_error', {})
        weight_err_list = []
        resistor_err_list = []
        for key, w_err in weight_errors.items():
            if 'relative_error_percent' in w_err:
                weight_err_list.append(w_err['relative_error_percent'])
                resistor_err_list.append(relative_errors.get(key, 0))

        if weight_err_list:
            ax6.scatter(weight_err_list, resistor_err_list, alpha=0.6, c='#3498DB')
            ax6.plot([0, max(weight_err_list)], [0, max(weight_err_list)],
                    'r--', label='y=x (Ideal)')
            ax6.set_xlabel('Weight Relative Error (%)')
            ax6.set_ylabel('Resistor Relative Error (%)')
            ax6.set_title('Weight Error vs Resistor Error', fontsize=12, fontweight='bold')
            ax6.legend()
            ax6.grid(True, alpha=0.3)

        # 总标题
        fig.suptitle('E96 Quantization Error Comprehensive Analysis', fontsize=16, fontweight='bold', y=0.98)

        plt.tight_layout(rect=[0, 0, 1, 0.96])

        plot_name = 'e96_comprehensive_analysis'
        fig_path = output_path / f'{plot_name}.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()

        return {plot_name: str(fig_path)}


def main():
    """主函数 - 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Weight E96 Quantization Comparison Visualization Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--input', required=True,
                        help='Quantization comparison data JSON file path')
    parser.add_argument('--output', default='inference/results/e96_quantization_analysis',
                        help='Output directory (default: inference/results/e96_quantization_analysis)')
    parser.add_argument('--config', default=None,
                        help='Config file path')

    args = parser.parse_args()

    # 加载数据
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 如果数据嵌套在 quantization_comparison 中，提取出来
    if 'quantization_comparison' in data:
        comparison_data = data['quantization_comparison']
        print(f"INFO: Extracted quantization_comparison from results.json")
    elif 'weight_matrix' in data:
        comparison_data = data
        print(f"INFO: Using top-level data as comparison data")
    else:
        print(f"ERROR: No 'quantization_comparison' or 'weight_matrix' key found in input file")
        print(f"Available keys: {list(data.keys())[:20]}")
        return

    # 创建可视化器并生成图表
    plotter = WeightE96QuantizationPlotter({'output_dir': args.output})
    files = plotter.plot_quantization_comparison(comparison_data, args.output)

    print(f"\nGenerated files:")
    for name, path in files.items():
        print(f"  - {name}: {path}")

    print(f"\nDone! Results saved to: {args.output}")


if __name__ == '__main__':
    main()
