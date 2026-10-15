# Knowledge Lifecycle Governance Specification

## Purpose
Govern how rules and lessons enter and change in the knowledge base — indexing existing atomic-format files, migrating legacy narrative documents, and reviewing/approving proposals — so nothing becomes enforceable knowledge without a curator's sign-off.
## Requirements
### Requirement: Index atomic-format Markdown files
The system SHALL parse atomic-format Markdown files and create or update the corresponding rule/lesson rows via `index_rules_from_markdown` / `index_lessons_from_markdown`, reporting `{indexed, created, updated, errors, warnings}`, without silently dropping malformed blocks.

#### Scenario: Index a well-formed file
- **WHEN** a curator calls `index_rules_from_markdown` on a valid atomic-format file
- **THEN** every block is parsed and a summary of `{indexed, created, updated, errors, warnings}` is returned

#### Scenario: Index a file with malformed blocks
- **WHEN** a file contains a malformed block
- **THEN** the malformed block is reported as a warning or error and is not silently dropped

### Requirement: Legacy migration into pending proposals
The system SHALL convert a narrative legacy knowledge file into `pending_proposals` via `convert_to_atomic_format`, never writing directly to `rules` or `lessons`, preserve the original text in `legacy_original`, discard non-rule narrative sections, and use word-boundary scope inference to avoid false-positive scope assignment.

#### Scenario: Convert a legacy file
- **WHEN** a curator calls `convert_to_atomic_format` on a legacy Markdown file
- **THEN** candidate proposals are created with `source_type="legacy"` and the original text is preserved in `legacy_original`
- **AND** no row is written directly to `rules` or `lessons`

#### Scenario: Non-rule sections are discarded
- **WHEN** the legacy file contains non-rule narrative sections (e.g. "Skill Suggestions")
- **THEN** those sections are discarded rather than mis-parsed as rules

#### Scenario: Scope inference avoids false positives
- **WHEN** scope inference evaluates a term such as "go" against text containing "golang" or "algorithm"
- **THEN** the term does not match inside the longer word (word-boundary matching)

### Requirement: Proposal review and approval lifecycle
The system SHALL let a curator list, edit, approve, or reject pending proposals. `approve_proposal` SHALL atomically allocate a canonical code, write the block to the correct file, insert or update the database row, and record history — or the whole operation SHALL fail together. When the destination file of a `rule` or `lesson` proposal does not exist and the proposal's scope exists, `approve_proposal` SHALL create the file (and its parent directory) and write the block as the file's first block. `approve_proposal` SHALL refuse to approve a proposal whose body contains an atomic block header line (`## RN-…` / `## LL-…`), without writing anything, and SHALL point the curator to `edit_proposal`.

#### Scenario: List and edit a pending proposal
- **WHEN** a curator calls `list_pending_proposals` filtered by project, type, or status
- **THEN** matching pending proposals are returned
- **AND** `edit_proposal` updates the proposal's text or metadata while keeping its status `pending`

#### Scenario: Approve a proposal
- **WHEN** a curator calls `approve_proposal` on a pending proposal
- **THEN** a canonical code is allocated, the block is written to the correct Markdown file, the database row is inserted or updated, and history is recorded
- **AND** if any step fails, none of the changes are applied

#### Scenario: Approve the first rule of a scope with no file
- **WHEN** a curator approves a `rule` proposal for an existing scope whose rules `.md` file does not exist yet
- **THEN** the file is created containing only the new block, at offset 0
- **AND** the row is inserted with that file path, and `indexed_files` records the file

#### Scenario: Approve the first lesson of a project with no lessons file
- **WHEN** a curator approves a `lesson` proposal for a project scope that has a rules file but no lessons `.md` file
- **THEN** the lessons file is created with the new block and the lesson row is inserted

#### Scenario: Approval refuses a body with a nested block header
- **WHEN** a curator approves a pending proposal whose `proposed_text` contains a line starting with `## RN-` or `## LL-`
- **THEN** the approval fails with an error that names the proposal and suggests `edit_proposal`
- **AND** no file, row, history entry or proposal status is changed

#### Scenario: Reject a proposal
- **WHEN** a curator calls `reject_proposal` with an optional reason
- **THEN** the reason is recorded and no trace is left in active knowledge

