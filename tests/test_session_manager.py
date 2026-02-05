import pytest
import tempfile
import os
from pathlib import Path


def test_session_config_defaults():
    from src.core.session_manager import SessionConfig

    with tempfile.TemporaryDirectory() as tmpdir:
        config = SessionConfig(tmpdir)
        assert config.enabled is True
        assert config.show_responsibilities is True
        assert config.show_todo is True
        assert config.show_pending is True


def test_get_agent_info():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(tmpdir)
        info = manager.get_agent_info("agent1")
        assert "role" in info
        assert "responsibilities" in info
        assert "产品经理" in info["role"]


def test_get_welcome_message():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(tmpdir)
        message = manager.get_welcome_message("agent1")
        assert "Agent 1" in message
        assert "当前项目" in message
        assert "当前阶段" in message


def test_welcome_disabled():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "state" / "project_state.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text("session_start:\n  enabled: false\n")

        manager = SessionManager(tmpdir)
        message = manager.get_welcome_message("agent1")
        assert message == ""


def test_common_commands():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(tmpdir)
        message = manager.get_welcome_message("agent2")
        assert "oc-collab status" in message
        assert "oc-collab todo" in message
