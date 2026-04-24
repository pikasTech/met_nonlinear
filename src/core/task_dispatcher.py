"""
任务分发模块

负责根据任务类型分发执行相应的任务，包括所有任务类型的处理逻辑。
从 cli.py 中移动而来，保持所有原有功能不变。
"""

import logging
import traceback
import shutil
import os
import json
import matplotlib.pyplot as plt
from core.project_manager import ProjectManager
from core.cli_helpers import met_comp_with_project
from core.tasks.resistance_task import ResistanceTaskHandler

logger = logging.getLogger(__name__)


_TRAIN_INVALIDATED_ARTIFACTS = (
    'metrics.json',
    'linear_response.json',
    'linearity_by_frequency.json',
)


def _get_arg_value(args, key, default=None):
    """
    从参数对象或字典中获取值（兼容性函数）
    
    Args:
        args: 参数对象或字典
        key: 参数键名
        default: 默认值
        
    Returns:
        参数值
    """
    if hasattr(args, key):
        return getattr(args, key)
    elif isinstance(args, dict):
        return args.get(key, default)
    else:
        return default


def _invalidate_downstream_artifacts_after_training(project_path):
    """清理训练后已过期的评估/汇总产物，避免下游读取旧快照。"""
    data_dir = os.path.join(project_path, 'data')
    training_info_path = os.path.join(data_dir, 'training_info.json')

    if os.path.exists(training_info_path):
        try:
            with open(training_info_path, 'r', encoding='utf-8') as file:
                training_info = json.load(file)
            if 'evaluation_metrics' in training_info:
                del training_info['evaluation_metrics']
                with open(training_info_path, 'w', encoding='utf-8') as file:
                    json.dump(training_info, file, indent=4)
                logger.info(
                    "[invalidate] Removed stale training_info.json.evaluation_metrics for '%s'",
                    project_path,
                )
        except Exception as error:
            logger.warning(
                "[invalidate] Failed to clear evaluation_metrics for '%s': %s",
                project_path,
                error,
            )

    for artifact_name in _TRAIN_INVALIDATED_ARTIFACTS:
        artifact_path = os.path.join(data_dir, artifact_name)
        if not os.path.exists(artifact_path):
            continue
        try:
            os.remove(artifact_path)
            logger.info("[invalidate] Removed stale artifact: %s", artifact_path)
        except Exception as error:
            logger.warning(
                "[invalidate] Failed to remove stale artifact '%s': %s",
                artifact_path,
                error,
            )


def _refresh_metrics_summary(project, reason):
    """在上游产物更新后立即刷新 metrics.json。"""
    metrics_path = os.path.join(project.checkpoint_dir, 'metrics.json')
    summary = project.export_metrics_summary()
    logger.info(
        "[ok] Metrics summary refreshed for project '%s' after %s",
        project.project_name,
        reason,
    )
    logger.info(f"   Status: {summary.get('status', 'unknown')}")
    logger.info(f"   Output file: {metrics_path}")
    return summary


