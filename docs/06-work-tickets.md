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

### TICKET-018 — Cross-platform installation and distribution
- **Type:** Feature | **Priority:** Must | **Status:** Done
- **Description:** Make Meridian installable in one command on Linux, macOS and Windows without cloning the repo, and distributable through agent-facing channels, while the server stays self-hosted. This covers:
  - The semantic-search libraries (`torch`, `sentence-transformers`, `chromadb`) become an optional `[rag]` extra. The base install drops from about 1.1 GB to 59 MB, and every RAG path degrades cleanly without it (`RAG_NOT_INSTALLED`, SQL fallback).
  - New cross-platform `meridian setup` (client detection and configuration for Claude Code, VSCode, Cursor, OpenCode and Kimi CLI, knowledge-base creation, no-clobber example seeding) and `meridian doctor` (read-only diagnostics).
  - `install.sh` is now a thin wrapper around `uv tool install` and `meridian setup`.
  - PyPI packaging with a Trusted Publishing release workflow, and a CI workflow across the three OSes.
  - A distributable skill, a Claude Code plugin with a marketplace, and an MCP Registry `server.json`.
  - Released as 0.1.0 (PR #3, PR #4): published to PyPI (`uv tool install axiom-meridian`), listed as `io.github.abeljumanuel/axiom-meridian` in the MCP Registry, the Claude Code plugin is installable from the repo's own marketplace, and CI is green on Linux, macOS and Windows. Third-party marketplace listings and the skill zip upload are deferred until a destination is chosen.
- **OpenSpec change:** [`improve-installation-and-distribution`](../openspec/changes/archive/2026-10-15-improve-installation-and-distribution/)

### TICKET-019 — Relicense to Apache License 2.0
- **Type:** Chore / Legal | **Priority:** Must | **Status:** Done
- **Description:** Move from MIT, which is declared but has no `LICENSE` file, to Apache-2.0 before the first public release: add `LICENSE` and `NOTICE` (attribution plus a trademark statement for "Axiom Meridian" / "Axiom JUMA"), PEP 639 package metadata, SPDX headers enforced by a test, a `CONTRIBUTING.md` with a DCO sign-off, and the dependency-compatibility review. It landed before TICKET-018's first PyPI release (commit `f800112`, PR #3), so 0.1.0 shipped under Apache-2.0. All preconditions are confirmed: sole authorship, the rights belong to the author (not the academic program), and the legal name.
- **OpenSpec change:** [`change-license-to-apache-2`](../openspec/changes/archive/2026-10-15-change-license-to-apache-2/)

### TICKET-020 — Proposal metadata and first block of a scope
- **Type:** Bug fix | **Priority:** Must | **Status:** Done
- **Description:** The documented proposal flow (template usage: rendered block as `proposed_text`) produced a nested, mis-filed block on approval, because `approve_proposal` builds the block from the body plus `metadata`, which the MCP tool couldn't set. Approving the first rule or lesson of a scope with no `.md` file failed, and a text-only `update` reset the target's other fields. Found while registering `RN-AXIOM-001`. Delivered in PR #6: `create_pending_proposal` takes `metadata` and normalizes a rendered block, `approve_proposal` rejects a nested header and creates a missing scope file, and `update` approvals inherit omitted fields.
- **OpenSpec change:** [`fix-proposal-metadata-and-scope-file`](../openspec/changes/archive/2026-10-15-fix-proposal-metadata-and-scope-file/)

### TICKET-021 — Indexing keeps `id_counters` ahead of hand-written codes
- **Type:** Bug fix | **Priority:** Must | **Status:** In review
- **Description:** Indexing atomic `.md` blocks with hand-written codes (e.g. `RN-GLOBAL-007`) inserted rows without advancing `id_counters`, so on a running server the next `approve_proposal` in that scope reissued an occupied code and failed with `UNIQUE constraint failed: rules.code` (or `lessons.code`); with a high manual code every approval from the matching number on failed, because each failure rolled back its own increment. A server restart repaired it (`initialize_db()` reseeds the counters), but a long-running server stayed broken. The atomic indexer now calls `bump_code_counter` in the same transaction as each created row.
- **Evidence:** Reproduced in a single process against a temporary knowledge base (index `RN-GLOBAL-001` then approve; index `RN-GLOBAL-007` then approve 8 in a row; the same with `LL-GLOBAL-001`), measuring `id_counters` after each step; all three failed before the fix and pass after it.
- **OpenSpec change:** [`fix-index-advances-id-counters`](../openspec/changes/fix-index-advances-id-counters/)

### Delivered without a ticket

These OpenSpec changes were completed and archived with the 0.1.0 release but never had a ticket of their own; they're listed here so the record is complete.

- [`add-actor-identity-tracking`](../openspec/changes/archive/2026-10-15-add-actor-identity-tracking/) — Record who originated each proposal, history entry and tool access (an actor column on `pending_proposals`, `rule_history`, `lesson_history` and `access_log`), so a future networked mode can attribute changes without backfilling history.
- [`add-rule-lesson-deprecation`](../openspec/changes/archive/2026-10-15-add-rule-lesson-deprecation/) — Deprecate a rule or lesson without changing its scope (`deprecate_rule`), exclude deprecated entries from semantic search, and record `DEPRECATED` history so the audit log surfaces them (ADR-007).
- [`add-server-version-visibility`](../openspec/changes/archive/2026-10-15-add-server-version-visibility/) — New `get_server_info` tool and richer `meridian version` output (version, git commit, dirty flag), with a `stale` flag when the code on disk is newer than what the running server loaded.
- [`fix-approve-proposal-stale-embeddings`](../openspec/changes/archive/2026-10-15-fix-approve-proposal-stale-embeddings/) — `approve_proposal` now refreshes the ChromaDB embedding for created and updated rules/lessons, so semantic search sees new rules and current tags.
- [`fix-approve-update-stale-offsets`](../openspec/changes/archive/2026-10-15-fix-approve-update-stale-offsets/) — Approving several UPDATE proposals against the same `.md` file no longer corrupts it: later blocks' offsets are shifted after an in-place rewrite (`shift_offsets_after`).
- [`fix-atomic-parser-plain-code-regex`](../openspec/changes/archive/2026-10-15-fix-atomic-parser-plain-code-regex/) — The atomic parser accepts the legacy plain-code headers (`RN-NNN` / `LL-NNN`) instead of silently dropping them.
- [`fix-installer-claude-mcp-check-and-url`](../openspec/changes/archive/2026-10-15-fix-installer-claude-mcp-check-and-url/) — The installer's Claude Code "already configured" check matches the real `claude mcp list` output and warns on a mismatched registration; the remote-install URL in the usage text is fixed.
- [`fix-installer-seed-overwrites-existing-kb`](../openspec/changes/archive/2026-10-15-fix-installer-seed-overwrites-existing-kb/) — Seeding the example knowledge base never overwrites a user's existing `.md` files (no-clobber).
- [`fix-installer-setup-venv-abort-on-decline`](../openspec/changes/archive/2026-10-15-fix-installer-setup-venv-abort-on-decline/) — Declining to recreate an existing virtual environment no longer aborts the installer.
- [`improve-approve-proposal-feedback`](../openspec/changes/archive/2026-10-15-improve-approve-proposal-feedback/) — `approve_proposal`'s response reports whether the embedding was updated (`embedded`), and in-place block rewrites keep the original trailing blank lines.
- [`warm-up-embedder-on-server-start`](../openspec/changes/archive/2026-10-15-warm-up-embedder-on-server-start/) — Warm up the embedding model when the server starts, so the first semantic query no longer pays the lazy-load cost (up to ~35 s, causing client timeouts).

---

## Backlog

Each Backlog ticket below has a corresponding [OpenSpec](../openspec/) change proposal under `openspec/changes/`, which holds the formal, testable acceptance criteria (as delta specs) plus the design and task breakdown. The ticket entries here stay short — ID, description, status — and defer to OpenSpec for the detail.

### TICKET-012 — Windows one-line installer
- **Type:** Feature | **Priority:** Should | **Status:** Superseded by [TICKET-018](#ticket-018--cross-platform-installation-and-distribution)
- **Description:** `scripts/install.sh` covered only Linux/macOS, and Windows required manual installation. The original plan was a PowerShell port (`install.ps1`) with the same client auto-detection. TICKET-018 covers Windows without it: client detection and configuration moved into the cross-platform `meridian setup` command (Python), so on Windows installing is `uv tool install axiom-meridian` followed by `meridian setup`, and a `.ps1` would only duplicate that logic.
- **OpenSpec change:** `add-windows-installer` (removed — superseded by [`improve-installation-and-distribution`](../openspec/changes/archive/2026-10-15-improve-installation-and-distribution/))

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
- **Type:** Feature | **Priority:** Could | **Status:** Discarded
- **Description:** Where Engram (episodic session memory) is present, allow a rule/lesson's `source_ref` to resolve to an Engram `observation_id` for cross-tool traceability, without introducing a hard dependency on Engram.
- **OpenSpec change:** `link-source-ref-to-engram` (removed — ticket discarded)

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
