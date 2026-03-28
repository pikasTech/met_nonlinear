# Excluded Literature

**Status**: STEP2 Updated 2026-03-28 (Round 2 additions)

## Cannot Verify / Not Found

**AFMAE**
- Original source NOT FOUND in literature
- Use Focal Frequency Loss (Jiang et al., 2021) instead

**FreDF (Original paper)**
- Referenced by SAMFre as Wang et al., 2024
- Not found in arXiv or major databases

## Out of Scope / Excluded

**Liu et al. - KAN 2.0 (2024)** arXiv:2408.10205
- Reason: Different goal - scientific discovery focus vs general ML
- Note: MultKAN has theoretical value but different application focus
- Decision: Excluded per STEP2 analysis

**Tagliabue, How - Airflow-Inertial Odometry (2021)** arXiv:2105.13506
- Reason: Different domain: robotics vs chemical sensing

**Feng et al. - Fre-CW (2025)** arXiv:2508.08955
- Reason: Attack-focused optimization vs Wiener-KAN compensation goal

**Basalaev et al. - CNN Wiener seismic isolation FFT (2024)** arXiv:2410.14806
- Reason: Highly specialized domain (gravitational wave detector seismic isolation)
- Relevance: Low for MET Nonlinear paper

**Karita et al. - Transformer vs RNN for Speech (2019)** arXiv:1909.06317
- Reason: Compares Transformer vs RNN, not relevant to RNN vs CNN comparison
- Relevance: Excluded per architecture scope

**Transformer for Time Series Papers**
- Informer, Autoformer, FEDformer, Transformers Survey, Attention Is All You Need, Efficient Transformers Survey
- Reason: NOT FOUND relevant for Wiener-KAN comparison
- Decision: Excluded per literature scope

## Conflicts and Caveats

**Ali et al. - KAN vs LSTM (2025)** arXiv:2511.18613
- Note: This paper shows LSTM OUTPERFORMS KAN in stock prediction
- This CONTRADICTS Wiener-KAN efficiency claims
- Decision: Kept in verified_literature.md with warning flag
- Use with caution: efficiency claims should focus on KAN-GRU hybrid (Rather 2025)

**Beintema et al. - Deep Encoder Networks (2020)** arXiv:2012.07697
- Note: Claims "lowest known simulation error" on Wiener-Hammerstein benchmark
- May conflict with Cruz SS-KAN performance claims
- Decision: Kept in verified_literature.md with caveat flag

## Pending Verification (Not Excluded)

**KAN 2.0 - Liu et al. (2024)** arXiv:2408.10205
- Status: Excluded - different goal (scientific discovery)
- Note: MultKAN has theoretical value but different application focus

**KAN 2.0 - MultKAN component**
- Could be relevant for modular structure claims
- Pending: further analysis if modularity becomes relevant

## Cannot Verify / Paywalled

**Zhou et al. - LSTM for MEMS Seabed Deformation (2025)** IEEE 11122349
- Reason: IEEE Xplore paywalled, cannot obtain full content
- Status: Excluded - cannot verify claims

## Analysis Report Reference
- docs/research/literature/20260328/STEP2_Deep_Analysis.md (Round 2)
- docs/research/literature/20260328/STEP2_Round3_Analysis.md (Round 3)
