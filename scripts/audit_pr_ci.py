# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
"""Run Meridian's own `audit_pr` on a pull request (run in CI).

Usage: python scripts/audit_pr_ci.py --base-ref origin/main >> "$GITHUB_STEP_SUMMARY"

Builds a throwaway knowledge base from the project rules versioned in
`.meridian/knowledge-base/projects/axiom-meridian.md`, runs `audit_pr` on the
diff between the base ref and HEAD, and prints a Markdown summary.

`audit_pr` does not decide whether a diff violates a rule: it records the
audit and returns the rules and lessons a reviewer (or an LLM client) must
check the diff against. This script therefore never fails on the *content*
of the diff, only when the audit itself cannot run (malformed rules file,
git failure).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES_FILE = ROOT / ".meridian" / "knowledge-base" / "projects" / "axiom-meridian.md"
DEFAULT_PROJECT_ID = "axiom-meridian"
KB_DIRS = ("knowledge-base/global", "knowledge-base/projects", "lessons/global", "lessons/projects")
MAX_LISTED_FILES = 50


def run_audit(rules_file: Path, diff: str, project_id: str, kb_dir: Path) -> dict:
    """Index `rules_file` into a fresh knowledge base at `kb_dir` and audit `diff`."""
    previous = os.environ.get("KNOWLEDGE_BASE_PATH")
    os.environ["KNOWLEDGE_BASE_PATH"] = str(kb_dir)
    try:
        from meridian.db.connection import get_connection, initialize_db
        from meridian.tools import audit_flows
        from meridian.tools.knowledge_management import index_rules_from_markdown

        for sub in KB_DIRS:
            (kb_dir / sub).mkdir(parents=True, exist_ok=True)
        db_path = kb_dir / "meridian.db"
        initialize_db(db_path)

        conn = get_connection(db_path)
        try:
            # The project scope is seeded by schema.sql; only its rules file is missing.
            target = kb_dir / "knowledge-base" / "projects" / f"{project_id}.md"
            shutil.copyfile(rules_file, target)
            index_result = index_rules_from_markdown(str(target), f"project-{project_id}")
            if index_result.get("errors"):
                raise RuntimeError(f"Rules file could not be indexed: {index_result['errors']}")
            return audit_flows.audit_pr(conn, diff, project_id)
        finally:
            conn.close()
    finally:
        if previous is None:
            os.environ.pop("KNOWLEDGE_BASE_PATH", None)
        else:
            os.environ["KNOWLEDGE_BASE_PATH"] = previous


def changed_files(diff: str) -> list[str]:
    return re.findall(r"^diff --git a/.+ b/(.+)$", diff, flags=re.MULTILINE)


def line_counts(diff: str) -> tuple[int, int]:
    added = sum(1 for ln in diff.splitlines() if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in diff.splitlines() if ln.startswith("-") and not ln.startswith("---"))
    return added, removed


def render_summary(audit: dict, diff: str) -> str:
    files = changed_files(diff)
    added, removed = line_counts(diff)
    digest = hashlib.sha256(diff.encode("utf-8")).hexdigest()[:12]
    lines = [
        "## audit_pr: rules context for this pull request",
        "",
        f"- Audit ID: `{audit['audit_id']}`",
        f"- Diff: {len(files)} files, +{added} / -{removed} lines, sha256 `{digest}`",
        f"- Rules evaluated: {len(audit['rules'])}; lessons returned: {len(audit['lessons'])}",
        "",
        "> `audit_pr` records the audit and lists the rules the diff must be checked against.",
        "> It does not decide whether the diff violates them: that judgement is the reviewer's.",
        "",
        "| Rule | Severity | Category | Applies to |",
        "|---|---|---|---|",
    ]
    for rule in audit["rules"]:
        code = rule.get("code") or rule.get("id")
        lines.append(
            f"| {code} | {rule.get('severity')} | {rule.get('category')} "
            f"| {rule.get('applies_to') or ''} |"
        )
    lines += ["", "<details><summary>Changed files</summary>", ""]
    lines += [f"- `{path}`" for path in files[:MAX_LISTED_FILES]]
    if len(files) > MAX_LISTED_FILES:
        lines.append(f"- … and {len(files) - MAX_LISTED_FILES} more")
    lines += ["", "</details>", ""]
    return "\n".join(lines)


def git_diff(base_ref: str) -> str:
    result = subprocess.run(
        ["git", "diff", f"{base_ref}...HEAD"],
        capture_output=True, text=True, encoding="utf-8", check=True, cwd=ROOT,
    )
    return result.stdout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-ref", help="Git ref to diff HEAD against, e.g. origin/main")
    parser.add_argument("--diff-file", type=Path, help="Read the diff from a file instead of git")
    parser.add_argument("--rules-file", type=Path, default=DEFAULT_RULES_FILE)
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    args = parser.parse_args(argv)

    if bool(args.base_ref) == bool(args.diff_file):
        parser.error("pass exactly one of --base-ref or --diff-file")
    diff = (
        args.diff_file.read_text(encoding="utf-8") if args.diff_file else git_diff(args.base_ref)
    )

    with tempfile.TemporaryDirectory() as tmp:
        audit = run_audit(args.rules_file, diff, args.project_id, Path(tmp))
    sys.stdout.write(render_summary(audit, diff))
    return 0


if __name__ == "__main__":
    sys.exit(main())
