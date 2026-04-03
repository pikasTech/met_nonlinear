"""LSTM QEMU C 推理 EP 任务实现。"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .external_path_parser import ExternalPath
from .qemu_cli import execute_qemu_workflow


logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
QEMU_HELLO_TEMPLATE_DIR = REPO_ROOT / 'src' / 'tests' / 'qemu' / 'stm32f405_hello'


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


def execute_lstm_qemu_inference_task(ep_path: ExternalPath,
                                     config: Dict[str, Any]) -> bool:
    """执行 qemu-c-inference EP 任务。"""
    ep_path.output_path.mkdir(parents=True, exist_ok=True)

    model_project_name = str(config['model_project_name']).replace('\\', '/')
    benchmark_config = _normalize_benchmark_config(config.get('benchmark_config', {}))
    generation_config = config.get('generation_config', {})
    qemu_config = config.get('qemu_config', {})

    model_dir = _resolve_model_project_dir(model_project_name)
    weights_json_path = _resolve_weights_json_path(model_dir, config.get('weights_file'))
    model_spec = _load_lstm_model_spec(model_project_name, weights_json_path)
    benchmark_input = _normalize_input_sequence(
        benchmark_config['input_sequence'],
        model_spec.input_dim,
    )

    generated_project_dir = _resolve_generated_project_dir(ep_path, generation_config)
    overwrite = bool(generation_config.get('overwrite', True))
    generate_qemu_project(
        output_dir=generated_project_dir,
        model_spec=model_spec,
        benchmark_config=benchmark_config,
        benchmark_input=benchmark_input,
        overwrite=overwrite,
    )

    execution_summary: Dict[str, Any] = {
        'task_type': 'qemu-c-inference',
        'model_project_name': model_project_name,
        'weights_json_path': _relative_or_str(weights_json_path),
        'generated_project_dir': _relative_or_str(generated_project_dir),
        'benchmark_config': {
            **benchmark_config,
            'input_sequence': benchmark_input,
        },
        'qemu_config': qemu_config,
    }

    action = str(qemu_config.get('action', 'build-run'))
    machine = str(qemu_config.get('machine', 'olimex-stm32-h405'))
    timeout = int(qemu_config.get('timeout', 5))
    qemu_path = qemu_config.get('qemu_path')
    gcc_path = qemu_config.get('gcc_path')
    linker_script = qemu_config.get('linker_script')
    output_path = qemu_config.get('output')

    if action == 'generate':
        _write_json(ep_path.output_path / 'benchmark_summary.json', {
            **execution_summary,
            'action': 'generate',
            'status': 'generated',
        })
        _write_json(ep_path.output_path / 'task_metadata.json', {
            'task_info': config['task_info'],
            'output_files': [_relative_or_str(generated_project_dir)],
            'action': 'generate',
        })
        logger.info('QEMU 工程已生成: %s', generated_project_dir)
        return True

    run_results: List[Dict[str, Any]] = []
    build_result: Optional[Dict[str, Any]] = None

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
                'output_files': [_relative_or_str(ep_path.output_path / 'benchmark_summary.json')],
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
                success_patterns=['output='],
            )
            parsed_output = _enrich_benchmark_output(
                _parse_benchmark_stdout(
                    str(run_workflow.get('run', {}).get('stdout', ''))
                ),
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
                    'output_files': [_relative_or_str(ep_path.output_path / 'benchmark_summary.json')],
                    'action': action,
                })
                return False

    execution_summary['build'] = build_result
    execution_summary['runs'] = run_results
    if run_results:
        execution_summary['aggregated'] = _aggregate_run_results(run_results)

    _write_json(ep_path.output_path / 'benchmark_summary.json', execution_summary)
    _write_json(ep_path.output_path / 'task_metadata.json', {
        'task_info': config['task_info'],
        'output_files': [
            _relative_or_str(ep_path.output_path / 'benchmark_summary.json'),
            _relative_or_str(generated_project_dir),
        ],
        'action': action,
    })
    logger.info('QEMU C 推理任务完成: %s', ep_path.output_path / 'benchmark_summary.json')
    return True


def generate_qemu_project(output_dir: Path,
                          model_spec: LstmModelSpec,
                          benchmark_config: Dict[str, Any],
                          benchmark_input: List[List[float]],
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
        _render_model_data_header(model_spec, benchmark_config, benchmark_input),
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
    normalized.setdefault('iterations', 1000)
    normalized.setdefault('input_sequence', [0.1])
    normalized.setdefault('reset_state_each_run', True)
    normalized.setdefault('repeat_runs', 1)
    return normalized


def _normalize_input_sequence(raw_input: Sequence[Any],
                              input_dim: int) -> List[List[float]]:
    if not raw_input:
        raise ValueError('benchmark_config.input_sequence 不能为空')

    first_item = raw_input[0]
    if isinstance(first_item, (list, tuple)):
        normalized: List[List[float]] = []
        for step in raw_input:
            row = [float(value) for value in step]
            if len(row) != input_dim:
                raise ValueError(
                    f'input_sequence 每个时间步必须包含 {input_dim} 个输入，实际为 {len(row)}'
                )
            normalized.append(row)
        return normalized

    if input_dim != 1:
        raise ValueError(
            '当前模型输入维度大于 1 时，benchmark_config.input_sequence 必须使用二维数组'
        )
    return [[float(value)] for value in raw_input]


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
                              benchmark_input: List[List[float]]) -> str:
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
        f'#define BENCHMARK_SEQ_LEN {len(benchmark_input)}u',
        f'#define BENCHMARK_REPEAT_RUNS {int(benchmark_config["repeat_runs"])}u',
        f'#define BENCHMARK_RESET_STATE_EACH_RUN {1 if benchmark_config.get("reset_state_each_run", True) else 0}u',
        '',
        f'static const port_float benchmark_input[BENCHMARK_SEQ_LEN][LSTM_INPUT_DIM] = {_render_initializer(benchmark_input)};',
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

static port_float abs_approx(port_float value)
{
    return value < 0.0f ? -value : value;
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

static void lstm_forward(const port_float sequence[BENCHMARK_SEQ_LEN][LSTM_INPUT_DIM],
                         port_float hidden_state[LSTM_UNITS],
                         port_float cell_state[LSTM_UNITS])
{
    uint32_t step;
    port_float previous_hidden[LSTM_UNITS];
    port_float previous_cell[LSTM_UNITS];

    for (step = 0u; step < BENCHMARK_SEQ_LEN; ++step) {
        uint32_t unit;
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
                port_float input_value = sequence[step][input_index];
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
    }
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

int main(void)
{
    uint32_t iteration;
    uint32_t dwt_supported;
    port_float hidden_state[LSTM_UNITS];
    port_float cell_state[LSTM_UNITS];
    port_float dense_output[DENSE_UNITS];
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
        if (BENCHMARK_RESET_STATE_EACH_RUN != 0u) {
            zero_buffer(hidden_state, LSTM_UNITS);
            zero_buffer(cell_state, LSTM_UNITS);
        }

        lstm_forward(benchmark_input, hidden_state, cell_state);
        dense_forward_relu(hidden_state, dense_output);
        output_value = output_forward_linear(dense_output);
    }

    if (dwt_supported != 0u) {
        end_cycles = dwt_read_cycles();
        total_cycles = end_cycles - start_cycles;
    }

    uart_puts("LSTM_QEMU_BENCHMARK\n");
    uart_puts("iterations=");
    uart_put_u32(BENCHMARK_ITERATIONS);
    uart_puts("\nseq_len=");
    uart_put_u32(BENCHMARK_SEQ_LEN);
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
    return aggregated


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