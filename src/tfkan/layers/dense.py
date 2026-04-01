import tensorflow as tf
from .base import PiecewiseActivationLayer
import numpy as np
from utils import grid_log
from keras.layers import Layer
from .base import LayerKAN
from ..ops.spline import fit_spline_coef
from ..ops.grid import build_adaptive_grid

from typing import Tuple, List, Any, Union, Callable


class DenseKAN(Layer, LayerKAN):
    def __init__(
        self,
        units: int,
        use_bias: bool = True,
        grid_size: int = 5,
        spline_order: int = 3,
        grid_range: Union[Tuple[float], List[float]] = (-1.0, 1.0),
        spline_initialize_stddev: float = 0.1,
        basis_activation: Union[str, Callable] = 'silu',
        dtype=tf.float32,
        fix_scale_factor: bool = False,
        disable_basis_activation: bool = False,
        kan_log_grid=False,
        grid_expand=True,
        only_positive: bool = True,
        use_even: bool = False,
        use_symmetry: bool = True,
        **kwargs
    ):
        super(DenseKAN, self).__init__(dtype=dtype, **kwargs)
        self.units = units
        self.grid_size = grid_size
        self.spline_order = spline_order
        self.grid_range = grid_range
        self.basis_activation = basis_activation
        self.use_bias = use_bias
        self.kan_log_grid = kan_log_grid
        self.grid_expand = grid_expand
        self.spline_initialize_stddev = spline_initialize_stddev
        self.fix_scale_factor = fix_scale_factor
        self.disable_basis_activation = disable_basis_activation
        self.only_positive = only_positive
        self.use_even = use_even
        self.use_symmetry = use_symmetry
        self.built = False

    def assign_weights(self, spline_kernel, scale_factor=None, bias=None):
        # reshape spline_kernel to (1, n, 1)
        spline_kernel = np.array(spline_kernel)
        spline_kernel = spline_kernel.reshape(1, spline_kernel.shape[0], 1)
        self.spline_kernel.assign(spline_kernel)
        if scale_factor is not None:
            self.scale_factor.assign(scale_factor)
        if bias is not None:
            self.bias.assign(bias)

    def build(self, input_shape: Any):
        if self.built:
            return
        # input_shape (batch_size, dim1, dim2, ..., in_size)
        if isinstance(input_shape, int):
            in_size = input_shape
        else:
            in_size = input_shape[-1]

        self.in_size = in_size
        self.spline_basis_size = self.grid_size + self.spline_order
        bound = self.grid_range[1] - self.grid_range[0]

        # Build grid
        if self.kan_log_grid:
            eps = 10e-4
            self.grid = grid_log.generate_mixed_log_linear_points(
                self.grid_range[0] + eps, self.grid_range[1],
                self.grid_size + 2 * self.spline_order + 1)
            # to self.dtype
            self.grid = tf.cast(self.grid, dtype=self.dtype)
        else:
            if self.grid_expand:
                self.grid = tf.linspace(
                    self.grid_range[0] - self.spline_order *
                    bound / self.grid_size,
                    self.grid_range[1] + self.spline_order *
                    bound / self.grid_size,
                    self.grid_size + 2 * self.spline_order + 1
                )
            else:
                self.grid = tf.linspace(
                    float(self.grid_range[0]), float(self.grid_range[1]), self.grid_size +
                    2 * self.spline_order + 1
                )
        # Expand the grid to (in_size, -1)
        self.grid = tf.repeat(self.grid[None, :], in_size, axis=0)

        # Disable grid as a tf.Variable
        # self.grid = tf.Variable(
        #     initial_value=tf.cast(self.grid, dtype=self.dtype),
        #     trainable=False,
        #     dtype=self.dtype,
        #     name="spline_grid"
        # )

        # The linear weights of the spline activation
        self.spline_kernel = self.add_weight(
            name="spline_kernel",
            shape=(self.in_size, self.spline_basis_size, self.units),
            initializer=tf.keras.initializers.RandomNormal(
                stddev=self.spline_initialize_stddev),
            trainable=True,
            dtype=self.dtype
        )

        # weight_spline_kernel = self.spline_kernel.numpy()  # shape: (1, 35, 1)
        # grid = self.grid.numpy()
        # len_weight_spline_kernel = weight_spline_kernel.shape[1]
        # linespace = np.linspace(
        #     0, 1, len_weight_spline_kernel)
        # for i in range(weight_spline_kernel.shape[1]):
        #     weight_spline_kernel[0, i, 0] = linespace[i]

        # self.spline_kernel.assign(weight_spline_kernel)
        grid = self.grid.numpy()[0]

        # self.assign_grid_xnyn(
        #     0,
        #     # np.linspace(0.01, 1, self.grid.shape[1]),
        #     # np.linspace(0.01, 1, self.grid.shape[1])
        #     # np.linspace(grid[0], grid[-1], self.grid_size),
        #     # np.linspace(grid[0], grid[-1], self.grid_size)
        #     np.linspace(0, grid[-1], self.grid_size),
        #     np.linspace(0, grid[-1], self.grid_size)
        # )

        if not self.fix_scale_factor:
            self.scale_factor = self.add_weight(
                name="scale_factor",
                shape=(self.in_size, self.units),
                initializer=tf.keras.initializers.GlorotUniform(),
                trainable=not self.fix_scale_factor,
                dtype=self.dtype
            )
        else:
            self.scale_factor = None

        # Build basis activation
        if isinstance(self.basis_activation, str):
            self.basis_activation = tf.keras.activations.get(
                self.basis_activation)
        elif not callable(self.basis_activation):
            raise ValueError(
                f"expected basis_activation to be str or callable, found {type(self.basis_activation)}")

        # Build bias
        if self.use_bias:
            self.bias = self.add_weight(
                name="bias",
                shape=(self.units,),
                initializer=tf.keras.initializers.Zeros(),
                trainable=True,
                dtype=self.dtype
            )
        else:
            self.bias = None

        self.built = True

    def call(self, inputs, *args, **kwargs):
        # Check the inputs and reshape inputs into 2D tensor (-1, in_size)
        inputs, orig_shape = self._check_and_reshape_inputs(inputs)
        output_shape = tf.concat([orig_shape, [self.units]], axis=0)

        # Compute the spline output using the new method
        spline_out = self.compute_spline_output(inputs)

        # Aggregate the output using sum (on in_size dim) and reshape into the original shape
        spline_out = tf.reshape(tf.reduce_sum(
            spline_out, axis=-2), output_shape)

        # Add bias
        if self.use_bias:
            spline_out += self.bias

        return spline_out

    def compute_spline_output(self, inputs):
        """
        Compute the spline output given the inputs.
        This method calculates the spline activation, adds the basis activation
        (if not disabled), scales the output, and returns the result without
        aggregating or adding bias.
        """
        # Calculate the B-spline output
        spline_out = self.calc_spline_output(inputs)

        # Calculate the basis activation
        if self.disable_basis_activation:
            basis_out = tf.zeros_like(inputs)
        else:
            basis_out = self.basis_activation(inputs)

        # Add basis to the spline_out: phi(x) = c * (b(x) + spline(x))
        spline_out += tf.expand_dims(basis_out, axis=-1)

        if not self.fix_scale_factor:
            # Scale the output
            spline_out *= tf.expand_dims(self.scale_factor, axis=0)

        return spline_out  # Shape: (batch_size, in_size, units)

    def _check_and_reshape_inputs(self, inputs):
        shape = inputs.get_shape()
        ndim = len(shape)

        tf.debugging.assert_greater_equal(
            ndim,
            2,
            f"Expected min_ndim=2, found ndim={ndim}. Full shape received: {shape}"
        )

        tf.debugging.assert_equal(
            inputs.shape[-1],
            self.in_size,
            f"Expected last dimension of inputs to be {self.in_size}, found {shape[-1]}."
        )

        orig_shape = tf.shape(inputs)[:-1]
        # Reshape the inputs to (-1, in_size)
        inputs = tf.reshape(inputs, (-1, self.in_size))

        return inputs, orig_shape

    def update_grid_from_samples(self,
                                 inputs: tf.Tensor,
                                 margin: float = 0.01,
                                 grid_eps: float = 0.01
                                 ):
        # Check the inputs and reshape inputs into 2D tensor (-1, in_size)
        inputs, _ = self._check_and_reshape_inputs(inputs)

        # Calculate the B-spline output
        spline_out = self.calc_spline_output(inputs)

        # Build the adaptive grid
        grid = build_adaptive_grid(
            inputs, self.grid_size, self.spline_order, grid_eps, margin, self.dtype)

        # Update the spline kernel using the new grid and LS method
        updated_kernel = fit_spline_coef(
            inputs, spline_out, grid, self.spline_order)

        # Assign to the model
        self.grid.assign(grid)
        self.spline_kernel.assign(updated_kernel)

    def extend_grid_from_samples(self,
                                 inputs: tf.Tensor,
                                 extend_grid_size: int,
                                 margin: float = 0.01,
                                 grid_eps: float = 0.01,
                                 **kwargs
                                 ):
        # Check extend_grid_size
        try:
            assert extend_grid_size >= self.grid_size
        except AssertionError:
            raise ValueError(
                f"expected extend_grid_size > grid_size, found {extend_grid_size} <= {self.grid_size}")

        # Check the inputs and reshape inputs into 2D tensor (-1, in_size)
        inputs, _ = self._check_and_reshape_inputs(inputs)

        # Calculate the B-spline output
        spline_out = self.calc_spline_output(inputs)

        # Build the adaptive grid
        # New shape with (in_size, extend_grid_size + 2 * spline_order + 1)
        grid = build_adaptive_grid(
            inputs, extend_grid_size, self.spline_order, grid_eps, margin, self.dtype)

        # Update the spline kernel using the new grid and LS method
        l2_reg, fast = kwargs.pop("l2_reg", 0), kwargs.pop("fast", True)
        updated_kernel = fit_spline_coef(
            inputs, spline_out, grid, self.spline_order, l2_reg, fast)

        # Update the grid and spline kernel
        delattr(self, "grid")
        self.grid = tf.Variable(
            initial_value=tf.cast(grid, dtype=self.dtype),
            trainable=False,
            dtype=self.dtype,
            name="spline_grid"
        )

        self.grid_size = extend_grid_size
        self.spline_basis_size = extend_grid_size + self.spline_order
        delattr(self, "spline_kernel")
        self.spline_kernel = self.add_weight(
            name="spline_kernel",
            shape=(self.in_size, self.spline_basis_size, self.units),
            initializer=tf.keras.initializers.Constant(updated_kernel),
            trainable=True,
            dtype=self.dtype
        )

    def get_config(self):
        config = super(DenseKAN, self).get_config()
        config.update({
            "units": self.units,
            "use_bias": self.use_bias,
            "grid_size": self.grid_size,
            "spline_order": self.spline_order,
            "grid_range": self.grid_range,
            "spline_initialize_stddev": self.spline_initialize_stddev,
            "basis_activation": tf.keras.activations.serialize(self.basis_activation),
            "fix_scale_factor": self.fix_scale_factor,
            "disable_basis_activation": self.disable_basis_activation,
            "only_positive": self.only_positive,
            "use_even": self.use_even,
            "use_symmetry": self.use_symmetry
        })

        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)

    def assign_grid_xnyn(
        self,
        feature_index: int,
        xn: List[float],
        yn: Union[List[float], List[List[float]]],
        use_debug: bool = False
    ):
        """
        Assign spline coefficients for a specified feature using given key points.

        Parameters
        ----------
        feature_index : int
            Index of the feature to update.
        xn : List[float]
            Input key points for the spline fitting.
        yn : List[float] or List[List[float]]
            Output key points corresponding to `xn`. If `units > 1`, provide a list of lists.
        use_debug : bool, optional
            If True, prints out the matrices for debugging purposes. Default is False.
        """
        batch_size = len(xn)

        # Convert xn to tensor and replicate across all features
        xn_tensor = tf.constant(xn, dtype=self.dtype)  # Shape: (batch_size,)
        # Shape: (batch_size, in_size)
        inputs = tf.tile(tf.reshape(xn_tensor, (batch_size, 1)), [
                         1, self.in_size])

        if use_debug:
            print("Inputs:")
            print(inputs.numpy())

        # Compute the spline output
        # Shape: (batch_size, in_size, units)
        spline_out = self.calc_spline_output(inputs)

        if use_debug:
            print("Initial Spline Output:")
            print(spline_out.numpy())

        # Modify spline_out only for the specified feature_index according to yn
        yn_tensor = tf.constant(yn, dtype=self.dtype)
        # Shape: (batch_size, )

        # replace yn_tensor_origin with selected feature_index

        spline_out_np = spline_out.numpy()  # (points, units, 1)
        yn_tensor_np = yn_tensor.numpy()

        # 根据 units 的维度进行赋值
        if self.units > 1:
            spline_out_np[:, 0, feature_index] = yn_tensor_np
        else:
            # spline_out_np[:, feature_index: 0] = yn_tensor_np.reshape(10, 1, 1)
            for i in range(batch_size):
                spline_out_np[i, feature_index, 0] = yn_tensor_np[i]

        # 将修改后的 numpy 数组转换回 Tensor
        spline_out = tf.constant(spline_out_np, dtype=self.dtype)

        if use_debug:
            print("Modified Spline Output:")
            print(spline_out.numpy())

        # Update spline_kernel
        updated_kernel = fit_spline_coef(
            inputs, spline_out, self.grid, self.spline_order,
            fast=False
        )

        if use_debug:
            print("Updated Kernel Coefficients:")
            print(updated_kernel.numpy())

        # spline_kernel shape: (in_size, spline_basis_size, units)
        self.spline_kernel.assign(updated_kernel)

    def assign_grid_xnkn(
        self,
        feature_index: int,
        xn: List[float],
        kn: List[float],
    ):
        xn, yn = PiecewiseActivationLayer.from_xk(xn, kn).to_xnyn()
        self.assign_grid_xnyn(feature_index, xn, yn)
