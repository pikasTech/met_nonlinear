"""
SPICE偏置补偿配置验证模块
提供严格的形状验证和类型检查功能
"""
import logging
from typing import Dict, Any, Union, List

logger = logging.getLogger(__name__)

def get_layer_output_channels(model: Any, layer_idx: int) -> int:
    """
    获取指定层的输出通道数
    
    Args:
        model: 模型对象
        layer_idx: 层索引
    
    Returns:
        int: 该层的输出通道数
    """
    model_config = model.subcfg
    
    if model_config:
        try:
            return get_expected_channels_from_config(model_config, layer_idx)
        except Exception as e:
            logger.warning(f"无法从配置推断第{layer_idx}层通道数: {e}")
    
    # 保守默认值
    logger.warning(f"无法确定第{layer_idx}层通道数，使用默认值1")
    return 1

def get_expected_channels_from_config(model_subcfg: Dict[str, Any], layer_idx: int) -> int:
    """
    根据WaveNet5配置推断层的输出通道数
    
    Args:
        model_subcfg: 模型子配置
        layer_idx: 层索引
    
    Returns:
        int: 预期的输出通道数
    """
    if layer_idx == 0:  # SVF层
        center_freqs = model_subcfg.get('init_center_freqs', [])
        return len(center_freqs) * 3  # 每个滤波器3个输出：HP、BP、LP
    
    # 获取Dense层数量
    post_dense_layers = model_subcfg.get('post_dense_layers', 3)
    
    if 1 <= layer_idx <= post_dense_layers:  # Dense层
        return model_subcfg.get('post_dense_units', 6)
    
    # 输出层
    if layer_idx == post_dense_layers + 1:
        return 1
    
    # 未知层
    raise ValueError(f"无法识别的层索引: {layer_idx}，模型配置: {model_subcfg}")

def validate_layer_bias_adjustments(layer_adjustments: Dict[str, Any], model: Any) -> None:
    """
    验证层偏置调整配置的形状匹配
    
    Args:
        layer_adjustments: 层偏置调整配置字典
        model: 模型对象
        
    Raises:
        ValueError: 当配置验证失败时
    """
    if not layer_adjustments:
        logger.info("层偏置调整配置为空，跳过验证")
        return
    
    validation_errors = []
    
    for layer_idx_str, adjustment in layer_adjustments.items():
        # 验证层索引格式
        try:
            layer_idx = int(layer_idx_str)
        except ValueError:
            validation_errors.append(f"无效的层索引格式: '{layer_idx_str}'，必须是整数")
            continue
        
        # 验证层索引范围
        if layer_idx < 0:
            validation_errors.append(f"层索引不能为负数: {layer_idx}")
            continue
        
        # 🚨 严格禁止SVF层(层"0")的偏置配置
        if layer_idx == 0:
            validation_errors.append(
                "❌ 禁止对SVF层(层\"0\")进行偏置调整！\n"
                "技术原因: SVFLayer.to_spice()方法完全不支持偏置补偿。\n"
                "虽然配置验证可能通过，但偏置调整在SPICE导出时会被完全忽略。\n"
                "SVF(状态变量滤波器)是纯模拟滤波器电路，不包含任何偏置调整功能。\n"
                "解决方案: 请移除层\"0\"的配置，仅对Dense层(1,2,3)和输出层(4)进行偏置调整。\n"
                "详见技术调查报告: svf_bias_capability_investigation.md"
            )
        
        # 获取期望的通道数
        try:
            expected_channels = get_layer_output_channels(model, layer_idx)
        except Exception as e:
            validation_errors.append(f"无法确定层{layer_idx}的输出通道数: {e}")
            continue
        
        # 验证调整值的类型和形状
        if isinstance(adjustment, (list, tuple)):
            adjustment_len = len(adjustment)
            if adjustment_len != expected_channels:
                validation_errors.append(
                    f"层{layer_idx}补偿值数量({adjustment_len}) "
                    f"与输出通道数({expected_channels})不匹配"
                )
            
            # 验证每个值都是数值类型
            for i, val in enumerate(adjustment):
                if not isinstance(val, (int, float)):
                    validation_errors.append(
                        f"层{layer_idx}补偿值[{i}]类型无效: {type(val).__name__}，"
                        f"期望 int 或 float"
                    )
        
        elif isinstance(adjustment, (int, float)):
            # 标量值：对于多通道层，会广播到所有通道
            logger.debug(f"层{layer_idx}使用标量补偿值{adjustment}，将广播到{expected_channels}个通道")
        
        else:
            validation_errors.append(
                f"层{layer_idx}补偿值类型无效: {type(adjustment).__name__}，"
                f"期望 list、tuple、int 或 float"
            )
    
    # 如果有验证错误，抛出异常
    if validation_errors:
        error_msg = "层偏置调整配置验证失败:\n" + "\n".join(f"  - {error}" for error in validation_errors)
        raise ValueError(error_msg)
    
    logger.info(f"层偏置调整配置验证通过，共{len(layer_adjustments)}层配置")

