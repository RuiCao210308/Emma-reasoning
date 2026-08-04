# Emma-reasoning Active Goal

Status: ACTIVE  
Owner: project repository  
Last updated: 2026-08-04  
Active branch: `architecture/openemma-upstream`  
Active phase: Phase 0 — stabilize the upstream-first foundation  
Current stop point: do not run model inference until Phase 1 passes

## 1. Project goal

Build a paper-grade causal audit of inference-time reasoning in vision-language motion planning.

The central question is:

> Does additional inference-time reasoning improve visually grounded driving decisions, or does it mainly reinforce ego-motion persistence, text-action shortcuts, and trajectory smoothness?

The project studies frozen vision-language models and compares Direct prediction, Chain-of-Thought (CoT), Self-Consistency (SC), candidate search / tree-style selection, and a later training-free grounded consensus method.

The main contribution is the diagnostic protocol and causal evidence. A new reasoning or selection method is secondary and must not replace the audit.

A successful project must produce evidence for four questions:

1. Do CoT, SC, and search use visual scene information beyond motion history?
2. Is the generated reasoning consistent with the final continuous action trajectory?
3. Does SC improve through genuine agreement, or by averaging incompatible actions into a smooth but ungrounded trajectory?
4. Is candidate selection driven by scene risk and visual evidence, or by history-action smoothness?

Negative results are acceptable. The project fails scientifically if it reports attractive metrics without proving what information the methods use.

## 2. Final deliverable

The intended paper working title is:

> Does More Thinking Improve Driving? A Causal Audit of Inference-Time Reasoning in Vision-Language Motion Planning

The final repository should support:

- exact upstream provenance;
- reproducible frozen-model inference;
- a trusted, timestamp-aware trajectory evaluator;
- strong non-visual motion-history controls;
- compute-matched Direct / CoT / SC / search comparisons;
- visual, history, and reasoning interventions;
- rationale-action consistency analysis;
- candidate-distribution and selector-shortcut analysis;
- a training-free grounded consensus method only after the audit is established;
- compact committed reports backed by immutable raw records;
- paper tables and figures generated from records rather than manually copied values.

## 3. Non-negotiable architecture

### 3.1 Official implementation first

Official OpenEMMA is the source of truth for:

- model classes and checkpoint loading;
- tokenizer and processor construction;
- image loading and preprocessing;
- frame ordering and visual input construction;
- official prompts and prompt sequence;
- original generation configuration;
- original Direct / OpenEMMA inference behavior;
- raw output text.

Emma-reasoning owns:

- upstream provenance and exact invocation records;
- explicit interventions;
- parser auditing and failure accounting;
- timestamp-aware trajectory reconstruction;
- trusted coordinate transforms and metrics;
- non-VLM controls;
- causal and faithfulness analyses;
- candidate consensus and selection diagnostics;
- report generation.

Do not independently rewrite an official model or inference path for convenience.

### 3.2 Separate execution and evaluation

OpenEMMA execution and trusted evaluation may use separate environments.

The exchange boundary is versioned JSON / JSONL plus referenced image paths. Do not pass opaque Python objects across environments.

The upstream environment emits:

- provenance;
- actual ordered image inputs;
- historical motion inputs;
- all prompt strings;
- generation settings;
- complete raw model text;
- retries and structured errors;
- original parser/evaluator outputs when available.

The audit environment performs:

- independent parsing;
- failure classification;
- trajectory reconstruction;
- metrics;
- paired comparisons;
- intervention analysis;
- report generation.

### 3.3 One source of truth per concern

Do not create parallel implementations of:

- nuScenes window extraction;
- official visual preprocessing;
- official prompt construction;
- action parsing;
- trajectory integration;
- metric aggregation;
- experiment manifests.

When a second implementation appears, stop and decide which implementation is authoritative, which is an audit/control, and how parity is measured.

### 3.4 No future leakage

Prediction code must not receive future pose, future heading, future action, or target-derived statistics.

A future timestamp schedule is allowed only when declared by the protocol and supplied identically to all methods.

Changing future targets while holding historical inputs and the schedule fixed must not change a prediction.

### 3.5 Failure accounting

Never silently remove:

- parse failures;
- empty generations;
- runtime errors;
- invalid numerical predictions;
- missing images;
- retry exhaustion;
- samples rejected by one method but accepted by another.

