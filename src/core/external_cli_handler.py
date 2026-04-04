"""
外部项目CLI处理器

处理ep子命令的所有操作，实现智能执行逻辑：
- 配置文件不存在时报错退出（不自动创建模板）
- 配置文件存在时直接执行任务
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

from .external_path_parser import ExternalPathParser, ExternalPath
from .cli_parser import CLIArgs

logger = logging.getLogger(__name__)


def handle_ep_command(args: CLIArgs) -> None:
    """
    处理ep子命令（简化版本）

    智能执行逻辑：
    1. 解析外部项目路径
    2. 检查配置文件是否存在
    3. 如果不存在，报错退出
    4. 如果存在，直接执行外部项目任务

    Args:
        args: CLI参数对象
    """
    try:
        logger.info(f"[EP] 开始处理外部项目: {args.ep_project_path}")
        # 解析路径
        parser = ExternalPathParser()
        ep_project_path = args.ep_project_path or ""
        ep_path = parser.parse(ep_project_path)

        logger.info(f"[INFO] 项目信息:")
        logger.info(f"   项目名称: {ep_path.project_name}")
        logger.info(f"   任务类型: {ep_path.task_type}")
        logger.info(f"   任务名称: {ep_path.task_name}")
        logger.info(f"   配置文件: {ep_path.config_path}")
        logger.info(f"   输出目录: {ep_path.output_path}")

        # 智能执行：检查配置文件，不存在则创建，然后执行任务
        execute_external_task_auto(ep_path)
    except Exception as e:
        logger.error(f"[ERROR] ep命令执行失败: {e}")
        _show_ep_help()
        sys.exit(1)


def execute_external_task_auto(ep_path: ExternalPath) -> None:
    """
    智能执行外部项目任务

    根据配置文件存在性自动选择行为：
    - 配置不存在：报错退出
    - 配置存在：直接执行任务

    Args:
        ep_path: 外部项目路径对象
    """
    logger.info(f"[TASK] 开始处理外部项目任务: {ep_path.task_name}")
    
    # 检查配置文件是否存在
    if not ep_path.config_path.exists():
        logger.error(f"[ERROR] 配置文件不存在: {ep_path.config_path}")
        logger.error("[HINT] 请确认项目路径是否正确，或手动创建配置文件")
        sys.exit(1)
    
    # 执行任务
    logger.info(f"[RUN] 执行外部项目任务...")
    result = _execute_task(ep_path)
    
    if result:
        logger.info(f"[OK] 任务执行完成")
        logger.info(f"   输出目录: {ep_path.output_path}")
    else:
        logger.error(f"[ERROR] 任务执行失败")
        sys.exit(1)


def create_external_template(ep_path: ExternalPath) -> None:
    """
    创建外部项目配置模板
    
    根据任务类型创建相应的配置模板文件
    
    Args:
        ep_path: 外部项目路径对象
    """
    # 确保目录存在
    ep_path.config_path.parent.mkdir(parents=True, exist_ok=True)
    ep_path.output_path.mkdir(parents=True, exist_ok=True)
    
    # 根据任务类型创建模板
    if ep_path.task_type == 'freq-response-compare':
        template = _create_freq_response_template(ep_path)
    elif ep_path.task_type == 'freq-response-compensator':
        template = _create_freq_response_compensator_template(ep_path)
    elif ep_path.task_type == 'bias-visualization':
        template = _create_bias_visualization_template(ep_path)
    elif ep_path.task_type == 'waveform-analysis':
        template = _create_waveform_analysis_template(ep_path)
    elif ep_path.task_type == 'wnet5-circuit-validation':
        template = _create_wnet5_circuit_validation_template(ep_path)
    elif ep_path.task_type == 'qemu-c-inference':
        template = _create_qemu_c_inference_template(ep_path)
    elif ep_path.task_type == 'ablation-study':
        template = _create_ablation_study_template(ep_path)
    else:
        template = _create_generic_template(ep_path)
    
    # 写入配置文件
    import json
    with open(ep_path.config_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    logger.debug(f"配置模板已写入: {ep_path.config_path}")


def _create_freq_response_template(ep_path: ExternalPath) -> dict:
    """创建频率响应对比配置模板"""
    return {
        "task_info": {
            "task_type": "freq-response-compare"
        },
        "visualization_config": {
            "layout": "side_by_side",
            "freq_range": [10, 200],
            "output_format": "png",
            "dpi": 300,
            "figsize": [12, 8],
            "title": f"{ep_path.project_name} 频率响应对比"
        },
        "data_sources": [
            {
                "project": ep_path.project_name,
                "state": "origin",
                "label": "补偿前"
            },
            {
                "project": ep_path.project_name,
                "state": "compensation",
                "label": "补偿后"
            }
        ]
    }


def _create_wnet5_circuit_validation_template(ep_path: ExternalPath) -> dict:
    """创建WNET5电路验证配置模板"""
    return {
        "task_info": {
            "task_type": "wnet5-circuit-validation",
            "description": "WNET5电路频率响应理论验证"
        },
        "model_project_name": ep_path.project_name,
        "frequency_range": {
            "start_freq": 0.1,
            "stop_freq": 1000
        }
    }


def _create_qemu_c_inference_template(ep_path: ExternalPath) -> dict:
    """创建 QEMU C 推理模板。"""
    return {
        "task_info": {
            "task_type": "qemu-c-inference",
            "description": "自动识别模型类型并执行 C/TF26 波形一致性验证"
        },
        "model_project_name": "00_MAE_VS_AFMAE/LSTMu16_base",
        "weights_file": "best_val.weights.json",
        "generation_config": {
            "project_dir": "qemu_project",
            "overwrite": True,
            "lut_points": 513,
            "lut_interpolation": False
        },
        "benchmark_config": {
            "iterations": 10,
            "reset_state_each_run": True,
            "repeat_runs": 1
        },
        "validation_config": {
            "dataset": {
                "source_project_config": "projects/LSTMu16/config.json",
                "dataset_type": "MET",
                "data_path": "data/M50",
                "sample_rate": 2000,
                "time_clipped_s": 4.0,
                "target_sweep": 2,
                "feature_range": [-1, 1],
                "use_scale": True,
                "use_cache_features": True
            },
            "selection": {
                "magnitudes": [0.24],
                "frequencies": [10.0],
                "start_time_s": 0.0,
                "end_time_s": 0.2
            },
            "wave_output": {
                "compress": True
            }
        },
        "qemu_config": {
            "action": "build-run",
            "machine": "olimex-stm32-h405",
            "timeout": 5
        }
    }


def _create_ablation_study_template(ep_path: ExternalPath) -> dict:
    """创建消融实验对比配置模板"""
    return {
        "task_info": {
            "task_type": "ablation-study",
            "description": "MAE vs AFMAE 消融实验对比"
        },
        "projects": [
            {
                "name": "LSTMu16_base",
                "label": "Base (MAE)",
                "path": "00_MAE_VS_AFMAE/LSTMu16_base"
            },
            {
                "name": "FRIKANh8u6l6_pureafmae",
                "label": "AFMAE",
                "path": "00_MAE_VS_AFMAE/FRIKANh8u6l6_pureafmae"
            }
        ],
        "metrics": {
            "natural_frequency_drift": {
                "enabled": True,
                "reference": "LSTMu16_base"
            },
            "sensitivity_drift": {
                "enabled": True,
                "reference": "LSTMu16_base",
                "frequency_hz": 100
            },
            "linearity": {
                "enabled": True
            }
        },
        "output": {
            "format": ["json", "markdown"],
            "output_dir": "ex_projects/compare/mae_vs_afmae/results"
        }
    }


def _create_bias_visualization_template(ep_path: ExternalPath) -> dict:
    """创建偏置可视化配置模板"""
    return {
        "task_info": {
            "task_type": "bias-visualization"
        },
        "visualization_config": {
            "output_format": "png",
            "dpi": 300,
            "figsize": [10, 6],
            "title": f"{ep_path.project_name} 偏置分析"
        },
        "data_sources": [
            {
                "project": ep_path.project_name,
                "state": "origin",
                "label": "原始数据"
            }
        ]
    }


def _create_waveform_analysis_template(ep_path: ExternalPath) -> dict:
    """创建波形分析配置模板"""
    return {
        "task_info": {
            "task_type": "waveform-analysis"
        },
        "visualization_config": {
            "output_format": "png",
            "dpi": 300,
            "figsize": [14, 8],
            "title": f"{ep_path.project_name} 波形分析"
        },
        "data_sources": [
            {
                "project": ep_path.project_name,
                "state": "origin",
                "label": "目标波形"
            }
        ]
    }


def _create_generic_template(ep_path: ExternalPath) -> dict:
    """创建通用配置模板"""
    return {
        "task_info": {
            "task_type": ep_path.task_type,
            "task_name": ep_path.task_name,
            "description": f"{ep_path.project_name}项目的{ep_path.task_type}任务",
            "version": "1.0"
        },
        "visualization_config": {
            "method": ep_path.task_type,
            "output_format": "png",
            "dpi": 300,
            "figsize": [10, 6],
            "title": f"{ep_path.project_name} {ep_path.task_type}"
        },
        "data_sources": [
            {
                "project": ep_path.project_name,
                "state": "origin",
                "label": "数据源"
            }
        ]
    }


def _execute_task(ep_path: ExternalPath) -> bool:
    """
    执行外部项目任务
    
    Args:
        ep_path: 外部项目路径对象
        
    Returns:
        bool: 执行是否成功
    """
    try:
        # 加载配置
        config = _load_config(ep_path.config_path)
        
        # 验证配置（使用严格验证器）
        validated_config = _validate_config(config, ep_path.task_type)
        
        # 根据任务类型选择执行器
        if ep_path.task_type == 'freq-response-compare':
            return _execute_freq_response_task(ep_path, validated_config)
        if ep_path.task_type == 'freq-response-compensator':
            return _execute_freq_response_compensator_task(ep_path, validated_config)
        elif ep_path.task_type == 'bias-visualization':
            return _execute_bias_visualization_task(ep_path, validated_config)
        elif ep_path.task_type == 'waveform-analysis':
            return _execute_waveform_analysis_task(ep_path, validated_config)
        elif ep_path.task_type == 'wnet5-circuit-validation':
            return _execute_wnet5_circuit_validation_task(ep_path, validated_config)
        elif ep_path.task_type == 'qemu-c-inference':
            return _execute_qemu_c_inference_task(ep_path, validated_config)
        elif ep_path.task_type in ('ablation-study', 'compare'):
            return _execute_ablation_study_task(ep_path, validated_config)
        else:
            logger.error(f"不支持的任务类型: {ep_path.task_type}")
            return False
            
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        return False

def _create_freq_response_compensator_template(ep_path: ExternalPath) -> dict:
    """创建频率响应补偿器（基于 linear_response.json）配置模板"""
    return {
        "task_info": {
            "task_type": "freq-response-compensator",
            "description": "基于 linear_response.json 绘制 gains_origin vs gains_comped (均值) 及差异曲线"
        },
        "project_name": ep_path.project_name,
        "visualization_config": {
            "output_format": "png",
            "dpi": 300,
            "figsize": [10, 6],
            "title": f"{ep_path.project_name} 补偿器频率响应",
            "log_scale": True
        }
    }


def _load_config(config_path: Path) -> dict:
    """加载配置文件"""
    import json
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _validate_config(config: dict, task_type: str) -> dict:
    """验证配置文件格式（使用严格验证器）"""
    from .config_validator import validate_visualization_config_data, ConfigValidationError

    # 跳过验证的任务类型（使用自定义配置格式）
    skip_validation_types = {'ablation-study', 'compare'}
    if task_type in skip_validation_types:
        logger.info(f"跳过配置验证 (自定义格式): {task_type}")
        return config
    
    try:
        # 使用严格的配置验证器
        validated_config = validate_visualization_config_data(config, task_type)
        logger.info(f"[OK] 配置验证通过: {task_type}")
        return validated_config
    except ConfigValidationError as e:
        logger.error(f"[ERROR] 配置验证失败: {e}")
        raise ValueError(f"配置验证失败: {e}")
    except Exception as e:
        logger.error(f"[ERROR] 配置验证过程出错: {e}")
        raise ValueError(f"配置验证过程出错: {e}")


def _execute_freq_response_task(ep_path: ExternalPath, config: dict) -> bool:
    """执行频率响应对比任务"""
    try:
        # 导入可视化模块
        from visualization.frequency_response_json_comparator import quick_compare
        
        # 构建参数
        viz_config = config['visualization_config']
        data_sources = config['data_sources']
        
        if len(data_sources) < 1:
            logger.error("配置文件中必须至少定义一个数据源")
            return False
        
        # 构建参数
        project1 = data_sources[0]['project']
        state1 = data_sources[0].get('state', 'origin')
        
        if len(data_sources) >= 2:
            project2 = data_sources[1]['project']
            state2 = data_sources[1].get('state', 'compensation')
        else:
            project2 = None  # 默认与project1相同
            state2 = 'compensation'
        
        layout = viz_config.get('layout', 'side_by_side')
        freq_range = viz_config.get('freq_range')
        gain_range = viz_config.get('gain_range')
        figsize = viz_config.get('figsize')
        dpi = viz_config.get('dpi', 300)
        title = viz_config.get('title')
        
        # 执行比较
        output_file = quick_compare(
            project1=project1,
            project2=project2 if project2 is not None else project1,
            state1=state1,
            state2=state2,
            layout=layout,
            output_dir=str(ep_path.output_path),
            projects_root="projects",
            freq_range=freq_range,
            gain_range=gain_range,
            figsize=figsize,
            dpi=dpi,
            title=title
        )
        
        if output_file and os.path.exists(output_file):
            logger.info(f"频率响应图已生成: {output_file}")
            
            # 保存元数据
            _save_task_metadata(ep_path, config, output_file)
            return True
        else:
            logger.error("图像生成失败")
            return False
        
    except ImportError as e:
        logger.error(f"无法导入频率响应比较模块: {e}")
        return False


def _execute_freq_response_compensator_task(ep_path: ExternalPath, config: dict) -> bool:
    """执行补偿器频率响应绘制任务 (基于 linear_response.json)

    需求更新：
    - 不再绘制均值曲线
    - 对每个震级( magnitude )绘制一条 Difference 曲线: diff_m(freq) = gains_comped[m] - gains_origin[m]
    - 仅绘制 Difference 曲线集合，并在图例中标注对应震级值
    """
    import json
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    try:
        viz_cfg = config.get('visualization_config', {})
        project_name = config['project_name']
        linear_path = Path('projects') / project_name / 'data' / 'linear_response.json'
        if not linear_path.exists():
            logger.error(f"未找到 linear_response.json: {linear_path}")
            return False
        with open(linear_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        required_keys = {'gains_origin', 'gains_comped', 'frequencies', 'magnitudes'}
        if not required_keys.issubset(data.keys()):
            logger.error(f"linear_response.json 缺少字段: {required_keys - set(data.keys())}")
            return False
        gains_origin = np.array(data['gains_origin'])
        gains_comped = np.array(data['gains_comped'])
        freqs = np.array(data['frequencies'])
        magnitudes = np.array(data['magnitudes'])
        if freqs.size == 0:
            logger.error('frequencies 为空')
            return False
        if gains_origin.ndim != 2 or gains_comped.shape != gains_origin.shape:
            logger.error('gains_origin/gains_comped 形状异常，期望二维且匹配')
            return False
        if gains_origin.shape[0] != magnitudes.shape[0]:
            logger.error(f"震级数量 {magnitudes.shape[0]} 与增益矩阵行数 {gains_origin.shape[0]} 不匹配")
            return False
        figsize = tuple(viz_cfg.get('figsize', [10, 6]))
        dpi = viz_cfg.get('dpi', 300)
        title = viz_cfg.get('title', f'{project_name} 补偿器差分响应 (按震级)')
        freq_range = viz_cfg.get('freq_range')
        gain_range = viz_cfg.get('gain_range')
        log_scale = viz_cfg.get('log_scale', True)

        # 过滤特定震级
        target_magnitudes = viz_cfg.get('target_magnitudes')
        if target_magnitudes:
            indices = []
            for target in target_magnitudes:
                # 找到最接近的震级索引
                idx = (np.abs(magnitudes - target)).argmin()
                indices.append(idx)
            # 去重并排序
            indices = sorted(list(set(indices)))
            
            magnitudes = magnitudes[indices]
            gains_origin = gains_origin[indices]
            gains_comped = gains_comped[indices]
            logger.info(f"已过滤震级，保留: {magnitudes}")

        # 样式调优：接近报告中使用的风格（tab20 调色板 + 半透明网格 + 细线 + 稀疏标记）
        fig, ax = plt.subplots(figsize=figsize)
        plot_fn = ax.semilogx if log_scale else ax.plot
        base_cmap = cm.get_cmap('tab20')  # 与报告中使用的 tab20 相近
        n_mag = gains_origin.shape[0]
        # 标记稀疏采样间隔
        mark_every = max(1, len(freqs) // 24)
        cmap_len = getattr(base_cmap, 'N', 20)
        for idx in range(n_mag):
            diff_curve = gains_comped[idx] - gains_origin[idx]
            color = base_cmap(idx % cmap_len)
            label = f'M={magnitudes[idx]:.2f} mm/s^2'
            plot_fn(
                freqs,
                diff_curve,
                label=label,
                linewidth=1.3,
                alpha=0.92,
                color=color,
                marker='o',
                markersize=3,
                markevery=mark_every
            )
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Gain Difference (Comp - Orig)')
        ax.set_title(title)
        ax.grid(True, which='both', alpha=0.3, linestyle='--')
        if freq_range and len(freq_range) == 2:
            ax.set_xlim(freq_range[0], freq_range[1])
        if gain_range and len(gain_range) == 2:
            ax.set_ylim(gain_range[0], gain_range[1])
        # 图例放置与滚动控制：若曲线很多，使用多列
        if n_mag <= 12:
            ax.legend(framealpha=0.45, fontsize=9)
        else:
            ax.legend(ncol=2, fontsize=8, framealpha=0.4)
        ep_path.output_path.mkdir(parents=True, exist_ok=True)
        out_fmt = viz_cfg.get('output_format', 'png')
        out_file = ep_path.output_path / f'compensator_difference_curves.{out_fmt}'
        fig.savefig(str(out_file), dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        logger.info(f"补偿器差分(按震级)频率响应图已保存: {out_file}")
        _save_task_metadata(ep_path, config, str(out_file))
        return True
    except Exception as e:
        logger.error(f"补偿器频率响应任务失败: {e}")
        return False


def _execute_bias_visualization_task(ep_path: ExternalPath, config: dict) -> bool:
    """执行偏置可视化任务"""
    logger.warning(f"偏置可视化任务暂未实现")
    return False


def _execute_waveform_analysis_task(ep_path: ExternalPath, config: dict) -> bool:
    """执行波形分析任务"""
    logger.warning(f"波形分析任务暂未实现")
    return False


def _save_task_metadata(ep_path: ExternalPath, config: dict, output_file: str) -> None:
    """保存任务元数据"""
    import json
    from datetime import datetime
    
    metadata = {
        "execution_time": datetime.now().isoformat(),
        "task_info": config['task_info'],
        "output_files": [output_file],
        "config_hash": _calculate_config_hash(config)
    }
    
    metadata_file = ep_path.output_path / "task_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def _calculate_config_hash(config: dict) -> str:
    """计算配置文件哈希值"""
    import hashlib
    import json
    config_str = json.dumps(config, sort_keys=True)
    return hashlib.md5(config_str.encode()).hexdigest()


def _show_ep_help() -> None:
    """显示ep命令帮助信息"""
    help_text = """
