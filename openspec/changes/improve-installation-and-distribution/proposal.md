## Why

Axiom Meridian today only installs by cloning the repo and running a bash
script (Linux/macOS only — no Windows path), and it only reaches agents as
a hand-rolled MCP server someone has to find, clone, and build themselves.
Two adoption paths are missing: (1) a one-line install on all three major
OSes without cloning, and (2) a packaged artifact — a skill and/or plugin —
that agent-facing marketplaces can list, while the server itself stays open
source and self-hostable. Shipping both lowers the barrier from "clone a
Python repo and run a shell script" to "one command," which is what every
comparable MCP server in this space now offers.

Verified directly in the code before writing this proposal:
- `torch`, `sentence-transformers`, and `chromadb` are top-level
  `dependencies` in `pyproject.toml`, but every import of them is already
  lazy at the call site (`rag/embedder.py::_load()` imports
  `sentence_transformers`/`torch` inside the method; `rag/vector_store.py`
  imports `chromadb` inside `_get_client()`). `rag/__init__.py` is an empty
  docstring — `from meridian.rag import embedder, vector_store` in
  `server.py`, `knowledge_consumption.py`, and `knowledge_management.py`
  only imports two small modules, not the heavy libraries themselves.
  `query_rules`/`query_lessons` already fall back to plain SQL when
  `vector_store.chromadb_available()` is false. So the only thing forcing
  these ~2GB+ of GPU-capable ML dependencies onto every installer run is
  `pyproject.toml`'s dependency list — nothing at runtime requires it for
  non-RAG use.
- The package is not on PyPI (confirmed: no published releases to check
  against; `axiom-meridian` has no listing). The name appears available.
- There is no Windows installer. `scripts/install.sh` is bash-only, and
  its own `print_usage()` and `detect_os()` tell Windows users to run
  `scripts/install.ps1`, which does not exist anywhere in the repo.
- `README.md` still points at `https://github.com/axiom-juma/meridian` in
  every quick-install/clone example; `git remote -v` shows the current
  repo is `abeljumanuel/axiom-meridian`. (`scripts/install.sh` already
  points at that one.)
- The project is moving to a new repository,
  **`https://github.com/abeljumanuel/axiom-meridian-project`** (already
  created, public, default branch `main`). It is a separate repo, not a
  rename, so GitHub will **not** redirect `github.com` or
  `raw.githubusercontent.com` URLs from the old one. Every
  repository-pointing URL this change touches — README, `install.sh`'s
  remote one-liner, `pyproject.toml`'s `[project.urls]`, `server.json`'s
  `repository.url`, and the PyPI Trusted Publisher — targets the new
  repo. Install commands that go through PyPI
  (`uvx --from axiom-meridian ...`, `uv tool install axiom-meridian`)
  don't reference GitHub at all and are unaffected.

## Prerequisite: repository migration

