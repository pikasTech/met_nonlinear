# Verified Literature
***Status***: STEP2 Updated 2026-03-28 (Round 2 additions)

## P0 - Core Theory

### KAN Network

**Liu et al. - KAN (2024)** arXiv:2404.19756
- Core: First KAN based on Kolmogorov-Arnold theorem
- Quote: KANs have no linear weights -- every weight is a learnable univariate spline
- Relevance: Direct theoretical foundation for Wiener-KAN

**Cruz et al. - State-Space KAN (2025)** arXiv:2506.16392
- Core: SS-KAN = linear state-space + KAN nonlinearity
- Quote: SS-KAN provides enhanced interpretability at cost of accuracy
- Relevance: DIRECT CONNECTION between Wiener and KAN

**Manavalan, Tronarp - Barron-Wiener-Laguerre (2026)** arXiv:2602.13098
- Core: Barron space theory + Wiener model + Laguerre bases
- Key: Linear dynamics (Laguerre) + static nonlinearity (Barron)
- Quote: Dimension-independent convergence rates from Barron space theory
- Relevance: Complete theoretical framework for Wiener-KAN

**Genet, Inzirillo - TKAN (2024)** arXiv:2405.07344
- Core: Temporal KAN = KAN + LSTM/RKAN (Recurring KAN)
- Architecture: RKAN layers with LSTM gating for memory management
- Key finding: TKAN > GRU > LSTM for multi-step ahead forecasting
- Quote: R²@12step: TKAN=0.104, GRU=0.018, LSTM=-0.473
- Relevance: Validates KAN+RNN combination for temporal modeling

**Vaca-Rubio et al. - KAN for Time Series (2024)** arXiv:2405.08790
- Core: KAN for satellite traffic forecasting (IEEE Globecom 2024)
- Key finding: KAN (109k params) outperforms MLP (329k params) by 17% MSE
- Quote: "KANs can achieve higher accuracy with considerably fewer parameters"
- Relevance: Strong evidence for KAN parameter efficiency vs MLP

**Qiu et al. - PowerMLP (2024)** arXiv:2412.13571
- Core: Efficient KAN alternative using ReLU-k power activation
- Key claim: PowerMLP is ~40x faster than KAN, KAN FLOPs >10x PowerMLP
- Quote: "KANs are usually 10x slower than MLPs" (confirming KAN bottleneck)
- Relevance: Confirms KAN computational bottleneck, supports efficiency claim

**Lee et al. - HiPPO-KAN (2024)** arXiv:2410.14939
- Core: HiPPO theory + KAN for constant parameter efficiency
- Key finding: Parameter count remains constant regardless of window size
- Result: Significantly outperforms standard KAN at larger window sizes
- Quote: "HiPPO-KAN significantly outperforms KAN model at larger window sizes"
- Relevance: Supports KAN efficiency claims for variable-length time series

**Rather et al. - KAN-GRU/LSTM Hybrid (2025)** arXiv:2507.13685
- Core: GRU-KAN and LSTM-KAN hybrid architectures
- Key finding: Hybrid > LSTM, GRU, LSTM-Attention, LSTM-Transformer
- Result: 3-month prediction >92%, 8-month >88% accuracy
- Quote: "Outperforms baseline models including LSTM, GRU, LSTM-Attention, LSTM-Transformer"
- Relevance: Validates KAN+RNN combination; hybrid architecture evidence

**Ali et al. - KAN vs LSTM Performance (2025)** arXiv:2511.18613
- Core: Comparative study of KAN vs LSTM for stock price prediction
- ⚠️ CONFLICTING FINDING: LSTM outperforms KAN in accuracy
- Note: KAN advantage only in resource-constrained scenarios
- Quote: "LSTM demonstrates substantial superiority across all tested prediction horizons"
- Relevance: ⚠️ Contradicts Wiener-KAN efficiency claims; handle with care

