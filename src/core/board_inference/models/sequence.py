"""Native board inference implementations for recurrent and convolutional models.

This module mirrors the non-FRIKAN portions of `core.lstm_qemu_ep_task` so the
refactored board_inference path no longer depends on the legacy monolith at runtime.
"""

from __future__ import annotations

import json
import logging
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np

from core.external_path_parser import ExternalPath
from core.qemu_cli import execute_qemu_workflow

from ..platforms import benchmark_common as common

logger = logging.getLogger(__name__)

SUPPORTED_SEQUENCE_MODEL_TYPES = frozenset({
    'lstm',
    'grn',
    'lstm_transformer',
    'onedcnn',
    'tcn',
    'wavenet2',
    'wavenet3',
})

ValidationRecord = common.ValidationRecord
ValidationArtifacts = common.ValidationArtifacts
KEIL_BENCHMARK_BASE_UVPROJX = common.KEIL_BENCHMARK_BASE_UVPROJX

generate_keil_project = common.generate_keil_project
_normalize_project_path = common._normalize_project_path
_apply_validation_dataset_overrides = common._apply_validation_dataset_overrides
_select_validation_dataset = common._select_validation_dataset
_build_validation_records = common._build_validation_records
_resolve_model_project_dir = common._resolve_model_project_dir
_resolve_weights_json_path = common._resolve_weights_json_path
_resolve_generated_project_dir = common._resolve_generated_project_dir
_normalize_benchmark_config = common._normalize_benchmark_config
_normalize_validation_config = common._normalize_validation_config
_normalize_keil_config = common._normalize_keil_config
_run_keil_build_job = common._run_keil_build_job
_run_keil_program_job = common._run_keil_program_job
_start_keil_serial_capture = common._start_keil_serial_capture
_finish_keil_serial_capture = common._finish_keil_serial_capture
_parse_benchmark_stdout = common._parse_benchmark_stdout
_extract_validation_outputs = common._extract_validation_outputs
_extract_c_debug_sequences = common._extract_c_debug_sequences
_enrich_benchmark_output = common._enrich_benchmark_output
_write_validation_wave_files = common._write_validation_wave_files
_write_validation_comparison_plots = common._write_validation_comparison_plots
_compute_wave_comparison = common._compute_wave_comparison
_compute_intermediate_comparison = common._compute_intermediate_comparison
_load_qemu_reference_comparison = common._load_qemu_reference_comparison
_aggregate_run_results = common._aggregate_run_results
_summarize_qemu_run_workflow = common._summarize_qemu_run_workflow
_summarize_parsed_output = common._summarize_parsed_output
_collect_output_files = common._collect_output_files
_relative_or_str = common._relative_or_str
_write_json = common._write_json
_write_text = common._write_text
_copy_runtime_template = common._copy_runtime_template
_save_wave_file = common._save_wave_file

_LSTM_CELL_PATTERN = re.compile(r'lstm_cell(?:_\d+)?/')
_GRU_CELL_PATTERN = re.compile(r'gru_cell(?:_\d+)?/')


def _load_project_config(model_dir: Path) -> Dict[str, Any]:
    config_path = model_dir / 'config.json'
    if not config_path.exists():
        return {}
    with open(config_path, 'r', encoding='utf-8') as file_obj:
        return json.load(file_obj)


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
        if use_model == '1DCNN':
            return 'onedcnn'
        if use_model == 'TCN':
            return 'tcn'
        if use_model == 'WAVENET2':
            return 'wavenet2'
        if use_model == 'WAVENET3':
            return 'wavenet3'

    with open(weights_json_path, 'r', encoding='utf-8') as file_obj:
        weights = json.load(file_obj)

    weight_names = [str(item.get('name', '')).replace('\\', '/') for item in weights]
    if any(_LSTM_CELL_PATTERN.search(name) for name in weight_names):
        if any('transformer_mha_' in name for name in weight_names):
            return 'lstm_transformer'
        return 'lstm'
    if any(_GRU_CELL_PATTERN.search(name) for name in weight_names):
        return 'grn'
    if any('dense_kan' in name for name in weight_names) and any('simple_rnn' in name for name in weight_names):
        return 'frikan'
    if any(re.fullmatch(r'conv_\d+/kernel:0', name) for name in weight_names):
        return 'onedcnn'
    if any(re.fullmatch(r'temporal_block_\d+_conv_1/kernel:0', name) for name in weight_names):
        return 'tcn'
    if any(name.endswith('output_conv/kernel:0') for name in weight_names):
        return 'wavenet2'
    if any(name.endswith('dense_1/kernel:0') for name in weight_names) and any(name.startswith('initial_conv/') for name in weight_names):
        return 'wavenet3'

    raise ValueError(f'无法自动识别 qemu-c-inference 模型类型: {model_project_name}')


def generate_qemu_project(output_dir: Path,
                          model_spec: Any,
                          benchmark_config: Dict[str, Any],
                          validation_artifacts: ValidationArtifacts,
                          overwrite: bool) -> None:
    """Generate the bare-metal QEMU project for a non-FRIKAN native model."""

    if output_dir.exists() and not overwrite:
        raise FileExistsError(f'QEMU ?????????????: {output_dir}')

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
    elif isinstance(model_spec, WaveNetModelSpec):
        main_c = _render_wavenet_main_c(model_spec)
        model_header = _render_wavenet_model_data_header(model_spec, benchmark_config, validation_artifacts)
    elif isinstance(model_spec, ConvStackModelSpec):
        main_c = _render_conv_stack_main_c(model_spec)
        model_header = _render_conv_stack_model_data_header(model_spec, benchmark_config, validation_artifacts)
    elif isinstance(model_spec, TcnModelSpec):
        main_c = _render_tcn_main_c(model_spec)
        model_header = _render_tcn_model_data_header(model_spec, benchmark_config, validation_artifacts)
    else:
        raise TypeError(f'??????????: {type(model_spec)}')

    main_c = _make_dual_platform_benchmark_c(main_c)
    _write_text(output_dir / 'main.c', main_c)
    _write_text(output_dir / 'model_data.h', model_header)

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
class WaveNetConv1DLayerSpec:
    """WaveNet 系列 Conv1D 层的导出规格。"""

    name: str
    input_channels: int
    output_channels: int
    kernel_size: int
    dilation: int
    activation: str
    kernel: List[List[List[float]]]
    bias: List[float]

@dataclass
class WaveNetModelSpec:
    """WaveNet2/WaveNet3 QEMU C 生成所需的模型规格。"""

    model_project_name: str
    weights_json_path: Path
    model_type: str
    input_dim: int
    initial_conv: WaveNetConv1DLayerSpec
    block_layers: List[WaveNetConv1DLayerSpec]
    post_layers: List[WaveNetConv1DLayerSpec]
    output_layer: Optional[WaveNetConv1DLayerSpec]
    output_dense_kernel: List[List[float]]
    output_dense_bias: List[float]
    use_parallel_blocks: bool
    merge_mode: str
    output_units: int

    @property
    def merged_channels(self) -> int:
        if not self.block_layers:
            return self.initial_conv.output_channels
        if self.merge_mode == 'add':
            return self.block_layers[0].output_channels
        return sum(layer.output_channels for layer in self.block_layers)

    @property
    def final_input_channels(self) -> int:
        if self.post_layers:
            return self.post_layers[-1].output_channels
        if self.block_layers:
            return self.merged_channels
        return self.initial_conv.output_channels

@dataclass
class ConvStackModelSpec:
    """1DCNN 这类顺序 Conv1D 堆叠模型的导出规格。"""

    model_project_name: str
    weights_json_path: Path
    model_type: str
    input_dim: int
    initial_conv: WaveNetConv1DLayerSpec
    conv_layers: List[WaveNetConv1DLayerSpec]
    post_layers: List[WaveNetConv1DLayerSpec]
    output_layer: WaveNetConv1DLayerSpec
    output_units: int

    @property
    def final_input_channels(self) -> int:
        if self.post_layers:
            return self.post_layers[-1].output_channels
        if self.conv_layers:
            return self.conv_layers[-1].output_channels
        return self.initial_conv.output_channels

@dataclass
class TcnTemporalBlockSpec:
    """TCN 单个 temporal block 的导出规格。"""

    block_index: int
    conv1: WaveNetConv1DLayerSpec
    conv2: WaveNetConv1DLayerSpec
    residual_projection: Optional[WaveNetConv1DLayerSpec]
    use_residual: bool
    output_activation: str

    @property
    def output_channels(self) -> int:
        return self.conv2.output_channels

@dataclass
class TcnModelSpec:
    """TCN QEMU C 生成所需的模型规格。"""

    model_project_name: str
    weights_json_path: Path
    model_type: str
    input_dim: int
    initial_projection: Optional[WaveNetConv1DLayerSpec]
    channel_projection: Optional[WaveNetConv1DLayerSpec]
    blocks: List[TcnTemporalBlockSpec]
    post_layers: List[WaveNetConv1DLayerSpec]
    output_layer: Optional[WaveNetConv1DLayerSpec]
    output_dense_kernel: List[List[float]]
    output_dense_bias: List[float]
    output_units: int

    @property
    def block_input_channels(self) -> int:
        if self.channel_projection is not None:
            return self.channel_projection.output_channels
        if self.initial_projection is not None:
            return self.initial_projection.output_channels
        return self.input_dim

    @property
    def final_input_channels(self) -> int:
        if self.post_layers:
            return self.post_layers[-1].output_channels
        if self.blocks:
            return self.blocks[-1].output_channels
        return self.block_input_channels

def execute_sequence_qemu_task(ep_path: ExternalPath,
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
    if model_type not in SUPPORTED_SEQUENCE_MODEL_TYPES:
        raise ValueError(f'?? {model_type} ??? native sequence ???????')
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
    keil_project_dir = generate_keil_project(
        ep_path=ep_path,
        qemu_project_dir=generated_project_dir,
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
        'keil_project_dir': _relative_or_str(keil_project_dir),
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
                keil_project_dir,
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
                keil_project_dir,
                comparison_file,
                *[Path(path) for path in execution_summary.get('wave_paths', {}).values()],
                *[Path(path) for path in execution_summary.get('plot_paths', {}).values()],
        ),
        'action': action,
    })
    logger.info('QEMU C 推理任务完成: %s', summary_path)
    return True

def execute_sequence_keil_bench_task(ep_path: ExternalPath,
                                           config: Dict[str, Any],
                                           keil_overrides: Optional[Dict[str, Any]] = None) -> bool:
    """执行 qemu-c-inference EP 的一键 Keil bench 流程。"""
    ep_path.output_path.mkdir(parents=True, exist_ok=True)

    model_project_name = str(config['model_project_name']).replace('\\', '/')
    benchmark_config = _normalize_benchmark_config(config.get('benchmark_config', {}))
    validation_config = _normalize_validation_config(config.get('validation_config', {}))
    generation_config = config.get('generation_config', {})
    keil_config = _normalize_keil_config(config.get('keil_config', {}), keil_overrides)

    model_dir = _resolve_model_project_dir(model_project_name)
    weights_json_path = _resolve_weights_json_path(model_dir, config.get('weights_file'))
    model_type = _detect_model_type(model_project_name, model_dir, weights_json_path)
    if model_type not in SUPPORTED_SEQUENCE_MODEL_TYPES:
        raise ValueError(f'?? {model_type} ??? native sequence ???????')
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
    keil_project_dir = generate_keil_project(
        ep_path=ep_path,
        qemu_project_dir=generated_project_dir,
        overwrite=overwrite,
    )

    wave_paths = _write_validation_wave_files(
        output_root=ep_path.output_path,
        validation_artifacts=validation_artifacts,
        c_output_sequences=None,
        compress=bool(validation_config['wave_output']['compress']),
        export_intermediates=bool(validation_config['wave_output'].get('export_intermediates', True)),
    )

    keil_project_file = keil_project_dir / 'MDK-ARM' / KEIL_BENCHMARK_BASE_UVPROJX.name
    summary_path = ep_path.output_path / 'keil_benchmark_summary.json'
    comparison_path = ep_path.output_path / 'keil_validation_comparison.json'
    metadata_path = ep_path.output_path / 'keil_benchmark_metadata.json'

    execution_summary: Dict[str, Any] = {
        'task_type': 'qemu-c-inference',
        'action': 'keil-bench',
        'model_type': model_type,
        'model_project_name': model_project_name,
        'weights_json_path': _relative_or_str(weights_json_path),
        'loaded_weights_path': _relative_or_str(validation_artifacts.loaded_weights_path),
        'generated_project_dir': _relative_or_str(generated_project_dir),
        'keil_project_dir': _relative_or_str(keil_project_dir),
        'keil_project_file': _relative_or_str(keil_project_file),
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
        'keil_config': dict(keil_config),
        'wave_paths': wave_paths,
        'status': 'generated',
    }

    action = str(keil_config.get('action', 'build-program-capture'))
    if action == 'generate':
        _write_json(summary_path, execution_summary)
        _write_json(metadata_path, {
            'task_info': config['task_info'],
            'output_files': _collect_output_files(
                summary_path,
                metadata_path,
                generated_project_dir,
                keil_project_dir,
                *[Path(path) for path in wave_paths.values()],
            ),
            'action': 'keil-bench',
        })
        logger.info('Keil benchmark 工程已生成: %s', keil_project_dir)
        return True

    build_result = _run_keil_build_job(
        project_file=keil_project_file,
        keil_config=keil_config,
    )
    execution_summary['keil_build'] = build_result
    if not bool(build_result.get('success', False)):
        execution_summary['status'] = 'build_failed'
        _write_json(summary_path, execution_summary)
        _write_json(metadata_path, {
            'task_info': config['task_info'],
            'output_files': _collect_output_files(summary_path, metadata_path),
            'action': 'keil-bench',
        })
        return False

    if action == 'build':
        execution_summary['status'] = 'build_completed'
        _write_json(summary_path, execution_summary)
        _write_json(metadata_path, {
            'task_info': config['task_info'],
            'output_files': _collect_output_files(
                summary_path,
                metadata_path,
                generated_project_dir,
                keil_project_dir,
                *[Path(path) for path in wave_paths.values()],
            ),
            'action': 'keil-bench',
        })
        return True

    capture_state: Optional[Dict[str, Any]] = None
    capture_result: Optional[Dict[str, Any]] = None
    program_result: Optional[Dict[str, Any]] = None

    try:
        if action == 'build-program-capture':
            capture_state = _start_keil_serial_capture(
                output_dir=ep_path.output_path,
                serial_port=str(keil_config['serial_port']),
                baud_rate=int(keil_config['baud_rate']),
                capture_timeout=int(keil_config['capture_timeout']),
                success_markers=keil_config['success_markers'],
            )

        program_result = _run_keil_program_job(
            project_file=keil_project_file,
            keil_config=keil_config,
        )
        execution_summary['keil_program'] = program_result
    finally:
        if capture_state is not None:
            capture_result = _finish_keil_serial_capture(
                capture_state,
                timeout_seconds=int(keil_config['capture_timeout']) + 10,
            )
            execution_summary['serial_capture'] = capture_result

    if not bool(program_result and program_result.get('success', False)):
        execution_summary['status'] = 'program_failed'
        _write_json(summary_path, execution_summary)
        _write_json(metadata_path, {
            'task_info': config['task_info'],
            'output_files': _collect_output_files(summary_path, metadata_path),
            'action': 'keil-bench',
        })
        return False

    if action == 'build-program':
        execution_summary['status'] = 'program_completed'
        _write_json(summary_path, execution_summary)
        _write_json(metadata_path, {
            'task_info': config['task_info'],
            'output_files': _collect_output_files(summary_path, metadata_path),
            'action': 'keil-bench',
        })
        return True

    if capture_result is None:
        raise RuntimeError('串口抓取结果缺失')

    stream_text_path = Path(str(capture_result['text_path']))
    stream_text = stream_text_path.read_text(encoding='utf-8')
    parsed_output = _parse_benchmark_stdout(stream_text)
    c_output_sequences = _extract_validation_outputs(parsed_output, validation_artifacts)
    comparison_payload = _compute_wave_comparison(validation_artifacts, c_output_sequences)
    keil_wave_path = ep_path.output_path / 'waves' / 'keil_output.wave'
    _save_wave_file(
        keil_wave_path,
        source_name='keil_output',
        sequences=c_output_sequences,
        validation_artifacts=validation_artifacts,
        compress=bool(validation_config['wave_output']['compress']),
    )
    qemu_reference = _load_qemu_reference_comparison(ep_path.output_path, c_output_sequences)

    comparison_payload['wave_paths'] = {
        'keil_output_wave': _relative_or_str(keil_wave_path),
    }
    _write_json(comparison_path, comparison_payload)

    execution_summary['status'] = 'completed'
    execution_summary['serial_capture'] = {
        **capture_result,
        'text_path': _relative_or_str(Path(str(capture_result['text_path']))),
        'jsonl_path': _relative_or_str(Path(str(capture_result['jsonl_path']))),
        'result_path': _relative_or_str(Path(str(capture_result['result_path']))),
    }
    execution_summary['parsed_output'] = _summarize_parsed_output(parsed_output)
    execution_summary['validation_outputs'] = {
        f'record_{index}': sequence
        for index, sequence in enumerate(c_output_sequences)
    }
    execution_summary['comparison'] = comparison_payload['overall']
    execution_summary['comparison_path'] = _relative_or_str(comparison_path)
    execution_summary['keil_wave_paths'] = comparison_payload['wave_paths']
    if qemu_reference is not None:
        execution_summary['qemu_reference_comparison'] = qemu_reference

    _write_json(summary_path, execution_summary)
    _write_json(metadata_path, {
        'task_info': config['task_info'],
        'output_files': _collect_output_files(
            summary_path,
            comparison_path,
            metadata_path,
            generated_project_dir,
            keil_project_dir,
            keil_wave_path,
            *[Path(path) for path in wave_paths.values()],
        ),
        'action': 'keil-bench',
    })
    logger.info('Keil benchmark 任务完成: %s', summary_path)
    return True

