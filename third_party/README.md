# Local external checkouts

This directory contains local clones managed by `scripts/manage_upstreams.py`.

Expected paths:

```text
third_party/OpenEMMA/
third_party/CoT-legacy/
```

The source trees are intentionally ignored by Git. Their repository URLs and exact commits are tracked under `upstreams/*.lock.json`.

Do not place datasets, model weights, or manually copied source files here.
