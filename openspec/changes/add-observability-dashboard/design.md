## Context

Meridian's MCP tools are agent-facing. There is no human-facing view of the knowledge base's current state today; a curator has to query tools manually or inspect `meridian.db`/`.md` files directly.

## Goals / Non-Goals

**Goals:**
- Give humans a read-only visual view of server health, scope hierarchy, rule/lesson counts, and pending proposals, without duplicating the knowledge-governance logic.

**Non-Goals:**
- Any write path — this is explicitly out of scope, not just unimplemented.
- Being part of the MCP protocol surface — it is a separate process/stack, and explicitly a deferred, optional companion to the core capstone deliverable.

## Decisions

### Decision 1: Separate process, shared library
The dashboard imports and calls the existing `knowledge_consumption` functions as a Python library rather than going through the MCP protocol, keeping the MCP server's tool surface untouched.

### Decision 2: Read-only by construction
No dashboard code path calls a write-level tool (`approve_proposal`, `index_*`, `promote_rule`, `generate_embeddings`, ...); this is enforced by only importing read-level functions, not by a runtime permission check.

### Decision 3: Manual/usage view generated from existing docs
The rendered usage manual is generated from `docs/`/README rather than duplicated by hand, so it can't drift from the source documentation.

### Decision 4: Embedding projector reads existing vectors, computes projection at request time
The projector queries ChromaDB's `meridian_rules`/`meridian_lessons` collections for a scope's existing 384-dim `BAAI/bge-small-en-v1.5` vectors (see [System Architecture § Tech Stack](../../../docs/03-system-architecture.md)) and reduces them to 2D/3D on the server at request time (or cached briefly) — no separate embedding index is built, and no embeddings are generated on the dashboard's behalf. UMAP is preferred over t-SNE as the default (deterministic-enough, faster on repeat runs, better global structure preservation); PCA is offered as a cheap fallback when the vector count is very small. This gives the same curator a visual read of the redundancy problem that `redundancy-detection`'s numeric report gives, using the same underlying vectors.

## Risks / Trade-offs

- Adds a second stack (HTTP API + frontend + its own auth/testing surface) for a capability outside the core capstone scope — hence deferred, and only pursued if time remains after the core backlog (TICKET-012 through TICKET-016).
- Dimensionality reduction (t-SNE/UMAP) is stochastic and can mislead if over-interpreted as exact distance; the UI should present it as an exploratory aid, not ground truth, and avoid recomputing the projection on every minor interaction (see facet-switch scenario).
- Projecting a very large number of vectors client-side can hurt render performance; acceptance criteria should cap or paginate rendered points if a scope's embedding count grows large.
