# Stage 1 nuScenes reconstruction audit

## Scope and conventions

Audit date: 2026-08-04. Dataset: nuScenes `v1.0-mini`, `CAM_FRONT`, dataroot
`/data2t/iuroac/nuscenes`. A window contains 10 observed keyframes and 10 future
keyframes at stride 1. The prediction anchor is observed index 9; future index 0 is the
state after the first future interval. Across the 10 scenes, the independent metadata
count `sum(max(0, scene_frames - 19))` is 214, matching the 214 emitted windows.

The anchor pose, never a future target, defines ego-local origin and yaw. Local `+x` is
anchor-forward and `+y` is anchor-left. Speed is in m/s, signed curvature in 1/m, and
camera `sample_data` timestamps supply one measured `dt` per interval. The nominal
comparison forces the same fitted actions to 0.5 s. ADE and FDE use the same 10 aligned
post-interval states.

## Full mini results

All values are metres except timestamp deviation (seconds).

| Metric | Mean | Median | p95 | Max |
|---|---:|---:|---:|---:|
| Actual-timestamp ADE | 0.091741 | 0.088441 | 0.223574 | 0.319455 |
| Actual-timestamp FDE | 0.165879 | 0.157919 | 0.423835 | 0.553636 |
| Nominal-0.5-s ADE | 0.153597 | 0.124017 | 0.446983 | 0.704037 |
| Nominal-0.5-s FDE | 0.227880 | 0.206305 | 0.706490 | 0.934450 |
| Interval arc-fit residual | 0.016751 | 0.014016 | 0.047656 | 0.084266 |
| `abs(actual dt - 0.5)` | 0.006755 | 0.000000 | 0.050000 | 0.100017 |

The per-window mean difference (actual minus nominal) is -0.061856 m ADE and
-0.062001 m FDE, so recorded timestamps are better overall. A small number of windows
have slightly worse actual FDE (maximum difference 0.074103 m); this is compatible with
the circular-arc approximation and does not reverse the aggregate result.

## Worst actual-ADE windows

All ten are overlapping windows from `scene-1077`, so they identify one localized
sequence rather than ten independent failures.

| Sample | ADE | FDE | Max arc residual | Max dt deviation |
|---|---:|---:|---:|---:|
| scene-1077:0016 | 0.319455 | 0.553636 | 0.084266 | 0.050000 |
| scene-1077:0017 | 0.313293 | 0.533982 | 0.084266 | 0.050000 |
| scene-1077:0018 | 0.310331 | 0.511129 | 0.084266 | 0.050000 |
| scene-1077:0019 | 0.307212 | 0.495211 | 0.084266 | 0.050000 |
| scene-1077:0015 | 0.278102 | 0.517648 | 0.084266 | 0.050000 |
| scene-1077:0020 | 0.267849 | 0.448940 | 0.067302 | 0.050000 |
| scene-1077:0014 | 0.266343 | 0.525595 | 0.084266 | 0.050000 |
| scene-1077:0021 | 0.249435 | 0.428170 | 0.067302 | 0.050000 |
| scene-1077:0013 | 0.243269 | 0.487792 | 0.084266 | 0.050000 |
| scene-1077:0000 | 0.230561 | 0.371369 | 0.067848 | 0.050000 |

## Diagnostics and decision

Mean actual-timestamp displacement error increases from 0.016998 m at step 1 to
0.083936 m at step 5 and 0.165879 m at step 10. This monotonic accumulation is explained
by integrating, rather than snapping away, each interval's measured arc-fit residual.
It is representation error, remains within the declared ADE gates, and does not show a
time-index or coordinate-sign discontinuity.

Observed speed ranges from -0.024106 to 15.158620 m/s. There are 358 negative-speed
interval occurrences, but none is below -0.1 m/s. Curvature ranges from -1095.06 to
1388.21 1/m: investigation found all 334 occurrences with `abs(curvature) > 1` 1/m at
`abs(speed) < 0.01` m/s, and zero while moving at or above that threshold. These are the
known speed-curvature singularity under near-stationary pose/yaw noise, not plausible
hard turns; no values were clipped or excluded. Recorded `dt` ranges from 0.399983 to
0.600000 s, with no interval more than 0.15 s away from nominal. No record is malformed,
non-finite, or missing an action.

**Stage 1: PASSED** for the trusted trajectory integration and ADE/FDE evaluator. The
actual ADE mean/p95/max gates pass, no arc residual exceeds 0.10 m, the full window count
is accounted for, and actual timestamps improve aggregate ADE/FDE.

Remaining risks are the near-stop curvature singularity, correlated worst cases in one
mini scene, and the limited size of `v1.0-mini`. Frozen trajectory baselines may begin
with this evaluator. Before training or scoring raw action regression, define and freeze
an explicit near-stop action policy (or a non-singular yaw-rate representation) and test
it without using future targets to select per-example behavior.
