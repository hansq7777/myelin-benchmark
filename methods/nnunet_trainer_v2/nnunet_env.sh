#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
METHOD_DIR=$(cd "$(dirname "$0")" && pwd)

export nnUNet_raw="${ROOT_DIR}/data/00_raw/nnUNet_raw"
export nnUNet_preprocessed="${ROOT_DIR}/data/04_processed/nnUNet_preprocessed"
export nnUNet_results="${METHOD_DIR}/nnUNet_results"

export VIRTUAL_ENV="${ROOT_DIR}/methods/nnunet/.venv"
export PATH="${VIRTUAL_ENV}/bin:${PATH}"
