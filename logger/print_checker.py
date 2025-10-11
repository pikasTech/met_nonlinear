#!/usr/bin/env python3
"""
Print Checker - 扫描 Python 代码中的 print() 语句使用情况

该工具用于查找项目中所有的 print() 语句，返回文件和行号，
方便后续进行日志系统的替换。
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Set
from collections import defaultdict


class PrintChecker(ast.NodeVisitor):
    """AST 访问器，用于查找 print() 函数调用"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.print_calls: List[Tuple[int, int, str]] = []
        self.current_line = None
        
    def visit_Call(self, node: ast.Call):
        """访问函数调用节点"""
        # 检查是否是 print 函数调用
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            # 获取 print 语句的内容预览
            try:
                # 尝试获取第一个参数的字符串表示
                if node.args:
                    first_arg = ast.get_source_segment(self.source, node.args[0])
                    preview = first_arg[:50] + '...' if len(first_arg) > 50 else first_arg
                else:
                    preview = '(empty)'
            except:
                preview = '(complex expression)'
                
            self.print_calls.append((node.lineno, node.col_offset, preview))
            
        self.generic_visit(node)
        
    def analyze(self, source: str) -> List[Tuple[int, int, str]]:
        """分析源代码并返回 print 调用位置"""
        self.source = source
        try:
            tree = ast.parse(source)
            self.visit(tree)
        except SyntaxError as e:
            print(f"语法错误在文件 {self.filepath}: {e}")
        return self.print_calls


class PrintUsageScanner:
    """扫描目录中的 Python 文件，查找 print() 使用情况"""
    
    def __init__(self, exclude_dirs: Set[str] = None):
        """
        初始化扫描器
        
        Args:
            exclude_dirs: 要排除的目录名称集合
        """
        self.exclude_dirs = exclude_dirs or {
            '__pycache__', '.git', '.pytest_cache', 'venv', 'env',
            'build', 'dist', '.eggs', 'temp', 'cache', '.data'
        }
        
    def scan_file(self, filepath: Path) -> List[Tuple[int, int, str]]:
        """扫描单个文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            checker = PrintChecker(str(filepath))
            return checker.analyze(content)
        except Exception as e:
            print(f"错误读取文件 {filepath}: {e}")
            return []
            
    def scan_directory(self, root_dir: Path) -> Dict[str, List[Tuple[int, int, str]]]:
        """
        扫描目录中的所有 Python 文件
        
        Returns:
            字典，键为文件路径，值为 print 调用列表
        """
        results = defaultdict(list)
        
        for filepath in root_dir.rglob('*.py'):
            # 跳过排除的目录
            if any(excluded in filepath.parts for excluded in self.exclude_dirs):
                continue
                
            print_calls = self.scan_file(filepath)
            if print_calls:
                relative_path = filepath.relative_to(root_dir)
                results[str(relative_path)] = print_calls
                
        return dict(results)
        
    def generate_report(self, scan_results: Dict[str, List[Tuple[int, int, str]]]) -> str:
        """生成扫描报告"""
        if not scan_results:
            return "未找到任何 print() 语句使用。"
            
        report_lines = ["Print 语句使用报告", "=" * 50, ""]
        
        total_prints = 0
        for filepath, print_calls in sorted(scan_results.items()):
            report_lines.append(f"\n文件: {filepath}")
            report_lines.append("-" * (len(filepath) + 6))
            
            for line_no, col_offset, preview in print_calls:
                report_lines.append(f"  行 {line_no:4d}: print({preview})")
                total_prints += 1
                
        report_lines.append(f"\n\n总计: {total_prints} 个 print 语句在 {len(scan_results)} 个文件中")
        
        return '\n'.join(report_lines)
        
    def export_to_json(self, scan_results: Dict[str, List[Tuple[int, int, str]]]) -> Dict:
        """导出为 JSON 格式"""
        json_data = {
            "summary": {
                "total_files": len(scan_results),
                "total_prints": sum(len(calls) for calls in scan_results.values())
            },
            "files": {}
        }
        
        for filepath, print_calls in scan_results.items():
            json_data["files"][filepath] = [
                {
                    "line": line_no,
                    "column": col_offset,
                    "preview": preview
                }
                for line_no, col_offset, preview in print_calls
            ]
            
        return json_data


def main():
    """主函数"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='扫描 Python 代码中的 print() 语句')
    parser.add_argument('path', nargs='?', default='.', 
                        help='要扫描的目录路径（默认为当前目录）')
    parser.add_argument('--exclude', nargs='+', 
                        help='要排除的目录名称')
    parser.add_argument('--json', action='store_true',
                        help='以 JSON 格式输出结果')
    parser.add_argument('--output', '-o', 
                        help='输出文件路径')
    
    args = parser.parse_args()
    
    # 设置排除目录
    exclude_dirs = set()
    if args.exclude:
        exclude_dirs.update(args.exclude)
        
    # 创建扫描器
    scanner = PrintUsageScanner(exclude_dirs)
    
    # 扫描路径
    root_path = Path(args.path).resolve()
    if not root_path.exists():
        print(f"错误: 路径 '{root_path}' 不存在")
        sys.exit(1)
    
    # 判断是文件还是目录
    if root_path.is_file():
        # 单文件扫描
        if not args.json:
            print(f"扫描文件: {root_path}")
        print_calls = scanner.scan_file(root_path)
        results = {root_path.name: print_calls} if print_calls else {}
    else:
        # 目录扫描
        if not args.json:
            print(f"扫描目录: {root_path}")
        results = scanner.scan_directory(root_path)
    
    # 生成输出
    if args.json:
        output = json.dumps(scanner.export_to_json(results), 
                          indent=2, ensure_ascii=False)
    else:
        output = scanner.generate_report(results)
        
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"结果已保存到: {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()