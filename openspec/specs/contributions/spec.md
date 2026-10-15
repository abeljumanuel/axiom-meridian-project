# contributions Specification

## Purpose
TBD - created by archiving change change-license-to-apache-2. Update Purpose after archive.
## Requirements
### Requirement: Contributions are accepted under Apache 2.0 with a DCO sign-off
`CONTRIBUTING.md` SHALL state that contributions submitted for inclusion are licensed under the Apache License 2.0 (per its section 5), and SHALL require each commit to carry a Developer Certificate of Origin sign-off (`Signed-off-by:`, e.g. via `git commit -s`), linking the DCO text rather than requiring a separate agreement.

#### Scenario: Contributor reads the guidelines
- **WHEN** a prospective contributor opens `CONTRIBUTING.md`
- **THEN** it states the inbound Apache-2.0 terms, explains the DCO sign-off, shows the `git commit -s` command, and links the DCO text

#### Scenario: README points to the guidelines
- **WHEN** `README.md` is read
- **THEN** it links to `CONTRIBUTING.md`

