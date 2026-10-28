## ADDED Requirements

### Requirement: Indexing keeps id_counters ahead of indexed codes
When the atomic indexer creates a rule or lesson row whose code matches
`<PREFIX>-<SEGMENT>-<digits>`, the system SHALL raise the `id_counters` entry
`<PREFIX>-<SEGMENT>` to at least `<digits> + 1` in the same transaction as the
insert, and SHALL NOT lower an already higher counter.

#### Scenario: Rule indexed with a manual code, then approval
- **WHEN** a file containing `RN-GLOBAL-001` is indexed and a rule proposal
  for scope `global` is then approved in the same process
- **THEN** the approval is assigned `RN-GLOBAL-002` and does not fail

#### Scenario: High manual code does not break later approvals
- **WHEN** a file containing `RN-GLOBAL-007` is indexed and eight rule
  proposals are approved in the same process
- **THEN** all eight are approved with codes `RN-GLOBAL-008` to `RN-GLOBAL-015`
  and none fails with a UNIQUE constraint error

#### Scenario: Lesson indexed with a manual code, then approval
- **WHEN** a file containing `LL-GLOBAL-001` is indexed and a lesson proposal
  for scope `global` is then approved in the same process
- **THEN** the approval is assigned `LL-GLOBAL-002` and does not fail

#### Scenario: Counter already ahead
- **WHEN** `RN-GLOBAL` has `next = 50` and a block `RN-GLOBAL-007` is indexed
- **THEN** the counter stays at 50

#### Scenario: Non-conforming code
- **WHEN** a block with a code not shaped `<PREFIX>-<SEGMENT>-<digits>` is
  indexed
- **THEN** indexing succeeds and no counter is changed

#### Scenario: Re-indexing an unchanged or updated block
- **WHEN** an already indexed block is indexed again
- **THEN** no counter changes
