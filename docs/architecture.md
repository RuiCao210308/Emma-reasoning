# Repository architecture

## Design objective

Emma-reasoning audits inference-time reasoning in vision-language motion planning. It is not a replacement implementation of OpenEMMA.

The architecture separates four responsibilities:

1. **Official upstream execution** — model loading, image preprocessing, prompts, and original inference behavior come from a pinned OpenEMMA checkout.
2. **Thin adapter and provenance capture** — project code records the exact upstream commit, model, command, prompts, images, raw text, errors, and interventions.
3. **Trusted evaluation** — project-owned trajectory geometry, time alignment, parser audits, metrics, and causal comparisons operate outside the upstream source tree.
4. **Research interventions** — image/history/reasoning perturbations are explicit experiment modules and must not silently change the baseline pipeline.

## Directory layout

```text
Emma-reasoning/
├── upstreams/                         # pinned external repository lock files
├── third_party/                       # local untracked checkouts
│   ├── OpenEMMA/
│   └── CoT-legacy/
├── patches/                           # reviewed patches only when unavoidable
│   └── openemma/
├── src/emma_reasoning/
│   ├── adapters/openemma/             # thin contracts and later instrumentation
│   ├── data/                          # trusted dataset/window definitions
│   ├── trajectory/                    # trusted action/trajectory representation
│   └── evaluation/                    # trusted metrics and audit logic
├── experiments/                       # one declarative experiment per directory
├── scripts/
│   ├── manage_upstreams.py            # clone and verify pinned checkouts
│   └── ...                            # audit and experiment entry points
├── docs/                              # architecture, protocols, provenance
├── reports/                           # compact committed experiment reports
├── outputs/                           # large local records, never committed
└── tests/
```

## Ownership boundary

### Reuse from official OpenEMMA

The following must be reused or instrumented in place before any independent implementation is considered:

- model class and checkpoint loading;
- processor/tokenizer construction;
- image loading and visual preprocessing;
- frame selection as performed by the official entry point;
- prompt text and prompt sequencing;
- generation settings and retry behavior;
- official CoT/openemma behavior;
- official output text.

### Owned by Emma-reasoning

The following remain independent and tested:

- provenance and raw-output recording;
- explicit intervention definitions;
- robust parsing with failure accounting;
- world/ego coordinate conversion;
- timestamp-aware action integration;
- ADE/FDE and action metrics;
- non-VLM controls;
- causal and faithfulness analysis.

### Not allowed

- copying an upstream function and changing it without recording the difference;
- running from a floating upstream branch;
- reporting official and trusted metrics as if they were identical;
- silently skipping parse failures or invalid samples;
- selecting an intervention or representation from future ground truth per sample;
- calling a rewritten pipeline an OpenEMMA reproduction before parity is established.

## Environment boundary

OpenEMMA and Emma-reasoning may require incompatible dependency versions. They should use separate environments until a compatibility audit proves otherwise.

- The **upstream environment** executes the pinned OpenEMMA checkout and emits raw, versioned records.
- The **audit environment** reads those records and performs parsing, trajectory reconstruction, interventions that do not require model execution, and evaluation.

Cross-environment exchange uses JSON/JSONL plus referenced image paths. Python objects are not passed between environments.

## Required experiment lifecycle

Every VLM experiment proceeds in this order:

1. **Provenance audit** — pin repository commit, model checkpoint, environment, command, and dataset split.
2. **Static pipeline audit** — document actual frame count, prompts, preprocessing, parser, retries, and evaluator behavior.
3. **Original parity run** — run the untouched upstream path on a small deterministic subset.
4. **Trusted re-evaluation** — evaluate the same raw outputs with project metrics and explain every discrepancy.
5. **Adapter parity** — prove the thin adapter produces identical upstream inputs and raw outputs under deterministic settings.
6. **Single intervention pilot** — change one factor only and define an acceptance/failure criterion before a full run.
7. **Full experiment** — execute only after the pilot passes.

No CoT, SC, ToT, or GRTC comparison starts before steps 1–5 are complete.

## Current component status

- Stage 1 trajectory evaluation: independent trusted evaluator, accepted.
- Stage 2 motion baselines: independent non-VLM controls, scientifically accepted pending repository cleanup.
- OpenEMMA integration: architecture only; no parity claim yet.
- Legacy `CoT` repository: historical prototype only; its outputs are not paper results until re-run through the pinned and audited pipeline.
