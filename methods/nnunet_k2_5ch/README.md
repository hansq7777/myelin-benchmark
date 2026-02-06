# nnUNet 2.5D k=2 (5-channel) Variant

- Purpose: 5-channel pseudo-3D input (k=2)
- Dataset: `Dataset002_20241206_MyelinConfData_5ch`
- Env: shared venv at `methods/nnunet/.venv`
- Results: `methods/nnunet_k2_5ch/nnUNet_results`

## Usage
```
source methods/nnunet_k2_5ch/nnunet_env.sh
nnUNetv2_train 2 2d 0
```
