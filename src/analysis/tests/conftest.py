"""
pytest配置文件，提供公共的fixture和配置
"""

import pytest
import sys
from pathlib import Path

# 将项目根目录添加到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))