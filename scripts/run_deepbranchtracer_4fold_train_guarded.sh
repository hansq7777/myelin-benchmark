#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${ROOT_DIR}/logs"
mkdir -p "${LOG_DIR}"

RUN_TS="$(date +%Y%m%d_%H%M%S)"
GUARD_LOG="${LOG_DIR}/deepbranchtracer_4fold_guarded_${RUN_TS}.log"
STATUS_TSV="${LOG_DIR}/deepbranchtracer_4fold_guarded_${RUN_TS}.tsv"
REPORT_JSON="${LOG_DIR}/deepbranchtracer_4fold_guarded_${RUN_TS}_preflight.json"
CONTRACT_JSON="${LOG_DIR}/deepbranchtracer_4fold_guarded_${RUN_TS}_contract.json"

DBT_FOLD_ROOT="${DBT_FOLD_ROOT:-${ROOT_DIR}/methods/deepbranchtracer/data/myelin_4fold}"
DBT_EXP_ROOT="${DBT_EXP_ROOT:-${ROOT_DIR}/methods/deepbranchtracer/experiments/myelin_4fold_seed42_2stage}"
DBT_PREPARED_RELPATH="${DBT_PREPARED_RELPATH:-training_data_seed42_ok}"
DBT_FOLD_INDICES="${DBT_FOLD_INDICES:-[0,1,2,3]}"
GUARD_MODE="${GUARD_MODE:-hybrid}"
HEARTBEAT_SEC="${HEARTBEAT_SEC:-30}"

cat > "${CONTRACT_JSON}" <<JSON
{
  "adapter": "dbt",
  "critical_checks": ["nonempty", "dbt_structure", "split"],
  "dataset": {
    "fold_root": "${DBT_FOLD_ROOT}",
    "fold_indices": ${DBT_FOLD_INDICES},
    "prepared_relpath": "${DBT_PREPARED_RELPATH}",
    "train_subdir": "training_datasets",
    "test_subdir": "test_datasets",
    "min_train_cases": 1,
    "min_test_cases": 1,
    "sample_cases_per_split": 3,
    "required_patch_files": ["node_img.tif", "node_matrix_1.txt", "node_matrix_2.txt", "node_matrix_3.txt"],
    "case_dir_pattern": "^.+_z[0-9]+$",
    "suspicious_globs": ["training_data_seed42training_datasets*"]
  },
  "output": {
    "path": "${DBT_EXP_ROOT}",
    "allow_nonempty": true
  }
}
JSON

echo "guard_log=${GUARD_LOG}"
echo "status_tsv=${STATUS_TSV}"
echo "report_json=${REPORT_JSON}"
echo "contract_json=${CONTRACT_JSON}"

"${ROOT_DIR}/scripts/nnunet_guarded_run.sh" \
  --adapter dbt \
  --contract "${CONTRACT_JSON}" \
  --log "${GUARD_LOG}" \
  --status-tsv "${STATUS_TSV}" \
  --report "${REPORT_JSON}" \
  --mode "${GUARD_MODE}" \
  --heartbeat-sec "${HEARTBEAT_SEC}" \
  -- bash "${ROOT_DIR}/scripts/run_deepbranchtracer_4fold_train.sh" "$@"