Every method must report expected records, produced records, valid records, failure classes, and the denominator used by each metric.

## 4. Operating model for Codex

`AGENTS.md` defines global behavior. `docs/context/PROJECT_STATE.md` records current facts. This file defines the ordered research roadmap.

When the user says:

> Continue the active goal.

Codex should:

1. read `AGENTS.md`;
2. read `docs/context/PROJECT_STATE.md`;
3. read this file;
4. identify the first incomplete phase and its gate;
5. read only the one or two relevant `.codex/rules/` files;
6. complete the smallest coherent unit toward that gate;
7. update reports and project state;
8. commit and push to the active feature branch;
9. stop at the next explicit gate.

Do not ask the user to paste project history already present in the repository.

### 4.1 Autonomy boundary

Codex may proceed autonomously with:

- source inspection;
- tests and lint fixes;
- architecture and adapter code;
- static audits;
- CPU-only dataset checks;
- report generation;
- bounded smoke tests that do not download large weights;
- offline re-evaluation of existing records.

Codex must stop and report before:

- downloading model weights larger than 5 GB;
- installing a substantially conflicting model environment;
- the first GPU model inference in a new pipeline;
- a run estimated above 2 GPU-hours;
- a full dataset run;
- changing the official prompt or visual preprocessing;
- merging a PR;
- changing the paper's central research question.

A later user instruction may explicitly authorize one of these gated actions.

## 5. Global scientific protocol

Every experiment must declare before execution:

- research question;
- falsifiable hypothesis;
- competing explanation;
- primary metric;
- diagnostic metrics;
- strongest reasonable baseline;
- exact frozen manifest;
- compute budget;
- deterministic or sampled status;
- random seeds;
- acceptance gate;
- failure / kill criterion;
- next action for PASSED and NOT PASSED.

Every comparison must use:

- the same sample manifest;
- the same observation history;
- the same target horizon;
- the same evaluator;
- the same failure-accounting policy;
- a declared compute-matching rule.

Do not redefine the primary outcome after seeing results.

## 6. Current accepted foundation

### Stage 1 — trusted trajectory evaluation

Scientific status: PASSED.  
Repository status: merged to `main`.

Established:

- ego-local `+x` forward, `+y` left;
- final observed pose as prediction anchor;
- recorded per-step timestamps;
- constant-curvature integration;
- aligned ADE/FDE and longitudinal/lateral metrics;
- deterministic nuScenes mini windows;
- pose-to-action reconstruction audit.

Key audit result on 214 mini windows:

- actual-timestamp mean ADE: 0.091741 m;
- actual-timestamp mean FDE: 0.165879 m;
- maximum interval arc-fit residual: 0.084266 m.

These utilities are an independent audit layer, not an OpenEMMA reproduction.

### Stage 2 — history-only frozen controls

Scientific status: PASSED.  
Repository status: Draft PR #2; compact-report cleanup still required before merge.

Established:

- global near-stop policy with `speed_epsilon_mps = 0.1`;
- raw curvature retained for audit;
- near-stop sanitized curvature set to zero;
- yaw-rate metrics on every interval;
- leakage-free prediction interface;
- stationary, last-speed-straight, constant-last, and median-3 controls.

Key result:

- best history-only baseline is `constant_last` with approximately 2.2080 m ADE and 5.3763 m FDE on mini;
- sanitized-minus-raw oracle mean ADE increase is 0.000167 m.

The Stage 2 control establishes the minimum bar for visual/reasoning methods.

## 7. Ordered roadmap

Each phase has an objective, required artifacts, and a gate. Do not skip phases.
## Phase 0 — stabilize the upstream-first foundation

Status: ACTIVE.
### Objective

Make PR #3 internally correct, context-efficient, and ready for static provenance work.
### Required work

1. Fix the current CI failure in adjacent timestamp validation.
2. Preserve strict validation for finite, aligned, strictly increasing observed histories.
3. Add tests for one timestamp, increasing timestamps, duplicate timestamps, decreasing timestamps, NaN, and infinity.
4. Run:
   - `python scripts/check_agent_context.py`
   - `pytest`
   - `ruff check .`
   - `git diff --check`
5. Keep `AGENTS.md`, `GOAL.md`, `PROJECT_STATE.md`, and task rules compact and mutually consistent.
6. Update PR #3 without merging it.

### Gate
Phase 0 passes only when:

