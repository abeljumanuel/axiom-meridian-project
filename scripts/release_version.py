#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
"""Keep Axiom Meridian's version consistent everywhere it is declared.

Single source of truth: ``__version__`` in ``src/meridian/__init__.py``
(pyproject.toml reads it dynamically). The same version is mirrored in the
distribution manifests listed in ``VERSION_FILES`` below.

Usage:
    python3 scripts/release_version.py current
    python3 scripts/release_version.py check [VERSION] [--require-changelog]
    python3 scripts/release_version.py bump VERSION [--dry-run]

``bump`` rewrites every version declaration and moves the ``[Unreleased]``
section of CHANGELOG.md under a new ``[VERSION] - YYYY-MM-DD`` heading.
It never commits, tags or publishes. Standard library only.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INIT_FILE = ROOT / "src" / "meridian" / "__init__.py"
CHANGELOG = ROOT / "CHANGELOG.md"

# (path, how many "version" keys must carry the package version)
VERSION_FILES: list[tuple[Path, int]] = [
    (ROOT / "server.json", 2),
    (ROOT / ".claude-plugin" / "marketplace.json", 1),
    (ROOT / "distribution" / "plugin" / "meridian" / ".claude-plugin" / "plugin.json", 1),
]

# PEP 440 subset used by this project: 1.2.3, 1.2.3a1, 1.2.3b1, 1.2.3rc1
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+((a|b|rc)\d+)?$")
INIT_RE = re.compile(r'^__version__\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)
JSON_VERSION_RE = re.compile(r'("version"\s*:\s*")([^"]*)(")')

CHANGELOG_HEADER = """# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
"""


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def current_version() -> str:
    match = INIT_RE.search(INIT_FILE.read_text(encoding="utf-8"))
    if not match:
        sys.exit(f"Could not find __version__ in {_rel(INIT_FILE)}")
    return match.group(1)


def _json_versions(path: Path) -> list[str]:
    return [m.group(2) for m in JSON_VERSION_RE.finditer(path.read_text(encoding="utf-8"))]


def _changelog_has(version: str) -> bool:
    if not CHANGELOG.exists():
        return False
    pattern = rf"^## \[{re.escape(version)}\]"
    return re.search(pattern, CHANGELOG.read_text(encoding="utf-8"), re.MULTILINE) is not None


def find_problems(expected: str | None, require_changelog: bool) -> list[str]:
    problems: list[str] = []
    version = current_version()
    if expected is not None and expected != version:
        problems.append(f"{_rel(INIT_FILE)} has __version__ = {version!r}, expected {expected!r}")
    target = expected or version
    if not VERSION_RE.match(target):
        problems.append(f"{target!r} is not a valid version (expected X.Y.Z, X.Y.ZaN, X.Y.ZbN or X.Y.ZrcN)")
    for path, count in VERSION_FILES:
        if not path.exists():
            problems.append(f"{_rel(path)} is missing")
            continue
        found = _json_versions(path)
        if len(found) != count:
            problems.append(f"{_rel(path)}: expected {count} \"version\" key(s), found {len(found)}")
        mismatched = [v for v in found if v != target]
        if mismatched:
            problems.append(f"{_rel(path)}: version(s) {mismatched} do not match {target!r}")
    if require_changelog and not _changelog_has(target):
        problems.append(f"CHANGELOG.md has no '## [{target}]' section")
    return problems


def cmd_check(args: argparse.Namespace) -> int:
    problems = find_problems(args.version, args.require_changelog)
    if problems:
        print("Version check failed:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"OK: every declaration is at {args.version or current_version()}")
    return 0


def _update_changelog(new: str, today: str, dry_run: bool) -> str:
    text = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else CHANGELOG_HEADER
    if _changelog_has(new):
        return "CHANGELOG.md already has this version (left unchanged)"
    marker = re.search(r"^## \[Unreleased\][^\n]*\n", text, re.MULTILINE)
    if not marker:
        return "CHANGELOG.md has no '## [Unreleased]' section (left unchanged — add one)"
    after = text[marker.end():]
    next_heading = re.search(r"^## \[", after, re.MULTILINE)
    body = after[: next_heading.start()] if next_heading else after
    rest = after[next_heading.start():] if next_heading else ""
    note = "" if body.strip() else " (WARNING: [Unreleased] was empty — write the release notes)"
    section = f"## [{new}] - {today}\n{body.rstrip()}\n\n" if body.strip() else f"## [{new}] - {today}\n\n"
    updated = text[: marker.end()] + "\n" + section + rest
    if not dry_run:
        CHANGELOG.write_text(updated.rstrip() + "\n", encoding="utf-8")
    return f"CHANGELOG.md: moved [Unreleased] under [{new}] - {today}{note}"


def cmd_bump(args: argparse.Namespace) -> int:
    new = args.version
    if not VERSION_RE.match(new):
        print(f"{new!r} is not a valid version (X.Y.Z, X.Y.ZaN, X.Y.ZbN, X.Y.ZrcN)", file=sys.stderr)
        return 1
    old = current_version()
    if new == old:
        print(f"Already at {old}; nothing to bump.", file=sys.stderr)
        return 1

    # Refuse to start from an inconsistent state: fix that first.
    problems = find_problems(None, require_changelog=False)
    if problems:
        print("Version declarations are already inconsistent; fix them first:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    changes: list[str] = []
    init_text = INIT_FILE.read_text(encoding="utf-8")
    new_init = INIT_RE.sub(f'__version__ = "{new}"', init_text, count=1)
    changes.append(f"{_rel(INIT_FILE)}: {old} -> {new}")
    pending = [(INIT_FILE, new_init)]

    for path, count in VERSION_FILES:
        text = path.read_text(encoding="utf-8")
        new_text, n = JSON_VERSION_RE.subn(lambda m: f"{m.group(1)}{new}{m.group(3)}", text)
        if n != count:
            print(f"{_rel(path)}: expected {count} version key(s), found {n}", file=sys.stderr)
            return 1
        pending.append((path, new_text))
        changes.append(f"{_rel(path)}: {old} -> {new} ({n} key(s))")

    today = _dt.date.today().isoformat()
    if not args.dry_run:
        for path, text in pending:
            path.write_text(text, encoding="utf-8")
    changes.append(_update_changelog(new, today, args.dry_run))

    prefix = "[dry run] " if args.dry_run else ""
    for change in changes:
        print(f"{prefix}{change}")
    if not args.dry_run:
        print(f"\nNext: review CHANGELOG.md, commit 'chore(release): v{new}', then tag v{new}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("current", help="print the current version")

    check = sub.add_parser("check", help="verify every declaration matches")
    check.add_argument("version", nargs="?", help="expected version (default: __version__)")
    check.add_argument("--require-changelog", action="store_true",
                       help="also require a CHANGELOG.md section for the version")

    bump = sub.add_parser("bump", help="set a new version everywhere")
    bump.add_argument("version", help="new version, e.g. 0.2.0 or 0.2.0rc1")
    bump.add_argument("--dry-run", action="store_true", help="show the changes without writing")

    args = parser.parse_args()
    if args.command == "current":
        print(current_version())
        return 0
    if args.command == "check":
        return cmd_check(args)
    return cmd_bump(args)


if __name__ == "__main__":
    sys.exit(main())
