## ADDED Requirements

### Requirement: README leads with one-line install
`README.md`'s Installation section SHALL present the `uvx`/PyPI-based
one-line install as the primary, first-shown path for Linux, macOS, and
Windows, with building from source presented as a clearly labeled
alternative for contributors and self-hosters who want an editable
install.

#### Scenario: One-line install shown first
- **WHEN** a reader opens README.md's Installation section
- **THEN** the first install instructions shown require no `git clone`
  step and work identically in form across Linux, macOS, and Windows

#### Scenario: Source install still documented
- **WHEN** a reader wants to contribute or run an editable install
- **THEN** README.md documents the `git clone` + `uv sync` + `uv pip
  install -e .` path under a clearly labeled "from source" section

### Requirement: Repository URLs are correct
Every URL in `README.md` SHALL point to `github.com/abeljumanuel/axiom-meridian-project` (or its `raw.githubusercontent.com` equivalent) wherever it references this project's GitHub repository, not `axiom-juma/meridian` or the old `abeljumanuel/axiom-meridian` repository.

#### Scenario: No stale URLs remain
- **WHEN** `README.md` is scanned for `axiom-juma` and for
  `github.com/abeljumanuel/axiom-meridian` /
  `raw.githubusercontent.com/abeljumanuel/axiom-meridian` not followed by
  `-project`
- **THEN** no occurrences are found

#### Scenario: Registry server name is not treated as a repository URL
- **WHEN** `README.md` contains the MCP Registry marker
  `mcp-name: io.github.abeljumanuel/axiom-meridian`
- **THEN** it is left unchanged — it is the registry server name, which
  intentionally keeps the `axiom-meridian` suffix

### Requirement: The `[rag]` extra is documented
`README.md` SHALL document the `rag` optional-dependency group:
what it enables (semantic/RAG search), how to install it
(`pip install "axiom-meridian[rag]"` or equivalent), and what behavior
to expect without it (SQL-only filtering, `RAG_NOT_INSTALLED` from
RAG-only tools).

#### Scenario: Extra documented near installation instructions
- **WHEN** a reader reads README.md's Installation section
- **THEN** they find an explicit mention of the `rag` extra, how to
  install it, and a one-sentence description of what functionality it
  adds

#### Scenario: RAG-not-installed behavior documented
- **WHEN** a reader reads README.md's Security or Tool Reference
  section (wherever `RAG_NOT_INSTALLED` is documented)
- **THEN** they find the structured error shape and which tools can
  return it, matching the `rag-optional-dependency` capability's
  behavior
