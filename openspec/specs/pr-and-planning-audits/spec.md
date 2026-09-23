# PR and Planning Audits Specification

## Purpose
Let developers check work against known rules and lessons before it's built or merged — auditing a PR diff, reconciling human review feedback with a prior audit, and checking a feature idea before writing code.

## Requirements

### Requirement: Audit a pull request diff
The system SHALL evaluate a PR diff against a project's resolved rules via `audit_pr`, persist a `pr_audits` record of the rules evaluated and violations found, and return actionable output.

#### Scenario: Audit a PR
- **WHEN** a developer calls `audit_pr` with a diff and project context
- **THEN** the diff is evaluated against the project's resolved rules
- **AND** a `pr_audits` record is persisted with the rules evaluated and violations found

### Requirement: Reconcile reviewer feedback with a prior audit
The system SHALL link human review feedback text to a prior audit via `pr_ref` and surface gaps between what the tool flagged and what the human flagged, via `analyze_pr_feedback`.

#### Scenario: Analyze feedback against a prior audit
- **WHEN** a developer calls `analyze_pr_feedback` with feedback text and a `pr_ref`
- **THEN** the feedback is linked to the prior audit for that PR
- **AND** discrepancies between flagged and unflagged issues are surfaced

### Requirement: Check a feature idea against existing rules
The system SHALL evaluate a feature description against relevant rules and lessons via `check_feature_against_rules`, persist a `planning_checks` record, and return conflicts plus the rules involved.

#### Scenario: Check a feature idea before implementation
- **WHEN** a developer calls `check_feature_against_rules` with a feature description
- **THEN** a `planning_checks` record is persisted
- **AND** the response returns any conflicts plus the rules involved
