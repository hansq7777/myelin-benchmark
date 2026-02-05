"""
Stack per-slice nnUNet predictions back into z-stacks and copy originals + preds to REVIEW.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List

import numpy as np
import tifffile

Z_RE = re.compile(r"_z(\d+)")


def _sorted_by_z(files: List[Path]) -> List[Path]:
    def _key(p: Path) -> int:
        m = Z_RE.search(p.stem)
        return int(m.group(1)) if m else -1

    return sorted(files, key=_key)


def stack_slices(files: List[Path]) -> np.ndarray:
    arrs = [tifffile.imread(f) for f in files]
    return np.stack(arrs, axis=0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outputs-root", required=True, help="nnUNet outputs root (timestamped)")
    ap.add_argument("--resampled-root", required=True, help="Resampled zstack root")
    ap.add_argument("--meta-root", required=True, help="Meta JSON root")
    ap.add_argument("--review-root", required=True, help="Review output root")
    args = ap.parse_args()

    outputs_root = Path(args.outputs_root)
    resampled_root = Path(args.resampled_root)
    meta_root = Path(args.meta_root)
    review_root = Path(args.review_root)

    review_root.mkdir(parents=True, exist_ok=True)
    (review_root / "original_zstacks").mkdir(parents=True, exist_ok=True)
    (review_root / "predictions").mkdir(parents=True, exist_ok=True)

    # Stack IDs from meta JSONs
    stack_ids = sorted([p.stem for p in meta_root.glob("*.json")])
    if not stack_ids:
        raise SystemExit(f"No meta json found in {meta_root}")

    # Copy original resampled stacks
    for sid in stack_ids:
        # prefer explicit dz0p396 naming if present
        cand = resampled_root / f"{sid}_dz0p396.tif"
        if not cand.exists():
            # fallback: any tif containing sid
            matches = list(resampled_root.glob(f"{sid}*.tif"))
            if matches:
                cand = matches[0]
            else:
                print(f"[WARN] Missing resampled stack for {sid}")
                continue
        shutil.copy2(cand, review_root / "original_zstacks" / cand.name)

    # For each model output, stack predictions
    model_dirs = sorted([p for p in outputs_root.iterdir() if p.is_dir()])
    for mdir in model_dirs:
        out_model_dir = review_root / "predictions" / mdir.name
        out_model_dir.mkdir(parents=True, exist_ok=True)

        for sid in stack_ids:
            files = list(mdir.glob(f"{sid}_z*.tif"))
            if not files:
                print(f"[WARN] {mdir.name}: no slices for {sid}")
                continue
            files = _sorted_by_z(files)
            stack = stack_slices(files)
            out_path = out_model_dir / f"{sid}_pred.tif"
            # minimal stack, keep uint8/uint16 as-is
            tifffile.imwrite(out_path, stack)

    # Copy manifest for traceability
    manifest = outputs_root / ".." / "manifest_inference_dz0p396.json"
    if manifest.exists():
        shutil.copy2(manifest, review_root / manifest.name)

    print(f"[DONE] review bundle at {review_root}")


if __name__ == "__main__":
    main()