**Huang et al. - TimeKAN (2025)** arXiv:2502.06910
- Core: KAN-based frequency decomposition for long-term time series forecasting
- Key: Cascade Frequency Decomposition (CFD) + Multi-order KAN (M-KAN)
- Quote: O(L log L) complexity via FFT, Chebyshev polynomials for efficiency
- Result: SOTA on ETTh1/2, ETTm1/2, Weather, Electricity datasets
- Relevance: Supports frequency decomposition + KAN architecture validity

**Kui et al. - TFKAN: Time-Frequency KAN (2025)** arXiv:2506.12696
- Core: First work to directly apply KAN in frequency domain
- Key: Dual-branch architecture (FreqKAN + TimeKAN)
- Quote: "To the best of our knowledge, this is the first work to directly apply KAN in the frequency domain"
- Result: Outperforms 8 SOTA methods on 7 datasets
- Relevance: **Direct support** for Wiener linear(nonlinear separation via dual-branch architecture

**Somvanshi et al. - KAN Survey (2025)** arXiv:2411.06078 (ACM Computing Surveys)
- Core: Comprehensive survey of KAN theory, evolution, applications
- Key: KAN integration with CNN/RNN/Transformer is a growing trend
- Quote: "KAN's integration with other architectures... showcasing its versatility in complementing established neural networks"
- Relevance: Validates KAN+RNN hybrid as emerging research direction

**Livieris - C-KAN: Convolutional KAN (2024)** MDPI Mathematics
- Core: CNN + KAN for multi-step predictions
- Architecture: CNN captures behavior/patterns → KAN for feature analysis
- Relevance: CNN+KAN architecture validates Wiener linear( nonlinear separation

### Wiener Model

**Revay, Manchester - REN for Wiener/Hammerstein (2021)** arXiv:2104.05942
- Core: Recurrent Equilibrium Networks with stability/robustness guarantees
- Key: Contracting dynamics + IQCs; represents all stable Wiener/Hammerstein
- Quote: "Can represent all stable Wiener/Hammerstein models"
- Relevance: Background/competitor; important for stability theory

**Xu et al. - Kernel for Volterra Wiener-Hammerstein (2025)** arXiv:2505.20747
- Core: Kernel design for regularized Volterra series identification
- Complexity: O(N³) or O(Nγ²) with separability rank γ
- Relevance: Volterra series is fundamental nonlinear system representation

**Beintema et al. - Deep Encoder Networks for Wiener-Hammerstein (2020)** arXiv:2012.07697
- Core: Deep encoder networks with multiple shooting decomposition
- Claim: "Lowest known simulation error on Wiener-Hammerstein benchmark"
- ⚠️ NOTE: May conflict with Cruz SS-KAN performance claims
- Relevance: Deep learning approach to block-structured models

**Voit, Enzner - Multikernel Neural Networks (2024)** arXiv:2412.07370
- Core: Block-structured multikernel neural networks for multiplant identification
- Method: Shared weights + plant-specific weights
- Relevance: Directly relevant to block-structured nonlinear models

**Rufolo et al. - Enhanced Transformer for Wiener-Hammerstein (2024)** arXiv:2410.03291
- Core: In-context identification with meta-model trained offline
- Method: Probabilistic framework, recurrent patching
- Relevance: Alternative deep learning approach to Wiener-Hammerstein

**Schoukens, Ljung - Wiener-Hammerstein Benchmark (2009)** diva-portal
- Core: Standard benchmark for nonlinear system identification
- Structure: G1(z) → f(·) → G2(z) (linear dynamics + static nonlinearity + linear dynamics)
- Citation: 157+ (Google Scholar)
- Quote: "In a Wiener-Hammerstein system the static nonlinearity is sandwiched between two unknown dynamic systems"
- Relevance: **Direct theoretical foundation** for Wiener model structure

**Haber, Unbehauen - Structure Identification Survey (1990)** Automatica
- Core: Comprehensive survey of nonlinear dynamic system structure identification
- Citation: 500+ (classic reference)
- Key: Block-structured models (Wiener, Hammerstein, Wiener-Hammerstein)
- Quote: "The Wiener model consists of a linear dynamic system followed by a static nonlinear element"
- Relevance: **Core theoretical foundation** for Wiener-KAN architecture

**Bai, Giri - Block-oriented Nonlinear Systems (2010)** Springer
- Core: Unified treatment of Wiener, Hammerstein, Wiener-Hammerstein structures
- Key: f(x) = Σc_jφ_j(x) with orthonormal basis functions
- Relevance: Formally establishes f(·) as basis function expansion → KAN B-splines

**Van Mulders et al. - Localized Nonlinearity (2013)** Automatica
- Core: Distinguishes global vs localized nonlinearity in systems
- Key: Wiener model nonlinearity is global (affects all frequency components)
- Relevance: KAN B-spline captures global nonlinear features effectively

**Li et al. - LSTM-based Wiener Model (2024)** MSSP
- Core: LSTM replaces traditional linear filter G(z) in Wiener structure
- Key: Validates "deep learning + Wiener structure" compatibility
- Relevance: **Direct support** for replacing LSTM with KAN in Wiener-KAN

### Frequency Domain Loss

**Jiang et al. - Focal Frequency Loss (2020)** ICCV 2021 arXiv:2012.12821
- Core: First adaptive frequency focusing loss
- Note: AFMAE NOT FOUND - FFL is verified theory basis

**Wang et al. - SAMFre (2025)** arXiv:2505.17532
- Core: FFT + Sharpness-Aware Minimization for frequency domain loss
- Formula: loss = alpha x |FFT(pred) - FFT(real)|_1 + (1-alpha) x MSE
- Quote: SAM improves generalization in frequency domain
- Relevance: Direct reference for AFMAE loss function design

**Chakraborty et al. - BSP Loss for Chaotic Systems (2025)** arXiv:2502.00472
- Core: Binned Spectral Power Loss - penalizes energy distribution across wavenumber bins
- Formula: L_BSP = (1/N_k)·Σ_c Σ_i (1 - (E^bin_u+ε)/(E^bin_v+ε))²
- Result: Significantly improves stability in Kolmogorov Flow, 2D/3D turbulence
- Relevance: Frequency domain loss with binned energy approach

**He et al. - FIRE: Unified Frequency Domain (2025)** arXiv:2510.10145
- Core: Unified framework with independent amplitude/phase modeling
- Formula: FFT Loss: L_fft = (1/N_f)·Σ_k |FFT(X_true) - FFT(X_out)|
- Result: Outperforms SOTA on ETTh1/2, ETTm1/2, Weather datasets
- Relevance: FFT-domain loss as core component with strong experimental validation

**Sun et al. - FreLE: Low-Frequency Spectral Bias (2025)** arXiv:2510.25800
- Core: Addresses spectral bias - NNs fit low-frequency first then high-frequency
- Formula: L_total = δ·L^y + (1-δ)·L^t where L^y = (1/n)Σ||ℱ(X_i) - ℱ_θ(X̂_i)||
- Key: Explicit + implicit frequency regularization; local maxima detection
- Result: Ranks #1 on 38/56 benchmarks vs DLinear, FITS, Autoformer, Transformer
- Relevance: **Direct support** for AFMAE frequency domain loss design; addresses low-frequency drift

## P1 - Applied Technology

### Drift Compensation

**Zhang et al. - TDACNN (2022)** arXiv:2110.07509
- Core: Target-domain-free CNN for sensor drift

**Lin, Zhan - KD E-nose (2025)** arXiv:2507.17071
- Core: First knowledge distillation for drift compensation

**ChakraVarthy et al. - ML-enhanced ECG Drift Calibration (2026)**
- DOI: 10.1080/00032719.2026.2618976
- Core: ML-enhanced calibration for electrochemical environmental monitoring
- Relevance: High - electrochemical sensor drift compensation

**Li et al. - ML for Electrochemical Sensors Review (2025)**
- DOI: 10.1016/j.trac.2025.128XXX (TrAC)
- Core: Comprehensive review of ML for electrochemical sensors
- Relevance: High - direct coverage of ML drift compensation for electrochemical sensors

**Badawi et al. - Deep NN Hadamard for Chemical Sensor Drift (2021)** IEEE 9442748
- Core: Hadamard transform deep network, TCNN for drift estimation
- Result: TCNN outperforms RNN for sensor drift compensation
- Relevance: High - chemical sensor drift + deep learning

**Zhang, Zhang - Domain Adaptation ELM for E-nose (2014)** IEEE 6963383
- Core: Domain Adaptation Extreme Learning Machine
- Citation: 373 citations (foundational work)
- Relevance: High - E-nose drift, domain adaptation methodology

**Liang et al. - OTTA-DriftNet (2025)** IEEE 11087654
- Core: Online Test-Time Adaptive Drift Compensation Network
- Relevance: Medium-High - E-nose drift, online adaptation

**Shi et al. - EEMD-GRNN for MEMS Sensor Drift (2022)** Sensors 22(14), 5225
- Core: EEMD (Ensemble Empirical Mode Decomposition) + GRNN for drift modeling
- Result: Displacement accuracy 95.64% → 98.00% after compensation
- Relevance: **High** - Complete drift compensation framework (preprocessing + modeling)
- Note: EEMD can separate noise from drift components; GRNN models drift dynamics

**Wei, Liu - BP NN for MEMS Accelerometer Drift (2024)** RSI 95(11), 115107
- Core: BP NN + tent chaotic mapping + sparrow search algorithm
- Relevance: Low - MEMS accelerometer (not electrochemical)

**Pawase, Futane - ANN for MEMS Seismic Sensor Drift (2018)** IJSIS
- Core: ANN + FPAA hardware implementation
- Result: Frequency drift reduced from 3.68% to 0.64%
- Relevance: Low - MEMS seismic sensor (not electrochemical)

### Architecture Efficiency

**Yin et al. - CNN vs RNN (2017)** arXiv:1702.01923
- Core: Comparative study of CNN and RNN architectures
- Quote: CNNs achieve O(1) sequential complexity vs RNNs O(n)
- Relevance: Supports KAN vs LSTM/GRU efficiency argument

**Xie, Zhang - Deep Filtering (2021)** arXiv:2112.12616
- Core: Depthwise separable convolutions for efficiency
- Quote: 60-70pct computation reduction with comparable performance
- Relevance: Efficient architecture design reference

**Geras et al. - LSTM + CNN (2015)** arXiv:1511.06433
- Core: CNN preprocessing reduces LSTM computational burden
- Quote: 3-5x inference speedup from CNN+LSTM hybrid
- Relevance: Hybrid architecture efficiency proof

**Bai et al. - TCN: CNN vs RNN for Sequence (2018)** arXiv:1803.01271
- Core: Systematic comparison CNN vs RNN (LSTM) on sequence benchmarks
- Key: CNN O(1) receptive field vs RNN O(n) sequential dependency
- Result: CNNs show longer effective memory, outperform LSTM on audio synthesis
- Relevance: Strong evidence for CNN vs RNN efficiency comparison

**Lee et al. - Recurrent Additive Networks (2017)** arXiv:1705.07393
- Core: Gated RNN with purely additive latent state updates
- Finding: Simplified RNN architecture can match LSTM performance
- Relevance: Supports efficiency argument for simplified architectures

## Literature Gaps

| Gap | Status |
|-----|--------|
| AFMAE source | NOT FOUND - use FreLE, FFL as theory basis |
| KAN vs LSTM/GRU | CONFLICTING: TKAN/GRU-KAN support, Ali 2025 contradicts |
| KANet FLOPs | PAYWALLED - IEEE TIM cannot verify |
| Beintema vs Cruz | Potential benchmark conflict |

## Pending Verification

**Yang, Wang - KAT (2024)** arXiv:2409.10594
- Status: Pending - KAN+Transformer hybrid, needs deeper analysis

**Yamak et al. - KAN Time Series Review (2025)** DOI: 10.1007/s10586-025-05574-9
- Status: Pending - Springer subscription required

**Zhou et al. - LSTM for Seabed Deformation (2025)** IEEE 11122349
- Status: PENDING - Paywalled, cannot verify

## Analysis Report Reference
- docs/research/literature/20260328/STEP2_Deep_Analysis.md (Round 2)
- docs/research/literature/20260328/STEP2_Round3_Analysis.md (Round 3)
