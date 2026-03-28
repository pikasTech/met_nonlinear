# Literature Survey Summary

**Status**: STEP3 Round 3 Completed (2026-03-28)
**Stage**: Decision-level organization complete

---

## Literature Processing Pipeline

| Stage | Date | Output | Count |
|-------|------|--------|-------|
| STEP1 | 2026-03-27 | raw_literature.md, catalog | Initial |
| STEP2 R1 | 2026-03-28 | verified_literature.md | 13 papers |
| STEP2 R2 | 2026-03-28 | verified_literature.md | 30+ papers |
| **STEP2 R3** | **2026-03-28** | **verified_literature.md (11 new)** | **40+ papers** |
| **STEP3 R3** | **2026-03-28** | **key_references.md (updated)** | **Framework consolidated** |

## Second Draft Claims Status

| Claim | Literature | Status |
|-------|------------|--------|
| Wiener-KAN architecture | Cruz 2025 SS-KAN, Manavalan 2026, TFKAN | **SUPPORTED** |
| Wiener classical theory | Schoukens 2009, Haber 1990, Bai-Giri 2010 | **SUPPORTED** |
| KAN replaces Wiener nonlinearity | Liu 2024, Cruz SS-KAN, Li 2024 | **SUPPORTED** |
| KAN+RNN hybrid | TKAN, KAN-GRU Hybrid, TFKAN, TimeKAN | **SUPPORTED** |
| KAN-GRU > LSTM/GRU | Rather 2025 | **SUPPORTED** |
| KAN in frequency domain | TFKAN (first in freq domain) | **SUPPORTED** |
| AFMAE frequency loss | Jiang FFL, SAMFre, FIRE, FreLE | **SUPPORTED (theory)** |
| RNN efficiency | Yin 2017, Bai TCN | **SUPPORTED** |
| Drift compensation | Zhang 2022, Lin 2025, Li 2025, Shi 2022 | **SUPPORTED** |

## Literature Gaps

| Gap | Status | Recommendation |
|-----|--------|----------------|
| AFMAE source | NOT FOUND | Use FFL/SAMFre/FIRE/FreLE |
| Transformer comparison | NOT FOUND | Use KAN-GRU hybrid (Rather 2025) |
| RVTDCNN PA linearization | NOT FOUND | Remove claim |
| KANet FLOPs | PAYWALLED | Remove claim |

## Round 3 Key Additions

- **TFKAN (Kui 2025)**: First KAN in frequency domain
- **TimeKAN (Huang 2025)**: KAN + frequency decomposition SOTA
- **Schoukens 2009**: Classical Wiener-Hammerstein benchmark
- **Sun 2025 FreLE**: Spectral bias correction
- **Shi 2022 EEMD-GRNN**: Complete drift compensation framework

## Key Output Documents

- `key_references.md` - Core literature (29 papers)
- `theory_framework.md` - Theory organized by claims
- `paper_draft_segments.md` - Usable draft content
- `verified_literature.md` - 40+ verified papers
- `excluded_literature.md` - 8 excluded papers
- `20260328/STEP2_Deep_Analysis.md` - Round 2 analysis
- `20260328/STEP2_Round3_Analysis.md` - Round 3 analysis

**Last Updated**: 2026-03-28 (STEP3 Round 3)
