# OpenEMMA static source audit

## Decision

**Phase 1: PASSED.** The pinned sources were synchronized, verified clean, and audited against
the Phase 1 questions in `GOAL.md`. Claims below are source-confirmed unless explicitly labeled
as an inference or runtime unknown.

**Untouched pilot readiness: NOT PASSED.** The official source exposes an auditable entry point,
but its current input, failure-accounting, backend, and evaluator behavior cannot yet satisfy the
Phase 2 record contract without an external capture harness and a frozen pilot specification.
No model was loaded or executed during this audit.

## Immutable provenance

| Role | Repository | Commit | Local checkout | Verification |
|---|---|---|---|---|
| Official reference | `https://github.com/taco-group/OpenEMMA` | `8403ea636696c5c10e8fdeca566410de0a07e449` | `third_party/OpenEMMA` | exact HEAD, clean |
| Historical prototype | `https://github.com/RuiCao210308/CoT` (`Config`) | `a214a2ccc2581e4a59e59d392fb969c29519044e` | `third_party/CoT-legacy` | exact HEAD, clean |

Source references use `repository@commit:path:Lx-Ly`. Local checkouts remain ignored and are not
vendored into Emma-reasoning.

## Official execution path

### Entrypoint and scope

- The GitHub README directs repository users to `python main.py --model-path ... --dataroot ...
  --version ... --method openemma` and claims GPT, LLaVA, Llama, and Qwen support
  (`OpenEMMA@8403ea6:README.md:L90-L112`).
- The CLI defaults are `model-path=gpt`, `plot=True`, `datasets/NuScenes`, `v1.0-mini`, and
  `method=openemma` (`OpenEMMA@8403ea6:main.py:L241-L248`). `type=bool` means command-line
  strings such as `"False"` still evaluate truthy; this is source-confirmed Python behavior.
- Evaluation is hard-coded to `scene-0103` and `scene-1077`
  (`OpenEMMA@8403ea6:main.py:L305-L318`). There is no manifest argument.
- `OBS_LEN=10` and `FUT_LEN=10`; the loop uses `range(scene_length - 20)`, omitting the final
  otherwise valid 20-frame window (`OpenEMMA@8403ea6:main.py:L31-L33,L351-L356,L391-L400`).

The repository also contains `BaseOpenEMMA`, a separate library-style waypoint path. It is not
the documented GitHub CLI. It consumes `gt_ego_fut_diff` and `gt_ego_fut_trajs` to construct a
meta-action rationale, so it has direct future-target leakage and is disqualified as a prediction
baseline (`OpenEMMA@8403ea6:openemma/vlm/base_backbone.py:L71-L76,L91-L142,L157-L166`).

### Frames gathered versus consumed

The CLI gathers one `CAM_FRONT` keyframe per nuScenes sample. GPT stores base64 strings; other
backends store paths (`OpenEMMA@8403ea6:main.py:L320-L344`). Each window initially contains ten
paths/strings (`main.py:L391-L400`). Actual VLM inputs then diverge:

| Backend selector | Actual input in documented CLI | Source-confirmed generation behavior |
|---|---|---|
| `gpt` | ten base64 strings remain in `obs_images` | custom image-message objects, `gpt-4o-2024-11-20`, `max_tokens=400`; system message appended after user message (`main.py:L136-L160,L394-L425`) |
| `qwen` / `Qwen` | only `obs_images[-1]`, a single path | chat template and vision processor; `max_new_tokens=128`, no sampling arguments (`main.py:L73-L93,L405-L425`) |
| `llava` | only the final image path | `do_sample=True`, temperature 0.2, one beam, `max_new_tokens=2048` (`main.py:L95-L134,L405-L425`) |
| `llama` / `Llama` | only the final image path | inference code exists, but the CLI loader has no Llama branch and leaves model/processor unset (`main.py:L53-L71,L252-L295,L405-L425`) |

All scene/object/intent prompts describe multiple front-view images over the past five seconds
(`main.py:L162-L193`). Non-GPT backends actually receive one image. Even for GPT, ten keyframes
at nominal 0.5-second intervals span nine intervals (4.5 seconds), not five seconds. The prompt
and processor inputs therefore do not describe the same temporal evidence.

