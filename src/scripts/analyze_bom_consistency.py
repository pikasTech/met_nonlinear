#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BOM合并前后编号一致性深度分析脚本

分析目标：
1. 验证合并后的BOM中每个Designator映射是否正确
2. 检查是否有任何编号丢失或重复
3. 验证排序算法的正确性
4. 生成详细的对比报告
"""
from __future__ import annotations

import pandas as pd
import json
import os
import re
from collections import defaultdict, Counter


def parse_designators(designator_str):
    """解析Designator字符串，返回编号列表"""
    # 移除引号
    designator_str = designator_str.strip('"')
    # 分割编号
    designators = [d.strip() for d in designator_str.split(',')]
    return designators


def extract_resistor_number(designator):
    """从R编号中提取数字部分"""
    match = re.match(r'R(\d+)', designator)
    if match:
        return int(match.group(1))
    return None


def analyze_bom_consistency(csv_path, bom_path):
    """深度分析BOM合并前后的一致性"""
    print("=" * 80)
    print("BOM合并前后编号一致性深度分析")
    print("=" * 80)
    
    # 1. 读取原始CSV数据（未合并）
    print("\n1. 读取原始CSV数据...")
    df_csv = pd.read_csv(csv_path)
    
    # 筛选权重电阻（包括input和bias电阻，与BOM生成器一致）
    weight_resistors = df_csv[df_csv['type'].isin(['input_pos', 'input_neg', 'bias_pos', 'bias_neg'])]
    print(f"   原始权重电阻总数: {len(weight_resistors)}")
    print(f"   - input电阻: {len(df_csv[df_csv['type'].isin(['input_pos', 'input_neg'])])}")
    print(f"   - bias电阻: {len(df_csv[df_csv['type'].isin(['bias_pos', 'bias_neg'])])}")
    
    # 构建原始电阻映射：编号 -> 阻值
    original_mapping = {}
    for idx, row in weight_resistors.iterrows():
        # 计算编号（从1开始）
        resistor_num = len(original_mapping) + 1
        designator = f"R{resistor_num}"
        value = row['Standardized_E96']
        original_mapping[designator] = value
    
    print(f"   原始编号范围: R1 - R{len(original_mapping)}")
    
    # 2. 读取合并后的BOM
    print("\n2. 读取合并后的BOM...")
    df_bom = pd.read_csv(bom_path)
    print(f"   合并后BOM行数: {len(df_bom)}")
    
    # 3. 提取所有合并后的编号
    print("\n3. 分析合并后的编号映射...")
    merged_designators = []
    merged_mapping = {}  # value -> [designators]
    
    for idx, row in df_bom.iterrows():
        designators = parse_designators(row['Designator'])
        quantity = row['Quantity']
        value_str = row['Value']
        
        # 提取数值（去除单位和公差）
        value_match = re.match(r'电阻\s+([\d.]+)(k|M)?Ω', value_str)
        if value_match:
            value = float(value_match.group(1))
            unit = value_match.group(2)
            if unit == 'k':
                value *= 1000
            elif unit == 'M':
                value *= 1000000
            
            # 记录映射
            if value not in merged_mapping:
                merged_mapping[value] = []
            merged_mapping[value].extend(designators)
        
        merged_designators.extend(designators)
        
        # 验证数量一致性
        if len(designators) != quantity:
            print(f"   [WARNING] 行{idx+1}的Quantity({quantity})与Designator数量({len(designators)})不匹配")
    
    print(f"   合并后总编号数: {len(merged_designators)}")
    print(f"   唯一阻值数: {len(merged_mapping)}")
    
    # 4. 验证编号完整性
    print("\n4. 验证编号完整性...")
    
    # 提取所有编号的数字部分
    merged_numbers = []
    for d in merged_designators:
        num = extract_resistor_number(d)
        if num:
            merged_numbers.append(num)
    
    merged_numbers_set = set(merged_numbers)
    expected_numbers = set(range(1, len(original_mapping) + 1))
    
    # 查找丢失的编号
    missing_numbers = expected_numbers - merged_numbers_set
    if missing_numbers:
        print(f"   [FAIL] 丢失的编号: {sorted(missing_numbers)}")
    else:
        print(f"   [PASS] 所有编号都存在（R1-R{len(original_mapping)}）")
    
    # 查找重复的编号
    number_counts = Counter(merged_numbers)
    duplicates = {num: count for num, count in number_counts.items() if count > 1}
    if duplicates:
        print(f"   [FAIL] 重复的编号: {duplicates}")
    else:
        print("   [PASS] 没有重复的编号")
    
    # 查找额外的编号
    extra_numbers = merged_numbers_set - expected_numbers
    if extra_numbers:
        print(f"   [FAIL] 额外的编号: {sorted(extra_numbers)}")
    else:
        print("   [PASS] 没有额外的编号")
    
    # 5. 验证阻值映射的正确性
    print("\n5. 验证阻值映射的正确性...")
    
    # 构建合并后的编号->阻值映射
    merged_designator_to_value = {}
    for value, designators in merged_mapping.items():
        for d in designators:
            merged_designator_to_value[d] = value
    
    # 对比原始映射和合并后映射
    mismatch_count = 0
    for designator, original_value in original_mapping.items():
        if designator in merged_designator_to_value:
            merged_value = merged_designator_to_value[designator]
            # 允许小的浮点误差
            if abs(original_value - merged_value) > 0.01:
                mismatch_count += 1
                if mismatch_count <= 10:  # 只显示前10个不匹配
                    print(f"   [FAIL] {designator}: 原始={original_value:.2f}Ω, 合并后={merged_value:.2f}Ω")
        else:
            print(f"   [FAIL] {designator} 在合并后的BOM中找不到")
    
    if mismatch_count == 0:
        print("   [PASS] 所有编号的阻值映射都正确")
    else:
        print(f"   [FAIL] 发现 {mismatch_count} 个阻值映射不匹配")
    
    # 6. 分析排序算法
    print("\n6. 分析编号排序算法...")
    
    for idx, row in df_bom.head(10).iterrows():  # 分析前10行
        designators = parse_designators(row['Designator'])
        numbers = [extract_resistor_number(d) for d in designators]
        numbers = [n for n in numbers if n is not None]
        
        # 检查是否按数字顺序排序
        is_sorted = numbers == sorted(numbers)
        status = "[PASS]" if is_sorted else "[FAIL]"
        
        print(f"   行{idx+1}: {row['Designator'][:50]}{'...' if len(row['Designator']) > 50 else ''}")
        print(f"         数字: {numbers[:10]}{'...' if len(numbers) > 10 else ''}")
        print(f"         排序状态: {status}")
    
    # 7. 生成总结报告
    print("\n" + "=" * 80)
    print("分析总结")
    print("=" * 80)
    
    analysis_result = {
        "原始电阻数": len(original_mapping),
        "合并后编号总数": len(merged_designators),
        "合并后行数": len(df_bom),
        "压缩率": f"{(1 - len(df_bom)/len(original_mapping)) * 100:.1f}%",
        "编号完整性": "[PASS]" if not missing_numbers and not duplicates and not extra_numbers else "[FAIL]",
        "阻值映射正确性": "[PASS]" if mismatch_count == 0 else f"[FAIL] {mismatch_count}个不匹配",
        "数量一致性": "[PASS]" if len(merged_designators) == len(original_mapping) else "[FAIL]"
    }
    
    for key, value in analysis_result.items():
        print(f"  {key}: {value}")
    
    # 保存详细报告
    report_path = os.path.join(os.path.dirname(bom_path), "bom_consistency_analysis.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": analysis_result,
            "missing_numbers": sorted(list(missing_numbers)) if missing_numbers else [],
            "duplicate_numbers": duplicates,
            "extra_numbers": sorted(list(extra_numbers)) if extra_numbers else [],
            "mismatch_count": mismatch_count
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细报告已保存到: {report_path}")
    
    return analysis_result


if __name__ == "__main__":
    # 设置文件路径
    project_path = "projects/WNET5q1h2u6l3"
    csv_path = os.path.join(project_path, "data/resistance_tables/all_layers_resistances.csv")
    bom_path = os.path.join(project_path, "data/resistance_tables/all_layers_resistances_bom.csv")
    
    # 执行分析
    if os.path.exists(csv_path) and os.path.exists(bom_path):
        analyze_bom_consistency(csv_path, bom_path)
    else:
        print(f"错误：找不到必要的文件")
        if not os.path.exists(csv_path):
            print(f"  缺少: {csv_path}")
        if not os.path.exists(bom_path):
            print(f"  缺少: {bom_path}")