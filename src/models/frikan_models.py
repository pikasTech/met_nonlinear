"""
神经网络模型库 - FRIKAN模型模块

此模块包含FRIKAN及其变体模型，这些模型结合了IIR滤波器和KAN（Kolmogorov-Arnold Network）网络
用于建模和补偿非线性动态系统。
"""

from typing import List
from tfkan.layers import DenseKAN
from experimental.mimoiir import DIAGIIR, SIMOIIR
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from .base_models import BaseModel
from calibration_analyzer.exam_class import System


def system2params(nonlinear_systems: List[System], fs):
    # 从系统对象创建 IIR-LNRNN 模型
    if nonlinear_systems is None:
        return None
    nonlinear_params_list = []
    for system in nonlinear_systems:
        b0, b1, b2, a0, a1, a2 = system.get_iir_parameters(fs)
        params = {
            'a1': a1,
            'a2': a2,
            'b0': b0,
            'b1': b1,
            'b2': b2,
        }
        nonlinear_params_list.append(params)
    return nonlinear_params_list


class FRIKAN(BaseModel):
    """
    FRIKAN (Frequency-response IIR-KAN) 模型

    结合了IIR滤波器和KAN网络，用于频率响应和非线性动态系统建模。
    """

    def __init__(self,
                 iir_params_list,
                 grid_size=5,
                 grid_range=(-1.0, 1.0),
                 spline_order=3,
                 basis_activation='silu',
                 fs=2000,
                 checkpoint_dir='data',
                 fix_scale_factor=True,
                 disable_basis_activation=True,
                 inner_kan_units=4,
                 inner_kan_layers=1,
                 use_fast_model=True,
                 iir_trainable=False,
                 iir_init_by_system=True,
                 dropout_rate=0.2,
                 kan_log_grid=False,
                 kan_grid_expand=True,
                 save_each_epoch=False,
                 model_subcfg={}
                 ):
        """
        初始化FRIKAN模型

        Args:
            iir_params_list: IIR滤波器参数列表
            grid_size: KAN网络的网格大小
            grid_range: 网格范围，如(-1.0, 1.0)
            spline_order: 样条阶数
            basis_activation: 基底激活函数
            fs: 采样频率
            checkpoint_dir: 检查点目录
            fix_scale_factor: 是否固定缩放因子
            disable_basis_activation: 是否禁用基底激活
            inner_kan_units: 内部KAN单元数量
            inner_kan_layers: 内部KAN层数
            use_fast_model: 是否使用快速模型
            iir_trainable: IIR参数是否可训练
            iir_init_by_system: 是否使用系统参数初始化IIR
            dropout_rate: Dropout比率
            kan_log_grid: 是否使用对数网格
            kan_grid_expand: 是否扩展网格
            save_each_epoch: 是否每个周期保存
            model_subcfg: 模型子配置
        """
        self.model_name = 'FRIKAN'
        self.callback = None
        if iir_params_list is not None:
            features_num = len(iir_params_list)
            a1_list = [iir_param['a1'] for iir_param in iir_params_list]
            a2_list = [iir_param['a2'] for iir_param in iir_params_list]
            b0_list = [iir_param['b0'] for iir_param in iir_params_list]
            b1_list = [iir_param['b1'] for iir_param in iir_params_list]
            b2_list = [iir_param['b2'] for iir_param in iir_params_list]
            iir = SIMOIIR(
                units=features_num,
                a1_list=a1_list,
                a2_list=a2_list,
                b0_list=b0_list,
                b1_list=b1_list,
                b2_list=b2_list,
                fs=fs,
                trainable=iir_trainable,
                init_by_system=iir_init_by_system
            )
            fast_iir = DIAGIIR(
                units=features_num,
                a1_list=a1_list,
                a2_list=a2_list,
                b0_list=b0_list,
                b1_list=b1_list,
                b2_list=b2_list,
                fs=fs,
                trainable=iir_trainable,
                init_by_system=iir_init_by_system
            )
        else:
            features_num = 1
            iir = SIMOIIR(
                units=features_num,
                fs=fs,
                a1_list=[0.0],
                a2_list=[0.0],
                b0_list=[1.0],
                b1_list=[0.0],
                b2_list=[0.0],
                trainable=iir_trainable,
                init_by_system=iir_init_by_system
            )

            fast_iir = DIAGIIR(
                units=features_num,
                fs=fs,
                a1_list=[0.0],
                a2_list=[0.0],
                b0_list=[1.0],
                b1_list=[0.0],
                b2_list=[0.0],
                trainable=iir_trainable,
                init_by_system=iir_init_by_system
            )
        kan = DenseKAN(
            units=1,
            grid_size=grid_size,
            grid_range=grid_range,
            spline_order=spline_order,
            use_bias=True,
            basis_activation=basis_activation,
            fix_scale_factor=fix_scale_factor,
            disable_basis_activation=disable_basis_activation,
            kan_log_grid=kan_log_grid,
            grid_expand=kan_grid_expand
        )

        self.kan_inner_layers = [
            DenseKAN(
                units=inner_kan_units,
                grid_size=grid_size,
                grid_range=grid_range,
                spline_order=spline_order,
                use_bias=True,
                basis_activation=basis_activation,
                fix_scale_factor=fix_scale_factor,
                disable_basis_activation=disable_basis_activation,
                kan_log_grid=kan_log_grid,
                grid_expand=kan_grid_expand
            ) for _ in range(inner_kan_layers)
        ]

        self.dropout_rate = dropout_rate
        self.dropout_layer = tf.keras.layers.Dropout(
            self.dropout_rate) if self.dropout_rate > 0.0 else None
        self.kan = kan
        self.iir = iir
        self.fast_iir = fast_iir
        self.kan_log_grid = kan_log_grid
        self.fs = fs
        self.features_num = features_num
        self.use_fast_model = use_fast_model
        self.dropout_position = 'input'
        self.save_each_epoch = save_each_epoch
        self.init_checkpoint(checkpoint_dir)
        self.build_model()

    def build_model(self):
        """
        构建并编译模型。
        """
        # 输入层，假设输入特征维度为1
        input_layer = tf.keras.layers.Input(shape=(None, 1), name='input')
        if self.dropout_layer is not None and self.dropout_position == 'input':
            input_drop_out = self.dropout_layer(input_layer)
        else:
            input_drop_out = input_layer

        # 初始 IIR 层
        # 假设 self.iir 已经定义，输出形状为 (None, None, 8)
        iir_out = self.iir(input_drop_out)
        fast_iir_out = tf.keras.layers.Input(
            shape=(None, iir_out.shape[2]), name='fast_input')

        # 添加 dropout 层
        if self.dropout_layer is not None and self.dropout_position == 'iir':
            iir_drop_out = self.dropout_layer(iir_out)
            fast_iir_drop_out = self.dropout_layer(fast_iir_out)
        else:
            iir_drop_out = iir_out
            fast_iir_drop_out = fast_iir_out

        kan_inner_output = self.build_kan_inner_layers(iir_drop_out)
        fast_kan_inner_output = self.build_kan_inner_layers(fast_iir_drop_out)

        # 添加 dropout 层
        if self.dropout_layer is not None and self.dropout_position == 'output':
            kan_inner_output = self.dropout_layer(kan_inner_output)
            fast_kan_inner_output = self.dropout_layer(fast_kan_inner_output)

        output = self.kan(kan_inner_output)
        fast_output = self.kan(fast_kan_inner_output)

        self.model = tf.keras.Model(
            inputs=input_layer, outputs=output, name='FRIKAN')
        self.model.build(input_shape=(None, None, 1))
        if self.use_fast_model:
            self.fast_model = tf.keras.Model(
                inputs=fast_iir_out, outputs=fast_output, name='fast_FRIKAN')
            self.fast_model.build(input_shape=(None, None, iir_out.shape[2]))

    @classmethod
    def fromSystem(cls,
                   hi_list,
                   fs,
                   grid_size=5,
                   grid_range=(-1.0, 1.0),
                   spline_order=3,
                   basis_activation='silu',
                   checkpoint_dir='data',
                   fix_scale_factor=True,
                   disable_basis_activation=True,
                   inner_kan_units=4,
                   inner_kan_layers=1,
                   iir_trainable=False,
                   use_fast_model=True,
                   use_debug=False,
                   iir_init_by_system=True,
                   kan_log_grid=False,
                   kan_grid_expand=True,
                   save_each_epoch=False,
                   model_subcfg={}
                   ):
        """
        从系统参数构建FRIKAN模型

        Args:
            hi_list: 系统参数列表
            fs: 采样频率
            grid_size: 网格大小
            grid_range: 网格范围
            spline_order: 样条阶数
            basis_activation: 基底激活函数
            checkpoint_dir: 检查点目录
            fix_scale_factor: 是否固定缩放因子
            disable_basis_activation: 是否禁用基底激活
            inner_kan_units: 内层KAN单元数
            inner_kan_layers: 内层KAN层数
            iir_trainable: IIR参数是否可训练
            use_fast_model: 是否使用快速模型
            use_debug: 是否启用调试
            iir_init_by_system: 是否使用系统参数初始化IIR
            kan_log_grid: 是否使用对数网格
            kan_grid_expand: 是否扩展网格
            save_each_epoch: 是否每个周期保存
            model_subcfg: 模型子配置

        Returns:
            FRIKAN模型实例
        """
        iir_params_list = system2params(
            hi_list, fs)
        if use_debug:
            for i in range(len(hi_list)):
                hi_list[i].plot(label=f'IIRKAN H{i}')
        kan = cls(iir_params_list,
                  grid_size=grid_size,
                  grid_range=grid_range,
                  spline_order=spline_order,
                  basis_activation=basis_activation,
                  fs=fs,
                  fix_scale_factor=fix_scale_factor,
                  checkpoint_dir=checkpoint_dir,
                  disable_basis_activation=disable_basis_activation,
                  inner_kan_units=inner_kan_units,
                  inner_kan_layers=inner_kan_layers,
                  iir_trainable=iir_trainable,
                  use_fast_model=use_fast_model,
                  iir_init_by_system=iir_init_by_system,
                  kan_log_grid=kan_log_grid,
                  kan_grid_expand=kan_grid_expand,
                  save_each_epoch=save_each_epoch,
                  model_subcfg=model_subcfg
                  )
        return kan

    def plot_spline(
            self,
            spline_points=200,
            skip_feature=[],
            use_debug=False,
            use_derivative=False,
            feature_range=[-1.0, 1.0]
    ):
        """
        绘制样条曲线

        Args:
            spline_points: 样条点数
            skip_feature: 要跳过的特征
            use_debug: 是否显示调试信息
            use_derivative: 是否计算导数
            feature_range: 特征范围
        """
        coler_list = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
        in_size = self.features_num

        # 构造输入数据，每个特征通道均从 0 到 1 均匀分布
        xmin = tf.Variable(feature_range[0], dtype=tf.float32)
        xmax = tf.Variable(feature_range[1], dtype=tf.float32)
        inputs = tf.linspace(xmin, xmax, spline_points)
        # 形状为 (batch_size, in_size)
        inputs = tf.stack([inputs] * in_size, axis=1)
        if use_debug:
            print(f'inputs: {inputs.numpy()}')

        # 计算样条输出
        spline_out = self.kan.compute_spline_output(
            inputs)  # 假设输出形状为 (batch_size, in_size, out_size)

        if use_debug:
            print(f'spline_out: {spline_out.numpy()}')

        # 绘制每个特征的输入和对应的输出曲线
        plt.figure(figsize=(12, 8))

        # 绘制 grid
        grid = self.kan.grid.numpy()
        # 绘制 grid 点
        for i in range(in_size):
            plt.plot(grid, np.zeros_like(grid), marker='o',
                     linestyle='', color='blue')

        feature_outputs = []
        for i in range(self.features_num):
            if i in skip_feature:
                continue
            # 获取形状为 (batch_size, out_size) 的当前特征的输出
            feature_output = spline_out[:, i, :][:, 0]
            feature_outputs.append(feature_output)
            plt.plot(inputs[:, 0].numpy(), feature_output.numpy(),
                     marker='', linestyle='-',  label=f"Feature {i+1}", color=coler_list[i % len(coler_list)])
            plt.xlabel(f"Feature {i+1} Input Value (0 to 1)")
            plt.ylabel("Spline Output")
            plt.legend()
            plt.title(f"Spline Output Curves for Feature {i+1}")

        if use_derivative:
            # 计算并绘制斜率（导数）
            for i in range(self.features_num):
                if i in skip_feature:
                    continue
                # 获取当前特征的输出
                feature_output = feature_outputs[i].numpy()  # 取第一个输出通道

                # 计算过零点斜率(yn/xn)
                slopes = [feature_output[i] / inputs[i, 0].numpy()
                          for i in range(len(feature_output))]

                # 绘制斜率曲线
                plt.plot(inputs[:, 0].numpy(), slopes, marker='.',
                         linestyle='--', label=f"Feature {i+1} Derivatives", color=coler_list[i % len(coler_list)])
                plt.legend()

    def assign_grid_xnyn(self, feature_index, xn, yn):
        """
        为指定特征赋值网格点值

        Args:
            feature_index: 特征索引
            xn: x值列表
            yn: y值列表
        """
        self.kan.assign_grid_xnyn(feature_index, xn, yn)

    def assign_grid_xnkn(self, feature_index, xn, kn):
        """
        为指定特征赋值网格点和斜率

        Args:
            feature_index: 特征索引
            xn: x值列表
            kn: 斜率列表
        """
        self.kan.assign_grid_xnkn(feature_index, xn, kn)

    def assign_weights(self, feature_index, weight):
        """
        为指定特征赋值权重

        Args:
            feature_index: 特征索引
            weight: 权重值
        """
        self.kan.assign_weights(weight)

    def build_kan_inner_layers(self, iir_out):
        """
        构建KAN内层

        Args:
            iir_out: IIR输出

        Returns:
            处理后的张量
        """
        # 直接全连接 KAN 的内层
        x = iir_out
        for i, kan_inner in enumerate(self.kan_inner_layers):
            x = kan_inner(x)
            if i + 1 == len(self.kan_inner_layers) // 2:
                if self.dropout_layer is not None and self.dropout_position == 'inner':
                    # 在最中间的层加入 dropout
                    x = self.dropout_layer(x)
        return x


