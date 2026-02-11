#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Deterministic strict final-recall probe for Codex CLI.

Usage:
  scripts/ops/codex_final_recall_probe.sh [options]

Options:
  --root PATH                 Project root where codex exec is run (default: git root)
  --out-dir PATH              Output directory (default: artifacts/reports/codex-final-recall-<UTC>)
  --plan SPEC                 Turn/trial plan, comma separated "<turns>x<trials>" (default: 50x1,100x1,150x1,200x1,250x1,300x1)
  --strategy MODE             baseline | recap | snapshot (default: baseline)
  --recap-interval N          recap interval for strategy=recap (default: 10)
  --snapshot-interval N       chunk interval for strategy=snapshot (default: 10)
  --init-lines N              Number of filler lines in turn 0 prompt (default: 90)
  --turn-lines N              Number of filler lines in subsequent turns (default: 50)
  --timeout-init-sec N        Timeout for turn 0 (default: 180)
  --timeout-turn-sec N        Timeout for turns >=1 (default: 180)
  --model MODEL               Optional model override via codex -c model=...
  --reasoning-effort LEVEL    Optional override via codex -c model_reasoning_effort=...
  --max-input-tokens N        Guard threshold per turn (default: 30000000, <=0 to disable)
  --max-delta-input-tokens N  Guard threshold for per-turn delta (default: 1500000, <=0 to disable)
  --stop-on-guard true|false  Stop remaining trials when guard is hit (default: true)
  --help                      Show this help

Strategies:
  baseline: Single thread resume across turns (pure memory stress)
  recap:    baseline + periodic recap injection every N turns
  snapshot: periodic thread reset with compact snapshot every N turns

