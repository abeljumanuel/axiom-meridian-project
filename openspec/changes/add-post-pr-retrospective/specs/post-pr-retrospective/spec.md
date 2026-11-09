## ADDED Requirements

### Requirement: Evidence-based candidates
The retrospective SHALL propose a rule or lesson only when it can cite evidence from the pull request (a failed or flaky check, a review comment, a commit, a documented mistake), and SHALL propose at most five candidates per pull request.

#### Scenario: PR with a lesson
- **WHEN** the retrospective runs on a PR whose checks failed for a reason that was then fixed
- **THEN** a candidate lesson is created that cites that failure as its evidence

#### Scenario: Routine PR
- **WHEN** the retrospective runs on a PR with nothing to learn
- **THEN** no proposal is created
- **AND** the outcome is reported as "none"

### Requirement: Human decision
The retrospective SHALL create only `pending_proposals` and SHALL NOT call `approve_proposal`. It SHALL work at access level `analyze`.

#### Scenario: Agent without write access
- **WHEN** the retrospective runs with `MERIDIAN_ACCESS_LEVEL=analyze`
- **THEN** candidates are created as pending proposals
- **AND** no row of `rules` or `lessons` and no `.md` file changes

### Requirement: Duplicate awareness
The retrospective SHALL compare each candidate with the existing rules and lessons and SHALL NOT create a proposal that duplicates one; it SHALL report the matching code to the person instead.

#### Scenario: Candidate matches an existing rule
- **WHEN** a candidate is equivalent to an existing rule
- **THEN** no proposal is created for it
- **AND** the report names the existing rule code

### Requirement: Provenance
Every proposal created by the retrospective SHALL carry `source_type="manual"` and a `source_ref` that points to the pull request.

#### Scenario: Trace a proposal to its PR
- **WHEN** a reviewer lists the pending proposals
- **THEN** each one shows the PR link it came from
