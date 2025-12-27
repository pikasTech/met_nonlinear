"""
使用组合模式的带符号加法器电路工厂类

通过组合模式而不是继承层次结构来实现不同运放模型和ReLU激活方式的组合，
从而避免类爆炸问题。每个组件（如运放模型和ReLU模型）自己管理其参数和行为，
提高了代码的模块性和可维护性。

主要类:
- DenseCircuit: 使用组合模式的带符号加法器电路类
- DenseCircuitFactory: 创建各种预配置电路的工厂类
"""
from spice_simulator.opamp_models import OpAmpModelFactory, IdealOpAmpModel, RealOpAmpModel
from spice_simulator.relu_models import ReluModelFactory
import numpy as np
from spice_simulator.circuit_base import BaseCircuit

MAX_RESISTANCE = 1e9 # 定义一个极大电阻值，用于近似断开连接


class DenseCircuit(BaseCircuit):
    """基于模板方法模式的带符号加法器电路基类

    该类使用模板方法模式定义了电路生成的算法骨架，
    允许子类通过重写特定方法来自定义运放模型、ReLU激活等行为。
    """

    def __init__(self, gains, biases=None, R_values=None, opamp_config=None,
                 use_e96=False, use_relu=False, relu_config=None, bias_compensation=None, high_pass_config=None, power_supply_config=None, layer_name=None,
                 include_quantization_comparison=False):
        """
        初始化带符号加法器电路

        参数:
            gains: 增益矩阵，形状为(inputs, outputs)，可以包含正负值
                  如果传入一维数组，则自动转换为(inputs, 1)的二维数组
            biases: 偏置值列表，每个输出通道一个偏置值，默认为None（无偏置）
                   当为None时，所有通道无偏置
                   当为标量时，所有通道使用相同偏置
                   当为数组时，需要与输出通道数量匹配
            R_values: 电阻配置字典，默认为None（使用默认配置）
            opamp_config: 运放配置字典，默认为None（使用理想运放模型）
                可配置参数:
                - model: 指定运放模型，如'LM324', 'TL084'等，默认为'ideal'
                - include_file: 运放模型文件路径，如包含SPICE模型的文件
                - power_pins: 是否连接电源引脚，默认为True
                - params: 自定义运放模型参数字典
            use_e96: 是否使用E96标准电阻值，默认为False
            use_relu: 是否在每个输出通道后添加ReLU激活电路，默认为False
            relu_config: ReLU电路配置字典，默认为None（使用默认配置）
                可配置参数:
                - type: ReLU实现类型，'op_amp'(运放实现)或'diode_clamp'(二极管钳位)，默认为'op_amp'
                - gain: ReLU输出增益，默认为1.0
                - R_value: ReLU电路电阻值，默认为10kΩ
                - diode_model: 二极管模型，默认为'1N4148'
                - clamp_voltage: 钳位电压(仅diode_clamp模式)，默认为0.0V
                - opamp_config: ReLU电路运放配置，默认使用与主电路相同的配置
            high_pass_config: 高通滤波器配置字典，默认为None（禁用）
                可配置参数:
                - enable: 是否启用高通滤波器，默认为False
                - cutoff_freq: 截止频率(Hz)，默认为1.0
                - capacitance: 电容值(F)，为None时自动计算
                - resistance: 电阻值(Ω)，为None时自动计算
                - bias_voltage: bias电压(V)，默认为0.0
                - auto_bias: 是否根据正负自动选择VCC/VEE分压，默认为True
                - bias_divider_high: 分压电阻上阻值(Ω)，默认为10kΩ
                - bias_divider_low: 分压电阻下阻值(Ω)，默认为10kΩ
        """
        # 将增益转换为numpy数组
        self.gains = np.array(gains) if not isinstance(
            gains, np.ndarray) else gains

        # 如果gains是一维数组，转换为(inputs, 1)的二维数组
        if self.gains.ndim == 1:
            self.gains = self.gains.reshape(-1, 1)

        self.use_e96 = use_e96
        self.use_relu = use_relu

        # 获取输入数量和输出通道数
        self.n_inputs, self.n_outputs = self.gains.shape

        # 处理偏置参数
        if biases is None:
            # 默认无偏置
            self.biases = np.zeros(self.n_outputs)
            self.has_bias = False
        else:
            self.has_bias = True
            # 将偏置转换为numpy数组
            biases_array = np.array(biases) if not isinstance(
                biases, np.ndarray) else biases
            if np.isscalar(biases_array):
                # 如果是标量，扩展为数组
                self.biases = np.full(self.n_outputs, biases_array)
            elif len(biases_array) != self.n_outputs:
                raise ValueError(
                    f"偏置值数量({len(biases_array)})与输出通道数({self.n_outputs})不匹配")
            else:
                self.biases = biases_array
        
        # 存储偏置补偿值
        self.bias_compensation = bias_compensation or {}
        
        # 电源配置
        self.power_supply_config = power_supply_config or {
            'vcc': 15.0,
            'vee': -15.0
        }
        self.vcc = self.power_supply_config.get('vcc', 15.0)
        self.vee = self.power_supply_config.get('vee', -15.0)

        # 处理高通滤波器配置
        # 
        # 高通滤波器的本质作用：
        # 1. 这是一个纯粹的硬件补偿措施，用于对抗实际电路中的非理想特性：
        #    - 运放的输入失调电压导致的DC偏移
        #    - ReLU二极管的正向压降
        #    - 温度漂移等其他DC误差
        # 
        # 2. 工作原理：
        #    - 通过电容隔离运放输出的DC误差
        #    - 使用电阻分压器将信号拉到正确的DC工作点
        #    - 这个DC工作点必须是神经网络的bias权重值（self.biases[ch]）
        # 
        # 3. 重要说明：
        #    - 高通滤波器仅在SPICE仿真中生效（硬件补偿）
        #    - 不应该影响NumPy仿真（理想仿真不需要补偿）
        #    - 每个输出通道使用其对应的神经网络bias权重
        #    - 绝不使用固定的bias_voltage配置值
        
        if high_pass_config is None:
            self.high_pass_config = {
                'enable': False,  # 默认禁用（理想仿真不需要）
                'cutoff_freq': 1.0,              # 高通截止频率 (Hz)
                'capacitance': None,             # 可选：指定电容值 (F)
                'resistance': None,              # 可选：指定电阻值 (Ω)
                # bias_voltage 参数已被移除！
                # 原因：bias必须来自神经网络权重，不是配置参数
                'auto_bias': True,               # 自动选择VCC/VEE作为分压源
                'bias_divider_high': 10e3,       # 分压器上电阻 (Ω)
                'bias_divider_low': 10e3,        # 分压器下电阻 (Ω) - 将被动态计算
            }
        else:
            # 验证配置：拒绝包含bias_voltage的配置
            if 'bias_voltage' in high_pass_config:
                raise ValueError(
                    "高通滤波器配置错误：不应包含'bias_voltage'参数。\n"
                    "高通滤波器会自动使用每个通道的神经网络bias权重。\n"
                    "bias权重来自训练结果，是每个神经元的最佳工作点。"
                )
            
            self.high_pass_config = {
                'enable': high_pass_config.get('enable', False),
                'cutoff_freq': high_pass_config.get('cutoff_freq', 1.0),
                'capacitance': high_pass_config.get('capacitance', None),
                'resistance': high_pass_config.get('resistance', None),
                'auto_bias': high_pass_config.get('auto_bias', True),
                'bias_divider_high': high_pass_config.get('bias_divider_high', 10e3),
                'bias_divider_low': high_pass_config.get('bias_divider_low', 10e3),
            }

        # 处理运放配置 - 这里创建运放模型实例
        if opamp_config is None:
            self.opamp_config = {
                'model': 'ideal',
                'include_file': None,
                'power_pins': True,
                'params': {}
            }
        else:
            # 合并默认值和用户提供的配置
            self.opamp_config = {
                'model': opamp_config.get('model', 'ideal'),
                'include_file': opamp_config.get('include_file', None),
                'power_pins': opamp_config.get('power_pins', True),
                'params': opamp_config.get('params', {})
            }

        # 创建运放模型
        self.opamp_model = self.create_opamp_model()

        # 处理ReLU配置 - 这里创建ReLU模型实例
        if relu_config is None:
            self.relu_config = {
                'type': 'op_amp',  # 默认使用运放实现
                'gain': 1.0,
                'R_value': 10e3,
                'diode_model': '1N4148',
                'clamp_voltage': 0.0,  # 钳位到0V (仅diode_clamp模式)
                'opamp_config': self.opamp_config  # 默认使用与主电路相同的运放配置
            }
        else:
            # 合并默认值和用户提供的配置
            self.relu_config = {
                'type': relu_config.get('type', 'op_amp'),
                'gain': relu_config.get('gain', 1.0),
                'R_value': relu_config.get('R_value', 10e3),
                'diode_model': relu_config.get('diode_model', '1N4148'),
                'clamp_voltage': relu_config.get('clamp_voltage', 0.0),
                'opamp_config': relu_config.get('opamp_config', self.opamp_config)
            }

        # 创建ReLU模型
        self.relu_model = self.create_relu_model()

        # 处理电阻值 - 为每个输出通道创建单独的电阻配置
        self.channel_configs = []
        self.resistance_records = []  # 新增：电阻数据收集列表
        self.layer_name = layer_name  # 新增：层名称标识，从参数传入
        self.validation_enabled = True  # 强制启用校验
        self.calculate_resistors(R_values, include_quantization_comparison)

        # 生成电路网表文本(不包含仿真指令)
        self.netlist_text = self._create_circuit_netlist()

    def create_opamp_model(self):
        """
        创建运放模型实例（模板方法模式的钩子方法）
        子类可以重写此方法来创建特定的运放模型实例

        返回:
            OpAmpModel: 运放模型实例
        """
        # 默认实现：使用OpAmpModelFactory创建模型
        return OpAmpModelFactory.create_model(self.opamp_config)

    def create_relu_model(self):
        """
        创建ReLU模型实例（模板方法模式的钩子方法）
        子类可以重写此方法来创建特定的ReLU模型实例

        返回:
            ReluModel: ReLU模型实例
        """
        # 默认实现：使用ReluModelFactory创建模型
        return ReluModelFactory.create_model(
            use_relu=self.use_relu,
            relu_config=self.relu_config,
            opamp_model=self.create_relu_opamp_model()
        )

    def create_relu_opamp_model(self):
        """
        创建ReLU电路中使用的运放模型实例（模板方法模式的钩子方法）
        子类可以重写此方法来创建特定的ReLU运放模型实例

        返回:
            OpAmpModel: 用于ReLU电路的运放模型实例
        """
        # 默认实现：使用与主电路相同的运放配置
        return OpAmpModelFactory.create_model(self.relu_config.get('opamp_config', self.opamp_config))

    def calculate_resistors(self, R_values=None, include_quantization_comparison=False):
        """
        计算电路所需的电阻值

        参数:
            R_values: 用户提供的电阻值配置字典，默认为None
            include_quantization_comparison: 是否包含E96量化对比数据，默认为False
        """
        # 保存是否需要生成量化对比数据的标志
        self._include_quantization_comparison = include_quantization_comparison
        for ch in range(self.n_outputs):
            # 获取当前通道的增益值和偏置值
            channel_gains = self.gains[:, ch]
            channel_bias = self.biases[ch]

            # 创建当前通道的电阻配置
            if R_values is None:
                # 输入电阻基准值 - 计算各通道电阻用
                R_base = 1e3
                R_ref = 1.0  # 电流采样电阻 - 较小值以便进行电流采样

                # 电流采样电阻 - 较小值以便进行电流采样
                Rin_pos = self._convert_to_standard_value(
                    R_ref) if self.use_e96 else R_ref
                Rin_neg = self._convert_to_standard_value(
                    R_ref) if self.use_e96 else R_ref

                R_total = R_base + R_ref  # 总电阻
                ratio_V_I = R_ref / R_total   # 电压到电流的转换比率

                # 运放电路电阻 - 调整这些电阻以提高电流转电压的增益
                R2_pos_raw = 500e3  # 提高到500kΩ (之前是10kΩ) - 增加50倍增益
                R2_neg_raw = 500e3  # 提高到500kΩ (之前是10kΩ) - 增加50倍增益

                R2_pos = self._convert_to_standard_value(
                    R2_pos_raw) if self.use_e96 else R2_pos_raw
                R2_neg = self._convert_to_standard_value(
                    R2_neg_raw) if self.use_e96 else R2_neg_raw

                R1_pos_raw = R2_pos * ratio_V_I
                R1_neg_raw = R2_neg * ratio_V_I

                R1_pos = self._convert_to_standard_value(
                    R1_pos_raw) if self.use_e96 else R1_pos_raw
                R1_neg = self._convert_to_standard_value(
                    R1_neg_raw) if self.use_e96 else R1_neg_raw

                # 计算各通道的电阻值 - 每个输入通道同时有正向和负向电阻
                # 电阻值与增益成反比
                R_pos_channels = []
                R_neg_channels = []

                for gain in channel_gains:
                    # 正向通道电阻计算
                    if gain > 0:
                        # 如果增益为正，正向通道有效
                        r_pos_raw = R_base / gain
                        # 负向通道设为极大电阻，近似断开
                        r_neg_raw = MAX_RESISTANCE
                    elif gain < 0:
                        # 如果增益为负，负向通道有效
                        r_neg_raw = R_base / abs(gain)
                        # 正向通道设为极大电阻，近似断开
                        r_pos_raw = MAX_RESISTANCE
                    else:
                        # 如果增益为零，两个通道都设为极大电阻
                        r_pos_raw = MAX_RESISTANCE
                        r_neg_raw = MAX_RESISTANCE

                    r_pos = self._convert_to_standard_value(
                        r_pos_raw) if self.use_e96 else r_pos_raw
                    r_neg = self._convert_to_standard_value(
                        r_neg_raw) if self.use_e96 else r_neg_raw

                    R_pos_channels.append(r_pos)
                    R_neg_channels.append(r_neg)

                # 应用偏置补偿
                compensation = self.bias_compensation.get(ch, 0)
                effective_bias = channel_bias - compensation
                
                # 确保effective_bias是标量
                if hasattr(effective_bias, '__len__'):
                    # 如果是数组，取第一个元素（应该只有一个元素）
                    effective_bias = float(effective_bias.item() if hasattr(effective_bias, 'item') else effective_bias[0])
                else:
                    effective_bias = float(effective_bias)
                
                # 计算偏置电阻
                if self.has_bias and effective_bias != 0:
                    # 使用配置的电源电压
                    vcc = self.vcc
                    vee = self.vee

                    # 根据偏置极性选择电源引脚和电阻配置
                    if effective_bias > 0:
                        # 正偏置 - 从Vcc引入
                        # 将偏置视为增益，计算等效电阻
                        r_bias_raw = R_base / effective_bias * vcc
                        r_bias = self._convert_to_standard_value(
                            r_bias_raw) if self.use_e96 else r_bias_raw
                        R_bias_pos = r_bias
                        R_bias_neg = MAX_RESISTANCE  # 负向通道设为极大电阻，近似断开
                    elif effective_bias < 0:
                        # 负偏置 - 从Vcc引入
                        # 计算等效电阻
                        r_bias_raw = R_base / abs(effective_bias) * vcc
                        r_bias = self._convert_to_standard_value(
                            r_bias_raw) if self.use_e96 else r_bias_raw
                        R_bias_neg = r_bias
                        R_bias_pos = MAX_RESISTANCE  # 正向通道设为极大电阻，近似断开
                    else:
                        # 零偏置 - 两个通道都设为极大电阻
                        R_bias_pos = MAX_RESISTANCE
                        R_bias_neg = MAX_RESISTANCE
                else:
                    # 无偏置 - 两个通道都设为极大电阻
                    R_bias_pos = MAX_RESISTANCE
                    R_bias_neg = MAX_RESISTANCE

                # 计算高通滤波器参数
                if self.high_pass_config['enable']:
                    # 如果未指定电容和电阻值，根据截止频率计算
                    if self.high_pass_config['capacitance'] is None or self.high_pass_config['resistance'] is None:
                        # 设定更小的电容值以获得更大的电阻，减少负载效应
                        C_default = 1e-5  # 10μF
                        # 根据截止频率计算电阻: R = 1 / (2π * f * C)
                        R_hp = 1 / (2 * np.pi * self.high_pass_config['cutoff_freq'] * C_default)
                        hp_capacitance = C_default
                        hp_resistance = R_hp
                    else:
                        hp_capacitance = self.high_pass_config['capacitance']
                        hp_resistance = self.high_pass_config['resistance']
                    
                    # 计算bias分压电阻
                    # 重要：使用当前通道的神经网络bias权重，而不是固定的配置值
                    # 原因：
                    # 1. 神经网络的bias是训练优化的结果，代表该神经元的最佳工作点
                    # 2. ReLU激活函数对bias敏感，bias决定了激活阈值
                    # 3. 使用错误的bias会破坏神经网络的功能
                    if self.high_pass_config['auto_bias']:
                        # 获取当前通道的bias权重
                        bias_value = self.biases[ch] if self.has_bias else 0.0
                        
                        if bias_value >= 0:
                            # 正bias：从VCC分压
                            # V_bias = VCC * R_low / (R_high + R_low)
                            # R_low = V_bias * R_high / (VCC - V_bias)
                            vcc = self.vcc
                            R_high = self.high_pass_config['bias_divider_high']
                            if bias_value < vcc:
                                R_low = bias_value * R_high / (vcc - bias_value)
                            else:
                                R_low = self.high_pass_config['bias_divider_low']
                            bias_source = 'vcc'
                        else:
                            # 负bias：从VEE分压
                            # V_bias = VEE * R_low / (R_high + R_low)
                            # R_low = V_bias * R_high / (VEE - V_bias)
                            vee = self.vee
                            R_high = self.high_pass_config['bias_divider_high']
                            if bias_value > vee:
                                R_low = bias_value * R_high / (vee - bias_value)
                            else:
                                R_low = self.high_pass_config['bias_divider_low']
                            bias_source = 'vee'
                        
                        hp_bias_r_high = R_high
                        hp_bias_r_low = R_low
                        hp_bias_source = bias_source
                    else:
                        hp_bias_r_high = self.high_pass_config['bias_divider_high']
                        hp_bias_r_low = self.high_pass_config['bias_divider_low']
                        hp_bias_source = 'vcc' if self.high_pass_config['bias_voltage'] >= 0 else 'vee'
                else:
                    hp_capacitance = None
                    hp_resistance = None
                    hp_bias_r_high = None
                    hp_bias_r_low = None
                    hp_bias_source = None

                # 存储当前通道的电阻配置
                channel_config = {
                    'R_base': R_base,
                    'Rin_pos': Rin_pos,
                    'Rin_neg': Rin_neg,
                    'R1_pos': R1_pos,
                    'R1_neg': R1_neg,
                    'R2_pos': R2_pos,
                    'R2_neg': R2_neg,
                    'R_pos_channels': R_pos_channels,
                    'R_neg_channels': R_neg_channels,
                    'R_bias_pos': R_bias_pos,  # 正偏置电阻
                    'R_bias_neg': R_bias_neg,  # 负偏置电阻
                    'bias': channel_bias,       # 偏置值
                    'hp_capacitance': hp_capacitance,
                    'hp_resistance': hp_resistance,
                    'hp_bias_r_high': hp_bias_r_high,
                    'hp_bias_r_low': hp_bias_r_low,
                    'hp_bias_source': hp_bias_source,
                }
                
                # 记录所有电阻值用于导出
                self._record_channel_resistances(ch, channel_config)
            else:
                # 从用户提供的配置中读取电阻值
                # 注意：对于多通道，用户需要提供每个通道的电阻值配置
                channel_key = f"channel_{ch}" if self.n_outputs > 1 else ""

                channel_config = {
                    'Rin_pos': R_values.get(f'Rin_pos{channel_key}', 1.0),
                    'Rin_neg': R_values.get(f'Rin_neg{channel_key}', 1.0),
                    'R1_pos': R_values.get(f'R1_pos{channel_key}', 1e3),
                    'R1_neg': R_values.get(f'R1_neg{channel_key}', 1e3),
                    'R2_pos': R_values.get(f'R2_pos{channel_key}', 100e3),
                    'R2_neg': R_values.get(f'R2_neg{channel_key}', 100e3),
                    'R_pos_channels': R_values.get(f'R_pos_channels{channel_key}', [10e3] * self.n_inputs),
                    'R_neg_channels': R_values.get(f'R_neg_channels{channel_key}', [10e3] * self.n_inputs),
                    # 默认无偏置
                    'R_bias_pos': R_values.get(f'R_bias_pos{channel_key}', MAX_RESISTANCE),
                    # 默认无偏置
                    'R_bias_neg': R_values.get(f'R_bias_neg{channel_key}', MAX_RESISTANCE),
                    'bias': self.biases[ch]
                }

                # 如果启用E96标准值，将用户提供的电阻值转换为标准值
                if self.use_e96:
                    for key in ['Rin_pos', 'Rin_neg', 'R1_pos', 'R1_neg', 'R2_pos', 'R2_neg', 'R_bias_pos', 'R_bias_neg']:
                        channel_config[key] = self._convert_to_standard_value(
                            channel_config[key])

                    channel_config['R_pos_channels'] = [
                        self._convert_to_standard_value(r) for r in channel_config['R_pos_channels']
                    ]
                    channel_config['R_neg_channels'] = [
                        self._convert_to_standard_value(r) for r in channel_config['R_neg_channels']
                    ]
            
            # 如果从用户配置读取，也需要记录
            if R_values is not None:
                self._record_channel_resistances(ch, channel_config)
            
            self.channel_configs.append(channel_config)

    def _create_circuit_netlist(self):
        """
        创建基于差分电流采样的带符号加法器电路网表，支持多通道输出

        返回:
            str: 电路网表内容
        """
        # 创建网表文本
        netlist_text = f"""* Differential Current-Sampling Signed Adder Circuit - NGspice Simulation
* 基于差分电流采样的带符号加法器电路
* 输入数量: {self.n_inputs}
* 输出通道数: {self.n_outputs}
* 增益矩阵形状: {self.gains.shape}
* 偏置功能: {"启用" if self.has_bias else "禁用"}
* ReLU激活: {"启用" if self.use_relu else "禁用"}
"""
        if self.has_bias:
            netlist_text += f"* 偏置值: {self.biases.tolist()}\n"

        # 添加运放模型包含语句
        netlist_text += self.opamp_model.get_include_text()

        # 如果启用ReLU，添加二极管模型
        if self.use_relu:
            diode_model = self.relu_config['diode_model']
            netlist_text += self.relu_model.get_diode_model_text(diode_model)

        netlist_text += f"""
* Power Supply
Vcc vcc 0 {self.vcc}
Vee vee 0 {self.vee}

* Define input voltage sources (will be replaced with PWL data)
"""

        # 添加输入电压源定义
        for i in range(self.n_inputs):
            netlist_text += f"Vin{i+1} in{i+1} 0 0\n"

        # 为每个输出通道创建独立的电路部分
        for ch in range(self.n_outputs):
            channel_config = self.channel_configs[ch]
            channel_gains = self.gains[:, ch]
            channel_bias = channel_config['bias']

            # 添加通道标题
            netlist_text += f"\n* 输出通道 {ch+1} - 差分电流采样的带符号加法器电路\n"
            netlist_text += f"* 通道 {ch+1} 的增益列表: {channel_gains.tolist()}\n"
            if self.has_bias:
                netlist_text += f"* 通道 {ch+1} 的偏置值: {channel_bias}\n"

            # 添加支路 - 每个输入通道同时连接到正向和负向支路
            for i in range(self.n_inputs):
                netlist_text += f"R_pos{ch+1}_{i+1} in{i+1} curr_pos{ch+1} {channel_config['R_pos_channels'][i]}\n"
                netlist_text += f"R_neg{ch+1}_{i+1} in{i+1} curr_neg{ch+1} {channel_config['R_neg_channels'][i]}\n"

            # 添加偏置电阻 - 始终创建正负偏置电阻连接，无论是否有偏置
            # 这里添加从正电源 (VCC) 到正输入支路的电阻
            netlist_text += f"R_bias_pos{ch+1} vcc curr_pos{ch+1} {channel_config['R_bias_pos']}\n"
            # 这里添加从正电源 (VCC) 到负输入支路的电阻
            netlist_text += f"R_bias_neg{ch+1} vcc curr_neg{ch+1} {channel_config['R_bias_neg']}\n"

            # 添加电流采样电阻
            netlist_text += f"Rin_pos{ch+1} curr_pos{ch+1} 0 {channel_config['Rin_pos']}\n"
            netlist_text += f"Rin_neg{ch+1} curr_neg{ch+1} 0 {channel_config['Rin_neg']}\n"

            # 添加差分放大器电路
            # 正向电流采样点连接到运放同相端
            netlist_text += f"R1_pos{ch+1} curr_pos{ch+1} pos{ch+1} {channel_config['R1_pos']}\n"
            # 负向电流采样点连接到运放反相端
            netlist_text += f"R1_neg{ch+1} curr_neg{ch+1} neg{ch+1} {channel_config['R1_neg']}\n"

            # 添加反馈电阻网络
            # 反相端到输出的电阻
            netlist_text += f"R2_neg{ch+1} neg{ch+1} out{ch+1}_pre {channel_config['R2_neg']}\n"
            # 同相端到地的电阻
            netlist_text += f"R2_pos{ch+1} pos{ch+1} 0 {channel_config['R2_pos']}\n"

            # 添加运放模型
            netlist_text += self.opamp_model.get_netlist_text(
                f"Xopamp{ch+1}",
                f"pos{ch+1}",
                f"neg{ch+1}",
                f"out{ch+1}_pre"
            )

            # 在运放输出后、ReLU之前插入高通滤波器
            # 高通滤波器只应用于有ReLU激活的层，用于补偿二极管非线性
            if self.high_pass_config['enable'] and self.use_relu:
                # 生成bias电压分压器
                netlist_text += f"""
* 高通滤波器 Bias 电压分压器 - 通道 {ch+1}
R_hp_bias_high{ch+1} {channel_config['hp_bias_source']} hp_bias{ch+1} {channel_config['hp_bias_r_high']}
R_hp_bias_low{ch+1} hp_bias{ch+1} 0 {channel_config['hp_bias_r_low']}
"""
                
                # 生成高通滤波器
                netlist_text += f"""
* 一阶无源高通滤波器 - 通道 {ch+1}
C_hp{ch+1} out{ch+1}_pre out{ch+1}_hp {channel_config['hp_capacitance']}
R_hp{ch+1} out{ch+1}_hp hp_bias{ch+1} {channel_config['hp_resistance']}
"""
                
                # 修改ReLU输入节点
                relu_input_node = f"out{ch+1}_hp"
            else:
                # 无高通滤波器或无ReLU激活时，直接使用运放输出
                relu_input_node = f"out{ch+1}_pre"

            # 添加ReLU激活电路
            if self.use_relu:
                netlist_text += self.relu_model.get_netlist_text(
                    ch+1,
                    relu_input_node,  # 使用动态确定的输入节点
                    f"out{ch+1}",
                    self.relu_config['diode_model']
                )
            else:
                # 如果不使用ReLU，直接连接输出
                netlist_text += f"""
* 直接连接输出（无ReLU激活）
Rlink{ch+1} {relu_input_node} out{ch+1} 1e-6
"""

        return netlist_text

    def get_circuit_netlist(self):
        """获取电路的网表文本(不包含仿真指令)"""
        return self.netlist_text

    def simulate_numpy(self, t, input_signals):
        """
        使用NumPy进行带符号加法器的理论仿真计算

        参数:
            t: 时间向量
            input_signals: 输入信号矩阵，必须是形状为 [time_steps, inputs] 的二维数组

        返回:
            np.ndarray: 输出信号矩阵，形状为 [time_steps, outputs]
        """
        # 检查输入矩阵形状
        if input_signals.ndim == 1:
            # 如果是一维数组，假设它只有一个时间步
            if len(input_signals) != self.n_inputs:
                raise ValueError(f"输入信号维度不匹配。期望长度为 {self.n_inputs}")
            input_signals = input_signals.reshape(1, -1)  # 形状变为 [1, inputs]

        # 确保输入是 [time_steps, inputs] 格式
        if input_signals.shape[1] != self.n_inputs:
            raise ValueError(f"输入信号维度不匹配。期望形状为 [time_steps, {self.n_inputs}]")

        # 初始化输出矩阵 [time_steps, outputs]
        n_timesteps = input_signals.shape[0]
        output = np.zeros((n_timesteps, self.n_outputs))

        # 计算每个输出通道的理论输出
        for ch in range(self.n_outputs):
            # 矩阵乘法实现： input_signals * gains[:, ch]
            for t_idx in range(n_timesteps):
                for w_idx in range(self.n_inputs):
                    output[t_idx, ch] += input_signals[t_idx,
                                                       w_idx] * self.gains[w_idx, ch]

            # 添加偏置值
            if self.has_bias:
                output[:, ch] += self.biases[ch]

        # 重要说明：高通滤波器不应该在NumPy仿真中实现！
        # 原因：
        # 1. NumPy仿真是理想仿真，不存在硬件非理想特性
        # 2. 高通滤波器是硬件补偿措施，专门对抗运放失调、二极管压降等
        # 3. 在理想仿真中加入硬件补偿会产生错误的结果
        # 
        # 高通滤波器仅在SPICE网表中生效，用于实际硬件电路的DC误差补偿

        # 如果启用ReLU，应用ReLU效果
        if self.use_relu:
            output = self.relu_model.modify_output_signals(
                output, self.relu_config)

        return output


    def _record_channel_resistances(self, channel: int, config: dict):
        """
        记录单个通道的所有电阻值

        # NO ROLLBACK: 记录失败直接抛出异常
        """
        # 记录输入电阻
        r_pos_channels = config.get('R_pos_channels', [])
        r_neg_channels = config.get('R_neg_channels', [])
        for i, (r_pos, r_neg) in enumerate(zip(r_pos_channels, r_neg_channels)):
            # 正向输入电阻
            self._record_resistance(channel, 'input_pos', i, f'R_pos{channel+1}_{i+1}', r_pos)
            # 负向输入电阻
            self._record_resistance(channel, 'input_neg', i, f'R_neg{channel+1}_{i+1}', r_neg)

        # 记录偏置电阻 - 无论是否开路都记录（确保BOM包含所有266个电阻）
        self._record_resistance(channel, 'bias_pos', None, f'R_bias_pos{channel+1}', config['R_bias_pos'])
        self._record_resistance(channel, 'bias_neg', None, f'R_bias_neg{channel+1}', config['R_bias_neg'])

        # 记录电流采样电阻
        self._record_resistance(channel, 'sampling_pos', None, f'Rin_pos{channel+1}', config['Rin_pos'])
        self._record_resistance(channel, 'sampling_neg', None, f'Rin_neg{channel+1}', config['Rin_neg'])

        # 记录差分放大器电阻
        self._record_resistance(channel, 'differential_pos', None, f'R1_pos{channel+1}', config['R1_pos'])
        self._record_resistance(channel, 'differential_neg', None, f'R1_neg{channel+1}', config['R1_neg'])

        # 记录反馈电阻
        self._record_resistance(channel, 'feedback_pos', None, f'R2_pos{channel+1}', config['R2_pos'])
        self._record_resistance(channel, 'feedback_neg', None, f'R2_neg{channel+1}', config['R2_neg'])
        
        # 记录高通滤波器电阻（如果启用）
        if config.get('hp_resistance') is not None:
            self._record_resistance(channel, 'highpass', None, f'R_hp{channel+1}', config['hp_resistance'])
            if config.get('hp_bias_r_high') is not None:
                self._record_resistance(channel, 'hp_bias_high', None, f'R_hp_bias_high{channel+1}', config['hp_bias_r_high'])
            if config.get('hp_bias_r_low') is not None:
                self._record_resistance(channel, 'hp_bias_low', None, f'R_hp_bias_low{channel+1}', config['hp_bias_r_low'])
    
    def _record_resistance(self, channel: int, res_type: str, index, name: str, value: float):
        """
        记录单个电阻值
        
        # NO ROLLBACK: 记录失败直接抛出异常
        """
        if value <= 0 and value != float('inf') and value != MAX_RESISTANCE:
            # 直接抛出异常，不隐藏错误
            raise ValueError(
                f"Invalid resistance value: {value} for {name}\n"
                f"Channel: {channel}, Type: {res_type}, Index: {index}"
            )
        
        self.resistance_records.append({
            'layer': self.layer_name,
            'channel': channel + 1,  # 使用1-based索引
            'type': res_type,
            'index': index + 1 if index is not None else None,  # 使用1-based索引
            'name': name,
            'value': value,
            'unit': 'Ω'
        })
    
    def calculate_only(self):
        """
        仅计算电阻值，不生成网表
        
        # NO MOCK: 必须真实计算，禁止虚假数据
        """
        # 电阻计算已在__init__中完成
        # 直接返回记录的电阻值
        return self.resistance_records
    
    def export_resistances(self, output_path=None, include_standardized=False):
        """
        导出电阻值到CSV或DataFrame
        
        # CRITICAL: 导出前必须执行校验
        # NO ROLLBACK: 校验失败直接报错
        """
        import pandas as pd
        
        # 强制校验数据完整性
        if not self.resistance_records:
            raise ValueError("No resistance data to export. Run calculate_only() first.")
        
        df = pd.DataFrame(self.resistance_records)
        
        # 验证数据一致性
        self._validate_resistance_data(df)
        
        if include_standardized:
            # 添加标准化列
            from .resistance_standardizer import ResistanceStandardizer
            standardizer = ResistanceStandardizer()
            for series in ['E96', 'E24', 'E12']:
                df[f'Standardized_{series}'] = df['value'].apply(
                    lambda x: standardizer.standardize(x, series)
                )
        
        if output_path:
            df.to_csv(output_path, index=False)
            
        return df
    
    def _validate_resistance_data(self, df):
        """
        验证电阻数据完整性
        
        # CRITICAL: 此校验必须执行，禁止跳过
        # NO ROLLBACK: 发现问题直接报错
        """
        # 检查必需字段
        required_fields = ['layer', 'channel', 'type', 'name', 'value']
        missing_fields = set(required_fields) - set(df.columns)
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # 检查数据有效性
        invalid_values = df[(df['value'] <= 0) & (df['value'] != float('inf')) & (df['value'] != MAX_RESISTANCE)]
        if not invalid_values.empty:
            raise ValueError(
                f"Invalid resistance values found:\n{invalid_values.to_string()}"
            )
        
        # 检查重复电阻名称
        duplicates = df[df.duplicated('name', keep=False)]
        if not duplicates.empty:
            raise ValueError(
                f"Duplicate resistance names found:\n{duplicates['name'].unique()}"
            )

    def generate_quantization_comparison_data(self):
        """
        生成E96量化对比数据

        此方法在 calculate_resistors() 之后调用，用于生成包含以下内容的对比数据：
        1. 原始权重矩阵
        2. 电阻（浮点数原始值）
        3. 电阻（E96量化值）
        4. 计算带E96量化误差的权重
        5. 量化前后的E96引入的相对误差

        返回:
            Dict: 量化对比数据字典
        """
        if not getattr(self, '_include_quantization_comparison', False):
            return None

        # 重新计算电阻值，捕获原始值和E96值
        r_raw_dict = {}
        r_e96_dict = {}
        R_base = 1000  # 基准电阻

        # 遍历所有通道的电阻配置
        for ch, channel_config in enumerate(self.channel_configs):
            # 获取输入通道电阻列表
            r_pos_channels = channel_config.get('R_pos_channels', [])
            r_neg_channels = channel_config.get('R_neg_channels', [])

            # 输入通道电阻
            for i, (r_pos_raw, r_neg_raw) in enumerate(zip(r_pos_channels, r_neg_channels)):
                # 正向通道
                key_pos = f"layer_{ch}_channel_{i}_type_pos"
                r_raw_dict[key_pos] = r_pos_raw
                r_e96_dict[key_pos] = self._convert_to_standard_value(r_pos_raw) if self.use_e96 else r_pos_raw

                # 负向通道
                key_neg = f"layer_{ch}_channel_{i}_type_neg"
                r_raw_dict[key_neg] = r_neg_raw
                r_e96_dict[key_neg] = self._convert_to_standard_value(r_neg_raw) if self.use_e96 else r_neg_raw

            # 偏置电阻 - 使用独立的索引0
            key_bias_pos = f"layer_{ch}_channel_0_type_bias_pos"
            r_raw_dict[key_bias_pos] = channel_config['R_bias_pos']
            r_e96_dict[key_bias_pos] = self._convert_to_standard_value(channel_config['R_bias_pos']) if self.use_e96 else channel_config['R_bias_pos']

            key_bias_neg = f"layer_{ch}_channel_0_type_bias_neg"
            r_raw_dict[key_bias_neg] = channel_config['R_bias_neg']
            r_e96_dict[key_bias_neg] = self._convert_to_standard_value(channel_config['R_bias_neg']) if self.use_e96 else channel_config['R_bias_neg']

            # 差分放大器电阻 - 使用独立的索引0
            r_raw_dict[f"layer_{ch}_channel_0_type_R1_pos"] = channel_config['R1_pos']
            r_e96_dict[f"layer_{ch}_channel_0_type_R1_pos"] = self._convert_to_standard_value(channel_config['R1_pos']) if self.use_e96 else channel_config['R1_pos']

            r_raw_dict[f"layer_{ch}_channel_0_type_R1_neg"] = channel_config['R1_neg']
            r_e96_dict[f"layer_{ch}_channel_0_type_R1_neg"] = self._convert_to_standard_value(channel_config['R1_neg']) if self.use_e96 else channel_config['R1_neg']

            r_raw_dict[f"layer_{ch}_channel_0_type_R2_pos"] = channel_config['R2_pos']
            r_e96_dict[f"layer_{ch}_channel_0_type_R2_pos"] = self._convert_to_standard_value(channel_config['R2_pos']) if self.use_e96 else channel_config['R2_pos']

            r_raw_dict[f"layer_{ch}_channel_0_type_R2_neg"] = channel_config['R2_neg']
            r_e96_dict[f"layer_{ch}_channel_0_type_R2_neg"] = self._convert_to_standard_value(channel_config['R2_neg']) if self.use_e96 else channel_config['R2_neg']

        # 构建对比数据
        comparison_data = {
            'weight_matrix': self.gains.tolist(),
            'resistor_raw': {},
            'resistor_e96': {},
            'weight_error': {},
            'relative_error_percent': {}
        }

        # 计算每个电阻的量化误差
        for key, r_raw in r_raw_dict.items():
            r_e96 = r_e96_dict.get(key, r_raw)

            comparison_data['resistor_raw'][key] = r_raw
            comparison_data['resistor_e96'][key] = r_e96

            # 计算相对误差（排除开路电阻）
            if r_raw > 0 and r_raw < MAX_RESISTANCE:
                rel_error = abs(r_e96 - r_raw) / r_raw * 100
            else:
                rel_error = 0.0

            comparison_data['relative_error_percent'][key] = rel_error

        # 计算等效权重误差（电阻误差转化为权重误差）
        for key, r_raw in r_raw_dict.items():
            if r_raw > 0 and r_raw < MAX_RESISTANCE:
                w_raw = R_base / r_raw  # 原始权重
                w_e96 = R_base / r_e96_dict.get(key, r_raw)  # E96量化后权重
                w_error = abs(w_e96 - w_raw)
                comparison_data['weight_error'][key] = {
                    'weight_raw': w_raw,
                    'weight_e96': w_e96,
                    'absolute_error': w_error,
                    'relative_error_percent': abs(w_e96 - w_raw) / w_raw * 100 if w_raw != 0 else 0
                }

        # 统计汇总 - 统计所有有效电阻的误差
        valid_error_list = []
        for key, rel_error in comparison_data['relative_error_percent'].items():
            r_raw = r_raw_dict.get(key, 0)
            if r_raw > 0 and r_raw < MAX_RESISTANCE:
                valid_error_list.append(rel_error)

        comparison_data['statistics'] = {
            'mean_relative_error': float(np.mean(valid_error_list)) if valid_error_list else 0,
            'max_relative_error': float(np.max(valid_error_list)) if valid_error_list else 0,
            'min_relative_error': float(np.min(valid_error_list)) if valid_error_list else 0,
            'within_1pct': float(sum(1 for e in valid_error_list if e < 1) / len(valid_error_list) * 100) if valid_error_list else 100,
            'within_5pct': float(sum(1 for e in valid_error_list if e < 5) / len(valid_error_list) * 100) if valid_error_list else 100,
            'total_count': len(valid_error_list)
        }

        return comparison_data