The GPT payload uses `{"image": ..., "resize": 768}` entries rather than the base64
`image_url` form used by `utils.query_gpt4`, and places the system message after the user message
(`main.py:L136-L160`; `utils.py:L23-L111`). Whether the pinned OpenAI client accepts this payload
is a runtime unknown.

### Prompt and call order

For `method=openemma`, each `GenerateMotion` attempt calls scene description, critical-object
description, and stateful intent description before the final motion prompt
(`OpenEMMA@8403ea6:main.py:L198-L239`). Other method strings skip the three rationale calls and
use a motion-history prompt without those descriptions (`main.py:L224-L234`).

The intent from one accepted or retried window becomes `prev_intent` for the next window
(`main.py:L386-L428`), so samples are not independent. The motion call retries up to three times
when text contains `unable`/`sorry` or lacks `[`. The outer parser loop can invoke
`GenerateMotion` up to three times, recomputing rationales (`main.py:L235-L239,L417-L434`). An
OpenEMMA sample can therefore make up to 18 VLM calls. Retry count and discarded raw texts are
not persisted.

The long safety/task system message is passed only through the GPT branch; the local Qwen,
LLaVA, and Llama inference branches ignore `sys_message` (`main.py:L53-L160,L222-L236`). This is
material backend prompt divergence.

### Model and generation configuration

- Qwen first loads a hard-coded local Qwen2.5-VL-3B path under `/root/OpenEMMA/models/`, then
  catches any exception and falls back to the floating Hub identifier `Qwen/Qwen2-VL-7B-Instruct`
  (`OpenEMMA@8403ea6:main.py:L255-L281`). Neither model revision is pinned.
- LLaVA loads either a fixed Hub identifier or the supplied path (`main.py:L282-L290`).
- The documented Llama selector has no corresponding CLI model initialization
  (`main.py:L282-L295`).
- GPT embeds an API-key placeholder and a dated model name in source (`main.py:L29,L136-L160`).
- No random seed is set. Qwen and Llama omit sampling arguments; LLaVA explicitly samples;
  GPT does not set temperature in this path.

There are two module-level `vlm_inference` definitions. When `main.py` is executed as a script,
the main loop runs before Python reaches the second definition, so the first multi-backend
implementation is active. When the module is imported, the later Qwen-only definition replaces
it (`OpenEMMA@8403ea6:main.py:L53-L160,L241-L524,L524-L580`). Script and import behavior are
therefore not equivalent.

## Motion representation, parsing, and evaluation

### Historical motion and scaling

- Position differences between adjacent keyframes are called velocities without division by
  timestamp delta; their Euclidean norm is formatted as speed (`main.py:L358-L370,L211-L217`).
  Reverse direction is lost by the norm.
- Signed three-point curvature is estimated in world XY
  (`OpenEMMA@8403ea6:utils.py:L246-L273`). Observed curvature is multiplied by 100 before prompt
  formatting and predicted curvature is divided by 100 after parsing
  (`main.py:L211-L217,L435-L445`).
- Actual nuScenes timestamps are never read. The prompt assumes 0.5 seconds, while integration
  uses `np.linspace(0, time_span, time_span)`, whose spacing is greater than one for more than one
  prediction (`utils.py:L275-L296`). Units are therefore not a verified m/s-by-seconds contract.

### Parser and failure accounting

The parser accepts any number of bracketed decimal pairs, truncates above ten, and does not
require ten actions (`OpenEMMA@8403ea6:main.py:L427-L445`). Empty matches are retried, then the
sample is silently skipped (`main.py:L417-L434`). Partial sequences are scored on a shorter
horizon. Runtime exceptions are not converted to structured per-sample records.

Only per-scene aggregate JSONL is written. Expected samples, produced samples, valid samples,
raw generations, retry counts, parse failures, and failure classes are absent
(`main.py:L491-L516`). The reported denominator can therefore change by backend/method without
being recoverable offline.

### Anchor, horizon, and metrics

