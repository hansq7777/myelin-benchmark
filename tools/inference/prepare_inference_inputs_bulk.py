#!/usr/bin/env python3
"""
Prepare bulk inference inputs for nnUNet (2D) with 7ch (k=3).

- Scan input_root for *.ome.tif
- Parse dz from OME-XML (fallback to sibling in same folder if missing)
- Resample along Z to target dz (linear interpolation)
- Create 7-channel per-slice cases in imagesTs
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Optional, Dict, List
import xml.etree.ElementTree as ET

import numpy as np
import tifffile as tiff


def parse_dz_from_ome(ome_xml: Optional[str]) -> Optional[float]:
    if not ome_xml:
        return None
    try:
        root = ET.fromstring(ome_xml)
    except Exception:
        return None
    ns = {"ome": "http://www.openmicroscopy.org/Schemas/OME/2016-06"}
    img = root.find("ome:Image", ns) or root.find("Image")
    if img is None:
        return None
    pixels = img.find("ome:Pixels", ns) or img.find("Pixels")
    if pixels is None:
        return None
    dz = pixels.attrib.get("PhysicalSizeZ")
    return float(dz) if dz else None


def load_stack(path: Path) -> np.ndarray:
    arr = tiff.imread(path)
    if arr.ndim == 2:
        arr = arr[None, ...]
    if arr.ndim != 3:
        raise ValueError(f"Unexpected stack shape {arr.shape} for {path}")
    return arr


def resample_z_linear(stack: np.ndarray, new_z: int) -> np.ndarray:
    z, y, x = stack.shape
    if new_z == z:
        return stack
    if new_z < 1:
        new_z = 1
    pos = np.linspace(0, z - 1, new_z)
    z0 = np.floor(pos).astype(int)
    z1 = np.clip(z0 + 1, 0, z - 1)
    w = (pos - z0).astype(np.float32)
    out = (1.0 - w)[:, None, None] * stack[z0] + w[:, None, None] * stack[z1]
    if np.issubdtype(stack.dtype, np.integer):
        out = np.clip(np.rint(out), 0, np.iinfo(stack.dtype).max).astype(stack.dtype)
    else:
        out = out.astype(stack.dtype)
    return out


def save_slice_images(stack: np.ndarray, out_dir: Path, case_prefix: str, k: int = 3) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    z, _, _ = stack.shape
    num_cases = 0
    for zi in range(1, z + 1):
        idx = zi - 1
        case_id = f"{case_prefix}_z{zi:03d}"
        for ch_idx, off in enumerate(range(-k, k + 1)):
            j = min(max(idx + off, 0), z - 1)
            out_path = out_dir / f"{case_id}_{ch_idx:04d}.tif"
            tiff.imwrite(out_path, stack[j], photometric="minisblack")
        num_cases += 1
    return num_cases


def unique_case_id(stem: str, rel_path: Path, seen: Dict[str, int]) -> str:
    if stem not in seen:
        seen[stem] = 1
        return stem
    # collision: include directory path
    safe = re.sub(r"[^A-Za-z0-9_\\-]", "_", str(rel_path.parent))
    cid = f"{safe}__{stem}"
    seen[cid] = 1
    return cid


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-root", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--target-dz", type=float, default=0.396)
    ap.add_argument("--suffix", default="all_7ch")
    args = ap.parse_args()

    input_root = Path(args.input_root)
    out_root = Path(args.out_root)
    target_dz = float(args.target_dz)

    resampled_dir = out_root / f"zstacks_resampled_dz0p396_{args.suffix}"
    meta_dir = out_root / f"meta_{args.suffix}"
    input_dir = out_root / "inputs" / f"dz0p396_7ch_{args.suffix}" / "imagesTs"

    resampled_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)
    input_dir.mkdir(parents=True, exist_ok=True)

    ome_files = list(input_root.rglob("*.ome.tif"))
    ome_files.sort()

    manifest = {
        "target_dz": target_dz,
        "input_root": str(input_root),
        "count_total": len(ome_files),
        "processed": [],
        "skipped": [],
    }

    seen: Dict[str, int] = {}

    for path in ome_files:
        rel = path.relative_to(input_root)
        with tiff.TiffFile(path) as tf:
            dz = parse_dz_from_ome(tf.ome_metadata)

        if dz is None:
            # fallback: look for sibling with metadata
            for sib in path.parent.glob("*.ome.tif"):
                with tiff.TiffFile(sib) as tf:
                    dz = parse_dz_from_ome(tf.ome_metadata)
                if dz is not None:
                    break

        if dz is None:
            manifest["skipped"].append({"path": str(path), "reason": "missing_dz"})
            continue

        try:
            stack = load_stack(path)
        except Exception as exc:
            manifest["skipped"].append(
                {"path": str(path), "reason": f"read_error: {type(exc).__name__}"}
            )
            continue
        z = stack.shape[0]
        new_z = max(1, int(round(z * dz / target_dz)))
        stack_rs = resample_z_linear(stack, new_z)

        case_id = unique_case_id(path.stem, rel, seen)

        out_stack = resampled_dir / f"{case_id}_dz0p396.tif"
        tiff.imwrite(out_stack, stack_rs, photometric="minisblack")

        counts = save_slice_images(stack_rs, input_dir, case_id, k=3)

        meta = {
            "id": case_id,
            "source_path": str(path),
            "dz_original": dz,
            "dz_target": target_dz,
            "z_original": int(z),
            "z_resampled": int(new_z),
            "resample_ratio": float(dz / target_dz),
            "resampled_stack": str(out_stack),
            "cases_7ch": counts,
        }
        (meta_dir / f"{case_id}.json").write_text(json.dumps(meta, indent=2))
        manifest["processed"].append(meta)

    (out_root / f"manifest_inference_dz0p396_{args.suffix}.json").write_text(
        json.dumps(manifest, indent=2)
    )


if __name__ == "__main__":
    main()
