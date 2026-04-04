"""QEMU C 推理 EP 任务实现。"""

from __future__ import annotations

import json
import logging
import math
import re
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from .external_path_parser import ExternalPath
from .qemu_cli import execute_qemu_workflow


logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
QEMU_HELLO_TEMPLATE_DIR = REPO_ROOT / 'src' / 'tests' / 'qemu' / 'stm32f405_hello'

DATASET_OVERRIDE_FIELDS = (
    'dataset_type',
    'data_path',
    'sample_rate',
    'time_clipped_s',
    'target_sweep',
    'feature_range',
    'use_scale',
    'use_cache_features',
    'data_base_path',
)


@dataclass
class LstmModelSpec:
    """LSTM C 生成所需的模型规格。"""

    model_project_name: str
    weights_json_path: Path
    input_dim: int
    lstm_units: int
    dense_units: int
    output_units: int
    lstm_kernel: List[List[float]]
    lstm_recurrent_kernel: List[List[float]]
    lstm_bias: List[float]
    dense_kernel: List[List[float]]
    dense_bias: List[float]
    output_kernel: List[List[float]]
    output_bias: List[float]


@dataclass
class GrnModelSpec:
    """GRN(GRU) C 生成所需的模型规格。"""

    model_project_name: str
    weights_json_path: Path
    input_dim: int
    gru_units: int
    dense_units: int
    output_units: int
    gru_kernel: List[List[float]]
    gru_recurrent_kernel: List[List[float]]
    gru_input_bias: List[float]
    gru_recurrent_bias: List[float]
    dense_kernel: List[List[float]]
    dense_bias: List[float]
    output_kernel: List[List[float]]
    output_bias: List[float]


@dataclass
class LstmTransformerLayerSpec:
    """LSTMTransformer 单个 Transformer block 的导出规格。"""

    query_kernel: List[List[List[float]]]
    query_bias: List[List[float]]
    key_kernel: List[List[List[float]]]
    key_bias: List[List[float]]
    value_kernel: List[List[List[float]]]
    value_bias: List[List[float]]
    attention_output_kernel: List[List[List[float]]]
    attention_output_bias: List[float]
    ln_attn_gamma: List[float]
    ln_attn_beta: List[float]
    ffn_expand_kernel: List[List[float]]
    ffn_expand_bias: List[float]
    ffn_project_kernel: List[List[float]]
    ffn_project_bias: List[float]
    ln_ffn_gamma: List[float]
    ln_ffn_beta: List[float]


@dataclass
class LstmTransformerModelSpec:
    """LSTMTransformer C 生成所需的模型规格。"""

    model_project_name: str
    weights_json_path: Path
    input_dim: int
    lstm_units: int
    transformer_num_heads: int
    transformer_key_dim: int
    transformer_ff_dim: int
    attention_pool_size: int
    lstm_kernel: List[List[float]]
    lstm_recurrent_kernel: List[List[float]]
    lstm_bias: List[float]
    layers: List[LstmTransformerLayerSpec]
    post_dense_units: int
    post_dense_activation: str
    post_dense_kernel: List[List[float]]
    post_dense_bias: List[float]
    output_input_units: int
    output_units: int
    output_kernel: List[List[float]]
    output_bias: List[float]
    layer_norm_epsilon: float = 1e-6

    @property
    def transformer_layer_count(self) -> int:
        return len(self.layers)


@dataclass
class FrikanIirSpec:
    """单个 FRIKAN 特征通道对应的二阶 IIR 系数。"""

    b0: float
    b1: float
    b2: float
    a1: float
    a2: float


@dataclass
class FrikanKanLayerSpec:
    """FRIKAN 中单层 DenseKAN 的导出规格。"""

    name: str
    input_dim: int
    output_dim: int
    grid_size: int
    spline_order: int
    grid_range: List[float]
    spline_kernel: List[List[List[float]]]
    bias: List[float]
    scale_factor: List[List[float]]
    use_symmetry: bool
    only_positive: bool
    use_even: bool
    basis_activation: str
    disable_basis_activation: bool
    lut_support_min: float
    lut_support_max: float
    lut_values: List[List[List[float]]]


@dataclass
class FrikanModelSpec:
    """FRIKAN C 生成所需的模型规格。"""

    model_project_name: str
    weights_json_path: Path
    input_dim: int
    feature_count: int
    kan_layers: List[FrikanKanLayerSpec]
    iir_filters: List[FrikanIirSpec]
    output_units: int
    lut_points: int
    lut_interpolation: bool
    use_symmetry: bool
    use_even: bool


@dataclass
class ValidationRecord:
    """单条验证波形记录。"""

    record_id: str
    magnitude: float
    frequency: float
    input_sequence: List[List[float]]
    target_sequence: List[float]
    tf_output_sequence: List[float]


@dataclass
class ValidationArtifacts:
    """验证任务所需的输入、参考输出与元数据。"""

    dataset_type: str
    full_data_path: str
    sample_rate: float
    time_window: Dict[str, float]
    input_data_range: float
    output_data_range: float
    loaded_weights_path: Path
    records: List[ValidationRecord]
    tf_debug_sequences: Dict[str, List[Any]] = field(default_factory=dict)

    @property
    def record_count(self) -> int:
        return len(self.records)

    @property
    def seq_len(self) -> int:
        if not self.records:
            return 0
        return len(self.records[0].tf_output_sequence)


def execute_qemu_inference_task(ep_path: ExternalPath,
                                config: Dict[str, Any]) -> bool:
    """执行 qemu-c-inference EP 任务。"""
    ep_path.output_path.mkdir(parents=True, exist_ok=True)

    model_project_name = str(config['model_project_name']).replace('\\', '/')
    benchmark_config = _normalize_benchmark_config(config.get('benchmark_config', {}))
    validation_config = _normalize_validation_config(config.get('validation_config', {}))
    generation_config = config.get('generation_config', {})
    qemu_config = config.get('qemu_config', {})

    model_dir = _resolve_model_project_dir(model_project_name)
    weights_json_path = _resolve_weights_json_path(model_dir, config.get('weights_file'))
    model_type = _detect_model_type(model_project_name, model_dir, weights_json_path)
    model_spec = _load_model_spec(
        model_project_name=model_project_name,
        model_dir=model_dir,
        weights_json_path=weights_json_path,
        model_type=model_type,
        generation_config=generation_config,
    )
    if getattr(model_spec, 'input_dim', 1) != 1:
        raise ValueError(f'当前仅支持单输入模型的数据集验证，实际 input_dim={model_spec.input_dim}')

    validation_artifacts = _prepare_validation_artifacts(
        model_project_name=model_project_name,
        weights_json_path=weights_json_path,
        validation_config=validation_config,
        model_type=model_type,
        model_spec=model_spec,
    )

    generated_project_dir = _resolve_generated_project_dir(ep_path, generation_config)
    overwrite = bool(generation_config.get('overwrite', True))
    generate_qemu_project(
        output_dir=generated_project_dir,
        model_spec=model_spec,
        benchmark_config=benchmark_config,
        validation_artifacts=validation_artifacts,
        overwrite=overwrite,
    )

    wave_paths = _write_validation_wave_files(
        output_root=ep_path.output_path,
        validation_artifacts=validation_artifacts,
        c_output_sequences=None,
        compress=bool(validation_config['wave_output']['compress']),
        export_intermediates=bool(validation_config['wave_output'].get('export_intermediates', True)),
    )
    plot_paths: Dict[str, str] = {}

    execution_summary: Dict[str, Any] = {
        'task_type': 'qemu-c-inference',
        'model_type': model_type,
        'model_project_name': model_project_name,
        'weights_json_path': _relative_or_str(weights_json_path),
        'loaded_weights_path': _relative_or_str(validation_artifacts.loaded_weights_path),
        'generated_project_dir': _relative_or_str(generated_project_dir),
        'benchmark_config': benchmark_config,
        'validation': {
            'dataset': {
                'dataset_type': validation_artifacts.dataset_type,
                'full_data_path': validation_artifacts.full_data_path,
                'sample_rate': validation_artifacts.sample_rate,
            },
            'selection': validation_artifacts.time_window,
            'record_count': validation_artifacts.record_count,
            'seq_len': validation_artifacts.seq_len,
        },
        'qemu_config': qemu_config,
        'wave_paths': wave_paths,
    }

    action = str(qemu_config.get('action', 'build-run'))
    machine = str(qemu_config.get('machine', 'olimex-stm32-h405'))
    timeout = int(qemu_config.get('timeout', 5))
    qemu_path = qemu_config.get('qemu_path')
    gcc_path = qemu_config.get('gcc_path')
    linker_script = qemu_config.get('linker_script')
    output_path = qemu_config.get('output')

    if action == 'generate':
        summary_path = ep_path.output_path / 'benchmark_summary.json'
        _write_json(summary_path, {
            **execution_summary,
            'action': 'generate',
            'status': 'generated',
        })
        _write_json(ep_path.output_path / 'task_metadata.json', {
            'task_info': config['task_info'],
            'output_files': _collect_output_files(
                generated_project_dir,
                summary_path,
                *[Path(path) for path in wave_paths.values()],
            ),
            'action': 'generate',
        })
        logger.info('QEMU 工程已生成: %s', generated_project_dir)
        return True

    run_results: List[Dict[str, Any]] = []
    build_result: Optional[Dict[str, Any]] = None
    first_c_output_sequences: Optional[List[List[float]]] = None
    first_c_debug_sequences: Dict[str, List[Any]] = {}
    validation_run_summary: Optional[Dict[str, Any]] = None

    if action in {'build', 'build-run'}:
        build_workflow = execute_qemu_workflow(
            action='build',
            project_dir=str(generated_project_dir),
            machine=machine,
            timeout=timeout,
            output_path=output_path,
            qemu_path_override=qemu_path,
            gcc_path_override=gcc_path,
            linker_script=linker_script,
        )
        build_result = build_workflow
        if int(build_workflow.get('exit_code', 1)) != 0:
            execution_summary['build'] = build_workflow
            _write_json(ep_path.output_path / 'benchmark_summary.json', execution_summary)
            _write_json(ep_path.output_path / 'task_metadata.json', {
                'task_info': config['task_info'],
                'output_files': _collect_output_files(ep_path.output_path / 'benchmark_summary.json'),
                'action': action,
            })
            return False

    if action in {'run', 'build-run'}:
        repeat_runs = int(benchmark_config['repeat_runs'])
        for run_index in range(repeat_runs):
            run_workflow = execute_qemu_workflow(
                action='run',
                project_dir=str(generated_project_dir),
                machine=machine,
                timeout=timeout,
                output_path=output_path,
                qemu_path_override=qemu_path,
                gcc_path_override=gcc_path,
                linker_script=linker_script,
                success_patterns=['benchmark_complete=1'],
            )
            parsed_output = _enrich_benchmark_output(
                _parse_benchmark_stdout(str(run_workflow.get('run', {}).get('stdout', ''))),
                run_workflow,
                benchmark_config,
            )
            run_results.append({
                'run_index': run_index,
                'workflow': run_workflow,
                'parsed_output': parsed_output,
            })
            if int(run_workflow.get('exit_code', 1)) != 0:
                execution_summary['build'] = build_result
                execution_summary['runs'] = run_results
                _write_json(ep_path.output_path / 'benchmark_summary.json', execution_summary)
                _write_json(ep_path.output_path / 'task_metadata.json', {
                    'task_info': config['task_info'],
                    'output_files': _collect_output_files(ep_path.output_path / 'benchmark_summary.json'),
                    'action': action,
                })
                return False

        validation_workflow = execute_qemu_workflow(
            action='run',
            project_dir=str(generated_project_dir),
            machine=machine,
            timeout=timeout,
            output_path=output_path,
            qemu_path_override=qemu_path,
            gcc_path_override=gcc_path,
            linker_script=linker_script,
            success_patterns=['validation_complete=1'],
        )
        validation_parsed_output = _enrich_benchmark_output(
            _parse_benchmark_stdout(str(validation_workflow.get('run', {}).get('stdout', ''))),
            validation_workflow,
            benchmark_config,
        )
        c_output_sequences = _extract_validation_outputs(validation_parsed_output, validation_artifacts)
        c_debug_sequences = _extract_c_debug_sequences(validation_parsed_output, validation_artifacts)
        comparison_payload = _compute_wave_comparison(validation_artifacts, c_output_sequences)
        intermediate_comparison = _compute_intermediate_comparison(
            validation_artifacts,
            c_debug_sequences,
        )
        first_c_output_sequences = c_output_sequences
        first_c_debug_sequences = c_debug_sequences
        validation_run_summary = {
            'workflow': _summarize_qemu_run_workflow(validation_workflow),
            'parsed_output': _summarize_parsed_output(validation_parsed_output),
            'comparison': comparison_payload['overall'],
            'intermediate_comparison': intermediate_comparison,
        }

        if int(validation_workflow.get('exit_code', 1)) != 0:
            execution_summary['build'] = build_result
            execution_summary['runs'] = run_results
            execution_summary['validation_run'] = validation_run_summary
            _write_json(ep_path.output_path / 'benchmark_summary.json', execution_summary)
            _write_json(ep_path.output_path / 'task_metadata.json', {
                'task_info': config['task_info'],
                'output_files': _collect_output_files(ep_path.output_path / 'benchmark_summary.json'),
                'action': action,
            })
            return False

    execution_summary['build'] = build_result
    execution_summary['runs'] = run_results
    if run_results:
        execution_summary['aggregated'] = _aggregate_run_results(run_results)
    if validation_run_summary is not None:
        execution_summary['validation_run'] = validation_run_summary

    comparison_file = ep_path.output_path / 'validation_comparison.json'
    if first_c_output_sequences is not None:
        wave_paths = _write_validation_wave_files(
            output_root=ep_path.output_path,
            validation_artifacts=validation_artifacts,
            c_output_sequences=first_c_output_sequences,
            compress=bool(validation_config['wave_output']['compress']),
            export_intermediates=bool(validation_config['wave_output'].get('export_intermediates', True)),
            c_debug_sequences=first_c_debug_sequences,
        )
        if bool(validation_config['wave_output'].get('plot_comparison', True)):
            plot_paths = _write_validation_comparison_plots(
                output_root=ep_path.output_path,
                validation_artifacts=validation_artifacts,
                c_output_sequences=first_c_output_sequences,
                dpi=int(validation_config['wave_output'].get('plot_dpi', 200)),
            )
        comparison_payload = _compute_wave_comparison(validation_artifacts, first_c_output_sequences)
        comparison_payload['intermediate'] = _compute_intermediate_comparison(
            validation_artifacts,
            first_c_debug_sequences,
        )
        comparison_payload['wave_paths'] = wave_paths
        if plot_paths:
            comparison_payload['plot_paths'] = plot_paths
        _write_json(comparison_file, comparison_payload)
        execution_summary['wave_paths'] = wave_paths
        if plot_paths:
            execution_summary['plot_paths'] = plot_paths
        execution_summary['comparison'] = comparison_payload['overall']
        execution_summary['comparison_path'] = _relative_or_str(comparison_file)

    summary_path = ep_path.output_path / 'benchmark_summary.json'
    _write_json(summary_path, execution_summary)
    _write_json(ep_path.output_path / 'task_metadata.json', {
        'task_info': config['task_info'],
        'output_files': _collect_output_files(
            summary_path,
            generated_project_dir,
            comparison_file,
            *[Path(path) for path in execution_summary.get('wave_paths', {}).values()],
            *[Path(path) for path in execution_summary.get('plot_paths', {}).values()],
        ),
        'action': action,
    })
    logger.info('QEMU C 推理任务完成: %s', summary_path)
    return True


def execute_lstm_qemu_inference_task(ep_path: ExternalPath,
                                     config: Dict[str, Any]) -> bool:
    """兼容旧调用名，内部统一走自动识别模型类型的任务入口。"""
    return execute_qemu_inference_task(ep_path, config)


def generate_qemu_project(output_dir: Path,
                          model_spec: Any,
                          benchmark_config: Dict[str, Any],
                          validation_artifacts: ValidationArtifacts,
                          overwrite: bool) -> None:
    """生成裸机 QEMU 工程目录。"""
    if output_dir.exists() and not overwrite:
        raise FileExistsError(f'QEMU 工程目录已存在且未允许覆盖: {output_dir}')

    output_dir.mkdir(parents=True, exist_ok=True)
    _copy_runtime_template('startup.c', output_dir / 'startup.c')
    _copy_runtime_template('stm32f405.ld', output_dir / 'stm32f405.ld')
    if isinstance(model_spec, LstmModelSpec):
        main_c = _render_main_c()
        model_header = _render_model_data_header(model_spec, benchmark_config, validation_artifacts)
    elif isinstance(model_spec, LstmTransformerModelSpec):
        main_c = _render_lstm_transformer_main_c()
        model_header = _render_lstm_transformer_model_data_header(model_spec, benchmark_config, validation_artifacts)
    elif isinstance(model_spec, GrnModelSpec):
        main_c = _render_grn_main_c()
        model_header = _render_grn_model_data_header(model_spec, benchmark_config, validation_artifacts)
    elif isinstance(model_spec, FrikanModelSpec):
        main_c = _render_frikan_main_c(model_spec)
        model_header = _render_frikan_model_data_header(model_spec, benchmark_config, validation_artifacts)
    else:
        raise TypeError(f'不支持的模型规格类型: {type(model_spec)}')

    _write_text(output_dir / 'main.c', main_c)
    _write_text(output_dir / 'model_data.h', model_header)


def _resolve_model_project_dir(model_project_name: str) -> Path:
    normalized = model_project_name.replace('\\', '/').strip('/').strip()
    candidate = Path(normalized)
    if not candidate.parts or candidate.parts[0] != 'projects':
        candidate = Path('projects') / candidate
    resolved = REPO_ROOT / candidate
    if not resolved.exists():
        raise FileNotFoundError(f'模型项目目录不存在: {resolved}')
    return resolved


def _resolve_weights_json_path(model_dir: Path, weights_file: Optional[str]) -> Path:
    if weights_file:
        specified = Path(str(weights_file))
        if not specified.is_absolute():
            if specified.parts and specified.parts[0] == 'data':
                specified = model_dir / specified
            else:
                specified = model_dir / 'data' / specified
        resolved = specified
        if not resolved.exists():
            raise FileNotFoundError(f'权重 JSON 不存在: {resolved}')
        return resolved

    candidates = [
        model_dir / 'data' / 'best_val.weights.json',
        model_dir / 'data' / 'best.weights.json',
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f'未找到权重 JSON: {candidates}')


def _resolve_generated_project_dir(ep_path: ExternalPath,
                                   generation_config: Dict[str, Any]) -> Path:
    project_dir = generation_config.get('project_dir', 'qemu_project')
    resolved = Path(str(project_dir))
    if not resolved.is_absolute():
        resolved = ep_path.full_path / resolved
    return resolved


def _load_project_config(model_dir: Path) -> Dict[str, Any]:
    config_path = model_dir / 'config.json'
    if not config_path.exists():
        return {}
    with open(config_path, 'r', encoding='utf-8') as file_obj:
        return json.load(file_obj)


