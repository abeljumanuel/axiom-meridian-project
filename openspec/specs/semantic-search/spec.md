# Semantic Search Specification

## Purpose
Let agents find relevant rules and lessons by meaning, not just exact tag matches, with a graceful fallback when no embeddings exist for the relevant scope.

## Requirements

### Requirement: Hybrid semantic ranking with SQL fallback
The system SHALL rank `query_rules`/`query_lessons` results by similarity when embeddings exist for the relevant scopes and free-text `query_text` is provided, and SHALL fall back to SQL filtering with no error and no signature change when embeddings don't exist.

#### Scenario: Query with embeddings available
- **WHEN** `query_text` is provided and embeddings exist for the relevant scopes
- **THEN** results are ranked by semantic similarity

#### Scenario: Query without embeddings available
- **WHEN** `query_text` is provided and no embeddings exist for the relevant scopes
- **THEN** the same call falls back to SQL filtering with no error and no change to the tool signature
