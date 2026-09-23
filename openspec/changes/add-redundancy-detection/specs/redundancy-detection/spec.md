## ADDED Requirements

### Requirement: Candidate duplicate report
The system SHALL cluster rules by embedding similarity and produce a report of candidate duplicate or overlapping rule pairs above a configurable similarity threshold, without performing any automatic write.

#### Scenario: Generate a redundancy report
- **WHEN** a curator requests a redundancy report for a scope
- **THEN** the system returns candidate duplicate/overlapping rule pairs whose similarity is above the configured threshold
- **AND** no rule or lesson row is modified as a result

#### Scenario: Scope without embeddings
- **WHEN** a redundancy report is requested for a scope that has no embeddings generated
- **THEN** the system returns an empty result rather than generating embeddings as a side effect
