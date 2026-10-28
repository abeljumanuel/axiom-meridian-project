## Context

`next_rule_code`/`next_lesson_code` allocate only from `id_counters`
(`id_generator.py:41-56`) and never look at `rules`/`lessons`. The atomic
indexer inserts rows with the block's own code (`knowledge_management.py`
`_insert_indexed_rule`, lesson counterpart) and does not touch the counter.
`initialize_db()` calls `seed_id_counters` on every startup
(`connection.py:64`), so drift is healed on restart but not while a process
keeps running. Evidence: cases B, C7 and D of the investigation (single
process, temp KBs, counters measured with a read-only connection).

## Goals / Non-Goals

**Goals:**
- No drift between `id_counters` and `rules`/`lessons` caused by indexing.
- Fix lives in the write path, in the same transaction as the insert.

**Non-Goals:**
- Guarding against writes that bypass the indexer (restored backups, direct
  DB edits); startup reconciliation keeps covering those.
- Retry-with-next-free in `next_*_code` (rejected, see Decisions).
- Cross-process locking during large indexing.

## Decisions

**D1. Raise the counter at insert time.** Add
`bump_code_counter(conn, code)` in `id_generator.py`: parse
`PREFIX-SEGMENT-NNN` like `_max_code_suffix_by_segment` and run the same
`INSERT ... ON CONFLICT DO UPDATE SET next = MAX(next, excluded.next)` that
`seed_id_counters` uses (O(1), never lowers). Called right after the row
INSERT in both indexing insert helpers, so the counter and row commit or roll
back together.
*Alternative: call `seed_id_counters` after each index run.* Rejected: scans
every code in both tables per run.
*Alternative: retry in `next_*_code`.* Rejected: adds a lookup to the hot path
ADR-004 removed and leaves the counter stale.

**D2. Only the create path.** The update path keeps the existing code, so the
counter already covers it (or was raised when it was created).

**D3. Malformed codes are ignored,** consistent with the seeding helper.

## Risks / Trade-offs

- A future path that inserts rule/lesson rows directly must also call the
  helper → document it on the helper's docstring, same as `sync_tags`.
- Indexing a very high manual code (e.g. `RN-GLOBAL-900`) makes the next
  generated code 901 → intended, same as seeding.