- local tests pass;
- GitHub Actions passes on the latest PR #3 head;
- no upstream source is vendored into the parent repository;
- `third_party/` remains ignored;
- current state and active goal are accurate.

### Stop condition

Do not run OpenEMMA model inference in this phase.
## Phase 1 — pinned upstream synchronization and static audit

Status: PENDING.
### Objective

Determine what the official OpenEMMA and legacy CoT code actually do before writing or running an adapter.
### Required work

1. Synchronize and verify the pinned official OpenEMMA checkout.
2. Synchronize and verify the pinned legacy CoT checkout for code archaeology.
3. Require exact commit identity and clean worktrees.
4. Audit the actual execution path, not only README claims.
5. Record immutable source references using repository, full commit, file, and line range.
6. Distinguish confirmed facts, evidence-backed inferences, runtime unknowns, and blockers.

### Questions to resolve

- entry point and CLI;
- observation and prediction windows;
- actual camera frames gathered and actually consumed;
- backend-specific image handling for Qwen, Llama, LLaVA, and GPT;
- prompt frame-count claims versus processor inputs;
- scene/object/intent/motion call order;
- baseline versus OpenEMMA behavior;
- generation parameters, retries, and sampling;
- hard-coded model and local paths;
- historical speed/curvature calculation and units;
- curvature ×100 formatting and inverse conversion;
- raw-text parsing and malformed-output handling;
- skipped samples and denominators;
- trajectory anchor, time step, and integration;
- ADE/FDE indexing and aggregation;
- duplicate function definitions and backend divergence;
- exact legacy CoT Config changes.

### Required artifacts

- `docs/provenance/openemma_static_audit.md`
- `reports/openemma_static_audit/report.md`
- `reports/openemma_static_audit/summary.json`

### Gate
Phase 1 passes when:

- both checkouts match lock files and are clean;
- all static questions are answered or explicitly marked runtime unknown;
- blockers to an untouched pilot are identified;
- the report states whether a pilot is ready;
- no runtime claim is presented as source-confirmed evidence.

### Stop condition

Static-audit PASSED does not mean parity PASSED. Stop before model inference unless the user authorizes the bounded pilot.
## Phase 2 — untouched official parity pilot

Status: PENDING.
### Objective

Run the clean pinned official path without modifying prompts, preprocessing, parsing, or evaluator behavior.
### Pilot scope

Default bounded scope:

- one supported frozen VLM backend;
- one deterministic model/checkpoint revision;
- 5 to 10 manifest samples chosen before inference;
- at least one straight-motion sample, one turning sample, one near-stop sample, and one visually nontrivial sample where available;
- one official method at a time;
- no more than 2 GPU-hours without renewed approval.

### Required preparation

1. Create a dedicated upstream runtime environment rather than forcing dependency compatibility with the audit environment.
2. Pin environment and model revision.
3. Create an immutable pilot manifest.
4. Verify image availability and model cache before launching.
5. Estimate storage, memory, and runtime.
6. Define resume behavior and output schema.

### Required records per sample

- manifest/sample ID;
- official commit and clean status;
- exact command;
- environment identity;
- model and checkpoint revision;
- ordered images actually consumed;
- historical speed/curvature input;
- all prompt strings;
- generation settings and seed where supported;
- raw scene/object/intent/motion text;
- retries and structured errors;
- official parser result;
- official metric record;
- wall time and peak GPU memory when practical.

### Gate
Phase 2 passes when:

- every expected sample has a record, including failures;
- raw text can be re-parsed offline;
- the official run is reproducible from command and manifest;
- no official source file was modified;
- the output schema is sufficient for trusted re-evaluation;
- runtime and memory make the next phase feasible.

### Kill criteria

Stop and mark NOT PASSED if:

- the official path cannot run from its pinned state without undocumented source edits;
- actual inputs cannot be recorded;
- sample failures disappear from the denominator;
- model output cannot be associated unambiguously with a manifest item;
- the projected full protocol is infeasible on available hardware.
## Phase 3 — trusted re-evaluation of identical raw outputs

Status: PENDING.
### Objective

Evaluate the untouched pilot outputs with Emma-reasoning without another model call.
### Required work

1. Build a parser-audit boundary that preserves raw text and structured parse status.
2. Run both official parsing and trusted parsing on the same text.
3. Reconstruct trajectories from the same anchor and recorded future schedule.
4. Compare official and trusted metrics sample by sample.
5. Explain every discrepancy by category:
   - parser;
   - scaling/units;
   - coordinate frame;
   - anchor;
   - time step;
   - horizon indexing;
   - skipped sample;
   - aggregation.

