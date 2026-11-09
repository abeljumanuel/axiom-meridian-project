## Why

What a pull request teaches the team becomes a rule or lesson only if someone remembers to write it down (TICKET-028). `RN-AXIOM-008` exists because someone noticed after TICKET-021; the flaky Windows backup test and a wrong data-model claim were only turned into knowledge in a manual session. Meridian already has the machinery (transcript extraction, pending proposals, human approval) but nothing that runs it when a PR closes.

## What Changes

- Add a retrospective workflow to the distributable skill: gather the evidence of a closed PR, run the existing extraction tools and leave candidate rules and lessons as `pending_proposals`.
- The agent never approves; a person decides.
- No new server tool and no schema change. Optionally, a deterministic evidence collector command.

## Capabilities

### New Capabilities
- `post-pr-retrospective`: evidence-based candidate rules and lessons from a closed pull request, queued for human review.

## Impact

- Skill text in `distribution/skill/meridian/` and its identical plugin copy
- Documentation in README / installation guide and CONTRIBUTING
- Optional CLI command to collect PR evidence
- Depends on `transcript-extraction` and on the audit from TICKET-026
