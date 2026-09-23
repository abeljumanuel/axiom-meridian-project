# User Stories

Format: `As a <role>, I want <goal>, so that <benefit>.` Each story names the role, goal, benefit, primary MCP tool(s), and MoSCoW priority (`Must` / `Should` / `Could`).

Formal, testable acceptance criteria (WHEN/THEN scenarios) live in [OpenSpec](../openspec/) — one capability spec per epic below — instead of being restated here. This file stays the narrative source: who wants what, and why. See [`openspec/specs/`](../openspec/specs/) for delivered epics and [`openspec/changes/`](../openspec/changes/) for epics still in progress.

## Epic A — Scoped Knowledge Consumption
Formal spec: [`openspec/specs/scoped-knowledge-consumption/`](../openspec/specs/scoped-knowledge-consumption/spec.md)

### US-A1 — Query relevant rules for my project
**As an** AI coding agent, **I want** to query only the rules that apply to the project I'm working in, **so that** I don't burn context reading rules for frameworks I'm not using.

- **Tool:** `query_rules`
- **Priority:** Must

### US-A2 — Query lessons learned for my project
**As an** AI coding agent, **I want** to retrieve past incidents relevant to my project's scope, **so that** I can avoid repeating a mistake that was already made and resolved.

- **Tool:** `query_lessons`
- **Priority:** Must

### US-A3 — Get full context and history for one rule
**As an** AI coding agent, **I want** to fetch the full text, change history, and linked lessons for a specific rule, **so that** I can explain *why* a rule exists when asked, without loading everything up front.

- **Tools:** `get_rule_timeline`, `get_rule_context`
- **Priority:** Should

### US-A4 — See which scopes apply to my project
**As a** developer onboarding a new project into Meridian, **I want** to see the effective scope chain and attributes for my project, **so that** I understand which knowledge sources feed into it before I query anything.

- **Tool:** `get_project_scope_resolution`
- **Priority:** Should

## Epic B — Governed Knowledge Lifecycle
Formal spec: [`openspec/specs/knowledge-lifecycle-governance/`](../openspec/specs/knowledge-lifecycle-governance/spec.md)

### US-B1 — Index a new knowledge file
**As a** knowledge curator, **I want** to index an existing atomic-format Markdown file into Meridian, **so that** its rules/lessons become queryable without hand-transcribing them into a database.

- **Tools:** `index_rules_from_markdown`, `index_lessons_from_markdown`
- **Priority:** Must

### US-B2 — Migrate a legacy free-form file safely
**As a** knowledge curator, **I want** to convert an old narrative `Global_Rules.md` into candidate proposals, **so that** I can adopt Meridian without losing or silently mis-indexing existing knowledge.

- **Tool:** `convert_to_atomic_format`
- **Priority:** Must

### US-B3 — Review and approve a proposal
**As a** knowledge curator, **I want** to review a pending proposal, optionally edit it, and approve or reject it, **so that** nothing becomes an enforceable rule without my sign-off.

- **Tools:** `list_pending_proposals`, `edit_proposal`, `approve_proposal`, `reject_proposal`
- **Priority:** Must

### US-B4 — Promote a rule to a broader scope
**As a** knowledge curator, **I want** to move a project-specific rule up to a framework- or language-wide scope, **so that** knowledge proven useful in one project benefits every project on that stack.

- **Tool:** `promote_rule`
- **Priority:** Should

## Epic C — Auditing Before Merge and Before Build
Formal spec: [`openspec/specs/pr-and-planning-audits/`](../openspec/specs/pr-and-planning-audits/spec.md)

### US-C1 — Audit a pull request against known rules
**As a** developer, **I want** to check a PR diff against the rules relevant to my project before requesting review, **so that** I catch known violations before a human reviewer has to.

- **Tool:** `audit_pr`
- **Priority:** Must

### US-C2 — Reconcile reviewer feedback with a prior audit
**As a** developer, **I want** to feed human review feedback back into Meridian, **so that** discrepancies between what the tool flagged and what a human flagged can inform future rule refinement.

- **Tool:** `analyze_pr_feedback`
- **Priority:** Could

