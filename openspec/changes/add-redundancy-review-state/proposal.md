## Why

`add-redundancy-detection` (TICKET-014) recomputes its report on every call, so a pair a curator already judged to be a false positive comes back every time and the report loses its value (TICKET-023).

## What Changes

- Add the table `redundancy_reviews` (migration `008`, additive) that stores a curator decision (`dismissed` | `confirmed`) per rule pair.
- Add a write-level tool `review_redundancy_pair` to record or replace that decision.
- `find_redundant_rules` hides dismissed pairs by default and marks confirmed ones.
- Nothing in `rules`, `lessons` or any `.md` file is modified.

## Capabilities

### New Capabilities
- `redundancy-review`: persisted curator decisions on candidate redundant rule pairs.

## Impact

- New table and migration 008; `schema.sql` updated
- New tool, access level `write` in `TOOL_ACCESS_LEVELS`
- `find_redundant_rules` gains an `include_reviewed` parameter (default `false`)
- Depends on `add-redundancy-detection`
