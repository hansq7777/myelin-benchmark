# nnUNet Z-Decay Augmentation Variant

- Purpose: Custom augmentation for Z attenuation / depth effects
- Env: shared venv at `methods/nnunet/.venv`
- Results: `methods/nnunet_aug_zdecay/nnUNet_results`

## Usage
```
source methods/nnunet_aug_zdecay/nnunet_env.sh
nnUNetv2_train 1 2d 0 -tr nnUNetTrainerZDecay
```
