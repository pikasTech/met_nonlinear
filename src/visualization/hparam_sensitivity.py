import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class HparamSensitivityAnalyzer:
    """Summarize R15 one-axis hyperparameter sensitivity projects."""

    METRIC_FIELDS = {
        'freq_drift_hz': 'Freq Drift (Hz)',
        'sens_drift_percent': 'Sens Drift (%)',
        'linearity_percent': 'Linearity (%)',
        'compute_cost': 'Compute Cost',
        'val_loss': 'Val Loss',
        'val_afmae': 'Val AFMAE',
    }

    AXIS_ORDER = ['H_UNITS', 'INNER_KAN_UNITS', 'INNER_KAN_LAYERS', 'GRID_SIZE', 'SPLINE_ORDER']

    def __init__(self, config: Dict[str, Any], output_dir: Optional[Path] = None):
        self.config = config
        self.output_dir = Path(output_dir or config.get('output_dir', 'ex_projects/compare/hparam_sensitivity_r15/data'))
        self.results: Dict[str, Any] = {}
        self.project_root = Path(config.get('project_root', 'projects/09_HPARAM_SENSITIVITY'))
        self.project_table = Path(config.get('project_table', self.project_root / 'R15_projects.tsv'))
        self.baseline_name = config.get('baseline_project', 'FRIKANh8u6l6g8s2_e1k_lr7e4_base')

    def run_analysis(self) -> Dict[str, Any]:
        records = self._load_project_records()
        rows = [self._load_project_result(record) for record in records]
        baseline = next((row for row in rows if row['name'] == self.baseline_name), None)
        axis_summary = self._build_axis_summary(rows, baseline)
        strict_dominators = self._find_strict_dominators(rows, baseline)

        self.results = {
            'task': 'hparam_sensitivity_r15',
            'generated_at': datetime.now().isoformat(timespec='seconds'),
            'project_root': str(self.project_root),
            'baseline_project': self.baseline_name,
            'baseline': baseline,
            'rows': rows,
            'axis_summary': axis_summary,
            'strict_dominators': strict_dominators,
            'conclusions': self._build_conclusions(axis_summary, strict_dominators),
        }
        return self.results

    def save_results(self) -> None:
        if not self.results:
            self.run_analysis()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'summary.json').write_text(
            json.dumps(self.results, indent=2, ensure_ascii=False), encoding='utf-8'
        )
        self._write_csv(self.output_dir / 'summary.csv')
        (self.output_dir / 'summary.md').write_text(self._render_markdown(), encoding='utf-8')
        self._plot_sensitivity_curves()
        self._plot_compute_cost()

    def _load_project_records(self) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        with self.project_table.open('r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                value = row.get('Value') or ''
                records.append({
                    'name': row['Name'],
                    'axis': row.get('Axis') or 'base',
                    'param': row.get('Param') or '',
                    'value': int(value) if value.strip().isdigit() else None,
                })
        return records

    def _load_project_result(self, record: Dict[str, Any]) -> Dict[str, Any]:
        project_path = self.project_root / record['name']
        metrics_path = project_path / 'data' / 'metrics.json'
        training_log = project_path / 'data' / 'training_log.jsonl'
        data: Dict[str, Any] = {}
        if metrics_path.exists():
            data = json.loads(metrics_path.read_text(encoding='utf-8'))
        status = 'complete' if data.get('status') == 'complete' else 'missing_metrics'
        epochs = data.get('epochs')
        if epochs is None and training_log.exists():
            lines = training_log.read_text(encoding='utf-8', errors='ignore').splitlines()
            if lines:
                try:
                    epochs = json.loads(lines[-1]).get('epoch')
                except Exception:
                    epochs = None
        row = {
            **record,
            'path': str(project_path),
            'status': status,
            'epochs': epochs,
        }
        for key in self.METRIC_FIELDS:
            row[key] = data.get(key)
        return row

    def _build_axis_summary(self, rows: List[Dict[str, Any]], baseline: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        summary: Dict[str, Any] = {}
        for axis in self.AXIS_ORDER:
            axis_rows = sorted([row for row in rows if row['axis'] == axis], key=lambda r: (r['value'] is None, r['value']))
            completed = [row for row in axis_rows if row['status'] == 'complete']
            best_freq = min(completed, key=lambda r: r['freq_drift_hz']) if completed else None
            best_sens = min(completed, key=lambda r: r['sens_drift_percent']) if completed else None
            best_linearity = min(completed, key=lambda r: r['linearity_percent']) if completed else None
            summary[axis] = {
                'planned_count': len(axis_rows),
                'complete_count': len(completed),
                'missing_count': len(axis_rows) - len(completed),
                'complete_values': [row['value'] for row in completed],
                'missing_values': [row['value'] for row in axis_rows if row['status'] != 'complete'],
                'best_freq_project': self._short_best(best_freq, 'freq_drift_hz'),
                'best_sens_project': self._short_best(best_sens, 'sens_drift_percent'),
                'best_linearity_project': self._short_best(best_linearity, 'linearity_percent'),
                'compute_cost_values': sorted({row['compute_cost'] for row in completed if row.get('compute_cost') is not None}),
                'baseline_value': baseline.get(self._axis_to_metric(axis)) if baseline else None,
            }
        return summary

    def _short_best(self, row: Optional[Dict[str, Any]], metric: str) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        return {'name': row['name'], 'value': row['value'], metric: row.get(metric)}

    def _axis_to_metric(self, axis: str) -> Optional[int]:
        return {
            'H_UNITS': 8,
            'INNER_KAN_UNITS': 6,
            'INNER_KAN_LAYERS': 6,
            'GRID_SIZE': 8,
            'SPLINE_ORDER': 2,
        }.get(axis)

    def _find_strict_dominators(self, rows: List[Dict[str, Any]], baseline: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not baseline:
            return []
        metrics = ['freq_drift_hz', 'sens_drift_percent', 'linearity_percent']
        dominators = []
        for row in rows:
            if row['status'] != 'complete' or row['axis'] == 'base':
                continue
            if all(row.get(m) is not None and baseline.get(m) is not None and row[m] <= baseline[m] for m in metrics):
                if any(row[m] < baseline[m] for m in metrics):
                    dominators.append({k: row[k] for k in ['name', 'axis', 'value', *metrics]})
        return dominators

    def _build_conclusions(self, axis_summary: Dict[str, Any], strict_dominators: List[Dict[str, Any]]) -> List[str]:
        complete_axes = [axis for axis, item in axis_summary.items() if item['missing_count'] == 0]
        truncated_axes = [axis for axis, item in axis_summary.items() if item['missing_count'] > 0]
        conclusions = [
            f"Complete axes: {', '.join(complete_axes) if complete_axes else 'none'}.",
            f"Incomplete axes: {', '.join(truncated_axes) if truncated_axes else 'none'}.",
            "No completed point strictly dominates the baseline on Freq Drift, Sens Drift, and Linearity."
            if not strict_dominators else f"Strict dominators found: {len(strict_dominators)}.",
            "GRID_SIZE and SPLINE_ORDER keep the same current LUT compute-cost estimate when H/U/L are unchanged.",
        ]
        return conclusions

    def _write_csv(self, path: Path) -> None:
        fieldnames = ['axis', 'param', 'value', 'name', 'status', 'epochs', *self.METRIC_FIELDS.keys(), 'path']
        with path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in self.results['rows']:
                writer.writerow({key: row.get(key) for key in fieldnames})

    def _render_markdown(self) -> str:
        lines = ['# R15 Hyperparameter Sensitivity Summary', '']
        baseline = self.results.get('baseline') or {}
        lines += [
            f"Generated at: `{self.results['generated_at']}`",
            f"Baseline: `{self.baseline_name}`",
            '',
            '## Conclusions',
            '',
        ]
        lines += [f"- {item}" for item in self.results['conclusions']]
        lines += ['', '## Baseline', '']
        lines += [self._row_table([baseline]) if baseline else 'Baseline metrics missing.', '', '## Axis Summary', '']
        lines += ['| Axis | Complete | Missing | Best Freq | Best Sens | Best Linearity | Compute Cost Values |', '| --- | ---: | ---: | --- | --- | --- | --- |']
        for axis, item in self.results['axis_summary'].items():
            lines.append(
                f"| `{axis}` | {item['complete_count']}/{item['planned_count']} | "
                f"{item['missing_values']} | {self._best_text(item['best_freq_project'], 'freq_drift_hz')} | "
                f"{self._best_text(item['best_sens_project'], 'sens_drift_percent')} | "
                f"{self._best_text(item['best_linearity_project'], 'linearity_percent')} | "
                f"{item['compute_cost_values']} |"
            )
        lines += ['', '## All Points', '', self._row_table(self.results['rows'])]
        lines += ['', '## Figures', '', '- `sensitivity_curves.png`', '- `compute_cost.png`', '']
        return '\n'.join(lines)

    def _best_text(self, item: Optional[Dict[str, Any]], metric: str) -> str:
        if not item:
            return '-'
        return f"`{item['name']}` ({item[metric]:.4g})"

    def _row_table(self, rows: List[Dict[str, Any]]) -> str:
        headers = ['Axis', 'Value', 'Project', 'Status', 'Freq Drift', 'Sens Drift', 'Linearity', 'Compute Cost']
        lines = ['| ' + ' | '.join(headers) + ' |', '| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |']
        for row in rows:
            if not row:
                continue
            vals = [
                row.get('axis'), row.get('value'), f"`{row.get('name')}`", row.get('status'),
                self._fmt(row.get('freq_drift_hz')), self._fmt(row.get('sens_drift_percent')),
                self._fmt(row.get('linearity_percent')), self._fmt(row.get('compute_cost')),
            ]
            lines.append('| ' + ' | '.join('' if v is None else str(v) for v in vals) + ' |')
        return '\n'.join(lines)

    def _fmt(self, value: Any) -> str:
        return '-' if value is None else f"{float(value):.4f}"

    def _plot_sensitivity_curves(self) -> None:
        metrics = [('freq_drift_hz', 'Freq Drift (Hz)'), ('sens_drift_percent', 'Sens Drift (%)'), ('linearity_percent', 'Linearity (%)')]
        fig, axes = plt.subplots(len(metrics), len(self.AXIS_ORDER), figsize=(22, 10), sharex=False)
        baseline = self.results.get('baseline') or {}
        for r, (metric, label) in enumerate(metrics):
            for c, axis in enumerate(self.AXIS_ORDER):
                ax = axes[r][c]
                rows = sorted([row for row in self.results['rows'] if row['axis'] == axis], key=lambda x: x['value'])
                xs = [row['value'] for row in rows if row['status'] == 'complete']
                ys = [row[metric] for row in rows if row['status'] == 'complete']
                ax.plot(xs, ys, marker='o', color='#1f77b4', linewidth=1.8)
                missing_x = [row['value'] for row in rows if row['status'] != 'complete']
                if missing_x:
                    ybase = baseline.get(metric) or (sum(ys) / len(ys) if ys else 0)
                    ax.scatter(missing_x, [ybase] * len(missing_x), marker='x', s=70, color='#d62728', label='missing')
                if baseline.get(metric) is not None:
                    ax.axhline(float(baseline[metric]), color='#444444', linestyle='--', linewidth=1.0)
                if r == 0:
                    ax.set_title(axis)
                if c == 0:
                    ax.set_ylabel(label)
                ax.grid(True, alpha=0.25)
        fig.suptitle('R15 FRIKAN Hyperparameter Sensitivity', fontsize=16)
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(self.output_dir / 'sensitivity_curves.png', dpi=300)
        plt.close(fig)

    def _plot_compute_cost(self) -> None:
        fig, axes = plt.subplots(1, len(self.AXIS_ORDER), figsize=(22, 4), sharey=False)
        baseline = self.results.get('baseline') or {}
        for ax, axis in zip(axes, self.AXIS_ORDER):
            rows = sorted([row for row in self.results['rows'] if row['axis'] == axis], key=lambda x: x['value'])
            xs = [row['value'] for row in rows if row['status'] == 'complete']
            ys = [row['compute_cost'] for row in rows if row['status'] == 'complete']
            ax.plot(xs, ys, marker='o', color='#2ca02c', linewidth=1.8)
            if baseline.get('compute_cost') is not None:
                ax.axhline(float(baseline['compute_cost']), color='#444444', linestyle='--', linewidth=1.0)
            ax.set_title(axis)
            ax.set_xlabel('value')
            ax.grid(True, alpha=0.25)
        axes[0].set_ylabel('Compute Cost')
        fig.suptitle('R15 Compute Cost by Hyperparameter Axis', fontsize=16)
        fig.tight_layout(rect=[0, 0, 1, 0.92])
        fig.savefig(self.output_dir / 'compute_cost.png', dpi=300)
        plt.close(fig)