def dispatch_task(task_type, project_names, args):
    """
    根据任务类型分发执行任务
    
    Args:
        task_type: 任务类型（字符串）
        project_names: 项目名称列表
        args: 解析后的参数对象（CLIArgs）或字典（兼容性）
    """
    # 检查是否为频率响应对比任务
    freq_compare_sources = _get_arg_value(args, 'freq_compare_sources', None)
    if freq_compare_sources is not None:
        _handle_freq_response_compare_task(project_names, args)
        return
    
    failures = []

    for project_name in project_names:
        normalized_project_name = project_name.replace('\\', '/')
        if os.path.isabs(project_name):
            project_path = project_name
        elif normalized_project_name.startswith('projects/'):
            project_path = normalized_project_name
        else:
            project_path = f'projects/{normalized_project_name}'
        logger.info(f'Project path: {project_path}')
        
        try:
            if task_type == 'train':
                _handle_train_task(project_path)
            elif task_type == 'evaluate':
                _handle_evaluate_task(project_path, project_names, args)
            elif task_type == 'metrics':
                _handle_metrics_task(project_path, project_names, args)
            elif task_type == 'clean':
                _handle_clean_task(project_path, project_name)
            elif task_type == 'model_info':
                _handle_model_info_task(project_path, project_name)
            elif task_type == 'lut':
                _handle_lut_task(project_path)
            elif task_type == 'inference':
                _handle_inference_task(project_path, project_names, args)
            elif task_type == 'analyze':
                _handle_analyze_task(project_path, project_names, args)
            elif task_type == 'wave':
                _handle_wave_task(project_path, project_name, args)
            elif task_type == 'bias_visualization':
                _handle_bias_visualization_task(project_path, project_names, args)
            elif task_type == 'export_resistance':
                _handle_export_resistance_task(project_path, project_name, args)
            elif task_type == 'standardize_resistance':
                _handle_standardize_resistance_task(project_path, project_name, args)
            elif task_type == 'waveform_vis':
                _handle_waveform_vis_task(project_path, project_name, args)
            elif task_type == 'loss_plot':
                _handle_loss_plot_task(project_path, project_name, args)
            else:
                logger.error(f"未知的任务类型: {task_type}")
                continue
                
        except Exception as e:
            error_msg = f"Error occurred while executing {task_type} task for project '{project_name}': {e}"
            logger.error(error_msg)
            traceback.print_exc()
            failures.append((project_name, e))
            continue

    if failures:
        if len(failures) == 1:
            raise failures[0][1]
        failed_projects = ', '.join(project_name for project_name, _ in failures)
        raise RuntimeError(
            f"{len(failures)} project(s) failed during task '{task_type}': {failed_projects}"
        )


def _handle_train_task(project_path):
    """处理训练任务"""
    met_comp_with_project(project_path)
    _invalidate_downstream_artifacts_after_training(project_path)
    logger.info("[chain] Training completed for '%s', starting downstream evaluation", project_path)
    _handle_evaluate_task(project_path, [project_path], {})


def _handle_evaluate_task(project_path, project_names, args):
    """处理评估任务"""
    project = ProjectManager(project_path)
    project.evaluate()
    _refresh_metrics_summary(project, 'evaluation')


def _handle_metrics_task(project_path, project_names, args):
    """处理指标提取任务。"""
    metrics_path = os.path.join(project_path, 'data', 'metrics.json')
    if _get_arg_value(args, 'missing_only', False) and os.path.exists(metrics_path):
        logger.info(f"[skip] Metrics export for '{project_path}' (metrics.json already exists)")
        return

    project = ProjectManager(project_path)
    _refresh_metrics_summary(project, 'metrics export')


def _handle_clean_task(project_path, project_name):
    """处理清理任务"""
    shutil.rmtree(f'{project_path}/data')
    logger.info(f'Cleaned project: {project_path}')


def _handle_model_info_task(project_path, project_name):
    """处理模型信息任务"""
    project = ProjectManager(project_path)
    project.model_info()
    _refresh_metrics_summary(project, 'model info export')


def _handle_lut_task(project_path):
    """处理LUT任务"""
    project = ProjectManager(project_path)
    project.lut()


def _handle_inference_task(project_path, project_names, args):
    """处理推理任务"""
    project = ProjectManager(project_path)
    project.run_inference(
        force=_get_arg_value(args, 'force_mode', False), 
        quick=_get_arg_value(args, 'quick_inference', False), 
        layers=_get_arg_value(args, 'layers_param', None)
    )
    if len(project_names) == 1:
        plt.show()


def _handle_analyze_task(project_path, project_names, args):
    """处理分析任务"""
    project = ProjectManager(project_path)
    # 设置偏置分析参数到配置中
    project.config.bias_method = _get_arg_value(args, 'bias_method', 'auto')
    project.config.bias_params = _get_arg_value(args, 'bias_params', {})
    project.config.enable_bias_analysis = True
    project.analyze_errors(force=_get_arg_value(args, 'force_mode', False))
    if len(project_names) == 1:
        plt.show()


def _handle_wave_task(project_path, project_name, args):
    """处理波形生成任务"""
    project = ProjectManager(project_path)
    result = project.generate_wave_data(force=_get_arg_value(args, 'force_mode', False))
    logger.info(f"✅ Wave data generated successfully for project '{project_name}'")
    logger.info(f"   Dataset type: {result['dataset_type']}")
    logger.info(f"   Output folder: {result['output_folder']}")
    logger.info(f"   Files generated: {len(result['files'])}")
    for file_type, file_path in result['files'].items():
        logger.info(f'     {file_type}: {file_path}')


