"""模块 C - 模拟复杂打印场景和错误处理"""

import sys
import traceback

class ComplexPrinter:
    def __init__(self, name):
        self.name = name
        print(f"{self.__class__.__name__} 初始化: {name}")
        
    def multi_line_print(self):
        """多行打印测试"""
        print("""这是一个
多行
打印测试""")
        
    def formatted_print(self):
        """格式化打印测试"""
        data = {'key1': 'value1', 'key2': 42, 'key3': [1, 2, 3]}
        print(f"格式化数据: {data}")
        print("表格式输出:")
        print("-" * 40)
        for key, value in data.items():
            print(f"{key:10} | {str(value):20}")
        print("-" * 40)
        
    def conditional_print(self, verbose=True):
        """条件打印"""
        if verbose:
            print("详细模式: 显示所有信息")
            print("  - 配置加载完成")
            print("  - 环境检查通过")
        else:
            # 静默模式下不打印
            pass
            
    def print_to_stderr(self):
        """打印到标准错误流"""
        print("这是标准输出")
        print("这是错误输出", file=sys.stderr)
        
    def print_with_flush(self):
        """带刷新的打印"""
        print("实时输出: ", end="", flush=True)
        for i in range(5):
            print(f"{i} ", end="", flush=True)
        print("完成!")
        
def exception_handler():
    """异常处理中的打印"""
    try:
        # 模拟错误
        result = 1 / 0
    except ZeroDivisionError as e:
        print(f"捕获异常: {e}")
        print("错误详情:")
        traceback.print_exc()
        
def progress_bar(total=100):
    """进度条打印"""
    print("开始处理...")
    for i in range(0, total + 1, 10):
        progress = i / total
        bar = '#' * int(progress * 20)
        spaces = ' ' * (20 - len(bar))
        print(f"\r[{bar}{spaces}] {i}%", end="")
    print("\n处理完成!")
    
def nested_function_calls():
    """嵌套函数调用中的打印"""
    def inner_function():
        print("  内部函数打印")
        
    print("外部函数开始")
    inner_function()
    print("外部函数结束")
    
class ContextPrinter:
    """上下文管理器中的打印"""
    def __enter__(self):
        print("进入上下文")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("退出上下文")
        if exc_type:
            print(f"上下文中发生异常: {exc_type.__name__}")