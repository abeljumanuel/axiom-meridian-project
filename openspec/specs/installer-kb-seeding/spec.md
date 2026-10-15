# Installer Knowledge Base Seeding Specification

## Purpose
Seed a knowledge base during installation without ever overwriting a user's existing knowledge files.
## Requirements
### Requirement: Seeding never overwrites an existing knowledge base file
The example-knowledge-base seeding step — now performed by `meridian setup` (invoked directly or by `scripts/install.sh`), reading the bundled examples from package data — SHALL check whether the destination path for a bundled example `.md` file already exists before copying to it, and SHALL skip copying and indexing that file — leaving it and its indexed data completely untouched — when the destination already exists, logging a warning that names the skipped file and the reason.

#### Scenario: Destination file already exists
- **WHEN** seeding runs (via `meridian setup --seed`, `SEED_KB=1 scripts/install.sh`, or an affirmative answer to the seed prompt) and a bundled example file's destination path already exists in the knowledge base
- **THEN** that file is not copied, its destination's bytes are unchanged, it is not indexed, and a warning naming it is logged

#### Scenario: Destination file does not exist (fresh install)
- **WHEN** seeding runs and a bundled example file's destination path does not yet exist
- **THEN** the file is copied and indexed exactly as before this change

