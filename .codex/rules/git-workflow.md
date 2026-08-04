# Git Workflow Rules

Read this file only for branch, commit, PR, or merge work.

## Before changes

- Run `git status --short`, `git branch --show-current`, and a short `git log`.
- Fetch the relevant remote before relying on branch or PR status.
- Confirm the requested branch and its upstream tracking relationship.
- If tracked user changes exist, do not reset, overwrite, delete, or hide them.
- Stop and report a conflict when the requested work cannot preserve user changes.
- Treat untracked files as user-owned unless the task clearly created them.

## Branch safety

- Work on a feature branch, never directly on `main`.
- Stay on the user-specified branch unless explicitly authorized to change it.
- Do not create a duplicate branch or PR for an existing task.
- Do not force-push or rewrite shared history.
- Use fast-forward-only pulls when updating an existing feature branch.
- Do not merge a PR without explicit user approval.

## Commit preparation

- Keep one PR focused on one clear stage or coherent objective.
- Inspect `git status`, `git diff --stat`, and the relevant diff before staging.
- Stage only files in scope; do not use broad staging when unrelated changes exist.
- Check for unexpectedly large files and generated artifacts.
- Confirm ignored outputs, local datasets, caches, weights, and checkpoints are not staged.
- Confirm `third_party/` source checkouts are not staged in the parent repository.
- Use a concise commit message describing the repository outcome.

## Required validation

Before committing code changes, run:

```bash
pytest
ruff check .
git diff --check
```

If a check cannot run, record the exact blocker. Re-run relevant checks after any fix that can
affect them. Inspect the staged diff and status before committing.

## Pull requests

- Update the existing PR when one already covers the branch and objective.
- Keep the PR as Draft until its declared acceptance criteria and review checklist pass.
- Give each PR one explicit stage, scope, validation section, and non-goals.
- Update the PR body when the implementation or validation scope materially changes.
- Do not claim merge readiness while required evidence or parity remains incomplete.
- Do not merge, enable auto-merge, or change the base branch without explicit approval.

## Push and handoff

- Push only the requested feature branch.
- Verify the remote branch/PR status after pushing.
- Report branch, commit SHA, checks, changed files, PR state, and blockers compactly.
- Do not paste full diffs, logs, or PR bodies into chat.
