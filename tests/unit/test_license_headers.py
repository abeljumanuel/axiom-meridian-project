"""Every Meridian source file carries the short SPDX license header
(change-license-to-apache-2, source-headers capability).

Scope: every *.py under src/meridian/, and *.sh / *.py directly under
scripts/. tests/ is deliberately out of scope.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

COPYRIGHT_LINE = "# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)"
LICENSE_LINE = "# SPDX-License-Identifier: Apache-2.0"
HEADER_WINDOW = 5  # lines inspected after an optional shebang


def _in_scope() -> list[Path]:
    files = sorted((ROOT / "src" / "meridian").rglob("*.py"))
    files += sorted((ROOT / "scripts").glob("*.sh"))
    files += sorted((ROOT / "scripts").glob("*.py"))
    return files


def _has_header(path: Path) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    if lines and lines[0].startswith("#!"):
        lines = lines[1:]
    head = [line.strip() for line in lines[:HEADER_WINDOW]]
    return COPYRIGHT_LINE in head and LICENSE_LINE in head


def test_scope_is_not_empty():
    assert len(_in_scope()) > 10


def test_every_source_file_has_spdx_header():
    missing = [p.relative_to(ROOT).as_posix() for p in _in_scope() if not _has_header(p)]
    assert not missing, (
        f"{len(missing)} file(s) lack the SPDX header:\n  "
        + "\n  ".join(missing)
        + "\n\nAdd these two lines at the top (after a shebang, if any):\n"
        + f"{COPYRIGHT_LINE}\n{LICENSE_LINE}\n"
    )
