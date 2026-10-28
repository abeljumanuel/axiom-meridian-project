<!-- Delete a section only if it truly does not apply, and say why in one line. -->

## Summary
<!-- What changes and why, in 2-4 lines. Lead with the problem and who it affects. -->

Ticket: TICKET-NNN
OpenSpec change: `change-name`

## Evidence
<!-- Fixes: how you reproduced it (commands, inputs, observed output) and the
     result after the fix. Features: the need or user story it answers. -->

## Scope
- **Size:** N files, N code lines (src + tests + scripts; command in CONTRIBUTING) <!-- S / M / L / XL; if L, why it cannot be split -->
- **Changes:**
- **Does not change:** <!-- explicit non-goals -->
- **Breaking:** none <!-- or describe, marked BREAKING -->

## Regression safety
- [ ] New tests fail on `main` and pass on this branch (name them):
- [ ] Full suite passes with and without the `rag` extra
- [ ] `uv run pytest -m benchmark` passes (required if ids, queries or indexing are touched)
- [ ] Invariants touched (see `CLAUDE.md`) and how each is preserved:
- [ ] Contract surfaces unchanged, or listed: MCP tool signatures, DB schema/migrations, atomic block labels, CLI commands
- [ ] Existing knowledge bases keep working (tried on a copy, never on the real KB)

## Verification
<!-- Exact commands and results, with counts. -->

## Risks and rollback
<!-- What could go wrong in a running server or an existing KB; how to undo. -->

## Not verified
<!-- What you could not test, and why. "Nothing" is a valid answer only if true. -->
