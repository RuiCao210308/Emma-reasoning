"""JSON-friendly boundary between OpenEMMA and trusted evaluation.

These contracts intentionally contain raw upstream inputs and outputs. They do not
reimplement OpenEMMA model loading, visual preprocessing, prompt construction, parsing,
or trajectory evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class UpstreamProvenance:
    """Identity of the exact external source used for one run."""

    name: str
    commit: str
    checkout_clean: bool
    model_id: str
    method: str
    command: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name or not self.model_id or not self.method:
            raise ValueError("name, model_id, and method must be non-empty.")
        if len(self.commit) != 40:
            raise ValueError("commit must be a full 40-character SHA.")
        if not self.command:
            raise ValueError("command must not be empty.")


@dataclass(frozen=True)
class OpenEmmaInvocation:
    """Audit record for the information presented to the upstream pipeline."""

    run_id: str
    sample_id: str
    image_paths: tuple[str, ...]
    observed_speeds_mps: tuple[float, ...]
    observed_curvatures_inv_m: tuple[float, ...]
    observed_timestamps_seconds: tuple[float, ...]
    provenance: UpstreamProvenance
    intervention: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.run_id or not self.sample_id:
            raise ValueError("run_id and sample_id must be non-empty.")
        if not self.image_paths:
            raise ValueError("image_paths must not be empty.")
        lengths = {
            len(self.observed_speeds_mps),
            len(self.observed_curvatures_inv_m),
            len(self.observed_timestamps_seconds),
        }
        if len(lengths) != 1 or next(iter(lengths)) == 0:
            raise ValueError("Observed speed, curvature, and timestamp sequences must align.")


@dataclass(frozen=True)
class OpenEmmaRawResult:
    """Unparsed upstream output captured before trusted post-processing."""

    run_id: str
    sample_id: str
    raw_motion_text: str | None
    scene_description: str | None
    object_description: str | None
    intent_description: str | None
    prompts: dict[str, str]
    generation_metadata: dict[str, Any]
    error: str | None = None

    def __post_init__(self) -> None:
        if not self.run_id or not self.sample_id:
            raise ValueError("run_id and sample_id must be non-empty.")
        if self.error is None and self.raw_motion_text is None:
            raise ValueError("A successful result must contain raw_motion_text.")
