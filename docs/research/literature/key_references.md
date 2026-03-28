# Key References

**Status**: STEP3 Updated (2026-03-28 Round 3)
**Based on**: verified_literature.md (STEP2 Round 2 + Round 3, 2026-03-28)
**Purpose**: Core literature supporting second draft claims per IDEA.md
**Supersedes**: All previous versions

### Round 3 Additions
- TFKAN (Kui 2025) - First KAN in frequency domain
- TimeKAN (Huang 2025) - KAN + frequency decomposition SOTA
- KAN Survey (Somvanshi 2025) - validates KAN+RNN hybrid trend
- Schoukens 2009 - Classical Wiener-Hammerstein benchmark
- Haber 1990 - Wiener structure identification survey
- Bai-Giri 2010 - Block-oriented nonlinear systems foundation
- Li 2024 - LSTM-Wiener deep learning validation
- Shi 2022 EEMD-GRNN - Complete drift compensation framework
- Sun 2025 FreLE - Spectral bias correction, direct AFMAE support

---

## P0 - Wiener-KAN Architecture (Core Claim: Modeling & Compensation Unification)

| Priority | Paper | Key Contribution | For Paper Claim |
|----------|-------|------------------|-----------------|
| **P0** | Cruz et al. 2025 SS-KAN (arXiv:2506.16392) | SS-KAN = linear state-space + KAN nonlinearity | **Direct foundation**: Wiener linear part ↔ RNN, Wiener nonlinearity ↔ KAN |
| **P0** | Manavalan, Tronarp 2026 Barron-Wiener-Laguerre (arXiv:2602.13098) | Barron space + linear dynamics + Laguerre bases | Convergence rates; dimension-independent bounds for Wiener-class |
| **P0** | Liu et al. 2024 KAN (arXiv:2404.19756) | B-spline on edges, LUT-based computation | KAN replaces Wiener static nonlinearity; LUT enables efficient inference |
| **P0** | Genet, Inzirillo 2024 TKAN (arXiv:2405.07344) | KAN + LSTM gating for memory | **Validates KAN+RNN combination**: TKAN > GRU > LSTM for multi-step ahead |
| **P0** | Rather et al. 2025 KAN-GRU Hybrid (arXiv:2507.13685) | GRU-KAN/LSTM-KAN architectures | **Hybrid > LSTM/GRU/LSTM-Attention/LSTM-Transformer** |
| **P0** | Kui et al. 2025 TFKAN (arXiv:2506.12696) | **First KAN in frequency domain**; dual-branch FreqKAN + TimeKAN | **Direct support**: Wiener linear(nonlinear separation via dual-branch architecture |
| **P0** | Schoukens, Ljung 2009 WH Benchmark (diva-portal) | G1(z)→f(·)→G2(z) standard benchmark; 157+ citations | **Classical foundation**: establishes Wiener block decomposition formally |
| **P0** | Haber, Unbehauen 1990 Structure Identification (Automatica) | "Wiener = linear dynamic system + static nonlinear element"; 500+ citations | **Core theoretical basis** |
| **P0** | Bai, Giri 2010 Block-oriented Systems (Springer) | f(x) = Σc_jφ_j(x) with orthonormal basis | **Foundation**: KAN B-splines = learnable basis functions for f(·) |
| **P0** | Li et al. 2024 LSTM-Wiener (MSSP) | LSTM replaces traditional G(z) in Wiener structure | **Direct support**: deep learning + Wiener structure compatibility |
| **P0** | Huang et al. 2025 TimeKAN (arXiv:2502.06910) | KAN + cascade frequency decomposition; O(L log L) | SOTA on ETTh/ETTm/Weather; validates frequency-aware KAN |

---

## P0 - Frequency Domain Loss (Core Claim: AFMAE Training Method)

| Priority | Paper | Key Contribution | For Paper Claim |
|----------|-------|------------------|-----------------|
| **P0** | Jiang et al. 2021 FFL (arXiv:2012.12821) | Focal Frequency Loss - adaptive frequency focusing | **Theory basis** for frequency-domain MAE; AFMAE conceptual predecessor |
| **P0** | Wang et al. 2025 SAMFre (arXiv:2505.17532) | FFT loss + Sharpness-Aware Minimization | Formula: `α·|FFT(pred)-FFT(real)|₁ + (1-α)·MSE`; validates frequency-domain loss design |
| **P0** | He et al. 2025 FIRE (arXiv:2510.10145) | Unified FFT-domain loss framework | `L_fft = (1/N_f)·Σ|FFT(X_true)-FFT(X_out)|`; outperforms SOTA on ETTh/ETTm/Weather |
| **P0** | Sun et al. 2025 FreLE (arXiv:2510.25800) | Low-Frequency Spectral Bias correction | **Direct support**: addresses NN priority fitting low-freq first; #1 on 38/56 benchmarks |

---

## P1 - KAN Efficiency (Supporting Claim: KAN LUT Efficiency)

| Priority | Paper | Key Contribution | For Paper Claim |
|----------|-------|------------------|-----------------|
| **P1** | Qiu et al. 2024 PowerMLP (arXiv:2412.13571) | Efficient KAN alternative | KAN 10x slower than MLP; KAN FLOPs >10x PowerMLP (confirms KAN efficiency bottleneck) |
| **P1** | Lee et al. 2024 HiPPO-KAN (arXiv:2410.14939) | Constant parameter efficiency | Parameter count constant regardless of window size; outperforms KAN at larger windows |
| **P1** | Vaca-Rubio et al. 2024 KAN for Time Series (arXiv:2405.08790) | KAN vs MLP comparison | KAN (109k) outperforms MLP (329k) by 17% MSE; fewer parameters |

---

## P1 - RNN vs CNN Efficiency (Supporting Claim: RNN > 1D-CNN)

| Priority | Paper | Key Contribution | For Paper Claim |
|----------|-------|------------------|-----------------|
| **P1** | Yin et al. 2017 CNN vs RNN (arXiv:1702.01923) | Systematic comparison | CNN O(1) sequential complexity vs RNN O(n); RNN fewer params than 1D-CNN |
| **P1** | Bai et al. 2018 TCN (arXiv:1803.01271) | CNN vs RNN on sequence benchmarks | CNN O(1) receptive field vs RNN O(n); CNN longer effective memory |
| **P1** | Miller, Hardt 2018 Stable RNN (arXiv:1805.10369) | RNN stability theory | Theoretical foundation for stable RNN dynamics |

---

## P1 - Drift Compensation (Supporting Related Work Chapter)

| Priority | Paper | Key Contribution | For Paper Claim |
|----------|-------|------------------|-----------------|
| **P1** | Zhang et al. 2022 TDACNN (arXiv:2110.07509) | Target-domain-free CNN for sensor drift | Deep learning for sensor drift (related work) |
| **P1** | Lin, Zhan 2025 KD E-nose (arXiv:2507.17071) | Knowledge distillation for drift | Transfer learning for drift compensation |
| **P1** | Li et al. 2025 ML E-chem Review (TrAC) | Comprehensive ML for electrochemical sensors | **Direct coverage**: ML drift compensation for electrochemical sensors |
| **P1** | ChakraVarthy et al. 2026 ML-enhanced ECG (DOI: 10.1080/00032719.2026.2618976) | ML for electrochemical monitoring drift | Electrochemical environmental monitoring drift |
| **P1** | Badawi et al. 2021 Hadamard TCNN (IEEE 9442748) | TCNN for chemical sensor drift | TCNN outperforms RNN for sensor drift |
| **P1** | Zhang, Zhang 2014 ELM E-nose (IEEE 6963383) | Domain adaptation ELM | 373 citations; foundational E-nose drift method |
| **P1** | Shi et al. 2022 EEMD-GRNN (Sensors) | EEMD + GRNN for MEMS drift; displacement 95.64%→98.00% | Complete drift compensation framework (preprocessing + modeling) |

---

## Reviewer Response Mapping

| Reviewer | Claim | Supporting Literature | Gap |
|----------|-------|----------------------|-----|
| R3-4 | CNN/Transformer/RNN comparison | Yin 2017 (CNN vs RNN), TKAN/GRU-KAN (KAN+RNN hybrid) | **Transformer NOT FOUND** - use KAN-GRU hybrid (Rather 2025) outperforms LSTM-Transformer as alternative |
| R3-5 | RVTDCNN PA linearization | **NOT FOUND** | Cannot support; recommend removing claim |
| R3-6 | Dataset construction | Li 2025 (E-chem dataset desc), Zhang 2022 (dataset details) | Use internal dataset description |
| R4-1 | Activation function comparison | Liu 2024 (B-spline), Qiu 2024 (KAN bottleneck) | Supported |
| R4-8 | Computational cost analysis | Yin 2017, Bai TCN, Qiu 2024, HiPPO-KAN (Lee 2024) | Supported |

### R3-4 Transformer Response
**Literature does not support direct Transformer comparison** for Wiener-KAN. However, Rather et al. [2025] demonstrates GRU-KAN hybrid outperforms LSTM-Attention and LSTM-Transformer, providing indirect validation that KAN-based approaches are competitive with Transformer-based methods.

---

## Literature Gaps (Cannot Support)

| Gap | Status | Recommendation |
|-----|--------|----------------|
| AFMAE original source | NOT FOUND | Use FFL (Jiang 2021), SAMFre (Wang 2025), FIRE (He 2025), FreLE (Sun 2025) as theory basis |
| Transformer for time series | NOT FOUND | Replace with KAN-GRU hybrid (Rather 2025) which outperforms LSTM-Transformer |
| RVTDCNN PA linearization | NOT FOUND | Remove claim; not critical to paper contribution |
| Beintema vs Cruz benchmark | POTENTIAL CONFLICT | Avoid direct benchmark comparison; focus on MET application |
| KANet FLOPs paper | PAYWALLED (IEEE TIM) | Cannot verify; remove quantitative FLOPs claim |
| KAN 2.0 | Different goal | Excluded per STEP2 analysis |

---

## Discarded Claims (per IDEA.md Second Draft)

- ~~PIKAN physical constraints~~ → Discontinued
- ~~FRIRNN frequency injection~~ → Discontinued  
- ~~Accuracy improvement vs LSTM/GRU~~ → Changed to efficiency focus
- ~~Generalization/extrapolation~~ → Discontinued

---

## Documents Referenced

- `docs/research/literature/verified_literature.md` (STEP2 Round 2 + Round 3, 2026-03-28)
- `docs/research/literature/20260328/STEP2_Deep_Analysis.md` (Round 2 analysis)
- `docs/research/literature/20260328/STEP2_Round3_Analysis.md` (Round 3 analysis)
- `docs/FRIKAN_REJECT.md`
- `docs/IDEA.md`

**STEP3 Round 3 Decision**: Added 9 papers from Round 3 analysis (TFKAN, TimeKAN, KAN Survey, Schoukens 2009, Haber 1990, Bai-Giri 2010, Li 2024, Shi 2022, Sun 2025). Focus shifted to KAN-GRU hybrid (Rather 2025) instead of pure KAN to address Ali 2025 conflict. TFKAN provides direct support for Wiener dual-branch (linear/nonlinear separation) architecture.
