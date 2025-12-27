# R14: 权重E96量化对比可视化修改计划

## 任务概述

在 R13 基础上继续调查，要求能够生成量化前后的权重对比图，用表格+热力图的形式展示：
1. 原始权重矩阵
2. 电阻（浮点数）
3. 电阻（E96量化）
4. 计算带E96量化误差的权重
5. 量化前后的E96引入的相对误差

## 实现方案

### 新建可视化模块

**新建文件**: `inference/tools/visualization/weight_e96_quantization_plotter.py`

此模块专门用于生成权重E96量化对比可视化图表。

### 修改现有文件

#### 1. 修改 `spice_simulator/circuit_dense.py`

**位置**: `spice_simulator/circuit_dense.py`

**修改内容**: 在 `calculate_resistors()` 方法中添加可选的量化对比数据输出

```python
# 在 calculate_resistors() 方法末尾（约第520行附近）添加新参数和返回值扩展

def calculate_resistors(self,
                        include_quantization_comparison: bool = False) -> Dict[str, Any]:
    """
    计算电阻值

    Args:
        include_quantization_comparison: 是否包含E96量化对比数据

    Returns:
        Dict: 包含电阻配置，如果启用量化对比则包含完整对比数据
    """
    # ... 现有代码 ...

    # 如果启用量化对比，添加对比数据
    if include_quantization_comparison:
        result['quantization_comparison'] = self._generate_quantization_comparison_data(
            weight_matrix, r_raw_dict, r_e96_dict
        )

    return result
```

**新增方法** (约第600行附近):

```python
def _generate_quantization_comparison_data(self,
                                           weight_matrix: np.ndarray,
                                           r_raw_dict: Dict[str, float],
                                           r_e96_dict: Dict[str, float]) -> Dict[str, Any]:
    """
    生成E96量化对比数据

    Args:
        weight_matrix: 权重矩阵
        r_raw_dict: 原始电阻值字典
        r_e96_dict: E96量化后电阻值字典

    Returns:
        Dict: 量化对比数据
    """
    comparison_data = {
        'weight_matrix': weight_matrix.tolist(),
        'resistor_raw': {},
        'resistor_e96': {},
        'weight_error': {},
        'relative_error_percent': {}
    }

    # 计算每个电阻的量化误差
    for key, r_raw in r_raw_dict.items():
        r_e96 = r_e96_dict.get(key, r_raw)

        comparison_data['resistor_raw'][key] = r_raw
        comparison_data['resistor_e96'][key] = r_e96

        # 计算相对误差
        if r_raw > 0 and r_raw < MAX_RESISTANCE:
            rel_error = abs(r_e96 - r_raw) / r_raw * 100
        else:
            rel_error = 0.0

        comparison_data['relative_error_percent'][key] = rel_error

    # 计算等效权重误差（电阻误差转化为权重误差）
    R_base = 1000  # 基准电阻
    for key, r_raw in r_raw_dict.items():
        if r_raw > 0 and r_raw < MAX_RESISTANCE:
            w_raw = R_base / r_raw  # 原始权重
            w_e96 = R_base / r_e96_dict.get(key, r_raw)  # E96量化后权重
            w_error = abs(w_e96 - w_raw)
            comparison_data['weight_error'][key] = {
                'weight_raw': w_raw,
                'weight_e96': w_e96,
                'absolute_error': w_error,
                'relative_error_percent': abs(w_e96 - w_raw) / w_raw * 100 if w_raw != 0 else 0
            }

    # 统计汇总
    errors = [e for e in comparison_data['relative_error_percent'].values() if e > 0]
    comparison_data['statistics'] = {
        'mean_relative_error': float(np.mean(errors)) if errors else 0,
        'max_relative_error': float(np.max(errors)) if errors else 0,
        'min_relative_error': float(np.min(errors)) if errors else 0,
        'within_1pct': float(sum(1 for e in errors if e < 1) / len(errors) * 100) if errors else 100,
        'within_5pct': float(sum(1 for e in errors if e < 5) / len(errors) * 100) if errors else 100,
        'total_count': len(errors)
    }

    return comparison_data
```

#### 2. 修改 `spice_simulator/unified_resistance_calculator.py`

**位置**: `spice_simulator/unified_resistance_calculator.py:115-125`

**修改内容**: 传递 `include_quantization_comparison` 参数给 DenseCircuit

```python
# 约第115行，修改 DenseCircuitFactory.create() 调用
circuit = DenseCircuitFactory.create(
    gains=weight_matrix,
    biases=processed_bias,
    opamp_config=self.opamp_config,
    use_e96=self.use_e96,  # 来自配置
    use_relu=self._determine_relu_usage(layer),
    high_pass_config=self.high_pass_config,
    bias_compensation=self.bias_compensation,
    vcc=self.power_supply_config['vcc'] if self.power_supply_config else 15.0,
    vee=self.power_supply_config['vee'] if self.power_supply_config else -15.0,
    # 新增参数
    include_quantization_comparison=self.inference_config.get('include_quantization_comparison', False)
)
```