def _make_dual_platform_benchmark_c(main_c: str) -> str:
    adapted = main_c.replace('_QEMU_VALIDATION', '_BENCHMARK_VALIDATION')
    adapted = _replace_once(
        adapted,
        '#include "model_data.h"\n',
        '#include "model_data.h"\n\n#if defined(BENCHMARK_PLATFORM_KEIL)\n#include "benchmark_keil_port.h"\n#endif\n',
    )
    adapted = _replace_once(
        adapted,
        'static void uart_init(void)\n{\n    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;\n    USART1_BRR = 0x05B2u;\n    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;\n}\n',
        'static void uart_init(void)\n{\n#if defined(BENCHMARK_PLATFORM_KEIL)\n    benchmark_keil_uart_init();\n#else\n    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;\n    USART1_BRR = 0x05B2u;\n    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;\n#endif\n}\n',
    )
    adapted = _replace_once(
        adapted,
        'static void uart_putc(char ch)\n{\n    while ((USART1_SR & USART_SR_TXE) == 0u) {\n    }\n\n    USART1_DR = (uint32_t)ch;\n}\n',
        'static void uart_putc(char ch)\n{\n#if defined(BENCHMARK_PLATFORM_KEIL)\n    benchmark_keil_uart_putc(ch);\n#else\n    while ((USART1_SR & USART_SR_TXE) == 0u) {\n    }\n\n    USART1_DR = (uint32_t)ch;\n#endif\n}\n',
    )
    adapted = _replace_once(
        adapted,
        '    uart_init();\n',
        '#if defined(BENCHMARK_PLATFORM_KEIL)\n    benchmark_keil_platform_init();\n#endif\n    uart_init();\n',
    )
    adapted = _replace_once(
        adapted,
        'static void uart_put_fixed6(port_float value)\n',
        'static void uart_put_ms_from_us(uint64_t value_us)\n'
        '{\n'
        '    uint32_t whole_ms = (uint32_t)(value_us / 1000u);\n'
        '    uint32_t frac_us = (uint32_t)(value_us % 1000u);\n'
        '\n'
        '    uart_put_u32(whole_ms);\n'
        '    uart_putc(\'.\');\n'
        '    uart_putc((char)(\'0\' + (frac_us / 100u)));\n'
        '    uart_putc((char)(\'0\' + ((frac_us / 10u) % 10u)));\n'
        '    uart_putc((char)(\'0\' + (frac_us % 10u)));\n'
        '    uart_puts("000");\n'
        '}\n'
        '\n'
        'static void uart_put_fixed6(port_float value)\n',
    )
    optional_replacements = (
        (
            '\n    uint32_t total_cycles = 0u;\n',
            '\n    uint32_t total_cycles = 0u;\n'
            '#if defined(BENCHMARK_PLATFORM_KEIL)\n'
            '    uint64_t total_tick_us = 0u;\n'
            '    uint64_t start_tick_us = 0u;\n'
            '    uint64_t end_tick_us = 0u;\n'
            '#endif\n',
        ),
        (
            '\n            start_cycles = dwt_read_cycles();\n',
            '\n            start_cycles = dwt_read_cycles();\n'
            '#if defined(BENCHMARK_PLATFORM_KEIL)\n'
            '            start_tick_us = benchmark_keil_get_tick_us();\n'
            '#endif\n',
        ),
        (
            '\n        start_cycles = dwt_read_cycles();\n',
            '\n        start_cycles = dwt_read_cycles();\n'
            '#if defined(BENCHMARK_PLATFORM_KEIL)\n'
            '        start_tick_us = benchmark_keil_get_tick_us();\n'
            '#endif\n',
        ),
        (
            '\n            total_cycles += (end_cycles - start_cycles);\n',
            '\n            total_cycles += (end_cycles - start_cycles);\n'
            '#if defined(BENCHMARK_PLATFORM_KEIL)\n'
            '            end_tick_us = benchmark_keil_get_tick_us();\n'
            '            total_tick_us += (end_tick_us - start_tick_us);\n'
            '#endif\n',
        ),
        (
            '\n        total_cycles = end_cycles - start_cycles;\n',
            '\n        total_cycles = end_cycles - start_cycles;\n'
            '#if defined(BENCHMARK_PLATFORM_KEIL)\n'
            '        end_tick_us = benchmark_keil_get_tick_us();\n'
            '        total_tick_us = end_tick_us - start_tick_us;\n'
            '#endif\n',
        ),
        (
            '\n        uart_puts("\\ncycles_per_iter=");\n'
            '        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));\n'
            '    }\n',
            '\n        uart_puts("\\ncycles_per_iter=");\n'
            '        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));\n'
            '#if defined(BENCHMARK_PLATFORM_KEIL)\n'
            '        uart_puts("\\nwall_time_unit=");\n'
            '        uart_puts("ms");\n'
            '        uart_puts("\\nwall_time_total_ms=");\n'
            '        uart_put_ms_from_us(total_tick_us);\n'
            '        uart_puts("\\nwall_time_per_iter_ms=");\n'
            '        uart_put_ms_from_us(BENCHMARK_ITERATIONS == 0u ? 0u : (total_tick_us / (uint64_t)BENCHMARK_ITERATIONS));\n'
            '#endif\n'
            '    }\n',
        ),
    )
    for old, new in optional_replacements:
        if old in adapted:
            adapted = _replace_once(adapted, old, new)
    return _disable_benchmark_uart_helper_inlining(adapted)

def _disable_benchmark_uart_helper_inlining(content: str) -> str:
    """Keep the benchmark text output helpers out-of-line to avoid Keil code bloat."""
    replacements = (
        ('static void uart_putc(char ch)\n', 'static __attribute__((noinline)) void uart_putc(char ch)\n'),
        ('static void uart_puts(const char *message)\n', 'static __attribute__((noinline)) void uart_puts(const char *message)\n'),
        ('static void uart_put_u32(uint32_t value)\n', 'static __attribute__((noinline)) void uart_put_u32(uint32_t value)\n'),
        ('static void uart_put_ms_from_us(uint64_t value_us)\n', 'static __attribute__((noinline)) void uart_put_ms_from_us(uint64_t value_us)\n'),
        ('static void uart_put_fixed6(port_float value)\n', 'static __attribute__((noinline)) void uart_put_fixed6(port_float value)\n'),
        (
            'static void uart_put_matrix_rows(const port_float *values,\n',
            'static __attribute__((noinline)) void uart_put_matrix_rows(const port_float *values,\n',
        ),
    )
    adapted = content
    for old, new in replacements:
        adapted = _replace_once(adapted, old, new)
    return adapted

def _replace_once(content: str, old: str, new: str) -> str:
    if old not in content:
        raise ValueError(f'生成代码结构已变化，未找到预期片段: {old.splitlines()[0]}')
    return content.replace(old, new, 1)

