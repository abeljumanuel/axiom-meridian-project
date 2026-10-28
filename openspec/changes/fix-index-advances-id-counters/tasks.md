## 1. Regression tests first (they fail before the fix)

- [x] 1.1 In `tests/integration/test_proposals_flow.py` (`tmp_kb` pattern),
  add tests: index `RN-GLOBAL-001` then approve a rule proposal; index
  `LL-GLOBAL-001` then approve a lesson proposal; index `RN-GLOBAL-007` then
  approve 8 rules in a row.
  **Verify**: all fail on `main` with `UNIQUE constraint failed`.
- [x] 1.2 In `tests/unit/test_id_generator.py`, add tests for
  `bump_code_counter`: creates the counter, raises it, never lowers it,
  ignores malformed codes.
  **Verify**: fail on `main` (helper missing).

## 2. Implementation

- [x] 2.1 Add `bump_code_counter(conn, code)` to `utils/id_generator.py`,
  reusing the code parsing and the `MAX(next, excluded.next)` upsert; share
  code with `seed_id_counters` rather than duplicating the SQL.
  **Verify**: task 1.2 tests pass.
- [x] 2.2 Call it after the INSERT in `_insert_indexed_rule` and
  `_insert_indexed_lesson` (create path only).
  **Verify**: task 1.1 tests pass.

## 3. Docs and verification

- [x] 3.1 Correct `CLAUDE.md` (IDs section) and `docs/design/ADR-004` where
  they say `seed_id_counters` runs only once: it also runs on every
  `initialize_db()`, and indexing now bumps counters.
- [x] 3.2 Run `uv run pytest` and `uv run ruff check src tests`; both clean.
- [x] 3.3 Re-run the investigation script cases B, C7, D against the fix and
  confirm no errors and counters advance after indexing.
