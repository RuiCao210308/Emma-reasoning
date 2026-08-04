# Upstream provenance

This directory contains machine-readable lock files for external repositories used by the project.

The lock files are the source of truth for repository URL, pinned commit, local checkout path, and reuse policy. External source trees are cloned into `third_party/` and are not committed into Emma-reasoning.

Rules:

1. Never run an experiment from a floating branch such as `main` or `Config`.
2. The checkout HEAD must exactly match the lock file commit.
3. Do not edit files inside an upstream checkout for a paper experiment.
4. Any unavoidable patch must be stored under `patches/<upstream>/`, reviewed, and identified in the experiment manifest.
5. Official OpenEMMA model loading, visual preprocessing, prompts, and inference behavior are reused through a thin adapter rather than independently reimplemented.
6. Emma-reasoning owns intervention design, provenance logging, parsing audits, and trusted trajectory evaluation.

Use `python scripts/manage_upstreams.py sync` to clone or update the pinned checkouts and `python scripts/manage_upstreams.py verify` before an experiment.
