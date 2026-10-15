## 0. Repository migration (prerequisite)

- [x] 0.1 **MANUAL (maintainer)**: migrate the code, history and this
  OpenSpec change to `https://github.com/abeljumanuel/axiom-meridian-project`
  and continue implementation there.
  **Verify**: `git remote -v` in the working copy shows
  `abeljumanuel/axiom-meridian-project`; `openspec list` there shows
  `improve-installation-and-distribution`.
- [x] 0.2 **MANUAL (maintainer)**: archive `abeljumanuel/axiom-meridian`
  on GitHub, with a README notice linking to the new repo (it won't
  redirect on its own — this is a new repo, not a rename).
  **Verify**: the old repo shows as archived and its README links to
  `axiom-meridian-project`.
  **Resolved (2026-10-14)**: not applicable — the old repo was deleted
  before the migration (404, not even private under the owner's account),
  so there is nothing to archive; old links 404 instead of serving stale code.
- [x] 0.3 Update `scripts/install.sh`'s remote one-liner (header comment
  and `print_usage()`) to
  `https://raw.githubusercontent.com/abeljumanuel/axiom-meridian-project/main/scripts/install.sh`.
  **Verify**: `grep -rnE 'github(usercontent)?\.com/abeljumanuel/axiom-meridian([^-]|$)|axiom-juma' scripts/` returns no matches.

## 1. RAG optional dependency

- [x] 1.1 Move `torch`, `sentence-transformers`, `chromadb` from
  `[project] dependencies` to a new `[project.optional-dependencies] rag`
  group in `pyproject.toml`.
  **Verify**: `uv sync` (no `--extra rag`) produces a venv without
  `torch`/`sentence_transformers`/`chromadb` importable; record venv size
  before (with all three) vs. after (without) in the PR description.
- [x] 1.2 Add a `rag_installed()` helper (based on
  `importlib.util.find_spec`, never importing the libraries) and
  `RagNotInstalledError` (with `to_response()`) to a new
  `src/meridian/rag/availability.py`.
  **Verify**: unit test asserts `rag_installed()` returns `True`/`False`
  correctly by setting `sys.modules["torch"] = None` (etc.) via
  `monkeypatch.setitem` to simulate absence, and that calling it does
  not add `torch` to `sys.modules`.
- [x] 1.3 Guard `embedder.warm_up_in_background()` to no-op + log when
  `rag_installed()` is `False`.
  **Verify**: unit test calls it in a simulated no-RAG environment and
  asserts no thread is started and no exception raised.
