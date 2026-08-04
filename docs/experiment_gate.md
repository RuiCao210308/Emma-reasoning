# Experiment feasibility gate

This checklist must be completed before implementation or a long-running experiment begins.

## 1. Research purpose

- What exact claim would the experiment support or falsify?
- Is the experiment diagnostic, baseline, ablation, or proposed method evaluation?
- Does a simpler existing baseline already answer the question?

## 2. Existing implementation reuse

- Is there an official or established repository for the target method?
- Which components can be reused unchanged?
- Which components must remain project-owned for auditability?
- Why is any new implementation necessary rather than an adapter or instrumentation patch?

A new model/inference implementation requires a written justification and parity plan.

## 3. Provenance and parity

- External repository and full commit SHA are pinned.
- Model checkpoint/revision is pinned.
- Dataset version and deterministic sample manifest are defined.
- Original command and environment are recorded.
- A small untouched upstream run is reproducible.
- Trusted re-evaluation discrepancies are explained.

## 4. Leakage and comparability

- Prediction inputs are separated from future targets.
- Interventions change one factor at a time.
- Compute budgets are defined and comparable.
- Parse failures and invalid samples remain in denominators.
- Baseline and intervention use the same evaluator and sample manifest.

## 5. Feasibility

- Estimated GPU memory, runtime, storage, and model calls are recorded.
- A small pilot can finish before the full run.
- Pilot acceptance and failure criteria are written before execution.
- Checkpoint/cache/network availability is verified.
- A recovery plan exists for interrupted runs.

## 6. Outputs

- Raw records are sufficient for offline re-evaluation.
- Compact committed report format is defined.
- Large outputs, weights, and datasets remain outside Git.
- Each reported number is generated from raw records rather than manually copied.

## Decision

An experiment may start only when the result is one of:

- `APPROVED`: purpose, reuse, provenance, parity, feasibility, and outputs are clear.
- `PILOT ONLY`: uncertainties remain but a bounded pilot can resolve them.
- `BLOCKED`: implementation or full execution would be premature.