ep 命令使用说明：

命令格式：
  cli.py ep <外部项目路径>

路径格式：
  1. 独立外部项目: external/projects/任务类型/任务名
  2. 完整训练项目: projects/项目名/external/任务类型/任务名  
  3. 相对训练项目: 项目名/任务类型/任务名
  4. 简化训练项目: 项目名/任务名 (自动检测任务类型)
  5. 绝对路径: 任意绝对路径

示例：
  cli.py ep external/projects/freq-response-compare/PS-5-190_vs_PS-5-360
  cli.py ep LSTMu32al_rs300_ex2/freq-response-compare/baseline-comparison
  cli.py ep LSTMu32al_rs300_ex2/baseline-comparison

支持的任务类型：
  - freq-response-compare: 频率响应对比
    - freq-response-compensator: 补偿器频率响应差分绘图
  - bias-visualization: 偏置可视化
  - waveform-analysis: 波形分析
  - wnet5-circuit-validation: WNET5电路验证
    - qemu-c-inference: 从 LSTM 权重生成 QEMU C 工程并做推理耗时测试
  - data-analysis: 数据分析
  - model-export: 模型导出
  - performance-benchmark: 性能基准测试

工作流程：
  1. 手动创建配置文件（参考文档或示例）
  2. 运行命令执行外部项目任务
    """
    print(help_text)


def _execute_wnet5_circuit_validation_task(ep_path: ExternalPath, config: dict) -> bool:
    """执行WNET5电路验证任务"""
    try:
        from visualization.wnet5_circuit_validator import WNET5CircuitValidator
        
        logger.info(f"执行WNET5电路验证任务: {ep_path.task_name}")
        
        validator = WNET5CircuitValidator(config, ep_path.output_path)
        result = validator.execute_validation()
        
        if result:
            logger.info(f"[OK] WNET5电路验证任务完成: {ep_path.output_path}")
        
        return result
        
    except ImportError as e:
        logger.error(f"无法导入WNET5电路验证模块: {e}")
        return False
    except Exception as e:
        logger.error(f"WNET5电路验证任务执行失败: {e}")
        return False


def _execute_qemu_c_inference_task(ep_path: ExternalPath, config: dict) -> bool:
    """执行自动识别模型类型的 QEMU C 推理任务。"""
    try:
        from .lstm_qemu_ep_task import execute_qemu_inference_task

        logger.info(f"执行 QEMU C 推理任务: {ep_path.task_name}")
        return execute_qemu_inference_task(ep_path, config)
    except ImportError as e:
        logger.error(f"无法导入 QEMU C 推理模块: {e}")
        return False
    except Exception as e:
        logger.error(f"QEMU C 推理任务执行失败: {e}")
        return False


def _execute_ablation_study_task(ep_path: ExternalPath, config: dict) -> bool:
    """执行消融实验对比任务"""
    try:
        from visualization.ablation_study import AblationStudyAnalyzer

        logger.info(f"执行消融实验对比任务: {ep_path.task_name}")

        analyzer = AblationStudyAnalyzer(config, ep_path.output_path)
        results = analyzer.run_analysis()
        analyzer.save_results()

        logger.info(f"[OK] 消融实验任务完成: {ep_path.output_path}")
        _save_task_metadata(ep_path, config, str(ep_path.output_path))
        return True

    except ImportError as e:
        logger.error(f"无法导入消融实验模块: {e}")
        return False
    except Exception as e:
        logger.error(f"消融实验任务执行失败: {e}")
        return False


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 简单自测留空，避免类型不匹配
    pass