# nnUNet Dice + clDice Variant (High-res only)

- Purpose: Custom loss to encourage line-like continuity (Dice/CE + 0.3 * clDice), applied only to highest-resolution output
- Env: shared venv at `methods/nnunet/.venv`
- Results: `methods/nnunet_dice_cldice/nnUNet_results`

## Usage
```
source methods/nnunet_dice_cldice/nnunet_env.sh
nnUNetv2_train 1 2d 0 -tr nnUNetTrainerCLDice
```

## Notes
- clDice uses soft skeletonization (iters=10) and is applied to the highest-resolution output only.
- Loss = base nnUNet loss + 0.3 * clDice.
- Small-target gating: excludes samples with skeleton length < 5 pixels.
