# Axiom Meridian

> **Code drifts. Meridian doesn't.**

Axiom Meridian is a Model Context Protocol (MCP) server that centralizes institutional technical knowledge — business rules, lessons learned, and meeting transcripts — and delivers it on-demand during the software development lifecycle.

As knowledge bases like `Global_Rules.md` and `Lessons_Learned.md` grow, AI agents must read entire files in every session, degrading speed and accuracy. Meridian solves this by returning only the knowledge relevant to the current task, using scoped hierarchies, dynamic attribute filtering, and optional semantic search (RAG). The Markdown files remain the single source of truth; SQLite serves as the index and state layer — never the other way around.

---

## Table of Contents

- [Installation](#installation)
  - [Quick Install](#quick-install-recommended)
  - [Prerequisites](#prerequisites)
  - [Semantic search](#semantic-search-optional-rag-extra)
  - [Install from Source](#install-from-source)
  - [Knowledge Base Directory](#knowledge-base-directory-optional)
- [MCP Configuration](#mcp-configuration)
  - [Claude Code](#claude-code)
  - [VSCode](#vscode)
  - [OpenCode](#opencode)
  - [Kimi CLI and Cursor](#kimi-cli-and-cursor)
- [Troubleshooting](#troubleshooting)
- [Quick Start](#quick-start)
- [Migrating Legacy Files](#migrating-legacy-files)
- [Environment Variables](#environment-variables)
- [Scripts](#scripts)
  - [install.sh](#installsh)
  - [uninstall.sh](#uninstallsh)
- [Security](#security)
  - [Access Levels](#access-levels)
  - [HTTP/SSE Session Token](#httpsse-session-token)
  - [Audit Log](#audit-log)
- [Tool Reference](#tool-reference)
- [Architecture](#architecture)
- [License](#license)

---

## Installation

> The complete, maintained guide is [`docs/installation.md`](../installation.md); this section summarizes it.

### Quick Install (Recommended)

**Linux / macOS:**

```bash
curl -fsSL https://raw.githubusercontent.com/abeljumanuel/axiom-meridian-project/main/scripts/install.sh | bash
```

`install.sh` is a thin wrapper: it installs [`uv`](https://docs.astral.sh/uv/) if missing (after asking), runs `uv tool install axiom-meridian` (add `RAG=1` for semantic search), then hands off to `meridian setup` — which detects your MCP clients, asks before configuring each one, creates the knowledge base, and optionally seeds it with the bundled examples — and finishes with `meridian doctor`.

**Windows (PowerShell)** — no script needed, `meridian setup` is plain Python:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install axiom-meridian
meridian setup
```

**Claude Code plugin** (server + usage skill in one unit):

```text
/plugin install meridian --marketplace abeljumanuel/axiom-meridian-project
```

### Prerequisites

- [`uv`](https://docs.astral.sh/uv/) — it fetches a compatible Python (3.11+) on its own.
- An MCP client: Claude Code, Kimi CLI, OpenCode, VS Code, or Cursor.

### Semantic search (optional `rag` extra)

`torch`, `sentence-transformers`, and `chromadb` (~900 MB) are an opt-in extra: `uv tool install "axiom-meridian[rag]"`. Without it, `query_text` searches fall back to SQL filtering, `generate_embeddings` returns `{"error": "RAG_NOT_INSTALLED", ...}`, and approval responses report `embedded: null`.

### Install from Source

```bash
git clone https://github.com/abeljumanuel/axiom-meridian-project.git
cd axiom-meridian-project
bash scripts/install.sh            # installs this checkout (editable) + runs meridian setup

# development
uv sync --extra dev --extra rag
uv run pytest
```

### Knowledge Base Directory (Optional)

Meridian auto-creates the knowledge base if not configured. By default:
- **Linux:** `~/.local/share/meridian`
- **macOS:** `~/Library/Application Support/meridian`
- **Windows:** `%APPDATA%/meridian`

To use a custom location, set `KNOWLEDGE_BASE_PATH` before running `meridian setup` (it is written into each client's configuration).

---

## MCP Configuration

`meridian setup` writes all of these for you, and is safe to re-run: it never replaces a registration that points at a different install — it warns and prints the commands to switch. The snippets below are for manual setup or review. `COMMAND` is the absolute path from `which meridian` (Windows: `where meridian`), or `uvx` with args `--from axiom-meridian meridian mcp` for a no-install setup.

> **Note:** For normal development sessions, `analyze` (the default access level) is sufficient. Use `write` only for administration and migration (approving proposals, indexing).

### Claude Code

```bash
claude mcp add -s user -e MERIDIAN_ACCESS_LEVEL=write -- meridian "$(which meridian)" mcp
```

> **Do not use `~/.claude/settings.json` to register MCP servers** — that file controls agent permissions and plugins, not the MCP server list.

### VSCode

User `mcp.json` (macOS `~/Library/Application Support/Code/User/mcp.json`, Linux `~/.config/Code/User/mcp.json`, Windows `%APPDATA%\Code\User\mcp.json`):

```json
{
  "servers": {
    "meridian": {
      "type": "stdio",
      "command": "/absolute/path/to/meridian",
      "args": ["mcp"],
      "env": { "MERIDIAN_ACCESS_LEVEL": "write" }
    }
  }
}
```

### OpenCode

`~/.config/opencode/opencode.json` (or project-level `opencode.json`):

```json
{
  "mcp": {
    "meridian": {
      "type": "local",
      "command": ["/absolute/path/to/meridian", "mcp"],
      "environment": { "MERIDIAN_ACCESS_LEVEL": "write" }
    }
  },
  "permission": { "mcp": { "meridian": "ask" } }
}
```

> **⚠️ Use `"environment"` not `"env"`:** OpenCode silently ignores `"env"`.

### Kimi CLI and Cursor

`~/.kimi/mcp.json` and `~/.cursor/mcp.json` share the same shape:

```json
{
  "mcpServers": {
    "meridian": {
      "command": "/absolute/path/to/meridian",
      "args": ["mcp"],
      "env": { "MERIDIAN_ACCESS_LEVEL": "write" }
    }
  }
}
```

> **⚠️ Never configure a client with `uv run ...`** — MCP clients often can't resolve it ("command not found" / "can't open file"). `meridian doctor` flags it.

---

## Troubleshooting

Run **`meridian doctor`** first — it is read-only, exits non-zero on problems, and prints the fix for each. It diagnoses:

- **A client's configured command is missing or not executable** (or `uvx` isn't installed for a `uvx` registration) → reinstall (`uv tool install axiom-meridian`) or re-run `meridian setup`.
- **"Library not loaded: @rpath/libpython3.11.dylib"** — the venv's base Python moved or was removed (e.g. after an OS update) → reinstall to recreate the environment.
- **Stale `uv run` configurations** — the cause of "bash: -m: command not found" / "can't open file" errors → re-run `meridian setup` after removing the old entry.
- **Cloud-sync corruption** — duplicated files like `name 2.py`, or macOS-"hidden" `.pth` files that Python silently skips, typical of a venv inside iCloud Drive's Desktop & Documents, OneDrive, or Dropbox → recreate the venv outside the synced folder.

Other issues:

- **MCP server does not appear in `claude mcp list`** — make sure it was registered with `claude mcp add` (not `~/.claude/settings.json`), then restart Claude Code.
- **"SQLite objects created in a thread can only be used in that same thread"** — fixed in v0.1.0-post (`check_same_thread=False` in `db/connection.py`).
- **Upgraded but nothing changed** — restart your MCP clients; with `uvx`, refresh the cache once with `uvx --refresh --from axiom-meridian meridian version`.

---

## Quick Start

### 1. Index a Seed File

The package bundles a sample rules file at `src/meridian/examples/knowledge-base/global/java.md`. `meridian setup --seed` copies and indexes it (and the Clean Code rules) for you; to do it by hand:

```bash
cp src/meridian/examples/knowledge-base/global/java.md ~/meridian-kb/knowledge-base/global/java.md
python -c "
from meridian.db.connection import initialize_db, get_connection
from meridian.config import get_db_path
from meridian.tools.knowledge_management import index_rules_from_markdown

initialize_db(get_db_path())
conn = get_connection(get_db_path())
result = index_rules_from_markdown(
    'src/meridian/examples/knowledge-base/global/java.md',
    default_scope_id='global-java',
    mode='atomic'
)
print(result)
"
```

Expected output:

```json
{"indexed": 3, "created": 3, "updated": 0, "by_scope": {"global-java": 3}, "errors": [], "warnings": []}
```

### 2. Query Rules

```bash
python -c "
from meridian.db.connection import get_connection
from meridian.config import get_db_path
from meridian.tools.knowledge_consumption import query_rules

conn = get_connection(get_db_path())
result = query_rules(
    project_id='project-example',
    category='logging',
    detail='summary',
    format='json',
    conn=conn
)
print(result)
"
```

This returns rules scoped to `project-project-example` (inheriting from `global-quarkus` → `global-java` → `global`), filtered by `category="logging"`.

### 3. Verify Access Control

With `MERIDIAN_ACCESS_LEVEL=read`, write operations are denied:

```bash
export MERIDIAN_ACCESS_LEVEL=read
python -c "
from meridian.utils.security import check_access, AccessDeniedError
try:
    check_access('approve_proposal')
except AccessDeniedError as e:
    print(e)
"
```

Expected output:

```
Tool 'approve_proposal' requires access level 'write'. Current level: 'read'. Set MERIDIAN_ACCESS_LEVEL=write to enable.
```

### 4. Generate Skills

With `MERIDIAN_ACCESS_LEVEL=write` and `MERIDIAN_PROJECT_PATH` set:

```bash
export MERIDIAN_ACCESS_LEVEL=write
export MERIDIAN_PROJECT_PATH=$(pwd)
python -c "
from meridian.db.connection import get_connection
from meridian.config import get_db_path
from meridian.utils.skill_generator import generate_project_skills

conn = get_connection(get_db_path())
result = generate_project_skills(conn, 'project-example', get_project_path())
print(result)
"
```

This generates `.claude/skills/meridian/project-example/SKILL.md` and `references/rules.md` in the project path.

---

## Migrating Legacy Files

If you have existing `Global_Rules.md` or `learned-prd-en.md` files in narrative format, Meridian can migrate them without data loss.

### Step 1 — Convert to Atomic Proposals

```python
from meridian.tools.knowledge_management import convert_to_atomic_format

result = convert_to_atomic_format(
    filepath="path/to/Global_Rules.md",
    default_scope_id="global-java",
    doc_type="rules"
)
```

This creates entries in `pending_proposals` with `source_type="legacy"`. The original text is preserved in `legacy_original` for audit purposes. Sections like "Skill Suggestions" (`/pr-implement`, `/pr-verify`, `/pr-feedback`) are discarded silently — they are not rules or lessons.

### Step 2 — Review and Approve

```python
from meridian.tools.knowledge_management import list_pending_proposals, approve_proposal

# List pending proposals
proposals = list_pending_proposals(status="pending")

# Approve one by one after review
result = approve_proposal(proposal_id="prop-0001")
```

On approval, Meridian:

1. Generates the next canonical code (e.g., `RN-JAVA-004`)
2. Appends the atomic block to the correct `.md` destination
3. Calculates `file_offset` and `byte_length`
4. Inserts into `rules` or `lessons` with `status = active`
5. Registers the creation in `rule_history`

**Important:** The destination `.md` file must exist before approval. Meridian never creates files automatically.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KNOWLEDGE_BASE_PATH` | No | Auto-created | Path to knowledge base. If not set, Meridian auto-creates in OS-specific default location (`~/.local/share/meridian` on Linux, `~/Library/Application Support/meridian` on macOS, `%APPDATA%/meridian` on Windows). |
| `MERIDIAN_PROJECT_PATH` | No | — | Path to the target project for `generate_project_skills()`. Optional if you pass `project_path` explicitly. |
| `MERIDIAN_ACCESS_LEVEL` | No | `analyze` | Operation level: `read` (queries only), `analyze` (queries + audits), `write` (full access). |

### Platform-Specific Default Paths

| Platform | Default Path |
|----------|-------------|
| Linux | `~/.local/share/meridian` |
| macOS | `~/Library/Application Support/meridian` |
| Windows | `%APPDATA%/meridian` |

---

## Security

### Access Levels

Every tool has an assigned access level. `MERIDIAN_ACCESS_LEVEL` determines what a connected client can execute.

| Level | Description | When to Use |
|-------|-------------|-------------|
| `read` | Queries only. Nothing is persisted. | Agents that only consume knowledge. |
| `analyze` | Read + audit and proposal persistence. | Normal development sessions. |
| `write` | Full access. Modifies knowledge-base, approves proposals, generates embeddings. | Administration and migration. |

**Rules:**

- If `MERIDIAN_ACCESS_LEVEL` is not set → defaults to `analyze`
- Valid values: `read`, `analyze`, `write`
- A higher level includes all lower levels: `write` includes `analyze` and `read`
- Invoking a tool with insufficient level returns `ACCESS_DENIED`

### Tools by Access Level

| Level | Tools |
|-------|-------|
| **read** | `query_rules`, `query_lessons`, `get_rule_context`, `get_rule_timeline`, `get_project_scope_resolution`, `get_rule_audit_log`, `list_pending_proposals` |
| **analyze** | `audit_pr`, `analyze_pr_feedback`, `check_feature_against_rules`, `extract_rules_from_transcript`, `extract_lessons_from_transcript`, `create_pending_proposal` |
| **write** | `index_rules_from_markdown`, `index_lessons_from_markdown`, `convert_to_atomic_format`, `approve_proposal`, `edit_proposal`, `reject_proposal`, `promote_rule`, `generate_embeddings`, `generate_project_skills` |

### Denial Response

```json
{
  "error": "ACCESS_DENIED",
  "tool": "approve_proposal",
  "required_level": "write",
  "current_level": "read",
  "message": "Tool 'approve_proposal' requires access level 'write'. Current level: 'read'. Set MERIDIAN_ACCESS_LEVEL=write to enable."
}
```

### HTTP/SSE Session Token

The stdio transport is inherently secure — only the parent process can communicate with the server. The following measures apply **only** to the HTTP/SSE transport.

**Localhost-only binding:**

```python
mcp.run(transport="sse", host="127.0.0.1", port=8080)
```

The HTTP/SSE server only accepts connections from `127.0.0.1`. It is not accessible from other devices on the network.

**Session token:**

When starting in HTTP/SSE mode, Meridian generates a random session token and prints it to stdout:

```
Meridian HTTP/SSE server started on 127.0.0.1:8080
Session token: abc123...
Include header: Authorization: Bearer abc123...
```

Every HTTP request must include `Authorization: Bearer <token>`. Requests without a token or with an invalid token receive `401 Unauthorized`. The token changes on every server restart and is never persisted.

In stdio transport, no token is generated or validated.

### Audit Log

Every tool invocation is recorded in the `access_log` table in SQLite:

| Column | Description |
|--------|-------------|
| `timestamp` | When the call occurred |
| `tool_name` | Which tool was invoked |
| `access_level` | Required level of the tool |
| `project_id` | Project context (if applicable) |
| `parameters` | JSON of metadata params only — **sensitive content is excluded** |
| `result` | `success`, `denied`, or `error` |
| `transport` | `stdio` or `http` |

**Sensitive parameters never logged:** `pr_diff`, `feedback_text`, `text`, `proposed_text`, `new_text`.

To query the audit log:

```python
from meridian.tools.knowledge_consumption import get_rule_audit_log

result = get_rule_audit_log(project_id="project-example", since="2026-04-01")
```

---

## Tool Reference

| Tool | Description | Key Parameters | Level |
|------|-------------|----------------|-------|
| `query_rules` | Query active rules for a project with scope resolution, filters, and optional semantic search | `project_id`, `category?`, `severity?`, `tags?`, `query_text?`, `format?` (`json`\|`toon`), `detail?` (`summary`\|`full`) | read |
| `query_lessons` | Query lessons for a project — same params as `query_rules` | `project_id`, `area?`, `tags?`, `query_text?`, `format?`, `detail?` | read |
| `get_rule_context` | Full rule text + complete history + linked lessons (Capa 3 Progressive Disclosure) | `rule_id` | read |
| `get_rule_timeline` | Chronological history of a rule without loading full text (Capa 2) | `rule_id` | read |
| `get_project_scope_resolution` | Effective scopes for a project in precedence order with attributes | `project_id` | read |
| `get_rule_audit_log` | Audit trail of rule changes, deprecations, and promotions | `project_id?`, `scope_id?`, `since?` | read |
| `list_pending_proposals` | List proposals filterable by project, type, and status | `project_id?`, `type?` (`rule`\|`lesson`), `status?` (`pending`\|`approved`\|`rejected`) | read |
| `index_rules_from_markdown` | Index rules from Markdown — atomic or legacy mode | `filepath`, `default_scope_id`, `mode?` (`atomic`\|`legacy`) | write |
| `index_lessons_from_markdown` | Index lessons from Markdown — atomic or legacy mode | `filepath`, `default_scope_id`, `mode?` (`atomic`\|`legacy`) | write |
| `convert_to_atomic_format` | Migrate legacy files to atomic proposals (no direct write) | `filepath`, `default_scope_id`, `doc_type` (`rules`\|`lessons`) | write |
| `approve_proposal` | Promote a pending proposal to an active rule/lesson in `.md` and DB | `proposal_id` | write |
| `edit_proposal` | Update proposed text and metadata while keeping status pending | `proposal_id`, `new_text`, `metadata?` | write |
| `reject_proposal` | Reject a proposal with optional reason | `proposal_id`, `reason?` | write |
| `promote_rule` | Move a rule to a broader scope; registers `PROMOTED` in history | `rule_id`, `new_scope_id` | write |
| `generate_embeddings` | Generate/update ChromaDB embeddings for semantic search | `scope_id?` (optional — all scopes if omitted) | write |
| `generate_project_skills` | Generate `.claude/skills/` files for a project per agentskills.io | `project_id`, `project_path?` | write |
| `audit_pr` | Retrieve relevant rules/lessons for a PR diff and persist audit record | `pr_diff`, `project_id` | analyze |
| `analyze_pr_feedback` | Analyze PR feedback against previously run audit | `feedback_text`, `pr_ref`, `project_id` | analyze |
| `check_feature_against_rules` | Check a feature description against relevant rules/lessons | `feature_description`, `project_id` | analyze |
| `extract_rules_from_transcript` | Extract rule candidates from meeting transcripts | `text`, `project_id` | analyze |
| `extract_lessons_from_transcript` | Extract lesson candidates from meeting transcripts | `text`, `project_id` | analyze |
| `create_pending_proposal` | Register a candidate rule/lesson from transcript analysis | `type`, `proposed_text`, `suggested_scope_id`, `suggested_attributes?`, `source_type?`, `source_ref?` | analyze |

---

## Architecture

```
KNOWLEDGE_BASE_PATH/                 ← outside the repo
├── knowledge-base/
│   ├── global/
│   │   ├── general.md
│   │   ├── java.md
│   │   ├── quarkus.md
│   │   ├── nestjs.md
│   │   ├── go.md
│   │   └── flutter.md
│   └── projects/
│       ├── project-example.md
│       ├── other-project-example.md
│       └── ledger.md
├── lessons/
│   ├── global/
│   └── projects/
├── meridian.db                      ← SQLite (index + state)
└── chroma/                          ← ChromaDB vector store (optional)
    ├── rules/
    └── lessons/
```

**Key principles:**

1. **Markdown is the source of truth.** SQLite is the index and state. Never the reverse.
2. **Nothing is written without explicit user approval.** All extractions go to `pending_proposals` first.
3. **Reads are served from the index, validated per file.** `detail="full"` queries read text from SQLite (`rules.text` / `lessons.what_happened`), not by re-reading the `.md` file per row. Freshness is checked once per distinct file against `indexed_files` (mtime fast path, sha256 arbiter on mismatch) — a stale or unindexed file returns `STALE_INDEX` rather than serving outdated text. `file_offset`/`byte_length` still exist, but only as write-path metadata. See [ADR-005](ADR-005-indexed-read-path.md).
4. **Scope hierarchy is resolved** before every query. More specific rules have higher precedence.
5. **Every rule is traceable** — which meeting originated it, which PR refined it, which lesson motivated it.
6. **RAG and SQL coexist.** `query_rules()` uses semantic search when embeddings exist, and falls back to SQL automatically when they don't. The tool signature never changes.

**Architecture decisions:** [ADR-001](ADR-001-response-serialization-format.md) (response serialization) · [ADR-002](ADR-002-dynamic-context-attributes.md) (dynamic attributes) · [ADR-003](ADR-003-legacy-scope-inference.md) (legacy scope inference) · [ADR-004](ADR-004-id-counters-and-nplus1-fix.md) (ID counters, N+1 fix) · [ADR-005](ADR-005-indexed-read-path.md) (indexed read path)

---

## Scripts

The `scripts/` directory contains installer utilities. All client detection and configuration logic lives in Python (`meridian setup` / `meridian doctor`); the shell scripts only wrap it.

### install.sh

Thin wrapper (Linux/macOS) that:
- Ensures `uv` is installed (asks before installing it)
- Runs `uv tool install --force axiom-meridian` — or, run from a clone, installs that clone in editable mode
- Hands off to `meridian setup` (client configuration, knowledge base, optional example seeding), then runs `meridian doctor`

```bash
# Default installation
bash scripts/install.sh

# Non-interactive, with semantic search and the example knowledge base
RAG=1 SEED_KB=1 bash scripts/install.sh

# Skip MCP configuration / custom knowledge base location
SKIP_MCP=1 KNOWLEDGE_BASE_PATH=/data/kb bash scripts/install.sh

# Remote installation
curl -fsSL https://raw.githubusercontent.com/abeljumanuel/axiom-meridian-project/main/scripts/install.sh | bash

# Dry run (show what would happen)
DRY_RUN=1 bash scripts/install.sh
```

### uninstall.sh

Removes the `uv tool` install, the legacy `~/.meridian` venv from older installers, and Meridian's entry from every client config (other servers in those files are left untouched). The knowledge base is never removed.

```bash
# Interactive uninstall
bash scripts/uninstall.sh

# Dry run (show what would be removed)
DRY_RUN=1 bash scripts/uninstall.sh
```

---

## License

Apache License 2.0 — see [LICENSE](../../LICENSE) and [NOTICE](../../NOTICE). Copyright 2026 Juan Manuel Rojas González (Axiom JUMA). Versions made available before the relicense were declared under the MIT License.
