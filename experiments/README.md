# Experiments

Each experiment lives in its own directory and must be reproducible from committed configuration plus pinned upstream locks.

Recommended layout:

```text
experiments/<experiment_id>/
├── README.md          # hypothesis, design, acceptance criteria
├── manifest.json      # dataset/model/upstream/intervention/seed/compute settings
└── run.sh             # small launcher; no hidden hard-coded paths
```

Rules:

- Do not place copied OpenEMMA source files here.
- Do not encode server-specific model or data paths in committed code; pass them through CLI arguments or environment variables.
- Every VLM experiment references `upstreams/openemma.lock.json` and records the verified checkout commit.
- Every intervention names the unchanged baseline and the single intended difference.
- Raw outputs go under `outputs/<experiment_id>/`; compact summaries go under `reports/<experiment_id>/`.
- Full runs require the approval state from `docs/experiment_gate.md`.
