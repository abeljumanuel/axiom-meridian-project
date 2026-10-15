## Context

Today: clone-only install via `scripts/install.sh` (bash, Linux/macOS),
no PyPI presence, no Windows path, no marketplace-distributable artifact.
Three dependencies (`torch`, `sentence-transformers`, `chromadb`) are
mandatory at the dependency-resolution level even though every actual
import of them is already lazy (verified in `rag/embedder.py` and
`rag/vector_store.py` — see proposal.md). Three installer bugfixes and
one warm-up feature are merged in code but not yet archived as OpenSpec
changes, and there is no `openspec/specs/` yet in this repo at all.

Constraints this design must respect:
- `.md` files remain the single source of truth; nothing here touches
  that invariant.
- Existing users who ran `install.sh` have a venv at `~/.meridian/venv`
  (or `$INSTALL_DIR/venv`) registered with their MCP clients pointing at
  `$BIN_DIR/meridian`. That registration must keep working.
- `TOOL_ACCESS_LEVELS` / `check_access` is the only gate on tool
  execution — a `RAG_NOT_INSTALLED` response is a new *result shape*,
  not a new access-control concept, and must not be confused with
  `ACCESS_DENIED`.

## Goals / Non-Goals

**Goals:**
- Any of `pip install axiom-meridian`, `uvx --from axiom-meridian meridian mcp`,
  `uv tool install axiom-meridian`, or the rewritten `install.sh`/one-line
  `uvx` command gets a working, non-RAG Meridian server with no manual
  dependency wrangling, on Linux, macOS, or Windows.
- Installing `axiom-meridian[rag]` (or running `meridian setup` and
  opting in) additionally gets semantic search, with no code change
  required elsewhere.
- A generic, marketplace-safe skill and a Claude Code plugin exist as
  separate, optional distribution artifacts — neither is required to
  use the server directly.
- Zero behavior change for any currently-passing non-RAG test or
  tool call when the `rag` extra **is** installed (this is additive at
  the dependency level, not a behavior rewrite of RAG itself).

**Non-Goals:**
- Not building a hosted/managed Meridian service — install remains
  self-hosted; PyPI/MCP-Registry/marketplace listings are discovery and
  distribution only.
- Not changing the scope-hierarchy, proposal-lifecycle, or serialization
  invariants documented in the root `CLAUDE.md` — this change is purely
  about how the server reaches a machine and how an agent discovers it.
- Not deciding marketplace submission targets (see proposal.md's Open
  Questions) — the skill is built to generic marketplace-safety rules,
  not a specific marketplace's bespoke requirements.
- Not writing a GUI installer or a Homebrew/Scoop/apt package — `uvx`
  plus a thin shell/PowerShell wrapper is the full scope.

## Decisions

### D1 — RAG as an extra, guarded by a structured error, not a feature flag

`pyproject.toml`:

```toml
dependencies = [
    "fastmcp>=0.4.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
rag = [
    "sentence-transformers>=3.0.0",
    "chromadb>=0.5.0",
    "torch>=2.2.0",
]
dev = [ ... ]
```

A new `meridian.rag.availability` module (name tentative) centralizes
the check:

```python
from importlib.util import find_spec

_RAG_MODULES = ("sentence_transformers", "torch", "chromadb")

def rag_installed() -> bool:
    # find_spec, not import: importing torch costs several seconds, and
    # warm_up_in_background() calls this on the main thread at startup —
    # an import here would move the exact cost warm-up exists to hide
    # back onto the startup path.
    return all(find_spec(name) is not None for name in _RAG_MODULES)

class RagNotInstalledError(Exception):
    def to_response(self) -> dict:
        return {
            "error": "RAG_NOT_INSTALLED",
            "message": "Semantic search requires the 'rag' extra. "
                        "Install with: uv tool install \"axiom-meridian[rag]\" "
                        "(uvx: uvx --from \"axiom-meridian[rag]\" meridian mcp; "
                        "pip: pip install \"axiom-meridian[rag]\")",
        }
```

Call sites:
- `generate_embeddings` (write-level tool): raises `RagNotInstalledError`
  at entry if not installed; `server.py`'s `_security_pattern` catches it
  the same way it already special-cases `AccessDeniedError`, returning
  `to_response()` as the tool's string result (serialized). Note the
  *current* behavior is not a raw traceback to the client: the import
  failure is caught inside `_generate_embeddings_for_table` and surfaces
  as `{"processed": 0, "errors": N}` plus a logged traceback — the guard
  replaces that misleading "N failures" result. The `access_log` row for
  this case is written with status `"error"` (the existing generic
  failure status), not `"denied"`.
