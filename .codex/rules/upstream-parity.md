# Upstream and Parity Rules

Read this file only for OpenEMMA, upstream, adapter, or provenance work.

## Locked sources

- Treat `upstreams/openemma.lock.json` as the declared official source and commit.
- Treat `upstreams/legacy_cot.lock.json` as historical code archaeology only.
- Use `scripts/manage_upstreams.py` to list, sync, and verify checkouts.
- Never run from a floating branch, tag, or unrecorded commit.
- Before a paper run, record the exact commit and require an empty upstream `git status --short`.
- A lock file is not proof that a local checkout exists or is clean; verify both.
- Keep local checkouts under the lock-declared `third_party/` paths.
- Never add a third-party source tree to the parent repository.

## Official source reuse boundary

Reuse or instrument official OpenEMMA for:

- model classes and checkpoint loading;
- tokenizer and processor construction;
- image loading and visual preprocessing;
- frame selection and ordering;
- prompt text and sequencing;
- generation settings, retries, and sampling behavior;
- original inference methods and raw output text.

Emma-reasoning may independently own:

- provenance and raw-output capture;
- explicit intervention definitions;
- parsing audits and failure accounting;
- timestamp-aware trajectory reconstruction;
- coordinate transforms and metrics;
- non-VLM controls and causal comparisons.

Prefer a thin adapter at the boundary. Do not copy upstream functions for convenience. If the
official interface is difficult to call, instrument it or wrap it before considering a rewrite.

## Required order

Perform OpenEMMA work in this order:

1. **Static audit:** locate the actual entry point and document frames, prompts, processor,
   generation settings, retries, parsing, evaluator, and backend differences.
2. **Untouched pilot:** execute the clean pinned upstream path on a small deterministic manifest.
3. **Trusted re-evaluation:** evaluate the same raw text and sample set with the independent
   evaluator; account for every discrepancy and denominator change.
4. **Adapter parity:** show that the thin adapter supplies identical inputs and preserves raw
   outputs under deterministic settings.

Do not implement or compare CoT, SC, ToT, or GRTC before all four steps are complete.

## Required records

For every pilot or parity sample, record at least:

- sample identifier and ordered image paths actually consumed;
- upstream repository URL, commit, and clean/dirty status;
- exact command, model identifier, checkpoint identifier, and environment;
- every prompt string and relevant processor input;
- generation configuration, seed when applicable, retry count, and stopping behavior;
- complete raw model text before parsing;
- parsed result, parse status, and structured failure reason;
- upstream metric record and trusted evaluator record when available;
- runtime errors, skipped samples, and their effect on the denominator.

Use referenced paths rather than embedding images in JSONL. Preserve enough information to
re-run parsing and evaluation offline without another model call.

## Environment separation

- The upstream runtime and Emma-reasoning audit environment may remain separate.
- The upstream environment emits versioned JSON/JSONL plus referenced image paths.
- The audit environment consumes those records using project-owned parsing and evaluation.
- Do not pass opaque Python objects across environments.
- Record dependency or hardware differences that can affect output.

## Clean-run policy

- Never use a dirty upstream checkout for a paper run.
- If a dirty checkout is discovered, stop before execution and report the exact status.
- Do not edit pinned checkouts in place for a convenient experiment.
- Do not describe an adapter as parity-complete without sample-level evidence.
- Do not describe trusted-evaluator output as the official OpenEMMA metric.

## Unavoidable patches

If an upstream patch is truly unavoidable:

1. Explain why wrapping or instrumentation is insufficient.
2. Put the patch under `patches/openemma/`.
3. Record the base upstream commit, patch hash, purpose, and changed behavior.
4. Keep an untouched control run from the clean pinned checkout.
5. Define and execute a parity or impact test for the patch.
6. Report patched results as patched, never as untouched upstream results.

No patch may silently alter prompts, image preprocessing, parsing, or the evaluation denominator.
