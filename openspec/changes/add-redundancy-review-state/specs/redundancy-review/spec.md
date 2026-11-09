## ADDED Requirements

### Requirement: Persisted review of a candidate pair
The system SHALL store, per unordered pair of rules, a curator decision of `dismissed` or `confirmed`, with an optional note, the actor and the time, and SHALL keep one row per pair.

#### Scenario: Record a decision
- **WHEN** a curator with `write` access records a decision for rules `RN-A` and `RN-B`
- **THEN** one row exists for the pair in canonical order
- **AND** recording it again as `(RN-B, RN-A)` updates that row instead of creating another

#### Scenario: Invalid input
- **WHEN** the rules do not exist, are the same rule, or the decision is not `dismissed` or `confirmed`
- **THEN** the system returns an error and writes nothing

### Requirement: Report honours reviews
`find_redundant_rules` SHALL omit `dismissed` pairs by default, SHALL mark `confirmed` pairs, and SHALL include dismissed pairs, marked, when `include_reviewed` is true.

#### Scenario: Dismissed pair hidden
- **WHEN** a pair was dismissed and the report is requested with default parameters
- **THEN** the pair is not in the report

### Requirement: No effect on knowledge content
Recording a review SHALL NOT modify any row of `rules` or `lessons` nor any `.md` file, and applying the migration SHALL leave every existing row of every other table unchanged.

#### Scenario: Migrating an existing database
- **WHEN** a database at `user_version = 7` is opened
- **THEN** the table is created, `user_version` becomes 8 and all existing rows are unchanged

### Requirement: Write access level
`review_redundancy_pair` SHALL require access level `write`.

#### Scenario: Read-only client
- **WHEN** a client at `read` or `analyze` level calls the tool
- **THEN** the call is denied and logged in `access_log`
