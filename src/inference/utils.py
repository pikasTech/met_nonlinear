import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\n工具函数模块\n\n此模块包含推理过程中使用的各种工具函数\n'
import os
from typing import List

def get_layer_paths(layer_dir: str) -> List[str]:
    """
    从指定目录获取分层输出文件路径

    参数:
        layer_dir: 分层输出目录路径

    返回:
        List[str]: 分层输出文件路径列表
    """
    if not os.path.exists(layer_dir):
        return []
    layer_paths = []
    for f in sorted(os.listdir(layer_dir)):
        if f.startswith('layer_') and f.endswith('.wave'):
            layer_paths.append(os.path.join(layer_dir, f))
    return layer_paths