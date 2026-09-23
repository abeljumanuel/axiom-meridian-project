## 1. Clustering

- [ ] 1.1 Implement similarity clustering over existing rule embeddings (per scope or cross-scope)
- [ ] 1.2 Make the similarity threshold configurable

## 2. Reporting tool

- [ ] 2.1 Add a read-only tool that returns candidate duplicate/overlapping pairs above the threshold
- [ ] 2.2 Return an empty result (no side effect) for scopes without embeddings

## 3. Verify

- [ ] 3.1 Confirm the report never writes to `rules`/`lessons`
- [ ] 3.2 Validate against a known set of intentionally duplicated rules to confirm recall at the default threshold
