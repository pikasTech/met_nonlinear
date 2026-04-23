import json
import logging
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CalibrationPair:
    label: str
    project_path: Path
    board_ep_path: Path
    additions: float
    multiplications: float
    maps: float
    measured_speed_ms_per_point: float


def _load_json(path: Path) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as file_obj:
        return json.load(file_obj)


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _nearest_step(value: float, step: float) -> float:
    if step <= 0:
        return value
    return round(value / step) * step


def _resolve_path(path_str: str) -> Path:
    path = Path(path_str.replace('\\', '/'))
    if path.is_absolute():
        return path
    return Path.cwd() / path


def _extract_board_speed_ms_per_point(
    metrics_payload: Dict[str, Any],
    keil_payload: Dict[str, Any],
) -> Optional[float]:
    metrics_speed = _to_float(metrics_payload.get('board_keil_speed'))
    if metrics_speed is not None:
        return metrics_speed

    parsed_output = keil_payload.get('parsed_output') or {}
    wall_time_per_iter_ms = _to_float(parsed_output.get('wall_time_per_iter_ms'))
    if wall_time_per_iter_ms is None:
        return None

    validation = keil_payload.get('validation') or {}
    record_count = _to_int(validation.get('record_count'))
    seq_len = _to_int(validation.get('seq_len'))
    if record_count is None or seq_len is None:
        record_count = _to_int(parsed_output.get('record_count'))
        seq_len = _to_int(parsed_output.get('seq_len'))
    if record_count is None or seq_len is None or record_count <= 0 or seq_len <= 0:
        return None
    return wall_time_per_iter_ms / float(record_count * seq_len)


def _build_grid(spec: Dict[str, Any]) -> np.ndarray:
    grid_type = str(spec.get('mode', 'logspace'))
    start = float(spec['start'])
    stop = float(spec['stop'])
    steps = int(spec['steps'])
    if steps < 2:
        raise ValueError(f'grid steps must be >= 2, got {steps}')
    if grid_type == 'linspace':
        return np.linspace(start, stop, steps)
    if start <= 0.0 or stop <= 0.0:
        raise ValueError(f'logspace grid requires positive bounds, got start={start}, stop={stop}')
    return np.geomspace(start, stop, steps)


