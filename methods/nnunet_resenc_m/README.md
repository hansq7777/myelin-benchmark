# nnUNet ResEnc M (Residual Encoder UNet)

- Purpose: ResEnc M preset (target ~9–11GB VRAM)
- Env: shared venv at `methods/nnunet/.venv`
- Results: `methods/nnunet_resenc_m/nnUNet_results`

## Usage
```
source methods/nnunet_resenc_m/nnunet_env.sh
# after planning with nnUNetPlannerResEncM
nnUNetv2_train 1 2d 0 -p nnUNetResEncUNetMPlans
```
