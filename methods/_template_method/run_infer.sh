#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH=${1:-"config.yaml"}
METHOD_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT_DIR=$(cd "${METHOD_DIR}/../.." && pwd)

if [[ ! -f "${METHOD_DIR}/${CONFIG_PATH}" && ! -f "${CONFIG_PATH}" ]]; then
  echo "Config not found: ${CONFIG_PATH}" >&2
  exit 1
fi

CONFIG_RESOLVED="${CONFIG_PATH}"
if [[ -f "${METHOD_DIR}/${CONFIG_PATH}" ]]; then
  CONFIG_RESOLVED="${METHOD_DIR}/${CONFIG_PATH}"
fi

mkdir -p "${METHOD_DIR}/outputs" "${ROOT_DIR}/data/06_inference/template_method"

python3 "${METHOD_DIR}/infer.py" --config "${CONFIG_RESOLVED}" \
  --method_dir "${METHOD_DIR}" \
  --root_dir "${ROOT_DIR}"
