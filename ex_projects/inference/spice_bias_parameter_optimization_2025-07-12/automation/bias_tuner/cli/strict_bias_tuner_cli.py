#!/usr/bin/env python3
"""
严格偏置调谐器CLI - 零容错路径验证

核心原则：FAIL FAST + 学术诚信保护 + 严格验证
严禁：容错机制、路径猜测、模糊匹配

设计目标：防止学术不端问题，确保精确路径验证
"""

import argparse
import sys
import os
from pathlib import Path
import logging

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
bias_tuner_dir = current_dir.parent
sys.path.insert(0, str(bias_tuner_dir))

# 直接导入文件，避免__init__.py的依赖问题
import importlib.util

# 直接导入path_validator.py
spec_path_validator = importlib.util.spec_from_file_location(
    "path_validator", 
    bias_tuner_dir / "utils" / "path_validator.py"
)
path_validator_module = importlib.util.module_from_spec(spec_path_validator)
spec_path_validator.loader.exec_module(path_validator_module)

# 直接导入strict_executor.py
spec_strict_executor = importlib.util.spec_from_file_location(
    "strict_executor", 
    bias_tuner_dir / "core" / "strict_executor.py"
)
strict_executor_module = importlib.util.module_from_spec(spec_strict_executor)
spec_strict_executor.loader.exec_module(strict_executor_module)

# 直接导入exceptions.py
spec_exceptions = importlib.util.spec_from_file_location(
    "exceptions", 
    bias_tuner_dir / "exceptions.py"
)
exceptions_module = importlib.util.module_from_spec(spec_exceptions)
spec_exceptions.loader.exec_module(exceptions_module)

# 重新导入必要的类
StrictPathValidator = path_validator_module.StrictPathValidator
StrictPathChecker = path_validator_module.StrictPathChecker
StrictBiasCompensationExecutor = strict_executor_module.StrictBiasCompensationExecutor
StrictExecutionManager = strict_executor_module.StrictExecutionManager

# 导入异常
AcademicIntegrityError = exceptions_module.AcademicIntegrityError
StrictValidationError = exceptions_module.StrictValidationError
PathSecurityError = exceptions_module.PathSecurityError

logger = logging.getLogger(__name__)


