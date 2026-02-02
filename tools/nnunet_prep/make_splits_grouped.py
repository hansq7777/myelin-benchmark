#!/usr/bin/env python3
"""Create grouped train/val split (by stack/animal/batch) for nnUNet dataset."""
from __future__ import annotations

import json
import random
import re
from pathlib import Path


DATASET_DIR = Path("/home/dilgerlab/Siqi/myelin-benchmark/data/00_raw/nnUNet_raw/Dataset001_20241206_MyelinConfData")
PREPROCESSED_DIR = Path("/home/dilgerlab/Siqi/myelin-benchmark/data/04_processed/nnUNet_preprocessed/Dataset001_20241206_MyelinConfData")
SPLITS_DIR = Path("/home/dilgerlab/Siqi/myelin-benchmark/data/05_splits")
SPLITS_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
TRAIN_RATIO = 0.8
N_SPLITS = 4  # use leave-one-stack-out when N_SPLITS >= number of stacks
EXCLUDE_FROM_VAL = set()


def case_to_group(case_id: str) -> str:
    m = re.match(r"(.+)_z\d+$", case_id)
    return m.group(1) if m else case_id


def main() -> None:
    labels = sorted((DATASET_DIR / "labelsTr").glob("*.tif"))
    case_ids = [p.stem for p in labels]

    groups = {}
    for cid in case_ids:
        g = case_to_group(cid)
        groups.setdefault(g, []).append(cid)

    group_ids = sorted(groups.keys())
    rng = random.Random(SEED)
    rng.shuffle(group_ids)

    n_groups = len(group_ids)

    candidates = [g for g in group_ids if g not in EXCLUDE_FROM_VAL]
    if len(candidates) == 0:
        raise RuntimeError("No candidates available for validation split after exclusions.")

    splits = []
    fold_groups = []
    if N_SPLITS >= n_groups:
        # leave-one-stack-out
        for val_group in group_ids:
            if val_group in EXCLUDE_FROM_VAL:
                continue
            train_groups = [g for g in group_ids if g != val_group]
            train_ids = sorted([cid for cid in case_ids if case_to_group(cid) in train_groups])
            val_ids = sorted([cid for cid in case_ids if case_to_group(cid) == val_group])
            splits.append({"train": train_ids, "val": val_ids})
            fold_groups.append({"train_stacks": train_groups, "val_stacks": [val_group]})
    else:
        n_train = max(1, int(round(n_groups * TRAIN_RATIO)))
        rng.shuffle(group_ids)
        val_group = rng.choice(candidates)
        val_groups = {val_group}
        train_groups = set([g for g in group_ids if g != val_group])
        train_ids = sorted([cid for cid in case_ids if case_to_group(cid) in train_groups])
        val_ids = sorted([cid for cid in case_ids if case_to_group(cid) in val_groups])
        splits = [{"train": train_ids, "val": val_ids}]
        fold_groups = [{"train_stacks": sorted(train_groups), "val_stacks": sorted(val_groups)}]

    with open(DATASET_DIR / "splits_final.json", "w", encoding="utf-8") as f:
        json.dump(splits, f, indent=2)

    if PREPROCESSED_DIR.exists():
        with open(PREPROCESSED_DIR / "splits_final.json", "w", encoding="utf-8") as f:
            json.dump(splits, f, indent=2)

    with open(SPLITS_DIR / "nnunet_Dataset001_20241206_MyelinConfData_splits.json", "w", encoding="utf-8") as f:
        json.dump({"train": train_ids, "val": val_ids}, f, indent=2)

    with open(SPLITS_DIR / "nnunet_Dataset001_20241206_MyelinConfData_splits_stacks.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "seed": SEED,
                "train_ratio": TRAIN_RATIO,
                "n_splits": N_SPLITS,
                "exclude_from_val": sorted(EXCLUDE_FROM_VAL),
                "n_stacks": n_groups,
                "folds": fold_groups,
            },
            f,
            indent=2,
        )

    print(f"Stacks total: {n_groups}, folds: {len(splits)}")
    print(f"Cases total: {len(case_ids)}")


if __name__ == "__main__":
    main()
