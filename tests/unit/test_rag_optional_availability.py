"""Unit tests for meridian.rag.availability and the embedder warm-up guard."""

from __future__ import annotations

import logging
import sys
import threading

import pytest

from meridian.rag import embedder as embedder_module
from meridian.rag.availability import RagNotInstalledError, rag_installed

_RAG_MODULES = ("sentence_transformers", "torch", "chromadb")


@pytest.fixture
def no_rag(monkeypatch):
    """Simulate an environment without the `rag` extra installed."""
    for name in _RAG_MODULES:
        monkeypatch.setitem(sys.modules, name, None)


@pytest.mark.parametrize("missing", _RAG_MODULES)
def test_rag_installed_false_when_any_module_missing(monkeypatch, missing):
    monkeypatch.setitem(sys.modules, missing, None)
    assert rag_installed() is False


def test_rag_installed_true_when_all_modules_present():
    pytest.importorskip("chromadb")
    pytest.importorskip("sentence_transformers")
    assert rag_installed() is True


def test_rag_installed_does_not_import_torch(monkeypatch):
    monkeypatch.delitem(sys.modules, "torch", raising=False)
    rag_installed()
    assert "torch" not in sys.modules


def test_rag_not_installed_error_response_shape():
    response = RagNotInstalledError().to_response()
    assert response["error"] == "RAG_NOT_INSTALLED"
    assert 'pip install "axiom-meridian[rag]"' in response["message"]


def test_warm_up_is_noop_without_rag(no_rag, monkeypatch, caplog):
    started: list[threading.Thread] = []
    monkeypatch.setattr(threading.Thread, "start", lambda self: started.append(self))

    with caplog.at_level(logging.INFO, logger=embedder_module.__name__):
        embedder_module.warm_up_in_background()  # must not raise

    assert started == []
    assert any(
        r.levelno == logging.INFO and "RAG extra not installed" in r.getMessage()
        for r in caplog.records
    )
