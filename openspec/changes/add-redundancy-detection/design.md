## Context

Rules and lessons already carry embeddings when `semantic-search` has been populated for a scope. Redundancy detection reuses those embeddings rather than introducing a second embedding pipeline.

## Goals / Non-Goals

**Goals:**
- Surface likely-duplicate/overlapping rule pairs across scopes as a report a curator can act on.

**Non-Goals:**
- Automatic merging, deprecation, or rewriting of rules — this capability never writes.
- Cross-language duplicate detection beyond whatever the underlying embedding model already supports.

## Decisions

### Decision 1: Report-only, curator-facing output
Clustering surfaces candidates above a similarity threshold; a human curator decides whether and how to resolve them (e.g. via `promote_rule`, `edit_proposal`, or manual deprecation) — this capability does not itself modify `rules`/`lessons`.

### Decision 2: Reuse existing embeddings rather than a separate model
Depends on `semantic-search` embeddings already existing for a scope; if none exist, the report SHALL return an empty result rather than triggering embedding generation as a side effect.

## Risks / Trade-offs

- Quality depends entirely on `semantic-search`'s embedding coverage; scopes without embeddings yield no candidates.
- Similarity threshold tuning is a trade-off between false positives (noisy report) and false negatives (missed duplicates); acceptance criteria require the threshold to be configurable.
