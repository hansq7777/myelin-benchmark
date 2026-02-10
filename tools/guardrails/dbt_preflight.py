#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional, Set


@dataclass
class Issue:
    severity: str  # error|warn
    check: str
    message: str
    context: str = ""


def _as_path(v: Optional[str]) -> Optional[Path]:
    return Path(v).expanduser().resolve() if v else None


def _issue_level(check: str, critical_checks: Set[str]) -> str:
    return "error" if check in critical_checks else "warn"


def _add_issue(issues: List[Issue], check: str, msg: str, critical_checks: Set[str], context: str = "") -> None:
    issues.append(Issue(_issue_level(check, critical_checks), check, msg, context))


def _count_files(root: Path) -> int:
    if not root.exists():
        return 0
    if root.is_file():
        return 1
    return sum(1 for p in root.rglob("*") if p.is_file())


def _check_output(out_cfg: dict, critical_checks: Set[str], issues: List[Issue], stats: dict) -> None:
    out_path = _as_path(out_cfg.get("path"))
    if out_path is None:
        return
    allow_nonempty = bool(out_cfg.get("allow_nonempty", False))
    exists = out_path.exists()
    file_count = _count_files(out_path)
    stats["output"] = {
        "path": str(out_path),
        "exists": exists,
        "file_count": file_count,
        "allow_nonempty": allow_nonempty,
    }
    if exists and file_count > 0 and not allow_nonempty:
        _add_issue(
            issues,
            "overwrite",
            f"output is non-empty and allow_nonempty=false: {out_path}",
            critical_checks,
            context=f"file_count={file_count}",
        )


def _check_case_dirs(
    split_name: str,
    split_dir: Path,
    min_cases: int,
    case_dir_pattern: Optional[str],
    required_patch_files: List[str],
    sample_cases_per_split: int,
    critical_checks: Set[str],
    issues: List[Issue],
) -> dict:
    if not split_dir.is_dir():
        _add_issue(issues, "nonempty", f"[{split_name}] missing dir: {split_dir}", critical_checks)
        return {"n_cases": 0, "sample_checked": 0}

    case_dirs = sorted([p for p in split_dir.iterdir() if p.is_dir()])
    n_cases = len(case_dirs)
    if n_cases < min_cases:
        _add_issue(
            issues,
            "nonempty",
            f"[{split_name}] too few cases: {n_cases} < {min_cases}",
            critical_checks,
            context=str(split_dir),
        )

    if case_dir_pattern:
        rx = re.compile(case_dir_pattern)
        bad = [p.name for p in case_dirs if not rx.match(p.name)]
        if bad:
            _add_issue(
                issues,
                "split",
                f"[{split_name}] case name pattern mismatch: {len(bad)}",
                critical_checks,
                context=", ".join(bad[:5]),
            )

    sample_checked = 0
    for case_dir in case_dirs[: max(0, sample_cases_per_split)]:
        patch_dirs = sorted([p for p in case_dir.iterdir() if p.is_dir()])
        if not patch_dirs:
            _add_issue(
                issues,
                "dbt_structure",
                f"[{split_name}] case has no patch dirs: {case_dir.name}",
                critical_checks,
            )
            continue
        patch = patch_dirs[0]
        missing = [f for f in required_patch_files if not (patch / f).is_file()]
        if missing:
            _add_issue(
                issues,
                "dbt_structure",
                f"[{split_name}] patch missing required files: {case_dir.name}/{patch.name}",
                critical_checks,
                context="missing=" + ",".join(missing),
            )
        sample_checked += 1

    return {"n_cases": n_cases, "sample_checked": sample_checked}


