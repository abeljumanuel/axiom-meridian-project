# Transcript Extraction Specification

## Purpose
Turn raw meeting and postmortem transcripts into candidate rules and lessons, without persisting anything until a curator explicitly creates a proposal.

## Requirements

### Requirement: Extract candidate rules from a meeting transcript
The system SHALL return candidate rule text and suggested scope/attributes from a raw transcript via `extract_rules_from_transcript`, without persisting anything until `create_pending_proposal` is called.

#### Scenario: Extract rules from a transcript
- **WHEN** a curator calls `extract_rules_from_transcript` with a raw meeting transcript
- **THEN** candidate rule text and suggested scope/attributes are returned
- **AND** nothing is persisted until `create_pending_proposal` is called separately

### Requirement: Extract candidate lessons from a postmortem transcript
The system SHALL mirror the rule-extraction flow for incident postmortems via `extract_lessons_from_transcript`, so a lesson receives the same governance as a rule.

#### Scenario: Extract lessons from a postmortem
- **WHEN** a curator calls `extract_lessons_from_transcript` with a postmortem transcript
- **THEN** candidate lesson text and suggested scope/attributes are returned
- **AND** the resulting candidate follows the same proposal governance as an extracted rule
