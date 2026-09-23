## Why

`scripts/install.sh` covers Linux/macOS with a one-line install and automatic MCP client detection. Windows currently has no equivalent — users must install Meridian manually, which is friction the project has already removed for other platforms (TICKET-012).

## What Changes

- Add a PowerShell installer (`scripts/install.ps1`) mirroring `install.sh`'s behavior: client auto-detection (Claude Code, VSCode, OpenCode, Kimi CLI) and a one-line `irm ... | iex` install.

## Capabilities

### New Capabilities
- `installation`: one-line, cross-platform install of the Meridian MCP server with automatic client registration.

## Impact

- New file: `scripts/install.ps1`
- README / install docs: add the Windows one-line command alongside the existing Unix one
