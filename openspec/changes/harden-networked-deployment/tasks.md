## 1. Threat model

- [ ] 1.1 Document the threat model for a non-localhost deployment (attacker capabilities, assets at risk, mitigations)
- [ ] 1.2 Get the threat model reviewed/approved before implementing the flag

## 2. Opt-in networked mode

- [ ] 2.1 Add the opt-in configuration flag (off by default)
- [ ] 2.2 Implement TLS support for the networked mode
- [ ] 2.3 Implement multi-token/per-client auth for the networked mode
- [ ] 2.4 Implement rate limiting for the networked mode

## 3. Verify

- [ ] 3.1 Confirm default behavior (flag unset) is unchanged: localhost-only, single-token, `401` on missing/invalid token
- [ ] 3.2 Confirm networked mode enforces TLS, per-client auth, and rate limiting when the flag is set
