# pypi-packaging Specification

## Purpose
TBD - created by archiving change improve-installation-and-distribution. Update Purpose after archive.
## Requirements
### Requirement: Complete package metadata
`pyproject.toml`'s `[project]` table SHALL include complete metadata for
PyPI publication: `authors` (with a legal name alongside "Axiom JUMA"),
`urls` (homepage, repository, issues), `classifiers`, and `keywords`, in
addition to the existing `name`, `version`, `description`, `readme`,
`requires-python`, and `license` fields.

#### Scenario: Metadata present for build
- **WHEN** `uv build` is run against the updated `pyproject.toml`
- **THEN** the resulting wheel and sdist metadata (`PKG-INFO` /
  `METADATA`) include non-empty `Author`, `Project-URL`, `Classifier`,
  and `Keywords` fields

### Requirement: uvx-based install target documented and functional
The package SHALL be installable and runnable via
`uvx --from axiom-meridian meridian mcp` once published to PyPI, with
documented equivalents for VS Code, OpenCode, Kimi CLI, and Cursor MCP
client configuration.

#### Scenario: uvx runs the MCP server
- **WHEN** a user with `uv` installed runs
  `uvx --from axiom-meridian meridian mcp` against a published release
- **THEN** the MCP server starts over stdio, with no prior `git clone`
  or manual dependency install

#### Scenario: Per-client config documented
- **WHEN** a user reads the MCP configuration documentation for VS Code,
  OpenCode, Kimi CLI, or Cursor
- **THEN** each client's documented config uses the `uvx --from
  axiom-meridian meridian mcp` invocation (or that client's equivalent
  syntax for an ephemeral `uv`-run command) instead of a path to a local
  clone's venv

### Requirement: Tag-triggered release workflow using Trusted Publishing
A GitHub Actions workflow SHALL build the package and publish it to
PyPI using Trusted Publishing (OpenID Connect token exchange, no stored
PyPI API token as a repository secret), triggered on pushing a version
tag matching `v*`.

#### Scenario: Tag push triggers the workflow
- **WHEN** a tag matching `v*` (e.g. `v0.2.0`) is pushed to the
  repository
- **THEN** the release workflow runs, builds the package with `uv build`,
  and attempts to publish to PyPI via the trusted-publishing action with
  `id-token: write` permission and no username/password/token secret
  referenced in the workflow file

#### Scenario: Trusted Publisher bound to the new repository
- **WHEN** the release workflow runs from `abeljumanuel/axiom-meridian-project`
- **THEN** PyPI accepts the OIDC token because the project's Trusted
  Publisher is configured for that repository and `release.yml`; a run
  from the old `abeljumanuel/axiom-meridian` repository is rejected

#### Scenario: Workflow does not run on other pushes
- **WHEN** a commit is pushed to `main` without an accompanying `v*` tag
- **THEN** the release workflow does not run

### Requirement: Manual tasks are explicit and not automated
Creating the PyPI account/project, configuring Trusted Publishing on PyPI's side, and executing the first release SHALL be documented as manual maintainer actions, and the workflow SHALL NOT attempt to create the PyPI project or configure its trusted publisher itself.

#### Scenario: First publish requires manual setup
- **WHEN** the release workflow runs against a PyPI project that has not
  yet had Trusted Publishing configured for it
- **THEN** the publish step fails with an authentication/authorization
  error from PyPI, and the workflow does not attempt any fallback
  credential method

