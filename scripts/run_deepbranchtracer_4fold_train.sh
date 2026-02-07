#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DBT_DIR="${ROOT_DIR}/methods/deepbranchtracer"
DATA_ROOT="${DBT_DIR}/data/myelin_4fold"
EXP_ROOT="${DBT_DIR}/experiments/myelin_4fold_seed42_2stage"
TRAIN_SCRIPT="${DBT_DIR}/train_2D.py"
SEED=42
DBT_PY="${DBT_DIR}/.venv/bin/python"
PREPARE_FIRST="${PREPARE_FIRST:-0}"
BATCH_SIZE="${BATCH_SIZE:-8}"
START_FOLD="${START_FOLD:-0}"
END_FOLD="${END_FOLD:-3}"
N_THREADS="${N_THREADS:-0}"
GPU_ID="${GPU_ID:-0}"
STAGE1_EPOCHS="${STAGE1_EPOCHS:-40}"
STAGE2_EPOCHS="${STAGE2_EPOCHS:-30}"
STAGE1_LR="${STAGE1_LR:-5e-5}"
STAGE2_LR="${STAGE2_LR:-2e-5}"
WEIGHT_DECAY="${WEIGHT_DECAY:-1e-5}"
EARLY_STOP_PATIENCE="${EARLY_STOP_PATIENCE:-8}"
EARLY_STOP_MIN_DELTA="${EARLY_STOP_MIN_DELTA:-0.001}"
EARLY_STOP_MIN_EPOCHS="${EARLY_STOP_MIN_EPOCHS:-12}"
MAX_RETRIES_PER_STAGE="${MAX_RETRIES_PER_STAGE:-1}"
RETRY_SLEEP_SEC="${RETRY_SLEEP_SEC:-10}"
HEARTBEAT_SEC="${HEARTBEAT_SEC:-30}"
RUN_STAGE1="${RUN_STAGE1:-1}"
RUN_STAGE2="${RUN_STAGE2:-1}"
export PYTHONUNBUFFERED=1

mkdir -p "${EXP_ROOT}"
if [[ ! -x "${DBT_PY}" ]]; then
  echo "Python env not found: ${DBT_PY}"
  exit 1
fi

RUN_TS="$(date +%Y%m%d_%H%M%S)"
RUN_LOG_DIR="${ROOT_DIR}/logs"
mkdir -p "${RUN_LOG_DIR}"
MASTER_LOG="${RUN_LOG_DIR}/deepbranchtracer_4fold_unified_${RUN_TS}.log"
SUMMARY_TSV="${RUN_LOG_DIR}/deepbranchtracer_4fold_unified_${RUN_TS}.tsv"
RESOURCE_LOG="${RUN_LOG_DIR}/deepbranchtracer_4fold_resources_${RUN_TS}.log"
LOCK_FILE="${RUN_LOG_DIR}/deepbranchtracer_4fold_train.lock"

exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  echo "Another DBT 4-fold run is active (lock: ${LOCK_FILE}). Exit."
  exit 1
fi

echo -e "fold\tstage\tstatus\tattempts\texit_code\tpid\tcheckpoint\terror_type\terror_snippet\tlog_file" > "${SUMMARY_TSV}"

sanitize_one_line() {
  local s="$1"
  s="${s//$'\t'/ }"
  s="${s//$'\n'/ }"
  echo "${s}" | sed 's/  \+/ /g'
}

classify_error_type() {
  local stage_log="$1"
  if rg -q "AcosBackward0|returned nan values" "${stage_log}"; then
    echo "AcosBackward0_NaN"
  elif rg -q "CUDA out of memory|OutOfMemoryError|CUDNN_STATUS_NOT_SUPPORTED" "${stage_log}"; then
    echo "CUDA_OOM"
  elif rg -q "ValueError|IndexError|KeyError|TypeError|AssertionError" "${stage_log}"; then
    echo "Python_ValueOrIndex"
  elif rg -q "No such file|not found|FileNotFoundError" "${stage_log}"; then
    echo "Missing_File"
  elif rg -q "killed|Killed" "${stage_log}"; then
    echo "Process_Killed"
  elif rg -q "Traceback|RuntimeError|Exception|Error" "${stage_log}"; then
    echo "Runtime_Error"
  else
    echo "Unknown"
  fi
}

append_summary_row() {
  local fold="$1"
  local stage="$2"
  local status="$3"
  local attempts="$4"
  local exit_code="$5"
  local pid="$6"
  local checkpoint="$7"
  local error_type="$8"
  local error_snippet="$9"
  local log_file="${10}"
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "${fold}" "${stage}" "${status}" "${attempts}" "${exit_code}" "${pid}" \
    "${checkpoint}" "${error_type}" "$(sanitize_one_line "${error_snippet}")" "${log_file}" >> "${SUMMARY_TSV}"
}

