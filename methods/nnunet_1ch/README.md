# nnUNet 1-channel Baseline (single-slice)

- Purpose: Baseline 2D single-channel model (no 2.5D)
- Dataset: Dataset003_20241206_MyelinConfData_1ch
- Env: shared venv at `methods/nnunet/.venv`
- Results: `methods/nnunet_1ch/nnUNet_results`

## Usage
```
source methods/nnunet_1ch/nnunet_env.sh
nnUNetv2_train 3 2d 0
```
