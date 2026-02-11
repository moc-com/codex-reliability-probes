# Strategy-100 Raw Data

This folder contains deterministic exact-match probe outputs for 100-turn runs.

## TSV Columns (Data Dictionary)

### `per_turn.tsv`

- `ts`: run timestamp (UTC, ISO8601)
- `strategy`: orchestration mode (`baseline` / `recap` / `snapshot`)
- `turns`: planned turn budget for the run
- `trial`: trial index within the same condition
- `turn_index`: current turn index (`0` = init turn)
- `is_final`: whether this row is the final-recall turn
- `expected`: expected exact output for this turn
- `actual`: observed model output for this turn (empty means no captured agent message)
- `exit_code`: command exit code for this turn
- `completed`: whether command exit code is zero
- `input_tokens`: reported input tokens for this turn
- `cached_input_tokens`: reported cached-input tokens for this turn
- `output_tokens`: reported output tokens for this turn
- `delta_input_tokens`: `input_tokens[t] - input_tokens[t-1]` when both are available
- `note`: turn-level execution note (`ok`, `timeout`, `nonzero_exit`, etc.)
- `thread_id`: thread id used for this turn
- `call_mode`: `resume` or `new` (snapshot reset paths use `new`)
- `event`: optional event annotation (`recap_injected`, `snapshot_reset`, `requirement_churn`, or combined with `;`)

### `results.tsv`

- `strict_pass`: exact string match success at run level
- `semantic_pass`: normalized-match success at run level
- `fail_stage`: failure stage label (`init_exec`, `init_ack`, `mid_turn`, `final_recall`, `guard_stop`, `none`)
- `fail_turn`: turn index where failure was first recorded (`0` when none)
- `note`: run-level reason note
- `guard_triggered`: whether stop was caused by guard policy
- `guard_metric`: which guard fired (`input_tokens` / `delta_input_tokens`)
- `guard_threshold`: configured guard threshold value
- `guard_observed`: observed value at guard trigger

### `summary.tsv`

- Per-condition aggregate with total trials, pass counts/rates, guard-stop counts, and average duration.

### `context_summary.tsv`

- Final-turn aggregate by condition:
  - `avg_final_input_tokens`
  - `avg_final_cached_input_tokens`
  - `avg_final_output_tokens`
  - `avg_final_delta_input_tokens`

### `manifest.txt`

- Run configuration metadata (timeouts, token guards, strategy, intervals, model/runtime metadata, CLI version).

## Failure Taxonomy (Current)

- `init_exec`: init turn execution failed or thread could not be created
- `init_ack`: init turn response mismatch for required `STORED`
- `mid_turn`: mismatch/non-success occurred before final turn
- `final_recall`: mismatch/non-success occurred at final recall turn
- `guard_stop`: run stopped due to configured guard threshold
- `none`: no failure recorded

Note:
- Some legacy notes use combined wording such as `semantic_mismatch_or_timeout`.
- For strict cause attribution, use both `results.tsv` and turn-level `per_turn.tsv` (`exit_code`, `note`, `actual`) together.

## Layout
- `baseline/`: single-thread no intervention
- `recap/`: single-thread with recap every 10 turns
- `snapshot/`: thread reset/snapshot every 10 turns

Each strategy directory includes:
- `results.tsv`: run-level outcome
- `per_turn.tsv`: turn-level raw log
- `summary.tsv`: aggregated pass metrics
- `manifest.txt`: run configuration metadata
- `context_summary.tsv` (when available): final-turn context usage summary

## Notes
- `baseline` failed before final turn in this run, so `context_summary.tsv` is not present.
- Local absolute paths are redacted in manifests.
