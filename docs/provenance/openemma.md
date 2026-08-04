# OpenEMMA provenance record

## Official upstream

- Repository: `https://github.com/taco-group/OpenEMMA`
- Pinned commit: `8403ea636696c5c10e8fdeca566410de0a07e449`
- Upstream commit message: `Merge pull request #38 from ChrisYang2017/main — add Qwen2.5-vl support`
- Local checkout: `third_party/OpenEMMA`
- Role: official reference implementation
- License recorded by upstream: Apache-2.0

The pinned commit is a provenance anchor, not an assumption that every implementation detail or metric is correct.

## Historical prototype

- Repository: `https://github.com/RuiCao210308/CoT`
- Branch at capture: `Config`
- Pinned commit: `a214a2ccc2581e4a59e59d392fb969c29519044e`
- Local checkout: `third_party/CoT-legacy`
- Role: historical prototype for comparison and code archaeology only

Results from this prototype are not promoted into paper tables. Useful ideas must be traced to a specific diff and reimplemented as an explicit adapter/intervention after OpenEMMA parity is established.

## Questions that must be answered by the static audit

1. How many camera frames are actually delivered to each model backend?
2. Does the prompt describe the same number and temporal span of frames that the processor receives?
3. Which image object or path is used for Qwen, Llama, LLaVA, and GPT paths?
4. What prompts and model calls are made by baseline versus `openemma` reasoning?
5. Which generation parameters, retries, and sampling settings are active?
6. How are historical positions, speed, and curvature computed and scaled?
7. How is raw text parsed, and what happens on partial, malformed, or failed output?
8. Which samples are skipped, retried, or excluded from aggregate metrics?
9. What pose anchors, time intervals, coordinate conventions, and horizon indices are used?
10. Does any part of trajectory reconstruction use a future ground-truth position as its initial state?
11. Are all model backends behaviorally comparable, or do they receive materially different inputs?
12. Does the checked-out commit contain local paths, duplicate definitions, or environment assumptions that change execution?

## Required parity artifacts

The first official parity run must save, for every sample:

- upstream repository commit and clean/dirty status;
- exact command and model identifier;
- ordered image paths actually passed to the upstream processor;
- historical speed/curvature values before and after any scaling;
- all prompt strings;
- generation parameters and retry count;
- raw scene/object/intent/motion text;
- parser result and parser failure reason;
- original upstream metric record;
- trusted evaluator metric record.

Until these artifacts exist, the project must not claim that its adapter reproduces OpenEMMA.
