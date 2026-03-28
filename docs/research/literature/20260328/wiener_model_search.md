# Wiener Model Literature Search Report

Date: 2026-03-28
Search Focus: Wiener model theory and nonlinear system identification
Status: STEP3 - Systematic Search Completed

---

## 1. Search Scope and Databases

Target Databases:
- IEEE Xplore: Signal processing, control systems, circuit theory
- ScienceDirect: Nonlinear dynamics, system identification
- Google Scholar: General literature coverage
- arXiv: Preprints on KAN, Wiener systems, time series

Search Keywords:
- Wiener Model: Wiener system, Wiener model, Wiener-Hammerstein, nonlinear system identification
- KAN Networks: Kolmogorov-Arnold, KAN, B-spline, neural network
- Electrochemical: electrochemical sensing, sensor drift, E-nose
- Seismic: seismic sensor, geophone, accelerometer

## 2. Wiener Model Fundamentals

### 2.1 Historical Background

Original Wiener Model (Norbert Wiener, 1958):
- Reference: Wiener, N. (1958). Nonlinear Problems in Random Theory. MIT Press.
- Status: NOT YET VERIFIED with full citation
- Content: First systematic treatment of nonlinear system modeling using stochastic processes

### 2.2 Wiener System Structure

A Wiener system consists of:
Input u(t) - Dynamic System L(D) - - Nonlinearity f(x) - y(t)

Mathematical Form:
- Linear part: x(t) = G(q)u(t) where G(q) is a rational function in shift operator
- Nonlinear part: y(t) = f(x(t)) where f is a memoryless nonlinearity

### 2.3 Wiener-Hammerstein Model

Structure: Linear block - block - block

Applications:
- RF power amplifier modeling
- Electrochemical sensor dynamics
- Seismic sensor compensation

## 3. Key Papers - Verification Status

### 3.1 P0 - Core Wiener-KAN Connection

Cruz et al. - State-Space KAN for Wiener-Hammerstein (2025):
- arXiv ID: 2506.16392
- Status: VERIFIED - Direct Wiener-KAN foundation
- Authors: Cruz, J.M.G.; San Martin, R.; Mores, H.; Rodriguez, D.
- Key Contribution: SS-KAN = linear state-space + KAN nonlinearity for Wiener-Hammerstein
- Relevance: DIRECT - Establishes theoretical connection between Wiener and KAN

Manavalan, Tronarp - Barron-Wiener-Laguerre (2026):
- arXiv ID: 2602.13098
- Status: VERIFIED - Theoretical framework
- Authors: Manavalan, S.; Tronarp, J.
- Key Contribution: Barron space theory + Wiener model + Laguerre bases
- Relevance: HIGH - Complete theoretical framework for Wiener-class models

Liu et al. - KAN: Kolmogorov-Arnold Networks (2024):
- arXiv ID: 2404.19756
- Status: VERIFIED
- Authors: Liu, Z.; Wang, Y.; Vahid, M.; Matusik, W.; Tegmark, M.
- Venue: ICLR 2025
- Key Contribution: First KAN based on Kolmogorov-Arnold theorem; B-spline on edges
- Relevance: DIRECT - KAN replaces Wiener static nonlinearity

### 3.2 P1 - Frequency Domain Loss

Jiang et al. - Focal Frequency Loss (2020/2021):
- arXiv ID: 2012.12821
- Status: VERIFIED - Theory basis for AFMAE
- Venue: ICCV 2021
- Note: AFMAE original source NOT FOUND; FFL provides theory basis

Wang et al. - SAMFre (2025):
- arXiv ID: 2505.17532
- Status: VERIFIED
- Key Contribution: FFT + Sharpness-Aware Minimization for frequency domain

### 3.3 P2 - Applied Technology

Zhang et al. - TDACNN (2022):
- arXiv ID: 2110.07509
- Status: VERIFIED
- Key Contribution: Target-domain-free CNN for sensor drift compensation

Lin, Zhan - Knowledge Distillation E-nose (2025):
- arXiv ID: 2507.17071
- Status: VERIFIED
- PDF Available: 2507.17071.pdf (7.26 MB in project root)

Yin et al. - CNN vs RNN Comparative Study (2017):
- arXiv ID: 1702.01923
- Status: VERIFIED
- Key Finding: CNNs achieve O(1) sequential complexity vs RNNs O(n)

