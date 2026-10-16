"""Every path this project uses, in one place.

This module exists so that no other file has to know where anything lives. It
is the worked example of the rule from the lecture: a path is configuration,
not code, and anything that differs between two machines belongs outside the
code that uses it.

Two things follow from that.

Nothing here is absolute. Every path is built from the repository root, which
is found from this file's own location, so a fresh clone works wherever it is
put. Move the repository, rename the folder, put it on another drive, and
nothing breaks.

Anything that genuinely has to vary can be overridden with an environment
variable, without editing a line of source:

    WEEK0506_DATA_RAW=/mnt/shared/plant python src/make_week.py --student-id your-github-username

Import it rather than retyping paths:

    from paths import DATA_RAW, ARTIFACTS
"""

from __future__ import annotations

import os
from pathlib import Path

# This file is <root>/src/paths.py, so the root is two levels up. Deriving it
# rather than naming it is what makes the repository relocatable.
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _from_env(name: str, default: Path) -> Path:
    """An override if one is set, otherwise the default inside the repository."""
    value = os.environ.get(name)
    return Path(value).expanduser().resolve() if value else default


DATA_RAW = _from_env("WEEK0506_DATA_RAW", PROJECT_ROOT / "data" / "raw")
DATA_PROCESSED = _from_env("WEEK0506_DATA_PROCESSED", PROJECT_ROOT / "data" / "processed")
ARTIFACTS = _from_env("WEEK0506_ARTIFACTS", PROJECT_ROOT / "artifacts")
DOCS = PROJECT_ROOT / "docs"


def ensure_output_dirs() -> None:
    """Create the directories this project writes into, if they are missing.

    Call this before writing, so that a fresh clone does not fail on a folder
    that Git did not carry because it was empty.
    """
    for path in (DATA_PROCESSED, ARTIFACTS):
        path.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Useful when a path is not resolving to what you expected.
    for label, value in [("PROJECT_ROOT", PROJECT_ROOT), ("DATA_RAW", DATA_RAW),
                         ("DATA_PROCESSED", DATA_PROCESSED),
                         ("ARTIFACTS", ARTIFACTS), ("DOCS", DOCS)]:
        print("%-16s %s" % (label, value))
