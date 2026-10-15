"""Integration tests for `meridian setup`'s knowledge-base seeding and the
`setup`/`doctor` CLI wiring (cli-setup-and-doctor)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from meridian.cli import _mcp_clients as mc
from meridian.cli import setup as setup_cli
from meridian.config import get_db_path
from meridian.db.connection import get_connection, initialize_db


@pytest.fixture
def tmp_kb(tmp_path, monkeypatch):
    kb_path = tmp_path / "kb"
    for sub in ("knowledge-base/global", "knowledge-base/projects", "lessons/global",
                "lessons/projects"):
        (kb_path / sub).mkdir(parents=True)
    monkeypatch.setenv("KNOWLEDGE_BASE_PATH", str(kb_path))
    initialize_db(get_db_path())
    return kb_path


def _rule_count(scope_id: str) -> int:
    conn = get_connection(get_db_path())
    try:
        return conn.execute(
            "SELECT COUNT(*) FROM rules WHERE scope_id = ?", (scope_id,)
        ).fetchone()[0]
    finally:
        conn.close()


def test_seeding_into_empty_kb_copies_and_indexes(tmp_kb):
    seeded, skipped = setup_cli.seed_examples(tmp_kb)

    assert (seeded, skipped) == (2, 0)
    assert (tmp_kb / "knowledge-base" / "global" / "java.md").is_file()
    assert (tmp_kb / "knowledge-base" / "global" / "clean-code.md").is_file()
    assert _rule_count("global-java") == 3


def test_seeding_never_overwrites_existing_file(tmp_kb, capsys):
    mine = tmp_kb / "knowledge-base" / "global" / "java.md"
    mine.write_text("## my own notes, not a rule block\n", encoding="utf-8")

    seeded, skipped = setup_cli.seed_examples(tmp_kb)

    assert skipped == 1
    assert mine.read_text(encoding="utf-8") == "## my own notes, not a rule block\n"
    assert _rule_count("global-java") == 0  # not reindexed
    out = capsys.readouterr().out
    assert "Skipping java.md" in out and "already exists" in out


def test_dry_run_seeding_changes_nothing(tmp_kb):
    seeded, _ = setup_cli.seed_examples(tmp_kb, dry_run=True)
    assert seeded == 2
    assert not (tmp_kb / "knowledge-base" / "global" / "java.md").exists()


def test_setup_end_to_end_configures_detected_client(tmp_kb, tmp_path, monkeypatch):
    client = mc.Client("cursor", "Cursor", "mcpServers", tmp_path / "cursor" / "mcp.json")
    monkeypatch.setattr(mc, "detect_clients", lambda: [client])
    monkeypatch.setattr(mc, "resolve_server_command", lambda rag: ["/opt/bin/meridian", "mcp"])

    assert setup_cli.run(["--yes", "--no-seed"]) == 0
    doc = mc.read_config(client.config_path)
    assert mc.configured_command(client, doc) == ["/opt/bin/meridian", "mcp"]
    assert doc["mcpServers"]["meridian"]["env"]["KNOWLEDGE_BASE_PATH"] == str(tmp_kb)

    # Re-running is a no-op: already configured, file untouched.
    before = client.config_path.read_text(encoding="utf-8")
    assert setup_cli.run(["--yes", "--no-seed"]) == 0
    assert client.config_path.read_text(encoding="utf-8") == before


def test_unknown_option_is_rejected(capsys):
    assert setup_cli.run(["--bogus"]) == 2


@pytest.mark.parametrize("command", ["setup", "doctor"])
def test_cli_help_wiring(command):
    proc = subprocess.run(
        [sys.executable, "-m", "meridian", command, "--help"],
        capture_output=True, text=True, timeout=60,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[2] / "src")},
    )
    assert proc.returncode == 0
    assert f"Usage: meridian {command}" in proc.stdout
