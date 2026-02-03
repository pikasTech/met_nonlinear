"""测试 print_replacer 模块"""

import pytest
import ast
from pathlib import Path
import tempfile

from print_replacer import (
    PrintReplacer, replace_prints_in_file, analyze_print_pattern
)


class TestPrintReplacer:
    """测试 PrintReplacer 类"""
    
    def test_simple_print_replacement(self):
        """测试简单 print 替换"""
        code = '''
def hello():
    print("Hello, World!")
'''
        replacer = PrintReplacer()
        modified_code, replacements = replacer.get_modified_code(code)
        
        assert "import logging" in modified_code
        assert "logger = logging.getLogger(__name__)" in modified_code
        # 检查 logger.info 调用，忽略引号类型
        assert "logger.info(" in modified_code
        assert "Hello, World!" in modified_code
        assert len(replacements) == 1
        
    def test_error_level_detection(self):
        """测试错误级别检测"""
        code = '''
print("Error: Something went wrong")
print("WARNING: This is a warning")
print("Debug info here")
print("CRITICAL: System failure")
print("Normal message")
'''
        replacer = PrintReplacer()
        modified_code, replacements = replacer.get_modified_code(code)
        
        # 检查日志调用，忽略引号类型
        assert "logger.error(" in modified_code and "Error: Something went wrong" in modified_code
        assert "logger.warning(" in modified_code and "WARNING: This is a warning" in modified_code
        assert "logger.debug(" in modified_code and "Debug info here" in modified_code
        assert "logger.critical(" in modified_code and "CRITICAL: System failure" in modified_code
        assert "logger.info(" in modified_code and "Normal message" in modified_code
        
        # 检查替换记录
        assert replacements[0]['level'] == 'ERROR'
        assert replacements[1]['level'] == 'WARNING'
        assert replacements[2]['level'] == 'DEBUG'
        assert replacements[3]['level'] == 'CRITICAL'
        assert replacements[4]['level'] == 'INFO'
        
    def test_formatted_string_replacement(self):
        """测试格式化字符串替换"""
        code = '''
x = 42
print(f"The value is {x}")
name = "test"
print(f"Error in {name}: failed")
'''
        replacer = PrintReplacer()
        modified_code, replacements = replacer.get_modified_code(code)
        
        # 检查格式化字符串，忽略引号类型
        assert "logger.info(f" in modified_code and "The value is" in modified_code
        assert "logger.error(f" in modified_code and "Error in" in modified_code and "failed" in modified_code
        
    def test_multi_arg_print(self):
        """测试多参数 print 替换"""
        code = '''
a, b, c = 1, 2, 3
print(a, b, c)
print("Values:", a, b, c)
'''
        replacer = PrintReplacer()
        modified_code, replacements = replacer.get_modified_code(code)
        
        # 多参数应该转换为格式化字符串
        assert "logger.info(" in modified_code
        assert "%s %s %s" in modified_code
        assert "a, b, c)" in modified_code
        
    def test_print_with_sep(self):
        """测试带 sep 参数的 print"""
        code = '''
print("A", "B", "C", sep=" - ")
'''
        replacer = PrintReplacer()
        modified_code, replacements = replacer.get_modified_code(code)
        
        # 应该使用正确的分隔符
        assert "logger.info(" in modified_code
        assert "%s - %s - %s" in modified_code
        
    def test_stderr_print(self):
        """测试打印到 stderr"""
        code = '''
import sys
print("Error output", file=sys.stderr)
'''
        replacer = PrintReplacer()
        modified_code, replacements = replacer.get_modified_code(code)
        
        # stderr 应该使用 error 级别
        assert "logger.error(" in modified_code and "Error output" in modified_code
        assert replacements[0]['level'] == 'ERROR'
        
    def test_empty_print(self):
        """测试空 print()"""
        code = '''
print()
print("")
'''
        replacer = PrintReplacer()
        modified_code, replacements = replacer.get_modified_code(code)
        
        assert "logger.info(" in modified_code
        assert '""' in modified_code or "''" in modified_code
        assert len(replacements) == 2
        
    def test_preserve_indentation(self):
        """测试保持缩进"""
        code = '''
class MyClass:
    def method(self):
        if True:
            print("Indented print")
'''
        replacer = PrintReplacer()
        modified_code, replacements = replacer.get_modified_code(code)
        
        # 应该保持正确的缩进
        lines = modified_code.split('\n')
        for i, line in enumerate(lines):
            if 'logger.info(' in line and 'Indented print' in line:
                assert line.startswith('            ')  # 12 个空格缩进
                
    def test_multiple_imports_handling(self):
        """测试处理已有导入的情况"""
        code = '''
import os
import sys

print("Test")
'''
        replacer = PrintReplacer()
        modified_code, replacements = replacer.get_modified_code(code)
        
        # logging 导入应该在其他导入之后
        lines = modified_code.split('\n')
        import_lines = [i for i, line in enumerate(lines) if line.startswith('import')]
        logger_init_line = [i for i, line in enumerate(lines) if 'logger = ' in line][0]
        
        # logger 初始化应该在所有导入之后
        assert logger_init_line > max(import_lines)


