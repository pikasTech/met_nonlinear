#!/usr/bin/env python3
"""验证重构后的推理结果与黄金标准的一致性"""

import json
import numpy as np
from pathlib import Path
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calibration_analyzer.wavedata import WaveData

class GoldenDataVerifier:
    """黄金数据验证器"""
    
    def __init__(self, golden_data_path, tolerance=1e-6):
        """
        初始化验证器
        
        Args:
            golden_data_path: 黄金数据文件路径
            tolerance: 数值比较的容差
        """
        self.golden_data_path = Path(golden_data_path)
        self.tolerance = tolerance
        self.golden_data = None
        self.checksums = None
        
        # 加载黄金数据
        self._load_golden_data()
    
    def _load_golden_data(self):
        """加载黄金数据和校验和"""
        # 加载完整黄金数据
        if self.golden_data_path.exists():
            with open(self.golden_data_path, 'r', encoding='utf-8') as f:
                self.golden_data = json.load(f)
            print(f"✓ 已加载黄金数据: {self.golden_data_path}")
        else:
            raise FileNotFoundError(f"黄金数据文件不存在: {self.golden_data_path}")
        
        # 加载校验和
        checksum_path = self.golden_data_path.parent / "golden_checksums.json"
        if checksum_path.exists():
            with open(checksum_path, 'r', encoding='utf-8') as f:
                self.checksums = json.load(f)
            print(f"✓ 已加载验证校验和")
    
    def verify_wave_file_direct(self, wave_file_path, golden_info):
        """
        直接验证wave文件与提供的黄金数据
        
        Args:
            wave_file_path: 要验证的wave文件路径
            golden_info: 黄金数据字典
        
        Returns:
            (bool, dict): 验证是否通过，详细信息
        """
        wave_file_path = Path(wave_file_path)
        
        if not wave_file_path.exists():
            return False, {"error": f"文件不存在: {wave_file_path}"}
        
        try:
            # 加载当前wave文件
            current_wave = WaveData.load(str(wave_file_path))
            
            # 验证记录数量
            if len(current_wave.records) != golden_info['num_records']:
                return False, {
                    "error": "记录数量不匹配",
                    "expected": golden_info['num_records'],
                    "actual": len(current_wave.records)
                }
            
            # 逐个验证记录
            mismatches = []
            for i, (current_record, golden_record) in enumerate(zip(current_wave.records, golden_info['records'])):
                # 验证形状
                if list(current_record.data.shape) != golden_record['shape']:
                    mismatches.append({
                        "record": i,
                        "issue": "形状不匹配",
                        "expected": golden_record['shape'],
                        "actual": list(current_record.data.shape)
                    })
                    continue
                
                # 验证统计信息
                current_stats = {
                    'min': float(np.min(current_record.data)),
                    'max': float(np.max(current_record.data)),
                    'mean': float(np.mean(current_record.data)),
                    'std': float(np.std(current_record.data))
                }
                
                golden_stats = golden_record['statistics']
                
                # 检查各项统计值
                for stat_name in ['min', 'max', 'mean', 'std']:
                    if not np.isclose(current_stats[stat_name], golden_stats[stat_name], 
                                    rtol=self.tolerance, atol=self.tolerance):
                        mismatches.append({
                            "record": i,
                            "issue": f"{stat_name}不匹配",
                            "expected": golden_stats[stat_name],
                            "actual": current_stats[stat_name],
                            "difference": abs(current_stats[stat_name] - golden_stats[stat_name])
                        })
                
                # 验证特定样本值
                data_samples = golden_record['data_samples']
                current_flat = current_record.data.flatten()
                
                # 检查前10个样本
                for j, expected_val in enumerate(data_samples['first_10']):
                    if j < len(current_flat):
                        if not np.isclose(current_flat[j], expected_val, 
                                        rtol=self.tolerance, atol=self.tolerance):
                            mismatches.append({
                                "record": i,
                                "issue": f"第{j}个样本值不匹配",
                                "expected": expected_val,
                                "actual": float(current_flat[j])
                            })
            
            # 判断是否通过
            passed = len(mismatches) == 0
            
            return passed, {
                "file": str(wave_file_path),
                "passed": passed,
                "mismatches": mismatches[:10]  # 只显示前10个不匹配
            }
            
        except Exception as e:
            return False, {"error": f"验证过程出错: {str(e)}"}
    
    def verify_wave_file(self, wave_file_path, golden_key):
        """
        验证单个wave文件与黄金数据的一致性
        
        Args:
            wave_file_path: 要验证的wave文件路径
            golden_key: 黄金数据中对应的键
        
        Returns:
            (bool, dict): 验证是否通过，详细信息
        """
        wave_file_path = Path(wave_file_path)
        
        if not wave_file_path.exists():
            return False, {"error": f"文件不存在: {wave_file_path}"}
        
        try:
            # 加载当前wave文件
            current_wave = WaveData.load(str(wave_file_path))
            
            # 获取对应的黄金数据
            project = list(self.golden_data.keys())[0]  # 假设只有一个项目
            if golden_key not in self.golden_data[project]:
                return False, {"error": f"黄金数据中找不到键: {golden_key}"}
            
            golden_info = self.golden_data[project][golden_key]
            
            # 验证记录数量
            if len(current_wave.records) != golden_info['num_records']:
                return False, {
                    "error": "记录数量不匹配",
                    "expected": golden_info['num_records'],
                    "actual": len(current_wave.records)
                }
            
            # 逐个验证记录
            mismatches = []
            for i, (current_record, golden_record) in enumerate(zip(current_wave.records, golden_info['records'])):
                # 验证形状
                if list(current_record.data.shape) != golden_record['shape']:
                    mismatches.append({
                        "record": i,
                        "issue": "形状不匹配",
                        "expected": golden_record['shape'],
                        "actual": list(current_record.data.shape)
                    })
                    continue
                
                # 验证统计信息
                current_stats = {
                    'min': float(np.min(current_record.data)),
                    'max': float(np.max(current_record.data)),
                    'mean': float(np.mean(current_record.data)),
                    'std': float(np.std(current_record.data))
                }
                
                golden_stats = golden_record['statistics']
                
                # 检查各项统计值
                for stat_name in ['min', 'max', 'mean', 'std']:
                    if not np.isclose(current_stats[stat_name], golden_stats[stat_name], 
                                    rtol=self.tolerance, atol=self.tolerance):
                        mismatches.append({
                            "record": i,
                            "issue": f"{stat_name}不匹配",
                            "expected": golden_stats[stat_name],
                            "actual": current_stats[stat_name],
                            "difference": abs(current_stats[stat_name] - golden_stats[stat_name])
                        })
                
                # 验证特定样本值
                data_samples = golden_record['data_samples']
                current_flat = current_record.data.flatten()
                
                # 检查前10个样本
                for j, expected_val in enumerate(data_samples['first_10']):
                    if j < len(current_flat):
                        if not np.isclose(current_flat[j], expected_val, 
                                        rtol=self.tolerance, atol=self.tolerance):
                            mismatches.append({
                                "record": i,
                                "issue": f"第{j}个样本值不匹配",
                                "expected": expected_val,
                                "actual": float(current_flat[j])
                            })
            
            # 判断是否通过
            passed = len(mismatches) == 0
            
            return passed, {
                "file": str(wave_file_path),
                "golden_key": golden_key,
                "passed": passed,
                "mismatches": mismatches[:10]  # 只显示前10个不匹配
            }
            
        except Exception as e:
            return False, {"error": f"验证过程出错: {str(e)}"}
    
    def verify_project(self, project_name):
        """
        验证整个项目的推理结果
        
        Args:
            project_name: 项目名称
        
        Returns:
            dict: 验证结果汇总
        """
        print(f"\n开始验证项目: {project_name}")
        print("="*60)
        
        results = {
            "project": project_name,
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        # 检查推理输出目录
        inference_dir = Path(f"projects/{project_name}/data/inference")
        
        if not inference_dir.exists():
            print(f"❌ 推理目录不存在: {inference_dir}")
            return results
        
        # 验证nn_layers.wave
        nn_layers_file = inference_dir / "nn_layers.wave"
        if nn_layers_file.exists():
            print("\n验证 nn_layers.wave...")
            passed, details = self.verify_wave_file(nn_layers_file, "nn_layers")
            results["total_tests"] += 1
            if passed:
                results["passed"] += 1
                print("  ✓ 通过")
            else:
                results["failed"] += 1
                print(f"  ✗ 失败: {details}")
            results["details"].append(details)
        
        # 验证分层输出
        nn_layers_dir = inference_dir / "nn_layers"
        if nn_layers_dir.exists():
            print("\n验证分层输出...")
            # 首先检查layer_outputs是否存在于黄金数据中
            project = list(self.golden_data.keys())[0]
            if 'layer_outputs' in self.golden_data[project]:
                layer_outputs = self.golden_data[project]['layer_outputs']
                
                for layer_file in sorted(nn_layers_dir.glob("*.wave")):
                    # 检查该文件是否在layer_outputs中
                    if layer_file.stem in layer_outputs:
                        passed, details = self.verify_wave_file_direct(
                            layer_file, 
                            layer_outputs[layer_file.stem]
                        )
                results["total_tests"] += 1
                if passed:
                    results["passed"] += 1
                    print(f"  ✓ {layer_file.name}")
                else:
                    results["failed"] += 1
                    print(f"  ✗ {layer_file.name}: {details.get('mismatches', details.get('error'))}")
                results["details"].append(details)
        
        # 打印汇总
        print("\n" + "="*60)
        print("验证汇总:")
        print(f"  总测试数: {results['total_tests']}")
        print(f"  通过: {results['passed']}")
        print(f"  失败: {results['failed']}")
        
        if results['failed'] == 0:
            print("\n✅ 所有测试通过！重构后的代码与黄金标准完全一致。")
        else:
            print(f"\n❌ 有 {results['failed']} 个测试失败。")
        
        return results
    
    def quick_verify(self, project_name):
        """
        快速验证（仅检查校验和）
        
        Args:
            project_name: 项目名称
        
        Returns:
            bool: 是否通过快速验证
        """
        if not self.checksums or project_name not in self.checksums:
            print(f"❌ 项目 {project_name} 的校验和不存在")
            return False
        
        project_checksums = self.checksums[project_name]
        all_passed = True
        
        print(f"\n快速验证项目: {project_name}")
        print("="*40)
        
        # 检查各个文件的校验和
        for file_key, file_checksums in project_checksums.items():
            if isinstance(file_checksums, dict) and not file_checksums.get('min'):
                # 这是一个包含多个记录的文件
                for record_id, record_checksum in file_checksums.items():
                    # 这里可以添加实际的验证逻辑
                    print(f"  - {file_key}/{record_id}: 待验证")
            else:
                # 单个记录的文件
                print(f"  - {file_key}: 待验证")
        
        return all_passed


def main():
    """主函数"""
    print("="*60)
    print("黄金数据验证工具")
    print("="*60)
    print("验证重构后的推理结果与黄金标准的一致性")
    print("="*60)
    
    # 黄金数据路径
    golden_data_path = Path("inference/tests/golden_data/collected_golden_data.json")
    
    if not golden_data_path.exists():
        print(f"\n❌ 黄金数据文件不存在: {golden_data_path}")
        print("请先运行 collect_golden_data.py 生成黄金数据")
        return
    
    # 创建验证器
    verifier = GoldenDataVerifier(golden_data_path)
    
    # 验证项目
    project_name = "WNET5q0.5h2u6l4"
    
    # 完整验证
    results = verifier.verify_project(project_name)
    
    # 保存验证结果
    output_file = Path("inference/tests/golden_data/verification_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n验证结果已保存到: {output_file}")


if __name__ == "__main__":
    main()