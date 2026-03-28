# KAN (Kolmogorov-Arnold Networks) Literature Search Report

**Date**: 2026-03-28
**Search Scope**: arXiv, Google Scholar
**Keywords**: KAN, Kolmogorov-Arnold, spline, time series, efficiency

---

## 1. Executive Summary

This report documents literature search on KAN networks.

**Key Findings**:
- Original KAN paper (Liu et al., 2024) is well-verified
- TKAN extends KAN with recurrent mechanisms
- State-Space KAN provides direct theoretical foundation for Wiener-KAN

---

## 2. Key Papers

### KAN Original (Liu et al.)
- arXiv: 2404.19756
- Link: https://arxiv.org/abs/2404.19756

### TKAN (Genet, Inzirillo)
- arXiv: 2405.07344
- Link: https://arxiv.org/abs/2405.07344

### State-Space KAN (Cruz et al.) - CRITICAL
- arXiv: 2506.16392
- DOI: 10.1109/LCSYS.2025.3578019
- Link: https://arxiv.org/abs/2506.16392
- **DIRECT CONNECTION**: Validated on Wiener-Hammerstein benchmarks

### PowerMLP (Qiu et al.)
- arXiv: 2412.13571
- ~40x faster than original KAN

### KANEL_E (Hoang et al.)
- arXiv: 2512.12850
- Up to 2700x speedup on FPGA

---

## 3. Papers Summary Table

| Paper | Year | arXiv ID | Status |
|-------|------|----------|--------|
| KAN Original | 2024 | 2404.19756 | Verified |
| TKAN | 2024 | 2405.07344 | Verified |
| KAN Time Series | 2024 | 2405.08790 | Verified |
| PowerMLP | 2024 | 2412.13571 | Verified |
| KAN 2.0 | 2024 | 2408.10205 | Verified |
| State-Space KAN | 2025 | 2506.16392 | Verified |
| Barron-Wiener-Laguerre | 2026 | 2602.13098 | Verified |
| KANEL_E | 2025 | 2512.12850 | Verified |
| Hardware KAN Edge | 2024 | 2409.11418 | Verified |
| GRU-KAN/LSTM-KAN | 2025 | 2507.13685 | Verified |

---

## 4. Computational Efficiency Summary

| Architecture | Relative Speed | Notes |
|--------------|----------------|-------|
| MLP | 1x baseline | Fixed activations |
| Original KAN | ~10x slower | Iterative splines |
| PowerMLP | ~1x | ~40x faster than KAN |
| KANEL_E (FPGA) | Up to 2700x | LUT-based |

**Critical Quote**: KANs are usually 10x slower than MLPs (Liu et al. 2024)

---

## 5. Pending Verification

| Item | Status | Notes |
|------|--------|-------|
| AFMAE original | NOT FOUND | Use FFL instead |
| FreDF original | NOT FOUND | Referenced by SAMFre |

---

## 6. Relevance to Wiener-KAN

### Direct Connections
1. State-Space KAN - Wiener-Hammerstein validation
2. Barron-Wiener-Laguerre - Theoretical framework
3. TKAN - Temporal modeling for sensor drift

### Efficiency for SPICE
1. KANEL_E - LUT-based feasible for hardware
2. Hardware papers - Area/power tradeoffs
3. PowerMLP - 40x speedup path

---

## 7. References

1. Liu et al. (2024). KAN. arXiv:2404.19756
2. Genet, Inzirillo (2024). TKAN. arXiv:2405.07344
3. Cruz et al. (2025). SS-KAN. arXiv:2506.16392
4. Qiu et al. (2024). PowerMLP. arXiv:2412.13571
5. Hoang et al. (2025). KANEL_E. arXiv:2512.12850
6. Huang et al. (2024). Hardware KAN Edge. arXiv:2409.11418
7. Yang et al. (2025). GRU-KAN/LSTM-KAN. arXiv:2507.13685

---

**Status**: Complete
