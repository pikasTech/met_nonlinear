"""测试样本文件，包含各种 print 语句"""

def simple_function():
    print("这是一个简单的 print 语句")
    x = 42
    print(f"x 的值是: {x}")
    
def complex_function():
    data = [1, 2, 3, 4, 5]
    print("处理数据:", data)
    
    for i, value in enumerate(data):
        print(f"索引 {i}: 值 {value}")
        
    # 多参数 print
    print("多个", "参数", "的", "print", sep=" - ")
    
    # 带 end 参数
    print("进度: ", end="")
    for i in range(5):
        print(f"{i}", end=" ")
    print()  # 空 print
    
class TestClass:
    def __init__(self):
        print("初始化 TestClass")
        
    def method(self):
        print(f"调用方法: {self.__class__.__name__}")
        
if __name__ == "__main__":
    print("主程序开始")
    simple_function()
    complex_function()
    obj = TestClass()
    obj.method()
    print("主程序结束")