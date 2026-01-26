#!/usr/bin/env python3
"""
Dense+nReLU电路偏置误差测试工具

核心功能:
- 零输入条件下的偏置误差精确测量
- SPICE仿真与理论值对比分析
- 多配置批量测试支持
- 详细的误差统计和可视化报告
- 为闭环微调提供数据基础

使用方法:
    from bias_error_tester import BiasErrorTester
    
    tester = BiasErrorTester()
    result = tester.test_bias_error(gains, biases, opamp_config)
    tester.generate_report()

作者: Claude Code Assistant
日期: 2025-01-01
"""

import numpy as np
import matplotlib.pyplot as plt
from simulation import CircuitSimulation
from circuit_dense import DenseCircuitFactory
import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import warnings


class BiasErrorTester:
    """Dense+nReLU电路偏置误差测试器"""
    
    def __init__(self, output_dir: str = './bias_test_output'):
        """
        初始化偏置误差测试器
        
        Args:
            output_dir: 测试结果输出目录
        """
        self.output_dir = output_dir
        self.test_results = []
        self.test_counter = 0
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 测试配置
        self.test_config = {
            'simulation_time': 0.1,        # 100ms仿真时间
            'sample_points': 1000,         # 采样点数
            'steady_state_ratio': 0.8,     # 稳态判断阈值（最后20%数据）
        }
        
        # 初始化仿真环境
        self.sim = None
        self._init_simulation_env()
    
    def _init_simulation_env(self):
        """初始化仿真环境"""
        try:
            # 尝试不同的NGspice路径
            ngspice_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "Spice64", "bin", "ngspice_con.exe"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "Spice64", "bin", "ngspice"),
                "ngspice"
            ]
            
            for path in ngspice_paths:
                try:
                    self.sim = CircuitSimulation(
                        output_folder=self.output_dir,
                        ngspice_path=path if path != "ngspice" else None
                    )
                    print(f"仿真环境初始化成功，使用NGspice路径: {path}")
                    break
                except FileNotFoundError:
                    continue
            
            if self.sim is None:
                print("警告: NGspice环境初始化失败，将只进行理论分析")
                
        except Exception as e:
            print(f"仿真环境初始化警告: {e}")
            self.sim = None
    
    def test_bias_error(self, 
                       gains: np.ndarray, 
                       biases: List[float], 
                       opamp_config: Dict = None,
                       use_relu: bool = False,
                       test_name: str = None) -> Dict:
        """
        执行单次偏置误差测试
        
        Args:
            gains: 增益矩阵 [inputs, outputs]
            biases: 偏置值列表 [outputs]
            opamp_config: 运放配置
            use_relu: 是否使用ReLU激活
            test_name: 测试名称
            
        Returns:
            测试结果字典
        """
        self.test_counter += 1
        if test_name is None:
            test_name = f"bias_test_{self.test_counter:03d}"
        
        print(f"\n=== 执行偏置误差测试: {test_name} ===")
        print(f"增益矩阵: {np.array(gains).shape}")
        print(f"偏置值: {biases}")
        print(f"使用ReLU: {use_relu}")
        
        # 创建电路
        circuit = DenseCircuitFactory.create(
            gains=gains,
            biases=biases,
            opamp_config=opamp_config or {'model': 'ideal'},
            use_e96=True,
            use_relu=use_relu
        )
        
        # 生成时间向量和零输入信号
        t = np.linspace(0, self.test_config['simulation_time'], 
                       self.test_config['sample_points'])
        zero_input = np.zeros((len(t), circuit.n_inputs))
        
        # 执行测试
        result = {
            'test_info': {
                'name': test_name,
                'timestamp': datetime.now().isoformat(),
                'gains': np.array(gains).tolist(),
                'biases': biases,
                'use_relu': use_relu,
                'opamp_config': opamp_config
            },
            'circuit_info': {
                'n_inputs': circuit.n_inputs,
                'n_outputs': circuit.n_outputs,
                'has_bias': circuit.has_bias
            }
        }
        
        # SPICE仿真（如果环境可用）
        spice_result = None
        if self.sim is not None:
            try:
                print("执行SPICE仿真...")
                spice_result = self.sim.run_simulation_once(
                    zero_input, circuit, print_netlist=False
                )
            except Exception as e:
                print(f"SPICE仿真失败: {e}")
        
        # 理论计算
        print("执行理论计算...")
        numpy_result = circuit.simulate_numpy(t, zero_input)
        
        # 分析结果
        analysis = self._analyze_results(
            spice_result, numpy_result, biases, t
        )
        result.update(analysis)
        
        # 保存结果
        self.test_results.append(result)
        self._save_single_test(result)
        
        # 打印摘要
        self._print_test_summary(analysis.get('measurements', {}))
        
        return result
    
    def _analyze_results(self, spice_result, numpy_result, expected_biases, t):
        """分析测试结果"""
        
        steady_start_idx = int(self.test_config['steady_state_ratio'] * len(t))
        measurements = {}
        
        # 分析每个输出通道
        for ch in range(len(expected_biases)):
            expected_bias = expected_biases[ch]
            
            # 理论值分析
            if numpy_result is not None and numpy_result.ndim > 1:
                numpy_steady = numpy_result[steady_start_idx:, ch]
                numpy_mean = np.mean(numpy_steady)
                numpy_std = np.std(numpy_steady)
            else:
                numpy_mean = expected_bias  # 理论上应该等于期望值
                numpy_std = 0.0
            
            # SPICE结果分析
            spice_measured = None
            spice_std = None
            spice_error = None
            
            if spice_result and 'v_out_spice' in spice_result:
                spice_outputs = spice_result['v_out_spice']
                
                if isinstance(spice_outputs, dict):
                    key = f'out{ch+1}'
                    if key in spice_outputs:
                        spice_data = spice_outputs[key][steady_start_idx:]
                        spice_measured = np.mean(spice_data)
                        spice_std = np.std(spice_data)
                        spice_error = spice_measured - expected_bias
                elif spice_outputs.ndim > 1 and ch < spice_outputs.shape[1]:
                    spice_data = spice_outputs[steady_start_idx:, ch]
                    spice_measured = np.mean(spice_data)
                    spice_std = np.std(spice_data)
                    spice_error = spice_measured - expected_bias
            
            # 构建测量结果
            channel_result = {
                'expected_bias': expected_bias,
                'numpy_value': numpy_mean,
                'numpy_std': numpy_std,
                'spice_measured': spice_measured,
                'spice_std': spice_std,
                'spice_error': spice_error,
                'spice_error_mv': spice_error * 1000 if spice_error is not None else None,
                'relative_error_percent': (spice_error / expected_bias * 100) 
                                        if spice_error is not None and expected_bias != 0 else None,
                'has_spice_data': spice_measured is not None
            }
            
            measurements[ch] = channel_result
        
        # 整体统计
        spice_errors = [m['spice_error'] for m in measurements.values() 
                       if m['spice_error'] is not None]
        
        statistics = {
            'total_channels': len(measurements),
            'channels_with_spice': len(spice_errors),
            'max_error_mv': max([abs(e) for e in spice_errors]) * 1000 if spice_errors else None,
            'mean_error_mv': np.mean([abs(e) for e in spice_errors]) * 1000 if spice_errors else None,
            'channels_within_1mv': sum(1 for e in spice_errors if abs(e) * 1000 <= 1.0),
            'channels_within_5mv': sum(1 for e in spice_errors if abs(e) * 1000 <= 5.0)
        }
        
        return {
            'measurements': measurements,
            'statistics': statistics,
            'raw_data': {
                'spice_result': spice_result,
                'numpy_result': numpy_result.tolist() if numpy_result is not None else None
            }
        }
    
    def _print_test_summary(self, measurements):
        """打印测试摘要"""
        print("\n测试结果摘要:")
        print("-" * 60)
        
        for ch, data in measurements.items():
            print(f"通道 {ch+1}:")
            print(f"  期望偏置: {data['expected_bias']:.3f} V")
            print(f"  理论值:   {data['numpy_value']:.4f} V")
            
            if data['has_spice_data']:
                print(f"  SPICE值:  {data['spice_measured']:.4f} V")
                print(f"  误差:     {data['spice_error_mv']:.2f} mV")
                print(f"  相对误差: {data['relative_error_percent']:.1f}%")
                print(f"  噪声:     {data['spice_std']*1000:.3f} mV")
            else:
                print(f"  SPICE值:  未获取")
            print()
    
    def _save_single_test(self, result):
        """保存单次测试结果"""
        filename = f"{self.output_dir}/{result['test_info']['name']}_result.json"
        
        # 创建可序列化的结果副本
        save_result = result.copy()
        if 'raw_data' in save_result:
            # 移除不能序列化的原始数据
            save_result['raw_data'] = {
                'has_spice_data': save_result['raw_data']['spice_result'] is not None,
                'has_numpy_data': save_result['raw_data']['numpy_result'] is not None
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_result, f, indent=2, ensure_ascii=False)
        
        print(f"测试结果已保存: {filename}")
    
    def batch_test(self, test_configs: List[Dict]):
        """
        批量测试不同配置
        
        Args:
            test_configs: 测试配置列表，每个配置包含:
                - name: 测试名称
                - gains: 增益矩阵
                - biases: 偏置值
                - opamp_config: 运放配置
                - use_relu: 是否使用ReLU
        """
        print(f"开始批量测试，共 {len(test_configs)} 个配置")
        
        for i, config in enumerate(test_configs):
            print(f"\n{'='*20} 配置 {i+1}/{len(test_configs)} {'='*20}")
            
            self.test_bias_error(
                gains=config['gains'],
                biases=config['biases'],
                opamp_config=config.get('opamp_config'),
                use_relu=config.get('use_relu', False),
                test_name=config.get('name', f'batch_test_{i+1:03d}')
            )
        
        # 生成批量测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成综合测试报告"""
        if not self.test_results:
            print("没有测试结果可生成报告")
            return
        
        print("\n" + "="*80)
        print("偏置误差测试综合报告")
        print("="*80)
        
        # 统计信息
        total_tests = len(self.test_results)
        total_channels = sum(len(test['measurements']) for test in self.test_results)
        
        all_errors_mv = []
        spice_test_count = 0
        
        for test in self.test_results:
            has_spice = any(m['has_spice_data'] for m in test['measurements'].values())
            if has_spice:
                spice_test_count += 1
                for measurement in test['measurements'].values():
                    if measurement['spice_error_mv'] is not None:
                        all_errors_mv.append(abs(measurement['spice_error_mv']))
        
        print(f"测试总数: {total_tests}")
        print(f"总通道数: {total_channels}")
        print(f"SPICE测试数: {spice_test_count}")
        
        if all_errors_mv:
            print(f"\n误差统计:")
            print(f"  最大误差: {max(all_errors_mv):.2f} mV")
            print(f"  平均误差: {np.mean(all_errors_mv):.2f} mV")
            print(f"  标准差: {np.std(all_errors_mv):.2f} mV")
            print(f"  ≤1mV: {sum(1 for e in all_errors_mv if e <= 1.0)}/{len(all_errors_mv)} "
                  f"({sum(1 for e in all_errors_mv if e <= 1.0)/len(all_errors_mv)*100:.1f}%)")
            print(f"  ≤5mV: {sum(1 for e in all_errors_mv if e <= 5.0)}/{len(all_errors_mv)} "
                  f"({sum(1 for e in all_errors_mv if e <= 5.0)/len(all_errors_mv)*100:.1f}%)")
        
        # 保存详细报告
        self._save_detailed_report(all_errors_mv)
        
        # 生成可视化
        if all_errors_mv:
            self._generate_visualization(all_errors_mv)
    
    def _save_detailed_report(self, all_errors_mv):
        """保存详细报告"""
        # JSON报告
        report = {
            'summary': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(self.test_results),
                'total_channels': sum(len(test['measurements']) for test in self.test_results),
                'max_error_mv': max(all_errors_mv) if all_errors_mv else None,
                'mean_error_mv': np.mean(all_errors_mv) if all_errors_mv else None,
                'std_error_mv': np.std(all_errors_mv) if all_errors_mv else None
            },
            'all_test_results': self.test_results
        }
        
        # 保存JSON报告（移除原始数据）
        clean_report = report.copy()
        for test in clean_report['all_test_results']:
            if 'raw_data' in test:
                test['raw_data'] = {
                    'has_spice_data': test['raw_data'].get('spice_result') is not None,
                    'has_numpy_data': test['raw_data'].get('numpy_result') is not None
                }
        
        json_filename = f"{self.output_dir}/comprehensive_report.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(clean_report, f, indent=2, ensure_ascii=False)
        print(f"详细报告已保存: {json_filename}")
        
        # CSV摘要
        self._save_csv_summary()
    
    def _save_csv_summary(self):
        """保存CSV格式摘要"""
        data = []
        for test in self.test_results:
            for ch, measurement in test['measurements'].items():
                data.append({
                    'test_name': test['test_info']['name'],
                    'channel': ch + 1,
                    'expected_bias_V': measurement['expected_bias'],
                    'numpy_value_V': measurement['numpy_value'],
                    'spice_measured_V': measurement['spice_measured'],
                    'spice_error_mV': measurement['spice_error_mv'],
                    'relative_error_percent': measurement['relative_error_percent'],
                    'spice_noise_mV': measurement['spice_std'] * 1000 if measurement['spice_std'] else None,
                    'has_spice_data': measurement['has_spice_data'],
                    'use_relu': test['test_info']['use_relu'],
                    'opamp_model': test['test_info']['opamp_config'].get('model', 'unknown') if test['test_info']['opamp_config'] else 'unknown'
                })
        
        df = pd.DataFrame(data)
        csv_filename = f"{self.output_dir}/test_summary.csv"
        df.to_csv(csv_filename, index=False)
        print(f"CSV摘要已保存: {csv_filename}")
    
    def _generate_visualization(self, all_errors_mv):
        """生成可视化报告"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Dense+nReLU电路偏置误差测试报告', fontsize=16)
        
        # 1. 误差分布直方图
        ax1 = axes[0, 0]
        ax1.hist(all_errors_mv, bins=min(20, len(set(all_errors_mv))), 
                edgecolor='black', alpha=0.7)
        ax1.axvline(x=1.0, color='r', linestyle='--', label='1mV目标')
        ax1.axvline(x=5.0, color='orange', linestyle='--', label='5mV阈值')
        ax1.set_xlabel('偏置误差 (mV)')
        ax1.set_ylabel('频次')
        ax1.set_title('误差分布直方图')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 各测试最大误差
        ax2 = axes[0, 1]
        test_names = []
        test_max_errors = []
        
        for test in self.test_results:
            if any(m['has_spice_data'] for m in test['measurements'].values()):
                test_names.append(test['test_info']['name'])
                errors = [abs(m['spice_error_mv']) for m in test['measurements'].values() 
                         if m['spice_error_mv'] is not None]
                test_max_errors.append(max(errors) if errors else 0)
        
        if test_max_errors:
            bars = ax2.bar(range(len(test_names)), test_max_errors)
            ax2.axhline(y=1.0, color='r', linestyle='--', label='1mV目标')
            ax2.axhline(y=5.0, color='orange', linestyle='--', label='5mV阈值')
            ax2.set_xlabel('测试')
            ax2.set_ylabel('最大误差 (mV)')
            ax2.set_title('各测试最大误差')
            ax2.set_xticks(range(len(test_names)))
            ax2.set_xticklabels([name[:10] + '...' if len(name) > 10 else name 
                               for name in test_names], rotation=45)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # 3. 误差累积分布
        ax3 = axes[1, 0]
        sorted_errors = np.sort(all_errors_mv)
        y = np.arange(1, len(sorted_errors) + 1) / len(sorted_errors) * 100
        ax3.plot(sorted_errors, y, linewidth=2)
        ax3.axvline(x=1.0, color='r', linestyle='--', label='1mV')
        ax3.axvline(x=5.0, color='orange', linestyle='--', label='5mV')
        ax3.set_xlabel('偏置误差 (mV)')
        ax3.set_ylabel('累积百分比 (%)')
        ax3.set_title('误差累积分布')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 性能统计
        ax4 = axes[1, 1]
        categories = ['≤1mV', '1-5mV', '>5mV']
        counts = [
            sum(1 for e in all_errors_mv if e <= 1.0),
            sum(1 for e in all_errors_mv if 1.0 < e <= 5.0),
            sum(1 for e in all_errors_mv if e > 5.0)
        ]
        colors = ['green', 'orange', 'red']
        
        wedges, texts, autotexts = ax4.pie(counts, labels=categories, colors=colors,
                                          autopct='%1.1f%%', startangle=90)
        ax4.set_title(f'误差分布统计\n(总计 {len(all_errors_mv)} 个通道)')
        
        plt.tight_layout()
        
        # 保存图像
        plot_filename = f"{self.output_dir}/bias_error_report.png"
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        print(f"可视化报告已保存: {plot_filename}")
        
        return fig


# 预定义测试配置
def get_standard_test_configs():
    """获取标准测试配置"""
    return [
        {
            'name': 'basic_positive_bias',
            'gains': np.array([[1.0, -0.5], [-0.7, 1.2]]),
            'biases': [0.3, 0.2],
            'opamp_config': {'model': 'ideal'},
            'use_relu': False
        },
        {
            'name': 'basic_negative_bias',
            'gains': np.array([[1.0, -0.5], [-0.7, 1.2]]),
            'biases': [-0.3, -0.2],
            'opamp_config': {'model': 'ideal'},
            'use_relu': False
        },
        {
            'name': 'mixed_bias_with_relu',
            'gains': np.array([[1.0, -0.5], [-0.7, 1.2]]),
            'biases': [0.3, -0.2],
            'opamp_config': {'model': 'ideal'},
            'use_relu': True
        }
    ]


# 使用示例
def main():
    """主程序示例"""
    print("Dense+nReLU电路偏置误差测试工具")
    print("="*50)
    
    # 创建测试器
    tester = BiasErrorTester()
    
    # 执行标准测试配置
    standard_configs = get_standard_test_configs()
    tester.batch_test(standard_configs)
    
    print(f"\n测试完成! 结果保存在: {tester.output_dir}")


if __name__ == "__main__":
    main()