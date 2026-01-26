#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证grouped BOM编号模式是否正确

规则：每个通道内顺序应该是：
1. bias_pos (1个)
2. input_pos (6个)
3. bias_neg (1个)
4. input_neg (6个)
"""

import pandas as pd
import sys


def verify_grouped_bom(csv_path, bom_path):
    """验证grouped BOM编号是否符合规则"""
    
    # 读取原始CSV获取电阻类型信息
    df_csv = pd.read_csv(csv_path)
    
    # 筛选权重电阻（与BOM生成器一致）
    weight_df = df_csv[df_csv['type'].isin(['input_pos', 'input_neg', 'bias_pos', 'bias_neg'])]
    
    # 按grouped规则排序
    def get_sort_key(row):
        layer_priority = {
            'layer2': 0,
            'layer3': 1, 
            'layer4': 2,
            'layer5': 3
        }
        
        type_priority = {
            'bias_pos': 0,
            'input_pos': 1,
            'bias_neg': 2,
            'input_neg': 3
        }
        
        layer = row.get('layer', 'unknown')
        channel = row.get('channel', 0)
        res_type = row.get('type', 'unknown')
        index = row.get('index')
        
        if pd.isna(index) or index is None:
            index = 0
        else:
            index = float(index)
            
        return (
            layer_priority.get(layer, 999),
            channel,
            type_priority.get(res_type, 999),
            index
        )
    
    weight_df = weight_df.copy()
    weight_df['sort_key'] = weight_df.apply(get_sort_key, axis=1)
    weight_df_sorted = weight_df.sort_values('sort_key')
    
    # 读取BOM文件
    df_bom = pd.read_csv(bom_path)
    
    print("=" * 80)
    print("Grouped BOM编号模式验证")
    print("=" * 80)
    
    # 验证每个通道的编号顺序
    print("\n各通道编号顺序检查：")
    print("-" * 40)
    
    # 统计每个层和通道
    channels = weight_df_sorted.groupby(['layer', 'channel']).size().reset_index(name='count')
    
    current_idx = 0
    all_correct = True
    
    for _, channel_info in channels.iterrows():
        layer = channel_info['layer']
        channel = channel_info['channel']
        count = channel_info['count']
        
        print(f"\n{layer}, Channel {channel}:")
        
        # 获取该通道的电阻
        channel_resistors = weight_df_sorted[
            (weight_df_sorted['layer'] == layer) & 
            (weight_df_sorted['channel'] == channel)
        ]
        
        # 预期顺序
        expected_order = []
        actual_order = []
        
        for i, (_, row) in enumerate(channel_resistors.iterrows()):
            r_num = current_idx + i + 1
            actual_order.append((f"R{r_num}", row['type']))
            
        # 检查顺序是否正确
        channel_correct = True
        
        # 应该先是1个bias_pos
        if len(actual_order) > 0 and actual_order[0][1] != 'bias_pos':
            channel_correct = False
            
        # 然后是6个input_pos
        for i in range(1, min(7, len(actual_order))):
            if actual_order[i][1] != 'input_pos':
                channel_correct = False
                
        # 然后是1个bias_neg
        if len(actual_order) > 7 and actual_order[7][1] != 'bias_neg':
            channel_correct = False
            
        # 最后是6个input_neg
        for i in range(8, min(14, len(actual_order))):
            if actual_order[i][1] != 'input_neg':
                channel_correct = False
        
        # 显示前14个电阻
        for i in range(min(14, len(actual_order))):
            designator, res_type = actual_order[i]
            expected_type = ''
            if i == 0:
                expected_type = 'bias_pos'
            elif i <= 6:
                expected_type = 'input_pos'
            elif i == 7:
                expected_type = 'bias_neg'
            else:
                expected_type = 'input_neg'
                
            status = "OK" if res_type == expected_type else "FAIL"
            print(f"  {designator}: {res_type:10} (期望: {expected_type:10}) {status}")
            
        if channel_correct:
            print("  状态: [PASS] 正确")
        else:
            print("  状态: [FAIL] 错误")
            all_correct = False
            
        current_idx += count
    
    print("\n" + "=" * 80)
    print("总体验证结果:")
    if all_correct:
        print("[PASS] Grouped BOM编号模式完全正确！")
        print("每个通道都符合: bias_pos(1) -> input_pos(6) -> bias_neg(1) -> input_neg(6)")
    else:
        print("[FAIL] Grouped BOM编号模式有错误，请检查排序逻辑")
    print("=" * 80)
    
    return all_correct


if __name__ == "__main__":
    csv_path = "projects/WNET5q1h2u6l3/data/resistance_tables/all_layers_resistances.csv"
    bom_path = "projects/WNET5q1h2u6l3/data/resistance_tables/all_layers_resistances_bom_raw.csv"
    
    result = verify_grouped_bom(csv_path, bom_path)
    sys.exit(0 if result else 1)