# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
"""Canonical atomic-format templates for rules, lessons, and transcription flows.

This module is the single source of truth for the markdown templates the LLM
client uses when proposing new knowledge artifacts. It exposes:

  - Module-level constants: RULE_TEMPLATE, LESSON_TEMPLATE, TRANSCRIPTION_TEMPLATE
  - Builder functions:      build_rule_template_response,
                            build_lesson_template_response,
                            build_transcription_template_response

Templates are plain strings with `{placeholder}` markers so they can be embedded
verbatim in MCP responses (the client LLM fills the placeholders, not us).
"""

from __future__ import annotations

import sqlite3
from typing import Any

from meridian.utils.scope_resolver import resolve_scope_hierarchy

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

RULE_TEMPLATE: str = (
    "## RN-XXX-NNN\n"
    "**Scope:** {scope_id}\n"
    "**Categoría:** {category}\n"
    "**Severidad:** {severity}\n"
    "**Aplica a:** {applies_to}\n"
    "**Tags:** {tags}\n"
    "**Fuente:** {source}\n"
    "**Regla:** {text}"
)

LESSON_TEMPLATE: str = (
    "## LL-XXX-NNN\n"
    "**Scope:** {scope_id}\n"
    "**Proyecto:** {project}\n"
    "**Fecha:** {date}\n"
    "**Severidad del impacto:** {severity}\n"
    "**Área afectada:** {area}\n"
    "**Tags:** {tags}\n"
    "**Qué pasó:** {what_happened}\n"
    "**Impacto:** {impact}\n"
    "**Causa raíz:** {root_cause}\n"
    "**Resolución:** {resolution}\n"
    "**Originó regla:** {originated_rule}"
)

TRANSCRIPTION_TEMPLATE: str = (
    "# Transcript Processing Guide\n\n"
    "## Rule format:\n\n" + RULE_TEMPLATE + "\n\n"
    "## Lesson format:\n\n" + LESSON_TEMPLATE
)

# ---------------------------------------------------------------------------
# Private: Rule fields + usage
# ---------------------------------------------------------------------------

_RULE_FIELDS: list[dict[str, Any]] = [
    {
        "name": "scope_id",
        "required": True,
        "description": "Target scope identifier (e.g. 'project-project-example', 'global-java').",
    },
    {
        "name": "category",
        "required": True,
        "description": "Rule category (e.g. 'quality', 'security', 'architecture', 'logging').",
    },
    {
        "name": "severity",
        "required": True,
        "description": "Severity level: 'low', 'medium', 'high', or 'critical'.",
    },
    {
        "name": "applies_to",
        "required": False,
        "description": "Applicability condition or context where the rule must be followed.",
    },
    {
        "name": "tags",
        "required": False,
        "description": "Comma-separated tags for filtering and discovery.",
    },
    {
        "name": "source",
        "required": False,
        "description": "Where this rule comes from (source type and reference, e.g. 'transcript / meeting-2024-01-15').",
    },
    {
        "name": "text",
        "required": True,
        "description": "The rule text itself — concise, actionable, and in imperative form.",
    },
]

_RULE_USAGE: str = (
    "The template above is the Markdown file format: a block written into a "
    "knowledge .md file is persisted with index_rules_from_markdown. To queue a "
    "rule for human review instead, call create_pending_proposal with "
    "type='rule', proposed_text set to the rule text only (the **Regla:** value) "
    "and the other fields in metadata — the block is built on approval. "
    "Example: create_pending_proposal(type='rule', suggested_scope_id='global-java', "
    "proposed_text='Close JDBC resources with try-with-resources.', "
    "metadata='{\"category\": \"quality\", \"severity\": \"high\", "
    "\"applies_to\": \"**/*.java\", \"tags\": [\"jdbc\"], \"source\": \"manual\"}')."
)

# ---------------------------------------------------------------------------
# Private: Lesson fields + usage
# ---------------------------------------------------------------------------

_LESSON_FIELDS: list[dict[str, Any]] = [
    {
        "name": "scope_id",
        "required": True,
        "description": "Target scope identifier.",
    },
    {
        "name": "project",
        "required": False,
        "description": "Project name or identifier where the lesson occurred.",
    },
    {
        "name": "date",
        "required": False,
        "description": "Date the lesson was learned (ISO-8601 preferred, e.g. '2024-01-15').",
    },
    {
        "name": "severity",
        "required": False,
        "description": "Impact severity level: 'low', 'medium', 'high', or 'critical'.",
    },
    {
        "name": "area",
        "required": False,
        "description": "Area affected (e.g. 'deployment', 'performance', 'security', 'architecture').",
    },
    {
        "name": "tags",
        "required": False,
        "description": "Comma-separated tags for filtering and discovery.",
    },
    {
        "name": "what_happened",
        "required": False,
        "description": "Concise description of what went wrong or was discovered.",
    },
    {
        "name": "impact",
        "required": False,
        "description": "Business or technical impact of the event.",
    },
    {
        "name": "root_cause",
        "required": False,
        "description": "Root cause analysis — why the event happened.",
    },
    {
        "name": "resolution",
        "required": False,
        "description": "How the issue was resolved or the lesson applied.",
    },
    {
        "name": "originated_rule",
        "required": False,
        "description": "Rule ID that originated from this lesson, if any (e.g. 'RN-JAVA-042').",
    },
]