The CLI starts integration at the final observed pose, not a future target
(`OpenEMMA@8403ea6:main.py:L402-L405,L443-L451`). This anchor choice itself is leakage-free.
However, `IntegrateCurvatureForPoints` returns the initial pose as prediction index zero, while
the evaluator compares it with future target index zero (`main.py:L443-L459`; `utils.py:L275-L296`).
This creates an alignment mismatch. The one-second ADE uniquely shifts prediction indices, while
the two- and three-second ADE do not (`main.py:L461-L471`). No FDE is computed. Aggregate
`avgade` is an unweighted mean of the three scene-level ADE means (`main.py:L500-L516`).

These official metrics are not trusted evaluation evidence. The same raw action text must be
re-evaluated with Emma-reasoning's timestamp-aware evaluator in Phase 3.

## Legacy Config archaeology

The pinned Config checkout is historical evidence only.

- Its `main.py` is close to the official CLI. The principal prompt-path change adds a
  `--reasoning-mode` flag and, for non-`cot` values, only inserts “Use cot-sc/tot reasoning” into
  the prompt. It does not implement candidate sampling/aggregation in that entry point
  (`CoT@a214a2c:main.py:L221-L263`). It also adds user-specific offline Hugging Face cache paths
  (`main.py:L286-L309`).
- Its modified `BaseOpenEMMA` implements CoT-SC by majority-voting meta-decisions and ToT by
  scoring thoughts. Both meta-decisions and ToT scores use `gt_ego_fut_diff` or
  `gt_ego_fut_trajs`, creating explicit future-target leakage
  (`CoT@a214a2c:openemma/vlm/base_backbone.py:L79-L177,L257-L282`).
- `run_tot_new.py` is a separate larger pipeline. SC numerically averages/medians/trims parsed
  action arrays after dropping invalid candidates; ToT selects with a score dominated by
  continuity, smoothness, comfort, and nonnegative progress relative to motion history
  (`CoT@a214a2c:run_tot_new.py:L158-L190,L237-L293,L542-L614`). It does not establish visually
  grounded selection.
- That script supplies `fut_traj_world_np[0]` as the prediction integration anchor, directly
  using a future target, and silently skips parse failures
  (`run_tot_new.py:L740-L801`). It saves selected predictions and scene aggregates, not all raw
  candidates, scores, seeds, or failures (`run_tot_new.py:L833-L909`).
- Defaults include a user-specific dataroot, floating Qwen model ID, five SC samples, trimmed
  aggregation, and 8x2 ToT sampling (`run_tot_new.py:L916-L945`).

The legacy outputs are not a paper baseline and must not be called an OpenEMMA reproduction.

## Confirmed blockers to an untouched pilot

1. Freeze a deterministic manifest outside the hard-coded two-scene loop and define how the
   untouched process is bounded without editing pinned source.
2. Pin one supported model/checkpoint revision and verify its cache/environment. Llama is not
   runnable through the documented loader as written.
3. Build an external capture harness for ordered actual image inputs, complete prompts, every raw
   call, retries, exceptions, parse outcomes, and expected/valid denominators.
4. Choose script execution versus imported invocation explicitly; they resolve different
   `vlm_inference` implementations.
5. Treat the official parser/evaluator as an observed output only. Do not use it for trusted
   parity claims; preserve raw text for offline re-evaluation.
6. Predeclare behavior for partial action sequences and failed samples without silently changing
   the manifest denominator.

## Runtime unknowns

- Whether the installed OpenAI client accepts the GPT message schema and message ordering.
- Which Qwen branch is selected by the Qwen2.5 model-type check when imported.
- Model/cache availability, dependency compatibility, GPU memory, latency, and deterministic
  repeatability for each backend.
- Whether PyPI `openemma` behavior matches this pinned GitHub tree; the PyPI package was not
  installed or audited.

## Next action

Phase 2 preparation may design a 5–10-sample immutable manifest and external provenance capture
harness. Stop before the first GPU model inference and request explicit authorization with the
model revision, environment plan, estimated memory/runtime, and failure policy.
