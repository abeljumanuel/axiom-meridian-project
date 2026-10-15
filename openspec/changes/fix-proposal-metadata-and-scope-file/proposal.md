## Why

Registering the first project-scoped rule through MCP (`RN-AXIOM-001`,
2026-10-15) only worked after two manual workarounds, because the documented
proposal flow and what `approve_proposal` actually does disagree:

1. **The documented flow writes a broken block.** `get_rule_template` /
   `get_lesson_template` say to "call `create_pending_proposal` with
   `proposed_text` set to the rendered markdown", and
   `get_transcription_template` says the same ("formatted in the canonical
   atomic markdown"). The skill (`references/workflows.md`) passes
   `proposed_text=<block>` too. But `approve_proposal` builds the block
   itself: it puts the whole `proposed_text` under `**Regla:**` /
   `**Qué pasó:**` and reads category, severity, applies-to, tags and source
   from the proposal's `metadata`. The `create_pending_proposal` MCP tool
   cannot set `metadata` (the implementation in `tools/extraction.py`
   accepts it, but `server.py` doesn't expose it). An agent that follows the
   instructions gets a block with a second `## RN-XXX-NNN` header nested
   inside `**Regla:**`, filed as `general` / `medium` / `**/*` with no tags.
   The `.md` file is the source of truth, so this corrupts the knowledge
   base: the row holds the defaults, while a reindex of the file reads the
   nested `**Scope:**`/`**Categoría:**`/… lines and the second `**Regla:**`,
   so the file and the index disagree about the same rule.
2. **The first rule or lesson of a scope can't be approved.**
   `_approve_create_proposal` raises `Destination file does not exist` when
   the scope's `.md` file is missing. That happens for any scope created
   without `create_project` (e.g. `project-axiom-meridian`), for every
   seeded `global-*` scope that has no file yet, and for the *lessons* file
   of every project, since `create_project` only creates the rules file.
3. **An `update` proposal without metadata rewrites the block's fields.**
   Same root cause: with empty `metadata`, `_approve_update_proposal`
   rebuilds the block with the builder's defaults (`general`, `medium`,
   `**/*`, `manual`) while the SQLite row keeps the target's values, and it
   clears tags in both places (`metadata.get("tags", [])`). The `.md` file
   and the index disagree after any text-only update made through MCP.

## What Changes

- `create_pending_proposal` (MCP tool) gains an optional `metadata`
  parameter: a JSON object with the block fields that aren't the body
  (rules: `category`, `severity`, `applies_to`, `tags`, `source`; lessons:
  `project`, `date_occurred`, `severity`, `area_affected`, `tags`,
  `impact`, `root_cause`, `resolution`, `originated_rule_id`).
  Unknown keys are rejected; `severity` is validated.
- `create_pending_proposal` accepts a rendered atomic block in
  `proposed_text` as well, for agents and skill copies that still follow the
  old instructions: it parses the block with the same field logic as the
  indexer, stores only the body as `proposed_text` and the fields as
  `metadata`. Explicit `metadata` wins over parsed fields. A block whose
  `**Scope:**` contradicts `suggested_scope_id` (or, for `update`, the
  target's scope) is rejected.
- `approve_proposal` refuses to write a body that still contains an atomic
  block header (`## RN-…` / `## LL-…`) and tells the curator to fix it with
  `edit_proposal`. This covers proposals already pending from before the fix.
- `approve_proposal` creates a missing destination file (and its parent
  directory) for a scope that exists in `scopes`, writing the block through
  `write_block` as it does for an append. An unknown scope still fails.
- `update` approvals inherit every field the proposal's `metadata` omits
  from the target's current block in the `.md` file (including tags and
  `**Fuente:**`, which has no column), so the rewritten block and the row
  agree.
- The template `usage` texts, the transcription workflow text, the
  `create_pending_proposal` tool description, and the skill references (both
  copies) describe the flow that actually works: body in `proposed_text`,
  fields in `metadata`.

No breaking changes: `metadata` is optional, and callers that send a
rendered block keep working (now correctly).

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `knowledge-lifecycle-governance`: proposal creation takes block fields as
  `metadata` and normalizes a rendered block; approval creates a missing
  scope file, rejects a body with a nested header, and `update` approvals
  inherit omitted fields from the target; template guidance matches this
  contract.

## Impact

- **Code**: `server.py` (`create_pending_proposal` signature/description);
  `tools/extraction.py` (`create_pending_proposal`: metadata validation,
  rendered-block normalization); `tools/knowledge_management.py`
  (`_approve_create_proposal`, `_approve_update_proposal`,
  `_update_rule_row` / `_update_lesson_row`, tag sync on update, a guard
  against nested headers, creating the destination file);
  `tools/knowledge_templates.py` (usage strings); possibly a small public
  helper in `parsers/atomic_parser.py` to parse a single block from text.
- **API**: one new optional parameter on an MCP tool; the contract test
  `tests/contract/test_mcp_tool_signatures.py` changes with it.
- **Docs**: `distribution/skill/meridian/` and
  `distribution/plugin/meridian/skills/meridian/` (`SKILL.md`,
  `references/workflows.md`, `references/tools.md`),
  `docs/03-system-architecture.md` (proposal sequence diagram),
  `CHANGELOG.md` (Unreleased), `docs/06-work-tickets.md` (Backlog ticket).
- **Data**: no migration. `pending_proposals.metadata` already exists.
  Existing pending proposals with a rendered block are caught at approval
  and fixed with `edit_proposal`.
