## 1. Benchmark harness

- [ ] 1.1 Assemble a representative rule set (multiple scopes, mixed English/non-English if available)
- [ ] 1.2 Benchmark current `bge-small-en-v1.5` retrieval quality on that set as the baseline

## 2. Model evaluation

- [ ] 2.1 Generate embeddings for the same set with `BAAI/bge-m3` and measure retrieval quality and inference latency
- [ ] 2.2 Document the comparison against the baseline

## 3. Vector store evaluation

- [ ] 3.1 Evaluate LanceDB and Qdrant local as alternative stores behind the existing internal interface
- [ ] 3.2 Document operational trade-offs (dependency footprint, query latency) versus the current store

## 4. Migration (only if benchmark justifies it)

- [ ] 4.1 Swap the embedding model / vector store behind the existing interface
- [ ] 4.2 Confirm `query_rules`/`query_lessons` signatures and the SQLite schema are unchanged
- [ ] 4.3 Regenerate embeddings for existing scopes

## 5. Verify

- [ ] 5.1 Confirm the benchmark shows a measurable quality improvement over `bge-small-en-v1.5`
- [ ] 5.2 Regression-test the SQL fallback path with embeddings absent
