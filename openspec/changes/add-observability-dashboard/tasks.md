## 1. API layer

- [ ] 1.1 Stand up a thin FastAPI layer that imports and calls read-level `knowledge_consumption` functions (`query_rules`, `query_lessons`, `get_project_scope_resolution`, `get_rule_audit_log`, `list_pending_proposals`)
- [ ] 1.2 Bind to `127.0.0.1` by default

## 2. Frontend

- [ ] 2.1 Build a minimal frontend (server-rendered templates or HTMX) showing server/process health, scope hierarchy, rule/lesson counts, and pending proposals
- [ ] 2.2 Render the usage manual from `docs/`/README rather than duplicating content by hand

## 3. Embedding projector

- [ ] 3.1 Add an endpoint that reads a scope's vectors from ChromaDB (`meridian_rules`/`meridian_lessons`) without generating embeddings
- [ ] 3.2 Implement server-side dimensionality reduction (UMAP default, PCA fallback for very small vector counts) to 2D/3D
- [ ] 3.3 Render an interactive scatter plot with hover text (rule/lesson ID + short text) and a facet selector (scope, category/area, severity) that re-colors without recomputing the projection
- [ ] 3.4 Render an empty-state message (not an error) when a scope has no embeddings
- [ ] 3.5 Cap or paginate rendered points for scopes with a large embedding count

## 4. Verify

- [ ] 4.1 Confirm no code path in the dashboard imports or calls a write-level tool, including the projector
- [ ] 4.2 Run the dashboard against a populated `KNOWLEDGE_BASE_PATH` and confirm `meridian.db` and all `.md` files are unchanged afterward
- [ ] 4.3 Confirm the dashboard binds to `127.0.0.1` by default
- [ ] 4.4 Confirm the projector renders correctly for a scope with embeddings and shows the empty state for one without
