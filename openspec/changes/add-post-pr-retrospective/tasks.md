## 1. Skill

- [ ] 1.1 Write the evidence checklist and the retrospective instructions in `distribution/skill/meridian/`
- [ ] 1.2 Mirror the change into the plugin copy and run `scripts/check_versions.py`
- [ ] 1.3 Run `scripts/check_skill_safety.py` and `scripts/package_skill.py`

## 2. Optional collector

- [ ] 2.1 Add `meridian retro collect --pr N` that prints the PR evidence as text using `gh`
- [ ] 2.2 Test it against a stubbed `gh` so no network is needed

## 3. Documentation

- [ ] 3.1 Document the flow in the README or `docs/installation.md`
- [ ] 3.2 Add the optional step to the PR-closing guidance in `CONTRIBUTING.md`

## 4. Verify

- [ ] 4.1 Run it by hand on PRs #12, #15 and #16 and record useful, duplicated and noisy candidates
- [ ] 4.2 Confirm that only `pending_proposals` rows change and that the flow works at `MERIDIAN_ACCESS_LEVEL=analyze`
- [ ] 4.3 Confirm a PR without lessons produces zero proposals
