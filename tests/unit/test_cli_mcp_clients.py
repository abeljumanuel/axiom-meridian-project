"""Unit tests for meridian.cli._mcp_clients — detection, command resolution,
config shapes, and Claude Code registration handling (cli-setup-and-doctor)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from meridian.cli import _mcp_clients as mc
from meridian.cli import setup as setup_cli


def _which(present: dict[str, str]):
    return lambda name: present.get(name)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for var in ("APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "UV_CACHE_DIR"):
        monkeypatch.delenv(var, raising=False)


# --- detection --------------------------------------------------------------


def test_detects_nothing_on_a_bare_machine(tmp_path):
    assert mc.detect_clients(which=_which({}), home=tmp_path, platform="linux") == []


@pytest.mark.parametrize("platform", ["linux", "darwin", "win32"])
def test_detects_cli_clients_via_path(tmp_path, platform):
    which = _which({n: f"/bin/{n}" for n in ("claude", "kimi", "opencode", "code", "cursor")})
    keys = [c.key for c in mc.detect_clients(which=which, home=tmp_path, platform=platform)]
    assert keys == ["claude-code", "kimi-cli", "opencode", "vscode", "cursor"]


def test_detects_vscode_and_cursor_by_directory(tmp_path):
    (tmp_path / ".config" / "Code").mkdir(parents=True)
    (tmp_path / ".cursor").mkdir()
    keys = [c.key for c in mc.detect_clients(which=_which({}), home=tmp_path, platform="linux")]
    assert keys == ["vscode", "cursor"]


def test_vscode_config_path_per_os(tmp_path):
    assert mc.vscode_user_dir(tmp_path, "linux") == tmp_path / ".config" / "Code" / "User"
    assert mc.vscode_user_dir(tmp_path, "darwin") == (
        tmp_path / "Library" / "Application Support" / "Code" / "User"
    )
    assert mc.vscode_user_dir(tmp_path, "win32") == (
        tmp_path / "AppData" / "Roaming" / "Code" / "User"
    )


def test_windows_uses_appdata_for_vscode(tmp_path, monkeypatch):
    appdata = tmp_path / "Roaming"
    monkeypatch.setenv("APPDATA", str(appdata))
    clients = mc.detect_clients(which=_which({"code": r"C:\bin\code.cmd"}), home=tmp_path,
                                platform="win32")
    assert clients[0].config_path == appdata / "Code" / "User" / "mcp.json"


# --- command resolution -----------------------------------------------------


def _fake_bin(root: Path, platform: str = "linux") -> Path:
    bindir = root / ("Scripts" if platform == "win32" else "bin")
    bindir.mkdir(parents=True)
    exe = bindir / ("meridian.exe" if platform == "win32" else "meridian")
    exe.write_text("")
    return exe


def test_persistent_meridian_on_path_is_registered(tmp_path):
    exe = _fake_bin(tmp_path / "tools" / "axiom-meridian")
    command = mc.resolve_server_command(
        which=_which({"meridian": str(exe)}), prefix=str(tmp_path / "nowhere"),
        platform="linux", cache_dirs=[tmp_path / "cache"],
    )
    assert command == [str(exe), "mcp"]


def test_running_venv_used_when_not_on_path(tmp_path):
    exe = _fake_bin(tmp_path / "venv", platform="win32")
    command = mc.resolve_server_command(
        which=_which({}), prefix=str(tmp_path / "venv"), platform="win32",
        cache_dirs=[tmp_path / "cache"],
    )
    assert command == [str(exe), "mcp"]


def test_running_install_wins_over_a_different_meridian_on_path(tmp_path):
    """install.sh just `uv tool install`ed this one; an unrelated venv's
    meridian earlier on PATH must not be registered instead."""
    running = _fake_bin(tmp_path / "tools" / "axiom-meridian")
    other = _fake_bin(tmp_path / "project" / ".venv")
    command = mc.resolve_server_command(
        which=_which({"meridian": str(other)}), prefix=str(tmp_path / "tools" / "axiom-meridian"),
        platform="linux", cache_dirs=[tmp_path / "cache"],
    )
    assert command == [str(running), "mcp"]


@pytest.mark.skipif(sys.platform == "win32", reason="symlinks")
def test_path_spelling_used_when_it_points_at_the_running_install(tmp_path):
    running = _fake_bin(tmp_path / "tools" / "axiom-meridian")
    (tmp_path / "localbin").mkdir()
    link = tmp_path / "localbin" / "meridian"
    link.symlink_to(running)
    command = mc.resolve_server_command(
        which=_which({"meridian": str(link)}), prefix=str(tmp_path / "tools" / "axiom-meridian"),
        platform="linux", cache_dirs=[tmp_path / "cache"],
    )
    assert command == [str(link), "mcp"]


@pytest.mark.parametrize("rag,source", [(False, "axiom-meridian"), (True, "axiom-meridian[rag]")])
def test_uvx_run_registers_uvx_not_cache_path(tmp_path, rag, source):
    """A `uvx` run: no meridian on PATH, sys.prefix inside the uv cache."""
    cache = tmp_path / "cache" / "uv"
    uvx_env = cache / "archive-v0" / "abc123"
    _fake_bin(uvx_env)
    command = mc.resolve_server_command(
        rag=rag, which=_which({}), prefix=str(uvx_env), platform="linux", cache_dirs=[cache],
    )
    assert command == ["uvx", "--from", source, "meridian", "mcp"]
    assert str(cache) not in " ".join(command)


def test_default_cache_dirs_per_os(tmp_path):
    assert mc.uv_cache_dirs(tmp_path, "linux") == [tmp_path / ".cache" / "uv"]
    assert mc.uv_cache_dirs(tmp_path, "win32") == [tmp_path / "AppData" / "Local" / "uv" / "cache"]


def test_same_install_rules():
    desired = ["/home/u/.local/bin/meridian", "mcp"]
    assert mc.same_install(["/home/u/.local/bin/meridian", "mcp"], desired)
    assert mc.same_install(["/home/u/.local/bin/python", "-m", "meridian", "mcp"], desired)
    assert not mc.same_install(["/home/u/.meridian/venv/bin/meridian", "mcp"], desired)
    uvx = mc.uvx_command(rag=False)
    assert mc.same_install(["/opt/uv/uvx", *uvx[1:]], uvx)
    assert not mc.same_install(mc.uvx_command(rag=True), uvx)


# --- JSON client config shapes ----------------------------------------------

_CMD = ["/opt/meridian/bin/meridian", "mcp"]
_ENV = {"KNOWLEDGE_BASE_PATH": "/kb", "MERIDIAN_ACCESS_LEVEL": "write"}


def test_config_shape_mcpservers():
    assert mc.new_config("mcpServers", _CMD, _ENV) == {
        "mcpServers": {"meridian": {"command": _CMD[0], "args": ["mcp"], "env": _ENV}}
    }


def test_config_shape_vscode():
    assert mc.new_config("vscode", _CMD, _ENV) == {
        "servers": {
            "meridian": {"type": "stdio", "command": _CMD[0], "args": ["mcp"], "env": _ENV}
        }
    }


def test_config_shape_opencode():
    doc = mc.new_config("opencode", _CMD, _ENV)
    assert doc["mcp"] == {
        "meridian": {"type": "local", "command": _CMD, "environment": _ENV}
    }
    assert doc["permission"] == {"mcp": {"meridian": "ask"}}


@pytest.mark.parametrize(
    "key,flavor", [("kimi-cli", "mcpServers"), ("vscode", "vscode"), ("opencode", "opencode"),
                   ("cursor", "mcpServers")],
)
def test_configure_writes_new_file(tmp_path, key, flavor):
    client = mc.Client(key, key, flavor, tmp_path / "cfg" / "mcp.json")
    assert setup_cli.configure_client(client, _CMD, _ENV)
    doc = json.loads(client.config_path.read_text())
    assert doc == mc.new_config(flavor, _CMD, _ENV)
    assert mc.configured_command(client, doc) == _CMD


def test_configure_merges_into_existing_file_with_backup(tmp_path):
    path = tmp_path / "mcp.json"
    original = {"mcpServers": {"other": {"command": "x"}}, "theme": "dark"}
    path.write_text(json.dumps(original))
    client = mc.Client("cursor", "Cursor", "mcpServers", path)

    assert setup_cli.configure_client(client, _CMD, _ENV)

    doc = json.loads(path.read_text())
    assert doc["theme"] == "dark"
    assert doc["mcpServers"]["other"] == {"command": "x"}
    assert doc["mcpServers"]["meridian"]["command"] == _CMD[0]
    assert json.loads((tmp_path / "mcp.json.meridian-bak").read_text()) == original


def test_configure_never_overwrites_a_different_install(tmp_path, capsys):
    path = tmp_path / "mcp.json"
    existing = mc.new_config("mcpServers", ["/old/venv/bin/meridian", "mcp"], _ENV)
    path.write_text(json.dumps(existing))
    client = mc.Client("kimi-cli", "Kimi CLI", "mcpServers", path)

    assert not setup_cli.configure_client(client, _CMD, _ENV)

    assert json.loads(path.read_text()) == existing
    assert "different Meridian install" in capsys.readouterr().out


def test_configure_leaves_jsonc_untouched(tmp_path, capsys):
    path = tmp_path / "mcp.json"
    path.write_text('{\n  // my servers\n  "servers": {}\n}\n')
    client = mc.Client("vscode", "VSCode", "vscode", path)

    assert not setup_cli.configure_client(client, _CMD, _ENV)
    assert "// my servers" in path.read_text()
    assert "Add manually" in capsys.readouterr().out


# --- Claude Code ------------------------------------------------------------


def _proc(stdout: str, returncode: int = 0):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="")


def test_claude_list_entry_parses_plain_output():
    out = (
        "Checking MCP server health...\n\n"
        "engram: engram mcp - ✓ Connected\n"
        "meridian: /home/u/.local/bin/meridian mcp - ✓ Connected\n"
    )
    line = mc.claude_list_entry("claude", run=lambda *a, **k: _proc(out))
    assert line == "meridian: /home/u/.local/bin/meridian mcp - ✓ Connected"


def test_claude_list_entry_ignores_prefixed_names():
    out = "meridian-dev: /x/bin/meridian mcp - ✓ Connected\n"
    assert mc.claude_list_entry("claude", run=lambda *a, **k: _proc(out)) is None


@pytest.fixture
def claude_env(monkeypatch):
    """Route setup's Claude Code calls through a fake `claude` CLI."""
    calls: list[list[str]] = []
    state = {"list": ""}

    def fake_run(argv, **kwargs):
        calls.append(argv)
        if argv[1:3] == ["mcp", "list"]:
            return _proc(state["list"])
        return _proc("Added")

    monkeypatch.setattr(setup_cli.shutil, "which", lambda name: "/bin/claude")
    monkeypatch.setattr(mc.subprocess, "run", fake_run)
    monkeypatch.setattr(setup_cli.subprocess, "run", fake_run)
    return state, calls


