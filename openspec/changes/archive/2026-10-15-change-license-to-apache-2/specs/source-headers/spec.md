## ADDED Requirements

### Requirement: Meridian source files carry SPDX headers
Every `*.py` file under `src/meridian/`, and every `*.sh` and `*.py` file directly under `scripts/`, SHALL contain, within its first five lines (after an optional shebang), the lines `# SPDX-FileCopyrightText: <year> <legal name> (Axiom JUMA)` and `# SPDX-License-Identifier: Apache-2.0`, without changing any module's docstring or behavior.

#### Scenario: Existing file has the header
- **WHEN** any in-scope file is opened
- **THEN** both SPDX lines appear within its first five lines, and a shebang, if present, remains the first line

#### Scenario: Docstrings are unaffected
- **WHEN** a module under `src/meridian/` that had a module docstring is imported
- **THEN** its `__doc__` is unchanged

### Requirement: Missing headers fail the test suite
The test suite SHALL include a check that fails, naming each offending file and printing the exact header to add, when an in-scope file lacks either SPDX line.

#### Scenario: New file without a header
- **WHEN** a new `.py` file without the SPDX lines is added under `src/meridian/` and `uv run pytest` is run
- **THEN** the header test fails and its message names that file and shows the two lines to add

#### Scenario: All files compliant
- **WHEN** every in-scope file has both lines and `uv run pytest` is run
- **THEN** the header test passes