def _handle_bias_visualization_task(project_path, project_names, args):
    """处理偏置可视化任务"""
    project = ProjectManager(project_path)
    project_name = project_path.split('/')[-1]
    
    # 设置默认路径
    baseline_dir = _get_arg_value(args, 'baseline_dir', None)
    compensated_dir = _get_arg_value(args, 'compensated_dir', None)
    if baseline_dir is None:
        baseline_dir = f"{project_path}/data/inference_baseline"
    if compensated_dir is None:
        compensated_dir = f"{project_path}/data/inference_c123"
    
    result = project.visualize_bias_comparison(
        baseline_dir=baseline_dir,
        compensated_dir=compensated_dir,
        output_dir=_get_arg_value(args, 'vis_output_dir', None),
        config_path=_get_arg_value(args, 'vis_config_path', None)
    )
    logger.info(f"✅ Bias comparison visualization completed for project '{project_name}'")
    logger.info(f"   Project: {result['project_name']}")
    logger.info(f"   Bias improvements: Mean {result['bias_global_improvements']['mean']:.1f}%, "
              f"Std {result['bias_global_improvements']['std']:.1f}%, "
              f"Max {result['bias_global_improvements']['max']:.1f}%")
    logger.info(f"   Output directory: {result['output_dir']}")
    logger.info(f"   Figures generated: {result['files_generated']['total_figures']}")
    logger.info(f"   Analysis report: {result['files_generated']['analysis_report']}")
    
    if len(project_names) == 1:
        plt.show()


def _handle_export_resistance_task(project_path, project_name, args):
    """
    处理电阻导出任务
    
    # CRITICAL: 包含强制验证步骤
    # NO ROLLBACK: 任何错误直接报告
    # NO MOCK: 所有操作基于真实数据
    """
    handler = ResistanceTaskHandler(project_path)
    
    # 获取参数
    include_standardized = len(_get_arg_value(args, 'series', ['E96', 'E24'])) > 0
    series_list = _get_arg_value(args, 'series', ['E96', 'E24'])
    output_dir = _get_arg_value(args, 'output_dir', None)
    validate = not _get_arg_value(args, 'skip_validation', False)
    
    # BOM相关参数
    generate_bom = _get_arg_value(args, 'generate_bom', False)
    bom_config = None
    if generate_bom:
        bom_config = {
            'package': _get_arg_value(args, 'bom_package', '0805'),
            'tolerance': _get_arg_value(args, 'bom_tolerance', '1%')
        }
        # 只有CLI明确指定了bom_numbering时才设置，否则从config.json读取
        bom_numbering = _get_arg_value(args, 'bom_numbering', None)
        if bom_numbering is not None:
            bom_config['numbering_mode'] = bom_numbering
        # 如果CLI指定了标准化系列，添加到配置中（覆盖config.json中的配置）
        bom_standardize = _get_arg_value(args, 'bom_standardize', None)
        if bom_standardize:
            bom_config['standardization_series'] = bom_standardize
    
    # 执行导出 - NO ROLLBACK: 失败直接报错
    result = handler.export_resistances(
        include_standardized=include_standardized,
        series_list=series_list,
        output_dir=output_dir,
        validate_with_netlist=validate,  # 默认启用验证
        generate_bom=generate_bom,
        bom_config=bom_config
    )
    
    # 打印结果
    logger.info("=" * 60)
    logger.info("电阻导出完成")
    logger.info(f"  总电阻数: {result['resistance_count']}")
    logger.info(f"  输出文件: {result['output_file']}")
    if result['standardized']:
        logger.info(f"  标准化系列: {', '.join(result['series'])}")
    if result.get('validation_passed') is not None:
        status = "✅ 通过" if result['validation_passed'] else "❌ 失败"
        logger.info(f"  验证状态: {status}")
    
    # BOM信息
    if 'bom' in result and result['bom'].get('success'):
        logger.info("BOM生成结果:")
        # 显示原始BOM文件
        if 'raw_bom_file' in result['bom']:
            logger.info(f"  原始BOM文件: {result['bom']['raw_bom_file']}")
        logger.info(f"  最终BOM文件: {result['bom']['output_file']}")
        logger.info(f"  权重电阻数: {result['bom']['count']}")
        
        # 显示压缩率信息（如果有）
        if 'compression_rate' in result['bom']:
            logger.info(f"  压缩率: {result['bom']['original_rows']} -> {result['bom']['final_rows']} 行 ({result['bom']['compression_rate']})")
        
        if 'summary' in result['bom']:
            summary = result['bom']['summary']
            logger.info(f"  封装规格: {summary.get('package', 'N/A')}")
            logger.info(f"  精度规格: {summary.get('tolerance', 'N/A')}")
    
    logger.info("=" * 60)
    
    # 如果验证失败，返回非零退出码
    if result.get('validation_passed') == False:
        import sys
        sys.exit(1)

