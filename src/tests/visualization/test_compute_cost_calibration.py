import json

from visualization.compute_cost_calibration import ComputeCostCalibrationAnalyzer


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file_obj:
        json.dump(data, file_obj, indent=2, ensure_ascii=False)


def test_compute_cost_calibration_recovers_expected_weights(tmp_path):
    true_mul_weight = 4.0
    true_map_weight = 25.0
    true_scale = 0.001
    pair_specs = [
        ('model_a', 10, 20, 4),
        ('model_b', 30, 10, 8),
        ('model_c', 12, 40, 2),
    ]

    pairs = []
    for name, additions, multiplications, maps in pair_specs:
        project_dir = tmp_path / name
        board_dir = tmp_path / 'ep' / name
        measured_speed = true_scale * (
            additions + multiplications * true_mul_weight + maps * true_map_weight
        )
        _write_json(
            project_dir / 'data' / 'compute_analysis.json',
            {
                'totals': {
                    'additions': additions,
                    'multiplications': multiplications,
                    'maps': maps,
                }
            },
        )
        _write_json(
            project_dir / 'data' / 'metrics.json',
            {
                'board_keil_speed': measured_speed,
            },
        )
        _write_json(
            board_dir / 'data' / 'keil_benchmark_summary.json',
            {
                'comparison': {'mae': 0.0},
            },
        )
        pairs.append(
            {
                'label': name,
                'project_path': str(project_dir),
                'on_board_inference_ep_path': str(board_dir),
            }
        )

    analyzer = ComputeCostCalibrationAnalyzer(
        {
            'task_info': {
                'task_type': 'compare',
                'analysis_type': 'compute-cost-calibration',
            },
            'pairs': pairs,
            'search': {
                'mul_weight': {'mode': 'linspace', 'start': 1.0, 'stop': 6.0, 'steps': 11},
                'map_weight': {'mode': 'linspace', 'start': 20.0, 'stop': 30.0, 'steps': 21},
                'regularization_lambda': 0.0,
                'adopt_round_to': 0.5,
                'default_mul_weight': 1.0,
                'default_map_weight': 6.0,
            },
        },
        output_dir=tmp_path / 'out',
    )

    results = analyzer.run_analysis()

    assert results['adopted_fit']['mul_weight'] == 4.0
    assert results['adopted_fit']['map_weight'] == 25.0
    assert results['adopted_fit']['scale_ms_per_unit'] == true_scale
    assert results['adopted_fit']['rmse_ms'] == 0.0
