#!/usr/bin/env python3
"""Inference entrypoint (template).

This file defines a minimal, professional inference skeleton with:
- config loading
- explicit output directory
- placeholder for post-processing and metrics export
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_run_metadata(config: Dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    meta_path = output_dir / "inference.metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


@dataclass
class Context:
    config: Dict[str, Any]
    method_dir: Path
    root_dir: Path


def infer(ctx: Context) -> None:
    # TODO: implement model loading, inference loop, output writing.
    # Write predictions to data/06_inference/<method_name>/
    raise NotImplementedError("Inference logic not implemented yet.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Myelin benchmark inference (template)")
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    parser.add_argument("--method_dir", required=True, help="Method directory")
    parser.add_argument("--root_dir", required=True, help="Project root directory")
    args = parser.parse_args()

    config = load_config(args.config)
    method_dir = Path(args.method_dir)
    root_dir = Path(args.root_dir)

    outputs_dir = method_dir / "outputs"
    save_run_metadata(config, outputs_dir)

    ctx = Context(config=config, method_dir=method_dir, root_dir=root_dir)
    infer(ctx)


if __name__ == "__main__":
    main()
