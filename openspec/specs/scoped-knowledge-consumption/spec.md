# Scoped Knowledge Consumption Specification

## Purpose
Let AI coding agents query only the rules and lessons relevant to their project's resolved scope, and inspect a rule's full context and history without loading the entire knowledge base up front.

## Requirements

### Requirement: Scoped rule querying
The system SHALL resolve a project's scope chain and return only rules from that chain via `query_rules`, ordered most specific first, with deprecated rules excluded by default.

#### Scenario: Query rules for a project
- **WHEN** an agent calls `query_rules` with a `project_id`
- **THEN** the response includes rules from the project's own scope and its ancestor scopes only, ordered most specific first
- **AND** deprecated rules are excluded unless explicitly requested

#### Scenario: Filter rules by category, severity, and tags
- **WHEN** `category`, `severity`, or `tags` filters are provided
- **THEN** only rules matching all provided filters (exact match) are returned

### Requirement: Scoped lesson querying
The system SHALL apply the same scope-resolution and filtering semantics as `query_rules` to `query_lessons`, scoped by `area` instead of `category`.

#### Scenario: Query lessons for a project
- **WHEN** an agent calls `query_lessons` with a `project_id`
- **THEN** the response includes lessons from the resolved scope chain, filterable by `area`, `severity`, and `tags`

### Requirement: Rule timeline and full context retrieval
The system SHALL provide a cheap chronological-history lookup (`get_rule_timeline`) separate from an expensive full-context lookup (`get_rule_context`), so agents only pay for the full text and linked lessons when justified.

#### Scenario: Request rule history only
- **WHEN** an agent calls `get_rule_timeline` for a rule ID
- **THEN** the response returns the chronological change history without loading the rule's full text

#### Scenario: Request full rule context
- **WHEN** an agent calls `get_rule_context` for a rule ID
- **THEN** the response returns the full text, complete change history, and linked lessons

### Requirement: Project scope resolution visibility
The system SHALL expose the effective, ordered scope chain and each scope's attributes for a given project via `get_project_scope_resolution`.

#### Scenario: Inspect a project's scope chain
- **WHEN** a developer calls `get_project_scope_resolution` for a project
- **THEN** the response returns the ordered scope chain with each scope's attributes
