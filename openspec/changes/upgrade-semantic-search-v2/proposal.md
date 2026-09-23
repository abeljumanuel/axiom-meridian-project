## Why

As the rule/lesson volume grows past roughly 1,000 entries, or when more accurate multilingual retrieval is needed, the current `bge-small-en-v1.5` embedding model and local vector store may no longer give strong-enough ranking quality for `semantic-search` (TICKET-013).

## What Changes

- Evaluate migrating the embedding model to `BAAI/bge-m3` (567M params, 100+ languages).
- Evaluate alternative local vector stores (LanceDB, Qdrant local) as a drop-in replacement for the current store.
- No changes to tool signatures or the SQLite schema.

## Capabilities

### Modified Capabilities
- `semantic-search`: the embedding model and vector store become swappable without changing `query_rules`/`query_lessons` call signatures.

## Impact

- `generate_embeddings` internals, vector store adapter
- New benchmark artifact documenting retrieval-quality comparison against `bge-small-en-v1.5`