_LESSON_USAGE: str = (
    "The template above is the Markdown file format: a block written into a "
    "lessons .md file is persisted with index_lessons_from_markdown. To queue a "
    "lesson for human review instead, call create_pending_proposal with "
    "type='lesson', proposed_text set to what happened only (the **Qué pasó:** "
    "value) and the other fields in metadata — the block is built on approval. "
    "Example: create_pending_proposal(type='lesson', suggested_scope_id='project-x', "
    "proposed_text='The cache served stale prices for 2 hours.', "
    "metadata='{\"severity\": \"high\", \"area_affected\": \"billing\", "
    "\"impact\": \"Wrong invoices.\", \"root_cause\": \"TTL too long.\", "
    "\"resolution\": \"Shorter TTL.\", \"tags\": [\"cache\"]}')."
)

# ---------------------------------------------------------------------------
# Private: Transcription fields + usage
# ---------------------------------------------------------------------------

_TRANSCRIPTION_FIELDS: list[dict[str, Any]] = [
    {
        "name": "text",
        "required": True,
        "description": (
            "Raw transcript text. Private tags (e.g. [[PRIVATE]]...[[/PRIVATE]]) "
            "will be stripped automatically."
        ),
    },
    {
        "name": "project_id",
        "required": True,
        "description": (
            "Project identifier. Determines scope hierarchy and existing knowledge "
            "for deduplication."
        ),
    },
]

_TRANSCRIPTION_USAGE: str = (
    "Workflow: "
    "(1) Call extract_rules_from_transcript or extract_lessons_from_transcript "
    "with 'text' and 'project_id'. "
    "The tool returns clean_text, scopes, existing knowledge for deduplication, "
    "and the canonical atomic template. "
    "(2) Analyze the transcript and identify rule and lesson candidates. "
    "(3) For each candidate, call create_pending_proposal with type='rule' or "
    "type='lesson', proposed_text set to the body only (the rule text, or what "
    "happened) and the other block fields in metadata (see the usage of "
    "get_rule_template / get_lesson_template for the keys). "
    "Proposals are queued for human review and do NOT immediately persist a rule "
    "or lesson — a human must approve each proposal before it becomes active."
)

# ---------------------------------------------------------------------------
# Private: scope suggestions helper
# ---------------------------------------------------------------------------


def _build_scope_suggestions(
    conn: sqlite3.Connection,
    project_id: str,
) -> list[dict[str, Any]]:
    """Return scope suggestions list; never raises.

    On success: list of {"scope_id": str, "recommended": bool}
    On ValueError: [{"error": "<message from ValueError>"}]
    """
    try:
        chain = resolve_scope_hierarchy(conn, project_id)
    except ValueError as exc:
        return [{"error": str(exc)}]

    return [{"scope_id": scope_id, "recommended": i == 0} for i, scope_id in enumerate(chain)]


# ---------------------------------------------------------------------------
# Public builders
# ---------------------------------------------------------------------------


def build_rule_template_response(
    project_id: str | None,
    conn: sqlite3.Connection,
) -> dict[str, Any]:
    """Build the response dict for get_rule_template."""
    response: dict[str, Any] = {
        "template": RULE_TEMPLATE,
        "fields": _RULE_FIELDS,
        "usage": _RULE_USAGE,
    }
    if project_id is not None:
        response["scope_suggestions"] = _build_scope_suggestions(conn, project_id)
    return response


def build_lesson_template_response(
    project_id: str | None,
    conn: sqlite3.Connection,
) -> dict[str, Any]:
    """Build the response dict for get_lesson_template."""
    response: dict[str, Any] = {
        "template": LESSON_TEMPLATE,
        "fields": _LESSON_FIELDS,
        "usage": _LESSON_USAGE,
    }
    if project_id is not None:
        response["scope_suggestions"] = _build_scope_suggestions(conn, project_id)
    return response


def build_transcription_template_response(
    project_id: str | None,
    conn: sqlite3.Connection,
) -> dict[str, Any]:
    """Build the response dict for get_transcription_template."""
    response: dict[str, Any] = {
        "template": TRANSCRIPTION_TEMPLATE,
        "fields": _TRANSCRIPTION_FIELDS,
        "usage": _TRANSCRIPTION_USAGE,
    }
    if project_id is not None:
        response["scope_suggestions"] = _build_scope_suggestions(conn, project_id)
    return response
