#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GUARDRAILS_DIR="${ROOT_DIR}/tools/guardrails"

CONTRACT=""
LOG_FILE=""
STATUS_TSV=""
REPORT_JSON=""
HEARTBEAT_SEC=30
MODE="hybrid"
ADAPTER=""
PRECHECK_PY=""

usage() {
  cat <<EOF
Usage:
  $(basename "$0") --contract <json> --log <log_file> --status-tsv <tsv_file> [--adapter nnunet|dbt] [--report <json>] [--mode hybrid|strict|warn] [--heartbeat-sec 30] -- <command...>
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --contract) CONTRACT="$2"; shift 2 ;;
    --log) LOG_FILE="$2"; shift 2 ;;
    --status-tsv) STATUS_TSV="$2"; shift 2 ;;
    --adapter) ADAPTER="$2"; shift 2 ;;
    --report) REPORT_JSON="$2"; shift 2 ;;
    --heartbeat-sec) HEARTBEAT_SEC="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --) shift; break ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "${CONTRACT}" || -z "${LOG_FILE}" || -z "${STATUS_TSV}" || "$#" -eq 0 ]]; then
  usage
  exit 2
fi

if [[ -z "${ADAPTER}" ]]; then
  ADAPTER="$(python3 - "${CONTRACT}" <<'PY'
import json, sys
from pathlib import Path
contract = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(str(contract.get("adapter", "nnunet")))
PY
)"
fi

case "${ADAPTER}" in
  nnunet)
    PRECHECK_PY="${GUARDRAILS_DIR}/nnunet_preflight.py"
    ;;
  dbt)
    PRECHECK_PY="${GUARDRAILS_DIR}/dbt_preflight.py"
    ;;
  *)
    echo "unsupported adapter: ${ADAPTER}" >&2
    exit 2
    ;;
esac

if [[ ! -f "${PRECHECK_PY}" ]]; then
  echo "missing preflight script for adapter=${ADAPTER}: ${PRECHECK_PY}" >&2
  exit 2
fi

if [[ -z "${REPORT_JSON}" ]]; then
  REPORT_JSON="${STATUS_TSV%.tsv}_preflight.json"
fi

mkdir -p "$(dirname "${LOG_FILE}")" "$(dirname "${STATUS_TSV}")" "$(dirname "${REPORT_JSON}")"

status_log() {
  local event="$1"; shift
  local phase="$1"; shift
  local pid="$1"; shift
  local exit_code="$1"; shift
  local msg="${*:-}"
  printf "%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$(date '+%F %T')" "${event}" "${phase}" "${pid}" "${exit_code}" "${msg}" >> "${STATUS_TSV}"
}

echo -e "timestamp\tevent\tphase\tpid\texit_code\tmessage" > "${STATUS_TSV}"

CHILD_PID=""
CURRENT_PHASE="bootstrap"
IN_EXIT_HANDLER=0

on_signal() {
  local sig="$1"
  status_log "signal" "${CURRENT_PHASE}" "${CHILD_PID:-}" "" "received_${sig}"
  if [[ -n "${CHILD_PID}" ]] && kill -0 "${CHILD_PID}" 2>/dev/null; then
    kill -TERM "${CHILD_PID}" 2>/dev/null || true
  fi
}

on_exit() {
  local rc=$?
  if [[ "${IN_EXIT_HANDLER}" -eq 1 ]]; then
    return
  fi
  IN_EXIT_HANDLER=1
  trap - EXIT
  if [[ -n "${CHILD_PID}" ]] && kill -0 "${CHILD_PID}" 2>/dev/null; then
    status_log "child_cleanup" "${CURRENT_PHASE}" "${CHILD_PID}" "" "kill_on_exit"
    kill -TERM "${CHILD_PID}" 2>/dev/null || true
  fi
  status_log "script_exit" "${CURRENT_PHASE}" "${CHILD_PID:-}" "${rc}" "guarded_run_finished"
  exit "${rc}"
}

trap 'on_signal TERM' TERM
trap 'on_signal INT' INT
trap 'on_exit' EXIT

status_log "start" "preflight" "" "" "adapter=${ADAPTER};contract=${CONTRACT}"
set +e
python3 "${PRECHECK_PY}" --contract "${CONTRACT}" --report "${REPORT_JSON}" --mode "${MODE}" >> "${LOG_FILE}" 2>&1
pre_rc=$?
set -e
if [[ "${pre_rc}" -ne 0 ]]; then
  rc="${pre_rc}"
  status_log "preflight_fail" "preflight" "" "${rc}" "report=${REPORT_JSON}"
  exit "${rc}"
fi
status_log "preflight_pass" "preflight" "" "0" "report=${REPORT_JSON}"

CURRENT_PHASE="run"
"$@" >> "${LOG_FILE}" 2>&1 &
CHILD_PID=$!
status_log "child_start" "${CURRENT_PHASE}" "${CHILD_PID}" "" "started"

while kill -0 "${CHILD_PID}" 2>/dev/null; do
  rss_kb="$(awk '/VmRSS:/ {print $2}' "/proc/${CHILD_PID}/status" 2>/dev/null || true)"
  gpu_mib=""
  if command -v nvidia-smi >/dev/null 2>&1; then
    gpu_mib="$(nvidia-smi --query-compute-apps=pid,used_gpu_memory --format=csv,noheader,nounits 2>/dev/null \
      | awk -F',' -v p="${CHILD_PID}" '{gsub(/ /,"",$1); gsub(/ /,"",$2); if($1==p){print $2; exit}}' || true)"
  fi
  status_log "heartbeat" "${CURRENT_PHASE}" "${CHILD_PID}" "" "rss_kb=${rss_kb:-na};gpu_mib=${gpu_mib:-na}"
  sleep "${HEARTBEAT_SEC}"
done

rc=0
if ! wait "${CHILD_PID}"; then
  rc=$?
fi
status_log "child_exit" "${CURRENT_PHASE}" "${CHILD_PID}" "${rc}" "finished"
CHILD_PID=""
exit "${rc}"