#### 3. 修改配置文件结构

**位置**: `ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1\config.json`

**新增配置项**:

```json
{
  "task_info": {
    "task_type": "wnet5-circuit-validation",
    "description": "WNET5电路频率响应理论验证 - Dense层1"
  },
  "model_project_name": "WNET5q1h2u6l3",
  "analysis_layer": 1,
  "frequency_range": {
    "start_freq": 2,
    "stop_freq": 500
  },
  "inference_config": {
    "use_e96": true,
    "include_quantization_comparison": true,
    "opamp_config": {
      "model": "ideal"
    }
  }
}
```

#### 4. 新建可视化模块

**新建文件**: `inference/tools/visualization/weight_e96_quantization_plotter.py`

```python
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
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

# 导入现有绘图辅助函数
from .utils.plot_helpers import setup_academic_style, save_plot_data


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

    def plot_quantization_comparison(self,
                                     comparison_data: Dict[str, Any],
                                     output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        生成完整的E96量化对比可视化图表

        Args:
            comparison_data: 量化对比数据（来自DenseCircuit._generate_quantization_comparison_data）
            output_dir: 输出目录

        Returns:
            Dict: 生成的文件路径
        """
        if output_dir:
            self.output_dir = output_dir

        # 创建输出目录
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        setup_academic_style(self.config)

        generated_files = {}

        # 1. 绘制权重矩阵热力图对比
        files = self._plot_weight_matrices(comparison_data, output_path)
        generated_files.update(files)

        # 2. 绘制电阻值热力图对比
        files = self._plot_resistor_values(comparison_data, output_path)
        generated_files.update(files)

        # 3. 绘制量化误差热力图
        files = self._plot_quantization_error_heatmap(comparison_data, output_path)
        generated_files.update(files)

        # 4. 绘制误差分布直方图
        files = self._plot_error_distribution(comparison_data, output_path)
        generated_files.update(files)

        # 5. 生成统计表格
        files = self._generate_statistics_table(comparison_data, output_path)
        generated_files.update(files)

        # 6. 生成综合对比大图
        files = self._plot_comprehensive_comparison(comparison_data, output_path)
        generated_files.update(files)

        return generated_files

    def _plot_weight_matrices(self,
                              comparison_data: Dict[str, Any],
                              output_path: Path) -> Dict[str, str]:
        """绘制权重矩阵热力图对比"""
        weight_matrix = np.array(comparison_data['weight_matrix'])

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # 原始权重
        im1 = axes[0].imshow(weight_matrix, cmap='viridis', aspect='auto')
        axes[0].set_title('原始权重矩阵', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('输入通道')
        axes[0].set_ylabel('输出通道')

        # 添加数值标注
        for i in range(weight_matrix.shape[0]):
            for j in range(weight_matrix.shape[1]):
                val = weight_matrix[i, j]
                text_color = 'white' if abs(val) > weight_matrix.mean() else 'black'
                axes[0].text(j, i, f'{val:.2f}', ha='center', va='center',
                           color=text_color, fontsize=8)

        # 量化后的等效权重（从E96电阻反推）
        weight_error = comparison_data.get('weight_error', {})
        weight_e96_matrix = np.zeros_like(weight_matrix)
        for key, error_data in weight_error.items():
            # 解析key格式: "layer_X_channel_Y_type_Z"
            parts = key.split('_')
            if len(parts) >= 4:
                ch = int(parts[3]) if parts[3].isdigit() else 0
                output_idx = int(parts[1]) if parts[1].isdigit() else 0
                if 0 <= output_idx < weight_matrix.shape[0] and 0 <= ch < weight_matrix.shape[1]:
                    weight_e96_matrix[output_idx, ch] = error_data.get('weight_e96', 0)

        im2 = axes[1].imshow(weight_e96_matrix, cmap='viridis', aspect='auto')
        axes[1].set_title('E96量化后等效权重矩阵', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('输入通道')
        axes[1].set_ylabel('输出通道')

        # 添加数值标注
        for i in range(weight_e96_matrix.shape[0]):
            for j in range(weight_e96_matrix.shape[1]):
                val = weight_e96_matrix[i, j]
                if val > 0:
                    text_color = 'white' if abs(val) > weight_e96_matrix.mean() else 'black'
                    axes[1].text(j, i, f'{val:.2f}', ha='center', va='center',
                               color=text_color, fontsize=8)

        # 共享颜色条
        fig.colorbar(im1, ax=axes, shrink=0.6, label='权重值')

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
            bars1 = axes[0].barh(y_pos, raw_values, color='#3498DB', alpha=0.8, label='原始电阻')
            axes[0].set_yticks(y_pos)
            axes[0].set_yticklabels(labels)
            axes[0].set_xlabel('电阻值 (Ω)')
            axes[0].set_title('原始浮点电阻值', fontsize=14, fontweight='bold')
            axes[0].xaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: f'{x/1e3:.1f}k' if x >= 1000 else f'{x:.0f}'))

            # 添加数值标注
            for bar, val in zip(bars1, raw_values):
                axes[0].text(val + max(raw_values)*0.01, bar.get_y() + bar.get_height()/2,
                           f'{val:.2f}Ω', va='center', fontsize=9)

        # E96量化电阻值
        if e96_values:
            y_pos = np.arange(len(labels))
            bars2 = axes[1].barh(y_pos, e96_values, color='#E74C3C', alpha=0.8, label='E96量化电阻')
            axes[1].set_yticks(y_pos)
            axes[1].set_yticklabels(labels)
            axes[1].set_xlabel('电阻值 (Ω)')
            axes[1].set_title('E96量化电阻值', fontsize=14, fontweight='bold')
            axes[1].xaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: f'{x/1e3:.1f}k' if x >= 1000 else f'{x:.0f}'))

            # 添加数值标注
            for bar, val in zip(bars2, e96_values):
                axes[1].text(val + max(e96_values)*0.01, bar.get_y() + bar.get_height()/2,
                           f'{val:.2f}Ω', va='center', fontsize=9)

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

    def _plot_quantization_error_heatmap(self,
                                         comparison_data: Dict[str, Any],
                                         output_path: Path) -> Dict[str, str]:
        """绘制量化误差热力图"""
        relative_errors = comparison_data.get('relative_error_percent', {})
        weight_errors = comparison_data.get('weight_error', {})

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

        fig, ax = plt.subplots(figsize=(14, 4))

        # 使用热力图展示误差分布
        im = ax.imshow(error_array, cmap='RdYlGn_r', aspect='auto',
                      vmin=0, vmax=max(error_array) * 1.2)

        # 添加数值标注
        for i in range(error_array.shape[1]):
            val = error_array[0, i]
            text_color = 'white' if val > error_array.max() * 0.5 else 'black'
            ax.text(i, 0, f'{val:.2f}%', ha='center', va='center',
                   color=text_color, fontsize=9, fontweight='bold')

        ax.set_yticks([0])
        ax.set_yticklabels(['E96量化误差'])
        ax.set_xlabel('电阻通道')
        ax.set_xticks(range(len(error_labels)))
        ax.set_xticklabels(error_labels, rotation=45, ha='right')

        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('相对误差 (%)', fontsize=12)

        ax.set_title('E96量化相对误差分布', fontsize=14, fontweight='bold')

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
        axes[0].set_xlabel('相对误差 (%)')
        axes[0].set_ylabel('频数')
        axes[0].set_title('E96量化误差分布直方图', fontsize=14, fontweight='bold')

        # 添加统计线
        mean_error = np.mean(errors)
        max_error = np.max(errors)
        axes[0].axvline(mean_error, color='red', linestyle='--', linewidth=2,
                       label=f'均值: {mean_error:.2f}%')
        axes[0].legend()

        # 箱线图
        bp = axes[1].boxplot(errors, vert=True, patch_artist=True)
        bp['boxes'][0].set_facecolor('#3498DB')
        bp['boxes'][0].set_alpha(0.7)
        axes[1].set_ylabel('相对误差 (%)')
        axes[1].set_title('E96量化误差箱线图', fontsize=14, fontweight='bold')
        axes[1].set_xticklabels(['E96量化误差'])

        # 添加统计标注
        stats_text = f'均值: {mean_error:.2f}%\n最大: {max_error:.2f}%\n中位数: {np.median(errors):.2f}%'
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
            ['统计指标', '数值'],
            ['电阻总数', str(stats.get('total_count', 0))],
            ['平均相对误差', f"{stats.get('mean_relative_error', 0):.4f}%"],
            ['最大相对误差', f"{stats.get('max_relative_error', 0):.4f}%"],
            ['最小相对误差', f"{stats.get('min_relative_error', 0):.4f}%"],
            ['误差 < 1% 比例', f"{stats.get('within_1pct', 0):.1f}%"],
            ['误差 < 5% 比例', f"{stats.get('within_5pct', 0):.1f}%"]
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

        ax.set_title('E96量化误差统计汇总', fontsize=16, fontweight='bold', pad=20)

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
        ax1.set_title('原始权重矩阵', fontsize=12, fontweight='bold')
        ax1.set_xlabel('输入')
        ax1.set_ylabel('输出')
        plt.colorbar(im1, ax=ax1, shrink=0.8)

        # 2. 误差直方图
        ax2 = fig.add_subplot(gs[0, 1])
        if errors:
            ax2.hist(errors, bins=15, color='#3498DB', alpha=0.7, edgecolor='black')
            ax2.axvline(np.mean(errors), color='red', linestyle='--', linewidth=2,
                       label=f'Mean: {np.mean(errors):.2f}%')
            ax2.legend()
        ax2.set_title('误差分布', fontsize=12, fontweight='bold')
        ax2.set_xlabel('相对误差 (%)')
        ax2.set_ylabel('频数')

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
        ax3.set_title('统计汇总', fontsize=12, fontweight='bold')

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
        ax4.set_title('E96量化相对误差', fontsize=12, fontweight='bold')
        ax4.set_xlabel('电阻索引')
        ax4.set_yticks([])

        # 5. 箱线图
        ax5 = fig.add_subplot(gs[1, 2])
        if errors:
            bp = ax5.boxplot(errors, vert=True, patch_artist=True)
            bp['boxes'][0].set_facecolor('#3498DB')
            bp['boxes'][0].set_alpha(0.7)
        ax5.set_title('误差箱线图', fontsize=12, fontweight='bold')
        ax5.set_ylabel('相对误差 (%)')

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
                    'r--', label='y=x (理想)')
            ax6.set_xlabel('权重相对误差 (%)')
            ax6.set_ylabel('电阻相对误差 (%)')
            ax6.set_title('权重误差 vs 电阻误差', fontsize=12, fontweight='bold')
            ax6.legend()
            ax6.grid(True, alpha=0.3)

        # 总标题
        fig.suptitle('E96量化误差综合分析', fontsize=16, fontweight='bold', y=0.98)

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
        description='权重E96量化对比可视化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--input', required=True,
                        help='量化对比数据JSON文件路径')
    parser.add_argument('--output', default='inference/results/e96_quantization_analysis',
                        help='输出目录 (默认: inference/results/e96_quantization_analysis)')
    parser.add_argument('--config', default=None,
                        help='配置文件路径')

    args = parser.parse_args()

    # 加载数据
    with open(args.input, 'r', encoding='utf-8') as f:
        comparison_data = json.load(f)

    # 创建可视化器并生成图表
    plotter = WeightE96QuantizationPlotter({'output_dir': args.output})
    files = plotter.plot_quantization_comparison(comparison_data, args.output)

    print(f"\n生成的文件:")
    for name, path in files.items():
        print(f"  - {name}: {path}")

    print(f"\n完成! 结果保存在: {args.output}")


if __name__ == '__main__':
    main()
```

