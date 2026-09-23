# Axiom Meridian

> **Code drifts. Meridian doesn't.**

Axiom Meridian is a Model Context Protocol (MCP) server that centralizes institutional technical knowledge — coding rules and lessons learned — and delivers only the slice relevant to the current task, instead of forcing AI agents to read entire knowledge-base files on every session.

This repository is the capstone project for a Master's Degree in Artificial Intelligence and tracks the project's implementation as it evolves. Documentation is written in English to keep the project consistent with the AI-assisted tooling used throughout the build.

## Documentation

All baseline documentation lives in [`docs/`](docs/):

| Document | Contents |
|---|---|
| [01 · Project Charter](docs/01-project-charter.md) | Fact sheet, objectives, scope, and stakeholders. |
| [02 · Product Description](docs/02-product-description.md) | Problem statement, solution, core capabilities, target users. |
| [03 · System Architecture](docs/03-system-architecture.md) | Layered architecture, read/write flow diagrams, security model, tech stack, architecture decision log. |
| [04 · Data Model](docs/04-data-model.md) | Entity-relationship diagram, table reference, scope hierarchy, atomic knowledge block format. |
| [05 · User Stories](docs/05-user-stories.md) | Requirements by epic, in `As a / I want / so that` format with acceptance criteria. |
| [06 · Work Tickets](docs/06-work-tickets.md) | Delivered milestones and backlog, traced to user stories and architecture decisions. |

## Spec-driven change tracking

New work is tracked with [OpenSpec](https://github.com/Fission-AI/OpenSpec) instead of ad hoc ticket entries:

- [`openspec/specs/`](openspec/specs/) — the current baseline: one capability per delivered epic (scoped knowledge consumption, knowledge lifecycle governance, PR/planning audits, transcript extraction, security & access control, semantic search, ecosystem integration), derived from [User Stories](docs/05-user-stories.md) and the delivered tickets in [Work Tickets](docs/06-work-tickets.md).
- [`openspec/changes/`](openspec/changes/) — active change proposals, one per item still in the backlog (Windows installer, semantic search v2, redundancy detection, networked deployment hardening, Engram cross-referencing, observability dashboard). Each has a `proposal.md` (why), a delta `specs/` (what), a `design.md` (how), and a `tasks.md` (checklist).

Run `openspec list` / `openspec list --specs` to see current state, or `openspec show <name>` for one item. [Work Tickets](docs/06-work-tickets.md) remains as the historical record of what shipped before this switch; going forward, new work starts as an OpenSpec change rather than a new ticket.

## Status

Documentation-first baseline. Source code, tests, and configuration are added incrementally on top of this documentation as the implementation progresses — see [`openspec/changes/`](openspec/changes/) for what's next.

## License

MIT
