## Context

`scripts/install.sh` is the existing Linux/macOS installer: it detects installed MCP clients and registers Meridian with each one it finds. Windows users are currently unsupported and must follow manual steps.

## Goals / Non-Goals

**Goals:**
- Match `install.sh`'s behavior on Windows: same client set, same one-line install ergonomics (`irm ... | iex`).

**Non-Goals:**
- Rewriting `install.sh` itself, or changing which clients are supported on Unix.
- Packaging Meridian as a signed `.exe`/MSI — a PowerShell script is sufficient parity with the existing shell script.

## Decisions

### Decision 1: PowerShell script, not a rewrite of the Unix installer's logic in a cross-platform language
Keep `install.sh` and `install.ps1` as separate, platform-native scripts rather than introducing a cross-platform runtime dependency (e.g. Node/Python) just for installation. This matches the zero-dependency, single-command philosophy of the existing installer.

## Risks / Trade-offs

- Two install scripts must be kept in sync as client-detection logic evolves; acceptance criteria below cover parity, but drift is possible over time.
