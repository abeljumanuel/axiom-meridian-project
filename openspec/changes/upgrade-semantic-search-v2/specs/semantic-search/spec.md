## MODIFIED Requirements

### Requirement: Hybrid semantic ranking with SQL fallback
The system SHALL rank `query_rules`/`query_lessons` results by similarity when embeddings exist for the relevant scopes and free-text `query_text` is provided, and SHALL fall back to SQL filtering with no error and no signature change when embeddings don't exist. The embedding model and vector store used to compute similarity SHALL be swappable without changing tool signatures or the SQLite schema.

#### Scenario: Query with embeddings available
- **WHEN** `query_text` is provided and embeddings exist for the relevant scopes
- **THEN** results are ranked by semantic similarity

#### Scenario: Query without embeddings available
- **WHEN** `query_text` is provided and no embeddings exist for the relevant scopes
- **THEN** the same call falls back to SQL filtering with no error and no change to the tool signature

#### Scenario: Embedding model or vector store upgrade preserves the interface
- **WHEN** the embedding model is migrated to `BAAI/bge-m3` or the vector store is swapped to an alternative local store
- **THEN** `query_rules`/`query_lessons` signatures and the SQLite schema remain unchanged
