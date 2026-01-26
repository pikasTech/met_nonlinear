import numpy as np
from typing import List
import json
import matplotlib.pyplot as plt


class KAN_LUT:
    def __init__(self,
                 grid_size=8,
                 spline_order=2,
                 grid_range=(0, 1),
                 spline_kernel=None,
                 lut_points=100,
                 lut_interp=True
                 ):
        self.grid_size = grid_size
        self.spline_order = spline_order
        self.grid_range = grid_range
        self.grid = self.generate_grid()
        self.spline_kernel = [
            1.0 / (self.grid_size + self.spline_order)] * (self.grid_size + self.spline_order)
        if spline_kernel is not None:
            self.set_spline_kernel(spline_kernel)
        self.lut_points = lut_points
        self.lut_log_scale = False
        self.lut_interp = lut_interp 
        self.min_x = 1e-2
        self.lut = None

    def set_spline_kernel(self, spline_kernel):
        """
        Set the spline kernel for the KAN LUT.

        Parameters
        ----------
        spline_kernel : list
            A list of spline kernel values.
        """
        if isinstance(spline_kernel, np.ndarray):
            spline_kernel = spline_kernel.reshape(-1).tolist()
        if len(spline_kernel) != self.grid_size + self.spline_order:
            raise ValueError(
                "The length of spline kernel should be equal to grid_size + spline_order.")
        self.spline_kernel = spline_kernel

    def generate_grid(self):
        """
        Generate the grid with evenly spaced points including extensions for spline order.

        Returns
        -------
        list
            A grid list with length (grid_size + 2 * spline_order + 1).
        """
        # Calculate the spacing (bound)
        bound = self.grid_range[1] - self.grid_range[0]

        # Generate the grid using linspace
        return np.linspace(
            self.grid_range[0] - self.spline_order * bound / self.grid_size,
            self.grid_range[1] + self.spline_order * bound / self.grid_size,
            self.grid_size + 2 * self.spline_order + 1
        ).tolist()

    def calc_spline_bases(self, x: float) -> list:
        """
        Calculate B-spline values for the input value.

        Parameters
        ----------
        x : float
            The input value.
        grid : list
            The grid list with length (grid_size + 2 * spline_order + 1).
        spline_order : int
            The spline order.

        Returns: list
            B-spline bases list of length (grid_size + spline_order).
        """
        # Initialize the order-0 B-spline bases
        bases = [1.0 if self.grid[i] <= x < self.grid[i + 1]
                 else 0.0 for i in range(len(self.grid) - 1)]

        # Iteratively calculate the B-spline values
        len_bases = len(bases)
        for k in range(1, self.spline_order + 1):
            len_bases -= 1
            for i in range(len_bases):
                left_term = 0.0
                right_term = 0.0

                # Calculate the left term
                if self.grid[i + k] - self.grid[i] != 0:
                    left_term = ((x - self.grid[i]) /
                                 (self.grid[i + k] - self.grid[i])) * bases[i]

                # Calculate the right term
                if self.grid[i + k + 1] - self.grid[i + 1] != 0:
                    right_term = (
                        (self.grid[i + k + 1] - x) / (self.grid[i + k + 1] - self.grid[i + 1])) * bases[i + 1]

                bases[i] = (left_term + right_term)

        return bases[:len_bases]

    def calc_spline_output(self, x: float, only_positive=True) -> float:
        """
        Calculate the output of the KAN LUT for the input value with optional positive constraint
        and symmetry restoration.

        Parameters
        ----------
        x : float
            The input value.
        only_positive : bool, optional
            Whether to constrain the output to be positive. Default is True.

        Returns
        -------
        float
            The output value.
        """
        # Calculate the B-spline bases
        # Step 1: Use the absolute value of the input
        bases = self.calc_spline_bases(abs(x))

        # Calculate the output value
        out = 0.0
        for i in range(len(bases)):
            out += bases[i] * self.spline_kernel[i]

        # Step 2: Apply positive constraint if required
        if only_positive:
            out = abs(out)  # Ensure the output is positive

        # Step 3: Restore the sign based on the input
        out = out * (1 if x >= 0 else -1)

        return out

    def build_lut(self):
        """
        Build the KAN LUT using the grid and spline kernel.

        Parameters
        ----------
        grid_range : tuple
            The range of the grid (min, max).
        grid : list
            The generated grid for the LUT.
        lut_points : int
            Number of points in the LUT.
        log_scale : bool, optional
            Whether to use a logarithmic scale for LUT construction. Default is False.

        Returns
        -------
        np.ndarray
            A lookup table array with precomputed output values.
        """
        lut_points_extern = int(
            self.lut_points / self.grid_range[1] * self.grid[-1])
        if self.lut_log_scale:
            lut_inputs = np.logspace(
                np.log10(self.grid_range[0] +
                         self.min_x), np.log10(self.grid[-1]), lut_points_extern)
        else:
            lut_inputs = np.linspace(
                self.grid_range[0], self.grid[-1], lut_points_extern)

        lut = [self.calc_spline_output(x) for x in lut_inputs]
        self.lut = lut

        return lut

    def calc_spline_output_lut(self, x: float, use_debug: bool = False) -> float:
        """
        Query the LUT for a specific input value by interpolating between the closest LUT points,
        or return the nearest left value if interpolation is disabled. Optionally, plot the LUT and result if `use_debug` is True.

        Parameters
        ----------
        x : float
            The input value.
        use_debug : bool, optional
            Whether to plot the LUT and output value. Default is False.

        Returns
        -------
        float
            The interpolated output value or the nearest left value.
        """

        if self.lut is None:
            self.build_lut()
        if isinstance(x, np.ndarray):
            x = float(x[0])
        x_abs = abs(x)
        # Normalize x_abs to find its relative position in the LUT grid
        normalized_x = (
            x_abs - self.grid_range[0]) / (self.grid_range[1] - self.grid_range[0])
        index = normalized_x * (self.lut_points - 1)

        # Get the indices of the closest points
        lower_index = min(int(index), len(self.lut) - 1)
        # Right point (cap to LUT length)
        upper_index = min(lower_index + 1, len(self.lut) - 1)

        # Get the LUT values at the closest points
        lower_value = self.lut[lower_index]
        upper_value = self.lut[upper_index]

        if self.lut_interp:
            # Perform linear interpolation
            weight = index - lower_index  # Fractional part determines interpolation weight
            interpolated_value = lower_value * \
                (1 - weight) + upper_value * weight
        else:
            # Use the left value directly
            interpolated_value = lower_value

        result_value = interpolated_value if x >= 0 else -interpolated_value

        # Debug plot: Plot LUT and the point corresponding to `x`
        if use_debug:
            plt.plot(range(len(self.lut)), self.lut, label='LUT',
                     marker='o', linestyle='-', color='b')
            plt.scatter([lower_index, upper_index], [
                        lower_value, upper_value], color='r', zorder=5)
            plt.scatter(index, interpolated_value, color='g',
                        label=f'Interpolated point ({x}, {interpolated_value:.2f})', zorder=5)
            plt.axvline(x=lower_index, linestyle='--', color='r',
                        label=f'Lower index ({lower_index})')
            plt.axvline(x=upper_index, linestyle='--', color='r',
                        label=f'Upper index ({upper_index})')
            plt.title(f"LUT Visualization and Interpolation: x = {x}")
            plt.xlabel('Index')
            plt.ylabel('LUT Value')
            plt.legend()

        return result_value

    def calc_spline_output_lut_logscale(self, x: float) -> float:
        """
        Query the LUT for a specific input value by interpolating between the closest LUT points.

        Parameters
        ----------
        x : float
            The input value.

        Returns
        -------
        float
            The interpolated output value.
        """
        if self.lut is None:
            self.build_lut()

        x_abs = abs(x)
        index = int((np.log10(x_abs) - np.log10(self.grid_range[0]+self.min_x)) / (np.log10(
            self.grid_range[1]) - np.log10(self.grid_range[0]+self.min_x)) * (self.lut_points))

        index = min(index, len(self.lut) - 1)
        return self.lut[index] if x >= 0 else -self.lut[index]

    def generate_c_struct(self, name):
        if self.lut is None:
            self.build_lut()
        grid_size = self.grid_size
        spline_order = self.spline_order
        grid = ", ".join([f"{x:.12f}f" for x in self.grid])
        spline_kernel = ", ".join([f"{x:.12f}f" for x in self.spline_kernel])
        lut = ", ".join([f"{x:.12f}f" for x in self.lut])

        # C代码模板（.c文件）
        c_code = f"""
// KAN_LUT arrays
const port_float KAN_LUT_{name}_grid[] = {{ {grid} }};
const port_float KAN_LUT_{name}_spline_kernel[] = {{ {spline_kernel} }};
const port_float KAN_LUT_{name}_lut[] = {{ {lut} }};

// KAN_LUT instance
const KAN_LUT KAN_LUT_{name} = {{
    .grid_size = {grid_size},
    .spline_order = {spline_order},
    .grid_range = {{ {self.grid_range[0]:.12f}f, {self.grid_range[1]:.12f}f }},
    .grid = KAN_LUT_{name}_grid,
    .spline_kernel = KAN_LUT_{name}_spline_kernel,
    .lut_points = {self.lut_points},
    .lut = KAN_LUT_{name}_lut
}};
    """

        # C头文件模板（.h文件）
        header_code = f"""
extern const KAN_LUT KAN_LUT_{name};
        """

        return c_code, header_code


