## 1. Database

- [ ] 1.1 Write migration `008_redundancy_reviews.sql` (new table, constraints, index on `decision`)
- [ ] 1.2 Add the table to `schema.sql` and to `EXPECTED_TABLES` in `tests/unit/test_connection.py`

## 2. Tool

- [ ] 2.1 Add `review_redundancy_pair` (normalize pair order, validate rules and decision, strip private tags, upsert)
- [ ] 2.2 Register it through `_security_pattern` and add it to `TOOL_ACCESS_LEVELS` as `write`
- [ ] 2.3 Make `find_redundant_rules` hide dismissed pairs and mark confirmed ones; add `include_reviewed`

## 3. Verify

- [ ] 3.1 Test migration 007 → 008 with existing data: every existing row unchanged, `user_version = 8`
- [ ] 3.2 Test constraints, upsert and report filtering
- [ ] 3.3 Confirm `rules`, `lessons` and `.md` files are byte-identical after any review call
- [ ] 3.4 Document the table and allowed values in README §3.2 and `docs/04-data-model.md`
