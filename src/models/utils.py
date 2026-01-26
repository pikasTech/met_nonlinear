"""
神经网络模型库 - 工具函数模块

此模块包含模型配置和其他通用工具函数。
"""

import logging

# 创建 logger
logger = logging.getLogger(__name__)

def merge_config(default_config, user_config):
    """
    合并默认配置和用户配置

    Args:
        default_config: 默认配置字典
        user_config: 用户传入的配置字典

    Returns:
        merged_config: 合并后的配置字典

    Raises:
        ValueError: 当用户配置包含未定义在默认配置中的键时
    """
    merged_config = default_config.copy()

    # 检查用户配置中是否有未定义在默认配置中的键
    unknown_keys = [key for key in user_config if key not in default_config]
    if unknown_keys:
        raise ValueError(
            f"未知模型子配置项: {', '.join(unknown_keys)}，可用配置项: {', '.join(default_config.keys())}")

    # 合并配置
    for key, value in user_config.items():
        if key in default_config:
            logger.info(f"模型子配置项 '{key}' 的值从 {default_config[key]} 覆盖为 {value}")
            merged_config[key] = value

    return merged_config