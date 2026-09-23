# Work Tickets

Tickets are grouped by status. **Delivered** tickets reflect work already completed on Axiom Meridian and are kept here as a record of the project's evolution, with full acceptance criteria. **Backlog** tickets are the next candidates for implementation; going forward these are tracked as [OpenSpec](../openspec/) change proposals (see the Backlog section below), so their formal acceptance criteria live there instead of being duplicated here. Each ticket links back to the user story it fulfills where applicable.

Ticket fields: `ID`, `Title`, `Type`, `Priority`, `Status`, `Related story`, `Description`, plus `Acceptance criteria` (Delivered) or `OpenSpec change` (Backlog).

---

## Delivered

### TICKET-001 — MCP server scaffold and core tool surface
- **Type:** Feature | **Priority:** Must | **Status:** Done
- **Related stories:** US-A1, US-A2, US-B1, US-E1
- **Description:** Stand up the FastMCP server, the `server.py` security wrapper pattern, the SQLite schema (`scopes`, `rules`, `lessons`, `pending_proposals`, `access_log`, ...), the atomic and legacy parsers, and the initial tool set for querying, indexing, and approving knowledge.
- **Acceptance criteria:**
  - `meridian mcp` starts a working stdio MCP server.
  - `query_rules`/`query_lessons` return scope-resolved, filtered results.
  - `index_rules_from_markdown`/`index_lessons_from_markdown` and the proposal lifecycle (`create_pending_proposal`, `approve_proposal`, `reject_proposal`) work end-to-end.
  - Access levels (`read`/`analyze`/`write`) gate every tool.

### TICKET-002 — Codebase cleanup pass
- **Type:** Chore | **Priority:** Should | **Status:** Done
- **Description:** General cleanup of the initial implementation ahead of broader use.

### TICKET-003 — Fix installer and deployment issues
- **Type:** Bug | **Priority:** Must | **Status:** Done
- **Description:** Resolve install/deploy failures surfaced during first real installs across environments.

### TICKET-004 — Fix additional installer bugs
- **Type:** Bug | **Priority:** Must | **Status:** Done
- **Description:** Follow-up fixes to `scripts/install.sh` after further installer testing.

### TICKET-005 — Resolve `pyproject.toml` path resolution from `scripts/`
- **Type:** Bug | **Priority:** Must | **Status:** Done
- **Description:** Fix a path-resolution bug that broke the installer when invoked relative to the `scripts/` directory rather than the repo root.

### TICKET-006 — Legacy scope inference via word-boundary matching (ADR-003)
- **Type:** Bug fix / Refactor | **Priority:** Must | **Status:** Done
- **Related story:** US-B2
- **Description:** Replace substring-based scope inference during legacy migration with word-boundary matching, preventing false-positive scope assignment (e.g. `"go"` matching inside `"golang"` or `"algorithm"`).
- **Acceptance criteria:** covered by `tests/unit/test_scope_inference.py`.

### TICKET-007 — Performance remediation, phase 1: migration runner, ID counters, N+1 fix (ADR-004)
- **Type:** Refactor / Performance | **Priority:** Must | **Status:** Done
- **Description:**
  - Build a real migration runner (`db/migrations.py`) applying versioned `NNN_*.sql` files against `PRAGMA user_version`, with automatic backup.
  - Replace `MAX(id) LIKE 'prefix-%'` ID generation with an atomic `id_counters` table (`UPDATE ... RETURNING`), fixing both a race condition and lexicographic-sort ID collisions.
  - Fix an N+1 query pattern in `scope_resolver.filter_by_attributes`.
- **Acceptance criteria:** covered by `tests/unit/test_migrations.py`, `tests/unit/test_id_generator.py`.

### TICKET-008 — Indexed read path with per-file freshness (ADR-005)
- **Type:** Feature / Performance | **Priority:** Must | **Status:** Done
- **Related story:** US-A3
- **Description:**
  - Add `indexed_files`, `rule_tags`, `lesson_tags` tables with a backfill migration.
  - Introduce `write_block` as the single choke point for writing knowledge Markdown files, keeping the index from drifting off disk.
  - Serve `detail="full"` queries from SQLite, validated per-file (mtime fast path, sha256 arbiter) instead of re-reading Markdown per row.
  - Switch tag filtering from substring `LIKE` to exact-match joins on `rule_tags`/`lesson_tags`.
- **Acceptance criteria:** covered by `tests/unit/test_read_index.py`, `tests/integration/test_index_and_query.py`.

### TICKET-009 — Enforce clean-code global rules across Meridian's own tools
- **Type:** Refactor | **Priority:** Should | **Status:** Done
- **Description:** Apply the project's own `clean-code` global rule set to the `tools/` modules, dogfooding Meridian's governance model against its own codebase.

### TICKET-010 — Connection hardening and atomic parser robustness (ADR-006)
- **Type:** Bug fix / Reliability | **Priority:** Must | **Status:** Done
- **Description:**
  - Add SQLite `busy_timeout` and early-commit handling to eliminate `"database is locked"` failures under concurrent tool calls.
  - Harden `atomic_parser` against malformed blocks with clearer diagnostics instead of silent misparses.