### US-C3 — Check a feature idea against existing rules before writing code
**As a** developer in the planning stage, **I want** to check a feature description against relevant rules and lessons, **so that** I avoid designing something that a known constraint will later block.

- **Tool:** `check_feature_against_rules`
- **Priority:** Should

## Epic D — Extraction From Meetings
Formal spec: [`openspec/specs/transcript-extraction/`](../openspec/specs/transcript-extraction/spec.md)

### US-D1 — Turn a meeting transcript into candidate rules
**As a** knowledge curator, **I want** to run a raw meeting transcript through Meridian, **so that** decisions made verbally become candidate rules instead of being forgotten.

- **Tools:** `extract_rules_from_transcript`, `create_pending_proposal`
- **Priority:** Should

### US-D2 — Turn a postmortem transcript into candidate lessons
**As a** knowledge curator, **I want** the same extraction flow for incident postmortems, **so that** the lesson gets captured with the same governance as a rule.

- **Tool:** `extract_lessons_from_transcript`
- **Priority:** Should

## Epic E — Security and Access Control
Formal spec: [`openspec/specs/security-access-control/`](../openspec/specs/security-access-control/spec.md)

### US-E1 — Restrict an agent session to read-only access
**As a** platform admin, **I want** to configure an agent's MCP session with `MERIDIAN_ACCESS_LEVEL=read`, **so that** an untrusted or exploratory session cannot modify the knowledge base.

- **Tool:** cross-cutting (`utils/security.py`)
- **Priority:** Must

### US-E2 — Audit what an agent did
**As a** platform admin, **I want** to review a chronological log of every tool call, its access level, and its outcome, **so that** I can investigate unexpected knowledge-base changes.

- **Tool:** `get_rule_audit_log`
- **Priority:** Must

### US-E3 — Run Meridian over HTTP without exposing it to the network
**As a** platform admin, **I want** the HTTP/SSE transport to require a bearer token and bind only to localhost, **so that** enabling network transport doesn't create a remote knowledge-base takeover vector.

- **Priority:** Must

## Epic F — Semantic Search (RAG)
Formal spec: [`openspec/specs/semantic-search/`](../openspec/specs/semantic-search/spec.md) (baseline) · [`openspec/changes/upgrade-semantic-search-v2/`](../openspec/changes/upgrade-semantic-search-v2/) (in progress)

### US-F1 — Find relevant rules by meaning, not just exact tags
**As an** AI coding agent, **I want** to pass free-text `query_text` and get semantically ranked results, **so that** I find relevant rules even when my wording doesn't match the rule's tags exactly.

- **Tool:** `query_rules` / `query_lessons` (hybrid mode), `generate_embeddings`
- **Priority:** Should

## Epic G — Ecosystem Integration
Formal spec: [`openspec/specs/ecosystem-integration/`](../openspec/specs/ecosystem-integration/spec.md)

### US-G1 — Generate an agent-loadable skill for my project
**As a** developer using Claude Code (or another skill-aware client), **I want** Meridian to generate a `.claude/skills/` file with my project's effective rules, **so that** the rules are auto-loaded without me having to query Meridian manually every session.

- **Tool:** `generate_project_skills`
- **Priority:** Could

## Epic H — Observability Dashboard (Optional Companion)
Formal spec: [`openspec/changes/add-observability-dashboard/`](../openspec/changes/add-observability-dashboard/) (not yet part of the baseline — see note below)

### US-H1 — Inspect Meridian's status and contents visually
**As a** knowledge curator or platform admin, **I want** a read-only web dashboard showing server health, indexed scopes, active/deprecated rules and lessons, pending proposals, a rendered usage manual, and an embedding projector, **so that** I don't have to run ad-hoc Python snippets or read raw Markdown/SQLite to understand the current state of the knowledge base.

- **Priority:** Could
- **Note:** explicitly a nice-to-have companion, not part of the core MCP/knowledge-governance value proposition — see [TICKET-017](06-work-tickets.md#ticket-017--read-only-observability-dashboard).

## Related Documents

- [Project Charter](01-project-charter.md)
- [Product Description](02-product-description.md)
- [System Architecture](03-system-architecture.md)
- [Data Model](04-data-model.md)
- [Work Tickets](06-work-tickets.md)
- [OpenSpec specs and changes](../openspec/)