class LayerKAN_LUT:
    def __init__(self,
                 in_size,
                 out_size,
                 grid_size=8,
                 spline_order=2,
                 grid_range=(0, 1),
                 lut_points=100,
                 weights=None,
                 lut_interp=True
                 ):
        """
        Initialize a LayerKAN_LUT instance.

        Parameters
        ----------
        in_size : int
            Number of inputs.
        out_size : int
            Number of outputs.
        grid_size : int, optional
            Grid size for each KAN_LUT instance.
        spline_order : int, optional
            Spline order for each KAN_LUT instance.
        grid_range : tuple, optional
            Range of the grid for each KAN_LUT instance.
        lut_points : int, optional
            Number of points in the LUT for each KAN_LUT instance.
        weights : np.ndarray, optional
            A numpy array of shape (in_size, spline_kernel_size, out_size) for weights.
        """
        self.in_size = in_size
        self.out_size = out_size
        spline_kernel_size = grid_size + spline_order
        self.spline_kernel_size = spline_kernel_size
        self.lut_interp = lut_interp
        self.kan_luts = [
            [KAN_LUT(grid_size, spline_order, grid_range, lut_points=lut_points,lut_interp=lut_interp)
             for _ in range(out_size)]
            for _ in range(in_size)
        ]

        if weights is not None:
            self.set_spline_kernels(weights)
        else:
            self.weights = np.random.uniform(-1, 1,
                                             (in_size, spline_kernel_size, out_size))
            self.set_spline_kernels(self.weights)

    def set_spline_kernels(self, weights):
        """
        weights.shape = (in_size, spline_kernel_size, out_size)
        """
        if weights.shape != (self.in_size, self.spline_kernel_size, self.out_size):
            raise ValueError(
                f"The shape of weights should be ({self.in_size}, {self.spline_kernel_size}, {self.out_size}), but got {weights.shape}.")
        for i in range(self.in_size):
            for o in range(self.out_size):
                self.kan_luts[i][o].set_spline_kernel(weights[i, :, o])
        self.weights = weights

    def forward_once(self, inputs, use_lut=False):
        """
        Perform a forward pass through the LayerKAN_LUT.

        Parameters
        ----------
        inputs : list or np.ndarray
            A list or numpy array of inputs of length `in_size`.

        Returns
        -------
        list
            A list of outputs of length `out_size`.
        """
        if len(inputs) != self.in_size:
            raise ValueError(f"Input size must be {self.in_size}.")

        outputs = [0.0] * self.out_size

        for o in range(self.out_size):
            for i in range(self.in_size):
                output = self.kan_luts[i][o].calc_spline_output_lut(
                    inputs[i]) if use_lut else self.kan_luts[i][o].calc_spline_output(inputs[i])
                outputs[o] += output

        return outputs

    def forward(self, inputs_list, use_lut=False):
        """
        Perform a forward pass through the LayerKAN_LUT.

        Parameters
        ----------
        inputs_list : list or np.ndarray
            A list or numpy array of inputs of shape (batch_size, in_size).

        Returns
        -------
        list
            A list of outputs of shape (batch_size, out_size).
        """
        if len(inputs_list[0]) != self.in_size:
            raise ValueError(f"Input size must be {self.in_size}.")

        outputs = [self.forward_once(inputs, use_lut)
                   for inputs in inputs_list]

        return outputs

    def build_lut(self):
        for i in range(self.in_size):
            for o in range(self.out_size):
                self.kan_luts[i][o].build_lut()

    def generate_c_struct(self, name):
        """
        Generate C struct code for this LayerKAN_LUT instance.

        Parameters
        ----------
        name : str
            The name of the layer, e.g., "layer0".

        Returns
        -------
        (str, str)
            c_code, header_code
        - c_code: C code containing the definitions of all KAN_LUT instances and the LayerKAN_LUT structure.
        - header_code: Corresponding extern declarations for the created variables.
        """

        # 为每个KAN_LUT实例生成C结构并累积代码
        c_code_list = []
        header_code_list = []

        # 保存KAN_LUT实例名的列表，用于之后初始化指针数组
        kan_lut_names = []

        for i in range(self.in_size):
            for o in range(self.out_size):
                lut_name = f"{name}_in{i}_out{o}"
                c_code_lut, header_code_lut = self.kan_luts[i][o].generate_c_struct(
                    lut_name)
                c_code_list.append(c_code_lut)
                header_code_list.append(header_code_lut)
                kan_lut_names.append(f"&KAN_LUT_{lut_name}")

        # 生成KAN_LUT指针数组
        # 数量为 in_size * out_size
        kan_lut_array_name = f"KAN_LUTs_{name}"
        kan_lut_array_code = f"const KAN_LUT *{kan_lut_array_name}[] = {{\n"
        for i in range(self.in_size):
            row_str = "    " + \
                ", ".join(kan_lut_names[i*self.out_size:(i+1)*self.out_size])
            kan_lut_array_code += row_str + ",\n"
        kan_lut_array_code += "};\n\n"

        # 生成LayerKAN_LUT结构体实例
        layer_struct_name = f"LayerKAN_LUT_{name}"
        layer_c_code = f"""
const LayerKAN_LUT {layer_struct_name} = {{
    .in_size = {self.in_size},
    .out_size = {self.out_size},
    .spline_kernel_size = {self.spline_kernel_size},
    .kan_luts = {kan_lut_array_name}
}};
"""

        # header extern
        header_code_layer = f"extern LayerKAN_LUT {layer_struct_name};\n"

        # 合并C代码和头文件代码
        c_code_final = "\n".join(c_code_list) + "\n" + \
            kan_lut_array_code + layer_c_code
        header_code_final = "\n".join(
            header_code_list) + "\n" + header_code_layer

        return c_code_final, header_code_final


