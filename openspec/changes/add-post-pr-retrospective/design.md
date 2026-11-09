## Context

`extract_rules_from_transcript` and `extract_lessons_from_transcript` return the cleaned text, the scope chain, the existing rules or lessons for duplicate detection and the block template. They do not analyse anything: the calling LLM does, and then calls `create_pending_proposal`. `audit_pr` works the same way. The retrospective is therefore a workflow around existing tools, not a new capability of the server.

## Goals / Non-Goals

**Goals:**
- Make the "what should we learn from this PR" question a routine step with a fixed input.
- Keep every decision with a person.

**Non-Goals:**
- Running automatically in CI. It needs an LLM, a secret and a cost, and CI cannot judge value.
- Approving, editing or deprecating existing rules.
- Scoring or ranking candidates beyond the cap.

## Decisions

### Decision 1: A skill, not a server tool
The analysis is done by the client LLM and the server already supplies the context. A new tool would add a contract (README section 4, contract test, `TOOL_ACCESS_LEVELS`) for no new capability.

### Decision 2: Works at `analyze` level
`create_pending_proposal` and the extraction tools are `analyze`; `approve_proposal` is `write`. An agent without `write` access cannot approve by construction, so the human gate does not depend on the agent obeying instructions.

### Decision 3: Evidence is mandatory, "none" is valid
Each candidate cites the PR evidence it comes from (a failed check, a review comment, a commit). A routine PR yields no candidates. A cap of five per PR bounds the noise.

### Decision 4: Provenance on every proposal
`source_type="manual"` and `source_ref` set to the PR link, so a reviewer can trace each proposal to its origin.

### Decision 5: Optional deterministic collector
`meridian retro collect --pr N` would print the evidence as text using `gh`. It makes the input reproducible and testable without an LLM. It is optional: the skill works with the agent running `gh` itself.

## Risks / Trade-offs

- LLM-invented lessons: mitigated by required evidence, the cap and the manual measurement on three PRs.
- Rule inflation and contradictions: mitigated by the duplicate comparison and the single human approver.
- Output varies between runs; the collector fixes the input but not the output.
- PR comments may carry sensitive text; extraction strips private tags, and the instructions exclude tokens and personal data.
- The skill and plugin copies must stay byte-identical (checked in CI).
