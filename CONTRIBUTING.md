# Contributing to Axiom Meridian

Thanks for your interest in improving Axiom Meridian.

## License of contributions

Axiom Meridian is licensed under the [Apache License, Version 2.0](LICENSE).
By submitting a contribution (a pull request, patch, or any other material
intended for inclusion), you agree that it is licensed under the same
Apache License 2.0, as described in section 5 of the license ("Submission of
Contributions"). There is no separate contributor license agreement.

The project names "Axiom Meridian" and "Axiom JUMA" are not licensed for
use by contributors (section 6 of the license).

## Developer Certificate of Origin (DCO)

Every commit must be signed off, certifying that you wrote the change or
otherwise have the right to submit it under the project's license, as stated
in the [Developer Certificate of Origin 1.1](https://developercertificate.org/).
Sign off by adding the `-s` flag when committing:

```bash
git commit -s -m "Describe your change"
```

This appends a line with the name and email from your git configuration:

```text
Signed-off-by: Your Name <you@example.com>
```

Use your real name. Pull requests with unsigned commits are asked to amend
them (`git commit --amend -s`, or `git rebase --signoff` for several
commits).

## Development setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/abeljumanuel/axiom-meridian-project.git
cd axiom-meridian-project
uv sync --extra dev --extra rag     # the rag extra is needed for the full test suite
uv run pytest
uv run ruff check src tests scripts
```

Every Python and shell source file under `src/meridian/` and `scripts/`
starts with the SPDX header below (after a shebang, if any). A test fails if
a new file is missing it:

```python
# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
```

## Proposing changes

New features and behavior changes are tracked as
[OpenSpec](https://github.com/Fission-AI/OpenSpec) changes under
`openspec/changes/` (proposal, delta specs, design, tasks). Open an issue or
a change proposal before starting larger work, so the approach can be agreed
first.

## Branches, tickets and commits

Work starts from a ticket in [`docs/06-work-tickets.md`](docs/06-work-tickets.md)
(`TICKET-NNN`). A ticket needs evidence of a real need (a reproduction, an
audit report, a user story); without it, it stays `Proposed`. `docs/` and
`chore/` branches may go without a ticket.

**Branch name:** `<type>/<NNN>-<short-description>`, lowercase, `a-z0-9-`
only, in English, 2-5 words, branched from an up-to-date `main`.

| Type | Use |
|---|---|
| `feat/` | New capability |
| `fix/` | Bug fix |
| `docs/` | Documentation only |
| `refactor/` | No behavior change |
| `test/` | Tests only |
| `chore/` | Tooling, maintenance, archiving changes |
| `release/` | `release/vX.Y.Z` |

Examples: `fix/021-index-advances-id-counters`, `docs/contributing-conventions`.

- One branch = one purpose = one pull request. If the title needs "and",
  split it.
- When there is an OpenSpec change, reuse its name after the number
  (`fix/021-index-advances-id-counters` and
  `openspec/changes/fix-index-advances-id-counters`).
- Commit subjects use Conventional Commits and cite the ticket, in 70
  characters or fewer: `fix(TICKET-021): advance id_counters on hand-written
  code index`.
- Delete the branch after merging.

## Pull request description

The description is what the reviewer decides on. It has to let them judge,
without re-deriving it, why the change exists and why it will not break what
already works. The template in `.github/pull_request_template.md` enforces the
sections; these are the rules behind them.

1. **Link, don't restate.** Cite the ticket and the OpenSpec change; the
   formal requirements live there.
2. **Evidence before claims.** For a fix, show the reproduction and the
   measured result before and after. "Fixes X" without a reproduction is not
   enough.
3. **State the scope both ways.** Say what changes and what deliberately does
   not. Mark anything that alters existing behavior as **BREAKING**.
4. **Name the regression safety.**
   - Tests that fail on `main` and pass on the branch, by name. A test that
     passes on `main` proves nothing about the fix.
   - Full suite with and without the `rag` extra, as CI runs it. The
     `benchmark` tests are excluded by default (`pyproject.toml`), so run
     `uv run pytest -m benchmark` when the change touches ids, queries or
     indexing.
   - Every invariant from `CLAUDE.md` the change touches (id counters,
     `write_block`, `shift_offsets_after`, `sync_tags`, `strip_private_tags`,
     access levels) and how it stays intact.
   - Contract surfaces: MCP tool signatures, DB schema and migrations, atomic
     block labels, CLI commands. List any that change.
   - Compatibility with an existing knowledge base, tried on a copy, never on
     the real one.
5. **Report results exactly:** command, pass/fail and counts, as in
   `uv run pytest`: `468 passed`.
6. **Say what you did not verify.** An honest "Not verified" section is more
   useful to the reviewer than a clean-looking one.
7. **Keep docs in step:** update `CHANGELOG.md` (Unreleased) and the affected
   `CLAUDE.md`/ADR text in the same pull request, and leave the ticket at
   `In review`. Archiving the OpenSpec change and moving the ticket to `Done`
   are done when the release is closed, in one `chore/close-X.Y.Z-release`
   pull request for everything that shipped (as in #5), not per ticket.

## Pull request size

A reviewer can only judge what fits in their head. Size is measured in
**code lines**: added plus deleted lines under `src/`, `tests/` and
`scripts/`, excluding lock files. Docs, OpenSpec artifacts, the CHANGELOG and
the ticket entry do not count, but they are read too, so keep them
proportionate.

```bash
git diff --numstat origin/main...HEAD -- src tests scripts ':!*.lock' \
  | awk '{a+=$1+$2; n++} END{print n" files, "a" lines"}'
```

| Size | Code lines | What it asks of the author |
|---|---|---|
| S | up to 150 | Nothing extra |
| M | 151 to 400 | The default target |
| L | 401 to 800 | Say in the description why it cannot be split; organize commits so each is reviewable on its own |
| XL | over 800 | Split it. Exceptions below |

Also:
- **Files:** more than 15 code files in one pull request is a signal to
  split, whatever the line count.
- **Tests do not buy extra room.** A fix whose tests are most of the diff is
  fine, but state the split (for example "40 source, 200 test").
- **Reviewable in one sitting:** aim for under about 60 minutes. If the
  description needs a guided tour, the pull request is too big.
- **How to split:** land refactors and renames first on their own branch;
  separate a behavior change from the cleanup around it; use one pull
  request per ticket.
- **Exceptions to XL** are mechanical changes with no behavior change: a
  license or header sweep, a rename or move, generated or vendored files,
  `release/` branches. Label the pull request as mechanical, keep it free of
  logic changes, and say how the reviewer can verify it (a command, a
  checksum, a diff filter).

The description states the measured size, and the template has a line for it.
For reference, the pull requests merged so far were: #6 (a bug fix with its
tests) about 700 code lines, and #3 (installation and distribution) about
16,000. The second is the case this section exists to avoid.