def _check_dataset(dataset_cfg: dict, critical_checks: Set[str], issues: List[Issue], stats: dict) -> None:
    fold_root = _as_path(dataset_cfg.get("fold_root"))
    if fold_root is None or not fold_root.is_dir():
        _add_issue(issues, "nonempty", f"dataset.fold_root missing: {fold_root}", critical_checks)
        return

    fold_indices = dataset_cfg.get("fold_indices", [0, 1, 2, 3])
    prepared_relpath = dataset_cfg.get("prepared_relpath", "training_data_seed42_ok")
    train_subdir = dataset_cfg.get("train_subdir", "training_datasets")
    test_subdir = dataset_cfg.get("test_subdir", "test_datasets")
    min_train_cases = int(dataset_cfg.get("min_train_cases", 1))
    min_test_cases = int(dataset_cfg.get("min_test_cases", 1))
    case_dir_pattern = dataset_cfg.get("case_dir_pattern", r"^.+_z\d+$")
    sample_cases_per_split = int(dataset_cfg.get("sample_cases_per_split", 3))
    required_patch_files = dataset_cfg.get(
        "required_patch_files",
        ["node_img.tif", "node_matrix_1.txt", "node_matrix_2.txt", "node_matrix_3.txt"],
    )
    suspicious_globs = dataset_cfg.get("suspicious_globs", ["training_data_seed42training_datasets*"])

    dataset_stats = {
        "fold_root": str(fold_root),
        "fold_indices": fold_indices,
        "folds": {},
    }

    for fold in fold_indices:
        fold_name = f"fold{fold}"
        fold_dir = fold_root / fold_name
        if not fold_dir.is_dir():
            _add_issue(issues, "split", f"missing fold dir: {fold_dir}", critical_checks)
            continue

        prepared_dir = fold_dir / prepared_relpath
        train_dir = prepared_dir / train_subdir
        test_dir = prepared_dir / test_subdir

        train_stat = _check_case_dirs(
            f"{fold_name}:train",
            train_dir,
            min_train_cases,
            case_dir_pattern,
            required_patch_files,
            sample_cases_per_split,
            critical_checks,
            issues,
        )
        test_stat = _check_case_dirs(
            f"{fold_name}:test",
            test_dir,
            min_test_cases,
            case_dir_pattern,
            required_patch_files,
            sample_cases_per_split,
            critical_checks,
            issues,
        )

        if train_dir.is_dir() and test_dir.is_dir():
            train_cases = {p.name for p in train_dir.iterdir() if p.is_dir()}
            test_cases = {p.name for p in test_dir.iterdir() if p.is_dir()}
            overlap = train_cases & test_cases
            if overlap:
                _add_issue(
                    issues,
                    "split",
                    f"{fold_name} train/test overlap: {len(overlap)}",
                    critical_checks,
                    context=", ".join(sorted(list(overlap))[:5]),
                )

        suspicious_hits = []
        for pat in suspicious_globs:
            suspicious_hits.extend([str(p) for p in fold_dir.glob(pat)])
        if suspicious_hits:
            _add_issue(
                issues,
                "dbt_hygiene",
                f"{fold_name} suspicious paths found: {len(suspicious_hits)}",
                critical_checks,
                context="; ".join(suspicious_hits[:5]),
            )

        dataset_stats["folds"][fold_name] = {
            "prepared_dir": str(prepared_dir),
            "train": train_stat,
            "test": test_stat,
        }

    stats["dataset"] = dataset_stats


def main() -> int:
    ap = argparse.ArgumentParser(description="Hybrid preflight checks for DeepBranchTracer runs")
    ap.add_argument("--contract", required=True, help="Run contract JSON path")
    ap.add_argument("--report", required=True, help="Output report JSON path")
    ap.add_argument("--mode", choices=["strict", "hybrid", "warn"], default="hybrid")
    args = ap.parse_args()

    contract_path = Path(args.contract).resolve()
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    critical_checks_cfg = set(contract.get("critical_checks", []))
    if not critical_checks_cfg:
        if args.mode in {"strict", "hybrid"}:
            critical_checks_cfg = {"nonempty", "dbt_structure", "split", "overwrite"}
        else:
            critical_checks_cfg = set()

    issues: List[Issue] = []
    stats: dict = {"contract": str(contract_path)}

    dataset_cfg = contract.get("dataset", {})
    _check_dataset(dataset_cfg, critical_checks_cfg, issues, stats)

    out_cfg = contract.get("output")
    if out_cfg:
        _check_output(out_cfg, critical_checks_cfg, issues, stats)

    errors = [asdict(i) for i in issues if i.severity == "error"]
    warns = [asdict(i) for i in issues if i.severity == "warn"]
    ok = len(errors) == 0
    report = {
        "ok": ok,
        "mode": args.mode,
        "adapter": "dbt",
        "critical_checks": sorted(list(critical_checks_cfg)),
        "stats": stats,
        "errors": errors,
        "warnings": warns,
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"preflight_ok={ok} errors={len(errors)} warnings={len(warns)} report={report_path}")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
