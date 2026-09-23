## Why

The HTTP/SSE transport is currently scoped to `127.0.0.1` by design. Teams that want a shared, networked deployment have no supported path today, and naively removing the localhost restriction would create a remote knowledge-base takeover vector (TICKET-015).

## What Changes

- Document a threat model for networked (non-localhost) deployment.
- If approved, add an opt-in configuration flag enabling TLS, multi-token/per-client auth, and rate limiting for networked deployments.
- The localhost-only, single-token behavior remains the default — this is strictly additive.

## Capabilities

### Modified Capabilities
- `security-access-control`: the transport's localhost/token model gains an opt-in, hardened networked mode without weakening the default.

## Impact

- Transport configuration/startup code
- New docs: threat model for networked deployment
