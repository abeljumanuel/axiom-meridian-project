# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
"""MCP client detection, registration-command resolution and config I/O,
shared by `meridian setup` and `meridian doctor`.

Cross-platform by construction: only shutil.which, pathlib and json — never a
shell. Everything that depends on the host (PATH lookup, home directory,
sys.platform, sys.prefix, subprocess) is injectable so tests can simulate any
OS without running on it.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

SERVER_NAME = "meridian"
PACKAGE = "axiom-meridian"

Which = Callable[[str], str | None]


@dataclass(frozen=True)
class Client:
    """An MCP client Meridian knows how to configure.

    flavor selects the config shape:
      - "claude-cli": managed through `claude mcp ...`, no file of ours
      - "mcpServers": {"mcpServers": {name: {command, args, env}}} (Kimi CLI, Cursor)
      - "vscode":     {"servers": {name: {type: stdio, command, args, env}}}
      - "opencode":   {"mcp": {name: {type: local, command: [...], environment}}}
    """

    key: str
    label: str
    flavor: str
    config_path: Path | None = None


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def _config_home(home: Path, platform: str) -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg and platform not in ("win32", "darwin"):
        return Path(xdg)
    return home / ".config"


def _appdata(home: Path) -> Path:
    raw = os.environ.get("APPDATA")
    return Path(raw) if raw else home / "AppData" / "Roaming"


def vscode_user_dir(home: Path, platform: str) -> Path:
    if platform == "darwin":
        return home / "Library" / "Application Support" / "Code" / "User"
    if platform == "win32":
        return _appdata(home) / "Code" / "User"
    return _config_home(home, platform) / "Code" / "User"


def detect_clients(
    *,
    which: Which = shutil.which,
    home: Path | None = None,
    platform: str = sys.platform,
) -> list[Client]:
    """Return the MCP clients present on this machine, in a stable order."""
    home = home if home is not None else Path.home()
    found: list[Client] = []

    if which("claude"):
        found.append(Client("claude-code", "Claude Code", "claude-cli"))
    if which("kimi"):
        found.append(Client("kimi-cli", "Kimi CLI", "mcpServers", home / ".kimi" / "mcp.json"))
    if which("opencode"):
        found.append(
            Client(
                "opencode",
                "OpenCode",
                "opencode",
                _config_home(home, platform) / "opencode" / "opencode.json",
            )
        )
    vscode_dir = vscode_user_dir(home, platform)
    if which("code") or vscode_dir.parent.is_dir() or (home / ".vscode").is_dir():
        found.append(Client("vscode", "VSCode", "vscode", vscode_dir / "mcp.json"))
    if which("cursor") or (home / ".cursor").is_dir():
        found.append(Client("cursor", "Cursor", "mcpServers", home / ".cursor" / "mcp.json"))
    return found


# ---------------------------------------------------------------------------
# What command to register
# ---------------------------------------------------------------------------


def uv_cache_dirs(home: Path | None = None, platform: str = sys.platform) -> list[Path]:
    home = home if home is not None else Path.home()
    dirs: list[Path] = []
    if os.environ.get("UV_CACHE_DIR"):
        dirs.append(Path(os.environ["UV_CACHE_DIR"]))
    if platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        dirs.append((Path(local) if local else home / "AppData" / "Local") / "uv" / "cache")
    else:
        xdg = os.environ.get("XDG_CACHE_HOME")
        dirs.append((Path(xdg) if xdg else home / ".cache") / "uv")
    return dirs


def is_in_uv_cache(path: Path, cache_dirs: list[Path]) -> bool:
    """True if *path* lives inside uv's cache (e.g. a `uvx` ephemeral env),
    which `uv cache clean`/prune can delete at any time."""
    resolved = Path(os.path.realpath(path))
    if "archive-v0" in resolved.parts:  # uv's layout for cached tool envs
        return True
    for cache in cache_dirs:
        try:
            resolved.relative_to(Path(os.path.realpath(cache)))
            return True
        except ValueError:
            continue
    return False


def uvx_command(rag: bool) -> list[str]:
    source = f"{PACKAGE}[rag]" if rag else PACKAGE
    return ["uvx", "--from", source, SERVER_NAME, "mcp"]


def resolve_server_command(
    *,
    rag: bool = False,
    which: Which = shutil.which,
    prefix: str = sys.prefix,
    platform: str = sys.platform,
    cache_dirs: list[Path] | None = None,
) -> list[str]:
    """The command every client should launch.

    The persistent install running this code wins (it's the one being
    configured — e.g. what install.sh just `uv tool install`ed), spelled as
    its PATH entry when that resolves to the same file (uv tool's bin/
    symlink). Failing that, a persistent `meridian` on PATH. Otherwise
    `uvx --from axiom-meridian ...`. Never a path inside uv's cache: an
    ephemeral `uvx` env disappears on `uv cache clean`, silently breaking
    every client registered against it.
    """
    cache_dirs = cache_dirs if cache_dirs is not None else uv_cache_dirs(platform=platform)
    exe = "meridian.exe" if platform == "win32" else "meridian"
    bindir = "Scripts" if platform == "win32" else "bin"

    def persistent(path: Path) -> bool:
        return path.exists() and not is_in_uv_cache(path, cache_dirs)

    running = Path(prefix) / bindir / exe
    on_path = Path(found) if (found := which(SERVER_NAME)) else None

    if persistent(running):
        if on_path is not None and os.path.realpath(on_path) == os.path.realpath(running):
            return [str(Path(os.path.abspath(on_path))), "mcp"]
        return [str(Path(os.path.abspath(running))), "mcp"]
    if on_path is not None and persistent(on_path):
        return [str(Path(os.path.abspath(on_path))), "mcp"]
    return uvx_command(rag)


def server_env(kb_path: Path) -> dict[str, str]:
    return {"KNOWLEDGE_BASE_PATH": str(kb_path), "MERIDIAN_ACCESS_LEVEL": "write"}


def same_install(configured: list[str], desired: list[str]) -> bool:
    """Whether an existing registration already points at this install.

    For a binary path, the bin/ directory is what identifies the install — an
    existing entry may invoke `python -m meridian mcp` from the same venv
    instead of the `meridian` entry point (same leniency as install.sh's
    old $BIN_DIR match). For `uvx`, the full invocation must match (the
    `[rag]` variant is a different install).
    """
    if not configured:
        return False
    if desired[0] == "uvx":
        return Path(configured[0]).name in ("uvx", "uvx.exe") and configured[1:] == desired[1:]
    return Path(configured[0]).parent == Path(desired[0]).parent


def format_command(argv: list[str], platform: str = sys.platform) -> str:
    if platform == "win32":
        return subprocess.list2cmdline(argv)
    return shlex.join(argv)


# ---------------------------------------------------------------------------
# JSON-config clients (Kimi CLI, OpenCode, VSCode, Cursor)
# ---------------------------------------------------------------------------

_TOP_KEY = {"mcpServers": "mcpServers", "vscode": "servers", "opencode": "mcp"}


def build_entry(flavor: str, command: list[str], env: dict[str, str]) -> dict:
    if flavor == "opencode":
        return {"type": "local", "command": command, "environment": env}
    entry = {"command": command[0], "args": command[1:], "env": env}
    if flavor == "vscode":
        return {"type": "stdio", **entry}
    return entry


def new_config(flavor: str, command: list[str], env: dict[str, str]) -> dict:
    doc: dict = {_TOP_KEY[flavor]: {SERVER_NAME: build_entry(flavor, command, env)}}
    if flavor == "opencode":
        doc = {"$schema": "https://opencode.ai/config.json", **doc}
        doc["permission"] = {"mcp": {SERVER_NAME: "ask"}}
    return doc


class UnreadableConfig(Exception):
    """The client's config file exists but isn't plain JSON (e.g. VSCode's
    JSONC with comments) — never rewritten, only reported."""


def read_config(path: Path) -> dict | None:
    """Parsed config, or None if the file doesn't exist."""
    if not path.exists():
        return None
    try:
        doc = json.loads(path.read_text(encoding="utf-8") or "{}")
    except (OSError, ValueError) as exc:
        raise UnreadableConfig(str(exc)) from exc
    if not isinstance(doc, dict):
        raise UnreadableConfig("top-level value is not a JSON object")
    return doc


