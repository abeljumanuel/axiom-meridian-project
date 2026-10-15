# SPDX-FileCopyrightText: 2026 Juan Manuel Rojas González (Axiom JUMA)
# SPDX-License-Identifier: Apache-2.0
"""Detect whether the optional `rag` extra is installed, without importing it."""

from __future__ import annotations

from importlib.util import find_spec

_RAG_MODULES = ("sentence_transformers", "torch", "chromadb")

INSTALL_HINT = (
    "Semantic search requires the 'rag' extra. "
    'Install with: uv tool install "axiom-meridian[rag]" '
    '(uvx: uvx --from "axiom-meridian[rag]" meridian mcp; '
    'pip: pip install "axiom-meridian[rag]")'
)


def rag_installed() -> bool:
    """Return True when every RAG library is importable.

    Uses find_spec, not import: importing torch costs several seconds, and
    warm_up_in_background() calls this on the main thread at startup — an
    import here would move the exact cost warm-up exists to hide back onto
    the startup path.
    """
    for name in _RAG_MODULES:
        try:
            if find_spec(name) is None:
                return False
        except ValueError:
            # find_spec raises ValueError when sys.modules[name] is None
            # (an explicitly blocked import) — treat it as absent.
            return False
    return True


class RagNotInstalledError(Exception):
    """Raised by a code path that strictly requires the `rag` extra."""

    def __init__(self) -> None:
        super().__init__(INSTALL_HINT)

    def to_response(self) -> dict:
        return {"error": "RAG_NOT_INSTALLED", "message": INSTALL_HINT}
