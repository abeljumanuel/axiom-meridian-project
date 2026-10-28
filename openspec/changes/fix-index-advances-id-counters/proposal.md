**Ticket:** TICKET-021 (`docs/06-work-tickets.md`)

## Why

Indexing atomic `.md` blocks with hand-written codes (e.g. `RN-GLOBAL-007`)
inserts rows without advancing `id_counters`. The next `approve_proposal` in
that scope reissues an occupied code and fails with `UNIQUE constraint failed:
rules.code` (or `lessons.code`). Since `initialize_db()` already reconciles
counters, only a server restart repairs it; a long-running server that indexes
and then approves stays broken. Reproduced with a single process in a temp KB:
indexing `RN-GLOBAL-001` then approving fails; indexing `RN-GLOBAL-007` makes
the 7th approval and every later one fail (the counter is stuck because each
failed approval rolls back its increment); lessons fail the same way.

## What Changes

- Indexing a rule or lesson block (create path) advances the matching
  `id_counters` entry to at least `suffix + 1`, in the same transaction as the
  row insert. The counter is never lowered.
- Codes that don't match `<PREFIX>-<SEGMENT>-<digits>` are skipped, as in
  `seed_id_counters`.
- Regression tests: index then approve in the same process, for rules and
  lessons, including the "7th approval" case.

No behavior change for update-only indexing, for approval, or for startup
reconciliation.

## Capabilities

### New Capabilities
- `id-counter-consistency`: `id_counters` never lags behind codes present in
  `rules`/`lessons`, whichever path wrote them.

### Modified Capabilities

## Impact

- `src/meridian/utils/id_generator.py`: new helper to raise a code counter
  from a code string (reusing the parsing in `_max_code_suffix_by_segment`).
- `src/meridian/tools/knowledge_management.py`: `_insert_indexed_rule` and the
  lesson counterpart (`_insert_indexed_lesson`) call it.
- Tests: `tests/unit/test_id_generator.py`,
  `tests/integration/test_proposals_flow.py`.
- Docs: `docs/design/ADR-004` and `CLAUDE.md` still say `seed_id_counters`
  runs only once; correct them to match `connection.py`.
