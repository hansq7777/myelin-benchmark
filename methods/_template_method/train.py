#!/usr/bin/env python3
"""Training entrypoint (template).

This file defines a minimal, professional training skeleton with:
- config loading
- deterministic settings
- structured logging
- explicit output directories

Replace TODO sections with method-specific logic.
"""

from __future__ import annotations

import argparse
import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import numpy as np
import yaml


def set_seed(seed: int, deterministic: bool) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        if deterministic:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except Exception:
        pass


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config_snapshot(config: Dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    snap_path = output_dir / "config.snapshot.json"
    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


@dataclass
class Context:
    config: Dict[str, Any]
    method_dir: Path
    root_dir: Path


def train(ctx: Context) -> None:
    # TODO: implement data loading, model, optimizer, scheduler, training loop.
    # Use ctx.config to fetch hyperparameters and paths.
    raise NotImplementedError("Training logic not implemented yet.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Myelin benchmark training (template)")
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    parser.add_argument("--method_dir", required=True, help="Method directory")
    parser.add_argument("--root_dir", required=True, help="Project root directory")
    args = parser.parse_args()

    config = load_config(args.config)
    method_dir = Path(args.method_dir)
    root_dir = Path(args.root_dir)

    seed = int(config.get("experiment", {}).get("seed", 42))
    deterministic = bool(config.get("experiment", {}).get("deterministic", True))
    set_seed(seed, deterministic)

    outputs_dir = method_dir / "outputs"
    save_config_snapshot(config, outputs_dir)

    ctx = Context(config=config, method_dir=method_dir, root_dir=root_dir)
    train(ctx)


if __name__ == "__main__":
    main()
