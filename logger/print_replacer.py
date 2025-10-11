"""
Print 替换器 - 将 print 语句替换为日志调用

该模块提供了将代码中的 print() 语句自动替换为适当的日志调用的功能。
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import logging


class PrintReplacer(ast.NodeTransformer):
    """
    AST 转换器，将 print() 调用替换为 logging 调用
    """
    
    def __init__(self, logger_name: str = 'metnl', default_level: str = 'INFO'):
        """
        初始化替换器
        
        Args:
            logger_name: 使用的 logger 名称
            default_level: 默认日志级别
        """
        self.logger_name = logger_name
        self.default_level = default_level
        self.imports_needed = set()
        self.replacements = []
        
    def visit_Call(self, node: ast.Call) -> ast.AST:
        """访问函数调用节点"""
        self.generic_visit(node)
        
        # 检查是否是 print 函数
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            # 分析 print 内容，确定合适的日志级别
            level = self._determine_log_level(node)
            
            # 创建 logger 调用
            logger_call = self._create_logger_call(node, level)
            
            # 记录替换
            self.replacements.append({
                'line': node.lineno,
                'col': node.col_offset,
                'level': level,
                'original': ast.unparse(node) if hasattr(ast, 'unparse') else 'print(...)'
            })
            
            return logger_call
            
        return node
        
    def _determine_log_level(self, node: ast.Call) -> str:
        """
        根据 print 内容确定日志级别
        
        Args:
            node: print 调用节点
            
        Returns:
            日志级别字符串
        """
        # 尝试获取第一个参数的字符串内容
        if node.args:
            first_arg = node.args[0]
            
            # 如果是字符串常量
            if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                content = first_arg.value.lower()
                
                # 根据内容模式确定级别 - 优先检查更高级别
                if any(keyword in content for keyword in ['critical', 'fatal', '严重']):
                    return 'CRITICAL'
                elif any(keyword in content for keyword in ['error', 'fail', '错误', '失败']):
                    return 'ERROR'
                elif any(keyword in content for keyword in ['warn', 'warning', '警告']):
                    return 'WARNING'
                elif any(keyword in content for keyword in ['debug', '调试']):
                    return 'DEBUG'
                    
            # 如果是格式化字符串
            elif isinstance(first_arg, ast.JoinedStr):
                # 检查格式化字符串的内容
                for value in first_arg.values:
                    if isinstance(value, ast.Constant) and isinstance(value.value, str):
                        content = value.value.lower()
                        if 'error' in content or '错误' in content:
                            return 'ERROR'
                        elif 'debug' in content or '调试' in content:
                            return 'DEBUG'
                            
        # 检查是否打印到 stderr
        for keyword in node.keywords:
            if keyword.arg == 'file':
                if (isinstance(keyword.value, ast.Attribute) and 
                    keyword.value.attr == 'stderr'):
                    return 'ERROR'
                    
        return self.default_level
        
    def _create_logger_call(self, print_node: ast.Call, level: str) -> ast.Call:
        """
        创建 logger 调用来替代 print
        
        Args:
            print_node: 原始的 print 节点
            level: 日志级别
            
        Returns:
            logger 调用节点
        """
        # 需要导入 logging
        self.imports_needed.add('logging')
        
        # 构建 logger.level() 调用
        logger_attr = ast.Attribute(
            value=ast.Name(id='logger', ctx=ast.Load()),
            attr=level.lower(),
            ctx=ast.Load()
        )
        
        # 处理 print 参数
        new_args = self._convert_print_args(print_node)
        
        # 创建新的调用
        logger_call = ast.Call(
            func=logger_attr,
            args=new_args,
            keywords=[]
        )
        
        # 复制位置信息
        ast.copy_location(logger_call, print_node)
        
        return logger_call
        
    def _convert_print_args(self, print_node: ast.Call) -> List[ast.AST]:
        """
        转换 print 参数为 logger 参数
        
        Args:
            print_node: print 调用节点
            
        Returns:
            转换后的参数列表
        """
        # 处理多个参数的情况
        if len(print_node.args) == 0:
            # print() -> logger.info("")
            return [ast.Constant(value="")]
        elif len(print_node.args) == 1:
            # print(x) -> logger.info(x)
            return print_node.args
        else:
            # print(a, b, c) -> logger.info("%s %s %s", a, b, c)
            # 获取 sep 参数
            sep = ' '
            for keyword in print_node.keywords:
                if keyword.arg == 'sep':
                    if isinstance(keyword.value, ast.Constant):
                        sep = keyword.value.value
                        
            # 创建格式字符串
            format_str = sep.join(['%s'] * len(print_node.args))
            
            return [ast.Constant(value=format_str)] + print_node.args
            
    def get_modified_code(self, source_code: str) -> Tuple[str, List[Dict]]:
        """
        获取修改后的代码
        
        Args:
            source_code: 原始源代码
            
        Returns:
            (修改后的代码, 替换信息列表)
        """
        # 解析 AST
        tree = ast.parse(source_code)
        
        # 应用转换
        modified_tree = self.visit(tree)
        
        # 添加必要的导入
        modified_tree = self._add_imports(modified_tree)
        
        # 添加 logger 初始化
        modified_tree = self._add_logger_init(modified_tree)
        
        # 转换回代码
        if hasattr(ast, 'unparse'):
            modified_code = ast.unparse(modified_tree)
        else:
            # Python < 3.9 的后备方案
            import astor
            modified_code = astor.to_source(modified_tree)
            
        return modified_code, self.replacements
        
    def _add_imports(self, tree: ast.Module) -> ast.Module:
        """添加必要的导入语句"""
        imports_to_add = []
        
        if 'logging' in self.imports_needed:
            import_node = ast.Import(names=[ast.alias(name='logging', asname=None)])
            # 设置位置信息
            import_node.lineno = 1
            import_node.col_offset = 0
            imports_to_add.append(import_node)
            
        # 在开头添加导入
        tree.body = imports_to_add + tree.body
        
        # 更新后续节点的行号
        if imports_to_add:
            for node in tree.body[len(imports_to_add):]:
                if hasattr(node, 'lineno'):
                    node.lineno += len(imports_to_add)
        
        return tree
        
    def _add_logger_init(self, tree: ast.Module) -> ast.Module:
        """添加 logger 初始化代码"""
        # 创建初始化语句列表
        init_statements = []
        
        # 创建 logger = logging.getLogger(__name__)
        logger_init = ast.Assign(
            targets=[ast.Name(id='logger', ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='logging', ctx=ast.Load()),
                    attr='getLogger',
                    ctx=ast.Load()
                ),
                args=[ast.Name(id='__name__', ctx=ast.Load())],
                keywords=[]
            )
        )
        init_statements.append(logger_init)
        
        # 如果是主模块，添加基本的日志配置
        # if __name__ == "__main__": logging.basicConfig(level=logging.INFO)
        main_check = ast.If(
            test=ast.Compare(
                left=ast.Name(id='__name__', ctx=ast.Load()),
                ops=[ast.Eq()],
                comparators=[ast.Constant(value='__main__')]
            ),
            body=[
                ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='logging', ctx=ast.Load()),
                            attr='basicConfig',
                            ctx=ast.Load()
                        ),
                        args=[],
                        keywords=[
                            ast.keyword(
                                arg='level',
                                value=ast.Attribute(
                                    value=ast.Name(id='logging', ctx=ast.Load()),
                                    attr='INFO',
                                    ctx=ast.Load()
                                )
                            )
                        ]
                    )
                )
            ],
            orelse=[]
        )
        init_statements.append(main_check)
        
        # 找到合适的位置插入（在导入语句之后）
        insert_pos = 0
        for i, node in enumerate(tree.body):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                insert_pos = i
                break
        
        # 设置位置信息
        current_lineno = 1
        if insert_pos > 0 and hasattr(tree.body[insert_pos-1], 'lineno'):
            current_lineno = tree.body[insert_pos-1].lineno + 1
        
        # 为每个初始化语句设置位置信息
        for stmt in init_statements:
            stmt.lineno = current_lineno
            stmt.col_offset = 0
            
            # 为所有子节点设置位置信息
            for node in ast.walk(stmt):
                if not hasattr(node, 'lineno'):
                    node.lineno = current_lineno
                    node.col_offset = 0
            
            current_lineno += 1
        
        # 插入所有初始化语句
        for i, stmt in enumerate(init_statements):
            tree.body.insert(insert_pos + i, stmt)
        
        # 更新后续节点的行号
        for node in tree.body[insert_pos + len(init_statements):]:
            if hasattr(node, 'lineno'):
                node.lineno += len(init_statements)
        
        return tree


def replace_prints_in_file(
    filepath: Path,
    output_path: Optional[Path] = None,
    logger_name: str = 'metnl',
    backup: bool = True
) -> Dict:
    """
    替换文件中的 print 语句
    
    Args:
        filepath: 输入文件路径
        output_path: 输出文件路径（None 则覆盖原文件）
        logger_name: logger 名称
        backup: 是否创建备份
        
    Returns:
        替换结果信息
    """
    filepath = Path(filepath)
    
    # 读取文件
    with open(filepath, 'r', encoding='utf-8') as f:
        original_code = f.read()
        
    # 创建替换器
    replacer = PrintReplacer(logger_name)
    
    try:
        # 执行替换
        modified_code, replacements = replacer.get_modified_code(original_code)
        
        # 写入文件
        if output_path is None:
            output_path = filepath
            if backup:
                backup_path = filepath.with_suffix(filepath.suffix + '.bak')
                filepath.rename(backup_path)
                
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(modified_code)
            
        return {
            'success': True,
            'filepath': str(filepath),
            'replacements': replacements,
            'count': len(replacements)
        }
        
    except Exception as e:
        return {
            'success': False,
            'filepath': str(filepath),
            'error': str(e),
            'count': 0
        }


def analyze_print_pattern(filepath: Path) -> Dict[str, int]:
    """
    分析文件中 print 语句的模式
    
    Args:
        filepath: 文件路径
        
    Returns:
        模式统计字典
    """
    patterns = {
        'simple': 0,      # print("text")
        'formatted': 0,   # print(f"...") 或 print("...".format())
        'multi_arg': 0,   # print(a, b, c)
        'with_sep': 0,    # print(..., sep=...)
        'with_end': 0,    # print(..., end=...)
        'to_file': 0,     # print(..., file=...)
        'empty': 0        # print()
    }
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'print':
            # 分析参数
            if len(node.args) == 0:
                patterns['empty'] += 1
            elif len(node.args) == 1:
                arg = node.args[0]
                if isinstance(arg, ast.JoinedStr) or (
                    isinstance(arg, ast.Call) and 
                    isinstance(arg.func, ast.Attribute) and 
                    arg.func.attr == 'format'
                ):
                    patterns['formatted'] += 1
                else:
                    patterns['simple'] += 1
            else:
                patterns['multi_arg'] += 1
                
            # 分析关键字参数
            for keyword in node.keywords:
                if keyword.arg == 'sep':
                    patterns['with_sep'] += 1
                elif keyword.arg == 'end':
                    patterns['with_end'] += 1
                elif keyword.arg == 'file':
                    patterns['to_file'] += 1
                    
    return patterns