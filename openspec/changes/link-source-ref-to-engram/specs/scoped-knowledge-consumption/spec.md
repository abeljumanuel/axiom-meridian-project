## MODIFIED Requirements

### Requirement: Rule timeline and full context retrieval
The system SHALL provide a cheap chronological-history lookup (`get_rule_timeline`) separate from an expensive full-context lookup (`get_rule_context`), so agents only pay for the full text and linked lessons when justified. When Engram is present and a rule's or lesson's `source_ref` resolves to an Engram `observation_id`, `get_rule_context` MAY optionally surface the linked observation; Meridian SHALL function identically when Engram is absent.

#### Scenario: Request rule history only
- **WHEN** an agent calls `get_rule_timeline` for a rule ID
- **THEN** the response returns the chronological change history without loading the rule's full text

#### Scenario: Request full rule context
- **WHEN** an agent calls `get_rule_context` for a rule ID
- **THEN** the response returns the full text, complete change history, and linked lessons

#### Scenario: Full context with a linked Engram observation
- **WHEN** Engram is present and the rule's `source_ref` resolves to an Engram `observation_id`
- **THEN** `get_rule_context`'s response optionally includes the linked observation

#### Scenario: Full context with Engram absent
- **WHEN** Engram is not present
- **THEN** `get_rule_context` behaves identically to before, with no linked-observation field populated
