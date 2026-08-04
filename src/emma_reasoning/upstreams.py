"""Validated provenance locks for external reference implementations."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class UpstreamSpec:
    """One pinned external repository checkout."""

    name: str
    role: str
    ssh_url: str
    https_url: str
    web_url: str
    pinned_commit: str
    checkout_path: Path
    policy: dict[str, Any]
    lock_path: Path

    def resolved_checkout(self, project_root: Path) -> Path:
        """Return the absolute local checkout path under a project root."""
        return (project_root / self.checkout_path).resolve()


def load_upstream_lock(path: Path) -> UpstreamSpec:
    """Load and strictly validate one upstream lock file."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != 1:
        raise ValueError(f"Unsupported schema_version in {path}.")

    repository = raw.get("repository")
    if not isinstance(repository, dict):
        raise ValueError(f"repository must be an object in {path}.")

    required_strings = {
        "name": raw.get("name"),
        "role": raw.get("role"),
        "ssh_url": repository.get("ssh_url"),
        "https_url": repository.get("https_url"),
        "web_url": repository.get("web_url"),
        "pinned_commit": raw.get("pinned_commit"),
        "checkout_path": raw.get("checkout_path"),
    }
    for field, value in required_strings.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string in {path}.")

    pinned_commit = required_strings["pinned_commit"]
    if not _COMMIT_RE.fullmatch(pinned_commit):
        raise ValueError(f"pinned_commit must be a full 40-character lowercase SHA in {path}.")

    checkout_path = Path(required_strings["checkout_path"])
    if checkout_path.is_absolute() or ".." in checkout_path.parts:
        raise ValueError(f"checkout_path must be project-relative in {path}.")
    if not checkout_path.parts or checkout_path.parts[0] != "third_party":
        raise ValueError(f"checkout_path must live under third_party/ in {path}.")

    policy = raw.get("policy")
    if not isinstance(policy, dict):
        raise ValueError(f"policy must be an object in {path}.")

    return UpstreamSpec(
        name=required_strings["name"],
        role=required_strings["role"],
        ssh_url=required_strings["ssh_url"],
        https_url=required_strings["https_url"],
        web_url=required_strings["web_url"],
        pinned_commit=pinned_commit,
        checkout_path=checkout_path,
        policy=policy,
        lock_path=path,
    )


def discover_upstreams(project_root: Path) -> tuple[UpstreamSpec, ...]:
    """Load every `*.lock.json` file in deterministic name order."""
    lock_dir = project_root / "upstreams"
    paths = sorted(lock_dir.glob("*.lock.json"))
    if not paths:
        raise FileNotFoundError(f"No upstream lock files found under {lock_dir}.")
    specs = tuple(load_upstream_lock(path) for path in paths)
    names = [spec.name for spec in specs]
    if len(names) != len(set(names)):
        raise ValueError("Upstream names must be unique.")
    return specs
