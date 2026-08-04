# Phase 2 execution approval

Decision date: 2026-08-04  
Status: APPROVED_WITH_GATES

## Approved control path

Use the recommended **minimal external control-plane wrapper**.

The wrapper must invoke or instrument the pinned official OpenEMMA Qwen path without editing the official checkout and without independently reimplementing model loading, processor construction, image preprocessing, prompt construction, generation, retry semantics, parser behavior, or official metric behavior.

Because the official CLI is hard-coded to two scenes and cannot select the six frozen windows, move adapter/input parity proof before the model pilot. The bounded pilot may proceed only after the wrapper passes the pre-inference parity gate below.

The following alternatives are not approved for this phase:

- an in-place upstream source edit;
- a patched run presented as untouched;
- the unbounded official two-scene CLI run;
- a parallel Qwen/OpenEMMA implementation.

## Approved scope

- Manifest: `experiments/openemma_parity_pilot/manifest.json`.
- Expected samples: exactly 6.
- Official source: OpenEMMA commit `8403ea636696c5c10e8fdeca566410de0a07e449`.
- Backend: `Qwen/Qwen2-VL-7B-Instruct`.
- Model revision: `eed13092ef92e448dd6875b2a00151bd3f7db0ac`.
- Method: official `openemma` path only.
- Maximum model-running budget: 2 GPU-hours.
- No full mini or trainval run is authorized.
- No CoT, SC, ToT, search, GRTC, or causal intervention is authorized in this phase.

## Pre-inference parity gate

Before model loading, the wrapper must prove on deterministic mocked or stubbed calls that it preserves:

1. ordered image paths actually supplied to the official Qwen processor;
2. observed speed/curvature values and curvature scaling;
3. exact scene, object, intent, and motion prompt strings;
4. call order;
5. generation parameters;
6. retry boundaries and terminal failure accounting;
7. official parser and official metric invocation boundaries;
8. one terminal record per manifest sample, including failures.

The proof must compare wrapper-captured inputs against values produced by the pinned official functions, not against manually rewritten expected strings alone.

A wrapper that imports a later redefined function while script execution would use an earlier definition does not pass. The chosen callable boundary must be explicit and backed by source/runtime evidence.

## Environment and download authorization

A separate upstream runtime environment may be created and required dependencies may be installed.

Model download is authorized only when all of the following are true:

- a working NVIDIA device and driver are visible;
- available GPU memory is sufficient for the declared dtype and loading method;
- at least 30 GB of free disk is available at the selected cache location;
- no equivalent pinned snapshot already exists in an accessible cache;
- the download path and cache identity are recorded;
- the official checkout remains clean.

Prefer an existing exact cached snapshot over downloading again.

If no working GPU is visible, complete the wrapper, schema, dry-run, and environment plan, then stop with `BLOCKED_GPU` rather than attempting CPU inference or changing the model.

## First inference authorization

The first GPU model inference is authorized only for a one-sample smoke after the pre-inference parity gate passes.

The smoke must stop and report before the remaining five samples if any of these occur:

- official and captured prompts/inputs differ;
- raw calls are not attributable to one manifest sample;
- a failure can disappear without a terminal record;
- peak memory is unsafe;
- projected six-sample runtime exceeds 2 GPU-hours;
- the official checkout becomes dirty;
- the model revision cannot be verified.

After a successful one-sample smoke, the remaining five manifest samples are authorized under the same unchanged configuration.

## Required records

Every sample must retain:

- sample and manifest identity;
- official commit and clean status;
- model ID and exact revision;
- environment identity and command;
- actual ordered image paths;
- observed motion input;
- every prompt and call type;
- generation settings;
- every raw response;
- retry count and structured errors;
- official parse result and metric record;
- terminal status;
- wall time and peak GPU memory when available.

Expected terminal-record coverage is 6/6, including failures.

## Stop after Phase 2

After the six-sample pilot, generate its compact report, update `GOAL.md` and `PROJECT_STATE.md`, push to PR #3, and stop before trusted re-evaluation or any reasoning-method experiment.
