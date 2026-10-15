## Context

A proposal has two parts that `approve_proposal` combines into an atomic
block:

- `pending_proposals.proposed_text`: the **body**, written verbatim after
  `**Regla:**` (rules) or `**Qué pasó:**` (lessons) by
  `_build_rule_atomic_block` / `_build_lesson_atomic_block`.
- `pending_proposals.metadata` (JSON): every other field, read with
  hard-coded defaults (`general`, `medium`, `**/*`, `manual`, no tags).

The pieces that write `metadata` today: legacy migration
(`knowledge_management.py`, two call sites), `edit_proposal` (merge), and
`deprecate_rule` (`superseded_by`). The `create_pending_proposal`
implementation (`tools/extraction.py`) already takes `metadata: dict | None`,
but the MCP wrapper in `server.py` doesn't expose it. So an MCP client has
exactly one field to put content in, and every instruction Meridian ships
(`_RULE_USAGE`, `_LESSON_USAGE`, `_TRANSCRIPTION_USAGE`, the skill's
`workflows.md`) tells it to put the whole rendered block there.

The destination file comes from `_scope_to_file_path(scope_id, doc_type)`.
`_approve_create_proposal` raises `FileNotFoundError` if it is missing;
`_append_atomic_block` reads the current bytes before appending.
`create_project` creates only the rules file (`knowledge-base/projects/<id>.md`
with a `# <name>` heading), not `lessons/projects/<id>.md`, and seeded or
otherwise created scopes get no file at all.

Constraints from `CLAUDE.md`: Markdown is the source of truth; `write_block`
is the only writer of knowledge `.md` bytes; `strip_private_tags` runs on
every inbound text; `sync_tags` is the only writer of `rule_tags` /
`lesson_tags`; field labels are load-bearing and shared by the parser, the
builders, `_extract_lesson_fields` and the templates.

## Goals / Non-Goals

**Goals:**
- An MCP client can create a proposal that approves into a correct block,
  following Meridian's own instructions.
- Clients that keep sending a rendered block (skill/plugin copies already
  installed from 0.1.0) get a correct block too, not a corrupted one.
- A proposal that would still produce a nested block can't be approved.
- The first rule or lesson of any existing scope can be approved.
- A text-only `update` keeps the target's other fields, in the file and the
  row.

**Non-Goals:**
- Changing the atomic block format or any field label.
- Repairing blocks already corrupted by this bug. Only one known case, and
  it was fixed by hand before approval. A curator fixes any other with an
  `update` proposal.
- Making `create_project` create the lessons file or go through
  `write_block`. Creating files on demand at approval covers both cases.
- Changing how legacy migration or `deprecate_rule` populate `metadata`.

## Decisions

### D1. Expose `metadata` as one JSON-object parameter

`create_pending_proposal` gets `metadata: str | None`, a JSON object, parsed
in the wrapper the same way `suggested_attributes` is. Allowed keys per type:

| type | keys |
|---|---|
| `rule` | `category`, `severity`, `applies_to`, `tags`, `source` |
| `lesson` | `project`, `date_occurred`, `severity`, `area_affected`, `tags`, `impact`, `root_cause`, `resolution`, `originated_rule_id` |
| `update` | the keys of the target's type |
| `deprecate` | unchanged (`superseded_by`, set by `deprecate_rule`) |

Unknown keys raise `ValueError` that names the allowed keys. `severity` must
be `low` / `medium` / `high` / `critical`. `tags` may be a list or a
comma-separated string; `_normalize_tags` already handles both. Values go
through `strip_private_tags` like the body.

*Alternatives:* typed parameters (`category=`, `severity=`, …) are more
discoverable, but that would mean 14 parameters across two shapes on one
tool. It would also diverge from `edit_proposal`, which already takes
`metadata` as a JSON object and merges it into the same column. Silently
ignoring unknown keys was rejected: a typo like `categoria` would quietly
produce `general` again, which is the bug being fixed.

### D2. Normalize a rendered block at creation; don't reject it

If the body (after stripping leading whitespace) starts with an atomic block
header line, `^## (RN|LL)-\S+`, `create_pending_proposal` parses it:

- rules: the field logic the indexer uses (`atomic_parser`; expose a public
  `parse_block_text(text) -> dict` that wraps `_parse_block_fields`, so the
  label mapping stays in one place);
- lessons: `_extract_lesson_fields` plus the label → key mapping used by
  `_insert_new_lesson` / `index_lessons_from_markdown`.

The parsed body becomes `proposed_text`. The parsed fields become
`metadata`, and explicit `metadata` keys override them. The header's code is
discarded: codes are allocated at approval (`RN-XXX-NNN` placeholders and
real-looking codes are treated the same). If the block's `**Scope:**` is
present and differs from `suggested_scope_id`, or from the target's scope for
`update`, the call fails. A disagreement on scope is ambiguous and must not
be resolved silently. A header with no body field (`**Regla:**` /
`**Qué pasó:**` missing or empty) also fails.

