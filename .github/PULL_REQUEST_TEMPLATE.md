## Purpose

Describe the exact research or engineering question this change addresses.

## Existing implementation reuse

- [ ] I checked whether an official/existing implementation already provides this behavior.
- [ ] Upstream repository and full commit SHA are pinned when applicable.
- [ ] New implementation is limited to code that cannot reasonably be reused or instrumented.
- [ ] Any difference from upstream is explicit and tested.

## Validity

- [ ] Prediction inputs are separated from future targets.
- [ ] Sample inclusion and failure accounting are explicit.
- [ ] Baselines and interventions share the same manifest and evaluator.
- [ ] Original-upstream parity is established, or this PR is clearly marked architecture/pilot only.

## Feasibility

- [ ] Runtime, GPU memory, storage, and external model-call costs were considered.
- [ ] A bounded pilot and acceptance/failure criteria are defined before a full run.
- [ ] Interrupted runs can resume or be safely repeated.

## Reproducibility

- [ ] Tests and lint pass.
- [ ] Raw outputs support offline re-evaluation.
- [ ] Large outputs, model weights, datasets, and upstream checkouts are not committed.
- [ ] Compact reports are generated from raw records rather than manually copied.

## Validation

List the exact commands and results used to validate this change.
