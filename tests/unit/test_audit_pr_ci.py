# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
"""scripts/audit_pr_ci.py: the CI job that runs audit_pr with the project's own rules."""

from __future__ import annotations

import importlib.util
import os
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "audit_pr_ci.py"
RULES_FILE = ROOT / ".meridian" / "knowledge-base" / "projects" / "axiom-meridian.md"

DIFF = (
    "diff --git a/src/meridian/a.py b/src/meridian/a.py\n"
    "--- a/src/meridian/a.py\n+++ b/src/meridian/a.py\n"
    "@@ -1 +1,2 @@\n-old\n+new\n+newer\n"
    "diff --git a/README.md b/README.md\n"
    "--- a/README.md\n+++ b/README.md\n@@ -1 +1 @@\n-x\n+y\n"
)


@pytest.fixture(scope="module")
def audit_pr_ci():
    spec = importlib.util.spec_from_file_location("audit_pr_ci", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_versioned_rules_file_holds_the_project_rules():
    text = RULES_FILE.read_text(encoding="utf-8")
    codes = [ln[3:].strip() for ln in text.splitlines() if ln.startswith("## RN-")]
    assert len(codes) >= 8
    assert codes == [f"RN-AXIOM-{n:03d}" for n in range(1, len(codes) + 1)]


def test_audit_evaluates_every_versioned_rule_and_records_it(audit_pr_ci, tmp_path, monkeypatch):
    monkeypatch.setenv("KNOWLEDGE_BASE_PATH", "/sentinel/kb")
    rules_before = RULES_FILE.read_bytes()

    audit = audit_pr_ci.run_audit(RULES_FILE, DIFF, "axiom-meridian", tmp_path)

    versioned = [
        ln[3:].strip() for ln in rules_before.decode("utf-8").splitlines() if ln.startswith("## RN-")
    ]
    assert sorted(r["code"] for r in audit["rules"]) == sorted(versioned)
    assert all(r["scope_id"] == "project-axiom-meridian" for r in audit["rules"])
    conn = sqlite3.connect(tmp_path / "meridian.db")
    try:
        rows = conn.execute("SELECT id, rules_evaluated FROM pr_audits").fetchall()
    finally:
        conn.close()
    assert rows == [(audit["audit_id"], len(versioned))]
    # The versioned file is only read, and the caller's environment is restored.
    assert RULES_FILE.read_bytes() == rules_before
    assert os.environ["KNOWLEDGE_BASE_PATH"] == "/sentinel/kb"


def test_audit_fails_loudly_when_the_rules_file_cannot_be_indexed(audit_pr_ci, tmp_path):
    missing = tmp_path / "nope.md"
    with pytest.raises(FileNotFoundError):
        audit_pr_ci.run_audit(missing, DIFF, "axiom-meridian", tmp_path / "kb")


def test_summary_reports_diff_stats_rules_and_the_no_verdict_notice(audit_pr_ci, tmp_path):
    audit = audit_pr_ci.run_audit(RULES_FILE, DIFF, "axiom-meridian", tmp_path)
    summary = audit_pr_ci.render_summary(audit, DIFF)

    assert f"`{audit['audit_id']}`" in summary
    assert "2 files, +3 / -2 lines" in summary
    assert "RN-AXIOM-001" in summary and "RN-AXIOM-009" in summary
    assert "does not decide whether the diff violates" in summary
    assert "`src/meridian/a.py`" in summary


def test_main_reads_a_diff_file_and_requires_exactly_one_source(audit_pr_ci, tmp_path, capsys):
    diff_file = tmp_path / "pr.diff"
    diff_file.write_text(DIFF, encoding="utf-8")

    assert audit_pr_ci.main(["--diff-file", str(diff_file)]) == 0
    assert "Rules evaluated: 9" in capsys.readouterr().out

    for argv in ([], ["--base-ref", "origin/main", "--diff-file", str(diff_file)]):
        with pytest.raises(SystemExit) as exc:
            audit_pr_ci.main(argv)
        assert exc.value.code == 2
