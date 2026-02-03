# nnUNet Oversample 0.66 Variant

- Purpose: Foreground oversampling set to 0.66 (single-change branch)
- Env: shared venv at `methods/nnunet/.venv`
- Results: `methods/nnunet_oversample066/nnUNet_results`

## Usage
```
source methods/nnunet_oversample066/nnunet_env.sh
nnUNetv2_train 1 2d 0 -tr nnUNetTrainerOversample066
```
