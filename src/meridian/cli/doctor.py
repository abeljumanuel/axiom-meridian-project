# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
"""`meridian doctor` — read-only installation diagnostics.

Turns the failure modes the README's Troubleshooting section used to describe
in prose into checks: the command each MCP client is configured to launch
(exists, executable, not a stale `uv run`), a venv whose base interpreter
moved (the "Library not loaded: @rpath/libpython3.11.dylib" case), cloud-sync
venv corruption (duplicated `name 2.py` files, macOS-hidden `.pth` files that
Python silently skips), plus the running version and whether the optional
`rag` extra is installed. Exit status is non-zero if any check fails.
"""

from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from meridian.cli import _mcp_clients as mc

USAGE = """\
Usage: meridian doctor

Check the Meridian installation and every detected MCP client's configuration.
Read-only: never changes anything. Exits non-zero if a problem is found.
"""

OK, WARN, FAIL, INFO = "ok", "warn", "fail", "info"
_MARK = {OK: "✓", WARN: "!", FAIL: "✗", INFO: "·"}


@dataclass
class Check:
    status: str
    title: str
    detail: str = ""
    fix: str = ""


# Files a sync conflict duplicates: "module 2.py", "_foo 3.pth", "lib 2.so"...
_SYNC_DUPLICATE = re.compile(r" \d+\.(py|pth|so|pyd|dylib|dll)$")
_SCAN_LIMIT = 5


def _is_windows(platform: str) -> bool:
    return platform == "win32"


# ---------------------------------------------------------------------------
# Environment checks (paths injectable for tests)
# ---------------------------------------------------------------------------


def site_packages_dirs(venv_root: Path, platform: str = sys.platform) -> list[Path]:
    if _is_windows(platform):
        candidate = venv_root / "Lib" / "site-packages"
        return [candidate] if candidate.is_dir() else []
    return sorted(p for p in venv_root.glob("lib/python*/site-packages") if p.is_dir())


def check_sync_corruption(venv_root: Path, platform: str = sys.platform) -> list[Check]:
    """Duplicated files from a cloud-sync conflict, and hidden .pth files."""
    duplicates: list[Path] = []
    hidden_pth: list[Path] = []
    uf_hidden = getattr(stat, "UF_HIDDEN", 0)
    for site in site_packages_dirs(venv_root, platform):
        for entry in site.iterdir():
            if entry.suffix == ".pth" and uf_hidden:
                try:
                    if entry.stat().st_flags & uf_hidden:
                        hidden_pth.append(entry)
                except (OSError, AttributeError):
                    pass
        for dirpath, _dirnames, filenames in os.walk(site):
            for name in filenames:
                if _SYNC_DUPLICATE.search(name):
                    duplicates.append(Path(dirpath) / name)
            if len(duplicates) >= _SCAN_LIMIT:
                break

    checks: list[Check] = []
    if duplicates:
        shown = "\n".join(f"    {p}" for p in duplicates[:_SCAN_LIMIT])
        checks.append(
            Check(
                FAIL,
                f"Venv at {venv_root} looks corrupted by a cloud-sync conflict",
                f"Duplicated files found (e.g.):\n{shown}",
                "Recreate the venv (reinstall Meridian), and keep it outside "
                "iCloud Drive / OneDrive / Dropbox folders.",
            )
        )
    if hidden_pth:
        shown = "\n".join(f"    {p}" for p in hidden_pth)
        checks.append(
            Check(
                FAIL,
                f"Hidden .pth file(s) in {venv_root} — Python skips them",
                f"macOS 'hidden' flag set (typical of cloud-synced folders):\n{shown}",
                "chflags nohidden " + " ".join(f'"{p}"' for p in hidden_pth),
            )
        )
    return checks


def check_base_interpreter(venv_root: Path, platform: str = sys.platform) -> Check | None:
    """A venv whose base interpreter moved or was removed — the cause of
    "Library not loaded: @rpath/libpython3.11.dylib"."""
    cfg = venv_root / "pyvenv.cfg"
    if not cfg.is_file():
        return None
    home = None
    for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
        key, _, value = line.partition("=")
        if key.strip() == "home":
            home = value.strip()
    python = venv_root / ("Scripts/python.exe" if _is_windows(platform) else "bin/python")
    broken_link = python.is_symlink() and not python.exists()
    if (home and not Path(home).is_dir()) or broken_link:
        return Check(
            FAIL,
            f"Venv at {venv_root} points at a Python that no longer exists",
            f"pyvenv.cfg home = {home}" + (" (bin/python is a broken symlink)" if broken_link else ""),
            "Recreate the venv (reinstall Meridian). This is the "
            "'Library not loaded: @rpath/libpython3.11.dylib' error.",
        )
    return None


def venv_root_of(command_path: Path) -> Path | None:
    """The venv a `.../bin/meridian` (or `...\\Scripts\\meridian.exe`) lives in."""
    resolved = Path(os.path.realpath(command_path))
    root = resolved.parent.parent
    return root if (root / "pyvenv.cfg").is_file() else None


# ---------------------------------------------------------------------------
# Client checks
# ---------------------------------------------------------------------------