def create_strict_cli_parser():
    """创建严格CLI参数解析器"""
    parser = argparse.ArgumentParser(
        description="严格偏置调谐器 - 零容错SPICE偏置补偿工具\n⚠️  学术诚信保护模式：严禁容错机制",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
严格模式示例:
  strict_bias_tuner_cli.py WNET5q1h2u6l3 --root /path/to/project --execute
  strict_bias_tuner_cli.py WNET5q1h2u6l3 --root /path/to/project --validate-only
  
⚠️  注意：此工具使用零容错验证，任何路径或文件问题都会立即失败
        """
    )
    
    parser.add_argument(
        "project_name",
        help="项目名称 (如 WNET5q1h2u6l3) - 必须精确匹配"
    )
    
    parser.add_argument(
        "--root", "-r",
        required=True,
        help="项目根目录绝对路径 - 必需参数"
    )
    
    parser.add_argument(
        "--execute", "-e",
        action="store_true",
        help="执行偏置补偿 (包含严格验证)"
    )
    
    parser.add_argument(
        "--validate-only", "-v",
        action="store_true",
        help="仅执行严格验证，不运行补偿"
    )
    
    parser.add_argument(
        "--mock", "-m",
        action="store_true",
        help="使用模拟模式 (仍需严格验证)"
    )
    
    parser.add_argument(
        "--fail-fast", "-f",
        action="store_true",
        default=True,
        help="快速失败模式 (默认启用)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出模式"
    )
    
    return parser


def strict_validate_arguments(args):
    """严格验证命令行参数"""
    # 验证项目根目录
    root_path = Path(args.root).resolve()
    if not root_path.exists():
        raise FileNotFoundError(
            f"项目根目录不存在: {root_path}\n"
            f"严格验证失败 - 学术不端风险阻止"
        )
    
    # 验证项目名称格式
    if not args.project_name.strip():
        raise ValueError(
            "项目名称不能为空\n"
            "严格验证失败 - 学术不端风险阻止"
        )
    
    # 验证操作模式
    if not (args.execute or args.validate_only):
        raise ValueError(
            "必须指定操作模式: --execute 或 --validate-only\n"
            "严格验证失败 - 学术不端风险阻止"
        )
    
    return root_path


def setup_strict_logging(verbose: bool = False):
    """设置严格日志模式"""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # 创建格式化器
    formatter = logging.Formatter(
        '🔒 [严格模式] %(asctime)s - %(name)s - %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def print_strict_validation_report(project_name: str, validation_passed: bool):
    """打印严格验证报告"""
    print("\n" + "=" * 70)
    print(f"🔒 严格验证报告: {project_name}")
    print("=" * 70)
    
    if validation_passed:
        print("✅ 项目路径验证: 通过")
        print("✅ JSON文件完整性: 通过")
        print("✅ 结构一致性验证: 通过")
        print("✅ 学术诚信检查: 通过")
        print(f"\n🔒 严格验证状态: 全部通过")
        print(f"🔒 执行准备状态: 就绪")
    else:
        print("❌ 严格验证状态: 失败")
        print("❌ 执行准备状态: 被阻止")
        print("⚠️  学术不端风险规避")
    
    print("=" * 70)


def main():
    """严格CLI主入口函数"""
    parser = create_strict_cli_parser()
    args = parser.parse_args()
    
    try:
        # 设置严格日志模式
        setup_strict_logging(args.verbose)
        
        logger.info(f"🔒 严格偏置调谐器启动: {args.project_name}")
        logger.warning("⚠️  零容错模式：任何验证失败都会立即终止")
        
        # 严格验证命令行参数
        project_root = strict_validate_arguments(args)
        logger.info(f"🔒 命令行参数验证通过")
        
        # 创建严格执行管理器
        execution_manager = StrictExecutionManager(str(project_root))
        
        # 严格验证模式
        if args.validate_only:
            logger.info(f"🔍 严格验证模式: {args.project_name}")
            
            # 创建执行器进行验证
            executor = execution_manager.create_strict_executor(
                args.project_name, 
                use_mock=args.mock
            )
            
            validation_passed = executor.strict_prepare_execution()
            
            # 打印详细验证报告
            print_strict_validation_report(args.project_name, validation_passed)
            
            if validation_passed:
                logger.info(f"🔒 严格验证完成: {args.project_name}")
                
                # 获取执行状态
                status = executor.get_execution_status()
                logger.info(f"🔒 验证文件数量: {status['validated_files_count']}")
                logger.info(f"🔒 学术诚信保护: {status['academic_integrity_protected']}")
                
                sys.exit(0)
            else:
                logger.error(f"❌ 严格验证失败: {args.project_name}")
                sys.exit(1)
                
        # 严格执行模式
        elif args.execute:
            logger.info(f"🚀 严格执行模式: {args.project_name}")
            logger.warning("⚠️  执行前进行完整严格验证")
            
            # 执行完整流程
            success = execution_manager.execute_project(
                args.project_name, 
                use_mock=args.mock
            )
            
            if success:
                logger.info(f"🔒 严格执行完成: {args.project_name}")
                print(f"\n🎉 项目 {args.project_name} 严格偏置补偿执行成功")
                print("🔒 学术诚信保护：已确保所有文件验证通过")
                sys.exit(0)
            else:
                logger.error(f"❌ 严格执行失败: {args.project_name}")
                print(f"\n❌ 项目 {args.project_name} 严格偏置补偿执行失败")
                print("🔒 学术诚信保护：执行被安全终止")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.warning(f"\n🛑 用户中断严格执行")
        sys.exit(130)
        
    except (FileNotFoundError, ValueError, KeyError, RuntimeError) as e:
        logger.error(f"❌ 严格验证错误: {e}")
        print(f"\n❌ 严格验证失败")
        print(f"错误详情: {e}")
        print("🔒 学术诚信保护：执行被安全阻止")
        sys.exit(1)
        
    except (AcademicIntegrityError, StrictValidationError, PathSecurityError) as e:
        logger.error(f"❌ 学术诚信保护错误: {e}")
        print(f"\n❌ 学术诚信保护触发")
        print(f"错误详情: {e}")
        print("🔒 执行被严格安全机制阻止")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ 严格执行失败: {e}")
        logger.error(f"❌ 学术不端风险规避 - 执行终止")
        print(f"\n❌ 严格执行异常")
        print(f"错误详情: {e}")
        print("🔒 学术诚信保护：系统安全终止")
        sys.exit(1)


if __name__ == "__main__":
    main()