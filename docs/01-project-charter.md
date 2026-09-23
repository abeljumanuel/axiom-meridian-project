# Project Charter

## Fact Sheet

| Field | Value |
|---|---|
| **Project name** | Axiom Meridian |
| **Tagline** | *"Code drifts. Meridian doesn't."* |
| **One-line pitch** | An MCP (Model Context Protocol) server that centralizes institutional technical knowledge and delivers only the slice relevant to the current task, instead of forcing AI agents to read entire knowledge-base files on every session. |
| **Author** | Juan Rojas ([abeljumanuel.rojas@gmail.com](mailto:abeljumanuel.rojas@gmail.com)) |
| **Academic context** | Capstone project — Master's Degree in Artificial Intelligence |
| **Category** | Developer tooling / AI agent infrastructure / knowledge management |
| **Current version** | v0.1.0 |
| **License** | MIT |
| **Primary language** | Python 3.11+ |
| **Core framework** | [FastMCP](https://github.com/jlowin/fastmcp) (Model Context Protocol server implementation) |
| **Persistence** | Markdown (source of truth) + SQLite (index/state layer) + ChromaDB (optional vector store for semantic search) |
| **Interfaces** | MCP tools over stdio (default) or HTTP/SSE; companion CLI (`meridian`) |
| **Distribution** | `uv`/`pip` editable install, one-line shell installer, MCP client auto-configuration (Claude Code, VSCode, OpenCode, Kimi CLI) |

## Repository Note

This repository documents and tracks the incremental build-out of Axiom Meridian for the Master's capstone submission. Documentation is written in English to keep the project consistent with the AI tooling (Claude Code, MCP clients) used throughout the course and to support an international audience.

## Elevator Pitch

AI coding agents increasingly rely on shared knowledge bases — coding standards, architecture decisions, lessons learned from incidents — written as long-lived Markdown files (`Global_Rules.md`, `Lessons_Learned.md`). As these files grow, every agent session pays the cost of reading them in full, degrading both response latency and answer quality. Axiom Meridian turns those files into a queryable, governed knowledge system: rules and lessons are indexed atomically, resolved through a project → framework → global scope hierarchy, optionally retrieved via semantic search, and served through typed MCP tools — while the Markdown files remain the single, human-readable source of truth and every write passes through an explicit human-approval step.

## Objectives

1. **Reduce context cost for AI agents.** Serve only the rules/lessons relevant to a project and task, instead of full-file reads.
2. **Preserve Markdown as the single source of truth.** SQLite exists purely as an index and state layer; it must never be the origin of knowledge content.
3. **Guarantee human-in-the-loop governance.** No extraction or migration path writes directly to active knowledge — everything is staged as a `pending_proposal` until explicitly approved.
4. **Support hybrid retrieval without breaking contracts.** Semantic search (RAG) augments SQL-based scope resolution when embeddings exist, and falls back transparently when they don't — tool signatures never change.
5. **Enforce least-privilege access.** Every tool call is gated by an operation level (`read` / `analyze` / `write`) and recorded in an auditable access log.
6. **Keep traceability end-to-end.** Every rule and lesson can be traced back to the meeting, PR, or incident that originated it.

## Scope

**In scope**
- Indexing, querying, and lifecycle management of technical rules and lessons learned.
- Scope-hierarchy resolution (global → framework → project) with dynamic attribute filtering.
- PR auditing and feature-vs-rules conflict checks.
- Extraction of rule/lesson candidates from meeting transcripts.
- Optional semantic search over rules and lessons.
- Access control, audit logging, and generation of per-project agent skill files.

**Out of scope (V1)**
- Multi-tenant / networked deployment beyond localhost HTTP binding.
- Automatic (un-reviewed) promotion of extracted knowledge into active rules.
- Non-Markdown knowledge sources (databases, wikis, ticketing systems) as direct ingestion targets.

## Stakeholders

| Role | Interest |
|---|---|
| AI coding agent (MCP client) | Consumes rules/lessons on demand during a coding session. |
| Tech lead / knowledge curator | Reviews and approves proposals; keeps the knowledge base authoritative. |
| Developer running audits | Uses `audit_pr` / `check_feature_against_rules` before merging or planning. |
| Platform / security admin | Configures access levels, reviews the audit log. |

See [User Stories](05-user-stories.md) for these roles expressed as concrete requirements.

## Related Documents

- [Product Description](02-product-description.md)
- [System Architecture](03-system-architecture.md)
- [Data Model](04-data-model.md)
- [User Stories](05-user-stories.md)
- [Work Tickets](06-work-tickets.md)
