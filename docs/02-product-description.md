# Product Description

## The Problem

Teams that work with AI coding agents accumulate institutional knowledge as long, narrative Markdown files: coding standards per language/framework, architecture decision records, and "lessons learned" from production incidents. This works while the files are small. As they grow:

- **Every agent session re-reads the whole file**, even when only two or three rules apply to the current task — burning context window and degrading response latency.
- **Relevance is all-or-nothing.** A Java rule file has no notion of "this project is Quarkus, that one is Spring Boot" — agents either get everything or must be manually pointed at the right section.
- **There is no governance.** Anyone (human or agent) can edit the file directly; there is no staged review, no audit trail, no way to tell which incident produced which rule.
- **Knowledge and code drift apart.** Rules stop reflecting what the codebase actually enforces, and nobody notices until the next incident repeats a lesson that was supposedly already learned.

## The Solution

Axiom Meridian is a Model Context Protocol (MCP) server that sits between these Markdown knowledge bases and the AI agents that need them. It indexes rules (`RN-*`) and lessons (`LL-*`) written in a canonical atomic block format, resolves a **scope hierarchy** (`project → framework → language → global`) to decide what applies to a given project, and serves only that filtered, optionally semantically-ranked slice through typed tools — while the Markdown files remain the single source of truth and every change to them passes through explicit human approval.

## Core Capabilities

1. **Scoped knowledge queries** — `query_rules` / `query_lessons` resolve the effective scope chain for a project, apply category/severity/tag filters, and return only matching, non-deprecated entries.
2. **Atomic, traceable knowledge format** — every rule/lesson is a self-contained Markdown block (`## RN-JAVA-011`, `## LL-PSP-003`) with structured fields, so it can be parsed, indexed, and diffed deterministically.
3. **Governed knowledge lifecycle** — extraction and legacy-file migration never write directly to active knowledge. Everything lands in `pending_proposals` first; a human reviews, edits, or rejects it before `approve_proposal` promotes it into the Markdown file and the SQLite index in one transaction.
4. **PR and feature auditing** — `audit_pr` surfaces the rules/lessons relevant to a diff before merge; `check_feature_against_rules` does the same during planning, before code is written.
5. **Meeting transcript extraction** — `extract_rules_from_transcript` / `extract_lessons_from_transcript` turn raw meeting notes into candidate proposals, keeping the loop from "we discussed it" to "it's an enforceable rule" short.
6. **Hybrid retrieval (SQL + RAG)** — when embeddings exist, `query_rules`/`query_lessons` rank by semantic similarity (`BAAI/bge-small-en-v1.5` via ChromaDB); when they don't, the same call transparently falls back to SQL filtering. The tool signature never changes.
7. **Access control and audit log** — every tool is gated by an operation level (`read` / `analyze` / `write`); every invocation is recorded with tool name, level, project, and result, with sensitive parameters (diff text, feedback text) excluded from the log.
8. **Ecosystem skill generation** — `generate_project_skills` emits `.claude/skills/` files following the `agentskills.io` convention, so a project's effective rules become a first-class, auto-loadable agent skill.

## Target Users

- **AI coding agents** (via any MCP-compatible client — Claude Code, VSCode, OpenCode, Kimi CLI) that need project-relevant rules and lessons without reading entire files.
- **Tech leads / knowledge curators** who own the Markdown knowledge base and decide what becomes an enforceable rule.
- **Developers** who want a pre-merge or pre-planning check against known rules and past incidents.
- **Platform/security admins** who need to control what a given agent session is allowed to write and to audit what it did.

## Why Not Just Grep the Markdown Files?

Grep (or a full-file read) has no concept of scope inheritance, dynamic attributes, severity filtering, deprecation status, or provenance. It cannot distinguish "this rule applies to every Java service" from "this rule only applies to services with `component_role=gateway`," cannot tell an agent which meeting produced a rule, and offers no safe write path — any edit is immediately live with no review step. Meridian adds exactly the structure needed to make a growing knowledge base cheap to query and safe to evolve, without asking teams to abandon Markdown as their authoring format.

## Non-Goals (V1)

- Meridian is not a general-purpose wiki or document store — it only models rules and lessons.
- It does not auto-promote extracted knowledge; every write requires human approval.
- It is not designed for networked, multi-tenant deployment; the HTTP/SSE transport binds to `127.0.0.1` only.

## Ecosystem Position

Meridian is self-sufficient — it has no hard dependency on any other tool. It optionally composes with:

| Tool | Role when present |
|---|---|
| Engram | Episodic session memory; a rule's `source_ref` can cross-reference an Engram `observation_id`. |
| GitNexus | Codebase structural analysis / blast-radius estimation; complements `audit_pr` but isn't required. |
| Agent Teams Lite | Sub-agent orchestration; can parallelize `extract_rules_from_transcript` across specialized agents. |
| Prowler Skills | Reference implementation of the `agentskills.io` standard that `generate_project_skills` follows. |

## Related Documents

- [Project Charter](01-project-charter.md)
- [System Architecture](03-system-architecture.md)
- [Data Model](04-data-model.md)
- [User Stories](05-user-stories.md)
- [Work Tickets](06-work-tickets.md)