Implementation of this change happens **in `axiom-meridian-project`**,
after the code (and this change's OpenSpec directory) has been migrated
there. In particular, nothing is published — PyPI Trusted Publisher,
first release, MCP Registry entry, plugin/skill marketplace submissions
— until the migration is done, so no published artifact ever points at
the old repo. The old `abeljumanuel/axiom-meridian` is archived with a
README notice pointing to the new one (maintainer task 0.x in tasks.md).

## Relationship to currently open changes

All four changes below are `isComplete: true` per `openspec status` —
their code is already merged (commits `3e5276d`, `a0e8f6b`) — but none
have been archived, and `openspec/specs/` does not exist yet in this repo
(no change has ever been synced to main specs), so there is no prior
`installer-*` capability for this change to issue a delta against. Each
relationship below is therefore against their *proposal text and code*,
not a spec file:

- **`fix-installer-claude-mcp-check-and-url`** — independent, but its
  fixed `setup_claude_code()` is exactly the function `cli-setup-and-doctor`
  reimplements in Python. This change's `meridian setup` **absorbs** that
  logic (the `grep '^meridian:'` detection, the `$BIN_DIR` comparison) when
  it replaces `install.sh`'s client-configuration code; the bash version
  stays correct and unmodified for the deprecation window described in
  design.md. Recommend archiving that change once `meridian setup` ships.
- **`fix-installer-seed-overwrites-existing-kb`** — same relationship:
  **absorbed** into `meridian setup`'s seeding step, which this change
  requires to keep the no-clobber behavior that change introduced
  (`cli-setup-and-doctor`'s spec includes a WHEN/THEN scenario for it
  directly, to not silently regress it in the rewrite).
- **`fix-installer-setup-venv-abort-on-decline`** — **independent**.
  It's a one-line bash fix to `setup_venv()`'s declined-recreate branch.
  `meridian setup` doesn't shell out to a venv-creation step the same
  way (it runs inside the already-resolved `uvx` environment), so this
  fix has no equivalent bug to inherit, but `scripts/install.sh` keeps
  existing as a thin wrapper (see design.md) and must keep this fix.
- **`warm-up-embedder-on-server-start`** — **depends on** this change.
  `embedder.warm_up_in_background()` calls `_Embedder._load()` on a
  daemon thread, which imports `sentence_transformers`/`torch` directly.
  Once those move to the `[rag]` extra, that import raises
  `ModuleNotFoundError` *on the background thread* — it does **not**
  kill server startup (an uncaught thread exception goes to
  `threading.excepthook`, which prints a traceback to stderr and lets
  the main thread keep serving), but it dumps a misleading traceback
  into every MCP client's server log on every start of a non-RAG
  install. `rag-optional-dependency`'s spec requires
  `warm_up_in_background()` to no-op (log at INFO and return) when the
  RAG extra isn't installed, without importing the heavy libraries to
  find that out.
- **`improve-approve-proposal-feedback`** / **`fix-approve-proposal-stale-embeddings`** /
  **`add-rule-lesson-deprecation`** — **affected**. Their post-commit
  vector-store hooks (`_embed_and_upsert_after_approve`,
  `_remove_embedding_after_deprecate`, called from `approve_proposal`,
  the deprecate-proposal path, and `promote_rule`) already swallow any
  exception, so a missing extra never fails the write — but each call
  logs a full `logger.exception` traceback and reports
  `embedded: false` / `embedding_removed: false`, which reads as a
  failure on an install where RAG was deliberately left out. This
  change makes those hooks skip quietly when the extra is absent.

## What Changes

- **BREAKING**: `torch`, `sentence-transformers`, and `chromadb` move
  from `pyproject.toml`'s `dependencies` to a new `[project.optional-dependencies]`
  `rag` extra. A plain `pip install axiom-meridian` / `uvx --from axiom-meridian meridian`
  no longer pulls them in; `pip install "axiom-meridian[rag]"` does.
- New structured `RAG_NOT_INSTALLED` error (parallel to `ACCESS_DENIED`)
  returned by `generate_embeddings` when the extra is absent. Today that
  tool does **not** raise without the libraries: `_generate_embeddings_for_table`
  catches the import failure, logs a traceback per table and returns
  `{"processed": 0, "errors": <N>, ...}` — indistinguishable from a real
  embedding failure. The structured error replaces that misleading
  result.
- Post-commit vector-store hooks in `approve_proposal`, the deprecation
  path and `promote_rule` skip quietly (no traceback) when the extra is
  absent, and report `embedded: null` / `embedding_removed: null`
  ("not applicable") instead of `false` ("failed").
- `embedder.warm_up_in_background()` becomes a no-op (with a log line)
  when the extra isn't installed, so server startup never crashes on a
  RAG-less install.
- Full PyPI packaging: complete `pyproject.toml` metadata, a GitHub
  Actions release workflow using PyPI Trusted Publishing (OIDC, no
  stored token) triggered by version tags. Publishing the first release
  and configuring Trusted Publishing on PyPI are **manual tasks for the
  maintainer** (tracked in tasks.md) — this change only adds the
  capability to publish, it does not publish.
- The example knowledge base (`knowledge-base/global/*.md`, today at
  the repo root and **not** included in the wheel — `[tool.hatch.build.targets.wheel]`
  only packages `src/meridian`) moves to package data under
  `src/meridian/examples/` so `meridian setup` can seed it from a PyPI /
  `uvx` install that has no repo clone.
- New `meridian setup` and `meridian doctor` Python subcommands:
  cross-platform (Linux/macOS/Windows) client detection and
  configuration, knowledge-base creation/seeding (preserving the
  no-clobber fix), and diagnostics. `scripts/install.sh` becomes a thin
  wrapper that calls `uvx --from axiom-meridian meridian setup` on
  Linux/macOS; Windows gets the one-line install through `uvx` directly
  (no `.ps1` needed — see design.md for why).
- New skill package at `distribution/skill/meridian/` (`SKILL.md` +
  `references/`), marketplace-safe (no network-calling scripts, no env
  var reads, no obfuscation), packaged as a zip by a new task/script.
  It teaches an agent when to call `query_rules`/`query_lessons`/`audit_pr`/
  `check_feature_against_rules`/the proposal flow, how to detect whether
  the Meridian MCP tools are present, and — if absent — what install
  command to show the user (never to run or fetch itself).
- New Claude Code plugin packaging (`.claude-plugin/plugin.json` +
  `.mcp.json` + `skills/meridian/SKILL.md`) bundling the MCP server and
  the same skill content in one installable unit, and a `server.json`
  for registration in the MCP Registry.
- New CI workflow (the repo has no `.github/` today): tests on
  Linux/macOS/Windows, with and without the `rag` extra, plus the
  version-sync and skill safety checks.
- `README.md` rewritten around one-line install as the primary path,
  source install as the documented alternative, every repository URL
  (`axiom-juma/meridian` and the old `abeljumanuel/axiom-meridian`)
  pointed at `abeljumanuel/axiom-meridian-project`, and the `[rag]`
  extra documented.
- `scripts/install.sh`'s remote one-liner URL updated to
  `raw.githubusercontent.com/abeljumanuel/axiom-meridian-project/main/...`.

## Capabilities

### New Capabilities
- `rag-optional-dependency`: the contract that `torch`/`sentence-transformers`/`chromadb`
  are an opt-in extra, that every tool and startup path degrades to a
  structured `RAG_NOT_INSTALLED` response (or a safe no-op, for warm-up)
  instead of crashing when the extra is absent, and that no read/analyze
  tool's existing SQL-fallback behavior changes.
- `pypi-packaging`: the contract for `pyproject.toml` metadata, the
  `uvx --from axiom-meridian meridian mcp` install target and its
  per-client equivalents, and the tag-triggered Trusted Publishing
  release workflow.
- `cli-setup-and-doctor`: the contract for `meridian setup` and
  `meridian doctor` — cross-platform MCP client detection/configuration
  with user confirmation, non-destructive knowledge-base creation and
  seeding, and diagnosis of the issues currently listed in README's
  Troubleshooting section.
- `skill-package`: the contract for the marketplace-distributable skill
  at `distribution/skill/meridian/` — what it teaches an agent, its
  safety constraints for automated marketplace review, and how it's
  packaged into a zip.
- `distribution-channels`: the contract for the Claude Code plugin
  bundle (MCP server + skill in one unit) and the `server.json` entry
  for the MCP Registry, per the current published schemas for each.
- `readme-and-docs`: the contract for what `README.md` must document
  post-change — one-line install as the primary path, corrected
  repository URLs, and the `[rag]` extra.

### Modified Capabilities
The three installer fixes were synced to main specs after this proposal was
written, so their behavior — now provided by `meridian setup` instead of
`install.sh`'s bash functions — gets explicit deltas:
- `installer-kb-seeding`: MODIFIED — same no-clobber guarantee, now provided
  by `meridian setup` reading bundled package data.
- `installer-claude-mcp-registration`: MODIFIED — same detection and
  mismatch-warning guarantees, compared against `meridian setup`'s resolved
  command instead of `$BIN_DIR`.
- `installer-venv-setup`: REMOVED — `install.sh` no longer creates a venv.

## Impact

- `pyproject.toml` — dependencies restructured (breaking for anyone
  depending on RAG libraries being present by default), full metadata
  added, new `[project.optional-dependencies] rag` group.
- `src/meridian/rag/embedder.py`, `src/meridian/rag/vector_store.py` —
  new `RAG_NOT_INSTALLED`-style guard helpers; `warm_up_in_background()`
  changes to a safe no-op path.
- `src/meridian/server.py`, `src/meridian/tools/knowledge_consumption.py`,
  `src/meridian/tools/knowledge_management.py` — error-path changes only
  where RAG is invoked; no change to non-RAG tool signatures or behavior.
- `src/meridian/tools/knowledge_management.py` — `generate_embeddings`
  entry guard and quiet-skip in the post-commit embed/remove hooks.
- `src/meridian/__main__.py` — new `setup`/`doctor` subcommands;
  `_check_python_environment()`'s "Run: uv sync" hint generalized (it is
  wrong for a PyPI/`uvx` install).
