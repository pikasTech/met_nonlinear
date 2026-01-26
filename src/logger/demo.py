#!/usr/bin/env python3
"""
演示脚本 - 展示日志系统的使用方法
"""

import sys
from pathlib import Path

# 添加 logger 目录到路径
logger_dir = Path(__file__).parent
sys.path.insert(0, str(logger_dir))

from print_checker import PrintUsageScanner
from print_replacer import replace_prints_in_file
from logging_setup import setup_logging, get_module_logger


def demo_print_checker():
    """演示 print 检查器功能"""
    print("\n=== Print 检查器演示 ===")
    
    # 扫描测试目录
    scanner = PrintUsageScanner()
    results = scanner.scan_directory(Path("tests"))
    
    # 生成报告
    report = scanner.generate_report(results)
    print(report)
    

def demo_print_replacer():
    """演示 print 替换器功能"""
    print("\n=== Print 替换器演示 ===")
    
    # 创建一个临时文件
    demo_file = Path("temp_demo.py")
    demo_file.write_text('''
def process_data(data):
    print("开始处理数据...")
    
    if not data:
        print("错误: 数据为空!")
        return None
        
    print(f"处理 {len(data)} 条数据")
    
    for i, item in enumerate(data):
        if i % 10 == 0:
            print(f"进度: {i}/{len(data)}")
            
    print("处理完成!")
    return [x * 2 for x in data]

if __name__ == "__main__":
    data = list(range(50))
    result = process_data(data)
    print(f"结果: {len(result)} 条")
''')
    
    print(f"创建了演示文件: {demo_file}")
    
    # 执行替换
    result = replace_prints_in_file(demo_file, output_path=Path("temp_demo_logged.py"))
    
    if result['success']:
        print(f"成功替换 {result['count']} 个 print 语句")
        print(f"输出文件: temp_demo_logged.py")
        
        # 显示替换后的内容
        print("\n替换后的代码:")
        print("-" * 50)
        print(Path("temp_demo_logged.py").read_text())
    else:
        print(f"替换失败: {result['error']}")
        
    # 清理临时文件
    demo_file.unlink()
    Path("temp_demo_logged.py").unlink(missing_ok=True)


def demo_logging_system():
    """演示日志系统使用"""
    print("\n=== 日志系统演示 ===")
    
    # 设置日志系统
    setup_logging()
    
    # 获取不同模块的 logger
    core_logger = get_module_logger('core')
    training_logger = get_module_logger('core.training')
    inference_logger = get_module_logger('inference')
    
    # 记录不同级别的日志
    core_logger.info("核心模块初始化")
    training_logger.debug("加载训练数据...")
    training_logger.info("开始训练，共 10 个 epoch")
    
    for epoch in range(3):
        training_logger.info(f"Epoch {epoch + 1}/10")
        training_logger.debug(f"  批次处理细节...")
        
        if epoch == 1:
            training_logger.warning("学习率可能过高")
            
    inference_logger.info("模型推理开始")
    inference_logger.error("推理失败: 输入维度不匹配")
    
    core_logger.critical("系统资源不足!")
    

def main():
    """主函数"""
    print("日志系统功能演示")
    print("=" * 60)
    
    # 1. 演示 print 检查
    demo_print_checker()
    
    # 2. 演示 print 替换
    demo_print_replacer()
    
    # 3. 演示日志系统
    demo_logging_system()
    
    print("\n演示完成!")


if __name__ == "__main__":
    main()