def _added(calls):
    return [c for c in calls if c[1:3] == ["mcp", "add"]]


def test_claude_not_registered_gets_added(claude_env):
    state, calls = claude_env
    client = mc.Client("claude-code", "Claude Code", "claude-cli")
    assert setup_cli.configure_client(client, _CMD, _ENV)
    (add,) = _added(calls)
    assert add[-3:] == ["meridian", *_CMD]
    assert "KNOWLEDGE_BASE_PATH=/kb" in add


def test_claude_registered_same_install_is_left_alone(claude_env, capsys):
    state, calls = claude_env
    state["list"] = f"meridian: {_CMD[0]} mcp - ✓ Connected\n"
    client = mc.Client("claude-code", "Claude Code", "claude-cli")
    assert setup_cli.configure_client(client, _CMD, _ENV)
    assert _added(calls) == []
    out = capsys.readouterr().out
    assert "already configured" in out and "different" not in out


def test_claude_registered_different_install_warns_with_switch_commands(claude_env, capsys):
    state, calls = claude_env
    state["list"] = "meridian: /home/u/.meridian/venv/bin/meridian mcp - ✓ Connected\n"
    client = mc.Client("claude-code", "Claude Code", "claude-cli")
    assert not setup_cli.configure_client(client, _CMD, _ENV)
    assert _added(calls) == []
    out = capsys.readouterr().out
    assert "different Meridian install" in out
    assert "claude mcp remove -s user meridian" in out
    assert f"-- meridian {_CMD[0]} mcp" in out


def test_claude_get_command_parses_details():
    out = (
        "meridian:\n  Scope: User config\n  Status: ✔ Connected\n  Type: stdio\n"
        "  Command: /home/u/.meridian/venv/bin/meridian\n  Args: mcp\n"
    )
    assert mc.claude_get_command("claude", run=lambda *a, **k: _proc(out)) == [
        "/home/u/.meridian/venv/bin/meridian", "mcp",
    ]
