#!/usr/bin/env python3
"""Audit the speed-curvature representation against nuScenes ego poses.

The script never calls a VLM. It fits one speed-curvature action between each
future pose pair, integrates those actions from the final observed pose, and
measures how much error is introduced by the action representation itself.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from nuscenes.nuscenes import NuScenes

from emma_reasoning.data import iter_ego_windows
from emma_reasoning.evaluation import evaluate_trajectory
from emma_reasoning.trajectory import (
    estimate_interval_actions,
    integrate_speed_curvature,
    world_to_ego_xy,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataroot", type=Path, required=True)
    parser.add_argument("--version", default="v1.0-mini")
    parser.add_argument("--camera-channel", default="CAM_FRONT")
    parser.add_argument("--obs-len", type=int, default=10)
    parser.add_argument("--fut-len", type=int, default=10)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--max-scenes", type=int, default=None)
    parser.add_argument("--max-windows", type=int, default=200)
    parser.add_argument("--nominal-dt", type=float, default=0.5)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/reconstruction_audit/records.jsonl"),
    )
    parser.add_argument(
        "--assert-max-actual-ade",
        type=float,
        default=None,
        help="Exit with failure when the maximum actual-timestamp ADE exceeds this value.",
    )
    return parser.parse_args()


def metrics_to_dict(metrics: Any) -> dict[str, float]:
    return {
        "ade_m": metrics.ade_m,
        "fde_m": metrics.fde_m,
        "longitudinal_mae_m": metrics.longitudinal_mae_m,
        "lateral_mae_m": metrics.lateral_mae_m,
    }


def horizon_metrics(
    predicted_xy: np.ndarray,
    target_xy: np.ndarray,
    *,
    dt: float,
) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    duration = predicted_xy.shape[0] * dt
    for horizon in (1.0, 2.0, 3.0, 5.0):
        if horizon <= duration + 1e-9:
            metrics = evaluate_trajectory(
                predicted_xy,
                target_xy,
                horizon_seconds=horizon,
                dt=dt,
            )
            result[f"{horizon:g}s"] = metrics_to_dict(metrics)
    return result


def summarize(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "p95": float(np.quantile(array, 0.95)),
        "max": float(np.max(array)),
    }


def main() -> None:
    args = parse_args()
    if not args.dataroot.exists():
        raise FileNotFoundError(f"nuScenes dataroot does not exist: {args.dataroot}")
    if args.nominal_dt <= 0:
        raise ValueError("--nominal-dt must be positive.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    summary_path = args.output.with_name("summary.json")

    nusc = NuScenes(version=args.version, dataroot=str(args.dataroot), verbose=True)

    actual_ades: list[float] = []
    actual_fdes: list[float] = []
    nominal_ades: list[float] = []
    nominal_fdes: list[float] = []
    fit_residuals: list[float] = []
    dt_deviations: list[float] = []
    records_written = 0

    with args.output.open("w", encoding="utf-8") as handle:
        for window in iter_ego_windows(
            nusc,
            obs_len=args.obs_len,
            fut_len=args.fut_len,
            stride=args.stride,
            camera_channel=args.camera_channel,
            max_scenes=args.max_scenes,
            max_windows=args.max_windows,
        ):
            anchor = window.anchor_index
            anchor_position = window.positions_world_xy[anchor]
            anchor_heading = float(window.headings_world_rad[anchor])

            state_slice = slice(anchor, anchor + window.fut_len + 1)
            future_state_positions = window.positions_world_xy[state_slice]
            future_state_headings = window.headings_world_rad[state_slice]
            future_state_timestamps = window.timestamps_seconds[state_slice]

            actions = estimate_interval_actions(
                future_state_positions,
                future_state_headings,
                future_state_timestamps,
            )
            target_local_xy = world_to_ego_xy(
                window.positions_world_xy[anchor + 1 : anchor + window.fut_len + 1],
                anchor_position,
                anchor_heading,
            )

            actual_rollout = integrate_speed_curvature(
                actions.speeds_mps,
                actions.curvatures_inv_m,
                dt=actions.dt_seconds,
            )
            nominal_rollout = integrate_speed_curvature(
                actions.speeds_mps,
                actions.curvatures_inv_m,
                dt=args.nominal_dt,
            )

            actual_metrics = evaluate_trajectory(actual_rollout.positions, target_local_xy)
            nominal_metrics = evaluate_trajectory(nominal_rollout.positions, target_local_xy)

            record = {
                "sample_id": window.sample_id,
                "scene_name": window.scene_name,
                "start_index": window.start_index,
                "anchor_sample_token": window.sample_tokens[anchor],
                "obs_len": window.obs_len,
                "fut_len": window.fut_len,
                "nominal_dt_seconds": args.nominal_dt,
                "dt_seconds": actions.dt_seconds.tolist(),
                "dt_abs_deviation_from_nominal_seconds": np.abs(
                    actions.dt_seconds - args.nominal_dt
                ).tolist(),
                "speeds_mps": actions.speeds_mps.tolist(),
                "curvatures_inv_m": actions.curvatures_inv_m.tolist(),
                "interval_arc_fit_residual_m": actions.fit_residual_m.tolist(),
                "target_ego_xy_m": target_local_xy.tolist(),
                "reconstructed_actual_dt_ego_xy_m": actual_rollout.positions.tolist(),
                "reconstructed_nominal_dt_ego_xy_m": nominal_rollout.positions.tolist(),
                "actual_timestamp_metrics": metrics_to_dict(actual_metrics),
                "nominal_dt_metrics": metrics_to_dict(nominal_metrics),
                "nominal_horizon_metrics": horizon_metrics(
                    nominal_rollout.positions,
                    target_local_xy,
                    dt=args.nominal_dt,
                ),
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

            actual_ades.append(actual_metrics.ade_m)
            actual_fdes.append(actual_metrics.fde_m)
            nominal_ades.append(nominal_metrics.ade_m)
            nominal_fdes.append(nominal_metrics.fde_m)
            fit_residuals.extend(actions.fit_residual_m.tolist())
            dt_deviations.extend(np.abs(actions.dt_seconds - args.nominal_dt).tolist())
            records_written += 1

            if records_written % 50 == 0:
                print(f"Processed {records_written} windows...")

    if records_written == 0:
        raise RuntimeError("No valid windows were produced. Check version, data, and lengths.")

    summary = {
        "version": args.version,
        "dataroot": str(args.dataroot.resolve()),
        "camera_channel": args.camera_channel,
        "obs_len": args.obs_len,
        "fut_len": args.fut_len,
        "stride": args.stride,
        "records": records_written,
        "actual_timestamp_ade_m": summarize(actual_ades),
        "actual_timestamp_fde_m": summarize(actual_fdes),
        "nominal_dt_ade_m": summarize(nominal_ades),
        "nominal_dt_fde_m": summarize(nominal_fdes),
        "interval_arc_fit_residual_m": summarize(fit_residuals),
        "timestamp_abs_deviation_from_nominal_seconds": summarize(dt_deviations),
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"Records: {args.output}")
    print(f"Summary: {summary_path}")

    if args.assert_max_actual_ade is not None:
        maximum = summary["actual_timestamp_ade_m"]["max"]
        if maximum > args.assert_max_actual_ade:
            raise SystemExit(
                f"Reconstruction audit failed: max actual ADE {maximum:.6f} m exceeds "
                f"{args.assert_max_actual_ade:.6f} m."
            )


if __name__ == "__main__":
    main()
