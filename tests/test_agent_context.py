from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_agent_context.py"
FILE_BUDGETS = {
    "AGENTS.md": 12 * 1024,
    "GOAL.md": 40 * 1024,
    "docs/context/PROJECT_STATE.md": 10 * 1024,
    ".codex/rules/upstream-parity.md": 8 * 1024,
    ".codex/rules/experiments.md": 8 * 1024,
    ".codex/rules/reporting.md": 8 * 1024,
    ".codex/rules/git-workflow.md": 8 * 1024,
}


def run_check(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )


def copy_context_tree(destination: Path) -> None:
    for relative in FILE_BUDGETS:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)


def test_all_context_files_exist() -> None:
    for relative in FILE_BUDGETS:
        assert (ROOT / relative).is_file(), relative


def test_context_files_respect_size_budgets() -> None:
    for relative, budget in FILE_BUDGETS.items():
        assert (ROOT / relative).stat().st_size <= budget, relative


def test_agent_rule_references_exist() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    references = set(re.findall(r"\.codex/rules/[a-z0-9-]+\.md", text))
    assert references
    assert all((ROOT / reference).is_file() for reference in references)


def test_agents_routes_active_work_through_goal() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "GOAL.md" in text
    assert (ROOT / "GOAL.md").is_file()


def test_context_check_script_succeeds() -> None:
    result = run_check(ROOT)
    assert result.returncode == 0, result.stdout + result.stderr


def test_oversized_agent_file_fails(tmp_path: Path) -> None:
    copy_context_tree(tmp_path)
    (tmp_path / "AGENTS.md").write_text("line\n" * 3000, encoding="utf-8")

    result = run_check(tmp_path)

    assert result.returncode != 0
    assert "budget" in result.stdout


def test_oversized_goal_file_fails(tmp_path: Path) -> None:
    copy_context_tree(tmp_path)
    (tmp_path / "GOAL.md").write_text("goal line\n" * 6000, encoding="utf-8")

    result = run_check(tmp_path)

    assert result.returncode != 0
    assert "GOAL.md" in result.stdout


def test_missing_goal_fails(tmp_path: Path) -> None:
    copy_context_tree(tmp_path)
    (tmp_path / "GOAL.md").unlink()

    result = run_check(tmp_path)

    assert result.returncode != 0
    assert "missing required file: GOAL.md" in result.stdout


def test_missing_rule_fails(tmp_path: Path) -> None:
    copy_context_tree(tmp_path)
    missing = tmp_path / ".codex/rules/reporting.md"
    missing.unlink()

    result = run_check(tmp_path)

    assert result.returncode != 0
    assert "missing" in result.stdout
    assert ".codex/rules/reporting.md" in result.stdout
