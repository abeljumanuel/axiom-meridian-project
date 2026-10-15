## REMOVED Requirements

### Requirement: Declining to recreate an existing venv does not abort the installer
**Reason**: `scripts/install.sh` no longer creates or manages a virtual environment — it delegates to `uv tool install --force`, which reinstalls in place without prompting, and then to `meridian setup` (see `cli-setup-and-doctor`). There is no `setup_venv()` step left whose decline branch could abort the installer.
**Migration**: None needed. Re-running `install.sh` over an existing install upgrades it in place; the legacy `~/.meridian/venv` from the old installer is removed by `scripts/uninstall.sh`.
