#!/usr/bin/env python3
"""收集现有推理结果作为黄金标准数据"""

import json
import numpy as np
from pathlib import Path
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calibration_analyzer.wavedata import WaveData

def collect_golden_data():
    """收集现有的推理结果作为黄金标准"""
    
    golden_dir = Path("inference/tests/golden_data")
    golden_dir.mkdir(parents=True, exist_ok=True)
    
    # 收集的项目
    project = "WNET5q0.5h2u6l4"
    
    print(f"收集项目 {project} 的现有推理结果...")
    
    results = {project: {}}
    
    # 推理输出目录
    inference_dir = Path(f"projects/{project}/data/inference")
    wave_output_dir = Path(f"projects/{project}/data/wave_output")
    
    # 1. 收集NN分层推理结果
    print("\n1. 收集NN分层推理结果...")
    if inference_dir.exists():
        # 收集nn_layers.wave
        nn_layers_file = inference_dir / "nn_layers.wave"
        if nn_layers_file.exists():
            print(f"  - 处理: {nn_layers_file.name}")
            try:
                wave_data = WaveData.load(str(nn_layers_file))
                results[project]['nn_layers'] = serialize_wave_data(wave_data)
            except Exception as e:
                print(f"    ❌ 错误: {e}")
        
        # 收集nn_layers目录下的分层结果
        nn_layers_dir = inference_dir / "nn_layers"
        if nn_layers_dir.exists():
            layer_results = {}
            for layer_file in sorted(nn_layers_dir.glob("*.wave")):
                print(f"  - 处理: {layer_file.name}")
                try:
                    wave_data = WaveData.load(str(layer_file))
                    layer_results[layer_file.stem] = serialize_wave_data(wave_data)
                except Exception as e:
                    print(f"    ❌ 错误: {e}")
            
            if layer_results:
                results[project]['layer_outputs'] = layer_results
    
    # 2. 收集原始输入输出数据
    print("\n2. 收集原始输入输出数据...")
    if wave_output_dir.exists():
        for wave_file in wave_output_dir.glob("*.wave"):
            print(f"  - 处理: {wave_file.name}")
            try:
                wave_data = WaveData.load(str(wave_file))
                results[project][wave_file.stem] = serialize_wave_data(wave_data)
            except Exception as e:
                print(f"    ❌ 错误: {e}")
    
    # 3. 收集SPICE推理结果（如果有）
    print("\n3. 查找SPICE推理结果...")
    spice_files = []
    if inference_dir.exists():
        spice_files.extend(inference_dir.glob("*_spice*.wave"))
    if wave_output_dir.exists():
        spice_files.extend(wave_output_dir.glob("*_spice*.wave"))
    for spice_file in spice_files:
        print(f"  - 处理: {spice_file.name}")
        try:
            wave_data = WaveData.load(str(spice_file))
            results[project][spice_file.stem] = serialize_wave_data(wave_data)
        except Exception as e:
            print(f"    ❌ 错误: {e}")
    
    # 4. 保存配置文件
    print("\n4. 保存项目配置...")
    config_file = Path(f"projects/{project}/config.json")
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            results[project]['config'] = json.load(f)
        print("  ✓ 配置文件已保存")
    
    # 保存黄金数据
    output_file = golden_dir / "collected_golden_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 黄金数据已保存到: {output_file}")
    
    # 生成验证校验和
    generate_checksums(results, golden_dir)
    
    # 打印统计信息
    print_statistics(results)

def serialize_wave_data(wave_data):
    """序列化WaveData对象"""
    result = {
        'description': wave_data.description,
        'author': wave_data.author,
        'num_records': len(wave_data.records),
        'records': []
    }
    
    for record in wave_data.records:
        data = record.data
        record_info = {
            'record_id': record.record_id,
            'shape': list(data.shape),
            'dtype': str(data.dtype),
            'sample_rate': record.sample_rate,
            'channel_names': record.channel_names,
            'statistics': {
                'min': float(np.min(data)),
                'max': float(np.max(data)),
                'mean': float(np.mean(data)),
                'std': float(np.std(data)),
                'median': float(np.median(data))
            },
            # 保存数据样本用于验证
            'data_samples': {
                'first_10': data.flatten()[:10].tolist(),
                'last_10': data.flatten()[-10:].tolist(),
                'random_indices': {
                    'indices': [100, 500, 1000, 5000, 10000],
                    'values': [float(data.flatten()[i]) if i < len(data.flatten()) else None 
                              for i in [100, 500, 1000, 5000, 10000]]
                }
            }
        }
        
        # 如果有多个通道，记录每个通道的统计信息
        if len(data.shape) > 1 and data.shape[1] > 1:
            channel_stats = []
            for ch in range(data.shape[1]):
                ch_data = data[:, ch]
                channel_stats.append({
                    'channel': ch,
                    'min': float(np.min(ch_data)),
                    'max': float(np.max(ch_data)),
                    'mean': float(np.mean(ch_data))
                })
            record_info['channel_statistics'] = channel_stats
        
        result['records'].append(record_info)
    
    return result

def generate_checksums(results, golden_dir):
    """生成验证校验和"""
    checksums = {}
    
    for project, data in results.items():
        checksums[project] = {}
        
        # 为每个wave文件生成校验和
        for key, value in data.items():
            if isinstance(value, dict) and 'records' in value:
                file_checksum = {}
                for record in value['records']:
                    stats = record['statistics']
                    file_checksum[record['record_id']] = {
                        'min': stats['min'],
                        'max': stats['max'],
                        'mean': stats['mean'],
                        'shape': record['shape']
                    }
                checksums[project][key] = file_checksum
    
    # 保存校验和
    checksum_file = golden_dir / "golden_checksums.json"
    with open(checksum_file, 'w', encoding='utf-8') as f:
        json.dump(checksums, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 验证校验和已保存到: {checksum_file}")

def print_statistics(results):
    """打印统计信息"""
    print("\n" + "="*60)
    print("黄金数据统计信息")
    print("="*60)
    
    for project, data in results.items():
        print(f"\n项目: {project}")
        
        wave_files = [k for k in data.keys() if k not in ['config', 'layer_outputs']]
        print(f"  - Wave文件数量: {len(wave_files)}")
        
        if 'layer_outputs' in data:
            print(f"  - 分层输出数量: {len(data['layer_outputs'])}")
        
        # 打印每个文件的关键信息
        for key, value in data.items():
            if isinstance(value, dict) and 'records' in value:
                print(f"\n  {key}:")
                for record in value['records']:
                    stats = record['statistics']
                    print(f"    - {record['record_id']}: "
                          f"shape={record['shape']}, "
                          f"range=[{stats['min']:.6f}, {stats['max']:.6f}], "
                          f"mean={stats['mean']:.6f}")

if __name__ == "__main__":
    print("="*60)
    print("黄金数据收集工具")
    print("="*60)
    print("收集现有的推理结果作为重构验证的黄金标准")
    print("="*60)
    
    collect_golden_data()