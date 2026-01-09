# 偏置调谐器生产部署方案 (路径重点版)

## 执行总结

基于**WNET5q1h2u6l3**项目的深度调研，重新设计偏置调谐器的路径构建系统和pathcheck机制。核心改进：**路径构建优先级+预检查机制+容错路径发现**。

## WNET5q1h2u6l3项目路径分析

### 🗂️ 项目结构完整映射

```
WNET5q1h2u6l3/
├── config.json                              # 主配置文件 ⭐
├── config_baseline.json                     # 基线配置
├── config_with_bias_compensation.json       # 带偏置补偿配置
├── config_test_layer*.json                  # 测试配置文件
└── data/
    ├── inference/                           # 推理结果目录 ⭐
    │   ├── error_analysis.json             # 核心错误分析文件 🔥
    │   ├── inference_metadata.json         # 推理元数据 🔥
    │   ├── nn_layers/                      # NN层输出
    │   ├── spice_layers/                   # SPICE层输出  
    │   ├── numpy_layers/                   # NumPy层输出
    │   ├── nn_spice_error_layers/          # NN-SPICE误差
    │   └── nn_numpy_error_layers/          # NN-NumPy误差
    ├── inference_enabled/                   # 启用推理状态
    ├── inference_disabled/                  # 禁用推理状态
    ├── scalers/                            # 数据缩放器
    │   ├── combined_scaler.json
    │   ├── scaler_x.json
    │   └── scaler_y.json
    ├── model_info.json                     # 模型信息
    ├── training_info.json                  # 训练信息
    ├── training_state.json                 # 训练状态
    └── *.weights.json                      # 权重文件
```

### 🎯 关键路径优先级分析

基于WNET5q1h2u6l3项目，定义路径重要性等级：

| 优先级 | 路径类型 | 具体路径 | 用途 | 必需性 |
|-------|----------|----------|------|--------|
| **P0 (必需)** | 主配置 | `config.json` | 项目配置 | 🔴 关键 |
| **P0 (必需)** | 错误分析 | `data/inference/error_analysis.json` | 偏置误差数据 | 🔴 关键 |
| **P1 (重要)** | 推理元数据 | `data/inference/inference_metadata.json` | 推理状态 | 🟠 重要 |
| **P1 (重要)** | 模型信息 | `data/model_info.json` | 模型验证 | 🟠 重要 |
| **P2 (可选)** | 层输出 | `data/inference/*/layers/` | 详细分析 | 🟡 可选 |
| **P2 (可选)** | 缩放器 | `data/scalers/*.json` | 数据预处理 | 🟡 可选 |
| **P3 (备用)** | 配置变体 | `config_*.json` | 备份配置 | 🟢 备用 |

## 路径构建系统重新设计

### A. 核心文件修改重点

#### A1. `utils/path_finder.py` - 路径构建核心 🔧

**全新设计，基于WNET5q1h2u6l3实际结构**

