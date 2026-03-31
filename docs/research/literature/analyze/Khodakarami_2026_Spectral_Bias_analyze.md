# Khodakarami_2026_Spectral_Bias Analysis

## Paper Basic Info

| Field | Value |
|-------|-------|
| Title | Spectral bias in physics-informed and operator learning: Analysis and mitigation guidelines |
| Authors | Siavash Khodakarami, Vivek Oommen, Nazanin Ahmadi Daryakenar, Maxim Beekenkamp, George Em Karniadakis |
| Institution | Brown University |
| Year | 2026 |

## Core Content Summary

This paper provides a systematic investigation of spectral bias in physics-informed neural networks (PINNs), physics-informed KANs (PIKANs), and neural operators. The authors demonstrate that spectral bias is not merely representational but fundamentally dynamical, strongly impacted by training strategies and optimization procedures. Key contributions include:

1. Quantifying spectral bias through frequency-resolved error metrics, Barron-norm diagnostics, and higher-order statistical moments
2. Demonstrating that second-order optimization methods substantially alter spectral learning order
3. Showing that spectral bias in neural operators can be mitigated through spectral-aware loss formulations without increasing inference cost
4. Comparing different loss functions including MSE and **binned spectral loss** for neural operators

The paper focuses on **how optimization methods and loss functions** affect spectral bias mitigation, with Section 2.2 providing theoretical analysis on optimization's role, and Section 3 describing methods including loss formulations.

## GAP10 Association Analysis (AFMAE vs Pure MAE Improvement)

**Critical Support**: Indirect support through spectral bias theory

- **Lines 49-51**: Discusses that "spectral bias also plays a central role in the performance of neural operators" and mentions that spectral-aware loss formulations can effectively mitigate spectral bias without increasing inference cost.
  
- **Lines 121-123**: Through Parseval's theorem, shows that L² neural training loss relates to Fourier coefficients, explaining why low-frequency modes have larger energies and contribute more to total loss. This theoretical foundation explains **why frequency-domain losses would improve over pure MAE**.

- **Lines 53-55**: Mentions that spectral bias mitigation strategies include "spectral-aware loss formulations" for operator learning.

**Direct Support**: Limited

The paper does NOT specifically compare Adaptive Frequency MAE (AFMAE) vs pure MAE. The loss functions discussed are primarily:
- Standard MSE loss (L²)
- Binned spectral loss (mentioned in line 26, 85)

The paper provides theoretical support for why frequency-domain losses would be beneficial but does not directly validate AFMAE improvements.

## GAP11 Association Analysis (AFMAE vs Other Frequency Domain Loss Efficiency)

**Critical Support**: Moderate support

- **Line 85**: Mentions "different loss functions (e.g., MSE and **binned spectral loss [26]**)" for neural operators in solving high-frequency problems.

- **Lines 177-186** (Section 2.3): Describes spectral bias metrics and the binned spectral loss approach. The binned spectral loss is a form of frequency-domain loss that groups frequencies into bins.

- The paper discusses theoretical analysis showing frequency-dependent convergence rates under first-order optimization (lines 245-251), providing rationale for frequency-aware losses.

**Direct Support**: Limited

The paper does not provide direct comparisons between different frequency domain loss functions (e.g., FFT-MAE vs DCT-MAE vs binned spectral loss). It mentions binned spectral loss as one approach but does not evaluate its efficiency relative to other frequency transforms.

## Key Quotes with Line Numbers

1. **Line 17**: "...spectral bias is not simply representational but fundamentally dynamical...spectral-aware loss formulations without increasing the inference cost."

2. **Line 53-55**: "For neural operators, we further show that spectral bias is dependent on the neural operator architecture and can also be effectively mitigated through **spectral-aware loss formulations** without increasing the inference cost."

3. **Line 85**: "...different loss functions (e.g., MSE and **binned spectral loss** [26])..."

4. **Line 121-123**: "Since for most physical systems |ê_k| > |ê_{k*}| if k < k* at the start of the training, then the **low-frequency modes have larger energies and contribute more to the total L² loss**. Therefore, the optimizer of the neural network tends to learn low-frequency modes first..."

## Conclusion Table

| GAP | Support Type | Support Strength | Key Evidence |
|-----|--------------|------------------|--------------|
| GAP10 (AFMAE vs pure MAE) | Indirect | Moderate | Theoretical basis provided (lines 121-123) showing frequency-domain losses address spectral bias by targeting energy distribution across frequencies. Does not directly validate AFMAE improvements. |
| GAP11 (AFMAE vs other frequency domain losses) | Indirect | Low | Mentions binned spectral loss as one spectral-aware approach (line 85) but does not compare efficiency of different frequency transforms (FFT vs DCT vs wavelet). |

## Summary

**Khodakarami 2026** provides theoretical foundation for why frequency-domain losses improve over time-domain losses (GAP10 support) through spectral bias analysis. However, it does not directly compare AFMAE vs pure MAE or evaluate efficiency of different frequency transforms for GAP11. The paper establishes that "spectral-aware loss formulations" can mitigate spectral bias without computational overhead, which is conceptually relevant to AFMAE but not a direct validation.
