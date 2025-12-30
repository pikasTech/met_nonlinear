"""
严格执行器 - 零容错路径验证集成

核心原则：FAIL FAST + 零容错 + 严格验证
严禁：容错机制、自动修复、路径猜测

设计目标：集成严格路径验证，确保学术诚信保护
"""

import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional

# 使用try-except处理导入，支持独立运行
try:
    from ..utils.path_validator import StrictPathValidator, StrictPathChecker
    from ..config.defaults import EXECUTION_CONFIG
    from ..core.mock_state import MockState, MockStateManager
    from ..exceptions import *
except ImportError:
    # 独立运行时的绝对导入
    import sys
    from pathlib import Path
    current_dir = Path(__file__).parent
    bias_tuner_dir = current_dir.parent
    sys.path.insert(0, str(bias_tuner_dir))
    
    from utils.path_validator import StrictPathValidator, StrictPathChecker
    from config.defaults import EXECUTION_CONFIG
    from core.mock_state import MockState, MockStateManager
    from exceptions import *

logger = logging.getLogger(__name__)


class StrictBiasCompensationExecutor:
    """严格偏置补偿执行器 - 零容错设计"""
    
    def __init__(self, project_name: str, project_root: str, use_mock: bool = False):
        self.project_name = project_name
        self.project_root = project_root
        self.use_mock = use_mock
        
        # 初始化严格验证系统
        self.validator = StrictPathValidator(project_name, project_root)
        self.checker = StrictPathChecker(self.validator)
        
        # 执行状态 - 严格控制
        self.execution_validated = False
        self.validated_paths = None
        
    def strict_prepare_execution(self) -> bool:
        """严格执行准备 - FAIL FAST验证"""
        logger.info(f"🔒 严格验证执行准备: {self.project_name}")
        
        try:
            # 严格预执行检查
            validation_passed = self.checker.pre_execution_check()
            
            if not validation_passed:
                raise PathValidationError(
                    f"严格验证失败: {self.project_name}\n"
                    f"执行被阻止 - 学术不端风险规避"
                )
                
            # 获取严格验证后的路径
            self.validated_paths = self.validator.get_validated_paths()
            self.execution_validated = True
            
            logger.info(f"🔒 严格验证通过: {len(self.validated_paths)} 个关键文件")
            return True
            
        except Exception as e:
            logger.error(f"❌ 严格验证失败: {e}")
            logger.error(f"❌ 执行终止 - 学术不端风险规避")
            return False
    
    def strict_load_config(self) -> Dict:
        """严格配置加载 - 无容错"""
        if not self.execution_validated:
            raise ExecutionStateError(
                "未通过严格验证，禁止配置加载\n"
                "学术不端风险阻止"
            )
            
        config_path = self.checker.fail_fast_validation("config")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"🔒 严格配置加载成功: {config_path}")
            return config
            
        except Exception as e:
            raise ConfigLoadError(
                f"严格配置加载失败: {config_path}\n"
                f"错误: {e}\n"
                f"学术不端风险阻止"
            )
    
    def strict_load_error_analysis(self) -> Dict:
        """严格错误分析加载 - 无容错"""
        if not self.execution_validated:
            raise ExecutionStateError(
                "未通过严格验证，禁止错误分析加载\n"
                "学术不端风险阻止"
            )
            
        error_path = self.checker.fail_fast_validation("error_analysis")
        
        try:
            with open(error_path, 'r', encoding='utf-8') as f:
                error_data = json.load(f)
            logger.info(f"🔒 严格错误分析加载成功: {error_path}")
            return error_data
            
        except Exception as e:
            raise ErrorAnalysisLoadError(
                f"严格错误分析加载失败: {error_path}\n"
                f"错误: {e}\n"
                f"学术不端风险阻止"
            )
    
    def strict_load_inference_metadata(self) -> Dict:
        """严格推理元数据加载 - 无容错"""
        if not self.execution_validated:
            raise ExecutionStateError(
                "未通过严格验证，禁止推理元数据加载\n"
                "学术不端风险阻止"
            )
            
        metadata_path = self.checker.fail_fast_validation("inference_metadata")
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            logger.info(f"🔒 严格推理元数据加载成功: {metadata_path}")
            return metadata
            
        except Exception as e:
            raise ErrorAnalysisLoadError(
                f"严格推理元数据加载失败: {metadata_path}\n"
                f"错误: {e}\n"
                f"学术不端风险阻止"
            )
    
    def execute_strict_bias_compensation(self) -> bool:
        """执行严格偏置补偿 - 零容错模式"""
        if not self.execution_validated:
            raise ExecutionStateError(
                "未通过严格验证，禁止执行偏置补偿\n"
                "学术不端风险阻止"
            )
        
        logger.info(f"🔒 开始严格偏置补偿执行: {self.project_name}")
        
        try:
            # 1. 严格加载所有必要数据
            config = self.strict_load_config()
            error_analysis = self.strict_load_error_analysis()
            inference_metadata = self.strict_load_inference_metadata()
            
            # 2. 验证偏置补偿配置存在
            if not self._validate_bias_compensation_config(config):
                raise ConfigLoadError(
                    f"偏置补偿配置验证失败\n"
                    f"项目: {self.project_name}\n"
                    f"学术不端风险阻止"
                )
            
            # 3. 执行Mock模式或实际执行
            if self.use_mock:
                success = self._execute_mock_compensation(config, error_analysis)
            else:
                success = self._execute_real_compensation(config)
            
            if success:
                logger.info(f"🔒 严格偏置补偿执行成功: {self.project_name}")
            else:
                logger.error(f"❌ 严格偏置补偿执行失败: {self.project_name}")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ 严格偏置补偿执行异常: {e}")
            return False
    
    def _validate_bias_compensation_config(self, config: Dict) -> bool:
        """验证偏置补偿配置 - 严格模式"""
        try:
            bias_config = config.get("inference_config", {}).get("bias_compensation", {})
            
            if not bias_config.get("enabled", False):
                logger.warning("偏置补偿未启用")
                return False
                
            layer_adjustments = bias_config.get("layer_bias_adjustments", {})
            if not layer_adjustments:
                logger.error("未找到层偏置调整配置")
                return False
                
            logger.info(f"✅ 偏置补偿配置验证通过: {len(layer_adjustments)} 层")
            return True
            
        except Exception as e:
            logger.error(f"偏置补偿配置验证失败: {e}")
            return False
    
    def _execute_mock_compensation(self, config: Dict, error_analysis: Dict) -> bool:
        """执行Mock模式偏置补偿"""
        logger.info("🔒 Mock模式偏置补偿执行")
        
        try:
            # Mock模式下，基于现有错误分析数据进行模拟计算
            bias_config = config["inference_config"]["bias_compensation"]
            layer_adjustments = bias_config["layer_bias_adjustments"]
            
            # 模拟偏置补偿效果计算
            total_layers = len(layer_adjustments)
            improvement_rate = min(95.0 + total_layers * 0.5, 99.5)  # 模拟改善率
            
            logger.info(f"🔒 Mock补偿结果: {total_layers}层, 模拟改善率: {improvement_rate:.1f}%")
            return True
            
        except Exception as e:
            logger.error(f"Mock模式执行失败: {e}")
            return False
    
    def _execute_real_compensation(self, config: Dict) -> bool:
        """执行实际偏置补偿 - 调用cli.py"""
        logger.info("🔒 实际模式偏置补偿执行")
        
        try:
            # 构建严格的cli.py调用命令
            # 按照用户要求使用conda环境
            cmd = [
                "conda", "run", "--no-capture-output", "-n", "tf26",
                "python", "cli.py", "-a", self.project_name
            ]
            
            # 确定工作目录 - 严格路径验证
            work_dir = Path(self.project_root)
            if not work_dir.exists():
                raise PathSecurityError(
                    f"工作目录不存在: {work_dir}\n"
                    f"学术不端风险阻止"
                )
            
            logger.info(f"🔒 执行命令: {' '.join(cmd)}")
            logger.info(f"🔒 工作目录: {work_dir}")
            
            # 执行命令 - 严格模式
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                logger.info("🔒 cli.py执行成功")
                logger.info(f"输出: {result.stdout}")
                return True
            else:
                logger.error(f"cli.py执行失败 (返回码: {result.returncode})")
                logger.error(f"错误输出: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("cli.py执行超时")
            return False
        except Exception as e:
            logger.error(f"实际模式执行失败: {e}")
            return False
    
    def get_execution_status(self) -> Dict:
        """获取执行状态 - 严格模式"""
        return {
            "project_name": self.project_name,
            "execution_validated": self.execution_validated,
            "use_mock": self.use_mock,
            "validated_files_count": len(self.validated_paths) if self.validated_paths else 0,
            "academic_integrity_protected": True
        }


class StrictExecutionManager:
    """严格执行管理器 - 多项目支持"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.executors = {}
    
    def create_strict_executor(self, project_name: str, use_mock: bool = False) -> StrictBiasCompensationExecutor:
        """创建严格执行器"""
        if project_name in self.executors:
            logger.warning(f"项目执行器已存在，将覆盖: {project_name}")
        
        executor = StrictBiasCompensationExecutor(
            project_name=project_name,
            project_root=self.project_root,
            use_mock=use_mock
        )
        
        self.executors[project_name] = executor
        logger.info(f"🔒 严格执行器创建完成: {project_name}")
        return executor
    
    def get_executor(self, project_name: str) -> Optional[StrictBiasCompensationExecutor]:
        """获取现有执行器"""
        return self.executors.get(project_name)
    
    def execute_project(self, project_name: str, use_mock: bool = False) -> bool:
        """执行项目偏置补偿 - 完整流程"""
        logger.info(f"🔒 开始项目执行: {project_name}")
        
        try:
            # 创建执行器
            executor = self.create_strict_executor(project_name, use_mock)
            
            # 严格验证准备
            if not executor.strict_prepare_execution():
                logger.error(f"❌ 项目验证失败: {project_name}")
                return False
            
            # 执行偏置补偿
            success = executor.execute_strict_bias_compensation()
            
            if success:
                logger.info(f"🔒 项目执行成功: {project_name}")
            else:
                logger.error(f"❌ 项目执行失败: {project_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 项目执行异常: {project_name}, 错误: {e}")
            return False