RUN_STAGE_LAST_CKPT=""
CURRENT_FOLD="NA"
CURRENT_STAGE="NA"
CURRENT_ATTEMPTS="NA"
CURRENT_STAGE_LOG="NA"
CURRENT_PID="NA"

record_trap_summary() {
  local exit_code="$?"
  if [[ "${CURRENT_STAGE}" == "NA" ]]; then
    return
  fi
  local error_type="Process_Exit"
  local error_snippet="trap_exit"
  if [[ "${exit_code}" -ne 0 ]]; then
    error_type="Process_Exit_${exit_code}"
  fi
  if [[ -n "${CURRENT_STAGE_LOG}" && "${CURRENT_STAGE_LOG}" != "NA" && -f "${CURRENT_STAGE_LOG}" ]]; then
    error_snippet="$(tail -n 5 "${CURRENT_STAGE_LOG}" | paste -sd ';' -)"
  fi
  append_summary_row "${CURRENT_FOLD}" "${CURRENT_STAGE}" "aborted" "${CURRENT_ATTEMPTS}" "${exit_code}" "${CURRENT_PID}" "NA" "${error_type}" "${error_snippet}" "${CURRENT_STAGE_LOG}"
  echo "[$(date +'%F %T')] trap exit: fold=${CURRENT_FOLD} stage=${CURRENT_STAGE} exit=${exit_code}" | tee -a "${MASTER_LOG}"
}

trap record_trap_summary SIGINT SIGTERM EXIT

