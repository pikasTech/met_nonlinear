"""
自定义模型层模块

此模块提供了各种自定义模型层的实现，用于特定模型的构建。
"""
# 标准库导入
import sys
import logging
from pathlib import Path

# 第三方库导入
import numpy as np
import tensorflow as tf
from tensorflow.keras import models, layers
from models.layer_support import LayeredModelSupport, SpiceModelSupport
from calibration_analyzer.wavedata import WaveData

# 类型注解导入
from typing import List, Dict, Any, Tuple, Optional, Union

# 创建 logger
logger = logging.getLogger(__name__)

# 添加spice_simulator目录到sys.path
try:
    # 尝试找到spice_simulator目录并添加到sys.path
    current_dir = Path.cwd()
    root_dir = current_dir
    while root_dir.name and not (root_dir / "spice_simulator").exists():
        root_dir = root_dir.parent

    spice_simulator_dir = root_dir / "spice_simulator"
    if spice_simulator_dir.exists():
        sys.path.append(str(spice_simulator_dir))
except Exception:
    pass

# 导入spice_simulator模块
try:
    from spice_simulator.circuit_svf import SVFFilter
except ImportError:
    SVFFilter = None  # 使用None表示未能成功导入

try:
    from spice_simulator.circuit_dense import DenseCircuitFactory
except ImportError:
    DenseCircuitFactory = None  # 使用None表示未能成功导入


class BaseLayerModel:
    """
    基础层模型，所有自定义层模型都继承自此类
    """

    def __init__(self, keras_model, layer_name: str, layer_type: str):
        """
        初始化基础层模型

        Args:
            keras_model: 封装的Keras模型
            layer_name: 层名称
            layer_type: 层类型标识符
        """
        self.model = keras_model
        self.name = layer_name
        self.type = layer_type

    def __call__(self, inputs):
        """
        使层模型可调用，实际调用底层Keras模型

        Args:
            inputs: 输入张量

        Returns:
            模型输出
        """
        return self.model(inputs)

    def __getattr__(self, name):
        """
        拦截属性访问，对于不存在的属性尝试从model对象获取

        Args:
            name: 属性名称

        Returns:
            请求的属性
        """
        # 如果属性不在当前实例中，尝试从model中获取
        if hasattr(self.model, name):
            return getattr(self.model, name)
        raise AttributeError(f"'{self.__class__.__name__}' 对象没有属性 '{name}'")

    def get_weights(self):
        """
        获取底层模型的权重

        Returns:
            模型权重列表
        """
        return self.model.get_weights()

    def set_weights(self, weights):
        """
        设置底层模型的权重

        Args:
            weights: 权重列表
        """
        self.model.set_weights(weights)

    def get_config(self):
        """
        获取层配置

        Returns:
            配置字典
        """
        return {
            'name': self.name,
            'type': self.type
        }

    def get_layer_info(self) -> Dict[str, Any]:
        """
        获取层信息

        Returns:
            层信息字典
        """
        return {
            'name': self.name,
            'type': self.type,
            'input_shape': self.model.input_shape,
            'output_shape': self.model.output_shape
        }

    def get_layer(self, name=None, index=None):
        """
        获取指定的层

        Args:
            name: 层名称
            index: 层索引

        Returns:
            找到的层
        """
        return self.model.get_layer(name=name, index=index)

    def summary(self, line_length=None, positions=None, print_fn=None):
        """
        打印模型摘要

        Args:
            line_length: 行长度
            positions: 各列位置
            print_fn: 打印函数
        """
        return self.model.summary(line_length=line_length, positions=positions, print_fn=print_fn)

    def predict(self, *args, **kwargs):
        """
        转发调用到模型的预测方法
        """
        kwargs.pop('use_scaler', None)
        return self.model.predict(*args, **kwargs)

    def get_inner_layers(self) -> List[layers.Layer]:
        """
        获取模型内部的所有层

        Returns:
            List[layers.Layer]: 模型内部的所有层
        """
        return self.model.layers

    # 以下属性直接代理到model对象，方便外部访问
    @property
    def input_shape(self):
        """获取输入形状"""
        return self.model.input_shape

    @property
    def output_shape(self):
        """获取输出形状"""
        return self.model.output_shape

    @property
    def trainable_weights(self):
        """获取可训练权重"""
        return self.model.trainable_weights

    @property
    def non_trainable_weights(self):
        """获取不可训练权重"""
        return self.model.non_trainable_weights

    @property
    def layers(self):
        """获取模型的层"""
        return self.model.layers

    @property
    def inputs(self):
        """获取模型输入"""
        return self.model.inputs

    @property
    def outputs(self):
        """获取模型输出"""
        return self.model.outputs

    @property
    def input(self):
        """获取模型输入张量"""
        return self.model.input

    @property
    def output(self):
        """获取模型输出张量"""
        return self.model.output