class IIR:
    def __init__(self, order=2, a=None, b=None):
        """
        初始化一个IIR滤波器实例。

        参数
        ----------
        order : int, 可选
            滤波器的阶数。默认值为2。
        a : list或np.ndarray, 可选
            分母系数 (a 系列)，长度应为 order + 1。默认值为 None。
        b : list或np.ndarray, 可选
            分子系数 (b 系列)，长度应为 order + 1。默认值为 None。
        """
        self.order = order
        if a is not None:
            self.set_a(a)
        else:
            self.a = np.ones(order + 1)
        if b is not None:
            self.set_b(b)
        else:
            self.b = np.zeros(order + 1)
            self.b[0] = 1.0  # 默认b0为1
        # 初始化延迟线
        self.x_history = np.zeros(self.order)
        self.y_history = np.zeros(self.order)

    def set_a(self, a):
        """
        设置分母系数。

        参数
        ----------
        a : list或np.ndarray
            分母系数，长度应为 order + 1。
        """
        a = np.array(a, dtype=np.float32).flatten()
        if len(a) != self.order + 1:
            raise ValueError(f"分母系数a的长度应为 {self.order + 1}，但得到 {len(a)}。")
        self.a = a

    def set_b(self, b):
        """
        设置分子系数。

        参数
        ----------
        b : list或np.ndarray
            分子系数，长度应为 order + 1。
        """
        b = np.array(b, dtype=np.float32).flatten()
        if len(b) != self.order + 1:
            raise ValueError(f"分子系数b的长度应为 {self.order + 1}，但得到 {len(b)}。")
        self.b = b

    def filter(self, input_signal):
        """
        对输入信号应用IIR滤波器。

        参数
        ----------
        input_signal : list或np.ndarray
            输入信号序列。

        返回
        -------
        np.ndarray
            滤波后的输出信号。
        """
        input_signal = np.array(input_signal, dtype=np.float32)
        output = np.zeros_like(input_signal)

        for n, x in enumerate(input_signal):
            # 计算当前输出
            y = self.b[0] * x
            for i in range(1, self.order + 1):
                if i < len(self.b):
                    y += self.b[i] * self.x_history[i-1]
                if i < len(self.a):
                    y -= self.a[i] * self.y_history[i-1]
            # 存储输出
            output[n] = y
            # 更新延迟线
            self.x_history = np.roll(self.x_history, 1)
            self.x_history[0] = x
            self.y_history = np.roll(self.y_history, 1)
            self.y_history[0] = y

        return output

    def generate_c_struct(self, name):
        """
        生成用于C语言实现的结构体代码。

        参数
        ----------
        name : str
            结构体的名称前缀，例如 "filter0"。

        返回
        -------
        (str, str)
            c_code: 包含滤波器系数和结构体定义的C代码字符串。
            header_code: 对应的头文件声明代码字符串。
        """
        # 生成a和b系数的C数组
        a_coeffs = ", ".join([f"{coeff:.12f}f" for coeff in self.a])
        b_coeffs = ", ".join([f"{coeff:.12f}f" for coeff in self.b])

        # C代码模板（.c文件）
        c_code = f"""
// IIR Filter: {name}
const port_float IIR_{name}_a[] = {{ {a_coeffs} }};
const port_float IIR_{name}_b[] = {{ {b_coeffs} }};

IIR IIR_{name} = {{
    .order = {self.order},
    .a = IIR_{name}_a,
    .b = IIR_{name}_b
}};
        """

        # C头文件模板（.h文件）
        header_code = f"""
extern IIR IIR_{name};
        """

        return c_code, header_code