*Alternative:* reject any rendered block and require `metadata`. It's
simpler, but every agent using a 0.1.0 skill/plugin copy, or an LLM that read
the old template, would break. Today their input carries all the right
information in a different shape, so normalizing it costs one parse.

### D3. Guard at approval against a nested header

`approve_proposal` (create and update paths) rejects a body that contains a
line matching `^## (RN|LL)-` anywhere, with an error naming the proposal and
pointing to `edit_proposal`. No write happens. This catches proposals created
before the fix and any path that bypasses D2 (direct SQL, a future writer).
It does not auto-repair at approval time: approval is the human checkpoint,
and it should approve exactly what was reviewed.

### D4. Create a missing destination file at approval

In `_approve_create_proposal`, when `dest_path` doesn't exist, and only
because the proposal's `scope_id` was validated against `scopes` at creation
(re-checked here), create `dest_path.parent` with `mkdir(parents=True,
exist_ok=True)`. `_append_atomic_block` treats a missing file as empty
(`current_bytes = b""`), so the block lands at offset 0 and `write_block`
records the file in `indexed_files` as it does for any append. No heading is
written: the parser ignores headings, a heading would change the separator
and offset arithmetic for the first block, and the manual workaround produced
exactly this shape (`RN-AXIOM-001` at offset 0).

`_approve_update_proposal` keeps raising if the target's file is missing.
There the file must exist, because the row points into it.

*Alternative:* make `create_project` (and scope seeding) create both files
up front. That only helps scopes created after the fix, and it touches more
call sites. Creating on demand covers old scopes, seeded `global-*` scopes
and the lessons file with one code path.

### D5. `update` approvals inherit omitted fields from the current block

Before building the new block, `_approve_update_proposal` reads the target's
current block (it already has `old_offset` / `old_length`, and
`_splice_atomic_block` reads `old_block_text`), parses it with the D2
helpers, and computes `effective = parsed_fields | proposal_metadata`. Both
the block builder and `_update_rule_row` / `_update_lesson_row` / `sync_tags`
use `effective`. Inheriting from the block, not the row, follows "Markdown is
the source of truth" and covers `**Fuente:**`, which has no column. The
current row fallbacks (`target.get(...)`) remain as a second layer for fields
the block doesn't carry. Tags are inherited unless `metadata` contains
`tags`; an explicit empty list clears them.

### D6. Docs say the same thing everywhere

- `_RULE_USAGE` / `_LESSON_USAGE`: the template is the file format (for
  `index_*_from_markdown`); for a proposal, pass the body as `proposed_text`
  and the other fields as `metadata`, with a one-line example.
- `_TRANSCRIPTION_USAGE` step 3: the same contract.
- `create_pending_proposal` docstring/`Field` descriptions: `proposed_text`
  is the body only; `metadata` lists the keys per type; a rendered block is
  accepted and normalized.
- Skill `SKILL.md`, `references/workflows.md`, `references/tools.md` in both
  `distribution/skill/meridian/` and
  `distribution/plugin/meridian/skills/meridian/`, kept identical
  (`scripts/check_skill_safety.py` and `scripts/package_skill.py` must pass).
- `docs/03-system-architecture.md` sequence diagram: `create_pending_proposal(type,
  proposed_text, scope, metadata, ...)`.
- `CHANGELOG.md` `Unreleased` → `Fixed`.
- `docs/06-work-tickets.md`: Backlog ticket linking this change (the
  existing convention).

## Risks / Trade-offs

- [A body that legitimately starts with `## RN-…` (a rule about rule IDs)
  gets parsed as a block] → D2 only triggers when the text *starts* with the
  header line, and the parse fails loudly if there's no body field. A curator
  can still set it with `edit_proposal`, and D3 would then flag it. This is
  acceptable for content that is about Meridian's own format.
- [The file write in `_approve_create_proposal` isn't rolled back if the row
  insert fails afterwards, which can leave a new file holding one orphan
  block] → Same exposure as today's append path. Not widened by D4, and a
  reindex reconciles it. Out of scope.
- [Two copies of the skill drift] → Tasks update both and diff them; the
  existing skill checks run in the verification step.
- [Parsing at creation stores fields the user didn't type explicitly] → They
  did type them, in the block. The stored proposal is visible through
  `list_pending_proposals` before approval, which is the review point.

## Migration Plan

No schema change. Deploy as a normal release. Proposals pending at upgrade
time that hold a rendered block are rejected by D3 at approval, with an
instruction to run `edit_proposal` (body only + `metadata`). Rollback is
reverting the release; data written under the fix is valid under the old
code.

## Open Questions

None blocking. Should a heading (`# <scope name>`) be added to files created
by D4 for human readers? Deferred: it can be added later without affecting
parsing, as long as the first-block offset logic is adjusted with it.
