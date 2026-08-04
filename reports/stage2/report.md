# Stage 2 frozen trajectory baselines

## 实验目的

建立仅使用历史观测、使用真实 future dt 积分的可复现 ego-motion 基线。

## 数据、窗口和时间定义

nuScenes `v1.0-mini`；10 observed + 10 future keyframes；214 windows / 856 records。名义 1/2/3/5 秒仅表示 keyframe step 2/4/6/10；所有积分使用实际时间戳差。

## Near-stop 动作策略

固定 `speed_epsilon_mps=0.1`。保留 raw speed/curvature；所有区间保存 yaw rate；near-stop curvature 置零并从 curvature MAE 排除，moving curvature 不裁剪。

## 防未来泄漏接口

预测器只接收 `ObservedMotion`（anchor 及之前）和 `PredictionSchedule`（step count 与 future dt）；
不接收 `EgoWindow`、未来 pose/heading/action。

## Baseline 定义

`stationary`、`last_speed_straight`、`constant_last`、`median3` 均输出 10-step chunk。

## Sanitized oracle 相对 raw oracle 的代价

ADE delta mean/median/p95/max = 0.000167 / 0.000000 / 0.000300 / 0.006113 m。
FDE delta mean/median/p95/max = 0.000433 / 0.000000 / 0.000989 / 0.015462 m。

## 完整结果

| Method | ADE mean/median/p95/max (m) | FDE mean/median/p95/max (m) | Long MAE | Lat MAE | Speed MAE | Yaw-rate MAE | Masked curvature MAE |
|---|---|---|---:|---:|---:|---:|---:|
| stationary | 15.0743/13.2931/37.6039/40.9990 | 27.6933/24.0507/70.0576/74.4328 | 14.8874 | 0.8903 | 5.5720 | 0.0385 | 0.0210 |
| last_speed_straight | 2.3568/1.5080/7.3472/11.1050 | 5.5635/3.4901/17.5627/25.3733 | 1.8916 | 0.8903 | 0.8914 | 0.0385 | 0.0210 |
| constant_last | 2.2080/1.4944/6.1171/11.1086 | 5.3763/3.4670/15.0399/27.0366 | 1.9621 | 0.6302 | 0.8914 | 0.0465 | 0.0232 |
| median3 | 2.7136/1.7383/8.6280/13.4743 | 6.2932/4.1656/20.0679/31.5204 | 2.4059 | 0.7806 | 1.0338 | 0.0519 | 0.0262 |

### 名义 keyframe 结果（实际 dt 积分）

| Method | step 2 ADE/FDE | step 4 ADE/FDE | step 6 ADE/FDE | step 10 ADE/FDE |
|---|---:|---:|---:|---:|
| stationary | 4.0571/5.4110 | 6.7750/10.8588 | 9.5140/16.3767 | 15.0743/27.6933 |
| last_speed_straight | 0.2427/0.3632 | 0.5931/1.1711 | 1.0741/2.3514 | 2.3568/5.5635 |
| constant_last | 0.2206/0.3274 | 0.5320/1.0479 | 0.9709/2.1452 | 2.2080/5.3763 |
| median3 | 0.3561/0.5078 | 0.7583/1.4111 | 1.2888/2.6954 | 2.7136/6.2932 |

### Sanitized-minus-raw oracle 每步 displacement error mean

step | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
delta m | -0.000000 | 0.000008 | 0.000027 | 0.000059 | 0.000105 | 0.000158 | 0.000225 | 0.000294 | 0.000366 | 0.000433

## 每个 scene 的主要差异

- `scene-0061`: best `constant_last` ADE 2.3730 m; worst `stationary` ADE 10.8215 m.
- `scene-0103`: best `constant_last` ADE 5.3742 m; worst `stationary` ADE 11.9247 m.
- `scene-0553`: best `stationary` ADE 0.0000 m; worst `last_speed_straight` ADE 0.0000 m.
- `scene-0655`: best `last_speed_straight` ADE 1.8557 m; worst `stationary` ADE 22.0358 m.
- `scene-0757`: best `stationary` ADE 1.0853 m; worst `median3` ADE 1.7943 m.
- `scene-0796`: best `last_speed_straight` ADE 0.5963 m; worst `stationary` ADE 32.7582 m.
- `scene-0916`: best `constant_last` ADE 3.1649 m; worst `stationary` ADE 13.5616 m.
- `scene-1077`: best `last_speed_straight` ADE 1.7269 m; worst `stationary` ADE 37.6547 m.
- `scene-1094`: best `last_speed_straight` ADE 5.0130 m; worst `stationary` ADE 20.4889 m.
- `scene-1100`: best `stationary` ADE 0.2597 m; worst `median3` ADE 0.3936 m.

## 最差样本

- `stationary` `scene-1077:0021`: ADE 40.9990 m, FDE 74.4328 m
- `stationary` `scene-1077:0019`: ADE 40.9833 m, FDE 74.1657 m
- `stationary` `scene-1077:0020`: ADE 40.9125 m, FDE 74.2148 m
- `stationary` `scene-1077:0016`: ADE 40.6791 m, FDE 74.3680 m
- `stationary` `scene-1077:0015`: ADE 40.3734 m, FDE 74.1243 m
- `stationary` `scene-1077:0018`: ADE 40.2691 m, FDE 73.3826 m
- `stationary` `scene-1077:0017`: ADE 40.2325 m, FDE 73.9665 m
- `stationary` `scene-1077:0014`: ADE 39.9599 m, FDE 73.0285 m
- `stationary` `scene-1077:0013`: ADE 39.5722 m, FDE 72.5722 m
- `stationary` `scene-1077:0012`: ADE 39.0674 m, FDE 71.8872 m

## 异常与风险

Future near-stop: 554/2140 (25.89%); negative predicted actions: 990; non-finite predictions: 0. Max |speed| 14.986 m/s; max moving |curvature| 0.192 1/m.
Observed/future negative speeds: 268/358; all are near-stop (negative moving count 0, minimum -0.0241 m/s), consistent with pose-fit noise. Near-stop raw curvature reaches 1388.212 1/m but is retained for audit and sanitized to zero; moving raw curvature max is 0.192 1/m.

- Pose-derived interval actions retain constant-curvature fitting residual.
- Nominal horizon labels are step 2/4/6/10; actual elapsed times vary.

## 质量检查

pytest: PASSED (27 tests)；ruff: PASSED；未来泄漏: PASSED by typed interface and unit test；离线重汇总: PASSED。

## Stage 2 状态

**Stage 2: PASSED**

## 下一阶段建议

Use these frozen baselines as mandatory non-VLM controls before later modeling.
