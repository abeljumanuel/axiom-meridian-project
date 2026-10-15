# rag-optional-dependency Specification

## Purpose
TBD - created by archiving change improve-installation-and-distribution. Update Purpose after archive.
## Requirements
### Requirement: RAG libraries are an opt-in extra
`torch`, `sentence-transformers`, and `chromadb` SHALL be declared under
`[project.optional-dependencies] rag` in `pyproject.toml`, not under the
top-level `dependencies` list.

#### Scenario: Installing without the extra
- **WHEN** a user runs `pip install axiom-meridian` (or
  `uvx --from axiom-meridian meridian mcp`) without specifying the `rag`
  extra
- **THEN** `torch`, `sentence-transformers`, and `chromadb` are not
  installed, and the installed package size reflects their absence

#### Scenario: Installing with the extra
- **WHEN** a user runs `pip install "axiom-meridian[rag]"`
- **THEN** `torch`, `sentence-transformers`, and `chromadb` are installed
  alongside the base package

### Requirement: Server starts without the RAG extra installed
The MCP server SHALL start successfully, over both stdio and HTTP/SSE
transports, when the `rag` extra is not installed.

#### Scenario: stdio startup without RAG
- **WHEN** `meridian mcp` is run in an environment without `torch`,
  `sentence-transformers`, or `chromadb` installed
- **THEN** the server starts and accepts MCP connections without
  raising `ImportError` or any other exception during startup

#### Scenario: HTTP/SSE startup without RAG
- **WHEN** `meridian serve <port>` is run in an environment without the
  `rag` extra installed
- **THEN** the server starts, prints its session token, and accepts
  HTTP connections without raising an exception during startup

### Requirement: Embedder warm-up is a safe no-op without RAG
`embedder.warm_up_in_background()` SHALL check whether the RAG extra is
importable — without importing the libraries themselves, so the check
adds no measurable startup cost — before starting its background
thread, and SHALL skip
starting the thread (logging at INFO level) when it is not, instead of
letting an `ImportError` escape on the background thread or at server
startup.

#### Scenario: Warm-up skipped without RAG
- **WHEN** `warm_up_in_background()` is called in an environment without
  the `rag` extra installed
- **THEN** no background thread is started, no exception is raised, and
  an INFO-level log line states that the RAG extra is not installed and
  warm-up was skipped

#### Scenario: Warm-up proceeds with RAG installed
- **WHEN** `warm_up_in_background()` is called in an environment with the
  `rag` extra installed
- **THEN** behavior is unchanged from before this capability: a daemon
  background thread starts loading the embedding model

### Requirement: RAG-dependent tools return a structured error, not a traceback
Any tool or code path whose execution strictly requires the RAG extra (`generate_embeddings`, and any future RAG-only tool) SHALL return a structured `RAG_NOT_INSTALLED` error response when the extra is not installed — following the same "caught exception → serialized error response" pattern `server.py` already uses for `AccessDeniedError` — rather than propagating a raw `ModuleNotFoundError`/`ImportError`.

#### Scenario: generate_embeddings without RAG installed
- **WHEN** `generate_embeddings` is invoked in an environment without
  the `rag` extra installed
- **THEN** the tool returns a JSON response with
  `"error": "RAG_NOT_INSTALLED"` and a `message` field containing the
  pip install command for the `rag` extra, and no traceback is raised
  to the MCP client

#### Scenario: generate_embeddings no longer reports a missing extra as embedding failures
- **WHEN** `generate_embeddings` is invoked without the `rag` extra and
  there are un-embedded active rules
- **THEN** the response is the `RAG_NOT_INSTALLED` error, not a
  `{"processed": 0, "errors": <N>}` result, and no `ERROR`-level
  traceback is logged

#### Scenario: generate_embeddings with RAG installed
- **WHEN** `generate_embeddings` is invoked in an environment with the
  `rag` extra installed
- **THEN** behavior is unchanged from before this capability

### Requirement: Post-commit vector-store hooks skip quietly without RAG
The post-commit embed/remove steps run by `approve_proposal`, the deprecate-proposal path, and `promote_rule` SHALL skip without logging an exception when the `rag` extra is not installed, and SHALL report the skipped step as `null` (not applicable) rather than `false` (failed) in the tool's response; the approval, deprecation, or promotion itself SHALL succeed exactly as with RAG installed.

#### Scenario: Approving a proposal without RAG installed
- **WHEN** `approve_proposal` approves a `new` proposal in an
  environment without the `rag` extra installed
- **THEN** the rule/lesson is written to the `.md` file and SQLite, the
  response has `"embedded": null`, and no `ERROR`-level log record is
  emitted

#### Scenario: Approving a proposal with RAG installed
- **WHEN** `approve_proposal` approves a proposal with the `rag` extra
  installed
- **THEN** `embedded` is `true` on success or `false` on an embedding
  failure, unchanged from before this capability

### Requirement: query_rules/query_lessons semantic search degrades to SQL without RAG
`query_rules` and `query_lessons` SHALL continue to fall back to plain SQL filtering when called with a `query_text` (semantic search) parameter, with no exception raised, whether the `rag` extra is absent or simply has no embeddings generated yet.

#### Scenario: Semantic query without RAG installed
- **WHEN** `query_rules` is called with a non-null `query_text` in an
  environment without the `rag` extra installed
- **THEN** the call returns SQL-filtered results (not a semantic-search
  error), with the same shape as a call with `query_text=None`

#### Scenario: Semantic query with RAG installed but no embeddings generated
- **WHEN** `query_rules` is called with a non-null `query_text` in an
  environment with the `rag` extra installed but `generate_embeddings`
  has never been run
- **THEN** the call returns SQL-filtered results, matching existing
  (pre-change) behavior

