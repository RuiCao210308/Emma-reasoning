# Experiment Rules

Read this file only for data experiments, baselines, metrics, or ablations.

## Pre-registration

Before changing code or launching a run, write down:

- the research question and falsifiable hypothesis;
- the primary metric and any diagnostic metrics;
- the strongest reasonable baseline and what it controls;
- the frozen dataset split and manifest identity;
- the bounded pilot size and runtime/compute budget;
- the acceptance criterion and failure/kill criterion;
- the planned action after PASSED and after NOT PASSED.

Do not redefine the primary outcome after seeing results. Diagnostics can motivate a later,
separately declared experiment, but cannot retroactively turn a failed gate into a pass.

## Existing implementation check

1. Search the current repository for datasets, loaders, parsers, metrics, and baselines.
2. For OpenEMMA-dependent work, search the pinned official upstream and read
   `.codex/rules/upstream-parity.md`.
3. Identify the source of truth and reuse, instrument, or thinly adapt it.
4. If a new implementation is required, state the necessity and parity test before coding.

Do not maintain parallel loaders, evaluators, or prompt paths without a documented boundary.

## Frozen comparison unit

- Materialize or identify one deterministic manifest before comparing methods.
- Record manifest path, hash or immutable identifier, ordering, split, and sample count.
- Compare every method on the same samples and with the same evaluator.
- Keep observation length, prediction horizon, timestamps, coordinate frame, and anchor fixed.
- Count one record per declared method/sample pair unless the protocol explicitly says otherwise.
- Treat missing, failed, and malformed records as outcomes; never silently shrink a denominator.
- Report paired coverage and explain any unavoidable unpaired comparison.

## Future-leakage boundary

- Prediction inputs may contain only information available at the declared prediction time.
- Future target poses, headings, actions, labels, and derived statistics are evaluator-only.
- A future timestamp schedule may be used only when the protocol explicitly permits it and all
  methods receive the same schedule.
- Do not choose a parser, representation, threshold, policy, or candidate per sample using its
  future target or test error.
- Test the boundary by mutating future targets and confirming predictions do not change.
- Inspect preprocessing, caches, manifests, and fallback paths for indirect leakage.

## Reproducibility and failures

- Record all random seeds and the libraries or generators they control.
- Record deterministic settings and distinguish them from sampled inference.
- Record model/checkpoint identity, environment, command, hardware, wall time, and peak compute
  when these affect feasibility or reproducibility.
- Preserve raw outputs and structured errors for offline parsing and aggregation.
- Classify parse failures, runtime failures, retries, invalid values, and skipped samples.
- Keep failure counts in summaries and method denominators.
- Never replace failed predictions with ground truth or an undeclared oracle.

## Pilot before full run

- Run tests and a construction smoke before consuming experimental budget.
- Run the declared bounded pilot on representative samples.
- Check coverage, schema, finite values, leakage tests, runtime, and offline re-summary.
- Continue to a full run only if the pilot gate passes exactly as written.
- If the pilot fails, report NOT PASSED and diagnose within the authorized scope.
- Do not scale a run merely because the pipeline executes.

## Raw records and offline aggregation

- Store detailed local records as JSONL under ignored `outputs/`.
- Include stable sample and method identifiers in every record.
- Include enough raw prediction and error information to re-parse and re-score offline.
- Generate summaries and report numbers programmatically from raw records.
- Verify offline re-summary without rerunning model inference.
- Keep raw records immutable for a run; write corrected derivations to a new run directory.
- Avoid NaN and Infinity in JSON; represent invalid values explicitly with status metadata.

## Completion

- Run `pytest`, `ruff check .`, and `git diff --check` for code changes.
- Confirm the manifest and evaluator are identical across methods.
- Confirm coverage and denominators match the declared protocol.
- Update a compact committed report and machine-readable summary when results are stable.
- Update `docs/context/PROJECT_STATE.md` in the same commit if active status changed.
- Do not paste large result tables, JSONL, or logs into chat; provide report paths and a compact
  decision summary.
