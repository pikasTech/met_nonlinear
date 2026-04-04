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
        main_c_content = (generated_dir / 'main.c').read_text(encoding='utf-8')
        assert 'if (scaled < 0)' in main_c_content
        assert 'validation_input_scaled_' in main_c_content

        summary_path = ep_path.output_path / 'benchmark_summary.json'
        assert summary_path.exists()
        with open(summary_path, 'r', encoding='utf-8') as file_obj:
            summary = json.load(file_obj)

        assert summary['aggregated']['run_count'] == 2
        assert summary['aggregated']['avg_measurement_per_iter'] == pytest.approx(0.0035)
        assert summary['aggregated']['measurement_sources'] == ['host_elapsed']
        assert summary['aggregated']['avg_host_elapsed_seconds'] == pytest.approx(0.35)
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
        assert mock_execute_qemu_workflow.call_count == 3