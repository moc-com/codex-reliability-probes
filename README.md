# Codex Reliability Probes (Deterministic Exact-Match)

This repository shares reproducible report artifacts for deterministic reliability probes on `gpt-5.3-codex`.

## Included Reports

- `reports/report_codex_benchmark_20260211_singlefile_full_30k.md` (Japanese)
- `reports/report_codex_benchmark_20260211_singlefile_full_30k_en.md` (English)

## Scope

- Multi-turn final-recall probe (`N={20,30,40,50}`)
- Long-context strict extraction probe (`L={5k,10k,15k,20k,300k}`)
- Strict exact-match evaluation and per-turn usage analysis

## Notes

- These are controlled reliability probes, not universal benchmarks.
- Raw traces / runner / plotting scripts can be published in a follow-up update.
