# Local Deployment Changes (Code-Only)

This document summarizes local adjustments made to deployed methods. It is intended to track **code-only** changes that are safe to version-control without datasets or model weights.

## Scope

- Code-only changes: scripts, configs, helper utilities, logging/monitoring.
- Excludes: datasets, checkpoints, inference outputs, and large preprocessed artifacts.

## DeepBranchTracer (DBT)

### Orchestration and monitoring

- Entry script: `scripts/run_deepbranchtracer_4fold_train.sh`
- Added:
  - Heartbeat logging with PID/elapsed/last-log line.
  - Exit trap capturing `SIGINT/SIGTERM/EXIT` and writing TSV summary.
  - Error-type classification (NaN/Inf, OOM, Missing file, RuntimeError).
  - Resource sampling to `logs/deepbranchtracer_4fold_resources_*.log`:
    - `nvidia-smi` GPU utilization/memory
    - `free -m` host memory
    - `ps` RSS per PID
    - `df -h` disk usage
  - Per-stage logs and unified TSV summary.

### Training stability changes

- File: `methods/deepbranchtracer/train_2D.py`
- Changes:
  - Clamp/sanitize inputs to avoid NaN/Inf propagation.
  - Skip invalid batches (bin out-of-range, NaN/Inf).
  - Gradient clipping (`clip_grad_norm_`).
  - `torch.autograd.set_detect_anomaly(True)` for traceback at failure point.
  - Stable loss computation (sigmoid + clamp for probabilities).
  - Metrics snapshot per epoch to JSON/CSV.
  - Checkpoint naming with true epoch, `checkpoint_best.pth`, `checkpoint_final.pth`.
  - Early stopping aligned to nnUNet-like defaults.
- Patch reference: `docs/patches/deepbranchtracer_train_2D_local.patch`

## nnU-Net

- Multiple local training/inference scripts under `scripts/`:
  - Examples: `scripts/run_4models_4fold_seed42.sh`, `scripts/run_infer_all_7ch_combo_parts8_2026-02-05.sh`
- Split control and dataset prep tools under `tools/nnunet_prep/`:
  - Grouped split generation, multi-channel (k=1/2/3) slice stacking, padding.
- These changes are logged in `notebooks/` lab reports and `docs/PROJECT_CONTEXT_v0.2.md`.

## Inference pipeline

- `tools/inference/prepare_inference_inputs.py` and scripts under `scripts/` handle:
  - Input list preparation.
  - 2.5D/7ch slice stacking with padding.
  - Partitioned inference runs with progress logs.

## Git policy

- Only code and documentation changes are versioned.
- Data/weights/outputs remain local and are excluded from commits.