## 修改汇总表

| 文件 | 修改类型 | 修改内容 | 行号 |
|------|---------|---------|------|
| `spice_simulator/circuit_dense.py` | 修改 | `calculate_resistors()` 添加 `include_quantization_comparison` 参数 | 约450行 |
| `spice_simulator/circuit_dense.py` | 新增 | `_generate_quantization_comparison_data()` 方法 | 约600行 |
| `spice_simulator/unified_resistance_calculator.py` | 修改 | `DenseCircuitFactory.create()` 调用传递新参数 | 约115行 |
| `ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1\config.json` | 修改 | 添加 `inference_config.use_e96` 和 `include_quantization_comparison` | 新增配置项 |
| `inference/tools/visualization/weight_e96_quantization_plotter.py` | **新建** | 完整的E96量化对比可视化模块 | - |

## 使用方法

### 1. 配置config.json

```json
{
  "inference_config": {
    "use_e96": true,
    "include_quantization_comparison": true,
    "opamp_config": {
      "model": "ideal"
    }
  }
}
```

### 2. 运行推理

```bash
python cli.py ep ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1
```

### 3. 生成可视化报告

```bash
python -m inference.tools.visualization.weight_e96_quantization_plotter \
    --input inference/results/e96_quantization_analysis/quantization_comparison.json \
    --output inference/results/e96_quantization_analysis
```

## 输出文件说明

| 文件名 | 说明 |
|--------|------|
| `weight_matrices_comparison.png` | 原始权重 vs E96量化权重矩阵热力图 |
| `resistor_values_comparison.png` | 浮点电阻 vs E96量化电阻对比条形图 |
| `e96_quantization_error_heatmap.png` | E96量化误差分布热力图 |
| `e96_error_distribution.png` | 误差直方图和箱线图 |
| `e96_quantization_statistics.png` | 统计汇总表格 |
| `e96_comprehensive_analysis.png` | 综合分析大图 |

## 注意事项

1. **R_base固定值**: 当前代码中R_base=1000Ω硬编码在计算逻辑中，如需修改需同时调整可视化代码
2. **MAX_RESISTANCE**: 开路电阻（>=1e8Ω）不参与误差统计
3. **配置优先级**: `config.json` 中的配置会覆盖默认值
4. **依赖库**: 新模块依赖 `seaborn` 用于高级热力图绘制