class LayerIIR:
    def __init__(self, in_size, out_size, order=2, weights_a=None, weights_b=None):
        """
        初始化一个LayerIIR实例，用于多输入多输出的IIR滤波器层。

        参数
        ----------
        in_size : int
            输入通道数。
        out_size : int
            输出通道数。
        order : int, 可选
            每个IIR滤波器的阶数。默认值为2。
        weights_a : np.ndarray, 可选
            分母系数的权重，形状应为 (in_size, out_size, order + 1)。默认值为 None。
        weights_b : np.ndarray, 可选
            分子系数的权重，形状应为 (in_size, out_size, order + 1)。默认值为 None。
        """
        self.in_size = in_size
        self.out_size = out_size
        self.order = order
        self.iirs = [
            [IIR(order=order) for _ in range(out_size)]
            for _ in range(in_size)
        ]

        if weights_a is not None and weights_b is not None:
            self.set_weights(weights_a, weights_b)
        else:
            # 随机初始化系数
            weights_a = np.random.uniform(-1, 1, (in_size,
                                          out_size, order + 1)).astype(np.float32)
            weights_b = np.random.uniform(-1, 1, (in_size,
                                          out_size, order + 1)).astype(np.float32)
            self.set_weights(weights_a, weights_b)

    def set_weights(self, weights_a, weights_b):
        """
        设置所有IIR滤波器的系数。

        参数
        ----------
        weights_a : np.ndarray
            分母系数，形状应为 (in_size, out_size, order + 1)。
        weights_b : np.ndarray
            分子系数，形状应为 (in_size, out_size, order + 1)。
        """
        if weights_a.shape != (self.in_size, self.out_size, self.order + 1):
            raise ValueError(
                f"weights_a的形状应为 ({self.in_size}, {self.out_size}, {self.order + 1})，但得到 {weights_a.shape}。")
        if weights_b.shape != (self.in_size, self.out_size, self.order + 1):
            raise ValueError(
                f"weights_b的形状应为 ({self.in_size}, {self.out_size}, {self.order + 1})，但得到 {weights_b.shape}。")

        for i in range(self.in_size):
            for o in range(self.out_size):
                self.iirs[i][o].set_a(weights_a[i, o])
                self.iirs[i][o].set_b(weights_b[i, o])

        self.weights_a = weights_a
        self.weights_b = weights_b

    def forward_once(self, inputs):
        """
        对单个输入样本执行前向传播。

        参数
        ----------
        inputs : list或np.ndarray
            输入信号列表，长度为 in_size。

        返回
        -------
        list
            输出信号列表，长度为 out_size。
        """
        len_inputs = 1 if isinstance(inputs, (int, float)) else len(inputs)
        if len_inputs != self.in_size:
            raise ValueError(f"输入长度必须为 {self.in_size}，但得到 {len(inputs)}。")

        outputs = [0.0 for _ in range(self.out_size)]
        for o in range(self.out_size):
            for i in range(self.in_size):
                input = inputs if isinstance(
                    inputs, (int, float)) else inputs[i]
                y = self.iirs[i][o].filter([input])[-1]  # 只取最新输出
                outputs[o] += y
        return outputs

    def forward(self, inputs_list):
        """
        对批量输入执行前向传播。

        参数
        ----------
        inputs_list : list或np.ndarray
            输入信号列表，形状为 (batch_size, in_size)。

        返回
        -------
        list
            输出信号列表，形状为 (batch_size, out_size)。
        """
        return [self.forward_once(inputs) for inputs in inputs_list]

    def generate_c_struct(self, name):
        """
        生成用于C语言实现的结构体代码。

        参数
        ----------
        name : str
            层的名称前缀，例如 "layer0"。

        返回
        -------
        (str, str)
            c_code: 包含所有IIR滤波器系数和LayerIIR结构体定义的C代码字符串。
            header_code: 对应的头文件声明代码字符串。
        """
        c_code_list = []
        header_code_list = []
        iir_names = []

        for i in range(self.in_size):
            for o in range(self.out_size):
                iir_name = f"{name}_in{i}_out{o}"
                c_code_iir, header_code_iir = self.iirs[i][o].generate_c_struct(
                    iir_name)
                c_code_list.append(c_code_iir)
                header_code_list.append(header_code_iir)
                iir_names.append(f"&IIR_{iir_name}")

        # 生成IIR指针数组
        iir_array_name = f"IIRs_{name}"
        iir_array_code = f"const IIR *{iir_array_name}[] = {{\n"
        for i in range(self.in_size):
            row = ", ".join(iir_names[i*self.out_size:(i+1)*self.out_size])
            iir_array_code += f"    {row},\n"
        iir_array_code += "};\n\n"

        # 生成LayerIIR结构体实例
        layer_struct_name = f"LayerIIR_{name}"
        layer_c_code = f"""
const LayerIIR {layer_struct_name} = {{
    .in_size = {self.in_size},
    .out_size = {self.out_size},
    .order = {self.order},
    .iirs = {iir_array_name}
}};
        """

        # 生成头文件声明
        header_code_layer = f"extern const LayerIIR {layer_struct_name};\n"

        # 合并所有C代码和头文件代码
        c_code_final = "\n".join(c_code_list) + "\n" + \
            iir_array_code + layer_c_code
        header_code_final = "\n".join(
            header_code_list) + "\n" + header_code_layer

        return c_code_final, header_code_final