class SVFLayer(BaseLayerModel, SpiceModelSupport):
    """
    状态变量滤波器(SVF)层，用于包装IIR滤波器层

    支持导出SVF SPICE模型，SVF SPICE模型在 circuit_svf.py ，参考: 对svf 的测试和扫频在 test_svf.py 和 simu_svf_sweep.py
    """

    def __init__(self, keras_model, layer_name: str = "SVF_Layer",
                 center_freqs: List[float] = None, quality_factors: List[float] = None):
        """
        初始化SVF层模型

        Args:
            keras_model: 封装的Keras模型，通常是IIR滤波器模型
            layer_name: 层名称
            center_freqs: 中心频率列表
            quality_factors: 品质因数列表
        """
        super().__init__(keras_model, layer_name, "SVF")
        self.center_freqs = center_freqs
        self.quality_factors = quality_factors

    def get_layer_info(self) -> Dict[str, Any]:
        """
        获取SVF层的特定信息

        Returns:
            层信息字典，包含SVF特定信息
        """
        info = super().get_layer_info()
        # 添加SVF特定的信息
        if self.center_freqs is not None:
            info['center_freqs'] = self.center_freqs
        if self.quality_factors is not None:
            info['quality_factors'] = self.quality_factors
        return info

    def to_spice(self, output_path: str = None, opamp_config: Dict[str, Any] = None, use_e96: bool = False, amp=1.0, power_supply_config: Dict[str, Any] = None):
        """
        导出SVF层到SPICE模型

        Args:
            output_path: 输出SPICE模型文件路径，如果为None则仅返回SPICE对象
            opamp_config: 运放配置字典，包含model, include_file, power_pins等信息
            use_e96: 是否使用E96标准电阻值
            amp: 信号增益倍数
            power_supply_config: 电源配置字典，包含vcc和vee电压值

        Returns:
            SVFilter: SPICE模型对象
        """
        # 确保SVFilter类可用
        global SVFFilter
        if SVFFilter is None:
            error_msg = "无法导出SPICE模型：SVFilter模块未成功导入"
            print(error_msg)
            return error_msg

        # 确保中心频率和品质因数存在
        if self.center_freqs is None or self.quality_factors is None:
            error_msg = "无法导出SPICE模型：中心频率或品质因数未提供"
            print(error_msg)
            return error_msg
        
        # 从model_config获取inference_config（如果参数未直接提供）
        if power_supply_config is None and hasattr(self, 'model') and hasattr(self.model, 'model_config'):
            inference_config = self.model.model_config.get('inference_config', {})
            power_supply_config = inference_config.get('power_supply', None)

        # 创建SVFilter对象
        svf = SVFFilter(
            cutoff_freq=self.center_freqs,
            Q=self.quality_factors,
            opamp_config=opamp_config,
            use_e96=use_e96,
            n_svf=len(self.center_freqs),
            power_supply_config=power_supply_config
        )

        # 获取SPICE模型文本
        spice_model_text = svf.get_circuit_netlist()

        # 如果提供了输出路径，保存到文件
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(spice_model_text)
                print(f"SVF SPICE模型已保存到: {output_path}")
            except Exception as e:
                print(f"保存SPICE模型文件时出错: {str(e)}")

        return svf

    def post_process(self, output_wave: WaveData, context=None):
        """
        SVF层后处理，支持上下文感知的相位修正
        
        输出的通道顺序是 HP0, BP0, LP0, HP1, BP1, LP1 ...
        HPn 和 LPn 需要反转反向
        
        参数:
            output_wave: 输出波形数据
            context: 处理上下文，包含仿真类型信息
        """
        # 检查输出波形是否有效
        if output_wave is None or not isinstance(output_wave, WaveData):
            raise ValueError("无效的输出波形数据")

        # 获取仿真类型上下文
        simulation_type = context.get('simulation_type', 'unknown') if context else 'unknown'
        
        if simulation_type == 'spice':
            # SPICE路径：相位处理由WaveNet5SPICEBackend统一管理
            # 这里不做处理，避免双重反相
            return output_wave
        elif simulation_type == 'numpy':
            # NumPy路径：保持现有的相位修正逻辑
            for i, record in enumerate(output_wave.records):
                if record.data is None:
                    raise ValueError("输出波形记录数据不能为空")
                # data shape: (n_samples, n_channels)
                # 反转 HP 通道和 LP 通道
                for j in range(record.data.shape[1]):
                    if j % 3 == 0 or j % 3 == 2:
                        record.data[:, j] = -record.data[:, j]
            return output_wave
        else:
            # 默认行为（兼容性）：应用相位修正
            for i, record in enumerate(output_wave.records):
                if record.data is None:
                    raise ValueError("输出波形记录数据不能为空")
                # data shape: (n_samples, n_channels)  
                # 反转 HP 通道和 LP 通道
                for j in range(record.data.shape[1]):
                    if j % 3 == 0 or j % 3 == 2:
                        record.data[:, j] = -record.data[:, j]
            return output_wave


