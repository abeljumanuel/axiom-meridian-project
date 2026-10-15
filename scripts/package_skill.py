# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
"""Package the distributable skill as a zip (pure Python, works on Windows).

Usage: python scripts/package_skill.py [--out dist/meridian-skill.zip]

The archive holds a top-level `meridian/` folder mirroring
distribution/skill/meridian/. Entries are sorted with fixed timestamps so
the same sources always produce the same bytes. After writing, the archive
is extracted to a temporary directory and compared byte for byte against the
source tree; any mismatch fails the run. The zip is a build artifact — it is
not committed (dist/ is gitignored).
"""

from __future__ import annotations

import argparse
import sys
import tempfile
import zipfile
from pathlib import Path

SOURCE = Path("distribution/skill/meridian")
_FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def build(source: Path, out: Path) -> list[Path]:
    files = sorted(p for p in source.rglob("*") if p.is_file())
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            info = zipfile.ZipInfo(
                f"{source.name}/{path.relative_to(source).as_posix()}", _FIXED_TIME
            )
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    return files


def verify(source: Path, out: Path) -> list[str]:
    problems: list[str] = []
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(out) as archive:
        archive.extractall(tmp)
        extracted = Path(tmp) / source.name
        src_files = {p.relative_to(source) for p in source.rglob("*") if p.is_file()}
        zip_files = {p.relative_to(extracted) for p in extracted.rglob("*") if p.is_file()}
        for missing in sorted(src_files - zip_files):
            problems.append(f"missing from zip: {missing}")
        for extra in sorted(zip_files - src_files):
            problems.append(f"unexpected in zip: {extra}")
        for rel in sorted(src_files & zip_files):
            if (source / rel).read_bytes() != (extracted / rel).read_bytes():
                problems.append(f"content differs: {rel}")
    return problems


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--out", type=Path, default=Path("dist/meridian-skill.zip"))
    args = parser.parse_args(argv)

    files = build(args.source, args.out)
    problems = verify(args.source, args.out)
    for problem in problems:
        print(f"FAIL {problem}")
    if problems:
        return 1
    print(f"Wrote {args.out} ({len(files)} files, verified byte-for-byte against {args.source})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
