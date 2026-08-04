import json
from pathlib import Path

import pytest

from emma_reasoning.upstreams import discover_upstreams, load_upstream_lock


def test_committed_upstream_locks_are_valid_and_pinned() -> None:
    specs = discover_upstreams(Path.cwd())
    assert {spec.name for spec in specs} == {
        "legacy-cot-prototype",
        "openemma-official",
    }
    by_name = {spec.name: spec for spec in specs}
    assert by_name["openemma-official"].pinned_commit == (
        "8403ea636696c5c10e8fdeca566410de0a07e449"
    )
    assert by_name["openemma-official"].checkout_path == Path("third_party/OpenEMMA")
    assert by_name["legacy-cot-prototype"].pinned_commit == (
        "a214a2ccc2581e4a59e59d392fb969c29519044e"
    )


def test_lock_rejects_floating_or_short_commit(tmp_path: Path) -> None:
    path = tmp_path / "bad.lock.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "bad",
                "role": "test",
                "repository": {
                    "ssh_url": "git@example.com:bad/repo.git",
                    "https_url": "https://example.com/bad/repo.git",
                    "web_url": "https://example.com/bad/repo",
                },
                "pinned_commit": "main",
                "checkout_path": "third_party/bad",
                "policy": {},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="40-character"):
        load_upstream_lock(path)


def test_lock_rejects_checkout_outside_third_party(tmp_path: Path) -> None:
    path = tmp_path / "bad-path.lock.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "bad",
                "role": "test",
                "repository": {
                    "ssh_url": "git@example.com:bad/repo.git",
                    "https_url": "https://example.com/bad/repo.git",
                    "web_url": "https://example.com/bad/repo",
                },
                "pinned_commit": "0" * 40,
                "checkout_path": "src/copied-upstream",
                "policy": {},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="third_party"):
        load_upstream_lock(path)
