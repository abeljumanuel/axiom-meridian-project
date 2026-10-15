## ADDED Requirements

### Requirement: `meridian setup` runs cross-platform
`python -m meridian setup` (and the `meridian setup` entry point) SHALL
run on Linux, macOS, and Windows, performing MCP client detection,
knowledge-base creation, and client configuration using only
cross-platform Python operations (no shelling out to bash-specific
commands).

#### Scenario: Setup runs on Windows
- **WHEN** `meridian setup` is run on Windows with Python 3.11+ and the
  package installed
- **THEN** it completes without invoking any bash-only command and
  without requiring WSL or Git Bash

#### Scenario: Setup runs on Linux/macOS
- **WHEN** `meridian setup` is run on Linux or macOS
- **THEN** it performs the same detection and configuration steps as on
  Windows, using the same Python code path

### Requirement: Claude Code registration detection has no false negatives
`meridian setup`'s Claude Code detection SHALL correctly identify an
existing Meridian registration from `claude mcp list`'s actual output
format (plain `name: command - status` lines), and SHALL warn — rather
than silently proceed or silently skip — when an existing registration
points at a different installation than the one `meridian setup` is
currently configuring.

#### Scenario: Already registered, same install
- **WHEN** `meridian setup` runs and `claude mcp list` shows a
  `meridian:` entry whose command matches the command `meridian setup`
  would register (the absolute path of a persistent `meridian` on
  `PATH`, or the `uvx --from axiom-meridian ... meridian mcp`
  invocation)
- **THEN** `meridian setup` reports Meridian is already configured and
  does not attempt to re-add it or report a false mismatch

#### Scenario: Already registered, different install
- **WHEN** `meridian setup` runs and `claude mcp list` shows a
  `meridian:` entry whose command does not match the command
  `meridian setup` would register (e.g. an old
  `~/.meridian/venv/bin/meridian` from the previous `install.sh`)
- **THEN** `meridian setup` warns that Claude Code is configured against
  a different Meridian install and shows the exact commands to switch it

#### Scenario: Not yet registered
- **WHEN** `meridian setup` runs and `claude mcp list` shows no
  `meridian:` entry
- **THEN** `meridian setup` registers Meridian with Claude Code and
  reports success

### Requirement: Registered command survives uv cache cleanup
`meridian setup` SHALL NOT register a client command that points inside uv's cache (the interpreter or script path of a `uvx` ephemeral environment).

#### Scenario: Setup run through uvx with no persistent install
- **WHEN** `meridian setup` is run via `uvx --from axiom-meridian meridian setup`
  and no persistent `meridian` command is on `PATH`
- **THEN** the command registered with each client is
  `uvx --from axiom-meridian meridian mcp` (or the `[rag]` variant if the
  user opted in), not `sys.executable` or any path under the uv cache

### Requirement: Knowledge-base seeding never overwrites existing files
`meridian setup` SHALL skip seeding any destination file that already
exists (printing a warning naming the file) when it seeds the bundled
example knowledge base, rather than overwriting it.

#### Scenario: Destination file already exists
- **WHEN** `meridian setup` seeds the example knowledge base and a
  bundled example file's destination path already exists in the user's
  knowledge base
- **THEN** that file is left untouched, is not reindexed, and a warning
  naming the file and the reason it was skipped is printed

#### Scenario: Destination file does not exist
- **WHEN** `meridian setup` seeds the example knowledge base and a
  bundled example file's destination path does not yet exist
- **THEN** the file is copied and indexed exactly as before this change

#### Scenario: Seeding from a PyPI/uvx install
- **WHEN** `meridian setup` runs from an installed wheel with no repo
  clone on disk
- **THEN** the example knowledge base is read from the package's own
  bundled data and seeding behaves exactly as from a clone

### Requirement: `meridian doctor` diagnoses documented failure modes
`python -m meridian doctor` SHALL check for, and report on, each of the
installation issues currently documented in README's Troubleshooting
section: the `libpython` dylib path mismatch, a cloud-sync-corrupted
venv, a missing `meridian` entry point, and a stale `uv run`-based MCP
client configuration.

#### Scenario: Healthy install
- **WHEN** `meridian doctor` runs against a correctly configured
  installation
- **THEN** it reports each checked condition as healthy and exits with
  status 0

#### Scenario: Configured entry point missing
- **WHEN** `meridian doctor` runs and an MCP client is configured to
  launch a `meridian` binary path that does not exist or is not
  executable (or a `uvx` command while `uvx` is not on `PATH`)
- **THEN** it reports that specific failure with the remediation command
  (reinstalling the package or re-running `meridian setup`) and exits
  with a non-zero status

#### Scenario: Stale uv run configuration detected
- **WHEN** `meridian doctor` runs and an MCP client's config file
  references `uv run` instead of a direct binary/uvx invocation
- **THEN** it reports that configuration as a likely source of
  "command not found"-style errors and shows the corrected invocation

### Requirement: `install.sh` delegates to `meridian setup`
`scripts/install.sh` SHALL be rewritten to ensure `uv` is available and
then delegate MCP client configuration and knowledge-base setup to
`meridian setup`, rather than reimplementing that logic in bash.

#### Scenario: Fresh install via install.sh
- **WHEN** `scripts/install.sh` is run on a machine with no prior
  Meridian installation
- **THEN** it ensures `uv` is present, then invokes `meridian setup`,
  which performs client detection, KB creation, and configuration

#### Scenario: Re-running install.sh over an existing installation
- **WHEN** `scripts/install.sh` is run again over an existing
  `~/.meridian` installation
- **THEN** `meridian setup`'s already-configured detection and
  no-clobber seeding (per the requirements above) apply, and no data is
  overwritten
