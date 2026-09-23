# User Stories

Format: `As a <role>, I want <goal>, so that <benefit>.` Each story lists acceptance criteria and the primary MCP tool(s) it maps to. Priority uses MoSCoW (`Must` / `Should` / `Could`).

## Epic A — Scoped Knowledge Consumption

### US-A1 — Query relevant rules for my project
**As an** AI coding agent, **I want** to query only the rules that apply to the project I'm working in, **so that** I don't burn context reading rules for frameworks I'm not using.

- **Acceptance criteria:**
  - Given a `project_id`, the response includes rules from the project's resolved scope chain only (its own scope + ancestors), most specific first.
  - Results can be filtered by `category`, `severity`, and `tags` (exact match).
  - Deprecated rules are excluded by default.
- **Tool:** `query_rules`
- **Priority:** Must

### US-A2 — Query lessons learned for my project
**As an** AI coding agent, **I want** to retrieve past incidents relevant to my project's scope, **so that** I can avoid repeating a mistake that was already made and resolved.

- **Acceptance criteria:** same filtering semantics as US-A1, scoped by `area` instead of `category`.
- **Tool:** `query_lessons`
- **Priority:** Must

### US-A3 — Get full context and history for one rule
**As an** AI coding agent, **I want** to fetch the full text, change history, and linked lessons for a specific rule, **so that** I can explain *why* a rule exists when asked, without loading everything up front.

- **Acceptance criteria:**
  - `get_rule_timeline` returns chronological history without loading full text (cheap call).
  - `get_rule_context` returns full text + complete history + linked lessons (expensive call, used only when justified).
- **Tools:** `get_rule_timeline`, `get_rule_context`
- **Priority:** Should

### US-A4 — See which scopes apply to my project
**As a** developer onboarding a new project into Meridian, **I want** to see the effective scope chain and attributes for my project, **so that** I understand which knowledge sources feed into it before I query anything.

- **Acceptance criteria:** `get_project_scope_resolution` returns the ordered scope chain with each scope's attributes.
- **Tool:** `get_project_scope_resolution`
- **Priority:** Should

## Epic B — Governed Knowledge Lifecycle

### US-B1 — Index a new knowledge file
**As a** knowledge curator, **I want** to index an existing atomic-format Markdown file into Meridian, **so that** its rules/lessons become queryable without hand-transcribing them into a database.

- **Acceptance criteria:**
  - `index_rules_from_markdown` / `index_lessons_from_markdown` parse every block, create or update the corresponding row, and report `{indexed, created, updated, errors, warnings}`.
  - Malformed blocks are reported as warnings/errors, not silently dropped.
- **Tools:** `index_rules_from_markdown`, `index_lessons_from_markdown`
- **Priority:** Must

### US-B2 — Migrate a legacy free-form file safely
**As a** knowledge curator, **I want** to convert an old narrative `Global_Rules.md` into candidate proposals, **so that** I can adopt Meridian without losing or silently mis-indexing existing knowledge.

- **Acceptance criteria:**
  - `convert_to_atomic_format` never writes directly to `rules`/`lessons`; it creates `pending_proposals` with `source_type="legacy"`.
  - The original text is preserved in `legacy_original` for audit.
  - Non-rule sections (e.g. "Skill Suggestions") are discarded, not mis-parsed as rules.
- **Tool:** `convert_to_atomic_format`
- **Priority:** Must

### US-B3 — Review and approve a proposal
**As a** knowledge curator, **I want** to review a pending proposal, optionally edit it, and approve or reject it, **so that** nothing becomes an enforceable rule without my sign-off.

- **Acceptance criteria:**
  - `list_pending_proposals` supports filtering by project, type, and status.
  - `edit_proposal` updates text/metadata while keeping status `pending`.
  - `approve_proposal` atomically: allocates a canonical code, writes the block to the correct `.md` file, inserts/updates the DB row, and records history — or the whole operation fails together.
  - `reject_proposal` records an optional reason and leaves no trace in active knowledge.
- **Tools:** `list_pending_proposals`, `edit_proposal`, `approve_proposal`, `reject_proposal`
- **Priority:** Must

### US-B4 — Promote a rule to a broader scope
**As a** knowledge curator, **I want** to move a project-specific rule up to a framework- or language-wide scope, **so that** knowledge proven useful in one project benefits every project on that stack.

- **Acceptance criteria:** `promote_rule` updates `scope_id` and registers a `PROMOTED` entry in `rule_history`.
- **Tool:** `promote_rule`
- **Priority:** Should

## Epic C — Auditing Before Merge and Before Build

### US-C1 — Audit a pull request against known rules
**As a** developer, **I want** to check a PR diff against the rules relevant to my project before requesting review, **so that** I catch known violations before a human reviewer has to.

- **Acceptance criteria:** `audit_pr` evaluates the diff against the project's resolved rules, persists a `pr_audits` record (rules evaluated, violations found), and returns actionable output.
- **Tool:** `audit_pr`
- **Priority:** Must

### US-C2 — Reconcile reviewer feedback with a prior audit
**As a** developer, **I want** to feed human review feedback back into Meridian, **so that** discrepancies between what the tool flagged and what a human flagged can inform future rule refinement.

- **Acceptance criteria:** `analyze_pr_feedback` links feedback text to the prior audit via `pr_ref` and surfaces gaps.
- **Tool:** `analyze_pr_feedback`
- **Priority:** Could

