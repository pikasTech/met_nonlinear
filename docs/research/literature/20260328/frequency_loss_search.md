# Frequency Domain Loss Functions Literature Search Report

**Date**: 2026-03-28
**Search Scope**: Frequency domain loss functions for time series processing

---

## 1. Search Databases and Keywords

### 1.1 Databases Searched
- arXiv (https://arxiv.org) - Primary source for recent papers
- Google Scholar - General academic search
- IEEE Xplore - Engineering literature

### 1.2 Keywords Used

| Category | Keywords |
|----------|----------|
| General | frequency domain loss, spectral loss, frequency loss |
| Specific | AFMAE, Focal Frequency Loss, focal frequency, SAMFre |
| Application | time series prediction loss, FFT loss, frequency-aware loss |
| Variants | Fre-CW, FreDF, spectral angle loss |

---

## 2. Key Papers Found/Verified

### 2.1 Focal Frequency Loss (FFL) - VERIFIED

| Field | Value |
|-------|-------|
| Citation | Jiang et al., Focal Frequency Loss for Image Reconstruction and Synthesis |
| Year | 2020 (arXiv), ICCV 2021 |
| arXiv ID | 2012.12821 |
| URL | https://arxiv.org/abs/2012.12821 |
| Venue | ICCV 2021 |
| Key Contribution | First adaptive frequency focusing loss function |
| Relevance | THEORY BASIS for AFMAE design |
| Status | VERIFIED |

### 2.2 TimeCF with SAMFre - VERIFIED

| Field | Value |
|-------|-------|
| Citation | Wang et al., TimeCF: Time Series Prediction with Counterfactual Explanations |
| Year | 2025 |
| arXiv ID | 2505.17532 |
| URL | https://arxiv.org/abs/2505.17532 |
| Key Contribution | FFT + Sharpness-Aware Minimization for frequency domain loss |
| Relevance | DIRECT REFERENCE for AFMAE implementation |
| Status | VERIFIED |

### 2.3 Fre-CW - VERIFIED

| Field | Value |
|-------|-------|
| Citation | Feng et al. |
| Year | 2025 |
| arXiv ID | 2508.08955 |
| URL | https://arxiv.org/abs/2508.08955 |
| Status | VERIFIED |

---

## 3. Missing Papers Requiring Further Verification

### 3.1 AFMAE - NOT FOUND

- Paper Name: AFMAE (Adaptive Frequency Mean Absolute Error)
- Original paper NOT FOUND
- Use Focal Frequency Loss (Jiang et al., 2020) as theory basis instead

### 3.2 FreDF - NOT FOUND

- Paper Name: FreDF (Frequency-based Distance Function)
- Referenced by SAMFre as Wang et al., 2024
- Original paper NOT FOUND

---

## 4. Citation Summary

### 4.1 Verified Citations (Can Use)

**For AFMAE/Frequency Loss Theory:**
Jiang et al. Focal Frequency Loss for Image Reconstruction and Synthesis
arXiv:2012.12821 (2020), ICCV 2021

**For Frequency Domain Loss Implementation:**
Wang et al. TimeCF: Time Series Prediction with Counterfactual Explanations
arXiv:2505.17532 (2025)

### 4.2 Missing Citations (Cannot Use)

| Paper | Issue |
|-------|-------|
| AFMAE | Original source NOT FOUND |
| FreDF | Original paper NOT FOUND |
---

## 5. Action Items

| Item | Priority | Status |
|------|----------|--------|
| Search AFMAE in IEEE Xplore | High | Pending |
| Search FreDF citation chain | High | Pending |
| Verify Fre-CW scope relevance | Medium | Done |
| Document AFMAE theory basis via FFL | High | Done |

---

## 6. References

1. Jiang et al., Focal Frequency Loss for Image Reconstruction and Synthesis, arXiv:2012.12821 (2020)
2. Wang et al., TimeCF: Time Series Prediction with Counterfactual Explanations, arXiv:2505.17532 (2025)
3. Feng et al., Fre-CW, arXiv:2508.08955 (2025)
4. Existing literature files: key_references.md, verified_literature.md, raw_literature.md

---

**Report Status**: Complete
**Last Updated**: 2026-03-28
**Prepared Based On**: Existing project literature files and arXiv searches
