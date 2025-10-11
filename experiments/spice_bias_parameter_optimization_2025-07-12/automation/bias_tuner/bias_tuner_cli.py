#!/usr/bin/env python3
"""
独立的偏置微调器CLI工具

解决相对导入问题，提供直接可执行的微调接口
按照automated_tuner_issues.md中的短期修复方案实现
"""

import sys
import os
from pathlib import Path
import importlib.util

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def import_module_from_file(module_name, file_path):
    """动态导入模块，避免相对导入问题"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def load_bias_tuner_modules():
    """加载微调器相关模块 - 使用简化实现避免相对导入"""
    try:
        # 尝试简单的sys.path导入
        import sys
        sys.path.insert(0, str(current_dir))
        sys.path.insert(0, str(current_dir / "core"))
        sys.path.insert(0, str(current_dir / "utils"))
        sys.path.insert(0, str(current_dir / "config"))
        
        # 直接导入 - 避免使用有相对导入的模块
        return create_standalone_modules()
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        print(f"❌ 详细错误: {str(e)}")
        return None

def create_standalone_modules():
    """创建独立的模块实现，避免相对导入问题"""
    from enum import Enum
    import json
    import subprocess
    import time
    from datetime import datetime
    import logging
    
    # 补偿策略枚举
    class CompensationStrategy(Enum):
        SAME_PHASE = "same_phase"
        SCALED = "scaled"
        ADAPTIVE = "adaptive"
        CONSERVATIVE = "conservative"
    
    # 简化的偏置补偿器
    class SimpleBiasCompensator:
        def __init__(self, strategy=CompensationStrategy.SAME_PHASE):
            self.strategy = strategy
        
        def calculate_compensation(self, layer_stats, scale_factor=1.0):
            """计算补偿值 - 支持多通道"""
            
            # 检查是否有通道级别的偏置数据
            if 'channel_bias_errors' in layer_stats:
                # 多通道补偿
                bias_errors = layer_stats['channel_bias_errors']
                compensations = []
                
                for bias_error in bias_errors:
                    if self.strategy == CompensationStrategy.SAME_PHASE:
                        comp = -bias_error * scale_factor
                    elif self.strategy == CompensationStrategy.SCALED:
                        comp = -bias_error * scale_factor * 0.8
                    elif self.strategy == CompensationStrategy.CONSERVATIVE:
                        comp = -bias_error * scale_factor * 0.5
                    else:
                        comp = -bias_error * scale_factor
                    compensations.append(comp)
                
                return compensations
            else:
                # 单个值补偿（向后兼容）
                mean_error = layer_stats.get('mean_error', 0)
                
                if self.strategy == CompensationStrategy.SAME_PHASE:
                    return -mean_error * scale_factor
                elif self.strategy == CompensationStrategy.SCALED:
                    return -mean_error * scale_factor * 0.8
                elif self.strategy == CompensationStrategy.CONSERVATIVE:
                    return -mean_error * scale_factor * 0.5
                else:
                    return -mean_error * scale_factor
    
    # 简化的分析器
    class SimpleBiasAnalyzer:
        def extract_layer_statistics(self, analysis_data):
            """提取层统计信息 - 包含通道级别偏置数据"""
            stats = {}
            
            # 尝试从nn_spice_analysis中提取
            nn_spice_analysis = analysis_data.get('nn_spice_analysis', {})
            layer_analysis = nn_spice_analysis.get('layer_analysis', [])
            
            for layer_data in layer_analysis:
                if isinstance(layer_data, dict):
                    layer_idx = layer_data.get('layer_index')
                    if layer_idx is not None:
                        stats[str(layer_idx)] = {
                            'mean_error': layer_data.get('mean_error', 0),
                            'abs_mean': abs(layer_data.get('mean_error', 0)),
                            'rms_error': layer_data.get('rms_error', 0),
                            'max_error': layer_data.get('max_error', 0),
                            'std_error': layer_data.get('std_error', 0)
                        }
            
            # 提取通道级别的偏置误差数据
            bias_analysis = analysis_data.get('bias_analysis', {})
            nn_spice_bias = bias_analysis.get('nn_spice_bias', {})
            layer_results = nn_spice_bias.get('layer_results', [])
            
            for layer_result in layer_results:
                if isinstance(layer_result, dict):
                    layer_info = layer_result.get('layer_info', {})
                    layer_idx = layer_info.get('layer')
                    if layer_idx is not None:
                        layer_str = str(layer_idx)
                        
                        # 提取每个通道的偏置误差
                        bias_errors = layer_result.get('bias_errors', [])
                        channel_bias_errors = [bias_err.get('bias_error', 0) for bias_err in bias_errors]
                        
                        # 如果已有该层的统计信息，添加通道偏置数据
                        if layer_str in stats:
                            stats[layer_str]['channel_bias_errors'] = channel_bias_errors
                            stats[layer_str]['channel_count'] = len(channel_bias_errors)
                        else:
                            # 创建新的统计信息
                            summary = layer_result.get('summary', {})
                            stats[layer_str] = {
                                'mean_error': summary.get('mean_bias_error', 0),
                                'abs_mean': abs(summary.get('mean_bias_error', 0)),
                                'rms_error': 0,  # 没有对应数据
                                'max_error': summary.get('max_bias_error', 0),
                                'std_error': summary.get('std_bias_error', 0),
                                'channel_bias_errors': channel_bias_errors,
                                'channel_count': len(channel_bias_errors)
                            }
            
            # 备用：尝试旧格式
            if not stats:
                layer_errors = analysis_data.get('layer_errors', {})
                for layer_str, errors in layer_errors.items():
                    if isinstance(errors, dict):
                        stats[layer_str] = {
                            'mean_error': errors.get('mean_error', 0),
                            'abs_mean': abs(errors.get('mean_error', 0)),
                            'rms_error': errors.get('rms_error', 0),
                            'max_error': errors.get('max_error', 0)
                        }
            
            return stats
        
        def get_timestamp(self):
            return datetime.now().isoformat()
    
    # 简化的执行器
    class SimpleCommandExecutor:
        def __init__(self, python_env="python", dry_run=False):
            self.python_env = python_env
            self.dry_run = dry_run
        
        def execute_command(self, cmd, timeout=600):
            """执行命令"""
            if self.dry_run:
                return {"success": True, "output": "Dry run mode", "error": None}
            
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, 
                    timeout=timeout, cwd="/mnt/f/Work/met_nonlinear_worktrees/met_nonlinear_master"
                )
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None
                }
            except subprocess.TimeoutExpired:
                return {"success": False, "output": "", "error": "Command timeout"}
            except Exception as e:
                return {"success": False, "output": "", "error": str(e)}
    
    # 简化的配置管理器
    class SimpleConfigManager:
        def __init__(self, project_path):
            self.project_path = project_path
            self.config_path = project_path / "config.json"
        
        def get_current_config(self):
            """获取当前配置"""
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        
        def update_layer_compensation(self, layer_idx, compensation_values):
            """更新层补偿配置
            
            Args:
                layer_idx: 层索引
                compensation_values: 补偿值列表，每个通道一个值
            """
            config = self.get_current_config()
            
            # 确保结构存在
            if "inference_config" not in config:
                config["inference_config"] = {}
            if "bias_compensation" not in config["inference_config"]:
                config["inference_config"]["bias_compensation"] = {}
            if "layer_bias_adjustments" not in config["inference_config"]["bias_compensation"]:
                config["inference_config"]["bias_compensation"]["layer_bias_adjustments"] = {}
            
            # 更新补偿值 - 确保是列表格式
            if isinstance(compensation_values, (list, tuple)):
                config["inference_config"]["bias_compensation"]["layer_bias_adjustments"][str(layer_idx)] = list(compensation_values)
            else:
                # 单个值转为列表
                config["inference_config"]["bias_compensation"]["layer_bias_adjustments"][str(layer_idx)] = [compensation_values]
            
            # 保存配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
    
    # 简单的日志函数
    def simple_get_logger(name):
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    # 简单的JSON写入函数
    def simple_write_json(file_path, data):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # 返回模块字典
    return {
        'CompensationStrategy': CompensationStrategy,
        'BiasCompensator': SimpleBiasCompensator,
        'BiasAnalyzer': SimpleBiasAnalyzer,
        'CommandExecutor': SimpleCommandExecutor,
        'ConfigManager': SimpleConfigManager,
        'get_logger': simple_get_logger,
        'write_json': simple_write_json,
        'NETWORK_CONFIG': {"default_layers": 5, "default_channels": 6},
        'EXECUTION_CONFIG': {"inference_timeout": 600, "analysis_timeout": 300},
        'TUNING_CONFIG': {"default_scale_factor": 0.8, "layer_delay": 2.0},
    }

class SimpleBiasTuner:
    """简化的偏置微调器 - 避免复杂的相对导入"""
    
    def __init__(self, project_path, strategy="SAME_PHASE", python_env=None, dry_run=False):
        self.project_path = Path(project_path)
        self.strategy = strategy
        self.python_env = python_env or "conda run --no-capture-output -n tf26 python"
        self.dry_run = dry_run
        
        # 加载模块
        modules = load_bias_tuner_modules()
        if modules is None:
            raise ImportError("无法加载必需的微调器模块")
        
        self.modules = modules
        self.logger = modules['get_logger']('simple_bias_tuner')
        
        # 初始化组件
        self.config_manager = modules['ConfigManager'](self.project_path)
        self.executor = modules['CommandExecutor'](
            python_env=self.python_env,
            dry_run=self.dry_run
        )
        self.analyzer = modules['BiasAnalyzer']()
        self.compensator = modules['BiasCompensator'](
            strategy=getattr(modules['CompensationStrategy'], strategy)
        )
        
        self.tuning_history = []
        
    def run_baseline_measurement(self):
        """执行基线测量"""
        self.logger.info("📊 开始基线测量...")
        
        try:
            # 执行推理分析
            cmd = f"{self.python_env} cli.py -a {self.project_path.name}"
            result = self.executor.execute_command(cmd, timeout=600)
            
            if not result['success']:
                raise Exception(f"基线测量执行失败: {result['error']}")
            
            # 分析错误数据
            error_analysis_path = self.project_path / "data" / "inference" / "error_analysis.json"
            
            if not error_analysis_path.exists():
                raise Exception(f"错误分析文件不存在: {error_analysis_path}")
            
            # 读取分析结果
            with open(error_analysis_path, 'r', encoding='utf-8') as f:
                import json
                analysis_data = json.load(f)
            
            # 提取统计信息
            baseline_stats = self.analyzer.extract_layer_statistics(analysis_data)
            
            baseline_result = {
                'timestamp': self.analyzer.get_timestamp(),
                'type': 'baseline',
                'statistics': baseline_stats,
                'analysis_data': analysis_data
            }
            
            self.tuning_history.append(baseline_result)
            
            self.logger.info(f"✅ 基线测量完成，覆盖 {len(baseline_stats)} 层")
            return baseline_result
            
        except Exception as e:
            self.logger.error(f"❌ 基线测量失败: {e}")
            raise
    
    def tune_single_layer(self, layer_idx, scale_factor=0.8):
        """真正的单层微调 - 包含完整的-i和-a循环"""
        self.logger.info(f"🔄 开始真正微调 Layer {layer_idx}，补偿系数: {scale_factor}")
        
        try:
            # 获取当前配置
            current_config = self.config_manager.get_current_config()
            
            # 获取最新的错误分析
            if not self.tuning_history:
                raise Exception("需要先运行基线测量")
            
            latest_analysis = self.tuning_history[-1]
            layer_stats = latest_analysis['statistics'].get(str(layer_idx))
            
            if not layer_stats:
                raise Exception(f"Layer {layer_idx} 统计信息不可用")
            
            # 步骤1: 计算补偿值并更新配置
            compensation = self.compensator.calculate_compensation(
                layer_stats, scale_factor
            )
            self.config_manager.update_layer_compensation(layer_idx, compensation)
            self.logger.info(f"✅ Layer {layer_idx} 配置已更新: {compensation}")
            
            # 步骤2: 重新生成SPICE推理数据 (关键!)
            self.logger.info(f"📊 Layer {layer_idx}: 重新生成SPICE推理数据...")
            import time
            start_time = time.time()
            
            inference_cmd = f"{self.python_env} cli.py -i -f {self.project_path.name}"
            inference_result = self.executor.execute_command(inference_cmd, timeout=600)
            
            inference_duration = time.time() - start_time
            self.logger.info(f"⏱️ Layer {layer_idx} 推理耗时: {inference_duration:.1f}秒")
            
            if not inference_result['success']:
                # 回滚配置
                self._rollback_layer_config(layer_idx)
                raise Exception(f"Layer {layer_idx} 推理失败: {inference_result['error']}")
            
            # 步骤3: 分析新的误差数据
            self.logger.info(f"🔍 Layer {layer_idx}: 分析新的误差数据...")
            analysis_start = time.time()
            
            analysis_cmd = f"{self.python_env} cli.py -a {self.project_path.name}"
            analysis_result = self.executor.execute_command(analysis_cmd, timeout=300)
            
            analysis_duration = time.time() - analysis_start
            self.logger.info(f"⏱️ Layer {layer_idx} 分析耗时: {analysis_duration:.1f}秒")
            
            if not analysis_result['success']:
                # 回滚配置
                self._rollback_layer_config(layer_idx)
                raise Exception(f"Layer {layer_idx} 分析失败: {analysis_result['error']}")
            
            # 步骤4: 验证改善效果
            new_analysis_data = self._load_error_analysis()
            new_stats = self.analyzer.extract_layer_statistics(new_analysis_data)
            
            improvement = self._calculate_layer_improvement(layer_idx, latest_analysis['statistics'], new_stats)
            self.logger.info(f"📈 Layer {layer_idx} 改善效果: {improvement:.1f}%")
            
            total_duration = inference_duration + analysis_duration
            self.logger.info(f"✅ Layer {layer_idx} 微调完成，总耗时: {total_duration:.1f}秒")
            
            tuning_result = {
                'timestamp': self.analyzer.get_timestamp(),
                'type': 'layer_compensation',
                'layer_idx': layer_idx,
                'scale_factor': scale_factor,
                'compensation_applied': compensation,
                'inference_duration': inference_duration,
                'analysis_duration': analysis_duration,
                'total_duration': total_duration,
                'improvement_percent': improvement,
                'statistics': new_stats,
                'analysis_data': new_analysis_data
            }
            
            self.tuning_history.append(tuning_result)
            
            return tuning_result
            
        except Exception as e:
            self.logger.error(f"❌ Layer {layer_idx} 微调失败: {e}")
            raise
    
    def tune_sequential(self, layer_order, scale_factors):
        """真正的序列微调 - 包含完整时间和效果监控"""
        import time
        
        self.logger.info(f"🎯 开始真正的序列微调: {layer_order}")
        self.logger.info(f"⏱️ 预计总耗时: {len(layer_order) * 180}秒 (~{len(layer_order) * 3}分钟)")
        
        start_time = time.time()
        results = []
        total_improvement = 0
        
        for i, layer_idx in enumerate(layer_order):
            self.logger.info(f"📋 进度: {i+1}/{len(layer_order)} - Layer {layer_idx}")
            
            scale_factor = scale_factors.get(layer_idx, 0.8)
            
            try:
                result = self.tune_single_layer(layer_idx, scale_factor)
                results.append(result)
                total_improvement += result['improvement_percent']
                
                # 层间延迟
                if i < len(layer_order) - 1:
                    self.logger.info("⏳ 层间冷却延迟: 5秒...")
                    time.sleep(5.0)
                
            except Exception as e:
                self.logger.error(f"❌ Layer {layer_idx} 序列微调失败: {e}")
                break
        
        total_duration = time.time() - start_time
        avg_improvement = total_improvement / len(results) if results else 0
        
        self.logger.info(f"🏁 序列微调完成:")
        self.logger.info(f"   📊 处理层数: {len(results)}/{len(layer_order)}")
        self.logger.info(f"   ⏱️ 总耗时: {total_duration:.1f}秒 ({total_duration/60:.1f}分钟)")
        self.logger.info(f"   📈 平均改善: {avg_improvement:.1f}%")
        
        return results
    
    def generate_report(self):
        """生成微调报告"""
        if not self.tuning_history:
            self.logger.warning("⚠️  无微调历史，无法生成报告")
            return None
        
        try:
            from datetime import datetime
            
            # 创建报告目录
            reports_dir = current_dir / "reports"
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = reports_dir / f"tuning_report_{self.project_path.name}_{timestamp}.json"
            
            # 生成报告内容
            report_data = {
                "project": self.project_path.name,
                "timestamp": datetime.now().isoformat(),
                "strategy": self.strategy,
                "tuning_history": self.tuning_history,
                "summary": self._generate_summary()
            }
            
            # 保存报告
            self.modules['write_json'](report_path, report_data)
            
            self.logger.info(f"✅ 报告已保存: {report_path}")
            return report_path
            
        except Exception as e:
            self.logger.error(f"❌ 报告生成失败: {e}")
            return None
    
    def _generate_summary(self):
        """生成微调效果总结"""
        if len(self.tuning_history) < 2:
            return {"error": "数据不足，无法生成总结"}
        
        baseline_stats = self.tuning_history[0]["statistics"]
        final_stats = self.tuning_history[-1]["statistics"]
        
        summary = {
            "total_iterations": len(self.tuning_history),
            "layers_tuned": [],
            "layer_improvements": {},
            "overall_improvement": 0
        }
        
        total_improvement = 0
        improved_layers = 0
        
        for layer_idx in [1, 2, 3, 4]:
            layer_str = str(layer_idx)
            if layer_str in baseline_stats and layer_str in final_stats:
                before = baseline_stats[layer_str].get("abs_mean", 0)
                after = final_stats[layer_str].get("abs_mean", 0)
                
                if before > 0:
                    improvement = (before - after) / before * 100
                    summary["layer_improvements"][layer_str] = {
                        "before": before,
                        "after": after,
                        "improvement_percent": improvement
                    }
                    
                    if improvement > 5:  # 认为5%以上才算有意义的改善
                        summary["layers_tuned"].append(layer_idx)
                        total_improvement += improvement
                        improved_layers += 1
        
        if improved_layers > 0:
            summary["overall_improvement"] = total_improvement / improved_layers
        
        return summary
    
    def _calculate_layer_improvement(self, layer_idx, before_stats, after_stats):
        """计算层级改善百分比"""
        layer_str = str(layer_idx)
        
        if layer_str not in before_stats or layer_str not in after_stats:
            return 0.0
        
        before_error = before_stats[layer_str].get('abs_mean', 0)
        after_error = after_stats[layer_str].get('abs_mean', 0)
        
        if before_error > 0:
            improvement = (before_error - after_error) / before_error * 100
            return max(improvement, -100)  # 限制最大恶化为-100%
        
        return 0.0
    
    def _rollback_layer_config(self, layer_idx):
        """回滚层配置到微调前状态"""
        self.logger.warning(f"🔄 回滚 Layer {layer_idx} 配置...")
        try:
            # 从历史中获取上一次成功的配置
            config = self.config_manager.get_current_config()
            
            # 删除当前层的补偿配置
            if ("inference_config" in config and 
                "bias_compensation" in config["inference_config"] and
                "layer_bias_adjustments" in config["inference_config"]["bias_compensation"]):
                
                adjustments = config["inference_config"]["bias_compensation"]["layer_bias_adjustments"]
                if str(layer_idx) in adjustments:
                    del adjustments[str(layer_idx)]
                    
                    # 保存回滚后的配置
                    with open(self.config_manager.config_path, 'w', encoding='utf-8') as f:
                        import json
                        json.dump(config, f, indent=2, ensure_ascii=False)
                    
                    self.logger.info(f"✅ Layer {layer_idx} 配置已回滚")
                    
        except Exception as e:
            self.logger.error(f"❌ 回滚 Layer {layer_idx} 配置失败: {e}")
    
    def _load_error_analysis(self):
        """加载错误分析数据"""
        error_analysis_path = self.project_path / "data" / "inference" / "error_analysis.json"
        
        if not error_analysis_path.exists():
            raise Exception(f"错误分析文件不存在: {error_analysis_path}")
        
        with open(error_analysis_path, 'r', encoding='utf-8') as f:
            import json
            return json.load(f)


def main():
    """CLI主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="简化偏置微调器CLI")
    parser.add_argument("project_name", help="项目名称")
    parser.add_argument("--dry-run", action="store_true", help="干运行模式")
    parser.add_argument("--strategy", default="SAME_PHASE", help="补偿策略")
    
    args = parser.parse_args()
    
    print("🎯 简化偏置微调器启动")
    print("=" * 50)
    
    try:
        # 项目路径
        project_path = Path(f"/mnt/f/Work/met_nonlinear_worktrees/met_nonlinear_master/projects/{args.project_name}")
        
        if not project_path.exists():
            print(f"❌ 项目不存在: {project_path}")
            return 1
        
        print(f"📁 项目路径: {project_path}")
        print(f"🔧 补偿策略: {args.strategy}")
        print(f"🧪 干运行模式: {args.dry_run}")
        print()
        
        # 创建微调器
        tuner = SimpleBiasTuner(
            project_path=project_path,
            strategy=args.strategy,
            dry_run=args.dry_run
        )
        
        # 执行微调流程
        print("📊 Step 1: 基线测量...")
        baseline = tuner.run_baseline_measurement()
        
        print("🔄 Step 2: 序列微调...")
        results = tuner.tune_sequential(
            layer_order=[2, 3, 4],
            scale_factors={2: 0.8, 3: 0.8, 4: 0.8}
        )
        
        print("📋 Step 3: 生成报告...")
        report_path = tuner.generate_report()
        
        print()
        print("🏁 微调完成！")
        if report_path:
            print(f"📋 报告位置: {report_path}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())