### Required artifacts

- per-sample parity records under ignored `outputs/`;
- compact report under `reports/openemma_parity/`;
- discrepancy table and failure taxonomy;
- tests for every confirmed evaluator discrepancy.

### Gate
Phase 3 passes when:

- the same raw outputs can be re-evaluated offline;
- denominators are explicit;
- metric discrepancies are explained rather than hidden;
- the trusted evaluator is stable enough to compare reasoning methods;
- no future-ground-truth anchor enters prediction.
## Phase 4 — thin adapter parity

Status: PENDING.
### Objective

Create the minimum adapter needed to invoke and instrument official OpenEMMA while preserving official behavior.
### Adapter responsibilities

The adapter may:

- verify the upstream lock and clean checkout;
- invoke official entry points/functions;
- record actual inputs and prompts;
- capture raw text and errors;
- attach provenance;
- expose explicit intervention hooks that are inactive by default.

The adapter must not:

- independently load the model through a parallel implementation;
- reimplement the processor;
- rewrite official prompts;
- silently normalize outputs;
- replace official retry behavior;
- change sample inclusion.

### Parity test

Under deterministic settings, adapter-off and untouched-upstream runs must match on:

- ordered image inputs;
- historical motion inputs;
- prompt strings;
- generation configuration;
- raw output, when provider determinism permits;
- otherwise tokenized input and declared stochastic distributional checks;
- parser/failure records.

### Gate
Phase 4 passes only with sample-level parity evidence. Architecture similarity is insufficient.
## Phase 5 — freeze the main experiment protocol

Status: PENDING.
### Objective

Pre-register the benchmark, methods, compute budgets, and interventions before large reasoning comparisons.
### Frozen comparison methods

At minimum:

1. motion-history controls from Stage 2;
2. Direct frozen-VLM prediction;
3. CoT frozen-VLM prediction;
4. SC with a declared sample count;
5. candidate search / legacy ToT-style method after exact definition;
6. later GRTC, evaluated separately as a proposed method.

### Compute matching

Record for every method:

- number of visual encodes;
- number of model generations;
- total generated tokens;
- candidate count;
- selector calls;
- wall time;
- peak memory;
- retry budget.

Primary comparisons must include a compute-matched view. A method cannot claim reasoning gain solely because it makes more model calls.

### Manifest

Freeze:

- dataset version;
- scene/sample IDs;
- image channels;
- observation and future horizons;
- ordering;
- target/evaluator version;
- sample exclusions decided before model output;
- manifest hash.

### Gate
Phase 5 passes when the full protocol is executable from one manifest and each claim maps to a planned table or figure.
## Phase 6 — Direct frozen-VLM baseline

Status: PENDING.
### Objective

Establish the visual model's parser-aware continuous trajectory baseline before reasoning.
### Required analyses

- coverage and parse-failure rate;
- ADE/FDE and longitudinal/lateral error;
- speed, masked curvature, and yaw-rate error;
- comparison with `constant_last` and other motion controls;
- performance by scene and motion regime;
- near-stop behavior;
- image ablation pilot;
- history ablation pilot.

### Gate
Direct is accepted as a research baseline only if:

- it is evaluated on the frozen manifest;
- failures remain in accounting;
- it meaningfully uses vision under at least one planned grounding check, or its lack of visual use is explicitly documented;
- official and trusted metrics are both reported when relevant.
## Phase 7 — CoT baseline and reasoning-action consistency

Status: PENDING.
### Objective

Test whether explicit reasoning improves trajectory prediction and whether the rationale is consistent with the final action.
### Required records

- rationale text;
- extracted scene facts;
- stated intent;
- final action chunk;
- parse/failure status;
- generation length and latency.

### Consistency diagnostics

Define before analysis:

- rationale mentions stop/slow/turn/change-lane versus predicted speed/curvature;
- object/risk references versus visual evidence;
- temporal consistency across the reasoning chain;
- sensitivity of action to rationale intervention;
- action change under rationale-preserving versus rationale-destroying edits.

### Gate
CoT is not considered an improvement merely because ADE decreases. It must be evaluated for grounding and rationale-action consistency.
## Phase 8 — Self-Consistency audit

