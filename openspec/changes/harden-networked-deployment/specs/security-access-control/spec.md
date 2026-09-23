## MODIFIED Requirements

### Requirement: Localhost-bound, token-authenticated HTTP transport
The system SHALL bind the HTTP/SSE transport to `127.0.0.1` by default and SHALL reject any request lacking a valid, current-session `Authorization: Bearer <token>` header with `401`. An opt-in configuration flag MAY enable a networked (non-localhost) mode with TLS, multi-token/per-client auth, and rate limiting; the default behavior SHALL remain localhost-only, single-token.

#### Scenario: Request without a valid bearer token
- **WHEN** a request to the HTTP/SSE transport omits a valid, current-session bearer token
- **THEN** the server responds `401`

#### Scenario: Default transport binding
- **WHEN** the HTTP/SSE transport starts with no networked-mode flag set
- **THEN** it binds only to `127.0.0.1` and requires single-token bearer auth

#### Scenario: Opt-in networked deployment
- **WHEN** the opt-in networked-mode configuration flag is set
- **THEN** the transport requires TLS and multi-token/per-client auth and applies rate limiting, per the documented threat model
