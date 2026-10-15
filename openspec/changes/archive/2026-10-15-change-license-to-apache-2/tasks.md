## 0. Preconditions (manual, maintainer)

- [x] 0.1 **MANUAL (maintainer)**: confirm the exact legal name (accents
  included) to replace `<NOMBRE_LEGAL>`.
  **Resolved (2026-10-14)**: `Juan Manuel Rojas González`.
- [x] 0.2 **MANUAL (maintainer)**: confirm that the academic program's
  terms don't assign rights to the program or mandate a license.
  **Resolved (2026-10-14)**: the maintainer holds proof that the rights are
  their own (kept privately).
- [x] 0.3 **MANUAL (maintainer)**: confirm sole authorship of the code
  migrated from the deleted `abeljumanuel/axiom-meridian` repository (no
  git history on this branch).
  **Resolved (2026-10-14)**: the maintainer was the only contributor.
- [x] 0.4 **MANUAL (maintainer)**: decide the copyright year and whether
  `tests/` gets headers.
  **Resolved (2026-10-14)**: year `2026`; no headers in `tests/`.

## 1. License files

- [x] 1.1 Fetch `https://www.apache.org/licenses/LICENSE-2.0.txt` into
  `LICENSE` unmodified. Record the SHA-256 in this task.
  **Verify**: re-download it and `cmp` it against `LICENSE`, with no
  output; `head -3 LICENSE` shows the "Apache License / Version 2.0" header.
  **Done (2026-10-14)**: `cmp` identical; SHA-256
  `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
- [x] 1.2 Create `NOTICE` per design.md D2, with the legal name and year
  from 0.1/0.4.
  **Verify**: it contains `Axiom Meridian`, the `Copyright … (Axiom JUMA)`
  line and the trademark statement; `grep -c "<NOMBRE_LEGAL>" NOTICE`
  returns 0.
- [x] 1.3 **MANUAL (maintainer)**: review the final NOTICE wording.
  **Verify**: approval noted here.
  **Approved (2026-10-15)** by the maintainer, wording unchanged.

## 2. Package metadata

- [x] 2.1 Re-check in the current hatch docs and release notes the minimum
  hatchling version with PEP 639 support (`license` SPDX string +
  `license-files`). Keep or raise `requires = ["hatchling>=1.27"]`
  accordingly.
  **Verify**: the source URL and the version found are noted here.
  **Done (2026-10-14)**: per
  https://github.com/pypa/hatch/blob/master/docs/history/hatchling.md —
  1.26.0 adopted the final `license-files` spec (array of globs) and core
  metadata 2.4; 1.27.0 made metadata 2.4 the default (needed for
  `License-Expression`/`License-File` without extra config). The
  `hatchling>=1.27` floor stays.
- [x] 2.2 In `pyproject.toml`:
  - set `license = "Apache-2.0"` and `license-files = ["LICENSE", "NOTICE"]`;
  - update the license comment;
  - add `"/LICENSE"` and `"/NOTICE"` to `[tool.hatch.build.targets.sdist] include`;
  - confirm there are no `License ::` classifiers;
  - fix `authors` to `Juan Manuel Rojas González` + "Axiom JUMA" (accent missing today).
  **Verify**: `grep -n 'license' pyproject.toml` shows only the Apache
  values; `grep -rn "Rojas Gonzalez" pyproject.toml distribution .claude-plugin`
  returns no matches.
- [x] 2.3 Build and inspect both artifacts.
  **Verify**: `uv build`; the wheel `METADATA` has
  `License-Expression: Apache-2.0` and `License-File: LICENSE` /
  `License-File: NOTICE`, and no `Classifier: License ::`; the wheel
  contains `*.dist-info/licenses/LICENSE` and `NOTICE`; the sdist contains
  top-level `LICENSE` and `NOTICE` and still none of `.claude/`, `.atl/`,
  `changes/`, `openspec/`, `docs/`; `uvx twine check dist/*` passes.

## 3. Source headers

- [x] 3.1 Write `tests/unit/test_license_headers.py` first (scope per
  design.md D4: `src/meridian/**/*.py`, `scripts/*.sh`, `scripts/*.py`;
  `tests/` excluded per 0.4). It checks both SPDX lines within the
  first five lines after an optional shebang, and on failure prints the
  offending files and the exact two lines to add.
  **Verify**: it fails before 3.2, listing every in-scope file.
- [x] 3.2 Add the two-line SPDX header to every in-scope file, after a
  shebang if there is one and before the module docstring.
  **Verify**: the test from 3.1 passes; `git diff --stat` shows only
  additions in those files; spot-check that `import meridian.server` keeps
  the same `__doc__`; `bash -n scripts/*.sh` passes.

## 4. Documentation

- [x] 4.1 Replace `README.md`'s License section per design.md D8:
  Apache-2.0 with links to `LICENSE`/`NOTICE`, the trademark note
  (section 6), the MIT transition note, a Third-party note for
  `.claude/skills/openspec-*`, and a link to `CONTRIBUTING.md`.
  **Verify**: manual read against the `documentation` spec scenarios.
- [x] 4.2 Update `docs/01-project-charter.md` (License row) and
  `docs/design/README.md` (License section) to Apache-2.0.
  **Verify**: `grep -nw MIT` in both files only matches transition or
  third-party wording, if any.
- [x] 4.3 Add a short dated note to
  `docs/design/meridian-implementation-plan.md` next to its historical
  `license = ...` snippet, referencing `change-license-to-apache-2`,
  without editing the snippet.
  **Verify**: `git diff` on that file shows only the added note.
- [x] 4.4 Create `CHANGELOG.md` in Keep a Changelog format with
  `## [Unreleased]` → "Changed: relicensed from MIT to Apache-2.0" (plus
  the NOTICE and CONTRIBUTING additions under "Added").
  **Verify**:
  `python3 scripts/release_version.py check --require-changelog` (or the
  equivalent check the script offers for Unreleased content) accepts the
  file.

## 5. Contributions

- [x] 5.1 Create `CONTRIBUTING.md`: inbound = outbound under Apache-2.0
  (section 5); DCO sign-off with `git commit -s` and a link to
  https://developercertificate.org/; the dev setup commands
  (`uv sync --extra dev --extra rag`, `uv run pytest`,
  `uv run ruff check src tests scripts`).
  **Verify**: manual read against the `contributions` spec; the link
  resolves.

## 6. Dependency compatibility

- [x] 6.1 Re-run the installed-metadata license query for every direct
  dependency (runtime, `rag`, dev) and reconcile it with design.md D6.
  **Verify**: every dependency in `pyproject.toml` appears in the table
  with a matching license; update the table if versions drifted.

## 7. Distribution alignment

- [x] 7.1 Set `"license": "Apache-2.0"` in
  `distribution/plugin/meridian/.claude-plugin/plugin.json`, and fix the
  author name to `Juan Manuel Rojas González` there and in `.claude-plugin/marketplace.json`'s
  `owner`.
  **Verify**: `claude plugin validate distribution/plugin/meridian` and
  `claude plugin validate .` both pass.
- [x] 7.2 Add `license: Apache-2.0` to the frontmatter of
  `distribution/skill/meridian/SKILL.md`, then re-copy the skill into
  `distribution/plugin/meridian/skills/meridian/`.
  **Verify**: `python scripts/check_versions.py` passes (byte-identical
  copy); `python scripts/check_skill_safety.py` passes;
  `python scripts/package_skill.py` passes.
- [x] 7.3 Add a test to `tests/integration/test_skill_generator.py`
  asserting that the files `generate_project_skills` writes (SKILL.md,
  `references/rules.md`, AGENTS.md) contain none of `license:`, `SPDX-`,
  `Apache`, `Axiom JUMA`.
  **Verify**: the test passes; temporarily adding `license: Apache-2.0` to
  `_build_skill_md` makes it fail, then revert.

## 8. Final verification

- [x] 8.1 Residual-MIT grep:
  `grep -rIwn MIT . --exclude-dir=.git --exclude-dir=.venv --exclude=uv.lock`
  minus `.claude/skills/openspec-*` and `openspec/changes/`.
  **Verify**: the only remaining hits are the README transition/third-party
  notes and the historical snippet in
  `docs/design/meridian-implementation-plan.md` (with its note).
- [x] 8.2 Placeholder grep: `grep -rn "<NOMBRE_LEGAL>" NOTICE pyproject.toml
  src scripts README.md CONTRIBUTING.md`.
  **Verify**: no matches (release blocker otherwise).
- [x] 8.3 Full suite and lint, with and without the `rag` extra, plus the
  distribution checks.
  **Verify**: `uv run pytest` is green in both environments;
  `uv run ruff check src tests scripts` is clean;
  `scripts/check_versions.py`, `scripts/check_skill_safety.py` and
  `scripts/package_skill.py` all pass; `uv build` + the 2.3 inspection
  still holds.
- [x] 8.4 **MANUAL (maintainer)**: commit (with a `Signed-off-by:` line,
  per the new DCO) and make sure this lands before
  `improve-installation-and-distribution`'s first `v*` tag, then cut the
  release.
  **Verify**: `git log -1` shows the commit; the first published PyPI
  release page shows "License: Apache-2.0".
  **Done**: commit `f800112` signed off (DCO), merged via PR #3, published
  in v0.1.0 (PR #4).
