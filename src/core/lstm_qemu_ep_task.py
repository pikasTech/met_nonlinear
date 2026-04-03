"""LSTM QEMU C 推理 EP 任务实现。"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

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

    @property
    def record_count(self) -> int:
        return len(self.records)

    @property
    def seq_len(self) -> int:
        if not self.records:
            return 0
        return len(self.records[0].tf_output_sequence)


def execute_lstm_qemu_inference_task(ep_path: ExternalPath,
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
    model_spec = _load_lstm_model_spec(model_project_name, weights_json_path)
    if model_spec.input_dim != 1:
        raise ValueError(f'当前仅支持单输入 LSTM 数据集验证，实际 input_dim={model_spec.input_dim}')

    validation_artifacts = _prepare_validation_artifacts(
        model_project_name=model_project_name,
        weights_json_path=weights_json_path,
        validation_config=validation_config,
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
    )

    execution_summary: Dict[str, Any] = {
        'task_type': 'qemu-c-inference',
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
                success_patterns=['validation_complete=1'],
            )
            parsed_output = _enrich_benchmark_output(
                _parse_benchmark_stdout(str(run_workflow.get('run', {}).get('stdout', ''))),
                run_workflow,
                benchmark_config,
            )
            c_output_sequences = _extract_validation_outputs(parsed_output, validation_artifacts)
            comparison_payload = _compute_wave_comparison(validation_artifacts, c_output_sequences)
            if first_c_output_sequences is None:
                first_c_output_sequences = c_output_sequences

            run_results.append({
                'run_index': run_index,
                'workflow': run_workflow,
                'parsed_output': parsed_output,
                'comparison': comparison_payload['overall'],
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

    execution_summary['build'] = build_result
    execution_summary['runs'] = run_results
    if run_results:
        execution_summary['aggregated'] = _aggregate_run_results(run_results)

    comparison_file = ep_path.output_path / 'validation_comparison.json'
    if first_c_output_sequences is not None:
        wave_paths = _write_validation_wave_files(
            output_root=ep_path.output_path,
            validation_artifacts=validation_artifacts,
            c_output_sequences=first_c_output_sequences,
            compress=bool(validation_config['wave_output']['compress']),
        )
        comparison_payload = _compute_wave_comparison(validation_artifacts, first_c_output_sequences)
        comparison_payload['wave_paths'] = wave_paths
        _write_json(comparison_file, comparison_payload)
        execution_summary['wave_paths'] = wave_paths
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
        ),
        'action': action,
    })
    logger.info('QEMU C 推理任务完成: %s', summary_path)
    return True


def generate_qemu_project(output_dir: Path,
                          model_spec: LstmModelSpec,
                          benchmark_config: Dict[str, Any],
                          validation_artifacts: ValidationArtifacts,
                          overwrite: bool) -> None:
    """生成裸机 QEMU 工程目录。"""
    if output_dir.exists() and not overwrite:
        raise FileExistsError(f'QEMU 工程目录已存在且未允许覆盖: {output_dir}')

    output_dir.mkdir(parents=True, exist_ok=True)
    _copy_runtime_template('startup.c', output_dir / 'startup.c')
    _copy_runtime_template('stm32f405.ld', output_dir / 'stm32f405.ld')
    _write_text(output_dir / 'main.c', _render_main_c())
    _write_text(
        output_dir / 'model_data.h',
        _render_model_data_header(model_spec, benchmark_config, validation_artifacts),
    )


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

    return {
        'dataset': dataset_config,
        'selection': selection_config,
        'wave_output': wave_output_config,
    }


def _prepare_validation_artifacts(model_project_name: str,
                                  weights_json_path: Path,
                                  validation_config: Dict[str, Any]) -> ValidationArtifacts:
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

    model_engine.build_model()
    loaded_weights_path = _load_requested_model_weights(model_engine, weights_json_path)

    x_input = selected_dataset.reshape2feature(selected_dataset.output_ori)
    batch_size = max(1, x_input.shape[0])
    tf_output = model_engine.model_comp.predict(
        x_input,
        batch_size=batch_size,
        use_scaler=bool(project_manager.config.use_scale),
    )
    tf_output_2d = np.asarray(tf_output, dtype=np.float64).reshape(x_input.shape[0], x_input.shape[1])
    records = _build_validation_records(selected_dataset, tf_output_2d)

    input_data_range = 1.0
    output_data_range = 1.0
    if project_manager.config.use_scale:
        input_data_range = float(model_engine.scaler.scaler_x.data_range_)
        output_data_range = float(model_engine.scaler.scaler_y.data_range_)

    return ValidationArtifacts(
        dataset_type=str(project_manager.config.dataset_type),
        full_data_path=str(project_manager.config.full_data_path),
        sample_rate=float(selected_dataset.fs),
        time_window=time_window,
        input_data_range=input_data_range,
        output_data_range=output_data_range,
        loaded_weights_path=loaded_weights_path,
        records=records,
    )


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


def _find_weight_entry(weights: Iterable[Dict[str, Any]], fragment: str) -> Dict[str, Any]:
    for item in weights:
        name = str(item.get('name', '')).replace('\\', '/')
        if fragment in name:
            return item
    raise KeyError(f'未找到权重项: {fragment}')


def _to_float_matrix(values: Sequence[Sequence[Any]]) -> List[List[float]]:
    return [[float(value) for value in row] for row in values]


def _to_float_vector(values: Sequence[Any]) -> List[float]:
    return [float(value) for value in values]


def _copy_runtime_template(filename: str, target: Path) -> None:
    source = QEMU_HELLO_TEMPLATE_DIR / filename
    if not source.exists():
        raise FileNotFoundError(f'QEMU 模板文件不存在: {source}')
    target.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')


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
    int32_t integer_part = scaled / 1000000;
    int32_t fraction = scaled % 1000000;
    int32_t divisor = 100000;

    if (fraction < 0) {
        fraction = -fraction;
    }

    uart_put_s32(integer_part);
    uart_putc('.');
    while (divisor > 0) {
        uart_putc((char)('0' + ((fraction / divisor) % 10)));
        divisor /= 10;
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
                              port_float *output_value)
{
    uint32_t unit;
    port_float previous_hidden[LSTM_UNITS];
    port_float previous_cell[LSTM_UNITS];
    port_float dense_output[DENSE_UNITS];

    for (unit = 0u; unit < LSTM_UNITS; ++unit) {
        previous_hidden[unit] = hidden_state[unit];
        previous_cell[unit] = cell_state[unit];
    }

    for (unit = 0u; unit < LSTM_UNITS; ++unit) {
        uint32_t input_index;
        uint32_t hidden_index;
        port_float input_gate_acc = lstm_bias[unit + LSTM_UNITS * 0u];
        port_float forget_gate_acc = lstm_bias[unit + LSTM_UNITS * 1u];
        port_float candidate_acc = lstm_bias[unit + LSTM_UNITS * 2u];
        port_float output_gate_acc = lstm_bias[unit + LSTM_UNITS * 3u];

        for (input_index = 0u; input_index < LSTM_INPUT_DIM; ++input_index) {
            port_float input_value = scale_input(input_step[input_index]);
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
        }
    }

    dense_forward_relu(hidden_state, dense_output);
    *output_value = inverse_scale_output(output_forward_linear(dense_output));
}

static void run_validation_record(const port_float sequence[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                  port_float output_sequence[VALIDATION_SEQ_LEN],
                                  uint32_t reset_state_each_run,
                                  port_float hidden_state[LSTM_UNITS],
                                  port_float cell_state[LSTM_UNITS])
{
    uint32_t step;
    if (reset_state_each_run != 0u) {
        zero_buffer(hidden_state, LSTM_UNITS);
        zero_buffer(cell_state, LSTM_UNITS);
    }

    for (step = 0u; step < VALIDATION_SEQ_LEN; ++step) {
        lstm_forward_step(sequence[step], hidden_state, cell_state, &output_sequence[step]);
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
                cell_state
            );
            output_value = validation_output[record_index][VALIDATION_SEQ_LEN - 1u];
        }
    }

    if (dwt_supported != 0u) {
        end_cycles = dwt_read_cycles();
        total_cycles = end_cycles - start_cycles;
    }

    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
        zero_buffer(hidden_state, LSTM_UNITS);
        zero_buffer(cell_state, LSTM_UNITS);
        run_validation_record(
            validation_input[record_index],
            validation_output[record_index],
            0u,
            hidden_state,
            cell_state
        );
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
                                 compress: bool) -> Dict[str, str]:
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

    return output_paths


def _save_wave_file(path: Path,
                    source_name: str,
                    sequences: Sequence[Sequence[float]],
                    validation_artifacts: ValidationArtifacts,
                    compress: bool) -> None:
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
        record_data_dict[record_key] = np.asarray(sequence, dtype=np.float32).reshape(-1, 1)
        record_metadata_dict[record_key] = {
            'standard': {
                'sample_rate': validation_artifacts.sample_rate,
                'channel_names': [source_name],
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
        'max_abs_error': float(np.max(np.abs(diff_flat))) if diff_flat.size else 0.0,
        'c_output_stats': _compute_signal_stats(c_flat),
        'tf_output_stats': _compute_signal_stats(tf_flat),
        'diff_stats': _compute_signal_stats(diff_flat),
    }
    return {
        'overall': overall,
        'per_record': per_record,
    }


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