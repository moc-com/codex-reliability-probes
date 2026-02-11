# Strategy-100 Raw Data

This folder contains deterministic exact-match probe outputs for 100-turn runs.

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
