## ADDED Requirements

### Requirement: Direct dependency licenses are recorded and compatible
The change's design SHALL record, for every direct dependency (runtime, `rag` extra, and dev), its license as read from installed package metadata or PyPI, and SHALL conclude whether each is compatible with distributing Meridian under Apache-2.0; no direct dependency SHALL carry a license that imposes terms on Meridian's own license.

#### Scenario: Table is complete
- **WHEN** the dependency table in `design.md` is compared with `[project] dependencies` and `[project.optional-dependencies]` in `pyproject.toml`
- **THEN** every listed dependency appears in the table with a license and a compatibility verdict

#### Scenario: Licenses re-verified before release
- **WHEN** the installed metadata (`License-Expression`, `License`, classifiers) of each direct dependency is queried before the first release
- **THEN** each reported license matches the table, or the table is updated and the compatibility verdict re-assessed
