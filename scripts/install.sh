#!/bin/bash
# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
#
# Meridian Installer (Linux / macOS)
# Installs the Axiom Meridian MCP server.
#
# A thin wrapper: ensures `uv` is available, installs a persistent `meridian`
# command with `uv tool install`, then hands off to `meridian setup` (Python,
# cross-platform) for MCP client configuration and knowledge-base seeding.
#
# Usage:
#   Local:     bash scripts/install.sh
#   Remote:    curl -fsSL https://raw.githubusercontent.com/abeljumanuel/axiom-meridian-project/main/scripts/install.sh | bash
#
# Options:
#   RAG=1 / RAG=0           - Install with / without semantic search (the 'rag'
#                             extra, ~900MB of ML libraries) without asking
#   SEED_KB=1 / SEED_KB=0   - Seed / skip the example knowledge base without asking
#   SKIP_MCP=1              - Skip MCP client configuration
#   KNOWLEDGE_BASE_PATH=/p  - Custom knowledge base path
#   MERIDIAN_PACKAGE=spec   - What to install when not run from a clone
#                             (default: axiom-meridian from PyPI; e.g.
#                             git+https://github.com/abeljumanuel/axiom-meridian-project)
#   DRY_RUN=1               - Show what would be done without executing
#
# Run from a clone, the clone itself is installed (editable), so source
# changes take effect on the next server restart.
#
# Windows: no script needed — see print_usage below.

set -e

PACKAGE_NAME="axiom-meridian"
SCRIPT_SOURCE="${BASH_SOURCE[0]:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Prompts read from the terminal, not stdin: under `curl ... | bash`, stdin
# *is* the script, and `read` would swallow the rest of it.
has_tty() {
    [ -t 1 ] && { : < /dev/tty; } 2>/dev/null
}

ask_yes_no() {
    # ask_yes_no "question" default(y|n) — returns 0 for yes.
    local question="$1" default="$2" reply suffix
    if [ "$default" = "y" ]; then suffix="[Y/n]"; else suffix="[y/N]"; fi
    if ! has_tty; then
        [ "$default" = "y" ]
        return
    fi
    read -r -p "$question $suffix " reply < /dev/tty
    reply="${reply:-$default}"
    [[ $reply =~ ^[YySs] ]]
}

run() {
    if [ "$DRY_RUN" = "1" ]; then
        echo "  [DRY RUN] $*"
    else
        "$@"
    fi
}

detect_os() {
    case "$(uname)" in
        Darwin) OS="macos" ;;
        Linux) OS="linux" ;;
        *)
            log_error "Unsupported operating system for this script."
            print_windows_instructions
            exit 1
            ;;
    esac
    log_info "Detected OS: $OS"
}

# Run from a checkout (bash scripts/install.sh) → install that checkout.
# Piped from curl (no script file on disk) → install from PyPI.
detect_source() {
    REPO_ROOT=""
    if [ -n "$SCRIPT_SOURCE" ] && [ -f "$SCRIPT_SOURCE" ]; then
        local candidate
        candidate="$(cd "$(dirname "$SCRIPT_SOURCE")/.." && pwd)"
        if [ -f "$candidate/pyproject.toml" ] && grep -q "^name = \"$PACKAGE_NAME\"" "$candidate/pyproject.toml"; then
            REPO_ROOT="$candidate"
        fi
    fi

    if [ -n "$REPO_ROOT" ]; then
        log_info "Installing from local checkout: $REPO_ROOT"
    else
        log_info "Installing package: ${MERIDIAN_PACKAGE:-$PACKAGE_NAME}"
    fi
}

ensure_uv() {
    log_step "Checking for uv..."
    if command -v uv &> /dev/null; then
        log_info "uv found: $(uv --version)"
        return
    fi

    log_warn "uv is not installed. Meridian uses it to install and run (https://docs.astral.sh/uv/)."
    if ! ask_yes_no "Install uv now with its official installer (https://astral.sh/uv/install.sh)?" n; then
        log_error "uv is required. Install it, then re-run this script:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi

    if [ "$DRY_RUN" = "1" ]; then
        echo "  [DRY RUN] curl -LsSf https://astral.sh/uv/install.sh | sh"
        return
    fi
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # The uv installer puts uv in ~/.local/bin (or $XDG_BIN_HOME); make it
    # visible to the rest of this run.
    export PATH="${XDG_BIN_HOME:-$HOME/.local/bin}:$HOME/.cargo/bin:$PATH"
    if ! command -v uv &> /dev/null; then
        log_error "uv was installed but isn't on PATH yet. Open a new shell and re-run this script."
        exit 1
    fi
    log_info "uv installed: $(uv --version)"
}

