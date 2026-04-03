"""
外部项目路径解析器

支持多种路径格式：
1. 完整路径: projects/project/external/task-type/task-name
2. 相对路径: project/task-type/task-name
3. 简化路径: project/task-name (自动检测task-type)
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import logging
import os

logger = logging.getLogger(__name__)


@dataclass
class ExternalPath:
    """外部项目路径数据结构"""
    project_name: str
    task_type: str
    task_name: str
    full_path: Path
    config_path: Path
    output_path: Path

    @property
    def external_dir(self) -> Path:
        """获取外部项目根目录"""
        return Path("projects") / self.project_name / "external"

    @property
    def task_dir(self) -> Path:
        """获取任务目录"""
        return self.external_dir / self.task_type / self.task_name


class ExternalPathParser:
    """外部项目路径解析器"""
    
    SUPPORTED_TASK_TYPES = [
        'freq-response-compare',
        'freq-response-compensator',
        'bias-visualization', 
        'waveform-analysis',
        'wnet5-circuit-validation',
        'data-analysis',
        'model-export',
        'performance-benchmark',
        'ablation-study',
        'compare'
    ]
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        初始化路径解析器
        
        Args:
            base_dir: 基础目录，默认为当前工作目录
        """
        self.base_dir = base_dir or Path.cwd()
    
    def parse(self, path_str: str) -> ExternalPath:
        """
        解析可视化项目路径
        
        支持的路径格式：
        1. 完整训练项目格式: projects/{project_name}/visualization/{task_type}/{task_name}
        2. 相对训练项目格式: {project_name}/{task_type}/{task_name}
        3. 简化训练项目格式: {project_name}/{task_name}
        4. 独立可视化项目格式: visualization/projects/{task_type}/{task_name}
        5. 绝对路径格式: 任意绝对路径
        
        Args:
            path_str: 路径字符串
            
        Returns:
            ExternalPath: 解析后的路径对象
            
        Raises:
            ValueError: 路径格式不正确
        """
        # 规范化路径
        path_str = path_str.replace('\\', '/').strip('/').strip()

        # 处理 ex_projects 独立可视化路径: ex_projects/visualization/{task_type}/{task_name}
        if path_str.startswith('ex_projects/visualization/'):
            parts = path_str.split('/')
            if len(parts) < 4:
                raise ValueError(f"ex_projects 路径格式错误: {path_str}")
            task_type = parts[2]
            task_name = parts[3]
            if task_type not in self.SUPPORTED_TASK_TYPES:
                raise ValueError(f"不支持的任务类型'{task_type}'，支持的类型: {self.SUPPORTED_TASK_TYPES}")
            project_name = task_name
            full_path = self.base_dir / path_str
            config_path = full_path / 'config.json'
            # 输出目录应为该任务目录下的 data 子目录
            output_path = full_path / 'data'
            return ExternalPath(
                project_name=project_name,
                task_type=task_type,
                task_name=task_name,
                full_path=full_path,
                config_path=config_path,
                output_path=output_path
            )
        
        logger.debug(f"解析路径: {path_str}")

        # 如果用户路径以 /data 结尾 (例如 .../freq-response-compensator/TaskX/data)
        # 期望该 data 目录即为输出目录，而不是再追加一层 /data
        data_suffix = False
        if path_str.endswith('/data'):
            data_suffix = True
            base_path_str = path_str[:-5].rstrip('/')  # 去掉末尾 /data
        else:
            base_path_str = path_str
        
        # 支持任何路径格式 - 通用解析逻辑
        try:
            ep = self._parse_universal_path(base_path_str)
            if data_suffix:
                # 覆盖输出目录：保持 config 放在主体目录，输出在主体目录/data
                ep.output_path = ep.full_path / 'data'
            return ep
        except Exception as e:
            logger.error(f"路径解析失败: {e}")
            self._show_path_format_help()
            raise
    
    def _is_independent_visualization_path(self, path_str: str) -> bool:
        """检查是否为独立可视化项目路径格式: visualization/projects/{task_type}/{task_name}"""
        parts = path_str.split('/')
        return (len(parts) >= 4 and 
                parts[0] == 'visualization' and 
                parts[1] == 'projects' and
                parts[2] in self.SUPPORTED_TASK_TYPES)
    
    def _is_absolute_path(self, path_str: str) -> bool:
        """检查是否为绝对路径格式（任意绝对路径）"""
        return os.path.isabs(path_str.replace('/', os.sep))
    
    def _is_full_training_path(self, path_str: str) -> bool:
        """检查是否为完整训练项目路径格式"""
        parts = path_str.split('/')
        return (len(parts) >= 5 and 
                parts[0] == 'projects' and 
                parts[2] == 'visualization')

    def _is_relative_training_path(self, path_str: str) -> bool:
        """检查是否为相对训练项目路径格式"""
        parts = path_str.split('/')
        return (len(parts) == 3 and 
                parts[1] in self.SUPPORTED_TASK_TYPES)

    def _is_simple_training_path(self, path_str: str) -> bool:
        """检查是否为简化训练项目路径格式"""
        parts = path_str.split('/')
        return len(parts) == 2
    
    def _parse_independent_visualization_path(self, path_str: str) -> ExternalPath:
        """解析独立可视化项目路径: visualization/projects/{task_type}/{task_name}"""
        parts = path_str.split('/')
        if len(parts) < 4:
            raise ValueError(f"独立可视化路径格式错误，期望至少4个部分: {path_str}")
        
        if parts[0] != 'visualization' or parts[1] != 'projects':
            raise ValueError(f"独立可视化路径必须以'visualization/projects'开头: {path_str}")
        
        task_type = parts[2]
        task_name = parts[3]
        
        if task_type not in self.SUPPORTED_TASK_TYPES:
            raise ValueError(f"不支持的任务类型'{task_type}'，支持的类型: {self.SUPPORTED_TASK_TYPES}")
        
        # 对于独立可视化项目，项目名称就是任务名称
        project_name = task_name
        
        return self._build_independent_path_object(path_str, project_name, task_type, task_name)
    
    def _parse_absolute_path(self, path_str: str) -> ExternalPath:
        """解析绝对路径格式"""
        abs_path = Path(path_str)
        
        # 尝试从路径中提取信息
        parts = abs_path.parts
        
        # 查找可能的任务类型
        task_type = None
        task_name = None
        
        for i, part in enumerate(parts):
            if part in self.SUPPORTED_TASK_TYPES:
                task_type = part
                if i + 1 < len(parts):
                    task_name = parts[i + 1]
                break
        
        if not task_type:
            # 如果无法从路径推断，使用默认值。
            task_type = 'freq-response-compare'
            task_name = abs_path.name or 'default-task'

        # 保证非 None
        if task_name is None:
            task_name = 'default-task'
        project_name = task_name or 'default-project'
        
        return self._build_absolute_path_object(abs_path, project_name, task_type, task_name)
    
    def _parse_full_training_path(self, path_str: str) -> ExternalPath:
        """解析完整训练项目路径: projects/project/visualization/task-type/task-name"""
        parts = path_str.split('/')
        if len(parts) < 5:
            raise ValueError(f"完整路径格式错误，期望至少5个部分: {path_str}")
        
        if parts[0] != 'projects':
            raise ValueError(f"完整路径必须以'projects'开头: {path_str}")
        
        if parts[2] != 'visualization':
            raise ValueError(f"完整路径第三部分必须是'visualization': {path_str}")
        
        project_name = parts[1]
        task_type = parts[3]
        task_name = parts[4]
        
        if task_type not in self.SUPPORTED_TASK_TYPES:
            raise ValueError(f"不支持的任务类型'{task_type}'，支持的类型: {self.SUPPORTED_TASK_TYPES}")
        
        return self._build_training_path_object(project_name, task_type, task_name)
    
    def _parse_relative_training_path(self, path_str: str) -> ExternalPath:
        """解析相对训练项目路径: project/task-type/task-name"""
        parts = path_str.split('/')
        if len(parts) != 3:
            raise ValueError(f"相对路径必须是3个部分: {path_str}")
        
        project_name, task_type, task_name = parts
        
        if task_type not in self.SUPPORTED_TASK_TYPES:
            raise ValueError(f"不支持的任务类型'{task_type}'，支持的类型: {self.SUPPORTED_TASK_TYPES}")
        
        return self._build_training_path_object(project_name, task_type, task_name)
    
    def _parse_simple_training_path(self, path_str: str) -> ExternalPath:
        """解析简化训练项目路径: project/task-name (自动检测task-type)"""
        parts = path_str.split('/')
        if len(parts) != 2:
            raise ValueError(f"简化路径必须是2个部分: {path_str}")
        
        project_name, task_name = parts
        task_type = self._detect_task_type(project_name, task_name)
        
        return self._build_training_path_object(project_name, task_type, task_name)
    
    def _detect_task_type(self, project_name: str, task_name: str) -> str:
        """
        自动检测任务类型
        
        基于任务名称中的关键词来推断任务类型
        """
        task_name_lower = task_name.lower()
        
        # 频率响应对比关键词
        freq_keywords = ['freq', 'frequency', 'response', 'compare', 'comparison', 'baseline']
        if any(keyword in task_name_lower for keyword in freq_keywords):
            return 'freq-response-compare'
        
        # 偏置可视化关键词
        bias_keywords = ['bias', 'offset', 'drift']
        if any(keyword in task_name_lower for keyword in bias_keywords):
            return 'bias-visualization'
        
        # 波形分析关键词
        wave_keywords = ['wave', 'waveform', 'signal', 'time']
        if any(keyword in task_name_lower for keyword in wave_keywords):
            return 'waveform-analysis'
        
        # 默认返回频率响应对比（最常用）
        logger.warning(f"无法自动检测任务类型，使用默认类型'freq-response-compare'")
        return 'freq-response-compare'
    
    def _build_independent_path_object(self, original_path: str, project_name: str, task_type: str, task_name: str) -> ExternalPath:
        """构建独立可视化项目路径对象"""
        # 使用原始路径作为基础
        full_path = self.base_dir / original_path
        config_path = full_path / "config.json"
        output_path = full_path / "data"
        
        return ExternalPath(
            project_name=project_name,
            task_type=task_type,
            task_name=task_name,
            full_path=full_path,
            config_path=config_path,
            output_path=output_path
        )
    
    def _build_absolute_path_object(self, abs_path: Path, project_name: str, task_type: str, task_name: str) -> ExternalPath:
        """构建绝对路径对象"""
        config_path = abs_path / "config.json"
        output_path = abs_path / "data"
        
        return ExternalPath(
            project_name=project_name,
            task_type=task_type,
            task_name=task_name,
            full_path=abs_path,
            config_path=config_path,
            output_path=output_path
        )
    
    def _build_training_path_object(self, project_name: str, task_type: str, task_name: str) -> ExternalPath:
        """构建训练项目相关的路径对象"""
        # 构建基础路径
        external_dir = Path("projects") / project_name / "external"
        task_dir = external_dir / task_type / task_name
        
        # 构建完整路径
        full_path = self.base_dir / task_dir
        config_path = full_path / "config.json"
        output_path = full_path / "data"
        
        return ExternalPath(
            project_name=project_name,
            task_type=task_type,
            task_name=task_name,
            full_path=full_path,
            config_path=config_path,
            output_path=output_path
        )
    
    def _parse_universal_path(self, path_str: str) -> ExternalPath:
        """通用路径解析 - 支持任何路径格式"""
        parts = path_str.split('/')

        # 处理 compare/{task_name} 短格式 (自动转换为 ex_projects/compare/{task_name})
        if len(parts) == 2 and parts[0] in self.SUPPORTED_TASK_TYPES:
            task_type = parts[0]
            task_name = parts[1]
            project_name = task_name
            full_path = Path(self.base_dir) / 'ex_projects' / path_str
            config_path = full_path / 'config.json'
            output_path = full_path / 'data'
            return ExternalPath(
                project_name=project_name,
                task_type=task_type,
                task_name=task_name,
                config_path=config_path,
                output_path=output_path,
                full_path=full_path
            )

        # 处理 ex_projects/{task_type}/{task_name} 格式 (如 ex_projects/compare/mae_vs_afmae)
        if len(parts) >= 3 and parts[0] == 'ex_projects' and parts[1] in self.SUPPORTED_TASK_TYPES:
            task_type = parts[1]
            task_name = parts[2]
            project_name = task_name
            full_path = Path(self.base_dir) / path_str
            config_path = full_path / 'config.json'
            output_path = full_path / 'data'
            return ExternalPath(
                project_name=project_name,
                task_type=task_type,
                task_name=task_name,
                config_path=config_path,
                output_path=output_path,
                full_path=full_path
            )

        # 优先匹配独立可视化路径 visualization/projects/{task_type}/{task_name}
        if len(parts) >= 4 and parts[0] == 'visualization' and parts[1] == 'projects' and parts[2] in self.SUPPORTED_TASK_TYPES:
            task_type = parts[2]
            task_name = parts[3]
            project_name = task_name  # 独立项目约定 project_name == task_name
            full_path = Path(self.base_dir) / path_str
            config_path = full_path / 'config.json'
            output_path = full_path / 'data'
            return ExternalPath(
                project_name=project_name,
                task_type=task_type,
                task_name=task_name,
                config_path=config_path,
                output_path=output_path,
                full_path=full_path
            )
        
        # 提取路径信息
        if len(parts) >= 3:
            # 尝试识别任务类型
            task_type = None
            project_name = None
            task_name = None
            
            # 从路径中查找已知的任务类型
            for i, part in enumerate(parts):
                if part in self.SUPPORTED_TASK_TYPES:
                    task_type = part
                    if i > 0:
                        project_name = parts[i-1]
                    if i < len(parts) - 1:
                        task_name = parts[i+1]
                    break
            
            # 如果没有找到任务类型，使用默认值
            if not task_type:
                # 使用最后一个部分作为任务名，倒数第二个作为项目名
                if len(parts) >= 2:
                    project_name = parts[-2]
                    task_name = parts[-1]
                    task_type = 'wnet5-circuit-validation'  # 默认任务类型
                else:
                    project_name = parts[0]
                    task_name = 'default-task'
                    task_type = 'wnet5-circuit-validation'
            
            # 如果仍然缺少信息，使用路径片段填充
            if not project_name:
                project_name = parts[0] if parts else 'default-project'
            if not task_name:
                task_name = parts[-1] if parts else 'default-task'
                
        else:
            # 路径太短，使用默认值
            project_name = parts[0] if parts else 'default-project'
            task_name = parts[-1] if len(parts) > 1 else 'default-task'
            task_type = 'wnet5-circuit-validation'
        
    # 构建完整路径
        full_path = Path(self.base_dir) / path_str
        config_path = full_path / "config.json"
        output_path = full_path / "data"
        
        return ExternalPath(
            project_name=project_name,
            task_type=task_type,
            task_name=task_name,
            config_path=config_path,
            output_path=output_path,
            full_path=full_path
        )
    
    def _show_path_format_help(self):
        """显示路径格式帮助信息"""
        help_text = """
外部项目路径格式说明：

1. 独立外部项目格式：
   external/projects/{task_type}/{task_name}
   例: external/projects/freq-response-compare/PS-5-190_vs_PS-5-360

2. 完整训练项目格式：
   projects/{project_name}/external/{task_type}/{task_name}
   例: projects/LSTMu32al_rs300_ex2/external/freq-response-compare/baseline-comparison

3. 相对训练项目格式：
   {project_name}/{task_type}/{task_name}
   例: LSTMu32al_rs300_ex2/freq-response-compare/baseline-comparison

4. 简化训练项目格式（自动检测任务类型）：
   {project_name}/{task_name}
   例: LSTMu32al_rs300_ex2/baseline-comparison

5. 绝对路径格式：
   任意绝对路径（自动检测任务类型）
   例: C:/work/my-external-project/freq-response-task

支持的任务类型：
   - freq-response-compare: 频率响应对比
    - freq-response-compensator: 补偿器传递函数(基于linear_response.json)
   - bias-visualization: 偏置可视化  
   - waveform-analysis: 波形分析
   - wnet5-circuit-validation: WNET5电路验证
        """
        logger.info(help_text)


