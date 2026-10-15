# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
"""Marketplace safety scan for a distributable skill directory.

Usage: python scripts/check_skill_safety.py [skill_dir ...]
       (default: distribution/skill/meridian)

Fails (exit 1) on anything an automated marketplace review typically flags:
network-calling patterns, code reading environment variables, `$VARS` in
shell snippets, executable or non-text files, symlinks, and long
base64-looking blobs. Mentioning an environment variable *by name* in prose
is allowed — only code that reads the environment is flagged.
"""

from __future__ import annotations

import os
import re
import stat
import sys
from pathlib import Path

DEFAULT_DIRS = [Path("distribution/skill/meridian")]

NETWORK = re.compile(
    r"\b(curl|wget|requests|urllib|http\.client|socket|irm|iex|Invoke-WebRequest|Invoke-RestMethod)\b",
    re.IGNORECASE,
)
ENV_ACCESS = re.compile(r"os\.environ|\bgetenv\b|process\.env|\$env:", re.IGNORECASE)
SHELL_VAR = re.compile(r"\$\{?[A-Za-z_][A-Za-z0-9_]*")
BLOB = re.compile(r"[A-Za-z0-9+/]{80,}={0,2}")
FENCE = re.compile(r"^```(\S*)")
SHELL_LANGS = {"sh", "bash", "shell", "zsh", "console", "powershell", "ps1", "pwsh", "bat", "cmd"}
ALLOWED_SUFFIXES = {".md", ".txt"}


def _shell_lines(text: str) -> list[tuple[int, str]]:
    """Lines inside fenced shell code blocks of a Markdown file."""
    lines: list[tuple[int, str]] = []
    in_shell = in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        match = FENCE.match(line.strip())
        if match:
            if in_fence:
                in_fence = in_shell = False
            else:
                in_fence = True
                in_shell = match.group(1).lower() in SHELL_LANGS
            continue
        if in_shell:
            lines.append((number, line))
    return lines


def scan(root: Path) -> list[str]:
    problems: list[str] = []
    if not root.is_dir():
        return [f"{root}: not a directory"]
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root.parent)
        if path.is_symlink():
            problems.append(f"{rel}: symlink (marketplace packaging may reject or resolve it)")
            continue
        if path.is_dir():
            continue
        mode = path.stat().st_mode
        if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH) and os.name != "nt":
            problems.append(f"{rel}: executable file")
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            problems.append(f"{rel}: not a plain-text/Markdown file ({path.suffix or 'no suffix'})")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"{rel}: not UTF-8 text (binary content)")
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for pattern, what in ((NETWORK, "network-call pattern"),
                                  (ENV_ACCESS, "environment access"),
                                  (BLOB, "base64-like blob")):
                match = pattern.search(line)
                if match:
                    problems.append(f"{rel}:{number}: {what} {match.group(0)[:40]!r}")
        code_lines = (
            _shell_lines(text) if path.suffix.lower() == ".md"
            else list(enumerate(text.splitlines(), 1))
        )
        for number, line in code_lines:
            match = SHELL_VAR.search(line)
            if match:
                problems.append(f"{rel}:{number}: shell variable {match.group(0)!r} in a snippet")
    return problems


def main(argv: list[str]) -> int:
    roots = [Path(a) for a in argv] or DEFAULT_DIRS
    problems = [p for root in roots for p in scan(root)]
    for problem in problems:
        print(f"FAIL {problem}")
    if problems:
        print(f"\n{len(problems)} problem(s) found.")
        return 1
    print(f"OK: {', '.join(map(str, roots))} passed the skill safety scan.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
