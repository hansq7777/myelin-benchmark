#!/usr/bin/env python3
"""Read CZI metadata and report stage positions and scaling.

Usage:
  python read_czi_meta.py /path/to/file.czi
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from czifile import CziFile


def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def read_xyz(node: ET.Element) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    def get_val(key: str) -> Optional[float]:
        val = node.get(key)
        if val is None:
            val = node.get(key.lower())
        if val is None:
            val = node.findtext(key)
        if val is None:
            val = node.findtext(key.lower())
        if val is None:
            return None
        try:
            return float(val)
        except Exception:
            return None

    return get_val("X"), get_val("Y"), get_val("Z")


def parse_scaling(root: ET.Element) -> Dict[str, Tuple[Optional[float], Optional[str]]]:
    scaling: Dict[str, Tuple[Optional[float], Optional[str]]] = {}
    for dist in root.findall(".//Scaling//Distance"):
        dist_id = dist.get("Id") or dist.get("id") or strip_ns(dist.tag)
        val_text = dist.findtext("Value")
        unit_text = dist.findtext("DefaultUnit") or dist.findtext("Unit")
        val = None
        if val_text is not None:
            try:
                val = float(val_text)
            except Exception:
                val = None
        if dist_id:
            scaling[dist_id] = (val, unit_text)
    return scaling


def parse_scene_positions(root: ET.Element) -> List[Dict[str, Optional[float]]]:
    scenes = root.findall(".//Scenes//Scene")
    if not scenes:
        scenes = root.findall(".//Scene")
    results: List[Dict[str, Optional[float]]] = []
    for idx, scene in enumerate(scenes):
        pos = {"scene_index": idx, "x": None, "y": None, "z": None}
        found = False
        for node in scene.iter():
            tag = strip_ns(node.tag).lower()
            if tag in {"centerposition", "stageposition", "position"}:
                x, y, z = read_xyz(node)
                if x is not None or y is not None or z is not None:
                    pos["x"], pos["y"], pos["z"] = x, y, z
                    found = True
                    break
        if not found:
            # Try any element that has X/Y/Z attributes
            for node in scene.iter():
                x, y, z = read_xyz(node)
                if x is not None or y is not None or z is not None:
                    pos["x"], pos["y"], pos["z"] = x, y, z
                    break
        results.append(pos)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Read CZI metadata and report scaling and stage positions")
    parser.add_argument("czi_path", type=str, help="Path to .czi file")
    parser.add_argument("--max-scenes", type=int, default=10, help="Max scene entries to print")
    args = parser.parse_args()

    czi_path = Path(args.czi_path)
    if not czi_path.exists():
        print(f"File not found: {czi_path}", file=sys.stderr)
        return 1

    with CziFile(czi_path) as czi:
        axes = czi.axes
        shape = czi.shape
        dims = dict(zip(axes, shape))
        meta_xml = czi.metadata()

    if isinstance(meta_xml, bytes):
        meta_xml = meta_xml.decode("utf-8", errors="ignore")

    root = ET.fromstring(meta_xml)

    scaling = parse_scaling(root)
    scene_positions = parse_scene_positions(root)

    print(f"File: {czi_path}")
    print(f"Axes: {axes}")
    print(f"Shape: {shape}")
    print(f"Scenes (S): {dims.get('S', 1)}")
    print(f"Z slices (Z): {dims.get('Z', 1)}")

    def fmt_scale(key: str) -> str:
        if key not in scaling:
            return "not found"
        val, unit = scaling[key]
        if val is None:
            return f"value missing (unit={unit})"
        return f"{val} {unit or ''}".strip()

    print(f"XY resolution X: {fmt_scale('X')}")
    print(f"XY resolution Y: {fmt_scale('Y')}")
    print(f"Z spacing/thickness: {fmt_scale('Z')}")

    if scene_positions:
        print("Stage coordinates (per scene):")
        for pos in scene_positions[: args.max_scenes]:
            print(f"  scene {pos['scene_index']}: X={pos['x']} Y={pos['y']} Z={pos['z']}")
        if len(scene_positions) > args.max_scenes:
            print(f"  ... {len(scene_positions) - args.max_scenes} more scenes")
    else:
        print("Stage coordinates: not found in metadata")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
