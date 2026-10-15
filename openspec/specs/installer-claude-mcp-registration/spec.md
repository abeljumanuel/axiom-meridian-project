# Installer Claude MCP Registration Specification

## Purpose
Detect and report existing Claude Code MCP registrations accurately during installation, including venv mismatches.
## Requirements
### Requirement: Detecting an existing Claude Code registration matches the real `claude mcp list` output format
Claude Code registration — now performed by `meridian setup` (invoked directly or by `scripts/install.sh`) — SHALL detect an existing `meridian` registration by matching `claude mcp list`'s actual plain-text output format (`name: command - status`, unquoted), and SHALL NOT attempt to re-add a registration that already exists.

#### Scenario: Meridian already registered
- **WHEN** `claude mcp list` includes a line starting with `meridian:`
- **THEN** `meridian setup` does not call `claude mcp add` and does not print a "Could not add to Claude Code" failure

#### Scenario: Meridian not yet registered
- **WHEN** `claude mcp list` includes no line starting with `meridian:`
- **THEN** `meridian setup` calls `claude mcp add` to register the command it resolved for this install

### Requirement: A venv mismatch in an existing registration is surfaced, not silently ignored or falsely claimed
When Meridian is already registered in Claude Code, `meridian setup` SHALL compare the registered command against the command it resolved for this install (the `bin/` directory of a persistent `meridian` binary, or the full `uvx --from axiom-meridian ... meridian mcp` invocation) and SHALL warn with the exact remediation commands only when they genuinely differ — not when the registration uses an equivalent invocation of the same install.

#### Scenario: Existing registration uses the same install via a different invocation
- **WHEN** the existing registration invokes `python -m meridian mcp` from the same `bin/` directory as the resolved `meridian` binary, rather than the `meridian` entry point itself
- **THEN** no mismatch warning is printed

#### Scenario: Existing registration points at a different install
- **WHEN** the existing registration's command does not match the resolved command's install (e.g. a legacy `~/.meridian/venv/bin/meridian` while this install is a `uv tool install`)
- **THEN** a warning is printed naming the currently-registered command and the exact `claude mcp remove`/`claude mcp add` commands to switch it to this install

