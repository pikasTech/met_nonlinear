# Survey Report: Wiener-KAN Model Literature

Date: 2026-03-27
Stage: STEP1 Survey

## Search Coverage
- P0: KAN networks, Wiener models, Frequency domain loss
- P1: Drift compensation, Architecture efficiency
- Used 5 parallel subagents for search

## Key Findings

### KAN Papers (arXiv verified IDs)
1. Original KAN: Liu et al. - 2404.19756 (ICLR 2025)
2. TKAN: Genet and Inzirillo - 2405.07344
3. KAN for Time Series: Vaca-Rubio et al. - 2405.08790
4. PowerMLP (efficiency): Qiu et al. - 2412.13571 (AAAI 2025)
5. State-Space KAN for Wiener: Cruz et al. - 2506.16392 (IEEE) **KEY**
6. KAN 2.0: Liu et al. - 2408.10205

### Wiener Model Papers
1. State-Space KAN for Wiener-Hammerstein: 2506.16392
2. Barron-Wiener-Laguerre: Manavalan and Tronarp - 2602.13098
3. Kernel Design for Wiener-Hammerstein: Xu et al. - 2505.20747

### Frequency Domain Loss
1. Focal Frequency Loss: Jiang et al. - 2012.12821 (ICCV 2021)
2. TimeCF with SAMFre: Wang et al. - 2505.17532
3. Fre-CW: Feng et al. - 2508.08955

### Drift Compensation
1. TDACNN (Gas Sensor): Zhang et al. - 2110.07509
2. Knowledge Distillation E-nose: Lin and Zhan - 2507.17071
3. Airflow-Inertial Odometry: Tagliabue and How - 2105.13506

### Architecture Efficiency
1. CNN vs RNN NLP: Yin et al. - 1702.01923
2. Deep Filtering: Xie and Zhang - 2112.12616
3. Stable RNN: Miller and Hardt - 1805.10369 (ICLR 2019)

## Pending Verification
1. AFMAE source (likely custom terminology)
2. FreDF original paper (referenced by SAMFre)
3. State-Space KAN for Wiener (2506.16392) - KEY PAPER

## Output Files
- docs/research/literature/literature_catalog.md
- docs/research/literature/raw_literature.md
- docs/research/literature/20260327/research_report.md
