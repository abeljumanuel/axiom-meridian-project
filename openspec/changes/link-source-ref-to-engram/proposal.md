## Why

Where Engram (episodic session memory) is present alongside Meridian, a rule or lesson's `source_ref` currently has no way to resolve to the Engram observation that originated it, losing cross-tool traceability (TICKET-016).

## What Changes

- Allow `source_ref` to optionally resolve to an Engram `observation_id`.
- `get_rule_context` can optionally surface the linked observation.
- Meridian SHALL function identically with Engram absent — no hard dependency is introduced.

## Capabilities

### Modified Capabilities
- `scoped-knowledge-consumption`: `get_rule_context` can surface a linked Engram observation when present.

## Impact

- `get_rule_context` implementation
- New `source_ref` resolution helper (soft dependency on Engram, no-op when absent)
