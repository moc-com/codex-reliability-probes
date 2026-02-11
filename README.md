# Codex Reliability Probes (Deterministic Exact-Match)

This repository shares reproducible reliability probe artifacts on `gpt-5.3-codex`.

## Reports

- `reports/report_codex_benchmark_20260211_singlefile_full_30k.md` (Japanese)
- `reports/report_codex_benchmark_20260211_singlefile_full_30k_en.md` (English)
- `reports/codex-turn-budget-decision-20260211.md`
- `reports/codex-strategy100-execution-report-20260211.md`

## New Strategy-100 Dataset (baseline vs recap vs snapshot)

Raw outputs:
- `data/strategy100/baseline/`
- `data/strategy100/recap/`
- `data/strategy100/snapshot/`

Runner:
- `scripts/codex_final_recall_probe.sh`

Measured result (100 turns, 1 trial each):

| Strategy | Strict | Semantic | Outcome |
|---|---:|---:|---|
| baseline | 0/1 | 0/1 | failed at turn 29 (mid-turn) |
| recap (every 10 turns) | 1/1 | 1/1 | pass |
| snapshot (every 10 turns) | 1/1 | 1/1 | pass |

Cost signal from this run:
- `recap` final-turn `input_tokens`: `17,961,775`
- `snapshot` final-turn `input_tokens`: `440,459`
- `snapshot` context footprint was about `40.8x` smaller than `recap` at final turn.

## Reproduce (CLI)

```bash
# baseline
scripts/codex_final_recall_probe.sh \
  --strategy baseline \
  --plan 100x1 \
  --max-input-tokens 20000000 \
  --max-delta-input-tokens 300000

# recap (every 10 turns)
scripts/codex_final_recall_probe.sh \
  --strategy recap \
  --recap-interval 10 \
  --plan 100x1 \
  --max-input-tokens 20000000 \
  --max-delta-input-tokens 300000

# snapshot (every 10 turns)
scripts/codex_final_recall_probe.sh \
  --strategy snapshot \
  --snapshot-interval 10 \
  --plan 100x1 \
  --max-input-tokens 20000000 \
  --max-delta-input-tokens 300000
```

## Operational Guidance

- Recommended validation set: `baseline@100`, `recap@100`, `snapshot@100`.
- Routine stop-line: `<=100 turns`.
- For routine operation, avoid `>100` unless running an explicit budget-approved stress test.

## Notes

- These are controlled reliability probes, not universal benchmarks.
- Sample size is still small; treat this as a reproducibility package and baseline for follow-up trials.
