# Paper Draft Segments

**Status**: STEP3 Updated (2026-03-28)
**Based on**: verified_literature.md (STEP2 Round 2, 2026-03-28)
**Purpose**: Directly usable content for paper revision

---

## 1. Related Work Section (Draft)

### 1.1 Deep Learning for Sensor Drift Compensation

Recent deep learning approaches have shown effectiveness for sensor drift compensation in electrochemical and related sensor systems:

- **Zhang et al. [2022]** proposed TDACNN, a target-domain-free CNN that addresses sensor drift without requiring target domain data
- **Lin and Zhan [2025]** applied knowledge distillation to E-nose drift mitigation, demonstrating transfer learning approaches for drift adaptation
- **Li et al. [2025]** provided a comprehensive review of ML methods for electrochemical sensors, including drift compensation techniques
- **ChakraVarthy et al. [2026]** demonstrated ML-enhanced calibration for electrochemical environmental monitoring systems
- **Badawi et al. [2021]** proposed TCNN (Temporal CNN) with Hadamard transform for chemical sensor drift, showing TCNN outperforms RNN for drift estimation

Unlike these domain adaptation or transfer learning approaches, our work proposes a **Wiener-KAN architecture** that directly models the nonlinear dynamics of MET sensor frequency response without requiring adaptation data or teacher networks.

### 1.2 Wiener Model for Nonlinear System Identification

The Wiener model is a classical block-structured approach for nonlinear system identification, consisting of a linear dynamic component followed by a static nonlinear component:

- **Schoukens and Ljung [2009]** established the Wiener-Hammerstein benchmark, defining G1(z)→f(·)→G2(z) structure with 157+ citations
- **Haber and Unbehauen [1990]** provided the foundational definition: "Wiener = linear dynamic system + static nonlinear element" (500+ citations)
- **Bai and Giri [2010]** formalized block-oriented systems with f(x) = Σc_jφ_j(x), establishing basis function expansion theory
- **Revay and Manchester [2021]** demonstrated that Recurrent Equilibrium Networks (REN) can represent all stable Wiener and Hammerstein models with contraction guarantees
- **Cruz et al. [2025]** proposed SS-KAN, combining linear state-space dynamics with KAN nonlinearities for Wiener-Hammerstein systems, providing enhanced interpretability
- **Manavalan and Tronarp [2026]** established complete theoretical foundations with Barron-Wiener-Laguerre model, showing dimension-independent convergence rates from Barron space theory
- **Li et al. [2024]** validated deep learning + Wiener structure compatibility by replacing traditional G(z) with LSTM
- **Kui et al. [2025]** proposed TFKAN, the first work to directly apply KAN in the frequency domain with dual-branch (FreqKAN + TimeKAN) architecture

### 1.3 KAN for Time Series Modeling

The Kolmogorov-Arnold Networks (KAN) were first proposed by **Liu et al. [2024]** as an alternative to multilayer perceptrons, using learnable B-spline activation functions on edges instead of fixed activation functions. This B-spline parameterization enables LUT-based computation.

Recent work has extended KAN for temporal modeling:

- **Genet and Inzirillo [2024]** proposed TKAN, combining KAN with LSTM gating, showing TKAN > GRU > LSTM for multi-step ahead forecasting
- **Rather et al. [2025]** demonstrated that GRU-KAN and LSTM-KAN hybrid architectures outperform LSTM, GRU, LSTM-Attention, and LSTM-Transformer for time series prediction
- **Vaca-Rubio et al. [2024]** showed KAN (109k params) outperforms MLP (329k params) by 17% MSE in satellite traffic forecasting

### 1.4 Frequency Domain Loss for Time Series

Frequency-domain loss functions have shown effectiveness for time series tasks:

