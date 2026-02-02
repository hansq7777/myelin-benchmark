# nnUNet Dice + clDice Variant

- Purpose: Custom loss (Dice + clDice)
- Env: shared venv at `methods/nnunet/.venv`
- Results: `methods/nnunet_dice_cldice/nnUNet_results`

## Usage
```
source methods/nnunet_dice_cldice/nnunet_env.sh
nnUNetv2_train 1 2d 0 -tr nnUNetTrainerDiceClDice
```
