#!/usr/bin/env python3
"""Check that Codex guidance stays present, routed, and compact."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

FILE_BUDGETS = {
    "AGENTS.md": 12 * 1024,
    "docs/context/PROJECT_STATE.md": 10 * 1024,
    ".codex/rules/upstream-parity.md": 8 * 1024,
    ".codex/rules/experiments.md": 8 * 1024,
    ".codex/rules/reporting.md": 8 * 1024,
    ".codex/rules/git-workflow.md": 8 * 1024,
}
RULE_REFERENCE = re.compile(r"\.codex/rules/[a-z0-9-]+\.md")
WEIGHT_PATH = re.compile(r"\S+\.(?:pt|pth|ckpt|safetensors)\b", re.IGNORECASE)


def check_context(root: Path) -> list[str]:
    """Return human-readable failures for the context tree under *root*."""
    failures: list[str] = []

    for relative, budget in FILE_BUDGETS.items():
        path = root / relative
        if not path.is_file():
            failures.append(f"missing required file: {relative}")
            continue
        size = path.stat().st_size
        if size > budget:
            failures.append(f"{relative} is {size} bytes; budget is {budget}")

    agents_path = root / "AGENTS.md"
    if not agents_path.is_file():
        return failures

    text = agents_path.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    if line_count > 400:
        failures.append(f"AGENTS.md is {line_count} lines; limit is 400")

    references = sorted(set(RULE_REFERENCE.findall(text)))
    if not references:
        failures.append("AGENTS.md contains no task-rule references")
    for reference in references:
        if not (root / reference).is_file():
            failures.append(f"AGENTS.md references missing rule: {reference}")

    json_blocks = re.findall(r"```json\s*\n(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if any(len(block.splitlines()) > 20 for block in json_blocks):
        failures.append("AGENTS.md contains a JSON block longer than 20 lines")

    if text.count('"sample_id"') > 5:
        failures.append("AGENTS.md appears to contain full experimental records")
    if len(WEIGHT_PATH.findall(text)) > 8:
        failures.append("AGENTS.md appears to contain a model-weight path inventory")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (defaults to the parent of scripts/)",
    )
    args = parser.parse_args()

    failures = check_context(args.root.resolve())
    if failures:
        print(f"agent context check: FAILED ({len(failures)} issue(s))")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"agent context check: PASSED ({len(FILE_BUDGETS)} files, all routes valid)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
