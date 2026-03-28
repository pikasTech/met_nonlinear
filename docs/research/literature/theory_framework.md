# Theory Framework

**Status**: STEP3 Updated (2026-03-28 Round 3)
**Based on**: verified_literature.md (STEP2 Round 2 + Round 3, 2026-03-28)
**Purpose**: Theoretical foundation for Wiener-KAN architecture claims

---

## 1. Wiener-KAN Architecture Theory

### 1.1 Core Concept: Block Decomposition

Wiener model = **linear dynamic component** (RNN) + **static nonlinear component** (KAN)

This decomposition is theoretically grounded:
- **Barron space theory** (Manavalan & Tronarp 2026): Dimension-independent convergence rates
- **Kolmogorov-Arnold theorem** (Liu et al. 2024): Univariate functions suffice for approximation
- **Stability theory** (Revay & Manchester 2021): Contracting dynamics guarantees

### 1.2 Classical Wiener Theory (Foundational)

| Paper | Contribution | Relevance |
|-------|--------------|-----------|
| Schoukens & Ljung 2009 WH Benchmark | G1(z)→f(·)→G2(z) standard benchmark; 157+ citations | **Classical foundation** |
| Haber & Unbehauen 1990 Structure Identification | "Wiener = linear dynamic + static nonlinear"; 500+ citations | **Core basis** |
| Bai & Giri 2010 Block-oriented Systems | f(x) = Σc_jφ_j(x) with orthonormal basis | **KAN B-splines = learnable basis** |
| Van Mulders et al. 2013 | Wiener nonlinearity is global (affects all freq components) | KAN captures global features |

### 1.3 Deep Learning Validation

| Paper | Contribution | Relevance |
|-------|--------------|-----------|
| Cruz et al. 2025 SS-KAN | SS-KAN = linear state-space + KAN for Wiener-Hammerstein | **Direct foundation** |
| Manavalan & Tronarp 2026 Barron-Wiener-Laguerre | Linear dynamics (Laguerre) + Barron space nonlinearity | Convergence rates |
| Li et al. 2024 LSTM-Wiener | LSTM replaces G(z) in Wiener structure | **Direct support**: deep learning + Wiener |
| Liu et al. 2024 KAN | KAN replaces static nonlinearity with B-spline on edges | KAN理论基础 |
| Revay 2021 REN | RNN-based Wiener/Hammerstein with stability guarantees | Stability theory |

### 1.3 Why KAN for Nonlinearity?

- **KAN** (Liu 2024): B-spline activation = O(1) LUT lookup, no matrix-vector multiplication
- **Traditional Wiener**: Polynomial nonlinearities require high-order terms
- **Advantage**: KAN可训练且自适应，比传统多项式非线性更具灵活性

---

## 2. KAN+RNN Hybrid: Empirical Validation

### 2.1 TKAN: KAN + LSTM Gating

**Genet & Inzirillo 2024**: TKAN = KAN layers + LSTM gating for memory management

Result: **TKAN (0.104 R²) > GRU (0.018) > LSTM (-0.473)** at 12-step ahead forecasting

Validates KAN+RNN combination for temporal modeling.

### 2.2 KAN-GRU/LSTM Hybrid: State-of-the-Art

**Rather et al. 2025**: GRU-KAN and LSTM-KAN architectures

- 3-month prediction >92% accuracy
- 8-month prediction >88% accuracy
- **Outperforms**: LSTM, GRU, LSTM-Attention, LSTM-Transformer

This directly supports Wiener-KAN's KAN+RNN architecture choice.

### 2.3 TFKAN: First KAN in Frequency Domain

**Kui et al. 2025**: Dual-branch architecture (FreqKAN + TimeKAN)

