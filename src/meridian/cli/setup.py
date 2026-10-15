# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
"""`meridian setup` — configure MCP clients and the knowledge base.

The cross-platform replacement for install.sh's bash client-configuration and
seeding logic. By the time this runs, `meridian` itself is already installed
(a `uv tool install`, a venv, or a `uvx` ephemeral env), so there is no venv
step here — only: knowledge base, optional example seeding, client config.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

from meridian.cli import _mcp_clients as mc

USAGE = """\
Usage: meridian setup [options]

Configure detected MCP clients (Claude Code, Kimi CLI, OpenCode, VSCode,
Cursor) to launch Meridian, create the knowledge base, and optionally seed it
with the bundled example rules. Safe to re-run: existing registrations and
knowledge-base files are never overwritten.

Options:
  -y, --yes      Configure every detected client without asking
  --seed         Seed the example knowledge base without asking
  --no-seed      Skip seeding without asking
  --rag          Register the semantic-search ('rag') variant when falling
                 back to uvx
  --no-clients   Skip MCP client configuration
  --dry-run      Show what would be done without changing anything
  -h, --help     Show this help

Environment:
  KNOWLEDGE_BASE_PATH  Knowledge base location (default: OS-specific)
"""


def _info(msg: str) -> None:
    print(f"[INFO] {msg}")


def _warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def _confirm(question: str, *, default: bool) -> bool:
    """Ask a yes/no question; non-interactive runs take the default."""
    if not sys.stdin.isatty():
        return default
    suffix = "[Y/n]" if default else "[y/N]"
    try:
        answer = input(f"{question} {suffix} ").strip().lower()
    except EOFError:
        return default
    if not answer:
        return default
    return answer in ("y", "yes", "s", "si", "sí")


# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------


def _kb_path_without_creating() -> Path:
    import os

    from meridian.config import _get_default_kb_path

    raw = os.environ.get("KNOWLEDGE_BASE_PATH")
    return Path(raw).resolve() if raw else _get_default_kb_path()


def _scope_for(sub: str, stem: str) -> str:
    # Mirrors _scope_to_file_path's convention: general.md is the "global"
    # scope itself; other global/*.md map to global-{name}; projects/*.md map
    # to project-{name}. Blocks declaring their own **Scope:** override this.
    if sub == "projects":
        return f"project-{stem}"
    if stem == "general":
        return "global"
    return f"global-{stem}"


def seed_examples(kb_path: Path, *, dry_run: bool = False) -> tuple[int, int]:
    """Copy and index the bundled example knowledge base into *kb_path*.

    Never overwrites: a destination file that already exists is skipped with
    a warning and not reindexed (the no-clobber guarantee from
    fix-installer-seed-overwrites-existing-kb). The source is package data
    read through importlib.resources, so this works the same from a clone, a
    `uv tool install`, or a `uvx` run with no repo on disk.

    Returns (seeded, skipped).
    """
    from meridian.tools.knowledge_management import (
        index_lessons_from_markdown,
        index_rules_from_markdown,
    )

    examples = files("meridian") / "examples"
    seeded = skipped = 0
    for src_dir, index_fn in (
        ("knowledge-base", index_rules_from_markdown),
        ("lessons", index_lessons_from_markdown),
    ):
        for sub in ("global", "projects"):
            source = examples / src_dir / sub
            if not source.is_dir():
                continue
            for item in sorted(source.iterdir(), key=lambda t: t.name):
                if not item.name.endswith(".md"):
                    continue
                dest = kb_path / src_dir / sub / item.name
                if dest.exists():
                    _warn(
                        f"Skipping {item.name} — {dest} already exists (not overwriting "
                        "your data). Remove or rename it first to reseed this example."
                    )
                    skipped += 1
                    continue
                scope = _scope_for(sub, item.name[: -len(".md")])
                if dry_run:
                    _info(f"[dry run] Would copy {item.name} -> {dest} and index it as {scope}")
                    seeded += 1
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(item.read_bytes())
                try:
                    result = index_fn(str(dest), default_scope_id=scope, mode="atomic")
                except Exception as exc:  # noqa: BLE001 — report, keep seeding the rest
                    _warn(f"Could not index {item.name} (scope {scope}): {exc}")
                    continue
                if result.get("errors"):
                    _warn(f"Indexed {item.name} with errors: {result['errors']}")
                else:
                    _info(f"Indexed {item.name} -> scope {scope}")
                seeded += 1
    return seeded, skipped


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------


def _configure_claude(command: list[str], env: dict[str, str], *, dry_run: bool) -> bool:
    claude = shutil.which("claude")
    if claude is None:
        return False
    add_argv = mc.claude_add_argv("claude", command, env)
    try:
        line = mc.claude_list_entry(claude)
    except (OSError, subprocess.SubprocessError) as exc:
        _warn(f"Could not run `claude mcp list` ({exc}). Add manually:")
        print(f"  {mc.format_command(add_argv)}")
        return False

    if line is not None:
        if mc.claude_line_matches(line, command):
            _info("Meridian already configured in Claude Code. Skipping.")
            return True
        _warn("Claude Code is configured against a different Meridian install:")
        print(f"  {line}")
        print("  To switch it to this one:")
        print(f"    claude mcp remove -s user {mc.SERVER_NAME}")
        print(f"    {mc.format_command(add_argv)}")
        return False

    if dry_run:
        _info(f"[dry run] Would run: {mc.format_command(add_argv)}")
        return True
    proc = subprocess.run(
        [claude, *add_argv[1:]], capture_output=True, text=True, timeout=120
    )
    if proc.returncode == 0:
        _info("Added to Claude Code")
        return True
    _warn("Could not add to Claude Code. Add manually:")
    print(f"  {mc.format_command(add_argv)}")
    return False


def _configure_json_client(
    client: mc.Client, command: list[str], env: dict[str, str], *, dry_run: bool
) -> bool:
    assert client.config_path is not None
    path = client.config_path
    snippet = mc.new_config(client.flavor, command, env)
    try:
        doc = mc.read_config(path)
    except mc.UnreadableConfig as exc:
        _warn(f"{path} isn't plain JSON ({exc}); not touching it. Add manually:")
        print(json.dumps(snippet, indent=2))
        return False

    existing = mc.configured_command(client, doc)
    if existing is not None:
        if mc.same_install(existing, command):
            _info(f"Meridian already configured in {client.label}. Skipping.")
            return True
        _warn(f"{client.label} ({path}) is configured against a different Meridian install:")
        print(f"  current: {mc.format_command(existing)}")
        print(f"  this install: {mc.format_command(command)}")
        print(f"  Edit the '{mc.SERVER_NAME}' entry in {path} to switch.")
        return False

    if dry_run:
        _info(f"[dry run] Would add Meridian to {path}")
        return True
    if doc is None:
        mc.write_config(path, snippet)
        _info(f"Created {client.label} config at {path}")
    else:
        backup = mc.write_config(path, mc.add_entry(client, doc, command, env))
        _info(f"Added Meridian to {path} (previous version saved as {backup})")
    return True


def configure_client(
    client: mc.Client, command: list[str], env: dict[str, str], *, dry_run: bool = False
) -> bool:
    if client.flavor == "claude-cli":
        return _configure_claude(command, env, dry_run=dry_run)
    return _configure_json_client(client, command, env, dry_run=dry_run)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run(argv: list[str]) -> int:
    if "-h" in argv or "--help" in argv:
        print(USAGE)
        return 0
    known = {"-y", "--yes", "--seed", "--no-seed", "--rag", "--no-clients", "--dry-run"}
    unknown = [a for a in argv if a not in known]
    if unknown:
        print(f"Unknown option(s): {' '.join(unknown)}\n")
        print(USAGE)
        return 2
    assume_yes = "-y" in argv or "--yes" in argv
    dry_run = "--dry-run" in argv
    rag = "--rag" in argv

    from meridian.rag.availability import rag_installed
    from meridian.utils.version_info import get_version_info

    print(f"Meridian setup — Axiom Meridian v{get_version_info()['version']}\n")

    # 1. Knowledge base
    if dry_run:
        kb_path = _kb_path_without_creating()
        _info(f"[dry run] Knowledge base: {kb_path}")
    else:
        from meridian.config import get_db_path, get_knowledge_base_path
        from meridian.db.connection import initialize_db

        kb_path = get_knowledge_base_path()  # creates the directory layout
        initialize_db(get_db_path())
        _info(f"Knowledge base: {kb_path}")

    # 2. Example seeding
    if "--seed" in argv:
        seed = True
    elif "--no-seed" in argv:
        seed = False
    else:
        seed = _confirm(
            "Copy and index the bundled example knowledge (Clean Code rules, Java sample)?",
            default=False,
        )
    if seed:
        seeded, skipped = seed_examples(kb_path, dry_run=dry_run)
        verb = "Would seed" if dry_run else "Seeded"
        _info(f"{verb} {seeded} example file(s), skipped {skipped} existing.")

    # 3. Command to register
    command = mc.resolve_server_command(rag=rag)
    env = mc.server_env(kb_path)
    if command[0] == "uvx":
        if shutil.which("uvx") is None:
            _warn("Registering a `uvx` command, but `uvx` isn't on PATH yet — install uv.")
    elif rag and not rag_installed():
        _warn(
            "--rag was given but this install lacks the 'rag' extra. Reinstall with: "
            'uv tool install --force "axiom-meridian[rag]"'
        )
    _info(f"Clients will launch: {mc.format_command(command)}")

    # 4. Clients
    configured: list[str] = []
    if "--no-clients" in argv:
        _info("Skipping MCP client configuration (--no-clients).")
    else:
        clients = mc.detect_clients()
        if not clients:
            _warn("No MCP clients detected. Install one and re-run `meridian setup`.")
        for client in clients:
            print()
            if not (assume_yes or _confirm(f"Configure {client.label}?", default=True)):
                _info(f"Skipped {client.label}.")
                continue
            if configure_client(client, command, env, dry_run=dry_run):
                configured.append(client.label)

    print("\n============================================")
    print("Setup complete" + (" (dry run — nothing changed)" if dry_run else ""))
    print("============================================")
    print(f"Knowledge base:     {kb_path}")
    print(f"Configured clients: {', '.join(configured) or 'none'}")
    print(f"Semantic search:    {'installed' if rag_installed() else 'not installed'}")
    print("\nManual configuration for other clients:")
    print(f"  Command: {mc.format_command(command)}")
    for key, value in env.items():
        print(f"  {key}={value}")
    print("\nRun `meridian doctor` any time to check the installation.")
    return 0
