# Reporting Rules

Read this file only for reports, summaries, or paper tables.

## Artifact boundary

- `outputs/` holds detailed local run records, raw JSONL, logs, caches, and large diagnostics.
- `reports/` holds compact, reviewable, committed reports and machine-readable summaries.
- Never commit raw model dumps, datasets, weights, checkpoints, or oversized JSON.
- A report should point to the run identifier and local output path without embedding raw data.
- Keep enough provenance in the report to identify the manifest, evaluator, code commit, and
  experimental decision.

## Programmatic derivation

- Generate every reported numeric result from raw records with checked code.
- Do not hand-copy or manually average primary results.
- Support offline re-summary without model inference.
- Record total expected records, observed records, failures, and denominators.
- Verify that report tables and `summary.json` agree on every key number.
- Treat a disagreement as a failed validation, not a formatting issue.
- Preserve sufficient decimal precision to reproduce gates; round only for presentation.

## JSON requirements

- `summary.json` must be valid strict JSON.
- Do not emit NaN, Infinity, or negative Infinity.
- Represent missing or invalid values as `null` plus an explicit status/reason when needed.
- Use stable field names and include units in names or schema documentation.
- Keep the summary compact; detailed per-sample records belong in ignored JSONL.

## Decision language

- State the predefined gate as **PASSED** or **NOT PASSED**.
- Do not substitute ambiguous language such as promising, encouraging, or mostly passed.
- Separate confirmed facts, evidence-backed inference, and runtime unknowns.
- Mark values that have not been locally verified.
- Distinguish scientific acceptance from merge, cleanup, or infrastructure status.
- Keep negative results and failed samples visible.
- Do not convert a diagnostic observation into a method-performance claim.
- Do not claim causality, grounding, parity, or generalization beyond the tested evidence.

## Report contents

A compact report normally includes:

1. question and preregistered gate;
2. data, manifest, samples, and evaluator;
3. methods and fairness controls;
4. primary results and coverage;
5. failure accounting and essential diagnostics;
6. decision, limitations, and next action;
7. code, environment, raw-output, and summary provenance.

Avoid full logs, per-sample tables, repeated background, and exhaustive historical narrative.

## Completion and handoff

- Validate strict JSON and regenerate summaries from raw records.
- Check report/summary agreement and Git diff hygiene.
- Keep reports committed while local output remains ignored.
- Update `docs/context/PROJECT_STATE.md` when a reported result changes active project state.
- After committing the report, chat should contain only its path, the short decision, tests,
  commit, and blockers. Do not paste the full report or table.
