# Community Support Call (2026-02-12)

## Why this call exists

To move from v1 observation to statistically stronger evidence, the project needs repeated long-turn runs.
At current observed scale, this is not realistic for a single maintainer to execute continuously.

## Observed scale from current logs

From existing `strategy100` data (`per_turn.tsv`, sum of `input_tokens`):

- Per run totals:
  - baseline: `43,305,760`
  - recap: `814,865,016`
  - snapshot: `22,194,832`
- Combined three-strategy budget:
  - `n=10`: `8,803,656,080` input tokens
  - `n=30`: `26,410,968,240` input tokens

These numbers are operationally heavy even before adding cross-model and external-validity scenarios.

## Requested support

1. Compute-backed reruns under fixed protocol (with raw logs).
2. Independent replication by external contributors.
3. Analysis contributions:
   - confidence intervals
   - survival curves
   - failure taxonomy improvements
   - cost/throughput comparisons

## Contribution requirements

- Keep runs additive (do not overwrite v1 artifacts).
- Publish `manifest.txt`, `results.tsv`, and `per_turn.tsv`.
- Declare model/runtime parameters explicitly.
- Separate factual findings from hypotheses.

## Practical path

If you cannot run full `n=30`, submit smaller complete batches (`n=3` or `n=5`) so the project can aggregate evidence across contributors.
