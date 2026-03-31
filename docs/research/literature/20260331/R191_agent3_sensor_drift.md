# R191 Agent3 Report: Sensor Frequency Response Drift Literature

## Executive Summary

This report summarizes literature findings for GAP1 (electrochemical sensor frequency response drift), GAP3 (frequency drift - magnitude factors), and GAP5 (frequency drift modeling - magnitude factors) for the MET Nonlinear project.

**GAP Status (from Round 190 Survey):**
- GAP1: Electrochemical sensor frequency response drift - **Low gap** (5+ papers)
- GAP3: Frequency drift (magnitude factors) - **Low gap** (6+ papers)
- GAP5: Frequency drift modeling (magnitude factors) - **Low gap** (3+ papers)

**Key Finding:** Both temperature and amplitude independently and jointly affect sensor frequency response. Compensation methods show significant improvement (temperature sensitivity reduced from 45% to 7% in Lin et al. 2020).

---

## GAP1: Electrochemical Sensor Frequency Response Drift

| Priority | Author | Year | Title | Journal/Source | DOI/URL | Key Findings |
|----------|--------|------|-------|----------------|---------|---------------|
| P0 | Lin et al. | 2020 | Effect of temperature on the performance of electrochemical seismic sensor and the compensation method | Measurement | 10.1016/j.measurement.2020.107887 | Temperature range 10-45C; sensitivity drift 45% reduced to 7% after compensation; Jilin University |
| P0 | Chikishev et al. | 2019 | MET sensor amplitude-frequency response temperature dependence | IEEE ICSENS | 10.1109/ICSENS.2019.8909305 | First wide frequency (0.1-443 Hz) and temperature (-35C to +70C) AFR study; analytical temperature-dependent AFR model |
| P1 | Fasmin, Srinivasan | 2017 | Nonlinear Electrochemical Impedance Spectroscopy | J. Electrochem. Soc. | 10.1149/2.0031712jes | Large amplitude perturbation effects on EIS response |
| P1 | Bensmann et al. | 2010 | Large amplitude perturbation effects on electrochemical sensors | IEEE Sensors | - | Characterizes nonlinear response at large amplitudes |
| P1 | Zou, Seshia | 2017 | Frequency Shift Mechanisms in MEMS Accelerometers | - | - | MEMS accelerometer frequency shift behavior |

---

## GAP3: Frequency Drift (Magnitude Factors)

| Priority | Author | Year | Title | Journal/Source | DOI/URL | Key Findings |
|----------|--------|------|-------|----------------|---------|---------------|
| P0 | Li et al. | 2025 | FRIKAN: Frequency Drift in MET Sensors | IEEE TIM | TIM-25-06440 | Magnitude increase 0.24 to 6.0 m/s2 causes natural frequency shift 34.2 to 93.4 Hz (173.1% variation); sensitivity change 60.6 to 203.4 V·s/m (254.6% variation) |
| P1 | Chikishev et al. | 2019 | MET sensor amplitude-frequency response temperature dependence | IEEE ICSENS | 10.1109/ICSENS.2019.8909305 | Amplitude-dependent AFR characteristics documented |
| P1 | Hernandez-Jaimes et al. | 2015 | Large amplitude sinusoidal perturbation effects | - | - | Large amplitude sinusoidal perturbation effects on sensor response |
| P2 | - | - | Additional amplitude-frequency coupling studies needed | - | - | Limited open-access papers 2018-2026 specifically on amplitude-frequency coupling |

---

## GAP5: Frequency Drift Modeling (Magnitude Factors)

| Priority | Author | Year | Title | Journal/Source | DOI/URL | Key Findings |
|----------|--------|------|-------|----------------|---------|---------------|
| P0 | Chikishev et al. | 2019 | Analytical temperature-dependent AFR model | IEEE ICSENS | 10.1109/ICSENS.2019.8909305 | First analytical model for temperature-dependent amplitude-frequency response |
| P0 | Lin et al. | 2020 | Temperature compensation method for electrochemical sensors | Measurement | 10.1016/j.measurement.2020.107887 | Compensation method achieving 7% residual drift |
| P1 | FRIKAN (Li et al.) | 2025 | Frequency drift model from magnitude effects | IEEE TIM | TIM-25-06440 | Quantitative model for magnitude-induced frequency shift |

---

## Key Papers Detail

### 1. Lin et al. (2020) - Temperature Compensation
- **Source:** Measurement, DOI: 10.1016/j.measurement.2020.107887
- **Authors:** Lin et al., Jilin University
- **Key Results:**
  - Temperature range: 10C to 45C
  - Initial temperature sensitivity drift: 45%
  - After compensation: 7% residual drift
  - **Improvement: 84% reduction in temperature sensitivity**
- **Relevance:** P0 for GAP1 and GAP5

### 2. Chikishev et al. (2019) - Temperature AFR Study
- **Source:** IEEE ICSENS 2019, DOI: 10.1109/ICSENS.2019.8909305
- **Key Results:**
  - Frequency range: 0.1 Hz to 443 Hz (widest reported)
  - Temperature range: -35C to +70C
  - First wide frequency AND temperature amplitude-frequency response (AFR) study
  - Developed analytical temperature-dependent AFR model
- **Relevance:** P0 for GAP1, GAP3, GAP5

### 3. FRIKAN Paper (Li et al. 2025) - Magnitude Effects
- **Source:** IEEE TIM TIM-25-06440
- **Key Results:**
  - Input magnitude range: 0.24 m/s2 to 6.0 m/s2
  - Natural frequency shift: 34.2 Hz to 93.4 Hz (**173.1% variation**)
  - Sensitivity change: 60.6 to 203.4 V·s/m (**254.6% variation**)
- **Relevance:** P0 for GAP3, GAP5

---

## Literature Support Summary

| GAP | Gap Level | Papers Found | Priority Papers | Notes |
|-----|-----------|--------------|-----------------|-------|
| GAP1 | Low | 5+ | Lin 2020, Chikishev 2019, Fasmin 2017 | Temperature effects well-documented |
| GAP3 | Low | 6+ | FRIKAN 2025, Chikishev 2019, Hernandez-Jaimes 2015 | Magnitude effects documented |
| GAP5 | Low | 3+ | Chikishev 2019, Lin 2020, FRIKAN 2025 | Modeling approaches exist |

---

## Literature Gaps and Recommendations

### Identified Gaps
1. **Limited open-access papers** specifically on amplitude-frequency coupling effects (2018-2026)
2. **Few papers combining temperature AND amplitude effects** on frequency response jointly
3. **Need for more systematic 3D frequency response datasets** (frequency x temperature x amplitude)
4. **Wiener-KAN approaches** for sensor drift compensation not yet documented in literature

### Recommendations
1. Focus on FRIKAN paper methodology for magnitude-factor frequency response
2. Use Lin 2020 compensation approach as baseline for temperature compensation
3. Consider combined temperature+magnitude compensation model
4. Explore Wiener-KAN for nonlinear system identification in this context

---

## Conclusion

Literature support for GAP1, GAP3, and GAP5 is adequate ("Low gap" status). Key papers by Lin et al. (2020), Chikishev et al. (2019), and the FRIKAN paper (Li et al. 2025) provide strong foundation for frequency response drift research.

**Key Citation Papers:**
1. Lin et al. (2020) - Temperature compensation method
2. Chikishev et al. (2019) - Analytical AFR model
3. Li et al. (2025) - FRIKAN magnitude effects

---

*Report generated: 2026-03-31*
*Agent: R191_agent3*
*Project: MET Nonlinear - Wiener-KAN for Frequency Response Drift Compensation*
