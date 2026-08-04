#!/usr/bin/env python3
"""Build the frozen Phase 2 pilot manifest without using future targets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from nuscenes import NuScenes

from emma_reasoning.data import iter_ego_windows

OPENEMMA_COMMIT = "8403ea636696c5c10e8fdeca566410de0a07e449"
MODEL_REVISION = "eed13092ef92e448dd6875b2a00151bd3f7db0ac"
SELECTED_SAMPLES = {
    "scene-0061:0010": "visually_nontrivial",
    "scene-0103:0008": "decelerating",
    "scene-0553:0021": "near_stop",
    "scene-0916:0011": "turn_right",
    "scene-1077:0015": "straight_fast",
    "scene-1094:0009": "turn_left",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataroot", type=Path, required=True)
    parser.add_argument("--version", default="v1.0-mini")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/openemma_parity_pilot/manifest.json"),
    )
    return parser.parse_args()


def observed_record(nusc: NuScenes, window: object) -> dict[str, object]:
    obs_len = window.obs_len
    positions = window.positions_world_xy[:obs_len]
    timestamps = window.timestamps_seconds[:obs_len]
    speeds = np.linalg.norm(np.diff(positions, axis=0), axis=1) / np.diff(timestamps)
    headings = np.unwrap(window.headings_world_rad[:obs_len])
    anchor_token = window.sample_tokens[window.anchor_index]
    anchor_sample = nusc.get("sample", anchor_token)
    dataroot = Path(nusc.dataroot)

    image_relpaths = [
        str(Path(path).relative_to(dataroot))
        for path in window.image_paths[:obs_len]
    ]
    return {
        "sample_id": window.sample_id,
        "regime": SELECTED_SAMPLES[window.sample_id],
        "scene_name": window.scene_name,
        "start_index": window.start_index,
        "anchor_sample_token": anchor_token,
        "observed_image_relpaths": image_relpaths,
        "official_qwen_image_relpaths": [image_relpaths[-1]],
        "selection_features": {
            "observed_anchor_speed_mps": round(float(speeds[-1]), 6),
            "observed_mean_speed_mps": round(float(speeds.mean()), 6),
            "observed_heading_change_rad": round(float(headings[-1] - headings[0]), 6),
            "anchor_annotation_count": len(anchor_sample["anns"]),
        },
    }


def build_manifest(dataroot: Path, version: str) -> dict[str, object]:
    nusc = NuScenes(version=version, dataroot=str(dataroot), verbose=False)
    selected: dict[str, dict[str, object]] = {}
    for window in iter_ego_windows(nusc, obs_len=10, fut_len=10, camera_channel="CAM_FRONT"):
        if window.sample_id in SELECTED_SAMPLES:
            selected[window.sample_id] = observed_record(nusc, window)

    missing = sorted(set(SELECTED_SAMPLES) - set(selected))
    if missing:
        raise RuntimeError(f"Selected samples are missing from {version}: {', '.join(missing)}")

    samples = [selected[sample_id] for sample_id in SELECTED_SAMPLES]
    return {
        "schema_version": 1,
        "experiment_id": "openemma_parity_pilot_v1",
        "status": "BLOCKED_PRE_INFERENCE",
        "dataset": {
            "name": "nuScenes",
            "version": version,
            "camera_channel": "CAM_FRONT",
            "observation_keyframes": 10,
            "future_keyframes": 10,
            "stride": 1,
        },
        "selection": {
            "uses_future_targets": False,
            "policy": "fixed IDs selected from observed motion and anchor annotations only",
            "expected_records": len(samples),
        },
        "upstream": {
            "repository": "https://github.com/taco-group/OpenEMMA",
            "commit": OPENEMMA_COMMIT,
            "checkout": "third_party/OpenEMMA",
            "required_clean": True,
        },
        "model": {
            "model_id": "Qwen/Qwen2-VL-7B-Instruct",
            "revision": MODEL_REVISION,
            "dtype": "bfloat16",
            "method": "openemma",
            "generation": {
                "max_new_tokens": 128,
                "sampling": False,
                "seed": 0,
            },
            "weights_cached_at_manifest_build": False,
        },
        "samples": samples,
        "record_contract": {
            "one_terminal_record_per_sample": True,
            "required_fields": [
                "run_id",
                "sample_id",
                "upstream_commit",
                "upstream_clean",
                "model_id",
                "model_revision",
                "ordered_image_paths",
                "observed_motion_inputs",
                "calls",
                "official_parse",
                "official_metric",
                "terminal_status",
                "error",
                "wall_time_seconds",
                "peak_gpu_memory_bytes",
            ],
            "call_fields": [
                "role",
                "attempt",
                "prompt",
                "system_message",
                "generation_config",
                "raw_text",
                "error",
            ],
        },
        "failure_policy": {
            "expected_denominator": len(samples),
            "retain_parse_failures": True,
            "retain_runtime_failures": True,
            "retain_partial_actions": True,
            "never_replace_with_ground_truth": True,
        },
        "compute_gate": {
            "maximum_gpu_hours": 2.0,
            "maximum_samples": len(samples),
            "full_run_authorized": False,
            "model_download_authorized": False,
            "model_inference_authorized": False,
        },
        "blockers": [
            (
                "The official CLI filters to scene-0103 and scene-1077, excluding "
                "four selected samples."
            ),
            (
                "The official CLI cannot bound execution to the six manifest windows "
                "without control-plane instrumentation."
            ),
            (
                "No Qwen weights are cached and the required download exceeds the "
                "autonomous 5 GB gate."
            ),
            "The current host exposes no working NVIDIA driver/device to nvidia-smi.",
            "The audit environment intentionally lacks torch, transformers, and qwen_vl_utils.",
        ],
    }


def main() -> None:
    args = parse_args()
    manifest = build_manifest(args.dataroot.resolve(), args.version)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(manifest['samples'])} samples to {args.output}")


if __name__ == "__main__":
    main()