def validate_project_name(project_name: str) -> bool:
    """验证项目名称格式"""
    if not project_name:
        return False
    
    # 项目名称应该只包含字母、数字、下划线和连字符
    import re
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, project_name))


def validate_task_name(task_name: str) -> bool:
    """验证任务名称格式"""
    if not task_name:
        return False
    
    # 任务名称应该只包含字母、数字、下划线和连字符
    import re
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, task_name))


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.DEBUG)
    
    parser = ExternalPathParser()
    
    # 测试不同的路径格式
    test_paths = [
        "projects/LSTMu32al_rs300_ex2/visualization/freq-response-compare/baseline-comparison",
        "LSTMu32al_rs300_ex2/freq-response-compare/baseline-comparison", 
        "LSTMu32al_rs300_ex2/baseline-comparison"
    ]
    
    for path_str in test_paths:
        try:
            result = parser.parse(path_str)
            print(f"✅ 解析成功: {path_str}")
            print(f"   项目: {result.project_name}")
            print(f"   类型: {result.task_type}")
            print(f"   任务: {result.task_name}")
            print(f"   配置: {result.config_path}")
            print(f"   输出: {result.output_path}")
            print()
        except Exception as e:
            print(f"❌ 解析失败: {path_str}")
            print(f"   错误: {e}")
            print()