## Context

`security-access-control` currently binds the HTTP/SSE transport to `127.0.0.1` and requires a single bearer token, by design, because it was built for a single-user local agent session. A shared team deployment needs a stronger model before it can safely bind beyond localhost.

## Goals / Non-Goals

**Goals:**
- Define what's required (TLS, multi-token/per-client auth, rate limiting) to safely support a shared, networked deployment.
- Make networked mode strictly opt-in; the default stays localhost-only, single-token.

**Non-Goals:**
- Making networked deployment the default or recommended mode.
- Building a full multi-tenant auth system (e.g. OAuth/SSO) in this change — per-client tokens are the target, not federated identity.

## Decisions

### Decision 1: Threat model first, implementation second
Ship the documented threat model as part of this change regardless of whether the opt-in flag is implemented in the same pass; the flag is only approved for implementation once the threat model is reviewed.

### Decision 2: Additive configuration, not a behavior change to the default path
The existing `Requirement: Localhost-bound, token-authenticated HTTP transport` scenarios (localhost binding, single-token 401 behavior) continue to hold when the new flag is unset.

## Risks / Trade-offs

- Rate limiting and multi-token auth add operational complexity (token issuance/rotation) that the current single-token model avoids entirely.
- A networked deployment, even hardened, expands the attack surface versus localhost-only; the threat model must make this trade-off explicit for whoever opts in.