- [x] 1.4 Wire `generate_embeddings` to raise `RagNotInstalledError` at
  entry when `rag_installed()` is `False`, and wire `server.py`'s
  `_security_pattern` to catch it, write the `access_log` row with
  status `"error"`, and serialize `to_response()` — following the
  existing `AccessDeniedError` catch pattern.
  **Verify**: integration test calls the `generate_embeddings` tool in a
  simulated no-RAG environment and asserts the returned JSON has
  `"error": "RAG_NOT_INSTALLED"` (not `{"processed": 0, "errors": N}`,
  today's behavior) and no `ERROR`-level log record was emitted.
- [x] 1.4b Make `_embed_and_upsert_after_approve` and
  `_remove_embedding_after_deprecate` return `None` (skip, no
  `logger.exception`) when `rag_installed()` is `False`; propagate as
  `embedded: null` / `embedding_removed: null` in `approve_proposal`,
  the deprecate-proposal path and `promote_rule` responses.
  **Verify**: integration tests approve a `new` proposal, approve a
  `deprecate` proposal and run `promote_rule` in a simulated no-RAG
  environment; each succeeds, reports `null` for the embedding field,
  and emits no `ERROR`-level log record. Existing tests asserting
  `embedded: true/false` with RAG installed still pass.
- [x] 1.5 Add a regression test locking in that `query_rules`/`query_lessons`
  with `query_text` set fall back to SQL without raising when
  `chromadb`/`sentence_transformers` are not importable.
  **Verify**: `uv run pytest tests/ -k rag_optional` passes; full suite
  (`uv run pytest`) still passes with the `rag` extra installed (no
  regression for the RAG-enabled path).
- [x] 1.5b Guard the RAG-dependent tests (`tests/integration/test_rag_query.py`,
  `tests/unit/test_embedder.py`, and any test that loads the real model)
  with `pytest.importorskip`, and update root `CLAUDE.md`'s Commands
  section to `uv sync --extra dev --extra rag` for the full suite.
  **Verify**: `uv sync --extra dev && uv run pytest` passes (RAG tests
  skipped, not failed); `uv sync --extra dev --extra rag && uv run pytest`
  passes with them running.
- [x] 1.6 Run `uv run ruff check src tests` after all of the above.
  **Verify**: zero lint errors.

## 2. CLI setup and doctor

- [x] 2.1 Design the exact module layout for `src/meridian/cli/` (e.g.
  `setup.py`, `doctor.py`, shared `_mcp_clients.py` helper) and wire
  `setup`/`doctor` into `__main__.py`'s `_COMMANDS` dict.
  **Verify**: `python -m meridian setup --help` and
  `python -m meridian doctor --help` both print usage without error.
- [x] 2.2 Implement cross-platform MCP client detection (Claude Code,
  Kimi CLI, OpenCode, VSCode, Cursor) using `shutil.which` / directory
  checks only — no bash-specific calls.
  **Verify**: unit tests monkeypatch `shutil.which`/filesystem to
  simulate each client present/absent and assert correct detection on
  a simulated Windows path format as well as POSIX.
- [x] 2.3 Implement the "command to register" resolution (persistent
  `meridian` on `PATH` → its absolute path; otherwise
  `uvx --from axiom-meridian[...] meridian mcp`; never a path inside the
  uv cache) and Claude Code config writing with the ported
  `grep '^meridian:'`-equivalent detection and mismatch warning from
  `fix-installer-claude-mcp-check-and-url`, comparing against that
  resolved command instead of `$BIN_DIR`.
  **Verify (extra)**: unit test simulating a `uvx` run (no `meridian` on
  `PATH`, `sys.prefix` under a uv cache dir) asserts the registered
  command is the `uvx` invocation, not `sys.executable`.
  **Verify**: unit test simulates `claude mcp list` output for (a) not
  registered, (b) registered at the same path, (c) registered at a
  different path, and asserts the three distinct behaviors from the
  spec's scenarios.
- [x] 2.4 Implement config writing for Kimi CLI, OpenCode, VSCode,
  Cursor (reusing `config.get_knowledge_base_path()` for KB path
  defaults instead of re-deriving them).
  **Verify**: unit test per client asserts the written config file
  matches the expected JSON shape.
- [x] 2.5 Move the example KB (`knowledge-base/global/*.md`) into package
  data at `src/meridian/examples/knowledge-base/global/` (update the
  README Quick Start paths that reference the old location), then
  implement knowledge-base creation + no-clobber example seeding read
  via `importlib.resources` (porting `fix-installer-seed-overwrites-existing-kb`'s
  skip-with-warning behavior).
  **Verify (extra)**: `uv build` and list the wheel — it contains
  `meridian/examples/knowledge-base/global/clean-code.md` and `java.md`.
  **Verify**: integration test seeds into a directory with a
  pre-existing colliding filename and asserts it is left untouched and a
  warning is emitted; a second test seeds into an empty directory and
  asserts the example files are copied and indexed.
- [x] 2.6 Implement `meridian doctor`'s checks: the command each detected
  client is configured to launch exists and is executable (or `uvx` is
  on `PATH` for a `uvx` registration), running version,
  `libpython` dylib path sanity, cloud-sync venv corruption heuristic
  (duplicate-named files like `name 2.py`), stale `uv run`-based client
  config detection, RAG-installed status.
  **Verify**: unit test per check, each simulating the broken condition
  and asserting `doctor` reports it with a non-zero exit code; a
  "healthy" case asserts exit code 0.
- [x] 2.7 Rewrite `scripts/install.sh` as a thin wrapper: ensure `uv`,
  then delegate to `meridian setup` (via `uv tool install` or `uvx` per
  design.md's D3 — finalize the choice during implementation and record
  the rationale in the PR description).
  **Verify**: manual run of the rewritten `install.sh` in a clean
  container/VM completes and leaves a working `meridian doctor` command
  callable afterward; re-run over the same install exercises the
  already-configured/no-clobber paths without data loss.
- [x] 2.8 Correct `print_usage()`'s Windows guidance to the two-command
  `uv` install + `uvx ... meridian setup` sequence (removing the
  reference to a non-existent `install.ps1`), per design.md's D3.
  **Verify**: `bash scripts/install.sh -h` output no longer mentions
  `install.ps1`.
- [x] 2.9 Run `uv run pytest` and `uv run ruff check src tests`.
  **Verify**: full suite passes; zero lint errors.

## 3. PyPI packaging

- [x] 3.1 Fill in `pyproject.toml` metadata: `authors` (legal name
  placeholder `<NOMBRE_LEGAL>` left for the maintainer to fill before
  first publish — flagged, not silently guessed), `urls` (Homepage,
  Repository, Issues — all under
  `https://github.com/abeljumanuel/axiom-meridian-project`), `classifiers`,
  `keywords`.
  **Verify**: `uv build` succeeds; `python -m twine check dist/*` (or
  equivalent) reports valid metadata.
- [x] 3.2 Confirm the `axiom-meridian` PyPI name is still unclaimed
  immediately before this task (not just at proposal-writing time).
  **Verify**: manual check of `pypi.org/project/axiom-meridian/` returns
  404 (or the maintainer's own prior reservation).
- [x] 3.3 Write `.github/workflows/release.yml`: triggered on `v*` tags,
  `uv build`, publish via `pypa/gh-action-pypi-publish` with
  `permissions: id-token: write` and no stored token.
  **Verify**: workflow YAML lints (`actionlint` or GitHub's own
  validation on a draft PR); a dry run against TestPyPI (if the
  maintainer sets that up manually) succeeds, or at minimum the build
  step (`uv build`) runs green in CI without the publish step erroring
  on missing OIDC claims in a non-tag push (should simply not trigger).
- [x] 3.4 Document the per-client `uvx --from axiom-meridian meridian mcp`
  install target and its VS Code/OpenCode/Kimi CLI/Cursor equivalents
  (feeds into task 6.x's README rewrite — written here first so 6.x can
  reference it). Include how to upgrade (`uv tool upgrade axiom-meridian`
  / `uvx --refresh ...`), since `uvx` keeps serving the cached version.
  **Verify**: each documented client config is syntactically valid for
  that client (validated against each client's own config schema/docs).
- [x] 3.4b Write `.github/workflows/ci.yml` per design.md's D7: ruff +
  pytest on Linux/macOS/Windows without the `rag` extra, one Linux job
  with `--extra rag`, plus the version-sync (5.5) and skill safety scan
  (4.3) scripts once they exist.
  **Verify**: the workflow runs green on a draft PR, including the
  `windows-latest` job.
- [x] 3.4c Add the MCP Registry ownership marker
  `<!-- mcp-name: io.github.abeljumanuel/axiom-meridian -->` to
  `README.md` (after Open Question #6 is answered) so it ships in the
  PyPI long description of the first release.
  **Verify**: `uv build` and confirm the marker appears in the wheel's
  `METADATA` description.
- [x] 3.5 **MANUAL (maintainer)**: create/confirm the PyPI account.
- [x] 3.6 **MANUAL (maintainer)**: configure Trusted Publishing on PyPI
  for the `axiom-meridian` project with owner `abeljumanuel`,
  repository `axiom-meridian-project`, workflow `release.yml` (not the
  old `axiom-meridian` repo — see design.md D6) — for a not-yet-existing project this is a
  *pending publisher* (no manual upload needed; the first tagged
  workflow run creates the project).
- [x] 3.7 **MANUAL (maintainer)**: push the first `v*` tag and confirm
  the first release publishes successfully.
  **Done**: tag `v0.1.0`; `release.yml` run 38689549840 (build + publish
  green, publish approved by the `pypi` environment reviewer); PyPI shows
  `axiom-meridian` 0.1.0 with `License-Expression: Apache-2.0`;
  `uvx --isolated --from axiom-meridian meridian version` installs from the
  index; GitHub Release `v0.1.0` created with the CHANGELOG notes.

## 4. Skill package

- [x] 4.1 Author `distribution/skill/meridian/SKILL.md` with standard
  frontmatter (`name: meridian`, a `description` saying what it does and
  when to use it; no `metadata.allowed_tools`, no `allowed-tools`)
  covering tool selection guidance (query_rules/query_lessons/audit_pr/
  check_feature_against_rules/proposal flow, referring to tools by base
  name since the MCP prefix differs between direct and plugin installs),
  tool-availability detection via normal tool discovery, and the literal
  install-command fallback text (no `curl | sh` / `irm | iex` lines).
  **Verify**: manual read-through against each scenario in the
  `skill-package` spec; no first-person claims about data the skill
  doesn't have.
- [x] 4.2 Add `distribution/skill/meridian/references/` with any
  supporting reference material (tool parameter reference, example
  flows) as plain Markdown.
  **Verify**: all files are plain text/Markdown, human-readable, no
  binary or encoded blobs.
- [x] 4.3 Run a safety scan over `distribution/skill/meridian/`: grep
  for network-call patterns (`curl`, `wget`, `requests`, `urllib`,
  `http.client`, `socket`, `irm`, `iex`), environment-variable access in
  code (`os.environ`, `getenv`, `process.env`; `$VARNAME` only inside
  script files or fenced shell blocks), and any executable script files.
  **Verify**: all scans return zero matches; document the exact grep
  commands run in the PR description so they're repeatable in CI later.
- [x] 4.4 Add a packaging task (Python `zipfile`-based script, for
  Windows-dev parity) that zips `distribution/skill/meridian/` into
  `meridian-skill.zip`.
  **Verify**: running the task produces a zip whose extracted contents
  byte-for-byte match the source directory.

## 5. Distribution channels

- [x] 5.1 Create the Claude Code plugin directory (location decided
  during implementation per design.md's Open Question #4 — default:
  same repo, e.g. `distribution/plugin/meridian/`) with
  `.claude-plugin/plugin.json` and `.mcp.json` per design.md's D5.
  **Verify**: `claude plugin validate` (if available in the dev
  environment) reports no errors; otherwise manual JSON-schema
  cross-check against the current plugin docs.
- [x] 5.2 Copy `distribution/skill/meridian/SKILL.md` into the plugin's
  `skills/meridian/SKILL.md` and add a verification step (diff check)
  rather than a symlink.
  **Verify**: a diff between the two files is empty.
- [x] 5.3 Load the plugin locally with `--plugin-dir` and confirm `/mcp`
  shows the Meridian server connected under the plugin's namespace.
  **Verify**: manual test in a local Claude Code session.
- [x] 5.4 Author `server.json` at the repo root per design.md's D5,
  validating it against the schema referenced by its `$schema` field.
  **Verify**: JSON Schema validation (e.g. via a quick `jsonschema`
  Python check against the fetched schema) passes with zero errors.
- [x] 5.5 Add a CI check (or pre-commit-style script) that keeps
  `plugin.json`'s `version`, `server.json`'s `version` and
  `packages[0].version`, and `src/meridian/__init__.py`'s `__version__`
  in sync with `pyproject.toml`'s `version` (or make `pyproject.toml`'s
  version dynamic from `__init__.py` and drop it from the check).
  **Verify**: deliberately mismatch one version locally and confirm the
  check fails; restore and confirm it passes.
- [x] 5.6 **MANUAL (maintainer)**: submit `server.json` to the MCP
  Registry (requires proving `io.github.abeljumanuel` ownership).
  **Done**: `io.github.abeljumanuel/axiom-meridian` 0.1.0 is `active` in
  the MCP Registry.
- [x] 5.7 **MANUAL (maintainer)**: submit the plugin to a Claude Code
  marketplace listing, and upload `meridian-skill.zip` to the intended
  skill marketplace (target confirmed per proposal.md's Open Question #5).
  **Done** via the repo's own marketplace (plugin installed and verified).
  Listing in third-party marketplaces and uploading the skill zip are
  deferred: no destination was chosen.

## 6. README and docs

- [x] 6.1 Rewrite README.md's Installation section to lead with the
  one-line `uvx`/PyPI install (Linux/macOS/Windows uniformly), moving
  the `git clone` + `uv sync` path under a clearly labeled "From source"
  subsection.
  **Verify**: manual read-through confirms the one-line path appears
  before any `git clone` instruction.
- [x] 6.2 Replace every repository URL in `README.md` — both
  `axiom-juma/meridian` and the old `abeljumanuel/axiom-meridian` — with
  `abeljumanuel/axiom-meridian-project`. Leave the
  `mcp-name: io.github.abeljumanuel/axiom-meridian` marker as is (it is
  the registry server name, not a URL).
  **Verify**: `grep -rnE 'github(usercontent)?\.com/abeljumanuel/axiom-meridian([^-]|$)|axiom-juma' README.md pyproject.toml server.json`
  returns no matches.
- [x] 6.3 Document the `[rag]` extra: what it enables, how to install
  it, and the `RAG_NOT_INSTALLED` error shape, cross-referencing the
  `rag-optional-dependency` capability's behavior.
  **Verify**: manual read-through against the `readme-and-docs` spec's
  scenarios.
- [x] 6.4 Update the Scripts section to describe `install.sh`'s new
  thin-wrapper behavior and add `meridian setup`/`meridian doctor` to
  the Tool Reference / CLI documentation.
  **Verify**: manual read-through; cross-check every documented command
  actually exists (`python -m meridian setup/doctor --help` succeeds).
- [x] 6.5 Update `scripts/uninstall.sh` if it references any now-stale
  URL or assumption (reviewed as part of this change per the proposal's
  Impact section, not a new capability of its own).
  **Verify**: `grep -rnE 'github(usercontent)?\.com/abeljumanuel/axiom-meridian([^-]|$)|axiom-juma' scripts/uninstall.sh` returns
  no matches; `bash scripts/uninstall.sh -h` (or equivalent) still runs.

## 7. Final verification

- [x] 7.1 Run the full test suite and lint one more time after all
  sections above.
  **Verify**: `uv run pytest` and `uv run ruff check src tests` both
  pass clean.
- [x] 7.2 Fresh-environment smoke test: in a clean container/VM with
  only `uv` installed (no repo clone), run
  `uvx --from <local build or TestPyPI> meridian mcp` and confirm the
  server starts; then run `meridian setup` and confirm client
  detection/config writing works end to end.
  **Verify**: documented command transcript attached to the PR.
  **Done (substituted)**: not run in a container (no Docker available).
  Covered by the CI matrix (Linux/macOS/Windows) and by the real install
  from PyPI with `uvx --isolated --from axiom-meridian`.
- [x] 7.3 Confirm venv-size reduction claim from task 1.1 with a final
  side-by-side measurement (`du -sh` of a venv built from the old vs.
  new `pyproject.toml`) and include it in the PR description.
