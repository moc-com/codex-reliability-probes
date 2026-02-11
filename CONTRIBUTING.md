# Contributing Guide

This repository is in **v1 freeze + community extension** mode.

## Ground Rules

- Do not rewrite existing v1 reports or raw datasets.
- Add new experiments as additive artifacts (new timestamped folders/files).
- Keep prompts and judgments deterministic and exact-match whenever possible.
- Avoid absolute local paths, API keys, and private identifiers in artifacts.

## Required for Experimental PRs

1. Add raw logs (`results.tsv`, `per_turn.tsv`, `manifest.txt`) under a new directory.
2. Include a short method note (what changed and why).
3. Include statistical summary with confidence intervals.
4. Mark any non-default model/runtime parameter explicitly.
5. Separate factual findings from hypotheses.

## Recommended Baseline Commands

```bash
# Example: 100-turn strategy run (single_recall scenario)
scripts/codex_final_recall_probe.sh \
  --strategy snapshot \
  --plan 100x3 \
  --scenario single_recall \
  --model gpt-5.3-codex \
  --require-explicit-model true \
  --max-input-tokens 20000000 \
  --max-delta-input-tokens 300000

# Analyze outputs (replace data root as needed)
python3 scripts/analyze_strategy_suite_v2.py \
  --data-root data/strategy100 \
  --out-dir reports/v2
```

## Scope for v2+ Contributions

- Survival analysis and failure-time modeling
- Cross-model comparison with identical task suites
- Snapshot drift and compression-loss analysis
- Cost/latency/throughput trade-off characterization
- Robustness under distractors and requirement churn
