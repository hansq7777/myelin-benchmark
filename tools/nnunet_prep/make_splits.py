#!/usr/bin/env python3
"""Create 7:3 train/val split for nnUNet dataset."""
from __future__ import annotations

import json
import random
from pathlib import Path

DATASET_DIR = Path("/home/dilgerlab/Siqi/myelin-benchmark/data/00_raw/nnUNet_raw/Dataset001_20241206_MyelinConfData")
SPLITS_DIR = Path("/home/dilgerlab/Siqi/myelin-benchmark/data/05_splits")
SPLITS_DIR.mkdir(parents=True, exist_ok=True)

labels = sorted((DATASET_DIR / "labelsTr").glob("*.tif"))
case_ids = [p.stem for p in labels]

rng = random.Random(42)
rng.shuffle(case_ids)

n_total = len(case_ids)
n_train = int(round(n_total * 0.7))
train_ids = sorted(case_ids[:n_train])
val_ids = sorted(case_ids[n_train:])

splits = [{"train": train_ids, "val": val_ids}]

with open(DATASET_DIR / "splits_final.json", "w", encoding="utf-8") as f:
    json.dump(splits, f, indent=2)

with open(SPLITS_DIR / "nnunet_Dataset001_20241206_MyelinConfData_splits.json", "w", encoding="utf-8") as f:
    json.dump({"train": train_ids, "val": val_ids}, f, indent=2)

print(f"Total: {n_total}, train: {len(train_ids)}, val: {len(val_ids)}")
