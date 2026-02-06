# nnUNet 5-channel (padded) baseline

- Purpose: 2.5D 5-channel with edge padding to match full slice set
- Dataset: Dataset005_20241206_MyelinConfData_5ch_pad
- Env: shared venv at `methods/nnunet/.venv`
- Results: `methods/nnunet_k2_5ch_pad/nnUNet_results`

## Usage
```
source methods/nnunet_k2_5ch_pad/nnunet_env.sh
nnUNetv2_train 5 2d 0
```
