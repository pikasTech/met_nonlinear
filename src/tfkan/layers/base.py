import tensorflow as tf
from keras.layers import Layer
from ..ops.spline import calc_spline_values, fit_spline_coef
from ..ops.grid import build_adaptive_grid

from typing import Tuple, List, Any, Union, Callable
from abc import ABC, abstractmethod

class PiecewiseActivationLayer(tf.keras.layers.Layer):
    """
    Custom Keras Layer for piecewise activation based on xn and yn.
    Args:
        xn (list of float): List of x-coordinates for breakpoints.
        yn (list of float): List of y-coordinates corresponding to xn.
    """

    def __init__(self, xn, yn, **kwargs):
        super(PiecewiseActivationLayer, self).__init__(**kwargs)
        # Ensure xn and yn have the same length
        assert len(xn) == len(yn), "xn and yn must have the same length."

        # Include (0, 0) if not already present
        if 0.0 not in xn:
            self.xn = [0.0] + xn
            self.yn = [0.0] + yn
        else:
            self.xn = xn
            self.yn = yn

        # Compute slopes (k) and intercepts (b) for each segment
        self.k = [(self.yn[i+1] - self.yn[i]) / (self.xn[i+1] - self.xn[i])
                  for i in range(len(self.xn) - 1)]
        self.b = [self.yn[i] - self.k[i] * self.xn[i]
                  for i in range(len(self.k))]

    def call(self, inputs):
        return self.piecewise_activation(inputs)

    def piecewise_activation(self, x):
        """
        Apply the piecewise linear activation function.
        Args:
            x (tf.Tensor): Input tensor.
        Returns:
            tf.Tensor: Output tensor with piecewise linear activation applied.
        """
        x_abs = tf.abs(x)  # Handle symmetry by using absolute value
        y = tf.zeros_like(x_abs, dtype=tf.float32)

        # Compute y for each segment
        for i in range(len(self.k)):
            left = self.xn[i]
            right = self.xn[i + 1]
            ki = self.k[i]
            bi = self.b[i]
            y += tf.where((x_abs >= left) & (x_abs < right),
                          ki * x_abs + bi, 0.0)

        # Handle x_abs >= xn[-1], extrapolate using the last segment
        ki = self.k[-1]
        bi = self.b[-1]
        y += tf.where(x_abs >= self.xn[-1], ki * x_abs + bi, 0.0)

        # Apply symmetry y(-x) = -y(x)
        y = tf.where(x >= 0, y, -y)

        return y

    def print_equations(self):
        """
        Print all line equations in the form y = kx + b and the corresponding x ranges.
        """
        for i in range(len(self.k)):
            left = self.xn[i]
            right = self.xn[i + 1]
            print(
                f"Segment {i + 1}: y = {self.k[i]:.2f}x + {self.b[i]:.2f}, for x in [{left}, {right}]")

    @classmethod
    def from_xk(cls, x: list, k: list, k_with_zero=True):
        """
        Create a PiecewiseActivationLayer from a list of x-values and slopes.
        Args:
            x (list of float): List of x-coordinates for breakpoints.
            k (list of float): List of slopes corresponding to x.
        Returns:
            PiecewiseActivationLayer: Instance of PiecewiseActivationLayer.
        """
        # Ensure the lengths of x and k match
        assert len(x) == len(k), "Length of x and k must be the same."

        # Initialize y-values, starting from 0
        if k_with_zero:
            y = [x[i] * k[i] for i in range(len(x))]
        else:
            y = [0.0]
            if 0.0 not in x:
                x = [0.0] + x
            for i in range(1, len(x)):
                # Compute y-value based on previous y, slope k[i-1], and delta x
                y_this = y[i-1] + k[i-1] * (x[i] - x[i-1])
                y.append(y_this)

        print(f"Creating PiecewiseActivationLayer with x = {x} and y = {y}")
        # Create the PiecewiseActivationLayer instance
        return cls(x, y)

    def reverse(self):
        """
        Generate the inverse function of this piecewise linear function.
        Returns:
            PiecewiseActivationLayer: An instance representing the inverse function.
        """
        # Since the function is symmetric about the origin and uses absolute value,
        # we can consider only the positive side (x >= 0) for inversion.

        # Extract positive side xn and yn (x >= 0)
        xn = self.xn
        yn = self.yn

        # Check for monotonicity on the positive side
        if not all(y2 > y1 for y1, y2 in zip(yn[:-1], yn[1:])):
            raise ValueError(
                "The function is not strictly increasing; inverse cannot be uniquely determined.")

        # Swap xn and yn to get the inverse function breakpoints
        xn_inv = yn
        yn_inv = xn

        # Create the inverse PiecewiseActivationLayer
        inverse_layer = PiecewiseActivationLayer(xn_inv, yn_inv)
        return inverse_layer

    def to_xnyn(self):
        return self.xn, self.yn

