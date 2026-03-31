# FreLE_Sun_2025 Analysis

## Paper Basic Info

| Field | Value |
|-------|-------|
| Title | FreLE: Low-Frequency Spectral Bias in Neural Networks for Time-Series Tasks |
| Authors | Jialong Sun, Xinpeng Ling, Jiaxuan Zou, Jiawen Kang, Kejia Zhang |
| Institution | Heilongjiang University, East China Normal University, Xi'an Jiaotong University, Guangdong University of Technology |
| Year | 2025 |

## Core Content Summary

FreLE (Frequency Loss Enhancement) is an algorithm that addresses spectral bias in neural networks for time series tasks. It combines:
1. **Explicit Frequency Regularization**: FFT-MAE style loss (lines 281-287, Equation 7)
2. **Implicit Frequency Regularization**: Adaptive frequency processing to reduce noise

The explicit regularization adds frequency-domain MAE to the optimization objective, while implicit regularization uses adaptive normalization to handle noise in frequency components. FreLE achieved first place 38 times and second place 18 times across seven real-world datasets.

## GAP10 Association Analysis (AFMAE vs Pure MAE Improvement)

**Critical Support**: Strong direct support

- **Lines 281-287 (Equation 7)**: Explicit frequency regularization definition.
  > "L^f = (1/n) sum_{i=1}^{N} || F(X_i) - F_theta(X_hat_i) ||"

  This is explicitly an MAE computation in the frequency domain using Fourier transform.

- **Lines 289-291**: When delta=1, only frequency loss is used.
  > "where, delta serves as a parameter for balancing between two types of losses. An interesting research question is whether, by using explicit regularization alone, significant optimization effects can already be achieved when delta = 1."

- **Lines 459-461**: When delta=0 (no frequency regularization), performance is worst.
  > "It can be observed that when delta = 0, the model performs worst, as the frequency regularization method is not applied."

**Direct Support**: Strong

The paper clearly shows that:
1. Frequency-domain MAE (Equation 7) is explicitly defined
2. Ablation shows removing frequency regularization (delta=0) degrades performance
3. Setting delta=1 (pure frequency loss) still yields good results

This provides direct evidence that frequency-domain MAE outperforms pure time-domain optimization.

## GAP11 Association Analysis (AFMAE vs Other Frequency Domain Loss Efficiency)

**Critical Support**: Indirect support

- **Lines 281-287 (Equation 7)**: Uses FFT for frequency transformation.
  > The explicit frequency regularization uses Fourier transform to compute MAE in frequency domain.

- **Lines 253-259**: Describes FreLE framework.
  > "FreLE algorithm balances frequency information and removes noise by separately discussing its two key components: explicit frequency regularization and implicit frequency regularization."

**Direct Support**: Limited

The paper does NOT compare FFT-MAE with DCT-MAE, wavelet-MAE, or other frequency-domain losses. FreLE uses FFT exclusively for the explicit regularization component. The comparison in Table 4 is between FreLE (full) vs variants with only explicit or implicit regularization, not between different frequency transforms.

## Key Quotes with Line Numbers

1. **Lines 269-275 (Equation 6)**: Time-domain MAE baseline.
   > "L_theta^t = (1/n) sum_{i=1}^{n} || X_i - X_hat_i ||"

2. **Lines 281-287 (Equation 7)**: Frequency-domain MAE.
   > "L^f = (1/n) sum_{i=1}^{N} || F(X_i) - F_theta(X_hat_i) ||"

3. **Lines 282-284**: Combined objective.
   > "min_theta; delta L_theta^f + (1 - delta) L_theta^t"

4. **Lines 459-461**: Ablation showing frequency regularization importance.
   > "It can be observed that when delta = 0, the model performs worst, as the frequency regularization method is not applied."

5. **Lines 461-463**: delta=1 (pure frequency) also works well.
   > "directly setting delta = 1 without hyperparameter tuning also yields good experimental performance."

6. **Lines 271-275**: Ablation study results showing FreLE (EFR+IFR) outperforms EFR alone.
   > Table 4 shows EFR-IFR (0.386) vs EFR (0.411) on ETTm1 MSE.

## Conclusion Table

| GAP | Support Type | Support Strength | Key Evidence |
|-----|--------------|------------------|--------------|
| GAP10 (AFMAE vs pure MAE) | Direct | Strong | Explicit frequency-domain MAE defined (Eq 7); ablation shows delta=0 (no freq) gives worst results; delta=1 (pure freq) gives good results. FreLE outperforms baselines. |
| GAP11 (AFMAE vs other frequency domain losses) | Indirect | Low | Uses FFT exclusively; does NOT compare with DCT-MAE, wavelet-MAE, or other frequency-domain losses. |

## Summary

**FreLE (Sun 2025)** provides strong direct support for GAP10 by:
1. Clearly defining frequency-domain MAE (Equation 7)
2. Showing ablation that removing frequency regularization degrades performance
3. Demonstrating that pure frequency loss (delta=1) still yields competitive results
4. Achieving superior performance across multiple datasets

For GAP11, the paper does NOT compare FFT-MAE with other frequency transforms. FreLE uses FFT exclusively for the explicit regularization component. There is no experimental comparison of efficiency between FFT-MAE, DCT-MAE, wavelet-MAE, etc.

**Key Distinction**: FreLE explicitly defines frequency-domain MAE (L^f) and shows it improves over time-domain MAE, which directly supports GAP10. However, for GAP11, the paper focuses on the combination of explicit and implicit regularization, not on comparing different frequency transforms.

**Key Limitation**: The paper focuses on spectral bias mitigation through combined explicit/implicit regularization, not on comparing efficiency of different frequency transforms.
