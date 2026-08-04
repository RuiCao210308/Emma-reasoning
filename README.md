# Emma-reasoning

Research code for auditing inference-time reasoning in vision-language motion planning.

The project asks whether additional inference-time computation—Chain-of-Thought, Self-Consistency, and candidate search—actually increases visual grounding, or merely reinforces ego-motion persistence and trajectory smoothness.

## Current milestone

**Stage 1: trusted trajectory evaluation core**

Before running any VLM experiments, the repository will establish and test:

- explicit `dt = 0.5 s` trajectory integration;
- prediction from the final observed ego pose, without future-point leakage;
- world-to-ego coordinate conversion;
- consistent ADE/FDE horizon indexing;
- speed and curvature metrics with explicit units;
- unit tests for temporal alignment and geometry.

No quantitative result should be treated as a paper result until it is produced by the tested evaluation pipeline in this repository.
