# OpenEMMA static audit report

## Decision

- **Phase 1 static audit: PASSED.** Both pinned sources match their lock commits, are clean, and
  the required source questions are answered or marked runtime unknown.
- **Untouched pilot readiness: NOT PASSED.** A frozen manifest, model revision, environment, and
  external provenance/failure capture harness are still required.
- No model was loaded or executed.

Detailed evidence: `docs/provenance/openemma_static_audit.md`.

## Provenance

| Source | Full commit | Status |
|---|---|---|
| `https://github.com/taco-group/OpenEMMA` | `8403ea636696c5c10e8fdeca566410de0a07e449` | exact, clean |
| `https://github.com/RuiCao210308/CoT` (`Config`) | `a214a2ccc2581e4a59e59d392fb969c29519044e` | exact, clean |

The checkouts are ignored under `third_party/` and are not committed.

## Official source findings

- The documented repository entry point is `main.py` with 10 observed and 10 future keyframes,
  but it evaluates only two hard-coded mini scenes and omits the last valid window.
- GPT retains ten base64 frames. Qwen, LLaVA, and Llama receive only the final frame even though
  prompts claim a five-second multi-frame sequence.
- OpenEMMA calls scene, object, and stateful intent generation before motion; the fallback method
  skips those rationale calls. Nested retries can make up to 18 calls per OpenEMMA sample, but
  discarded text and retry counts are not saved.
- Backend prompts and generation differ materially. The long system message reaches only GPT;
  LLaVA samples at temperature 0.2; Qwen has a hard-coded local 3B path and floating 7B fallback;
  the documented Llama selector has no CLI loader.
- Script execution uses the first multi-backend `vlm_inference`; importing the module exposes a
  later Qwen-only redefinition.
- Motion “speed” is keyframe displacement norm, actual timestamps are unused, integration spacing
  is inconsistent, and prediction/target index zero is misaligned. No FDE is reported.
- Parsing accepts partial sequences, skips failures after retries, and changes denominators without
  structured records. Only scene aggregates are saved.
- The separate official `BaseOpenEMMA` waypoint API derives rationale from future ground truth and
  is not a leakage-free baseline.

## Legacy Config findings

- `main.py --reasoning-mode cot-sc/tot` mostly adds an instruction string; it is not a validated
  SC or ToT implementation.
- Legacy `BaseOpenEMMA` uses future targets in meta-decisions and ToT scoring.
- `run_tot_new.py` averages valid SC actions after dropping failures and selects ToT candidates
  with history-continuity/smoothness heuristics. It also anchors integration at the first future
  target and does not retain all candidates or failures.

Legacy results are therefore code-archaeology evidence only, not paper baselines.

## Pilot blockers

1. Freeze a 5–10-sample deterministic manifest and a supported model/checkpoint revision.
2. Verify a separate upstream environment and cached model without editing the pinned checkout.
3. Capture actual ordered images, prompts, settings, every raw call, retries, errors, and method
   denominators externally.
4. Preserve official parsing/metrics as observed outputs while retaining raw text for trusted
   offline re-evaluation.
5. Predeclare partial-output and failure policy.

## Runtime unknowns

- GPT payload compatibility and actual backend availability.
- Qwen2.5 branch selection when imported.
- Dependency compatibility, GPU memory, latency, and deterministic repeatability.
- PyPI package parity with the pinned GitHub tree.

## Next gate

Prepare the bounded Phase 2 pilot contract and stop before the first GPU model inference. Explicit
authorization is required before model loading or inference.