def _handle_standardize_resistance_task(project_path, project_name, args):
    """
    处理电阻标准化任务
    
    # NO MOCK: 必须基于真实CSV文件
    # NO ROLLBACK: 错误直接报告
    """
    handler = ResistanceTaskHandler(project_path)
    
    # 获取输入CSV路径
    input_csv = _get_arg_value(args, 'input_csv', None)
    if not input_csv:
        # 使用默认路径
        from spice_simulator.spice_path_manager import SPICEPathManager
        path_manager = SPICEPathManager(project_path)
        input_csv = path_manager.get_resistance_csv_path()
    
    import os
    if not os.path.exists(input_csv):
        logger.error(
            f"Input CSV file not found: {input_csv}\n"
            f"Please run --export-resistance first"
        )
        import sys
        sys.exit(1)
    
    # 执行标准化
    result = handler.standardize_existing_csv(
        input_csv=input_csv,
        series_list=_get_arg_value(args, 'series', ['E96', 'E24']),
        output_dir=_get_arg_value(args, 'output_dir', None)
    )
    
    # 打印结果
    logger.info("=" * 60)
    logger.info("电阻标准化完成")
    logger.info(f"  输入文件: {result['input_file']}")
    logger.info(f"  输出文件: {result['output_file']}")
    logger.info(f"  标准化系列: {', '.join(result['series'])}")


def _handle_waveform_vis_task(project_path: str, project_name: str, args):
    """处理波形可视化任务"""
    from core.waveform_visualizer import WaveformVisualizer
    
    logger.info(f"开始为项目 {project_name} 生成波形可视化")
    
    # 创建项目管理器
    project = ProjectManager(project_path)
    
    # 创建可视化器（支持并行化）
    max_workers = _get_arg_value(args, 'max_workers', None)
    visualizer = WaveformVisualizer(project, max_workers=max_workers)
    
    # 执行可视化
    force = _get_arg_value(args, 'force_mode', False)
    
    import time
    start_time = time.time()
    
    result = visualizer.visualize_dataset(force=force)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # 输出结果
    logger.info("=" * 60)
    logger.info(f"波形可视化完成 (耗时: {duration:.2f}秒)")
    logger.info(f"  - 项目名称: {project_name}")
    logger.info(f"  - 输出目录: {result['output_directory']}")
    logger.info(f"  - 相对路径: visualizations/waveforms/")
    logger.info(f"  - 生成文件数: {len(result['generated_files'])}")
    logger.info(f"  - 跳过文件数: {len(result['skipped_files'])}")
    logger.info(f"  - 总组合数: {result['total_combinations']}")
    logger.info(f"  - 并行线程数: {visualizer.max_workers}")
    
    if result['generated_files']:
        logger.info("新生成的文件列表:")
        for file_path in result['generated_files']:
            logger.info(f"        {os.path.relpath(file_path, project_path)}")