class ModelKAN_LUT:
    def __init__(self, lut_points=100,lut_interp=True):
        self.layers: List[LayerKAN_LUT] = []
        self.layers_rnn: List[LayerIIR] = []
        self.lut_points = lut_points
        self.lut_interp = lut_interp

    def add_kanlayer(self, in_size, out_size, grid_size=8, spline_order=2, grid_range=(0, 1)):
        layer = LayerKAN_LUT(in_size, out_size, grid_size=grid_size,
                             spline_order=spline_order, grid_range=grid_range, lut_points=self.lut_points, lut_interp=self.lut_interp)
        self.layers.append(layer)

    def add_iirlayer(self, in_size, out_size, order=2):
        layer = LayerIIR(in_size, out_size, order=order)
        self.layers_rnn.append(layer)

    def set_weights(self, weights):
        for i, layer in enumerate(self.layers):
            layer.set_spline_kernels(weights[i])

    def load_weights_json(self, json_path):
        with open(json_path, 'r') as f:
            layers = json.load(f)
        layers_kan = [layer for layer in layers if 'kan' in layer['name']
                      and 'kernel' in layer['name']]
        self.layers = []
        for i, layer in enumerate(layers_kan):
            in_size = layer['shape'][0]
            out_size = layer['shape'][2]
            grid_size = layer['config']['grid_size']
            spline_order = layer['config']['spline_order']
            grid_range = layer['config']['grid_range']
            self.add_kanlayer(in_size, out_size, grid_size,
                              spline_order, grid_range)
        kan_weights = [np.array(layer['value']) for layer in layers_kan]
        self.set_weights(kan_weights)

        layers_rnn = [layer for layer in layers if 'rnn' in layer['name']]
        self.layers_rnn = []
        kernels_rnn = [
            layer for layer in layers_rnn if '/kernel' in layer['name']]
        recurrent_kernels_rnn = [
            layer for layer in layers_rnn if '/recurrent_kernel' in layer['name']]
        if len(kernels_rnn) != len(recurrent_kernels_rnn):
            raise ValueError(
                'The number of kernel and recurrent kernel should be equal.')
        in_size = 1
        out_size = len(kernels_rnn)
        order = 2
        a = []
        b = []
        for i in range(out_size):
            b0 = kernels_rnn[i]['value'][0][0]
            r_val = recurrent_kernels_rnn[i]['value']
            a1, a2, b1, b2 = [-r_val[0][0], -r_val[1]
                              [0], r_val[2][0], r_val[3][0]]
            a.append([1, a1, a2])
            b.append([b0, b1, b2])
        self.add_iirlayer(in_size, out_size, order)
        # shape (out_size, order + 1) -> (in_size, out_size, order + 1)
        a = np.array(a).reshape(1, out_size, order + 1)
        b = np.array(b).reshape(1, out_size, order + 1)
        self.layers_rnn[0].set_weights(np.array(a), np.array(b))

    def forward(self, inputs_list, use_lut=False, verbose=True):
        """
        input_list.shape = (batch_size, in_size)
        """
        for i, rnn in enumerate(self.layers_rnn):
            if verbose:
                print(f'LayerIIR forwarding ({i+1}/{len(self.layers_rnn)})...')
            inputs_list = rnn.forward(inputs_list)
        if use_lut:
            for i, layer in enumerate(self.layers):
                if verbose:
                    print(
                        f'KAN_LUT building lut[{self.lut_points}]({i+1}/{len(self.layers)})...')
                layer.build_lut()
        else:
            print('KAN_LUT without LUT')
        for i, layer in enumerate(self.layers):
            if verbose:
                print(f'KAN_LUT forwarding ({i+1}/{len(self.layers)})...')
            inputs_list = layer.forward(inputs_list, use_lut)
        return inputs_list

    def generate_c_struct(self, model_name):
        """
        生成整个模型的C结构体代码。

        Parameters
        ----------
        model_name : str
            模型的名称，用于生成C代码中的变量名。

        Returns
        -------
        (str, str)
            c_code, header_code
        - c_code: C代码文件内容，包括所有层和KAN_LUT实例的定义。
        - header_code: C头文件内容，包括所有层和KAN_LUT实例的extern声明。
        """

        c_code_list = []
        header_code_list = []

        # 保存所有层的名称，用于模型结构体
        layer_struct_names = []
        layer_struct_names_rnn = []
        for layer_idx, layer in enumerate(self.layers_rnn):
            layer_name = f"{model_name}_layer{layer_idx}"
            c_code_layer, header_code_layer = layer.generate_c_struct(
                layer_name)
            c_code_list.append(c_code_layer)
            header_code_list.append(header_code_layer)
            layer_struct_names_rnn.append(f"&LayerIIR_{layer_name}")

        for layer_idx, layer in enumerate(self.layers):
            layer_name = f"{model_name}_layer{layer_idx}"
            c_code_layer, header_code_layer = layer.generate_c_struct(
                layer_name)
            c_code_list.append(c_code_layer)
            header_code_list.append(header_code_layer)
            layer_struct_names.append(f"&LayerKAN_LUT_{layer_name}")

        # 生成模型的指针数组
        model_layers_array_name = f"LayerKAN_LUTs_{model_name}"
        model_layers_array_code = f"const LayerKAN_LUT *{model_layers_array_name}[] = {{\n"
        for layer_struct in layer_struct_names:
            model_layers_array_code += f"    {layer_struct},\n"
        model_layers_array_code += "};\n\n"

        model_rnn_layers_array_name = f"LayerIIRs_{model_name}"
        model_rnn_layers_array_code = f"const LayerIIR *{model_rnn_layers_array_name}[] = {{\n"
        for layer_struct in layer_struct_names_rnn:
            model_rnn_layers_array_code += f"    {layer_struct},\n"
        model_rnn_layers_array_code += "};\n\n"

        # 生成模型的结构体定义
        model_struct_name = f"ModelKAN_LUT_{model_name}"
        model_c_code = f"""
const ModelKAN_LUT {model_struct_name} = {{
    .num_layers = {len(self.layers)},
    .layers = {model_layers_array_name},
    .num_rnn_layers = {len(self.layers_rnn)},
    .rnn_layers = {model_rnn_layers_array_name}
}};
        """

        # 生成模型结构体的头文件声明
        header_code_model = f"extern ModelKAN_LUT {model_struct_name};\n"

        # 合并所有C代码和头文件代码
        c_code_final = "\n".join(c_code_list) + "\n" + \
            model_layers_array_code + model_rnn_layers_array_code + model_c_code
        header_code_final = "\n".join(
            header_code_list) + "\n" + header_code_model

        # add include "frikan.h" for h
        c_code_final = '#include "frikan.h"\n' + c_code_final
        header_code_final = '#include "frikan.h"\n' + header_code_final

        # add ifndef for h
        header_code_final = f"""#ifndef __{model_struct_name.upper()}_H__

#define __{model_struct_name.upper()}_H__

{header_code_final}

#endif
        """

        return c_code_final, header_code_final


