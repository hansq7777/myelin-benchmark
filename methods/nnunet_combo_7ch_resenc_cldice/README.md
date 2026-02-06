# nnUNet Combo: 7ch + ResEnc M + clDice (multi-scale) + oversample066

Planned combination based on current best-performing strategies:
- **Input**: 7ch padded (k=3) dataset: `Dataset004_20241206_MyelinConfData_7ch`
- **Plans**: `nnUNetResEncUNetMPlans`
- **Trainer**: `nnUNetTrainerCLDiceMS_Oversample066`

Notes:
- This intentionally excludes `artifact_aug` (underperformed vs vanilla).
- Oversample is applied via trainer variant (oversample_foreground_percent=0.66).

Run (after confirmation):
```
source methods/nnunet_combo_7ch_resenc_cldice/nnunet_env.sh
nnUNetv2_train Dataset004_20241206_MyelinConfData_7ch 2d 0 -tr nnUNetTrainerCLDiceMS_Oversample066 -p nnUNetResEncUNetMPlans
```
