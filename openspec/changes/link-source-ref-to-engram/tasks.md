## 1. Resolution helper

- [ ] 1.1 Implement a `source_ref` → Engram `observation_id` resolver behind a soft dependency (no-op when Engram is absent)
- [ ] 1.2 Ensure import/config failures degrade to "no link" rather than raising

## 2. `get_rule_context` integration

- [ ] 2.1 Surface the linked observation in `get_rule_context`'s response when resolution succeeds
- [ ] 2.2 Leave the field omitted when Engram is absent or resolution fails

## 3. Verify

- [ ] 3.1 Regression-test `get_rule_context` with Engram absent — response unchanged from current behavior
- [ ] 3.2 Test `get_rule_context` with Engram present and a resolvable `source_ref` — linked observation appears
