# nnUNet Dice + clDice Variant (Multi-scale)

- Purpose: Custom loss to encourage line-like continuity (Dice/CE + 0.3 * clDice), applied across deep supervision outputs
- Env: shared venv at `methods/nnunet/.venv`
- Results: `methods/nnunet_dice_cldice_ms/nnUNet_results`

## Usage
```
source methods/nnunet_dice_cldice_ms/nnunet_env.sh
nnUNetv2_train 1 2d 0 -tr nnUNetTrainerCLDiceMS
```

## Notes
- clDice uses soft skeletonization (iters=10) and is applied to all deep supervision outputs using nnUNet DS weights.
- Loss = base nnUNet loss + 0.3 * clDice.
- Small-target gating: excludes samples with skeleton length < 5 pixels.