def dense_kan_siso(x, weight):
    import tensorflow as tf
    from tfkan.layers import DenseKAN
    # tf random seed
    tf.random.set_seed(42)
    # random input data
    model = tf.keras.Sequential()
    kan = DenseKAN(
        units=1,
        grid_size=3,
        spline_order=2,
        fix_scale_factor=True,
        use_bias=False,
        grid_range=(0, 1),
        disable_basis_activation=True
    )
    model.add(kan)
    model.build(input_shape=(None, 1))
    model.summary()
    # wight from (5, 1) to (1, 5, 1)
    weight = weight.reshape(1, 5, 1)
    model.weights[0].assign(weight)
    print(model.weights)
    # print(kan.grid.numpy())
    y = model(x)
    print(y)
    return y


def kan_lut_siso(x, weight):
    # create the KAN LUT
    kan = KAN_LUT(grid_size=3, spline_order=2, spline_kernel=weight)
    print(kan.grid)
    print(kan.calc_spline_bases(0.5))
    output = [kan.calc_spline_output(xi) for xi in x]
    output_lut = [kan.calc_spline_output_lut(xi) for xi in x]
    # plt.plot(output, label='KAN')
    # plt.plot(output_lut, label='KAN LUT', linestyle='', marker='o')
    c_struct, h_struct = kan.generate_c_struct('test')
    # print(f'c_struct:\n{c_struct}')
    # print(f'h_struct:\n{h_struct}')
    return output_lut


