import json
import os

# 定义数据文件路径
# boxplot_data.json 包含灵敏度和自然频率的统计信息（最小值、中位数、最大值）
# nonlinearity_data.json 包含非线性误差及模型参数信息
boxplot_path = os.path.join('paper/image_data', 'boxplot_data.json')
nonlinearity_path = os.path.join('paper/image_data', 'nonlinearity_data.json')

def load_data(path):
    """
    从指定路径加载JSON数据
    
    Args:
        path: JSON文件路径
    Returns:
        解析后的JSON数据
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 加载箱线图数据和非线性数据
boxplot_data = load_data(boxplot_path)
nonlinearity_data = load_data(nonlinearity_path)

def calculate_drift(metric):
    """
    计算参数漂移程度
    
    科学含义: 使用中位数与极值间的最大差值作为漂移指标
    这种方法假设中位数代表稳定值，与极值间的最大距离反映了漂移程度
    
    评价: 这种计算较为简化，未考虑分布的形状和离群值的影响
         更严谨的方法可能需要考虑标准差或四分位距
    
    Args:
        metric: 包含'min', 'median', 'max'键的字典
    Returns:
        计算出的漂移值
    """
    median = metric['median']
    return max(abs(metric['max'] - median), abs(median - metric['min']))

# 计算原始模型的基准漂移值和非线性误差
# 这些值将用作比较基准来计算改进百分比
origin_sens = calculate_drift(boxplot_data['ORIGIN']['sensitivity'])
origin_nf = calculate_drift(boxplot_data['ORIGIN']['natural_frequency'])
origin_nonlinearity = nonlinearity_data['ORIGIN']['nonlinearity_mean']

# 创建Markdown表格的表头
header = [
    "| Model            | Parameters | Sensitivity Drift Suppression (%) | Natural Frequency Suppression (%) | Nonlinearity Error Suppression (%) |",
    "|------------------|------------|-----------------------------------|------------------------------------|-------------------------------------|"
]

rows = []
for model in nonlinearity_data:
    if model == "ORIGIN":
        continue
    
    # 获取基础数据
    params = nonlinearity_data[model]['total_params']
    model_nonlinearity = nonlinearity_data[model]['nonlinearity_mean']
    
    # 计算各项指标
    # 科学含义: 计算各模型相对于原始模型的抑制率(改进百分比)
    # 评价: 这种相对比较方法适合评估改进效果，但当原始值接近0时可能导致数值不稳定
    #      未考虑统计显著性，理想情况下应包含置信区间或p值
    nonlinearity_suppress = (origin_nonlinearity - model_nonlinearity) / origin_nonlinearity * 100
    sens_drift = calculate_drift(boxplot_data[model]['sensitivity'])
    nf_drift = calculate_drift(boxplot_data[model]['natural_frequency'])
    sens_suppress = (origin_sens - sens_drift) / origin_sens * 100
    nf_suppress = (origin_nf - nf_drift) / origin_nf * 100
    
    # 带千位分隔符的参数显示
    formatted_params = f"{params:,}"
    
    # 构建表格行
    row = (
        f"| {model:<16} | {formatted_params:>9} | {sens_suppress:>29.2f}% | "
        f"{nf_suppress:>24.2f}% | {nonlinearity_suppress:>27.2f}% |"
    )
    rows.append(row)

# 按参数量排序（从小到大）
# 评价: 按参数量排序有助于分析模型复杂度与性能间的关系，但可能忽略其他重要因素
sorted_rows = sorted(rows, key=lambda x: int(x.split('|')[2].strip().replace(',', '')))

# 生成最终表格
result_table = header + sorted_rows
print('\n'.join(result_table))


origin_nonlinearity = nonlinearity_data['ORIGIN']['nonlinearity_mean']

# 打印 ORIGIN 系统的参数变化范围信息
print("\n===== ORIGIN系统参数变化范围 =====")
print(f"灵敏度(sensitivity):")
print(f"  - 最小值: {boxplot_data['ORIGIN']['sensitivity']['min']}")
print(f"  - 中位数: {boxplot_data['ORIGIN']['sensitivity']['median']}")
print(f"  - 最大值: {boxplot_data['ORIGIN']['sensitivity']['max']}")
print(f"  - 漂移量: {origin_sens}")

print(f"\n自然频率(natural_frequency):")
print(f"  - 最小值: {boxplot_data['ORIGIN']['natural_frequency']['min']}")
print(f"  - 中位数: {boxplot_data['ORIGIN']['natural_frequency']['median']}")
print(f"  - 最大值: {boxplot_data['ORIGIN']['natural_frequency']['max']}")
print(f"  - 漂移量: {origin_nf}")

print(f"\n非线性误差(nonlinearity):")
print(f"  - 平均值: {origin_nonlinearity}")
print("===============================\n")