- Post-commit hooks `_embed_and_upsert_after_approve` and
  `_remove_embedding_after_deprecate` (used by `approve_proposal`, the
  deprecate-proposal path and `promote_rule`): check `rag_installed()`
  first and, if absent, return `None` without touching the vector store
  or logging an exception. Callers pass that through as
  `embedded: null` / `embedding_removed: null`, keeping `false` to mean
  "RAG is installed and the step failed". The approval/deprecation
  itself is unaffected either way (these hooks already run after the
  commit).
- `query_rules`/`query_lessons`'s `query_text` path: unchanged in
  *spirit* — it already checks `vector_store.chromadb_available()` and
  falls back to SQL. That check itself must not raise ImportError when
  chromadb isn't installed; `chromadb_available()` wraps its body in
  `try/except Exception` already (confirmed in `vector_store.py`), so
  this already degrades safely — **no code change needed there**, only
  a test added to lock in the behavior (see tasks.md).
- `embedder.warm_up_in_background()`: guarded at the top — if
  `not rag_installed()`, logs at INFO ("RAG extra not installed, skipping
  embedder warm-up") and returns without starting the thread.

Tests and dev environment: `tests/integration/test_rag_query.py` and
`tests/unit/test_embedder.py` need the real libraries
(`test_vector_store.py` already uses `pytest.importorskip("chromadb")`).
The RAG-dependent tests get the same `importorskip` guard, and the
`dev` extra stays lean; contributors run `uv sync --extra dev --extra rag`
for the full suite (root `CLAUDE.md`'s Commands section updated to
match). CI runs both variants (see D7) so the no-RAG path is exercised
by real absence, not only by monkeypatching.

**Alternatives considered:**
- *Env var feature flag (`MERIDIAN_ENABLE_RAG=1`)* — rejected. It adds a
  second axis of "is RAG on" independent of "is RAG importable," which
  can silently diverge (flag on, package missing → crash anyway). Import
  availability is the actual ground truth; checking it directly removes
  a whole class of misconfiguration.
- *Try/except at every call site inline* — rejected in favor of one
  `RagNotInstalledError` type so `server.py`'s existing
  exception-to-response pattern (next to `AccessDeniedError`) handles it
  uniformly, matching the "follow this exact pattern" rule in root
  `CLAUDE.md` for tool registration.

### D2 — `meridian setup` / `meridian doctor` as Python subcommands, not a rewrite of bash logic

New subcommands dispatched from `__main__.py`'s existing `_COMMANDS` dict,
implemented in a new `src/meridian/cli/setup.py` and `src/meridian/cli/doctor.py`
(mirroring the existing flat-module style of `__main__.py` rather than
introducing a CLI framework dependency like `click`/`typer` — this
project has zero CLI-framework dependencies today and the existing
hand-rolled `_get_flag`/`_COMMANDS` pattern is sufficient for two more
subcommands with a handful of flags each).

`meridian setup` responsibilities (mirrors `install.sh` minus venv
creation, since by the time `meridian setup` runs, `meridian` itself is
already importable — it's either in a `uvx` ephemeral env or a venv
`pip install`'d it):
1. Detect MCP clients cross-platform: `shutil.which("claude")`,
   `shutil.which("kimi")`, `shutil.which("opencode")`, `shutil.which("cursor")`,
   and the existing VSCode directory-existence checks — all of which are
   already OS-agnostic Python operations (no bash-specific `command -v`).
2. For each detected client, write/update its config with the same
   not-overwrite-silently and already-configured-detection logic that
   `fix-installer-claude-mcp-check-and-url` introduced for Claude Code —
   reimplemented once in Python and shared across clients instead of
   four near-duplicate bash functions.
3. Create the knowledge base directory (OS-specific default path logic
   already exists in Python — `config.py`'s `get_knowledge_base_path()` —
   this reuses it directly rather than re-deriving paths, unlike
   `install.sh`'s own `get_default_kb_path()` bash duplicate of the same
   logic).
4. Offer to seed the bundled example KB, preserving the no-clobber
   behavior from `fix-installer-seed-overwrites-existing-kb` (spec'd as
   an explicit WHEN/THEN scenario so the rewrite can't regress it
   silently). The source can no longer be "the repo root next to
   `scripts/`" (what `install.sh::seed_knowledge_base` uses): a wheel
   only contains `src/meridian`. The example files move to
   `src/meridian/examples/knowledge-base/global/` and are read via
   `importlib.resources`, so seeding works identically from a clone, a
   `uv tool install` or a `uvx` run.

**What command gets registered with each client.** `install.sh` today
registers `$BIN_DIR/meridian` from a persistent venv. `meridian setup`
must never register `sys.executable`/its own script path when it is
running inside a `uvx` ephemeral environment — that path lives in uv's
cache and disappears on `uv cache clean`/prune, silently breaking every
client. Rule: if a persistent `meridian` resolves on `PATH`
(`shutil.which("meridian")`, e.g. from `uv tool install`), register that
absolute path; otherwise register `uvx --from axiom-meridian meridian mcp`
(or `axiom-meridian[rag]` when the user opted into RAG). The Claude Code
"same install" check (ported from `fix-installer-claude-mcp-check-and-url`)
compares against *this* computed command, not a `$BIN_DIR` that has no
equivalent under `uvx`.

**RAG opt-in.** `meridian setup` cannot add packages to the environment
it is running in (a `uvx` env is ephemeral). Opting in therefore changes
what it registers/installs: `uv tool install "axiom-meridian[rag]"`
(suggested as a command to run, or run with explicit confirmation) or
`--from "axiom-meridian[rag]"` in the registered `uvx` command.

`meridian doctor` responsibilities: re-run the same client-detection and
entry-point checks as read-only diagnostics — "entry point" meaning the
command *each detected client is configured to launch* (does the path
exist and is it executable, is `uvx` on `PATH`), since `meridian doctor`
itself running already proves its own entry point works — plus the specific
failure modes already documented in README's Troubleshooting section
(`libpython dylib` path issue, cloud-sync `.venv` corruption, stale
`uv run` MCP configs) — translated into actionable checks instead of
prose a user has to self-diagnose against.

**Alternatives considered:**
- *Keep all logic in bash, just add a `.ps1` port* — rejected. Doubles
  the maintenance surface (two scripts to keep in sync for every future
  client-detection tweak) and still can't share code with the Python
  package the way an in-package CLI command can (e.g., directly calling
  `config.get_knowledge_base_path()` instead of re-deriving the same
  default path string in a second language).
- *`click`/`typer` dependency* — rejected for scope control: two new
  subcommands with simple flags don't justify a new mandatory dependency
  in a project that specifically wants to *shrink* its default install
  footprint this change.

### D3 — `install.sh` becomes a thin wrapper; no `install.ps1`

`scripts/install.sh` is rewritten to:
1. Ensure `uv` is present (existing `check_prerequisites` logic, kept).
2. Run `uv tool install axiom-meridian` or
   `uvx --from axiom-meridian meridian setup` (exact invocation decided
   in tasks.md based on whether a persistent `meridian` command on PATH
   is wanted vs. an ephemeral one-shot setup run — leaning toward
   `uv tool install` for anyone who wants `meridian doctor` available
   later without re-fetching).
3. Hand off entirely to `meridian setup` for client configuration and KB
   seeding.

For Windows: **no `install.ps1`**. The one-line install is:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uvx --from axiom-meridian meridian setup
```

Rationale: `uv`'s own installer is already a one-line PowerShell command
(documented in this repo's README already, for installing `uv` itself);
once `uv`/`uvx` exists, `uvx --from axiom-meridian meridian setup` is
*already* one line and *already* cross-platform — Python, not bash,
does the client-detection and config-writing (D2), so there is no
OS-specific logic left for a `.ps1` to own. Writing one anyway would be
~150 lines of PowerShell duplicating what `meridian setup` already does,
for zero behavior difference. `print_usage()`'s current claim that
`install.ps1` exists is corrected to point at this two-command sequence
instead (this also fixes the dangling-reference bug noted in the
`fix-installer-claude-mcp-check-and-url` proposal, flagged there but
explicitly deferred to "a different-shaped decision").

This is listed as Open Question #3 in proposal.md since it's a design
default, not a hard requirement — the maintainer may still want a
`.ps1` for discoverability parity even though it's not technically
load-bearing.

### D4 — Skill package is hand-authored content, not generated by `skill_generator.py`

`src/meridian/utils/skill_generator.py::generate_project_skills` bakes a
*live, per-project* snapshot of the actual knowledge base (a markdown
table of the project's current active rules, sourced from `query_rules`)
into `.claude/skills/meridian/<project_id>/SKILL.md`. That is the right
design for its purpose (a project-local skill reflecting *this* KB's
current content) and the wrong design for a marketplace skill: a
marketplace artifact is reviewed once and distributed broadly — it must
not embed a snapshot of any particular user's rule data (stale the
moment the KB changes, and a privacy/review concern besides, since it'd
bake arbitrary rule text into a public package).

`distribution/skill/meridian/SKILL.md` is therefore hand-authored,
generic, and describes *behavior* (when to call which tool, how to
detect whether Meridian's tools are present, what to tell the user if
they aren't) rather than *data*. It does **not** copy
`skill_generator.py`'s frontmatter: that generator nests a non-standard
`metadata.allowed_tools` list (snake_case, under `metadata`), which
Claude Code ignores for tool permissions. The marketplace skill uses the
standard Agent Skills frontmatter — `name` (lowercase, hyphenated:
`meridian`) and `description` (what it does *and when to use it*), with
no `allowed-tools` restriction, because MCP tool names differ by install
channel (`mcp__meridian__query_rules` when registered directly,
`mcp__plugin_meridian_meridian__query_rules` inside the plugin). The
skill body therefore refers to tools by their base names (`query_rules`,
`audit_pr`, ...) and tells the agent to match on that suffix.

Marketplace-safety constraints (from proposal.md, restated as concrete
rules this skill's content and packaging must satisfy):
- No script file with network access (no `curl`, no `requests`, no
  `urllib` calls) anywhere under `distribution/skill/meridian/`.
- No reading of environment variables.
- No shell-escaped or base64/obfuscated content.
- The "how to detect Meridian's tools" instruction describes checking
  for tool availability through the agent's own normal tool-listing
  mechanism (e.g., attempting `query_rules` and handling a
  tool-not-found condition) — it never shells out or probes a network
  endpoint.
- The install-command fallback text is a literal string the skill shows
  the user (e.g., `uvx --from axiom-meridian meridian mcp`) — the skill
  never executes it itself. It does not include a `curl ... | sh` /
  `irm ... | iex` uv bootstrap line (that would trip the network-pattern
  scan and is exactly what reviewers flag); for installing `uv` it links
  to uv's documentation instead.
- Mentioning an environment variable *by name* in prose (e.g. that
  approving proposals needs `MERIDIAN_ACCESS_LEVEL=write` on the server)
  is allowed; what is forbidden is code that *reads* the environment.
  The safety scan's env-var patterns therefore target script files and
  code constructs (`os.environ`, `getenv`, `process.env`), not variable
  names in Markdown prose.

Packaging: a new task runs `zip -r meridian-skill.zip distribution/skill/meridian/`
(or Python's `zipfile`, for Windows-dev parity) as a build artifact, not
committed to the repo — generated on demand per tasks.md's verification
step.

### D5 — Claude Code plugin bundles the MCP server + the same skill; MCP Registry gets its own `server.json`

Verified against current docs (`code.claude.com/docs/en/plugins`,
`.../plugins/components`) rather than assumed from memory:

```
<plugin-root>/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
└── skills/
    └── meridian/
        └── SKILL.md         # same content as distribution/skill/meridian/SKILL.md
```

`.mcp.json`:

```json
{
  "mcpServers": {
    "meridian": {
      "command": "uvx",
      "args": ["--from", "axiom-meridian", "meridian", "mcp"]
    }
  }
}
```

(`${CLAUDE_PLUGIN_ROOT}` substitution isn't needed here since the server
is fetched via `uvx` rather than shipped as a bundled script inside the
plugin directory — unlike the doc's own `node ${CLAUDE_PLUGIN_ROOT}/server.js`
example, which applies when the plugin vendors its own server code.)

`plugin.json` carries `name`, `version` (kept in sync with
`pyproject.toml`'s `version` — a tasks.md verification step checks this),
`description`, `author`.

The skill content is **duplicated** between `distribution/skill/meridian/SKILL.md`
and `<plugin>/skills/meridian/SKILL.md` rather than symlinked, because
the plugin and the standalone-skill zip are published to different
places with different packaging tools; tasks.md adds a verification
step (diff the two files) rather than a build-time symlink, to keep
each distribution artifact a plain, self-contained directory a
marketplace's automated review can walk without following links.

MCP Registry `server.json` (schema verified via the registry's own
`generic-server-json.md` reference, not assumed):

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.abeljumanuel/axiom-meridian",
  "description": "Knowledge audit MCP server — Code drifts. Meridian doesn't.",
  "version": "0.1.0",
  "repository": { "url": "https://github.com/abeljumanuel/axiom-meridian-project", "source": "github" },
  "packages": [
    {
      "registryType": "pypi",
      "registryBaseUrl": "https://pypi.org",
      "identifier": "axiom-meridian",
      "version": "0.1.0",
      "runtimeHint": "uvx",
      "transport": { "type": "stdio" },
      "environmentVariables": [
        { "name": "KNOWLEDGE_BASE_PATH", "isRequired": false },
        { "name": "MERIDIAN_ACCESS_LEVEL", "isRequired": false, "default": "analyze" }
      ]
    }
  ]
}
```

The server `name` deliberately stays `io.github.abeljumanuel/axiom-meridian`
(matching the PyPI package) while `repository.url` points at the new
`axiom-meridian-project` repo — the `io.github.abeljumanuel/` namespace
is verified against the GitHub *account*, not a specific repo name
(proposal.md Open Question #6, resolved). Registration itself is a
manual task. Separately, for `registryType: "pypi"` the registry verifies that
the PyPI package belongs to that server name by finding the line
`mcp-name: io.github.abeljumanuel/axiom-meridian` in the package's long
description — i.e. `README.md`, since `pyproject.toml` uses it as
`readme`. That line (an HTML comment is enough) must ship in the
published release *before* registration. The `$schema` URL above must
be re-checked against the registry's current docs at implementation
time; the task validates against whatever the referenced schema is.

Version sync: the version lives in **three** places today —
`pyproject.toml`'s `version`, `src/meridian/__init__.py`'s
`__version__` (hard-coded, read by `meridian version` and
`get_server_info`) — plus the new `plugin.json` and `server.json`
(`version` and `packages[0].version`). Either make `pyproject.toml`
read it dynamically from `__init__.py` (`[tool.hatch.version]` +
`dynamic = ["version"]`) or include `__init__.py` in the sync check;
the check covers all of them.

**Alternatives considered:**
- *Separate plugin repo* — rejected as the default (kept as Open
  Question #4) because it adds a second repo to keep in version-sync
  with every release for no behavior gain at this project's current
  size; revisit if the plugin grows its own release cadence.
- *Symlinking the skill content instead of duplicating* — rejected
  because marketplace zip/plugin packaging tools commonly resolve or
  reject symlinks inconsistently; a plain duplicated file with an
  automated diff-check is more robust than debugging packaging-tool
  symlink behavior across two different distribution pipelines.

### D6 — PyPI release via Trusted Publishing, manual first publish

PyPI's Trusted Publisher is bound to an exact *owner / repository /
workflow file* triple. It is configured for
`abeljumanuel` / `axiom-meridian-project` / `release.yml` — a publisher
configured against the old `axiom-meridian` repo would reject every
upload from the new one with an OIDC authorization error. This is why
the repository migration (proposal.md, "Prerequisite") must land before
the Trusted Publisher is configured.

GitHub Actions workflow (`.github/workflows/release.yml`), triggered on
`v*` tags, using `pypa/gh-action-pypi-publish` with OIDC
(`permissions: id-token: write`, no stored secret) — verified against
current PyPI/GitHub documentation on Trusted Publishing rather than
assumed. Steps: checkout → `uv build` → upload via the trusted-publishing
action. The *first* publish, creating the PyPI project and configuring
its Trusted Publisher, must happen manually once (PyPI requires the
project to either already exist or be configured as a "pending
publisher" before the OIDC exchange works for a brand-new package name)
— tracked as a manual task in tasks.md, not automated by this change.

### D7 — A CI workflow, because there is none

The repo has no `.github/` directory, yet several verification steps
(build green in CI, version-sync check, skill safety scan) and the
Windows support claim in `cli-setup-and-doctor` assume one. A
`.github/workflows/ci.yml` runs on push/PR: `uv run ruff check src tests`,
`uv run pytest` on `ubuntu-latest`, `macos-latest` and `windows-latest`
without the `rag` extra, one Linux job *with* `--extra rag`, plus the
version-sync script and the skill safety scan. Without the Windows job
nothing in this change actually exercises Windows.

## Risks / Trade-offs

- **[Risk]** Moving RAG libs to an extra is a breaking change for any
  existing automation that does a bare `pip install axiom-meridian`
  expecting semantic search to just work. → **Mitigation**: `RAG_NOT_INSTALLED`
  gives an actionable error instead of silent degradation to SQL-only
  behavior that could confuse a caller expecting ranked semantic results;
  README documents the `[rag]` extra prominently; `meridian doctor`
  reports whether RAG is installed.
- **[Risk]** Duplicated skill content (D4/D5) can drift between the
  standalone zip and the plugin's copy. → **Mitigation**: tasks.md adds
  an explicit diff-check verification step; both are generated from the
  same source file conceptually (the plugin's copy is specified as "same
  content as" in this design, enforced by that check, not by independent
  authoring).
- **[Risk]** `uv tool install` vs `uvx` ephemeral-run semantics differ
  (persistent PATH entry vs. one-shot) — picking the wrong one for
  `install.sh`'s handoff could leave users without a `meridian` command
  for later `meridian doctor` runs. → **Mitigation**: tasks.md's
  verification step explicitly tests `meridian doctor` works after a
  fresh `install.sh` run in a clean environment.
- **[Risk]** `uvx --from axiom-meridian` reuses whatever version uv
  already cached, so registered clients don't pick up new releases on
  their own. → **Mitigation**: README documents `uv tool upgrade
  axiom-meridian` / `uvx --refresh`; `meridian doctor` reports the
  running version (it already has `get_version_info()`).
- **[Risk]** PyPI package name squatting between writing this design and
  the manual first-publish task. → **Mitigation**: Open Question #2 flags
  it; the manual publish task itself is the final confirmation point,
  not this design.
- **[Trade-off]** Not building a `.ps1` installer (D3) means Windows
  users' install path differs in *shape* (two commands instead of one
  curl-pipe) from the Linux/macOS one-liner, even though both are
  one-line-*equivalent*. Accepted given the maintenance cost of a
  parallel PowerShell script that would otherwise just re-implement
  `meridian setup`.

## Migration Plan

**Backward compatibility for existing `install.sh` users (`~/.meridian/venv`):**
- Existing installs are untouched by this change landing — nothing
  auto-upgrades or auto-migrates. The venv at `~/.meridian/venv` keeps
  working exactly as installed (editable install from the old
  dependency list, RAG libs already present in that venv from the old
  `pyproject.toml`).
- Re-running the *new* `install.sh` against an existing `~/.meridian`
  installation: `meridian setup` detects the existing KB and existing
  MCP client registrations the same way the current bash logic does
  (no-clobber seeding, already-configured detection) — this change's
  `cli-setup-and-doctor` spec requires parity with those two already-merged
  bugfixes explicitly, so re-running setup is safe.
- A user who wants the *smaller* non-RAG footprint from an existing
  install has to explicitly recreate their venv (`uv sync` with the new
  `pyproject.toml` doesn't retroactively shrink an existing venv's
  installed packages) — this is a manual, opt-in action, documented in
  README's migration note, not automated.
- `meridian doctor` reports whether RAG is installed in the current
  environment either way, so a migrated-or-not user can self-diagnose.

**Rollout steps (sequencing, detailed further in tasks.md):**
1. `rag-optional-dependency` (independent, lowest risk, unblocks
   everything else being testable without network/PyPI access).
2. `cli-setup-and-doctor` (depends on nothing else in this change;
   `install.sh` rewrite depends on this).
3. `pypi-packaging` (depends on #1 for correct metadata; the workflow
   itself can be written and tested via `uv build` without publishing).
4. `skill-package` and `distribution-channels` (depend on #2/#3 only for
   the install-command text they display/reference — otherwise
   independent of each other; can be built in parallel).
5. `readme-and-docs` last, since it documents the end state of all of
   the above.

**Rollback:** every piece here is additive-or-isolated (new optional
dependency group, new CLI subcommands, new files under `distribution/`,
a new workflow file, a rewritten but behaviorally-equivalent
`install.sh`) — reverting any single capability's commits is sufficient;
none require a data migration or schema change to roll back.

## Open Questions

See proposal.md's "Open Questions" section — not duplicated here to
keep a single source of truth for them.
