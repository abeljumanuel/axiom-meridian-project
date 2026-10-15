# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `create_pending_proposal` takes an optional `metadata` JSON object with the
  block fields other than the body (rules: category, severity, applies-to,
  tags, source; lessons: project, date, severity, affected area, tags,
  impact, root cause, resolution, originating rule). Unknown keys and invalid
  severities are rejected.

### Fixed

- Following the template instructions (the whole rendered block as
  `proposed_text`) no longer produces a broken block, with a second header
  nested inside the rule text and the fields reset to `general` / `medium`.
  A rendered block is now split into body and fields when the proposal is
  created, and `approve_proposal` refuses any proposal whose text still
  contains a block header. The template, transcription and skill
  instructions now describe the body + `metadata` contract.
- Approving the first rule or lesson of a scope no longer fails with
  `Destination file does not exist`; the scope's file is created. This
  includes the lessons file of projects created with `create_project`.
- A text-only `update` proposal no longer resets the target's category,
  severity, applies-to and source, or clears its tags; fields the proposal
  doesn't set keep their current values in the file and the index.

## [0.1.0] - 2026-10-15

### Added

- PyPI package `axiom-meridian`, installable on Linux, macOS, and Windows
  with `uv tool install axiom-meridian` (or `pip`), or run without installing
  via `uvx --from axiom-meridian meridian mcp`.
- `meridian setup`: cross-platform configuration of detected MCP clients
  (Claude Code, VS Code, Cursor, OpenCode, Kimi CLI). It asks before
  configuring each one, creates the knowledge base, and can seed it with the
  bundled example rules. It never overwrites existing knowledge-base files
  and never replaces a client registration that points at a different
  install.
- `meridian doctor`: read-only installation diagnostics, covering:
  - clients' configured commands (missing binary, stale `uv run` configs);
  - a venv whose base Python moved (the `libpython` error);
  - cloud-sync venv corruption (duplicated files, hidden `.pth` files);
  - the running version and whether the `rag` extra is installed.
- Claude Code plugin (server and usage skill in one unit), installable with
  `/plugin install meridian --marketplace abeljumanuel/axiom-meridian-project`.
- Standalone, marketplace-safe skill (`distribution/skill/meridian/`) teaching
  agents when to use each Meridian tool, packaged as a zip.
- MCP Registry entry (`server.json`, name
  `io.github.abeljumanuel/axiom-meridian`).
- Installation guide: `docs/installation.md`.
- `LICENSE` with the full Apache License 2.0 text, and `NOTICE` with the
  copyright attribution and the "Axiom Meridian" / "Axiom JUMA" trademark
  statement.
- `CONTRIBUTING.md`: contributions are accepted under Apache-2.0 with a
  Developer Certificate of Origin sign-off (`git commit -s`).
- SPDX license headers on every source file under `src/meridian/` and
  `scripts/`, enforced by a test.

### Changed

- **Breaking:** semantic search is now the optional `rag` extra
  (`torch`, `sentence-transformers`, `chromadb`). Install
  `axiom-meridian[rag]` to keep it; the base install shrinks from about
  1.1 GB to 59 MB. Without the extra:
  - `query_rules`/`query_lessons` with `query_text` fall back to SQL
    filtering;
  - `generate_embeddings` returns `{"error": "RAG_NOT_INSTALLED", ...}`;
  - approval and promotion responses report `embedded` /
    `embedding_removed` as `null`;
  - the embedder warm-up at startup is skipped.
- `scripts/install.sh` is now a thin wrapper: it ensures uv, runs
  `uv tool install`, then hands off to `meridian setup` and `meridian doctor`.
  `scripts/uninstall.sh` also removes the uv tool install and Cursor's
  config entry.
- Relicensed from MIT to Apache License 2.0. Versions made available
  before this change were declared under MIT, and copies obtained under
  those terms remain available under them. Package metadata now declares
  `License-Expression: Apache-2.0` (PEP 639) and ships `LICENSE` and
  `NOTICE` in the wheel and sdist.

### Fixed

- `create_project` wrote the project's Markdown file in the locale's
  encoding (cp1252 on Windows), corrupting non-ASCII project names. It now
  writes UTF-8.
- OpenCode client configuration uses `environment` (not `env`), so the
  server's environment variables are no longer silently ignored.
- VS Code client configuration on macOS uses
  `~/Library/Application Support/Code/User/mcp.json`.
- `uninstall.sh` now detects an existing Claude Code registration (it matched
  a quoted `"meridian"` that `claude mcp list` never prints).
