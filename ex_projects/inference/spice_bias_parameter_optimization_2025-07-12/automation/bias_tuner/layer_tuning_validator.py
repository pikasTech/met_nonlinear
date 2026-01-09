#!/usr/bin/env python3
"""
Layer-by-Layer Tuning验证工具

验证以下方面：
1. 每层微调是否真正执行了-i和-a命令
2. 配置更新是否在SPICE推理中生效
3. 时间消耗是否符合预期
4. 改善效果是否真实
"""

import time
import json
from pathlib import Path
from datetime import datetime


class LayerTuningValidator:
    """Layer-by-Layer微调验证器"""
    
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.validation_log = []
    
    def validate_execution_time(self, layer_results):
        """验证执行时间合理性"""
        expected_min_time = 120  # 每层最少2分钟
        expected_max_time = 300  # 每层最多5分钟
        
        validation_result = {
            'timestamp': datetime.now().isoformat(),
            'test_type': 'execution_time_validation',
            'results': [],
            'overall_valid': True
        }
        
        for result in layer_results:
            layer_idx = result['layer_idx']
            total_time = result['total_duration']
            inference_time = result.get('inference_duration', 0)
            analysis_time = result.get('analysis_duration', 0)
            
            layer_validation = {
                'layer_idx': layer_idx,
                'total_duration': total_time,
                'inference_duration': inference_time,
                'analysis_duration': analysis_time,
                'valid': True,
                'issues': []
            }
            
            # 验证总时间
            if total_time < expected_min_time:
                layer_validation['valid'] = False
                layer_validation['issues'].append(
                    f"执行时间过短: {total_time:.1f}秒 < {expected_min_time}秒 (可能为假微调)"
                )
                validation_result['overall_valid'] = False
            
            if total_time > expected_max_time:
                layer_validation['issues'].append(
                    f"执行时间过长: {total_time:.1f}秒 > {expected_max_time}秒 (可能存在异常)"
                )
            
            # 验证推理时间占比
            if inference_time > 0 and inference_time < 60:
                layer_validation['issues'].append(
                    f"推理时间过短: {inference_time:.1f}秒 < 60秒 (可能未真正执行-i命令)"
                )
            
            # 验证分析时间占比
            if analysis_time > 0 and analysis_time < 15:
                layer_validation['issues'].append(
                    f"分析时间过短: {analysis_time:.1f}秒 < 15秒 (可能未真正执行-a命令)"
                )
            
            validation_result['results'].append(layer_validation)
        
        self.validation_log.append(validation_result)
        return validation_result
    
    def validate_config_effectiveness(self, layer_idx, compensation_values):
        """验证配置更新是否在SPICE中生效"""
        validation_result = {
            'timestamp': datetime.now().isoformat(),
            'test_type': 'config_effectiveness_validation',
            'layer_idx': layer_idx,
            'compensation_values': compensation_values,
            'valid': True,
            'issues': []
        }
        
        try:
            # 检查配置文件
            config_path = self.project_path / "config.json"
            if not config_path.exists():
                validation_result['valid'] = False
                validation_result['issues'].append("配置文件不存在")
                return validation_result
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 验证配置结构
            bias_config = (config.get('inference_config', {})
                          .get('bias_compensation', {})
                          .get('layer_bias_adjustments', {}))
            
            layer_str = str(layer_idx)
            if layer_str not in bias_config:
                validation_result['valid'] = False
                validation_result['issues'].append(f"Layer {layer_idx} 补偿配置未找到")
                return validation_result
            
            # 验证补偿值匹配
            config_values = bias_config[layer_str]
            if not isinstance(config_values, list):
                validation_result['valid'] = False
                validation_result['issues'].append(f"Layer {layer_idx} 补偿值格式错误 (非列表)")
                return validation_result
            
            if len(config_values) != len(compensation_values):
                validation_result['valid'] = False
                validation_result['issues'].append(
                    f"Layer {layer_idx} 补偿值数量不匹配: "
                    f"期望{len(compensation_values)}个，实际{len(config_values)}个"
                )
            
            # 检查SPICE模型文件是否更新
            spice_file = Path(f"/mnt/f/Work/met_nonlinear_worktrees/met_nonlinear_master/temp/spice_output/WaveNet5_spice_model_layer{layer_idx}.cir")
            if spice_file.exists():
                # 检查文件修改时间是否最近（5分钟内）
                file_mtime = spice_file.stat().st_mtime
                current_time = time.time()
                if (current_time - file_mtime) > 300:  # 5分钟
                    validation_result['issues'].append(
                        f"SPICE模型文件可能未更新 (修改时间: {datetime.fromtimestamp(file_mtime)})"
                    )
            else:
                validation_result['issues'].append(f"SPICE模型文件不存在: {spice_file}")
                
        except Exception as e:
            validation_result['valid'] = False
            validation_result['issues'].append(f"配置验证异常: {e}")
        
        self.validation_log.append(validation_result)
        return validation_result
    
    def validate_improvement_authenticity(self, before_stats, after_stats, expected_layers):
        """验证改善效果是否真实"""
        validation_result = {
            'timestamp': datetime.now().isoformat(),
            'test_type': 'improvement_authenticity_validation',
            'results': [],
            'overall_valid': True
        }
        
        for layer_idx in expected_layers:
            layer_str = str(layer_idx)
            
            layer_validation = {
                'layer_idx': layer_idx,
                'valid': True,
                'issues': [],
                'improvement_percent': 0
            }
            
            if layer_str not in before_stats:
                layer_validation['valid'] = False
                layer_validation['issues'].append(f"Layer {layer_idx} 基线统计缺失")
                validation_result['overall_valid'] = False
                continue
            
            if layer_str not in after_stats:
                layer_validation['valid'] = False
                layer_validation['issues'].append(f"Layer {layer_idx} 微调后统计缺失")
                validation_result['overall_valid'] = False
                continue
            
            before_error = before_stats[layer_str].get('abs_mean', 0)
            after_error = after_stats[layer_str].get('abs_mean', 0)
            
            if before_error > 0:
                improvement = (before_error - after_error) / before_error * 100
                layer_validation['improvement_percent'] = improvement
                
                # 验证改善的合理性
                if improvement < -50:  # 恶化超过50%
                    layer_validation['issues'].append(
                        f"改善效果异常恶化: {improvement:.1f}% (可能存在问题)"
                    )
                elif improvement > 90:  # 改善超过90%
                    layer_validation['issues'].append(
                        f"改善效果异常理想: {improvement:.1f}% (可能为虚假改善)"
                    )
                elif abs(improvement) < 1:  # 改善小于1%
                    layer_validation['issues'].append(
                        f"改善效果微小: {improvement:.1f}% (微调可能无效)"
                    )
            else:
                layer_validation['valid'] = False
                layer_validation['issues'].append(f"Layer {layer_idx} 基线误差为0 (数据异常)")
                validation_result['overall_valid'] = False
            
            validation_result['results'].append(layer_validation)
        
        self.validation_log.append(validation_result)
        return validation_result
    
    def validate_overall_execution(self, tuning_results):
        """验证整体执行的完整性"""
        validation_result = {
            'timestamp': datetime.now().isoformat(),
            'test_type': 'overall_execution_validation',
            'total_layers': len(tuning_results),
            'total_duration': sum(r['total_duration'] for r in tuning_results),
            'valid': True,
            'issues': []
        }
        
        # 验证总执行时间
        expected_min_total = len(tuning_results) * 120  # 每层至少2分钟
        expected_max_total = len(tuning_results) * 300  # 每层最多5分钟
        
        if validation_result['total_duration'] < expected_min_total:
            validation_result['valid'] = False
            validation_result['issues'].append(
                f"总执行时间过短: {validation_result['total_duration']:.1f}秒 < {expected_min_total}秒"
            )
        
        # 验证每层都有必要的字段
        required_fields = ['layer_idx', 'total_duration', 'inference_duration', 'analysis_duration', 'improvement_percent']
        for i, result in enumerate(tuning_results):
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                validation_result['issues'].append(
                    f"第{i+1}层结果缺少字段: {missing_fields}"
                )
        
        self.validation_log.append(validation_result)
        return validation_result
    
    def generate_validation_report(self, output_path=None):
        """生成验证报告"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"validation_report_{timestamp}.json")
        
        report = {
            'project': self.project_path.name,
            'validation_timestamp': datetime.now().isoformat(),
            'total_validations': len(self.validation_log),
            'validation_log': self.validation_log,
            'summary': self._generate_validation_summary()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def _generate_validation_summary(self):
        """生成验证总结"""
        summary = {
            'total_tests': len(self.validation_log),
            'passed_tests': 0,
            'failed_tests': 0,
            'issues_found': []
        }
        
        for validation in self.validation_log:
            if validation.get('valid', False) or validation.get('overall_valid', False):
                summary['passed_tests'] += 1
            else:
                summary['failed_tests'] += 1
                
                # 收集问题
                if 'issues' in validation:
                    summary['issues_found'].extend(validation['issues'])
                
                # 从结果中收集问题
                if 'results' in validation:
                    for result in validation['results']:
                        if 'issues' in result:
                            summary['issues_found'].extend(result['issues'])
        
        summary['success_rate'] = (summary['passed_tests'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        
        return summary


def main():
    """测试验证器"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Layer Tuning验证工具")
    parser.add_argument("project_name", help="项目名称")
    parser.add_argument("--test-time", action="store_true", help="测试时间验证")
    
    args = parser.parse_args()
    
    project_path = Path(f"/mnt/f/Work/met_nonlinear_worktrees/met_nonlinear_master/projects/{args.project_name}")
    
    if not project_path.exists():
        print(f"❌ 项目不存在: {project_path}")
        return 1
    
    validator = LayerTuningValidator(project_path)
    
    if args.test_time:
        # 模拟测试时间验证
        mock_results = [
            {'layer_idx': 2, 'total_duration': 165, 'inference_duration': 105, 'analysis_duration': 60},
            {'layer_idx': 3, 'total_duration': 178, 'inference_duration': 112, 'analysis_duration': 66},
            {'layer_idx': 4, 'total_duration': 156, 'inference_duration': 98, 'analysis_duration': 58}
        ]
        
        result = validator.validate_execution_time(mock_results)
        print(f"时间验证结果: {'✅ 通过' if result['overall_valid'] else '❌ 失败'}")
        
        for layer_result in result['results']:
            print(f"  Layer {layer_result['layer_idx']}: {layer_result['total_duration']:.1f}s")
            if layer_result['issues']:
                for issue in layer_result['issues']:
                    print(f"    ⚠️ {issue}")
    
    # 生成报告
    report_path = validator.generate_validation_report()
    print(f"📋 验证报告已生成: {report_path}")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())