- New `src/meridian/examples/` package data (example KB moved from the
  repo-root `knowledge-base/`).
- New `src/meridian/cli/` (or similar) module(s) implementing them —
  exact layout is a design.md decision.
- `scripts/install.sh` — rewritten as a thin wrapper; `scripts/uninstall.sh`
  reviewed for the same URL/metadata staleness.
- New `.github/workflows/release.yml` and `.github/workflows/ci.yml`.
- `pyproject.toml`'s `dev` extra and root `CLAUDE.md`'s Commands section
  — the RAG test suites (`tests/integration/test_rag_query.py`,
  `tests/unit/test_embedder.py`) need the `rag` extra to run.
- New `distribution/skill/meridian/` and Claude Code plugin directory
  (exact paths decided in design.md) + a packaging task/script.
- New `server.json` at repo root (or `.mcp/` — decided in design.md).
- `README.md` — substantially rewritten.
- No SQLite schema change. No change to any existing MCP tool's
  request/response contract for a client that already has RAG installed.

## Open Questions

1. **Legal author name.** `pyproject.toml`'s `authors` field needs a
   real legal name alongside "Axiom JUMA" for PyPI metadata — placeholder
   `<NOMBRE_LEGAL>` left in `pyproject.toml`'s spec/design; needs the
   maintainer's actual name before the first publish.
