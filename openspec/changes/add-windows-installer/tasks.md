## 1. Installer script

- [ ] 1.1 Write `scripts/install.ps1` covering: Python 3.11 detection, Meridian install, MCP client auto-detection (Claude Code, VSCode, OpenCode, Kimi CLI)
- [ ] 1.2 Register Meridian with each detected client, mirroring `install.sh`'s registration steps

## 2. Distribution

- [ ] 2.1 Host `install.ps1` such that `irm <url> | iex` works as a one-liner
- [ ] 2.2 Add the Windows one-line command to the README / install docs

## 3. Verify

- [ ] 3.1 Run the one-liner on a clean Windows + Python 3.11 environment and confirm at least one client is registered
- [ ] 3.2 Confirm behavior parity with `install.sh` on a machine with multiple supported clients installed
