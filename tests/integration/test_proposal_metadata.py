# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
"""create_pending_proposal: body vs. block-field metadata, and normalization of
rendered atomic blocks (openspec/changes/fix-proposal-metadata-and-scope-file)."""

from __future__ import annotations

import json

import pytest

from meridian import server
from meridian.db.connection import get_connection, initialize_db
from meridian.tools.extraction import create_pending_proposal


@pytest.fixture
def conn(tmp_path, monkeypatch):
    kb_path = tmp_path / "kb"
    for sub in ("knowledge-base/global", "knowledge-base/projects",
                "lessons/global", "lessons/projects"):
        (kb_path / sub).mkdir(parents=True)
    monkeypatch.setenv("KNOWLEDGE_BASE_PATH", str(kb_path))

    from meridian.config import get_db_path

    db_path = get_db_path()
    initialize_db(db_path)
    connection = get_connection(db_path)
    yield connection
    connection.close()


def _stored(conn, prop_id: str) -> tuple[str, dict]:
    text, metadata = conn.execute(
        "SELECT proposed_text, metadata FROM pending_proposals WHERE id = ?", (prop_id,)
    ).fetchone()
    return text, json.loads(metadata) if metadata else {}


def _block(scope: str = "global-java", severity: str = "low", body: str = "Validate tokens.") -> str:
    return (
        f"## RN-XXX-NNN\n**Scope:** {scope}\n**Categoría:** security\n"
        f"**Severidad:** {severity}\n**Tags:** auth, jwt\n**Regla:** {body}"
    )


def test_metadata_is_stored_and_body_kept_as_is(conn):
    prop_id = create_pending_proposal(
        conn, "rule", "Pin every dependency.", "global-java",
        metadata={"category": "dependencies", "severity": "high", "tags": "deps, supply-chain"},
    )
    text, metadata = _stored(conn, prop_id)
    assert text == "Pin every dependency."
    assert metadata == {
        "category": "dependencies",
        "severity": "high",
        "tags": ["deps", "supply-chain"],
    }


def test_unknown_metadata_key_is_rejected(conn):
    with pytest.raises(ValueError, match="Allowed keys"):
        create_pending_proposal(
            conn, "rule", "Text.", "global-java", metadata={"categoria": "security"}
        )
    assert conn.execute("SELECT COUNT(*) FROM pending_proposals").fetchone()[0] == 0


def test_lesson_keys_are_not_valid_for_a_rule(conn):
    with pytest.raises(ValueError, match="root_cause"):
        create_pending_proposal(
            conn, "rule", "Text.", "global-java", metadata={"root_cause": "x"}
        )


def test_invalid_severity_is_rejected(conn):
    with pytest.raises(ValueError, match="Invalid severity"):
        create_pending_proposal(
            conn, "rule", "Text.", "global-java", metadata={"severity": "urgent"}
        )


def test_private_tags_are_stripped_from_metadata(conn):
    prop_id = create_pending_proposal(
        conn, "rule", "Text.", "global-java",
        metadata={"source": "PR <private>internal-link</private>"},
    )
    _, metadata = _stored(conn, prop_id)
    assert "internal-link" not in metadata["source"]


def test_rendered_block_is_split_into_body_and_metadata(conn):
    prop_id = create_pending_proposal(conn, "rule", _block(), "global-java")
    text, metadata = _stored(conn, prop_id)
    assert text == "Validate tokens."
    assert metadata == {"category": "security", "severity": "low", "tags": ["auth", "jwt"]}


def test_explicit_metadata_overrides_parsed_fields(conn):
    prop_id = create_pending_proposal(
        conn, "rule", _block(severity="low"), "global-java", metadata={"severity": "high"}
    )
    _, metadata = _stored(conn, prop_id)
    assert metadata["severity"] == "high"


def test_block_scope_contradicting_requested_scope_is_rejected(conn):
    with pytest.raises(ValueError, match="global-python"):
        create_pending_proposal(conn, "rule", _block(scope="global-python"), "global-java")
    assert conn.execute("SELECT COUNT(*) FROM pending_proposals").fetchone()[0] == 0


def test_rendered_block_without_body_is_rejected(conn):
    with pytest.raises(ValueError, match="Regla"):
        create_pending_proposal(
            conn, "rule", "## RN-XXX-NNN\n**Scope:** global-java\n**Severidad:** low",
            "global-java",
        )


def test_lesson_block_sent_as_rule_is_rejected(conn):
    with pytest.raises(ValueError, match="lesson block"):
        create_pending_proposal(
            conn, "rule", "## LL-XXX-NNN\n**Qué pasó:** Something.", "global-java"
        )


def test_update_block_scope_is_checked_against_the_target(conn):
    conn.execute(
        "INSERT INTO rules (id, scope_id, code, text, category, severity) "
        "VALUES ('RN-JAVA-001', 'global-java', 'RN-JAVA-001', 'Old.', 'general', 'medium')"
    )
    conn.commit()
    with pytest.raises(ValueError, match="does not match"):
        create_pending_proposal(
            conn, "update", _block(scope="global"), "global", target_id="RN-JAVA-001"
        )
    prop_id = create_pending_proposal(
        conn, "update", _block(scope="global-java"), "global", target_id="RN-JAVA-001"
    )
    assert _stored(conn, prop_id)[0] == "Validate tokens."


@pytest.fixture
def server_conn(conn, monkeypatch):
    monkeypatch.setenv("MERIDIAN_ACCESS_LEVEL", "analyze")
    old_conn, old_transport = server.conn, server.current_transport
    server.conn, server.current_transport = conn, "stdio"
    yield conn
    server.conn, server.current_transport = old_conn, old_transport


def test_mcp_tool_accepts_metadata_json(server_conn):
    prop_id = server.create_pending_proposal(
        type="rule",
        proposed_text="Pin every dependency.",
        suggested_scope_id="global-java",
        metadata=json.dumps({"category": "dependencies", "severity": "high"}),
    )
    _, metadata = _stored(server_conn, prop_id)
    assert metadata == {"category": "dependencies", "severity": "high"}


def test_mcp_tool_rejects_non_object_metadata(server_conn):
    with pytest.raises(ValueError, match="JSON object"):
        server.create_pending_proposal(
            type="rule",
            proposed_text="Text.",
            suggested_scope_id="global-java",
            metadata=json.dumps(["security"]),
        )
