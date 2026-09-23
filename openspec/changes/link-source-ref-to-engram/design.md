## Context

`get_rule_context` (part of `scoped-knowledge-consumption`) already returns a rule's full text, history, and linked lessons. Rules/lessons carry a `source_ref` field, currently opaque outside Meridian. Engram, where present, keeps its own episodic `observation_id` records that may be the true origin of a rule.

## Goals / Non-Goals

**Goals:**
- Let `get_rule_context` surface the linked Engram observation when `source_ref` resolves to one and Engram is present.
- Keep Meridian fully functional, with identical behavior, when Engram is absent.

**Non-Goals:**
- Introducing a hard dependency on Engram (import failures, required config, etc. if Engram is not installed).
- Writing to Engram, or changing how `source_ref` is populated at proposal-approval time.

## Decisions

### Decision 1: Soft dependency via optional resolution
`source_ref` resolution against Engram is attempted only if Engram is importable/configured; any failure or absence results in the field simply being omitted, not an error.

## Risks / Trade-offs

- Coupling `get_rule_context`'s response shape to an optional external system risks silent divergence between "Engram absent" and "Engram present but resolution failed" if error handling isn't precise — both must produce the same omitted-field outcome.
