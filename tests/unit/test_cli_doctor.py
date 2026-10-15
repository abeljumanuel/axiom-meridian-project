"""Unit tests for meridian.cli.doctor — one per diagnosed failure mode."""

from __future__ import annotations

import os
import stat
import sys

import pytest

from meridian.cli import doctor
from meridian.cli import _mcp_clients as mc


def _venv(root, *, home=None):
    site = root / "lib" / "python3.11" / "site-packages"
    site.mkdir(parents=True)
    bindir = root / "bin"
    bindir.mkdir()
    exe = bindir / "meridian"
    exe.write_text("#!/bin/sh\n")
    exe.chmod(0o755)
    (root / "pyvenv.cfg").write_text(f"home = {home or sys.prefix}\n")
    return exe, site


def _statuses(checks):
    return [c.status for c in checks]


def test_healthy_configured_binary(tmp_path):
    exe, _ = _venv(tmp_path / "venv", home=os.path.dirname(sys.executable))
    checks = doctor.check_configured_command("Claude Code", [str(exe), "mcp"])
    assert _statuses(checks) == [doctor.OK]


def test_missing_binary_fails(tmp_path):
    checks = doctor.check_configured_command(
        "Claude Code", [str(tmp_path / "gone" / "bin" / "meridian"), "mcp"]
    )
    assert _statuses(checks) == [doctor.FAIL]
    assert "meridian setup" in checks[0].fix


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX executable bit")
def test_non_executable_binary_fails(tmp_path):
    exe, _ = _venv(tmp_path / "venv")
    exe.chmod(0o644)
    checks = doctor.check_configured_command("Kimi CLI", [str(exe), "mcp"])
    assert _statuses(checks) == [doctor.FAIL]


def test_stale_uv_run_config_fails():
    checks = doctor.check_configured_command(
        "VSCode", ["uv", "run", "--directory", "/src/meridian", "python", "-m", "meridian", "mcp"]
    )
    assert _statuses(checks) == [doctor.FAIL]
    assert "uv run" in checks[0].title


def test_uvx_without_uvx_installed_fails():
    checks = doctor.check_configured_command("Cursor", mc.uvx_command(False), which=lambda n: None)
    assert _statuses(checks) == [doctor.FAIL]


def test_uvx_with_uvx_installed_ok():
    checks = doctor.check_configured_command(
        "Cursor", mc.uvx_command(False), which=lambda n: "/usr/local/bin/uvx"
    )
    assert _statuses(checks) == [doctor.OK]


def test_moved_base_interpreter_fails(tmp_path):
    """The 'Library not loaded: @rpath/libpython3.11.dylib' case."""
    root = tmp_path / "venv"
    _venv(root, home=str(tmp_path / "deleted-python" / "bin"))
    check = doctor.check_base_interpreter(root, "linux")
    assert check is not None and check.status == doctor.FAIL
    assert "libpython" in check.fix


def test_cloud_sync_duplicates_fail(tmp_path):
    root = tmp_path / "venv"
    _, site = _venv(root)
    (site / "meridian").mkdir()
    (site / "meridian" / "server 2.py").write_text("")
    checks = doctor.check_sync_corruption(root, "linux")
    assert _statuses(checks) == [doctor.FAIL]
    assert "server 2.py" in checks[0].detail


@pytest.mark.skipif(not hasattr(stat, "UF_HIDDEN"), reason="BSD file flags (macOS) only")
def test_hidden_pth_fails(tmp_path):
    root = tmp_path / "venv"
    _, site = _venv(root)
    pth = site / "_editable_impl_axiom_meridian.pth"
    pth.write_text("/src\n")
    os.chflags(pth, stat.UF_HIDDEN)
    checks = doctor.check_sync_corruption(root, "darwin")
    assert _statuses(checks) == [doctor.FAIL]
    assert "chflags nohidden" in checks[0].fix


def test_clean_venv_has_no_sync_findings(tmp_path):
    root = tmp_path / "venv"
    _, site = _venv(root)
    (site / "_editable_impl_axiom_meridian.pth").write_text("/src\n")
    assert doctor.check_sync_corruption(root, "linux") == []


# --- end to end: exit codes --------------------------------------------------


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    kb = tmp_path / "kb"
    for sub in ("knowledge-base/global", "lessons/global"):
        (kb / sub).mkdir(parents=True)
    monkeypatch.setenv("KNOWLEDGE_BASE_PATH", str(kb))
    monkeypatch.setattr(doctor, "check_sync_corruption", lambda *a, **k: [])
    monkeypatch.setattr(doctor, "check_base_interpreter", lambda *a, **k: None)
    return tmp_path


def test_doctor_exits_zero_when_healthy(isolated, monkeypatch, capsys):
    exe, _ = _venv(isolated / "venv")
    client = mc.Client("cursor", "Cursor", "mcpServers", isolated / "mcp.json")
    mc.write_config(client.config_path, mc.new_config("mcpServers", [str(exe), "mcp"], {}))
    monkeypatch.setattr(mc, "detect_clients", lambda: [client])

    assert doctor.run([]) == 0
    assert "No problems found" in capsys.readouterr().out


def test_doctor_exits_nonzero_on_broken_client(isolated, monkeypatch, capsys):
    client = mc.Client("cursor", "Cursor", "mcpServers", isolated / "mcp.json")
    mc.write_config(
        client.config_path,
        mc.new_config("mcpServers", [str(isolated / "missing" / "meridian"), "mcp"], {}),
    )
    monkeypatch.setattr(mc, "detect_clients", lambda: [client])

    assert doctor.run([]) == 1
    assert "1 problem(s) found" in capsys.readouterr().out
