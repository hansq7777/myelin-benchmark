# Model Performance Summary (2026-02-03)

## Experimental Consistency
- Split: fixed 4-fold split (stack-grouped), `splits_final.json`
- Seed: 42 (`NNUNET_SEED=42`, `PYTHONHASHSEED=42`)
- Note: Dataset002 (5ch) uses the same split strategy; same seed.

## Metrics
- Reported metric: best EMA pseudo Dice per fold, taken from training logs.
- Two summaries provided:
  - **All folds (0–3)**
  - **Excluding fold2** (0/1/3 only)

## Summary Table (mean of best EMA pseudo Dice)

| Model | Dataset | Folds Used | Mean (all folds) | Mean (no fold2) |
|---|---|---|---:|---:|
| vanilla | Dataset001_20241206_MyelinConfData | 0,1,2,3 | 0.5252 | 0.6219 |
| artifact_aug | Dataset001_20241206_MyelinConfData | 0,1,2,3 | 0.5212 | 0.6136 |
| cldice_highres | Dataset001_20241206_MyelinConfData | 0,1,2,3 | 0.5216 | 0.5992 |
| cldice_ms | Dataset001_20241206_MyelinConfData | 0,1,2,3 | 0.5258 | 0.6221 |
| oversample066 | Dataset001_20241206_MyelinConfData | 0,1,2,3 | 0.5375 | 0.6192 |
| k2_5ch | Dataset002_20241206_MyelinConfData_5ch | 0,1,2,3 | 0.5902 | 0.6440 |

## Fold-Level Bests (EMA pseudo Dice)

- vanilla: {0: 0.6232, 1: 0.6223, 2: 0.2348, 3: 0.6203}
- artifact_aug: {0: 0.5998, 1: 0.6261, 2: 0.2442, 3: 0.6148}
- cldice_highres: {0: 0.5455, 1: 0.6278, 2: 0.2889, 3: 0.6244}
- cldice_ms: {0: 0.6216, 1: 0.6192, 2: 0.2370, 3: 0.6254}
- oversample066: {0: 0.6177, 1: 0.6225, 2: 0.2922, 3: 0.6175}
- k2_5ch: {0: 0.6375, 1: 0.6497, 2: 0.4290, 3: 0.6448}

## Brief
- **k2_5ch is best overall** and remains best even when excluding fold2.
- Fold2 is consistently low across all 3ch models; it dominates variance.
- cldice_ms ≈ vanilla ≈ oversample066 when fold2 excluded.

## Memory/Channel Considerations
- Input tensor memory scales linearly with channels:
  - 5ch vs 3ch ≈ **1.67x input memory**
  - 7ch vs 3ch ≈ **2.33x input memory**
- Overall GPU memory impact is **less than linear** because most activations depend on feature width, not input channels.
- Practical expectation: **5ch adds ~10–25% GPU memory**, **7ch adds ~20–40%**, but should be verified on this GPU.

## 7ch Feasibility
- Yes, **7ch is feasible** on 12GB, but may require reducing batch size or patch size.
- Recommendation: run a quick dry train (1–2 epochs) and watch `nvidia-smi` peak memory.
