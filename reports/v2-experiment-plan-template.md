# v2 Experiment Plan Template

Use this template for reproducible, statistically stronger follow-up studies.

## 1. Objective

- Primary question:
- Secondary questions:
- Decision impact:

## 2. Design Matrix

| Factor | Levels |
|---|---|
| Strategy | baseline / recap / snapshot |
| Scenario | single_recall / multi_task / requirement_churn |
| Turns | 100 (minimum), optional 150 for stress-only |
| Repetitions | n>=10 per condition |
| Model | explicit fixed model id |
| Runtime overrides | explicit list (`--set`) |

## 3. Reproducibility Locks

- Pin `--model` and set `--require-explicit-model true`.
- Record all overrides in `manifest.txt`.
- Keep prompt protocol and evaluation rules unchanged inside one experiment batch.
- Publish raw logs and analysis artifacts together.

## 4. Metrics (Required)

1. Pass-rate metrics
- strict pass rate + Wilson 95% CI
- semantic pass rate + Wilson 95% CI

2. Reliability dynamics
- failure stage distribution
- survival table (`turn`, `n_at_risk`, `events`, `survival`)

3. Cost/latency/throughput
- aggregate token usage per run
- duration distribution (mean/std; optional quantiles)
- turns/sec
- interruption rate (timeout/nonzero exit)
- optional USD/run conversion with explicit rates

4. Drift and robustness
- event-based mismatch proxies
- snapshot-boundary mismatch rate
- requirement-churn mismatch rate

## 5. Minimum Acceptance Criteria

- Each main condition has `n>=10`.
- No missing raw logs for included runs.
- CI and survival outputs are generated and attached.
- Limitations section is present and explicit.

## 6. Suggested Commands

```bash
# Example batch
scripts/codex_final_recall_probe.sh \
  --strategy snapshot \
  --scenario multi_task \
  --plan 100x10 \
  --snapshot-interval 10 \
  --model gpt-5.3-codex \
  --require-explicit-model true \
  --max-input-tokens 20000000 \
  --max-delta-input-tokens 300000

python3 scripts/analyze_strategy_suite_v2.py \
  --data-root data/strategy100 \
  --out-dir reports/v2
```
