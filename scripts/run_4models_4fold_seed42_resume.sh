#!/usr/bin/env bash
set -euo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]:-$0}"
ROOT_DIR=$(cd "$(dirname "$SCRIPT_PATH")/.." && pwd)

export PYTHONHASHSEED=42
export NNUNET_SEED=42

run_fold() {
  local method_dir="$1"
  local dataset_id="$2"
  local dataset_name="$3"
  local trainer="$4"
  local plans="$5"
  local config="$6"
  local fold="$7"

  # shellcheck source=/dev/null
  source "${ROOT_DIR}/methods/${method_dir}/nnunet_env.sh"

  local fold_dir="${nnUNet_results}/${dataset_name}/${trainer}__${plans}__${config}/fold_${fold}"
  if [ -f "${fold_dir}/checkpoint_latest.pth" ]; then
    echo "[resume] ${method_dir} ${dataset_name} fold ${fold}"
    nnUNetv2_train "${dataset_id}" "${config}" "${fold}" -tr "${trainer}" -p "${plans}" --c
  elif [ -f "${fold_dir}/checkpoint_final.pth" ]; then
    echo "[skip] ${method_dir} ${dataset_name} fold ${fold} (checkpoint_final exists)"
  else
    echo "[start] ${method_dir} ${dataset_name} fold ${fold}"
    nnUNetv2_train "${dataset_id}" "${config}" "${fold}" -tr "${trainer}" -p "${plans}"
  fi
}

run_folds() {
  local method_dir="$1"
  local dataset_id="$2"
  local dataset_name="$3"
  local trainer="$4"
  local plans="$5"
  local config="2d"

  for f in 0 1 2 3; do
    run_fold "${method_dir}" "${dataset_id}" "${dataset_name}" "${trainer}" "${plans}" "${config}" "${f}"
  done
}

run_folds "nnunet_dice_cldice" 1 "Dataset001_20241206_MyelinConfData" "nnUNetTrainerCLDice" "nnUNetPlans"
run_folds "nnunet_dice_cldice_ms" 1 "Dataset001_20241206_MyelinConfData" "nnUNetTrainerCLDiceMS" "nnUNetPlans"
run_folds "nnunet_oversample066" 1 "Dataset001_20241206_MyelinConfData" "nnUNetTrainerOversample066" "nnUNetPlans"
run_folds "nnunet_k2_5ch" 2 "Dataset002_20241206_MyelinConfData_5ch" "nnUNetTrainer" "nnUNetPlans"
