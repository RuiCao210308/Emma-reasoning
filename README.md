# Emma-reasoning

Research code for auditing inference-time reasoning in vision-language motion planning.

The project asks whether additional inference-time computation—Chain-of-Thought, Self-Consistency, and candidate search—actually increases visual grounding, or merely reinforces ego-motion persistence and trajectory smoothness.

## Architecture principle

Emma-reasoning does **not** independently rewrite OpenEMMA model inference. The official implementation is cloned at a pinned commit under `third_party/OpenEMMA`, then invoked through a thin, provenance-recording adapter.

Responsibilities are separated:

- **OpenEMMA upstream:** model loading, image preprocessing, prompts, and original inference behavior;
- **Emma-reasoning adapter:** exact input/output/provenance capture and explicit interventions;
- **Emma-reasoning evaluator:** parsing audits, timestamp-aware trajectory integration, metrics, and causal comparisons;
- **local outputs:** large raw JSONL, caches, and checkpoints that are not committed.

See `docs/architecture.md`, `docs/experiment_gate.md`, and `docs/provenance/openemma.md` before implementing a VLM experiment.

## Repository map

```text
upstreams/                     pinned external repository locks
third_party/                   local ignored OpenEMMA/legacy checkouts
patches/openemma/              reviewed patches only when unavoidable
src/emma_reasoning/adapters/   thin upstream boundaries
src/emma_reasoning/evaluation/ trusted evaluation
src/emma_reasoning/trajectory/ trusted action and trajectory geometry
experiments/                   declarative experiment manifests
reports/                       compact committed results
outputs/                       large local records
```

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

## External repositories

List the pinned sources:

```bash
python scripts/manage_upstreams.py list
```

Clone both official OpenEMMA and the historical CoT prototype using SSH:

```bash
python scripts/manage_upstreams.py sync --transport ssh
```

Verify exact commits and clean worktrees before any run:

```bash
python scripts/manage_upstreams.py verify
```

The official OpenEMMA checkout is pinned to commit `8403ea636696c5c10e8fdeca566410de0a07e449`. The legacy `CoT` Config prototype is pinned separately and is never treated as a paper baseline without parity re-evaluation.

## Trusted evaluation status

Stage 1 established and tested:

- speed-curvature integration with scalar or recorded per-step `dt`;
- prediction from the final observed ego pose, without future-point leakage;
- world-to-ego coordinate conversion;
- aligned ADE/FDE horizon indexing;
- deterministic nuScenes sliding windows;
- pose-to-action fitting with an explicit residual audit.

These utilities are an external audit layer. They do not constitute an OpenEMMA reproduction.

## Next required milestone

The next VLM milestone is an **OpenEMMA provenance and parity audit**, not a new inference implementation:

1. inspect the pinned official source path;
2. record actual frames, prompts, generation settings, parsing, retries, and evaluator behavior;
3. run an untouched deterministic upstream pilot;
4. re-evaluate the same raw outputs with the trusted evaluator;
5. explain discrepancies before adding CoT, SC, ToT, or GRTC interventions.
