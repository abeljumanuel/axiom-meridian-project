## ADDED Requirements

### Requirement: Claude Code plugin bundles the MCP server and the skill
A Claude Code plugin directory SHALL exist with a valid
`.claude-plugin/plugin.json` manifest, a `.mcp.json` declaring the
Meridian MCP server launched via `uvx`, and a `skills/meridian/SKILL.md`
whose content matches `distribution/skill/meridian/SKILL.md`.

#### Scenario: Plugin validates
- **WHEN** `claude plugin validate` is run against the plugin directory
- **THEN** it reports no errors for `plugin.json` or `.mcp.json`

#### Scenario: Plugin installs and exposes the server
- **WHEN** the plugin is installed in a Claude Code session
- **THEN** running `/mcp` shows the Meridian server as connected under
  the plugin's namespace

#### Scenario: Plugin skill content matches the standalone skill
- **WHEN** `skills/meridian/SKILL.md` inside the plugin is compared to
  `distribution/skill/meridian/SKILL.md`
- **THEN** their instructional content is identical

### Requirement: MCP Registry entry describes the published package
A `server.json` file SHALL exist at the repository root, conforming to
the current MCP Registry server.json schema, identifying the PyPI
package, the `uvx` runtime hint, and the stdio transport.

#### Scenario: server.json validates against the schema
- **WHEN** `server.json` is validated against the schema referenced by
  its `$schema` field
- **THEN** validation succeeds with no schema errors

#### Scenario: server.json points at the current repository
- **WHEN** `server.json` is inspected
- **THEN** `name` is `io.github.abeljumanuel/axiom-meridian` and
  `repository.url` is `https://github.com/abeljumanuel/axiom-meridian-project`

#### Scenario: server.json references the published package
- **WHEN** `server.json`'s `packages` array is inspected
- **THEN** it contains an entry with `registryType: "pypi"`,
  `identifier: "axiom-meridian"`, and `runtimeHint: "uvx"`

### Requirement: Registration in the MCP Registry is a manual task
Submitting `server.json` to the MCP Registry SHALL be documented as a
manual maintainer action requiring proof of GitHub repository
ownership, and SHALL NOT be automated by this change.

#### Scenario: Registration requires manual proof of ownership
- **WHEN** the maintainer submits `server.json` to the MCP Registry
- **THEN** the registry requires proof of ownership of the
  `io.github.abeljumanuel` namespace before accepting the entry, and no
  CI workflow in this change attempts that submission automatically

#### Scenario: PyPI package carries the registry ownership marker
- **WHEN** the published `axiom-meridian` release's PyPI description is
  inspected
- **THEN** it contains `mcp-name: io.github.abeljumanuel/axiom-meridian`,
  matching `server.json`'s `name`, so the registry's package-ownership
  verification succeeds

### Requirement: Distribution manifests stay version-synced
`plugin.json`'s `version`, `server.json`'s `version` and `packages[0].version`, and `src/meridian/__init__.py`'s `__version__` SHALL match `pyproject.toml`'s `version`, enforced by an automated check.

#### Scenario: Version mismatch fails the check
- **WHEN** any one of those versions differs from `pyproject.toml`'s
- **THEN** the version-sync check exits non-zero naming the mismatched file
