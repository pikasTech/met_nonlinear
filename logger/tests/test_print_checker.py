"""测试 print_checker 模块"""

import pytest
from pathlib import Path
import sys
import tempfile

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from print_checker import PrintChecker, PrintUsageScanner


class TestPrintChecker:
    """测试 PrintChecker 类"""
    
    def test_simple_print_detection(self):
        """测试简单 print 语句检测"""
        code = '''
def hello():
    print("Hello, World!")
'''
        checker = PrintChecker("test.py")
        results = checker.analyze(code)
        
        assert len(results) == 1
        assert results[0][0] == 3  # 行号
        assert "Hello, World!" in results[0][2]  # 预览内容
        
    def test_multiple_prints(self):
        """测试多个 print 语句"""
        code = '''
print("First")
x = 10
print(f"Value: {x}")
for i in range(3):
    print(i)
'''
        checker = PrintChecker("test.py")
        results = checker.analyze(code)
        
        assert len(results) == 3
        assert results[0][0] == 2  # print("First")
        assert results[1][0] == 4  # print(f"Value: {x}")
        assert results[2][0] == 6  # print(i)
        
    def test_empty_print(self):
        """测试空 print()"""
        code = '''
print()
print("")
print("text")
'''
        checker = PrintChecker("test.py")
        results = checker.analyze(code)
        
        assert len(results) == 3
        assert results[0][2] == "(empty)"  # print()
        
    def test_complex_print_args(self):
        """测试复杂参数的 print"""
        code = '''
data = [1, 2, 3]
print("Data:", data, "Length:", len(data))
print(*data, sep=", ")
'''
        checker = PrintChecker("test.py")
        results = checker.analyze(code)
        
        assert len(results) == 2
        
    def test_no_prints(self):
        """测试没有 print 的代码"""
        code = '''
def add(a, b):
    return a + b
    
result = add(1, 2)
'''
        checker = PrintChecker("test.py")
        results = checker.analyze(code)
        
        assert len(results) == 0


class TestPrintUsageScanner:
    """测试 PrintUsageScanner 类"""
    
    def test_scan_directory(self, temp_dir):
        """测试目录扫描"""
        # 创建测试文件
        file1 = temp_dir / "file1.py"
        file1.write_text('''
print("File 1")
def func():
    print("Inside function")
''')
        
        file2 = temp_dir / "file2.py"
        file2.write_text('''
# No prints here
x = 10
y = 20
''')
        
        file3 = temp_dir / "subdir" / "file3.py"
        file3.parent.mkdir()
        file3.write_text('''
print("File 3 in subdir")
''')
        
        # 扫描目录
        scanner = PrintUsageScanner()
        results = scanner.scan_directory(temp_dir)
        
        assert len(results) == 2  # file1 和 file3 有 print
        assert "file1.py" in results
        assert str(Path("subdir/file3.py")) in results
        assert "file2.py" not in results  # 没有 print
        
    def test_exclude_directories(self, temp_dir):
        """测试排除目录功能"""
        # 创建测试结构
        (temp_dir / "__pycache__").mkdir()
        cache_file = temp_dir / "__pycache__" / "test.py"
        cache_file.write_text('print("Should be excluded")')
        
        normal_file = temp_dir / "normal.py"
        normal_file.write_text('print("Should be included")')
        
        # 扫描
        scanner = PrintUsageScanner()
        results = scanner.scan_directory(temp_dir)
        
        assert "normal.py" in results
        assert "__pycache__" not in str(results)
        
    def test_generate_report(self):
        """测试报告生成"""
        scan_results = {
            "module1.py": [(10, 0, "Hello"), (20, 0, "World")],
            "module2.py": [(5, 0, "Debug info")]
        }
        
        scanner = PrintUsageScanner()
        report = scanner.generate_report(scan_results)
        
        assert "Print 语句使用报告" in report
        assert "module1.py" in report
        assert "module2.py" in report
        assert "总计: 3 个 print 语句在 2 个文件中" in report
        
    def test_empty_report(self):
        """测试空报告"""
        scanner = PrintUsageScanner()
        report = scanner.generate_report({})
        
        assert "未找到任何 print() 语句使用" in report
        
    def test_export_to_json(self):
        """测试 JSON 导出"""
        scan_results = {
            "test.py": [(10, 4, "Test message")]
        }
        
        scanner = PrintUsageScanner()
        json_data = scanner.export_to_json(scan_results)
        
        assert json_data["summary"]["total_files"] == 1
        assert json_data["summary"]["total_prints"] == 1
        assert "test.py" in json_data["files"]
        assert json_data["files"]["test.py"][0]["line"] == 10
        assert json_data["files"]["test.py"][0]["preview"] == "Test message"
        
    def test_syntax_error_handling(self, temp_dir, capsys):
        """测试语法错误处理"""
        bad_file = temp_dir / "bad.py"
        bad_file.write_text('''
def bad_func(
    print("This has syntax error")
''')
        
        scanner = PrintUsageScanner()
        results = scanner.scan_directory(temp_dir)
        
        # 应该处理错误而不崩溃
        captured = capsys.readouterr()
        assert "语法错误" in captured.out


@pytest.mark.parametrize("code,expected_count", [
    ('print("test")', 1),
    ('print("a"); print("b")', 2),
    ('logger.info("not a print")', 0),
    ('# print("commented")', 0),
    ('"""print("in docstring")"""', 0),
])
def test_print_detection_patterns(code, expected_count):
    """测试各种 print 模式的检测"""
    checker = PrintChecker("test.py")
    results = checker.analyze(code)
    assert len(results) == expected_count