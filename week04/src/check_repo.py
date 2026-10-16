"""Reproducibility checks for a project repository.

Week 3 checked a data file. This checks the repository around it.

Three checks are written for you as worked examples. Three are marked TODO and
are your work in this lab. Run the tests to see which ones are outstanding:

    pytest -q

Every check answers the same four questions, exactly as in Week 3:

    name         what do we call this rule?
    expectation  what should be true, in one sentence a colleague can read?
    passed       did it hold?
    evidence     which files or lines should a human open?

A check never repairs anything. It produces evidence and lets a person decide.

Usage:

    python src/check_repo.py --repo ../my-week03-repo
    python src/check_repo.py --repo ../my-week03-repo --output artifacts/repo_audit.json

Exit status 0 means every check passed. Exit status 1 means the audit ran and
found failures. A traceback means the program itself broke, which is a
different thing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Paths a human wrote that only exist on one machine. Kept here rather than
# inline so the rule is readable and so a new pattern is a one-line change.
ABSOLUTE_PATH_PATTERNS = [
    r"[A-Za-z]:[\\/]",        # C:\Users\... or C:/Users/...
    r"/Users/[A-Za-z0-9._-]+",
    r"/home/[A-Za-z0-9._-]+",
]

# Things that must never be committed. Matched against tracked file names.
SECRET_NAME_PATTERNS = [r"\.env$", r"^secrets?\.", r"\.pem$", r"_rsa$",
                        r"credentials?\.(json|ya?ml|ini|toml)$"]

# Patterns a .gitignore is expected to carry.
REQUIRED_IGNORES = [".venv", "__pycache__", ".env"]


@dataclass
class Result:
    """The outcome of one check."""

    name: str
    expectation: str
    passed: bool
    evidence: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"name": self.name, "expectation": self.expectation,
                "passed": self.passed, "evidence": self.evidence}


# --------------------------------------------------------------- helpers
def read(path: Path) -> str:
    """File contents, or an empty string if it is not there or not text."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeError):
        return ""


def python_files(repo: Path) -> list[Path]:
    """Every .py file in the repository, excluding the environment itself."""
    out = []
    for p in sorted(repo.rglob("*.py")):
        parts = set(p.parts)
        if ".venv" in parts or "__pycache__" in parts or "site-packages" in parts:
            continue
        out.append(p)
    return out


# ------------------------------------------------------- worked examples
def check_environment_pinned(repo: Path) -> Result:
    """Worked example: every dependency names an exact version."""
    req = repo / "requirements.txt"
    if not req.exists():
        return Result("environment_pinned",
                      "Every dependency is pinned to an exact version",
                      False, ["requirements.txt is missing"])
    loose = []
    for n, line in enumerate(read(req).splitlines(), start=1):
        text = line.split("#", 1)[0].strip()
        if not text or text.startswith("-"):
            continue
        if "==" not in text:
            loose.append("requirements.txt line %d: %s" % (n, text))
    return Result("environment_pinned",
                  "Every dependency is pinned to an exact version",
                  not loose, loose)


def check_entry_point(repo: Path) -> Result:
    """Worked example: the README shows a command, in a fenced block."""
    readme = repo / "README.md"
    if not readme.exists():
        return Result("entry_point", "The README gives a command that can be run",
                      False, ["README.md is missing"])
    body = read(readme)
    fenced = re.findall(r"```[a-zA-Z]*\n(.*?)```", body, re.S)
    commands = [c.strip() for block in fenced for c in block.splitlines()
                if c.strip() and not c.strip().startswith("#")]
    if not commands:
        return Result("entry_point", "The README gives a command that can be run",
                      False, ["README.md has no fenced command block"])
    return Result("entry_point", "The README gives a command that can be run",
                  True, ["README.md: %s" % commands[0]])


def check_no_absolute_paths(repo: Path) -> Result:
    """Worked example: no source file names a path from one machine."""
    hits = []
    for path in python_files(repo):
        for n, line in enumerate(read(path).splitlines(), start=1):
            # A path in a comment cannot break a run, and examples in comments
            # are common. Only what executes counts.
            code = line.split("#", 1)[0]
            if not code.strip():
                continue
            line = code
            for pattern in ABSOLUTE_PATH_PATTERNS:
                if re.search(pattern, line):
                    hits.append("%s line %d: %s"
                                % (path.relative_to(repo).as_posix(), n, line.strip()[:70]))
                    break
    return Result("no_absolute_paths",
                  "No source file contains a path that exists on one machine only",
                  not hits, hits)


# ------------------------------------------------------------- your work
def check_data_documented(repo: Path) -> Result:
    """TODO 1.

    The repository records where its data came from and whether it may be
    used. Pass when a file under docs/, or the README, mentions both a
    source and a licence.

    Suggested evidence when it fails: which of the two words is missing, and
    which files under docs/ you looked at.
    """
    raise NotImplementedError("check_data_documented is your work in this lab")


def check_secrets_ignored(repo: Path) -> Result:
    """TODO 2.

    Two things have to be true, and a useful check reports them separately:
    the .gitignore carries the patterns in REQUIRED_IGNORES, and no file whose
    name matches SECRET_NAME_PATTERNS is present in the repository.

    A missing .gitignore is a failure, not a crash.
    """
    raise NotImplementedError("check_secrets_ignored is your work in this lab")


def check_tests_present(repo: Path) -> Result:
    """TODO 3.

    Something checks this repository without the author being present. Pass
    when a tests/ directory exists and contains at least one file named
    test_*.py that contains at least one function named test_*.

    A tests/ folder holding no tests is the case worth catching.
    """
    raise NotImplementedError("check_tests_present is your work in this lab")


CHECKS = [
    check_environment_pinned,
    check_entry_point,
    check_no_absolute_paths,
    check_data_documented,
    check_secrets_ignored,
    check_tests_present,
]


def audit(repo: Path) -> list[Result]:
    """Run every check that has been written. Unwritten ones fail loudly."""
    results = []
    for check in CHECKS:
        try:
            results.append(check(repo))
        except NotImplementedError as exc:
            results.append(Result(check.__name__.replace("check_", ""),
                                  "Not written yet", False, [str(exc)]))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, type=Path,
                        help="path to the repository to audit")
    parser.add_argument("--output", type=Path,
                        help="where to write the JSON result")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    if not repo.is_dir():
        print("No such directory: %s" % repo, file=sys.stderr)
        return 2

    results = audit(repo)
    for r in results:
        print("%-4s %-22s %s" % ("PASS" if r.passed else "FAIL", r.name,
                                 r.expectation))
        for line in r.evidence[:5]:
            print("       %s" % line)
        if len(r.evidence) > 5:
            print("       ... and %d more" % (len(r.evidence) - 5))

    failed = [r for r in results if not r.passed]
    print("\nOverall status: %s (%d of %d checks passed)"
          % ("PASS" if not failed else "FAIL",
             len(results) - len(failed), len(results)))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(
            {"repository": repo.name,
             "overall": "PASS" if not failed else "FAIL",
             "checks": [r.as_dict() for r in results]},
            indent=2), encoding="utf-8")
        print("Wrote %s" % args.output)

    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