- **First work to directly apply KAN in the frequency domain**
- Quote: "To the best of our knowledge, this is the first work to directly apply KAN in the frequency domain"
- **Directly supports**: Wiener linear(nonlinear separation via dual-branch architecture

### 2.4 TimeKAN: KAN + Frequency Decomposition

**Huang et al. 2025**: Cascade Frequency Decomposition + Multi-order KAN

- O(L log L) complexity via FFT, Chebyshev polynomials
- SOTA on ETTh1/2, ETTm1/2, Weather, Electricity datasets
- Validates frequency-aware KAN for time series

### 2.5 ⚠️ Conflict: Ali (2025) KAN vs LSTM

**Ali et al. 2025** find LSTM outperforms pure KAN in stock prediction.

**Resolution for Wiener-KAN claims**:
1. Focus on **KAN-GRU hybrid architecture** (Rather 2025 shows hybrid > pure LSTM/GRU)
2. Emphasize **parameter efficiency** rather than raw accuracy
3. Context: MET application-specific advantages

---

## 3. Frequency Domain Loss: Theoretical Basis

### 3.1 AFMAE Conceptual Framework

AFMAE = frequency-domain Mean Absolute Error:

```
L_AFMAE = α · |FFT(pred) - FFT(real)|₁ + (1-α) · MAE
```

### 3.2 Theory Sources

| Paper | Contribution | For AFMAE |
|-------|--------------|-----------|
| Jiang et al. 2021 FFL | Focal Frequency Loss - adaptive frequency focusing | **Primary theory basis** |
| Wang et al. 2025 SAMFre | loss = α × |FFT(pred) - FFT(real)|₁ + (1-α) × MSE | Direct formula reference |
| He et al. 2025 FIRE | Unified FFT-domain loss framework | Validates FFT loss effectiveness |
| **Sun et al. 2025 FreLE** | Low-Frequency Spectral Bias correction | **Direct support**: addresses NN priority fitting low-freq first; #1 on 38/56 benchmarks |
| Chakraborty 2025 BSP | Binned Spectral Power Loss | Alternative frequency bin approach |

### 3.3 Note on AFMAE Source

**AFMAE appears to be an internal project term**, not an established academic term. No original AFMAE paper exists. Use the above sources (FFL, SAMFre, FIRE, FreLE) as theoretical justification instead of citing "AFMAE" as a standalone method. FreLE (Sun 2025) is particularly relevant as it directly addresses spectral bias correction, which is critical for MET low-frequency drift compensation.

---

## 4. Efficiency Claims: Literature Support

### 4.1 KAN LUT Efficiency

**Qiu et al. 2024 PowerMLP** confirms KAN computational bottleneck:
- KAN 10x slower than MLP
- KAN FLOPs >10x PowerMLP
- **Claim focus**: KAN效率优势在于参数效率，而非原始速度

**Lee et al. 2024 HiPPO-KAN** provides efficiency solution:
- Parameter count constant regardless of window size
- Addresses KAN's "lag problem" at larger window sizes

### 4.2 RNN vs CNN Efficiency

**Yin et al. 2017**:
- CNN: O(1) sequential complexity per step, but more parameters
- RNN: O(n) sequential dependency, but fewer parameters
- **Key point**: RNN has fewer parameters than 1D-CNN

**Bai et al. 2018 TCN**:
- CNN achieves longer effective memory than LSTM
- Simple CNN architectures outperform LSTM on audio synthesis

---

## 5. Deep Learning Drift Compensation: Related Work Context

### 5.1 Sensor Drift Compensation Methods

| Method | Paper | Key Finding |
|--------|-------|-------------|
| TDACNN | Zhang et al. 2022 | Target-domain-free CNN for sensor drift |
| Knowledge Distillation | Lin, Zhan 2025 | First knowledge distillation for drift compensation |
| TCNN | Badawi et al. 2021 | TCNN outperforms RNN for chemical sensor drift |
| Domain Adaptation ELM | Zhang & Zhang 2014 | 373 citations; foundational E-nose drift method |
| OTTA-DriftNet | Liang et al. 2025 | Online test-time adaptive drift compensation |

### 5.2 Electrochemical Sensor Context

| Paper | Contribution |
|-------|--------------|
| Li et al. 2025 (TrAC) | Comprehensive review: ML for electrochemical sensors |
| ChakraVarthy et al. 2026 | ML-enhanced calibration for electrochemical monitoring |
| **Shi et al. 2022 EEMD-GRNN** | Complete drift framework: EEMD (noise/drift separation) + GRNN (drift modeling); displacement 95.64%→98.00% |

### 5.3 Comparison with Wiener-KAN Approach

| Approach | Method | Advantage |
|----------|--------|----------|
| Zhang 2022 | Domain adaptation | No labeled target data needed |
| Lin 2025 | Transfer learning | Knowledge distillation |
| **Ours** | Direct nonlinear dynamics modeling | No domain adaptation; unified modeling + compensation |

---

## 6. Second Draft Claims - Literature Support Status

| Claim | Supporting Literature | Status |
|-------|----------------------|--------|
| Wiener-KAN architecture | Cruz SS-KAN, Manavalan Barron-Wiener, TFKAN | **SUPPORTED** |
| Wiener classical theory | Schoukens 2009, Haber 1990, Bai-Giri 2010 | **SUPPORTED** |
| Wiener linear ↔ RNN | Revay 2021, Miller 2018, Yin 2017 | **SUPPORTED** |
| Wiener nonlinear ↔ KAN | Liu 2024, Cruz 2025, Li 2024 LSTM-Wiener | **SUPPORTED** |
| KAN+RNN hybrid validity | TKAN (Genet 2024), KAN-GRU (Rather 2025), TFKAN, TimeKAN | **SUPPORTED** |
| KAN-GRU > pure LSTM/GRU | Rather 2025 | **SUPPORTED** |
| KAN in frequency domain | TFKAN (first KAN in freq domain) | **SUPPORTED** |
| KAN LUT parameter efficiency | HiPPO-KAN (Lee 2024), KAN vs MLP (Vaca-Rubio 2024) | **SUPPORTED** |
| RNN fewer params than 1D-CNN | Yin 2017, Bai TCN | **SUPPORTED** |
| AFMAE frequency-domain loss | Jiang 2021 FFL, Wang 2025 SAMFre, FIRE, FreLE | **SUPPORTED (theory)** |
| Deep learning drift comp | Zhang 2022, Lin 2025, Li 2025, Shi 2022 EEMD-GRNN | **SUPPORTED** |

---

## 7. Claims NOT Supported / Discontinued

| Claim | Reason | Action |
|-------|--------|--------|
| PIKAN physical constraints | Discontinued per IDEA.md | Remove from paper |
| FRIRNN frequency injection | Discontinued per IDEA.md | Remove from paper |
| Accuracy improvement vs LSTM/GRU | Not supported by data | Change to efficiency focus |
| Generalization/extrapolation | No evidence | Discontinue |
| RVTDCNN PA linearization | NOT FOUND in literature | Cannot support; remove claim |
| Transformer comparison | NOT FOUND relevant | Replace with KAN-GRU hybrid |

---

## 8. Literature Gaps Requiring Attention

| Gap | Impact on Paper | Recommendation |
|-----|----------------|----------------|
| AFMAE original source | Must cite FFL/SAMFre/FIRE/FreLE | State AFMAE is based on focal frequency loss principles |
| KAN vs pure LSTM | Ali 2025 contradicts | Focus on KAN-GRU hybrid, not pure KAN |
| Transformer comparison | R3-4 cannot support | Use KAN-GRU hybrid (Rather 2025) which outperforms LSTM-Transformer |
| RVTDCNN PA linearization | R3-5 cannot support | Remove claim |
| Dataset construction | R3-6 must use internal | Describe MET dataset following standard practices |
| KANet FLOPs | Cannot verify | Remove quantitative FLOPs claim |

---

## Documents Referenced

- `docs/research/literature/verified_literature.md` (STEP2 Round 2 + Round 3, 2026-03-28)
- `docs/research/literature/20260328/STEP2_Deep_Analysis.md` (Round 2 analysis)
- `docs/research/literature/20260328/STEP2_Round3_Analysis.md` (Round 3 analysis)
- `docs/IDEA.md` (second draft strategy)
- `docs/FRIKAN_REJECT.md`

**Round 3 Updates**: Added TFKAN, TimeKAN, Schoukens 2009, Haber 1990, Bai-Giri 2010, Li 2024, Shi 2022 EEMD-GRNN, Sun 2025 FreLE to theoretical framework.
