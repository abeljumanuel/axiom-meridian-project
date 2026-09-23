## ADDED Requirements

### Requirement: Windows one-line install
The system SHALL provide a PowerShell installer that installs Meridian and registers at least one detected MCP client via a single `irm ... | iex` command on Windows.

#### Scenario: Fresh Windows install
- **WHEN** a user runs the one-line `irm ... | iex` command on a clean Windows + Python 3.11 environment
- **THEN** the install succeeds and at least one detected MCP client (Claude Code, VSCode, OpenCode, or Kimi CLI) is registered

### Requirement: Client auto-detection parity with the Unix installer
The system SHALL detect the same set of MCP clients on Windows that `scripts/install.sh` detects on Linux/macOS.

#### Scenario: Multiple clients present
- **WHEN** more than one supported client is present on the machine
- **THEN** the installer registers Meridian with each detected client, consistent with `install.sh`'s behavior
