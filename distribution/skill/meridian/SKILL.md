---
name: meridian
license: Apache-2.0
description: Use Axiom Meridian's MCP tools to apply a team's coding rules (RN-*) and lessons learned (LL-*) while working — fetch only the rules relevant to the current project before writing or reviewing code, audit a PR diff or a planned feature against them, and turn new insights into reviewable proposals. Use when the user mentions coding standards, team rules, lessons learned, Meridian, RN-/LL- identifiers, or asks to review a diff or plan a feature against project conventions.
---

# Meridian

Axiom Meridian is an MCP server that stores a team's institutional knowledge —
technical **rules** (`RN-*`) and **lessons learned** (`LL-*`) — in Markdown
files and serves only the slice relevant to a project. Rules are organized in
a scope hierarchy (for example `project-x → global-quarkus → global-java →
global`); every query resolves the full chain, most specific first.

## Detecting the tools

Meridian's tools may appear under different prefixes depending on how the
server was installed — for example `mcp__meridian__query_rules` when
registered directly, or a plugin-namespaced name inside the Claude Code
plugin. Match tools by their **base name** (the part after the last `__`):
`query_rules`, `audit_pr`, and so on.

If no tool whose name ends in `query_rules` is available, Meridian is not
connected. Do not try to install or start it yourself — tell the user and
show them the install commands under [If Meridian isn't installed](#if-meridian-isnt-installed).

## Which tool to use

| Situation | Tool |
|---|---|
| Starting work on a project; need its conventions | `query_rules` (and `query_lessons` for past incidents) |
| Searching by meaning ("how do we handle retries?") | `query_rules` / `query_lessons` with `query_text` |
| Reviewing a diff or PR before merge | `audit_pr` |
| Planning a feature or design before coding | `check_feature_against_rules` |
| Need the full story behind one rule | `get_rule_context` (lighter: `get_rule_timeline`) |
| Unsure which scopes apply to a project | `get_project_scope_resolution` |
| A discussion or transcript produced new rules or lessons | `extract_rules_from_transcript` / `extract_lessons_from_transcript`, then `create_pending_proposal` |
| A rule should change, or no longer applies | `create_pending_proposal` with `type="update"`, or `deprecate_rule` |
| PR review comments came back | `analyze_pr_feedback` |

Project ids are normalized: `my-service` and `project-my-service` refer to the
same project.

### Reading rules

- Call `query_rules(project_id=...)` once at the start of a task and keep the
  result in mind; don't re-query for every file.
- Use `detail="summary"` (default) to scan, `detail="full"` when you need the
  exact rule text to apply or quote.
- Filter with `category`, `severity`, or `tags` when you know what you need.
  Tag matching is exact (`go` does not match `golang`).
- `query_text` ranks results by meaning when the server has semantic search
  installed; otherwise the same call quietly falls back to plain filtering.
- Cite rules by id (`RN-JAVA-003`) when they drive a decision, so the user can
  check them.

### Auditing

- `audit_pr(pr_diff=..., project_id=...)` returns the applicable rules and
  lessons in full plus an audit record. Evaluate the diff against them and
  report concrete findings with the rule id, file, and line — the tool gives
  you context; the judgment is yours.
- `check_feature_against_rules(feature_description=..., project_id=...)` does
  the same for a plan before any code exists.

### Proposing knowledge

Meridian never lets an agent write rules directly. New or changed knowledge
becomes a **pending proposal** that a human approves.

1. Get the fields with `get_rule_template` / `get_lesson_template`
   (or `get_transcription_template` for a whole transcript).
2. Draft the rule or lesson and submit it with `create_pending_proposal`:
   the body (rule text, or what happened) as `proposed_text`, the other
   fields as `metadata`.
3. Tell the user it is pending and how to review it (`list_pending_proposals`).

Approving (`approve_proposal`), editing, rejecting, and promoting proposals
are write-level actions meant for the human reviewer. Only run them when the
user explicitly asks. If a tool answers with `ACCESS_DENIED`, the server's
access level is too low for that action — report it; the user can raise it by
setting `MERIDIAN_ACCESS_LEVEL=write` in the server's configuration.

## If Meridian isn't installed

Show the user these commands; never run them on their behalf:

```text
uv tool install axiom-meridian
meridian setup
```

`meridian setup` detects their MCP clients and configures each one after
asking. Without a persistent install, a client can launch the server with:

```text
uvx --from axiom-meridian meridian mcp
```

These need uv — point the user to
https://docs.astral.sh/uv/getting-started/installation/ if they don't have
it. Optional semantic search is the `axiom-meridian[rag]` variant.

## References

- `references/tools.md` — every tool with its parameters and access level.
- `references/workflows.md` — worked examples: starting a task, PR review,
  feature planning, capturing a lesson.