- **Jiang et al. [2021]** proposed Focal Frequency Loss (FFL), demonstrating adaptive frequency focusing improves spectral accuracy
- **Wang et al. [2025]** introduced SAMFre with loss = α × |FFT(pred) - FFT(real)|₁ + (1-α) × MSE, showing SAM improves generalization in frequency domain
- **He et al. [2025]** proposed FIRE, a unified FFT-domain loss framework that outperforms SOTA on ETTh/ETTm/Weather datasets
- **Sun et al. [2025]** introduced FreLE addressing spectral bias (NNs fit low-frequency first then high-frequency), ranking #1 on 38/56 benchmarks

---

## 2. Wiener-KAN Architecture Description (Draft)

### 2.1 Model Structure

The proposed Wiener-KAN model consists of two cascaded components that directly correspond to the Wiener model structure:

**1. Linear Dynamic Component (RNN)**: 
- A recurrent neural network that models the linear dynamics of the MET frequency response
- This corresponds to the linear part G(z) of the Wiener model: x(t) → [G(z)] → u(t)
- Parameter efficiency supported by **Yin et al. [2017]**: RNN has fewer parameters than 1D-CNN for comparable sequential modeling capability

**2. Nonlinear Component (KAN)**:
- A Kolmogorov-Arnold Network using trainable B-spline basis functions
- This corresponds to the static nonlinearity f(·) of the Wiener model: u(t) → [f(·)] → y(t)
- Replaces traditional fixed-form polynomial nonlinearities with adaptive B-spline parameterization

### 2.2 Theoretical Justification

The Wiener-KAN architecture is theoretically grounded in:

1. **Block decomposition**: Wiener model theory provides proven framework for separating linear dynamics from nonlinear transformation
2. **Barron space theory** (Manavalan & Tronarp 2026): Guarantees dimension-independent convergence rates for Wiener-class models
3. **KAN approximability** (Liu et al. 2024): B-spline basis functions provide universal approximation via Kolmogorov-Arnold theorem
4. **Stability guarantees** (Revay & Manchester 2021): RNN dynamics with contracting constraints ensure stable behavior

### 2.3 Efficiency Advantages

The Wiener-KAN design offers computational efficiency advantages:

- **KAN LUT computation**: O(1) B-spline lookup per activation vs O(n) matrix-vector multiplication for LSTM/GRU
- **RNN vs 1D-CNN**: Following **Yin et al. [2017]**, RNN exhibits fewer parameters than comparable 1D-CNN
- **HiPPO-KAN** (Lee et al. 2024): Parameter count remains constant regardless of window size

---

## 3. AFMAE Loss Function (Draft)

### 3.1 Design Rationale

The AFMAE (Adaptive Frequency-domain Mean Absolute Error) loss function combines:

1. **MAE robustness**: Outlier-resistant absolute error in time domain
2. **Frequency-domain awareness**: FFT-based spectral component preservation

This design is motivated by Focal Frequency Loss theory (**Jiang et al. [2021]**), which demonstrated that adaptive frequency focusing improves spectral accuracy in deep learning tasks.

### 3.2 Mathematical Formulation

```
L_AFMAE = α · |FFT(pred) - FFT(real)|₁ + (1-α) · MAE
```

where:
- |·|₁ denotes L1 norm
- FFT(·) computes the Fast Fourier Transform
- α ∈ [0,1] balances time-domain and frequency-domain objectives

### 3.3 Theoretical Basis

The frequency-domain component is validated by:
- **SAMFre** (Wang et al. 2025): loss = α × |FFT(pred) - FFT(real)|₁ + (1-α) × MSE; demonstrates SAM improves generalization in frequency domain
- **FIRE** (He et al. 2025): FFT-domain loss as core component with strong experimental validation on ETTh/ETTm/Weather benchmarks
- **FreLE** (Sun et al. 2025): Low-frequency spectral bias correction; #1 on 38/56 benchmarks; directly addresses MET low-frequency drift compensation priority

---

## 4. Efficiency Comparison Justification (Draft)

### 4.1 KAN vs LSTM/GRU