Status: PENDING.
### Objective

Determine whether SC improves through genuine candidate agreement or through smoothing incompatible actions.
### Required candidate analysis

For every sample:

- all raw generations;
- parsed action chunks;
- parse failures;
- pairwise trajectory distances;
- action-space modes/clusters;
- cluster sizes;
- medoid and arithmetic mean;
- selector/aggregation result;
- distance from the selected result to every candidate;
- whether the result lies between incompatible modes.

### Required comparisons

- text majority voting when applicable;
- action mean;
- trajectory mean;
- largest-cluster medoid;
- all-candidate medoid;
- random valid candidate;
- best candidate oracle for diagnosis only, never as a deployable method.

### Key question

Does SC gain disappear when incompatible candidates are not averaged across modes?

### Gate
SC conclusions require mode-aware candidate diagnostics, not only final ADE/FDE.
## Phase 9 — candidate search and selector-shortcut audit

Status: PENDING.
### Objective

Determine whether search/selection rewards visual risk grounding or merely history-action smoothness.
### Required candidate logging

- candidate generation prompts and outputs;
- candidate trajectories;
- scene facts available to the selector;
- history-motion features available to the selector;
- every score component;
- selected candidate;
- rank ordering;
- selector failures.

### Selector interventions

At minimum:

- remove visual facts while preserving history;
- remove history smoothness terms while preserving visual facts;
- shuffle candidate rationales;
- swap scene-risk descriptions between samples;
- preserve action while changing rationale;
- preserve rationale while perturbing action;
- compare selector choice under each intervention.

### Gate
Search can claim grounded selection only if selector decisions respond to scene-risk evidence more than to irrelevant or shortcut-preserving changes.
## Phase 10 — causal grounding interventions

Status: PENDING.
### Objective

Separate visual grounding, history persistence, reasoning faithfulness, and output smoothness.
### Intervention families

#### Visual interventions

- blank or neutral image;
- temporal frame shuffle;
- last-frame-only versus multi-frame input;
- targeted crop/mask of relevant actors or lane evidence;
- scene swap with history preserved;
- image-history mismatch.

#### History interventions

- zero history;
- constant history;
- shuffled history;
- history from another sample with image preserved;
- speed-only versus curvature-only history;
- last-state-only versus full history.

#### Reasoning interventions

- remove rationale before action generation when pipeline permits;
- rationale shuffle;
- fact-preserving paraphrase;
- fact-destroying counterfactual;
- action-preserving rationale swap;
- rationale-preserving action candidate perturbation.

### Required outcomes

Measure changes in:

- raw text;
- parsed action;
- trajectory;
- confidence/consensus;
- selector score;
- rationale-action consistency;
- failure rate.

### Causal claim discipline

Use paired sample-level effects and explicitly define the intervention target. Do not infer causal grounding from aggregate correlation alone.
## Phase 11 — Grounded Risk-Conditioned Trajectory Consensus (GRTC)

Status: PENDING.
### Objective

Evaluate a training-free method only after the audit identifies concrete failure modes.
### Intended pipeline

1. extract structured visual facts once;
2. form risk-conditioned reasoning branches from those facts;
3. generate continuous speed-curvature candidates;
4. cluster candidates in trajectory/action space;
5. choose a mode-aware medoid rather than averaging incompatible modes;
6. score grounding, rationale-action consistency, dynamics, and within-mode consensus.

### Required ablations

- no visual-fact grounding;
- no risk branching;
- arithmetic mean instead of medoid;
- no clustering;
- no rationale-action consistency term;
- no dynamics term;
- no consensus term;
- history-smoothness-only selector;
- equal compute Direct/CoT/SC comparison.

### Positioning rule

GRTC is a secondary contribution. Do not allow method tuning to erase or obscure negative audit findings.

### Gate
GRTC must improve the predefined primary metric or grounding diagnostics without relying on oracle target information, unequal hidden compute, or post-hoc sample selection.
## Phase 12 — robustness and scale

Status: PENDING.
### Objective

Test whether findings generalize beyond one model, one small split, or one prompt configuration.
### Preferred expansion order

1. full nuScenes trainval manifest or a larger deterministic subset;
2. at least two frozen VLM backends or model sizes;
3. multiple seeds for sampled methods;
4. prompt wording robustness;
5. scene-risk and motion-regime slices;
6. optional closed-loop or simulator validation if feasible and scientifically aligned.

