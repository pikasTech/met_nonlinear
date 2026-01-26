import matplotlib.pyplot as plt
import numpy as np
from IIR_LNRNN import PiecewiseActivationLayer
import tensorflow as tf

# Original piecewise function
f = PiecewiseActivationLayer.from_xk([1.0, 2.0], [1.0, 0.1])

# Generate the inverse function
fr = f.reverse()

# Test the inverse function

x_values = np.linspace(-3, 3, 100)
x_tensor = tf.constant(x_values, dtype=tf.float32)

# Apply the original function
y_values = f(x_tensor)

# Apply the inverse function
x_reconstructed = fr(y_values)
y_values_fr = fr(x_tensor)

# Verify that x_reconstructed is approximately equal to x_tensor

plt.plot(x_values, y_values, label='f', linestyle='--')
plt.plot(x_values, y_values_fr, label='f_r', linestyle='--')
plt.plot(x_values, x_reconstructed, label='Reconstructed x')
# plt.plot(x_values, x_reconstructed.numpy(), label='Reconstructed x')
plt.legend()
plt.show()
