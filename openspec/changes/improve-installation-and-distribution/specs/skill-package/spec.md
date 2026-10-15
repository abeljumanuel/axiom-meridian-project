## ADDED Requirements

### Requirement: Skill teaches correct tool usage
The skill at `distribution/skill/meridian/SKILL.md` SHALL instruct an
agent on when to call `query_rules`, `query_lessons`, `audit_pr`,
`check_feature_against_rules`, and the proposal-review flow
(`list_pending_proposals`, `approve_proposal`, `reject_proposal`), with
enough context that an agent can decide which tool applies to a given
task without additional guidance.

#### Scenario: Agent reads the skill before a PR review task
- **WHEN** an agent with the skill loaded is asked to review a pull
  request diff
- **THEN** the skill's instructions direct it to call `audit_pr` with
  the diff and project ID, rather than leaving tool selection ambiguous

#### Scenario: Agent reads the skill before answering a "what are the rules for X" question
- **WHEN** an agent with the skill loaded is asked what the project's
  rules are for a given area
- **THEN** the skill's instructions direct it to call `query_rules`
  (or `query_lessons` for past incidents) rather than guessing from its
  own training data

### Requirement: Skill detects tool availability without side effects
The skill SHALL instruct the agent to check whether Meridian's MCP
tools are available using the agent's normal tool-discovery mechanism,
and SHALL NOT instruct the agent to make a network request, read an
environment variable, or execute a script to perform this check.

#### Scenario: Meridian tools are available
- **WHEN** an agent with the skill loaded has Meridian's MCP tools
  available in its current tool list
- **THEN** the skill's instructions lead the agent to use those tools
  directly

#### Scenario: Meridian tools are not available
- **WHEN** an agent with the skill loaded does not have Meridian's MCP
  tools available
- **THEN** the skill's instructions lead the agent to show the user the
  literal install command text, and the agent does not attempt to
  install, download, or execute anything on the user's behalf

#### Scenario: Tools exposed under a plugin prefix
- **WHEN** Meridian's tools are exposed with a plugin-specific prefix
  (e.g. `mcp__plugin_meridian_meridian__query_rules`) instead of
  `mcp__meridian__query_rules`
- **THEN** the skill's instructions still identify them as available,
  because they refer to tools by base name

### Requirement: Skill uses standard frontmatter
`SKILL.md` SHALL use standard skill frontmatter: a lowercase hyphenated `name` and a `description` stating what the skill does and when to use it, and SHALL NOT restrict tools via `allowed-tools` or carry the non-standard `metadata.allowed_tools` list used by `skill_generator.py`.

#### Scenario: Frontmatter check
- **WHEN** `SKILL.md`'s frontmatter is parsed
- **THEN** it has `name: meridian` and a non-empty `description`, and no
  `allowed_tools`/`allowed-tools` key

### Requirement: Skill package is safe for automated marketplace review
The `distribution/skill/meridian/` directory SHALL contain no script
with network access, no code that reads environment variables, no
obfuscated or encoded content, and no instructions phrased in a way
that could be interpreted as directing the agent to act against the
user's or marketplace's interest (prompt-injection-shaped content).

#### Scenario: No network-capable scripts
- **WHEN** every file under `distribution/skill/meridian/` is scanned
  for outbound network calls (`curl`, `wget`, `requests`, `urllib`,
  `http.client`, raw socket usage)
- **THEN** none are found in any script or instruction file

#### Scenario: No environment variable reads
- **WHEN** every file under `distribution/skill/meridian/` is scanned
  for environment variable access in code (`os.environ`, `process.env`,
  `getenv`, and `$VARNAME` inside script files or fenced shell blocks)
- **THEN** none are found (naming a variable in prose, e.g. that
  approvals need `MERIDIAN_ACCESS_LEVEL=write` on the server, is not a
  read and is allowed)

#### Scenario: No obfuscated content
- **WHEN** every file under `distribution/skill/meridian/` is inspected
  for base64-encoded blobs, minified/obfuscated code, or non-human-readable
  content
- **THEN** none is found — all content is plain, readable Markdown and
  (if any) plain, readable reference text

### Requirement: Skill is packaged as a zip
A task SHALL produce a zip archive of `distribution/skill/meridian/`
suitable for upload to a skill marketplace, generated on demand rather
than committed to version control.

#### Scenario: Building the zip
- **WHEN** the packaging task is run
- **THEN** it produces a zip file containing `SKILL.md` and its
  `references/` directory, with the same relative paths as
  `distribution/skill/meridian/`