class FRIKAND(FRIKAN):
    """
    FRIKAND (FRIKAN Dense) 模型

    用普通 Dense 层替换原有的 DenseKAN，实现对 FRIKAN 的消融。
    与 FRIKAN2 类似，通过继承 FRIKAN 并重写必要部分来切换网络结构。
    """

    def __init__(self,
                 iir_params_list,
                 grid_size=5,
                 grid_range=(-1.0, 1.0),
                 spline_order=3,
                 basis_activation='silu',
                 fs=2000,
                 checkpoint_dir='data',
                 fix_scale_factor=True,
                 disable_basis_activation=True,
                 inner_kan_units=4,
                 inner_kan_layers=1,
                 use_fast_model=True,
                 iir_trainable=False,
                 iir_init_by_system=True,
                 dropout_rate=0.2,
                 kan_log_grid=False,
                 kan_grid_expand=True,
                 save_each_epoch=False
                 ):
        """
        这里和 FRIKAN 的构造函数保持同样的参数签名，方便直接替换。
        重点是：我们会在构造函数中把 self.kan 换成 Dense，把 self.kan_inner_layers
        换成普通 Dense 层列表，然后保持其它逻辑不变。
        """
        # 先调用父类构造函数，完成 IIR 初始化、checkpoint 初始化等
        super().__init__(iir_params_list=iir_params_list,
                         grid_size=grid_size,
                         grid_range=grid_range,
                         spline_order=spline_order,
                         basis_activation=basis_activation,
                         fs=fs,
                         checkpoint_dir=checkpoint_dir,
                         fix_scale_factor=fix_scale_factor,
                         disable_basis_activation=disable_basis_activation,
                         inner_kan_units=inner_kan_units,
                         inner_kan_layers=inner_kan_layers,
                         use_fast_model=use_fast_model,
                         iir_trainable=iir_trainable,
                         iir_init_by_system=iir_init_by_system,
                         dropout_rate=dropout_rate,
                         kan_log_grid=kan_log_grid,
                         kan_grid_expand=kan_grid_expand,
                         save_each_epoch=save_each_epoch)

        # 注意：父类 __init__() 里已经 build_model() 过一次了，其中用的还是 KAN。
        # 我们要覆盖掉 self.kan、self.kan_inner_layers 然后再重建模型。

        self.model_name = 'FRIDENSE'

        # 1) 覆盖掉原先的 self.kan，改用普通的 Dense 作为输出层
        self.kan = tf.keras.layers.Dense(
            units=1,
            activation=None,    # 或 'linear'
            name='final_dense'
        )

        # 2) 覆盖掉原先的 self.kan_inner_layers，用普通 Dense 列表来替代
        self.kan_inner_layers = []
        for i in range(inner_kan_layers):
            # 可以根据自己需求定激活函数
            dense_layer = tf.keras.layers.Dense(
                units=inner_kan_units,
                activation='relu',
                name=f'fridense_inner_{i}'
            )
            self.kan_inner_layers.append(dense_layer)

        # 3) 重新 build 一遍模型（不再使用父类的 build_model 内容）
        self.build_model()

    def build_model(self):
        """
        直接复制 FRIKAN 的 build_model 逻辑，但把"KAN部分"改为普通 Dense。
        """
        # 输入层
        input_layer = tf.keras.layers.Input(shape=(None, 1), name='input')
        if self.dropout_layer is not None and self.dropout_position == 'input':
            input_drop_out = self.dropout_layer(input_layer)
        else:
            input_drop_out = input_layer

        # IIR 层
        iir_out = self.iir(input_drop_out)
        fast_iir_out = tf.keras.layers.Input(
            shape=(None, iir_out.shape[2]), name='fast_input')

        # dropout
        if self.dropout_layer is not None and self.dropout_position == 'iir':
            iir_drop_out = self.dropout_layer(iir_out)
            fast_iir_drop_out = self.dropout_layer(fast_iir_out)
        else:
            iir_drop_out = iir_out
            fast_iir_drop_out = fast_iir_out

        # 中间若干层（原先是 KAN 内层，这里改为 Dense）
        kan_inner_output = self.build_kan_inner_layers(iir_drop_out)
        fast_kan_inner_output = self.build_kan_inner_layers(fast_iir_drop_out)

        # dropout
        if self.dropout_layer is not None and self.dropout_position == 'output':
            kan_inner_output = self.dropout_layer(kan_inner_output)
            fast_kan_inner_output = self.dropout_layer(fast_kan_inner_output)

        # 最终输出层（self.kan 已经被普通 Dense 覆盖）
        output = self.kan(kan_inner_output)
        fast_output = self.kan(fast_kan_inner_output)

        # 建立完整模型
        self.model = tf.keras.Model(
            inputs=input_layer,
            outputs=output,
            name='FRIDENSE'
        )
        self.model.build(input_shape=(None, None, 1))

        if self.use_fast_model:
            self.fast_model = tf.keras.Model(
                inputs=fast_iir_out,
                outputs=fast_output,
                name='fast_FRIDENSE'
            )
            self.fast_model.build(
                input_shape=(None, None, iir_out.shape[2])
            )

    def build_kan_inner_layers(self, iir_out):
        """
        用普通 Dense 实现原先的 KAN 中间层。
        """
        x = iir_out
        for i, dense_layer in enumerate(self.kan_inner_layers):
            x = dense_layer(x)

            # 如果要在中间插入 dropout，可以根据自身需要来加：
            # if i + 1 == len(self.kan_inner_layers) // 2:
            #     if self.dropout_layer is not None and self.dropout_position == 'inner':
            #         x = self.dropout_layer(x)

        return x


