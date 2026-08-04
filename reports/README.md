# Experiment reports

This directory stores compact, version-controlled experiment summaries that can be reviewed without copying terminal output from the server.

## Layout

Each stage uses its own directory:

```text
reports/
  stage1/
    report.md
    summary.json
  stage2/
    report.md
    summary.json
```

## What to commit

Commit:

- `report.md`: concise human-readable setup, metrics, diagnostics, decision, and next step;
- `summary.json`: machine-readable metrics, status, dataset scope, branch, and commit SHA;
- small tables or figures only when they are directly needed for review.

Do not commit:

- large per-sample JSONL files;
- model weights or caches;
- raw datasets;
- duplicated logs;
- absolute secrets, tokens, or credentials.

Large records remain under `outputs/` on the experiment machine. Every report must state which local output directory generated it.

## Required final status

Every stage report must end with exactly one status:

- `PASSED`
- `NOT PASSED`

A stage is not accepted from a chat summary alone. The committed report and summary are the source of truth.
