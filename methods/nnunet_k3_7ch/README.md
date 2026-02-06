# nnUNet 7-channel baseline

- Purpose: 2.5D 7-channel with edge padding
- Dataset: Dataset004_20241206_MyelinConfData_7ch
- Env: shared venv at `methods/nnunet/.venv`
- Results: `methods/nnunet_k3_7ch/nnUNet_results`

## Usage
```
source methods/nnunet_k3_7ch/nnunet_env.sh
nnUNetv2_train 4 2d 0
```
