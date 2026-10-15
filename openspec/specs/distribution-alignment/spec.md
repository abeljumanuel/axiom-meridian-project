# distribution-alignment Specification

## Purpose
TBD - created by archiving change change-license-to-apache-2. Update Purpose after archive.
## Requirements
### Requirement: Meridian-distributed artifacts declare Apache-2.0
Every skill or plugin that Meridian itself distributes SHALL declare `Apache-2.0`: the Claude Code plugin manifest's `license` field, and the `license` frontmatter field of `distribution/skill/meridian/SKILL.md` and of its copy inside the plugin.

#### Scenario: Plugin manifest
- **WHEN** `distribution/plugin/meridian/.claude-plugin/plugin.json` is parsed
- **THEN** its `license` is `"Apache-2.0"` and `claude plugin validate` passes

#### Scenario: Distributable skill frontmatter
- **WHEN** the frontmatter of `distribution/skill/meridian/SKILL.md` and `distribution/plugin/meridian/skills/meridian/SKILL.md` is parsed
- **THEN** both declare `license: Apache-2.0`, the two files are byte-identical, and the skill safety scan still passes

### Requirement: Skills generated for user projects carry no Meridian license
Files written by `generate_project_skills` into a user's project (its SKILL.md, `references/rules.md`, and AGENTS.md updates) SHALL NOT contain a `license` frontmatter key, an SPDX identifier, the text "Apache", or a Meridian/Axiom JUMA copyright line, because their content belongs to the user.

#### Scenario: Generated skill is license-free
- **WHEN** `generate_project_skills` runs for a project and the generated files are read
- **THEN** none contains `license:`, `SPDX-`, `Apache`, or `Axiom JUMA`, and a test asserting this passes

