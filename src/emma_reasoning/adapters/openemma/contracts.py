"""JSON-friendly boundary between OpenEMMA and trusted evaluation.

These contracts intentionally contain raw upstream inputs and outputs. They do not
reimplement OpenEMMA model loading, visual preprocessing, prompt construction, parsing,
or trajectory evaluation.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any

_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


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
        if not _COMMIT_RE.fullmatch(self.commit):
            raise ValueError("commit must be a full 40-character lowercase SHA.")
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
        if not self.image_paths or any(not path for path in self.image_paths):
            raise ValueError("image_paths must contain non-empty paths.")
        lengths = {
            len(self.observed_speeds_mps),
            len(self.observed_curvatures_inv_m),
            len(self.observed_timestamps_seconds),
        }
        if len(lengths) != 1 or next(iter(lengths)) == 0:
            raise ValueError("Observed speed, curvature, and timestamp sequences must align.")
        numeric_values = (
            *self.observed_speeds_mps,
            *self.observed_curvatures_inv_m,
            *self.observed_timestamps_seconds,
        )
        if not all(math.isfinite(value) for value in numeric_values):
            raise ValueError("Observed motion sequences must contain only finite values.")
        if any(
            later <= earlier
            for earlier, later in zip(
                self.observed_timestamps_seconds,
                self.observed_timestamps_seconds[1:],
                strict=False,
            )
        ):
            raise ValueError("observed_timestamps_seconds must be strictly increasing.")


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
