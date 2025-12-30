"""
Custom exceptions for bias tuner.
Provides specific exception types for better error handling and debugging.
"""


class BiasTunerError(Exception):
    """Base exception class for all bias tuner errors."""
    pass


class ConfigurationError(BiasTunerError):
    """Raised when there are configuration-related errors."""
    pass


class ProjectNotFoundError(ConfigurationError):
    """Raised when project directory or files are not found."""
    pass


class InvalidConfigError(ConfigurationError):
    """Raised when configuration format or values are invalid."""
    pass


class InferenceError(BiasTunerError):
    """Raised when inference execution fails."""
    pass


class InferenceTimeoutError(InferenceError):
    """Raised when inference execution times out."""
    pass


class AnalysisError(BiasTunerError):
    """Raised when error analysis fails."""
    pass


class AnalysisDataError(AnalysisError):
    """Raised when analysis data is missing or invalid."""
    pass


class CompensationError(BiasTunerError):
    """Raised when compensation calculation fails."""
    pass


class InvalidLayerError(CompensationError):
    """Raised when attempting to compensate invalid layer."""
    pass


class ConvergenceError(CompensationError):
    """Raised when optimization fails to converge."""
    pass


class MockModeError(BiasTunerError):
    """Raised when there are mock mode related errors."""
    pass


class InvalidMockStateError(MockModeError):
    """Raised when invalid mock state is requested."""
    pass


class MockResourcesError(MockModeError):
    """Raised when mock resources are missing or invalid."""
    pass


class ExecutionError(BiasTunerError):
    """Raised when command execution fails."""
    pass


class CommandNotFoundError(ExecutionError):
    """Raised when required command or executable is not found."""
    pass


# 严格验证和学术诚信保护异常
class AcademicIntegrityError(BiasTunerError):
    """学术诚信保护异常 - 防止严重的学术不端问题"""
    pass


class StrictValidationError(AcademicIntegrityError):
    """严格验证错误 - 零容错验证失败"""
    pass


class PathSecurityError(AcademicIntegrityError):
    """路径安全错误 - 防止读取错误文件"""
    pass


class PathValidationError(StrictValidationError):
    """路径验证错误 - 精确路径验证失败"""
    pass


class ConfigLoadError(StrictValidationError):
    """配置加载错误 - 严格配置验证失败"""
    pass


class ErrorAnalysisLoadError(StrictValidationError):
    """错误分析加载错误 - 严格数据验证失败"""
    pass


class ExecutionStateError(StrictValidationError):
    """执行状态错误 - 严格执行状态验证失败"""
    pass


class ProjectDiscoveryError(PathSecurityError):
    """项目发现错误 - 项目结构验证失败"""
    pass