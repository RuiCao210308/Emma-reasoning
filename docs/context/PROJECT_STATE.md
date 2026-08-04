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
  and GitHub Actions passed after the timestamp-validation repair.
- **OpenEMMA static audit / Phase 1 — PASSED.** Both pinned checkouts are exact and clean. The
  source audit found input/prompt divergence, silent failure-denominator changes, untrusted
  official timing/alignment, and future leakage in the separate waypoint/legacy paths. Untouched
  pilot readiness was NOT PASSED before the bounded route was approved; see
  `reports/openemma_static_audit/report.md`.
- **Untouched pilot preparation / Phase 2 — APPROVED_WITH_GATES.** A six-sample observed-only
  manifest and record contract are frozen under `experiments/openemma_parity_pilot/`. The approved
  route is a minimal external control-plane wrapper with pre-inference input parity. One-sample
  smoke and the remaining five samples are authorized only under the gates in `APPROVAL.md`.

## Active branches and PRs

- `main`: Stage 1 evaluator merged.
- PR #2, `stage2-frozen-baselines` -> `main`: open Draft and unmerged.
- PR #3, `architecture/openemma-upstream` -> `main`: open Draft and unmerged; this is the
  active branch. `GOAL.md` defines Phase 2 as the first incomplete milestone.

## Pinned upstreams

- Official OpenEMMA: `https://github.com/taco-group/OpenEMMA`, commit
  `8403ea636696c5c10e8fdeca566410de0a07e449`, local path `third_party/OpenEMMA`.
  The local checkout matches the commit and is clean: **verified locally**.
- Legacy CoT (`Config`): `https://github.com/RuiCao210308/CoT`, commit
  `a214a2ccc2581e4a59e59d392fb969c29519044e`, local path `third_party/CoT-legacy`.
  The local checkout matches the commit and is clean: **verified locally**.

## Data and environment

- Repository: `/home/iuroac/emma/Emma-reasoning`.
- Conda environment: `emma-reasoning`.
- nuScenes dataroot: `/data2t/iuroac/nuscenes`.
- Dataset version used for accepted Stage 1/2 results: `v1.0-mini` (`CAM_FRONT`).

## Current blockers

- PR #2 and PR #3 remain Draft and unmerged, so their artifacts are not available on `main`.
- No OpenEMMA parity evidence exists yet.
- The approved wrapper still needs pre-inference parity proof and a validated terminal-record
  schema before model loading.
- No Qwen weights were cached at pilot-contract creation, the audit environment lacks model
  dependencies, and the last runtime check did not expose a working NVIDIA driver/device.
- Model download and GPU inference may proceed only when the environment, disk, revision, and
  one-sample smoke gates in `experiments/openemma_parity_pilot/APPROVAL.md` pass.

## Next milestone

Implement the minimal external control-plane wrapper, prove pre-inference parity against the
pinned official Qwen functions, validate the runtime environment, then run the authorized
one-sample smoke if a working GPU is available. Stop with `BLOCKED_GPU` when it is not.

## Update rule

Update this file in the same commit whenever active state changes. Do not keep full history here;
remove completed active items once stable committed reports own them. Keep the file below 10 KiB.
