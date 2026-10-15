## Why

Axiom Meridian is about to make its first public release (PyPI package,
Claude Code plugin, MCP Registry entry, distributable skill — all defined by
`improve-installation-and-distribution`). Its license is declared as MIT in a
few places, but **there is no `LICENSE` file at all**. So the project is not
verifiably licensed today, and every channel about to publish it would ship
under that ambiguity. Moving to **Apache License 2.0** before the first
release closes that gap and adds three things MIT lacks:

- an explicit patent grant;
- a `NOTICE` mechanism for attribution;
- a clause that excludes the trademark (section 6), which protects the
  "Axiom Meridian" / "Axiom JUMA" names separately from the code.

Doing it now is the cheap moment. After a PyPI release, every published
artifact is permanently MIT, and the change could only apply going forward.

## Prerequisite / blocking check: sole authorship

`git shortlog -sne --all` shows a single author under two identities with
the same email (`Juan Rojas` and `juanrojasdev`,
`abeljumanuel.rojas@gmail.com`). **Not a blocker** — with no third-party
contributors in the history, the copyright holder can relicense
unilaterally.

**Caveat (resolved 2026-10-14):** this branch's git history only covers 3
commits, essentially the documentation baseline. `src/` and `tests/` have
**no tracked files** yet: the code was migrated from the old
`abeljumanuel/axiom-meridian` repository, which has since been deleted, so
`git shortlog` cannot vouch for the code's authorship. The maintainer has
confirmed being the only contributor to that repository.

## Dependency on `improve-installation-and-distribution`

This change **must be applied before that change's first PyPI release**
(its task 3.7, the first `v*` tag). It also touches files that change
created on this same branch and that are not yet released, so it applies
*on top of* them:

- `pyproject.toml` already uses the PEP 639 SPDX form
  (`license = "MIT"`, `hatchling>=1.27`), with no license classifiers. The
  brief assumed `license = { text = "MIT" }`; that is outdated.
- `distribution/plugin/meridian/.claude-plugin/plugin.json` has
  `"license": "MIT"`.
- `distribution/skill/meridian/SKILL.md` and its plugin copy have no
  `license` frontmatter yet.
- The README Installation section and `docs/installation.md`.

Nothing has been published under MIT through those channels. The only
public MIT declaration is the GitHub repository's README, which has said
"MIT" since commit `a262b0e`.

## What Changes

- **New `LICENSE`**: the official, unmodified Apache License 2.0 text,
  fetched from `https://www.apache.org/licenses/LICENSE-2.0.txt`, not
  written from memory.
- **New `NOTICE`**: names the project and the copyright holder
  (`Copyright 2026 Juan Manuel Rojas González (Axiom JUMA)`), and states that
  "Axiom Meridian" and "Axiom JUMA" are trademarks of their owner.
- **`pyproject.toml`**:
  - `license = "Apache-2.0"`, plus `license-files = ["LICENSE", "NOTICE"]`.
  - No license classifiers (PEP 639 deprecates them).
  - `authors` becomes `Juan Manuel Rojas González` + "Axiom JUMA" (the accent is missing
    today, in `pyproject.toml`, `plugin.json` and `marketplace.json`).
  - The wheel's METADATA carries `License-Expression: Apache-2.0`, and
    LICENSE/NOTICE ship in both the wheel and the sdist.
- **Short SPDX headers** (`SPDX-License-Identifier: Apache-2.0` + an
  `SPDX-FileCopyrightText` line) on every `.py` file under `src/meridian/`
  and on every shell and Python script under `scripts/`. A test fails if a
  file is missing its header. design.md covers the alternatives.
- **Documentation**:
  - The README License section moves to Apache 2.0, with links to
    LICENSE/NOTICE, a trademark note, and a note on the MIT transition.
  - A new "Third-party" note says `.claude/skills/openspec-*` keep their
    own MIT license.
  - `docs/01-project-charter.md` and `docs/design/README.md` get the
    license line updated.
  - `docs/design/meridian-implementation-plan.md` gets only a dated note,
    with no history rewrite.
  - New `CHANGELOG.md` with the entry.
- **New `CONTRIBUTING.md`**: contributions are accepted under Apache 2.0
  (section 5) and signed off under the Developer Certificate of Origin
  (`Signed-off-by:`).
- **Distribution alignment**:
  - The plugin manifest and the distributable skill (both copies) declare
    `Apache-2.0`.
  - Skills that `generate_project_skills` writes for *users'* projects
    carry **no** Meridian license. That content belongs to the user, and a
    new test guarantees it.
- **Dependency compatibility**: a verified table of direct-dependency
  licenses in design.md. They are all permissive and compatible.
- **Not touched**: `.claude/skills/openspec-*` (third-party, OpenSpec,
  MIT), user knowledge content, git history.

## Capabilities

### New Capabilities
- `license-files`: `LICENSE` holds the verbatim Apache 2.0 text and
  `NOTICE` holds the attribution and trademark statement.
- `package-metadata`: PEP 639 license metadata in `pyproject.toml`, with
  LICENSE/NOTICE inside the wheel and sdist, verified from the built
  artifacts.
- `source-headers`: SPDX headers on Meridian's own source files, enforced
  by a test.
- `documentation`: README license section, third-party note, transition
  note, charter and design-doc updates, CHANGELOG entry.
- `contributions`: CONTRIBUTING.md with the inbound=outbound Apache 2.0
  terms and DCO sign-off.
- `dependency-compatibility`: a recorded, verified license table for direct
  dependencies, with the compatibility conclusion.
- `distribution-alignment`: every Meridian-distributed skill/plugin declares
  Apache-2.0, and user-generated skills never carry Meridian's license.

### Modified Capabilities
(none) — no existing main spec defines license behavior.
`ecosystem-integration`'s "Generate an agent-loadable skill" requirement
keeps its behavior. The new no-license guarantee for generated skills lives
in `distribution-alignment` so it can be tested in isolation.

## Impact

- **New files**: `LICENSE`, `NOTICE`, `CONTRIBUTING.md`, `CHANGELOG.md`,
  `tests/unit/test_license_headers.py`, plus a test for generated skills.
- **Modified**:
  - `pyproject.toml`
  - every `src/meridian/**/*.py` (header lines only, no code change)
  - `scripts/*.sh` and `scripts/*.py`
  - `README.md`, `docs/01-project-charter.md`, `docs/design/README.md`,
    `docs/design/meridian-implementation-plan.md` (note only)
  - `distribution/plugin/meridian/.claude-plugin/plugin.json`
  - both copies of the distributable `SKILL.md`
- **No runtime behavior change** and no API or schema change. Tool
  responses are identical.
- **Legal**: copies already obtained under MIT stay under MIT; that grant
  can't be revoked. The relicense covers this version onward.

## Open Questions

None. All were resolved by the maintainer on 2026-10-14:

### Resolved (2026-10-14, maintainer)

- **Academic program IP:** the capstone belongs to an academic program
  (not a university). The maintainer holds proof that the rights are their
  own, so nothing blocks the relicense or the release.

- **Legal name:** `Juan Manuel Rojas González` (with the accent). It replaces `<NOMBRE_LEGAL>`
  in NOTICE and the SPDX headers, and fixes the unaccented "Gonzalez"
  currently in `pyproject.toml`, `plugin.json` and `marketplace.json`.
- **Authorship of the migrated code:** the maintainer was the only
  contributor to the deleted `abeljumanuel/axiom-meridian` repository.
- **Copyright year:** `2026`.
- **Headers on tests:** no. The scope stays `src/meridian/` + `scripts/`,
  as recommended in design.md D4.
