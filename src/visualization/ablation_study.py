import json
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from visualization.image_data_process import calculate_drift

logger = logging.getLogger(__name__)


class SimpleProjectResult:
    """简化的项目数据加载器，替代 ProjectResult 避免 broken imports"""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.raw_data_path = Path(project_path) / 'data' / 'linear_response.json'
        self.compute_analysis_path = Path(project_path) / 'data' / 'compute_analysis.json'
        self.training_info_path = Path(project_path) / 'data' / 'training_info.json'
        self.raw_data = {}
        self.processed_data = {}
        self.compute_data = {}
        self.training_info = {}

    def load_compute_analysis(self) -> bool:
        """Load compute analysis from JSON file."""
        try:
            with open(self.compute_analysis_path, 'r') as f:
                self.compute_data = json.load(f)
            return True
        except FileNotFoundError:
            logger.warning(f"compute_analysis.json not found: {self.compute_analysis_path}")
            return False
        except Exception as e:
            logger.error(f"Error loading compute analysis: {e}")
            return False

    def load_training_info(self) -> bool:
        """Load training info from JSON file."""
        try:
            with open(self.training_info_path, 'r') as f:
                self.training_info = json.load(f)
            return True
        except FileNotFoundError:
            logger.warning(f"training_info.json not found: {self.training_info_path}")
            return False
        except Exception as e:
            logger.error(f"Error loading training info: {e}")
            return False

    def load_data(self):
        """Load raw data from the JSON file."""
        try:
            with open(self.raw_data_path, 'r') as json_file:
                self.raw_data = json.load(json_file)
        except Exception as e:
            logger.error(f'Error loading raw data: {e}')
            raise

    def process_data(self, freq_sen=100):
        """Process raw data and store it in processed_data."""
        import math

        self.processed_data['gains_origin'] = [
            np.array(g) for g in self.raw_data['gains_origin']]
        self.processed_data['gains_comped'] = [
            np.array(g) for g in self.raw_data['gains_comped']]
        self.processed_data['magnitudes'] = self.raw_data['magnitudes']
        self.processed_data['frequencies'] = self.raw_data['frequencies']

        freq = np.array(self.processed_data['frequencies'])
        gains_origin = np.array(self.processed_data['gains_origin'])
        gains_comped = np.array(self.processed_data['gains_comped'])
        sensitive_origin = []
        sensitive_comped = []
        for i in range(len(gains_origin)):
            gain_origin = gains_origin[i]
            gain_comped = gains_comped[i]
            gain_origin_interp = np.interp(freq_sen, freq, gain_origin)
            gain_comped_interp = np.interp(freq_sen, freq, gain_comped)
            sensitive_origin.append(gain_origin_interp)
            sensitive_comped.append(gain_comped_interp)

        self.processed_data['sensitive_origin'] = sensitive_origin
        self.processed_data['sensitive_comped'] = sensitive_comped

        paramss_origin = self.raw_data.get('fit_params_origin', [])
        paramss_comped = self.raw_data.get('fit_params_comped', [])

        wn_origin, zeta_origin, A_origin = self._calculate_parameters(paramss_origin)
        wn_comped, zeta_comped, A_comped = self._calculate_parameters(paramss_comped)

        self.processed_data['fn_origin'] = np.array(wn_origin) / (2 * np.pi)
        self.processed_data['fn_comped'] = np.array(wn_comped) / (2 * np.pi)
        self.processed_data['Sn_origin'] = np.array(
            A_origin) / (4 * np.pi * np.array(zeta_origin) * self.processed_data['fn_origin'])
        self.processed_data['Sn_comped'] = np.array(
            A_comped) / (4 * np.pi * np.array(zeta_comped) * self.processed_data['fn_comped'])
        self.processed_data['zeta_origin'] = zeta_origin
        self.processed_data['zeta_comped'] = zeta_comped

    def _calculate_parameters(self, paramss):
        """Helper method to calculate wn, zeta, and A from fit parameters."""
        wn = []
        zeta = []
        A = []
        for A_val, B_val, C_val in paramss:
            wn_val = np.sqrt(B_val)
            zeta_val = C_val / (2 * wn_val)
            wn.append(wn_val)
            zeta.append(zeta_val)
            A.append(A_val)
        return wn, zeta, A


