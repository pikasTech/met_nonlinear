"""Tests for qemu-c-inference EP task."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


def _sample_lstm_weights() -> list[dict]:
    return [
        {
            'name': 'sequential/lstm/lstm_cell/kernel:0',
            'shape': [1, 8],
            'value': [[0.1, 0.2, 0.3, 0.4, 0.11, 0.21, 0.31, 0.41]],
        },
        {
            'name': 'sequential/lstm/lstm_cell/recurrent_kernel:0',
            'shape': [2, 8],
            'value': [
                [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08],
                [0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16],
            ],
        },
        {
            'name': 'sequential/lstm/lstm_cell/bias:0',
            'shape': [8],
            'value': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08],
        },
        {
            'name': 'sequential/dense/kernel:0',
            'shape': [2, 2],
            'value': [[0.2, 0.3], [0.4, 0.5]],
        },
        {
            'name': 'sequential/dense/bias:0',
            'shape': [2],
            'value': [0.1, 0.2],
        },
        {
            'name': 'sequential/dense_1/kernel:0',
            'shape': [2, 1],
            'value': [[0.6], [0.7]],
        },
        {
            'name': 'sequential/dense_1/bias:0',
            'shape': [1],
            'value': [0.3],
        },
    ]


def _sample_grn_weights() -> list[dict]:
    return [
        {
            'name': 'sequential/gru/gru_cell/kernel:0',
            'shape': [1, 6],
            'value': [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6]],
        },
        {
            'name': 'sequential/gru/gru_cell/recurrent_kernel:0',
            'shape': [2, 6],
            'value': [
                [0.01, 0.02, 0.03, 0.04, 0.05, 0.06],
                [0.07, 0.08, 0.09, 0.10, 0.11, 0.12],
            ],
        },
        {
            'name': 'sequential/gru/gru_cell/bias:0',
            'shape': [2, 6],
            'value': [
                [0.01, 0.02, 0.03, 0.04, 0.05, 0.06],
                [0.07, 0.08, 0.09, 0.10, 0.11, 0.12],
            ],
        },
        {
            'name': 'sequential/dense/kernel:0',
            'shape': [2, 2],
            'value': [[0.2, 0.3], [0.4, 0.5]],
        },
        {
            'name': 'sequential/dense/bias:0',
            'shape': [2],
            'value': [0.1, 0.2],
        },
        {
            'name': 'sequential/dense_1/kernel:0',
            'shape': [2, 1],
            'value': [[0.6], [0.7]],
        },
        {
            'name': 'sequential/dense_1/bias:0',
            'shape': [1],
            'value': [0.3],
        },
    ]


def _sample_lstm_transformer_weights() -> list[dict]:
    return [
        {
            'name': 'lstm_backbone/lstm_cell/kernel:0',
            'shape': [1, 8],
            'value': [[0.11, 0.12, 0.13, 0.14, 0.21, 0.22, 0.23, 0.24]],
        },
        {
            'name': 'lstm_backbone/lstm_cell/recurrent_kernel:0',
            'shape': [2, 8],
            'value': [
                [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08],
                [0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16],
            ],
        },
        {
            'name': 'lstm_backbone/lstm_cell/bias:0',
            'shape': [8],
            'value': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08],
        },
        {
            'name': 'transformer_mha_0/query/kernel:0',
            'shape': [2, 1, 2],
            'value': [
                [[0.11, 0.12]],
                [[0.13, 0.14]],
            ],
        },
        {
            'name': 'transformer_mha_0/query/bias:0',
            'shape': [1, 2],
            'value': [[0.01, 0.02]],
        },
        {
            'name': 'transformer_mha_0/key/kernel:0',
            'shape': [2, 1, 2],
            'value': [
                [[0.21, 0.22]],
                [[0.23, 0.24]],
            ],
        },
        {
            'name': 'transformer_mha_0/key/bias:0',
            'shape': [1, 2],
            'value': [[0.00, 0.00]],
        },
        {
            'name': 'transformer_mha_0/value/kernel:0',
            'shape': [2, 1, 2],
            'value': [
                [[0.31, 0.32]],
                [[0.33, 0.34]],
            ],
        },
        {
            'name': 'transformer_mha_0/value/bias:0',
            'shape': [1, 2],
            'value': [[0.01, -0.01]],
        },
        {
            'name': 'transformer_mha_0/attention_output/kernel:0',
            'shape': [1, 2, 2],
            'value': [
                [
                    [0.15, 0.16],
                    [0.17, 0.18],
                ]
            ],
        },
        {
            'name': 'transformer_mha_0/attention_output/bias:0',
            'shape': [2],
            'value': [0.01, 0.02],
        },
        {
            'name': 'transformer_ln_attn_0/gamma:0',
            'shape': [2],
            'value': [1.0, 1.1],
        },
        {
            'name': 'transformer_ln_attn_0/beta:0',
            'shape': [2],
            'value': [0.01, -0.02],
        },
        {
            'name': 'transformer_ffn_expand_0/kernel:0',
            'shape': [2, 3],
            'value': [
                [0.11, 0.12, 0.13],
                [0.14, 0.15, 0.16],
            ],
        },
        {
            'name': 'transformer_ffn_expand_0/bias:0',
            'shape': [3],
            'value': [0.01, 0.02, 0.03],
        },
        {
            'name': 'transformer_ffn_project_0/kernel:0',
            'shape': [3, 2],
            'value': [
                [0.21, 0.22],
                [0.23, 0.24],
                [0.25, 0.26],
            ],
        },
        {
            'name': 'transformer_ffn_project_0/bias:0',
            'shape': [2],
            'value': [0.01, 0.02],
        },
        {
            'name': 'transformer_ln_ffn_0/gamma:0',
            'shape': [2],
            'value': [0.9, 1.0],
        },
        {
            'name': 'transformer_ln_ffn_0/beta:0',
            'shape': [2],
            'value': [0.03, -0.01],
        },
        {
            'name': 'post_dense/kernel:0',
            'shape': [2, 2],
            'value': [
                [0.31, 0.32],
                [0.33, 0.34],
            ],
        },
        {
            'name': 'post_dense/bias:0',
            'shape': [2],
            'value': [0.01, 0.02],
        },
        {
            'name': 'output/kernel:0',
            'shape': [2, 1],
            'value': [
                [0.41],
                [0.42],
            ],
        },
        {
            'name': 'output/bias:0',
            'shape': [1],
            'value': [0.05],
        },
    ]


def _sample_onedcnn_weights() -> list[dict]:
    return [
        {
            'name': 'conv_1/kernel:0',
            'shape': [3, 1, 2],
            'value': [
                [[0.11, 0.12]],
                [[0.13, 0.14]],
                [[0.15, 0.16]],
            ],
        },
        {
            'name': 'conv_1/bias:0',
            'shape': [2],
            'value': [0.01, 0.02],
        },
        {
            'name': 'conv_2/kernel:0',
            'shape': [3, 2, 2],
            'value': [
                [[0.21, 0.22], [0.23, 0.24]],
                [[0.25, 0.26], [0.27, 0.28]],
                [[0.29, 0.30], [0.31, 0.32]],
            ],
        },
        {
            'name': 'conv_2/bias:0',
            'shape': [2],
            'value': [0.03, 0.04],
        },
        {
            'name': 'post_dense_1/kernel:0',
            'shape': [1, 2, 2],
            'value': [
                [[0.41, 0.42], [0.43, 0.44]],
            ],
        },
        {
            'name': 'post_dense_1/bias:0',
            'shape': [2],
            'value': [0.05, 0.06],
        },
        {
            'name': 'output_conv/kernel:0',
            'shape': [1, 2, 1],
            'value': [
                [[0.51], [0.52]],
            ],
        },
        {
            'name': 'output_conv/bias:0',
            'shape': [1],
            'value': [0.07],
        },
    ]


def _sample_tcn_weights() -> list[dict]:
    return [
        {
            'name': 'initial_projection/kernel:0',
            'shape': [1, 1, 2],
            'value': [
                [[0.11, 0.12]],
            ],
        },
        {
            'name': 'initial_projection/bias:0',
            'shape': [2],
            'value': [0.01, 0.02],
        },
        {
            'name': 'temporal_block_1_conv_1/kernel:0',
            'shape': [3, 2, 2],
            'value': [
                [[0.21, 0.22], [0.23, 0.24]],
                [[0.25, 0.26], [0.27, 0.28]],
                [[0.29, 0.30], [0.31, 0.32]],
            ],
        },
        {
            'name': 'temporal_block_1_conv_1/bias:0',
            'shape': [2],
            'value': [0.03, 0.04],
        },
        {
            'name': 'temporal_block_1_conv_2/kernel:0',
            'shape': [3, 2, 2],
            'value': [
                [[0.33, 0.34], [0.35, 0.36]],
                [[0.37, 0.38], [0.39, 0.40]],
                [[0.41, 0.42], [0.43, 0.44]],
            ],
        },
        {
            'name': 'temporal_block_1_conv_2/bias:0',
            'shape': [2],
            'value': [0.05, 0.06],
        },
        {
            'name': 'post_dense_1/kernel:0',
            'shape': [1, 2, 2],
            'value': [
                [[0.51, 0.52], [0.53, 0.54]],
            ],
        },
        {
            'name': 'post_dense_1/bias:0',
            'shape': [2],
            'value': [0.07, 0.08],
        },
        {
            'name': 'output_conv/kernel:0',
            'shape': [1, 2, 1],
            'value': [
                [[0.61], [0.62]],
            ],
        },
        {
            'name': 'output_conv/bias:0',
            'shape': [1],
            'value': [0.09],
        },
    ]


class TestQemuCInferenceTemplate:
    def test_create_qemu_c_inference_template(self, tmp_path):
        from core.external_cli_handler import _create_qemu_c_inference_template
        from core.external_path_parser import ExternalPath

        ep_path = ExternalPath(
            project_name='demo',
            task_type='qemu-c-inference',
            task_name='demo_task',
            full_path=tmp_path / 'demo_task',
            config_path=tmp_path / 'demo_task' / 'config.json',
            output_path=tmp_path / 'demo_task' / 'data',
        )

        template = _create_qemu_c_inference_template(ep_path)
        assert template['task_info']['task_type'] == 'qemu-c-inference'
        assert template['model_project_name'] == '00_MAE_VS_AFMAE/LSTMu16_base'
        assert template['validation_config']['dataset']['dataset_type'] == 'MET'
        assert template['qemu_config']['action'] == 'build-run'


class TestExecuteLstmQemuInferenceTask:
    @patch('core.lstm_qemu_ep_task.execute_qemu_workflow')
    @patch('core.lstm_qemu_ep_task._prepare_validation_artifacts')
    def test_execute_build_run_success(self, mock_prepare_validation_artifacts, mock_execute_qemu_workflow, tmp_path, monkeypatch):
        from core.external_path_parser import ExternalPath
        import core.lstm_qemu_ep_task as task_module

        actual_template_dir = task_module.QEMU_HELLO_TEMPLATE_DIR
        monkeypatch.setattr(task_module, 'REPO_ROOT', tmp_path)
        monkeypatch.setattr(task_module, 'QEMU_HELLO_TEMPLATE_DIR', actual_template_dir)

        mock_prepare_validation_artifacts.return_value = task_module.ValidationArtifacts(
            dataset_type='MET',
            full_data_path='data/M50',
            sample_rate=2000.0,
            time_window={
                'start_time_s': 0.0,
                'end_time_s': 0.003,
                'sample_count': 3,
            },
            input_data_range=2.0,
            output_data_range=4.0,
            loaded_weights_path=tmp_path / 'projects' / 'demo_project' / 'data' / 'best_val.weights.h5',
            records=[
                task_module.ValidationRecord(
                    record_id='mag0.4_freq10',
                    magnitude=0.4,
                    frequency=10.0,
                    input_sequence=[[0.1], [0.2], [0.3]],
                    target_sequence=[0.5, 0.6, 0.7],
                    tf_output_sequence=[0.11, 0.22, 0.33],
                ),
                task_module.ValidationRecord(
                    record_id='mag0.4_freq20',
                    magnitude=0.4,
                    frequency=20.0,
                    input_sequence=[[0.4], [0.5], [0.6]],
                    target_sequence=[0.8, 0.9, 1.0],
                    tf_output_sequence=[0.44, 0.55, 0.66],
                ),
            ],
            tf_debug_sequences={
                'input_scaled': [
                    [[0.05], [0.10], [0.15]],
                    [[0.20], [0.25], [0.30]],
                ],
                'lstm_hidden': [
                    [[0.01, 0.02], [0.03, 0.04], [0.05, 0.06]],
                    [[0.07, 0.08], [0.09, 0.10], [0.11, 0.12]],
                ],
                'dense_output': [
                    [[0.10, 0.20], [0.30, 0.40], [0.50, 0.60]],
                    [[0.70, 0.80], [0.90, 1.00], [1.10, 1.20]],
                ],
                'output_scaled': [
                    [[0.0275], [0.0550], [0.0825]],
                    [[0.1100], [0.1375], [0.1650]],
                ],
            },
        )

        model_dir = tmp_path / 'projects' / 'demo_project' / 'data'
        model_dir.mkdir(parents=True)
        with open(model_dir / 'best_val.weights.json', 'w', encoding='utf-8') as file_obj:
            json.dump(_sample_lstm_weights(), file_obj)

        ep_path = ExternalPath(
            project_name='demo_task',
            task_type='qemu-c-inference',
            task_name='demo_task',
            full_path=tmp_path / 'ex_projects' / 'inference' / 'qemu-c-inference' / 'demo_task',
            config_path=tmp_path / 'ex_projects' / 'inference' / 'qemu-c-inference' / 'demo_task' / 'config.json',
            output_path=tmp_path / 'ex_projects' / 'inference' / 'qemu-c-inference' / 'demo_task' / 'data',
        )

        mock_execute_qemu_workflow.side_effect = [
            {
                'action': 'build',
                'exit_code': 0,
                'build': {'elapsed_seconds': 0.12},
            },
            {
                'action': 'run',
                'exit_code': 0,
                'run': {
                    'elapsed_seconds': 0.34,
                    'stdout': (
                        'iterations=100\n'
                        'dwt_supported=0\n'
                        'timer_source=host_elapsed\n'
                        'measurement_unit=seconds\n'
                        'measurement_per_iter=0.0034\n'
                        'output=0.330000\n'
                        'validation_record_0=0.110000,0.220000,0.330000\n'
                        'validation_input_scaled_0=0.050000;0.100000;0.150000\n'
                        'validation_lstm_hidden_0=0.010000,0.020000;0.030000,0.040000;0.050000,0.060000\n'
                        'validation_dense_output_0=0.100000,0.200000;0.300000,0.400000;0.500000,0.600000\n'
                        'validation_output_scaled_0=0.027500;0.055000;0.082500\n'
                        'validation_record_1=0.440000,0.550000,0.660000\n'
                        'validation_input_scaled_1=0.200000;0.250000;0.300000\n'
                        'validation_lstm_hidden_1=0.070000,0.080000;0.090000,0.100000;0.110000,0.120000\n'
                        'validation_dense_output_1=0.700000,0.800000;0.900000,1.000000;1.100000,1.200000\n'
                        'validation_output_scaled_1=0.110000;0.137500;0.165000\n'
                        'validation_complete=1\n'
                    ),
                    'stderr': '',
                    'timed_out': False,
                },
            },
            {
                'action': 'run',
                'exit_code': 0,
                'run': {
                    'elapsed_seconds': 0.35,
                    'stdout': (
                        'iterations=100\n'
                        'dwt_supported=0\n'
                        'timer_source=host_elapsed\n'
                        'measurement_unit=seconds\n'
                        'measurement_per_iter=0.0035\n'
                        'output=0.330000\n'
                        'benchmark_complete=1\n'
                    ),
                    'stderr': '',
                    'timed_out': False,
                },
            },
            {
                'action': 'run',
                'exit_code': 0,
                'run': {
                    'elapsed_seconds': 0.36,
                    'stdout': (
                        'iterations=100\n'
                        'dwt_supported=0\n'
                        'timer_source=host_elapsed\n'
                        'measurement_unit=seconds\n'
                        'measurement_per_iter=0.0036\n'
                        'output=0.330000\n'
                        'validation_record_0=0.110000,0.220000,0.330000\n'
                        'validation_input_scaled_0=0.050000;0.100000;0.150000\n'
                        'validation_lstm_hidden_0=0.010000,0.020000;0.030000,0.040000;0.050000,0.060000\n'
                        'validation_dense_output_0=0.100000,0.200000;0.300000,0.400000;0.500000,0.600000\n'
                        'validation_output_scaled_0=0.027500;0.055000;0.082500\n'
                        'validation_record_1=0.440000,0.550000,0.660000\n'
                        'validation_input_scaled_1=0.200000;0.250000;0.300000\n'
                        'validation_lstm_hidden_1=0.070000,0.080000;0.090000,0.100000;0.110000,0.120000\n'
                        'validation_dense_output_1=0.700000,0.800000;0.900000,1.000000;1.100000,1.200000\n'
                        'validation_output_scaled_1=0.110000;0.137500;0.165000\n'
                        'validation_complete=1\n'
                    ),
                    'stderr': '',
                    'timed_out': False,
                },
            },
        ]

        config = {
            'task_info': {
                'task_type': 'qemu-c-inference',
            },
            'model_project_name': 'demo_project',
            'benchmark_config': {
                'iterations': 100,
                'reset_state_each_run': True,
                'repeat_runs': 2,
            },
            'validation_config': {
                'dataset': {
                    'dataset_type': 'MET',
                    'data_path': 'data/M50',
                    'sample_rate': 2000,
                    'time_clipped_s': 4.0,
                    'target_sweep': 2,
                },
                'selection': {
                    'magnitudes': [0.4],
                    'frequencies': [10.0, 20.0],
                    'start_time_s': 0.0,
                    'end_time_s': 0.003,
                },
                'wave_output': {
                    'compress': True,
                },
            },
            'generation_config': {
                'project_dir': 'qemu_project',
                'overwrite': True,
            },
            'qemu_config': {
                'action': 'build-run',
                'timeout': 5,
            },
        }

        result = task_module.execute_lstm_qemu_inference_task(ep_path, config)

        assert result is True
        generated_dir = ep_path.full_path / 'qemu_project'
        assert (generated_dir / 'main.c').exists()
        assert (generated_dir / 'model_data.h').exists()
        assert (generated_dir / 'startup.c').exists()
        assert (generated_dir / 'stm32f405.ld').exists()
        keil_project_dir = ep_path.full_path / 'keil_project'
        assert (keil_project_dir / 'Application' / 'benchmark_keil_port.c').exists()
        assert (keil_project_dir / 'MDK-ARM' / 'Electrochemical geophone.uvprojx').exists()
        main_c_content = (generated_dir / 'main.c').read_text(encoding='utf-8')
        assert 'if (scaled < 0)' in main_c_content
        assert 'validation_input_scaled_' in main_c_content
        assert '#if defined(BENCHMARK_PLATFORM_KEIL)' in main_c_content
        assert 'benchmark_keil_platform_init();' in main_c_content
        assert 'static __attribute__((noinline)) void uart_putc(char ch)' in main_c_content
        assert 'static __attribute__((noinline)) void uart_puts(const char *message)' in main_c_content
        assert 'static __attribute__((noinline)) void uart_put_u32(uint32_t value)' in main_c_content
        assert 'static __attribute__((noinline)) void uart_put_fixed6(port_float value)' in main_c_content
        assert 'static __attribute__((noinline)) void uart_put_matrix_rows(const port_float *values,' in main_c_content
        assert 'benchmark_keil_get_tick_us();' in main_c_content
        assert 'wall_time_total_ms' in main_c_content
        assert 'wall_time_per_iter_ms' in main_c_content

        keil_port_content = (keil_project_dir / 'Application' / 'benchmark_keil_port.c').read_text(encoding='utf-8')
        assert 'benchmark_keil_write_string' in keil_port_content
        assert 'benchmark_gpio_config_usart' in keil_port_content
        assert 'benchmark_uart_config' in keil_port_content
        assert 'benchmark_enable_cycle_counter' in keil_port_content
        assert 'USART3' in keil_port_content
        assert 'benchmark_keil_get_tick_us' in keil_port_content
        assert 'HAL_Init();' not in keil_port_content
        assert 'MX_DMA_Init' not in keil_port_content
        assert 'SystemClock_Config' not in keil_port_content

        main_h_content = (keil_project_dir / 'Application' / 'main.h').read_text(encoding='utf-8')
        assert '#include <stdint.h>' in main_h_content
        assert 'stm32f4xx_hal.h' not in main_h_content

        it_content = (keil_project_dir / 'Application' / 'stm32f4xx_it.c').read_text(encoding='utf-8')
        assert 'TIM3_IRQHandler' in it_content
        assert 'USART1_IRQHandler' in it_content
        assert 'DMA1_Stream3_IRQHandler' in it_content
        assert 'SysTick_Handler' in it_content
        assert 'HAL_TIM_IRQHandler' not in it_content

        uvprojx_content = (keil_project_dir / 'MDK-ARM' / 'Electrochemical geophone.uvprojx').read_text(encoding='utf-8')
        assert 'BENCHMARK_PLATFORM_KEIL' in uvprojx_content
        assert 'STM32F405xx' in uvprojx_content
        assert 'qemu_project\\main.c' in uvprojx_content
        assert 'benchmark_keil_port.c' in uvprojx_content
        assert 'system_stm32f4xx.c' in uvprojx_content
        assert 'stm32f4xx_it.c' in uvprojx_content
        assert 'Hardware\\gpio.c' not in uvprojx_content
        assert 'Hardware\\usart.c' not in uvprojx_content
        assert 'Hardware\\tim.c' not in uvprojx_content
        assert 'stm32f4xx_hal_uart.c' not in uvprojx_content
        assert 'stm32f4xx_hal_dma.c' not in uvprojx_content

        summary_path = ep_path.output_path / 'benchmark_summary.json'
        assert summary_path.exists()
        with open(summary_path, 'r', encoding='utf-8') as file_obj:
            summary = json.load(file_obj)

        assert summary['aggregated']['run_count'] == 2
        assert summary['aggregated']['avg_measurement_per_iter'] == pytest.approx(0.00345)
        assert summary['aggregated']['measurement_sources'] == ['host_elapsed']
        assert summary['aggregated']['avg_host_elapsed_seconds'] == pytest.approx(0.345)
        assert summary['keil_project_dir'].endswith('keil_project')
        assert summary['comparison']['mae'] == pytest.approx(0.0)
        assert 'c_output_wave' in summary['wave_paths']
        assert 'tf_lstm_hidden_wave' in summary['wave_paths']
        assert 'c_lstm_hidden_wave' in summary['wave_paths']
        assert 'comparison_plot_0' in summary['plot_paths']
        assert (tmp_path / summary['plot_paths']['comparison_plot_0']).exists()
        comparison_path = ep_path.output_path / 'validation_comparison.json'
        with open(comparison_path, 'r', encoding='utf-8') as file_obj:
            comparison_payload = json.load(file_obj)
        assert 'plot_paths' in comparison_payload
        assert comparison_payload['overall']['mse'] == pytest.approx(0.0)
        assert mock_execute_qemu_workflow.call_count == 4

    @patch('core.lstm_qemu_ep_task.execute_qemu_workflow')
    @patch('core.lstm_qemu_ep_task._prepare_validation_artifacts')
    def test_execute_build_run_success_grn(self, mock_prepare_validation_artifacts, mock_execute_qemu_workflow, tmp_path, monkeypatch):
        from core.external_path_parser import ExternalPath
        import core.lstm_qemu_ep_task as task_module

        actual_template_dir = task_module.QEMU_HELLO_TEMPLATE_DIR
        monkeypatch.setattr(task_module, 'REPO_ROOT', tmp_path)
        monkeypatch.setattr(task_module, 'QEMU_HELLO_TEMPLATE_DIR', actual_template_dir)

        mock_prepare_validation_artifacts.return_value = task_module.ValidationArtifacts(
            dataset_type='MET',
            full_data_path='data/M50',
            sample_rate=2000.0,
            time_window={
                'start_time_s': 0.0,
                'end_time_s': 0.003,
                'sample_count': 3,
            },
            input_data_range=2.0,
            output_data_range=4.0,
            loaded_weights_path=tmp_path / 'projects' / 'demo_grn' / 'data' / 'best_val.weights.h5',
            records=[
                task_module.ValidationRecord(
                    record_id='mag0.4_freq10',
                    magnitude=0.4,
                    frequency=10.0,
                    input_sequence=[[0.1], [0.2], [0.3]],
                    target_sequence=[0.5, 0.6, 0.7],
                    tf_output_sequence=[0.11, 0.22, 0.33],
                ),
            ],
            tf_debug_sequences={
                'input_scaled': [
                    [[0.05], [0.10], [0.15]],
                ],
                'gru_hidden': [
                    [[0.01, 0.02], [0.03, 0.04], [0.05, 0.06]],
                ],
                'dense_output': [
                    [[0.10, 0.20], [0.30, 0.40], [0.50, 0.60]],
                ],
                'output_scaled': [
                    [[0.0275], [0.0550], [0.0825]],
                ],
            },
        )

        model_dir = tmp_path / 'projects' / 'demo_grn' / 'data'
        model_dir.mkdir(parents=True)
        with open(model_dir / 'best_val.weights.json', 'w', encoding='utf-8') as file_obj:
            json.dump(_sample_grn_weights(), file_obj)

        ep_path = ExternalPath(
            project_name='demo_grn_task',
            task_type='qemu-c-inference',
            task_name='demo_grn_task',
            full_path=tmp_path / 'ex_projects' / 'inference' / 'qemu-c-inference' / 'demo_grn_task',
            config_path=tmp_path / 'ex_projects' / 'inference' / 'qemu-c-inference' / 'demo_grn_task' / 'config.json',
            output_path=tmp_path / 'ex_projects' / 'inference' / 'qemu-c-inference' / 'demo_grn_task' / 'data',
        )

        mock_execute_qemu_workflow.side_effect = [
            {
                'action': 'build',
                'exit_code': 0,
                'build': {'elapsed_seconds': 0.12},
            },
            {
                'action': 'run',
                'exit_code': 0,
                'run': {
                    'elapsed_seconds': 0.20,
                    'stdout': (
                        'iterations=100\n'
                        'dwt_supported=0\n'
                        'timer_source=host_elapsed\n'
                        'measurement_unit=seconds\n'
                        'measurement_per_iter=0.0020\n'
                        'output=0.330000\n'
                        'benchmark_complete=1\n'
                    ),
                    'stderr': '',
                    'timed_out': False,
                },
            },
            {
                'action': 'run',
                'exit_code': 0,
                'run': {
                    'elapsed_seconds': 0.22,
                    'stdout': (
                        'iterations=100\n'
                        'dwt_supported=0\n'
                        'timer_source=host_elapsed\n'
                        'measurement_unit=seconds\n'
                        'measurement_per_iter=0.0022\n'
                        'output=0.330000\n'
                        'validation_record_0=0.110000,0.220000,0.330000\n'
                        'validation_input_scaled_0=0.050000;0.100000;0.150000\n'
                        'validation_gru_hidden_0=0.010000,0.020000;0.030000,0.040000;0.050000,0.060000\n'
                        'validation_dense_output_0=0.100000,0.200000;0.300000,0.400000;0.500000,0.600000\n'
                        'validation_output_scaled_0=0.027500;0.055000;0.082500\n'
                        'validation_complete=1\n'
                    ),
                    'stderr': '',
                    'timed_out': False,
                },
            },
        ]

        config = {
            'task_info': {
                'task_type': 'qemu-c-inference',
            },
            'model_project_name': 'demo_grn',
            'benchmark_config': {
                'iterations': 100,
                'reset_state_each_run': True,
                'repeat_runs': 1,
            },
            'validation_config': {
                'dataset': {
                    'dataset_type': 'MET',
                    'data_path': 'data/M50',
                    'sample_rate': 2000,
                    'time_clipped_s': 4.0,
                    'target_sweep': 2,
                },
                'selection': {
                    'magnitudes': [0.4],
                    'frequencies': [10.0],
                    'start_time_s': 0.0,
                    'end_time_s': 0.003,
                },
                'wave_output': {
                    'compress': True,
                },
            },
            'generation_config': {
                'project_dir': 'qemu_project',
                'overwrite': True,
            },
            'qemu_config': {
                'action': 'build-run',
                'timeout': 5,
            },
        }

        result = task_module.execute_lstm_qemu_inference_task(ep_path, config)

        assert result is True
        generated_dir = ep_path.full_path / 'qemu_project'
        main_c_content = (generated_dir / 'main.c').read_text(encoding='utf-8')
        assert 'validation_gru_hidden_' in main_c_content
        assert 'gru_forward_step(' in main_c_content

        summary_path = ep_path.output_path / 'benchmark_summary.json'
        with open(summary_path, 'r', encoding='utf-8') as file_obj:
            summary = json.load(file_obj)

        assert summary['model_type'] == 'grn'
        assert summary['comparison']['mse'] == pytest.approx(0.0)
        assert 'tf_gru_hidden_wave' in summary['wave_paths']
        assert 'c_gru_hidden_wave' in summary['wave_paths']

    @patch('core.lstm_qemu_ep_task.execute_qemu_workflow')
    @patch('core.lstm_qemu_ep_task._prepare_validation_artifacts')
    def test_execute_build_run_success_lstm_transformer(self, mock_prepare_validation_artifacts, mock_execute_qemu_workflow, tmp_path, monkeypatch):
        from core.external_path_parser import ExternalPath
        import core.lstm_qemu_ep_task as task_module

        actual_template_dir = task_module.QEMU_HELLO_TEMPLATE_DIR
        monkeypatch.setattr(task_module, 'REPO_ROOT', tmp_path)
        monkeypatch.setattr(task_module, 'QEMU_HELLO_TEMPLATE_DIR', actual_template_dir)

        mock_prepare_validation_artifacts.return_value = task_module.ValidationArtifacts(
            dataset_type='MET',
            full_data_path='data/M50',
            sample_rate=2000.0,
            time_window={
                'start_time_s': 0.0,
                'end_time_s': 0.003,
                'sample_count': 3,
            },
            input_data_range=2.0,
            output_data_range=4.0,
            loaded_weights_path=tmp_path / 'projects' / 'demo_lstm_transformer' / 'data' / 'best_val.weights.h5',
            records=[
                task_module.ValidationRecord(
                    record_id='mag0.4_freq10',
                    magnitude=0.4,
                    frequency=10.0,
                    input_sequence=[[0.1], [0.2], [0.3]],
                    target_sequence=[0.5, 0.6, 0.7],
                    tf_output_sequence=[0.11, 0.22, 0.33],
                ),
            ],
            tf_debug_sequences={
                'input_scaled': [
                    [[0.05], [0.10], [0.15]],
                ],
                'lstm_hidden': [
                    [[0.01, 0.02], [0.03, 0.04], [0.05, 0.06]],
                ],
                'transformer_ln_attn_0': [
                    [[0.10, 0.11], [0.12, 0.13], [0.14, 0.15]],
                ],
                'transformer_ln_ffn_0': [
                    [[0.16, 0.17], [0.18, 0.19], [0.20, 0.21]],
                ],
                'post_dense': [
                    [[0.22, 0.23], [0.24, 0.25], [0.26, 0.27]],
                ],
                'output_scaled': [
                    [[0.0275], [0.0550], [0.0825]],
                ],
            },
        )

        project_dir = tmp_path / 'projects' / 'demo_lstm_transformer'
        model_dir = project_dir / 'data'
        model_dir.mkdir(parents=True)
        with open(model_dir / 'best_val.weights.json', 'w', encoding='utf-8') as file_obj:
            json.dump(_sample_lstm_transformer_weights(), file_obj)
        with open(project_dir / 'config.json', 'w', encoding='utf-8') as file_obj:
            json.dump({
                'use_model': 'LSTMTransformer',
                'model_subcfg': {
                    'attention_pool_size': 2,
                    'dense_activation': 'relu',
                    'transformer_layers': 1,
                },
            }, file_obj)

        ep_path = ExternalPath(
            project_name='demo_lstm_transformer_task',
            task_type='qemu-c-inference',
            task_name='demo_lstm_transformer_task',
            full_path=tmp_path / 'ex_projects' / 'inference' / 'qemu-c-inference' / 'demo_lstm_transformer_task',
            config_path=tmp_path / 'ex_projects' / 'inference' / 'qemu-c-inference' / 'demo_lstm_transformer_task' / 'config.json',
            output_path=tmp_path / 'ex_projects' / 'inference' / 'qemu-c-inference' / 'demo_lstm_transformer_task' / 'data',
        )

        mock_execute_qemu_workflow.side_effect = [
            {
                'action': 'build',
                'exit_code': 0,
                'build': {'elapsed_seconds': 0.11},
            },
            {
                'action': 'run',
                'exit_code': 0,
                'run': {
                    'elapsed_seconds': 0.21,
                    'stdout': (
                        'iterations=100\n'
                        'dwt_supported=0\n'
                        'timer_source=host_elapsed\n'
                        'measurement_unit=seconds\n'
                        'measurement_per_iter=0.0021\n'
                        'output=0.330000\n'
                        'benchmark_complete=1\n'
                    ),
                    'stderr': '',
                    'timed_out': False,
                },
            },
            {
                'action': 'run',
                'exit_code': 0,
                'run': {
                    'elapsed_seconds': 0.23,
                    'stdout': (
                        'iterations=100\n'
                        'dwt_supported=0\n'
                        'timer_source=host_elapsed\n'
                        'measurement_unit=seconds\n'
                        'measurement_per_iter=0.0023\n'
                        'output=0.330000\n'
                        'validation_record_0=0.110000,0.220000,0.330000\n'
                        'validation_input_scaled_0=0.050000;0.100000;0.150000\n'
                        'validation_lstm_hidden_0=0.010000,0.020000;0.030000,0.040000;0.050000,0.060000\n'
                        'validation_transformer_ln_attn_0_0=0.100000,0.110000;0.120000,0.130000;0.140000,0.150000\n'
                        'validation_transformer_ln_ffn_0_0=0.160000,0.170000;0.180000,0.190000;0.200000,0.210000\n'
                        'validation_post_dense_0=0.220000,0.230000;0.240000,0.250000;0.260000,0.270000\n'
                        'validation_output_scaled_0=0.027500;0.055000;0.082500\n'
                        'validation_complete=1\n'
                    ),
                    'stderr': '',
                    'timed_out': False,
                },
            },
        ]

        config = {
            'task_info': {
                'task_type': 'qemu-c-inference',
            },
            'model_project_name': 'demo_lstm_transformer',
            'benchmark_config': {
                'iterations': 100,
                'reset_state_each_run': True,
                'repeat_runs': 1,
            },
            'validation_config': {
                'dataset': {
                    'dataset_type': 'MET',
                    'data_path': 'data/M50',
                    'sample_rate': 2000,
                    'time_clipped_s': 4.0,
                    'target_sweep': 2,
                },
                'selection': {
                    'magnitudes': [0.4],
                    'frequencies': [10.0],
                    'start_time_s': 0.0,
                    'end_time_s': 0.003,
                },
                'wave_output': {
                    'compress': True,
                },
            },
            'generation_config': {
                'project_dir': 'qemu_project',
                'overwrite': True,
            },
            'qemu_config': {
                'action': 'build-run',
                'timeout': 5,
            },
        }

        result = task_module.execute_lstm_qemu_inference_task(ep_path, config)

        assert result is True
        generated_dir = ep_path.full_path / 'qemu_project'
        main_c_content = (generated_dir / 'main.c').read_text(encoding='utf-8')
        model_header_content = (generated_dir / 'model_data.h').read_text(encoding='utf-8')

        assert 'transformer_forward_layer(' in main_c_content
        assert 'validation_transformer_ln_attn_' in main_c_content
        assert '#define TRANSFORMER_LAYER_COUNT 1u' in model_header_content
        assert '#define ATTENTION_POOL_SIZE 2u' in model_header_content

        summary_path = ep_path.output_path / 'benchmark_summary.json'
        with open(summary_path, 'r', encoding='utf-8') as file_obj:
            summary = json.load(file_obj)

        assert summary['model_type'] == 'lstm_transformer'
        assert summary['comparison']['mse'] == pytest.approx(0.0)
        assert 'tf_transformer_ln_attn_0_wave' in summary['wave_paths']
        assert 'c_transformer_ln_attn_0_wave' in summary['wave_paths']
        assert 'tf_post_dense_wave' in summary['wave_paths']
        assert 'c_post_dense_wave' in summary['wave_paths']


class TestAdditionalModelCodegen:
    def test_generate_qemu_project_for_onedcnn(self, tmp_path, monkeypatch):
        import core.lstm_qemu_ep_task as task_module

        actual_template_dir = task_module.QEMU_HELLO_TEMPLATE_DIR
        monkeypatch.setattr(task_module, 'REPO_ROOT', tmp_path)
        monkeypatch.setattr(task_module, 'QEMU_HELLO_TEMPLATE_DIR', actual_template_dir)

        project_dir = tmp_path / 'projects' / 'demo_onedcnn'
        data_dir = project_dir / 'data'
        data_dir.mkdir(parents=True)
        with open(data_dir / 'best_val.weights.json', 'w', encoding='utf-8') as file_obj:
            json.dump(_sample_onedcnn_weights(), file_obj)
        with open(project_dir / 'config.json', 'w', encoding='utf-8') as file_obj:
            json.dump({
                'use_model': '1DCNN',
                'activation': 'relu',
                'model_subcfg': {
                    'post_dense_activation': 'relu',
                },
            }, file_obj)

        model_type = task_module._detect_model_type('demo_onedcnn', project_dir, data_dir / 'best_val.weights.json')
        model_spec = task_module._load_model_spec(
            model_project_name='demo_onedcnn',
            model_dir=project_dir,
            weights_json_path=data_dir / 'best_val.weights.json',
            model_type=model_type,
            generation_config={},
        )
        assert model_type == 'onedcnn'

        output_dir = tmp_path / 'generated_onedcnn'
        task_module.generate_qemu_project(
            output_dir=output_dir,
            model_spec=model_spec,
            benchmark_config={
                'iterations': 10,
                'repeat_runs': 1,
                'reset_state_each_run': True,
            },
            validation_artifacts=task_module.ValidationArtifacts(
                dataset_type='MET',
                full_data_path='data/M50',
                sample_rate=2000.0,
                time_window={'start_time_s': 0.0, 'end_time_s': 0.003, 'sample_count': 3},
                input_data_range=2.0,
                output_data_range=4.0,
                loaded_weights_path=data_dir / 'best_val.weights.h5',
                records=[
                    task_module.ValidationRecord(
                        record_id='mag0.4_freq10',
                        magnitude=0.4,
                        frequency=10.0,
                        input_sequence=[[0.1], [0.2], [0.3]],
                        target_sequence=[0.5, 0.6, 0.7],
                        tf_output_sequence=[0.11, 0.22, 0.33],
                    ),
                ],
            ),
            overwrite=True,
        )

        main_c_content = (output_dir / 'main.c').read_text(encoding='utf-8')
        model_header_content = (output_dir / 'model_data.h').read_text(encoding='utf-8')

        assert 'ONEDCNN_BENCHMARK_VALIDATION' in main_c_content
        assert 'validation_conv_block_0_' in main_c_content
        assert 'conv_stack_initial_kernel' in model_header_content
        assert 'post_dense_1_kernel' in model_header_content

    def test_generate_qemu_project_for_tcn(self, tmp_path, monkeypatch):
        import core.lstm_qemu_ep_task as task_module

        actual_template_dir = task_module.QEMU_HELLO_TEMPLATE_DIR
        monkeypatch.setattr(task_module, 'REPO_ROOT', tmp_path)
        monkeypatch.setattr(task_module, 'QEMU_HELLO_TEMPLATE_DIR', actual_template_dir)

        project_dir = tmp_path / 'projects' / 'demo_tcn'
        data_dir = project_dir / 'data'
        data_dir.mkdir(parents=True)
        with open(data_dir / 'best_val.weights.json', 'w', encoding='utf-8') as file_obj:
            json.dump(_sample_tcn_weights(), file_obj)
        with open(project_dir / 'config.json', 'w', encoding='utf-8') as file_obj:
            json.dump({
                'use_model': 'TCN',
                'activation': 'relu',
                'model_subcfg': {
                    'dilations': [1],
                    'skip_initial_conv': False,
                    'use_residual': False,
                    'post_dense': True,
                    'post_dense_activation': 'relu',
                    'skip_output_conv': False,
                },
            }, file_obj)

        model_type = task_module._detect_model_type('demo_tcn', project_dir, data_dir / 'best_val.weights.json')
        model_spec = task_module._load_model_spec(
            model_project_name='demo_tcn',
            model_dir=project_dir,
            weights_json_path=data_dir / 'best_val.weights.json',
            model_type=model_type,
            generation_config={},
        )
        assert model_type == 'tcn'

        output_dir = tmp_path / 'generated_tcn'
        task_module.generate_qemu_project(
            output_dir=output_dir,
            model_spec=model_spec,
            benchmark_config={
                'iterations': 10,
                'repeat_runs': 1,
                'reset_state_each_run': True,
            },
            validation_artifacts=task_module.ValidationArtifacts(
                dataset_type='MET',
                full_data_path='data/M50',
                sample_rate=2000.0,
                time_window={'start_time_s': 0.0, 'end_time_s': 0.003, 'sample_count': 3},
                input_data_range=2.0,
                output_data_range=4.0,
                loaded_weights_path=data_dir / 'best_val.weights.h5',
                records=[
                    task_module.ValidationRecord(
                        record_id='mag0.4_freq10',
                        magnitude=0.4,
                        frequency=10.0,
                        input_sequence=[[0.1], [0.2], [0.3]],
                        target_sequence=[0.5, 0.6, 0.7],
                        tf_output_sequence=[0.11, 0.22, 0.33],
                    ),
                ],
            ),
            overwrite=True,
        )

        main_c_content = (output_dir / 'main.c').read_text(encoding='utf-8')
        model_header_content = (output_dir / 'model_data.h').read_text(encoding='utf-8')

        assert 'TCN_BENCHMARK_VALIDATION' in main_c_content
        assert 'validation_tcn_block_1_' in main_c_content
        assert 'debug_tcn_block_1_conv1' in main_c_content
        assert 'tcn_initial_projection_kernel' in model_header_content
        assert 'temporal_block_1_conv_1_kernel' in model_header_content
