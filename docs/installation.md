# Installation

Axiom Meridian is a Python package (`axiom-meridian`) that provides the
`meridian` command. Installing it and connecting it to your MCP clients takes
one or two commands on Linux, macOS, and Windows.

- [Requirements](#requirements)
- [Install](#install)
- [Semantic search (the `rag` extra)](#semantic-search-the-rag-extra)
- [Configuring MCP clients](#configuring-mcp-clients)
- [Upgrading](#upgrading)
- [Uninstalling](#uninstalling)
- [Install from source](#install-from-source)
- [Diagnostics: `meridian doctor`](#diagnostics-meridian-doctor)
- [Environment variables](#environment-variables)

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — it fetches
  a compatible Python (3.11+) on its own if your system one is older.
- At least one MCP client: Claude Code, Kimi CLI, OpenCode, VS Code, or
  Cursor (any other MCP client works with [manual configuration](#manual-configuration)).

## Install

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/abeljumanuel/axiom-meridian-project/main/scripts/install.sh | bash
```

The script installs uv if it is missing (after asking), runs
`uv tool install axiom-meridian`, then hands off to `meridian setup`, which
detects your MCP clients, asks before configuring each one, creates the
knowledge base, and offers to seed it with example rules. It finishes by
running `meridian doctor`.

Unattended options (environment variables): `RAG=1`/`RAG=0` (semantic search
on/off), `SEED_KB=1`/`SEED_KB=0` (example knowledge base), `SKIP_MCP=1` (skip
client configuration), `KNOWLEDGE_BASE_PATH=/path`, `DRY_RUN=1`.

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install axiom-meridian
meridian setup
```

No installer script is needed: `meridian setup` is plain Python and does the
same client detection and configuration on every OS.

### Claude Code plugin

The plugin bundles the server (launched through `uvx`) with a skill that tells
the agent when to use each Meridian tool:

```text
/plugin install meridian --marketplace abeljumanuel/axiom-meridian-project
```

Its server runs with the default `analyze` access level and the default
knowledge base location. To approve proposals from Claude Code, register the
server directly instead (below) with `MERIDIAN_ACCESS_LEVEL=write`.

### Any OS, step by step

```bash
uv tool install axiom-meridian      # persistent `meridian` command
meridian setup                      # configure clients + knowledge base
meridian doctor                     # check everything
```

`meridian setup` is safe to re-run: it never overwrites an existing
knowledge-base file or replaces a client registration that points at a
different install — it warns and prints the commands to switch instead.

Prefer not to keep anything installed? `uvx --from axiom-meridian meridian setup`
works too; clients are then registered to launch
`uvx --from axiom-meridian meridian mcp`.

## Semantic search (the `rag` extra)

Meridian works fully without machine-learning dependencies: queries filter by
scope, category, severity, and tags in SQLite. The optional `rag` extra adds
semantic ranking for free-text `query_text` searches, using
`sentence-transformers` (`BAAI/bge-small-en-v1.5`), `torch`, and `chromadb` —
roughly 900 MB.

```bash
uv tool install "axiom-meridian[rag]"          # or: RAG=1 with install.sh
uvx --from "axiom-meridian[rag]" meridian mcp  # uvx
pip install "axiom-meridian[rag]"              # pip
```

Without the extra:

- `query_rules` / `query_lessons` with `query_text` fall back to plain SQL
  filtering — same response shape, no error.
- `generate_embeddings` returns a structured error instead of running:

  ```json
  {"error": "RAG_NOT_INSTALLED", "message": "Semantic search requires the 'rag' extra. Install with: ..."}
  ```

- `approve_proposal`, deprecation approvals, and `promote_rule` still succeed;
  their `embedded` / `embedding_removed` fields are `null` ("not applicable")
  rather than `false` ("failed").
- The server skips its embedding-model warm-up at startup.

`meridian doctor` reports whether the extra is installed. After adding it to
an existing install, run `generate_embeddings` once to index existing rules.

## Configuring MCP clients

`meridian setup` writes these for you. They are listed here for manual setup
or review. `COMMAND` is the absolute path of the `meridian` binary (`which
meridian`; on Windows `where meridian`), or `uvx` with the arguments
`--from axiom-meridian meridian mcp` for a no-install setup.

All examples set `MERIDIAN_ACCESS_LEVEL=write` (needed to approve proposals);
omit it for the default `analyze` level. `KNOWLEDGE_BASE_PATH` is optional.

### Claude Code

```bash
claude mcp add -s user -e MERIDIAN_ACCESS_LEVEL=write -- meridian "$(which meridian)" mcp
# without a persistent install:
claude mcp add -s user -e MERIDIAN_ACCESS_LEVEL=write -- meridian uvx --from axiom-meridian meridian mcp
```

### VS Code

User `mcp.json` — macOS `~/Library/Application Support/Code/User/mcp.json`,
Linux `~/.config/Code/User/mcp.json`, Windows `%APPDATA%\Code\User\mcp.json`:

```json
{
  "servers": {
    "meridian": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "axiom-meridian", "meridian", "mcp"],
      "env": { "MERIDIAN_ACCESS_LEVEL": "write" }
    }
  }
}
```

### Cursor

`~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "meridian": {
      "command": "uvx",
      "args": ["--from", "axiom-meridian", "meridian", "mcp"],
      "env": { "MERIDIAN_ACCESS_LEVEL": "write" }
    }
  }
}
```

### Kimi CLI

`~/.kimi/mcp.json` — same shape as Cursor (`mcpServers`).

### OpenCode

`~/.config/opencode/opencode.json` — note `command` is a single array and the
key is `environment`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "meridian": {
      "type": "local",
      "command": ["uvx", "--from", "axiom-meridian", "meridian", "mcp"],
      "environment": { "MERIDIAN_ACCESS_LEVEL": "write" }
    }
  }
}
```

### Manual configuration

Any other MCP client: run `meridian mcp` (stdio transport) with the
environment variables below. For HTTP/SSE, `meridian serve 8080` prints a
bearer session token to include as `Authorization: Bearer <token>`.

Avoid `uv run ...` as the configured command: MCP clients often can't
resolve it ("command not found" / "can't open file"). `meridian doctor` flags
it.

## Upgrading

```bash
uv tool upgrade axiom-meridian
```

With `uvx`, the cached version keeps being served until refreshed — run
`uvx --refresh --from axiom-meridian meridian version` once (don't put
`--refresh` in the client config: it would re-resolve on every start).
Restart your MCP clients afterwards.

## Uninstalling

```bash
uv tool uninstall axiom-meridian
```

From a clone, `bash scripts/uninstall.sh` also removes Meridian's entry from
every client config (other servers in those files are left untouched) and
the legacy `~/.meridian` venv from older installers. Neither touches your
knowledge base.

## Install from source

```bash
git clone https://github.com/abeljumanuel/axiom-meridian-project.git
cd axiom-meridian-project
bash scripts/install.sh            # installs this checkout (editable) + runs setup
```

`install.sh` run from a clone installs that clone in editable mode, so source
changes take effect on the next server restart. For development:

```bash
uv sync --extra dev --extra rag    # full test suite needs the rag extra
uv run pytest
uv run ruff check src tests
```

## Diagnostics: `meridian doctor`

Read-only; exits non-zero if it finds a problem. It checks:

- the command each detected client is configured to launch — exists, is
  executable, or `uvx` is installed — and flags stale `uv run` configurations;
- a venv whose base Python moved or was removed (the cause of
  `Library not loaded: @rpath/libpython3.11.dylib`);
- cloud-sync corruption: duplicated files such as `module 2.py`, and macOS
  "hidden" `.pth` files that Python silently skips (typical of a venv inside
  iCloud Drive's Desktop & Documents, OneDrive, or Dropbox — keep venvs
  outside synced folders);
- the knowledge base location, the running version, and whether the `rag`
  extra is installed.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `KNOWLEDGE_BASE_PATH` | macOS `~/Library/Application Support/meridian`, Linux `~/.local/share/meridian`, Windows `%APPDATA%\meridian` | Knowledge base root (Markdown files + SQLite index). Created if missing. |
| `MERIDIAN_ACCESS_LEVEL` | `analyze` | `read` / `analyze` / `write` — gates which tools may run. |
| `MERIDIAN_PROJECT_PATH` | — | Target project for `generate_project_skills`. |