```python
"""
路径查找器 - 基于WNET5q1h2u6l3项目优化的路径构建系统
重点：可靠的路径发现 + 智能容错 + 完整验证
"""

from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
import os
import json
import logging

logger = logging.getLogger(__name__)

class ProjectPathMapper:
    """项目路径映射器 - 基于WNET5q1h2u6l3结构设计"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_root = None
        self.project_path = None
        self._path_cache = {}
        
    def discover_project_structure(self) -> bool:
        """发现项目结构，基于WNET5q1h2u6l3模式"""
        # 1. 查找项目根目录
        self.project_root = self._find_project_root()
        if not self.project_root:
            return False
            
        # 2. 查找具体项目目录
        self.project_path = self._find_project_directory()
        if not self.project_path:
            return False
            
        # 3. 验证项目结构
        return self._validate_project_structure()
    
    def _find_project_root(self) -> Optional[Path]:
        """查找项目根目录 - 多策略发现"""
        current = Path.cwd().resolve()
        
        # 策略1: 向上查找关键标记文件
        root_markers = [
            'cli.py',           # 主程序文件
            'projects',             # 项目目录
            'config.py',            # 配置文件
            'metnl.py'              # 核心模块
        ]
        
        for _ in range(10):  # 最多向上10层
            for marker in root_markers:
                if (current / marker).exists():
                    logger.info(f"发现项目根目录标记 '{marker}': {current}")
                    return current
            
            parent = current.parent
            if parent == current:  # 已达根目录
                break
            current = parent
        
        # 策略2: 环境变量或配置指定
        env_root = os.environ.get('MET_NONLINEAR_ROOT')
        if env_root and Path(env_root).exists():
            logger.info(f"使用环境变量指定的根目录: {env_root}")
            return Path(env_root)
        
        # 策略3: 已知路径模式匹配
        known_patterns = [
            '/mnt/f/Work/met_nonlinear_worktrees/met_nonlinear_master',
            '~/met_nonlinear',
            './met_nonlinear'
        ]
        
        for pattern in known_patterns:
            candidate = Path(pattern).expanduser().resolve()
            if candidate.exists() and (candidate / 'projects').exists():
                logger.info(f"使用已知路径模式: {candidate}")
                return candidate
        
        logger.error("无法找到项目根目录")
        return None
    
    def _find_project_directory(self) -> Optional[Path]:
        """查找具体项目目录 - 基于WNET5q1h2u6l3模式"""
        if not self.project_root:
            return None
            
        projects_dir = self.project_root / 'projects'
        if not projects_dir.exists():
            logger.error(f"项目目录不存在: {projects_dir}")
            return None
        
        # 策略1: 精确匹配
        exact_path = projects_dir / self.project_name
        if exact_path.exists() and (exact_path / 'config.json').exists():
            logger.info(f"精确匹配项目: {exact_path}")
            return exact_path
        
        # 策略2: 模糊匹配
        for candidate in projects_dir.iterdir():
            if not candidate.is_dir():
                continue
                
            # 部分匹配
            if (self.project_name.lower() in candidate.name.lower() and 
                (candidate / 'config.json').exists()):
                logger.info(f"模糊匹配项目: {candidate}")
                return candidate
        
        # 策略3: 交互式选择（如果有多个候选）
        candidates = [
            d for d in projects_dir.iterdir() 
            if d.is_dir() and (d / 'config.json').exists()
        ]
        
        if candidates:
            logger.warning(f"找到多个项目候选: {[c.name for c in candidates]}")
            # 选择最近修改的
            latest = max(candidates, key=lambda p: p.stat().st_mtime)
            logger.info(f"选择最近修改的项目: {latest}")
            return latest
        
        logger.error(f"无法找到项目: {self.project_name}")
        return None
    
    def _validate_project_structure(self) -> bool:
        """验证项目结构 - 基于WNET5q1h2u6l3标准"""
        if not self.project_path:
            return False
        
        # 必需文件检查
        required_files = [
            'config.json',
        ]
        
        # 必需目录检查  
        required_dirs = [
            'data',
        ]
        
        # 检查必需文件
        for file_name in required_files:
            file_path = self.project_path / file_name
            if not file_path.exists():
                logger.error(f"缺少必需文件: {file_path}")
                return False
        
        # 检查必需目录
        for dir_name in required_dirs:
            dir_path = self.project_path / dir_name
            if not dir_path.exists():
                logger.warning(f"缺少目录: {dir_path}")
                # data目录可以创建
                if dir_name == 'data':
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"创建数据目录: {dir_path}")
        
        logger.info(f"项目结构验证通过: {self.project_path}")
        return True
    
    def get_path_map(self) -> Dict[str, Path]:
        """获取完整路径映射表"""
        if not self.project_path:
            raise RuntimeError("项目路径未初始化")
        
        return {
            # 核心路径
            'project_root': self.project_root,
            'project_path': self.project_path,
            
            # 配置文件
            'config': self.project_path / 'config.json',
            'config_baseline': self.project_path / 'config_baseline.json',
            'config_with_bias': self.project_path / 'config_with_bias_compensation.json',
            
            # 数据目录
            'data_dir': self.project_path / 'data',
            'inference_dir': self.project_path / 'data' / 'inference',
            'scalers_dir': self.project_path / 'data' / 'scalers',
            
            # 关键文件
            'error_analysis': self.project_path / 'data' / 'inference' / 'error_analysis.json',
            'inference_metadata': self.project_path / 'data' / 'inference' / 'inference_metadata.json', 
            'model_info': self.project_path / 'data' / 'model_info.json',
            'training_info': self.project_path / 'data' / 'training_info.json',
            
            # 层输出目录
            'nn_layers': self.project_path / 'data' / 'inference' / 'nn_layers',
            'spice_layers': self.project_path / 'data' / 'inference' / 'spice_layers',
            'numpy_layers': self.project_path / 'data' / 'inference' / 'numpy_layers',
            
            # 误差分析目录
            'nn_spice_errors': self.project_path / 'data' / 'inference' / 'nn_spice_error_layers',
            'nn_numpy_errors': self.project_path / 'data' / 'inference' / 'nn_numpy_error_layers',
            
            # 状态目录
            'inference_enabled': self.project_path / 'data' / 'inference_enabled',
            'inference_disabled': self.project_path / 'data' / 'inference_disabled',
        }

# 便利函数
def find_project_paths(project_name: str) -> Optional[Dict[str, Path]]:
    """查找项目路径的便利函数"""
    mapper = ProjectPathMapper(project_name)
    if mapper.discover_project_structure():
        return mapper.get_path_map()
    return None

def validate_project_paths(project_name: str) -> Tuple[bool, List[str]]:
    """验证项目路径的便利函数"""
    mapper = ProjectPathMapper(project_name)
    if not mapper.discover_project_structure():
        return False, ["无法发现项目结构"]
    
    path_map = mapper.get_path_map()
    issues = []
    
    # 检查关键路径
    critical_paths = ['config', 'data_dir', 'inference_dir']
    for key in critical_paths:
        if key in path_map and not path_map[key].exists():
            issues.append(f"关键路径不存在: {path_map[key]}")
    
    return len(issues) == 0, issues
```

