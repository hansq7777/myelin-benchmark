#!/usr/bin/env python3
"""
Prepare inference inputs for nnUNet (2D) from selected zstacks.

- Resample along Z to a target dz (linear interpolation).
- Keep XY unchanged.
- Generate per-slice cases with channel files: case_id_0000.tif, case_id_0001.tif, ...
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, Optional, Tuple
import xml.etree.ElementTree as ET

import numpy as np
import tifffile as tiff

PROJECT_ROOT = Path("/home/dilgerlab/Siqi/myelin-benchmark")
OUT_ROOT = PROJECT_ROOT / "data/06_inference/nnunet"
TARGET_DZ = 0.396  # um

STACKS = [
    {
        "id": "slice_144_left_hemisphere_S1BF_S05",
        "path": PROJECT_ROOT
        / "data/00_raw/20241206_s1bf/slice_144_left_hemisphere_S1BF_ometiff"
        / "slice_144_left_hemisphere_S1BF_S05.ome.tif",
        "fallback_dz_path": None,
    },
    {
        "id": "slice_144_left_hemisphere_S1BF_S12",
        "path": PROJECT_ROOT
        / "data/00_raw/20241206_s1bf/slice_144_left_hemisphere_S1BF_ometiff"
        / "slice_144_left_hemisphere_S1BF_S12.ome.tif",
        "fallback_dz_path": None,
    },
    {
        "id": "pig_hippocampus_2x2_S02",
        "path": PROJECT_ROOT
        / "data/00_raw/20241206_pig_hippocampus/pig_hippocampus_2x2_ometiff"
        / "pig_hippocampus_2x2_S02.ome.tif",
        "fallback_dz_path": None,
    },
    {
        "id": "2504_42_L_M1_S01",
        "path": Path(
            "/dfs/snout/Histology/RND2412/Microscopy data/Confocal scans/202512_8rats_3ROIs/2504_42_L_M1/2504_42_L_M1_S01.ome.tif"
        ),
        "fallback_dz_path": Path(
            "/dfs/snout/Histology/RND2412/Microscopy data/Confocal scans/202512_8rats_3ROIs/2504_42_L_M1/2504_42_L_M1_S00.ome.tif"
        ),
    },
    {
        "id": "2505_48_L_PL_S13",
        "path": Path(
            "/dfs/snout/Histology/RND2412/Microscopy data/Confocal scans/202512_8rats_3ROIs/2505_48_L_PL/2505_48_L_PL_S13.ome.tif"
        ),
        "fallback_dz_path": None,
    },
    {
        "id": "2507_54_R_IL_S10",
        "path": Path(
            "/dfs/snout/Histology/RND2412/Microscopy data/Confocal scans/202512_8rats_3ROIs/2507_54_R_IL/2507_54_R_IL_S10.ome.tif"
        ),
        "fallback_dz_path": None,
    },
]


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
    # positions in original index space
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


def save_slice_images(stack: np.ndarray, out_dir: Path, case_prefix: str, k: int) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    z, y, x = stack.shape
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


def main() -> None:
    resampled_dir = OUT_ROOT / "zstacks_resampled_dz0p396"
    meta_dir = OUT_ROOT / "meta"
    resampled_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    channel_configs = {
        1: 0,  # 1ch
        3: 1,  # 3ch
        5: 2,  # 5ch
        7: 3,  # 7ch
    }
    input_dirs = {
        ch: OUT_ROOT / "inputs" / f"dz0p396_{ch}ch" / "imagesTs"
        for ch in channel_configs
    }

    manifest = {"target_dz": TARGET_DZ, "stacks": []}

    for item in STACKS:
        path = Path(item["path"])
        if not path.exists():
            raise FileNotFoundError(f"Missing stack: {path}")
        with tiff.TiffFile(path) as tf:
            dz = parse_dz_from_ome(tf.ome_metadata)
        if dz is None and item.get("fallback_dz_path"):
            fb = Path(item["fallback_dz_path"])
            with tiff.TiffFile(fb) as tf:
                dz = parse_dz_from_ome(tf.ome_metadata)
        if dz is None:
            raise RuntimeError(f"Missing dz for {path}")

        stack = load_stack(path)
        z = stack.shape[0]
        new_z = max(1, int(round(z * dz / TARGET_DZ)))
        stack_rs = resample_z_linear(stack, new_z)

        out_stack = resampled_dir / f"{item['id']}_dz0p396.tif"
        tiff.imwrite(out_stack, stack_rs, photometric="minisblack")

        # write slices for each channel config
        counts = {}
        for ch, k in channel_configs.items():
            counts[ch] = save_slice_images(stack_rs, input_dirs[ch], item["id"], k)

        meta = {
            "id": item["id"],
            "source_path": str(path),
            "dz_original": dz,
            "dz_target": TARGET_DZ,
            "z_original": int(z),
            "z_resampled": int(new_z),
            "resample_ratio": float(dz / TARGET_DZ),
            "resampled_stack": str(out_stack),
            "cases_per_channel": counts,
        }
        (meta_dir / f"{item['id']}.json").write_text(json.dumps(meta, indent=2))
        manifest["stacks"].append(meta)

    (OUT_ROOT / "manifest_inference_dz0p396.json").write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