- **Acceptance criteria:** covered by `tests/unit/test_connection.py`, `tests/unit/test_atomic_parser.py`.

### TICKET-011 — Add UPDATE proposal type support
- **Type:** Feature | **Priority:** Must | **Status:** Done
- **Related story:** US-B3
- **Description:** Extend `pending_proposals` with a `target_id` column and an `update` proposal type so an existing rule/lesson block can be revised in place (byte-level slice replacement in the `.md` file) rather than only ever appended as new.
- **Acceptance criteria:**
  - `create_pending_proposal(type="update", target_id=...)` validates the target exists and infers rule vs. lesson from the ID prefix.
  - `approve_proposal` on an `update` proposal replaces the block in the source file, updates the row via `UPDATE` (not `INSERT`), and records `change_type="UPDATED"` in history.
  - Existing (non-update) proposal flows remain unchanged — regression-covered in `tests/integration/test_proposals_flow.py`.

---

## Backlog

Each Backlog ticket below has a corresponding [OpenSpec](../openspec/) change proposal under `openspec/changes/`, which holds the formal, testable acceptance criteria (as delta specs) plus the design and task breakdown. The ticket entries here stay short — ID, description, status — and defer to OpenSpec for the detail.

### TICKET-012 — Windows one-line installer
- **Type:** Feature | **Priority:** Should | **Status:** Backlog
- **Description:** `scripts/install.sh` covers Linux/macOS; Windows currently requires manual installation. Provide a PowerShell equivalent (`install.ps1`) with the same client auto-detection (Claude Code, VSCode, OpenCode, Kimi CLI).
- **OpenSpec change:** [`add-windows-installer`](../openspec/changes/add-windows-installer/)

### TICKET-013 — V2 semantic search upgrade
- **Type:** Feature / Performance | **Priority:** Could | **Status:** Backlog
- **Related story:** US-F1
- **Description:** When the rule/lesson volume exceeds roughly 1,000 entries or more accurate multilingual retrieval is needed: evaluate migrating the embedding model to `BAAI/bge-m3` (567M params, 100+ languages) and evaluate alternative local vector stores (LanceDB, Qdrant local).
- **OpenSpec change:** [`upgrade-semantic-search-v2`](../openspec/changes/upgrade-semantic-search-v2/)

### TICKET-014 — Semantic clustering for redundancy detection
- **Type:** Feature | **Priority:** Could | **Status:** Backlog
- **Description:** Cluster rules by embedding similarity to surface likely-duplicate or overlapping rules across scopes, as a curator-facing report rather than an automatic merge.
- **OpenSpec change:** [`add-redundancy-detection`](../openspec/changes/add-redundancy-detection/)

### TICKET-015 — Networked (non-localhost) deployment hardening
- **Type:** Feature / Security | **Priority:** Could | **Status:** Backlog
- **Related story:** US-E3
- **Description:** The HTTP/SSE transport is currently scoped to `127.0.0.1` by design. Evaluate what's required (TLS, multi-token/per-client auth, rate limiting) to safely support a shared, networked deployment for a team, without weakening the current localhost-only default.
- **OpenSpec change:** [`harden-networked-deployment`](../openspec/changes/harden-networked-deployment/)

### TICKET-016 — Cross-reference `source_ref` with Engram observations
- **Type:** Feature | **Priority:** Could | **Status:** Backlog
- **Description:** Where Engram (episodic session memory) is present, allow a rule/lesson's `source_ref` to resolve to an Engram `observation_id` for cross-tool traceability, without introducing a hard dependency on Engram.
- **OpenSpec change:** [`link-source-ref-to-engram`](../openspec/changes/link-source-ref-to-engram/)

### TICKET-017 — Read-only observability dashboard
- **Type:** Feature | **Priority:** Could | **Status:** Backlog
- **Related story:** US-H1
- **Description:** Build a small, standalone frontend for humans (not agents) to visually inspect Meridian's state without writing Python snippets — server health, scope hierarchy, rule/lesson counts, pending proposals, a rendered usage manual, and an embedding projector. Runs as a separate local process, reusing `knowledge_consumption` functions as a library; never speaks the MCP protocol or performs writes.
- **Explicitly deferred because:** it sits outside the core MCP/knowledge-governance scope of the capstone (agent-facing tools, scope resolution, governed writes, RAG) and would add a second stack (HTTP API + frontend + its own auth/testing surface) without changing what an agent can do. Treated as an optional companion, evaluated only if time remains after the core backlog above.
- **OpenSpec change:** [`add-observability-dashboard`](../openspec/changes/add-observability-dashboard/)

## Related Documents

- [Project Charter](01-project-charter.md)
- [Product Description](02-product-description.md)
- [System Architecture](03-system-architecture.md)
- [Data Model](04-data-model.md)
- [User Stories](05-user-stories.md)
- [OpenSpec specs and changes](../openspec/)