class DenseCircuitFactory:
    """使用组合模式的带符号加法器电路工厂类"""

    @staticmethod
    def create(gains=None, biases=None, R_values=None,
               opamp_config=None, use_e96=False, use_relu=False, relu_config=None, high_pass_config=None, power_supply_config=None, layer_name=None,
               include_quantization_comparison=False):
        """
        创建带符号加法器电路，通过组合模式实现灵活配置

        参数:
            gains: 增益矩阵，形状为 (weights, channels)
            biases: 偏置向量，形状为 (channels,)
            R_values: 电阻值数组，如果为None则根据增益自动计算
            opamp_config: 运放配置字典，例如:
                - {'model': 'ideal'} 使用理想运放模型
                - {'model': 'LM324'} 使用LM324运放模型
                - {'model': 'TL084'} 使用TL084运放模型
                - {'model': 'OPAx205A', 'include_file': '...'} 使用OPAx205A模型
            use_e96: 是否使用E96系列电阻
            use_relu: 是否使用ReLU激活
            relu_config: ReLU配置字典，例如:
                - {'type': 'none'} 不使用ReLU激活
                - {'type': 'op_amp', 'gain': 1.0, 'R_value': 10e3, 'diode_model': '1N4148', 'clamp_voltage': 0.0}
                  使用运放实现的ReLU激活
                - {'type': 'diode_clamp', 'R_value': 10e3, 'diode_model': '1N4148', 'clamp_voltage': 0.0}
                  使用二极管钳位实现的ReLU激活
            high_pass_config: 高通滤波器配置字典，例如:
                - {'enable': False} 禁用高通滤波器
                - {'enable': True, 'cutoff_freq': 0.5, 'bias_voltage': 2.5}
                  启用高通滤波器，0.5Hz截止频率，2.5V bias电压
            include_quantization_comparison: 是否包含E96量化对比数据，默认为False

        返回:
            DenseCircuit实例
        """        # 创建运放模型
        opamp_model = None
        if opamp_config:
            if opamp_config.get('model') == 'ideal':
                opamp_model = IdealOpAmpModel()
            else:
                opamp_model = OpAmpModelFactory.create_model(opamp_config)
                # 创建ReLU模型
        local_use_relu = use_relu
        local_relu_config = relu_config or {}

        # 确定是否需要特殊处理'none'类型的ReLU
        if local_relu_config.get('type', '') == 'none':
            local_use_relu = False

        # 准备运放模型用于op_amp类型的ReLU
        # ReluModelFactory会在内部处理创建运放模型，但我们可以提供预先创建好的运放模型
        opamp_for_relu = None
        if local_use_relu and local_relu_config.get('type', '') == 'op_amp':
            # 如果有特定的ReLU运放配置，使用它；否则使用主电路的运放配置/模型
            if 'opamp_config' in local_relu_config:
                opamp_for_relu = OpAmpModelFactory.create_model(
                    local_relu_config['opamp_config'])
            else:
                # 复用主电路的运放模型
                opamp_for_relu = opamp_model

        # 创建并返回电路实例
        return DenseCircuit(
            gains=gains,
            biases=biases,
            R_values=R_values,
            opamp_config=opamp_config,
            use_e96=use_e96,
            use_relu=local_use_relu,
            relu_config=local_relu_config,
            high_pass_config=high_pass_config,
            power_supply_config=power_supply_config,
            layer_name=layer_name,
            include_quantization_comparison=include_quantization_comparison
        )

    @staticmethod
    def create_ideal(gains=None, biases=None, R_values=None, use_e96=False, use_relu=False, high_pass_config=None):
        """创建使用理想运放模型的电路"""
        opamp_config = {'model': 'ideal'}
        # 如果需要ReLU，设置默认的ReLU配置
        relu_config = {'type': 'op_amp', 'opamp_config': {
            'model': 'ideal'}} if use_relu else None
        return DenseCircuitFactory.create(
            gains=gains,
            biases=biases,
            R_values=R_values,
            opamp_config=opamp_config,
            use_e96=use_e96,
            use_relu=use_relu,
            relu_config=relu_config,
            high_pass_config=high_pass_config
        )

    @staticmethod
    def create_with_relu(gains=None, biases=None, R_values=None,
                         opamp_config=None, use_e96=False, relu_type='op_amp', high_pass_config=None):
        """创建带ReLU激活的电路"""
        # 根据ReLU类型创建适当的配置
        if relu_type == 'op_amp':
            relu_config = {
                'type': 'op_amp',
                'gain': 1.0,
                'R_value': 10e3,
                # 如果有运放配置，也将其用于ReLU的运放
                'opamp_config': opamp_config
            }
        elif relu_type == 'diode_clamp':
            relu_config = {'type': 'diode_clamp', 'R_value': 10e3}
        else:
            relu_config = {'type': 'none'}

        # 让ReluModelFactory通过工厂模式创建ReLU模型
        return DenseCircuitFactory.create(
            gains=gains,
            biases=biases,
            R_values=R_values,
            opamp_config=opamp_config,
            use_e96=use_e96,
            use_relu=True,
            relu_config=relu_config,
            high_pass_config=high_pass_config
        )

    @staticmethod
    def create_ideal_with_relu(gains=None, biases=None, R_values=None, use_e96=False, high_pass_config=None):
        """创建使用理想运放模型和ReLU激活的电路"""
        # 设置理想运放配置
        opamp_config = {'model': 'ideal'}

        # 设置ReLU配置，使用与主电路相同的理想运放模型
        relu_config = {
            'type': 'op_amp',
            'gain': 1.0,
            'R_value': 10e3,
            'opamp_config': {'model': 'ideal'}  # 为ReLU电路明确指定理想运放模型
        }        # 使用工厂方法创建电路
        return DenseCircuitFactory.create(
            gains=gains,
            biases=biases,
            R_values=R_values,
            opamp_config=opamp_config,
            use_e96=use_e96,
            use_relu=True,
            relu_config=relu_config,
            high_pass_config=high_pass_config
        )

    @staticmethod
    def create_with_tanh(gains=None, biases=None, R_values=None,
                         opamp_config=None, use_e96=False, 
                         scaling_factor=1.0, add_high_pass=True, 
                         high_pass_cutoff=1.0, high_pass_config=None):
        """
        创建带tanh激活的电路，用于解决DC偏置问题
        
        参数:
            gains: 增益矩阵，形状为 (weights, channels)
            biases: 偏置向量，形状为 (channels,)
            R_values: 电阻值数组，如果为None则根据增益自动计算
            opamp_config: 运放配置字典
            use_e96: 是否使用E96系列电阻
            scaling_factor: tanh函数的缩放因子，控制激活函数的陡峭程度
            add_high_pass: 是否添加高通滤波器以进一步消除DC偏置
            high_pass_cutoff: 高通滤波器截止频率(Hz)
            high_pass_config: 高通滤波器配置字典
            
        返回:
            DenseCircuit实例，包含tanh激活和可选的高通滤波
        """
        # 设置tanh激活配置
        relu_config = {
            'type': 'tanh',
            'gain': 1.0,
            'R_value': 10e3,
            'scaling_factor': scaling_factor,
            'add_high_pass': add_high_pass,
            'high_pass_cutoff': high_pass_cutoff,
            'opamp_config': opamp_config  # 使用与主电路相同的运放配置
        }

        return DenseCircuitFactory.create(
            gains=gains,
            biases=biases,
            R_values=R_values,
            opamp_config=opamp_config,
            use_e96=use_e96,
            use_relu=True,  # 虽然是tanh，但仍使用ReLU参数名保持兼容性
            relu_config=relu_config,
            high_pass_config=high_pass_config
        )

    @staticmethod
    def create_ideal_with_tanh(gains=None, biases=None, R_values=None, 
                               use_e96=False, scaling_factor=1.0, 
                               add_high_pass=True, high_pass_cutoff=1.0, high_pass_config=None):
        """创建使用理想运放模型和tanh激活的电路"""
        # 设置理想运放配置
        opamp_config = {'model': 'ideal'}

        return DenseCircuitFactory.create_with_tanh(
            gains=gains,
            biases=biases,
            R_values=R_values,
            opamp_config=opamp_config,
            use_e96=use_e96,
            scaling_factor=scaling_factor,
            add_high_pass=add_high_pass,
            high_pass_cutoff=high_pass_cutoff,
            high_pass_config=high_pass_config
        )