### Required reporting

- mean and uncertainty across seeds;
- paired bootstrap confidence intervals across samples;
- effect size of interventions;
- compute and latency;
- model-specific versus shared conclusions;
- failures and unavailable comparisons.

### Gate
The paper must distinguish mini/pilot evidence from general conclusions. A result from nuScenes mini alone cannot be presented as universal.
## Phase 13 — paper artifacts

Status: PENDING.
### Objective

Generate the paper from immutable reports and records.
### Planned paper structure

1. Introduction and central causal question.
2. Related work: VLM driving, CoT/SC/search, shortcut learning, reasoning faithfulness.
3. Trusted evaluation and compute-matched protocol.
4. Motion-history controls and official-parity analysis.
5. Direct/CoT/SC/search results.
6. Causal interventions and shortcut diagnosis.
7. GRTC method and ablations, if supported.
8. Limitations, negative findings, and broader implications.

### Planned core tables

- official versus trusted evaluation parity;
- motion controls versus Direct/CoT/SC/search;
- compute and failure accounting;
- visual/history intervention effects;
- rationale-action consistency;
- SC mode-aware aggregation;
- selector ablations;
- GRTC ablations if retained.

### Planned core figures

- pipeline and causal-audit overview;
- visual/history intervention design;
- candidate action/trajectory distributions;
- SC multimodality examples;
- selector shortcut sensitivity;
- trajectory error by step and regime;
- grounding versus smoothness trade-off.

### Artifact rule

Every paper number and figure must be generated from committed compact summaries or immutable raw records. Do not manually type experimental values into LaTeX or plotting scripts.

## 8. Branch and report plan

Use one focused branch/PR per phase or coherent milestone.

Suggested future branches:

- `audit/openemma-static`
- `audit/openemma-parity-pilot`
- `adapter/openemma-parity`
- `protocol/reasoning-benchmark`
- `experiment/direct-baseline`
- `experiment/cot-baseline`
- `experiment/self-consistency`
- `experiment/search-audit`
- `experiment/causal-interventions`
- `method/grtc`
- `paper/artifacts`

Do not create a new branch while an existing branch already owns the same work.

Suggested report directories:

- `reports/openemma_static_audit/`
- `reports/openemma_parity/`
- `reports/direct_baseline/`
- `reports/cot_baseline/`
- `reports/self_consistency/`
- `reports/search_audit/`
- `reports/causal_interventions/`
- `reports/grtc/`
- `reports/paper/`

Detailed records remain in ignored `outputs/<experiment_id>/`.

## 9. Immediate next actions

The first incomplete work is Phase 0.

Execute in this order:

1. repair adjacent timestamp validation in `OpenEmmaInvocation`;
2. add complete timestamp-validation tests;
3. run context check, pytest, Ruff, and diff check;
4. commit and push the focused fix to `architecture/openemma-upstream`;
5. wait for the latest PR #3 CI result;
6. after CI passes, synchronize pinned upstreams;
7. perform Phase 1 static audit;
8. update `PROJECT_STATE.md`, reports, and this file's active phase;
9. stop before model inference.

## 10. Updating this goal

This file is a living execution plan, not a historical log.

When a phase passes:

1. change its status to PASSED;
2. update `Active phase` at the top;
3. replace `Current stop point` with the next gate;
4. add only the final report path and essential decision;
5. move transient details into the phase report;
6. update `docs/context/PROJECT_STATE.md` in the same commit;
7. keep future phases unless the scientific design changes.

When a phase fails:

1. mark it NOT PASSED;
2. record the failed gate and report path;
3. do not silently weaken the gate;
4. choose whether to repair, redesign, or terminate the branch;
5. preserve negative evidence.

Do not expand this file with full logs, per-sample results, or long implementation notes.

## 11. Definition of project completion

The project is complete only when:

- official upstream provenance and parity are established;
- trusted evaluation discrepancies are explained;
- strong history-only controls are included;
- Direct, CoT, SC, and search are compared fairly;
- causal interventions isolate visual, history, and reasoning dependence;
- SC and selector mechanisms are audited at candidate level;
- proposed-method claims, if any, survive predefined ablations;
- failures and negative findings remain visible;
- robustness scope and limitations are explicit;
- all paper artifacts are reproducible from records and reports.

Until then, continue from the first incomplete phase rather than starting a parallel research direction.
