## ADDED Requirements

### Requirement: Read-only dashboard
The dashboard SHALL be read-only: no code path SHALL call any write-level tool (`approve_proposal`, `index_*`, `promote_rule`, `generate_embeddings`, ...), and it SHALL run and render correctly against a populated `KNOWLEDGE_BASE_PATH` with zero changes to `meridian.db` or any `.md` file.

#### Scenario: Dashboard renders without side effects
- **WHEN** the dashboard is run against a populated `KNOWLEDGE_BASE_PATH`
- **THEN** it renders correctly
- **AND** `meridian.db` and every `.md` file remain unchanged

### Requirement: Dashboard content
The dashboard SHALL show server/process health, the resolved scope hierarchy, active/deprecated rule and lesson counts per scope, pending proposals awaiting review, and a rendered usage manual generated from existing docs.

#### Scenario: View dashboard contents
- **WHEN** a curator or admin opens the dashboard
- **THEN** it shows server/process health, the scope hierarchy tree, active/deprecated rule and lesson counts per scope, pending proposals, and a rendered usage manual sourced from `docs/`/README rather than duplicated by hand

### Requirement: Separate process, localhost-bound
The dashboard SHALL run as a separate local process from the MCP server, reusing the existing `knowledge_consumption` functions as a library rather than speaking the MCP protocol, and SHALL bind to `127.0.0.1` by default.

#### Scenario: Dashboard process isolation and binding
- **WHEN** the dashboard starts
- **THEN** it runs as a process separate from the MCP server, calls the existing consumption functions directly as a library, and binds only to `127.0.0.1` by default

### Requirement: Embedding projector
The dashboard SHALL provide an embedding projector view that reads existing rule/lesson vectors from ChromaDB, reduces them to 2D or 3D via a dimensionality-reduction method (e.g. PCA, t-SNE, or UMAP), and renders them as an interactive, hoverable scatter plot colored by a selectable facet (scope, category/area, or severity). It SHALL NOT trigger embedding generation as a side effect.

#### Scenario: View the projector with embeddings present
- **WHEN** a curator opens the embedding projector for a scope that has embeddings in ChromaDB
- **THEN** the dashboard renders a 2D/3D scatter plot of those vectors, colored by the selected facet, with hover text showing the rule/lesson's identifier and short text

#### Scenario: View the projector with no embeddings present
- **WHEN** a curator opens the embedding projector for a scope that has no embeddings in ChromaDB
- **THEN** the dashboard shows an empty-state message instead of an error, and does not call `generate_embeddings` or any other write-level tool

#### Scenario: Facet switch re-colors without recomputing the projection
- **WHEN** a curator switches the color facet (e.g. from scope to severity)
- **THEN** the existing 2D/3D coordinates are re-colored without recomputing the dimensionality reduction
