# package-metadata Specification

## Purpose
TBD - created by archiving change change-license-to-apache-2. Update Purpose after archive.
## Requirements
### Requirement: Package declares Apache-2.0 via PEP 639
`pyproject.toml` SHALL declare `license = "Apache-2.0"` (an SPDX expression) and `license-files = ["LICENSE", "NOTICE"]`, SHALL require a hatchling version that supports PEP 639 in `[build-system]`, and SHALL NOT declare any `License ::` trove classifier.

#### Scenario: Built wheel metadata
- **WHEN** `uv build` is run and the wheel's `METADATA` file is inspected
- **THEN** it contains `License-Expression: Apache-2.0` and `License-File` entries for `LICENSE` and `NOTICE`, and no `Classifier: License ::` line

#### Scenario: Build backend supports the metadata
- **WHEN** the package is built in a clean environment honoring `[build-system] requires`
- **THEN** the build succeeds without license-related errors or warnings

### Requirement: LICENSE and NOTICE ship in every artifact
The wheel and the sdist SHALL both contain `LICENSE` and `NOTICE`, with content identical to the repository files.

#### Scenario: Wheel contents
- **WHEN** the built wheel's file list is inspected
- **THEN** it contains `LICENSE` and `NOTICE` under its `.dist-info/licenses/` directory

#### Scenario: sdist contents
- **WHEN** the built sdist's file list is inspected
- **THEN** it contains `LICENSE` and `NOTICE` at its top level, and still contains none of the excluded local directories (`.claude/`, `.atl/`, `changes/`, `openspec/`, `docs/`)

### Requirement: Authors name the legal rights holder
`pyproject.toml`'s `authors` SHALL list the maintainer's legal name and "Axiom JUMA".

#### Scenario: Author metadata
- **WHEN** the wheel's `METADATA` is inspected
- **THEN** the `Author` field lists the legal name and `Axiom JUMA`

