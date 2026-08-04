#!/usr/bin/env python3
"""Clone and verify pinned external repositories without vendoring their source."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from emma_reasoning.upstreams import UpstreamSpec, discover_upstreams

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str, capture: bool = False) -> str:
    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )
    return result.stdout.strip() if capture else ""


def _git(spec: UpstreamSpec, *args: str, capture: bool = False) -> str:
    checkout = spec.resolved_checkout(PROJECT_ROOT)
    return _run("git", "-C", str(checkout), *args, capture=capture)


def _is_clean(spec: UpstreamSpec) -> bool:
    return _git(spec, "status", "--porcelain", capture=True) == ""


def verify(spec: UpstreamSpec, *, allow_dirty: bool = False) -> dict[str, object]:
    """Verify checkout presence, commit identity, and worktree cleanliness."""
    checkout = spec.resolved_checkout(PROJECT_ROOT)
    if not (checkout / ".git").exists():
        raise RuntimeError(f"{spec.name}: missing git checkout at {checkout}.")
    head = _git(spec, "rev-parse", "HEAD", capture=True)
    clean = _is_clean(spec)
    if head != spec.pinned_commit:
        raise RuntimeError(
            f"{spec.name}: HEAD {head} does not match pinned commit {spec.pinned_commit}."
        )
    if not clean and not allow_dirty:
        raise RuntimeError(f"{spec.name}: checkout is dirty; paper runs require a clean upstream.")
    return {
        "name": spec.name,
        "checkout": str(checkout),
        "head": head,
        "clean": clean,
        "verified": True,
    }


def sync(spec: UpstreamSpec, *, transport: str) -> dict[str, object]:
    """Clone or update one checkout and detach it at the pinned commit."""
    checkout = spec.resolved_checkout(PROJECT_ROOT)
    remote = spec.ssh_url if transport == "ssh" else spec.https_url
    checkout.parent.mkdir(parents=True, exist_ok=True)

    if checkout.exists() and not (checkout / ".git").exists():
        raise RuntimeError(f"{spec.name}: {checkout} exists but is not a git checkout.")
    if (checkout / ".git").exists() and not _is_clean(spec):
        raise RuntimeError(f"{spec.name}: refusing to update a dirty checkout at {checkout}.")

    if not checkout.exists():
        _run("git", "clone", "--no-checkout", remote, str(checkout))
    else:
        _git(spec, "remote", "set-url", "origin", remote)

    _git(spec, "fetch", "--tags", "--prune", "origin")
    _git(spec, "checkout", "--detach", spec.pinned_commit)
    return verify(spec)


def _select(specs: tuple[UpstreamSpec, ...], names: list[str]) -> tuple[UpstreamSpec, ...]:
    if not names:
        return specs
    by_name = {spec.name: spec for spec in specs}
    unknown = sorted(set(names) - set(by_name))
    if unknown:
        raise ValueError(f"Unknown upstream name(s): {', '.join(unknown)}")
    return tuple(by_name[name] for name in names)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="Print locked upstream specifications.")
    list_parser.add_argument("--name", action="append", default=[])

    sync_parser = subparsers.add_parser("sync", help="Clone/update pinned checkouts.")
    sync_parser.add_argument("--name", action="append", default=[])
    sync_parser.add_argument("--transport", choices=("ssh", "https"), default="ssh")

    verify_parser = subparsers.add_parser("verify", help="Verify commit and cleanliness.")
    verify_parser.add_argument("--name", action="append", default=[])
    verify_parser.add_argument("--allow-dirty", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    specs = _select(discover_upstreams(PROJECT_ROOT), args.name)

    if args.command == "list":
        payload = [
            {
                "name": spec.name,
                "role": spec.role,
                "web_url": spec.web_url,
                "pinned_commit": spec.pinned_commit,
                "checkout_path": str(spec.checkout_path),
            }
            for spec in specs
        ]
    elif args.command == "sync":
        payload = [sync(spec, transport=args.transport) for spec in specs]
    else:
        payload = [verify(spec, allow_dirty=args.allow_dirty) for spec in specs]

    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
