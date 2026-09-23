## Context

`semantic-search` currently ranks `query_rules`/`query_lessons` by similarity against `bge-small-en-v1.5` embeddings when available, falling back to SQL filtering otherwise. This is adequate at low entry counts but is expected to degrade as scopes accumulate more rules/lessons, and offers weak non-English retrieval.

## Goals / Non-Goals

**Goals:**
- Improve retrieval quality (and multilingual coverage) without touching the public tool contract.
- Keep the fallback-to-SQL behavior intact.

**Non-Goals:**
- Changing `query_rules`/`query_lessons` signatures or response shape.
- Migrating the SQLite schema.

## Decisions

### Decision 1: Benchmark before committing to a model/store swap
Migrate only if a documented benchmark on a representative rule set shows a measurable retrieval-quality improvement over `bge-small-en-v1.5`. This is an evaluate-then-adopt change, not a guaranteed swap.

### Decision 2: Keep the embedding/vector-store layer behind the existing internal interface
Whatever model or store is chosen, it sits behind the same internal abstraction `generate_embeddings` and the query path already use, so the change is isolated from the tool surface.

## Risks / Trade-offs

- `bge-m3` is a larger model (567M params); local inference cost/latency must be measured, not assumed acceptable.
- Introducing LanceDB/Qdrant local adds an operational dependency that the current pure-SQLite setup avoids; the benchmark should weigh this against the quality gain.
