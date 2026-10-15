# Worked examples

## Starting a task on a project

1. `query_rules(project_id="billing-service")` — skim the summaries.
2. If the task touches a specific area, narrow it:
   `query_rules(project_id="billing-service", category="error-handling", detail="full")`.
3. `query_lessons(project_id="billing-service", query_text="payment retries")`
   to surface past incidents related to the task.
4. Apply the rules while working; mention the ids that shaped a decision
   ("following RN-JAVA-012, the DTO is a record").

## Reviewing a pull request

1. Get the diff (from the user, or from version control).
2. `audit_pr(pr_diff=<diff>, project_id="billing-service")`.
3. For each returned rule, check the diff. Report only real findings:

   ```text
   RN-JAVA-012 (high) — src/billing/InvoiceDto.java:14
   Mutable DTO with setters; the rule requires immutable records.
   ```

4. If review comments arrive later, `analyze_pr_feedback(feedback_text=...,
   pr_ref=..., project_id=...)` returns the rules from the original audit so
   you can tell which comments a rule already covered and which reveal a gap.

## Planning a feature

1. `check_feature_against_rules(feature_description=<plan>, project_id=...)`.
2. Flag every rule or lesson the plan conflicts with, and adjust the plan
   before writing code.

## Capturing a lesson after an incident

1. `get_lesson_template()` for the fields and their meaning.
2. Draft the lesson (what happened, impact, root cause, resolution) and pick
   the narrowest scope that fits.
3. `create_pending_proposal(type="lesson", proposed_text=<what happened>,
   metadata='{"severity": "high", "impact": ..., "root_cause": ...,
   "resolution": ..., "tags": [...]}',
   suggested_scope_id="project-billing-service")`. Send only the body as
   `proposed_text`; the block is built from it and `metadata` on approval.
4. Tell the user the proposal id and that it awaits review in
   `list_pending_proposals`.

## Changing or retiring a rule

- Wording or content changes: `create_pending_proposal(type="update",
  target_id="RN-JAVA-012", proposed_text=<new rule text>,
  suggested_scope_id="global-java")`. Add `metadata` only for the fields that
  change (e.g. `'{"severity": "critical"}'`); the others keep their values.
- No longer valid: `deprecate_rule(rule_id="RN-JAVA-012", reason=...,
  superseded_by="RN-JAVA-020")` (the replacement is optional).

Both only create proposals; nothing changes until a reviewer approves.