def test_siso():
    np.random.seed(42)
    weight = np.random.uniform(-1, 1, (5, 1))
    # random input data
    x = np.random.uniform(-1, 1, (10, 1))
    y = dense_kan_siso(x, weight)
    y_lut = kan_lut_siso(x, weight)
    print(f'KAN output: {y.numpy().reshape(-1).tolist()}')
    print(f'KAN_LUT output: {y_lut}')
    plt.plot(y, label='KAN_dense')
    plt.plot(y_lut, label='KAN_LUT', linestyle='', marker='o')
    plt.legend()
    plt.show()


def mimo_kan(x, weight, in_size, out_size):
    import tensorflow as tf
    from tfkan.layers import DenseKAN
    # tf random seed
    tf.random.set_seed(42)
    model = tf.keras.Sequential()
    kan = DenseKAN(
        units=out_size,
        grid_size=3,
        spline_order=2,
        fix_scale_factor=True,
        use_bias=False,
        grid_range=(0, 1),
        disable_basis_activation=True
    )
    model.add(kan)
    model.build(input_shape=(None, in_size))
    model.summary()
    model.weights[0].assign(weight)
    print(model.weights)
    y = model(x)
    print(y)
    return y


def mimo_kan_lut(x, weight, in_size, out_size):
    layer = LayerKAN_LUT(
        in_size=in_size,
        out_size=out_size,
        grid_size=3,
        spline_order=2,
        grid_range=(0, 1),
    )
    layer.set_spline_kernels(weight)
    y = layer.forward(x, use_lut=True)
    print(f'KAN_LUT output: {y}')
    c, h = layer.generate_c_struct('test')
    # print(f'c_struct:\n{c}')
    # print(f'h_struct:\n{h}')
    return y


def test_mimo():
    in_size = 6
    out_size = 6
    layers = 8
    np.random.seed(42)
    x_origin = np.random.uniform(-1, 1, (10, in_size))
    weight = np.random.uniform(-1, 1, (in_size, 5, out_size))

    x = x_origin.copy()
    x_lut = x_origin.copy()
    for i in range(layers):
        x = mimo_kan_lut(x, weight, in_size=in_size, out_size=out_size)
        x_lut = mimo_kan(x_lut, weight, in_size=in_size, out_size=out_size)
    subplots = out_size
    if subplots == 1:
        fig = plt.figure(figsize=(12, 6))
        yi = [yj[0] for yj in x]
        y_luti = [yj[0] for yj in x_lut]
        plt.plot(y_luti, label='KAN')
        plt.plot(yi, label='KAN LUT', linestyle='', marker='o')
        plt.legend()
    else:
        fig, axs = plt.subplots(subplots, 1, figsize=(12, 6))
        for i in range(subplots):
            yi = [yj[i] for yj in x]
            y_luti = [yj[i] for yj in x_lut]
            axs[i].plot(y_luti, label='KAN')
            axs[i].plot(yi, label='KAN LUT', linestyle='', marker='o')
            axs[i].legend()
    plt.show()