run_stage_train() {
  local fold="$1"
  local stage="$2"
  local train_seg_flag="$3"
  local to_restore_flag="$4"
  local restore_ckpt="$5"
  local epochs="$6"
  local lr="$7"
  local model_root="$8"
  local log_root="$9"
  local prep_root="${10}"

  local attempts=0
  local max_attempts=$((MAX_RETRIES_PER_STAGE + 1))
  local exit_code=0
  local stage_status="failed"
  local stage_ckpt="NA"
  local err_type="NA"
  local err_snippet="NA"
  local stage_log=""
  local hb_sec="${HEARTBEAT_SEC}"

  if [[ "${hb_sec}" -lt 5 ]]; then
    hb_sec=5
  fi

  mkdir -p "${log_root}"
  mkdir -p "${model_root}"

  while (( attempts < max_attempts )); do
    attempts=$((attempts + 1))
    stage_log="${RUN_LOG_DIR}/deepbranchtracer_fold${fold}_${stage}_attempt${attempts}_${RUN_TS}.log"
    CURRENT_FOLD="${fold}"
    CURRENT_STAGE="${stage}"
    CURRENT_ATTEMPTS="${attempts}"
    CURRENT_STAGE_LOG="${stage_log}"
    echo "[$(date +'%F %T')] fold${fold} ${stage} attempt ${attempts}/${max_attempts}" | tee -a "${MASTER_LOG}"

    set +e
    if [[ "${to_restore_flag}" == "true" ]]; then
      "${DBT_PY}" -u "${TRAIN_SCRIPT}" \
        --train_or_test train \
        --train_seg "${train_seg_flag}" \
        --to_restore true \
        --restore_ckpt "${restore_ckpt}" \
        --gpu_id "${GPU_ID}" \
        --n_threads "${N_THREADS}" \
        --seed "${SEED}" \
        --batch_size "${BATCH_SIZE}" \
        --epochs "${epochs}" \
        --lr "${lr}" \
        --weight_decay "${WEIGHT_DECAY}" \
        --early_stop_patience "${EARLY_STOP_PATIENCE}" \
        --early_stop_min_delta "${EARLY_STOP_MIN_DELTA}" \
        --early_stop_min_epochs "${EARLY_STOP_MIN_EPOCHS}" \
        --dataset_img_path "${prep_root}/training_datasets/" \
        --dataset_img_test_path "${prep_root}/test_datasets/" \
        --model_save_dir "${model_root}" \
        --log_save_dir "${log_root}" > "${stage_log}" 2>&1 &
    else
      "${DBT_PY}" -u "${TRAIN_SCRIPT}" \
        --train_or_test train \
        --train_seg "${train_seg_flag}" \
        --to_restore false \
        --gpu_id "${GPU_ID}" \
        --n_threads "${N_THREADS}" \
        --seed "${SEED}" \
        --batch_size "${BATCH_SIZE}" \
        --epochs "${epochs}" \
        --lr "${lr}" \
        --weight_decay "${WEIGHT_DECAY}" \
        --early_stop_patience "${EARLY_STOP_PATIENCE}" \
        --early_stop_min_delta "${EARLY_STOP_MIN_DELTA}" \
        --early_stop_min_epochs "${EARLY_STOP_MIN_EPOCHS}" \
        --dataset_img_path "${prep_root}/training_datasets/" \
        --dataset_img_test_path "${prep_root}/test_datasets/" \
        --model_save_dir "${model_root}" \
        --log_save_dir "${log_root}" > "${stage_log}" 2>&1 &
    fi

    local train_pid=$!
    CURRENT_PID="${train_pid}"
    local start_ts
    start_ts=$(date +%s)
    while kill -0 "${train_pid}" 2>/dev/null; do
      sleep "${hb_sec}"
      if ! kill -0 "${train_pid}" 2>/dev/null; then
        break
      fi
      local now_ts
      now_ts=$(date +%s)
      local elapsed=$((now_ts - start_ts))
      local last_line
      last_line=$(tail -n 1 "${stage_log}" 2>/dev/null || true)
      echo "[$(date +'%F %T')] heartbeat fold${fold} ${stage} pid=${train_pid} elapsed=${elapsed}s last_log='${last_line}'" | tee -a "${MASTER_LOG}"
      if command -v nvidia-smi >/dev/null 2>&1; then
        local gpu_line
        gpu_line=$(nvidia-smi --query-gpu=timestamp,index,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits | head -n 1)
        echo "[$(date +'%F %T')] pid=${train_pid} gpu=${gpu_line}" >> "${RESOURCE_LOG}"
      fi
      if command -v free >/dev/null 2>&1; then
        local mem_line
        mem_line=$(free -m | awk 'NR==2{print $3\"/\"$2\"MB\"}')
        echo "[$(date +'%F %T')] pid=${train_pid} mem=${mem_line}" >> "${RESOURCE_LOG}"
      fi
      if command -v ps >/dev/null 2>&1; then
        local rss_kb
        rss_kb=$(ps -o rss= -p "${train_pid}" | tr -d ' ')
        echo "[$(date +'%F %T')] pid=${train_pid} rss_kb=${rss_kb}" >> "${RESOURCE_LOG}"
      fi
      if command -v df >/dev/null 2>&1; then
        local df_line
        df_line=$(df -h "${ROOT_DIR}" | awk 'NR==2{print $3"/"$2" used="$5}')
        echo "[$(date +'%F %T')] pid=${train_pid} disk=${df_line}" >> "${RESOURCE_LOG}"
      fi
    done
    wait "${train_pid}"
    exit_code=$?
    set -e

    local run_dir="${model_root}${GPU_ID}/${epochs}_${BATCH_SIZE}"
    local best_ckpt="${run_dir}/checkpoint_best.pth"
    local final_ckpt="${run_dir}/checkpoint_final.pth"
    if [[ -f "${best_ckpt}" ]]; then
      stage_ckpt="${best_ckpt}"
    elif [[ -f "${final_ckpt}" ]]; then
      stage_ckpt="${final_ckpt}"
    fi

    if [[ "${exit_code}" -eq 0 ]]; then
      stage_status="ok"
      append_summary_row "${fold}" "${stage}" "${stage_status}" "${attempts}" "${exit_code}" "${train_pid}" "${stage_ckpt}" "NA" "NA" "${stage_log}"
      echo "[$(date +'%F %T')] fold${fold} ${stage} success, ckpt=${stage_ckpt}" | tee -a "${MASTER_LOG}"
      RUN_STAGE_LAST_CKPT="${stage_ckpt}"
      CURRENT_STAGE="NA"
      CURRENT_STAGE_LOG="NA"
      CURRENT_PID="NA"
      return 0
    fi

    err_type="$(classify_error_type "${stage_log}")"
    err_snippet="$(
      {
        tail -n 120 "${stage_log}" \
          | rg -n "Traceback|RuntimeError|ValueError|Error|Exception|AcosBackward0|out of memory|No such file|not found" \
          | tail -n 6 \
          | paste -sd ';' -
      } || true
    )"
    if [[ -z "${err_snippet}" ]]; then
      err_snippet="no traceback signature captured; inspect full stage log"
    fi
    append_summary_row "${fold}" "${stage}" "failed" "${attempts}" "${exit_code}" "${train_pid}" "${stage_ckpt}" "${err_type}" "${err_snippet}" "${stage_log}"
    echo "[$(date +'%F %T')] fold${fold} ${stage} failed (exit=${exit_code}, err=${err_type})" | tee -a "${MASTER_LOG}"
    CURRENT_STAGE="NA"
    CURRENT_STAGE_LOG="NA"
    CURRENT_PID="NA"

    if (( attempts < max_attempts )); then
      echo "[$(date +'%F %T')] retrying in ${RETRY_SLEEP_SEC}s..." | tee -a "${MASTER_LOG}"
      sleep "${RETRY_SLEEP_SEC}"
    fi
  done

  RUN_STAGE_LAST_CKPT="${stage_ckpt}"
  return 1
}

