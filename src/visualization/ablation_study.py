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
        self.config_path = Path(project_path) / 'config.json'
        self.raw_data_path = Path(project_path) / 'data' / 'linear_response.json'
        self.compute_analysis_path = Path(project_path) / 'data' / 'compute_analysis.json'
        self.training_info_path = Path(project_path) / 'data' / 'training_info.json'
        self.raw_data = {}
        self.processed_data = {}
        self.compute_data = {}
        self.training_info = {}
        self.config_data = {}

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

    def load_config(self) -> bool:
        """Load project config.json file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            return True
        except FileNotFoundError:
            logger.warning(f"config.json not found: {self.config_path}")
            return False
        except Exception as e:
            logger.error(f"Error loading config: {e}")
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

    def _scan_project_dirs(self) -> List[dict]:
        """扫描 project_dirs 目录，自动发现所有包含 config.json 的子目录"""
        discovered = []
        for proj_dir in self.config.get('project_dirs', []):
            base_path = Path(proj_dir)
            if not base_path.exists():
                logger.warning(f"项目目录不存在: {proj_dir}")
                continue
            for subdir in base_path.iterdir():
                if not subdir.is_dir():
                    continue
                config_file = subdir / 'config.json'
                if config_file.exists():
                    # 自动生成 name 和 label (使用目录名)
                    proj_name = subdir.name
                    proj_path = str(subdir)
                    discovered.append({
                        'name': proj_name,
                        'label': proj_name,
                        'path': proj_path
                    })
                    logger.info(f"发现项目: {proj_name} ({proj_path})")
        return discovered

    def load_all_projects(self) -> None:
        """使用 SimpleProjectResult 加载所有项目

        支持两种配置方式:
        - project_dirs: 目录列表，自动扫描子目录中的 config.json
        - fixed_projects / projects: 显式指定的项目列表
        """
        # 合并 fixed_projects (显式指定) 和 projects (兼容旧格式)
        explicit_projects = self.config.get('fixed_projects', []) or self.config.get('projects', [])

        # 自动扫描 project_dirs
        scanned_projects = self._scan_project_dirs()

        # 合并所有项目 (explicit + scanned)
        all_projects = explicit_projects + scanned_projects

        # 按 path 去重，保留先出现的 (explicit 优先)
        seen_paths = set()
        deduplicated = []
        for proj in all_projects:
            if proj['path'] not in seen_paths:
                seen_paths.add(proj['path'])
                deduplicated.append(proj)

        for proj in deduplicated:
            proj_name = proj['name']
            proj_path = proj['path']
            try:
                result = SimpleProjectResult(proj_path)
                result.load_data()
                result.process_data()
                result.load_compute_analysis()
                result.load_training_info()
                result.load_config()
                self.projects[proj_name] = result
                logger.info(f"已加载项目: {proj_name} ({proj_path})")
            except Exception as e:
                logger.error(f"加载项目失败 {proj_name}: {e}")

        # 保存去重后的项目列表，供 run_analysis 使用
        self.project_list = deduplicated

    def _get_project_path(self, proj_name: str) -> str:
        """根据项目名查找项目路径"""
        project_list = getattr(self, 'project_list', self.config.get('projects', []))
        for proj in project_list:
            if proj['name'] == proj_name:
                return proj.get('path', '')
        return ''

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

    def calculate_config_info(self, project_name: str) -> dict:
        """获取项目配置信息 (epoch_train, learning_rate)"""
        if project_name not in self.projects:
            raise ValueError(f"项目未加载: {project_name}")

        proj = self.projects[project_name]
        if not proj.config_data:
            return {'error': 'config.json not available'}

        return {
            'epoch_train': proj.config_data.get('epoch_train'),
            'learning_rate': proj.config_data.get('learning_rate'),
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

        for proj in getattr(self, 'project_list', self.config.get('projects', [])):
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

        results['metrics']['config_info'] = self._analyze_config_info()

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
            proj_path = self._get_project_path(proj_name)
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
            proj_path = self._get_project_path(proj_name)
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
            proj_path = self._get_project_path(proj_name)
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

    def _analyze_config_info(self) -> dict:
        """分析项目配置信息 (epoch_train, learning_rate)"""
        metric_results = {}

        for proj_name in self.projects.keys():
            config_data = self.calculate_config_info(proj_name)
            if 'error' in config_data:
                metric_results[proj_name] = config_data
            else:
                metric_results[proj_name] = {
                    'epoch_train': config_data.get('epoch_train'),
                    'learning_rate': config_data.get('learning_rate'),
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

    def save_to_excel(self, filename: str) -> None:
        """导出结果到 xlsx 文件"""
        import pandas as pd
        from openpyxl.styles import Alignment

        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        metrics = self.results.get('metrics', {})
        compute_cost = metrics.get('compute_cost', {})
        mae_afmae = metrics.get('mae_afmae', {})
        freq_drift = metrics.get('natural_frequency_drift', {})
        sens_drift = metrics.get('sensitivity_drift', {})
        linearity = metrics.get('linearity', {})
        config_info = metrics.get('config_info', {})
        freq_drift_origin = metrics.get('natural_frequency_drift_origin', {})
        sens_drift_origin = metrics.get('sensitivity_drift_origin', {})
        linearity_origin = metrics.get('linearity_origin', {})

        # Sheet 1: Summary 综合对比表
        summary_rows = []
        origin_added = False
        for proj_entry in self.results.get('projects', []):
            proj_name = proj_entry['name']
            proj_path = proj_entry.get('path', '')
            is_00_series = proj_path.startswith('00_MAE_VS_AFMAE')

            if is_00_series and not origin_added:
                fd_keys = list(freq_drift_origin.keys())
                if fd_keys:
                    fd_o = freq_drift_origin[fd_keys[0]]
                    sd_o = sens_drift_origin[fd_keys[0]]
                    lin_o = linearity_origin[fd_keys[0]]
                    summary_rows.append({
                        'Project': 'ORIGIN (未补偿)',
                        'Epochs': None,
                        'LR': None,
                        '加权估计': None,
                        'Val MAE': None,
                        'Val AFMAE': None,
                        'Freq Drift (Hz)': fd_o.get('drift'),
                        'Sens Drift (%)': sd_o.get('drift'),
                        'Linearity (%)': lin_o.get('mean'),
                        'Freq Suppression (%)': None,
                        'Sens Suppression (%)': None,
                    })
                    origin_added = True

            cc = compute_cost.get(proj_name, {})
            ma = mae_afmae.get(proj_name, {})
            fd = freq_drift.get(proj_name, {})
            sd = sens_drift.get(proj_name, {})
            lin = linearity.get(proj_name, {})
            ci = config_info.get(proj_name, {})

            summary_rows.append({
                'Project': proj_name,
                'Epochs': ci.get('epoch_train') if 'error' not in ci else None,
                'LR': ci.get('learning_rate') if 'error' not in ci else None,
                '加权估计': cc.get('weighted_total') if 'error' not in cc else None,
                'Val MAE': ma.get('val_mae') if 'error' not in ma else None,
                'Val AFMAE': ma.get('val_afmae') if 'error' not in ma else None,
                'Freq Drift (Hz)': fd.get('drift') if 'error' not in fd else None,
                'Sens Drift (%)': sd.get('drift') if 'error' not in sd else None,
                'Linearity (%)': lin.get('mean') if 'error' not in lin else None,
                'Freq Suppression (%)': fd.get('suppression') if 'error' not in fd else None,
                'Sens Suppression (%)': sd.get('suppression') if 'error' not in sd else None,
            })

        summary_df = pd.DataFrame(summary_rows)

        # Sheet 2: Natural Frequency Drift Detail
        freq_rows = []
        for proj_name, data in freq_drift.items():
            row = {'Project': proj_name}
            row.update(data)
            freq_rows.append(row)
        freq_df = pd.DataFrame(freq_rows) if freq_rows else pd.DataFrame()

        # Sheet 3: Sensitivity Drift Detail
        sens_rows = []
        for proj_name, data in sens_drift.items():
            row = {'Project': proj_name}
            row.update(data)
            sens_rows.append(row)
        sens_df = pd.DataFrame(sens_rows) if sens_rows else pd.DataFrame()

        # Sheet 4: Linearity Detail
        lin_rows = []
        for proj_name, data in linearity.items():
            row = {'Project': proj_name}
            row.update(data)
            lin_rows.append(row)
        lin_df = pd.DataFrame(lin_rows) if lin_rows else pd.DataFrame()

        # Sheet 5: Compute Cost Detail
        comp_rows = []
        for proj_name, data in compute_cost.items():
            row = {'Project': proj_name}
            row.update(data)
            comp_rows.append(row)
        comp_df = pd.DataFrame(comp_rows) if comp_rows else pd.DataFrame()

        # Sheet 6: MAE/AFMAE Detail
        mae_rows = []
        for proj_name, data in mae_afmae.items():
            row = {'Project': proj_name}
            row.update(data)
            mae_rows.append(row)
        mae_df = pd.DataFrame(mae_rows) if mae_rows else pd.DataFrame()

        # Sheet 7: Config Info Detail
        cfg_rows = []
        for proj_name, data in config_info.items():
            row = {'Project': proj_name}
            row.update(data)
            cfg_rows.append(row)
        cfg_df = pd.DataFrame(cfg_rows) if cfg_rows else pd.DataFrame()

        with pd.ExcelWriter(str(output_path)) as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            if not freq_df.empty:
                freq_df.to_excel(writer, sheet_name='Freq Drift', index=False)
            if not sens_df.empty:
                sens_df.to_excel(writer, sheet_name='Sens Drift', index=False)
            if not lin_df.empty:
                lin_df.to_excel(writer, sheet_name='Linearity', index=False)
            if not comp_df.empty:
                comp_df.to_excel(writer, sheet_name='Compute Cost', index=False)
            if not mae_df.empty:
                mae_df.to_excel(writer, sheet_name='MAE AFMAE', index=False)
            if not cfg_df.empty:
                cfg_df.to_excel(writer, sheet_name='Config Info', index=False)

            # Apply auto-wrap and auto-adjust column width to all sheets
            for sheet_name in writer.sheets:
                sheet = writer.sheets[sheet_name]
                for col_idx, column_cells in enumerate(sheet.columns, 1):
                    max_length = 0
                    for cell in column_cells:
                        try:
                            if cell.value:
                                max_length = max(max_length, len(str(cell.value)))
                        except:
                            pass
                    # Set wrap alignment and optimal width
                    for cell in column_cells:
                        cell.alignment = Alignment(wrap_text=True, vertical='top')
                    adjusted_width = min(max_length + 2, 50)
                    sheet.column_dimensions[column_cells[0].column_letter].width = adjusted_width

        logger.info(f"Excel 报告已保存: {output_path}")

    def save_results(self) -> None:
        """保存结果到 JSON、Markdown 和 Xlsx 文件"""
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

        # 检查是否需要导出 xlsx
        output_formats = self.config.get('output', {}).get('format', [])
        if 'xlsx' in output_formats:
            xlsx_path = self.output_dir / 'ablation_report.xlsx'
            self.save_to_excel(str(xlsx_path))


def run_ablation_study(config: dict, output_dir: Optional[Path] = None) -> dict:
    """运行消融实验的便捷函数"""
    analyzer = AblationStudyAnalyzer(config, output_dir)
    results = analyzer.run_analysis()
    analyzer.save_results()
    return results