def _normalize_benchmark_config(config: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(config)
    normalized.setdefault('iterations', 100)
    normalized.setdefault('reset_state_each_run', True)
    normalized.setdefault('repeat_runs', 1)
    return normalized


def _normalize_validation_config(config: Dict[str, Any]) -> Dict[str, Any]:
    dataset_config = dict(config.get('dataset', {}))
    selection_config = dict(config.get('selection', {}))
    wave_output_config = dict(config.get('wave_output', {}))

    selection_config.setdefault('start_time_s', 0.0)
    selection_config.setdefault('end_time_s', None)
    wave_output_config.setdefault('compress', True)
    wave_output_config.setdefault('export_intermediates', True)
    wave_output_config.setdefault('plot_comparison', True)
    wave_output_config.setdefault('plot_dpi', 200)

    return {
        'dataset': dataset_config,
        'selection': selection_config,
        'wave_output': wave_output_config,
    }


def _prepare_validation_artifacts(model_project_name: str,
                                  weights_json_path: Path,
                                  validation_config: Dict[str, Any],
                                  model_type: str,
                                  model_spec: Any) -> ValidationArtifacts:
    from .model_engine import ModelEngine
    from .project_manager import ProjectManager

    project_path = _normalize_project_path(model_project_name)
    project_manager = ProjectManager(project_path)
    _apply_validation_dataset_overrides(project_manager.config, validation_config['dataset'])

    model_engine = ModelEngine(project_manager, checkpoint_dir=project_manager.checkpoint_dir)
    model_engine.load_dataset(project_manager.config.dataset_type)
    selected_dataset, time_window = _select_validation_dataset(
        model_engine.dataset_origin,
        validation_config['selection'],
    )

    if project_manager.config.use_scale:
        if model_engine.load_scalers() is None or model_engine.scaler is None:
            raise FileNotFoundError(
                f'未找到推理所需 scaler: {project_manager.checkpoint_dir}/scalers/combined_scaler.json'
            )

    x_input = selected_dataset.reshape2feature(selected_dataset.output_ori)
    batch_size = max(1, x_input.shape[0])

    input_data_range = 1.0
    output_data_range = 1.0
    if project_manager.config.use_scale:
        input_data_range = float(model_engine.scaler.scaler_x.data_range_)
        output_data_range = float(model_engine.scaler.scaler_y.data_range_)

    if model_type == 'frikan':
        loaded_weights_path = _resolve_reference_weights_path(weights_json_path)
        tf_output, tf_debug_sequences = _run_frikan_reference_from_spec(
            model_spec=model_spec,
            x_input=x_input,
            input_data_range=input_data_range,
            output_data_range=output_data_range,
            use_scaler=bool(project_manager.config.use_scale),
        )
    else:
        model_engine.build_model()
        loaded_weights_path = _load_requested_model_weights(model_engine, weights_json_path)
        tf_output = _predict_reference_output(
            model_engine=model_engine,
            x_input=x_input,
            batch_size=batch_size,
            use_scaler=bool(project_manager.config.use_scale),
            model_type=model_type,
        )
        tf_debug_sequences = _collect_tf_debug_sequences(
            model_engine=model_engine,
            x_input=x_input,
            batch_size=batch_size,
            use_scaler=bool(project_manager.config.use_scale),
            model_type=model_type,
        )

    tf_output_2d = np.asarray(tf_output, dtype=np.float64).reshape(x_input.shape[0], x_input.shape[1])
    records = _build_validation_records(selected_dataset, tf_output_2d)

    return ValidationArtifacts(
        dataset_type=str(project_manager.config.dataset_type),
        full_data_path=str(project_manager.config.full_data_path),
        sample_rate=float(selected_dataset.fs),
        time_window=time_window,
        input_data_range=input_data_range,
        output_data_range=output_data_range,
        loaded_weights_path=loaded_weights_path,
        records=records,
        tf_debug_sequences=tf_debug_sequences,
    )


def _predict_reference_output(model_engine: Any,
                              x_input: np.ndarray,
                              batch_size: int,
                              use_scaler: bool,
                              model_type: str) -> np.ndarray:
    return model_engine.model_comp.predict(
        x_input,
        batch_size=batch_size,
        use_scaler=use_scaler,
    )


def _collect_tf_debug_sequences(model_engine: Any,
                                x_input: np.ndarray,
                                batch_size: int,
                                use_scaler: bool,
                                model_type: str) -> Dict[str, List[Any]]:
    import tensorflow as tf

    keras_model = model_engine.model_comp.model
    x_scaled = np.asarray(x_input, dtype=np.float64)
    if use_scaler and model_engine.scaler is not None:
        x_scaled = model_engine.scaler.transform_x(
            x_scaled.reshape(-1, x_scaled.shape[-1])
        ).reshape(x_scaled.shape)

    if model_type == 'lstm_transformer':
        stage_names = ['lstm_hidden']
        stage_outputs = [keras_model.get_layer('lstm_backbone').output]

        transformer_layer_indices = sorted({
            int(match.group(1))
            for layer in keras_model.layers
            for match in [re.fullmatch(r'transformer_ln_attn_(\d+)', layer.name)]
            if match is not None
        })

        for layer_index in transformer_layer_indices:
            stage_names.append(f'transformer_ln_attn_{layer_index}')
            stage_outputs.append(keras_model.get_layer(f'transformer_ln_attn_{layer_index}').output)
            stage_names.append(f'transformer_ln_ffn_{layer_index}')
            stage_outputs.append(keras_model.get_layer(f'transformer_ln_ffn_{layer_index}').output)

        try:
            post_dense_layer = keras_model.get_layer('post_dense')
        except ValueError:
            post_dense_layer = None

        if post_dense_layer is not None:
            stage_names.append('post_dense')
            stage_outputs.append(post_dense_layer.output)

        stage_names.append('output_scaled')
        stage_outputs.append(keras_model.get_layer('output').output)

        intermediate_model = tf.keras.Model(inputs=keras_model.input, outputs=stage_outputs)
        predicted_outputs = intermediate_model.predict(
            x_scaled,
            batch_size=max(1, batch_size),
            verbose=0,
        )
        if not isinstance(predicted_outputs, list):
            predicted_outputs = [predicted_outputs]

        debug_sequences: Dict[str, List[Any]] = {
            'input_scaled': _split_batch_sequences(x_scaled),
        }
        for stage_name, stage_output in zip(stage_names, predicted_outputs):
            debug_sequences[stage_name] = _split_batch_sequences(stage_output)
        return debug_sequences

    intermediate_model = tf.keras.Model(
        inputs=keras_model.input,
        outputs=[
            keras_model.layers[0].output,
            keras_model.layers[1].output,
            keras_model.layers[2].output,
        ],
    )
    lstm_hidden, dense_output, output_scaled = intermediate_model.predict(
        x_scaled,
        batch_size=max(1, batch_size),
        verbose=0,
    )

    recurrent_stage_name = 'gru_hidden' if model_type == 'grn' else 'lstm_hidden'

    return {
        'input_scaled': _split_batch_sequences(x_scaled),
        recurrent_stage_name: _split_batch_sequences(lstm_hidden),
        'dense_output': _split_batch_sequences(dense_output),
        'output_scaled': _split_batch_sequences(output_scaled),
    }


def _split_batch_sequences(array: np.ndarray) -> List[Any]:
    values = np.asarray(array, dtype=np.float64)
    if values.ndim == 2:
        values = values[..., np.newaxis]
    if values.ndim != 3:
        raise ValueError(f'中间输出维度非法，期望 3 维张量，实际 {values.ndim}')
    return [values[index].tolist() for index in range(values.shape[0])]


def _resolve_reference_weights_path(weights_json_path: Path) -> Path:
    weights_h5_path = weights_json_path.with_suffix('.h5')
    if weights_h5_path.exists():
        return weights_h5_path
    return weights_json_path


def _run_frikan_reference_from_spec(model_spec: FrikanModelSpec,
                                    x_input: np.ndarray,
                                    input_data_range: float,
                                    output_data_range: float,
                                    use_scaler: bool) -> tuple[np.ndarray, Dict[str, List[Any]]]:
    x_values = np.asarray(x_input, dtype=np.float64)
    if x_values.ndim != 3 or x_values.shape[-1] != 1:
        raise ValueError(f'FRIKAN 参考推理输入维度非法: {x_values.shape}')

    x_scaled = x_values.copy()
    if use_scaler and input_data_range != 0.0:
        x_scaled = x_scaled / input_data_range

    batch_size = int(x_scaled.shape[0])
    seq_len = int(x_scaled.shape[1])
    output_scaled = np.zeros((batch_size, seq_len, 1), dtype=np.float64)
    iir_output = np.zeros((batch_size, seq_len, model_spec.feature_count), dtype=np.float64)
    kan_outputs = [
        np.zeros((batch_size, seq_len, layer.output_dim), dtype=np.float64)
        for layer in model_spec.kan_layers
    ]
    layer_grids = [
        _build_densekan_grid(layer.grid_range, layer.grid_size, layer.spline_order)
        for layer in model_spec.kan_layers
    ]

    for batch_index in range(batch_size):
        x1 = np.zeros(model_spec.feature_count, dtype=np.float64)
        x2 = np.zeros(model_spec.feature_count, dtype=np.float64)
        y1 = np.zeros(model_spec.feature_count, dtype=np.float64)
        y2 = np.zeros(model_spec.feature_count, dtype=np.float64)

        for step_index in range(seq_len):
            scaled_sample = float(x_scaled[batch_index, step_index, 0])
            current_values = np.zeros(model_spec.feature_count, dtype=np.float64)

            for feature_index, iir_spec in enumerate(model_spec.iir_filters):
                response = (
                    iir_spec.b0 * scaled_sample
                    + iir_spec.b1 * x1[feature_index]
                    + iir_spec.b2 * x2[feature_index]
                    - iir_spec.a1 * y1[feature_index]
                    - iir_spec.a2 * y2[feature_index]
                )
                x2[feature_index] = x1[feature_index]
                x1[feature_index] = scaled_sample
                y2[feature_index] = y1[feature_index]
                y1[feature_index] = response
                current_values[feature_index] = response

            iir_output[batch_index, step_index] = current_values

            for layer_index, layer_spec in enumerate(model_spec.kan_layers):
                next_values = np.asarray(layer_spec.bias[:layer_spec.output_dim], dtype=np.float64).copy()
                layer_grid = layer_grids[layer_index]
                for output_index in range(layer_spec.output_dim):
                    for input_index in range(layer_spec.input_dim):
                        next_values[output_index] += _evaluate_frikan_edge_function(
                            x=float(current_values[input_index]),
                            grid=layer_grid,
                            spline_order=layer_spec.spline_order,
                            spline_kernel=np.asarray(layer_spec.spline_kernel[input_index], dtype=np.float64)[:, output_index],
                            scale_factor=float(layer_spec.scale_factor[input_index][output_index]),
                            basis_activation=layer_spec.basis_activation,
                            disable_basis_activation=layer_spec.disable_basis_activation,
                            use_symmetry=layer_spec.use_symmetry,
                            only_positive=layer_spec.only_positive,
                            use_even=layer_spec.use_even,
                        )
                kan_outputs[layer_index][batch_index, step_index] = next_values
                current_values = next_values

            output_scaled[batch_index, step_index, 0] = current_values[0]

    output_values = output_scaled.copy()
    if use_scaler:
        output_values *= output_data_range

    debug_sequences: Dict[str, List[Any]] = {
        'input_scaled': _split_batch_sequences(x_scaled),
        'iir_output': _split_batch_sequences(iir_output),
        'output_scaled': _split_batch_sequences(output_scaled),
    }
    for layer_index, layer_output in enumerate(kan_outputs):
        debug_sequences[f'kan_layer_{layer_index}'] = _split_batch_sequences(layer_output)

    return output_values, debug_sequences


def _normalize_project_path(model_project_name: str) -> str:
    normalized = model_project_name.replace('\\', '/').strip('/').strip()
    if not normalized.startswith('projects/'):
        normalized = f'projects/{normalized}'
    return normalized


def _apply_validation_dataset_overrides(config_obj: Any,
                                        dataset_config: Dict[str, Any]) -> None:
    source_project_config = dataset_config.get('source_project_config')
    if source_project_config:
        source_path = _resolve_path(source_project_config)
        with open(source_path, 'r', encoding='utf-8') as file_obj:
            source_config = json.load(file_obj)
        for field_name in DATASET_OVERRIDE_FIELDS:
            if field_name in source_config:
                setattr(config_obj, field_name, source_config[field_name])

    for field_name in DATASET_OVERRIDE_FIELDS:
        if field_name in dataset_config:
            setattr(config_obj, field_name, dataset_config[field_name])


def _resolve_path(path_str: str) -> Path:
    path = Path(str(path_str))
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _select_validation_dataset(dataset_origin: Any,
                               selection_config: Dict[str, Any]) -> tuple[Any, Dict[str, float]]:
    magnitudes = selection_config.get('magnitudes')
    frequencies = selection_config.get('frequencies')

    magn_indices = _resolve_requested_indices(magnitudes, dataset_origin.magn_list, 'magnitude')
    freq_indices = _resolve_requested_indices(frequencies, dataset_origin.freq_list, 'frequency')
    selected_dataset = dataset_origin.select(magn_indices=magn_indices, freq_indices=freq_indices)
    if selected_dataset.magn_num <= 0 or selected_dataset.freq_num <= 0:
        raise ValueError('筛选后数据集为空，请检查 magnitudes/frequencies 配置')

    return _crop_dataset_time_window(selected_dataset, selection_config)


def _resolve_requested_indices(requested_values: Optional[Sequence[Any]],
                               available_values: Sequence[Any],
                               label: str) -> Optional[List[int]]:
    if requested_values is None:
        return None
    if len(requested_values) == 0:
        raise ValueError(f'{label} 选择列表不能为空')

    indices: List[int] = []
    for requested in requested_values:
        requested_value = float(requested)
        matched_index: Optional[int] = None
        for index, candidate in enumerate(available_values):
            if abs(float(candidate) - requested_value) <= 1e-9:
                matched_index = index
                break
        if matched_index is None:
            raise ValueError(f'未在数据集中找到 {label}={requested_value}，可选值: {list(available_values)}')
        indices.append(matched_index)
    return indices


def _crop_dataset_time_window(dataset: Any,
                              selection_config: Dict[str, Any]) -> tuple[Any, Dict[str, float]]:
    total_points = int(dataset.output_ori.shape[2])
    sample_rate = float(dataset.fs)
    start_time_s = float(selection_config.get('start_time_s', 0.0) or 0.0)
    requested_end = selection_config.get('end_time_s')
    end_time_s = float(requested_end) if requested_end is not None else total_points / sample_rate

    start_idx = max(0, int(round(start_time_s * sample_rate)))
    end_idx = min(total_points, int(round(end_time_s * sample_rate)))
    if end_idx <= start_idx:
        raise ValueError('时间窗口非法，end_time_s 必须大于 start_time_s')

    cropped_dataset = dataset.select()
    cropped_dataset.inputs = dataset.inputs[:, :, start_idx:end_idx].copy()
    cropped_dataset.output_ori = dataset.output_ori[:, :, start_idx:end_idx].copy()
    cropped_dataset.output_tar = dataset.output_tar[:, :, start_idx:end_idx].copy()
    cropped_dataset.time_cliped_s = (end_idx - start_idx) / sample_rate

    return cropped_dataset, {
        'start_time_s': start_idx / sample_rate,
        'end_time_s': end_idx / sample_rate,
        'sample_count': end_idx - start_idx,
    }


def _load_requested_model_weights(model_engine: Any, weights_json_path: Path) -> Path:
    weights_h5_path = weights_json_path.with_suffix('.h5')
    if weights_h5_path.exists():
        model_engine.model_comp.load_weights(str(weights_h5_path))
        return weights_h5_path

    if weights_json_path.name.startswith('best_val'):
        model_engine.load_val_best_weights()
        return Path(model_engine.model_comp.best_val_weights_file)
    if weights_json_path.name.startswith('best'):
        model_engine.load_best_weights()
        return Path(model_engine.model_comp.best_weights_file)

    raise FileNotFoundError(f'无法定位与 {weights_json_path} 对应的 .h5 权重文件')


def _build_validation_records(selected_dataset: Any,
                              tf_output_2d: np.ndarray) -> List[ValidationRecord]:
    records: List[ValidationRecord] = []
    row_index = 0
    for mag_index, magnitude in enumerate(selected_dataset.magn_list):
        for freq_index, frequency in enumerate(selected_dataset.freq_list):
            input_sequence = np.asarray(selected_dataset.output_ori[mag_index, freq_index], dtype=np.float64)
            target_sequence = np.asarray(selected_dataset.output_tar[mag_index, freq_index], dtype=np.float64)
            tf_output_sequence = np.asarray(tf_output_2d[row_index], dtype=np.float64)
            record_id = f'mag{float(magnitude):g}_freq{float(frequency):g}'
            records.append(ValidationRecord(
                record_id=record_id,
                magnitude=float(magnitude),
                frequency=float(frequency),
                input_sequence=[[float(value)] for value in input_sequence.tolist()],
                target_sequence=target_sequence.tolist(),
                tf_output_sequence=tf_output_sequence.tolist(),
            ))
            row_index += 1
    return records


def _detect_model_type(model_project_name: str,
                       model_dir: Path,
                       weights_json_path: Path) -> str:
    project_config = _load_project_config(model_dir)
    if project_config:
        use_model = str(project_config.get('use_model', '')).strip().upper()
        if use_model == 'FRIKAN':
            return 'frikan'
        if use_model == 'LSTM':
            return 'lstm'
        if use_model == 'LSTMTRANSFORMER':
            return 'lstm_transformer'
        if use_model in {'GRN', 'GRU'}:
            return 'grn'

    with open(weights_json_path, 'r', encoding='utf-8') as file_obj:
        weights = json.load(file_obj)

    weight_names = [str(item.get('name', '')).replace('\\', '/') for item in weights]
    if any('lstm_cell/' in name for name in weight_names):
        if any('transformer_mha_' in name for name in weight_names):
            return 'lstm_transformer'
        return 'lstm'
    if any('gru_cell/' in name for name in weight_names):
        return 'grn'
    if any('dense_kan' in name for name in weight_names) and any('simple_rnn' in name for name in weight_names):
        return 'frikan'

    raise ValueError(f'无法自动识别 qemu-c-inference 模型类型: {model_project_name}')


def _load_model_spec(model_project_name: str,
                     model_dir: Path,
                     weights_json_path: Path,
                     model_type: str,
                     generation_config: Dict[str, Any]) -> Any:
    if model_type == 'lstm':
        return _load_lstm_model_spec(model_project_name, weights_json_path)
    if model_type == 'lstm_transformer':
        return _load_lstm_transformer_model_spec(model_project_name, model_dir, weights_json_path)
    if model_type == 'grn':
        return _load_grn_model_spec(model_project_name, weights_json_path)
    if model_type == 'frikan':
        return _load_frikan_model_spec(
            model_project_name=model_project_name,
            model_dir=model_dir,
            weights_json_path=weights_json_path,
            lut_points=int(generation_config.get('lut_points', 513)),
            lut_interpolation=bool(generation_config.get('lut_interpolation', False)),
        )
    raise ValueError(f'不支持的模型类型: {model_type}')


def _load_lstm_model_spec(model_project_name: str,
                          weights_json_path: Path) -> LstmModelSpec:
    with open(weights_json_path, 'r', encoding='utf-8') as file_obj:
        weights = json.load(file_obj)

    lstm_kernel = _find_weight_entry(weights, 'lstm_cell/kernel')
    lstm_recurrent_kernel = _find_weight_entry(weights, 'lstm_cell/recurrent_kernel')
    lstm_bias = _find_weight_entry(weights, 'lstm_cell/bias')
    dense_kernel = _find_weight_entry(weights, 'dense/kernel')
    dense_bias = _find_weight_entry(weights, 'dense/bias')
    output_kernel = _find_weight_entry(weights, 'dense_1/kernel')
    output_bias = _find_weight_entry(weights, 'dense_1/bias')

    input_dim = int(lstm_kernel['shape'][0])
    lstm_units = int(lstm_recurrent_kernel['shape'][0])
    dense_units = int(dense_bias['shape'][0])
    output_units = int(output_bias['shape'][0])

    if int(lstm_kernel['shape'][1]) != lstm_units * 4:
        raise ValueError('LSTM kernel 形状非法，第二维必须等于 4 * lstm_units')
    if int(lstm_recurrent_kernel['shape'][1]) != lstm_units * 4:
        raise ValueError('LSTM recurrent kernel 形状非法，第二维必须等于 4 * lstm_units')
    if int(lstm_bias['shape'][0]) != lstm_units * 4:
        raise ValueError('LSTM bias 形状非法，长度必须等于 4 * lstm_units')
    if int(dense_kernel['shape'][0]) != lstm_units:
        raise ValueError('Dense kernel 输入维度必须与 LSTM units 一致')
    if int(output_kernel['shape'][0]) != dense_units:
        raise ValueError('输出层 kernel 输入维度必须与 dense units 一致')
    if output_units != 1:
        raise ValueError(f'当前仅支持单输出 LSTM，实际 output_units={output_units}')

    return LstmModelSpec(
        model_project_name=model_project_name,
        weights_json_path=weights_json_path,
        input_dim=input_dim,
        lstm_units=lstm_units,
        dense_units=dense_units,
        output_units=output_units,
        lstm_kernel=_to_float_matrix(lstm_kernel['value']),
        lstm_recurrent_kernel=_to_float_matrix(lstm_recurrent_kernel['value']),
        lstm_bias=_to_float_vector(lstm_bias['value']),
        dense_kernel=_to_float_matrix(dense_kernel['value']),
        dense_bias=_to_float_vector(dense_bias['value']),
        output_kernel=_to_float_matrix(output_kernel['value']),
        output_bias=_to_float_vector(output_bias['value']),
    )


def _load_grn_model_spec(model_project_name: str,
                         weights_json_path: Path) -> GrnModelSpec:
    with open(weights_json_path, 'r', encoding='utf-8') as file_obj:
        weights = json.load(file_obj)

    gru_kernel = _find_weight_entry(weights, 'gru_cell/kernel')
    gru_recurrent_kernel = _find_weight_entry(weights, 'gru_cell/recurrent_kernel')
    gru_bias = _find_weight_entry(weights, 'gru_cell/bias')
    dense_kernel = _find_weight_entry(weights, 'dense/kernel')
    dense_bias = _find_weight_entry(weights, 'dense/bias')
    output_kernel = _find_weight_entry(weights, 'dense_1/kernel')
    output_bias = _find_weight_entry(weights, 'dense_1/bias')

    input_dim = int(gru_kernel['shape'][0])
    gru_units = int(gru_recurrent_kernel['shape'][0])
    dense_units = int(dense_bias['shape'][0])
    output_units = int(output_bias['shape'][0])

    if int(gru_kernel['shape'][1]) != gru_units * 3:
        raise ValueError('GRU kernel 形状非法，第二维必须等于 3 * gru_units')
    if int(gru_recurrent_kernel['shape'][1]) != gru_units * 3:
        raise ValueError('GRU recurrent kernel 形状非法，第二维必须等于 3 * gru_units')

    bias_values = np.asarray(gru_bias['value'], dtype=np.float64)
    if bias_values.shape == (2, gru_units * 3):
        gru_input_bias = bias_values[0]
        gru_recurrent_bias = bias_values[1]
    elif bias_values.shape == (gru_units * 3,):
        gru_input_bias = bias_values
        gru_recurrent_bias = np.zeros_like(gru_input_bias)
    else:
        raise ValueError(f'GRU bias 形状非法: {bias_values.shape}')

    if int(dense_kernel['shape'][0]) != gru_units:
        raise ValueError('Dense kernel 输入维度必须与 GRU units 一致')
    if int(output_kernel['shape'][0]) != dense_units:
        raise ValueError('输出层 kernel 输入维度必须与 dense units 一致')
    if output_units != 1:
        raise ValueError(f'当前仅支持单输出 GRN，实际 output_units={output_units}')

    return GrnModelSpec(
        model_project_name=model_project_name,
        weights_json_path=weights_json_path,
        input_dim=input_dim,
        gru_units=gru_units,
        dense_units=dense_units,
        output_units=output_units,
        gru_kernel=_to_float_matrix(gru_kernel['value']),
        gru_recurrent_kernel=_to_float_matrix(gru_recurrent_kernel['value']),
        gru_input_bias=_to_float_vector(gru_input_bias.tolist()),
        gru_recurrent_bias=_to_float_vector(gru_recurrent_bias.tolist()),
        dense_kernel=_to_float_matrix(dense_kernel['value']),
        dense_bias=_to_float_vector(dense_bias['value']),
        output_kernel=_to_float_matrix(output_kernel['value']),
        output_bias=_to_float_vector(output_bias['value']),
    )


def _load_lstm_transformer_model_spec(model_project_name: str,
                                      model_dir: Path,
                                      weights_json_path: Path) -> LstmTransformerModelSpec:
    with open(weights_json_path, 'r', encoding='utf-8') as file_obj:
        weights = json.load(file_obj)

    project_config = _load_project_config(model_dir)
    model_subcfg = project_config.get('model_subcfg', {}) if isinstance(project_config.get('model_subcfg', {}), dict) else {}
    attention_pool_size = int(model_subcfg.get('attention_pool_size', 1))
    if attention_pool_size <= 0:
        raise ValueError(f'attention_pool_size 必须大于 0，实际 {attention_pool_size}')

    post_dense_activation = str(model_subcfg.get('dense_activation', 'relu')).strip().lower()

    lstm_kernel = _find_weight_entry(weights, 'lstm_backbone/lstm_cell/kernel')
    lstm_recurrent_kernel = _find_weight_entry(weights, 'lstm_backbone/lstm_cell/recurrent_kernel')
    lstm_bias = _find_weight_entry(weights, 'lstm_backbone/lstm_cell/bias')

    input_dim = int(lstm_kernel['shape'][0])
    lstm_units = int(lstm_recurrent_kernel['shape'][0])
    if int(lstm_kernel['shape'][1]) != lstm_units * 4:
        raise ValueError('LSTMTransformer backbone kernel 形状非法，第二维必须等于 4 * lstm_units')
    if int(lstm_recurrent_kernel['shape'][1]) != lstm_units * 4:
        raise ValueError('LSTMTransformer backbone recurrent kernel 形状非法，第二维必须等于 4 * lstm_units')
    if int(lstm_bias['shape'][0]) != lstm_units * 4:
        raise ValueError('LSTMTransformer backbone bias 形状非法，长度必须等于 4 * lstm_units')

    layer_indices = sorted({
        int(match.group(1))
        for item in weights
        for match in [re.fullmatch(r'transformer_mha_(\d+)/query/kernel:0', str(item.get('name', '')).replace('\\', '/'))]
        if match is not None
    })
    if not layer_indices:
        raise ValueError('LSTMTransformer 权重中未找到任何 transformer_mha query/kernel')

    configured_layers = project_config.get('model_subcfg', {}).get('transformer_layers') if isinstance(project_config.get('model_subcfg', {}), dict) else None
    if configured_layers is not None and int(configured_layers) != len(layer_indices):
        raise ValueError(
            f'LSTMTransformer transformer_layers 与权重层数不一致，配置={configured_layers}，权重={len(layer_indices)}'
        )

    transformer_num_heads: Optional[int] = None
    transformer_key_dim: Optional[int] = None
    transformer_ff_dim: Optional[int] = None
    layers: List[LstmTransformerLayerSpec] = []

    for layer_index in layer_indices:
        query_kernel = _find_weight_entry(weights, f'transformer_mha_{layer_index}/query/kernel')
        query_bias = _find_weight_entry(weights, f'transformer_mha_{layer_index}/query/bias')
        key_kernel = _find_weight_entry(weights, f'transformer_mha_{layer_index}/key/kernel')
        key_bias = _find_weight_entry(weights, f'transformer_mha_{layer_index}/key/bias')
        value_kernel = _find_weight_entry(weights, f'transformer_mha_{layer_index}/value/kernel')
        value_bias = _find_weight_entry(weights, f'transformer_mha_{layer_index}/value/bias')
        attention_output_kernel = _find_weight_entry(weights, f'transformer_mha_{layer_index}/attention_output/kernel')
        attention_output_bias = _find_weight_entry(weights, f'transformer_mha_{layer_index}/attention_output/bias')
        ln_attn_gamma = _find_weight_entry(weights, f'transformer_ln_attn_{layer_index}/gamma')
        ln_attn_beta = _find_weight_entry(weights, f'transformer_ln_attn_{layer_index}/beta')
        ffn_expand_kernel = _find_weight_entry(weights, f'transformer_ffn_expand_{layer_index}/kernel')
        ffn_expand_bias = _find_weight_entry(weights, f'transformer_ffn_expand_{layer_index}/bias')
        ffn_project_kernel = _find_weight_entry(weights, f'transformer_ffn_project_{layer_index}/kernel')
        ffn_project_bias = _find_weight_entry(weights, f'transformer_ffn_project_{layer_index}/bias')
        ln_ffn_gamma = _find_weight_entry(weights, f'transformer_ln_ffn_{layer_index}/gamma')
        ln_ffn_beta = _find_weight_entry(weights, f'transformer_ln_ffn_{layer_index}/beta')

        current_heads = int(query_kernel['shape'][1])
        current_key_dim = int(query_kernel['shape'][2])
        current_ff_dim = int(ffn_expand_kernel['shape'][1])
        if transformer_num_heads is None:
            transformer_num_heads = current_heads
        elif transformer_num_heads != current_heads:
            raise ValueError(f'LSTMTransformer 各层 num_heads 不一致，期望 {transformer_num_heads}，实际 {current_heads}')
        if transformer_key_dim is None:
            transformer_key_dim = current_key_dim
        elif transformer_key_dim != current_key_dim:
            raise ValueError(f'LSTMTransformer 各层 key_dim 不一致，期望 {transformer_key_dim}，实际 {current_key_dim}')
        if transformer_ff_dim is None:
            transformer_ff_dim = current_ff_dim
        elif transformer_ff_dim != current_ff_dim:
            raise ValueError(f'LSTMTransformer 各层 ff_dim 不一致，期望 {transformer_ff_dim}，实际 {current_ff_dim}')

        if int(query_kernel['shape'][0]) != lstm_units:
            raise ValueError('LSTMTransformer query/kernel 输入维度必须等于 lstm_units')
        if list(query_bias['shape']) != [current_heads, current_key_dim]:
            raise ValueError(f'LSTMTransformer query/bias 形状非法: {query_bias["shape"]}')
        if list(key_kernel['shape']) != [lstm_units, current_heads, current_key_dim]:
            raise ValueError(f'LSTMTransformer key/kernel 形状非法: {key_kernel["shape"]}')
        if list(key_bias['shape']) != [current_heads, current_key_dim]:
            raise ValueError(f'LSTMTransformer key/bias 形状非法: {key_bias["shape"]}')
        if list(value_kernel['shape']) != [lstm_units, current_heads, current_key_dim]:
            raise ValueError(f'LSTMTransformer value/kernel 形状非法: {value_kernel["shape"]}')
        if list(value_bias['shape']) != [current_heads, current_key_dim]:
            raise ValueError(f'LSTMTransformer value/bias 形状非法: {value_bias["shape"]}')
        if list(attention_output_kernel['shape']) != [current_heads, current_key_dim, lstm_units]:
            raise ValueError(f'LSTMTransformer attention_output/kernel 形状非法: {attention_output_kernel["shape"]}')
        if list(attention_output_bias['shape']) != [lstm_units]:
            raise ValueError(f'LSTMTransformer attention_output/bias 形状非法: {attention_output_bias["shape"]}')
        if list(ln_attn_gamma['shape']) != [lstm_units] or list(ln_attn_beta['shape']) != [lstm_units]:
            raise ValueError(f'LSTMTransformer ln_attn 形状非法: gamma={ln_attn_gamma["shape"]}, beta={ln_attn_beta["shape"]}')
        if list(ffn_expand_kernel['shape']) != [lstm_units, current_ff_dim]:
            raise ValueError(f'LSTMTransformer ffn_expand/kernel 形状非法: {ffn_expand_kernel["shape"]}')
        if list(ffn_expand_bias['shape']) != [current_ff_dim]:
            raise ValueError(f'LSTMTransformer ffn_expand/bias 形状非法: {ffn_expand_bias["shape"]}')
        if list(ffn_project_kernel['shape']) != [current_ff_dim, lstm_units]:
            raise ValueError(f'LSTMTransformer ffn_project/kernel 形状非法: {ffn_project_kernel["shape"]}')
        if list(ffn_project_bias['shape']) != [lstm_units]:
            raise ValueError(f'LSTMTransformer ffn_project/bias 形状非法: {ffn_project_bias["shape"]}')
        if list(ln_ffn_gamma['shape']) != [lstm_units] or list(ln_ffn_beta['shape']) != [lstm_units]:
            raise ValueError(f'LSTMTransformer ln_ffn 形状非法: gamma={ln_ffn_gamma["shape"]}, beta={ln_ffn_beta["shape"]}')

        layers.append(LstmTransformerLayerSpec(
            query_kernel=_to_float_tensor3(query_kernel['value']),
            query_bias=_to_float_matrix(query_bias['value']),
            key_kernel=_to_float_tensor3(key_kernel['value']),
            key_bias=_to_float_matrix(key_bias['value']),
            value_kernel=_to_float_tensor3(value_kernel['value']),
            value_bias=_to_float_matrix(value_bias['value']),
            attention_output_kernel=_to_float_tensor3(attention_output_kernel['value']),
            attention_output_bias=_to_float_vector(attention_output_bias['value']),
            ln_attn_gamma=_to_float_vector(ln_attn_gamma['value']),
            ln_attn_beta=_to_float_vector(ln_attn_beta['value']),
            ffn_expand_kernel=_to_float_matrix(ffn_expand_kernel['value']),
            ffn_expand_bias=_to_float_vector(ffn_expand_bias['value']),
            ffn_project_kernel=_to_float_matrix(ffn_project_kernel['value']),
            ffn_project_bias=_to_float_vector(ffn_project_bias['value']),
            ln_ffn_gamma=_to_float_vector(ln_ffn_gamma['value']),
            ln_ffn_beta=_to_float_vector(ln_ffn_beta['value']),
        ))

    if transformer_num_heads is None or transformer_key_dim is None or transformer_ff_dim is None:
        raise ValueError('LSTMTransformer 未能从权重中解析 attention 规格')

    post_dense_kernel_entry = _find_weight_entry_optional(weights, 'post_dense/kernel')
    post_dense_bias_entry = _find_weight_entry_optional(weights, 'post_dense/bias')
    if post_dense_kernel_entry is not None:
        if post_dense_bias_entry is None:
            raise ValueError('LSTMTransformer post_dense 权重不完整，缺少 bias')
        post_dense_units = int(post_dense_bias_entry['shape'][0])
        if list(post_dense_kernel_entry['shape']) != [lstm_units, post_dense_units]:
            raise ValueError(f'LSTMTransformer post_dense/kernel 形状非法: {post_dense_kernel_entry["shape"]}')
        post_dense_kernel = _to_float_matrix(post_dense_kernel_entry['value'])
        post_dense_bias = _to_float_vector(post_dense_bias_entry['value'])
        output_input_units = post_dense_units
    else:
        post_dense_units = 0
        post_dense_kernel = _zero_matrix(lstm_units, 1)
        post_dense_bias = [0.0]
        output_input_units = lstm_units

    output_kernel = _find_weight_entry_exact_name(weights, 'output/kernel:0')
    output_bias = _find_weight_entry_exact_name(weights, 'output/bias:0')
    output_units = int(output_bias['shape'][0])
    if list(output_kernel['shape']) != [output_input_units, output_units]:
        raise ValueError(f'LSTMTransformer output/kernel 形状非法: {output_kernel["shape"]}')
    if output_units != 1:
        raise ValueError(f'当前仅支持单输出 LSTMTransformer，实际 output_units={output_units}')

    return LstmTransformerModelSpec(
        model_project_name=model_project_name,
        weights_json_path=weights_json_path,
        input_dim=input_dim,
        lstm_units=lstm_units,
        transformer_num_heads=transformer_num_heads,
        transformer_key_dim=transformer_key_dim,
        transformer_ff_dim=transformer_ff_dim,
        attention_pool_size=attention_pool_size,
        lstm_kernel=_to_float_matrix(lstm_kernel['value']),
        lstm_recurrent_kernel=_to_float_matrix(lstm_recurrent_kernel['value']),
        lstm_bias=_to_float_vector(lstm_bias['value']),
        layers=layers,
        post_dense_units=post_dense_units,
        post_dense_activation=post_dense_activation,
        post_dense_kernel=post_dense_kernel,
        post_dense_bias=post_dense_bias,
        output_input_units=output_input_units,
        output_units=output_units,
        output_kernel=_to_float_matrix(output_kernel['value']),
        output_bias=_to_float_vector(output_bias['value']),
    )


def _load_frikan_model_spec(model_project_name: str,
                            model_dir: Path,
                            weights_json_path: Path,
                            lut_points: int,
                            lut_interpolation: bool) -> FrikanModelSpec:
    with open(weights_json_path, 'r', encoding='utf-8') as file_obj:
        weights = json.load(file_obj)

    project_config: Dict[str, Any] = {}
    config_path = model_dir / 'config.json'
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as file_obj:
            project_config = json.load(file_obj)

    model_subcfg = project_config.get('model_subcfg', {}) if isinstance(project_config.get('model_subcfg', {}), dict) else {}
    use_symmetry = bool(model_subcfg.get('use_symmetry', True))
    only_positive = bool(model_subcfg.get('only_positive', True))
    use_even = bool(model_subcfg.get('use_even', False))
    basis_activation = str(project_config.get('basis_activation', 'silu'))
    disable_basis_activation = bool(project_config.get('disable_basis_activation', True))

    simple_rnn_kernel_entries: List[Dict[str, Any]] = []
    simple_rnn_recurrent_entries: List[Dict[str, Any]] = []
    for item in weights:
        name = str(item.get('name', '')).replace('\\', '/')
        if re.fullmatch(r'simple_rnn(?:_\d+)?/simple_rnn_cell(?:_\d+)?/kernel:0', name):
            simple_rnn_kernel_entries.append(item)
        elif re.fullmatch(r'simple_rnn(?:_\d+)?/simple_rnn_cell(?:_\d+)?/recurrent_kernel:0', name):
            simple_rnn_recurrent_entries.append(item)

    simple_rnn_kernel_entries.sort(key=lambda item: _simple_rnn_sort_key(str(item.get('name', ''))))
    simple_rnn_recurrent_entries.sort(key=lambda item: _simple_rnn_sort_key(str(item.get('name', ''))))
    if not simple_rnn_kernel_entries or len(simple_rnn_kernel_entries) != len(simple_rnn_recurrent_entries):
        raise ValueError('FRIKAN 权重中 simple_rnn kernel / recurrent_kernel 数量不匹配')

    iir_filters: List[FrikanIirSpec] = []
    for kernel_entry, recurrent_entry in zip(simple_rnn_kernel_entries, simple_rnn_recurrent_entries):
        kernel_values = np.asarray(kernel_entry['value'], dtype=np.float64)
        recurrent_values = np.asarray(recurrent_entry['value'], dtype=np.float64)
        if kernel_values.shape != (1, 4):
            raise ValueError(f'FRIKAN simple_rnn kernel 形状非法: {kernel_values.shape}')
        if recurrent_values.shape != (4, 4):
            raise ValueError(f'FRIKAN simple_rnn recurrent_kernel 形状非法: {recurrent_values.shape}')
        iir_filters.append(FrikanIirSpec(
            b0=float(kernel_values[0, 0]),
            b1=float(recurrent_values[2, 0]),
            b2=float(recurrent_values[3, 0]),
            a1=float(-recurrent_values[0, 0]),
            a2=float(-recurrent_values[1, 0]),
        ))

    spline_entries: List[Dict[str, Any]] = []
    for item in weights:
        name = str(item.get('name', '')).replace('\\', '/')
        if re.fullmatch(r'dense_kan(?:_\d+)?/spline_kernel:0', name):
            spline_entries.append(item)

    spline_entries.sort(key=lambda item: _dense_kan_sort_key(str(item.get('name', ''))))
    if not spline_entries:
        raise ValueError('FRIKAN 权重中未找到任何 DenseKAN spline_kernel')

    dense_kan_layers: List[FrikanKanLayerSpec] = []
    for spline_entry in spline_entries:
        layer_name = str(spline_entry.get('name', '')).replace('\\', '/').split('/')[0]
        kernel = np.asarray(spline_entry['value'], dtype=np.float64)
        if kernel.ndim != 3:
            raise ValueError(f'{layer_name} spline_kernel 维度非法: {kernel.shape}')

        bias_entry = _find_weight_entry(weights, f'{layer_name}/bias')
        bias = np.asarray(bias_entry['value'], dtype=np.float64).reshape(-1)

        scale_factor_entry = _find_weight_entry_optional(weights, f'{layer_name}/scale_factor')
        if scale_factor_entry is not None:
            scale_factor = np.asarray(scale_factor_entry['value'], dtype=np.float64)
        else:
            scale_factor = np.ones((kernel.shape[0], kernel.shape[2]), dtype=np.float64)

        if scale_factor.shape != (kernel.shape[0], kernel.shape[2]):
            raise ValueError(
                f'{layer_name} scale_factor 形状非法，期望 {(kernel.shape[0], kernel.shape[2])}，实际 {scale_factor.shape}'
            )

        config = spline_entry.get('config', {}) or {}
        grid_size = int(config.get('grid_size', kernel.shape[1]))
        spline_order = int(config.get('spline_order', 0))
        grid_range = [float(value) for value in config.get('grid_range', [0.0, 1.0])]
        support_min, support_max = _compute_kan_lut_support(grid_range, grid_size, spline_order, use_symmetry)
        lut_values = _build_frikan_lut_values(
            spline_kernel=kernel,
            scale_factor=scale_factor,
            grid_range=grid_range,
            grid_size=grid_size,
            spline_order=spline_order,
            lut_points=lut_points,
            basis_activation=basis_activation,
            disable_basis_activation=disable_basis_activation,
            use_symmetry=use_symmetry,
            only_positive=only_positive,
            use_even=use_even,
            support_min=support_min,
            support_max=support_max,
        )

        dense_kan_layers.append(FrikanKanLayerSpec(
            name=layer_name,
            input_dim=int(kernel.shape[0]),
            output_dim=int(kernel.shape[2]),
            grid_size=grid_size,
            spline_order=spline_order,
            grid_range=grid_range,
            spline_kernel=kernel.tolist(),
            bias=bias.tolist(),
            scale_factor=scale_factor.tolist(),
            use_symmetry=use_symmetry,
            only_positive=only_positive,
            use_even=use_even,
            basis_activation=basis_activation,
            disable_basis_activation=disable_basis_activation,
            lut_support_min=support_min,
            lut_support_max=support_max,
            lut_values=lut_values,
        ))

    if dense_kan_layers[-1].output_dim != 1:
        raise ValueError(f'当前仅支持单输出 FRIKAN，实际 output_dim={dense_kan_layers[-1].output_dim}')

    return FrikanModelSpec(
        model_project_name=model_project_name,
        weights_json_path=weights_json_path,
        input_dim=1,
        feature_count=len(iir_filters),
        kan_layers=dense_kan_layers,
        iir_filters=iir_filters,
        output_units=1,
        lut_points=lut_points,
        lut_interpolation=lut_interpolation,
        use_symmetry=use_symmetry,
        use_even=use_even,
    )


def _find_weight_entry(weights: Iterable[Dict[str, Any]], fragment: str) -> Dict[str, Any]:
    for item in weights:
        name = str(item.get('name', '')).replace('\\', '/')
        if fragment in name:
            return item
    raise KeyError(f'未找到权重项: {fragment}')


def _find_weight_entry_optional(weights: Iterable[Dict[str, Any]], fragment: str) -> Optional[Dict[str, Any]]:
    for item in weights:
        name = str(item.get('name', '')).replace('\\', '/')
        if fragment in name:
            return item
    return None


def _find_weight_entry_by_suffix(weights: Iterable[Dict[str, Any]], suffix: str) -> Dict[str, Any]:
    normalized_suffix = str(suffix).replace('\\', '/')
    for item in weights:
        name = str(item.get('name', '')).replace('\\', '/')
        if name.endswith(normalized_suffix):
            return item
    raise KeyError(f'未找到权重项后缀: {suffix}')


def _find_weight_entry_exact_name(weights: Iterable[Dict[str, Any]], exact_name: str) -> Dict[str, Any]:
    normalized_name = str(exact_name).replace('\\', '/')
    for item in weights:
        name = str(item.get('name', '')).replace('\\', '/')
        if name == normalized_name:
            return item
    raise KeyError(f'未找到精确权重项: {exact_name}')


def _simple_rnn_sort_key(weight_name: str) -> int:
    match = re.match(r'simple_rnn(?:_(\d+))?/', weight_name.replace('\\', '/'))
    if not match or match.group(1) is None:
        return 0
    return int(match.group(1)) + 1


def _dense_kan_sort_key(weight_name: str) -> int:
    match = re.match(r'dense_kan(?:_(\d+))?/', weight_name.replace('\\', '/'))
    if not match:
        return 10_000
    if match.group(1) is None:
        return 10_000
    return int(match.group(1))


def _compute_kan_lut_support(grid_range: Sequence[float],
                             grid_size: int,
                             spline_order: int,
                             use_symmetry: bool) -> tuple[float, float]:
    bound = float(grid_range[1]) - float(grid_range[0])
    expansion = 0.0 if grid_size <= 0 else (spline_order * bound / grid_size)
    support_min = float(grid_range[0]) - expansion
    support_max = float(grid_range[1]) + expansion
    if use_symmetry:
        support_min = max(0.0, float(grid_range[0]))
    return support_min, support_max


def _build_frikan_lut_values(spline_kernel: np.ndarray,
                             scale_factor: np.ndarray,
                             grid_range: Sequence[float],
                             grid_size: int,
                             spline_order: int,
                             lut_points: int,
                             basis_activation: str,
                             disable_basis_activation: bool,
                             use_symmetry: bool,
                             only_positive: bool,
                             use_even: bool,
                             support_min: float,
                             support_max: float) -> List[List[List[float]]]:
    if lut_points < 2:
        raise ValueError(f'FRIKAN LUT 点数必须大于等于 2，实际 {lut_points}')

    grid = _build_densekan_grid(grid_range, grid_size, spline_order)
    sample_axis = np.linspace(support_min, support_max, lut_points, dtype=np.float64)
    lut_values: List[List[List[float]]] = []

    for input_index in range(int(spline_kernel.shape[0])):
        per_input: List[List[float]] = []
        for output_index in range(int(spline_kernel.shape[2])):
            kernel_values = np.asarray(spline_kernel[input_index, :, output_index], dtype=np.float64)
            edge_scale = float(scale_factor[input_index, output_index])
            sampled = [
                _evaluate_frikan_edge_function(
                    x=float(sample_value),
                    grid=grid,
                    spline_order=spline_order,
                    spline_kernel=kernel_values,
                    scale_factor=edge_scale,
                    basis_activation=basis_activation,
                    disable_basis_activation=disable_basis_activation,
                    use_symmetry=use_symmetry,
                    only_positive=only_positive,
                    use_even=use_even,
                )
                for sample_value in sample_axis
            ]
            per_input.append(sampled)
        lut_values.append(per_input)

    return lut_values


def _build_densekan_grid(grid_range: Sequence[float],
                         grid_size: int,
                         spline_order: int) -> np.ndarray:
    bound = float(grid_range[1]) - float(grid_range[0])
    return np.linspace(
        float(grid_range[0]) - spline_order * bound / grid_size,
        float(grid_range[1]) + spline_order * bound / grid_size,
        grid_size + 2 * spline_order + 1,
        dtype=np.float64,
    )


def _evaluate_frikan_edge_function(x: float,
                                   grid: np.ndarray,
                                   spline_order: int,
                                   spline_kernel: np.ndarray,
                                   scale_factor: float,
                                   basis_activation: str,
                                   disable_basis_activation: bool,
                                   use_symmetry: bool,
                                   only_positive: bool,
                                   use_even: bool) -> float:
    eval_x = abs(x) if use_symmetry else x
    basis_values = _calc_bspline_values(eval_x, grid, spline_order)
    kernel_values = np.asarray(spline_kernel, dtype=np.float64)
    if use_symmetry and only_positive:
        kernel_values = np.abs(kernel_values)

    spline_output = float(np.dot(basis_values, kernel_values))
    if use_symmetry and not use_even:
        spline_output *= 1.0 if x >= 0.0 else -1.0

    if disable_basis_activation:
        basis_output = 0.0
    else:
        basis_output = _apply_basis_activation(x, basis_activation)

    return (spline_output + basis_output) * scale_factor


def _calc_bspline_values(x: float,
                         grid: np.ndarray,
                         spline_order: int) -> np.ndarray:
    bases = np.asarray([
        1.0 if grid[index] <= x < grid[index + 1] else 0.0
        for index in range(len(grid) - 1)
    ], dtype=np.float64)

    active_length = int(bases.shape[0])
    for order_index in range(1, spline_order + 1):
        active_length -= 1
        next_bases = np.zeros_like(bases)
        for base_index in range(active_length):
            left_term = 0.0
            right_term = 0.0
            left_denominator = grid[base_index + order_index] - grid[base_index]
            right_denominator = grid[base_index + order_index + 1] - grid[base_index + 1]
            if left_denominator != 0.0:
                left_term = ((x - grid[base_index]) / left_denominator) * bases[base_index]
            if right_denominator != 0.0:
                right_term = ((grid[base_index + order_index + 1] - x) / right_denominator) * bases[base_index + 1]
            next_bases[base_index] = left_term + right_term
        bases = next_bases

    return bases[:active_length]


def _apply_basis_activation(x: float, basis_activation: str) -> float:
    normalized = basis_activation.strip().lower()
    if normalized in {'linear', 'identity', 'none'}:
        return x
    if normalized == 'relu':
        return x if x > 0.0 else 0.0
    if normalized == 'tanh':
        return float(np.tanh(x))
    if normalized == 'sigmoid':
        return float(1.0 / (1.0 + np.exp(-x)))
    if normalized in {'silu', 'swish'}:
        sigmoid = 1.0 / (1.0 + np.exp(-x))
        return float(x * sigmoid)
    raise ValueError(f'当前 qemu-c-inference 尚未支持 basis_activation={basis_activation}')


def _to_float_matrix(values: Sequence[Sequence[Any]]) -> List[List[float]]:
    return [[float(value) for value in row] for row in values]


def _to_float_tensor3(values: Sequence[Sequence[Sequence[Any]]]) -> List[List[List[float]]]:
    return [
        [
            [float(value) for value in row]
            for row in matrix
        ]
        for matrix in values
    ]


def _to_float_vector(values: Sequence[Any]) -> List[float]:
    return [float(value) for value in values]


def _zero_matrix(rows: int, cols: int) -> List[List[float]]:
    return [[0.0 for _ in range(cols)] for _ in range(rows)]


def _copy_runtime_template(filename: str, target: Path) -> None:
    source = QEMU_HELLO_TEMPLATE_DIR / filename
    if not source.exists():
        raise FileNotFoundError(f'QEMU 模板文件不存在: {source}')
    target.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')


def _resolve_activation_code(activation: str) -> int:
    normalized = str(activation).strip().lower()
    if normalized in {'linear', 'identity', 'none'}:
        return 0
    if normalized == 'relu':
        return 1
    if normalized == 'tanh':
        return 2
    if normalized == 'sigmoid':
        return 3
    if normalized in {'silu', 'swish'}:
        return 4
    raise ValueError(f'当前 qemu-c-inference 尚未支持 activation={activation}')


def _render_model_data_header(model_spec: LstmModelSpec,
                              benchmark_config: Dict[str, Any],
                              validation_artifacts: ValidationArtifacts) -> str:
    validation_input = [record.input_sequence for record in validation_artifacts.records]
    lines = [
        '#ifndef GENERATED_LSTM_MODEL_DATA_H',
        '#define GENERATED_LSTM_MODEL_DATA_H',
        '',
        '#include <stdint.h>',
        '',
        'typedef float port_float;',
        '',
        f'#define LSTM_INPUT_DIM {model_spec.input_dim}u',
        f'#define LSTM_UNITS {model_spec.lstm_units}u',
        f'#define DENSE_UNITS {model_spec.dense_units}u',
        f'#define OUTPUT_UNITS {model_spec.output_units}u',
        f'#define BENCHMARK_ITERATIONS {int(benchmark_config["iterations"])}u',
        f'#define BENCHMARK_REPEAT_RUNS {int(benchmark_config["repeat_runs"])}u',
        f'#define BENCHMARK_RESET_STATE_EACH_RUN {1 if benchmark_config.get("reset_state_each_run", True) else 0}u',
        f'#define VALIDATION_RECORD_COUNT {validation_artifacts.record_count}u',
        f'#define VALIDATION_SEQ_LEN {validation_artifacts.seq_len}u',
        '',
        f'#define SCALER_INPUT_DATA_RANGE {_format_c_float(validation_artifacts.input_data_range)}',
        f'#define SCALER_OUTPUT_DATA_RANGE {_format_c_float(validation_artifacts.output_data_range)}',
        '',
        f'static const port_float validation_input[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN][LSTM_INPUT_DIM] = {_render_initializer(validation_input)};',
        '',
        f'static const port_float lstm_kernel[LSTM_INPUT_DIM][LSTM_UNITS * 4u] = {_render_initializer(model_spec.lstm_kernel)};',
        '',
        f'static const port_float lstm_recurrent_kernel[LSTM_UNITS][LSTM_UNITS * 4u] = {_render_initializer(model_spec.lstm_recurrent_kernel)};',
        '',
        f'static const port_float lstm_bias[LSTM_UNITS * 4u] = {_render_initializer(model_spec.lstm_bias)};',
        '',
        f'static const port_float dense_kernel[LSTM_UNITS][DENSE_UNITS] = {_render_initializer(model_spec.dense_kernel)};',
        '',
        f'static const port_float dense_bias[DENSE_UNITS] = {_render_initializer(model_spec.dense_bias)};',
        '',
        f'static const port_float output_kernel[DENSE_UNITS][OUTPUT_UNITS] = {_render_initializer(model_spec.output_kernel)};',
        '',
        f'static const port_float output_bias[OUTPUT_UNITS] = {_render_initializer(model_spec.output_bias)};',
        '',
        '#endif',
        '',
    ]
    return '\n'.join(lines)


def _render_lstm_transformer_model_data_header(model_spec: LstmTransformerModelSpec,
                                               benchmark_config: Dict[str, Any],
                                               validation_artifacts: ValidationArtifacts) -> str:
    validation_input = [record.input_sequence for record in validation_artifacts.records]
    attention_context_len = max(1, math.ceil(validation_artifacts.seq_len / model_spec.attention_pool_size))
    has_post_dense = model_spec.post_dense_units > 0
    post_dense_units = model_spec.post_dense_units if has_post_dense else 1
    attention_scale = 1.0 / math.sqrt(float(model_spec.transformer_key_dim))

    lines = [
        '#ifndef GENERATED_LSTM_TRANSFORMER_MODEL_DATA_H',
        '#define GENERATED_LSTM_TRANSFORMER_MODEL_DATA_H',
        '',
        '#include <stdint.h>',
        '',
        'typedef float port_float;',
        '',
        '#define ACT_LINEAR 0u',
        '#define ACT_RELU 1u',
        '#define ACT_TANH 2u',
        '#define ACT_SIGMOID 3u',
        '#define ACT_SILU 4u',
        '',
        f'#define LSTM_INPUT_DIM {model_spec.input_dim}u',
        f'#define LSTM_UNITS {model_spec.lstm_units}u',
        f'#define TRANSFORMER_LAYER_COUNT {model_spec.transformer_layer_count}u',
        f'#define TRANSFORMER_HEADS {model_spec.transformer_num_heads}u',
        f'#define TRANSFORMER_KEY_DIM {model_spec.transformer_key_dim}u',
        f'#define TRANSFORMER_FF_DIM {model_spec.transformer_ff_dim}u',
        f'#define ATTENTION_POOL_SIZE {model_spec.attention_pool_size}u',
        f'#define TRANSFORMER_CONTEXT_LEN {attention_context_len}u',
        f'#define ATTENTION_SCALE {_format_c_float(attention_scale)}',
        f'#define TRANSFORMER_LAYER_NORM_EPSILON {_format_c_float(model_spec.layer_norm_epsilon)}',
        f'#define HAS_POST_DENSE {1 if has_post_dense else 0}u',
        f'#define POST_DENSE_INPUT_UNITS {model_spec.lstm_units}u',
        f'#define POST_DENSE_UNITS {post_dense_units}u',
        f'#define POST_DENSE_ACTIVATION {_resolve_activation_code(model_spec.post_dense_activation)}u',
        f'#define OUTPUT_INPUT_UNITS {model_spec.output_input_units}u',
        f'#define OUTPUT_UNITS {model_spec.output_units}u',
        f'#define BENCHMARK_ITERATIONS {int(benchmark_config["iterations"])}u',
        f'#define BENCHMARK_REPEAT_RUNS {int(benchmark_config["repeat_runs"])}u',
        f'#define BENCHMARK_RESET_STATE_EACH_RUN {1 if benchmark_config.get("reset_state_each_run", True) else 0}u',
        f'#define VALIDATION_RECORD_COUNT {validation_artifacts.record_count}u',
        f'#define VALIDATION_SEQ_LEN {validation_artifacts.seq_len}u',
        '',
        f'#define SCALER_INPUT_DATA_RANGE {_format_c_float(validation_artifacts.input_data_range)}',
        f'#define SCALER_OUTPUT_DATA_RANGE {_format_c_float(validation_artifacts.output_data_range)}',
        '',
        f'static const port_float validation_input[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN][LSTM_INPUT_DIM] = {_render_initializer(validation_input)};',
        '',
        f'static const port_float lstm_kernel[LSTM_INPUT_DIM][LSTM_UNITS * 4u] = {_render_initializer(model_spec.lstm_kernel)};',
        '',
        f'static const port_float lstm_recurrent_kernel[LSTM_UNITS][LSTM_UNITS * 4u] = {_render_initializer(model_spec.lstm_recurrent_kernel)};',
        '',
        f'static const port_float lstm_bias[LSTM_UNITS * 4u] = {_render_initializer(model_spec.lstm_bias)};',
        '',
        f'static const port_float transformer_query_kernel[TRANSFORMER_LAYER_COUNT][LSTM_UNITS][TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM] = {_render_initializer([layer.query_kernel for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_query_bias[TRANSFORMER_LAYER_COUNT][TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM] = {_render_initializer([layer.query_bias for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_key_kernel[TRANSFORMER_LAYER_COUNT][LSTM_UNITS][TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM] = {_render_initializer([layer.key_kernel for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_key_bias[TRANSFORMER_LAYER_COUNT][TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM] = {_render_initializer([layer.key_bias for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_value_kernel[TRANSFORMER_LAYER_COUNT][LSTM_UNITS][TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM] = {_render_initializer([layer.value_kernel for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_value_bias[TRANSFORMER_LAYER_COUNT][TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM] = {_render_initializer([layer.value_bias for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_attention_output_kernel[TRANSFORMER_LAYER_COUNT][TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM][LSTM_UNITS] = {_render_initializer([layer.attention_output_kernel for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_attention_output_bias[TRANSFORMER_LAYER_COUNT][LSTM_UNITS] = {_render_initializer([layer.attention_output_bias for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_ln_attn_gamma[TRANSFORMER_LAYER_COUNT][LSTM_UNITS] = {_render_initializer([layer.ln_attn_gamma for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_ln_attn_beta[TRANSFORMER_LAYER_COUNT][LSTM_UNITS] = {_render_initializer([layer.ln_attn_beta for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_ffn_expand_kernel[TRANSFORMER_LAYER_COUNT][LSTM_UNITS][TRANSFORMER_FF_DIM] = {_render_initializer([layer.ffn_expand_kernel for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_ffn_expand_bias[TRANSFORMER_LAYER_COUNT][TRANSFORMER_FF_DIM] = {_render_initializer([layer.ffn_expand_bias for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_ffn_project_kernel[TRANSFORMER_LAYER_COUNT][TRANSFORMER_FF_DIM][LSTM_UNITS] = {_render_initializer([layer.ffn_project_kernel for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_ffn_project_bias[TRANSFORMER_LAYER_COUNT][LSTM_UNITS] = {_render_initializer([layer.ffn_project_bias for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_ln_ffn_gamma[TRANSFORMER_LAYER_COUNT][LSTM_UNITS] = {_render_initializer([layer.ln_ffn_gamma for layer in model_spec.layers])};',
        '',
        f'static const port_float transformer_ln_ffn_beta[TRANSFORMER_LAYER_COUNT][LSTM_UNITS] = {_render_initializer([layer.ln_ffn_beta for layer in model_spec.layers])};',
        '',
        f'static const port_float post_dense_kernel[POST_DENSE_INPUT_UNITS][POST_DENSE_UNITS] = {_render_initializer(model_spec.post_dense_kernel)};',
        '',
        f'static const port_float post_dense_bias[POST_DENSE_UNITS] = {_render_initializer(model_spec.post_dense_bias)};',
        '',
        f'static const port_float output_kernel[OUTPUT_INPUT_UNITS][OUTPUT_UNITS] = {_render_initializer(model_spec.output_kernel)};',
        '',
        f'static const port_float output_bias[OUTPUT_UNITS] = {_render_initializer(model_spec.output_bias)};',
        '',
        '#endif',
        '',
    ]
    return '\n'.join(lines)


def _render_grn_model_data_header(model_spec: GrnModelSpec,
                                  benchmark_config: Dict[str, Any],
                                  validation_artifacts: ValidationArtifacts) -> str:
    validation_input = [record.input_sequence for record in validation_artifacts.records]
    lines = [
        '#ifndef GENERATED_GRN_MODEL_DATA_H',
        '#define GENERATED_GRN_MODEL_DATA_H',
        '',
        '#include <stdint.h>',
        '',
        'typedef float port_float;',
        '',
        f'#define GRU_INPUT_DIM {model_spec.input_dim}u',
        f'#define GRU_UNITS {model_spec.gru_units}u',
        f'#define DENSE_UNITS {model_spec.dense_units}u',
        f'#define OUTPUT_UNITS {model_spec.output_units}u',
        f'#define BENCHMARK_ITERATIONS {int(benchmark_config["iterations"])}u',
        f'#define BENCHMARK_REPEAT_RUNS {int(benchmark_config["repeat_runs"])}u',
        f'#define BENCHMARK_RESET_STATE_EACH_RUN {1 if benchmark_config.get("reset_state_each_run", True) else 0}u',
        f'#define VALIDATION_RECORD_COUNT {validation_artifacts.record_count}u',
        f'#define VALIDATION_SEQ_LEN {validation_artifacts.seq_len}u',
        '',
        f'#define SCALER_INPUT_DATA_RANGE {_format_c_float(validation_artifacts.input_data_range)}',
        f'#define SCALER_OUTPUT_DATA_RANGE {_format_c_float(validation_artifacts.output_data_range)}',
        '',
        f'static const port_float validation_input[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN][GRU_INPUT_DIM] = {_render_initializer(validation_input)};',
        '',
        f'static const port_float gru_kernel[GRU_INPUT_DIM][GRU_UNITS * 3u] = {_render_initializer(model_spec.gru_kernel)};',
        '',
        f'static const port_float gru_recurrent_kernel[GRU_UNITS][GRU_UNITS * 3u] = {_render_initializer(model_spec.gru_recurrent_kernel)};',
        '',
        f'static const port_float gru_input_bias[GRU_UNITS * 3u] = {_render_initializer(model_spec.gru_input_bias)};',
        '',
        f'static const port_float gru_recurrent_bias[GRU_UNITS * 3u] = {_render_initializer(model_spec.gru_recurrent_bias)};',
        '',
        f'static const port_float dense_kernel[GRU_UNITS][DENSE_UNITS] = {_render_initializer(model_spec.dense_kernel)};',
        '',
        f'static const port_float dense_bias[DENSE_UNITS] = {_render_initializer(model_spec.dense_bias)};',
        '',
        f'static const port_float output_kernel[DENSE_UNITS][OUTPUT_UNITS] = {_render_initializer(model_spec.output_kernel)};',
        '',
        f'static const port_float output_bias[OUTPUT_UNITS] = {_render_initializer(model_spec.output_bias)};',
        '',
        '#endif',
        '',
    ]
    return '\n'.join(lines)


def _render_initializer(values: Any, indent: int = 0) -> str:
    if isinstance(values, (list, tuple)):
        if values and isinstance(values[0], (list, tuple)):
            inner_indent = '    ' * (indent + 1)
            closing_indent = '    ' * indent
            rendered_rows = []
            for item in values:
                rendered_rows.append(f'{inner_indent}{_render_initializer(item, indent + 1)}')
            return '{\n' + ',\n'.join(rendered_rows) + f'\n{closing_indent}' + '}'
        return '{ ' + ', '.join(_format_c_float(float(item)) for item in values) + ' }'
    return _format_c_float(float(values))


def _format_c_float(value: float) -> str:
    return f'{value:.8f}f'


def _compute_frikan_lut_index_params(support_min: float,
                                     support_max: float,
                                     lut_points: int) -> tuple[float, float]:
    if lut_points < 2:
        raise ValueError(f'FRIKAN LUT 点数必须大于等于 2，实际 {lut_points}')

    support_span = float(support_max) - float(support_min)
    if support_span <= 0.0:
        raise ValueError(
            f'FRIKAN LUT 支撑区间非法: support_min={support_min}, support_max={support_max}'
        )

    scale = float(lut_points - 1) / support_span
    offset = -float(support_min) * scale
    return scale, offset


def _render_frikan_model_data_header(model_spec: FrikanModelSpec,
                                     benchmark_config: Dict[str, Any],
                                     validation_artifacts: ValidationArtifacts) -> str:
    validation_input = [record.input_sequence for record in validation_artifacts.records]
    max_layer_inputs = max(layer.input_dim for layer in model_spec.kan_layers)
    max_layer_outputs = max(layer.output_dim for layer in model_spec.kan_layers)

    padded_bias = [
        _pad_float_vector(layer.bias, max_layer_outputs, 0.0)
        for layer in model_spec.kan_layers
    ]
    padded_luts = [
        _pad_frikan_lut_layer(layer.lut_values, max_layer_inputs, max_layer_outputs, model_spec.lut_points)
        for layer in model_spec.kan_layers
    ]
    lines = [
        '#ifndef GENERATED_FRIKAN_MODEL_DATA_H',
        '#define GENERATED_FRIKAN_MODEL_DATA_H',
        '',
        '#include <stdint.h>',
        '',
        'typedef float port_float;',
        '',
        f'#define FRIKAN_INPUT_DIM {model_spec.input_dim}u',
        f'#define FRIKAN_FEATURES {model_spec.feature_count}u',
        f'#define FRIKAN_KAN_LAYER_COUNT {len(model_spec.kan_layers)}u',
        f'#define FRIKAN_MAX_LAYER_INPUTS {max_layer_inputs}u',
        f'#define FRIKAN_MAX_LAYER_OUTPUTS {max_layer_outputs}u',
        f'#define FRIKAN_LUT_POINTS {model_spec.lut_points}u',
        f'#define FRIKAN_LUT_INTERPOLATION {1 if model_spec.lut_interpolation else 0}u',
        f'#define FRIKAN_USE_SYMMETRY {1 if model_spec.use_symmetry else 0}u',
        f'#define FRIKAN_USE_EVEN {1 if model_spec.use_even else 0}u',
        f'#define OUTPUT_UNITS {model_spec.output_units}u',
        f'#define BENCHMARK_ITERATIONS {int(benchmark_config["iterations"])}u',
        f'#define BENCHMARK_REPEAT_RUNS {int(benchmark_config["repeat_runs"])}u',
        f'#define BENCHMARK_RESET_STATE_EACH_RUN {1 if benchmark_config.get("reset_state_each_run", True) else 0}u',
        f'#define VALIDATION_RECORD_COUNT {validation_artifacts.record_count}u',
        f'#define VALIDATION_SEQ_LEN {validation_artifacts.seq_len}u',
        '',
        f'#define SCALER_INPUT_DATA_RANGE {_format_c_float(validation_artifacts.input_data_range)}',
        f'#define SCALER_OUTPUT_DATA_RANGE {_format_c_float(validation_artifacts.output_data_range)}',
        '',
        f'static const port_float validation_input[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN][FRIKAN_INPUT_DIM] = {_render_initializer(validation_input)};',
        '',
        f'static const uint16_t frikan_layer_input_dims[FRIKAN_KAN_LAYER_COUNT] = {_render_uint_initializer([layer.input_dim for layer in model_spec.kan_layers])};',
        '',
        f'static const uint16_t frikan_layer_output_dims[FRIKAN_KAN_LAYER_COUNT] = {_render_uint_initializer([layer.output_dim for layer in model_spec.kan_layers])};',
        '',
        f'static const port_float frikan_iir_b0[FRIKAN_FEATURES] = {_render_initializer([item.b0 for item in model_spec.iir_filters])};',
        '',
        f'static const port_float frikan_iir_b1[FRIKAN_FEATURES] = {_render_initializer([item.b1 for item in model_spec.iir_filters])};',
        '',
        f'static const port_float frikan_iir_b2[FRIKAN_FEATURES] = {_render_initializer([item.b2 for item in model_spec.iir_filters])};',
        '',
        f'static const port_float frikan_iir_a1[FRIKAN_FEATURES] = {_render_initializer([item.a1 for item in model_spec.iir_filters])};',
        '',
        f'static const port_float frikan_iir_a2[FRIKAN_FEATURES] = {_render_initializer([item.a2 for item in model_spec.iir_filters])};',
        '',
        f'static const port_float frikan_layer_bias[FRIKAN_KAN_LAYER_COUNT][FRIKAN_MAX_LAYER_OUTPUTS] = {_render_initializer(padded_bias)};',
        '',
        f'static const port_float frikan_layer_lut[FRIKAN_KAN_LAYER_COUNT][FRIKAN_MAX_LAYER_INPUTS][FRIKAN_MAX_LAYER_OUTPUTS][FRIKAN_LUT_POINTS] = {_render_initializer(padded_luts)};',
        '',
        '#endif',
        '',
    ]
    return '\n'.join(lines)


def _pad_float_vector(values: Sequence[float],
                      target_length: int,
                      fill_value: float) -> List[float]:
    padded = [float(value) for value in values]
    while len(padded) < target_length:
        padded.append(fill_value)
    return padded


def _pad_frikan_lut_layer(lut_values: Sequence[Sequence[Sequence[float]]],
                          max_inputs: int,
                          max_outputs: int,
                          lut_points: int) -> List[List[List[float]]]:
    padded_inputs: List[List[List[float]]] = []
    for input_index in range(max_inputs):
        padded_outputs: List[List[float]] = []
        if input_index < len(lut_values):
            layer_input = lut_values[input_index]
        else:
            layer_input = []
        for output_index in range(max_outputs):
            if output_index < len(layer_input):
                padded_outputs.append(_pad_float_vector(layer_input[output_index], lut_points, 0.0))
            else:
                padded_outputs.append([0.0] * lut_points)
        padded_inputs.append(padded_outputs)
    return padded_inputs


def _render_uint_initializer(values: Sequence[int], suffix: str = 'u') -> str:
    return '{ ' + ', '.join(f'{int(value)}{suffix}' for value in values) + ' }'


def _render_frikan_forward_body(model_spec: FrikanModelSpec,
                                include_debug_kan_output: bool = True) -> str:
    lines: List[str] = []

    for layer_index, layer_spec in enumerate(model_spec.kan_layers):
        lines.append('    {')
        for output_index in range(layer_spec.output_dim):
            accumulator_name = f'layer_{layer_index}_out_{output_index}'
            lines.append(
                f'        port_float {accumulator_name} = frikan_layer_bias[{layer_index}u][{output_index}u];'
            )
            for input_index in range(layer_spec.input_dim):
                lines.append(
                    f'        {accumulator_name} += FRIKAN_LUT_LOOKUP_LAYER_{layer_index}('
                    f'frikan_layer_lut[{layer_index}u][{input_index}u][{output_index}u], '
                    f'current_values[{input_index}u]);'
                )

        if include_debug_kan_output:
            lines.append('        if (debug_kan_step != 0) {')
            for output_index in range(layer_spec.output_dim):
                lines.append(
                    f'            debug_kan_step[{layer_index}u][{output_index}u] = '
                    f'layer_{layer_index}_out_{output_index};'
                )
            lines.append('        }')

        for output_index in range(layer_spec.output_dim):
            lines.append(
                f'        current_values[{output_index}u] = layer_{layer_index}_out_{output_index};'
            )
        lines.append('    }')

    return '\n'.join(lines)


def _render_frikan_main_c(model_spec: FrikanModelSpec) -> str:
    template = r"""#include <stdint.h>

#include "model_data.h"

#define RCC_BASE 0x40023800u
#define DEMCR (*(volatile uint32_t *)0xE000EDFCu)
#define DWT_CTRL (*(volatile uint32_t *)0xE0001000u)
#define DWT_CYCCNT (*(volatile uint32_t *)0xE0001004u)

#define USART1_BASE 0x40011000u
#define RCC_APB2ENR (*(volatile uint32_t *)(RCC_BASE + 0x44u))
#define USART1_SR (*(volatile uint32_t *)(USART1_BASE + 0x00u))
#define USART1_DR (*(volatile uint32_t *)(USART1_BASE + 0x04u))
#define USART1_BRR (*(volatile uint32_t *)(USART1_BASE + 0x08u))
#define USART1_CR1 (*(volatile uint32_t *)(USART1_BASE + 0x0Cu))

#define RCC_APB2ENR_USART1EN (1u << 4)
#define USART_SR_TXE (1u << 7)
#define USART_CR1_TE (1u << 3)
#define USART_CR1_UE (1u << 13)
#define DEMCR_TRCENA (1u << 24)
#define DWT_CTRL_CYCCNTENA (1u << 0)

static port_float validation_output[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN];
static port_float debug_scaled_input[VALIDATION_SEQ_LEN];
static port_float debug_iir_output[VALIDATION_SEQ_LEN][FRIKAN_FEATURES];
static port_float debug_kan_output[FRIKAN_KAN_LAYER_COUNT][VALIDATION_SEQ_LEN][FRIKAN_MAX_LAYER_OUTPUTS];
static port_float debug_output_scaled[VALIDATION_SEQ_LEN];

static void uart_init(void)
{
    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;
    USART1_BRR = 0x05B2u;
    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;
}

static void uart_putc(char ch)
{
    while ((USART1_SR & USART_SR_TXE) == 0u) {
    }

    USART1_DR = (uint32_t)ch;
}

static void uart_puts(const char *message)
{
    while (*message != '\0') {
        if (*message == '\n') {
            uart_putc('\r');
        }

        uart_putc(*message++);
    }
}

static void uart_put_u32(uint32_t value)
{
    char buffer[11];
    uint32_t index = 0u;

    if (value == 0u) {
        uart_putc('0');
        return;
    }

    while (value > 0u && index < (uint32_t)sizeof(buffer)) {
        buffer[index++] = (char)('0' + (value % 10u));
        value /= 10u;
    }

    while (index > 0u) {
        uart_putc(buffer[--index]);
    }
}

static void uart_put_fixed6(port_float value)
{
    int32_t scaled = (int32_t)(value * 1000000.0f);
    int32_t abs_scaled = scaled;
    int32_t integer_part;
    int32_t fraction;
    int32_t divisor = 100000;

    if (scaled < 0) {
        uart_putc('-');
        abs_scaled = -scaled;
    }

    integer_part = abs_scaled / 1000000;
    fraction = abs_scaled % 1000000;

    uart_put_u32((uint32_t)integer_part);
    uart_putc('.');
    while (divisor > 0) {
        uart_putc((char)('0' + ((fraction / divisor) % 10)));
        divisor /= 10;
    }
}

static void uart_put_matrix_rows(const port_float *values,
                                 uint32_t row_count,
                                 uint32_t column_count)
{
    uint32_t row_index;
    for (row_index = 0u; row_index < row_count; ++row_index) {
        uint32_t column_index;
        if (row_index > 0u) {
            uart_putc(';');
        }
        for (column_index = 0u; column_index < column_count; ++column_index) {
            if (column_index > 0u) {
                uart_putc(',');
            }
            uart_put_fixed6(values[row_index * column_count + column_index]);
        }
    }
}

static void dwt_init(void)
{
    DEMCR |= DEMCR_TRCENA;
    DWT_CYCCNT = 0u;
    DWT_CTRL |= DWT_CTRL_CYCCNTENA;
}

static uint32_t dwt_read_cycles(void)
{
    return DWT_CYCCNT;
}

static uint32_t dwt_is_counting(void)
{
    volatile uint32_t spin;
    uint32_t before;
    uint32_t after;

    dwt_init();
    before = dwt_read_cycles();
    for (spin = 0u; spin < 64u; ++spin) {
        __asm volatile ("nop");
    }
    after = dwt_read_cycles();
    return after > before ? 1u : 0u;
}

static void zero_buffer(port_float *buffer, uint32_t length)
{
    uint32_t index;
    for (index = 0u; index < length; ++index) {
        buffer[index] = 0.0f;
    }
}

static port_float scale_input(port_float value)
{
    if (SCALER_INPUT_DATA_RANGE == 0.0f) {
        return value;
    }
    return value / SCALER_INPUT_DATA_RANGE;
}

static port_float inverse_scale_output(port_float value)
{
    return value * SCALER_OUTPUT_DATA_RANGE;
}

#define FRIKAN_LUT_LAST_INDEX (FRIKAN_LUT_POINTS - 1u)
#define FRIKAN_LUT_LAST_INDEX_FLOAT ((port_float)(FRIKAN_LUT_POINTS - 1u))

#if FRIKAN_USE_SYMMETRY
#define FRIKAN_LUT_PREPARE_VALUE(raw_value) (((raw_value) < 0.0f) ? -(raw_value) : (raw_value))
#else
#define FRIKAN_LUT_PREPARE_VALUE(raw_value) (raw_value)
#endif

#define FRIKAN_LUT_MAP_INDEX(lookup_value, lut_scale, lut_offset) (((lookup_value) * (lut_scale)) + (lut_offset))

__FRIKAN_LUT_LAYER_FUNCTIONS__

__FRIKAN_LUT_LAYER_MACROS__

static void frikan_iir_reset(port_float x1[FRIKAN_FEATURES],
                             port_float x2[FRIKAN_FEATURES],
                             port_float y1[FRIKAN_FEATURES],
                             port_float y2[FRIKAN_FEATURES])
{
    zero_buffer(x1, FRIKAN_FEATURES);
    zero_buffer(x2, FRIKAN_FEATURES);
    zero_buffer(y1, FRIKAN_FEATURES);
    zero_buffer(y2, FRIKAN_FEATURES);
}

static void frikan_forward_step(port_float input_value,
                                port_float x1[FRIKAN_FEATURES],
                                port_float x2[FRIKAN_FEATURES],
                                port_float y1[FRIKAN_FEATURES],
                                port_float y2[FRIKAN_FEATURES],
                                port_float *output_scaled_value,
                                port_float *debug_scaled_input_value,
                                port_float debug_iir_step[FRIKAN_FEATURES],
                                port_float debug_kan_step[FRIKAN_KAN_LAYER_COUNT][FRIKAN_MAX_LAYER_OUTPUTS],
                                port_float *output_value)
{
    uint32_t feature_index;
    port_float scaled_input = scale_input(input_value);
    port_float current_values[FRIKAN_MAX_LAYER_INPUTS];

    if (debug_scaled_input_value != 0) {
        *debug_scaled_input_value = scaled_input;
    }

    if (debug_iir_step != 0) {
        for (feature_index = 0u; feature_index < FRIKAN_FEATURES; ++feature_index) {
            port_float response = frikan_iir_b0[feature_index] * scaled_input
                + frikan_iir_b1[feature_index] * x1[feature_index]
                + frikan_iir_b2[feature_index] * x2[feature_index]
                - frikan_iir_a1[feature_index] * y1[feature_index]
                - frikan_iir_a2[feature_index] * y2[feature_index];

            x2[feature_index] = x1[feature_index];
            x1[feature_index] = scaled_input;
            y2[feature_index] = y1[feature_index];
            y1[feature_index] = response;
            current_values[feature_index] = response;
            debug_iir_step[feature_index] = response;
        }
    } else {
        for (feature_index = 0u; feature_index < FRIKAN_FEATURES; ++feature_index) {
            port_float response = frikan_iir_b0[feature_index] * scaled_input
                + frikan_iir_b1[feature_index] * x1[feature_index]
                + frikan_iir_b2[feature_index] * x2[feature_index]
                - frikan_iir_a1[feature_index] * y1[feature_index]
                - frikan_iir_a2[feature_index] * y2[feature_index];

            x2[feature_index] = x1[feature_index];
            x1[feature_index] = scaled_input;
            y2[feature_index] = y1[feature_index];
            y1[feature_index] = response;
            current_values[feature_index] = response;
        }
    }

__FRIKAN_FORWARD_BODY__

    if (output_scaled_value != 0) {
        *output_scaled_value = current_values[0u];
    }
    *output_value = inverse_scale_output(current_values[0u]);
}

static void run_validation_record(const port_float sequence[VALIDATION_SEQ_LEN][FRIKAN_INPUT_DIM],
                                  port_float output_sequence[VALIDATION_SEQ_LEN],
                                  uint32_t reset_state_each_run,
                                  port_float x1[FRIKAN_FEATURES],
                                  port_float x2[FRIKAN_FEATURES],
                                  port_float y1[FRIKAN_FEATURES],
                                  port_float y2[FRIKAN_FEATURES],
                                  port_float debug_scaled_input_buffer[VALIDATION_SEQ_LEN],
                                  port_float debug_iir_output_buffer[VALIDATION_SEQ_LEN][FRIKAN_FEATURES],
                                  port_float debug_kan_output_buffer[FRIKAN_KAN_LAYER_COUNT][VALIDATION_SEQ_LEN][FRIKAN_MAX_LAYER_OUTPUTS],
                                  port_float debug_output_scaled_buffer[VALIDATION_SEQ_LEN])
{
    uint32_t step;

    if (reset_state_each_run != 0u) {
        frikan_iir_reset(x1, x2, y1, y2);
    }

    for (step = 0u; step < VALIDATION_SEQ_LEN; ++step) {
        port_float step_kan_debug[FRIKAN_KAN_LAYER_COUNT][FRIKAN_MAX_LAYER_OUTPUTS];
        uint32_t layer_index;
        uint32_t output_index;

        for (layer_index = 0u; layer_index < FRIKAN_KAN_LAYER_COUNT; ++layer_index) {
            for (output_index = 0u; output_index < FRIKAN_MAX_LAYER_OUTPUTS; ++output_index) {
                step_kan_debug[layer_index][output_index] = 0.0f;
            }
        }

        frikan_forward_step(
            sequence[step][0u],
            x1,
            x2,
            y1,
            y2,
            debug_output_scaled_buffer != 0 ? &debug_output_scaled_buffer[step] : 0,
            debug_scaled_input_buffer != 0 ? &debug_scaled_input_buffer[step] : 0,
            debug_iir_output_buffer != 0 ? debug_iir_output_buffer[step] : 0,
            debug_kan_output_buffer != 0 ? step_kan_debug : 0,
            &output_sequence[step]
        );

        if (debug_kan_output_buffer != 0) {
            for (layer_index = 0u; layer_index < FRIKAN_KAN_LAYER_COUNT; ++layer_index) {
                for (output_index = 0u; output_index < FRIKAN_MAX_LAYER_OUTPUTS; ++output_index) {
                    debug_kan_output_buffer[layer_index][step][output_index] = step_kan_debug[layer_index][output_index];
                }
            }
        }
    }
}

static void run_benchmark_record(const port_float sequence[VALIDATION_SEQ_LEN][FRIKAN_INPUT_DIM],
                                 uint32_t reset_state_each_run,
                                 port_float x1[FRIKAN_FEATURES],
                                 port_float x2[FRIKAN_FEATURES],
                                 port_float y1[FRIKAN_FEATURES],
                                 port_float y2[FRIKAN_FEATURES],
                                 port_float *output_value)
{
    uint32_t step;
    port_float current_output = 0.0f;

    if (reset_state_each_run != 0u) {
        frikan_iir_reset(x1, x2, y1, y2);
    }

    for (step = 0u; step < VALIDATION_SEQ_LEN; ++step) {
        frikan_forward_step(
            sequence[step][0u],
            x1,
            x2,
            y1,
            y2,
            0,
            0,
            0,
            0,
            &current_output
        );
    }

    *output_value = current_output;
}

int main(void)
{
    uint32_t iteration;
    uint32_t record_index;
    uint32_t step_index;
    uint32_t layer_index;
    uint32_t dwt_supported;
    uint32_t start_cycles;
    uint32_t end_cycles;
    uint32_t total_cycles = 0u;
    port_float x1[FRIKAN_FEATURES];
    port_float x2[FRIKAN_FEATURES];
    port_float y1[FRIKAN_FEATURES];
    port_float y2[FRIKAN_FEATURES];
    port_float output_value = 0.0f;

    uart_init();
    dwt_supported = dwt_is_counting();
    frikan_iir_reset(x1, x2, y1, y2);

    if (dwt_supported != 0u) {
        start_cycles = dwt_read_cycles();
    }

    for (iteration = 0u; iteration < BENCHMARK_ITERATIONS; ++iteration) {
        for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
            run_benchmark_record(
                validation_input[record_index],
                BENCHMARK_RESET_STATE_EACH_RUN,
                x1,
                x2,
                y1,
                y2,
                &output_value
            );
        }
    }

    if (dwt_supported != 0u) {
        end_cycles = dwt_read_cycles();
        total_cycles = end_cycles - start_cycles;
    }

    uart_puts("FRIKAN_QEMU_VALIDATION\n");
    uart_puts("iterations=");
    uart_put_u32(BENCHMARK_ITERATIONS);
    uart_puts("\nrecord_count=");
    uart_put_u32(VALIDATION_RECORD_COUNT);
    uart_puts("\nseq_len=");
    uart_put_u32(VALIDATION_SEQ_LEN);
    uart_puts("\nfeature_count=");
    uart_put_u32(FRIKAN_FEATURES);
    uart_puts("\nkan_layer_count=");
    uart_put_u32(FRIKAN_KAN_LAYER_COUNT);
    uart_puts("\ndwt_supported=");
    uart_put_u32(dwt_supported);
    uart_puts("\ntimer_source=");
    uart_puts(dwt_supported != 0u ? "dwt" : "host_elapsed");
    if (dwt_supported != 0u) {
        uart_puts("\nmeasurement_unit=");
        uart_puts("cycles");
        uart_puts("\nmeasurement_total=");
        uart_put_u32(total_cycles);
        uart_puts("\nmeasurement_per_iter=");
        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));
        uart_puts("\ncycles_total=");
        uart_put_u32(total_cycles);
        uart_puts("\ncycles_per_iter=");
        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));
    }
    uart_puts("\noutput=");
    uart_put_fixed6(output_value);
    uart_puts("\n");
    uart_puts("benchmark_complete=1\n");

    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
        frikan_iir_reset(x1, x2, y1, y2);
        run_validation_record(
            validation_input[record_index],
            validation_output[record_index],
            0u,
            x1,
            x2,
            y1,
            y2,
            debug_scaled_input,
            debug_iir_output,
            debug_kan_output,
            debug_output_scaled
        );
    }

    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
        uart_puts("validation_record_");
        uart_put_u32(record_index);
        uart_puts("=");
        for (step_index = 0u; step_index < VALIDATION_SEQ_LEN; ++step_index) {
            if (step_index > 0u) {
                uart_putc(',');
            }
            uart_put_fixed6(validation_output[record_index][step_index]);
        }
        uart_puts("\n");

        uart_puts("validation_input_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_scaled_input[0u], VALIDATION_SEQ_LEN, 1u);
        uart_puts("\n");

        uart_puts("validation_iir_output_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_iir_output[0u][0u], VALIDATION_SEQ_LEN, FRIKAN_FEATURES);
        uart_puts("\n");

        for (layer_index = 0u; layer_index < FRIKAN_KAN_LAYER_COUNT; ++layer_index) {
            uart_puts("validation_kan_layer_");
            uart_put_u32(layer_index);
            uart_putc('_');
            uart_put_u32(record_index);
            uart_puts("=");
            uart_put_matrix_rows(
                &debug_kan_output[layer_index][0u][0u],
                VALIDATION_SEQ_LEN,
                (uint32_t)frikan_layer_output_dims[layer_index]
            );
            uart_puts("\n");
        }

        uart_puts("validation_output_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_output_scaled[0u], VALIDATION_SEQ_LEN, 1u);
        uart_puts("\n");
    }

    uart_puts("validation_complete=1\n");

    while (1) {
    }
}
"""
    lut_layer_function_lines: List[str] = []
    lut_layer_macro_lines: List[str] = []
    for layer_index, layer_spec in enumerate(model_spec.kan_layers):
        lut_scale, lut_offset = _compute_frikan_lut_index_params(
            layer_spec.lut_support_min,
            layer_spec.lut_support_max,
            model_spec.lut_points,
        )
        lut_layer_function_lines.extend([
            f'#define FRIKAN_LUT_SCALE_LAYER_{layer_index} {_format_c_float(lut_scale)}',
            f'#define FRIKAN_LUT_OFFSET_LAYER_{layer_index} {_format_c_float(lut_offset)}',
            '',
            f'static __attribute__((noinline)) port_float frikan_lut_lookup_fast_layer_{layer_index}(',
            '    const port_float lut_values[FRIKAN_LUT_POINTS],',
            '    port_float raw_value)',
            '{',
            '    port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);',
            '    port_float mapped_index = FRIKAN_LUT_MAP_INDEX(',
            '        lookup_value,',
            f'        FRIKAN_LUT_SCALE_LAYER_{layer_index},',
            f'        FRIKAN_LUT_OFFSET_LAYER_{layer_index}',
            '    );',
            '    port_float result;',
            '',
            '    if ((mapped_index < 0.0f) || (mapped_index > FRIKAN_LUT_LAST_INDEX_FLOAT)) {',
            '        return 0.0f;',
            '    }',
            '',
            '    #if FRIKAN_LUT_INTERPOLATION',
            '    {',
            '        uint32_t lower_index = (uint32_t)mapped_index;',
            '        if (lower_index >= FRIKAN_LUT_LAST_INDEX) {',
            '            result = lut_values[FRIKAN_LUT_LAST_INDEX];',
            '        } else {',
            '            port_float frac = mapped_index - (port_float)lower_index;',
            '            port_float lower_value = lut_values[lower_index];',
            '            port_float upper_value = lut_values[lower_index + 1u];',
            '            result = lower_value + (upper_value - lower_value) * frac;',
            '        }',
            '    }',
            '    #else',
            '    result = lut_values[(uint32_t)mapped_index];',
            '    #endif',
            '',
            '    #if FRIKAN_USE_SYMMETRY && !FRIKAN_USE_EVEN',
            '    if (raw_value < 0.0f) {',
            '        result = -result;',
            '    }',
            '    #endif',
            '',
            '    return result;',
            '}',
            '',
        ])
        lut_layer_macro_lines.append(
            f'#define FRIKAN_LUT_LOOKUP_LAYER_{layer_index}(lut_values, raw_value) '
            f'frikan_lut_lookup_fast_layer_{layer_index}((lut_values), (raw_value))'
        )

    return (
        template
        .replace('__FRIKAN_LUT_LAYER_FUNCTIONS__', '\n'.join(lut_layer_function_lines))
        .replace('__FRIKAN_LUT_LAYER_MACROS__', '\n'.join(lut_layer_macro_lines))
        .replace('__FRIKAN_FORWARD_BODY__', _render_frikan_forward_body(model_spec))
    )


def _render_lstm_transformer_main_c() -> str:
    return r"""#include <stdint.h>

#include "model_data.h"

#define RCC_BASE 0x40023800u
#define DEMCR (*(volatile uint32_t *)0xE000EDFCu)
#define DWT_CTRL (*(volatile uint32_t *)0xE0001000u)
#define DWT_CYCCNT (*(volatile uint32_t *)0xE0001004u)

#define USART1_BASE 0x40011000u
#define RCC_APB2ENR (*(volatile uint32_t *)(RCC_BASE + 0x44u))
#define USART1_SR (*(volatile uint32_t *)(USART1_BASE + 0x00u))
#define USART1_DR (*(volatile uint32_t *)(USART1_BASE + 0x04u))
#define USART1_BRR (*(volatile uint32_t *)(USART1_BASE + 0x08u))
#define USART1_CR1 (*(volatile uint32_t *)(USART1_BASE + 0x0Cu))

#define RCC_APB2ENR_USART1EN (1u << 4)
#define USART_SR_TXE (1u << 7)
#define USART_CR1_TE (1u << 3)
#define USART_CR1_UE (1u << 13)
#define DEMCR_TRCENA (1u << 24)
#define DWT_CTRL_CYCCNTENA (1u << 0)

static port_float validation_output[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN];
static port_float debug_scaled_input[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM];
static port_float debug_lstm_hidden[VALIDATION_SEQ_LEN][LSTM_UNITS];
static port_float debug_transformer_ln_attn[TRANSFORMER_LAYER_COUNT][VALIDATION_SEQ_LEN][LSTM_UNITS];
static port_float debug_transformer_ln_ffn[TRANSFORMER_LAYER_COUNT][VALIDATION_SEQ_LEN][LSTM_UNITS];
static port_float debug_post_dense[VALIDATION_SEQ_LEN][POST_DENSE_UNITS];
static port_float debug_output_scaled[VALIDATION_SEQ_LEN];
static port_float scratch_sequence_a[VALIDATION_SEQ_LEN][LSTM_UNITS];
static port_float scratch_sequence_b[VALIDATION_SEQ_LEN][LSTM_UNITS];

static void uart_init(void)
{
    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;
    USART1_BRR = 0x05B2u;
    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;
}

static void uart_putc(char ch)
{
    while ((USART1_SR & USART_SR_TXE) == 0u) {
    }

    USART1_DR = (uint32_t)ch;
}

static void uart_puts(const char *message)
{
    while (*message != '\0') {
        if (*message == '\n') {
            uart_putc('\r');
        }

        uart_putc(*message++);
    }
}

static void uart_put_u32(uint32_t value)
{
    char buffer[11];
    uint32_t index = 0u;

    if (value == 0u) {
        uart_putc('0');
        return;
    }

    while (value > 0u && index < (uint32_t)sizeof(buffer)) {
        buffer[index++] = (char)('0' + (value % 10u));
        value /= 10u;
    }

    while (index > 0u) {
        uart_putc(buffer[--index]);
    }
}

static void uart_put_fixed6(port_float value)
{
    int32_t scaled = (int32_t)(value * 1000000.0f);
    int32_t abs_scaled = scaled;
    int32_t integer_part;
    int32_t fraction;
    int32_t divisor = 100000;

    if (scaled < 0) {
        uart_putc('-');
        abs_scaled = -scaled;
    }

    integer_part = abs_scaled / 1000000;
    fraction = abs_scaled % 1000000;

    uart_put_u32((uint32_t)integer_part);
    uart_putc('.');
    while (divisor > 0) {
        uart_putc((char)('0' + ((fraction / divisor) % 10)));
        divisor /= 10;
    }
}

static void uart_put_matrix_rows(const port_float *values,
                                 uint32_t row_count,
                                 uint32_t column_count)
{
    uint32_t row_index;
    for (row_index = 0u; row_index < row_count; ++row_index) {
        uint32_t column_index;
        if (row_index > 0u) {
            uart_putc(';');
        }
        for (column_index = 0u; column_index < column_count; ++column_index) {
            if (column_index > 0u) {
                uart_putc(',');
            }
            uart_put_fixed6(values[row_index * column_count + column_index]);
        }
    }
}

static void dwt_init(void)
{
    DEMCR |= DEMCR_TRCENA;
    DWT_CYCCNT = 0u;
    DWT_CTRL |= DWT_CTRL_CYCCNTENA;
}

static uint32_t dwt_read_cycles(void)
{
    return DWT_CYCCNT;
}

static uint32_t dwt_is_counting(void)
{
    volatile uint32_t spin;
    uint32_t before;
    uint32_t after;

    dwt_init();
    before = dwt_read_cycles();
    for (spin = 0u; spin < 64u; ++spin) {
        __asm volatile ("nop");
    }
    after = dwt_read_cycles();
    return after > before ? 1u : 0u;
}

static port_float tanh_approx(port_float value)
{
    port_float squared;

    if (value > 3.0f) {
        return 0.99505478f;
    }
    if (value < -3.0f) {
        return -0.99505478f;
    }

    squared = value * value;
    return value * (27.0f + squared) / (27.0f + 9.0f * squared);
}

static port_float sigmoid_approx(port_float value)
{
    if (value > 8.0f) {
        return 0.99966466f;
    }
    if (value < -8.0f) {
        return 0.00033535f;
    }
    return 0.5f * (tanh_approx(value * 0.5f) + 1.0f);
}

static port_float relu(port_float value)
{
    return value > 0.0f ? value : 0.0f;
}

static port_float silu_approx(port_float value)
{
    return value * sigmoid_approx(value);
}

static port_float exp_approx(port_float value)
{
    const port_float ln2 = 0.6931471805599453f;
    int32_t exponent = 0;
    port_float squared;
    port_float polynomial;

    if (value < -16.0f) {
        return 0.0f;
    }

    while (value < -ln2) {
        value += ln2;
        exponent += 1;
    }
    while (value > ln2) {
        value -= ln2;
        exponent -= 1;
    }

    squared = value * value;
    polynomial = 1.0f
        + value
        + (squared * 0.5f)
        + (squared * value * 0.16666666666666666f)
        + (squared * squared * 0.041666666666666664f)
        + (squared * squared * value * 0.008333333333333333f);

    while (exponent > 0) {
        polynomial *= 0.5f;
        exponent -= 1;
    }
    while (exponent < 0) {
        polynomial *= 2.0f;
        exponent += 1;
    }

    return polynomial;
}

static port_float sqrt_approx(port_float value)
{
    uint32_t scale_up = 0u;
    uint32_t scale_down = 0u;
    uint32_t iteration;
    port_float guess;
    port_float normalized;

    if (value <= 0.0f) {
        return 0.0f;
    }

    normalized = value;
    while (normalized < 0.25f) {
        normalized *= 4.0f;
        scale_up += 1u;
    }
    while (normalized > 4.0f) {
        normalized *= 0.25f;
        scale_down += 1u;
    }

    guess = normalized > 1.0f ? normalized : 1.0f;
    for (iteration = 0u; iteration < 6u; ++iteration) {
        guess = 0.5f * (guess + normalized / guess);
    }

    while (scale_down > 0u) {
        guess *= 2.0f;
        scale_down -= 1u;
    }
    while (scale_up > 0u) {
        guess *= 0.5f;
        scale_up -= 1u;
    }

    return guess;
}

static port_float apply_activation(port_float value, uint32_t activation_code)
{
    if (activation_code == ACT_LINEAR) {
        return value;
    }
    if (activation_code == ACT_RELU) {
        return relu(value);
    }
    if (activation_code == ACT_TANH) {
        return tanh_approx(value);
    }
    if (activation_code == ACT_SIGMOID) {
        return sigmoid_approx(value);
    }
    if (activation_code == ACT_SILU) {
        return silu_approx(value);
    }
    return value;
}

static void zero_buffer(port_float *buffer, uint32_t length)
{
    uint32_t index;
    for (index = 0u; index < length; ++index) {
        buffer[index] = 0.0f;
    }
}

static port_float scale_input(port_float value)
{
    if (SCALER_INPUT_DATA_RANGE == 0.0f) {
        return value;
    }
    return value / SCALER_INPUT_DATA_RANGE;
}

static port_float inverse_scale_output(port_float value)
{
    return value * SCALER_OUTPUT_DATA_RANGE;
}

static void dense_forward_generic(const port_float *input,
                                  uint32_t input_dim,
                                  const port_float *kernel,
                                  const port_float *bias,
                                  uint32_t output_dim,
                                  uint32_t activation_code,
                                  port_float *output)
{
    uint32_t output_index;
    for (output_index = 0u; output_index < output_dim; ++output_index) {
        uint32_t input_index;
        port_float sum = bias[output_index];
        for (input_index = 0u; input_index < input_dim; ++input_index) {
            sum += input[input_index] * kernel[input_index * output_dim + output_index];
        }
        output[output_index] = apply_activation(sum, activation_code);
    }
}

static void layer_norm_forward(const port_float *input,
                               const port_float *gamma,
                               const port_float *beta,
                               port_float *output)
{
    uint32_t feature_index;
    port_float mean = 0.0f;
    port_float variance = 0.0f;
    port_float denominator;

    for (feature_index = 0u; feature_index < LSTM_UNITS; ++feature_index) {
        mean += input[feature_index];
    }
    mean /= (port_float)LSTM_UNITS;

    for (feature_index = 0u; feature_index < LSTM_UNITS; ++feature_index) {
        port_float centered = input[feature_index] - mean;
        variance += centered * centered;
    }
    variance /= (port_float)LSTM_UNITS;
    denominator = sqrt_approx(variance + TRANSFORMER_LAYER_NORM_EPSILON);
    if (denominator <= 0.0f) {
        denominator = 1.0f;
    }

    for (feature_index = 0u; feature_index < LSTM_UNITS; ++feature_index) {
        output[feature_index] = ((input[feature_index] - mean) / denominator) * gamma[feature_index] + beta[feature_index];
    }
}

static void transformer_average_pool_same(const port_float input_sequence[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                          port_float pooled_sequence[TRANSFORMER_CONTEXT_LEN][LSTM_UNITS])
{
    uint32_t output_index;
    uint32_t padded_length = ((TRANSFORMER_CONTEXT_LEN - 1u) * ATTENTION_POOL_SIZE) + ATTENTION_POOL_SIZE;
    uint32_t total_padding = padded_length > VALIDATION_SEQ_LEN ? padded_length - VALIDATION_SEQ_LEN : 0u;
    int32_t pad_left = (int32_t)(total_padding / 2u);

    for (output_index = 0u; output_index < TRANSFORMER_CONTEXT_LEN; ++output_index) {
        uint32_t feature_index;
        int32_t window_start = (int32_t)(output_index * ATTENTION_POOL_SIZE) - pad_left;
        int32_t window_end = window_start + (int32_t)ATTENTION_POOL_SIZE;
        uint32_t valid_count = 0u;

        for (feature_index = 0u; feature_index < LSTM_UNITS; ++feature_index) {
            pooled_sequence[output_index][feature_index] = 0.0f;
        }

        for (; window_start < window_end; ++window_start) {
            if (window_start >= 0 && window_start < (int32_t)VALIDATION_SEQ_LEN) {
                for (feature_index = 0u; feature_index < LSTM_UNITS; ++feature_index) {
                    pooled_sequence[output_index][feature_index] += input_sequence[(uint32_t)window_start][feature_index];
                }
                valid_count += 1u;
            }
        }

        if (valid_count > 0u) {
            for (feature_index = 0u; feature_index < LSTM_UNITS; ++feature_index) {
                pooled_sequence[output_index][feature_index] /= (port_float)valid_count;
            }
        }
    }
}

static void lstm_backbone_forward(const port_float sequence[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                  uint32_t reset_state_each_run,
                                  port_float hidden_state[LSTM_UNITS],
                                  port_float cell_state[LSTM_UNITS],
                                  port_float output_sequence[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                  port_float debug_scaled_input_buffer[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                  port_float debug_lstm_hidden_buffer[VALIDATION_SEQ_LEN][LSTM_UNITS])
{
    uint32_t step;

    if (reset_state_each_run != 0u) {
        zero_buffer(hidden_state, LSTM_UNITS);
        zero_buffer(cell_state, LSTM_UNITS);
    }

    for (step = 0u; step < VALIDATION_SEQ_LEN; ++step) {
        uint32_t unit;
        uint32_t input_index;
        port_float previous_hidden[LSTM_UNITS];
        port_float previous_cell[LSTM_UNITS];
        port_float scaled_input_step[LSTM_INPUT_DIM];

        for (input_index = 0u; input_index < LSTM_INPUT_DIM; ++input_index) {
            scaled_input_step[input_index] = scale_input(sequence[step][input_index]);
            if (debug_scaled_input_buffer != 0) {
                debug_scaled_input_buffer[step][input_index] = scaled_input_step[input_index];
            }
        }

        for (unit = 0u; unit < LSTM_UNITS; ++unit) {
            previous_hidden[unit] = hidden_state[unit];
            previous_cell[unit] = cell_state[unit];
        }

        for (unit = 0u; unit < LSTM_UNITS; ++unit) {
            uint32_t hidden_index;
            port_float input_gate_acc = lstm_bias[unit + LSTM_UNITS * 0u];
            port_float forget_gate_acc = lstm_bias[unit + LSTM_UNITS * 1u];
            port_float candidate_acc = lstm_bias[unit + LSTM_UNITS * 2u];
            port_float output_gate_acc = lstm_bias[unit + LSTM_UNITS * 3u];

            for (input_index = 0u; input_index < LSTM_INPUT_DIM; ++input_index) {
                port_float input_value = scaled_input_step[input_index];
                input_gate_acc += input_value * lstm_kernel[input_index][unit + LSTM_UNITS * 0u];
                forget_gate_acc += input_value * lstm_kernel[input_index][unit + LSTM_UNITS * 1u];
                candidate_acc += input_value * lstm_kernel[input_index][unit + LSTM_UNITS * 2u];
                output_gate_acc += input_value * lstm_kernel[input_index][unit + LSTM_UNITS * 3u];
            }

            for (hidden_index = 0u; hidden_index < LSTM_UNITS; ++hidden_index) {
                port_float hidden_value = previous_hidden[hidden_index];
                input_gate_acc += hidden_value * lstm_recurrent_kernel[hidden_index][unit + LSTM_UNITS * 0u];
                forget_gate_acc += hidden_value * lstm_recurrent_kernel[hidden_index][unit + LSTM_UNITS * 1u];
                candidate_acc += hidden_value * lstm_recurrent_kernel[hidden_index][unit + LSTM_UNITS * 2u];
                output_gate_acc += hidden_value * lstm_recurrent_kernel[hidden_index][unit + LSTM_UNITS * 3u];
            }

            {
                port_float input_gate = sigmoid_approx(input_gate_acc);
                port_float forget_gate = sigmoid_approx(forget_gate_acc);
                port_float candidate = tanh_approx(candidate_acc);
                port_float output_gate = sigmoid_approx(output_gate_acc);
                port_float cell_value = forget_gate * previous_cell[unit] + input_gate * candidate;
                port_float hidden_value = output_gate * tanh_approx(cell_value);

                cell_state[unit] = cell_value;
                hidden_state[unit] = hidden_value;
                output_sequence[step][unit] = hidden_value;
                if (debug_lstm_hidden_buffer != 0) {
                    debug_lstm_hidden_buffer[step][unit] = hidden_value;
                }
            }
        }
    }
}

static void transformer_forward_layer(uint32_t layer_index,
                                      const port_float input_sequence[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                      port_float output_sequence[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                      port_float debug_ln_attn_sequence[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                      port_float debug_ln_ffn_sequence[VALIDATION_SEQ_LEN][LSTM_UNITS])
{
    port_float pooled_sequence[TRANSFORMER_CONTEXT_LEN][LSTM_UNITS];
    port_float key_cache[TRANSFORMER_CONTEXT_LEN][TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM];
    port_float value_cache[TRANSFORMER_CONTEXT_LEN][TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM];
    uint32_t context_index;

    transformer_average_pool_same(input_sequence, pooled_sequence);

    for (context_index = 0u; context_index < TRANSFORMER_CONTEXT_LEN; ++context_index) {
        uint32_t head_index;
        for (head_index = 0u; head_index < TRANSFORMER_HEADS; ++head_index) {
            uint32_t dim_index;
            for (dim_index = 0u; dim_index < TRANSFORMER_KEY_DIM; ++dim_index) {
                uint32_t input_index;
                port_float key_sum = transformer_key_bias[layer_index][head_index][dim_index];
                port_float value_sum = transformer_value_bias[layer_index][head_index][dim_index];
                for (input_index = 0u; input_index < LSTM_UNITS; ++input_index) {
                    port_float input_value = pooled_sequence[context_index][input_index];
                    key_sum += input_value * transformer_key_kernel[layer_index][input_index][head_index][dim_index];
                    value_sum += input_value * transformer_value_kernel[layer_index][input_index][head_index][dim_index];
                }
                key_cache[context_index][head_index][dim_index] = key_sum;
                value_cache[context_index][head_index][dim_index] = value_sum;
            }
        }
    }

    for (context_index = 0u; context_index < VALIDATION_SEQ_LEN; ++context_index) {
        uint32_t head_index;
        port_float query_cache[TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM];
        port_float head_output[TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM];
        port_float attention_projected[LSTM_UNITS];
        port_float residual_buffer[LSTM_UNITS];
        port_float ln_attn_output[LSTM_UNITS];
        port_float ffn_expand_output[TRANSFORMER_FF_DIM];
        port_float ffn_project_output[LSTM_UNITS];
        port_float ln_ffn_output[LSTM_UNITS];

        for (head_index = 0u; head_index < TRANSFORMER_HEADS; ++head_index) {
            uint32_t dim_index;
            for (dim_index = 0u; dim_index < TRANSFORMER_KEY_DIM; ++dim_index) {
                uint32_t input_index;
                port_float sum = transformer_query_bias[layer_index][head_index][dim_index];
                for (input_index = 0u; input_index < LSTM_UNITS; ++input_index) {
                    sum += input_sequence[context_index][input_index] * transformer_query_kernel[layer_index][input_index][head_index][dim_index];
                }
                query_cache[head_index][dim_index] = sum;
            }
        }

        for (head_index = 0u; head_index < TRANSFORMER_HEADS; ++head_index) {
            uint32_t output_index;
            port_float scores[TRANSFORMER_CONTEXT_LEN];
            port_float max_score = -1.0e30f;
            port_float softmax_sum = 0.0f;

            for (output_index = 0u; output_index < TRANSFORMER_CONTEXT_LEN; ++output_index) {
                uint32_t dim_index;
                port_float score = 0.0f;
                for (dim_index = 0u; dim_index < TRANSFORMER_KEY_DIM; ++dim_index) {
                    score += query_cache[head_index][dim_index] * key_cache[output_index][head_index][dim_index];
                }
                score *= ATTENTION_SCALE;
                scores[output_index] = score;
                if (score > max_score) {
                    max_score = score;
                }
            }

            for (output_index = 0u; output_index < TRANSFORMER_CONTEXT_LEN; ++output_index) {
                scores[output_index] = exp_approx(scores[output_index] - max_score);
                softmax_sum += scores[output_index];
            }

            if (softmax_sum <= 0.0f) {
                for (output_index = 0u; output_index < TRANSFORMER_CONTEXT_LEN; ++output_index) {
                    scores[output_index] = output_index == 0u ? 1.0f : 0.0f;
                }
                softmax_sum = 1.0f;
            }

            for (output_index = 0u; output_index < TRANSFORMER_KEY_DIM; ++output_index) {
                head_output[head_index][output_index] = 0.0f;
            }

            for (output_index = 0u; output_index < TRANSFORMER_CONTEXT_LEN; ++output_index) {
                uint32_t dim_index;
                port_float normalized_score = scores[output_index] / softmax_sum;
                for (dim_index = 0u; dim_index < TRANSFORMER_KEY_DIM; ++dim_index) {
                    head_output[head_index][dim_index] += normalized_score * value_cache[output_index][head_index][dim_index];
                }
            }
        }

        for (head_index = 0u; head_index < LSTM_UNITS; ++head_index) {
            uint32_t input_index;
            port_float sum = transformer_attention_output_bias[layer_index][head_index];
            for (input_index = 0u; input_index < TRANSFORMER_HEADS; ++input_index) {
                uint32_t dim_index;
                for (dim_index = 0u; dim_index < TRANSFORMER_KEY_DIM; ++dim_index) {
                    sum += head_output[input_index][dim_index] * transformer_attention_output_kernel[layer_index][input_index][dim_index][head_index];
                }
            }
            attention_projected[head_index] = sum;
            residual_buffer[head_index] = input_sequence[context_index][head_index] + sum;
        }

        layer_norm_forward(
            residual_buffer,
            transformer_ln_attn_gamma[layer_index],
            transformer_ln_attn_beta[layer_index],
            ln_attn_output
        );
        if (debug_ln_attn_sequence != 0) {
            for (head_index = 0u; head_index < LSTM_UNITS; ++head_index) {
                debug_ln_attn_sequence[context_index][head_index] = ln_attn_output[head_index];
            }
        }

        dense_forward_generic(
            ln_attn_output,
            LSTM_UNITS,
            &transformer_ffn_expand_kernel[layer_index][0u][0u],
            transformer_ffn_expand_bias[layer_index],
            TRANSFORMER_FF_DIM,
            ACT_RELU,
            ffn_expand_output
        );
        dense_forward_generic(
            ffn_expand_output,
            TRANSFORMER_FF_DIM,
            &transformer_ffn_project_kernel[layer_index][0u][0u],
            transformer_ffn_project_bias[layer_index],
            LSTM_UNITS,
            ACT_LINEAR,
            ffn_project_output
        );

        for (head_index = 0u; head_index < LSTM_UNITS; ++head_index) {
            residual_buffer[head_index] = ln_attn_output[head_index] + ffn_project_output[head_index];
        }
        layer_norm_forward(
            residual_buffer,
            transformer_ln_ffn_gamma[layer_index],
            transformer_ln_ffn_beta[layer_index],
            ln_ffn_output
        );
        for (head_index = 0u; head_index < LSTM_UNITS; ++head_index) {
            output_sequence[context_index][head_index] = ln_ffn_output[head_index];
        }
        if (debug_ln_ffn_sequence != 0) {
            for (head_index = 0u; head_index < LSTM_UNITS; ++head_index) {
                debug_ln_ffn_sequence[context_index][head_index] = ln_ffn_output[head_index];
            }
        }
    }
}

static void lstm_transformer_forward_sequence(const port_float sequence[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                              uint32_t reset_state_each_run,
                                              port_float hidden_state[LSTM_UNITS],
                                              port_float cell_state[LSTM_UNITS],
                                              port_float output_sequence[VALIDATION_SEQ_LEN],
                                              port_float debug_scaled_input_buffer[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                              port_float debug_lstm_hidden_buffer[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                              port_float debug_ln_attn_buffer[TRANSFORMER_LAYER_COUNT][VALIDATION_SEQ_LEN][LSTM_UNITS],
                                              port_float debug_ln_ffn_buffer[TRANSFORMER_LAYER_COUNT][VALIDATION_SEQ_LEN][LSTM_UNITS],
                                              port_float debug_post_dense_buffer[VALIDATION_SEQ_LEN][POST_DENSE_UNITS],
                                              port_float debug_output_scaled_buffer[VALIDATION_SEQ_LEN])
{
    uint32_t layer_index;
    uint32_t step_index;
    port_float (*current_sequence)[LSTM_UNITS] = scratch_sequence_a;
    port_float (*next_sequence)[LSTM_UNITS] = scratch_sequence_b;

    lstm_backbone_forward(
        sequence,
        reset_state_each_run,
        hidden_state,
        cell_state,
        current_sequence,
        debug_scaled_input_buffer,
        debug_lstm_hidden_buffer
    );

    for (layer_index = 0u; layer_index < TRANSFORMER_LAYER_COUNT; ++layer_index) {
        port_float (*temp_sequence)[LSTM_UNITS];
        transformer_forward_layer(
            layer_index,
            current_sequence,
            next_sequence,
            debug_ln_attn_buffer != 0 ? debug_ln_attn_buffer[layer_index] : 0,
            debug_ln_ffn_buffer != 0 ? debug_ln_ffn_buffer[layer_index] : 0
        );
        temp_sequence = current_sequence;
        current_sequence = next_sequence;
        next_sequence = temp_sequence;
    }

    for (step_index = 0u; step_index < VALIDATION_SEQ_LEN; ++step_index) {
        port_float post_dense_output[POST_DENSE_UNITS];
        port_float output_scaled_vector[OUTPUT_UNITS];

        if (HAS_POST_DENSE != 0u) {
            dense_forward_generic(
                current_sequence[step_index],
                POST_DENSE_INPUT_UNITS,
                &post_dense_kernel[0u][0u],
                post_dense_bias,
                POST_DENSE_UNITS,
                POST_DENSE_ACTIVATION,
                post_dense_output
            );
            if (debug_post_dense_buffer != 0) {
                uint32_t post_index;
                for (post_index = 0u; post_index < POST_DENSE_UNITS; ++post_index) {
                    debug_post_dense_buffer[step_index][post_index] = post_dense_output[post_index];
                }
            }
            dense_forward_generic(
                post_dense_output,
                OUTPUT_INPUT_UNITS,
                &output_kernel[0u][0u],
                output_bias,
                OUTPUT_UNITS,
                ACT_LINEAR,
                output_scaled_vector
            );
        } else {
            dense_forward_generic(
                current_sequence[step_index],
                OUTPUT_INPUT_UNITS,
                &output_kernel[0u][0u],
                output_bias,
                OUTPUT_UNITS,
                ACT_LINEAR,
                output_scaled_vector
            );
        }

        if (debug_output_scaled_buffer != 0) {
            debug_output_scaled_buffer[step_index] = output_scaled_vector[0u];
        }
        output_sequence[step_index] = inverse_scale_output(output_scaled_vector[0u]);
    }
}

static void run_validation_record(const port_float sequence[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                  port_float output_sequence[VALIDATION_SEQ_LEN],
                                  uint32_t reset_state_each_run,
                                  port_float debug_scaled_input_buffer[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                  port_float debug_lstm_hidden_buffer[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                  port_float debug_ln_attn_buffer[TRANSFORMER_LAYER_COUNT][VALIDATION_SEQ_LEN][LSTM_UNITS],
                                  port_float debug_ln_ffn_buffer[TRANSFORMER_LAYER_COUNT][VALIDATION_SEQ_LEN][LSTM_UNITS],
                                  port_float debug_post_dense_buffer[VALIDATION_SEQ_LEN][POST_DENSE_UNITS],
                                  port_float debug_output_scaled_buffer[VALIDATION_SEQ_LEN])
{
    port_float hidden_state[LSTM_UNITS];
    port_float cell_state[LSTM_UNITS];

    zero_buffer(hidden_state, LSTM_UNITS);
    zero_buffer(cell_state, LSTM_UNITS);
    lstm_transformer_forward_sequence(
        sequence,
        reset_state_each_run,
        hidden_state,
        cell_state,
        output_sequence,
        debug_scaled_input_buffer,
        debug_lstm_hidden_buffer,
        debug_ln_attn_buffer,
        debug_ln_ffn_buffer,
        debug_post_dense_buffer,
        debug_output_scaled_buffer
    );
}

static void run_benchmark_record(const port_float sequence[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                 uint32_t reset_state_each_run,
                                 port_float hidden_state[LSTM_UNITS],
                                 port_float cell_state[LSTM_UNITS],
                                 port_float *output_value)
{
    port_float output_sequence[VALIDATION_SEQ_LEN];
    lstm_transformer_forward_sequence(
        sequence,
        reset_state_each_run,
        hidden_state,
        cell_state,
        output_sequence,
        0,
        0,
        0,
        0,
        0,
        0
    );
    *output_value = output_sequence[VALIDATION_SEQ_LEN - 1u];
}

int main(void)
{
    uint32_t iteration;
    uint32_t record_index;
    uint32_t step_index;
    uint32_t layer_index;
    uint32_t dwt_supported;
    uint32_t start_cycles;
    uint32_t end_cycles;
    uint32_t total_cycles = 0u;
    port_float hidden_state[LSTM_UNITS];
    port_float cell_state[LSTM_UNITS];
    port_float output_value = 0.0f;

    uart_init();
    dwt_supported = dwt_is_counting();
    zero_buffer(hidden_state, LSTM_UNITS);
    zero_buffer(cell_state, LSTM_UNITS);

    if (dwt_supported != 0u) {
        start_cycles = dwt_read_cycles();
    }

    for (iteration = 0u; iteration < BENCHMARK_ITERATIONS; ++iteration) {
        for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
            run_benchmark_record(
                validation_input[record_index],
                BENCHMARK_RESET_STATE_EACH_RUN,
                hidden_state,
                cell_state,
                &output_value
            );
        }
    }

    if (dwt_supported != 0u) {
        end_cycles = dwt_read_cycles();
        total_cycles = end_cycles - start_cycles;
    }

    uart_puts("LSTM_TRANSFORMER_QEMU_VALIDATION\n");
    uart_puts("iterations=");
    uart_put_u32(BENCHMARK_ITERATIONS);
    uart_puts("\nrecord_count=");
    uart_put_u32(VALIDATION_RECORD_COUNT);
    uart_puts("\nseq_len=");
    uart_put_u32(VALIDATION_SEQ_LEN);
    uart_puts("\ninput_dim=");
    uart_put_u32(LSTM_INPUT_DIM);
    uart_puts("\nlstm_units=");
    uart_put_u32(LSTM_UNITS);
    uart_puts("\ntransformer_layers=");
    uart_put_u32(TRANSFORMER_LAYER_COUNT);
    uart_puts("\ntransformer_heads=");
    uart_put_u32(TRANSFORMER_HEADS);
    uart_puts("\ntransformer_ff_dim=");
    uart_put_u32(TRANSFORMER_FF_DIM);
    uart_puts("\nattention_pool_size=");
    uart_put_u32(ATTENTION_POOL_SIZE);
    uart_puts("\ndwt_supported=");
    uart_put_u32(dwt_supported);
    uart_puts("\ntimer_source=");
    uart_puts(dwt_supported != 0u ? "dwt" : "host_elapsed");
    if (dwt_supported != 0u) {
        uart_puts("\nmeasurement_unit=");
        uart_puts("cycles");
        uart_puts("\nmeasurement_total=");
        uart_put_u32(total_cycles);
        uart_puts("\nmeasurement_per_iter=");
        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));
        uart_puts("\ncycles_total=");
        uart_put_u32(total_cycles);
        uart_puts("\ncycles_per_iter=");
        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));
    }
    uart_puts("\noutput=");
    uart_put_fixed6(output_value);
    uart_puts("\n");
    uart_puts("benchmark_complete=1\n");

    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
        run_validation_record(
            validation_input[record_index],
            validation_output[record_index],
            1u,
            debug_scaled_input,
            debug_lstm_hidden,
            debug_transformer_ln_attn,
            debug_transformer_ln_ffn,
            debug_post_dense,
            debug_output_scaled
        );

        uart_puts("validation_record_");
        uart_put_u32(record_index);
        uart_puts("=");
        for (step_index = 0u; step_index < VALIDATION_SEQ_LEN; ++step_index) {
            if (step_index > 0u) {
                uart_putc(',');
            }
            uart_put_fixed6(validation_output[record_index][step_index]);
        }
        uart_puts("\n");

        uart_puts("validation_input_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_scaled_input[0u][0u], VALIDATION_SEQ_LEN, LSTM_INPUT_DIM);
        uart_puts("\n");

        uart_puts("validation_lstm_hidden_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_lstm_hidden[0u][0u], VALIDATION_SEQ_LEN, LSTM_UNITS);
        uart_puts("\n");

        for (layer_index = 0u; layer_index < TRANSFORMER_LAYER_COUNT; ++layer_index) {
            uart_puts("validation_transformer_ln_attn_");
            uart_put_u32(layer_index);
            uart_putc('_');
            uart_put_u32(record_index);
            uart_puts("=");
            uart_put_matrix_rows(&debug_transformer_ln_attn[layer_index][0u][0u], VALIDATION_SEQ_LEN, LSTM_UNITS);
            uart_puts("\n");

            uart_puts("validation_transformer_ln_ffn_");
            uart_put_u32(layer_index);
            uart_putc('_');
            uart_put_u32(record_index);
            uart_puts("=");
            uart_put_matrix_rows(&debug_transformer_ln_ffn[layer_index][0u][0u], VALIDATION_SEQ_LEN, LSTM_UNITS);
            uart_puts("\n");
        }

        if (HAS_POST_DENSE != 0u) {
            uart_puts("validation_post_dense_");
            uart_put_u32(record_index);
            uart_puts("=");
            uart_put_matrix_rows(&debug_post_dense[0u][0u], VALIDATION_SEQ_LEN, POST_DENSE_UNITS);
            uart_puts("\n");
        }

        uart_puts("validation_output_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_output_scaled[0u], VALIDATION_SEQ_LEN, 1u);
        uart_puts("\n");
    }

    uart_puts("validation_complete=1\n");

    while (1) {
    }
}
"""


def _render_grn_main_c() -> str:
    return r"""#include <stdint.h>

#include "model_data.h"

#define RCC_BASE 0x40023800u
#define DEMCR (*(volatile uint32_t *)0xE000EDFCu)
#define DWT_CTRL (*(volatile uint32_t *)0xE0001000u)
#define DWT_CYCCNT (*(volatile uint32_t *)0xE0001004u)

#define USART1_BASE 0x40011000u
#define RCC_APB2ENR (*(volatile uint32_t *)(RCC_BASE + 0x44u))
#define USART1_SR (*(volatile uint32_t *)(USART1_BASE + 0x00u))
#define USART1_DR (*(volatile uint32_t *)(USART1_BASE + 0x04u))
#define USART1_BRR (*(volatile uint32_t *)(USART1_BASE + 0x08u))
#define USART1_CR1 (*(volatile uint32_t *)(USART1_BASE + 0x0Cu))

#define RCC_APB2ENR_USART1EN (1u << 4)
#define USART_SR_TXE (1u << 7)
#define USART_CR1_TE (1u << 3)
#define USART_CR1_UE (1u << 13)
#define DEMCR_TRCENA (1u << 24)
#define DWT_CTRL_CYCCNTENA (1u << 0)

static port_float validation_output[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN];
static port_float debug_scaled_input[VALIDATION_SEQ_LEN][GRU_INPUT_DIM];
static port_float debug_gru_hidden[VALIDATION_SEQ_LEN][GRU_UNITS];
static port_float debug_dense_output[VALIDATION_SEQ_LEN][DENSE_UNITS];
static port_float debug_output_scaled[VALIDATION_SEQ_LEN];

static void uart_init(void)
{
    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;
    USART1_BRR = 0x05B2u;
    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;
}

static void uart_putc(char ch)
{
    while ((USART1_SR & USART_SR_TXE) == 0u) {
    }

    USART1_DR = (uint32_t)ch;
}

static void uart_puts(const char *message)
{
    while (*message != '\0') {
        if (*message == '\n') {
            uart_putc('\r');
        }

        uart_putc(*message++);
    }
}

static void uart_put_u32(uint32_t value)
{
    char buffer[11];
    uint32_t index = 0u;

    if (value == 0u) {
        uart_putc('0');
        return;
    }

    while (value > 0u && index < (uint32_t)sizeof(buffer)) {
        buffer[index++] = (char)('0' + (value % 10u));
        value /= 10u;
    }

    while (index > 0u) {
        uart_putc(buffer[--index]);
    }
}

static void uart_put_fixed6(port_float value)
{
    int32_t scaled = (int32_t)(value * 1000000.0f);
    int32_t abs_scaled = scaled;
    int32_t integer_part;
    int32_t fraction;
    int32_t divisor = 100000;

    if (scaled < 0) {
        uart_putc('-');
        abs_scaled = -scaled;
    }

    integer_part = abs_scaled / 1000000;
    fraction = abs_scaled % 1000000;

    uart_put_u32((uint32_t)integer_part);
    uart_putc('.');
    while (divisor > 0) {
        uart_putc((char)('0' + ((fraction / divisor) % 10)));
        divisor /= 10;
    }
}

static void uart_put_matrix_rows(const port_float *values,
                                 uint32_t row_count,
                                 uint32_t column_count)
{
    uint32_t row_index;
    for (row_index = 0u; row_index < row_count; ++row_index) {
        uint32_t column_index;
        if (row_index > 0u) {
            uart_putc(';');
        }
        for (column_index = 0u; column_index < column_count; ++column_index) {
            if (column_index > 0u) {
                uart_putc(',');
            }
            uart_put_fixed6(values[row_index * column_count + column_index]);
        }
    }
}

static void dwt_init(void)
{
    DEMCR |= DEMCR_TRCENA;
    DWT_CYCCNT = 0u;
    DWT_CTRL |= DWT_CTRL_CYCCNTENA;
}

static uint32_t dwt_read_cycles(void)
{
    return DWT_CYCCNT;
}

static uint32_t dwt_is_counting(void)
{
    volatile uint32_t spin;
    uint32_t before;
    uint32_t after;

    dwt_init();
    before = dwt_read_cycles();
    for (spin = 0u; spin < 64u; ++spin) {
        __asm volatile ("nop");
    }
    after = dwt_read_cycles();
    return after > before ? 1u : 0u;
}

static port_float tanh_approx(port_float value)
{
    port_float squared;

    if (value > 3.0f) {
        return 0.99505478f;
    }
    if (value < -3.0f) {
        return -0.99505478f;
    }

    squared = value * value;
    return value * (27.0f + squared) / (27.0f + 9.0f * squared);
}

static port_float sigmoid_approx(port_float value)
{
    if (value > 8.0f) {
        return 0.99966466f;
    }
    if (value < -8.0f) {
        return 0.00033535f;
    }
    return 0.5f * (tanh_approx(value * 0.5f) + 1.0f);
}

static port_float relu(port_float value)
{
    return value > 0.0f ? value : 0.0f;
}

static port_float silu_approx(port_float value)
{
    return value * sigmoid_approx(value);
}

static void zero_buffer(port_float *buffer, uint32_t length)
{
    uint32_t index;
    for (index = 0u; index < length; ++index) {
        buffer[index] = 0.0f;
    }
}

static port_float scale_input(port_float value)
{
    if (SCALER_INPUT_DATA_RANGE == 0.0f) {
        return value;
    }
    return value / SCALER_INPUT_DATA_RANGE;
}

static port_float inverse_scale_output(port_float value)
{
    return value * SCALER_OUTPUT_DATA_RANGE;
}

static void dense_forward_silu(const port_float input[GRU_UNITS],
                               port_float output[DENSE_UNITS])
{
    uint32_t out_index;
    for (out_index = 0u; out_index < DENSE_UNITS; ++out_index) {
        uint32_t input_index;
        port_float sum = dense_bias[out_index];
        for (input_index = 0u; input_index < GRU_UNITS; ++input_index) {
            sum += input[input_index] * dense_kernel[input_index][out_index];
        }
        output[out_index] = silu_approx(sum);
    }
}

static port_float output_forward_linear(const port_float input[DENSE_UNITS])
{
    uint32_t input_index;
    port_float sum = output_bias[0u];
    for (input_index = 0u; input_index < DENSE_UNITS; ++input_index) {
        sum += input[input_index] * output_kernel[input_index][0u];
    }
    return sum;
}

static void gru_forward_step(const port_float input_step[GRU_INPUT_DIM],
                             port_float hidden_state[GRU_UNITS],
                             port_float *output_scaled_value,
                             port_float debug_scaled_input_step[GRU_INPUT_DIM],
                             port_float debug_hidden_step[GRU_UNITS],
                             port_float debug_dense_step[DENSE_UNITS],
                             port_float *output_value)
{
    uint32_t unit;
    uint32_t input_index;
    port_float previous_hidden[GRU_UNITS];
    port_float dense_output[DENSE_UNITS];
    port_float scaled_input_step[GRU_INPUT_DIM];

    for (input_index = 0u; input_index < GRU_INPUT_DIM; ++input_index) {
        scaled_input_step[input_index] = scale_input(input_step[input_index]);
        if (debug_scaled_input_step != 0) {
            debug_scaled_input_step[input_index] = scaled_input_step[input_index];
        }
    }

    for (unit = 0u; unit < GRU_UNITS; ++unit) {
        previous_hidden[unit] = hidden_state[unit];
    }

    for (unit = 0u; unit < GRU_UNITS; ++unit) {
        uint32_t hidden_index;
        port_float update_gate_input = gru_input_bias[unit + GRU_UNITS * 0u];
        port_float reset_gate_input = gru_input_bias[unit + GRU_UNITS * 1u];
        port_float candidate_input = gru_input_bias[unit + GRU_UNITS * 2u];
        port_float update_gate_recurrent = gru_recurrent_bias[unit + GRU_UNITS * 0u];
        port_float reset_gate_recurrent = gru_recurrent_bias[unit + GRU_UNITS * 1u];
        port_float candidate_recurrent = gru_recurrent_bias[unit + GRU_UNITS * 2u];
        port_float update_gate;
        port_float reset_gate;
        port_float candidate;
        port_float hidden_value;

        for (input_index = 0u; input_index < GRU_INPUT_DIM; ++input_index) {
            port_float input_value = scaled_input_step[input_index];
            update_gate_input += input_value * gru_kernel[input_index][unit + GRU_UNITS * 0u];
            reset_gate_input += input_value * gru_kernel[input_index][unit + GRU_UNITS * 1u];
            candidate_input += input_value * gru_kernel[input_index][unit + GRU_UNITS * 2u];
        }

        for (hidden_index = 0u; hidden_index < GRU_UNITS; ++hidden_index) {
            port_float prev_value = previous_hidden[hidden_index];
            update_gate_recurrent += prev_value * gru_recurrent_kernel[hidden_index][unit + GRU_UNITS * 0u];
            reset_gate_recurrent += prev_value * gru_recurrent_kernel[hidden_index][unit + GRU_UNITS * 1u];
            candidate_recurrent += prev_value * gru_recurrent_kernel[hidden_index][unit + GRU_UNITS * 2u];
        }

        update_gate = sigmoid_approx(update_gate_input + update_gate_recurrent);
        reset_gate = sigmoid_approx(reset_gate_input + reset_gate_recurrent);
        candidate = tanh_approx(candidate_input + reset_gate * candidate_recurrent);
        hidden_value = update_gate * previous_hidden[unit] + (1.0f - update_gate) * candidate;

        hidden_state[unit] = hidden_value;
        if (debug_hidden_step != 0) {
            debug_hidden_step[unit] = hidden_value;
        }
    }

    dense_forward_silu(hidden_state, dense_output);
    for (unit = 0u; unit < DENSE_UNITS; ++unit) {
        if (debug_dense_step != 0) {
            debug_dense_step[unit] = dense_output[unit];
        }
    }

    {
        port_float output_scaled = output_forward_linear(dense_output);
        if (output_scaled_value != 0) {
            *output_scaled_value = output_scaled;
        }
        *output_value = inverse_scale_output(output_scaled);
    }
}

static void run_validation_record(const port_float sequence[VALIDATION_SEQ_LEN][GRU_INPUT_DIM],
                                  port_float output_sequence[VALIDATION_SEQ_LEN],
                                  uint32_t reset_state_each_run,
                                  port_float hidden_state[GRU_UNITS],
                                  port_float debug_scaled_input_buffer[VALIDATION_SEQ_LEN][GRU_INPUT_DIM],
                                  port_float debug_gru_hidden_buffer[VALIDATION_SEQ_LEN][GRU_UNITS],
                                  port_float debug_dense_output_buffer[VALIDATION_SEQ_LEN][DENSE_UNITS],
                                  port_float debug_output_scaled_buffer[VALIDATION_SEQ_LEN])
{
    uint32_t step;
    if (reset_state_each_run != 0u) {
        zero_buffer(hidden_state, GRU_UNITS);
    }

    for (step = 0u; step < VALIDATION_SEQ_LEN; ++step) {
        port_float *step_scaled_input = 0;
        port_float *step_hidden = 0;
        port_float *step_dense = 0;
        port_float *step_output_scaled = 0;

        if (debug_scaled_input_buffer != 0) {
            step_scaled_input = debug_scaled_input_buffer[step];
        }
        if (debug_gru_hidden_buffer != 0) {
            step_hidden = debug_gru_hidden_buffer[step];
        }
        if (debug_dense_output_buffer != 0) {
            step_dense = debug_dense_output_buffer[step];
        }
        if (debug_output_scaled_buffer != 0) {
            step_output_scaled = &debug_output_scaled_buffer[step];
        }

        gru_forward_step(
            sequence[step],
            hidden_state,
            step_output_scaled,
            step_scaled_input,
            step_hidden,
            step_dense,
            &output_sequence[step]
        );
    }
}

int main(void)
{
    uint32_t iteration;
    uint32_t record_index;
    uint32_t step_index;
    uint32_t dwt_supported;
    port_float hidden_state[GRU_UNITS];
    port_float output_value = 0.0f;
    uint32_t start_cycles;
    uint32_t end_cycles;
    uint32_t total_cycles = 0u;

    uart_init();
    dwt_supported = dwt_is_counting();
    zero_buffer(hidden_state, GRU_UNITS);

    if (dwt_supported != 0u) {
        start_cycles = dwt_read_cycles();
    }

    for (iteration = 0u; iteration < BENCHMARK_ITERATIONS; ++iteration) {
        for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
            run_validation_record(
                validation_input[record_index],
                validation_output[record_index],
                BENCHMARK_RESET_STATE_EACH_RUN,
                hidden_state,
                0,
                0,
                0,
                0
            );
            output_value = validation_output[record_index][VALIDATION_SEQ_LEN - 1u];
        }
    }

    if (dwt_supported != 0u) {
        end_cycles = dwt_read_cycles();
        total_cycles = end_cycles - start_cycles;
    }

    uart_puts("GRN_QEMU_VALIDATION\n");
    uart_puts("iterations=");
    uart_put_u32(BENCHMARK_ITERATIONS);
    uart_puts("\nrecord_count=");
    uart_put_u32(VALIDATION_RECORD_COUNT);
    uart_puts("\nseq_len=");
    uart_put_u32(VALIDATION_SEQ_LEN);
    uart_puts("\ninput_dim=");
    uart_put_u32(GRU_INPUT_DIM);
    uart_puts("\ngru_units=");
    uart_put_u32(GRU_UNITS);
    uart_puts("\ndense_units=");
    uart_put_u32(DENSE_UNITS);
    uart_puts("\ndwt_supported=");
    uart_put_u32(dwt_supported);
    uart_puts("\ntimer_source=");
    uart_puts(dwt_supported != 0u ? "dwt" : "host_elapsed");
    if (dwt_supported != 0u) {
        uart_puts("\nmeasurement_unit=");
        uart_puts("cycles");
        uart_puts("\nmeasurement_total=");
        uart_put_u32(total_cycles);
        uart_puts("\nmeasurement_per_iter=");
        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));
        uart_puts("\ncycles_total=");
        uart_put_u32(total_cycles);
        uart_puts("\ncycles_per_iter=");
        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));
    }
    uart_puts("\noutput=");
    uart_put_fixed6(output_value);
    uart_puts("\n");
    uart_puts("benchmark_complete=1\n");

    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
        zero_buffer(hidden_state, GRU_UNITS);
        run_validation_record(
            validation_input[record_index],
            validation_output[record_index],
            0u,
            hidden_state,
            debug_scaled_input,
            debug_gru_hidden,
            debug_dense_output,
            debug_output_scaled
        );
    }

    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
        uart_puts("validation_record_");
        uart_put_u32(record_index);
        uart_puts("=");
        for (step_index = 0u; step_index < VALIDATION_SEQ_LEN; ++step_index) {
            if (step_index > 0u) {
                uart_putc(',');
            }
            uart_put_fixed6(validation_output[record_index][step_index]);
        }
        uart_puts("\n");

        uart_puts("validation_input_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_scaled_input[0u][0u], VALIDATION_SEQ_LEN, GRU_INPUT_DIM);
        uart_puts("\n");

        uart_puts("validation_gru_hidden_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_gru_hidden[0u][0u], VALIDATION_SEQ_LEN, GRU_UNITS);
        uart_puts("\n");

        uart_puts("validation_dense_output_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_dense_output[0u][0u], VALIDATION_SEQ_LEN, DENSE_UNITS);
        uart_puts("\n");

        uart_puts("validation_output_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_output_scaled[0u], VALIDATION_SEQ_LEN, 1u);
        uart_puts("\n");
    }
    uart_puts("validation_complete=1\n");

    while (1) {
    }
}
"""


def _render_main_c() -> str:
    return r"""#include <stdint.h>

#include "model_data.h"

#define RCC_BASE 0x40023800u
#define DEMCR (*(volatile uint32_t *)0xE000EDFCu)
#define DWT_CTRL (*(volatile uint32_t *)0xE0001000u)
#define DWT_CYCCNT (*(volatile uint32_t *)0xE0001004u)

#define USART1_BASE 0x40011000u
#define RCC_APB2ENR (*(volatile uint32_t *)(RCC_BASE + 0x44u))
#define USART1_SR (*(volatile uint32_t *)(USART1_BASE + 0x00u))
#define USART1_DR (*(volatile uint32_t *)(USART1_BASE + 0x04u))
#define USART1_BRR (*(volatile uint32_t *)(USART1_BASE + 0x08u))
#define USART1_CR1 (*(volatile uint32_t *)(USART1_BASE + 0x0Cu))

#define RCC_APB2ENR_USART1EN (1u << 4)
#define USART_SR_TXE (1u << 7)
#define USART_CR1_TE (1u << 3)
#define USART_CR1_UE (1u << 13)
#define DEMCR_TRCENA (1u << 24)
#define DWT_CTRL_CYCCNTENA (1u << 0)

static port_float validation_output[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN];
static port_float debug_scaled_input[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM];
static port_float debug_lstm_hidden[VALIDATION_SEQ_LEN][LSTM_UNITS];
static port_float debug_dense_output[VALIDATION_SEQ_LEN][DENSE_UNITS];
static port_float debug_output_scaled[VALIDATION_SEQ_LEN];

static void uart_init(void)
{
    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;
    USART1_BRR = 0x05B2u;
    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;
}

static void uart_putc(char ch)
{
    while ((USART1_SR & USART_SR_TXE) == 0u) {
    }

    USART1_DR = (uint32_t)ch;
}

static void uart_puts(const char *message)
{
    while (*message != '\0') {
        if (*message == '\n') {
            uart_putc('\r');
        }

        uart_putc(*message++);
    }
}

static void uart_put_u32(uint32_t value)
{
    char buffer[11];
    uint32_t index = 0u;

    if (value == 0u) {
        uart_putc('0');
        return;
    }

    while (value > 0u && index < (uint32_t)sizeof(buffer)) {
        buffer[index++] = (char)('0' + (value % 10u));
        value /= 10u;
    }

    while (index > 0u) {
        uart_putc(buffer[--index]);
    }
}

static void uart_put_s32(int32_t value)
{
    if (value < 0) {
        uart_putc('-');
        uart_put_u32((uint32_t)(-value));
        return;
    }

    uart_put_u32((uint32_t)value);
}

static void uart_put_fixed6(port_float value)
{
    int32_t scaled = (int32_t)(value * 1000000.0f);
    int32_t abs_scaled = scaled;
    int32_t integer_part;
    int32_t fraction;
    int32_t divisor = 100000;

    if (scaled < 0) {
        uart_putc('-');
        abs_scaled = -scaled;
    }

    integer_part = abs_scaled / 1000000;
    fraction = abs_scaled % 1000000;

    uart_put_u32((uint32_t)integer_part);
    uart_putc('.');
    while (divisor > 0) {
        uart_putc((char)('0' + ((fraction / divisor) % 10)));
        divisor /= 10;
    }
}

static void uart_put_matrix_rows(const port_float *values,
                                 uint32_t row_count,
                                 uint32_t column_count)
{
    uint32_t row_index;
    for (row_index = 0u; row_index < row_count; ++row_index) {
        uint32_t column_index;
        if (row_index > 0u) {
            uart_putc(';');
        }
        for (column_index = 0u; column_index < column_count; ++column_index) {
            if (column_index > 0u) {
                uart_putc(',');
            }
            uart_put_fixed6(values[row_index * column_count + column_index]);
        }
    }
}

static void dwt_init(void)
{
    DEMCR |= DEMCR_TRCENA;
    DWT_CYCCNT = 0u;
    DWT_CTRL |= DWT_CTRL_CYCCNTENA;
}

static uint32_t dwt_read_cycles(void)
{
    return DWT_CYCCNT;
}

static uint32_t dwt_is_counting(void)
{
    volatile uint32_t spin;
    uint32_t before;
    uint32_t after;

    dwt_init();
    before = dwt_read_cycles();
    for (spin = 0u; spin < 64u; ++spin) {
        __asm volatile ("nop");
    }
    after = dwt_read_cycles();
    return after > before ? 1u : 0u;
}

static port_float tanh_approx(port_float value)
{
    port_float squared;

    if (value > 3.0f) {
        return 0.99505478f;
    }
    if (value < -3.0f) {
        return -0.99505478f;
    }

    squared = value * value;
    return value * (27.0f + squared) / (27.0f + 9.0f * squared);
}

static port_float sigmoid_approx(port_float value)
{
    if (value > 8.0f) {
        return 0.99966466f;
    }
    if (value < -8.0f) {
        return 0.00033535f;
    }
    return 0.5f * (tanh_approx(value * 0.5f) + 1.0f);
}

static port_float relu(port_float value)
{
    return value > 0.0f ? value : 0.0f;
}

static void zero_buffer(port_float *buffer, uint32_t length)
{
    uint32_t index;
    for (index = 0u; index < length; ++index) {
        buffer[index] = 0.0f;
    }
}

static port_float scale_input(port_float value)
{
    if (SCALER_INPUT_DATA_RANGE == 0.0f) {
        return value;
    }
    return value / SCALER_INPUT_DATA_RANGE;
}

static port_float inverse_scale_output(port_float value)
{
    return value * SCALER_OUTPUT_DATA_RANGE;
}

static void dense_forward_relu(const port_float input[LSTM_UNITS],
                               port_float output[DENSE_UNITS])
{
    uint32_t out_index;
    for (out_index = 0u; out_index < DENSE_UNITS; ++out_index) {
        uint32_t input_index;
        port_float sum = dense_bias[out_index];
        for (input_index = 0u; input_index < LSTM_UNITS; ++input_index) {
            sum += input[input_index] * dense_kernel[input_index][out_index];
        }
        output[out_index] = relu(sum);
    }
}

static port_float output_forward_linear(const port_float input[DENSE_UNITS])
{
    uint32_t input_index;
    port_float sum = output_bias[0u];
    for (input_index = 0u; input_index < DENSE_UNITS; ++input_index) {
        sum += input[input_index] * output_kernel[input_index][0u];
    }
    return sum;
}

static void lstm_forward_step(const port_float input_step[LSTM_INPUT_DIM],
                              port_float hidden_state[LSTM_UNITS],
                              port_float cell_state[LSTM_UNITS],
                              port_float *output_scaled_value,
                              port_float debug_scaled_input_step[LSTM_INPUT_DIM],
                              port_float debug_hidden_step[LSTM_UNITS],
                              port_float debug_dense_step[DENSE_UNITS],
                              port_float *output_value)
{
    uint32_t unit;
    uint32_t input_index;
    port_float previous_hidden[LSTM_UNITS];
    port_float previous_cell[LSTM_UNITS];
    port_float dense_output[DENSE_UNITS];
    port_float scaled_input_step[LSTM_INPUT_DIM];

    for (input_index = 0u; input_index < LSTM_INPUT_DIM; ++input_index) {
        scaled_input_step[input_index] = scale_input(input_step[input_index]);
        if (debug_scaled_input_step != 0) {
            debug_scaled_input_step[input_index] = scaled_input_step[input_index];
        }
    }

    for (unit = 0u; unit < LSTM_UNITS; ++unit) {
        previous_hidden[unit] = hidden_state[unit];
        previous_cell[unit] = cell_state[unit];
    }

    for (unit = 0u; unit < LSTM_UNITS; ++unit) {
        uint32_t hidden_index;
        port_float input_gate_acc = lstm_bias[unit + LSTM_UNITS * 0u];
        port_float forget_gate_acc = lstm_bias[unit + LSTM_UNITS * 1u];
        port_float candidate_acc = lstm_bias[unit + LSTM_UNITS * 2u];
        port_float output_gate_acc = lstm_bias[unit + LSTM_UNITS * 3u];

        for (input_index = 0u; input_index < LSTM_INPUT_DIM; ++input_index) {
            port_float input_value = scaled_input_step[input_index];
            input_gate_acc += input_value * lstm_kernel[input_index][unit + LSTM_UNITS * 0u];
            forget_gate_acc += input_value * lstm_kernel[input_index][unit + LSTM_UNITS * 1u];
            candidate_acc += input_value * lstm_kernel[input_index][unit + LSTM_UNITS * 2u];
            output_gate_acc += input_value * lstm_kernel[input_index][unit + LSTM_UNITS * 3u];
        }

        for (hidden_index = 0u; hidden_index < LSTM_UNITS; ++hidden_index) {
            port_float hidden_value = previous_hidden[hidden_index];
            input_gate_acc += hidden_value * lstm_recurrent_kernel[hidden_index][unit + LSTM_UNITS * 0u];
            forget_gate_acc += hidden_value * lstm_recurrent_kernel[hidden_index][unit + LSTM_UNITS * 1u];
            candidate_acc += hidden_value * lstm_recurrent_kernel[hidden_index][unit + LSTM_UNITS * 2u];
            output_gate_acc += hidden_value * lstm_recurrent_kernel[hidden_index][unit + LSTM_UNITS * 3u];
        }

        {
            port_float input_gate = sigmoid_approx(input_gate_acc);
            port_float forget_gate = sigmoid_approx(forget_gate_acc);
            port_float candidate = tanh_approx(candidate_acc);
            port_float output_gate = sigmoid_approx(output_gate_acc);
            port_float cell_value = forget_gate * previous_cell[unit] + input_gate * candidate;
            port_float hidden_value = output_gate * tanh_approx(cell_value);

            cell_state[unit] = cell_value;
            hidden_state[unit] = hidden_value;
            if (debug_hidden_step != 0) {
                debug_hidden_step[unit] = hidden_value;
            }
        }
    }

    dense_forward_relu(hidden_state, dense_output);
    for (unit = 0u; unit < DENSE_UNITS; ++unit) {
        if (debug_dense_step != 0) {
            debug_dense_step[unit] = dense_output[unit];
        }
    }

    {
        port_float output_scaled = output_forward_linear(dense_output);
        if (output_scaled_value != 0) {
            *output_scaled_value = output_scaled;
        }
        *output_value = inverse_scale_output(output_scaled);
    }
}

static void run_validation_record(const port_float sequence[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                  port_float output_sequence[VALIDATION_SEQ_LEN],
                                  uint32_t reset_state_each_run,
                                  port_float hidden_state[LSTM_UNITS],
                                  port_float cell_state[LSTM_UNITS],
                                  port_float debug_scaled_input_buffer[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                  port_float debug_lstm_hidden_buffer[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                  port_float debug_dense_output_buffer[VALIDATION_SEQ_LEN][DENSE_UNITS],
                                  port_float debug_output_scaled_buffer[VALIDATION_SEQ_LEN])
{
    uint32_t step;
    if (reset_state_each_run != 0u) {
        zero_buffer(hidden_state, LSTM_UNITS);
        zero_buffer(cell_state, LSTM_UNITS);
    }

    for (step = 0u; step < VALIDATION_SEQ_LEN; ++step) {
        port_float *step_scaled_input = 0;
        port_float *step_hidden = 0;
        port_float *step_dense = 0;
        port_float *step_output_scaled = 0;

        if (debug_scaled_input_buffer != 0) {
            step_scaled_input = debug_scaled_input_buffer[step];
        }
        if (debug_lstm_hidden_buffer != 0) {
            step_hidden = debug_lstm_hidden_buffer[step];
        }
        if (debug_dense_output_buffer != 0) {
            step_dense = debug_dense_output_buffer[step];
        }
        if (debug_output_scaled_buffer != 0) {
            step_output_scaled = &debug_output_scaled_buffer[step];
        }

        lstm_forward_step(
            sequence[step],
            hidden_state,
            cell_state,
            step_output_scaled,
            step_scaled_input,
            step_hidden,
            step_dense,
            &output_sequence[step]
        );
    }
}

int main(void)
{
    uint32_t iteration;
    uint32_t record_index;
    uint32_t step_index;
    uint32_t dwt_supported;
    port_float hidden_state[LSTM_UNITS];
    port_float cell_state[LSTM_UNITS];
    port_float output_value = 0.0f;
    uint32_t start_cycles;
    uint32_t end_cycles;
    uint32_t total_cycles = 0u;

    uart_init();
    dwt_supported = dwt_is_counting();
    zero_buffer(hidden_state, LSTM_UNITS);
    zero_buffer(cell_state, LSTM_UNITS);

    if (dwt_supported != 0u) {
        start_cycles = dwt_read_cycles();
    }

    for (iteration = 0u; iteration < BENCHMARK_ITERATIONS; ++iteration) {
        for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
            run_validation_record(
                validation_input[record_index],
                validation_output[record_index],
                BENCHMARK_RESET_STATE_EACH_RUN,
                hidden_state,
                cell_state,
                0,
                0,
                0,
                0
            );
            output_value = validation_output[record_index][VALIDATION_SEQ_LEN - 1u];
        }
    }

    if (dwt_supported != 0u) {
        end_cycles = dwt_read_cycles();
        total_cycles = end_cycles - start_cycles;
    }

    uart_puts("LSTM_QEMU_VALIDATION\n");
    uart_puts("iterations=");
    uart_put_u32(BENCHMARK_ITERATIONS);
    uart_puts("\nrecord_count=");
    uart_put_u32(VALIDATION_RECORD_COUNT);
    uart_puts("\nseq_len=");
    uart_put_u32(VALIDATION_SEQ_LEN);
    uart_puts("\ninput_dim=");
    uart_put_u32(LSTM_INPUT_DIM);
    uart_puts("\nlstm_units=");
    uart_put_u32(LSTM_UNITS);
    uart_puts("\ndense_units=");
    uart_put_u32(DENSE_UNITS);
    uart_puts("\ndwt_supported=");
    uart_put_u32(dwt_supported);
    uart_puts("\ntimer_source=");
    uart_puts(dwt_supported != 0u ? "dwt" : "host_elapsed");
    if (dwt_supported != 0u) {
        uart_puts("\nmeasurement_unit=");
        uart_puts("cycles");
        uart_puts("\nmeasurement_total=");
        uart_put_u32(total_cycles);
        uart_puts("\nmeasurement_per_iter=");
        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));
        uart_puts("\ncycles_total=");
        uart_put_u32(total_cycles);
        uart_puts("\ncycles_per_iter=");
        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));
    }
    uart_puts("\noutput=");
    uart_put_fixed6(output_value);
    uart_puts("\n");
    uart_puts("benchmark_complete=1\n");

    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
        zero_buffer(hidden_state, LSTM_UNITS);
        zero_buffer(cell_state, LSTM_UNITS);
        run_validation_record(
            validation_input[record_index],
            validation_output[record_index],
            0u,
            hidden_state,
            cell_state,
            debug_scaled_input,
            debug_lstm_hidden,
            debug_dense_output,
            debug_output_scaled
        );
    }

    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
        uart_puts("validation_record_");
        uart_put_u32(record_index);
        uart_puts("=");
        for (step_index = 0u; step_index < VALIDATION_SEQ_LEN; ++step_index) {
            if (step_index > 0u) {
                uart_putc(',');
            }
            uart_put_fixed6(validation_output[record_index][step_index]);
        }
        uart_puts("\n");

        uart_puts("validation_input_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_scaled_input[0u][0u], VALIDATION_SEQ_LEN, LSTM_INPUT_DIM);
        uart_puts("\n");

        uart_puts("validation_lstm_hidden_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_lstm_hidden[0u][0u], VALIDATION_SEQ_LEN, LSTM_UNITS);
        uart_puts("\n");

        uart_puts("validation_dense_output_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_dense_output[0u][0u], VALIDATION_SEQ_LEN, DENSE_UNITS);
        uart_puts("\n");

        uart_puts("validation_output_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_output_scaled[0u], VALIDATION_SEQ_LEN, 1u);
        uart_puts("\n");
    }
    uart_puts("validation_complete=1\n");

    while (1) {
    }
}
"""


def _parse_benchmark_stdout(stdout: str) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {}
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        try:
            if '.' in value:
                parsed[key] = float(value)
            else:
                parsed[key] = int(value)
        except ValueError:
            parsed[key] = value
    return parsed


def _extract_validation_outputs(parsed_output: Dict[str, Any],
                                validation_artifacts: ValidationArtifacts) -> List[List[float]]:
    c_output_sequences: List[List[float]] = []
    for record_index in range(validation_artifacts.record_count):
        key = f'validation_record_{record_index}'
        if key not in parsed_output:
            raise ValueError(f'QEMU 输出缺少 {key}')
        raw_value = str(parsed_output[key])
        samples = [float(item) for item in raw_value.split(',') if item]
        if len(samples) != validation_artifacts.seq_len:
            raise ValueError(
                f'{key} 样本数不匹配，期望 {validation_artifacts.seq_len}，实际 {len(samples)}'
            )
        c_output_sequences.append(samples)

    if int(parsed_output.get('validation_complete', 0) or 0) != 1:
        raise ValueError('QEMU 输出未标记 validation_complete=1')
    return c_output_sequences


def _extract_c_debug_sequences(parsed_output: Dict[str, Any],
                               validation_artifacts: ValidationArtifacts) -> Dict[str, List[Any]]:
    debug_sequences: Dict[str, List[Any]] = {}

    stage_names = sorted({
        match.group(1)
        for key in parsed_output
        for match in [re.match(r'^validation_(.+)_(\d+)$', key)]
        if match is not None and match.group(1) != 'record'
    })

    for stage_name in stage_names:
        stage_records: List[Any] = []
        for record_index in range(validation_artifacts.record_count):
            key = f'validation_{stage_name}_{record_index}'
            if key not in parsed_output:
                stage_records = []
                break
            matrix = _parse_float_matrix(str(parsed_output[key]))
            if matrix.shape[0] != validation_artifacts.seq_len:
                raise ValueError(
                    f'{key} 样本数不匹配，期望 {validation_artifacts.seq_len}，实际 {matrix.shape[0]}'
                )
            stage_records.append(matrix.tolist())
        if stage_records:
            debug_sequences[stage_name] = stage_records

    return debug_sequences


def _parse_float_matrix(raw_value: str) -> np.ndarray:
    rows = [row for row in raw_value.split(';') if row]
    parsed_rows: List[List[float]] = []
    expected_columns: Optional[int] = None

    for row in rows:
        values = [float(item) for item in row.split(',') if item]
        if expected_columns is None:
            expected_columns = len(values)
        elif len(values) != expected_columns:
            raise ValueError(f'矩阵列数不一致，期望 {expected_columns}，实际 {len(values)}')
        parsed_rows.append(values)

    if not parsed_rows:
        return np.zeros((0, 0), dtype=np.float64)
    return np.asarray(parsed_rows, dtype=np.float64)


def _enrich_benchmark_output(parsed_output: Dict[str, Any],
                             run_workflow: Dict[str, Any],
                             benchmark_config: Dict[str, Any]) -> Dict[str, Any]:
    enriched = dict(parsed_output)
    if 'measurement_per_iter' in enriched:
        return enriched

    run_details = run_workflow.get('run', {})
    elapsed_seconds = float(run_details.get('elapsed_seconds', 0.0))
    iterations = int(enriched.get('iterations', benchmark_config.get('iterations', 0)) or 0)

    enriched['timer_source'] = 'host_elapsed'
    enriched['measurement_unit'] = 'seconds'
    enriched['measurement_total'] = elapsed_seconds
    if iterations > 0:
        enriched['measurement_per_iter'] = elapsed_seconds / iterations
    return enriched


def _write_validation_wave_files(output_root: Path,
                                 validation_artifacts: ValidationArtifacts,
                                 c_output_sequences: Optional[List[List[float]]],
                                 compress: bool,
                                 export_intermediates: bool,
                                 c_debug_sequences: Optional[Dict[str, List[Any]]] = None) -> Dict[str, str]:
    wave_dir = output_root / 'waves'
    wave_dir.mkdir(parents=True, exist_ok=True)

    output_paths: Dict[str, str] = {}
    tf_wave_path = wave_dir / 'tf_output.wave'
    _save_wave_file(
        tf_wave_path,
        source_name='tf_output',
        sequences=[record.tf_output_sequence for record in validation_artifacts.records],
        validation_artifacts=validation_artifacts,
        compress=compress,
    )
    output_paths['tf_output_wave'] = _relative_or_str(tf_wave_path)

    origin_wave_path = wave_dir / 'origin_input.wave'
    _save_wave_file(
        origin_wave_path,
        source_name='origin_input',
        sequences=[[sample[0] for sample in record.input_sequence] for record in validation_artifacts.records],
        validation_artifacts=validation_artifacts,
        compress=compress,
    )
    output_paths['origin_input_wave'] = _relative_or_str(origin_wave_path)

    target_wave_path = wave_dir / 'target_output.wave'
    _save_wave_file(
        target_wave_path,
        source_name='target_output',
        sequences=[record.target_sequence for record in validation_artifacts.records],
        validation_artifacts=validation_artifacts,
        compress=compress,
    )
    output_paths['target_output_wave'] = _relative_or_str(target_wave_path)

    if c_output_sequences is not None:
        c_wave_path = wave_dir / 'c_output.wave'
        _save_wave_file(
            c_wave_path,
            source_name='c_output',
            sequences=c_output_sequences,
            validation_artifacts=validation_artifacts,
            compress=compress,
        )
        output_paths['c_output_wave'] = _relative_or_str(c_wave_path)

    if export_intermediates:
        output_paths.update(_write_intermediate_wave_files(
            wave_dir=wave_dir,
            prefix='tf',
            debug_sequences=validation_artifacts.tf_debug_sequences,
            validation_artifacts=validation_artifacts,
            compress=compress,
        ))
        if c_debug_sequences:
            output_paths.update(_write_intermediate_wave_files(
                wave_dir=wave_dir,
                prefix='c',
                debug_sequences=c_debug_sequences,
                validation_artifacts=validation_artifacts,
                compress=compress,
            ))

    return output_paths


def _write_intermediate_wave_files(wave_dir: Path,
                                   prefix: str,
                                   debug_sequences: Dict[str, List[Any]],
                                   validation_artifacts: ValidationArtifacts,
                                   compress: bool) -> Dict[str, str]:
    output_paths: Dict[str, str] = {}
    for stage_name, sequences in debug_sequences.items():
        wave_path = wave_dir / f'{prefix}_{stage_name}.wave'
        _save_wave_file(
            wave_path,
            source_name=f'{prefix}_{stage_name}',
            sequences=sequences,
            validation_artifacts=validation_artifacts,
            compress=compress,
            channel_names=_build_channel_names(stage_name, sequences),
        )
        output_paths[f'{prefix}_{stage_name}_wave'] = _relative_or_str(wave_path)
    return output_paths


def _build_channel_names(stage_name: str,
                         sequences: Sequence[Sequence[Any]]) -> List[str]:
    if not sequences:
        return [stage_name]

    first = np.asarray(sequences[0], dtype=np.float64)
    if first.ndim == 1:
        channel_count = 1
    elif first.ndim == 2:
        channel_count = int(first.shape[1])
    else:
        raise ValueError(f'波形维度非法: {first.ndim}')

    if channel_count == 1:
        return [stage_name]
    if stage_name == 'iir_output':
        return [f'iir_{index}' for index in range(channel_count)]
    if stage_name == 'lstm_hidden':
        return [f'hidden_{index}' for index in range(channel_count)]
    if stage_name == 'gru_hidden':
        return [f'hidden_{index}' for index in range(channel_count)]
    if stage_name == 'dense_output':
        return [f'dense_{index}' for index in range(channel_count)]
    if stage_name.startswith('kan_layer_'):
        return [f'{stage_name}_{index}' for index in range(channel_count)]
    return [f'{stage_name}_{index}' for index in range(channel_count)]


def _save_wave_file(path: Path,
                    source_name: str,
                    sequences: Sequence[Sequence[float]],
                    validation_artifacts: ValidationArtifacts,
                    compress: bool,
                    channel_names: Optional[Sequence[str]] = None) -> None:
    target_path = path if path.suffix == '.wave' else path.with_suffix('.wave')
    target_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    global_metadata = {
        'standard': {
            'description': f'{source_name} validation waveforms',
            'version': '1.0',
            'creation_date': timestamp,
            'modified_date': timestamp,
            'author': 'qemu-c-inference',
            'tags': ['validation', source_name],
        },
        'user': {
            'dataset_type': validation_artifacts.dataset_type,
            'full_data_path': validation_artifacts.full_data_path,
            'time_window': validation_artifacts.time_window,
        },
    }

    record_data_dict: Dict[str, np.ndarray] = {}
    record_metadata_dict: Dict[str, Dict[str, Any]] = {}
    for index, (record, sequence) in enumerate(zip(validation_artifacts.records, sequences)):
        record_key = f'record_{index}'
        record_values = np.asarray(sequence, dtype=np.float32)
        if record_values.ndim == 1:
            record_values = record_values.reshape(-1, 1)
        if record_values.ndim != 2:
            raise ValueError(f'Wave 数据维度非法，期望 1 或 2 维，实际 {record_values.ndim}')

        resolved_channel_names = list(channel_names) if channel_names is not None else [source_name]
        if len(resolved_channel_names) != int(record_values.shape[1]):
            raise ValueError(
                f'Wave 通道名数量不匹配，期望 {record_values.shape[1]}，实际 {len(resolved_channel_names)}'
            )

        record_data_dict[record_key] = record_values
        record_metadata_dict[record_key] = {
            'standard': {
                'sample_rate': validation_artifacts.sample_rate,
                'channel_names': resolved_channel_names,
                'record_id': record.record_id,
                'creation_date': timestamp,
                'modified_date': timestamp,
                'units': 'V',
            },
            'user': {
                'magnitude': record.magnitude,
                'frequency': record.frequency,
                'source': source_name,
            },
        }

    payload = {
        'metadata': np.array(json.dumps({
            '__format_version__': '1.0',
            'global': global_metadata,
            'records': record_metadata_dict,
        }), dtype='object'),
        **record_data_dict,
    }

    save_func = np.savez_compressed if compress else np.savez
    with open(target_path, 'wb') as file_obj:
        save_func(file_obj, **payload)


def _write_validation_comparison_plots(output_root: Path,
                                       validation_artifacts: ValidationArtifacts,
                                       c_output_sequences: Sequence[Sequence[float]],
                                       dpi: int) -> Dict[str, str]:
    plot_dir = output_root / 'plots'
    plot_dir.mkdir(parents=True, exist_ok=True)

    output_paths: Dict[str, str] = {}
    for index, (record, c_sequence) in enumerate(zip(validation_artifacts.records, c_output_sequences)):
        plot_path = plot_dir / f'{_sanitize_filename(record.record_id)}_comparison.png'
        _save_validation_comparison_plot(
            plot_path=plot_path,
            record=record,
            c_output_sequence=c_sequence,
            sample_rate=validation_artifacts.sample_rate,
            dpi=dpi,
        )
        output_paths[f'comparison_plot_{index}'] = _relative_or_str(plot_path)

    return output_paths


def _save_validation_comparison_plot(plot_path: Path,
                                     record: ValidationRecord,
                                     c_output_sequence: Sequence[float],
                                     sample_rate: float,
                                     dpi: int) -> None:
    origin_values = np.asarray([sample[0] for sample in record.input_sequence], dtype=np.float64)
    target_values = np.asarray(record.target_sequence, dtype=np.float64)
    tf_values = np.asarray(record.tf_output_sequence, dtype=np.float64)
    c_values = np.asarray(c_output_sequence, dtype=np.float64)

    sequence_length = min(len(origin_values), len(target_values), len(tf_values), len(c_values))
    if sequence_length == 0:
        raise ValueError(f'记录 {record.record_id} 没有可绘制的波形数据')

    time_axis = np.arange(sequence_length, dtype=np.float64) / float(sample_rate)

    fig, ax = plt.subplots(figsize=(14, 6))
    try:
        ax.plot(time_axis, origin_values[:sequence_length], label='origin', color='#1f77b4', linewidth=1.4, alpha=0.90)
        ax.plot(time_axis, target_values[:sequence_length], label='target', color='#2ca02c', linewidth=1.4, alpha=0.85)
        ax.plot(time_axis, c_values[:sequence_length], label='c_inference', color='#d62728', linewidth=1.6, alpha=0.85)
        ax.plot(time_axis, tf_values[:sequence_length], label='tf_inference', color='#ff7f0e', linewidth=1.4, alpha=0.85)

        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.set_title(
            f'Waveform Comparison: {record.record_id}\n'
            f'Frequency={record.frequency:.1f} Hz, Magnitude={record.magnitude:.2f}'
        )
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        fig.tight_layout()
        fig.savefig(plot_path, dpi=dpi, bbox_inches='tight')
    finally:
        plt.close(fig)


def _sanitize_filename(value: str) -> str:
    sanitized = ''.join(character if character.isalnum() or character in {'-', '_'} else '_' for character in value)
    return sanitized.strip('_') or 'record'


def _compute_wave_comparison(validation_artifacts: ValidationArtifacts,
                             c_output_sequences: Sequence[Sequence[float]]) -> Dict[str, Any]:
    c_arrays = [np.asarray(sequence, dtype=np.float64) for sequence in c_output_sequences]
    tf_arrays = [
        np.asarray(record.tf_output_sequence, dtype=np.float64)
        for record in validation_artifacts.records
    ]

    per_record: List[Dict[str, Any]] = []
    for record, c_array, tf_array in zip(validation_artifacts.records, c_arrays, tf_arrays):
        diff = c_array - tf_array
        per_record.append({
            'record_id': record.record_id,
            'magnitude': record.magnitude,
            'frequency': record.frequency,
            'mae': float(np.mean(np.abs(diff))),
            'mse': float(np.mean(np.square(diff))),
            'max_abs_error': float(np.max(np.abs(diff))),
            'c_output_stats': _compute_signal_stats(c_array),
            'tf_output_stats': _compute_signal_stats(tf_array),
            'diff_stats': _compute_signal_stats(diff),
        })

    c_flat = np.concatenate(c_arrays) if c_arrays else np.asarray([], dtype=np.float64)
    tf_flat = np.concatenate(tf_arrays) if tf_arrays else np.asarray([], dtype=np.float64)
    diff_flat = c_flat - tf_flat
    overall = {
        'record_count': len(per_record),
        'sample_count': int(diff_flat.size),
        'mae': float(np.mean(np.abs(diff_flat))) if diff_flat.size else 0.0,
        'mse': float(np.mean(np.square(diff_flat))) if diff_flat.size else 0.0,
        'max_abs_error': float(np.max(np.abs(diff_flat))) if diff_flat.size else 0.0,
        'c_output_stats': _compute_signal_stats(c_flat),
        'tf_output_stats': _compute_signal_stats(tf_flat),
        'diff_stats': _compute_signal_stats(diff_flat),
    }
    return {
        'overall': overall,
        'per_record': per_record,
    }


def _compute_intermediate_comparison(validation_artifacts: ValidationArtifacts,
                                     c_debug_sequences: Dict[str, List[Any]]) -> Dict[str, Any]:
    comparisons: Dict[str, Any] = {}
    tf_debug_sequences = validation_artifacts.tf_debug_sequences

    for stage_name in sorted(set(tf_debug_sequences) & set(c_debug_sequences)):
        c_arrays = [np.asarray(sequence, dtype=np.float64) for sequence in c_debug_sequences[stage_name]]
        tf_arrays = [np.asarray(sequence, dtype=np.float64) for sequence in tf_debug_sequences[stage_name]]

        if len(c_arrays) != len(tf_arrays):
            raise ValueError(f'{stage_name} 记录数不匹配，TF={len(tf_arrays)}，C={len(c_arrays)}')

        diff_arrays: List[np.ndarray] = []
        for c_array, tf_array in zip(c_arrays, tf_arrays):
            if c_array.shape != tf_array.shape:
                raise ValueError(f'{stage_name} 形状不匹配，TF={tf_array.shape}，C={c_array.shape}')
            diff_arrays.append(c_array - tf_array)

        c_flat = np.concatenate([array.reshape(-1) for array in c_arrays]) if c_arrays else np.asarray([], dtype=np.float64)
        tf_flat = np.concatenate([array.reshape(-1) for array in tf_arrays]) if tf_arrays else np.asarray([], dtype=np.float64)
        diff_flat = np.concatenate([array.reshape(-1) for array in diff_arrays]) if diff_arrays else np.asarray([], dtype=np.float64)
        channel_count = int(c_arrays[0].shape[1]) if c_arrays and c_arrays[0].ndim == 2 else 1

        comparisons[stage_name] = {
            'record_count': len(c_arrays),
            'sample_count': int(diff_flat.size),
            'channel_count': channel_count,
            'mae': float(np.mean(np.abs(diff_flat))) if diff_flat.size else 0.0,
            'mse': float(np.mean(np.square(diff_flat))) if diff_flat.size else 0.0,
            'max_abs_error': float(np.max(np.abs(diff_flat))) if diff_flat.size else 0.0,
            'c_output_stats': _compute_signal_stats(c_flat),
            'tf_output_stats': _compute_signal_stats(tf_flat),
            'diff_stats': _compute_signal_stats(diff_flat),
        }

    return comparisons


def _compute_signal_stats(values: np.ndarray) -> Dict[str, float]:
    if values.size == 0:
        return {
            'min': 0.0,
            'max': 0.0,
            'mean': 0.0,
            'energy': 0.0,
        }
    return {
        'min': float(np.min(values)),
        'max': float(np.max(values)),
        'mean': float(np.mean(values)),
        'energy': float(np.sum(np.square(values))),
    }


def _aggregate_run_results(run_results: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    host_elapsed = [float(item['workflow'].get('run', {}).get('elapsed_seconds', 0.0)) for item in run_results]
    measurement_values = [
        float(item['parsed_output']['measurement_per_iter'])
        for item in run_results
        if 'measurement_per_iter' in item['parsed_output']
    ]
    cycle_values = [
        int(item['parsed_output']['cycles_per_iter'])
        for item in run_results
        if 'cycles_per_iter' in item['parsed_output'] and int(item['parsed_output']['cycles_per_iter']) > 0
    ]
    measurement_sources = sorted({
        str(item['parsed_output']['timer_source'])
        for item in run_results
        if 'timer_source' in item['parsed_output']
    })
    mae_values = [
        float(item['comparison']['mae'])
        for item in run_results
        if 'comparison' in item and 'mae' in item['comparison']
    ]

    aggregated: Dict[str, Any] = {
        'run_count': len(run_results),
        'avg_host_elapsed_seconds': sum(host_elapsed) / len(host_elapsed) if host_elapsed else 0.0,
    }
    if measurement_values:
        aggregated['avg_measurement_per_iter'] = sum(measurement_values) / len(measurement_values)
    if measurement_sources:
        aggregated['measurement_sources'] = measurement_sources
    if cycle_values:
        aggregated['avg_cycles_per_iter'] = sum(cycle_values) / len(cycle_values)
    if mae_values:
        aggregated['avg_mae'] = sum(mae_values) / len(mae_values)
    return aggregated


def _summarize_qemu_run_workflow(run_workflow: Dict[str, Any]) -> Dict[str, Any]:
    run_details = dict(run_workflow.get('run', {}))
    return {
        'exit_code': int(run_workflow.get('exit_code', 1)),
        'timed_out': bool(run_details.get('timed_out', False)),
        'elapsed_seconds': float(run_details.get('elapsed_seconds', 0.0)),
    }


def _summarize_parsed_output(parsed_output: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in parsed_output.items()
        if not str(key).startswith('validation_')
    }


def _collect_output_files(*paths: Path) -> List[str]:
    output_files: List[str] = []
    for path in paths:
        if path.exists():
            output_files.append(_relative_or_str(path))
    return output_files


def _relative_or_str(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve())).replace('\\', '/')
    except ValueError:
        return str(path)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file_obj:
        json.dump(payload, file_obj, indent=2, ensure_ascii=False)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')