class ComputeCostCalibrationAnalyzer:
    def __init__(self, config: Dict[str, Any], output_dir: Optional[Path] = None):
        self.config = config
        self.output_dir = output_dir or Path('ex_projects/compare/compute_cost_calibration/results')
        self.results: Dict[str, Any] = {}
        self.pairs: List[CalibrationPair] = []

    def load_pairs(self) -> None:
        loaded_pairs: List[CalibrationPair] = []
        for pair_cfg in self.config.get('pairs', []):
            label = str(pair_cfg['label'])
            project_path = _resolve_path(str(pair_cfg['project_path']))
            board_ep_path = _resolve_path(str(pair_cfg['on_board_inference_ep_path']))

            compute_payload = _load_json(project_path / 'data' / 'compute_analysis.json')
            metrics_payload = _load_json(project_path / 'data' / 'metrics.json')
            keil_payload = _load_json(board_ep_path / 'data' / 'keil_benchmark_summary.json')

            totals = compute_payload.get('totals') or {}
            additions = _to_float(totals.get('additions'))
            multiplications = _to_float(totals.get('multiplications'))
            maps = _to_float(totals.get('maps'))
            measured_speed = _extract_board_speed_ms_per_point(metrics_payload, keil_payload)

            if additions is None or multiplications is None or maps is None:
                raise ValueError(f'compute totals missing for pair {label}')
            if measured_speed is None:
                raise ValueError(f'board speed missing for pair {label}')

            loaded_pairs.append(CalibrationPair(
                label=label,
                project_path=project_path,
                board_ep_path=board_ep_path,
                additions=additions,
                multiplications=multiplications,
                maps=maps,
                measured_speed_ms_per_point=measured_speed,
            ))
        self.pairs = loaded_pairs

    def _fit_model(self, mul_weight: float, map_weight: float) -> Dict[str, Any]:
        xs = np.asarray([
            pair.additions + pair.multiplications * mul_weight + pair.maps * map_weight
            for pair in self.pairs
        ], dtype=np.float64)
        ys = np.asarray([pair.measured_speed_ms_per_point for pair in self.pairs], dtype=np.float64)
        denominator = float(np.dot(xs, xs))
        scale = float(np.dot(xs, ys) / denominator) if denominator > 0.0 else 0.0
        predicted = scale * xs
        residual = predicted - ys
        relative_error = residual / ys
        log_rmse = float(np.sqrt(np.mean((np.log(predicted) - np.log(ys)) ** 2)))
        rmse_ms = float(np.sqrt(np.mean(residual ** 2)))
        mae_ms = float(np.mean(np.abs(residual)))
        mape_percent = float(np.mean(np.abs(relative_error)) * 100.0)
        max_relative_error_percent = float(np.max(np.abs(relative_error)) * 100.0)
        return {
            'add_weight': 1.0,
            'mul_weight': float(mul_weight),
            'map_weight': float(map_weight),
            'scale_ms_per_unit': scale,
            'predicted_speed_ms_per_point': predicted.tolist(),
            'rmse_ms': rmse_ms,
            'mae_ms': mae_ms,
            'mape_percent': mape_percent,
            'max_relative_error_percent': max_relative_error_percent,
            'log_rmse': log_rmse,
        }

    def _search_best(self, regularization_lambda: float) -> Dict[str, Any]:
        search_cfg = self.config.get('search', {})
        mul_grid = _build_grid(search_cfg['mul_weight'])
        map_grid = _build_grid(search_cfg['map_weight'])
        score_grid = np.zeros((len(mul_grid), len(map_grid)), dtype=np.float64)

        best_result: Optional[Dict[str, Any]] = None
        best_score: Optional[float] = None
        for mul_index, mul_weight in enumerate(mul_grid):
            for map_index, map_weight in enumerate(map_grid):
                fit = self._fit_model(float(mul_weight), float(map_weight))
                penalty = regularization_lambda * (
                    math.log1p(float(mul_weight)) + math.log1p(float(map_weight))
                )
                score = fit['log_rmse'] + penalty
                score_grid[mul_index, map_index] = score
                if best_score is None or score < best_score:
                    best_score = score
                    best_result = {
                        **fit,
                        'objective_score': score,
                        'regularization_lambda': regularization_lambda,
                    }

        if best_result is None or best_score is None:
            raise RuntimeError('search failed to produce a result')
        return {
            'best': best_result,
            'mul_grid': mul_grid.tolist(),
            'map_grid': map_grid.tolist(),
            'score_grid': score_grid.tolist(),
        }

    def run_analysis(self) -> Dict[str, Any]:
        self.load_pairs()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        search_cfg = self.config.get('search', {})
        regularization_lambda = float(search_cfg.get('regularization_lambda', 0.02))
        round_to = float(search_cfg.get('adopt_round_to', 1.0))

        default_fit = self._fit_model(
            mul_weight=float(search_cfg.get('default_mul_weight', 1.0)),
            map_weight=float(search_cfg.get('default_map_weight', 6.0)),
        )
        pure_search = self._search_best(regularization_lambda=0.0)
        regularized_search = self._search_best(regularization_lambda=regularization_lambda)
        regularized_best = regularized_search['best']
        adopted_mul = _nearest_step(float(regularized_best['mul_weight']), round_to)
        adopted_map = _nearest_step(float(regularized_best['map_weight']), round_to)
        adopted_fit = self._fit_model(adopted_mul, adopted_map)
        adopted_fit.update({
            'regularization_lambda': regularization_lambda,
            'rounded_from_mul_weight': float(regularized_best['mul_weight']),
            'rounded_from_map_weight': float(regularized_best['map_weight']),
            'round_to': round_to,
        })

        pair_rows = []
        for pair, default_pred, adopted_pred in zip(
            self.pairs,
            default_fit['predicted_speed_ms_per_point'],
            adopted_fit['predicted_speed_ms_per_point'],
        ):
            pair_rows.append({
                'label': pair.label,
                'project_path': str(pair.project_path).replace('\\', '/'),
                'on_board_inference_ep_path': str(pair.board_ep_path).replace('\\', '/'),
                'additions': pair.additions,
                'multiplications': pair.multiplications,
                'maps': pair.maps,
                'measured_speed_ms_per_point': pair.measured_speed_ms_per_point,
                'default_predicted_speed_ms_per_point': default_pred,
                'adopted_predicted_speed_ms_per_point': adopted_pred,
                'default_relative_error_percent': (
                    (default_pred - pair.measured_speed_ms_per_point) / pair.measured_speed_ms_per_point * 100.0
                ),
                'adopted_relative_error_percent': (
                    (adopted_pred - pair.measured_speed_ms_per_point) / pair.measured_speed_ms_per_point * 100.0
                ),
            })

        self.results = {
            'timestamp': timestamp,
            'task_info': self.config.get('task_info', {}),
            'pairs': pair_rows,
            'default_fit': default_fit,
            'pure_fit': pure_search['best'],
            'regularized_fit': regularized_best,
            'adopted_fit': adopted_fit,
            'recommended_cost_model': {
                'platform': 'stm32f405',
                'unit': 'add_equivalent',
                'add_weight': 1.0,
                'mul_weight': adopted_fit['mul_weight'],
                'map_weight': adopted_fit['map_weight'],
                'basis': (
                    'Calibrated against measured STM32F405 board latency using a '
                    'least-squares scale factor and a lightly regularized search '
                    'over add-normalized mul/map ratios.'
                ),
            },
            'search': {
                'regularization_lambda': regularization_lambda,
                'adopt_round_to': round_to,
                'mul_weight': search_cfg['mul_weight'],
                'map_weight': search_cfg['map_weight'],
                'pure_score_grid': pure_search['score_grid'],
                'regularized_score_grid': regularized_search['score_grid'],
                'mul_grid': pure_search['mul_grid'],
                'map_grid': pure_search['map_grid'],
            },
        }
        return self.results

    def _make_heatmap(self) -> str:
        search = self.results['search']
        mul_grid = np.asarray(search['mul_grid'], dtype=np.float64)
        map_grid = np.asarray(search['map_grid'], dtype=np.float64)
        regularized_grid = np.asarray(search['regularized_score_grid'], dtype=np.float64)

        fig, ax = plt.subplots(figsize=(8.2, 6.4), constrained_layout=True)
        im = ax.imshow(
            regularized_grid.T,
            origin='lower',
            aspect='auto',
            extent=[math.log10(mul_grid[0]), math.log10(mul_grid[-1]), math.log10(map_grid[0]), math.log10(map_grid[-1])],
            cmap='viridis',
        )
        plt.colorbar(im, ax=ax, label='Objective score')

        pure_fit = self.results['pure_fit']
        regularized_fit = self.results['regularized_fit']
        adopted_fit = self.results['adopted_fit']
        ax.scatter(math.log10(pure_fit['mul_weight']), math.log10(pure_fit['map_weight']), c='white', s=70, marker='x', label='Pure fit')
        ax.scatter(math.log10(regularized_fit['mul_weight']), math.log10(regularized_fit['map_weight']), c='#ffcc00', s=70, marker='o', label='Regularized fit')
        ax.scatter(math.log10(adopted_fit['mul_weight']), math.log10(adopted_fit['map_weight']), c='#ff5a36', s=80, marker='D', label='Adopted')
        ax.set_xlabel('log10(Mul weight)')
        ax.set_ylabel('log10(Map weight)')
        ax.set_title('Compute-cost calibration search heatmap')
        ax.legend(frameon=True, loc='upper left')

        output_path = self.output_dir / 'compute_cost_calibration_heatmap.png'
        fig.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close(fig)
        return output_path.name

    def _make_prediction_scatter(self) -> str:
        labels = [pair.label for pair in self.pairs]
        measured = np.asarray([pair.measured_speed_ms_per_point for pair in self.pairs], dtype=np.float64)
        default_pred = np.asarray(self.results['default_fit']['predicted_speed_ms_per_point'], dtype=np.float64)
        adopted_pred = np.asarray(self.results['adopted_fit']['predicted_speed_ms_per_point'], dtype=np.float64)

        fig, ax = plt.subplots(figsize=(7.4, 6.2), constrained_layout=True)
        min_value = float(min(measured.min(), default_pred.min(), adopted_pred.min()) * 0.95)
        max_value = float(max(measured.max(), default_pred.max(), adopted_pred.max()) * 1.05)
        ax.plot([min_value, max_value], [min_value, max_value], linestyle='--', color='#666666', linewidth=1.0, label='Ideal')
        ax.scatter(measured, default_pred, color='#1f4e79', s=60, label='Default (1:1:6)')
        ax.scatter(measured, adopted_pred, color='#c96b00', s=60, label='Adopted')
        for label, x_value, y_value in zip(labels, measured, adopted_pred):
            ax.annotate(label, (x_value, y_value), textcoords='offset points', xytext=(4, 4), fontsize=8)
        ax.set_xlabel('Measured board latency (ms/point)')
        ax.set_ylabel('Predicted latency (ms/point)')
        ax.set_title('Predicted vs. measured board latency')
        ax.legend(frameon=True)

        output_path = self.output_dir / 'compute_cost_calibration_scatter.png'
        fig.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close(fig)
        return output_path.name

    def _make_error_bar_chart(self) -> str:
        labels = [pair.label for pair in self.pairs]
        default_errors = [row['default_relative_error_percent'] for row in self.results['pairs']]
        adopted_errors = [row['adopted_relative_error_percent'] for row in self.results['pairs']]
        x = np.arange(len(labels))
        width = 0.36

        fig, ax = plt.subplots(figsize=(9.0, 5.2), constrained_layout=True)
        ax.bar(x - width / 2, default_errors, width=width, color='#1f4e79', label='Default (1:1:6)')
        ax.bar(x + width / 2, adopted_errors, width=width, color='#c96b00', label='Adopted')
        ax.axhline(0.0, color='#333333', linewidth=1.0)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha='right')
        ax.set_ylabel('Relative error (%)')
        ax.set_title('Per-model latency prediction error')
        ax.legend(frameon=True)

        output_path = self.output_dir / 'compute_cost_calibration_error.png'
        fig.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close(fig)
        return output_path.name

    def generate_markdown_report(self) -> str:
        if not self.results:
            self.run_analysis()

        default_fit = self.results['default_fit']
        pure_fit = self.results['pure_fit']
        regularized_fit = self.results['regularized_fit']
        adopted_fit = self.results['adopted_fit']

        lines = [
            '# Compute Cost Calibration Report',
            '',
            f"Generated at: {self.results['timestamp']}",
            '',
            '## Recommended cost model',
            '',
            f"- Add : Mul : Map = `1 : {adopted_fit['mul_weight']:.1f} : {adopted_fit['map_weight']:.1f}`",
            f"- Scale factor `A` = `{adopted_fit['scale_ms_per_unit']:.8f}` ms / add-equivalent",
            f"- Default log-RMSE = `{default_fit['log_rmse']:.4f}`, adopted log-RMSE = `{adopted_fit['log_rmse']:.4f}`",
            f"- Default max relative error = `{default_fit['max_relative_error_percent']:.2f}%`, adopted max relative error = `{adopted_fit['max_relative_error_percent']:.2f}%`",
            '',
            '## Search summary',
            '',
            f"- Pure fit best: `1 : {pure_fit['mul_weight']:.4f} : {pure_fit['map_weight']:.4f}`",
            f"- Regularized fit best: `1 : {regularized_fit['mul_weight']:.4f} : {regularized_fit['map_weight']:.4f}`",
            f"- Adopted rounded model: `1 : {adopted_fit['mul_weight']:.1f} : {adopted_fit['map_weight']:.1f}`",
            '',
            '## Pair-wise fit',
            '',
            '| Model | Add | Mul | Map | Measured (ms/point) | Default pred | Adopted pred | Default err (%) | Adopted err (%) |',
            '| --- | --- | --- | --- | --- | --- | --- | --- | --- |',
        ]
        for row in self.results['pairs']:
            lines.append(
                f"| {row['label']} | {row['additions']:.0f} | {row['multiplications']:.0f} | "
                f"{row['maps']:.0f} | {row['measured_speed_ms_per_point']:.6f} | "
                f"{row['default_predicted_speed_ms_per_point']:.6f} | "
                f"{row['adopted_predicted_speed_ms_per_point']:.6f} | "
                f"{row['default_relative_error_percent']:.2f} | "
                f"{row['adopted_relative_error_percent']:.2f} |"
            )
        return '\n'.join(lines)

    def save_results(self) -> None:
        if not self.results:
            self.run_analysis()

        self.output_dir.mkdir(parents=True, exist_ok=True)
        figures = {
            'search_heatmap': self._make_heatmap(),
            'prediction_scatter': self._make_prediction_scatter(),
            'error_bar_chart': self._make_error_bar_chart(),
        }
        self.results['figures'] = figures

        json_path = self.output_dir / 'compute_cost_calibration_results.json'
        with open(json_path, 'w', encoding='utf-8') as file_obj:
            json.dump(self.results, file_obj, indent=2, ensure_ascii=False)

        markdown_path = self.output_dir / 'compute_cost_calibration_report.md'
        markdown_path.write_text(self.generate_markdown_report(), encoding='utf-8')

        logger.info('compute cost calibration results saved to: %s', json_path)


def run_compute_cost_calibration(config: Dict[str, Any], output_dir: Optional[Path] = None) -> Dict[str, Any]:
    analyzer = ComputeCostCalibrationAnalyzer(config, output_dir=output_dir)
    results = analyzer.run_analysis()
    analyzer.save_results()
    return results