#### A2. `core/path_checker.py` - 路径预检查系统 🔍

**全新模块，执行前完整验证**

```python
"""
路径检查器 - 运行前完整验证所有必需路径和JSON文件
基于WNET5q1h2u6l3项目需求设计
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ..utils import get_logger
from ..utils.path_finder import ProjectPathMapper

logger = get_logger(__name__)

class CheckSeverity(Enum):
    """检查严重性等级"""
    CRITICAL = "critical"    # 阻断执行
    WARNING = "warning"      # 警告但可继续
    INFO = "info"           # 信息提示

@dataclass
class PathCheckResult:
    """路径检查结果"""
    path: Path
    exists: bool
    readable: bool
    writable: bool
    size_bytes: Optional[int]
    severity: CheckSeverity
    message: str
    json_valid: Optional[bool] = None
    json_content: Optional[Dict] = None

class PathChecker:
    """路径检查器 - 基于WNET5q1h2u6l3优化"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.mapper = ProjectPathMapper(project_name)
        self.check_results: List[PathCheckResult] = []
        
    def run_full_check(self) -> Tuple[bool, Dict[str, Any]]:
        """运行完整的路径检查"""
        logger.info(f"开始完整路径检查: {self.project_name}")
        
        # 1. 发现项目结构
        if not self.mapper.discover_project_structure():
            return False, {
                "success": False,
                "error": "无法发现项目结构",
                "results": []
            }
        
        # 2. 获取路径映射
        try:
            path_map = self.mapper.get_path_map()
        except Exception as e:
            return False, {
                "success": False, 
                "error": f"获取路径映射失败: {e}",
                "results": []
            }
        
        # 3. 执行分层检查
        self._check_critical_paths(path_map)
        self._check_configuration_files(path_map)
        self._check_data_files(path_map)
        self._check_inference_structure(path_map)
        
        # 4. 分析结果
        success, summary = self._analyze_results()
        
        return success, {
            "success": success,
            "summary": summary,
            "results": [self._result_to_dict(r) for r in self.check_results],
            "project_path": str(self.mapper.project_path),
            "path_map": {k: str(v) for k, v in path_map.items()}
        }
    
    def _check_critical_paths(self, path_map: Dict[str, Path]):
        """检查关键路径 - P0级别"""
        critical_paths = [
            ('project_path', CheckSeverity.CRITICAL, "项目根目录"),
            ('config', CheckSeverity.CRITICAL, "主配置文件"),
            ('data_dir', CheckSeverity.CRITICAL, "数据目录"),
            ('inference_dir', CheckSeverity.WARNING, "推理目录")
        ]
        
        for key, severity, description in critical_paths:
            if key in path_map:
                result = self._check_single_path(
                    path_map[key], severity, description
                )
                self.check_results.append(result)
    
    def _check_configuration_files(self, path_map: Dict[str, Path]):
        """检查配置文件"""
        config_files = [
            ('config', CheckSeverity.CRITICAL, "主配置文件"),
            ('config_baseline', CheckSeverity.INFO, "基线配置"),
            ('config_with_bias', CheckSeverity.INFO, "偏置补偿配置")
        ]
        
        for key, severity, description in config_files:
            if key in path_map:
                result = self._check_json_file(
                    path_map[key], severity, description
                )
                self.check_results.append(result)
    
    def _check_data_files(self, path_map: Dict[str, Path]):
        """检查数据文件"""
        data_files = [
            ('error_analysis', CheckSeverity.CRITICAL, "错误分析数据"),
            ('inference_metadata', CheckSeverity.WARNING, "推理元数据"),
            ('model_info', CheckSeverity.WARNING, "模型信息"),
            ('training_info', CheckSeverity.INFO, "训练信息")
        ]
        
        for key, severity, description in data_files:
            if key in path_map:
                result = self._check_json_file(
                    path_map[key], severity, description
                )
                self.check_results.append(result)
    
    def _check_inference_structure(self, path_map: Dict[str, Path]):
        """检查推理结构目录"""
        inference_dirs = [
            ('nn_layers', CheckSeverity.WARNING, "神经网络层输出"),
            ('spice_layers', CheckSeverity.WARNING, "SPICE层输出"),
            ('numpy_layers', CheckSeverity.INFO, "NumPy层输出"),
            ('nn_spice_errors', CheckSeverity.INFO, "NN-SPICE误差"),
            ('nn_numpy_errors', CheckSeverity.INFO, "NN-NumPy误差")
        ]
        
        for key, severity, description in inference_dirs:
            if key in path_map:
                result = self._check_single_path(
                    path_map[key], severity, description
                )
                self.check_results.append(result)
    
    def _check_single_path(self, path: Path, severity: CheckSeverity, 
                          description: str) -> PathCheckResult:
        """检查单个路径"""
        exists = path.exists()
        readable = exists and os.access(path, os.R_OK)
        writable = exists and os.access(path, os.W_OK)
        size_bytes = path.stat().st_size if exists else None
        
        if not exists:
            message = f"{description} 不存在"
        elif not readable:
            message = f"{description} 无读取权限"
        elif path.is_dir() and not writable:
            message = f"{description} 无写入权限"
        else:
            message = f"{description} 正常"
        
        return PathCheckResult(
            path=path,
            exists=exists,
            readable=readable,
            writable=writable,
            size_bytes=size_bytes,
            severity=severity,
            message=message
        )
    
    def _check_json_file(self, path: Path, severity: CheckSeverity,
                        description: str) -> PathCheckResult:
        """检查JSON文件"""
        basic_result = self._check_single_path(path, severity, description)
        
        if basic_result.exists and basic_result.readable:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                basic_result.json_valid = True
                basic_result.json_content = content
                
                # 针对不同文件类型的特殊检查
                if path.name == 'config.json':
                    if 'use_model' not in content:
                        basic_result.message += " (缺少use_model配置)"
                        basic_result.severity = CheckSeverity.WARNING
                
                elif path.name == 'error_analysis.json':
                    # 检查错误分析数据的完整性
                    if 'bias_analysis' in content or 'nn_spice_bias' in content:
                        basic_result.message += " (包含偏置分析数据)"
                    else:
                        basic_result.message += " (缺少偏置分析数据)"
                        basic_result.severity = CheckSeverity.WARNING
                
            except json.JSONDecodeError as e:
                basic_result.json_valid = False
                basic_result.message += f" (JSON格式错误: {e})"
                basic_result.severity = CheckSeverity.CRITICAL
            except Exception as e:
                basic_result.json_valid = False
                basic_result.message += f" (读取错误: {e})"
                basic_result.severity = CheckSeverity.WARNING
        else:
            basic_result.json_valid = False
        
        return basic_result
    
    def _analyze_results(self) -> Tuple[bool, Dict[str, Any]]:
        """分析检查结果"""
        critical_issues = [r for r in self.check_results 
                          if r.severity == CheckSeverity.CRITICAL and not r.exists]
        warning_issues = [r for r in self.check_results 
                         if r.severity == CheckSeverity.WARNING and not r.exists]
        
        success = len(critical_issues) == 0
        
        summary = {
            "total_checks": len(self.check_results),
            "critical_issues": len(critical_issues),
            "warning_issues": len(warning_issues),
            "success_rate": len([r for r in self.check_results if r.exists]) / len(self.check_results),
            "critical_issue_details": [r.message for r in critical_issues],
            "warning_issue_details": [r.message for r in warning_issues]
        }
        
        return success, summary
    
    def _result_to_dict(self, result: PathCheckResult) -> Dict[str, Any]:
        """将检查结果转换为字典"""
        return {
            "path": str(result.path),
            "exists": result.exists,
            "readable": result.readable,
            "writable": result.writable,
            "size_bytes": result.size_bytes,
            "severity": result.severity.value,
            "message": result.message,
            "json_valid": result.json_valid,
            "json_keys": list(result.json_content.keys()) if result.json_content else None
        }

# 便利函数
def check_project_paths(project_name: str) -> Tuple[bool, Dict[str, Any]]:
    """检查项目路径的便利函数"""
    checker = PathChecker(project_name)
    return checker.run_full_check()

def quick_path_check(project_name: str) -> bool:
    """快速路径检查"""
    checker = PathChecker(project_name)
    success, _ = checker.run_full_check()
    return success
```

