---
name: release-version
description: Prepare and cut a new Axiom Meridian release — decide the SemVer bump, update every version declaration and the CHANGELOG, verify the build and create the release tag that CI publishes to PyPI. Use when the user asks to release, bump or check the version, cut a tag, write the changelog or publish to PyPI.
---

# Release a new version of Axiom Meridian

Take a release from "what changed?" to an annotated `vX.Y.Z` tag. Publishing is
done by CI: pushing the tag runs `.github/workflows/release.yml`, which builds
and publishes to PyPI with Trusted Publishing. Never publish from this machine.

**Ask the user before every irreversible step**: writing the new version, creating
the tag, pushing, and creating the GitHub release. A PyPI version number can
never be reused, not even after a yank.

## Where the version lives

`src/meridian/__init__.py` (`__version__`) is the single source of truth;
`pyproject.toml` reads it dynamically. It is mirrored in:

- `server.json` (2 keys: the server and its PyPI package)
- `.claude-plugin/marketplace.json`
- `distribution/plugin/meridian/.claude-plugin/plugin.json`

Never edit these by hand. Use `scripts/release_version.py`:

```bash
python3 scripts/release_version.py current
python3 scripts/release_version.py check [X.Y.Z] [--require-changelog]
python3 scripts/release_version.py bump X.Y.Z [--dry-run]
```

If a new file starts declaring the version, add it to `VERSION_FILES` in that
script in the same change. The `check-release-version.sh` hook blocks any
`git tag vX.Y.Z` that `check X.Y.Z --require-changelog` rejects, and any local
`uv publish` / `twine upload`.

## 1. Preconditions

Check each one and stop with a clear message if it fails:

- Clean working tree: `git status --porcelain` is empty.
- On `main` and up to date: `git fetch origin && git status -sb`.
- `uv sync --extra dev`, then `uv run pytest` passes and `uv run ruff check src tests` is clean.
- `python3 scripts/release_version.py check` passes (declarations already agree).
- No OpenSpec change in `openspec/changes/` that is implemented but not archived.
  If there is one, offer to archive it first (openspec-archive-change).

## 2. Find what changed

- Last release: `git describe --tags --abbrev=0 --match 'v*'` (none → first release).
- Commits since then: `git log <last-tag>..HEAD --oneline` (or the whole history).
- OpenSpec changes archived since then: their `proposal.md` is the best source
  for release notes.

## 3. Decide the version (SemVer, PEP 440 spelling)

What counts as **breaking** for Meridian:

- An MCP tool removed or renamed, a required parameter added, a parameter
  removed, or a response format changed.
- A non-additive database change (dropped or renamed table/column) or a
  migration that can lose data.
- An environment variable, CLI command or default access level removed or changed.
- The license changed.

Rules:

- While on `0.x`: breaking changes or new features → MINOR (`0.1.0` → `0.2.0`);
  fixes and docs only → PATCH (`0.1.0` → `0.1.1`).
- From `1.0.0` on: breaking → MAJOR, features → MINOR, fixes → PATCH.
- Pre-releases: `0.2.0rc1`, `0.2.0b1`, `0.2.0a1` (tag `v0.2.0rc1`).

Show the proposed version, why, and the list of changes. **Wait for the user to
confirm** before changing anything.

## 4. Write the release notes

Keep `CHANGELOG.md` in Keep a Changelog format. The script creates the file if
it is missing. Before bumping, fill the `## [Unreleased]` section with the notes:

```markdown
## [Unreleased]
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
```

- Omit empty subsections. Write for users: what changed for them and what they
  must do. Link the OpenSpec change when useful.
- Breaking changes go first under `### Changed` or `### Removed`, prefixed with
  **BREAKING:**, with a migration note.

## 5. Bump

1. `python3 scripts/release_version.py bump X.Y.Z --dry-run` and show the output.
2. After confirmation, run it without `--dry-run`. It updates every declaration
   and moves `[Unreleased]` under `## [X.Y.Z] - YYYY-MM-DD`, leaving a fresh
   empty `[Unreleased]` on top. If it warns that `[Unreleased]` was empty, go
   back to step 4.
3. Show `git diff` for review.

## 6. Verify the build

- `rm -rf dist && uv build`
- Wheel metadata: `unzip -p dist/*.whl '*/METADATA' | head -20` shows the new
  `Version` and the expected license.
- Clean-environment smoke test:
  `uvx --from ./dist/<wheel-file> meridian version` prints the new version.
- `python3 scripts/release_version.py check X.Y.Z --require-changelog`

## 7. Commit and tag (ask first)

- Commit only the release files: `chore(release): vX.Y.Z`.
- Annotated tag: `git tag -a vX.Y.Z -m "vX.Y.Z"`. The hook re-checks everything.
- Push only after explicit confirmation: `git push origin main --follow-tags`.
  This starts the PyPI publish in CI.

## 8. After the release (ask first)

- GitHub release with the CHANGELOG section as notes:
  `gh release create vX.Y.Z --title "vX.Y.Z" --notes-file <section.md>`
  (add `--prerelease` for a/b/rc versions).
- Report the CI run, the PyPI page and the GitHub release once the workflow ends.
- The MCP Registry entry (`server.json`) is published separately; remind the
  user if they publish there.

## Never

- Run `uv publish` or `twine upload` locally.
- Delete, move or reuse a tag that was already pushed. Fix forward with a new
  PATCH version.
- Yank a PyPI release unless the user explicitly asks.
- Edit version strings by hand instead of using the script.
