-- Migration 007: drop the unused rule_lesson_links table (TICKET-022).
--
-- No code path ever inserted into it, so get_rule_context and
-- get_rule_timeline always read an empty set from it. The relationship
-- between a lesson and the rule it originated exists only as the
-- `**Originó regla:**` field of the lesson's Markdown block (the source of
-- truth), which was never copied to SQLite.
--
-- IF EXISTS: databases created after schema.sql dropped the table never had
-- it. rules.originated_lesson_id and lessons.originated_rule_id are left in
-- place (unused): SQLite cannot DROP COLUMN on a foreign-key column, and
-- rebuilding rules/lessons is not worth the risk on existing knowledge bases.

DROP TABLE IF EXISTS rule_lesson_links;