#### A3. `core/executor.py` - 执行器路径集成 🚀

**关键修改点：集成路径检查**

```python
# 在run_inference和run_analysis方法开始前添加路径检查

def run_inference(self, project_name: str, timeout: Optional[int] = None,
                 monitor_progress: bool = True) -> Tuple[bool, str]:
    """运行推理，先进行路径检查"""
    
    # 预检查路径
    logger.info(f"开始路径预检查: {project_name}")
    success, check_result = check_project_paths(project_name)
    
    if not success:
        error_msg = f"路径检查失败: {check_result['summary']['critical_issue_details']}"
        logger.error(error_msg)
        return False, error_msg
    
    logger.info(f"路径检查通过，成功率: {check_result['summary']['success_rate']:.1%}")
    
    # 继续原有逻辑...
    if timeout is None:
        timeout = EXECUTION_CONFIG["inference_timeout"]
    
    if is_mock_mode():
        return self._mock_inference(project_name)
    else:
        return self._real_inference(project_name, timeout, monitor_progress)

def run_analysis(self, project_name: str, timeout: Optional[int] = None) -> Tuple[bool, str]:
    """运行分析，先进行路径检查"""
    
    # 预检查路径，重点检查error_analysis.json
    logger.info(f"开始分析路径预检查: {project_name}")
    success, check_result = check_project_paths(project_name)
    
    if not success:
        error_msg = f"分析路径检查失败: {check_result['summary']['critical_issue_details']}"
        logger.error(error_msg)
        return False, error_msg
    
    # 特别检查error_analysis.json
    path_map = check_result.get('path_map', {})
    error_analysis_path = path_map.get('error_analysis')
    if not error_analysis_path or not Path(error_analysis_path).exists():
        error_msg = f"缺少关键文件 error_analysis.json: {error_analysis_path}"
        logger.error(error_msg)
        return False, error_msg
    
    logger.info(f"分析路径检查通过")
    
    # 继续原有逻辑...
    if timeout is None:
        timeout = EXECUTION_CONFIG["analysis_timeout"]
    
    if is_mock_mode():
        return self._mock_analysis(project_name)
    else:
        return self._real_analysis(project_name, timeout)
```

