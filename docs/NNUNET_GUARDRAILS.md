# Guardrails (nnUNet + DBT)

This document defines the P0 "inference consistency + misrun prevention" guardrails and the shared blocked-run policy.

## Scope

Implemented now:

- Unified preflight checkers:
  - `tools/guardrails/nnunet_preflight.py`
  - `tools/guardrails/dbt_preflight.py`
- Unified guarded launcher:
  - `scripts/nnunet_guarded_run.sh`
- Integrated entries:
  - `scripts/run_combo_7ch_review_5fold_detached.sh` (nnUNet training)
  - `scripts/run_infer_dataset006_665_chunked_to_review.sh` (nnUNet inference)
  - `scripts/run_deepbranchtracer_4fold_train_guarded.sh` (DBT training)

Partially implemented Step 2:

- DBT adapter is now on the same contract/runner interface.
- Future new-model adapters remain to be added.

## Hybrid Policy

Hybrid mode blocks only critical checks and warns on non-critical checks.

Current critical checks:

- `spacing`
- `channels`
- `split`
- `nonempty`
- `overwrite` (when enabled by contract)
- `dbt_structure` (DBT adapter)

## Contract Schema (Core)

All guarded runs use a JSON contract. Contract fields are adapter-specific, but this structure is shared:

```json
{
  "adapter": "nnunet|dbt",
  "critical_checks": ["..."],
  "...adapter_specific_blocks...": {},
  "output": {
    "path": "...",
    "allow_nonempty": true
  }
}
```

### nnUNet Contract (example)

```json
{
  "adapter": "nnunet",
  "critical_checks": ["spacing", "channels", "split", "nonempty"],
  "inputs": [
    {
      "name": "dataset006_imagesTr",
      "images_dir": ".../imagesTr",
      "required_channels": [0,1,2,3,4,5,6],
      "min_cases": 1,
      "filename_pattern": "^(?P<case>.+)_000(?P<ch>\\d+)\\.tif$",
      "manifest_json": ".../manifest_inference_*.json",
      "expected_target_dz": 0.396,
      "target_dz_tol": 0.000001
    }
  ],
  "split": {
    "path": ".../splits_final.json",
    "expected_folds": 5,
    "require_disjoint_train_val": true,
    "check_case_subset": "warn"
  },
  "output": {
    "path": ".../outputs/...",
    "allow_nonempty": true
  }
}
```

Notes:

- Channel completeness is not hardcoded globally. It is controlled by `required_channels` in the contract and can vary by task/model.
- Inference contracts can include manifest-based `target_dz` validation.

### DBT Contract (example)

```json
{
  "adapter": "dbt",
  "critical_checks": ["nonempty", "dbt_structure", "split"],
  "dataset": {
    "fold_root": ".../methods/deepbranchtracer/data/myelin_4fold",
    "fold_indices": [0,1,2,3],
    "prepared_relpath": "training_data_seed42_ok",
    "train_subdir": "training_datasets",
    "test_subdir": "test_datasets",
    "min_train_cases": 1,
    "min_test_cases": 1,
    "sample_cases_per_split": 3,
    "required_patch_files": ["node_img.tif", "node_matrix_1.txt", "node_matrix_2.txt", "node_matrix_3.txt"],
    "case_dir_pattern": "^.+_z[0-9]+$",
    "suspicious_globs": ["training_data_seed42training_datasets*"]
  },
  "output": {
    "path": ".../methods/deepbranchtracer/experiments/myelin_4fold_seed42_2stage",
    "allow_nonempty": true
  }
}
```

DBT preflight checks:

- fold and prepared data directories exist
- train/test case counts are not empty
- sampled patch directories contain required DBT files
- train/test case overlap detection
- suspicious malformed path detection (known failure pattern)

## Guarded Launcher

Use `scripts/nnunet_guarded_run.sh`:

```bash
scripts/nnunet_guarded_run.sh \
  --adapter nnunet \
  --contract <contract.json> \
  --log <run.log> \
  --status-tsv <run.tsv> \
  --report <preflight_report.json> \
  --mode hybrid \
  --heartbeat-sec 30 \
  -- <actual command...>
```

DBT guarded entry:

```bash
scripts/run_deepbranchtracer_4fold_train_guarded.sh
```

The launcher writes:

- preflight status (`preflight_pass` / `preflight_fail`)
- child PID lifecycle (`child_start`, `heartbeat`, `child_exit`)
- signal events (`SIGTERM`, `SIGINT`)
- final script exit code

## Why this reduces misruns

- Blocks expensive compute when spacing/channel/split/structure is invalid.
- Prevents silent empty runs via minimum-case checks.
- Captures exit codes and signals in standardized TSV logs.
- Keeps checks data-driven and reusable for future adapters.

## Next Adapter Targets

- Add adapters for future methods on the same contract + runner interface.
- Keep one common status TSV schema for cross-method troubleshooting.
