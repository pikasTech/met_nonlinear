import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\nSVF层导出SPICE模型示例\n\n这个脚本展示如何使用模型层中的SVFLayer导出SPICE模型\n'
from models.model_layers import SVFLayer
import os
import sys
import numpy as np
import tensorflow as tf
from pathlib import Path
import traceback
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

def create_test_svf_layer():
    """创建一个测试用的SVF层"""
    input_shape = (None, 1)
    inputs = tf.keras.Input(shape=input_shape[1:])
    x = inputs
    model = tf.keras.Model(inputs=inputs, outputs=x)
    center_freqs = [10.0, 50.0, 100.0]
    quality_factors = [1.0, 0.707, 2.0]
    svf_layer = SVFLayer(keras_model=model, layer_name='SVF_Test_Layer', center_freqs=center_freqs, quality_factors=quality_factors)
    return svf_layer

def main():
    """主函数"""
    try:
        output_dir = Path('temp')
        output_dir.mkdir(exist_ok=True)
        svf_layer = create_test_svf_layer()
        spice_model_path = output_dir / 'svf_model.cir'
        opamp_config = {'model': 'ideal', 'include_file': None, 'power_pins': True, 'params': {}}
        svf_layer.to_spice(output_path=str(spice_model_path), opamp_config=opamp_config, use_e96=True)
        logger.info(f'SVF层已成功导出到SPICE模型: {spice_model_path}')
    except Exception as e:
        logger.info(f'执行过程中出错: {str(e)}')
        traceback.print_exc()
if __name__ == '__main__':
    main()