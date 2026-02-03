#!/usr/bin/env bash
set -euo pipefail

# Project root (robust when sourced from any shell)
SCRIPT_PATH="${BASH_SOURCE[0]:-$0}"
SCRIPT_DIR=$(cd "$(dirname "$SCRIPT_PATH")" && pwd)
ROOT_DIR=$(cd "${SCRIPT_DIR}/../.." && pwd)
METHOD_DIR="${SCRIPT_DIR}"

# nnUNet v2 required environment variables
export nnUNet_raw="${ROOT_DIR}/data/00_raw/nnUNet_raw"
export nnUNet_preprocessed="${ROOT_DIR}/data/04_processed/nnUNet_preprocessed"
export nnUNet_results="${METHOD_DIR}/nnUNet_results"

# Optional: place inference outputs here by convention
export NNUNET_INFERENCE_DIR="${ROOT_DIR}/data/06_inference/nnunet"

# Activate local venv
export VIRTUAL_ENV="${METHOD_DIR}/.venv"
export PATH="${VIRTUAL_ENV}/bin:${PATH}"
