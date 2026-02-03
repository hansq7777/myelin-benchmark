# nnUNet v2 Local Patches

This project uses a local editable clone of nnUNet v2 in:
`methods/nnunet/nnunetv2_src/`

The file `nnunetv2_local_changes.patch` captures all local modifications on top of
upstream commit:
`a30c7a3cd25907973a4bf4c05cf1008d24f54a0e`

Apply (from repo root):
```
cd methods/nnunet/nnunetv2_src
git apply ../../patches/nnunetv2_local_changes.patch
```

This is kept as a record for reproducibility and for re-applying changes when
updating nnUNet v2.