choose_rag() {
    case "$RAG" in
        1) WITH_RAG=1 ;;
        0) WITH_RAG=0 ;;
        *)
            if ask_yes_no "Enable semantic search (installs ~900MB of ML libraries; Meridian works without it)?" n; then
                WITH_RAG=1
            else
                WITH_RAG=0
            fi
            ;;
    esac
}

install_meridian() {
    log_step "Installing the meridian command..."

    local extra=""
    [ "$WITH_RAG" = "1" ] && extra="[rag]"

    # --force: re-running over an existing install upgrades/reinstalls it in
    # place instead of failing on "already installed".
    if [ -n "$REPO_ROOT" ]; then
        run uv tool install --force --editable "${REPO_ROOT}${extra}"
    else
        run uv tool install --force "${MERIDIAN_PACKAGE:-$PACKAGE_NAME}${extra}"
    fi

    if [ "$DRY_RUN" = "1" ]; then
        MERIDIAN_BIN="meridian"
        return
    fi

    MERIDIAN_BIN="$(uv tool dir --bin)/meridian"
    if [ ! -x "$MERIDIAN_BIN" ]; then
        log_error "Install verification failed: $MERIDIAN_BIN was not created."
        exit 1
    fi
    log_info "Installed: $("$MERIDIAN_BIN" version | head -n 1)"

    if ! command -v meridian &> /dev/null; then
        log_warn "$(uv tool dir --bin) is not on your PATH, so 'meridian' won't be found in new shells."
        log_warn "Fix it with: uv tool update-shell"
    fi
}

run_setup() {
    local args=()
    [ "$SEED_KB" = "1" ] && args+=(--seed)
    [ "$SEED_KB" = "0" ] && args+=(--no-seed)
    [ "$SKIP_MCP" = "1" ] && args+=(--no-clients)
    [ "$WITH_RAG" = "1" ] && args+=(--rag)

    log_step "Handing off to meridian setup..."
    echo
    if [ "$DRY_RUN" = "1" ]; then
        echo "  [DRY RUN] meridian setup ${args[*]}"
        return
    fi
    if has_tty; then
        "$MERIDIAN_BIN" setup "${args[@]}" < /dev/tty
    else
        "$MERIDIAN_BIN" setup "${args[@]}"
    fi
}

run_doctor() {
    [ "$DRY_RUN" = "1" ] && return
    echo
    log_step "Checking the installation (meridian doctor)..."
    "$MERIDIAN_BIN" doctor || log_warn "meridian doctor reported problems — see above."
}

print_windows_instructions() {
    cat <<'EOF'
Windows: no script needed. In PowerShell, run:

  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  uv tool install axiom-meridian
  meridian setup

(Or, without a persistent install: uvx --from axiom-meridian meridian setup)
EOF
}

print_usage() {
    cat <<EOF
Meridian Installer (Linux / macOS)

Installs a persistent 'meridian' command with 'uv tool install', then runs
'meridian setup' to configure your MCP clients and knowledge base.

Usage:
  bash scripts/install.sh           # From a clone (installs the clone, editable)
  curl -fsSL URL | bash             # Remote installation (installs from PyPI)

Options:
  RAG=1 / RAG=0          Install with / without semantic search without asking
  SEED_KB=1 / SEED_KB=0  Seed / skip the example knowledge base without asking
  SKIP_MCP=1             Skip MCP client configuration
  KNOWLEDGE_BASE_PATH=/path  Custom knowledge base path
  MERIDIAN_PACKAGE=spec  Package to install when not run from a clone
  DRY_RUN=1              Show what would be done without executing

Examples:
  # Default installation
  bash scripts/install.sh

  # Remote installation
  curl -fsSL https://raw.githubusercontent.com/abeljumanuel/axiom-meridian-project/main/scripts/install.sh | bash

  # Non-interactive, with semantic search and the example knowledge base
  RAG=1 SEED_KB=1 bash scripts/install.sh

  # Dry run (show what would happen)
  DRY_RUN=1 bash scripts/install.sh

After installing:
  meridian doctor     # check the installation
  meridian setup      # re-run client configuration (safe to repeat)

EOF
    print_windows_instructions
    echo
}

main() {
    for arg in "$@"; do
        case "$arg" in
            -h|--help|help)
                print_usage
                exit 0
                ;;
        esac
    done

    echo "════════════════════════════════════════════════"
    echo -e "  ${GREEN}Meridian Installer${NC}"
    echo "════════════════════════════════════════════════"
    echo
    [ "$DRY_RUN" = "1" ] && log_warn "DRY RUN — nothing will be changed"

    detect_os
    detect_source
    ensure_uv
    choose_rag
    install_meridian
    run_setup
    run_doctor
}

main "$@"