class TestReplacePrintsInFile:
    """测试文件级别的 print 替换"""
    
    def test_replace_in_file(self, temp_dir):
        """测试替换文件中的 print"""
        # 创建测试文件
        test_file = temp_dir / "test.py"
        original_content = '''
def main():
    print("Starting program")
    result = calculate()
    print(f"Result: {result}")
    
def calculate():
    print("Calculating...")
    return 42
'''
        test_file.write_text(original_content)
        
        # 执行替换
        result = replace_prints_in_file(test_file)
        
        assert result['success']
        assert result['count'] == 3
        
        # 检查文件内容
        modified_content = test_file.read_text()
        assert "import logging" in modified_content
        assert "logger.info" in modified_content
        assert "print(" not in modified_content
        
    def test_replace_with_backup(self, temp_dir):
        """测试带备份的替换"""
        test_file = temp_dir / "test.py"
        original_content = 'print("Test")'
        test_file.write_text(original_content)
        
        # 执行替换
        result = replace_prints_in_file(test_file, backup=True)
        
        assert result['success']
        
        # 检查备份文件
        backup_file = test_file.with_suffix('.py.bak')
        assert backup_file.exists()
        assert backup_file.read_text() == original_content
        
    def test_replace_to_different_file(self, temp_dir):
        """测试输出到不同文件"""
        input_file = temp_dir / "input.py"
        output_file = temp_dir / "output.py"
        
        input_file.write_text('print("Test")')
        
        # 执行替换
        result = replace_prints_in_file(input_file, output_path=output_file)
        
        assert result['success']
        assert output_file.exists()
        assert "logger.info" in output_file.read_text()
        assert input_file.read_text() == 'print("Test")'  # 原文件未改变
        
    def test_syntax_error_handling(self, temp_dir):
        """测试语法错误处理"""
        test_file = temp_dir / "bad.py"
        test_file.write_text('''
def bad_function(
    print("Syntax error")
''')
        
        result = replace_prints_in_file(test_file)
        
        assert not result['success']
        assert 'error' in result


class TestAnalyzePrintPattern:
    """测试 print 模式分析"""
    
    def test_pattern_analysis(self, temp_dir):
        """测试模式分析功能"""
        test_file = temp_dir / "patterns.py"
        test_file.write_text('''
# Various print patterns
print("Simple")
print(f"Formatted {x}")
print("Multiple", "args", "here")
print("With sep", "test", sep=", ")
print("No newline", end="")
print("To file", file=f)
print()
''')
        
        patterns = analyze_print_pattern(test_file)
        
        # 验证模式计数
        assert patterns['simple'] >= 1  # 至少有一个简单 print
        assert patterns['formatted'] == 1
        assert patterns['multi_arg'] >= 1  # 至少有一个多参数
        assert patterns['with_sep'] == 1
        assert patterns['with_end'] == 1
        assert patterns['to_file'] == 1
        assert patterns['empty'] == 1
        
    def test_no_prints_pattern(self, temp_dir):
        """测试没有 print 的文件"""
        test_file = temp_dir / "no_prints.py"
        test_file.write_text('''
def add(a, b):
    return a + b
''')
        
        patterns = analyze_print_pattern(test_file)
        
        # 所有计数应该为 0
        assert all(count == 0 for count in patterns.values())


@pytest.mark.parametrize("print_stmt,expected_level", [
    ('print("Error: failed")', 'ERROR'),
    ('print("错误：失败")', 'ERROR'),
    ('print("Warning: check this")', 'WARNING'),
    ('print("DEBUG: value = 1")', 'DEBUG'),
    ('print("Info message")', 'INFO'),
    ('print("FATAL: crash")', 'CRITICAL'),
])
def test_level_detection_patterns(print_stmt, expected_level):
    """测试各种级别检测模式"""
    code = f'''
{print_stmt}
'''
    replacer = PrintReplacer()
    _, replacements = replacer.get_modified_code(code)
    
    assert replacements[0]['level'] == expected_level