2. **PyPI package name availability.** Confirmed unclaimed as of this
   writing by absence from search results, not by a reserved/verified
   claim — the maintainer should do a final check (or just attempt the
   first `uv publish`) before relying on it.
3. **Windows installer shape.** Design.md proposes relying on `uvx`
   alone (no `.ps1` script) since `uv` itself installs via a one-line
   PowerShell command and `uvx --from axiom-meridian meridian setup`
   is OS-agnostic from there. Open question: does the maintainer want a
   thin `install.ps1` anyway for parity/discoverability with
   `install.sh`, even though it isn't technically required?
4. **`distribution/` directory name and plugin repo location.** Should
   the Claude Code plugin and MCP Registry `server.json` live in this
   same repo (simplest, chosen in design.md) or a separate
   `axiom-meridian-plugin` repo (cleaner separation, matches how some
   other projects split "server" from "marketplace packaging")?
5. **Skill zip distribution target.** No specific marketplace was named.
   The skill is built generically to the security constraints of
   marketplace review in general; design.md doesn't assume a specific
   submission target. Confirm if there's a specific one in mind before
   the "upload the zip" manual task.
6. ~~**MCP Registry namespace.**~~ **Resolved:** the server name stays
   `io.github.abeljumanuel/axiom-meridian`, matching the PyPI package
   name, even though the repository is now `axiom-meridian-project`. The
   `io.github.<owner>/` namespace only proves ownership of the GitHub
   *account* `abeljumanuel`, so the part after the slash doesn't have to
   match the repo name. `server.json`'s `repository.url` points at the
   new repo. The same name goes in the `mcp-name:` marker in
   `README.md`, which the registry checks against the PyPI description
   of the release being registered.
7. **Kimi CLI / Cursor MCP config format currency.** `install.sh`'s
   existing Kimi CLI/OpenCode/VSCode blocks were taken as ground truth
   for `cli-setup-and-doctor`'s equivalents; Cursor's own MCP config
   format was not independently re-verified against current Cursor docs
   in this pass (only against general MCP-client conventions) — worth a
   final check before implementation if Cursor support ships.
