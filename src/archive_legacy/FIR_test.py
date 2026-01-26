import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import bilinear, lfilter, freqs, freqz, TransferFunction, bode, firwin

# System parameters
omega_n = 5   # Natural frequency (rad/s)
zeta = 0.2    # Damping ratio

# Transfer function coefficients
numerator = [omega_n**2]  # Numerator of the transfer function: [omega_n**2]
# Denominator: [1, 2*zeta*omega_n, omega_n**2]
denominator = [1, 2*zeta*omega_n, omega_n**2]

# Create transfer function
system = TransferFunction(numerator, denominator)

# Frequency response of the analog system
w, mag, phase = bode(system, np.linspace(0.1, 20, 800))

# Sampling rate and time step for digital system
fs = 100  # Sampling frequency (Hz)
Ts = 1/fs  # Sampling period

# Convert analog transfer function to digital (IIR) using bilinear transformation
b_iir, a_iir = bilinear(numerator, denominator, fs)

# Frequency response of the digital IIR filter
w_iir, h_iir = freqz(b_iir, a_iir, worN=8000, fs=fs)

# FIR filter design parameters
fir_order = 50  # Increase FIR filter order
cutoff = omega_n / (2 * np.pi * fs)  # Normalized cutoff frequency

# Design FIR filter using firwin
b_fir = firwin(fir_order+1, cutoff=cutoff, window='hamming')
a_fir = [1]  # FIR filters have denominator [1]

# Frequency response of the FIR filter
w_fir, h_fir = freqz(b_fir, a_fir, worN=8000, fs=fs)

# Plotting the magnitude frequency responses
plt.figure(figsize=(12, 8))
# Original analog system
plt.plot(w, mag, label='Analog System', linestyle='--')
# IIR filter
plt.plot(w_iir, 20 * np.log10(np.abs(h_iir)), label='Equivalent IIR Filter')
# FIR filter
plt.plot(w_fir, 20 * np.log10(np.abs(h_fir)),
         label='Equivalent FIR Filter (Order=50)')
plt.title(
    'Magnitude Frequency Response of Analog System and Equivalent IIR/FIR Filters')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude (dB)')
plt.grid(True)
plt.legend()
plt.ylim(-60, 10)
plt.axvline(omega_n / (2 * np.pi), color='r',
            linestyle='--', label='Natural Frequency')
plt.xlim(0, 10)
plt.show()