run_fold() {
  local fold="$1"
  local fold_root="${DATA_ROOT}/fold${fold}"
  local prep_root="${fold_root}/training_data_seed42_ok"
  local stage1_model_root="${EXP_ROOT}/fold${fold}/stage1/models/model2d_"
  local stage1_log_root="${EXP_ROOT}/fold${fold}/stage1/logs/log2d_"
  local stage2_model_root="${EXP_ROOT}/fold${fold}/stage2/models/model2d_"
  local stage2_log_root="${EXP_ROOT}/fold${fold}/stage2/logs/log2d_"

  echo "========== fold ${fold} =========="
  echo "========== fold ${fold} ==========" >> "${MASTER_LOG}"
  if [[ "${PREPARE_FIRST}" == "1" ]]; then
    echo "[fold ${fold}] prepare datasets"
    "${DBT_PY}" prepare_datasets_2D.py \
      --datasets_name ROAD \
      --image_dir "${fold_root}/" \
      --train_dataset_root_dir "${prep_root}/" \
      --N_patches 20000 \
      --multi_cpu 1 \
      --seed "${SEED}"
  else
    echo "[fold ${fold}] skip prepare (use existing ${prep_root}/)"
  fi

  local stage1_ckpt=""
  if [[ "${RUN_STAGE1}" == "1" ]]; then
    echo "[fold ${fold}] stage1 train_seg=True"
    if ! run_stage_train "${fold}" "stage1" "true" "false" "" "${STAGE1_EPOCHS}" "${STAGE1_LR}" "${stage1_model_root}" "${stage1_log_root}" "${prep_root}"; then
      echo "[fold ${fold}] stage1 failed after retries. skip stage2 and continue next fold." | tee -a "${MASTER_LOG}"
      return 0
    fi
    stage1_ckpt="${RUN_STAGE_LAST_CKPT}"
  else
    local stage1_ckpt_dir="${stage1_model_root}${GPU_ID}/${STAGE1_EPOCHS}_${BATCH_SIZE}"
    stage1_ckpt="${stage1_ckpt_dir}/checkpoint_best.pth"
    if [[ ! -f "${stage1_ckpt}" ]]; then
      stage1_ckpt="${stage1_ckpt_dir}/checkpoint_final.pth"
    fi
  fi

  if [[ "${RUN_STAGE2}" == "1" ]]; then
    local restore_ckpt="${stage1_ckpt}"
    local stage1_ckpt_dir="${stage1_model_root}${GPU_ID}/${STAGE1_EPOCHS}_${BATCH_SIZE}"
    if [[ -z "${restore_ckpt}" || ! -f "${restore_ckpt}" ]]; then
      restore_ckpt="${stage1_ckpt_dir}/checkpoint_best.pth"
    fi
    if [[ ! -f "${restore_ckpt}" ]]; then
      restore_ckpt="${stage1_ckpt_dir}/checkpoint_final.pth"
    fi
    if [[ ! -f "${restore_ckpt}" ]]; then
      local missing_msg="[fold ${fold}] missing stage1 checkpoint for stage2: ${restore_ckpt}"
      echo "[fold ${fold}] missing stage1 checkpoint for stage2: ${restore_ckpt}"
      append_summary_row "${fold}" "stage2" "skipped" "0" "NA" "NA" "NA" "Missing_Stage1_CKPT" "${missing_msg}" "NA"
      return 0
    fi

    mkdir -p "${stage2_model_root}${GPU_ID}/${STAGE2_EPOCHS}_${BATCH_SIZE}"

    echo "[fold ${fold}] stage2 train_seg=False (restore from: ${restore_ckpt})"
    if ! run_stage_train "${fold}" "stage2" "false" "true" "${restore_ckpt}" "${STAGE2_EPOCHS}" "${STAGE2_LR}" "${stage2_model_root}" "${stage2_log_root}" "${prep_root}"; then
      echo "[fold ${fold}] stage2 failed after retries. continue next fold." | tee -a "${MASTER_LOG}"
      return 0
    fi
  fi
}

cd "${DBT_DIR}"
for fold in 0 1 2 3; do
  if [[ "${fold}" -lt "${START_FOLD}" || "${fold}" -gt "${END_FOLD}" ]]; then
    continue
  fi
  run_fold "${fold}"
done

echo "Requested folds finished: ${START_FOLD}-${END_FOLD}."
echo "Requested folds finished: ${START_FOLD}-${END_FOLD}." | tee -a "${MASTER_LOG}"
echo "Master log: ${MASTER_LOG}" | tee -a "${MASTER_LOG}"
echo "Summary: ${SUMMARY_TSV}" | tee -a "${MASTER_LOG}"
  RUN_STAGE_LAST_CKPT="NA"
