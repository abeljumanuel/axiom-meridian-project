# Meridian tool reference

Base names; the prefix depends on how the server is installed. Access levels
are cumulative (`read` < `analyze` < `write`); the server's configured level
decides which tools can run (default `analyze`).

## Read

| Tool | Parameters | Returns |
|---|---|---|
| `query_rules` | `project_id`, `category?`, `severity?`, `tags?`, `query_text?`, `format?` (`json`/`toon`), `detail?` (`summary`/`full`), `include_deprecated?` | Active rules across the project's scope chain, most specific first |
| `query_lessons` | `project_id`, `area?`, `tags?`, `query_text?`, `format?`, `detail?`, `include_deprecated?` | Active lessons across the scope chain |
| `get_rule_context` | `rule_id` | Full rule text, complete history, linked lessons |
| `get_rule_timeline` | `rule_id` | Chronological history without full text |
| `get_project_scope_resolution` | `project_id` | The project's scope chain with each scope's attributes |
| `get_rule_audit_log` | `project_id?`, `scope_id?`, `since?` | History of rule changes plus currently deprecated rules |
| `list_pending_proposals` | `project_id?`, `type?`, `status?` | Proposals awaiting review |
| `get_rule_template` / `get_lesson_template` / `get_transcription_template` | — | Canonical block formats and instructions |
| `get_server_info` | — | Server version and whether its code changed on disk since start |

## Analyze

| Tool | Parameters | Returns |
|---|---|---|
| `audit_pr` | `pr_diff`, `project_id` | Applicable rules/lessons in full + an audit record id |
| `check_feature_against_rules` | `feature_description`, `project_id` | Applicable rules/lessons in full + a planning check record |
| `analyze_pr_feedback` | `feedback_text`, `pr_ref`, `project_id` | The rules that applied at audit time, for classifying feedback |
| `extract_rules_from_transcript` / `extract_lessons_from_transcript` | `text`, `project_id` | Clean text, scope chain, existing items for duplicate checks, template |
| `create_pending_proposal` | `type` (`rule`/`lesson`/`update`), `proposed_text`, `suggested_scope_id`, `target_id?` (for `update`), `target_type?`, `suggested_attributes?`, `source_type?`, `source_ref?` | The new proposal id |
| `deprecate_rule` | `rule_id` (`RN-*` or `LL-*`), `reason`, `superseded_by?` | A pending deprecation proposal |

## Write (human reviewer actions — run only when asked)

`approve_proposal`, `edit_proposal`, `reject_proposal`, `promote_rule`,
`create_project`, `index_rules_from_markdown`, `index_lessons_from_markdown`,
`convert_to_atomic_format`, `generate_embeddings`, `generate_project_skills`.

## Error responses

| `error` | Meaning |
|---|---|
| `ACCESS_DENIED` | The server's access level is below the tool's; includes `required_level` and `current_level`. |
| `RAG_NOT_INSTALLED` | `generate_embeddings` was called on a server without the optional semantic-search extra. Queries still work without it. |