def test_model_kan():
    model_kan_lut = ModelKAN_LUT(lut_points=800)
    model_kan_lut.load_weights_json(
        'projects/FRIKANh8u6l6/data/best_val.weights.json')
    np.random.seed(42)
    # x = np.random.uniform(-1, 1, (10))
    x = [-0.0085857,
         -0.01197907,
         -0.01121598,
         -0.00747459,
         -0.00176137,
         0.00513324,
         0.01086711,
         0.01185316,
         0.00659737,
         -0.00217565]
    print(f'x: {x}')
    y = model_kan_lut.forward(x, use_lut=1)
    print(f'y: {y}')
    c, h = model_kan_lut.generate_c_struct('test')
    # 保存到 cimpl/models 文件夹
    with open('cimpl/frikan_test.c', 'w') as f:
        f.write(c)
    with open('cimpl/frikan_test.h', 'w') as f:
        f.write(h)
    plt.plot(y)


def test_lut_points_accuracy(lut_points_list,
                             grid_range=(0, 1),
                             test_size=5000,
                             seed=42,
                             lut_interp=True
                             ):
    """
    测试在不同的lut_points配置下，插值结果与真实结果之间的MAE，并画图。

    Parameters
    ----------
    lut_points_list : list
        待测试的 lut_points 列表，例如 [10, 50, 100, 200, 500].
    grid_size : int
        KAN_LUT 的 grid_size.
    spline_order : int
        KAN_LUT 的 spline_order.
    grid_range : tuple
        KAN_LUT 的 grid_range, 如 (0, 1).
    test_size : int
        用于计算MAE的测试样本数.
    seed : int
        随机种子.

    Returns
    -------
    (list, list)
        以 (lut_points_list, mae_list) 返回：每个 lut_points 对应的 MAE.
    """

    # 设置随机种子，保证结果可复现
    np.random.seed(seed)

    # 引入 KAN_LUT 类（假设与提问中的类在同一脚本或者已正确import）
    # from your_module import KAN_LUT  # 如果单独使用，需要这样导入

    # 生成一些测试输入数据：例如在 grid_range 范围内随机分布 test_size 个点
    x_test = np.random.uniform(grid_range[0], grid_range[1], test_size)

    # 准备列表存放结果
    mae_list = []

    # 在每个 lut_points 设置下做测试
    for lut_points in lut_points_list:
        # 初始化一个 KAN_LUT 实例
        lut_instance = ModelKAN_LUT(lut_points=lut_points, lut_interp=lut_interp)
        lut_instance.load_weights_json(
            'projects/FRIKANh8u6l6/data/best_val.weights.json')

        # 这里可以根据需要给 spline_kernel 赋值，或者使用默认值
        # 例如随机初始化 spline_kernel，或使用某个固定的分布
        # 为简单起见，这里先保留默认值，也可自行替换
        # kernel = np.random.uniform(-1, 1, grid_size + spline_order)
        # lut_instance.set_spline_kernel(kernel)

        # 分别计算真实输出(不使用 LUT) 与 插值输出(使用 LUT)
        # 注意 calc_spline_output, calc_spline_output_lut 都是对单个x计算，所以需要遍历

        real_output = np.array(lut_instance.forward(x_test, use_lut=0))
        lut_output = np.array(lut_instance.forward(x_test, use_lut=1))

        # 计算 MAE
        mae = np.mean(np.abs(real_output - lut_output))
        mae_list.append(mae)

        print(f"lut_points={lut_points}, MAE={mae:.6f}")

    return lut_points_list, mae_list


if __name__ == '__main__':
    # test_siso()
    # test_mimo()
    # test_model_kan()
    # 示例：取若干常见插值点数配置
    lut_points_candidates = [10, 50, 100, 200,
                             300, 400, 500, 600, 700, 800, 900, 1000]
    # # 运行测试并画图
    _, mae_list_interp = test_lut_points_accuracy(lut_points_candidates, lut_interp=True)
    _, mae_list_nointerrp = test_lut_points_accuracy(lut_points_candidates, lut_interp=False)
    # 保存到json
    with open('lut_points_mae.json', 'w') as f:
        json.dump({
            'lut_points': lut_points_candidates,
            'mae_interp': mae_list_interp,
            'mae_nointerp': mae_list_nointerrp
        }, f)
    # 画图：lut_points vs MAE

    plt.figure(figsize=(8, 5))
    plt.plot(lut_points_candidates, mae_list_interp, label='LUT Interp')
    plt.plot(lut_points_candidates, mae_list_nointerrp, label='LUT No Interp')
    plt.xlabel("Number of LUT Points")
    plt.ylabel("MAE")
    plt.legend()
    plt.title("MAE vs LUT Points")
    plt.grid(True)
    plt.show()

