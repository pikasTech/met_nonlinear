#!/usr/bin/env python3
"""比较重构前后的推理输出"""

import subprocess
import os
import sys
import difflib
from pathlib import Path

def run_inference(work_dir, project="WNET5q0.5h2u6l4"):
    """在指定目录运行推理并捕获输出"""
    
    print(f"\n运行推理: {work_dir}")
    
    # 切换到工作目录并运行推理
    cmd = [
        "conda", "run", "-n", "tf26",
        "python", "cli.py", "-i", project
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=work_dir,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            print(f"错误: {result.stderr}")
            return None
            
        return result.stdout
        
    except Exception as e:
        print(f"执行失败: {e}")
        return None

def clean_output(text):
    """清理输出文本，移除时间戳等可变内容"""
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # 跳过包含时间戳的行
        if any(x in line for x in ['timestamp', '耗时', 'elapsed', '时间', 'ms', 'seconds']):
            continue
        # 跳过路径相关的行（可能不同）
        if any(x in line for x in ['Loading', 'Saving', '保存到', '加载自']):
            continue
        # 跳过GPU相关信息
        if any(x in line for x in ['GPU', 'CUDA', 'cudart', 'tensorflow']):
            continue
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def compare_outputs(output1, output2):
    """比较两个输出并显示差异"""
    
    # 清理输出
    clean1 = clean_output(output1)
    clean2 = clean_output(output2)
    
    # 分行比较
    lines1 = clean1.split('\n')
    lines2 = clean2.split('\n')
    
    # 使用difflib比较
    differ = difflib.unified_diff(
        lines1, 
        lines2,
        fromfile='重构前',
        tofile='重构后',
        lineterm=''
    )
    
    differences = list(differ)
    
    if not differences:
        print("\n✅ 输出完全一致！")
        return True
    else:
        print("\n❌ 发现差异：")
        for line in differences[:50]:  # 只显示前50行差异
            print(line)
        
        if len(differences) > 50:
            print(f"\n... 还有 {len(differences) - 50} 行差异")
            
        return False

def extract_key_values(output):
    """提取关键数值用于比较"""
    import re
    
    values = {}
    
    # 提取数据范围
    range_pattern = r"数据范围.*?最小值=([-\d.]+).*?最大值=([-\d.]+)"
    for match in re.finditer(range_pattern, output):
        key = f"range_{len(values)}"
        values[key] = (float(match.group(1)), float(match.group(2)))
    
    # 提取层输出范围
    layer_pattern = r"第(\d+)层输出范围.*?最小值=([-\d.]+).*?最大值=([-\d.]+)"
    for match in re.finditer(layer_pattern, output):
        layer = match.group(1)
        values[f"layer_{layer}"] = (float(match.group(2)), float(match.group(3)))
    
    # 提取修正前后的值
    correction_pattern = r"(修正前|修正后).*?最小值=([-\d.]+).*?最大值=([-\d.]+)"
    for match in re.finditer(correction_pattern, output):
        key = f"{match.group(1)}_{len(values)}"
        values[key] = (float(match.group(2)), float(match.group(3)))
    
    return values

def compare_numerical_values(output1, output2, tolerance=1e-6):
    """比较数值是否在容差范围内一致"""
    
    values1 = extract_key_values(output1)
    values2 = extract_key_values(output2)
    
    print("\n数值比较:")
    
    all_keys = set(values1.keys()) | set(values2.keys())
    
    differences = []
    
    for key in sorted(all_keys):
        if key not in values1:
            differences.append(f"  ❌ {key}: 仅在重构后存在")
        elif key not in values2:
            differences.append(f"  ❌ {key}: 仅在重构前存在")
        else:
            v1_min, v1_max = values1[key]
            v2_min, v2_max = values2[key]
            
            min_diff = abs(v1_min - v2_min)
            max_diff = abs(v1_max - v2_max)
            
            if min_diff > tolerance or max_diff > tolerance:
                differences.append(
                    f"  ❌ {key}: [{v1_min:.6f}, {v1_max:.6f}] vs [{v2_min:.6f}, {v2_max:.6f}]"
                )
            else:
                print(f"  ✓ {key}: 数值一致")
    
    if differences:
        print("\n发现数值差异:")
        for diff in differences:
            print(diff)
        return False
    else:
        print("\n✅ 所有数值在容差范围内一致")
        return True

def main():
    """主函数"""
    
    print("="*60)
    print("推理输出比较工具")
    print("="*60)
    
    # 获取工作目录
    current_dir = Path.cwd()
    before_dir = current_dir.parent / "met_nonlinear_before_refactor"
    
    if not before_dir.exists():
        print(f"❌ 重构前目录不存在: {before_dir}")
        return
    
    # 运行推理
    print("\n1. 运行重构前版本...")
    output_before = run_inference(str(before_dir))
    
    print("\n2. 运行重构后版本...")
    output_after = run_inference(str(current_dir))
    
    if not output_before or not output_after:
        print("\n❌ 无法获取推理输出")
        return
    
    # 保存原始输出用于调试
    with open("output_before.txt", "w", encoding='utf-8') as f:
        f.write(output_before)
    with open("output_after.txt", "w", encoding='utf-8') as f:
        f.write(output_after)
    print("\n输出已保存到 output_before.txt 和 output_after.txt")
    
    # 比较输出
    print("\n3. 比较文本输出...")
    text_match = compare_outputs(output_before, output_after)
    
    print("\n4. 比较数值输出...")
    numerical_match = compare_numerical_values(output_before, output_after)
    
    # 总结
    print("\n" + "="*60)
    print("比较结果总结:")
    print("="*60)
    
    if text_match and numerical_match:
        print("✅ 重构成功！输出完全一致")
    else:
        print("❌ 发现差异，需要进一步调试")
        
        # 提供调试建议
        print("\n调试建议:")
        print("1. 检查 output_before.txt 和 output_after.txt 的完整内容")
        print("2. 特别关注数据范围和层输出的差异")
        print("3. 检查是否有代码逻辑被意外修改")

if __name__ == "__main__":
    main()