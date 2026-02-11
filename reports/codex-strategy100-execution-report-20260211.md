# Codex 100-Turn Strategy Execution Report (2026-02-11)

## Scope
- Goal: Execute the agreed 3-run set and finalize stop-line guidance.
- Runs executed:
  - `baseline@100` (single thread, no intervention)
  - `recap@100` (single thread + recap every 10 turns)
  - `snapshot@100` (thread snapshot/reset every 10 turns)
- Guardrails:
  - `max_input_tokens = 20,000,000`
  - `max_delta_input_tokens = 300,000`
  - stop on guard enabled

## Primary Results
| Strategy | Turns | Strict | Semantic | Status | Fail stage | Fail turn | Duration (sec) |
|---|---:|---:|---:|---|---|---:|---:|
| baseline | 100 | 0/1 | 0/1 | Failed | mid_turn | 29 | 340 |
| recap | 100 | 1/1 | 1/1 | Passed | none | 0 | 1127 |
| snapshot | 100 | 1/1 | 1/1 | Passed | none | 0 | 1041 |

## Cost/Context Signals
| Strategy | Final-turn input_tokens | Final-turn delta_input_tokens | Notes |
|---|---:|---:|---|
| baseline | N/A (no final turn reached) | N/A | failed at turn 29 |
| recap | 17,961,775 | 179,089 | high absolute context load |
| snapshot | 440,459 | 79,579 | periodic reset kept context low |

Derived efficiency view:
- `recap` final-turn input was about **40.8x** `snapshot` (`17,961,775 / 440,459`).
- `snapshot` completed successfully with much smaller context footprint.

## Interpretation
1. `baseline@100` was not reliable in this run (mid-turn failure at 29).
2. Both intervention strategies (`recap`, `snapshot`) reached 100-turn final recall successfully.
3. From a cost perspective, `snapshot` is strongly favorable because context growth is structurally bounded by reset windows.

## Why >100 turns is not recommended for routine operation
Even before this 3-run set, observed growth envelopes already indicated rapid cost escalation beyond 100 turns:
- projected turn100 input range: `15.7M` to `20.5M`
- projected turn150 input range: `23.6M` to `32.5M`
- projected turn300 input range: `47.3M` to `68.5M`

Practical conclusion:
- Beyond 100 turns, marginal insight gain is small relative to token-cost growth and instability risk.
- For normal engineering operation, >100 should be treated as stress-only mode with explicit budget approval.

## Final Operational Recommendation
- Keep the agreed standard: **3 runs total** (`baseline@100`, `recap@100`, `snapshot@100`) for validation windows.
- Default production-like long workflow mode: **snapshot**.
- Use recap when single-thread continuity is required and higher context budget is acceptable.
- Routine stop-line: **100 turns max**.

## Evidence Files
- `artifacts/reports/codex-strategy100-baseline-20260211T080832Z/results.tsv`
- `artifacts/reports/codex-strategy100-baseline-20260211T080832Z/per_turn.tsv`
- `artifacts/reports/codex-strategy100-recap-20260211T081433Z/results.tsv`
- `artifacts/reports/codex-strategy100-recap-20260211T081433Z/per_turn.tsv`
- `artifacts/reports/codex-strategy100-recap-20260211T081433Z/context_summary.tsv`
- `artifacts/reports/codex-strategy100-snapshot-20260211T083326Z/results.tsv`
- `artifacts/reports/codex-strategy100-snapshot-20260211T083326Z/per_turn.tsv`
- `artifacts/reports/codex-strategy100-snapshot-20260211T083326Z/context_summary.tsv`
- `artifacts/reports/codex-turn-budget-decision-20260211.md`