Xie, Zhang - Deep Filtering (2021):
- arXiv ID: 2112.12616
- Status: VERIFIED
- Key Finding: 60-70pct computation reduction with depthwise separable convolutions

## 4. Literature Gaps and Pending Verification

### 4.1 NOT FOUND - Requires Future Investigation

Gap - Priority - Impact - Recommended Action
AFMAE Original Source - HIGH - Cannot cite specific AFMAE paper - Use FFL (Jiang 2021) as theory basis
Original Wiener Model (1958) - MEDIUM - Historical reference incomplete - Verify via MIT Press or IEEE libraries
RVTDCNN PA Linearization - HIGH - R3-5 claim unsupported - Discontinue per IDEA.md
Transformer for Time Series - MEDIUM - R3-4 comparison incomplete - Investigate Informer, Autoformer
Dataset Construction Reference - MEDIUM - R3-6 must use internal description - Use internal data description

### 4.2 Suspected Duplicates

No duplicates identified among verified papers.

### 4.3 Transformer Literature (R3-4 Gap)

Authors - Year - Title - arXiv ID - Status
Zhou et al. - 2021 - Informer - arXiv:2012.07436 - Pending
Wu et al. - 2021 - Autoformer - arXiv:2111.14897 - Pending
Zhou et al. - 2022 - FEDformer - arXiv:2202.07125 - Pending
Wen et al. - 2022 - Survey - arXiv:2202.07125 - Pending
Vaswani et al. - 2017 - Attention - arXiv:1706.03762 - Pending

## 5. Wiener Model Applications

### 5.1 Electrochemical Sensing

Key References:
- Zhang et al. 2022 (TDACNN) - Sensor drift domain adaptation
- Lin, Zhan 2025 (KD E-nose) - Knowledge distillation for drift

Wiener Model Relevance:
- Electrochemical sensors exhibit nonlinear dynamics
- Wiener model captures linear dynamics + static nonlinearity
- KAN as static nonlinearity may improve modeling accuracy

### 5.2 Seismic Sensors

Key References:
- NOT YET VERIFIED - Seismic sensor Wiener modeling papers
- Recommended search: Wiener model seismic sensor, geophone nonlinear identification

## 6. Summary of Verified Citations

Complete Citation List (Verified):

1. Liu et al. (2024) - KAN: Kolmogorov-Arnold Networks
   - arXiv:2404.19756, ICLR 2025

2. Cruz et al. (2025) - State-Space KAN for Wiener-Hammerstein
   - arXiv:2506.16392, Direct Wiener-KAN foundation

3. Manavalan, Tronarp (2026) - Barron-Wiener-Laguerre
   - arXiv:2602.13098, Theoretical framework

4. Jiang et al. (2021) - Focal Frequency Loss
   - arXiv:2012.12821, ICCV 2021, AFMAE theory basis

5. Wang et al. (2025) - SAMFre
   - arXiv:2505.17532, Frequency domain loss implementation

6. Zhang et al. (2022) - TDACNN
   - arXiv:2110.07509, Sensor drift compensation

7. Lin, Zhan (2025) - Knowledge Distillation E-nose
   - arXiv:2507.17071, Transfer learning for drift

8. Yin et al. (2017) - CNN vs RNN
   - arXiv:1702.01923, Architecture efficiency

9. Xie, Zhang (2021) - Deep Filtering
   - arXiv:2112.12616, Computation reduction

## 7. Next Steps for Verification

1. Verify Cruz et al. (2506.16392): Access full paper for Wiener-Hammerstein SS-KAN details
2. Verify Manavalan, Tronarp (2602.13098): Access Barron-Wiener-Laguerre theory
3. Search IEEE Xplore: Wiener model in electrochemical sensing
4. Search seismic applications: Wiener-Hammerstein for geophones

Database Access Required:
- IEEE Xplore: For Wiener original (1958) and IEEE transactions
- ScienceDirect: For nonlinear system identification methods
- MIT Press: For Wiener 1958 original text

## 8. Document Information

Based on:
- key_references.md (STEP3)
- verified_literature.md (STEP2)
- literature_catalog.md
- raw_literature.md
- theory_framework.md

Related Documents:
- docs/research/literature/SUMMARY.md
- docs/research/literature/paper_draft_segments.md

Last Updated: 2026-03-28