#### A4. `bias_tuner_cli.py` - 命令行工具路径集成 🖥️

**新增命令行工具，集成pathcheck功能**

```python
#!/usr/bin/env python
"""
偏置调谐器命令行工具
重点：路径检查优先 + 基于WNET5q1h2u6l3优化
"""

import argparse
import sys
from pathlib import Path

from bias_tuner import BiasTuner, CompensationStrategy
from bias_tuner.core.path_checker import check_project_paths
from bias_tuner.utils.path_finder import find_project_paths

def main():
    parser = argparse.ArgumentParser(
        description='SPICE偏置补偿自动调谐器 (基于WNET5q1h2u6l3优化)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s WNET5q1h2u6l3 --check-only          # 仅进行路径检查
  %(prog)s WNET5q1h2u6l3 --strategy same_phase  # 同相补偿策略
  %(prog)s WNET5q1h2u6l3 --layers 1,2,3         # 指定补偿层
        """
    )
    
    # 基础参数
    parser.add_argument('project_name', help='项目名称 (如: WNET5q1h2u6l3)')
    
    # 路径相关
    parser.add_argument('--check-only', action='store_true', 
                       help='仅进行路径检查，不执行调优')
    parser.add_argument('--force-check', action='store_true',
                       help='即使路径检查有警告也继续执行')
    parser.add_argument('--show-paths', action='store_true',
                       help='显示完整路径映射表')
    
    # 调优参数
    parser.add_argument('--strategy', 
                       choices=['same_phase', 'scaled', 'adaptive', 'conservative'],
                       default='same_phase', help='补偿策略 (默认: same_phase)')
    parser.add_argument('--layers', help='指定要补偿的层，逗号分隔 (如: 1,2,3)')
    parser.add_argument('--target-error', type=float, default=0.001, 
                       help='目标误差 (默认: 0.001)')
    parser.add_argument('--max-iterations', type=int, default=5,
                       help='最大迭代次数 (默认: 5)')
    
    # 执行模式
    parser.add_argument('--dry-run', action='store_true',
                       help='模拟运行，不执行实际命令')
    parser.add_argument('--mock', action='store_true', 
                       help='启用Mock模式用于测试')
    parser.add_argument('--python-env', default='python',
                       help='Python环境命令 (默认: python)')
    
    # 输出控制
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='静默模式')
    
    args = parser.parse_args()
    
    # 配置日志
    import logging
    level = logging.DEBUG if args.verbose else logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
    
    logger = logging.getLogger(__name__)
    
    print(f"🔍 偏置调谐器 - 路径检查优先版")
    print(f"📁 目标项目: {args.project_name}")
    print("="*60)
    
    # 1. 路径检查
    print("1️⃣  执行路径检查...")
    success, check_result = check_project_paths(args.project_name)
    
    if not success:
        print("❌ 路径检查失败:")
        for issue in check_result['summary']['critical_issue_details']:
            print(f"   🔴 {issue}")
        
        if not args.force_check:
            print("\n💡 使用 --force-check 强制继续执行")
            sys.exit(1)
        else:
            print("\n⚠️  强制继续执行...")
    else:
        print(f"✅ 路径检查通过 (成功率: {check_result['summary']['success_rate']:.1%})")
    
    # 显示警告
    if check_result['summary']['warning_issues'] > 0:
        print(f"\n⚠️  发现 {check_result['summary']['warning_issues']} 个警告:")
        for warning in check_result['summary']['warning_issue_details']:
            print(f"   🟡 {warning}")
    
    # 显示路径映射
    if args.show_paths:
        print("\n📋 路径映射表:")
        for key, path in check_result['path_map'].items():
            exists = "✅" if Path(path).exists() else "❌"
            print(f"   {exists} {key}: {path}")
    
    # 仅检查模式
    if args.check_only:
        print(f"\n🎯 路径检查完成，项目路径: {check_result['project_path']}")
        sys.exit(0 if success else 1)
    
    # 2. 创建调谐器
    print("\n2️⃣  初始化偏置调谐器...")
    
    # 配置Mock模式
    if args.mock:
        from bias_tuner.core import set_mock_mode
        test_resources = Path(__file__).parent / "test_resources"
        set_mock_mode(True, test_resources)
        print("🧪 Mock模式已启用")
    
    # 获取项目路径
    project_path = Path(check_result['project_path'])
    strategy = CompensationStrategy(args.strategy)
    
    tuner = BiasTuner(
        project_path=project_path,
        strategy=strategy,
        python_env=args.python_env,
        dry_run=args.dry_run
    )
    
    print(f"✅ 调谐器已初始化 (策略: {args.strategy})")
    
    try:
        # 3. 执行调优流程
        print("\n3️⃣  执行偏置补偿调优...")
        
        # 基线测量
        print("📊 执行基线测量...")
        baseline = tuner.run_baseline_measurement()
        print(f"✅ 基线测量完成")
        
        # 确定补偿层
        if args.layers:
            layer_order = [int(x.strip()) for x in args.layers.split(',')]
            print(f"🎯 指定补偿层: {layer_order}")
        else:
            # 按误差大小排序
            worst_layers = tuner.analyzer.get_worst_layers()
            layer_order = [layer_idx for layer_idx, _ in worst_layers[:3]]
            print(f"🎯 自动选择补偿层: {layer_order}")
        
        # 顺序补偿
        print(f"🔧 开始层序补偿...")
        results = tuner.tune_sequential(layer_order)
        print(f"✅ 层序补偿完成")
        
        # 生成报告
        print("📄 生成调优报告...")
        report_path = tuner.generate_report()
        print(f"✅ 调优报告: {report_path}")
        
        # 显示结果摘要
        summary = tuner._generate_summary()
        if summary:
            print("\n🎉 调优结果摘要:")
            print(f"   📈 总体改善: {summary.get('overall_improvement', 0):.1f}%")
            for layer_idx, improvement in summary.get('layer_improvements', {}).items():
                print(f"   🔹 层 {layer_idx}: {improvement['improvement_percent']:.1f}% "
                      f"({improvement['before']:.6f} → {improvement['after']:.6f})")
        
        print(f"\n🎯 偏置补偿调优成功完成！")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 调优过程出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
```

