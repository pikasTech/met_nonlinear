# Napkin Runbook

## Curation Rules
- Re-prioritize on every read.
- Keep recurring, high-value notes only.
- Max 10 items per category.
- Each item includes date + "Do instead".

## User Directives
1. **[2026-04-13] Continue through unrelated dirty changes by default**
   Do instead: when unrelated working-tree changes already exist, proceed with the requested task without stopping to ask; do not overwrite, revert, or expand scope into those unrelated files.
2. **[2026-04-10] Only change the requested scope**
   Do instead: when the user says "只改 X" or "其他不变", modify only that variable and leave all other configs, model structure, and training knobs untouched.
3. **[2026-04-13] Do not hand-edit MDTODO files**
   Do instead: use the `mdtodo-edit` skill if a task list file itself needs status or content updates.

## Execution & Validation (Highest Priority)
1. **[2026-04-10] Offline evaluation must always load trained weights**
   Do instead: make offline evaluation/export load existing weights unconditionally; use `use_best_val_weights` only to choose `best_val.weights.h5` vs `best.weights.h5`.
2. **[2026-04-10] Custom `predict()` must preserve scaler logic**
   Do instead: when overriding model `predict()`, reuse `BaseModel.predict()` scaling and de-scaling behavior and spot-check `linear_response.json.gains_comped` stays in physical units.
3. **[2026-04-11] FRIKAN ablations must preserve semantic equivalence**
   Do instead: when doing FRIMLP/FRIKAND-style ablations, keep the FRI front-end, fast-model path, and `prepare_systems()` semantics intact; only swap the intended local module.
4. **[2026-04-04] Build-only smoke tests still need scaler setup**
   Do instead: if skipping `prepare_training_data()`, set `config.use_scale=False` or inject a `CombinedScaler` before calling `set_scaler`/build flows.
5. **[2026-04-05] Long-sequence models need explicit batch caps**
   Do instead: verify sample-count estimation against real tensor shape and set a conservative `MAX_BATCH_SIZE` before training long-sequence models.

## Shell & Command Reliability
1. **[2026-04-01] Avoid shell text creation for Markdown or config edits**
   Do instead: use `Edit`/`Write` instead of `echo`/`printf`/heredoc-style shell writes to avoid Windows encoding corruption.
2. **[2026-04-03] Research toolchain blockers before local thrash**
   Do instead: for QEMU/toolchain/environment failures, do external research first, then return to repo-specific debugging.
3. **[2026-04-03] Use the `tf26` environment, not stale hardcoded interpreters**
   Do instead: invoke Python through the `tf26` conda environment (for example `conda run -n tf26 python`) unless a machine-specific path is explicitly required and verified.
4. **[2026-04-10] Create EP templates explicitly**
   Do instead: run `python cli.py ep create "..."` before executing a new EP path; do not expect `python cli.py ep "..."` to create missing config.

## Domain Behavior Guardrails
1. **[2026-04-03] RNN-vs-1D-CNN efficiency is not a safe default claim**
   Do instead: delete or avoid that claim unless it is re-proven on the current task with current measurements.
2. **[2026-04-13] MN transfer work needs both sensor-centric reframing and stronger experiment design**
   Do instead: when preparing the MN transfer manuscript, treat topic reframing, broader horizontal comparisons, and stronger ablation design as a bundled requirement rather than choosing only one.
3. **[2026-04-04] FRIKAN LUT tuning starts from ROM limits**
   Do instead: check flash/ROM budget first, then tune LUT points and interpolation; keep interpolation when accuracy depends on it.
4. **[2026-04-03] QEMU benchmark timing cannot rely on DWT by default**
   Do instead: confirm `DWT_CYCCNT` actually advances; otherwise use host-side elapsed time and label it accordingly.
5. **[2026-04-03] QEMU C/TF sign mismatches often come from UART formatting**
   Do instead: inspect formatted output helpers and compare intermediate tensors (`input_scaled`, hidden states, dense output, final output) before blaming core math.