class AblationStudyAnalyzer:
    """消融实验分析器 - 复用现有基础设施，不复制代码"""

    def __init__(self, config: dict, output_dir: Optional[Path] = None):
        self.config = config
        self.output_dir = output_dir or Path("ex_projects/compare/mae_vs_afmae/results")
        self.projects: Dict[str, SimpleProjectResult] = {}
        self.results: Dict[str, Any] = {}

    def load_all_projects(self) -> None:
        """使用 SimpleProjectResult 加载所有项目"""
        for proj in self.config.get('projects', []):
            proj_name = proj['name']
            proj_path = proj['path']
            try:
                result = SimpleProjectResult(proj_path)
                result.load_data()
                result.process_data()
                result.load_compute_analysis()
                result.load_training_info()
                self.projects[proj_name] = result
                logger.info(f"已加载项目: {proj_name} ({proj_path})")
            except Exception as e:
                logger.error(f"加载项目失败 {proj_name}: {e}")

    def calculate_natural_frequency_drift(self, project_name: str, use_origin: bool = False) -> dict:
        """计算固有频率漂移 - 复用 ProjectResult + calculate_drift()"""
        if project_name not in self.projects:
            raise ValueError(f"项目未加载: {project_name}")

        key = 'fn_origin' if use_origin else 'fn_comped'
        fn = self.projects[project_name].processed_data[key]
        metric = {
            'min': float(np.min(fn)),
            'max': float(np.max(fn)),
            'median': float(np.median(fn))
        }
        metric['drift'] = calculate_drift(metric)
        return metric

    def calculate_sensitivity_drift(self, project_name: str, freq_hz: float = 100, use_origin: bool = False) -> dict:
        """计算灵敏度漂移 - 复用 ProjectResult.process_data(freq_sen) + calculate_drift()"""
        if project_name not in self.projects:
            raise ValueError(f"项目未加载: {project_name}")

        result = self.projects[project_name]
        result.process_data(freq_sen=freq_hz)
        key = 'sensitive_origin' if use_origin else 'sensitive_comped'
        sens = result.processed_data[key]
        metric = {
            'min': float(np.min(sens)),
            'max': float(np.max(sens)),
            'median': float(np.median(sens))
        }
        metric['drift'] = calculate_drift(metric)
        return metric

    def calculate_linearity(self, project_name: str, use_origin: bool = False) -> dict:
        """计算平均线性度 (1 - R²) - 直接读取 JSON"""
        if project_name not in self.projects:
            raise ValueError(f"项目未加载: {project_name}")

        proj = self.projects[project_name]
        path = Path(proj.project_path) / 'data' / 'linearity_by_frequency.json'
        if not path.exists():
            return {'error': 'linearity_by_frequency.json not available', 'hint': 'run python cli.py -e PROJECT_NAME to generate'}

        with open(path) as f:
            data = json.load(f)

        r2_key = 'r_squared_origin' if use_origin else 'r_squared_comped'
        r2_values = [item[r2_key] for item in data['linearity_by_frequency']]
        nonlinearity = [1 - r2 for r2 in r2_values]
        return {
            'mean': float(np.mean(nonlinearity)) * 100,
            'max': float(np.max(nonlinearity)) * 100,
            'min': float(np.min(nonlinearity)) * 100
        }

    def calculate_compute_cost(self, project_name: str) -> dict:
        """计算计算量估计指标"""
        if project_name not in self.projects:
            raise ValueError(f"项目未加载: {project_name}")

        proj = self.projects[project_name]
        if not proj.compute_data:
            return {}

        totals = proj.compute_data.get('totals', {})
        estimated = proj.compute_data.get('estimated_cost', {}).get('weighted_units', {})
        params = proj.compute_data.get('total_params', 0)

        return {
            'total_params': params,
            'additions': totals.get('additions', 0),
            'multiplications': totals.get('multiplications', 0),
            'maps': totals.get('maps', 0),
            'total_ops': totals.get('total', 0),
            'weighted_total': estimated.get('total', 0),
            'weighted_additions': estimated.get('additions', 0),
            'weighted_multiplications': estimated.get('multiplications', 0),
            'weighted_maps': estimated.get('maps', 0),
        }

    def calculate_mae_afmae(self, project_name: str) -> dict:
        """获取 MAE 和 AFMAE 指标"""
        if project_name not in self.projects:
            raise ValueError(f"项目未加载: {project_name}")

        proj = self.projects[project_name]
        eval_metrics = proj.training_info.get('evaluation_metrics', {})

        if not eval_metrics:
            return {'error': 'evaluation_metrics not available', 'hint': 'run python cli.py -e PROJECT_NAME to generate'}

        return {
            'val_mae': eval_metrics.get('val_mae', 0),
            'val_afmae': eval_metrics.get('val_afmae', 0),
        }

    def calculate_suppression_rate(self, ref_drift: float, comp_drift: float) -> float:
        """计算抑制率"""
        if ref_drift == 0:
            return 0.0
        return (ref_drift - comp_drift) / ref_drift * 100

    def run_analysis(self) -> dict:
        """执行完整的消融实验分析"""
        self.load_all_projects()

        metrics_cfg = self.config.get('metrics', {})
        results = {
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'projects': [],
            'metrics': {}
        }

        for proj in self.config.get('projects', []):
            proj_name = proj['name']
            proj_label = proj.get('label', proj_name)
            results['projects'].append({
                'name': proj_name,
                'label': proj_label,
                'path': proj['path']
            })

        if metrics_cfg.get('natural_frequency_drift', {}).get('enabled', False):
            results['metrics']['natural_frequency_drift'] = self._analyze_natural_frequency_drift(
                metrics_cfg['natural_frequency_drift']
            )

        if metrics_cfg.get('sensitivity_drift', {}).get('enabled', False):
            freq_hz = metrics_cfg['sensitivity_drift'].get('frequency_hz', 100)
            results['metrics']['sensitivity_drift'] = self._analyze_sensitivity_drift(
                metrics_cfg['sensitivity_drift'],
                freq_hz
            )

        if metrics_cfg.get('linearity', {}).get('enabled', False):
            results['metrics']['linearity'] = self._analyze_linearity()

        if metrics_cfg.get('compute_cost', {}).get('enabled', False):
            results['metrics']['compute_cost'] = self._analyze_compute_cost(
                metrics_cfg['compute_cost']
            )

        if metrics_cfg.get('mae_afmae', {}).get('enabled', False):
            results['metrics']['mae_afmae'] = self._analyze_mae_afmae()

        results['metrics']['natural_frequency_drift_origin'] = self._analyze_natural_frequency_drift_origin(
            metrics_cfg.get('natural_frequency_drift', {})
        )
        results['metrics']['sensitivity_drift_origin'] = self._analyze_sensitivity_drift_origin(
            metrics_cfg.get('sensitivity_drift', {}),
            metrics_cfg.get('sensitivity_drift', {}).get('frequency_hz', 100)
        )
        results['metrics']['linearity_origin'] = self._analyze_linearity_origin()

        self.results = results
        return results

    def _analyze_natural_frequency_drift(self, metric_cfg: dict) -> dict:
        """分析固有频率漂移"""
        ref_project = metric_cfg.get('reference')
        metric_results = {}

        for proj_name in self.projects.keys():
            drift_data = self.calculate_natural_frequency_drift(proj_name, use_origin=False)
            metric_results[proj_name] = {
                'drift': drift_data['drift'],
                'unit': 'Hz',
                'min': drift_data['min'],
                'max': drift_data['max'],
                'median': drift_data['median']
            }

        if ref_project and ref_project in metric_results:
            ref_drift = metric_results[ref_project]['drift']
            for proj_name, data in metric_results.items():
                if proj_name != ref_project:
                    data['suppression'] = self.calculate_suppression_rate(ref_drift, data['drift'])

        return metric_results

    def _analyze_natural_frequency_drift_origin(self, metric_cfg: dict) -> dict:
        """分析固有频率漂移 (未补偿/Origin)"""
        metric_results = {}

        for proj_name in self.projects.keys():
            proj_path = self.config['projects'][list(self.projects.keys()).index(proj_name)]['path']
            if not proj_path.startswith('00_MAE_VS_AFMAE'):
                continue

            drift_data = self.calculate_natural_frequency_drift(proj_name, use_origin=True)
            metric_results[proj_name] = {
                'drift': drift_data['drift'],
                'unit': 'Hz',
                'min': drift_data['min'],
                'max': drift_data['max'],
                'median': drift_data['median']
            }

        return metric_results

    def _analyze_sensitivity_drift(self, metric_cfg: dict, freq_hz: float) -> dict:
        """分析灵敏度漂移"""
        ref_project = metric_cfg.get('reference')
        metric_results = {}

        for proj_name in self.projects.keys():
            drift_data = self.calculate_sensitivity_drift(proj_name, freq_hz, use_origin=False)
            metric_results[proj_name] = {
                'drift': drift_data['drift'],
                'unit': '%',
                'min': drift_data['min'],
                'max': drift_data['max'],
                'median': drift_data['median']
            }

        if ref_project and ref_project in metric_results:
            ref_drift = metric_results[ref_project]['drift']
            for proj_name, data in metric_results.items():
                if proj_name != ref_project:
                    data['suppression'] = self.calculate_suppression_rate(ref_drift, data['drift'])

        return metric_results

    def _analyze_sensitivity_drift_origin(self, metric_cfg: dict, freq_hz: float) -> dict:
        """分析灵敏度漂移 (未补偿/Origin)"""
        metric_results = {}

        for proj_name in self.projects.keys():
            proj_path = self.config['projects'][list(self.projects.keys()).index(proj_name)]['path']
            if not proj_path.startswith('00_MAE_VS_AFMAE'):
                continue

            drift_data = self.calculate_sensitivity_drift(proj_name, freq_hz, use_origin=True)
            metric_results[proj_name] = {
                'drift': drift_data['drift'],
                'unit': '%',
                'min': drift_data['min'],
                'max': drift_data['max'],
                'median': drift_data['median']
            }

        return metric_results

    def _analyze_linearity(self) -> dict:
        """分析线性度"""
        metric_results = {}

        for proj_name in self.projects.keys():
            linearity_data = self.calculate_linearity(proj_name, use_origin=False)
            if 'error' in linearity_data:
                metric_results[proj_name] = linearity_data
            else:
                metric_results[proj_name] = {
                    'mean': linearity_data['mean'],
                    'max': linearity_data['max'],
                    'min': linearity_data['min'],
                    'unit': '%'
                }

        return metric_results

    def _analyze_linearity_origin(self) -> dict:
        """分析线性度 (未补偿/Origin)"""
        metric_results = {}

        for proj_name in self.projects.keys():
            proj_path = self.config['projects'][list(self.projects.keys()).index(proj_name)]['path']
            if not proj_path.startswith('00_MAE_VS_AFMAE'):
                continue

            linearity_data = self.calculate_linearity(proj_name, use_origin=True)
            if 'error' in linearity_data:
                metric_results[proj_name] = linearity_data
            else:
                metric_results[proj_name] = {
                    'mean': linearity_data['mean'],
                    'max': linearity_data['max'],
                    'min': linearity_data['min'],
                    'unit': '%'
                }

        return metric_results

    def _analyze_compute_cost(self, metric_cfg: dict) -> dict:
        """分析计算量估计指标"""
        metric_results = {}
        show_details = metric_cfg.get('show_details', True)

        for proj_name in self.projects.keys():
            compute_data = self.calculate_compute_cost(proj_name)
            if not compute_data:
                metric_results[proj_name] = {'error': 'compute_analysis not available'}
                continue

            result = {
                'total_params': compute_data.get('total_params', 0),
                'additions': compute_data.get('additions', 0),
                'multiplications': compute_data.get('multiplications', 0),
                'maps': compute_data.get('maps', 0),
                'total_ops': compute_data.get('total_ops', 0),
                'weighted_total': compute_data.get('weighted_total', 0),
            }

            if show_details:
                result['weighted_additions'] = compute_data.get('weighted_additions', 0)
                result['weighted_multiplications'] = compute_data.get('weighted_multiplications', 0)
                result['weighted_maps'] = compute_data.get('weighted_maps', 0)

            metric_results[proj_name] = result

        return metric_results

    def _analyze_mae_afmae(self) -> dict:
        """分析 MAE 和 AFMAE 指标"""
        metric_results = {}

        for proj_name in self.projects.keys():
            mae_afmae_data = self.calculate_mae_afmae(proj_name)
            if 'error' in mae_afmae_data:
                metric_results[proj_name] = mae_afmae_data
            else:
                metric_results[proj_name] = {
                    'val_mae': mae_afmae_data.get('val_mae', 0),
                    'val_afmae': mae_afmae_data.get('val_afmae', 0),
                }

        return metric_results

    def generate_markdown_report(self) -> str:
        """生成 Markdown 对比报告"""
        if not self.results:
            self.run_analysis()

        lines = [
            "# 消融实验对比报告",
            "",
            f"**生成时间**: {self.results['timestamp']}",
            "",
            "---",
            ""
        ]

        metrics = self.results.get('metrics', {})

        lines.extend(self._format_summary_section(metrics))

        return '\n'.join(lines)

    def _format_natural_frequency_section(self, data: dict) -> List[str]:
        lines = [
            "## 1. 固有频率漂移",
            "",
            "| Project | Drift (Hz) | Suppression (%) |",
            "|---------|------------|-----------------|"
        ]
        for proj_name, proj_data in data.items():
            drift = proj_data['drift']
            suppression = proj_data.get('suppression')
            sup_str = f"{suppression:.2f}%" if suppression is not None else "-"
            lines.append(f"| {proj_name} | {drift:.4f} | {sup_str} |")
        lines.append("")
        return lines

    def _format_sensitivity_section(self, data: dict, freq_hz: float) -> List[str]:
        lines = [
            f"## 2. 灵敏度漂移 ({freq_hz}Hz)",
            "",
            "| Project | Drift (%) | Suppression (%) |",
            "|---------|-----------|-----------------|"
        ]
        for proj_name, proj_data in data.items():
            drift = proj_data['drift']
            suppression = proj_data.get('suppression')
            sup_str = f"{suppression:.2f}%" if suppression is not None else "-"
            lines.append(f"| {proj_name} | {drift:.4f} | {sup_str} |")
        lines.append("")
        return lines

    def _format_linearity_section(self, data: dict) -> List[str]:
        lines = [
            "## 3. 线性度 (1 - R²)",
            "",
            "| Project | Mean (%) | Max (%) | Min (%) |",
            "|---------|----------|---------|---------|"
        ]
        has_missing = False
        for proj_name, proj_data in data.items():
            if 'error' in proj_data:
                lines.append(f"| {proj_name} | ERROR: {proj_data['error']} | - | - |")
                has_missing = True
            else:
                lines.append(f"| {proj_name} | {proj_data['mean']:.4f} | {proj_data['max']:.4f} | {proj_data['min']:.4f} |")
        if has_missing:
            lines.append("")
            lines.append("> **提示**: 缺少 `linearity_by_frequency.json` 的项目可通过 `python cli.py -e PROJECT_NAME` 生成")
        lines.append("")
        return lines

    def _format_compute_cost_section(self, data: dict) -> List[str]:
        lines = [
            "## 4. 计算量估计",
            "",
            "| Project | Add | Mul | MAP | Total Ops | 加权估计 |",
            "|---------|-----|-----|-----|-----------|------------|"
        ]
        has_missing = False
        for proj_name, proj_data in data.items():
            if 'error' in proj_data:
                lines.append(f"| {proj_name} | ERROR: {proj_data['error']} | - | - | - | - |")
                has_missing = True
            else:
                lines.append(
                    f"| {proj_name} | "
                    f"{proj_data.get('additions', 0)} | "
                    f"{proj_data.get('multiplications', 0)} | "
                    f"{proj_data.get('maps', 0)} | "
                    f"{proj_data.get('total_ops', 0)} | "
                    f"{proj_data.get('weighted_total', 0):.1f} |"
                )
        if has_missing:
            lines.append("")
            lines.append("> **提示**: 缺少 `compute_analysis.json` 的项目可通过 `python cli.py -m PROJECT_NAME` 或 `python cli.py -e PROJECT_NAME` 生成")
        lines.append("")
        return lines

    def _format_summary_section(self, metrics: dict) -> List[str]:
        lines = [
            "## 5. 综合对比",
            "",
            "| Project | 加权估计 | Val MAE | Val AFMAE | Freq Drift (Hz) | Sens Drift (%) | Linearity (%) |",
            "|---------|------------|---------|------------|------------------|-----------------|----------------|"
        ]

        compute_cost = metrics.get('compute_cost', {})
        mae_afmae = metrics.get('mae_afmae', {})
        freq_drift = metrics.get('natural_frequency_drift', {})
        sens_drift = metrics.get('sensitivity_drift', {})
        linearity = metrics.get('linearity', {})
        freq_drift_origin = metrics.get('natural_frequency_drift_origin', {})
        sens_drift_origin = metrics.get('sensitivity_drift_origin', {})
        linearity_origin = metrics.get('linearity_origin', {})

        has_missing = False

        origin_added = False
        for proj_entry in self.results.get('projects', []):
            proj_name_only = proj_entry['name']
            proj_path = proj_entry.get('path', '')
            is_00_series = proj_path.startswith('00_MAE_VS_AFMAE')

            if is_00_series and not origin_added:
                fd_keys = list(freq_drift_origin.keys())
                if fd_keys:
                    fd_o = freq_drift_origin[fd_keys[0]]
                    sd_o = sens_drift_origin[fd_keys[0]]
                    lin_o = linearity_origin[fd_keys[0]]
                    lines.append("| ORIGIN (未补偿) | - | - | - | "
                                 f"{fd_o.get('drift', 0):.4f} | "
                                 f"{sd_o.get('drift', 0):.4f} | "
                                 f"{lin_o.get('mean', 0):.4f} |")
                    origin_added = True

            row = [proj_name_only]

            cc = compute_cost.get(proj_name_only, {})
            if 'error' in cc:
                row.append('ERROR')
                has_missing = True
            else:
                row.append(f"{cc.get('weighted_total', 0):.1f}")

            ma = mae_afmae.get(proj_name_only, {})
            if 'error' in ma:
                row.extend(['ERROR', 'ERROR'])
                has_missing = True
            else:
                row.append(f"{ma.get('val_mae', 0):.4f}")
                row.append(f"{ma.get('val_afmae', 0):.4f}")

            fd = freq_drift.get(proj_name_only, {})
            if 'error' in fd:
                row.append('ERROR')
                has_missing = True
            else:
                row.append(f"{fd.get('drift', 0):.4f}")

            sd = sens_drift.get(proj_name_only, {})
            if 'error' in sd:
                row.append('ERROR')
                has_missing = True
            else:
                row.append(f"{sd.get('drift', 0):.4f}")

            lin = linearity.get(proj_name_only, {})
            if 'error' in lin:
                row.append('ERROR')
                has_missing = True
            else:
                row.append(f"{lin.get('mean', 0):.4f}")

            lines.append("| " + " | ".join(row) + " |")

        if has_missing:
            lines.append("")
            lines.append("> **提示**: 缺少数据的项目可通过 `python cli.py -e PROJECT_NAME` 生成")
        lines.append("")
        return lines

    def save_results(self) -> None:
        """保存结果到 JSON 和 Markdown 文件"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.output_dir / 'ablation_results.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        logger.info(f"结果已保存: {json_path}")

        md_report = self.generate_markdown_report()
        md_path = self.output_dir / 'ablation_report.md'
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_report)
        logger.info(f"报告已保存: {md_path}")


def run_ablation_study(config: dict, output_dir: Optional[Path] = None) -> dict:
    """运行消融实验的便捷函数"""
    analyzer = AblationStudyAnalyzer(config, output_dir)
    results = analyzer.run_analysis()
    analyzer.save_results()
    return results