def validate_bias_compensation_config(config: Dict[str, Any], model: Any = None) -> None:
    """
    验证完整的偏置补偿配置
    
    Args:
        config: 偏置补偿配置
        model: 模型对象（可选）
        
    Raises:
        ValueError: 当配置验证失败时
    """
    if not isinstance(config, dict):
        raise ValueError(f"偏置补偿配置必须是字典类型，当前类型: {type(config).__name__}")
    
    # 检查是否启用
    enabled = config.get('enabled', True)
    if not enabled:
        logger.debug("偏置补偿已禁用，跳过配置验证")
        return
    
    # 检查废弃的配置字段
    if 'bias_adjustment_matrix' in config:
        raise ValueError(
            "❌ 检测到已废弃的 'bias_adjustment_matrix' 字段！\n"
            "此字段已被彻底移除，请使用 'layer_bias_adjustments' 代替。\n"
            "请更新您的配置文件以使用新的配置格式。"
        )
    
    # 验证layer_bias_adjustments
    layer_adjustments = config.get('layer_bias_adjustments', {})
    if not isinstance(layer_adjustments, dict):
        raise ValueError(
            f"'layer_bias_adjustments' 必须是字典类型，"
            f"当前类型: {type(layer_adjustments).__name__}"
        )
    
    # 如果有模型可用，进行形状验证
    if model and layer_adjustments:
        validate_layer_bias_adjustments(layer_adjustments, model)
    elif layer_adjustments:
        logger.warning("缺少模型对象，无法进行形状验证")
    
    logger.info("偏置补偿配置验证完成")

def get_validation_summary(layer_adjustments: Dict[str, Any], model: Any) -> Dict[str, Any]:
    """
    获取验证配置的摘要信息
    
    Args:
        layer_adjustments: 层偏置调整配置
        model: 模型对象
        
    Returns:
        Dict: 包含验证摘要的字典
    """
    summary = {
        'total_layers': len(layer_adjustments),
        'layer_details': {},
        'validation_status': 'unknown'
    }
    
    try:
        for layer_idx_str, adjustment in layer_adjustments.items():
            layer_idx = int(layer_idx_str)
            expected_channels = get_layer_output_channels(model, layer_idx)
            
            if isinstance(adjustment, (list, tuple)):
                actual_values = len(adjustment)
                adjustment_type = 'array'
            else:
                actual_values = 1
                adjustment_type = 'scalar'
            
            summary['layer_details'][layer_idx_str] = {
                'expected_channels': expected_channels,
                'actual_values': actual_values,
                'adjustment_type': adjustment_type,
                'shape_match': actual_values == expected_channels or adjustment_type == 'scalar'
            }
        
        # 执行验证以确定状态
        validate_layer_bias_adjustments(layer_adjustments, model)
        summary['validation_status'] = 'passed'
        
    except ValueError as e:
        summary['validation_status'] = 'failed'
        summary['error_message'] = str(e)
    except Exception as e:
        summary['validation_status'] = 'error'
        summary['error_message'] = f"验证过程发生异常: {e}"
    
    return summary