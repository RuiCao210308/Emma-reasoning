# Project State

## Research question

The project asks whether inference-time reasoning improves visually grounded motion planning,
or whether apparent gains can be explained by historical-motion persistence and smoother
trajectories. CoT, Self-Consistency, and candidate search must ultimately beat frozen,
leakage-free controls on the same samples and evaluator. Negative results remain valid outcomes.

## Stable architectural decisions

- Official OpenEMMA is the source of truth for model loading, image preprocessing, prompts,
  and original inference behavior.
- Emma-reasoning owns provenance capture, audits, evaluation, and explicit interventions.
- Upstream repositories are commit-pinned and paper runs require exact, clean checkouts.
- The independent trusted evaluator is an audit layer, not an OpenEMMA reproduction.
- Detailed raw records stay under ignored `outputs/`; compact reports belong in `reports/`.
- OpenEMMA execution and audit evaluation may use separate environments and exchange JSON/JSONL.
- `GOAL.md` is the ordered executable roadmap; work continues from its first incomplete phase.

## Accepted stages

- **Stage 1 — scientifically accepted and merged to `main`: PASSED.** The trusted evaluator
  covers 214 nuScenes mini windows. Recorded-timestamp reconstruction achieved mean ADE
  0.091741 m and mean FDE 0.165879 m; maximum arc-fit residual was 0.084266 m.
  Compact `reports/stage1/` artifacts exist on PR #2 but are not yet merged.
- **Stage 2 — scientifically accepted, awaiting merge/cleanup in Draft PR #2: PASSED.**
  The frozen history-only baseline run covers 214 windows and 856 records. Four deterministic
  baselines were evaluated; sanitized-minus-raw oracle mean ADE was 0.000167 m.
- **OpenEMMA architecture / Phase 0 — PASSED in Draft PR #3, awaiting review/merge.** Locking,
  ownership boundaries, contracts, context guidance, and feasibility gates exist. Local checks
  and GitHub Actions passed after the timestamp-validation repair. Static audit, untouched pilot,
  trusted re-evaluation, and adapter parity have not been performed.

## Active branches and PRs

- `main`: Stage 1 evaluator merged.
- PR #2, `stage2-frozen-baselines` -> `main`: open Draft and unmerged.
- PR #3, `architecture/openemma-upstream` -> `main`: open Draft and unmerged; this is the
  active branch. `GOAL.md` defines Phase 1 as the first incomplete milestone.

## Pinned upstreams

- Official OpenEMMA: `https://github.com/taco-group/OpenEMMA`, commit
  `8403ea636696c5c10e8fdeca566410de0a07e449`, local path `third_party/OpenEMMA`.
  The checkout is absent: **not yet verified locally**.
- Legacy CoT (`Config`): `https://github.com/RuiCao210308/CoT`, commit
  `a214a2ccc2581e4a59e59d392fb969c29519044e`, local path `third_party/CoT-legacy`.
  The checkout is absent: **not yet verified locally**.

## Data and environment

- Repository: `/home/iuroac/emma/Emma-reasoning`.
- Conda environment: `emma-reasoning`.
- nuScenes dataroot: `/data2t/iuroac/nuscenes`.
- Dataset version used for accepted Stage 1/2 results: `v1.0-mini` (`CAM_FRONT`).

## Current blockers

- PR #2 and PR #3 remain Draft and unmerged, so their artifacts are not available on `main`.
- Pinned upstream checkouts are absent and have not been locally verified.
- No OpenEMMA parity evidence exists yet.
- The PR #3 body still lacks the context-guidance summary because this host has no authenticated
  GitHub API client; branch commits and CI are current.

## Next milestone

Complete Phase 1 in `GOAL.md`: synchronize the pinned clean upstreams, perform the static source
audit, and publish its compact report. Stop before model inference.

## Update rule

Update this file in the same commit whenever active state changes. Do not keep full history here;
remove completed active items once stable committed reports own them. Keep the file below 10 KiB.