class LayerKAN:
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    def calc_spline_output_origin(self, inputs):
        """
        calculate the spline output, each feature of each sample is mapped to `out_size` features, \
        using `out_size` different B-spline basis functions, so the output shape is `(batch_size, in_size, out_size)`

        Parameters
        ----------
        inputs : tf.Tensor
            the input tensor with shape `(batch_size, in_size)`

        Returns
        -------
        spline_out : tf.Tensor
            the output tensor with shape `(batch_size, in_size, out_size)`
        """
        # calculate the B-spline output
        # (B, in_size, grid_basis_size)
        spline_in = calc_spline_values(inputs, self.grid, self.spline_order)
        # matrix multiply: (batch, in_size, grid_basis_size) @ (in_size, grid_basis_size, out_size) -> (batch, in_size, out_size)
        spline_out = tf.einsum("bik,iko->bio", spline_in, self.spline_kernel)

        return spline_out

    def calc_spline_output_symmetry(
            self,
            inputs,
            only_positive=True,
            use_even=False,  # 偶对称
            use_zero_point=False,  # 过零点
            use_debug=False
    ):
        """
        计算关于零点中心对称的样条输出。

        Parameters
        ----------
        inputs : tf.Tensor
            输入张量，形状为 `(batch_size, in_size)`

        Returns
        -------
        spline_out : tf.Tensor
            输出张量，形状为 `(batch_size, in_size, out_size)`
        """
        # 1. 对输入取绝对值
        abs_inputs = tf.abs(inputs)
        if use_debug:
            print(f'max(abs_inputs): {tf.reduce_max(abs_inputs)}')
            print(f'min(abs_inputs): {tf.reduce_min(abs_inputs)}')

        # 2. 计算样条值
        spline_in = calc_spline_values(
            abs_inputs, self.grid, self.spline_order)

        if only_positive:
            # 转换负值
            # spline_out = spline_out - 2
            # spline_out = tf.nn.softplus(spline_out)

            # 对 spline_kernel 取绝对值
            self.spline_kernel.assign(tf.abs(self.spline_kernel))
            # spline_out = tf.nn.relu(spline_out)
            # x**2
            # spline_out = tf.square(spline_out)
            if use_debug:
                print(f'positive max(spline_out): {tf.reduce_max(spline_out)}')
                print(f'positive min(spline_out): {tf.reduce_min(spline_out)}')

        # 3. 计算样条输出
        spline_out = tf.einsum("bik,iko->bio", spline_in, self.spline_kernel)

        if use_debug:
            print(f'max(spline_out): {tf.reduce_max(spline_out)}')
            print(f'min(spline_out): {tf.reduce_min(spline_out)}')

        if use_zero_point:
            # 乘上一个过零点的包络，使得输出在零点对称
            # zero_curve = tf.abs(inputs)
            # tanh
            # zero_curve = tf.tanh(inputs)
            # 分段，0~0.2 为 0~1, 0.2~1 为 1
            zero_curve = 4 * abs_inputs
            zero_curve = tf.clip_by_value(zero_curve, 0, 1)
            zero_curve = tf.expand_dims(zero_curve, axis=-1)
            spline_out = spline_out * zero_curve

        # 4. 根据输入的正负调整输出
        if not use_even:
            # 奇对称
            sign = tf.sign(inputs)
            sign = tf.expand_dims(sign, axis=-1)  # 调整形状以匹配 spline_out
            spline_out = spline_out * sign
        if use_debug:
            print(f'max(spline_out): {tf.reduce_max(spline_out)}')
            print(f'min(spline_out): {tf.reduce_min(spline_out)}')

        return spline_out

    def calc_spline_output(self, inputs, use_symmetry=True):
        if use_symmetry:
            return self.calc_spline_output_symmetry(inputs)
        else:
            return self.calc_spline_output_origin(inputs)

    @abstractmethod
    def update_grid_from_samples(self,
                                 inputs: tf.Tensor,
                                 margin: float = 0.01,
                                 grid_eps: float = 0.01
                                 ):
        """
        update the grid based on the inputs adaptively

        Parameters
        ----------
        inputs : tf.Tensor
            the input tensor with shape (batch_size, dim1, dim2, ..., in_size)
        margin : float, optional
            the margin for extending the grid, default to `0.01`, \
            the grid range will be extended into `[min - margin, max + margin]`
        grid_eps : float, optional
            the weight for combining the adaptive grid and uniform grid, default to `0.02`, \n
            the combined grid will be `grid_eps * grid_uniform + (1 - grid_eps) * grid_adaptive`
        """

        raise NotImplementedError

    @abstractmethod
    def extend_grid_from_samples(self,
                                 inputs: tf.Tensor,
                                 extend_grid_size: int,
                                 margin: float = 0.01,
                                 grid_eps: float = 0.01,
                                 l2_reg: float = 0.0,
                                 fast: bool = True
                                 ):
        """
        extend the grid based on the inputs adaptively

        Parameters
        ----------
        inputs : tf.Tensor
            the input tensor with shape (batch_size, dim1, dim2, ..., in_size)
        extend_grid_size : int
            the number of grid points after extending the grid
        margin : float, optional
            the margin for extending the grid, default to `0.01`, \
            the grid range will be extended into `[min - margin, max + margin]`
        grid_eps : float, optional
            the weight for combining the adaptive grid and uniform grid, default to `0.02`, \n
            the combined grid will be `grid_eps * grid_uniform + (1 - grid_eps) * grid_adaptive`
        l2_reg : float, optional
            The L2 regularization factor for the least square solver, by default `0.0`
        fast : bool, optional
            Whether to use the fast solver for the least square problem, by default `True`
        """

        raise NotImplementedError
