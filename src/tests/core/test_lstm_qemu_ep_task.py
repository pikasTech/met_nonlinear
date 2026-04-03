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
        assert template['qemu_config']['action'] == 'build-run'


class TestExecuteLstmQemuInferenceTask:
    @patch('core.lstm_qemu_ep_task.execute_qemu_workflow')
    def test_execute_build_run_success(self, mock_execute_qemu_workflow, tmp_path, monkeypatch):
        from core.external_path_parser import ExternalPath
        import core.lstm_qemu_ep_task as task_module

        actual_template_dir = task_module.QEMU_HELLO_TEMPLATE_DIR
        monkeypatch.setattr(task_module, 'REPO_ROOT', tmp_path)
        monkeypatch.setattr(task_module, 'QEMU_HELLO_TEMPLATE_DIR', actual_template_dir)

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
                    'stdout': 'iterations=100\ndwt_supported=0\ntimer_source=systick\nmeasurement_unit=ticks\nmeasurement_per_iter=321\noutput=0.125000\n',
                    'stderr': '',
                    'timed_out': True,
                },
            },
            {
                'action': 'run',
                'exit_code': 0,
                'run': {
                    'elapsed_seconds': 0.36,
                    'stdout': 'iterations=100\ndwt_supported=0\ntimer_source=systick\nmeasurement_unit=ticks\nmeasurement_per_iter=323\noutput=0.126000\n',
                    'stderr': '',
                    'timed_out': True,
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
                'input_sequence': [0.1, 0.2],
                'reset_state_each_run': True,
                'repeat_runs': 2,
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

        summary_path = ep_path.output_path / 'benchmark_summary.json'
        assert summary_path.exists()
        with open(summary_path, 'r', encoding='utf-8') as file_obj:
            summary = json.load(file_obj)

        assert summary['aggregated']['run_count'] == 2
        assert summary['aggregated']['avg_measurement_per_iter'] == 322.0
        assert summary['aggregated']['measurement_sources'] == ['systick']
        assert summary['aggregated']['avg_host_elapsed_seconds'] == pytest.approx(0.35)
        assert mock_execute_qemu_workflow.call_count == 3