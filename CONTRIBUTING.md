# Contributing to Axiom Meridian

Thanks for your interest in improving Axiom Meridian.

## License of contributions

Axiom Meridian is licensed under the [Apache License, Version 2.0](LICENSE).
By submitting a contribution (a pull request, patch, or any other material
intended for inclusion), you agree that it is licensed under the same
Apache License 2.0, as described in section 5 of the license ("Submission of
Contributions"). There is no separate contributor license agreement.

The project names "Axiom Meridian" and "Axiom JUMA" are not licensed for
use by contributors (section 6 of the license).

## Developer Certificate of Origin (DCO)

Every commit must be signed off, certifying that you wrote the change or
otherwise have the right to submit it under the project's license, as stated
in the [Developer Certificate of Origin 1.1](https://developercertificate.org/).
Sign off by adding the `-s` flag when committing:

```bash
git commit -s -m "Describe your change"
```

This appends a line with the name and email from your git configuration:

```text
Signed-off-by: Your Name <you@example.com>
```

Use your real name. Pull requests with unsigned commits are asked to amend
them (`git commit --amend -s`, or `git rebase --signoff` for several
commits).

## Development setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/abeljumanuel/axiom-meridian-project.git
cd axiom-meridian-project
uv sync --extra dev --extra rag     # the rag extra is needed for the full test suite
uv run pytest
uv run ruff check src tests scripts
```

Every Python and shell source file under `src/meridian/` and `scripts/`
starts with the SPDX header below (after a shebang, if any). A test fails if
a new file is missing it:

```python
# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
```

## Proposing changes

New features and behavior changes are tracked as
[OpenSpec](https://github.com/Fission-AI/OpenSpec) changes under
`openspec/changes/` (proposal, delta specs, design, tasks). Open an issue or
a change proposal before starting larger work, so the approach can be agreed
first.
