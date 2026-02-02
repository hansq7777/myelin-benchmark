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


class EarlyStopping:
    """Simple early stopping utility for validation metrics."""

    def __init__(
        self,
        patience: int = 20,
        min_delta: float = 0.001,
        mode: str = "min",
        min_epochs: int = 30,
        cooldown: int = 5,
    ) -> None:
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.min_epochs = min_epochs
        self.cooldown = cooldown
        self.best: float | None = None
        self.bad_epochs = 0
        self.cooldown_counter = 0

    def _improved(self, current: float) -> bool:
        if self.best is None:
            return True
        if self.mode == "min":
            return current < (self.best - self.min_delta)
        return current > (self.best + self.min_delta)

    def step(self, current: float, epoch: int) -> bool:
        """Return True if training should stop."""
        if epoch < self.min_epochs:
            return False

        if self._improved(current):
            self.best = current
            self.bad_epochs = 0
            self.cooldown_counter = self.cooldown
            return False

        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1
            return False

        self.bad_epochs += 1
        return self.bad_epochs >= self.patience

@dataclass
class Context:
    config: Dict[str, Any]
    method_dir: Path
    root_dir: Path


def train(ctx: Context) -> None:
    # TODO: implement data loading, model, optimizer, scheduler, training loop.
    # Use ctx.config to fetch hyperparameters and paths.
    # Example early stopping wiring:
    # es_cfg = ctx.config.get("training", {}).get("early_stopping", {})
    # early_stop = EarlyStopping(
    #     patience=int(es_cfg.get("patience", 20)),
    #     min_delta=float(es_cfg.get("min_delta", 0.001)),
    #     mode=str(es_cfg.get("mode", "min")),
    #     min_epochs=int(es_cfg.get("min_epochs", 30)),
    #     cooldown=int(es_cfg.get("cooldown", 5)),
    # )
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
