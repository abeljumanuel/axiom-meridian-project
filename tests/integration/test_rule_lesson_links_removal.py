"""Regression for TICKET-022: dropping the unused ``rule_lesson_links`` table
(migration 007) must leave existing records untouched and keep lesson
creation, update and import working on a database that went through it."""

from __future__ import annotations

import json
import sqlite3

import pytest

from meridian.config import get_db_path
from meridian.db.connection import get_connection, initialize_db
from meridian.tools import knowledge_management
from meridian.tools.extraction import create_pending_proposal
from meridian.tools.knowledge_consumption import (
    get_rule_context,
    get_rule_timeline,
    query_lessons,
    query_rules,
)
from meridian.tools.knowledge_management import approve_proposal

_RULE = (
    "## RN-GLOBAL-001\n\n**Scope:** global\n**Categoría:** security\n"
    "**Severidad:** high\n**Aplica a:** all\n**Tags:** manual\n**Fuente:** hand\n\n"
    "**Regla:** Hand written rule.\n\n---\n"
)
_LESSON = (
    "## {code}\n\n**Scope:** global\n**Severidad:** high\n**Tags:** manual\n"
    "**Originó regla:** RN-GLOBAL-001\n\n"
    "**Qué pasó:** Hand written lesson {code}.\n\n**Impacto:** x\n\n"
    "**Causa raíz:** y\n\n**Resolución:** z\n\n---\n"
)
_TABLES = ("rules", "lessons", "rule_history", "lesson_history", "rule_tags", "lesson_tags")


def _snapshot(conn: sqlite3.Connection) -> dict[str, list[tuple]]:
    return {
        t: conn.execute(f"SELECT * FROM {t} ORDER BY 1, 2").fetchall()
        for t in _TABLES
    }


@pytest.fixture
def pre_007_kb(tmp_path, monkeypatch):
    """A knowledge base populated at schema version 6, i.e. still carrying the
    ``rule_lesson_links`` table (with a row in it), before migration 007."""
    kb = tmp_path / "kb"
    for sub in ("knowledge-base/global", "knowledge-base/projects",
                "lessons/global", "lessons/projects"):
        (kb / sub).mkdir(parents=True)
    monkeypatch.setenv("KNOWLEDGE_BASE_PATH", str(kb))
    db_path = get_db_path()
    initialize_db(db_path)

    rules_md = kb / "hand-rules.md"
    rules_md.write_text(_RULE, encoding="utf-8")
    lessons_md = kb / "hand-lessons.md"
    lessons_md.write_text(_LESSON.format(code="LL-GLOBAL-001"), encoding="utf-8")
    assert knowledge_management.index_rules_from_markdown(str(rules_md), "global")["created"] == 1
    assert knowledge_management.index_lessons_from_markdown(str(lessons_md), "global")["created"] == 1

    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE rule_lesson_links (rule_id TEXT NOT NULL, lesson_id TEXT NOT NULL, "
        "link_type TEXT NOT NULL, PRIMARY KEY (rule_id, lesson_id))"
    )
    conn.execute(
        "INSERT INTO rule_lesson_links VALUES ('RN-GLOBAL-001', 'LL-GLOBAL-001', 'originated')"
    )
    conn.execute("PRAGMA user_version = 6")
    conn.commit()
    conn.close()
    return kb, db_path


def test_migration_007_leaves_existing_records_untouched(pre_007_kb):
    kb, db_path = pre_007_kb
    conn = get_connection(db_path)
    before = _snapshot(conn)
    files_before = {p: p.read_bytes() for p in kb.rglob("*.md")}
    conn.close()

    initialize_db(db_path)

    conn = get_connection(db_path)
    try:
        assert _snapshot(conn) == before
        assert before["rules"] and before["lessons"]
        assert not conn.execute(
            "SELECT 1 FROM sqlite_master WHERE name = 'rule_lesson_links'"
        ).fetchall()
        assert {p: p.read_bytes() for p in kb.rglob("*.md")} == files_before
        assert [r[0] for r in conn.execute("SELECT code FROM rules")] == ["RN-GLOBAL-001"]
    finally:
        conn.close()


def test_lessons_can_be_created_updated_and_imported_after_migration_007(pre_007_kb):
    kb, db_path = pre_007_kb
    initialize_db(db_path)  # applies migration 007
    conn = get_connection(db_path)
    try:
        # Create: a new lesson via proposal gets the next code, no collision.
        prop = create_pending_proposal(
            conn, "lesson", "Created after the migration.", "global",
            metadata={"severity": "high", "tags": ["logs"]},
        )
        conn.commit()
        assert approve_proposal(prop)["code"] == "LL-GLOBAL-002"

        # Update: rewrite the pre-existing lesson in place.
        upd = create_pending_proposal(
            conn, "update", "Updated old lesson.", "global", target_id="LL-GLOBAL-001"
        )
        conn.commit()
        approve_proposal(upd)
        assert conn.execute(
            "SELECT what_happened FROM lessons WHERE code = 'LL-GLOBAL-001'"
        ).fetchone()[0] == "Updated old lesson."
        assert "Updated old lesson." in (kb / "hand-lessons.md").read_text(encoding="utf-8")

        # Import: a hand-written lesson file is indexed and the next approval
        # does not reissue its code.
        imp = kb / "imported-lessons.md"
        imp.write_text(_LESSON.format(code="LL-GLOBAL-007"), encoding="utf-8")
        assert knowledge_management.index_lessons_from_markdown(str(imp), "global")["created"] == 1
        prop = create_pending_proposal(
            conn, "lesson", "After import.", "global", metadata={"severity": "low"}
        )
        conn.commit()
        assert approve_proposal(prop)["code"] == "LL-GLOBAL-008"

        codes = {r["code"] for r in json.loads(query_lessons("global"))}
        assert {"LL-GLOBAL-001", "LL-GLOBAL-002", "LL-GLOBAL-007", "LL-GLOBAL-008"} <= codes
        assert json.loads(query_rules("global"))

        # The rule-side readers keep working without the links table.
        assert get_rule_context("RN-GLOBAL-001", conn=conn)["rule"]["code"] == "RN-GLOBAL-001"
        assert get_rule_timeline("RN-GLOBAL-001", conn=conn)["rule_code"] == "RN-GLOBAL-001"
    finally:
        conn.close()
