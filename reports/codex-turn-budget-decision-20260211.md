# Codex Turn-Budget Decision Note (2026-02-11)

## Decision (for current operation)
- Recommended execution set: **3 runs total**.
- Run design: `baseline@100`, `recap@100`, `snapshot@100` (1 trial each).
- Operational upper bound: **100 turns**.
- Policy: **Do not run >100 turns in normal operation** unless there is a separate budget-approved stress test objective.

## Why 100 turns is the practical stop line
Current measurement shows token growth slope worsening in mid-to-late turns. This makes >100 turns expensive and lower ROI for reliability validation.

### Observed facts from this branch run
- 50-turn completed pass: strict/semantic both pass.
- 50-turn final usage: `input_tokens=7,832,079`, `delta_input_tokens=194,444`.
- 100-turn run (stopped intentionally for budget control) reached turn 42 with:
  - `input_tokens=6,532,084`
  - `delta_input_tokens=240,345`
- In 100-turn partial run, recent delta (turn 33-42 average): `205,875` tokens/turn.
- Largest observed delta in collected rows: `248,884` tokens/turn.

Interpretation:
- Growth remains roughly monotonic upward and the per-turn delta is already larger than the 50-turn endpoint behavior.
- This is enough evidence to conclude that pushing beyond 100 materially worsens cost efficiency.

## Extrapolation (for budget-risk communication)
Using turn 42 as anchor (`6,532,084`) and two slope envelopes:
- Lower envelope (avg slope turn1-42): `158,201` tokens/turn
- Upper envelope (recent slope-like bound): `240,345` tokens/turn

Projected final input token ranges:
- Turn 100: `15,707,742` to `20,472,094`
- Turn 150: `23,617,792` to `32,489,344`
- Turn 300: `47,347,942` to `68,541,094`

Conclusion from projection:
- Around 150 turns, upper envelope already exceeds 30M class.
- 300-turn stress is likely to be disproportionately expensive relative to incremental learning value.

## Stop criteria to keep cost controlled
- Hard stop: `input_tokens >= 20,000,000`
- Safety stop: `delta_input_tokens >= 300,000` for 2 consecutive turns
- Absolute policy stop for routine validation: `turns > 100`

## Is report preparation ready?
- **Yes.** Stop-line policy and 3-strategy execution are both documented.
- 3-strategy execution report: `artifacts/reports/codex-strategy100-execution-report-20260211.md`

## Post-run status update (executed after this note's first draft)
- `baseline@100`: failed at turn 29 (`mid_turn`).
- `recap@100`: strict/semantic pass.
- `snapshot@100`: strict/semantic pass.
- Cost signal: `snapshot` final-turn context was far smaller than `recap`, supporting cost-efficient operation.

## Data sources (this branch)
- `artifacts/reports/codex-final-recall-baseline-300-20260211T074502Z/results.tsv`
- `artifacts/reports/codex-final-recall-baseline-300-20260211T074502Z/per_turn.tsv`
- `artifacts/reports/codex-final-recall-baseline-300-20260211T074502Z/manifest.txt`
- `artifacts/reports/codex-strategy100-baseline-20260211T080832Z/results.tsv`
- `artifacts/reports/codex-strategy100-baseline-20260211T080832Z/per_turn.tsv`
- `artifacts/reports/codex-strategy100-recap-20260211T081433Z/results.tsv`
- `artifacts/reports/codex-strategy100-recap-20260211T081433Z/per_turn.tsv`
- `artifacts/reports/codex-strategy100-snapshot-20260211T083326Z/results.tsv`
- `artifacts/reports/codex-strategy100-snapshot-20260211T083326Z/per_turn.tsv`
