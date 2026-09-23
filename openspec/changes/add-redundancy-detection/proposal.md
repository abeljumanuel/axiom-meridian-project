## Why

As the rule set grows across scopes, near-duplicate or overlapping rules accumulate — e.g. the same constraint re-authored slightly differently in two projects. Nothing today surfaces these for a curator to review (TICKET-014).

## What Changes

- Cluster rules by embedding similarity and produce a curator-facing report of candidate duplicate/overlapping rule pairs above a similarity threshold.
- No automatic merge or write — the report is informational only.

## Capabilities

### New Capabilities
- `redundancy-detection`: curator-facing report of likely-duplicate or overlapping rules across scopes, based on embedding similarity clustering.

## Impact

- New read-only tool built on existing embeddings (from `semantic-search`)
- No schema writes; no change to existing tool signatures