### B. 配置增强

#### B1. `config/defaults.py` - 路径配置优化

```python
# 基于WNET5q1h2u6l3的路径配置
PATH_CONFIG = {
    "project_discovery": {
        "root_markers": ["cli.py", "projects", "config.py", "metnl.py"],
        "project_indicators": ["config.json", "data/"],
        "search_depth": 10,
        "fuzzy_match": True,
        "case_sensitive": False
    },
    "required_files": {
        "critical": ["config.json"],
        "important": ["data/inference/error_analysis.json"],
        "optional": ["data/inference/inference_metadata.json"]
    },
    "directory_structure": {
        "create_missing": ["data", "data/inference"],
        "check_writable": ["data", "data/inference"],
        "backup_dirs": ["backups", "data/backups"]
    },
    "json_validation": {
        "config_required_fields": ["use_model", "dataset_type"],
        "error_analysis_required_fields": ["bias_analysis", "nn_spice_bias"],
        "encoding": "utf-8"
    }
}
```

## 部署计划 (路径重点版)

### 🎯 实施优先级

| 阶段 | 重点内容 | 预计时间 | 成功标准 |
|------|----------|----------|----------|
| **P1** | 路径映射系统 | 1.5小时 | WNET5q1h2u6l3项目100%路径发现 |
| **P2** | 路径检查器 | 1小时 | 所有JSON文件预检查通过 |
| **P3** | 执行器集成 | 45分钟 | 预检查集成到推理/分析流程 |
| **P4** | 命令行工具 | 30分钟 | 完整的路径检查CLI |