class FRIKAN2(FRIKAN):
    """
    FRIKAN2 模型，使用跳跃连接
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = 'FRIKAN2'

    def build_kan_inner_layers(self, iir_out):
        """
        使用跳跃连接构建KAN内层
        """
        # 通过 skip_connections 进行跳跃连接
        input_units = self.iir.units
        kan_inner_units = self.kan_inner_layers[0].units
        if input_units != kan_inner_units:
            self.adjust_conv_initial = tf.keras.layers.Conv1D(
                filters=kan_inner_units,
                kernel_size=1,
                padding='same',
                activation=None,  # 通常不使用激活函数
                name='adjust_conv_initial'
            )
            x = self.adjust_conv_initial(iir_out)
        else:
            x = iir_out

        skip_connections = [x]  # 第一个跳跃连接是输入
        for kan_inner in self.kan_inner_layers:
            x = kan_inner(x)
            skip_connections.append(x)  # 保存跳跃连接

        if skip_connections:
            x = tf.keras.layers.Add()(skip_connections)

        return x


class FRIKAN3(FRIKAN):
    """
    FRIKAN3 模型，使用残差连接
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = 'FRIKAN3'

    def build_kan_inner_layers(self, iir_out):
        """
        使用残差连接构建KAN内层
        """
        # 进行残差连接
        input_units = self.iir.units
        kan_inner_units = self.kan_inner_layers[0].units

        # 如果输入和第一个内层的通道数不一致，进行调整
        if input_units != kan_inner_units:
            self.adjust_conv_initial = tf.keras.layers.Conv1D(
                filters=kan_inner_units,
                kernel_size=1,
                padding='same',
                activation=None,
                name='adjust_conv_initial'
            )
            x = self.adjust_conv_initial(iir_out)
        else:
            x = iir_out

        # 遍历每一层并进行残差连接
        for kan_inner in self.kan_inner_layers:
            residual = x  # 保留当前层的输入作为残差
            x = kan_inner(x)
            x = tf.keras.layers.Add()([x, residual])  # 残差连接

        return x


