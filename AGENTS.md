# Codex Working Guide

## Mission

Emma-reasoning tests whether inference-time reasoning genuinely improves visual grounding in motion planning. In particular, it asks whether Chain-of-Thought (CoT), Self-Consistency (SC), and candidate search add scene-grounded information or mainly strengthen historical-motion persistence and trajectory smoothness.

Scientific validity, reproducibility, and auditability come first. Scores, code volume, and apparent novelty are not primary objectives. A well-supported negative result is useful.

## Sources of truth

Use this precedence order:

1. The current Git worktree and commit history.
2. `docs/context/PROJECT_STATE.md` for current verified facts.
3. `GOAL.md` for the ordered research roadmap and active gate.
4. Upstream lock files under `upstreams/`.
5. Committed reports under `reports/`.
6. The task-specific rules routed below.
7. The user's current task.

Chat history and old Codex sessions are not sources of fact. If sources conflict, prefer the newer, verifiable repository state. Do not silently combine conflicting claims into a new conclusion; record the conflict in the report or handoff.

## Minimal session startup

At the start of a new task, run only:

```bash
git status --short
git branch --show-current
git log --oneline -5
```

Then read, in order:

1. `AGENTS.md`.
2. `docs/context/PROJECT_STATE.md`.
3. `GOAL.md` when the user asks to continue the project, continue the active goal, or advance a research milestone.
4. At most one or two task-specific rules selected from the routing table.
5. Files directly involved in the user's task.

For a narrow one-off maintenance request, read only the relevant section of `GOAL.md` or skip it when the task is clearly outside the research roadmap.

Do not make any of these the default context-recovery procedure:

- scan the whole repository with `find .`;
- read all documentation or all reports;
- print the complete Git history;
- read complete JSONL files or logs;
- recursively inspect third-party repositories;
- load all source code merely to understand the project.

Expand context only when the task requires it.

## Context discipline

- Search before reading whole files. Use `rg` to locate symbols, fields, headings, and known error text.
- Check size, summaries, and relevant ranges before opening a large file.
- For JSONL, inspect line count, schema/field frequencies, and a small deterministic sample first.
- Read logs only around the failure and its immediate setup.
- Prefer a committed report over raw output when answering an already-settled question.
- Do not reinvestigate facts already captured in `PROJECT_STATE.md` unless they may have changed or the task challenges them.
- Follow the first incomplete phase and gate in `GOAL.md`; do not start a later parallel phase.
- Do not repeat long logs, reports, or diffs in the final reply.
- By default, the final reply contains only status, key conclusions, commit, and blockers.

When scope expands, a second implementation appears, or work crosses multiple subsystems, perform a complexity reset:

1. Reread the user's original objective.
2. Check whether an official or existing implementation already exists.
3. Confirm the smallest necessary change.
4. Avoid extending a parallel implementation.

## Existing implementation first

Before implementing model loading, data loading, inference, prompts, processors, parsers, or evaluators:

1. Search this repository.
2. Search the pinned upstream relevant to the task without recursively loading unrelated code.
3. Identify and record the source of truth.
4. Prefer reuse, instrumentation, or a thin adapter.
5. Before an independent rewrite, state why it is necessary and define the parity plan in the task report or PR.

The following are prohibited:

- rewriting official OpenEMMA model loading;
- rewriting official image preprocessing;
- copying an official prompt and silently changing it;
- calling a self-built path an OpenEMMA reproduction;
- comparing reasoning methods before parity is established.

## Task routing

| Task type | Required rule |
|---|---|
| OpenEMMA, upstream, adapter, provenance | `.codex/rules/upstream-parity.md` |
| Data experiment, baseline, metric, ablation | `.codex/rules/experiments.md` |
| Report, summary, paper table | `.codex/rules/reporting.md` |
| Branch, commit, PR, merge | `.codex/rules/git-workflow.md` |

For work spanning categories, read only the rules actually needed, normally no more than two. Do not load all rules by default.

## Scientific validity

- Define the question and a falsifiable hypothesis before implementation.
- Use reasonable, fair baselines and state what each baseline controls.
- Keep future targets separate from prediction inputs, including representation and policy selection.
- Never silently discard parse failures, invalid outputs, or failed samples; count and classify them.
- Compare methods on the same frozen manifest and evaluator.
- Record seeds for stochastic experiments and distinguish deterministic from sampled runs.
- Run a bounded pilot before a full experiment.
- Write acceptance and failure criteria before inspecting the result.
- Do not select a representation, parser, or policy per sample using test results.
- Preserve and report negative results.
- Do not present a diagnostic result as a method-performance improvement.

## Validation and completion

For code changes, run from the declared project environment:

```bash
python scripts/check_agent_context.py
pytest
ruff check .
git diff --check
```

Before completion, check:

- Was an existing or official implementation reused where required?
- Was any future information introduced?
- Did any failure handling change the denominator?
- Is every hard-coded path declared and justified?
- Are outputs, data, checkpoints, or weights staged for commit?
- Does `docs/context/PROJECT_STATE.md` need an update in the same commit?
- Does the active phase or gate in `GOAL.md` need an update?

Report any check that cannot run and why. A task is not complete merely because code was written.

## Git safety

- Stay on the user-specified branch by default.
- Never reset, overwrite, or delete user modifications.
- Never force-push.
- Do not commit directly to `main`.
- Do not merge a PR unless the user explicitly requests it.
- Keep commits focused on one coherent task.
- Keep large outputs, datasets, caches, checkpoints, and weights out of Git.
- Keep `third_party/` checkouts out of the parent repository.
- Inspect status and the staged diff before committing.

## Compact handoff

The default final handoff contains only the applicable fields:

- status;
- tests;
- changed files;
- commit SHA;
- report path;
- blockers;
- next step.

Do not paste a complete report, diff, or log into chat. Link the committed artifact instead.
