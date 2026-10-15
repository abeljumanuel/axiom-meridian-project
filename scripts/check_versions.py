# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
"""Distribution consistency check (run in CI).

Usage: python scripts/check_versions.py

1. Version sync — `src/meridian/__init__.py`'s `__version__` is the single
   source (pyproject.toml reads it dynamically); the Claude Code plugin
   manifest, the marketplace entry, and server.json (`version` and
   `packages[0].version`) must all match it.
2. Skill copy — the plugin's `skills/meridian/` must be byte-identical to
   `distribution/skill/meridian/` (duplicated on purpose instead of
   symlinked; see design.md D5).

Exits non-zero naming every mismatched file.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "src" / "meridian" / "__init__.py"
SKILL = ROOT / "distribution" / "skill" / "meridian"
PLUGIN = ROOT / "distribution" / "plugin" / "meridian"


def source_version(init: Path = INIT) -> str:
    match = re.search(r'^__version__ = "([^"]+)"$', init.read_text(encoding="utf-8"), re.M)
    if not match:
        raise SystemExit(f"FAIL {init}: no __version__ found")
    return match.group(1)


def manifest_versions(root: Path = ROOT) -> list[tuple[str, str | None]]:
    """(label, version) for every place that must match __version__."""
    def load(rel: str) -> dict:
        return json.loads((root / rel).read_text(encoding="utf-8"))

    plugin = load("distribution/plugin/meridian/.claude-plugin/plugin.json")
    marketplace = load(".claude-plugin/marketplace.json")
    server = load("server.json")
    entry = next((p for p in marketplace.get("plugins", []) if p.get("name") == "meridian"), {})
    packages = server.get("packages") or [{}]
    return [
        ("distribution/plugin/meridian/.claude-plugin/plugin.json version", plugin.get("version")),
        (".claude-plugin/marketplace.json plugins[meridian].version", entry.get("version")),
        ("server.json version", server.get("version")),
        ("server.json packages[0].version", packages[0].get("version")),
    ]


def skill_copy_problems(skill: Path = SKILL, plugin: Path = PLUGIN) -> list[str]:
    copy = plugin / "skills" / skill.name
    src = {p.relative_to(skill) for p in skill.rglob("*") if p.is_file()}
    dst = {p.relative_to(copy) for p in copy.rglob("*") if p.is_file()} if copy.is_dir() else set()
    problems = [f"{copy / rel} is missing (present in {skill})" for rel in sorted(src - dst)]
    problems += [f"{copy / rel} has no counterpart in {skill}" for rel in sorted(dst - src)]
    problems += [
        f"{copy / rel} differs from {skill / rel}"
        for rel in sorted(src & dst)
        if (skill / rel).read_bytes() != (copy / rel).read_bytes()
    ]
    return problems


def main() -> int:
    expected = source_version()
    problems = [
        f"{label} is {found!r}, expected {expected!r} (from src/meridian/__init__.py)"
        for label, found in manifest_versions()
        if found != expected
    ]
    problems += skill_copy_problems()
    for problem in problems:
        print(f"FAIL {problem}")
    if problems:
        print("\nFix: bump every version together; re-copy the skill with "
              "`cp -R distribution/skill/meridian distribution/plugin/meridian/skills/`.")
        return 1
    print(f"OK: all distribution manifests at {expected}; plugin skill copy identical.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
