# FIRE_He_2025 Analysis

## Paper Basic Info

| Field | Value |
|-------|-------|
| Title | A Unified Frequency Domain Decomposition Framework for Interpretable and Robust Time Series Forecasting |
| Authors | Cheng He, Xijie Liang, Zengrong Zheng, Patrick P.C. Lee, Xu Huang, Zhaoyi Li, Hong Xie, Defu Lian, Enhong Chen |
| Institution | USTC, CUHK, Shanghai Black Wing Asset |
| Year | 2025 |

## Core Content Summary

FIRE proposes a unified frequency domain decomposition framework for time series forecasting. Key innovations include:
1. Independent modeling of amplitude and phase components
2. Adaptive learning of frequency basis component weights via causal attention
3. Composite loss function: Huber + FFT-MAE + Phase regularization
4. Novel training paradigm combining strong and weak convergence

## GAP10 Association Analysis (AFMAE vs Pure MAE Improvement)

**Support Type**: Direct with Ablation Evidence

- **Line 646**: FFT loss is explicitly defined as MAE in frequency domain:
```
L_fft = (1/N_f) Σ |FFT(X_true) - FFT(X_out)|
```
This is FFT-MAE directly used in the composite loss.

- **Line 600**: Composite loss definition:
```
L = L_wh + L_fft + R_phi  (Equation 22)
```

- **Lines 747-756 (Table 4)**: Loss ablation study comparing FIRE vs FIRE_advanced (removes FFT loss) vs FIRE_base (Huber only):
  - FIRE (full): Best in 4/7 datasets for MSE, 4/7 for MAE
  - FIRE_advanced (no FFT loss): Best in 0/7 datasets
  - FIRE_base (Huber only): Best in 0/7 datasets

**Key Evidence (Line 747)**:
> "FIRE_advanced (removes FFT loss based on FIRE_base)... While the full model FIRE shows slightly better average MSE and MAE compared to FIRE_enhanced, the full detailed results reveal that FIRE consistently outperforms all variants on a larger number of individual experiments."

This ablation demonstrates that FFT-MAE contributes positively to forecasting accuracy.

## GAP11 Association Analysis (AFMAE vs Other Frequency Domain Loss Efficiency)

**Support Type**: Indirect - Limited Transform Comparison

- **Line 669**: "We choose FFT over other basis decomposition methods because it is reversible and parameter-free"
- **Lines 641-651**: FFT is used as the frequency transform; no comparison with DCT, wavelet, or other frequency transforms
- The paper does NOT compare efficiency of different frequency domain losses (FFT-MAE vs DCT-MAE vs wavelet-MAE)

**Conclusion**: The paper uses FFT-MAE but does not evaluate its efficiency relative to other frequency transforms.

## Key Quotes with Line Numbers

1. **Line 167**: "FIRE introduces several key innovations: (i) independent modeling of amplitude and phase components, (ii) adaptive learning of weights of frequency basis components, (iii) a targeted loss function..."

2. **Line 600 (Equation 22)**: Composite loss definition:
> "FIRE employs a composite loss comprising the Huber loss with hybrid convergence (L_wh), FFT loss (L_fft), and phase regularization (R_phi)"

3. **Line 646 (Equation 26)**: FFT loss definition:
> "The FFT loss, L_fft, is defined as the mean absolute error (MAE) between the predicted and ground truth sequences in the frequency domain"

4. **Line 749**: Ablation evidence for FFT loss contribution:
> "FIRE_advanced (removes FFT loss based on FIRE_base)... FIRE consistently outperforms all variants on a larger number of individual experiments"

## Conclusion Table

| GAP | Support Type | Support Strength | Key Evidence |
|-----|--------------|------------------|--------------|
| GAP10 (AFMAE vs pure MAE) | Direct | Moderate | FFT-MAE defined (Eq 26), ablation shows removing it hurts performance (Table 4) |
| GAP11 (AFMAE vs other frequency losses) | Indirect | Low | FFT used exclusively; no comparison with DCT/wavelet |

## Summary

**FIRE (He 2025)** provides moderate support for GAP10 through:
1. Clear definition of FFT-MAE as frequency domain loss
2. Ablation study demonstrating FFT loss component contributes to model performance

For **GAP11**, the paper does not compare FFT-MAE against DCT-MAE or other frequency domain losses. The paper focuses on amplitude/phase decomposition and composite loss design rather than comparing different frequency transforms.

**Domain Note**: FIRE addresses spectral bias through frequency domain operations, which is conceptually related to AFMAE's goal of frequency-aware loss functions. However, FIRE is designed for general time series forecasting, not specifically for seismic sensor frequency response drift compensation.