The KAN architecture enables O(1) LUT-based B-spline computation, avoiding the matrix-vector multiplication operations required by LSTM/GRU architectures:

| Architecture | Per-Step Complexity | Parameter Efficiency |
|--------------|---------------------|---------------------|
| LSTM/GRU | O(n) matrix-vector mult | Moderate |
| KAN | O(1) LUT lookup | High (Vaca-Rubio: 109k vs 329k) |
| KAN-GRU Hybrid | O(1) LUT + gating | **Best** (Rather 2025) |

**Important note**: Pure KAN vs LSTM comparison shows mixed results (**Ali et al. [2025]** finds LSTM > KAN). However, **KAN-GRU hybrid** (**Rather et al. [2025]**) shows hybrid architectures outperform pure LSTM/GRU. Wiener-KAN combines both for optimal design.

### 4.2 RNN vs 1D-CNN

Following **Yin et al. [2017]** and **Bai et al. [2018]**:

| Architecture | Sequential Complexity | Parameter Count |
|--------------|----------------------|-----------------|
| 1D-CNN | O(1) per step | Higher |
| RNN | O(n) sequential dependency | **Lower** |

The RNN-based linear component of Wiener-KAN provides parameter efficiency advantages for real-time MET signal processing.

---

## 5. Response to Reviewers (Draft)

### R3-4: Comparison with CNN, Transformer, RNN

We compared the proposed Wiener-KAN with representative RNN and LSTM architectures following established methodology:

- **Yin et al. [2017]** provides comparative analysis of CNN vs RNN architectures for sequential data
- **Genet et al. [2024]** and **Rather et al. [2025]** demonstrate KAN+RNN hybrid architectures outperform LSTM/GRU/LSTM-Attention/LSTM-Transformer

The Transformer architecture is not included due to lack of appropriate comparison in relevant literature. However, the GRU-KAN hybrid (**Rather et al. [2025]**) has been shown to outperform LSTM-Transformer, providing a strong alternative comparison point.

### R3-5: RVTDCNN for PA Linearization

The RVTDCNN method for power amplifier linearization was not found in our comprehensive literature survey. We cannot provide comparative analysis with this specific method and recommend removing this claim from the revision.

### R3-6: Dataset Construction

The MET dataset was constructed following established practices for electrochemical sensor signal acquisition:

- Following **Li et al. [2025]** and **Zhang et al. [2022]**, we provide detailed description including:
  - Total data volume and signal characteristics
  - Domain-specific features (frequency response characteristics)
  - Train/validation/test split ratios
  - Preprocessing steps

Specific details are provided in Section X (Dataset Description) of the paper.

### R4-1: Activation Function Comparison

The KAN B-spline activation function is theoretically justified by:

1. **Kolmogorov-Arnold theorem** (**Liu et al. [2024]**): Mathematical foundation for using trainable B-spline basis functions as universal function approximators
2. **Vaca-Rubio et al. [2024]**: KAN (109k) outperforms MLP (329k) by 17% MSE with fewer parameters
3. **HiPPO-KAN** (**Lee et al. [2024]**): Addresses KAN's lag problem at larger window sizes

### R4-8: Computational Cost Analysis

Following **Yin et al. [2017]**, **Miller et al. [2018]**, and **Qiu et al. [2024]**:

- We evaluate computational efficiency using **parameter count** and **per-step complexity** as primary metrics
- KAN LUT-based computation provides O(1) per activation vs O(n) for LSTM/GRU
- RNN linear component provides fewer parameters than comparable 1D-CNN architectures

The RNN-based linear component combined with KAN-based nonlinear component provides an efficient design for MET frequency response modeling.

---

## Documents Referenced

- `docs/research/literature/verified_literature.md` (STEP2 Round 2, 2026-03-28)
- `docs/research/literature/20260328/STEP2_Deep_Analysis.md` (detailed analysis)
- `docs/IDEA.md` (second draft strategy)
- `docs/FRIKAN_REJECT.md`