Outputs:
  <out-dir>/results.tsv
  <out-dir>/per_turn.tsv
  <out-dir>/summary.tsv
  <out-dir>/context_summary.tsv
  <out-dir>/manifest.txt
  <out-dir>/runs/* (raw prompts/stdout/stderr)
USAGE
}

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
OUT_DIR="artifacts/reports/codex-final-recall-$(date -u +%Y%m%dT%H%M%SZ)"
PLAN_SPEC="50x1,100x1,150x1,200x1,250x1,300x1"
STRATEGY="baseline"
RECAP_INTERVAL=10
SNAPSHOT_INTERVAL=10
INIT_LINES=90
TURN_LINES=50
TIMEOUT_INIT_SEC=180
TIMEOUT_TURN_SEC=180
MODEL=""
REASONING_EFFORT=""
MAX_INPUT_TOKENS=30000000
MAX_DELTA_INPUT_TOKENS=1500000
STOP_ON_GUARD="true"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      ROOT="$2"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    --plan)
      PLAN_SPEC="$2"
      shift 2
      ;;
    --strategy)
      STRATEGY="$2"
      shift 2
      ;;
    --recap-interval)
      RECAP_INTERVAL="$2"
      shift 2
      ;;
    --snapshot-interval)
      SNAPSHOT_INTERVAL="$2"
      shift 2
      ;;
    --init-lines)
      INIT_LINES="$2"
      shift 2
      ;;
    --turn-lines)
      TURN_LINES="$2"
      shift 2
      ;;
    --timeout-init-sec)
      TIMEOUT_INIT_SEC="$2"
      shift 2
      ;;
    --timeout-turn-sec)
      TIMEOUT_TURN_SEC="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --reasoning-effort)
      REASONING_EFFORT="$2"
      shift 2
      ;;
    --max-input-tokens)
      MAX_INPUT_TOKENS="$2"
      shift 2
      ;;
    --max-delta-input-tokens)
      MAX_DELTA_INPUT_TOKENS="$2"
      shift 2
      ;;
    --stop-on-guard)
      STOP_ON_GUARD="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "[error] unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ "$STRATEGY" != "baseline" && "$STRATEGY" != "recap" && "$STRATEGY" != "snapshot" ]]; then
  echo "[error] --strategy must be baseline|recap|snapshot" >&2
  exit 2
fi

for v in INIT_LINES TURN_LINES TIMEOUT_INIT_SEC TIMEOUT_TURN_SEC RECAP_INTERVAL SNAPSHOT_INTERVAL MAX_INPUT_TOKENS MAX_DELTA_INPUT_TOKENS; do
  if [[ ! "${!v}" =~ ^-?[0-9]+$ ]]; then
    echo "[error] ${v} must be integer" >&2
    exit 2
  fi
done

if [[ "$STOP_ON_GUARD" != "true" && "$STOP_ON_GUARD" != "false" ]]; then
  echo "[error] --stop-on-guard must be true|false" >&2
  exit 2
fi

declare -a PLAN_TURNS=()
declare -a PLAN_TRIALS=()
IFS=',' read -r -a PLAN_ITEMS <<< "$PLAN_SPEC"
for item in "${PLAN_ITEMS[@]}"; do
  if [[ ! "$item" =~ ^([0-9]+)x([0-9]+)$ ]]; then
    echo "[error] invalid --plan item: $item (expected <turns>x<trials>)" >&2
    exit 2
  fi
  PLAN_TURNS+=("${BASH_REMATCH[1]}")
  PLAN_TRIALS+=("${BASH_REMATCH[2]}")
done

mkdir -p "$OUT_DIR/runs"
RESULTS="$OUT_DIR/results.tsv"
PER_TURN="$OUT_DIR/per_turn.tsv"
SUMMARY="$OUT_DIR/summary.tsv"
CONTEXT_SUMMARY="$OUT_DIR/context_summary.tsv"
MANIFEST="$OUT_DIR/manifest.txt"

printf 'ts\tstrategy\tturns\ttrial\tduration_sec\tinit_ec\tfinal_ec\tstrict_pass\tsemantic_pass\tfail_stage\tfail_turn\texpected_final\tactual_final\tthread_id\tnote\tguard_triggered\tguard_metric\tguard_threshold\tguard_observed\n' > "$RESULTS"
printf 'ts\tstrategy\tturns\ttrial\tturn_index\tis_final\texpected\tactual\texit_code\tcompleted\tinput_tokens\tcached_input_tokens\toutput_tokens\tdelta_input_tokens\tnote\tthread_id\n' > "$PER_TURN"

CODEX_PREFIX=(codex)
if [[ -n "$MODEL" ]]; then
  CODEX_PREFIX+=(-c "model=${MODEL}")
fi
if [[ -n "$REASONING_EFFORT" ]]; then
  CODEX_PREFIX+=(-c "model_reasoning_effort=${REASONING_EFFORT}")
fi

GLOBAL_STOP="false"
GLOBAL_STOP_REASON=""

extract_msg() {
  local f="$1"
  jq -r 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text' "$f" | tail -n1
}

extract_usage() {
  local f="$1"
  local key="$2"
  jq -r "select(.type==\"turn.completed\") | .usage.${key} // empty" "$f" | tail -n1
}

normalize() {
  local s="$1"
  printf '%s' "$s" | tr -d '\r\n\t ' | sed 's/[^[:alnum:]_]//g'
}

long_block() {
  local lines="$1"
  local out="$2"
  : > "$out"
  for i in $(seq 1 "$lines"); do
    echo "LINE_${i}: alpha beta gamma delta epsilon zeta eta theta iota kappa ${i}" >> "$out"
  done
}

run_trial() {
  local turns="$1"
  local trial="$2"

  local ts start end dur
  local run_tag="${STRATEGY}_t${turns}_r${trial}"
  local run_dir="$OUT_DIR/runs/${run_tag}"
  mkdir -p "$run_dir"

  local token="FR_${STRATEGY}_${turns}_${trial}_$(date -u +%Y%m%dT%H%M%SZ)"
  local init_ec=1
  local final_ec=1
  local strict_pass=true
  local semantic_pass=true
  local fail_stage=""
  local fail_turn="0"
  local note="ok"
  local expected_final="$token"
  local actual_final=""
  local thread_id=""
  local prev_input=""
  local guard_triggered="false"
  local guard_metric=""
  local guard_threshold=""
  local guard_observed=""

  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  start=$(date +%s)

  local p0="$run_dir/turn_000_prompt.txt"
  local lb0="$run_dir/turn_000_block.txt"
  local o0="$run_dir/turn_000.out"
  local e0="$run_dir/turn_000.err"

  long_block "$INIT_LINES" "$lb0"
  {
    echo "Store the token and keep it through multiple turns."
    cat "$lb0"
    echo "TOKEN=${token}"
    echo "Reply exactly STORED"
  } > "$p0"

  set +e
  (cd "$ROOT" && timeout "${TIMEOUT_INIT_SEC}s" "${CODEX_PREFIX[@]}" exec --json < "$p0") > "$o0" 2> "$e0"
  init_ec=$?
  set -e

  thread_id="$(jq -r 'select(.type=="thread.started") | .thread_id' "$o0" | tail -n1)"
  local init_msg init_input init_cached init_output
  init_msg="$(extract_msg "$o0" || true)"
  init_input="$(extract_usage "$o0" input_tokens || true)"
  init_cached="$(extract_usage "$o0" cached_input_tokens || true)"
  init_output="$(extract_usage "$o0" output_tokens || true)"
  [[ -z "$init_input" ]] && init_input=-1
  [[ -z "$init_cached" ]] && init_cached=-1
  [[ -z "$init_output" ]] && init_output=-1
  prev_input="$init_input"

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$ts" "$STRATEGY" "$turns" "$trial" "0" "false" "STORED" "$init_msg" "$init_ec" \
    "$([[ $init_ec -eq 0 ]] && echo true || echo false)" "$init_input" "$init_cached" "$init_output" "" "init_turn" "$thread_id" >> "$PER_TURN"

  if [[ "$init_ec" -ne 0 || -z "$thread_id" || "$thread_id" == "null" ]]; then
    strict_pass=false
    semantic_pass=false
    fail_stage="init_exec"
    note="init_exec_or_thread_failed"
  else
    if [[ "$init_msg" != "STORED" ]]; then
      strict_pass=false
    fi
    if [[ "$(normalize "$init_msg")" != "STORED" ]]; then
      semantic_pass=false
      fail_stage="init_ack"
      note="init_ack_mismatch"
    fi
  fi

  if [[ "$semantic_pass" == true ]]; then
    local t
    for t in $(seq 1 $((turns - 1))); do
      local pt="$run_dir/turn_$(printf '%03d' "$t")_prompt.txt"
      local lbt="$run_dir/turn_$(printf '%03d' "$t")_block.txt"
      local ot="$run_dir/turn_$(printf '%03d' "$t").out"
      local et="$run_dir/turn_$(printf '%03d' "$t").err"
      local expected actual prompt_inline ec completed usage_in usage_cached usage_out delta note_turn is_final
      local call_mode="resume"

      long_block "$TURN_LINES" "$lbt"
      is_final="false"
      if [[ "$t" -lt $((turns - 1)) ]]; then
        expected="ACK_${t}"
      else
        expected="$token"
        is_final="true"
      fi

      {
        if [[ "$is_final" == "true" ]]; then
          echo "Final step."
        else
          echo "Continue memory test."
        fi
        cat "$lbt"

        if [[ "$STRATEGY" == "recap" && "$is_final" == "false" && $((t % RECAP_INTERVAL)) -eq 0 ]]; then
          echo "RECAP_ORIGINAL_TOKEN=${token}"
          if (( t > 1 )); then
            echo "RECAP_LAST_ACK=ACK_$((t-1))"
          fi
        fi

        if [[ "$STRATEGY" == "snapshot" && ( "$t" -eq 1 || $(((t - 1) % SNAPSHOT_INTERVAL)) -eq 0 ) ]]; then
          call_mode="new"
          echo "SNAPSHOT_MODE=on"
          echo "SNAPSHOT_ORIGINAL_TOKEN=${token}"
          if (( t > 1 )); then
            echo "SNAPSHOT_LAST_ACK=ACK_$((t-1))"
          fi
        fi

        if [[ "$is_final" == "true" ]]; then
          echo "Return exactly TOKEN value only"
        else
          echo "Reply exactly ${expected}"
        fi
      } > "$pt"

      if [[ "$STRATEGY" == "snapshot" && "$call_mode" == "new" ]]; then
        set +e
        (cd "$ROOT" && timeout "${TIMEOUT_TURN_SEC}s" "${CODEX_PREFIX[@]}" exec --json < "$pt") > "$ot" 2> "$et"
        ec=$?
        set -e
        local new_thread
        new_thread="$(jq -r 'select(.type=="thread.started") | .thread_id' "$ot" | tail -n1)"
        if [[ -n "$new_thread" && "$new_thread" != "null" ]]; then
          thread_id="$new_thread"
        fi
      else
        prompt_inline="$(tr '\n' ' ' < "$pt")"
        set +e
        (cd "$ROOT" && timeout "${TIMEOUT_TURN_SEC}s" "${CODEX_PREFIX[@]}" exec resume "$thread_id" --json "$prompt_inline") > "$ot" 2> "$et"
        ec=$?
        set -e
      fi
      final_ec=$ec

      actual="$(extract_msg "$ot" || true)"
      usage_in="$(extract_usage "$ot" input_tokens || true)"
      usage_cached="$(extract_usage "$ot" cached_input_tokens || true)"
      usage_out="$(extract_usage "$ot" output_tokens || true)"
      [[ -z "$usage_in" ]] && usage_in=-1
      [[ -z "$usage_cached" ]] && usage_cached=-1
      [[ -z "$usage_out" ]] && usage_out=-1

      delta=""
      if [[ "$prev_input" =~ ^[0-9]+$ ]] && [[ "$usage_in" =~ ^[0-9]+$ ]] && (( prev_input >= 0 )) && (( usage_in >= 0 )); then
        delta=$((usage_in - prev_input))
      fi
      prev_input="$usage_in"

      completed="$([[ "$ec" -eq 0 ]] && echo true || echo false)"
      note_turn="ok"
      if [[ "$ec" -eq 124 ]]; then
        note_turn="timeout"
      elif [[ "$ec" -ne 0 ]]; then
        note_turn="nonzero_exit"
      fi

      printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$ts" "$STRATEGY" "$turns" "$trial" "$t" "$is_final" "$expected" "$actual" "$ec" "$completed" \
        "$usage_in" "$usage_cached" "$usage_out" "$delta" "$note_turn" "$thread_id" >> "$PER_TURN"

      if [[ "$actual" != "$expected" ]]; then
        strict_pass=false
      fi

      if [[ "$MAX_INPUT_TOKENS" -gt 0 && "$usage_in" =~ ^[0-9]+$ && "$usage_in" -gt "$MAX_INPUT_TOKENS" ]]; then
        semantic_pass=false
        fail_stage="guard_stop"
        fail_turn="$t"
        note="guard_input_tokens_exceeded"
        actual_final="$actual"
        guard_triggered="true"
        guard_metric="input_tokens"
        guard_threshold="$MAX_INPUT_TOKENS"
        guard_observed="$usage_in"
        if [[ "$STOP_ON_GUARD" == "true" ]]; then
          GLOBAL_STOP="true"
          GLOBAL_STOP_REASON="input_tokens>${MAX_INPUT_TOKENS} at turns=${turns} trial=${trial} turn=${t}"
        fi
        break
      fi
      if [[ "$MAX_DELTA_INPUT_TOKENS" -gt 0 && "$delta" =~ ^-?[0-9]+$ && "$delta" -gt "$MAX_DELTA_INPUT_TOKENS" ]]; then
        semantic_pass=false
        fail_stage="guard_stop"
        fail_turn="$t"
        note="guard_delta_input_tokens_exceeded"
        actual_final="$actual"
        guard_triggered="true"
        guard_metric="delta_input_tokens"
        guard_threshold="$MAX_DELTA_INPUT_TOKENS"
        guard_observed="$delta"
        if [[ "$STOP_ON_GUARD" == "true" ]]; then
          GLOBAL_STOP="true"
          GLOBAL_STOP_REASON="delta_input_tokens>${MAX_DELTA_INPUT_TOKENS} at turns=${turns} trial=${trial} turn=${t}"
        fi
        break
      fi

      if [[ "$ec" -ne 0 || "$(normalize "$actual")" != "$(normalize "$expected")" ]]; then
        semantic_pass=false
        fail_turn="$t"
        if [[ "$is_final" == "true" ]]; then
          fail_stage="final_recall"
          note="final_recall_semantic_mismatch_or_timeout"
        else
          fail_stage="mid_turn"
          note="turn_${t}_semantic_mismatch_or_timeout"
        fi
        actual_final="$actual"
        break
      fi

      if [[ "$is_final" == "true" ]]; then
        actual_final="$actual"
      fi
    done
  fi

  if [[ -z "$fail_stage" ]]; then
    fail_stage="none"
    fail_turn="0"
  fi

  end=$(date +%s)
  dur=$((end - start))

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$ts" "$STRATEGY" "$turns" "$trial" "$dur" "$init_ec" "$final_ec" "$strict_pass" "$semantic_pass" \
    "$fail_stage" "$fail_turn" "$expected_final" "$actual_final" "$thread_id" "$note" "$guard_triggered" "$guard_metric" "$guard_threshold" "$guard_observed" >> "$RESULTS"

  echo "[trial-done] strategy=${STRATEGY} turns=${turns} trial=${trial} strict=${strict_pass} semantic=${semantic_pass} fail_stage=${fail_stage} note=${note}"
}

{
  echo "generated_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "root=${ROOT}"
  echo "out_dir=${OUT_DIR}"
  echo "plan=${PLAN_SPEC}"
  echo "strategy=${STRATEGY}"
  echo "recap_interval=${RECAP_INTERVAL}"
  echo "snapshot_interval=${SNAPSHOT_INTERVAL}"
  echo "init_lines=${INIT_LINES}"
  echo "turn_lines=${TURN_LINES}"
  echo "timeout_init_sec=${TIMEOUT_INIT_SEC}"
  echo "timeout_turn_sec=${TIMEOUT_TURN_SEC}"
  echo "max_input_tokens=${MAX_INPUT_TOKENS}"
  echo "max_delta_input_tokens=${MAX_DELTA_INPUT_TOKENS}"
  echo "stop_on_guard=${STOP_ON_GUARD}"
  if [[ -n "$MODEL" ]]; then
    echo "model=${MODEL}"
  else
    echo "model=default_from_codex_config"
  fi
  if [[ -n "$REASONING_EFFORT" ]]; then
    echo "reasoning_effort=${REASONING_EFFORT}"
  fi
  echo "codex_version=$("${CODEX_PREFIX[@]}" --version 2>/dev/null || echo unknown)"
} > "$MANIFEST"

idx=0
for turns in "${PLAN_TURNS[@]}"; do
  trials="${PLAN_TRIALS[$idx]}"
  for trial in $(seq 1 "$trials"); do
    if [[ "$GLOBAL_STOP" == "true" ]]; then
      echo "[stop] global_stop=true reason=${GLOBAL_STOP_REASON}"
      break 2
    fi
    echo "[run] strategy=${STRATEGY} turns=${turns} trial=${trial}"
    run_trial "$turns" "$trial"
  done
  idx=$((idx + 1))
done

{
  echo -e "strategy\tturns\ttotal\tstrict_pass\tsemantic_pass\tstrict_rate_pct\tsemantic_rate_pct\tguard_stop_count\tavg_duration_sec"
  awk -F'\t' 'NR>1{
    key=$2"\t"$3
    t[key]++
    if($8=="true") sp[key]++
    if($9=="true") mp[key]++
    if($10=="guard_stop") gp[key]++
    d[key]+=$5
  }
  END{
    for(k in t){
      printf "%s\t%d\t%d\t%d\t%.1f\t%.1f\t%d\t%.1f\n", k, t[k], sp[k]+0, mp[k]+0, (sp[k]+0)*100.0/t[k], (mp[k]+0)*100.0/t[k], gp[k]+0, d[k]/t[k]
    }
  }' "$RESULTS" | sort -t$'\t' -k1,1 -k2,2n
} > "$SUMMARY"

{
  echo -e "strategy\tturns\ttotal_final_turns\tavg_final_input_tokens\tavg_final_cached_input_tokens\tavg_final_output_tokens\tavg_final_delta_input_tokens"
  awk -F'\t' 'NR>1 && $6=="true"{
    key=$2"\t"$3
    t[key]++
    if($11 ~ /^[0-9]+$/) input_sum[key]+=$11
    if($12 ~ /^[0-9]+$/) cached_sum[key]+=$12
    if($13 ~ /^[0-9]+$/) output_sum[key]+=$13
    if($14 ~ /^-?[0-9]+$/) delta_sum[key]+=$14
  }
  END{
    for(k in t){
      printf "%s\t%d\t%.1f\t%.1f\t%.1f\t%.1f\n", k, t[k], input_sum[k]/t[k], cached_sum[k]/t[k], output_sum[k]/t[k], delta_sum[k]/t[k]
    }
  }' "$PER_TURN" | sort -t$'\t' -k1,1 -k2,2n
} > "$CONTEXT_SUMMARY"

echo "[done] output_dir=${OUT_DIR}"
echo "[done] summary=${SUMMARY}"
echo "[done] context_summary=${CONTEXT_SUMMARY}"
if [[ "$GLOBAL_STOP" == "true" ]]; then
  echo "[done] global_stop_reason=${GLOBAL_STOP_REASON}"
fi
