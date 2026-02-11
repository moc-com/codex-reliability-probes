# v1 Freeze and Handoff Note (2026-02-12)

## Decision

The repository is transitioned to **v1 freeze** for core benchmark scope.

Rationale:
- The current package already provides actionable operational insight.
- Marginal utility from additional large in-house sweeps is low versus token/runtime cost.
- The best next step is reproducible community extension with clear contribution rules.

## What is Fixed in v1

- Existing v1 datasets and reports remain unchanged as reference baseline.
- Core v1 message:
  - `baseline` can fail early in long-turn operation.
  - `recap` and `snapshot` can stabilize final recall at 100 turns in the observed run.
  - `snapshot` can achieve much lower final-turn context load versus `recap`.

## What is Added for Community v2

1. Probe runner supports explicit scenario/event metadata for richer experiments.
2. Analysis utility supports:
   - Wilson CI summaries
   - Survival tables
   - Failure-stage aggregation
   - Cost/throughput summary tables
   - Drift/event proxy summaries

## Non-Claims

- v1 does not claim universal model quality ranking.
- v1 does not provide high-power statistical significance.
- v1 does not establish a causal theory of long-turn failures.

## Next-Step Policy

- Accept additive PRs that improve statistical rigor and external validity.
- Prioritize reproducibility and transparent limitations over larger headline numbers.