def check_configured_command(
    label: str, command: list[str], *, which=shutil.which, platform: str = sys.platform
) -> list[Check]:
    """Checks for the command one client is configured to launch."""
    exe = Path(command[0]).name.lower()
    shown = mc.format_command(command, platform)

    if exe in ("uv", "uv.exe") and "run" in command[1:]:
        return [
            Check(
                FAIL,
                f"{label} launches Meridian through `uv run`",
                f"Configured: {shown}\nMCP clients often can't resolve `uv run` "
                "(\"command not found\" / \"can't open file\" errors).",
                "Re-run `meridian setup` (after removing the old entry) so it registers "
                "the `meridian` binary or `uvx --from axiom-meridian meridian mcp`.",
            )
        ]
    if exe in ("uvx", "uvx.exe"):
        if which("uvx") is None and not Path(command[0]).is_file():
            return [
                Check(
                    FAIL,
                    f"{label} launches Meridian with uvx, but uvx isn't installed",
                    f"Configured: {shown}",
                    "Install uv: https://docs.astral.sh/uv/getting-started/installation/",
                )
            ]
        return [Check(OK, f"{label}: {shown}")]

    path = Path(command[0])
    if not path.is_absolute():
        resolved = which(command[0])
        if resolved is None:
            return [
                Check(
                    FAIL,
                    f"{label}'s configured command isn't on PATH",
                    f"Configured: {shown}",
                    "Reinstall (uv tool install axiom-meridian) or re-run `meridian setup`.",
                )
            ]
        path = Path(resolved)
    if not path.exists() or not (os.access(path, os.X_OK) or _is_windows(platform)):
        return [
            Check(
                FAIL,
                f"{label}'s configured Meridian binary is missing or not executable",
                f"Configured: {shown}",
                "Reinstall (uv tool install axiom-meridian) or re-run `meridian setup` "
                "to point it at a working install.",
            )
        ]

    checks = [Check(OK, f"{label}: {shown}")]
    root = venv_root_of(path)
    if root is not None:
        interpreter = check_base_interpreter(root, platform)
        if interpreter:
            checks.append(interpreter)
        checks.extend(check_sync_corruption(root, platform))
    return checks


def _client_commands(clients: list[mc.Client]) -> list[tuple[str, list[str] | None, Check | None]]:
    """(label, configured command or None, error check or None) per client."""
    out: list[tuple[str, list[str] | None, Check | None]] = []
    for client in clients:
        if client.flavor == "claude-cli":
            claude = shutil.which("claude")
            try:
                command = mc.claude_get_command(claude) if claude else None
            except (OSError, subprocess.SubprocessError) as exc:
                out.append((client.label, None, Check(WARN, f"Couldn't query Claude Code: {exc}")))
                continue
            out.append((client.label, command, None))
            continue
        assert client.config_path is not None
        try:
            doc = mc.read_config(client.config_path)
        except mc.UnreadableConfig as exc:
            out.append(
                (
                    client.label,
                    None,
                    Check(
                        WARN,
                        f"{client.label}: couldn't parse {client.config_path}",
                        str(exc),
                        "Check it manually (comments in VSCode's mcp.json are fine but "
                        "can't be checked here).",
                    ),
                )
            )
            continue
        out.append((client.label, mc.configured_command(client, doc), None))
    return out


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def collect_checks() -> list[Check]:
    from meridian.cli.setup import _kb_path_without_creating
    from meridian.rag.availability import INSTALL_HINT, rag_installed
    from meridian.utils.version_info import get_version_info

    info = get_version_info()
    version = f"v{info['version']}" + (f" (commit {info['commit']})" if info["commit"] else "")
    checks = [Check(INFO, f"Axiom Meridian {version}", f"Running from {sys.prefix}")]

    if rag_installed():
        checks.append(Check(INFO, "Semantic search ('rag' extra): installed"))
    else:
        checks.append(Check(INFO, "Semantic search ('rag' extra): not installed", INSTALL_HINT))

    kb = _kb_path_without_creating()
    missing = [d for d in ("knowledge-base", "lessons") if not (kb / d).is_dir()]
    if missing:
        checks.append(
            Check(
                WARN,
                f"Knowledge base at {kb} is missing {', '.join(missing)}/",
                fix="Run `meridian setup` to create it.",
            )
        )
    else:
        checks.append(Check(OK, f"Knowledge base: {kb}"))

    interpreter = check_base_interpreter(Path(sys.prefix))
    if interpreter:
        checks.append(interpreter)
    checks.extend(check_sync_corruption(Path(sys.prefix)))

    clients = mc.detect_clients()
    if not clients:
        checks.append(Check(WARN, "No MCP clients detected"))
    for label, command, error in _client_commands(clients):
        if error is not None:
            checks.append(error)
        elif command is None:
            checks.append(
                Check(INFO, f"{label}: Meridian not configured", fix="Run `meridian setup`.")
            )
        else:
            checks.extend(check_configured_command(label, command))
    return checks


def render(checks: list[Check]) -> str:
    lines = []
    for check in checks:
        lines.append(f"{_MARK[check.status]} {check.title}")
        for detail_line in check.detail.splitlines():
            lines.append(f"    {detail_line}")
        if check.fix:
            lines.append(f"    → {check.fix}")
    return "\n".join(lines)


def run(argv: list[str]) -> int:
    if "-h" in argv or "--help" in argv:
        print(USAGE)
        return 0
    if argv:
        print(f"Unknown option(s): {' '.join(argv)}\n")
        print(USAGE)
        return 2
    checks = collect_checks()
    print(render(checks))
    failures = sum(1 for c in checks if c.status == FAIL)
    print()
    print(f"{failures} problem(s) found." if failures else "No problems found.")
    return 1 if failures else 0