def _prepare_validation_artifacts(model_project_name: str,
                                  weights_json_path: Path,
                                  validation_config: Dict[str, Any],
                                  model_type: str,
                                  model_spec: Any) -> ValidationArtifacts:
    from ...model_engine import ModelEngine
    from ...project_manager import ProjectManager

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

    if model_type in {'wavenet2', 'wavenet3'}:
        stage_names, stage_outputs = _collect_wavenet_stage_outputs(keras_model, model_type)
        intermediate_model = tf.keras.Model(inputs=keras_model.input, outputs=stage_outputs)
        predicted_outputs = intermediate_model.predict(
            x_scaled,
            batch_size=max(1, batch_size),
            verbose=0,
        )
        if not isinstance(predicted_outputs, list):
            predicted_outputs = [predicted_outputs]

        debug_sequences = {
            'input_scaled': _split_batch_sequences(x_scaled),
        }
        for stage_name, stage_output in zip(stage_names, predicted_outputs):
            debug_sequences[stage_name] = _split_batch_sequences(stage_output)
        return debug_sequences

    if model_type == 'onedcnn':
        stage_names, stage_outputs = _collect_conv_stack_stage_outputs(keras_model)
        intermediate_model = tf.keras.Model(inputs=keras_model.input, outputs=stage_outputs)
        predicted_outputs = intermediate_model.predict(
            x_scaled,
            batch_size=max(1, batch_size),
            verbose=0,
        )
        if not isinstance(predicted_outputs, list):
            predicted_outputs = [predicted_outputs]

        debug_sequences = {
            'input_scaled': _split_batch_sequences(x_scaled),
        }
        for stage_name, stage_output in zip(stage_names, predicted_outputs):
            debug_sequences[stage_name] = _split_batch_sequences(stage_output)
        return debug_sequences

    if model_type == 'tcn':
        stage_names, stage_outputs = _collect_tcn_stage_outputs(keras_model)
        intermediate_model = tf.keras.Model(inputs=keras_model.input, outputs=stage_outputs)
        predicted_outputs = intermediate_model.predict(
            x_scaled,
            batch_size=max(1, batch_size),
            verbose=0,
        )
        if not isinstance(predicted_outputs, list):
            predicted_outputs = [predicted_outputs]

        debug_sequences = {
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

def _collect_wavenet_stage_outputs(keras_model: Any,
                                   model_type: str) -> tuple[List[str], List[Any]]:
    stage_names: List[str] = ['initial_conv']
    stage_outputs: List[Any] = [keras_model.get_layer('initial_conv').output]

    if model_type == 'wavenet2':
        block_conv_indices = sorted({
            int(match.group(1))
            for layer in keras_model.layers
            for match in [re.fullmatch(r'conv1d_(\d+)', layer.name)]
            if match is not None
        })
        for block_index, layer_index in enumerate(block_conv_indices):
            layer_name = f'conv1d_{layer_index}'
            stage_names.append(f'conv_block_{block_index}')
            stage_outputs.append(keras_model.get_layer(layer_name).output)

    post_dense_indices = sorted({
        int(match.group(1))
        for layer in keras_model.layers
        for match in [re.fullmatch(r'post_dense_(\d+)', layer.name)]
        if match is not None
    })
    for layer_index in post_dense_indices:
        stage_names.append(f'post_dense_{layer_index}')
        stage_outputs.append(keras_model.get_layer(f'post_dense_{layer_index}').output)

    output_layer_name = 'output_conv' if model_type == 'wavenet2' else 'dense_1'
    stage_names.append('output_scaled')
    stage_outputs.append(keras_model.get_layer(output_layer_name).output)
    return stage_names, stage_outputs

def _collect_conv_stack_stage_outputs(keras_model: Any) -> tuple[List[str], List[Any]]:
    stage_names: List[str] = ['initial_conv']
    stage_outputs: List[Any] = [_get_layer_output_by_candidates(keras_model, 'conv_activation_1', 'conv_1')]

    conv_layer_indices = sorted({
        int(match.group(1))
        for layer in keras_model.layers
        for match in [re.fullmatch(r'conv_(\d+)', layer.name)]
        if match is not None
    })
    for layer_index in conv_layer_indices:
        if layer_index <= 1:
            continue
        stage_names.append(f'conv_block_{layer_index - 2}')
        stage_outputs.append(
            _get_layer_output_by_candidates(
                keras_model,
                f'conv_activation_{layer_index}',
                f'conv_{layer_index}',
            )
        )

    post_dense_indices = sorted({
        int(match.group(1))
        for layer in keras_model.layers
        for match in [re.fullmatch(r'post_dense_(\d+)', layer.name)]
        if match is not None
    })
    for layer_index in post_dense_indices:
        stage_names.append(f'post_dense_{layer_index}')
        stage_outputs.append(
            _get_layer_output_by_candidates(
                keras_model,
                f'post_dense_activation_{layer_index}',
                f'post_dense_{layer_index}',
            )
        )

    stage_names.append('output_scaled')
    stage_outputs.append(keras_model.get_layer('output_conv').output)
    return stage_names, stage_outputs

def _collect_tcn_stage_outputs(keras_model: Any) -> tuple[List[str], List[Any]]:
    stage_names: List[str] = []
    stage_outputs: List[Any] = []

    if _has_layer(keras_model, 'initial_projection') or _has_layer(keras_model, 'initial_projection_activation'):
        stage_names.append('initial_projection')
        stage_outputs.append(
            _get_layer_output_by_candidates(
                keras_model,
                'initial_projection_activation',
                'initial_projection',
            )
        )

    if _has_layer(keras_model, 'channel_projection'):
        stage_names.append('channel_projection')
        stage_outputs.append(keras_model.get_layer('channel_projection').output)

    block_indices = sorted({
        int(match.group(1))
        for layer in keras_model.layers
        for match in [re.fullmatch(r'temporal_block_(\d+)_conv_1', layer.name)]
        if match is not None
    })
    for block_index in block_indices:
        stage_names.append(f'tcn_block_{block_index}')
        stage_outputs.append(
            _get_layer_output_by_candidates(
                keras_model,
                f'temporal_block_{block_index}_output_activation',
                f'temporal_block_{block_index}_residual_add',
                f'temporal_block_{block_index}_conv_2',
            )
        )

    post_dense_indices = sorted({
        int(match.group(1))
        for layer in keras_model.layers
        for match in [re.fullmatch(r'post_dense_(\d+)', layer.name)]
        if match is not None
    })
    for layer_index in post_dense_indices:
        stage_names.append(f'post_dense_{layer_index}')
        stage_outputs.append(
            _get_layer_output_by_candidates(
                keras_model,
                f'post_dense_activation_{layer_index}',
                f'post_dense_{layer_index}',
            )
        )

    output_layer_name = 'output_conv' if _has_layer(keras_model, 'output_conv') else 'output_dense'
    stage_names.append('output_scaled')
    stage_outputs.append(keras_model.get_layer(output_layer_name).output)
    return stage_names, stage_outputs

def _has_layer(keras_model: Any, layer_name: str) -> bool:
    try:
        keras_model.get_layer(layer_name)
    except ValueError:
        return False
    return True

def _get_layer_output_by_candidates(keras_model: Any, *layer_names: str) -> Any:
    for layer_name in layer_names:
        if not layer_name:
            continue
        try:
            return keras_model.get_layer(layer_name).output
        except ValueError:
            continue
    raise ValueError(f'未找到任一候选层输出: {layer_names}')

def _resolve_reference_weights_path(weights_json_path: Path) -> Path:
    weights_h5_path = weights_json_path.with_suffix('.h5')
    if weights_h5_path.exists():
        return weights_h5_path
    return weights_json_path

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
    if model_type == 'onedcnn':
        return _load_conv_stack_model_spec(model_project_name, model_dir, weights_json_path)
    if model_type == 'tcn':
        return _load_tcn_model_spec(model_project_name, model_dir, weights_json_path)
    if model_type in {'wavenet2', 'wavenet3'}:
        return _load_wavenet_model_spec(
            model_project_name=model_project_name,
            model_dir=model_dir,
            weights_json_path=weights_json_path,
            model_type=model_type,
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

def _load_conv_stack_model_spec(model_project_name: str,
                                model_dir: Path,
                                weights_json_path: Path) -> ConvStackModelSpec:
    with open(weights_json_path, 'r', encoding='utf-8') as file_obj:
        weights = json.load(file_obj)

    project_config = _load_project_config(model_dir)
    model_subcfg = project_config.get('model_subcfg', {}) if isinstance(project_config.get('model_subcfg', {}), dict) else {}

    final_activation = str(model_subcfg.get('final_activation', 'linear') or 'linear').strip().lower()
    if final_activation not in {'linear', 'identity', 'none'}:
        raise ValueError(f'当前 qemu-c-inference 暂不支持 1DCNN final_activation={final_activation}')

    conv_activation = str(model_subcfg.get('conv_activation') or project_config.get('activation', 'linear') or 'linear').strip().lower()
    post_activation = str(model_subcfg.get('post_dense_activation', 'linear') or 'linear').strip().lower()

    conv_names = sorted({
        str(item.get('name', '')).replace('\\', '/').split('/')[0]
        for item in weights
        if re.fullmatch(r'conv_\d+/kernel:0', str(item.get('name', '')).replace('\\', '/'))
    }, key=_conv_stack_layer_sort_key)
    if not conv_names:
        raise ValueError('1DCNN 权重中未找到 conv_* 卷积层')

    initial_conv = _load_wavenet_conv1d_layer(weights, conv_names[0], activation=conv_activation, dilation=1)
    conv_layers = [
        _load_wavenet_conv1d_layer(weights, layer_name, activation=conv_activation, dilation=1)
        for layer_name in conv_names[1:]
    ]
    post_layers = _load_wavenet_post_layers(weights, activation=post_activation)
    output_layer = _load_wavenet_conv1d_layer(weights, 'output_conv', activation='linear', dilation=1)

    model_spec = ConvStackModelSpec(
        model_project_name=model_project_name,
        weights_json_path=weights_json_path,
        model_type='onedcnn',
        input_dim=1,
        initial_conv=initial_conv,
        conv_layers=conv_layers,
        post_layers=post_layers,
        output_layer=output_layer,
        output_units=1,
    )
    _validate_conv_stack_model_spec(model_spec)
    return model_spec

def _load_tcn_model_spec(model_project_name: str,
                         model_dir: Path,
                         weights_json_path: Path) -> TcnModelSpec:
    with open(weights_json_path, 'r', encoding='utf-8') as file_obj:
        weights = json.load(file_obj)

    project_config = _load_project_config(model_dir)
    model_subcfg = project_config.get('model_subcfg', {}) if isinstance(project_config.get('model_subcfg', {}), dict) else {}

    if bool(model_subcfg.get('use_gating', False)):
        raise ValueError('当前 qemu-c-inference 暂不支持 TCN use_gating=True')
    if bool(model_subcfg.get('use_parallel_blocks', False)):
        raise ValueError('当前 qemu-c-inference 暂不支持 TCN use_parallel_blocks=True')
    if bool(model_subcfg.get('combine_blocks_by_add', False)):
        raise ValueError('当前 qemu-c-inference 暂不支持 TCN combine_blocks_by_add=True')
    if bool(model_subcfg.get('block_dense', False)):
        raise ValueError('当前 qemu-c-inference 暂不支持 TCN block_dense=True')

    final_activation = str(model_subcfg.get('final_activation', 'linear') or 'linear').strip().lower()
    if final_activation not in {'linear', 'identity', 'none'}:
        raise ValueError(f'当前 qemu-c-inference 暂不支持 TCN final_activation={final_activation}')

    block_activation = str(model_subcfg.get('block_activation') or project_config.get('activation', 'linear') or 'linear').strip().lower()
    post_activation = str(model_subcfg.get('post_dense_activation', 'linear') or 'linear').strip().lower()
    dilations = [int(item) for item in model_subcfg.get('dilations', [])]
    use_residual = bool(model_subcfg.get('use_residual', True))

    initial_projection = None
    if not bool(model_subcfg.get('skip_initial_conv', False)):
        initial_projection = _load_wavenet_conv1d_layer(
            weights,
            'initial_projection',
            activation=block_activation,
            dilation=1,
        )

    channel_projection = _load_optional_conv1d_layer(
        weights,
        'channel_projection',
        activation='linear',
        dilation=1,
    )

    block_indices = sorted({
        int(match.group(1))
        for item in weights
        for match in [re.fullmatch(r'temporal_block_(\d+)_conv_1/kernel:0', str(item.get('name', '')).replace('\\', '/'))]
        if match is not None
    })
    if not block_indices:
        raise ValueError('TCN 权重中未找到 temporal_block_*_conv_1 卷积层')

    blocks: List[TcnTemporalBlockSpec] = []
    for list_index, block_index in enumerate(block_indices):
        dilation = dilations[list_index] if list_index < len(dilations) else 1
        residual_projection = _load_optional_conv1d_layer(
            weights,
            f'temporal_block_{block_index}_residual_projection',
            activation='linear',
            dilation=1,
        )
        blocks.append(TcnTemporalBlockSpec(
            block_index=block_index,
            conv1=_load_wavenet_conv1d_layer(
                weights,
                f'temporal_block_{block_index}_conv_1',
                activation=block_activation,
                dilation=dilation,
            ),
            conv2=_load_wavenet_conv1d_layer(
                weights,
                f'temporal_block_{block_index}_conv_2',
                activation=block_activation,
                dilation=dilation,
            ),
            residual_projection=residual_projection,
            use_residual=use_residual,
            output_activation=block_activation,
        ))

    post_layers = _load_wavenet_post_layers(weights, activation=post_activation)

    output_layer: Optional[WaveNetConv1DLayerSpec] = None
    output_dense_kernel = _zero_matrix(1, 1)
    output_dense_bias = [0.0]
    if bool(model_subcfg.get('skip_output_conv', False)):
        output_kernel = _find_weight_entry(weights, 'output_dense/kernel')
        output_bias = _find_weight_entry(weights, 'output_dense/bias')
        if list(output_bias['shape']) != [1]:
            raise ValueError(f'TCN 输出 dense bias 形状非法: {output_bias["shape"]}')
        if list(output_kernel['shape'])[1] != 1:
            raise ValueError(f'TCN 输出 dense kernel 形状非法: {output_kernel["shape"]}')
        output_dense_kernel = _to_float_matrix(output_kernel['value'])
        output_dense_bias = _to_float_vector(output_bias['value'])
    else:
        output_layer = _load_wavenet_conv1d_layer(weights, 'output_conv', activation='linear', dilation=1)

    model_spec = TcnModelSpec(
        model_project_name=model_project_name,
        weights_json_path=weights_json_path,
        model_type='tcn',
        input_dim=1,
        initial_projection=initial_projection,
        channel_projection=channel_projection,
        blocks=blocks,
        post_layers=post_layers,
        output_layer=output_layer,
        output_dense_kernel=output_dense_kernel,
        output_dense_bias=output_dense_bias,
        output_units=1,
    )
    _validate_tcn_model_spec(model_spec)
    return model_spec

def _load_wavenet_model_spec(model_project_name: str,
                             model_dir: Path,
                             weights_json_path: Path,
                             model_type: str) -> WaveNetModelSpec:
    with open(weights_json_path, 'r', encoding='utf-8') as file_obj:
        weights = json.load(file_obj)

    project_config = _load_project_config(model_dir)
    model_subcfg = project_config.get('model_subcfg', {}) if isinstance(project_config.get('model_subcfg', {}), dict) else {}

    if bool(model_subcfg.get('skip_initial_conv', False)):
        raise ValueError('当前 qemu-c-inference 暂不支持 skip_initial_conv=True 的 WaveNet 模型')
    if bool(model_subcfg.get('use_gating', False)):
        raise ValueError('当前 qemu-c-inference 暂不支持 use_gating=True 的 WaveNet 模型')
    if bool(model_subcfg.get('use_residual', False)):
        raise ValueError('当前 qemu-c-inference 暂不支持 use_residual=True 的 WaveNet 模型')
    if bool(model_subcfg.get('block_dense', False)):
        raise ValueError('当前 qemu-c-inference 暂不支持 block_dense=True 的 WaveNet 模型')

    final_activation = str(model_subcfg.get('final_activation', 'linear') or 'linear').strip().lower()
    if final_activation not in {'linear', 'identity', 'none'}:
        raise ValueError(f'当前 qemu-c-inference 暂不支持 final_activation={final_activation}')

    initial_conv = _load_wavenet_conv1d_layer(weights, 'initial_conv', activation='linear', dilation=1)
    block_activation = str(model_subcfg.get('block_activation', 'linear') or 'linear').strip().lower()
    post_activation = str(model_subcfg.get('post_dense_activation', 'linear') or 'linear').strip().lower()
    block_layers = _load_wavenet_block_layers(
        weights,
        dilations=list(model_subcfg.get('dilations', [])),
        activation=block_activation,
    ) if model_type == 'wavenet2' else []
    post_layers = _load_wavenet_post_layers(weights, activation=post_activation)

    merge_mode = 'concat'
    if model_type == 'wavenet2' and bool(model_subcfg.get('combine_blocks_by_add', True)):
        merge_mode = 'add'

    output_layer: Optional[WaveNetConv1DLayerSpec] = None
    output_dense_kernel = _zero_matrix(initial_conv.output_channels, 1)
    output_dense_bias = [0.0]
    if model_type == 'wavenet2':
        if bool(model_subcfg.get('skip_output_conv', False)):
            raise ValueError('当前 qemu-c-inference 暂不支持 skip_output_conv=True 的 WaveNet2 模型')
        output_layer = _load_wavenet_conv1d_layer(weights, 'output_conv', activation='linear', dilation=1)
    else:
        output_kernel = _find_weight_entry(weights, 'dense_1/kernel')
        output_bias = _find_weight_entry(weights, 'dense_1/bias')
        if list(output_bias['shape']) != [1]:
            raise ValueError(f'WaveNet3 输出 bias 形状非法: {output_bias["shape"]}')
        if list(output_kernel['shape'])[1] != 1:
            raise ValueError(f'WaveNet3 输出 kernel 形状非法: {output_kernel["shape"]}')
        output_dense_kernel = _to_float_matrix(output_kernel['value'])
        output_dense_bias = _to_float_vector(output_bias['value'])

    model_spec = WaveNetModelSpec(
        model_project_name=model_project_name,
        weights_json_path=weights_json_path,
        model_type=model_type,
        input_dim=1,
        initial_conv=initial_conv,
        block_layers=block_layers,
        post_layers=post_layers,
        output_layer=output_layer,
        output_dense_kernel=output_dense_kernel,
        output_dense_bias=output_dense_bias,
        use_parallel_blocks=bool(model_subcfg.get('use_parallel_blocks', False)),
        merge_mode=merge_mode,
        output_units=1,
    )
    _validate_wavenet_model_spec(model_spec)
    return model_spec

def _validate_wavenet_model_spec(model_spec: WaveNetModelSpec) -> None:
    if model_spec.merge_mode == 'add' and model_spec.block_layers:
        expected_channels = model_spec.block_layers[0].output_channels
        for layer in model_spec.block_layers[1:]:
            if layer.output_channels != expected_channels:
                raise ValueError('WaveNet 按 add 合并时，各 block 输出通道数必须一致')

    expected_channels = model_spec.merged_channels if model_spec.block_layers else model_spec.initial_conv.output_channels
    for layer in model_spec.post_layers:
        if layer.kernel_size != 1:
            raise ValueError(f'当前 qemu-c-inference 仅支持 kernel_size=1 的 post_dense 层，实际 {layer.name}={layer.kernel_size}')
        if layer.input_channels != expected_channels:
            raise ValueError(
                f'{layer.name} 输入通道数非法，期望 {expected_channels}，实际 {layer.input_channels}'
            )
        expected_channels = layer.output_channels

    if model_spec.output_layer is not None:
        if model_spec.output_layer.kernel_size != 1:
            raise ValueError(f'当前 qemu-c-inference 仅支持 kernel_size=1 的 output_conv，实际 {model_spec.output_layer.kernel_size}')
        if model_spec.output_layer.input_channels != expected_channels:
            raise ValueError(
                f'output_conv 输入通道数非法，期望 {expected_channels}，实际 {model_spec.output_layer.input_channels}'
            )
        if model_spec.output_layer.output_channels != model_spec.output_units:
            raise ValueError(
                f'output_conv 输出通道数非法，期望 {model_spec.output_units}，实际 {model_spec.output_layer.output_channels}'
            )
    else:
        if len(model_spec.output_dense_kernel) != expected_channels:
            raise ValueError(
                f'WaveNet3 输出层输入通道数非法，期望 {expected_channels}，实际 {len(model_spec.output_dense_kernel)}'
            )
        if any(len(row) != model_spec.output_units for row in model_spec.output_dense_kernel):
            raise ValueError('WaveNet3 输出层 kernel 形状非法')
        if len(model_spec.output_dense_bias) != model_spec.output_units:
            raise ValueError('WaveNet3 输出层 bias 形状非法')

def _validate_conv_stack_model_spec(model_spec: ConvStackModelSpec) -> None:
    expected_channels = model_spec.initial_conv.output_channels
    for layer in model_spec.conv_layers:
        if layer.input_channels != expected_channels:
            raise ValueError(
                f'{layer.name} 输入通道数非法，期望 {expected_channels}，实际 {layer.input_channels}'
            )
        expected_channels = layer.output_channels

    for layer in model_spec.post_layers:
        if layer.kernel_size != 1:
            raise ValueError(f'当前 qemu-c-inference 仅支持 kernel_size=1 的 post_dense 层，实际 {layer.name}={layer.kernel_size}')
        if layer.input_channels != expected_channels:
            raise ValueError(
                f'{layer.name} 输入通道数非法，期望 {expected_channels}，实际 {layer.input_channels}'
            )
        expected_channels = layer.output_channels

    if model_spec.output_layer.kernel_size != 1:
        raise ValueError(f'当前 qemu-c-inference 仅支持 kernel_size=1 的 output_conv，实际 {model_spec.output_layer.kernel_size}')
    if model_spec.output_layer.input_channels != expected_channels:
        raise ValueError(
            f'output_conv 输入通道数非法，期望 {expected_channels}，实际 {model_spec.output_layer.input_channels}'
        )
    if model_spec.output_layer.output_channels != model_spec.output_units:
        raise ValueError(
            f'output_conv 输出通道数非法，期望 {model_spec.output_units}，实际 {model_spec.output_layer.output_channels}'
        )

def _validate_tcn_model_spec(model_spec: TcnModelSpec) -> None:
    expected_channels = model_spec.input_dim
    if model_spec.initial_projection is not None:
        if model_spec.initial_projection.kernel_size != 1:
            raise ValueError('TCN initial_projection 仅支持 kernel_size=1')
        if model_spec.initial_projection.input_channels != expected_channels:
            raise ValueError(
                f'initial_projection 输入通道数非法，期望 {expected_channels}，实际 {model_spec.initial_projection.input_channels}'
            )
        expected_channels = model_spec.initial_projection.output_channels

    if model_spec.channel_projection is not None:
        if model_spec.channel_projection.kernel_size != 1:
            raise ValueError('TCN channel_projection 仅支持 kernel_size=1')
        if model_spec.channel_projection.input_channels != expected_channels:
            raise ValueError(
                f'channel_projection 输入通道数非法，期望 {expected_channels}，实际 {model_spec.channel_projection.input_channels}'
            )
        expected_channels = model_spec.channel_projection.output_channels

    for block in model_spec.blocks:
        if block.conv1.input_channels != expected_channels:
            raise ValueError(
                f'temporal_block_{block.block_index}_conv_1 输入通道数非法，期望 {expected_channels}，实际 {block.conv1.input_channels}'
            )
        if block.conv2.input_channels != block.conv1.output_channels:
            raise ValueError(
                f'temporal_block_{block.block_index}_conv_2 输入通道数非法，期望 {block.conv1.output_channels}，实际 {block.conv2.input_channels}'
            )
        if block.use_residual and expected_channels != block.output_channels and block.residual_projection is None:
            raise ValueError(
                f'temporal_block_{block.block_index} 缺少 residual_projection，无法将 {expected_channels} 通道映射到 {block.output_channels}'
            )
        if block.residual_projection is not None:
            if block.residual_projection.kernel_size != 1:
                raise ValueError(f'temporal_block_{block.block_index}_residual_projection 仅支持 kernel_size=1')
            if block.residual_projection.input_channels != expected_channels:
                raise ValueError(
                    f'temporal_block_{block.block_index}_residual_projection 输入通道数非法，期望 {expected_channels}，实际 {block.residual_projection.input_channels}'
                )
            if block.residual_projection.output_channels != block.output_channels:
                raise ValueError(
                    f'temporal_block_{block.block_index}_residual_projection 输出通道数非法，期望 {block.output_channels}，实际 {block.residual_projection.output_channels}'
                )
        expected_channels = block.output_channels

    for layer in model_spec.post_layers:
        if layer.kernel_size != 1:
            raise ValueError(f'当前 qemu-c-inference 仅支持 kernel_size=1 的 post_dense 层，实际 {layer.name}={layer.kernel_size}')
        if layer.input_channels != expected_channels:
            raise ValueError(
                f'{layer.name} 输入通道数非法，期望 {expected_channels}，实际 {layer.input_channels}'
            )
        expected_channels = layer.output_channels

    if model_spec.output_layer is not None:
        if model_spec.output_layer.kernel_size != 1:
            raise ValueError(f'当前 qemu-c-inference 仅支持 kernel_size=1 的 output_conv，实际 {model_spec.output_layer.kernel_size}')
        if model_spec.output_layer.input_channels != expected_channels:
            raise ValueError(
                f'output_conv 输入通道数非法，期望 {expected_channels}，实际 {model_spec.output_layer.input_channels}'
            )
        if model_spec.output_layer.output_channels != model_spec.output_units:
            raise ValueError(
                f'output_conv 输出通道数非法，期望 {model_spec.output_units}，实际 {model_spec.output_layer.output_channels}'
            )
    else:
        if len(model_spec.output_dense_kernel) != expected_channels:
            raise ValueError(
                f'TCN 输出 dense 输入通道数非法，期望 {expected_channels}，实际 {len(model_spec.output_dense_kernel)}'
            )
        if any(len(row) != model_spec.output_units for row in model_spec.output_dense_kernel):
            raise ValueError('TCN 输出 dense kernel 形状非法')
        if len(model_spec.output_dense_bias) != model_spec.output_units:
            raise ValueError('TCN 输出 dense bias 形状非法')

def _get_wavenet_stage_names(model_spec: WaveNetModelSpec) -> List[str]:
    stage_names = ['input_scaled', 'initial_conv']
    stage_names.extend(f'conv_block_{index}' for index in range(len(model_spec.block_layers)))
    stage_names.extend(f'post_dense_{index + 1}' for index in range(len(model_spec.post_layers)))
    stage_names.append('output_scaled')
    return stage_names

def _resolve_wavenet_stage_channels(model_spec: WaveNetModelSpec,
                                    stage_name: str) -> int:
    if stage_name == 'input_scaled':
        return model_spec.input_dim
    if stage_name == 'initial_conv':
        return model_spec.initial_conv.output_channels
    if stage_name.startswith('conv_block_'):
        layer_index = int(stage_name.rsplit('_', 1)[1])
        return model_spec.block_layers[layer_index].output_channels
    if stage_name.startswith('post_dense_'):
        layer_index = int(stage_name.rsplit('_', 1)[1]) - 1
        return model_spec.post_layers[layer_index].output_channels
    if stage_name == 'output_scaled':
        return model_spec.output_units
    raise ValueError(f'未知的 WaveNet 调试阶段: {stage_name}')

def _get_conv_stack_stage_names(model_spec: ConvStackModelSpec) -> List[str]:
    stage_names = ['input_scaled', 'initial_conv']
    stage_names.extend(f'conv_block_{index}' for index in range(len(model_spec.conv_layers)))
    stage_names.extend(f'post_dense_{index + 1}' for index in range(len(model_spec.post_layers)))
    stage_names.append('output_scaled')
    return stage_names

def _resolve_conv_stack_stage_channels(model_spec: ConvStackModelSpec,
                                       stage_name: str) -> int:
    if stage_name == 'input_scaled':
        return model_spec.input_dim
    if stage_name == 'initial_conv':
        return model_spec.initial_conv.output_channels
    if stage_name.startswith('conv_block_'):
        layer_index = int(stage_name.rsplit('_', 1)[1])
        return model_spec.conv_layers[layer_index].output_channels
    if stage_name.startswith('post_dense_'):
        layer_index = int(stage_name.rsplit('_', 1)[1]) - 1
        return model_spec.post_layers[layer_index].output_channels
    if stage_name == 'output_scaled':
        return model_spec.output_units
    raise ValueError(f'未知的 ConvStack 调试阶段: {stage_name}')

def _get_tcn_stage_names(model_spec: TcnModelSpec) -> List[str]:
    stage_names = ['input_scaled']
    if model_spec.initial_projection is not None:
        stage_names.append('initial_projection')
    if model_spec.channel_projection is not None:
        stage_names.append('channel_projection')
    stage_names.extend(f'tcn_block_{block.block_index}' for block in model_spec.blocks)
    stage_names.extend(f'post_dense_{index + 1}' for index in range(len(model_spec.post_layers)))
    stage_names.append('output_scaled')
    return stage_names

def _resolve_tcn_stage_channels(model_spec: TcnModelSpec,
                                stage_name: str) -> int:
    if stage_name == 'input_scaled':
        return model_spec.input_dim
    if stage_name == 'initial_projection':
        if model_spec.initial_projection is None:
            raise ValueError('TCN 不存在 initial_projection 调试阶段')
        return model_spec.initial_projection.output_channels
    if stage_name == 'channel_projection':
        if model_spec.channel_projection is None:
            raise ValueError('TCN 不存在 channel_projection 调试阶段')
        return model_spec.channel_projection.output_channels
    if stage_name.startswith('tcn_block_'):
        block_index = int(stage_name.rsplit('_', 1)[1])
        for block in model_spec.blocks:
            if block.block_index == block_index:
                return block.output_channels
        raise ValueError(f'未知的 TCN block: {stage_name}')
    if stage_name.startswith('post_dense_'):
        layer_index = int(stage_name.rsplit('_', 1)[1]) - 1
        return model_spec.post_layers[layer_index].output_channels
    if stage_name == 'output_scaled':
        return model_spec.output_units
    raise ValueError(f'未知的 TCN 调试阶段: {stage_name}')

def _load_wavenet_block_layers(weights: Iterable[Dict[str, Any]],
                               dilations: Sequence[Any],
                               activation: str) -> List[WaveNetConv1DLayerSpec]:
    layer_names = sorted({
        str(item.get('name', '')).replace('\\', '/').split('/')[0]
        for item in weights
        if re.fullmatch(r'conv1d_\d+/kernel:0', str(item.get('name', '')).replace('\\', '/'))
    }, key=_wavenet_conv_block_sort_key)
    layers: List[WaveNetConv1DLayerSpec] = []
    for index, layer_name in enumerate(layer_names):
        dilation = int(dilations[index]) if index < len(dilations) else 1
        layers.append(_load_wavenet_conv1d_layer(weights, layer_name, activation=activation, dilation=dilation))
    return layers

def _load_wavenet_post_layers(weights: Iterable[Dict[str, Any]],
                              activation: str) -> List[WaveNetConv1DLayerSpec]:
    layer_names = sorted({
        str(item.get('name', '')).replace('\\', '/').split('/')[0]
        for item in weights
        if re.fullmatch(r'post_dense_\d+/kernel:0', str(item.get('name', '')).replace('\\', '/'))
    }, key=_wavenet_post_layer_sort_key)
    return [
        _load_wavenet_conv1d_layer(weights, layer_name, activation=activation, dilation=1)
        for layer_name in layer_names
    ]

def _load_wavenet_conv1d_layer(weights: Iterable[Dict[str, Any]],
                               layer_name: str,
                               activation: str,
                               dilation: int) -> WaveNetConv1DLayerSpec:
    kernel_entry = _find_weight_entry_exact_name(weights, f'{layer_name}/kernel:0')
    bias_entry = _find_weight_entry_exact_name(weights, f'{layer_name}/bias:0')
    kernel_shape = list(kernel_entry['shape'])
    if len(kernel_shape) != 3:
        raise ValueError(f'{layer_name} kernel 维度非法: {kernel_shape}')
    if list(bias_entry['shape']) != [kernel_shape[2]]:
        raise ValueError(f'{layer_name} bias 形状非法: {bias_entry["shape"]}')
    return WaveNetConv1DLayerSpec(
        name=layer_name,
        input_channels=int(kernel_shape[1]),
        output_channels=int(kernel_shape[2]),
        kernel_size=int(kernel_shape[0]),
        dilation=int(dilation),
        activation=str(activation),
        kernel=_to_float_tensor3(kernel_entry['value']),
        bias=_to_float_vector(bias_entry['value']),
    )

def _load_optional_conv1d_layer(weights: Iterable[Dict[str, Any]],
                                layer_name: str,
                                activation: str,
                                dilation: int) -> Optional[WaveNetConv1DLayerSpec]:
    kernel_entry = _find_weight_entry_optional_exact_name(weights, f'{layer_name}/kernel:0')
    if kernel_entry is None:
        return None
    return _load_wavenet_conv1d_layer(weights, layer_name, activation=activation, dilation=dilation)

def _conv_stack_layer_sort_key(layer_name: str) -> int:
    match = re.fullmatch(r'conv_(\d+)', layer_name)
    if match is None:
        return 1_000_000
    return int(match.group(1))

def _wavenet_conv_block_sort_key(layer_name: str) -> int:
    match = re.fullmatch(r'conv1d_(\d+)', layer_name)
    if match is None:
        return 1_000_000
    return int(match.group(1))

def _wavenet_post_layer_sort_key(layer_name: str) -> int:
    match = re.fullmatch(r'post_dense_(\d+)', layer_name)
    if match is None:
        return 1_000_000
    return int(match.group(1))

def _format_c_identifier(name: str) -> str:
    return re.sub(r'[^0-9A-Za-z_]', '_', str(name))

def _render_wavenet_model_data_header(model_spec: WaveNetModelSpec,
                                      benchmark_config: Dict[str, Any],
                                      validation_artifacts: ValidationArtifacts) -> str:
    validation_input = [record.input_sequence for record in validation_artifacts.records]
    lines = [
        '#ifndef GENERATED_WAVENET_MODEL_DATA_H',
        '#define GENERATED_WAVENET_MODEL_DATA_H',
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
        f'#define WAVENET_INPUT_DIM {model_spec.input_dim}u',
        f'#define BENCHMARK_ITERATIONS {int(benchmark_config["iterations"])}u',
        f'#define BENCHMARK_REPEAT_RUNS {int(benchmark_config["repeat_runs"])}u',
        f'#define BENCHMARK_RESET_STATE_EACH_RUN {1 if benchmark_config.get("reset_state_each_run", True) else 0}u',
        f'#define VALIDATION_RECORD_COUNT {validation_artifacts.record_count}u',
        f'#define VALIDATION_SEQ_LEN {validation_artifacts.seq_len}u',
        '',
        f'#define SCALER_INPUT_DATA_RANGE {_format_c_float(validation_artifacts.input_data_range)}',
        f'#define SCALER_OUTPUT_DATA_RANGE {_format_c_float(validation_artifacts.output_data_range)}',
        '',
        f'static const port_float validation_input[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN][WAVENET_INPUT_DIM] = {_render_initializer(validation_input)};',
        '',
        f'static const port_float wavenet_initial_kernel[{model_spec.initial_conv.kernel_size}u][{model_spec.initial_conv.input_channels}u][{model_spec.initial_conv.output_channels}u] = {_render_initializer(model_spec.initial_conv.kernel)};',
        '',
        f'static const port_float wavenet_initial_bias[{model_spec.initial_conv.output_channels}u] = {_render_initializer(model_spec.initial_conv.bias)};',
        '',
    ]

    for layer_spec in model_spec.block_layers:
        identifier = _format_c_identifier(layer_spec.name)
        lines.extend([
            f'static const port_float {identifier}_kernel[{layer_spec.kernel_size}u][{layer_spec.input_channels}u][{layer_spec.output_channels}u] = {_render_initializer(layer_spec.kernel)};',
            '',
            f'static const port_float {identifier}_bias[{layer_spec.output_channels}u] = {_render_initializer(layer_spec.bias)};',
            '',
        ])

    for layer_spec in model_spec.post_layers:
        identifier = _format_c_identifier(layer_spec.name)
        lines.extend([
            f'static const port_float {identifier}_kernel[{layer_spec.kernel_size}u][{layer_spec.input_channels}u][{layer_spec.output_channels}u] = {_render_initializer(layer_spec.kernel)};',
            '',
            f'static const port_float {identifier}_bias[{layer_spec.output_channels}u] = {_render_initializer(layer_spec.bias)};',
            '',
        ])

    if model_spec.output_layer is not None:
        identifier = _format_c_identifier(model_spec.output_layer.name)
        lines.extend([
            f'static const port_float {identifier}_kernel[{model_spec.output_layer.kernel_size}u][{model_spec.output_layer.input_channels}u][{model_spec.output_layer.output_channels}u] = {_render_initializer(model_spec.output_layer.kernel)};',
            '',
            f'static const port_float {identifier}_bias[{model_spec.output_layer.output_channels}u] = {_render_initializer(model_spec.output_layer.bias)};',
            '',
        ])
    else:
        lines.extend([
            f'static const port_float wavenet_output_dense_kernel[{model_spec.final_input_channels}u][{model_spec.output_units}u] = {_render_initializer(model_spec.output_dense_kernel)};',
            '',
            f'static const port_float wavenet_output_dense_bias[{model_spec.output_units}u] = {_render_initializer(model_spec.output_dense_bias)};',
            '',
        ])

    lines.extend([
        '#endif',
        '',
    ])
    return '\n'.join(lines)

def _render_wavenet_main_c(model_spec: WaveNetModelSpec) -> str:
    stage_names = _get_wavenet_stage_names(model_spec)
    stage_decls = [
        f'static port_float debug_{stage_name}[VALIDATION_SEQ_LEN][{_resolve_wavenet_stage_channels(model_spec, stage_name)}u];'
        for stage_name in stage_names
    ]
    clear_lines = [
        f'    zero_buffer(&debug_{stage_name}[0u][0u], VALIDATION_SEQ_LEN * {_resolve_wavenet_stage_channels(model_spec, stage_name)}u);'
        for stage_name in stage_names
    ]
    print_lines: List[str] = []
    for stage_name in stage_names:
        channels = _resolve_wavenet_stage_channels(model_spec, stage_name)
        print_lines.extend([
            f'        uart_puts("validation_{stage_name}_");',
            '        uart_put_u32(record_index);',
            '        uart_puts("=");',
            f'        uart_put_matrix_rows(&debug_{stage_name}[0u][0u], VALIDATION_SEQ_LEN, {channels}u);',
            '        uart_puts("\\n");',
            '',
        ])

    max_kernel_outputs = max(
        [model_spec.initial_conv.output_channels]
        + [layer.output_channels for layer in model_spec.block_layers]
        + [layer.output_channels for layer in model_spec.post_layers]
        + ([model_spec.output_layer.output_channels] if model_spec.output_layer is not None else [model_spec.output_units])
    )
    max_merge_channels = max(1, model_spec.merged_channels)
    lines: List[str] = [
        '#include <stdint.h>',
        '',
        '#include "model_data.h"',
        '',
        '#define RCC_BASE 0x40023800u',
        '#define DEMCR (*(volatile uint32_t *)0xE000EDFCu)',
        '#define DWT_CTRL (*(volatile uint32_t *)0xE0001000u)',
        '#define DWT_CYCCNT (*(volatile uint32_t *)0xE0001004u)',
        '',
        '#define USART1_BASE 0x40011000u',
        '#define RCC_APB2ENR (*(volatile uint32_t *)(RCC_BASE + 0x44u))',
        '#define USART1_SR (*(volatile uint32_t *)(USART1_BASE + 0x00u))',
        '#define USART1_DR (*(volatile uint32_t *)(USART1_BASE + 0x04u))',
        '#define USART1_BRR (*(volatile uint32_t *)(USART1_BASE + 0x08u))',
        '#define USART1_CR1 (*(volatile uint32_t *)(USART1_BASE + 0x0Cu))',
        '',
        '#define RCC_APB2ENR_USART1EN (1u << 4)',
        '#define USART_SR_TXE (1u << 7)',
        '#define USART_CR1_TE (1u << 3)',
        '#define USART_CR1_UE (1u << 13)',
        '#define DEMCR_TRCENA (1u << 24)',
        '#define DWT_CTRL_CYCCNTENA (1u << 0)',
        '',
        'static port_float validation_output[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN];',
        *stage_decls,
        '',
        'static void uart_init(void)',
        '{',
        '    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;',
        '    USART1_BRR = 0x05B2u;',
        '    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;',
        '}',
        '',
        'static void uart_putc(char ch)',
        '{',
        '    while ((USART1_SR & USART_SR_TXE) == 0u) {',
        '    }',
        '    USART1_DR = (uint32_t)ch;',
        '}',
        '',
        'static void uart_puts(const char *message)',
        '{',
        "    while (*message != '\\0') {",
        "        if (*message == '\\n') {",
        "            uart_putc('\\r');",
        '        }',
        '        uart_putc(*message++);',
        '    }',
        '}',
        '',
        'static void uart_put_u32(uint32_t value)',
        '{',
        '    char buffer[11];',
        '    uint32_t index = 0u;',
        '    if (value == 0u) {',
        "        uart_putc('0');",
        '        return;',
        '    }',
        '    while (value > 0u && index < (uint32_t)sizeof(buffer)) {',
        "        buffer[index++] = (char)('0' + (value % 10u));",
        '        value /= 10u;',
        '    }',
        '    while (index > 0u) {',
        '        uart_putc(buffer[--index]);',
        '    }',
        '}',
        '',
        'static void uart_put_fixed6(port_float value)',
        '{',
        '    int32_t scaled = (int32_t)(value * 1000000.0f);',
        '    int32_t abs_scaled = scaled;',
        '    int32_t integer_part;',
        '    int32_t fraction;',
        '    int32_t divisor = 100000;',
        '    if (scaled < 0) {',
        "        uart_putc('-');",
        '        abs_scaled = -scaled;',
        '    }',
        '    integer_part = abs_scaled / 1000000;',
        '    fraction = abs_scaled % 1000000;',
        '    uart_put_u32((uint32_t)integer_part);',
        "    uart_putc('.');",
        '    while (divisor > 0) {',
        "        uart_putc((char)('0' + ((fraction / divisor) % 10)));",
        '        divisor /= 10;',
        '    }',
        '}',
        '',
        'static void uart_put_matrix_rows(const port_float *values, uint32_t row_count, uint32_t column_count)',
        '{',
        '    uint32_t row_index;',
        '    for (row_index = 0u; row_index < row_count; ++row_index) {',
        '        uint32_t column_index;',
        '        if (row_index > 0u) {',
        "            uart_putc(';');",
        '        }',
        '        for (column_index = 0u; column_index < column_count; ++column_index) {',
        '            if (column_index > 0u) {',
        "                uart_putc(',');",
        '            }',
        '            uart_put_fixed6(values[row_index * column_count + column_index]);',
        '        }',
        '    }',
        '}',
        '',
        'static void dwt_init(void)',
        '{',
        '    DEMCR |= DEMCR_TRCENA;',
        '    DWT_CYCCNT = 0u;',
        '    DWT_CTRL |= DWT_CTRL_CYCCNTENA;',
        '}',
        '',
        'static uint32_t dwt_read_cycles(void)',
        '{',
        '    return DWT_CYCCNT;',
        '}',
        '',
        'static uint32_t dwt_is_counting(void)',
        '{',
        '    volatile uint32_t spin;',
        '    uint32_t before;',
        '    uint32_t after;',
        '    dwt_init();',
        '    before = dwt_read_cycles();',
        '    for (spin = 0u; spin < 64u; ++spin) {',
        '        __asm volatile ("nop");',
        '    }',
        '    after = dwt_read_cycles();',
        '    return after > before ? 1u : 0u;',
        '}',
        '',
        'static port_float tanh_approx(port_float value)',
        '{',
        '    port_float squared;',
        '    if (value > 3.0f) {',
        '        return 0.99505478f;',
        '    }',
        '    if (value < -3.0f) {',
        '        return -0.99505478f;',
        '    }',
        '    squared = value * value;',
        '    return value * (27.0f + squared) / (27.0f + 9.0f * squared);',
        '}',
        '',
        'static port_float sigmoid_approx(port_float value)',
        '{',
        '    if (value > 8.0f) {',
        '        return 0.99966466f;',
        '    }',
        '    if (value < -8.0f) {',
        '        return 0.00033535f;',
        '    }',
        '    return 0.5f * (tanh_approx(value * 0.5f) + 1.0f);',
        '}',
        '',
        'static port_float silu_approx(port_float value)',
        '{',
        '    return value * sigmoid_approx(value);',
        '}',
        '',
        'static port_float relu(port_float value)',
        '{',
        '    return value > 0.0f ? value : 0.0f;',
        '}',
        '',
        'static port_float apply_activation_code(port_float value, uint32_t activation_code)',
        '{',
        '    if (activation_code == ACT_RELU) {',
        '        return relu(value);',
        '    }',
        '    if (activation_code == ACT_TANH) {',
        '        return tanh_approx(value);',
        '    }',
        '    if (activation_code == ACT_SIGMOID) {',
        '        return sigmoid_approx(value);',
        '    }',
        '    if (activation_code == ACT_SILU) {',
        '        return silu_approx(value);',
        '    }',
        '    return value;',
        '}',
        '',
        'static void zero_buffer(port_float *buffer, uint32_t length)',
        '{',
        '    uint32_t index;',
        '    for (index = 0u; index < length; ++index) {',
        '        buffer[index] = 0.0f;',
        '    }',
        '}',
        '',
        'static port_float scale_input(port_float value)',
        '{',
        '    if (SCALER_INPUT_DATA_RANGE == 0.0f) {',
        '        return value;',
        '    }',
        '    return value / SCALER_INPUT_DATA_RANGE;',
        '}',
        '',
        'static port_float inverse_scale_output(port_float value)',
        '{',
        '    return value * SCALER_OUTPUT_DATA_RANGE;',
        '}',
        '',
        'static port_float conv1d_causal_step(const port_float *history, uint32_t step_index, uint32_t history_channels, uint32_t kernel_size, uint32_t dilation, uint32_t output_channels, const port_float *kernel_values, const port_float *bias_values, uint32_t output_channel)',
        '{',
        '    port_float sum = bias_values[output_channel];',
        '    uint32_t kernel_index;',
        '    for (kernel_index = 0u; kernel_index < kernel_size; ++kernel_index) {',
        '        int32_t sample_index = (int32_t)step_index - (int32_t)((kernel_size - 1u - kernel_index) * dilation);',
        '        uint32_t input_channel;',
        '        if (sample_index < 0) {',
        '            continue;',
        '        }',
        '        for (input_channel = 0u; input_channel < history_channels; ++input_channel) {',
        '            uint32_t history_offset = ((uint32_t)sample_index * history_channels) + input_channel;',
        '            uint32_t kernel_offset = ((kernel_index * history_channels) + input_channel) * output_channels + output_channel;',
        '            sum += history[history_offset] * kernel_values[kernel_offset];',
        '        }',
        '    }',
        '    return sum;',
        '}',
        '',
        'static void dense_pointwise_forward(const port_float *input_values, uint32_t input_channels, uint32_t output_channels, const port_float *kernel_values, const port_float *bias_values, uint32_t activation_code, port_float *output_values)',
        '{',
        '    uint32_t output_index;',
        '    for (output_index = 0u; output_index < output_channels; ++output_index) {',
        '        uint32_t input_index;',
        '        port_float sum = bias_values[output_index];',
        '        for (input_index = 0u; input_index < input_channels; ++input_index) {',
        '            sum += input_values[input_index] * kernel_values[(input_index * output_channels) + output_index];',
        '        }',
        '        output_values[output_index] = apply_activation_code(sum, activation_code);',
        '    }',
        '}',
        '',
        'static void clear_debug_buffers(void)',
        '{',
        *clear_lines,
        '}',
        '',
        'static void run_wavenet_record(const port_float input_sequence[VALIDATION_SEQ_LEN][WAVENET_INPUT_DIM], port_float output_sequence[VALIDATION_SEQ_LEN])',
        '{',
        '    uint32_t step_index;',
        '    uint32_t channel_index;',
        f'    port_float merged_buffer[{max_merge_channels}u];',
        '    clear_debug_buffers();',
        '    for (step_index = 0u; step_index < VALIDATION_SEQ_LEN; ++step_index) {',
        '        debug_input_scaled[step_index][0u] = scale_input(input_sequence[step_index][0u]);',
        f'        for (channel_index = 0u; channel_index < {model_spec.initial_conv.output_channels}u; ++channel_index) {{',
        f'            debug_initial_conv[step_index][channel_index] = conv1d_causal_step(&debug_input_scaled[0u][0u], step_index, WAVENET_INPUT_DIM, {model_spec.initial_conv.kernel_size}u, 1u, {model_spec.initial_conv.output_channels}u, &wavenet_initial_kernel[0u][0u][0u], &wavenet_initial_bias[0u], channel_index);',
        '        }',
    ]

    for block_index, layer_spec in enumerate(model_spec.block_layers):
        source_name = 'debug_initial_conv'
        source_channels = model_spec.initial_conv.output_channels
        if not model_spec.use_parallel_blocks and block_index > 0:
            source_name = f'debug_conv_block_{block_index - 1}'
            source_channels = model_spec.block_layers[block_index - 1].output_channels
        identifier = _format_c_identifier(layer_spec.name)
        activation_code = _resolve_activation_code(layer_spec.activation)
        lines.extend([
            f'        for (channel_index = 0u; channel_index < {layer_spec.output_channels}u; ++channel_index) {{',
            f'            port_float raw_value = conv1d_causal_step(&{source_name}[0u][0u], step_index, {source_channels}u, {layer_spec.kernel_size}u, {layer_spec.dilation}u, {layer_spec.output_channels}u, &{identifier}_kernel[0u][0u][0u], &{identifier}_bias[0u], channel_index);',
            f'            debug_conv_block_{block_index}[step_index][channel_index] = apply_activation_code(raw_value, {activation_code}u);',
            '        }',
        ])

    if not model_spec.block_layers:
        lines.extend([
            f'        for (channel_index = 0u; channel_index < {model_spec.initial_conv.output_channels}u; ++channel_index) {{',
            '            merged_buffer[channel_index] = debug_initial_conv[step_index][channel_index];',
            '        }',
        ])
    elif model_spec.merge_mode == 'add':
        lines.extend([
            f'        for (channel_index = 0u; channel_index < {model_spec.merged_channels}u; ++channel_index) {{',
            '            merged_buffer[channel_index] = 0.0f;',
            '        }',
        ])
        for block_index, layer_spec in enumerate(model_spec.block_layers):
            lines.extend([
                f'        for (channel_index = 0u; channel_index < {layer_spec.output_channels}u; ++channel_index) {{',
                f'            merged_buffer[channel_index] += debug_conv_block_{block_index}[step_index][channel_index];',
                '        }',
            ])
    else:
        offset = 0
        for block_index, layer_spec in enumerate(model_spec.block_layers):
            lines.extend([
                f'        for (channel_index = 0u; channel_index < {layer_spec.output_channels}u; ++channel_index) {{',
                f'            merged_buffer[{offset}u + channel_index] = debug_conv_block_{block_index}[step_index][channel_index];',
                '        }',
            ])
            offset += layer_spec.output_channels

    current_ptr = 'merged_buffer'
    current_channels = model_spec.merged_channels if model_spec.block_layers else model_spec.initial_conv.output_channels
    for post_index, layer_spec in enumerate(model_spec.post_layers):
        identifier = _format_c_identifier(layer_spec.name)
        target_name = f'debug_post_dense_{post_index + 1}'
        activation_code = _resolve_activation_code(layer_spec.activation)
        lines.append(
            f'        dense_pointwise_forward({current_ptr}, {current_channels}u, {layer_spec.output_channels}u, &{identifier}_kernel[0u][0u][0u], &{identifier}_bias[0u], {activation_code}u, &{target_name}[step_index][0u]);'
        )
        current_ptr = f'&{target_name}[step_index][0u]'
        current_channels = layer_spec.output_channels

    if model_spec.output_layer is not None:
        identifier = _format_c_identifier(model_spec.output_layer.name)
        lines.append(
            f'        dense_pointwise_forward({current_ptr}, {current_channels}u, {model_spec.output_units}u, &{identifier}_kernel[0u][0u][0u], &{identifier}_bias[0u], ACT_LINEAR, &debug_output_scaled[step_index][0u]);'
        )
    else:
        lines.append(
            f'        dense_pointwise_forward({current_ptr}, {current_channels}u, {model_spec.output_units}u, &wavenet_output_dense_kernel[0u][0u], &wavenet_output_dense_bias[0u], ACT_LINEAR, &debug_output_scaled[step_index][0u]);'
        )

    lines.extend([
        '        output_sequence[step_index] = inverse_scale_output(debug_output_scaled[step_index][0u]);',
        '    }',
        '}',
        '',
        'int main(void)',
        '{',
        '    uint32_t iter_index;',
        '    uint32_t record_index;',
        '    uint32_t step_index;',
        '    uint32_t dwt_supported;',
        '    uint32_t total_cycles = 0u;',
        '    uint32_t start_cycles = 0u;',
        '    uint32_t end_cycles = 0u;',
        '    port_float output_value = 0.0f;',
        '    uart_init();',
        f'    uart_puts("{model_spec.model_type.upper()}_QEMU_VALIDATION\\n");',
        '    dwt_supported = dwt_is_counting();',
        '    for (iter_index = 0u; iter_index < BENCHMARK_ITERATIONS; ++iter_index) {',
        '        if (BENCHMARK_RESET_STATE_EACH_RUN != 0u) {',
        '            clear_debug_buffers();',
        '        }',
        '        if (dwt_supported != 0u) {',
        '            dwt_init();',
        '            start_cycles = dwt_read_cycles();',
        '        }',
        '        run_wavenet_record(validation_input[0u], validation_output[0u]);',
        '        if (dwt_supported != 0u) {',
        '            end_cycles = dwt_read_cycles();',
        '            total_cycles += (end_cycles - start_cycles);',
        '        }',
        '        output_value = validation_output[0u][VALIDATION_SEQ_LEN - 1u];',
        '    }',
        '    uart_puts("iterations=");',
        '    uart_put_u32(BENCHMARK_ITERATIONS);',
        '    uart_puts("\\ndwt_supported=");',
        '    uart_put_u32(dwt_supported);',
        '    uart_puts("\\ntimer_source=");',
        '    uart_puts(dwt_supported != 0u ? "dwt" : "host_elapsed");',
        '    if (dwt_supported != 0u) {',
        '        uart_puts("\\nmeasurement_unit=");',
        '        uart_puts("cycles");',
        '        uart_puts("\\nmeasurement_total=");',
        '        uart_put_u32(total_cycles);',
        '        uart_puts("\\nmeasurement_per_iter=");',
        '        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));',
        '        uart_puts("\\ncycles_total=");',
        '        uart_put_u32(total_cycles);',
        '        uart_puts("\\ncycles_per_iter=");',
        '        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));',
        '    }',
        '    uart_puts("\\noutput=");',
        '    uart_put_fixed6(output_value);',
        '    uart_puts("\\n");',
        '    uart_puts("benchmark_complete=1\\n");',
        '    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {',
        '        run_wavenet_record(validation_input[record_index], validation_output[record_index]);',
        '        uart_puts("validation_record_");',
        '        uart_put_u32(record_index);',
        '        uart_puts("=");',
        '        for (step_index = 0u; step_index < VALIDATION_SEQ_LEN; ++step_index) {',
        '            if (step_index > 0u) {',
        "                uart_putc(',');",
        '            }',
        '            uart_put_fixed6(validation_output[record_index][step_index]);',
        '        }',
        '        uart_puts("\\n");',
        '#if !defined(BENCHMARK_PLATFORM_KEIL)',
        *print_lines,
        '#endif',
        '    }',
        '    uart_puts("validation_complete=1\\n");',
        '    while (1) {',
        '    }',
        '}',
        '',
    ])
    return '\n'.join(lines)

def _build_debug_stage_decls(stage_names: Sequence[str],
                             resolve_stage_channels: Any) -> List[str]:
    return [
        f'static port_float debug_{stage_name}[VALIDATION_SEQ_LEN][{resolve_stage_channels(stage_name)}u];'
        for stage_name in stage_names
    ]

def _build_debug_stage_clear_lines(stage_names: Sequence[str],
                                   resolve_stage_channels: Any) -> List[str]:
    return [
        f'    zero_buffer(&debug_{stage_name}[0u][0u], VALIDATION_SEQ_LEN * {resolve_stage_channels(stage_name)}u);'
        for stage_name in stage_names
    ]

def _build_debug_stage_print_lines(stage_names: Sequence[str],
                                   resolve_stage_channels: Any) -> List[str]:
    lines: List[str] = []
    for stage_name in stage_names:
        channel_count = resolve_stage_channels(stage_name)
        lines.extend([
            f'        uart_puts("validation_{stage_name}_");',
            '        uart_put_u32(record_index);',
            '        uart_puts("=");',
            f'        uart_put_matrix_rows(&debug_{stage_name}[0u][0u], VALIDATION_SEQ_LEN, {channel_count}u);',
            '        uart_puts("\\n");',
            '',
        ])
    return lines

def _render_generic_conv_benchmark_main_c(model_banner: str,
                                          input_dim_macro: str,
                                          stage_names: Sequence[str],
                                          resolve_stage_channels: Any,
                                          step_lines: Sequence[str],
                                          extra_global_decls: Optional[Sequence[str]] = None,
                                          extra_clear_lines: Optional[Sequence[str]] = None,
                                          extra_run_locals: Optional[Sequence[str]] = None) -> str:
    stage_decls = _build_debug_stage_decls(stage_names, resolve_stage_channels)
    clear_lines = _build_debug_stage_clear_lines(stage_names, resolve_stage_channels)
    print_lines = _build_debug_stage_print_lines(stage_names, resolve_stage_channels)

    if extra_global_decls:
        stage_decls.extend(extra_global_decls)
    if extra_clear_lines:
        clear_lines.extend(extra_clear_lines)

    run_locals = list(extra_run_locals or [])

    lines: List[str] = [
        '#include <stdint.h>',
        '',
        '#include "model_data.h"',
        '',
        '#define RCC_BASE 0x40023800u',
        '#define DEMCR (*(volatile uint32_t *)0xE000EDFCu)',
        '#define DWT_CTRL (*(volatile uint32_t *)0xE0001000u)',
        '#define DWT_CYCCNT (*(volatile uint32_t *)0xE0001004u)',
        '',
        '#define USART1_BASE 0x40011000u',
        '#define RCC_APB2ENR (*(volatile uint32_t *)(RCC_BASE + 0x44u))',
        '#define USART1_SR (*(volatile uint32_t *)(USART1_BASE + 0x00u))',
        '#define USART1_DR (*(volatile uint32_t *)(USART1_BASE + 0x04u))',
        '#define USART1_BRR (*(volatile uint32_t *)(USART1_BASE + 0x08u))',
        '#define USART1_CR1 (*(volatile uint32_t *)(USART1_BASE + 0x0Cu))',
        '',
        '#define RCC_APB2ENR_USART1EN (1u << 4)',
        '#define USART_SR_TXE (1u << 7)',
        '#define USART_CR1_TE (1u << 3)',
        '#define USART_CR1_UE (1u << 13)',
        '#define DEMCR_TRCENA (1u << 24)',
        '#define DWT_CTRL_CYCCNTENA (1u << 0)',
        '',
        'static port_float validation_output[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN];',
        *stage_decls,
        '',
        'static void uart_init(void)',
        '{',
        '    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;',
        '    USART1_BRR = 0x05B2u;',
        '    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;',
        '}',
        '',
        'static void uart_putc(char ch)',
        '{',
        '    while ((USART1_SR & USART_SR_TXE) == 0u) {',
        '    }',
        '',
        '    USART1_DR = (uint32_t)ch;',
        '}',
        '',
        'static void uart_puts(const char *message)',
        '{',
        "    while (*message != '\\0') {",
        "        if (*message == '\\n') {",
        "            uart_putc('\\r');",
        '        }',
        '        uart_putc(*message++);',
        '    }',
        '}',
        '',
        'static void uart_put_u32(uint32_t value)',
        '{',
        '    char buffer[11];',
        '    uint32_t index = 0u;',
        '    if (value == 0u) {',
        "        uart_putc('0');",
        '        return;',
        '    }',
        '    while (value > 0u && index < (uint32_t)sizeof(buffer)) {',
        "        buffer[index++] = (char)('0' + (value % 10u));",
        '        value /= 10u;',
        '    }',
        '    while (index > 0u) {',
        '        uart_putc(buffer[--index]);',
        '    }',
        '}',
        '',
        'static void uart_put_fixed6(port_float value)',
        '{',
        '    int32_t scaled = (int32_t)(value * 1000000.0f);',
        '    int32_t abs_scaled = scaled;',
        '    int32_t integer_part;',
        '    int32_t fraction;',
        '    int32_t divisor = 100000;',
        '    if (scaled < 0) {',
        "        uart_putc('-');",
        '        abs_scaled = -scaled;',
        '    }',
        '    integer_part = abs_scaled / 1000000;',
        '    fraction = abs_scaled % 1000000;',
        '    uart_put_u32((uint32_t)integer_part);',
        "    uart_putc('.');",
        '    while (divisor > 0) {',
        "        uart_putc((char)('0' + ((fraction / divisor) % 10)));",
        '        divisor /= 10;',
        '    }',
        '}',
        '',
        'static void uart_put_matrix_rows(const port_float *values,',
        '                                 uint32_t row_count,',
        '                                 uint32_t column_count)',
        '{',
        '    uint32_t row_index;',
        '    for (row_index = 0u; row_index < row_count; ++row_index) {',
        '        uint32_t column_index;',
        '        if (row_index > 0u) {',
        "            uart_putc(';');",
        '        }',
        '        for (column_index = 0u; column_index < column_count; ++column_index) {',
        '            if (column_index > 0u) {',
        "                uart_putc(',');",
        '            }',
        '            uart_put_fixed6(values[row_index * column_count + column_index]);',
        '        }',
        '    }',
        '}',
        '',
        'static void dwt_init(void)',
        '{',
        '    DEMCR |= DEMCR_TRCENA;',
        '    DWT_CYCCNT = 0u;',
        '    DWT_CTRL |= DWT_CTRL_CYCCNTENA;',
        '}',
        '',
        'static uint32_t dwt_read_cycles(void)',
        '{',
        '    return DWT_CYCCNT;',
        '}',
        '',
        'static uint32_t dwt_is_counting(void)',
        '{',
        '    volatile uint32_t spin;',
        '    uint32_t before;',
        '    uint32_t after;',
        '    dwt_init();',
        '    before = dwt_read_cycles();',
        '    for (spin = 0u; spin < 64u; ++spin) {',
        '        __asm volatile ("nop");',
        '    }',
        '    after = dwt_read_cycles();',
        '    return after > before ? 1u : 0u;',
        '}',
        '',
        'static port_float tanh_approx(port_float value)',
        '{',
        '    port_float squared;',
        '    if (value > 3.0f) {',
        '        return 0.99505478f;',
        '    }',
        '    if (value < -3.0f) {',
        '        return -0.99505478f;',
        '    }',
        '    squared = value * value;',
        '    return value * (27.0f + squared) / (27.0f + 9.0f * squared);',
        '}',
        '',
        'static port_float sigmoid_approx(port_float value)',
        '{',
        '    if (value > 8.0f) {',
        '        return 0.99966466f;',
        '    }',
        '    if (value < -8.0f) {',
        '        return 0.00033535f;',
        '    }',
        '    return 0.5f * (tanh_approx(value * 0.5f) + 1.0f);',
        '}',
        '',
        'static port_float silu_approx(port_float value)',
        '{',
        '    return value * sigmoid_approx(value);',
        '}',
        '',
        'static port_float relu(port_float value)',
        '{',
        '    return value > 0.0f ? value : 0.0f;',
        '}',
        '',
        'static port_float apply_activation_code(port_float value, uint32_t activation_code)',
        '{',
        '    if (activation_code == ACT_RELU) {',
        '        return relu(value);',
        '    }',
        '    if (activation_code == ACT_TANH) {',
        '        return tanh_approx(value);',
        '    }',
        '    if (activation_code == ACT_SIGMOID) {',
        '        return sigmoid_approx(value);',
        '    }',
        '    if (activation_code == ACT_SILU) {',
        '        return silu_approx(value);',
        '    }',
        '    return value;',
        '}',
        '',
        'static void zero_buffer(port_float *buffer, uint32_t length)',
        '{',
        '    uint32_t index;',
        '    for (index = 0u; index < length; ++index) {',
        '        buffer[index] = 0.0f;',
        '    }',
        '}',
        '',
        'static port_float scale_input(port_float value)',
        '{',
        '    if (SCALER_INPUT_DATA_RANGE == 0.0f) {',
        '        return value;',
        '    }',
        '    return value / SCALER_INPUT_DATA_RANGE;',
        '}',
        '',
        'static port_float inverse_scale_output(port_float value)',
        '{',
        '    return value * SCALER_OUTPUT_DATA_RANGE;',
        '}',
        '',
        'static port_float conv1d_causal_step(const port_float *history, uint32_t step_index, uint32_t history_channels, uint32_t kernel_size, uint32_t dilation, uint32_t output_channels, const port_float *kernel_values, const port_float *bias_values, uint32_t output_channel)',
        '{',
        '    port_float sum = bias_values[output_channel];',
        '    uint32_t kernel_index;',
        '    for (kernel_index = 0u; kernel_index < kernel_size; ++kernel_index) {',
        '        int32_t sample_index = (int32_t)step_index - (int32_t)((kernel_size - 1u - kernel_index) * dilation);',
        '        uint32_t input_channel;',
        '        if (sample_index < 0) {',
        '            continue;',
        '        }',
        '        for (input_channel = 0u; input_channel < history_channels; ++input_channel) {',
        '            uint32_t history_offset = ((uint32_t)sample_index * history_channels) + input_channel;',
        '            uint32_t kernel_offset = ((kernel_index * history_channels) + input_channel) * output_channels + output_channel;',
        '            sum += history[history_offset] * kernel_values[kernel_offset];',
        '        }',
        '    }',
        '    return sum;',
        '}',
        '',
        'static void dense_pointwise_forward(const port_float *input_values, uint32_t input_channels, uint32_t output_channels, const port_float *kernel_values, const port_float *bias_values, uint32_t activation_code, port_float *output_values)',
        '{',
        '    uint32_t output_index;',
        '    for (output_index = 0u; output_index < output_channels; ++output_index) {',
        '        uint32_t input_index;',
        '        port_float sum = bias_values[output_index];',
        '        for (input_index = 0u; input_index < input_channels; ++input_index) {',
        '            sum += input_values[input_index] * kernel_values[(input_index * output_channels) + output_index];',
        '        }',
        '        output_values[output_index] = apply_activation_code(sum, activation_code);',
        '    }',
        '}',
        '',
        'static void clear_debug_buffers(void)',
        '{',
        *clear_lines,
        '}',
        '',
        f'static void run_generated_record(const port_float input_sequence[VALIDATION_SEQ_LEN][{input_dim_macro}], port_float output_sequence[VALIDATION_SEQ_LEN])',
        '{',
        '    uint32_t step_index;',
        '    uint32_t channel_index;',
        *run_locals,
        '    clear_debug_buffers();',
        '    for (step_index = 0u; step_index < VALIDATION_SEQ_LEN; ++step_index) {',
        *step_lines,
        '        output_sequence[step_index] = inverse_scale_output(debug_output_scaled[step_index][0u]);',
        '    }',
        '}',
        '',
        'int main(void)',
        '{',
        '    uint32_t iter_index;',
        '    uint32_t record_index;',
        '    uint32_t step_index;',
        '    uint32_t dwt_supported;',
        '    uint32_t total_cycles = 0u;',
        '    uint32_t start_cycles = 0u;',
        '    uint32_t end_cycles = 0u;',
        '    port_float output_value = 0.0f;',
        '    uart_init();',
        f'    uart_puts("{model_banner}\\n");',
        '    dwt_supported = dwt_is_counting();',
        '    for (iter_index = 0u; iter_index < BENCHMARK_ITERATIONS; ++iter_index) {',
        '        if (BENCHMARK_RESET_STATE_EACH_RUN != 0u) {',
        '            clear_debug_buffers();',
        '        }',
        '        if (dwt_supported != 0u) {',
        '            dwt_init();',
        '            start_cycles = dwt_read_cycles();',
        '        }',
        '        run_generated_record(validation_input[0u], validation_output[0u]);',
        '        if (dwt_supported != 0u) {',
        '            end_cycles = dwt_read_cycles();',
        '            total_cycles += (end_cycles - start_cycles);',
        '        }',
        '        output_value = validation_output[0u][VALIDATION_SEQ_LEN - 1u];',
        '    }',
        '    uart_puts("iterations=");',
        '    uart_put_u32(BENCHMARK_ITERATIONS);',
        '    uart_puts("\\ndwt_supported=");',
        '    uart_put_u32(dwt_supported);',
        '    uart_puts("\\ntimer_source=");',
        '    uart_puts(dwt_supported != 0u ? "dwt" : "host_elapsed");',
        '    if (dwt_supported != 0u) {',
        '        uart_puts("\\nmeasurement_unit=");',
        '        uart_puts("cycles");',
        '        uart_puts("\\nmeasurement_total=");',
        '        uart_put_u32(total_cycles);',
        '        uart_puts("\\nmeasurement_per_iter=");',
        '        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));',
        '        uart_puts("\\ncycles_total=");',
        '        uart_put_u32(total_cycles);',
        '        uart_puts("\\ncycles_per_iter=");',
        '        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));',
        '    }',
        '    uart_puts("\\noutput=");',
        '    uart_put_fixed6(output_value);',
        '    uart_puts("\\n");',
        '    uart_puts("benchmark_complete=1\\n");',
        '    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {',
        '        run_generated_record(validation_input[record_index], validation_output[record_index]);',
        '        uart_puts("validation_record_");',
        '        uart_put_u32(record_index);',
        '        uart_puts("=");',
        '        for (step_index = 0u; step_index < VALIDATION_SEQ_LEN; ++step_index) {',
        '            if (step_index > 0u) {',
        "                uart_putc(',');",
        '            }',
        '            uart_put_fixed6(validation_output[record_index][step_index]);',
        '        }',
        '        uart_puts("\\n");',
        '#if !defined(BENCHMARK_PLATFORM_KEIL)',
        *print_lines,
        '#endif',
        '    }',
        '    uart_puts("validation_complete=1\\n");',
        '    while (1) {',
        '    }',
        '}',
        '',
    ]
    return '\n'.join(lines)

def _render_conv_stack_model_data_header(model_spec: ConvStackModelSpec,
                                         benchmark_config: Dict[str, Any],
                                         validation_artifacts: ValidationArtifacts) -> str:
    validation_input = [record.input_sequence for record in validation_artifacts.records]
    lines = [
        '#ifndef GENERATED_CONV_STACK_MODEL_DATA_H',
        '#define GENERATED_CONV_STACK_MODEL_DATA_H',
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
        f'#define CONV_STACK_INPUT_DIM {model_spec.input_dim}u',
        f'#define CONV_STACK_OUTPUT_UNITS {model_spec.output_units}u',
        f'#define BENCHMARK_ITERATIONS {int(benchmark_config["iterations"])}u',
        f'#define BENCHMARK_REPEAT_RUNS {int(benchmark_config["repeat_runs"])}u',
        f'#define BENCHMARK_RESET_STATE_EACH_RUN {1 if benchmark_config.get("reset_state_each_run", True) else 0}u',
        f'#define VALIDATION_RECORD_COUNT {validation_artifacts.record_count}u',
        f'#define VALIDATION_SEQ_LEN {validation_artifacts.seq_len}u',
        '',
        f'#define SCALER_INPUT_DATA_RANGE {_format_c_float(validation_artifacts.input_data_range)}',
        f'#define SCALER_OUTPUT_DATA_RANGE {_format_c_float(validation_artifacts.output_data_range)}',
        '',
        f'static const port_float validation_input[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN][CONV_STACK_INPUT_DIM] = {_render_initializer(validation_input)};',
        '',
        f'static const port_float conv_stack_initial_kernel[{model_spec.initial_conv.kernel_size}u][{model_spec.initial_conv.input_channels}u][{model_spec.initial_conv.output_channels}u] = {_render_initializer(model_spec.initial_conv.kernel)};',
        '',
        f'static const port_float conv_stack_initial_bias[{model_spec.initial_conv.output_channels}u] = {_render_initializer(model_spec.initial_conv.bias)};',
        '',
    ]

    for layer_spec in model_spec.conv_layers:
        identifier = _format_c_identifier(layer_spec.name)
        lines.extend([
            f'static const port_float {identifier}_kernel[{layer_spec.kernel_size}u][{layer_spec.input_channels}u][{layer_spec.output_channels}u] = {_render_initializer(layer_spec.kernel)};',
            '',
            f'static const port_float {identifier}_bias[{layer_spec.output_channels}u] = {_render_initializer(layer_spec.bias)};',
            '',
        ])

    for layer_spec in model_spec.post_layers:
        identifier = _format_c_identifier(layer_spec.name)
        lines.extend([
            f'static const port_float {identifier}_kernel[{layer_spec.kernel_size}u][{layer_spec.input_channels}u][{layer_spec.output_channels}u] = {_render_initializer(layer_spec.kernel)};',
            '',
            f'static const port_float {identifier}_bias[{layer_spec.output_channels}u] = {_render_initializer(layer_spec.bias)};',
            '',
        ])

    lines.extend([
        f'static const port_float conv_stack_output_kernel[{model_spec.output_layer.kernel_size}u][{model_spec.output_layer.input_channels}u][{model_spec.output_layer.output_channels}u] = {_render_initializer(model_spec.output_layer.kernel)};',
        '',
        f'static const port_float conv_stack_output_bias[{model_spec.output_layer.output_channels}u] = {_render_initializer(model_spec.output_layer.bias)};',
        '',
        '#endif',
        '',
    ])
    return '\n'.join(lines)

def _render_conv_stack_main_c(model_spec: ConvStackModelSpec) -> str:
    stage_names = _get_conv_stack_stage_names(model_spec)
    step_lines: List[str] = [
        '        debug_input_scaled[step_index][0u] = scale_input(input_sequence[step_index][0u]);',
    ]

    initial_activation = _resolve_activation_code(model_spec.initial_conv.activation)
    step_lines.extend([
        f'        for (channel_index = 0u; channel_index < {model_spec.initial_conv.output_channels}u; ++channel_index) {{',
        f'            port_float raw_value = conv1d_causal_step(&debug_input_scaled[0u][0u], step_index, CONV_STACK_INPUT_DIM, {model_spec.initial_conv.kernel_size}u, 1u, {model_spec.initial_conv.output_channels}u, &conv_stack_initial_kernel[0u][0u][0u], &conv_stack_initial_bias[0u], channel_index);',
        f'            debug_initial_conv[step_index][channel_index] = apply_activation_code(raw_value, {initial_activation}u);',
        '        }',
    ])

    current_ptr = '&debug_initial_conv[step_index][0u]'
    current_channels = model_spec.initial_conv.output_channels
    for layer_index, layer_spec in enumerate(model_spec.conv_layers):
        source_name = 'debug_initial_conv' if layer_index == 0 else f'debug_conv_block_{layer_index - 1}'
        source_channels = model_spec.initial_conv.output_channels if layer_index == 0 else model_spec.conv_layers[layer_index - 1].output_channels
        identifier = _format_c_identifier(layer_spec.name)
        activation_code = _resolve_activation_code(layer_spec.activation)
        target_name = f'debug_conv_block_{layer_index}'
        step_lines.extend([
            f'        for (channel_index = 0u; channel_index < {layer_spec.output_channels}u; ++channel_index) {{',
            f'            port_float raw_value = conv1d_causal_step(&{source_name}[0u][0u], step_index, {source_channels}u, {layer_spec.kernel_size}u, {layer_spec.dilation}u, {layer_spec.output_channels}u, &{identifier}_kernel[0u][0u][0u], &{identifier}_bias[0u], channel_index);',
            f'            {target_name}[step_index][channel_index] = apply_activation_code(raw_value, {activation_code}u);',
            '        }',
        ])
        current_ptr = f'&{target_name}[step_index][0u]'
        current_channels = layer_spec.output_channels

    for post_index, layer_spec in enumerate(model_spec.post_layers):
        identifier = _format_c_identifier(layer_spec.name)
        target_name = f'debug_post_dense_{post_index + 1}'
        activation_code = _resolve_activation_code(layer_spec.activation)
        step_lines.append(
            f'        dense_pointwise_forward({current_ptr}, {current_channels}u, {layer_spec.output_channels}u, &{identifier}_kernel[0u][0u][0u], &{identifier}_bias[0u], {activation_code}u, &{target_name}[step_index][0u]);'
        )
        current_ptr = f'&{target_name}[step_index][0u]'
        current_channels = layer_spec.output_channels

    step_lines.append(
        f'        dense_pointwise_forward({current_ptr}, {current_channels}u, {model_spec.output_units}u, &conv_stack_output_kernel[0u][0u][0u], &conv_stack_output_bias[0u], ACT_LINEAR, &debug_output_scaled[step_index][0u]);'
    )

    return _render_generic_conv_benchmark_main_c(
        model_banner=f'{model_spec.model_type.upper()}_QEMU_VALIDATION',
        input_dim_macro='CONV_STACK_INPUT_DIM',
        stage_names=stage_names,
        resolve_stage_channels=lambda stage_name: _resolve_conv_stack_stage_channels(model_spec, stage_name),
        step_lines=step_lines,
    )

def _render_tcn_model_data_header(model_spec: TcnModelSpec,
                                  benchmark_config: Dict[str, Any],
                                  validation_artifacts: ValidationArtifacts) -> str:
    validation_input = [record.input_sequence for record in validation_artifacts.records]
    lines = [
        '#ifndef GENERATED_TCN_MODEL_DATA_H',
        '#define GENERATED_TCN_MODEL_DATA_H',
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
        f'#define TCN_INPUT_DIM {model_spec.input_dim}u',
        f'#define TCN_BLOCK_COUNT {len(model_spec.blocks)}u',
        f'#define TCN_OUTPUT_UNITS {model_spec.output_units}u',
        f'#define TCN_HAS_INITIAL_PROJECTION {1 if model_spec.initial_projection is not None else 0}u',
        f'#define TCN_HAS_CHANNEL_PROJECTION {1 if model_spec.channel_projection is not None else 0}u',
        f'#define TCN_HAS_OUTPUT_CONV {1 if model_spec.output_layer is not None else 0}u',
        f'#define BENCHMARK_ITERATIONS {int(benchmark_config["iterations"])}u',
        f'#define BENCHMARK_REPEAT_RUNS {int(benchmark_config["repeat_runs"])}u',
        f'#define BENCHMARK_RESET_STATE_EACH_RUN {1 if benchmark_config.get("reset_state_each_run", True) else 0}u',
        f'#define VALIDATION_RECORD_COUNT {validation_artifacts.record_count}u',
        f'#define VALIDATION_SEQ_LEN {validation_artifacts.seq_len}u',
        '',
        f'#define SCALER_INPUT_DATA_RANGE {_format_c_float(validation_artifacts.input_data_range)}',
        f'#define SCALER_OUTPUT_DATA_RANGE {_format_c_float(validation_artifacts.output_data_range)}',
        '',
        f'static const port_float validation_input[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN][TCN_INPUT_DIM] = {_render_initializer(validation_input)};',
        '',
    ]

    if model_spec.initial_projection is not None:
        lines.extend([
            f'static const port_float tcn_initial_projection_kernel[{model_spec.initial_projection.kernel_size}u][{model_spec.initial_projection.input_channels}u][{model_spec.initial_projection.output_channels}u] = {_render_initializer(model_spec.initial_projection.kernel)};',
            '',
            f'static const port_float tcn_initial_projection_bias[{model_spec.initial_projection.output_channels}u] = {_render_initializer(model_spec.initial_projection.bias)};',
            '',
        ])

    if model_spec.channel_projection is not None:
        lines.extend([
            f'static const port_float tcn_channel_projection_kernel[{model_spec.channel_projection.kernel_size}u][{model_spec.channel_projection.input_channels}u][{model_spec.channel_projection.output_channels}u] = {_render_initializer(model_spec.channel_projection.kernel)};',
            '',
            f'static const port_float tcn_channel_projection_bias[{model_spec.channel_projection.output_channels}u] = {_render_initializer(model_spec.channel_projection.bias)};',
            '',
        ])

    for block in model_spec.blocks:
        conv1_identifier = _format_c_identifier(block.conv1.name)
        conv2_identifier = _format_c_identifier(block.conv2.name)
        lines.extend([
            f'static const port_float {conv1_identifier}_kernel[{block.conv1.kernel_size}u][{block.conv1.input_channels}u][{block.conv1.output_channels}u] = {_render_initializer(block.conv1.kernel)};',
            '',
            f'static const port_float {conv1_identifier}_bias[{block.conv1.output_channels}u] = {_render_initializer(block.conv1.bias)};',
            '',
            f'static const port_float {conv2_identifier}_kernel[{block.conv2.kernel_size}u][{block.conv2.input_channels}u][{block.conv2.output_channels}u] = {_render_initializer(block.conv2.kernel)};',
            '',
            f'static const port_float {conv2_identifier}_bias[{block.conv2.output_channels}u] = {_render_initializer(block.conv2.bias)};',
            '',
        ])
        if block.residual_projection is not None:
            projection_identifier = _format_c_identifier(block.residual_projection.name)
            lines.extend([
                f'static const port_float {projection_identifier}_kernel[{block.residual_projection.kernel_size}u][{block.residual_projection.input_channels}u][{block.residual_projection.output_channels}u] = {_render_initializer(block.residual_projection.kernel)};',
                '',
                f'static const port_float {projection_identifier}_bias[{block.residual_projection.output_channels}u] = {_render_initializer(block.residual_projection.bias)};',
                '',
            ])

    for layer_spec in model_spec.post_layers:
        identifier = _format_c_identifier(layer_spec.name)
        lines.extend([
            f'static const port_float {identifier}_kernel[{layer_spec.kernel_size}u][{layer_spec.input_channels}u][{layer_spec.output_channels}u] = {_render_initializer(layer_spec.kernel)};',
            '',
            f'static const port_float {identifier}_bias[{layer_spec.output_channels}u] = {_render_initializer(layer_spec.bias)};',
            '',
        ])

    if model_spec.output_layer is not None:
        lines.extend([
            f'static const port_float tcn_output_kernel[{model_spec.output_layer.kernel_size}u][{model_spec.output_layer.input_channels}u][{model_spec.output_layer.output_channels}u] = {_render_initializer(model_spec.output_layer.kernel)};',
            '',
            f'static const port_float tcn_output_bias[{model_spec.output_layer.output_channels}u] = {_render_initializer(model_spec.output_layer.bias)};',
            '',
        ])
    else:
        lines.extend([
            f'static const port_float tcn_output_dense_kernel[{model_spec.final_input_channels}u][{model_spec.output_units}u] = {_render_initializer(model_spec.output_dense_kernel)};',
            '',
            f'static const port_float tcn_output_dense_bias[{model_spec.output_units}u] = {_render_initializer(model_spec.output_dense_bias)};',
            '',
        ])

    lines.extend([
        '#endif',
        '',
    ])
    return '\n'.join(lines)

def _render_tcn_main_c(model_spec: TcnModelSpec) -> str:
    stage_names = _get_tcn_stage_names(model_spec)
    max_block_channels = max([1] + [block.output_channels for block in model_spec.blocks])
    extra_global_decls = [
        f'static port_float debug_tcn_block_{block.block_index}_conv1[VALIDATION_SEQ_LEN][{block.conv1.output_channels}u];'
        for block in model_spec.blocks
    ]
    extra_clear_lines = [
        f'    zero_buffer(&debug_tcn_block_{block.block_index}_conv1[0u][0u], VALIDATION_SEQ_LEN * {block.conv1.output_channels}u);'
        for block in model_spec.blocks
    ]
    extra_run_locals = [f'    port_float residual_buffer[{max_block_channels}u];']

    step_lines: List[str] = [
        '        debug_input_scaled[step_index][0u] = scale_input(input_sequence[step_index][0u]);',
    ]

    current_stage_name = 'input_scaled'
    current_ptr = '&debug_input_scaled[step_index][0u]'
    current_channels = model_spec.input_dim

    if model_spec.initial_projection is not None:
        activation_code = _resolve_activation_code(model_spec.initial_projection.activation)
        step_lines.append(
            f'        dense_pointwise_forward({current_ptr}, {current_channels}u, {model_spec.initial_projection.output_channels}u, &tcn_initial_projection_kernel[0u][0u][0u], &tcn_initial_projection_bias[0u], {activation_code}u, &debug_initial_projection[step_index][0u]);'
        )
        current_stage_name = 'initial_projection'
        current_ptr = '&debug_initial_projection[step_index][0u]'
        current_channels = model_spec.initial_projection.output_channels

    if model_spec.channel_projection is not None:
        step_lines.append(
            f'        dense_pointwise_forward({current_ptr}, {current_channels}u, {model_spec.channel_projection.output_channels}u, &tcn_channel_projection_kernel[0u][0u][0u], &tcn_channel_projection_bias[0u], ACT_LINEAR, &debug_channel_projection[step_index][0u]);'
        )
        current_stage_name = 'channel_projection'
        current_ptr = '&debug_channel_projection[step_index][0u]'
        current_channels = model_spec.channel_projection.output_channels

    for block in model_spec.blocks:
        conv1_identifier = _format_c_identifier(block.conv1.name)
        conv2_identifier = _format_c_identifier(block.conv2.name)
        conv1_activation = _resolve_activation_code(block.conv1.activation)
        conv2_activation = _resolve_activation_code(block.conv2.activation)
        output_activation = _resolve_activation_code(block.output_activation)
        source_history_name = f'debug_{current_stage_name}'
        conv1_history_name = f'debug_tcn_block_{block.block_index}_conv1'
        target_stage_name = f'debug_tcn_block_{block.block_index}'

        step_lines.extend([
            f'        for (channel_index = 0u; channel_index < {block.conv1.output_channels}u; ++channel_index) {{',
            f'            port_float raw_value = conv1d_causal_step(&{source_history_name}[0u][0u], step_index, {current_channels}u, {block.conv1.kernel_size}u, {block.conv1.dilation}u, {block.conv1.output_channels}u, &{conv1_identifier}_kernel[0u][0u][0u], &{conv1_identifier}_bias[0u], channel_index);',
            f'            {conv1_history_name}[step_index][channel_index] = apply_activation_code(raw_value, {conv1_activation}u);',
            '        }',
            f'        for (channel_index = 0u; channel_index < {block.conv2.output_channels}u; ++channel_index) {{',
            f'            port_float raw_value = conv1d_causal_step(&{conv1_history_name}[0u][0u], step_index, {block.conv1.output_channels}u, {block.conv2.kernel_size}u, {block.conv2.dilation}u, {block.conv2.output_channels}u, &{conv2_identifier}_kernel[0u][0u][0u], &{conv2_identifier}_bias[0u], channel_index);',
            f'            {target_stage_name}[step_index][channel_index] = apply_activation_code(raw_value, {conv2_activation}u);',
            '        }',
        ])

        if block.use_residual:
            if block.residual_projection is not None:
                projection_identifier = _format_c_identifier(block.residual_projection.name)
                step_lines.append(
                    f'        dense_pointwise_forward({current_ptr}, {current_channels}u, {block.output_channels}u, &{projection_identifier}_kernel[0u][0u][0u], &{projection_identifier}_bias[0u], ACT_LINEAR, &residual_buffer[0u]);'
                )
            else:
                step_lines.extend([
                    f'        for (channel_index = 0u; channel_index < {block.output_channels}u; ++channel_index) {{',
                    f'            residual_buffer[channel_index] = {current_ptr}[channel_index];',
                    '        }',
                ])

            step_lines.extend([
                f'        for (channel_index = 0u; channel_index < {block.output_channels}u; ++channel_index) {{',
                f'            {target_stage_name}[step_index][channel_index] = apply_activation_code({target_stage_name}[step_index][channel_index] + residual_buffer[channel_index], {output_activation}u);',
                '        }',
            ])
        elif output_activation != 0:
            step_lines.extend([
                f'        for (channel_index = 0u; channel_index < {block.output_channels}u; ++channel_index) {{',
                f'            {target_stage_name}[step_index][channel_index] = apply_activation_code({target_stage_name}[step_index][channel_index], {output_activation}u);',
                '        }',
            ])

        current_stage_name = f'tcn_block_{block.block_index}'
        current_ptr = f'&debug_tcn_block_{block.block_index}[step_index][0u]'
        current_channels = block.output_channels

    for post_index, layer_spec in enumerate(model_spec.post_layers):
        identifier = _format_c_identifier(layer_spec.name)
        target_name = f'debug_post_dense_{post_index + 1}'
        activation_code = _resolve_activation_code(layer_spec.activation)
        step_lines.append(
            f'        dense_pointwise_forward({current_ptr}, {current_channels}u, {layer_spec.output_channels}u, &{identifier}_kernel[0u][0u][0u], &{identifier}_bias[0u], {activation_code}u, &{target_name}[step_index][0u]);'
        )
        current_ptr = f'&{target_name}[step_index][0u]'
        current_channels = layer_spec.output_channels

    if model_spec.output_layer is not None:
        step_lines.append(
            f'        dense_pointwise_forward({current_ptr}, {current_channels}u, {model_spec.output_units}u, &tcn_output_kernel[0u][0u][0u], &tcn_output_bias[0u], ACT_LINEAR, &debug_output_scaled[step_index][0u]);'
        )
    else:
        step_lines.append(
            f'        dense_pointwise_forward({current_ptr}, {current_channels}u, {model_spec.output_units}u, &tcn_output_dense_kernel[0u][0u], &tcn_output_dense_bias[0u], ACT_LINEAR, &debug_output_scaled[step_index][0u]);'
        )

    return _render_generic_conv_benchmark_main_c(
        model_banner=f'{model_spec.model_type.upper()}_QEMU_VALIDATION',
        input_dim_macro='TCN_INPUT_DIM',
        stage_names=stage_names,
        resolve_stage_channels=lambda stage_name: _resolve_tcn_stage_channels(model_spec, stage_name),
        step_lines=step_lines,
        extra_global_decls=extra_global_decls,
        extra_clear_lines=extra_clear_lines,
        extra_run_locals=extra_run_locals,
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

def _find_weight_entry_optional_exact_name(weights: Iterable[Dict[str, Any]], exact_name: str) -> Optional[Dict[str, Any]]:
    normalized_name = str(exact_name).replace('\\', '/')
    for item in weights:
        name = str(item.get('name', '')).replace('\\', '/')
        if name == normalized_name:
            return item
    return None

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

def _render_uint_initializer(values: Sequence[int], suffix: str = 'u') -> str:
    return '{ ' + ', '.join(f'{int(value)}{suffix}' for value in values) + ' }'

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

#if !defined(BENCHMARK_PLATFORM_KEIL)
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
#endif
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

#if !defined(BENCHMARK_PLATFORM_KEIL)
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
#endif
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

#if !defined(BENCHMARK_PLATFORM_KEIL)
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
#endif
    }
    uart_puts("validation_complete=1\n");

    while (1) {
    }
}
"""

__all__ = [
    "SUPPORTED_SEQUENCE_MODEL_TYPES",
    "execute_sequence_keil_bench_task",
    "execute_sequence_qemu_task",
    "generate_qemu_project",
]
