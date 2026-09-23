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
The system SHALL let a curator list, edit, approve, or reject pending proposals. `approve_proposal` SHALL atomically allocate a canonical code, write the block to the correct file, insert or update the database row, and record history — or the whole operation SHALL fail together.

#### Scenario: List and edit a pending proposal
- **WHEN** a curator calls `list_pending_proposals` filtered by project, type, or status
- **THEN** matching pending proposals are returned
- **AND** `edit_proposal` updates the proposal's text or metadata while keeping its status `pending`

#### Scenario: Approve a proposal
- **WHEN** a curator calls `approve_proposal` on a pending proposal
- **THEN** a canonical code is allocated, the block is written to the correct Markdown file, the database row is inserted or updated, and history is recorded
- **AND** if any step fails, none of the changes are applied

#### Scenario: Reject a proposal
- **WHEN** a curator calls `reject_proposal` with an optional reason
- **THEN** the reason is recorded and no trace is left in active knowledge

### Requirement: In-place update proposals
The system SHALL support an `update` proposal type that revises an existing rule or lesson block in place via byte-level slice replacement, without disturbing existing non-update proposal flows.

#### Scenario: Create and approve an update proposal
- **WHEN** a curator calls `create_pending_proposal` with `type="update"` and a `target_id`
- **THEN** the system validates the target exists and infers rule vs. lesson from the ID prefix
- **AND** approving it replaces the block in the source file, updates the row via `UPDATE`, and records `change_type="UPDATED"` in history
