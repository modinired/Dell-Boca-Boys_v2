"""
Unit tests for the Dell Boca Vista Boys agent.

These tests exercise the high‑level methods of ``DellBocaAgent`` to
ensure they return well‑formed data structures even when no language
models are available.  They do not attempt to contact external
services and should pass in an isolated environment.
"""

import os
from pathlib import Path

import pytest

from web_dashboard.agents import DellBocaAgent


def test_chat_without_models(tmp_path, monkeypatch):
    """Agent.chat returns a fallback response when models are unavailable."""
    # Use a temporary directory for the database to avoid clobbering user data
    monkeypatch.setenv("DB_BASE_DIR", str(tmp_path))
    agent = DellBocaAgent()
    # Simulate models not available
    agent.ollama_available = False
    agent.gemini_available = False
    result = agent.chat("hello")
    assert isinstance(result, dict)
    assert 'response' in result
    assert result['model_used'] == 'none'
    assert 'unavailable' in result['response'].lower()


def test_generate_workflow_fallback(tmp_path, monkeypatch):
    """Agent.generate_workflow returns fallback data when no models are configured."""
    monkeypatch.setenv("DB_BASE_DIR", str(tmp_path))
    agent = DellBocaAgent()
    agent.ollama_available = False
    agent.gemini_available = False
    output = agent.generate_workflow("Test the system")
    # Ensure keys are present
    for key in ['description', 'diagram', 'workflow', 'code_explanations', 'agent_collaboration', 'metrics']:
        assert key in output
    # Should fallback to empty nodes
    assert output['workflow'].get('nodes') == []
    assert output['workflow'].get('connections') == []
    # Metrics should reflect zero complexity
    assert output['metrics']['node_count'] == 0