def configured_command(client: Client, doc: dict | None) -> list[str] | None:
    """The command *doc* registers for Meridian, or None if it has no entry."""
    if doc is None:
        return None
    entry = (doc.get(_TOP_KEY[client.flavor]) or {}).get(SERVER_NAME)
    if not isinstance(entry, dict):
        return None
    command = entry.get("command")
    if isinstance(command, list):
        return [str(c) for c in command]
    if isinstance(command, str):
        return [command, *[str(a) for a in entry.get("args") or []]]
    return None


def add_entry(client: Client, doc: dict, command: list[str], env: dict[str, str]) -> dict:
    servers = doc.setdefault(_TOP_KEY[client.flavor], {})
    servers[SERVER_NAME] = build_entry(client.flavor, command, env)
    return doc


def write_config(path: Path, doc: dict) -> Path | None:
    """Write *doc*, backing up any existing file first. Returns the backup path."""
    backup = None
    if path.exists():
        backup = path.with_name(path.name + ".meridian-bak")
        shutil.copy2(path, backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return backup


# ---------------------------------------------------------------------------
# Claude Code (managed through its own CLI)
# ---------------------------------------------------------------------------

Runner = Callable[..., subprocess.CompletedProcess]


def claude_list_entry(claude: str, run: Runner | None = None) -> str | None:
    """The `meridian:` line of `claude mcp list`, or None if not registered.

    `claude mcp list` prints plain "name: command - status" lines, not JSON
    (matching a quoted '"meridian"' never hits — the bug
    fix-installer-claude-mcp-check-and-url fixed in the bash installer).
    """
    run = run or subprocess.run
    proc = run([claude, "mcp", "list"], capture_output=True, text=True, timeout=120)
    for line in (proc.stdout or "").splitlines():
        if line.startswith(f"{SERVER_NAME}:"):
            return line.strip()
    return None


def claude_line_matches(line: str, desired: list[str]) -> bool:
    if format_command(desired, "posix") in line or " ".join(desired) in line:
        return True
    if desired[0] != "uvx":
        return str(Path(desired[0]).parent) in line
    return False


def claude_get_command(claude: str, run: Runner | None = None) -> list[str] | None:
    """The command/args `claude mcp get meridian` reports, or None."""
    run = run or subprocess.run
    proc = run([claude, "mcp", "get", SERVER_NAME], capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        return None
    command: str | None = None
    args: list[str] = []
    for raw in (proc.stdout or "").splitlines():
        line = raw.strip()
        if line.startswith("Command:"):
            command = line.split(":", 1)[1].strip()
        elif line.startswith("Args:"):
            args = line.split(":", 1)[1].split()
    return [command, *args] if command else None


def claude_add_argv(claude: str, command: list[str], env: dict[str, str]) -> list[str]:
    argv = [claude, "mcp", "add", "-s", "user"]
    for key, value in env.items():
        argv += ["-e", f"{key}={value}"]
    return [*argv, "--", SERVER_NAME, *command]