class FRIKAN4(FRIKAN):
    """
    FRIKAN4 模型，使用通道平均
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = 'FRIKAN4'

    def build_kan_inner_layers(self, iir_out):
        """
        对每层的通道输出进行平均
        """
        # 对每一层的各通道输出聚合，再送入下一层
        x = iir_out
        for kan_inner in self.kan_inner_layers:
            out = kan_inner(x)
            # 假如 out.shape = (None, None, 4)，对四个通道的输出求和得到 out_sum=(None, None, 1)
            out_mean = tf.reduce_mean(out, axis=-1, keepdims=True)
            x = out_mean
        return x


class FRIKAN6(FRIKAN):
    """
    FRIKAN6 模型，使用替代结构（注意：当前实现有问题）
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = 'FRIKAN5'

    def build_kan_layers(self, iir_out):
        """
        构建KAN层（替代结构）
        """
        # 获取输入和第一个内层的通道数
        input_units = self.iir.units
        kan_inner_units = self.kan_inner_layers[0].units

        # 如果输入和第一个内层的通道数不一致，进行调整
        if input_units != kan_inner_units:
            self.adjust_conv_initial = tf.keras.layers.Conv1D(
                filters=kan_inner_units,
                kernel_size=1,
                padding='same',
                activation=None,
                name='adjust_conv_initial'
            )
            x = self.adjust_conv_initial(iir_out)
        else:
            x = iir_out

        x = self.kan(x)

        # 跳跃连接存储
        skip_connections = [x]  # 第一个跳跃连接是输入

        # 遍历每一层进行处理
        for kan_inner in self.kan_inner_layers:
            x = kan_inner(x)
            x = tf.reduce_mean(x, axis=-1, keepdims=True)
            skip_connections.append(x)  # 添加到跳跃连接列表
            if skip_connections:
                x = tf.keras.layers.Add()(skip_connections)  # 密集残差连接

        return x