### 🧪 测试验证计划

#### 阶段1: WNET5q1h2u6l3项目验证
```bash
# 1. 路径发现测试
python -c "
from bias_tuner.utils.path_finder import find_project_paths
paths = find_project_paths('WNET5q1h2u6l3')
print('✅ 路径发现成功' if paths else '❌ 路径发现失败')
"

# 2. 路径检查测试
python -c "
from bias_tuner.core.path_checker import check_project_paths
success, result = check_project_paths('WNET5q1h2u6l3')
print(f'检查结果: {success}, 成功率: {result[\"summary\"][\"success_rate\"]:.1%}')
"

# 3. 完整流程测试
python bias_tuner_cli.py WNET5q1h2u6l3 --check-only --show-paths
```

#### 阶段2: 容错性测试
- 测试缺失文件情况
- 测试权限问题处理
- 测试JSON格式错误处理
- 测试项目路径变化处理

### 🎪 成功标准

#### 功能标准
- ✅ **WNET5q1h2u6l3项目100%路径发现**: 所有关键路径自动识别
- ✅ **JSON文件完整预检查**: 运行前验证所有配置和数据文件
- ✅ **智能容错处理**: 缺失文件自动创建，权限问题提醒
- ✅ **路径映射表**: 完整的路径可视化和管理

#### 性能标准
- ✅ **路径检查速度 < 5秒**: 包含所有JSON文件验证
- ✅ **内存占用 < 100MB**: 路径系统轻量化设计
- ✅ **兼容性100%**: 支持不同操作系统路径格式

#### 可靠性标准
- ✅ **路径发现成功率 > 95%**: 各种项目结构下的适应性
- ✅ **错误诊断准确率100%**: 精确定位路径和文件问题
- ✅ **恢复能力**: 自动创建缺失目录，智能修复路径问题

## 结论

通过**以WNET5q1h2u6l3为重点的路径系统重新设计**，偏置调谐器将具备：

1. **🔍 智能路径发现**: 基于真实项目结构优化的自动发现算法
2. **✅ 完整预检查**: 运行前验证所有关键JSON文件的存在性和有效性  
3. **🛡️ 强健容错机制**: 智能处理缺失文件、权限问题、格式错误
4. **📊 路径可视化**: 完整的路径映射表和状态监控

**预计4小时完成，将显著提升系统可靠性和用户体验**。