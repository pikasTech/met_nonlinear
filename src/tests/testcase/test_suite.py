# 测试套件组装模块
import unittest
import os
import importlib
import inspect
import sys
import traceback


def create_test_suite():
    """
    创建包含所有测试用例的测试套件
    自动收集testcase目录下所有test_*.py文件中的测试类
    
    返回:
        unittest.TestSuite: 测试套件对象
    """
    # 获取testcase目录的绝对路径
    testcase_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"正在扫描测试目录: {testcase_dir}")
    
    # 确保testcase包可以被正确导入
    if testcase_dir not in sys.path:
        sys.path.insert(0, os.path.dirname(testcase_dir))
    
    # 使用unittest内置的discover方法查找并加载测试
    print(f"使用unittest.discover自动查找测试模块")
    loader = unittest.TestLoader()
    test_suite = loader.discover(
        start_dir=testcase_dir,
        pattern='test_*.py',
        top_level_dir=os.path.dirname(testcase_dir)
    )
    
    # 打印发现的测试信息
    count = 0
    for suite in test_suite:
        for test_case in suite:
            count += test_case.countTestCases()
    
    print(f"已加载 {count} 个测试用例")
    
    return test_suite
    
    return test_suite


def discover_and_run_tests(verbosity=2, test_names=None):
    """
    发现并运行所有测试
    
    参数:
        verbosity: 测试输出的详细程度 (0-2)
        test_names: 要运行的测试名称列表，如果为None则运行所有测试
    
    返回:
        unittest.TestResult: 测试运行结果
    """
    print("开始收集测试用例...")
    
    # 如果指定了测试名称，则只运行这些测试
    if test_names:
        loader = unittest.TestLoader()
        test_suite = unittest.TestSuite()
        
        for name in test_names:
            try:
                if '.' in name:
                    # 加载特定测试方法，格式如: test_module.TestClass.test_method
                    test = loader.loadTestsFromName(name)
                else:
                    # 加载整个模块
                    if not name.startswith('test_'):
                        name = f'test_{name}'
                    if not name.startswith('testcase.'):
                        name = f'testcase.{name}'
                    
                    test = loader.loadTestsFromName(name)
                test_suite.addTest(test)
                print(f"已加载测试: {name}")
            except Exception as e:
                print(f"加载测试 {name} 失败: {str(e)}")
                traceback.print_exc()
    else:
        # 加载所有测试
        test_suite = create_test_suite()
    
    print("测试套件创建完成，开始执行测试...")
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(test_suite)


if __name__ == '__main__':
    # 设置stdout编码，以避免中文输出问题
    import sys
    import io
    import argparse
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='运行单元测试')
    parser.add_argument('test_names', nargs='*', help='要运行的测试模块名称或测试方法')
    parser.add_argument('-v', '--verbose', action='count', default=1, help='增加输出详细程度')
    args = parser.parse_args()
    
    # 运行测试
    result = discover_and_run_tests(verbosity=args.verbose, test_names=args.test_names)
    
    # 打印结果摘要
    print("\n测试结果摘要:")
    print(f"总测试数: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    print(f"结果: {'成功' if result.wasSuccessful() else '失败'}")
    
    # 设置退出码
    sys.exit(not result.wasSuccessful())
