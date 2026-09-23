# Security and Access Control Specification

## Purpose
Ensure every tool call is gated by access level, every action is auditable, and enabling the network transport never creates a remote knowledge-base takeover vector.

## Requirements

### Requirement: Access-level gating
The system SHALL gate every tool by access level (`read`/`analyze`/`write`) and SHALL return a structured `ACCESS_DENIED` response naming the required level, with no side effect, when a session's configured `MERIDIAN_ACCESS_LEVEL` is insufficient.

#### Scenario: Read-only session attempts a write-level tool
- **WHEN** a session configured with `MERIDIAN_ACCESS_LEVEL=read` calls a tool requiring `write` level
- **THEN** the response is a structured `ACCESS_DENIED` naming the required level
- **AND** no side effect occurs

### Requirement: Tool-call audit log
The system SHALL log every tool call chronologically with its access level and outcome, filterable by project/scope/date, and SHALL NOT record sensitive parameter values such as diff text, feedback text, or proposed text.

#### Scenario: Review the audit log
- **WHEN** a platform admin calls `get_rule_audit_log` filtered by project, scope, or date
- **THEN** matching log entries are returned
- **AND** no entry contains diff text, feedback text, or proposed text

### Requirement: Localhost-bound, token-authenticated HTTP transport
The system SHALL bind the HTTP/SSE transport to `127.0.0.1` and SHALL reject any request lacking a valid, current-session `Authorization: Bearer <token>` header with `401`.

#### Scenario: Request without a valid bearer token
- **WHEN** a request to the HTTP/SSE transport omits a valid, current-session bearer token
- **THEN** the server responds `401`

#### Scenario: Transport binding
- **WHEN** the HTTP/SSE transport starts
- **THEN** it binds only to `127.0.0.1`
