# nnUNet Artifact Augmentation Variant

- Purpose: Add artifact augmentation (granular points, surface patches, granular rings)
- Env: shared venv at `methods/nnunet/.venv`
- Results: `methods/nnunet_artifact_aug/nnUNet_results`

## Usage
```
source methods/nnunet_artifact_aug/nnunet_env.sh
nnUNetv2_train 1 2d 0 -tr nnUNetTrainerArtifactAug
```

## Notes
- Augmentation is implemented in `nnUNetTrainerArtifactAug`.
- Artifacts follow the project definition: background granular points, surface-adjacent dense patches, and granular ring-like scatter.
