# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `LICENSE` with the full Apache License 2.0 text, and `NOTICE` with the
  copyright attribution and the "Axiom Meridian" / "Axiom JUMA" trademark
  statement.
- `CONTRIBUTING.md`: contributions are accepted under Apache-2.0 with a
  Developer Certificate of Origin sign-off (`git commit -s`).
- SPDX license headers on every source file under `src/meridian/` and
  `scripts/`, enforced by a test.

### Changed

- Relicensed from MIT to Apache License 2.0. Versions made available
  before this change were declared under MIT, and copies obtained under
  those terms remain available under them. Package metadata now declares
  `License-Expression: Apache-2.0` (PEP 639) and ships `LICENSE` and
  `NOTICE` in the wheel and sdist.