### Requirement: In-place update proposals
The system SHALL support an `update` proposal type that revises an existing rule or lesson block in place via byte-level slice replacement, without disturbing existing non-update proposal flows. Every block field that the proposal's `metadata` omits SHALL be inherited from the target's current block in the Markdown file (falling back to the target's row), so that the rewritten block and the database row hold the same values; an explicit value in `metadata`, including an empty tag list, SHALL replace the inherited one.

#### Scenario: Create and approve an update proposal
- **WHEN** a curator calls `create_pending_proposal` with `type="update"` and a `target_id`
- **THEN** the system validates the target exists and infers rule vs. lesson from the ID prefix
- **AND** approving it replaces the block in the source file, updates the row via `UPDATE`, and records `change_type="UPDATED"` in history

#### Scenario: Text-only update keeps the target's other fields
- **WHEN** a curator approves an `update` proposal with a new body and no `metadata` for a rule whose block has `**Categoría:** security`, `**Severidad:** high`, `**Tags:** auth, jwt` and `**Fuente:** PR #12`
- **THEN** the rewritten block keeps `security`, `high`, `auth, jwt` and `PR #12`, with only the `**Regla:**` body changed
- **AND** the row's category, severity and tags and the rule's `rule_tags` rows match the block

#### Scenario: Update with explicit metadata changes only those fields
- **WHEN** a curator approves an `update` proposal whose `metadata` is `{"severity": "critical"}`
- **THEN** the rewritten block and the row have severity `critical` and every other field inherited from the current block

### Requirement: Proposal creation separates the body from the block fields
`create_pending_proposal` SHALL accept an optional `metadata` JSON object holding every atomic-block field other than the body, and SHALL store `proposed_text` as the body only. Allowed `metadata` keys SHALL be `category`, `severity`, `applies_to`, `tags`, `source` for rules and `project`, `date_occurred`, `severity`, `area_affected`, `tags`, `impact`, `root_cause`, `resolution`, `originated_rule_id` for lessons (`update` proposals use the keys of the target's type). Unknown keys and a `severity` outside `low`/`medium`/`high`/`critical` SHALL be rejected. Private tags SHALL be stripped from `metadata` values as well as from the body.

#### Scenario: Create a rule proposal with metadata
- **WHEN** a client calls `create_pending_proposal` with `type="rule"`, a body in `proposed_text`, and `metadata` `{"category": "documentation", "severity": "medium", "applies_to": "README.md", "tags": ["readme"], "source": "manual"}`
- **THEN** the proposal stores the body as `proposed_text` and those fields as `metadata`
- **AND** approving it writes a block whose `**Categoría:**`, `**Severidad:**`, `**Aplica a:**`, `**Tags:**` and `**Fuente:**` lines hold those values and whose `**Regla:**` holds only the body

#### Scenario: Unknown metadata key is rejected
- **WHEN** a client calls `create_pending_proposal` with `type="rule"` and `metadata` containing a key outside the allowed rule keys (e.g. `categoria`)
- **THEN** the call fails with an error that names the allowed keys
- **AND** no proposal is created

#### Scenario: Invalid severity is rejected
- **WHEN** a client calls `create_pending_proposal` with `metadata` `{"severity": "urgent"}`
- **THEN** the call fails and no proposal is created

### Requirement: A rendered atomic block sent as a proposal is normalized
When the `proposed_text` given to `create_pending_proposal` starts with an atomic block header line (`## RN-…` or `## LL-…`), the system SHALL parse it with the same field labels the indexer uses, store only the body field (`**Regla:**` / `**Qué pasó:**`) as `proposed_text`, and store the other parsed fields as `metadata`, with keys given explicitly in `metadata` taking precedence. The header's code SHALL be discarded (codes are allocated at approval). The call SHALL fail if the block's `**Scope:**` differs from `suggested_scope_id` (or from the target's scope for an `update`), or if the block has no non-empty body field.

#### Scenario: Rendered rule block is split into body and metadata
- **WHEN** a client calls `create_pending_proposal` with `type="rule"`, `suggested_scope_id="project-x"`, and a `proposed_text` that is a full rendered block with header `## RN-XXX-NNN`, `**Scope:** project-x`, `**Categoría:** security`, `**Severidad:** high`, `**Tags:** auth, jwt` and `**Regla:** Validate every token.`
- **THEN** the stored `proposed_text` is `Validate every token.`
- **AND** the stored `metadata` holds `category="security"`, `severity="high"` and tags `auth`, `jwt`
- **AND** approving it produces a single block with no nested header

#### Scenario: Explicit metadata overrides parsed fields
- **WHEN** a client sends a rendered block with `**Severidad:** low` together with `metadata` `{"severity": "high"}`
- **THEN** the stored `metadata` has `severity="high"`

#### Scenario: Scope in the block contradicts the requested scope
- **WHEN** a client sends a rendered block with `**Scope:** global-java` and `suggested_scope_id="project-x"`
- **THEN** the call fails with an error naming both scopes and no proposal is created

#### Scenario: Rendered block without a body
- **WHEN** a client sends a rendered rule block with no `**Regla:**` line or an empty one
- **THEN** the call fails and no proposal is created

### Requirement: Proposal guidance matches the proposal contract
The `usage` returned by `get_rule_template` and `get_lesson_template`, the workflow returned by `get_transcription_template`, the `create_pending_proposal` tool description, and the distributed skill references SHALL describe the template as the Markdown file format and SHALL instruct clients to send the body as `proposed_text` and the remaining fields as `metadata`.

#### Scenario: Template usage describes the proposal contract
- **WHEN** a client calls `get_rule_template` or `get_lesson_template`
- **THEN** the returned `usage` tells it to pass the body as `proposed_text` and the other fields as `metadata` when calling `create_pending_proposal`
- **AND** it no longer tells it to pass the rendered markdown as `proposed_text`