class FRIKAN23(FRIKAN):
    """
    FRIKAN23 模型，结合FRIKAN2和FRIKAN3的特点
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = 'FRIKAN23'

    def build_kan_inner_layers(self, iir_out):
        """
        结合跳跃连接和残差连接
        """
        # 获取输入和第一个内层的通道数
        input_units = self.iir.units
        kan_inner_units = self.kan_inner_layers[0].units

        # 如果输入和第一个内层的通道数不一致，进行调整
        if input_units != kan_inner_units:
            self.adjust_conv_initial = tf.keras.layers.Conv1D(
                filters=kan_inner_units,
                kernel_size=1,
                padding='same',
                activation=None,
                name='adjust_conv_initial'
            )
            x = self.adjust_conv_initial(iir_out)
        else:
            x = iir_out

        # 跳跃连接存储
        skip_connections = [x]  # 第一个跳跃连接是输入

        # 遍历每一层进行处理
        for kan_inner in self.kan_inner_layers:
            residual = x  # 保留当前层的输入作为残差
            x = kan_inner(x)
            skip_connections.append(x)  # 添加到跳跃连接列表
            x = tf.keras.layers.Add()([x, residual])  # 残差连接

        # 将所有跳跃连接的输出相加
        if skip_connections:
            x = tf.keras.layers.Add()(skip_connections)

        return x


class FRIKAN5(FRIKAN):
    """
    FRIKAN5 模型，使用密集残差连接
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = 'FRIKAN5'

    def build_kan_inner_layers(self, iir_out):
        """
        使用密集残差连接构建KAN内层
        """
        # 获取输入和第一个内层的通道数
        input_units = self.iir.units
        kan_inner_units = self.kan_inner_layers[0].units

        # 如果输入和第一个内层的通道数不一致，进行调整
        if input_units != kan_inner_units:
            self.adjust_conv_initial = tf.keras.layers.Conv1D(
                filters=kan_inner_units,
                kernel_size=1,
                padding='same',
                activation=None,
                name='adjust_conv_initial'
            )
            x = self.adjust_conv_initial(iir_out)
        else:
            x = iir_out

        # 跳跃连接存储
        skip_connections = [x]  # 第一个跳跃连接是输入

        # 遍历每一层进行处理
        for kan_inner in self.kan_inner_layers:
            x = kan_inner(x)
            skip_connections.append(x)  # 添加到跳跃连接列表
            if skip_connections:
                x = tf.keras.layers.Add()(skip_connections)  # 密集残差连接

        return x


