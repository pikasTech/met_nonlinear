# Napkin

## Corrections
| Date | Source | What Went Wrong | What To Do Instead |
|------|--------|----------------|-------------------|

## User Preferences
- (none recorded)

## Patterns That Work
- STEP3 documents (key_references.md, theory_framework.md, paper_draft_segments.md, SUMMARY.md) are already comprehensive after R32/R33 analysis
- Only status updates needed for STEP3 - no content changes required
- R33 confirmed Luo KANLoc exclusion (domain mismatch: robot vision vs sensor drift compensation)

## Patterns That Don't Work
- Trying to remove the corrupted `-p` directory in root (encoding issues make it inaccessible)

## Domain Notes
- MET非线性项目: Wiener-KAN用于频率响应漂移补偿
- 所有P0-P1主张支撑已完备
- R3-4对比方法支撑: Yin 2017 CNN/RNN, Bai TCN, Rather 2025 KAN-GRU
- R4-8计算成本支撑: KANtize, LUT-KAN, IoT KAN (LUT效率)
- RNN vs 1D-CNN声称已被冲突文献反驳，必须删除

## Session Log
- 2026-03-29: R1.1.1 完成 - 1DCNN_KAN (CNNKAN) 模型实现，参考 LSTM 写法（不需要 system 参数）
- 2026-03-29: STEP3 完成 - 文档状态更新完成
- 2026-03-29: R1.1 完成 - 1DCNN_KAN 方案2详细计划已写入 `docs/MDTODO/details/05_1DCNN_KAN/20260329_0941_Task_Report.md`
- 2026-03-29: STEP2 R54 final confirmation completed
- All "待核实" MEASUREMENT entries confirmed verified in R28
- Literature library complete: 50+ KAN, 30+ Wiener, 20+ Freq Loss, 25+ Drift, 15+ Efficiency
- MEASUREMENT target 50篇 exceeded (85篇)
- STEP2 analysis officially complete
- 2026-03-29: Root directory cleaned - `-p` file moved to `logs/temp/`
- 2026-03-29 R65: Parallel 3-agent search confirmed no new papers - literature library still complete
- 2026-03-29 R72: 3-agent parallel search confirmed literature completeness - 50+ KAN, 30+ Wiener, 20+ Freq Loss, 25+ Drift, 15+ Efficiency, 90+ MEASUREMENT
