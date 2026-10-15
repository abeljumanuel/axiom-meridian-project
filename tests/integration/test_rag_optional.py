"""Integration tests: every RAG-touching path degrades cleanly without the
`rag` extra (rag-optional-dependency capability).

Absence is simulated by blocking the imports via sys.modules, so these run
with or without the extra actually installed; CI's no-RAG jobs also exercise
the real absence.
"""

from __future__ import annotations

import json
import logging
import sys

import pytest

from meridian import server
from meridian.db.connection import get_connection, initialize_db
from meridian.rag.vector_store import reset_client
from meridian.tools.knowledge_consumption import query_lessons, query_rules
from meridian.tools.knowledge_management import (
    approve_proposal,
    index_rules_from_markdown,
    promote_rule,
)

_RULES_MD = (
    "## RN-JAVA-001\n"
    "**Scope:** global-java\n"
    "**Categoría:** design\n"
    "**Severidad:** high\n"
    "**Tags:** dto, records\n"
    "**Regla:** Use immutable records for DTOs.\n"
    "\n"
    "## RN-JAVA-002\n"
    "**Scope:** global-java\n"
    "**Categoría:** testing\n"
    "**Severidad:** medium\n"
    "**Tags:** tests\n"
    "**Regla:** Every public method needs a unit test.\n"
)


@pytest.fixture
def no_rag(monkeypatch):
    for name in ("sentence_transformers", "torch", "chromadb"):
        monkeypatch.setitem(sys.modules, name, None)
    reset_client()
    yield
    reset_client()


@pytest.fixture
def tmp_kb(tmp_path, monkeypatch):
    kb_path = tmp_path / "kb"
    for sub in ("knowledge-base/global", "knowledge-base/projects", "lessons/global",
                "lessons/projects"):
        (kb_path / sub).mkdir(parents=True)
    monkeypatch.setenv("KNOWLEDGE_BASE_PATH", str(kb_path))
    monkeypatch.setenv("MERIDIAN_ACCESS_LEVEL", "write")

    from meridian.config import get_chroma_path, get_db_path

    # Make chromadb_available() get as far as importing chromadb, so the
    # fallback is exercised by the missing import, not a missing directory.
    get_chroma_path().mkdir(parents=True)

    db_path = get_db_path()
    initialize_db(db_path)
    conn = get_connection(db_path)

    rules_md = kb_path / "knowledge-base" / "global" / "java.md"
    rules_md.write_text(_RULES_MD)
    index_rules_from_markdown(str(rules_md), default_scope_id="global-java", mode="atomic")

    yield kb_path, conn
    conn.close()


@pytest.fixture
def server_conn(tmp_kb, monkeypatch):
    _, conn = tmp_kb
    monkeypatch.setattr(server, "conn", conn)
    monkeypatch.setattr(server, "current_transport", "stdio")
    return conn


def _errors(caplog) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.levelno >= logging.ERROR]


def test_generate_embeddings_returns_rag_not_installed(no_rag, server_conn, caplog):
    with caplog.at_level(logging.DEBUG):
        result = json.loads(server.generate_embeddings())

    assert result["error"] == "RAG_NOT_INSTALLED"
    assert 'pip install "axiom-meridian[rag]"' in result["message"]
    assert "processed" not in result
    assert _errors(caplog) == []

    status = server_conn.execute(
        "SELECT result FROM access_log WHERE tool_name = 'generate_embeddings' "
        "ORDER BY timestamp DESC LIMIT 1"
    ).fetchone()[0]
    assert status == "error"


def test_approve_new_proposal_without_rag_reports_embedded_null(no_rag, tmp_kb, caplog):
    kb_path, conn = tmp_kb
    (kb_path / "knowledge-base" / "global" / "quarkus.md").write_text("")
    conn.execute(
        "INSERT INTO pending_proposals "
        "(id, type, scope_id, proposed_text, metadata, source_type) "
        "VALUES ('prop-0001', 'rule', 'global-quarkus', 'A brand new rule.', ?, 'manual')",
        (json.dumps({"tags": ["x"]}),),
    )
    conn.commit()

    with caplog.at_level(logging.DEBUG):
        result = approve_proposal("prop-0001")

    assert result["embedded"] is None
    assert _errors(caplog) == []
    assert conn.execute(
        "SELECT COUNT(*) FROM rules WHERE code = ?", (result["code"],)
    ).fetchone()[0] == 1


def test_approve_deprecate_proposal_without_rag_reports_null(no_rag, tmp_kb, caplog):
    _, conn = tmp_kb
    conn.execute(
        "INSERT INTO pending_proposals "
        "(id, type, target_id, proposed_text, metadata, reason, status) "
        "VALUES ('prop-dep-001', 'deprecate', 'RN-JAVA-002', 'x', '{}', 'obsolete', 'pending')"
    )
    conn.commit()

    with caplog.at_level(logging.DEBUG):
        result = approve_proposal("prop-dep-001")

    assert result["status"] == "deprecated"
    assert result["embedding_removed"] is None
    assert _errors(caplog) == []


def test_promote_rule_without_rag_reports_null(no_rag, tmp_kb, caplog):
    _, conn = tmp_kb
    with caplog.at_level(logging.DEBUG):
        result = promote_rule("RN-JAVA-001", "global-quarkus")

    assert result["status"] == "deprecated"
    assert result["embedding_removed"] is None
    assert _errors(caplog) == []


@pytest.mark.parametrize("query_fn", [query_rules, query_lessons])
def test_semantic_query_without_rag_falls_back_to_sql(no_rag, tmp_kb, query_fn):
    semantic = json.loads(query_fn("project-example", query_text="immutable DTOs"))
    plain = json.loads(query_fn("project-example"))
    assert semantic == plain
    if query_fn is query_rules:
        assert plain, "fixture rules should be visible to project-example"
