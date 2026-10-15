# license-files Specification

## Purpose
TBD - created by archiving change change-license-to-apache-2. Update Purpose after archive.
## Requirements
### Requirement: LICENSE contains the verbatim Apache License 2.0
The repository root SHALL contain a `LICENSE` file whose content is byte-for-byte identical to the official text published at `https://www.apache.org/licenses/LICENSE-2.0.txt`, obtained from that URL rather than written by hand.

#### Scenario: LICENSE matches the upstream text
- **WHEN** `LICENSE` is compared with a fresh download of `https://www.apache.org/licenses/LICENSE-2.0.txt`
- **THEN** the two are byte-for-byte identical

#### Scenario: License detectors recognize the file
- **WHEN** a license scanner (e.g. GitHub's license detection or an SPDX matcher) inspects the repository
- **THEN** it identifies the project license as `Apache-2.0`

### Requirement: NOTICE carries attribution and the trademark statement
The repository root SHALL contain a `NOTICE` file that names the product (`Axiom Meridian`), states `Copyright <year> <legal name> (Axiom JUMA)`, and states that "Axiom Meridian" and "Axiom JUMA" are trademarks of their owner that the license does not grant, and SHALL contain no other third-party attributions while no third-party code is vendored.

#### Scenario: NOTICE content
- **WHEN** `NOTICE` is read
- **THEN** it contains the line `Axiom Meridian`, a `Copyright` line naming the legal name followed by `(Axiom JUMA)`, and a statement that both names are trademarks not licensed under the Apache License

#### Scenario: No placeholder ships
- **WHEN** a release is prepared
- **THEN** `grep -rn "<NOMBRE_LEGAL>"` over `NOTICE`, `pyproject.toml`, `src/`, and `scripts/` returns no matches

