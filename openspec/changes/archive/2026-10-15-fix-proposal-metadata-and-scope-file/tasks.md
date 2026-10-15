## 1. Regression tests first (they fail before the fix)

- [x] 1.1 In `tests/integration/test_proposals_flow.py` (use the `tmp_kb`
  fixture pattern), add a test that creates a rule proposal with a rendered
  block (`## RN-XXX-NNN` + all fields) in `proposed_text`, approves it, and
  asserts the `.md` file holds exactly one header and the row/block carry
  the block's category, severity, applies-to and tags.
  **Verify**: fails on `main` (nested header, `general`/`medium`).
- [x] 1.2 Add a test that approves the first rule of an existing scope with
  no rules file, and one that approves the first lesson of a project created
  with `create_project` (rules file exists, lessons file doesn't).
  **Verify**: both fail on `main` with `Destination file does not exist`.
- [x] 1.3 Add a test that approves a text-only `update` (no `metadata`) of a
  rule with non-default category, severity, applies-to, tags and
  `**Fuente:**`, and asserts the block and the row keep them, with
  `rule_tags` unchanged.
  **Verify**: fails on `main` (block reset to defaults, tags cleared).

## 2. Parsing helpers

- [x] 2.1 Add a public `parse_block_text(text: str) -> dict` to
  `parsers/atomic_parser.py` that wraps `_parse_block_fields` for a single
  block given as text (design D2), and a lesson counterpart that maps
  `_extract_lesson_fields`' Spanish labels to the metadata keys used by
  `_build_lesson_atomic_block` (reuse the existing mapping; don't add
  labels).
  **Verify**: unit tests in `tests/unit/test_atomic_parser.py` for a rule
  block, a lesson block, a multi-line body, and a placeholder header
  `## RN-XXX-NNN`.
- [x] 2.2 Add one shared regex/helper for "text contains an atomic block
  header line" (`^## (RN|LL)-`, multiline) used by D2 (starts-with check)
  and D3 (anywhere check).

## 3. `create_pending_proposal`: metadata + normalization

- [x] 3.1 In `tools/extraction.py::create_pending_proposal`, validate
  `metadata` keys per type (design D1 table) and `severity`; raise
  `ValueError` naming the allowed keys. Strip private tags from string
  values. Leave `deprecate`'s `superseded_by` handling unchanged.
- [x] 3.2 Normalize a rendered block (design D2): if the stripped body
  starts with a header line, parse it, set `proposed_text` to the body field,
  merge parsed fields under explicit `metadata`, fail on a scope mismatch
  (vs. `suggested_scope_id`, or the target's scope for `update`) or a
  missing/empty body.
- [x] 3.3 Expose `metadata: str | None` (JSON object) on the
  `create_pending_proposal` MCP tool in `server.py`. Parse it like
  `suggested_attributes`, include it in `params` for the access log, and
  update the docstring and `Field` descriptions (body only in
  `proposed_text`; keys per type; rendered blocks are normalized).
- [x] 3.4 Update `tests/contract/test_mcp_tool_signatures.py` for the new
  parameter.
- [x] 3.5 Unit/integration tests for every scenario of "Proposal creation
  separates the body from the block fields" and "A rendered atomic block
  sent as a proposal is normalized".
  **Verify**: 1.1 now passes.

## 4. `approve_proposal`

- [x] 4.1 Guard (design D3): in `approve_proposal`, before any write, reject
  a `rule`/`lesson`/`update` proposal whose `proposed_text` contains a block
  header line, with an error naming the proposal and `edit_proposal`.
  **Verify**: test that nothing changes on disk, in `rules`, history or the
  proposal status.
- [x] 4.2 Missing file (design D4): in `_approve_create_proposal`, when
  `dest_path` doesn't exist, re-check the scope exists, `mkdir` the parent,
  and let `_append_atomic_block` treat a missing file as empty. Keep
  `_approve_update_proposal`'s `FileNotFoundError`.
  **Verify**: 1.2 passes; `indexed_files` has the new file; the block is at
  offset 0; a reindex of the file yields the same row.
- [x] 4.3 Inheritance on update (design D5): parse the target's current
  block, compute `effective = parsed | metadata`, and use it for the block
  builder, `_update_rule_row` / `_update_lesson_row` and `sync_tags` (tags
  inherited unless `metadata` has `tags`; `[]` clears).
  **Verify**: 1.3 passes; add the "explicit metadata changes only those
  fields" scenario.
- [x] 4.4 Confirm the embedding upsert after an update uses the effective
  tags/severity (`_rule_embedding_metadata` / `_lesson_embedding_metadata`).

## 5. Guidance and documentation

- [x] 5.1 `tools/knowledge_templates.py`: rewrite `_RULE_USAGE`,
  `_LESSON_USAGE` and step 3 of `_TRANSCRIPTION_USAGE` per design D6, each
  with a one-line `create_pending_proposal(..., proposed_text=<body>,
  metadata={...})` example. Update `tests/unit/test_knowledge_templates.py` /
  `tests/integration/test_knowledge_templates.py` if they assert the text.
- [x] 5.2 Skill references in `distribution/skill/meridian/` *and*
  `distribution/plugin/meridian/skills/meridian/`: `SKILL.md` (proposal
  steps), `references/workflows.md` (lesson and update flows: body +
  `metadata`, not `<block>`), `references/tools.md` (`metadata?` in the
  `create_pending_proposal` row).
  **Verify**: `diff -r distribution/skill/meridian
  distribution/plugin/meridian/skills/meridian` is empty;
  `scripts/check_skill_safety.py` and `scripts/package_skill.py` pass.
- [x] 5.3 `docs/03-system-architecture.md`: add `metadata` to the
  `create_pending_proposal` call in the proposal sequence diagram.
- [x] 5.4 `CHANGELOG.md` → `Unreleased` → `Fixed`: the three bugs, in user
  terms (broken block from the documented flow, first rule/lesson of a scope
  can't be approved, text-only update resets fields), plus `Added`: the
  `metadata` parameter.
- [x] 5.5 `docs/06-work-tickets.md`: add a Backlog ticket (next free ID)
  linking `openspec/changes/fix-proposal-metadata-and-scope-file/`.

## 6. Final verification

- [x] 6.1 `uv run pytest` (with and without the `rag` extra) and
  `uv run ruff check src tests scripts` pass clean; `openspec validate
  fix-proposal-metadata-and-scope-file --strict` passes.
- [x] 6.2 End-to-end through MCP against a scratch knowledge base: following
  only `get_rule_template`'s `usage`, create and approve a rule for a scope
  with no file, then a text-only update of it; the `.md` file holds one
  well-formed block with the right fields, and `query_rules(detail="full")`
  returns it without `STALE_INDEX`.
