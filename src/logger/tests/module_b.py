"""模块 B - 模拟推理和数据处理模块"""

import json

class DataProcessor:
    def __init__(self):
        print("数据处理器初始化")
        self.data = []
        
    def load_data(self, filepath):
        print(f"正在加载数据: {filepath}")
        # 模拟数据加载
        self.data = list(range(100))
        print(f"成功加载 {len(self.data)} 条数据")
        
    def preprocess(self):
        print("开始数据预处理...")
        # 模拟预处理步骤
        print("  - 归一化")
        print("  - 去除异常值")
        print("  - 特征提取")
        print("预处理完成")
        
class InferenceManager:
    def __init__(self, model_path):
        print(f"加载模型: {model_path}")
        self.model_loaded = True
        
    def predict(self, input_data):
        if not self.model_loaded:
            print("错误: 模型未加载")
            return None
            
        print(f"执行推理，输入形状: {len(input_data)}")
        # 模拟推理
        result = [x * 2 for x in input_data]
        print(f"推理完成，输出形状: {len(result)}")
        return result
        
    def batch_predict(self, batch_data):
        print(f"批量推理: {len(batch_data)} 个批次")
        results = []
        for i, batch in enumerate(batch_data):
            print(f"  处理批次 {i+1}/{len(batch_data)}", end="\r")
            results.append(self.predict(batch))
        print()  # 换行
        return results
        
def verbose_operation():
    """模拟详细输出的操作"""
    print("执行详细操作...")
    for step in range(5):
        print(f"  步骤 {step + 1}: 处理中...")
        for substep in ['a', 'b', 'c']:
            print(f"    子步骤 {substep}: 完成")
            
def silent_operation():
    """模拟静默操作（不应该有 print）"""
    # 这里故意不放 print，测试是否正确识别
    result = sum(range(100))
    return result