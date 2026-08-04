# OpenEMMA untouched parity pilot contract

Status: **BLOCKED_PRE_INFERENCE**. This contract freezes the desired bounded pilot, but the
official CLI cannot execute it unchanged and this host is not runtime-ready. No model was loaded
or called while preparing it.

## Question and hypothesis

Question: can the clean pinned official Qwen path produce complete, attributable raw-call records
for six frozen nuScenes samples without changing prompts, image preprocessing, parsing, retries,
or evaluator behavior?

Falsifiable hypothesis: an external control-plane harness can preserve official Qwen inputs and
raw outputs while producing one terminal record per manifest sample, including every failure.

Competing explanation: apparent success is only possible through the unbounded hard-coded scene
loop, import/CLI divergence, or silent removal of failed samples.

## Frozen inputs

- Manifest: `experiments/openemma_parity_pilot/manifest.json`.
- Manifest SHA256: `e0c0a116fc1264f9054fe12c0025760b27e0183919488bd72c764d157508785e`.
- Dataset: nuScenes `v1.0-mini`, `CAM_FRONT`, 10 observed + 10 future keyframes.
- Selection uses observed motion and anchor-time annotation count only; it does not use future
  targets, model output, or test error.
- Regimes: near-stop, left turn, right turn, fast straight, deceleration, and an
  annotation-rich anchor scene.
- Official source: OpenEMMA `8403ea636696c5c10e8fdeca566410de0a07e449`, clean checkout.
- Intended backend: `Qwen/Qwen2-VL-7B-Instruct` revision
  `eed13092ef92e448dd6875b2a00151bd3f7db0ac`, bfloat16, official 128-token greedy generation.

Regenerate the manifest without model execution:

```bash
python scripts/build_openemma_pilot_manifest.py \
  --dataroot /path/to/nuscenes \
  --version v1.0-mini \
  --output experiments/openemma_parity_pilot/manifest.json
```

The committed manifest contains only dataset-relative image paths. The dataroot remains a runtime
argument and is not embedded in committed code or configuration.

## Primary gate

This is a construction/provenance pilot, not a performance experiment. The primary outcome is
terminal record coverage: exactly 6/6 records, counting failures. Each record must contain actual
ordered image inputs, observed motion input, every scene/object/intent/motion call, prompts,
generation settings, raw text, retries, errors, official parse/metric output, runtime, and peak GPU
memory. Offline schema validation must work without another model call.

PASSED requires:

- exact clean upstream and exact model revision;
- no official source modification;
- official Qwen prompt, processor, generation, parser, and evaluator behavior preserved;
- six terminal records and an explicit expected/valid denominator;
- raw calls sufficient for later trusted re-evaluation;
- runtime below two GPU-hours.

NOT PASSED if any manifest item disappears, actual inputs cannot be recorded, source edits are
required but undisclosed, the model revision floats, or the projected budget exceeds two GPU-hours.

## Current blockers

1. Official `main.py` filters to `scene-0103` and `scene-1077`; four manifest samples are outside
   that set. Even within those scenes it cannot select individual windows, so an unchanged CLI run
   would process 43 windows rather than six.
2. Importing `main.py` exposes the later Qwen-only `vlm_inference`, whereas script execution uses
   the earlier multi-backend definition. A wrapper cannot be called “untouched” until this control
   boundary and input parity are explicitly accepted.
3. No selected Qwen snapshot is cached. Its bfloat16 7B weights exceed the 5 GB autonomous
   download gate, so no download is authorized.
4. `nvidia-smi` cannot communicate with a driver and no `/dev/nvidia*` device is visible.
5. The audit environment has nuScenes but intentionally lacks torch, transformers, and
   `qwen_vl_utils`; a separate upstream environment is required.

## Required user decision

Choose one route before implementation or inference:

- allow a minimal external control-plane wrapper and move its input-parity proof before the
  untouched pilot (recommended);
- authorize a reviewed upstream patch adding manifest/window selection, which makes the run
  explicitly patched rather than untouched; or
- authorize the unbounded official two-scene run after a new compute estimate (not recommended).

After that choice, model download, environment installation, and first inference remain separately
gated. Do not start them from this contract alone.
