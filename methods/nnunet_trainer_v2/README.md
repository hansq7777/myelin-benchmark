# nnUNet Custom Trainer Variant

- Purpose: Custom trainer (sampling, augmentations, etc.)
- Env: shared venv at `methods/nnunet/.venv`
- Results: `methods/nnunet_trainer_v2/nnUNet_results`

## Usage
```
source methods/nnunet_trainer_v2/nnunet_env.sh
nnUNetv2_train 1 2d 0 -tr nnUNetTrainerV2
```
