"""Tests for the Week 4 repository auditor.

Run them from the project root:

    pytest -q

Three tests fail when you start. Each one names a check you have to write in
`src/check_repo.py`. Work through them one at a time and re-run.

These tests build tiny repositories in a temporary folder rather than pointing
at your real work, so a test tells you whether your rule is correct, not
whether your own repository happens to be tidy.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from check_repo import (  # noqa: E402
    check_data_documented,
    check_entry_point,
    check_environment_pinned,
    check_no_absolute_paths,
    check_secrets_ignored,
    check_tests_present,
)


def build(tmp_path: Path, files: dict[str, str]) -> Path:
    """Create a throwaway repository from a mapping of path to contents."""
    for rel, body in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return tmp_path


# ------------------------------------------------- worked examples: green
def test_environment_pinned_accepts_exact_versions(tmp_path):
    repo = build(tmp_path, {"requirements.txt": "pandas==2.2.2\npytest==8.3.2\n"})
    assert check_environment_pinned(repo).passed


def test_environment_pinned_rejects_a_bare_name(tmp_path):
    repo = build(tmp_path, {"requirements.txt": "pandas==2.2.2\nnumpy\n"})
    result = check_environment_pinned(repo)
    assert not result.passed
    assert any("numpy" in line for line in result.evidence)


def test_environment_pinned_ignores_comments_and_flags(tmp_path):
    repo = build(tmp_path, {
        "requirements.txt": "# the course environment\n-r base.txt\npandas==2.2.2\n"})
    assert check_environment_pinned(repo).passed


def test_entry_point_needs_a_fenced_command(tmp_path):
    repo = build(tmp_path, {"README.md": "# Project\n\nRun it somehow.\n"})
    assert not check_entry_point(repo).passed

    repo2 = build(tmp_path / "two", {
        "README.md": "# Project\n\n```bash\npython src/run.py\n```\n"})
    assert check_entry_point(repo2).passed


def test_no_absolute_paths_finds_a_windows_path(tmp_path):
    repo = build(tmp_path, {
        "src/run.py": 'import pandas\ndf = pandas.read_csv("C:/Users/Sam/plant.csv")\n'})
    result = check_no_absolute_paths(repo)
    assert not result.passed
    assert "src/run.py" in result.evidence[0]


def test_no_absolute_paths_allows_a_relative_one(tmp_path):
    repo = build(tmp_path, {
        "src/run.py": 'import pandas\ndf = pandas.read_csv("data/raw/plant.csv")\n'})
    assert check_no_absolute_paths(repo).passed


# ------------------------------------------------------ your work: red
def test_data_documented_wants_a_source_and_a_licence(tmp_path):
    """TODO 1 in src/check_repo.py."""
    good = build(tmp_path / "good", {
        "docs/data_choice.md": "Source: plant reporting system.\nLicence: teaching use only.\n"})
    assert check_data_documented(good).passed

    bad = build(tmp_path / "bad", {
        "docs/data_choice.md": "Source: plant reporting system.\n"})
    assert not check_data_documented(bad).passed


def test_data_documented_fails_when_docs_is_empty(tmp_path):
    """TODO 1. An empty docs/ is a failure, not a crash."""
    repo = build(tmp_path, {"README.md": "# Project\n"})
    (repo / "docs").mkdir(exist_ok=True)
    assert not check_data_documented(repo).passed


def test_secrets_ignored_wants_the_patterns_present(tmp_path):
    """TODO 2."""
    good = build(tmp_path / "good", {".gitignore": ".venv/\n__pycache__/\n*.env\n"})
    assert check_secrets_ignored(good).passed

    bad = build(tmp_path / "bad", {".gitignore": "__pycache__/\n"})
    result = check_secrets_ignored(bad)
    assert not result.passed
    assert any(".venv" in line for line in result.evidence)


def test_secrets_ignored_catches_a_committed_secret(tmp_path):
    """TODO 2. The patterns being listed is not enough if the file is there."""
    repo = build(tmp_path, {".gitignore": ".venv/\n__pycache__/\n*.env\n",
                            "config/.env": "API_KEY=not-a-real-key\n"})
    result = check_secrets_ignored(repo)
    assert not result.passed
    assert any(".env" in line for line in result.evidence)


def test_secrets_ignored_fails_without_a_gitignore(tmp_path):
    """TODO 2. A missing .gitignore is a failure, not a crash."""
    repo = build(tmp_path, {"README.md": "# Project\n"})
    assert not check_secrets_ignored(repo).passed


def test_tests_present_wants_an_actual_test(tmp_path):
    """TODO 3."""
    good = build(tmp_path / "good", {
        "tests/test_rules.py": "def test_one():\n    assert True\n"})
    assert check_tests_present(good).passed

    empty = build(tmp_path / "empty", {"README.md": "# Project\n"})
    (empty / "tests").mkdir(exist_ok=True)
    assert not check_tests_present(empty).passed


def test_tests_present_rejects_a_file_with_no_test_function(tmp_path):
    """TODO 3. A file called test_something.py containing no test is the case
    worth catching."""
    repo = build(tmp_path, {"tests/test_rules.py": "HELPERS = 1\n"})
    assert not check_tests_present(repo).passed