### US-C3 — Check a feature idea against existing rules before writing code
**As a** developer in the planning stage, **I want** to check a feature description against relevant rules and lessons, **so that** I avoid designing something that a known constraint will later block.

- **Acceptance criteria:** `check_feature_against_rules` persists a `planning_checks` record and returns conflicts plus the rules involved.
- **Tool:** `check_feature_against_rules`
- **Priority:** Should

## Epic D — Extraction From Meetings

### US-D1 — Turn a meeting transcript into candidate rules
**As a** knowledge curator, **I want** to run a raw meeting transcript through Meridian, **so that** decisions made verbally become candidate rules instead of being forgotten.

- **Acceptance criteria:** `extract_rules_from_transcript` returns candidate rule text and suggested scope/attributes without persisting anything until `create_pending_proposal` is called.
- **Tool:** `extract_rules_from_transcript`, `create_pending_proposal`
- **Priority:** Should

### US-D2 — Turn a postmortem transcript into candidate lessons
**As a** knowledge curator, **I want** the same extraction flow for incident postmortems, **so that** the lesson gets captured with the same governance as a rule.

- **Acceptance criteria:** `extract_lessons_from_transcript` mirrors US-D1 for lessons.
- **Tool:** `extract_lessons_from_transcript`
- **Priority:** Should

## Epic E — Security and Access Control

### US-E1 — Restrict an agent session to read-only access
**As a** platform admin, **I want** to configure an agent's MCP session with `MERIDIAN_ACCESS_LEVEL=read`, **so that** an untrusted or exploratory session cannot modify the knowledge base.

- **Acceptance criteria:** any tool above `read` level returns a structured `ACCESS_DENIED` response naming the required level; no side effect occurs.
- **Tool:** cross-cutting (`utils/security.py`)
- **Priority:** Must

### US-E2 — Audit what an agent did
**As a** platform admin, **I want** to review a chronological log of every tool call, its access level, and its outcome, **so that** I can investigate unexpected knowledge-base changes.

- **Acceptance criteria:** `get_rule_audit_log` filters by project/scope/date; sensitive parameter values (diff text, feedback text, proposed text) are never present in the log.
- **Tool:** `get_rule_audit_log`
- **Priority:** Must

### US-E3 — Run Meridian over HTTP without exposing it to the network
**As a** platform admin, **I want** the HTTP/SSE transport to require a bearer token and bind only to localhost, **so that** enabling network transport doesn't create a remote knowledge-base takeover vector.

- **Acceptance criteria:** server binds to `127.0.0.1`; every request without a valid, current-session `Authorization: Bearer <token>` header receives `401`.
- **Priority:** Must

## Epic F — Semantic Search (RAG)

### US-F1 — Find relevant rules by meaning, not just exact tags
**As an** AI coding agent, **I want** to pass free-text `query_text` and get semantically ranked results, **so that** I find relevant rules even when my wording doesn't match the rule's tags exactly.

- **Acceptance criteria:** when embeddings exist for the relevant scopes, `query_rules`/`query_lessons` rank by similarity; when they don't, the same call falls back to SQL filtering with no error and no signature change.
- **Tool:** `query_rules` / `query_lessons` (hybrid mode), `generate_embeddings`
- **Priority:** Should

## Epic G — Ecosystem Integration

### US-G1 — Generate an agent-loadable skill for my project
**As a** developer using Claude Code (or another skill-aware client), **I want** Meridian to generate a `.claude/skills/` file with my project's effective rules, **so that** the rules are auto-loaded without me having to query Meridian manually every session.

- **Acceptance criteria:** `generate_project_skills` writes `SKILL.md` and `references/rules.md` under the target project path, following the `agentskills.io` convention.
- **Tool:** `generate_project_skills`
- **Priority:** Could

## Epic H — Observability Dashboard (Optional Companion)

### US-H1 — Inspect Meridian's status and contents visually
**As a** knowledge curator or platform admin, **I want** a read-only web dashboard showing server health, indexed scopes, active/deprecated rules and lessons, pending proposals, and a rendered usage manual, **so that** I don't have to run ad-hoc Python snippets or read raw Markdown/SQLite to understand the current state of the knowledge base.

- **Acceptance criteria:**
  - Dashboard is read-only — it calls the existing consumption functions (`query_rules`, `query_lessons`, `get_project_scope_resolution`, `get_rule_audit_log`, `list_pending_proposals`) directly; it never writes to `rules`/`lessons`/`pending_proposals`.
  - Shows: server/process health, the scope hierarchy tree, counts and lists of active/deprecated rules and lessons per scope, pending proposals awaiting review, a rendered version of the project's usage manual (README/PRD), and an embedding projector — a 2D/3D scatter plot of existing rule/lesson embeddings (read from ChromaDB, never generated by the dashboard) colored by scope/category/severity, for visually inspecting how knowledge clusters.
  - Runs as a separate local process from the MCP server itself — it does not speak the MCP protocol; it reuses the same Python functions as a library.
  - Bound to `127.0.0.1` by default, consistent with the existing HTTP/SSE transport's security posture (no MCP session token required, since it never calls a gated tool at `write` level).
- **Priority:** Could
- **Note:** explicitly a nice-to-have companion, not part of the core MCP/knowledge-governance value proposition — see [TICKET-017](06-work-tickets.md#ticket-017--read-only-observability-dashboard).

## Related Documents

- [Project Charter](01-project-charter.md)
- [Product Description](02-product-description.md)
- [System Architecture](03-system-architecture.md)
- [Data Model](04-data-model.md)
- [Work Tickets](06-work-tickets.md)
