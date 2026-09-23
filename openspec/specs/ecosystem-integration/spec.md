# Ecosystem Integration Specification

## Purpose
Let agent-facing clients auto-load a project's effective rules without the agent having to query Meridian manually every session.

## Requirements

### Requirement: Generate an agent-loadable skill
The system SHALL generate a `.claude/skills/` file containing a project's effective rules via `generate_project_skills`, writing `SKILL.md` and `references/rules.md` under the target project path following the `agentskills.io` convention.

#### Scenario: Generate a project skill
- **WHEN** a developer calls `generate_project_skills` for a project
- **THEN** `SKILL.md` and `references/rules.md` are written under the target project path
- **AND** the output follows the `agentskills.io` convention