class CNNKAN(BaseModel):
    """
    CNNKAN (1D CNN based KAN) 模型
    
    用 Conv1D 完全替换 IIR 滤波器层，直接继承 BaseModel 构建新模型。
    参考 LSTM 的简洁写法，不需要传入 system 参数。
    
    架构: Input(1) → Conv1D(filters=8, kernel_size=3) → DenseKAN×6 → DenseKAN → Output(1)
    """

    def __init__(self,
                 grid_size=5,
                 grid_range=(-1.0, 1.0),
                 spline_order=3,
                 basis_activation='silu',
                 fs=2000,
                 checkpoint_dir='data',
                 fix_scale_factor=True,
                 disable_basis_activation=True,
                 inner_kan_units=6,
                 inner_kan_layers=6,
                 use_fast_model=True,
                 cnn_filters=8,
                 cnn_kernel_size=3,
                 dropout_rate=0.2,
                 kan_log_grid=False,
                 kan_grid_expand=True,
                 save_each_epoch=False,
                 model_subcfg={}
                 ):
        """
        初始化 CNNKAN 模型

        Args:
            grid_size: KAN网络的网格大小
            grid_range: 网格范围，如(-1.0, 1.0)
            spline_order: 样条阶数
            basis_activation: 基底激活函数
            fs: 采样频率
            checkpoint_dir: 检查点目录
            fix_scale_factor: 是否固定缩放因子
            disable_basis_activation: 是否禁用基底激活
            inner_kan_units: 内部KAN单元数量
            inner_kan_layers: 内部KAN层数
            use_fast_model: 是否使用快速模型
            cnn_filters: Conv1D 输出通道数 (h8 = 8)
            cnn_kernel_size: Conv1D 卷积核大小
            dropout_rate: Dropout比率
            kan_log_grid: 是否使用对数网格
            kan_grid_expand: 是否扩展网格
            save_each_epoch: 是否每个周期保存
            model_subcfg: 模型子配置
        """
        self.model_name = 'CNNKAN'
        self.callback = None
        
        self.cnn_filters = cnn_filters
        self.cnn_kernel_size = cnn_kernel_size
        self.cnn = tf.keras.layers.Conv1D(
            filters=cnn_filters,
            kernel_size=cnn_kernel_size,
            strides=1,
            padding='same',
            activation='linear',
            name='cnn_filter'
        )
        
        self.fast_cnn = tf.keras.layers.Conv1D(
            filters=cnn_filters,
            kernel_size=cnn_kernel_size,
            strides=1,
            padding='same',
            activation='linear',
            name='fast_cnn_filter'
        )
        self.fast_iir = self.fast_cnn
        
        self.kan = DenseKAN(
            units=1,
            grid_size=grid_size,
            grid_range=grid_range,
            spline_order=spline_order,
            use_bias=True,
            basis_activation=basis_activation,
            fix_scale_factor=fix_scale_factor,
            disable_basis_activation=disable_basis_activation,
            kan_log_grid=kan_log_grid,
            grid_expand=kan_grid_expand
        )

        self.kan_inner_layers = [
            DenseKAN(
                units=inner_kan_units,
                grid_size=grid_size,
                grid_range=grid_range,
                spline_order=spline_order,
                use_bias=True,
                basis_activation=basis_activation,
                fix_scale_factor=fix_scale_factor,
                disable_basis_activation=disable_basis_activation,
                kan_log_grid=kan_log_grid,
                grid_expand=kan_grid_expand
            ) for _ in range(inner_kan_layers)
        ]

        self.dropout_rate = dropout_rate
        self.dropout_layer = tf.keras.layers.Dropout(
            self.dropout_rate) if self.dropout_rate > 0.0 else None
        self.fs = fs
        self.features_num = cnn_filters
        self.use_fast_model = use_fast_model
        self.dropout_position = 'input'
        self.save_each_epoch = save_each_epoch
        self.init_checkpoint(checkpoint_dir)
        self.build_model()

    def build_model(self):
        """
        构建并编译模型
        """
        input_layer = tf.keras.layers.Input(shape=(None, 1), name='input')
        if self.dropout_layer is not None and self.dropout_position == 'input':
            input_drop_out = self.dropout_layer(input_layer)
        else:
            input_drop_out = input_layer

        cnn_out = self.cnn(input_drop_out)
        fast_input = tf.keras.layers.Input(
            shape=(None, self.cnn_filters), name='fast_input')
        fast_cnn_out = self.fast_cnn(fast_input)

        if self.dropout_layer is not None and self.dropout_position == 'cnn':
            cnn_drop_out = self.dropout_layer(cnn_out)
            fast_cnn_drop_out = self.dropout_layer(fast_cnn_out)
        else:
            cnn_drop_out = cnn_out
            fast_cnn_drop_out = fast_cnn_out

        kan_inner_output = self.build_kan_inner_layers(cnn_drop_out)
        fast_kan_inner_output = self.build_kan_inner_layers(fast_cnn_drop_out)

        if self.dropout_layer is not None and self.dropout_position == 'output':
            kan_inner_output = self.dropout_layer(kan_inner_output)
            fast_kan_inner_output = self.dropout_layer(fast_kan_inner_output)

        output = self.kan(kan_inner_output)
        fast_output = self.kan(fast_kan_inner_output)

        self.model = tf.keras.Model(
            inputs=input_layer, outputs=output, name='CNNKAN')
        self.model.build(input_shape=(None, None, 1))
        
        if self.use_fast_model:
            self.fast_model = tf.keras.Model(
                inputs=fast_input, outputs=fast_output, name='fast_CNNKAN')
            self.fast_model.build(input_shape=(None, None, self.cnn_filters))

    def build_kan_inner_layers(self, cnn_out):
        """
        构建KAN内层

        Args:
            cnn_out: CNN输出

        Returns:
            处理后的张量
        """
        x = cnn_out
        for i, kan_inner in enumerate(self.kan_inner_layers):
            x = kan_inner(x)
            if i + 1 == len(self.kan_inner_layers) // 2:
                if self.dropout_layer is not None and self.dropout_position == 'inner':
                    x = self.dropout_layer(x)
        return x

    def evaluate(self, *args, **kwargs):
        """
        评估模型性能

        对于 CNNKAN，直接使用完整模型评估，
        因为 fast_model 期望的输入（CNN输出，8通道）与原始输入（1通道）不同
        """
        return self.model.evaluate(*args, **kwargs)

    def fit(self, *args, **kwargs):
        """
        训练模型

        对于 CNNKAN，直接使用完整模型训练，
        因为 fast_model 期望的输入（CNN输出，8通道）与原始输入（1通道）不同
        """
        return self.model.fit(*args, **kwargs)

    def save_weights(self, *args, **kwargs):
        """
        保存模型权重

        对于 CNNKAN，直接保存完整模型权重，
        因为 fast_model 的层结构与 model 不同，不能直接从 fast_model 复制权重
        """
        return self.model.save_weights(*args, **kwargs)

    def predict(self, x_input, batch_size=None, verbose=1, **kwargs):
        """
        预测

        对于 CNNKAN，直接使用完整模型预测，
        因为 fast_model 期望的输入（CNN输出，8通道）与原始输入（1通道）不同
        """
        kwargs.pop('use_scaler', None)
        return self.model.predict(x_input, batch_size=batch_size, verbose=verbose, **kwargs)

