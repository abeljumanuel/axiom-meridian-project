# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
"""Extraction tools — transcript analysis and pending proposal creation."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from meridian.parsers.atomic_parser import (
    BLOCK_HEADER_LINE_RE,
    LESSON_FIELD_KEYS,
    RULE_FIELD_KEYS,
    parse_block_text,
)
from meridian.tools.knowledge_consumption import query_lessons, query_rules
from meridian.tools.knowledge_templates import (
    LESSON_TEMPLATE as _LESSON_TEMPLATE,
    RULE_TEMPLATE as _RULE_TEMPLATE,
)
from meridian.utils.id_generator import next_sequential_id
from meridian.utils.privacy import strip_private_tags
from meridian.utils.scope_resolver import load_scope_attributes, resolve_scope_hierarchy
from meridian.utils.security import resolve_actor


def extract_rules_from_transcript(
    conn: sqlite3.Connection, text: str, project_id: str
) -> dict[str, Any]:
    """Return structured context for the client LLM to extract rules from a transcript.

    - Clean text (private tags stripped)
    - Available scopes with attributes
    - Existing rules for duplicate detection
    - Canonical atomic format template
    """
    clean_text = strip_private_tags(text)

    scopes = resolve_scope_hierarchy(conn, project_id)
    scope_data: list[dict[str, Any]] = []
    for scope in scopes:
        attrs = load_scope_attributes(conn, scope)
        scope_data.append({"scope_id": scope, "attributes": attrs})

    existing_rules = json.loads(query_rules(project_id, detail="summary"))

    return {
        "clean_text": clean_text,
        "scopes": scope_data,
        "existing_rules": existing_rules,
        "template": _RULE_TEMPLATE,
        "instruction_for_client": (
            "Analyze the transcript and identify candidate rules. "
            "For each candidate, call create_pending_proposal with type='rule'."
        ),
    }


def extract_lessons_from_transcript(
    conn: sqlite3.Connection, text: str, project_id: str
) -> dict[str, Any]:
    """Return structured context for the client LLM to extract lessons from a transcript.

    - Clean text (private tags stripped)
    - Available scopes with attributes
    - Existing lessons for duplicate detection
    - Canonical atomic format template
    """
    clean_text = strip_private_tags(text)

    scopes = resolve_scope_hierarchy(conn, project_id)
    scope_data: list[dict[str, Any]] = []
    for scope in scopes:
        attrs = load_scope_attributes(conn, scope)
        scope_data.append({"scope_id": scope, "attributes": attrs})

    existing_lessons = json.loads(query_lessons(project_id, detail="summary"))

    return {
        "clean_text": clean_text,
        "scopes": scope_data,
        "existing_lessons": existing_lessons,
        "template": _LESSON_TEMPLATE,
        "instruction_for_client": (
            "Analyze the transcript and identify candidate lessons learned. "
            "For each candidate, call create_pending_proposal with type='lesson'."
        ),
    }


_ALLOWED_METADATA_KEYS = {
    "rule": frozenset(RULE_FIELD_KEYS.values()),
    "lesson": frozenset(LESSON_FIELD_KEYS.values()),
}
_VALID_SEVERITIES = ("low", "medium", "high", "critical")


def _validate_block_metadata(metadata: dict, kind: str) -> dict:
    """Check *metadata* holds only block fields of *kind* and return a clean
    copy (valid severity, tags as a list, private tags stripped)."""
    allowed = _ALLOWED_METADATA_KEYS[kind]
    unknown = sorted(set(metadata) - allowed)
    if unknown:
        raise ValueError(
            f"Unknown metadata key(s) for a {kind}: {unknown}. "
            f"Allowed keys: {sorted(allowed)}."
        )

    clean: dict = {}
    for key, value in metadata.items():
        if key == "tags":
            raw_tags = value.split(",") if isinstance(value, str) else list(value or [])
            clean["tags"] = [
                strip_private_tags(str(t)).strip() for t in raw_tags if str(t).strip()
            ]
        elif isinstance(value, str):
            clean[key] = strip_private_tags(value)
        else:
            clean[key] = value

    severity = clean.get("severity")
    if severity is not None and severity not in _VALID_SEVERITIES:
        raise ValueError(
            f"Invalid severity '{severity}'. Must be one of {list(_VALID_SEVERITIES)}."
        )
    return clean


def _split_body_and_metadata(
    proposed_text: str, metadata: dict | None, kind: str, scope_id: str
) -> tuple[str, dict]:
    """Return the proposal body and its block metadata.

    A body sent as a whole rendered atomic block (what the 0.1.0 template
    usage told clients to do) is parsed into body + fields; explicit
    *metadata* keys win over parsed ones. See
    openspec/changes/fix-proposal-metadata-and-scope-file, design D1/D2.
    """
    explicit = _validate_block_metadata(metadata or {}, kind)
    if not BLOCK_HEADER_LINE_RE.match(proposed_text.lstrip()):
        return proposed_text, explicit

    parsed = parse_block_text(proposed_text.lstrip(), kind)
    if parsed.header_kind != kind:
        raise ValueError(
            f"proposed_text is a {parsed.header_kind} block, but the proposal is for a {kind}."
        )
    if parsed.scope is not None and parsed.scope != scope_id:
        raise ValueError(
            f"The block's Scope '{parsed.scope}' does not match the proposal's scope "
            f"'{scope_id}'. Fix one of them so they agree."
        )
    if not parsed.body:
        body_label = "Regla" if kind == "rule" else "Qué pasó"
        raise ValueError(
            f"proposed_text is a rendered block without a '**{body_label}:**' body."
        )
    return parsed.body, {**_validate_block_metadata(parsed.metadata, kind), **explicit}


def create_pending_proposal(
    conn: sqlite3.Connection,
    type: str,
    proposed_text: str,
    suggested_scope_id: str,
    target_id: str | None = None,
    target_type: str | None = None,
    suggested_attributes: list[dict[str, str]] | None = None,
    source_type: str | None = None,
    source_ref: str | None = None,
    reason: str | None = None,
    metadata: dict | None = None,
) -> str:
    """Validate and persist a pending proposal.

    1. Validates that suggested_scope_id exists in scopes (for rule/lesson types).
    2. For UPDATE/DEPRECATE types: validates target_id exists and references
       an existing rule/lesson (and, for DEPRECATE, that metadata's
       superseded_by, if given, references an existing active one).
    3. For RULE/LESSON/UPDATE: validates metadata's block-field keys, and
       splits a rendered atomic block in proposed_text into body + metadata.
    4. Sanitizes proposed_text via strip_private_tags (Layer 2 guarantee).
    5. Generates a sequential ID and inserts into pending_proposals.
    6. Returns the proposal ID.
    """
    type = type.lower() if type else None
    # Validate type
    if type not in ("rule", "lesson", "update", "deprecate"):
        raise ValueError(
            f"Invalid proposal type: {type}. "
            "Must be 'rule', 'lesson', 'update', or 'deprecate'."
        )

    # Handle UPDATE/DEPRECATE proposal types (both target an existing rule/lesson)
    if type in ("update", "deprecate"):
        if target_id is None:
            raise ValueError(
                f"target_id is required for {type.upper()} proposals. "
                "Specify the ID of the rule or lesson to target."
            )

        # Infer target_type from ID prefix
        if target_type is None:
            if target_id.startswith("RN-"):
                target_type = "rule"
            elif target_id.startswith("LL-"):
                target_type = "lesson"
            else:
                raise ValueError(
                    f"Invalid target_id format: {target_id}. "
                    "Must start with 'RN-' for rules or 'LL-' for lessons."
                )

        # Validate target exists
        if target_type == "rule":
            cursor = conn.execute(
                "SELECT scope_id FROM rules WHERE id = ?", (target_id,)
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(
                    f"Target rule '{target_id}' does not exist. "
                    f"Verify the rule_id before submitting the {type.upper()} proposal."
                )
            # Use target's scope_id, not suggested_scope_id
            suggested_scope_id = row[0]
        elif target_type == "lesson":
            cursor = conn.execute(
                "SELECT scope_id FROM lessons WHERE id = ?", (target_id,)
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(
                    f"Target lesson '{target_id}' does not exist. "
                    f"Verify the lesson_id before submitting the {type.upper()} proposal."
                )
            # Use target's scope_id, not suggested_scope_id
            suggested_scope_id = row[0]
        else:
            raise ValueError(f"Invalid target_type: {target_type}")

        if type == "deprecate":
            superseded_by = (metadata or {}).get("superseded_by")
            if superseded_by:
                replacement_table = (
                    "rules" if superseded_by.startswith("RN-")
                    else "lessons" if superseded_by.startswith("LL-")
                    else None
                )
                row = (
                    conn.execute(
                        f"SELECT 1 FROM {replacement_table} "  # noqa: S608
                        "WHERE id = ? AND status = 'active'",
                        (superseded_by,),
                    ).fetchone()
                    if replacement_table
                    else None
                )
                if row is None:
                    raise ValueError(
                        f"superseded_by '{superseded_by}' does not reference an "
                        "existing active rule or lesson."
                    )

    else:
        # Validate scope for rule/lesson types
        cursor = conn.execute(
            "SELECT 1 FROM scopes WHERE id = ?", (suggested_scope_id,)
        )
        if cursor.fetchone() is None:
            raise ValueError(
                f"Scope '{suggested_scope_id}' does not exist. "
                "Verify the scope_id before submitting the proposal."
            )

    if type != "deprecate":
        kind = target_type if type == "update" else type
        proposed_text, metadata = _split_body_and_metadata(
            proposed_text, metadata, kind, suggested_scope_id
        )

    clean_text = strip_private_tags(proposed_text)
    prop_id = next_sequential_id(conn, "pending_proposals", "prop")

    conn.execute(
        """
        INSERT INTO pending_proposals
        (id, type, scope_id, target_id, proposed_text,
         suggested_attributes, source_type, source_ref, reason, metadata,
         actor_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            prop_id,
            type,
            suggested_scope_id,
            target_id,
            clean_text,
            json.dumps(suggested_attributes) if suggested_attributes else None,
            source_type,
            source_ref,
            reason,
            json.dumps(metadata) if metadata else None,
            resolve_actor(),
        ),
    )
    conn.commit()

    return prop_id
