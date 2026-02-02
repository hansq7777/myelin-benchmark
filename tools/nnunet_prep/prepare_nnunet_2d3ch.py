#!/usr/bin/env python3
"""Prepare nnUNet v2 2D 3-channel pseudo-3D dataset.

Sliding window: for each center slice z, use (z-1, z, z+1) as 3 channels.
Label: center slice from annotation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import tifffile as tiff


DATASET_NAME = "20241206_MyelinConfData"
DATASET_ID = "001"

PROJECT_ROOT = Path("/home/dilgerlab/Siqi/myelin-benchmark")
NNUNET_RAW = PROJECT_ROOT / "data/00_raw/nnUNet_raw"
DATASET_DIR = NNUNET_RAW / f"Dataset{DATASET_ID}_{DATASET_NAME}"
IMAGES_TR = DATASET_DIR / "imagesTr"
LABELS_TR = DATASET_DIR / "labelsTr"

# Raw/label pairs
PAIRS = [
    (
        "S1BF_S19",
        PROJECT_ROOT / "data/00_raw/20241206_s1bf/slice_144_left_hemisphere_S1BF_ometiff/slice_144_left_hemisphere_S1BF_S19.ome.tif",
        PROJECT_ROOT / "data/03_labels/20241206_s1bf/slice_144_left_hemisphere_S1BF_S19_annotation.tif",
    ),
    (
        "S1BF_S24",
        PROJECT_ROOT / "data/00_raw/20241206_s1bf/slice_144_left_hemisphere_S1BF_ometiff/slice_144_left_hemisphere_S1BF_S24.ome.tif",
        PROJECT_ROOT / "data/03_labels/20241206_s1bf/slice_144_left_hemisphere_S1BF_S24_annotation.tif",
    ),
    (
        "S1BF_S26",
        PROJECT_ROOT / "data/00_raw/20241206_s1bf/slice_144_left_hemisphere_S1BF_ometiff/slice_144_left_hemisphere_S1BF_S26.ome.tif",
        PROJECT_ROOT / "data/03_labels/20241206_s1bf/slice_144_left_hemisphere_S1BF_S26_annotation.tif",
    ),
    (
        "PIG_INTERFACE_S00",
        PROJECT_ROOT / "data/00_raw/20241206_pig_hippocampus/pig_hippocampus_interface_ometiff/pig_hippocampus_interface_S00.ome.tif",
        PROJECT_ROOT / "data/03_labels/20241206_pig_hippocampus/pig_hippocampus_interface_S00_annotation.tif",
    ),
]


def load_stack(path: Path) -> np.ndarray:
    arr = tiff.imread(path)
    if arr.ndim == 2:
        arr = arr[None, ...]
    return arr


def save_tif(path: Path, arr: np.ndarray) -> None:
    # Save as 2D single-channel tif
    tiff.imwrite(path, arr.astype(arr.dtype), photometric="minisblack")


def main() -> None:
    IMAGES_TR.mkdir(parents=True, exist_ok=True)
    LABELS_TR.mkdir(parents=True, exist_ok=True)

    case_count = 0
    for case_prefix, raw_path, ann_path in PAIRS:
        raw = load_stack(raw_path)
        ann = load_stack(ann_path)

        z_raw = raw.shape[0]
        z_ann = ann.shape[0]
        if z_ann < z_raw:
            pad = np.zeros((z_raw - z_ann, *ann.shape[1:]), dtype=ann.dtype)
            ann = np.concatenate([ann, pad], axis=0)
            z_ann = z_raw
        elif z_ann > z_raw:
            ann = ann[:z_raw]
            z_ann = z_raw
        z_min = z_raw

        # sliding window centers: 1..z_min-2
        for z in range(1, z_min - 1):
            case_id = f"{case_prefix}_z{z:03d}"

            ch0 = raw[z - 1]
            ch1 = raw[z]
            ch2 = raw[z + 1]
            label = ann[z]

            img0 = IMAGES_TR / f"{case_id}_0000.tif"
            img1 = IMAGES_TR / f"{case_id}_0001.tif"
            img2 = IMAGES_TR / f"{case_id}_0002.tif"
            lab = LABELS_TR / f"{case_id}.tif"

            save_tif(img0, ch0)
            save_tif(img1, ch1)
            save_tif(img2, ch2)
            save_tif(lab, label)

            case_count += 1

    dataset_json = {
        "name": DATASET_NAME,
        "description": "Myelin confocal pseudo-3D 2D dataset (3-channel sliding window)",
        "tensorImageSize": "2D",
        "reference": "",
        "licence": "",
        "release": "",
        "channel_names": {
            "0": "slice_-1",
            "1": "slice_0",
            "2": "slice_+1",
        },
        "labels": {
            "background": 0,
            "myelin": 1,
        },
        "numTraining": case_count,
        "numTest": 0,
        "file_ending": ".tif",
    }

    with open(DATASET_DIR / "dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset_json, f, indent=2)

    print(f"Prepared {case_count} training cases in {DATASET_DIR}")


if __name__ == "__main__":
    main()
