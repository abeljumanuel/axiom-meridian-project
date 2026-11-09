## Context

The redundancy report is derived data and has no memory. A curator decision is the only information in this feature that cannot be recomputed, so it is the only thing worth persisting.

## Goals / Non-Goals

**Goals:**
- Remember per rule pair whether a curator dismissed or confirmed it, with who and when.

**Non-Goals:**
- Merging, deprecating or editing rules from a decision. A confirmed pair is a signal; resolution still goes through `promote_rule`, `edit_proposal` or deprecation.
- Storing the full report or the similarity matrix.

## Decisions

### Decision 1: One canonical row per unordered pair
`CHECK (rule_a_id < rule_b_id)` plus `UNIQUE (rule_a_id, rule_b_id)`; the tool sorts the pair before writing. `(A, B)` and `(B, A)` are the same review.

### Decision 2: Additive migration only
Migration 008 creates one table with `CREATE TABLE IF NOT EXISTS` and touches nothing else, per ADR-007. Existing databases behave as before until the tool is used.

### Decision 3: Reviews are history, not rules
Deprecating a rule keeps its reviews. The report stops listing the pair because deprecated rules are skipped, not because the review is deleted.

### Decision 4: Write goes through the standard security pattern
`review_redundancy_pair` is registered through `_security_pattern`, requires access level `write`, strips private tags from `note`, and is logged in `access_log`.

## Risks / Trade-offs

- A dismissal can become stale if either rule is edited later; `similarity` and `decided_at` are stored so the report can flag it.
- A rule re-created under a new code loses its reviews. Accepted and documented.
- A released migration cannot be cleanly reverted (SQLite, ADR-007), so the table design is settled before the release.
