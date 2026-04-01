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
        self.raw_data_path = Path('projects') / project_path / 'data' / 'linear_response.json'
        self.raw_data = {}
        self.processed_data = {}

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
                self.projects[proj_name] = result
                logger.info(f"已加载项目: {proj_name} ({proj_path})")
            except Exception as e:
                logger.error(f"加载项目失败 {proj_name}: {e}")

    def calculate_natural_frequency_drift(self, project_name: str) -> dict:
        """计算固有频率漂移 - 复用 ProjectResult + calculate_drift()"""
        if project_name not in self.projects:
            raise ValueError(f"项目未加载: {project_name}")

        fn = self.projects[project_name].processed_data['fn_comped']
        metric = {
            'min': float(np.min(fn)),
            'max': float(np.max(fn)),
            'median': float(np.median(fn))
        }
        metric['drift'] = calculate_drift(metric)
        return metric

    def calculate_sensitivity_drift(self, project_name: str, freq_hz: float = 100) -> dict:
        """计算灵敏度漂移 - 复用 ProjectResult.process_data(freq_sen) + calculate_drift()"""
        if project_name not in self.projects:
            raise ValueError(f"项目未加载: {project_name}")

        result = self.projects[project_name]
        result.process_data(freq_sen=freq_hz)
        sens = result.processed_data['sensitive_comped']
        metric = {
            'min': float(np.min(sens)),
            'max': float(np.max(sens)),
            'median': float(np.median(sens))
        }
        metric['drift'] = calculate_drift(metric)
        return metric

    def calculate_linearity(self, project_name: str) -> dict:
        """计算平均线性度 (1 - R²) - 直接读取 JSON"""
        if project_name not in self.projects:
            raise ValueError(f"项目未加载: {project_name}")

        proj = self.projects[project_name]
        path = Path('projects') / proj.project_path / 'data' / 'linearity_by_frequency.json'
        if not path.exists():
            raise FileNotFoundError(f"linearity_by_frequency.json not found: {path}")

        with open(path) as f:
            data = json.load(f)

        r2_values = [item['r_squared_comped'] for item in data['linearity_by_frequency']]
        nonlinearity = [1 - r2 for r2 in r2_values]
        return {
            'mean': float(np.mean(nonlinearity)) * 100,
            'max': float(np.max(nonlinearity)) * 100,
            'min': float(np.min(nonlinearity)) * 100
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

        self.results = results
        return results

    def _analyze_natural_frequency_drift(self, metric_cfg: dict) -> dict:
        """分析固有频率漂移"""
        ref_project = metric_cfg.get('reference')
        metric_results = {}

        for proj_name in self.projects.keys():
            drift_data = self.calculate_natural_frequency_drift(proj_name)
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

    def _analyze_sensitivity_drift(self, metric_cfg: dict, freq_hz: float) -> dict:
        """分析灵敏度漂移"""
        ref_project = metric_cfg.get('reference')
        metric_results = {}

        for proj_name in self.projects.keys():
            drift_data = self.calculate_sensitivity_drift(proj_name, freq_hz)
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

    def _analyze_linearity(self) -> dict:
        """分析线性度"""
        metric_results = {}

        for proj_name in self.projects.keys():
            linearity_data = self.calculate_linearity(proj_name)
            metric_results[proj_name] = {
                'mean': linearity_data['mean'],
                'max': linearity_data['max'],
                'min': linearity_data['min'],
                'unit': '%'
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

        if 'natural_frequency_drift' in metrics:
            lines.extend(self._format_natural_frequency_section(metrics['natural_frequency_drift']))

        if 'sensitivity_drift' in metrics:
            freq_hz = self.config.get('metrics', {}).get('sensitivity_drift', {}).get('frequency_hz', 100)
            lines.extend(self._format_sensitivity_section(metrics['sensitivity_drift'], freq_hz))

        if 'linearity' in metrics:
            lines.extend(self._format_linearity_section(metrics['linearity']))

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
        for proj_name, proj_data in data.items():
            lines.append(f"| {proj_name} | {proj_data['mean']:.4f} | {proj_data['max']:.4f} | {proj_data['min']:.4f} |")
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
