# Stage 1 nuScenes reconstruction audit

## Scope and conventions

Audit date: 2026-08-04. Dataset: nuScenes `v1.0-mini`, `CAM_FRONT`, dataroot `/data2t/iuroac/nuscenes`. A window contains 10 observed keyframes and 10 future keyframes at stride 1. The prediction anchor is observed index 9; future index 0 is the state after the first future interval. Across the 10 scenes, the independent metadata count is 214, matching the emitted windows.

The anchor pose, never a future target, defines ego-local origin and yaw. Local `+x` is anchor-forward and `+y` is anchor-left. Speed is in m/s, signed curvature in 1/m, and camera `sample_data` timestamps provide one measured `dt` per interval. ADE and FDE use the same 10 aligned post-interval states.

## Results

| Metric | Mean | Median | p95 | Max |
|---|---:|---:|---:|---:|
| Actual-timestamp ADE | 0.091741 | 0.088441 | 0.223574 | 0.319455 |
| Actual-timestamp FDE | 0.165879 | 0.157919 | 0.423835 | 0.553636 |
| Nominal-0.5-s ADE | 0.153597 | 0.124017 | 0.446983 | 0.704037 |
| Nominal-0.5-s FDE | 0.227880 | 0.206305 | 0.706490 | 0.934450 |
| Interval arc-fit residual | 0.016751 | 0.014016 | 0.047656 | 0.084266 |
| `abs(actual dt - 0.5)` | 0.006755 | 0.000000 | 0.050000 | 0.100017 |

Recorded timestamps improve mean ADE by 0.061856 m and mean FDE by 0.062001 m relative to forcing every interval to 0.5 s.

## Diagnostics

The worst actual-ADE window is `scene-1077:0016` with ADE 0.319455 m and FDE 0.553636 m. All ten worst windows overlap within `scene-1077`, indicating one localized sequence rather than ten independent failures.

Observed speed ranges from -0.024106 to 15.158620 m/s. Extreme curvature values occur only in near-stationary intervals: all 334 occurrences with `abs(curvature) > 1` 1/m have `abs(speed) < 0.01` m/s. No moving interval at or above that threshold exceeds 1 1/m.

Mean displacement error accumulates from 0.016998 m at step 1 to 0.165879 m at step 10, consistent with integrating interval arc-fit residuals rather than a time-index or coordinate-sign discontinuity.

## Decision

Stage 1 passes the predefined ADE gates, accounts for all 214 valid windows, keeps arc-fit residual below 0.10 m, and shows that recorded timestamps improve aggregate reconstruction.

Remaining risks are the near-stop curvature singularity, correlated worst cases in one mini scene, and the limited size of `v1.0-mini`. Stage 2 must freeze a near-stop action policy before action-level regression or scoring.

**Stage 1: PASSED**
