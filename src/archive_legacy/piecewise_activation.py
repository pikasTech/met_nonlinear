import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf


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
    def from_xk(cls, x: list, k: list):
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


# Example breakpoints and corresponding slopes
xn = [1.0, 2.0]
kn = [0.5, 1.0]

# Create the custom layer using from_xk
layer = PiecewiseActivationLayer.from_xk(xn, kn)

# Print the linear equations and their corresponding ranges
layer.print_equations()

# Test the function
x_test = np.linspace(-4, 4, 100).reshape(-1, 1)
x_test_tf = tf.constant(x_test, dtype=tf.float32)
y_test_tf = layer.piecewise_activation(x_test_tf)
y_test = y_test_tf.numpy()

# Plot the function
plt.plot(x_test, y_test)
plt.title("Piecewise Activation Function")
plt.xlabel("x")
plt.ylabel("y")
plt.grid()
plt.show()