class DenseLayer(BaseLayerModel, SpiceModelSupport):
    """
    带激活函数的密集层

    支持导出 Dense 的 SPICE 模型，Dense SPICE 模型在 circuit_dense.py ，参考: 对 dense 的测试在 test_dense.py 
    """

    def __init__(self, keras_model, layer_name: str = "Dense_Layer",
                 activation: Optional[str] = None, units: Optional[int] = None):
        """
        初始化带激活函数的密集层模型

        Args:
            keras_model: 封装的Keras模型
            layer_name: 层名称
            activation: 激活函数名称
            units: 输出单元数
        """
        super().__init__(keras_model, layer_name, "Dense")
        self.activation = activation
        self.units = units

    def get_layer_info(self) -> Dict[str, Any]:
        """
        获取密集层的特定信息

        Returns:
            层信息字典，包含密集层特定信息
        """
        info = super().get_layer_info()
        info['activation'] = self.activation
        if self.units is not None:
            info['units'] = self.units
        return info

    def to_spice(self, output_path: str = None, opamp_config: Dict[str, Any] = None, use_e96: bool = False, relu_config: Dict[str, Any] = None, high_pass_config: Dict[str, Any] = None, power_supply_config: Dict[str, Any] = None, amp=1):
        """
        导出Dense层到SPICE模型

        Args:
            output_path: 输出SPICE模型文件路径，如果为None则仅返回SPICE对象
            opamp_config: 运放配置字典，包含model, include_file, power_pins等信息
            use_e96: 是否使用E96标准电阻值
            use_relu: 是否在输出添加ReLU激活电路，当self.activation为'relu'时默认为True
            relu_config: ReLU电路配置字典
            high_pass_config: 高通滤波器配置字典

        Returns:
            DenseCircuit: SPICE模型对象
        """        # 导入circuit_dense模块
        global DenseCircuitFactory
        if DenseCircuitFactory is None:
            error_msg = "无法导出SPICE模型：DenseCircuitFactory模块未成功导入"
            print(error_msg)
            return error_msg

        # 获取密集层权重和偏置
        weights = self.get_weights()
        if len(weights) < 1:
            error_msg = "无法导出SPICE模型：密集层权重不可用"
            print(error_msg)
            return error_msg

        # 权重矩阵应该是第一个元素
        weight_matrix = weights[0]
        if weight_matrix.ndim == 3:
            # shalpe: (1, input_dim, output_dim) -> (input_dim, output_dim)
            weight_matrix = np.reshape(
                weight_matrix, (weight_matrix.shape[1], weight_matrix.shape[2]))

        # 偏置向量是可选的（如果存在）
        bias_vector = weights[1] if len(weights) > 1 else None

        if bias_vector is not None:
            bias_vector = bias_vector * amp  # 偏置向量放大
            
            # 🔧 应用 SPICE 偏置补偿（仅用于 SPICE 电路生成）
            # 这是为了补偿 SPICE 仿真与 NN 推理之间的系统性偏差
            if hasattr(self, '_temp_bias_compensation'):
                compensation = self._temp_bias_compensation
                
                # 由于现在有严格的形状验证，可以简化处理逻辑
                if isinstance(compensation, (list, tuple)):
                    # 列表格式：每个输出单元一个补偿值
                    compensation = np.array(compensation)
                    # 验证已通过，直接应用
                    assert len(compensation) == len(bias_vector), \
                        f"补偿值长度({len(compensation)})与偏置向量长度({len(bias_vector)})不匹配。" \
                        f"这应该在验证阶段被捕获。"
                elif isinstance(compensation, (int, float)):
                    # 标量格式：应用到所有输出单元
                    compensation = np.full_like(bias_vector, compensation)
                else:
                    logger.warning(f"未知的补偿值类型: {type(compensation)}")
                    compensation = np.array(compensation)
                
                logger.info(f"SPICE 偏置补偿 - {self.name}:")
                logger.info(f"  原始偏置权重 {bias_vector}")
                logger.info(f"  补偿值: {compensation}")
                
                bias_vector = bias_vector + compensation
                
                logger.info(f"  调整后偏置权重 {bias_vector}")
        else:
            bias_vector = None

        inner_layers = self.get_inner_layers()

        for layer in inner_layers:
            if 'activation' in layer.name:
                use_relu = True
            else:
                use_relu = False

        self.use_relu = use_relu

        # 从模型配置中获取各项配置（如果未提供）
        if hasattr(self, 'model_config'):
            inference_config = self.model_config.get('inference_config', {})
            
            # 获取高通滤波器配置
            if high_pass_config is None:
                high_pass_config = inference_config.get('high_pass_config', None)
            
            # 获取电源配置
            if power_supply_config is None:
                power_supply_config = inference_config.get('power_supply', None)
            
            # 获取运放配置
            if opamp_config is None:
                opamp_config = inference_config.get('opamp_config', None)
        
        # 创建DenseCircuit对象
        dense_circuit = DenseCircuitFactory.create(
            gains=weight_matrix,
            biases=bias_vector,
            opamp_config=opamp_config,
            use_e96=use_e96,
            use_relu=use_relu,
            relu_config=relu_config,
            high_pass_config=high_pass_config,
            power_supply_config=power_supply_config
        )

        # 获取SPICE模型文本
        spice_model_text = dense_circuit.get_circuit_netlist()

        # 如果提供了输出路径，保存到文件
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(spice_model_text)
                logger.info(f"Dense SPICE模型已保存到: {output_path}")
            except Exception as e:
                print(f"保存SPICE模型文件时出错: {str(e)}")

        return dense_circuit

    def post_process(self, output_wave: WaveData):
        """
        将输出进行正负反转
        """
        # 检查输出波形是否有效
        if output_wave is None or not isinstance(output_wave, WaveData):
            raise ValueError("无效的输出波形数据")

        # 反转输出波形
        for record in output_wave.records:
            if record.data is None:
                raise ValueError("输出波形记录数据不能为空")
            # 反转数据
            if self.use_relu:
                # 电路是反相 relu, 需要反转
                record.data = -record.data

        return output_wave