def _handle_freq_response_compare_task(project_names, args):
    """处理频率响应对比任务（基于JSON数据的轻量级实现）"""
    from visualization.frequency_response_json_comparator import (
        LinearResponseDataLoader, FrequencyResponseComparator, 
        DataSourceSpec, LayoutMode, DataState
    )
    
    freq_compare_sources = _get_arg_value(args, 'freq_compare_sources', None)
    layout_mode_str = _get_arg_value(args, 'layout_mode', 'overlay')
    
    if not freq_compare_sources:
        logger.error("频率响应对比任务缺少数据源规范")
        return
    
    logger.info(f"🚀 开始基于JSON数据的频率响应对比任务")
    logger.info(f"📊 数据源: {freq_compare_sources}")
    logger.info(f"🎨 布局模式: {layout_mode_str}")
    
    try:
        # 解析数据源规范
        if len(freq_compare_sources) == 1:
            # 默认行为：项目内补偿前后对比
            project_name = freq_compare_sources[0]
            source1_spec = DataSourceSpec(project_name, DataState.ORIGIN)
            source2_spec = DataSourceSpec(project_name, DataState.COMPENSATION)
            logger.info(f"📋 对比项目 {project_name} 的补偿前后数据")
        elif len(freq_compare_sources) == 2:
            # 任意两个数据源对比
            source1_spec = DataSourceSpec.parse(freq_compare_sources[0])
            source2_spec = DataSourceSpec.parse(freq_compare_sources[1])
            logger.info(f"🔍 对比数据源: {source1_spec} vs {source2_spec}")
        else:
            raise ValueError("--vis-freq-response-compare 参数数量错误，应为1-2个")
        
        # 加载数据源
        logger.info("⚡ 正在从JSON文件加载数据源...")
        data_loader = LinearResponseDataLoader("projects")
        source1_data = data_loader.extract_data_source(source1_spec)
        source2_data = data_loader.extract_data_source(source2_spec)
        
        # 创建对比可视化器
        layout_mode = LayoutMode(layout_mode_str)
        comparator = FrequencyResponseComparator(layout_mode)
        
        # 生成对比可视化
        logger.info("🎨 正在生成对比可视化...")
        fig, output_path = comparator.compare_sources(
            source1_data, source2_data, 
            output_folder=os.path.join('projects', 'results'),
            show_plot=False  # 不自动显示，让用户控制
        )
        
        logger.info(f"✅ 频率响应对比图已生成: {output_path}")
        
        # 关闭图形以释放内存
        plt.close(fig)
        
    except FileNotFoundError as e:
        logger.error(f"❌ 数据文件未找到: {e}")
        logger.error("请确保项目已完成训练并生成了linear_response.json文件")
    except Exception as e:
        logger.error(f"❌ 频率响应对比任务执行失败: {e}")
        import traceback
        traceback.print_exc()
        raise


def _handle_loss_plot_task(project_path, project_name, args):
    """处理loss曲线绘制任务"""
    from core.training_log import TrainingLogger
    import numpy as np

    if project_path.startswith('projects/'):
        checkpoint_dir = f'{project_path}/data'
    else:
        checkpoint_dir = f'projects/{project_path}/data'
    training_logger = TrainingLogger(checkpoint_dir)
    log_data = training_logger.load()

    if 'epoch' not in log_data or len(log_data['epoch']) == 0:
        logger.error(f"项目 {project_name} 没有训练日志数据")
        return

    epochs = np.array(log_data['epoch'])
    loss = np.array(log_data.get('loss', []))
    val_loss = np.array(log_data.get('val_loss', []))
    lr = np.array(log_data.get('lr', []))

    fig, ax1 = plt.subplots(figsize=(10, 6))

    if len(loss) > 0:
        ax1.semilogy(epochs, loss, label='Loss', color='blue', linestyle='-', linewidth=1)
    if len(val_loss) > 0:
        ax1.semilogy(epochs, val_loss, label='Validation Loss', color='orange', linestyle='--', linewidth=1)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss (Log Scale)')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)

    if len(lr) > 0:
        ax2 = ax1.twinx()
        ax2.plot(epochs, lr, label='Learning Rate', color='red', linestyle='-', linewidth=0.8, alpha=0.7)
        ax2.set_ylabel('Learning Rate', color='red')
        ax2.tick_params(axis='y', labelcolor='red')

    lines1, labels1 = ax1.get_legend_handles_labels()
    if len(lr) > 0:
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='best')
    else:
        ax1.legend(loc='best')

    project_name_short = project_name.split('/')[-1]
    ax1.set_title(f'Training Loss Curves - {project_name_short}')

    plt.tight_layout()
    plt.savefig(os.path.join(checkpoint_dir, 'loss_curve.png'), dpi=150)
    logger.info(f"Loss曲线已保存: {checkpoint_dir}/loss_curve.png")
    plt.close(fig)
