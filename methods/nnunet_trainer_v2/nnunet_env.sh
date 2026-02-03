#!/usr/bin/env bash
set -euo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]:-$0}"
SCRIPT_DIR=$(cd "$(dirname "$SCRIPT_PATH")" && pwd)
ROOT_DIR=$(cd "${SCRIPT_DIR}/../.." && pwd)
METHOD_DIR="${SCRIPT_DIR}"

export nnUNet_raw="${ROOT_DIR}/data/00_raw/nnUNet_raw"
export nnUNet_preprocessed="${ROOT_DIR}/data/04_processed/nnUNet_preprocessed"
export nnUNet_results="${METHOD_DIR}/nnUNet_results"

export VIRTUAL_ENV="${ROOT_DIR}/methods/nnunet/.venv"
export PATH="${VIRTUAL_ENV}/bin:${PATH}"
