# Emma-reasoning

Research code for auditing inference-time reasoning in vision-language motion planning.

The project asks whether additional inference-time computation—Chain-of-Thought, Self-Consistency, and candidate search—actually increases visual grounding, or merely reinforces ego-motion persistence and trajectory smoothness.

## Current milestone

**Stage 1: trusted trajectory evaluation core**

Before running any VLM experiments, the repository establishes and tests:

- explicit speed-curvature integration with scalar or recorded per-step `dt`;
- prediction from the final observed ego pose, without future-point leakage;
- world-to-ego coordinate conversion;
- consistent ADE/FDE horizon indexing;
- speed and curvature metrics with explicit units;
- deterministic nuScenes sliding windows;
- pose-to-action fitting with a reported constant-curvature residual;
- unit tests for temporal alignment and geometry.

No quantitative result should be treated as a paper result until it is produced by the tested evaluation pipeline in this repository.

## Installation

```bash
conda create -n emma-reasoning python=3.11 -y
conda activate emma-reasoning
python -m pip install -U pip
python -m pip install -e ".[all]"
```

Run code-quality checks:

```bash
pytest
ruff check .
```

## nuScenes reconstruction audit

The first dataset-level experiment does not call a VLM. It extracts timestamped ego poses, fits one speed-curvature action per future interval, integrates from the final observed pose, and measures representation and timing error.

Start with a small pilot:

```bash
python scripts/audit_nuscenes_reconstruction.py \
  --dataroot /path/to/nuscenes \
  --version v1.0-mini \
  --obs-len 10 \
  --fut-len 10 \
  --max-windows 50
```

Outputs:

```text
outputs/reconstruction_audit/records.jsonl
outputs/reconstruction_audit/summary.json
```

The summary separates:

- reconstruction using recorded camera timestamps;
- reconstruction after forcing every future interval to `0.5 s`;
- per-interval circular-arc fitting residual;
- deviation of recorded timestamps from the nominal sampling interval.

This audit must be inspected before adding OpenEMMA or Qwen inference.
