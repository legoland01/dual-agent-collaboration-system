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


def test_session_config_with_state_file():
    from src.core.session_manager import SessionConfig

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("session_start:\n  enabled: false\n  show_responsibilities: false\n  show_todo: true\n  show_pending: true\n")

        config = SessionConfig(tmpdir)
        assert config.enabled is False
        assert config.show_responsibilities is False


def test_session_config_exception_handling():
    from src.core.session_manager import SessionConfig

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("invalid: yaml: [[[")

        config = SessionConfig(tmpdir)
        assert config.enabled is True


def test_get_agent_info():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(tmpdir)
        info = manager.get_agent_info("agent1")
        assert "role" in info
        assert "responsibilities" in info
        assert "产品经理" in info["role"]


def test_get_agent_info_with_state():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(tmpdir)
        info = manager.get_agent_info("agent1")
        assert info["role"] == "产品经理"


def test_get_agent_info_unknown_agent():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(tmpdir)
        info = manager.get_agent_info("unknown_agent")
        assert info["role"] == "未知"


def test_get_project_info():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(tmpdir)
        info = manager.get_project_info()
        assert "name" in info
        assert "phase" in info
        assert "milestone" in info


def test_get_project_info_with_metadata():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("metadata:\n  project_name: TestProject\nproject:\n  phase: development\n")

        manager = SessionManager(tmpdir)
        info = manager.get_project_info()
        assert info["name"] == "TestProject"
        assert info["phase"] == "development"


def test_get_responsibilities_text():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(tmpdir)
        text = manager.get_responsibilities_text("agent1")
        assert "你的职责:" in text
        assert "编写和评审需求文档" in text
        assert "定义验收标准" in text


def test_get_responsibilities_hidden():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("session_start:\n  show_responsibilities: false\n")

        manager = SessionManager(tmpdir)
        text = manager.get_responsibilities_text("agent1")
        assert text == ""


def test_get_todo_items_empty():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(tmpdir)
        text = manager.get_todo_items()
        assert "待办事项:" in text
        assert "暂无" in text


def test_get_todo_items_with_content():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("session_start:\n  show_todo: true\n")

        manager = SessionManager(tmpdir)
        text = manager.get_todo_items()
        assert "待办事项:" in text


def test_get_todo_items_hidden():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("session_start:\n  show_todo: false\n")

        manager = SessionManager(tmpdir)
        text = manager.get_todo_items()
        assert text == ""


def test_get_pending_issues_empty():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(tmpdir)
        text = manager.get_pending_issues()
        assert "上次会话遗留:" in text
        assert "无遗留问题" in text


def test_get_pending_issues_with_content():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("session_start:\n  show_pending: true\n")

        pending_file = Path(tmpdir) / "state" / "memory" / "pending.yaml"
        pending_file.parent.mkdir(parents=True, exist_ok=True)
        pending_file.write_text("- description: Bug BUG-001 pending\n")

        manager = SessionManager(tmpdir)
        text = manager.get_pending_issues()
        assert "上次会话遗留:" in text
        assert "Bug BUG-001 pending" in text


def test_get_pending_issues_hidden():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("session_start:\n  show_pending: false\n")

        manager = SessionManager(tmpdir)
        text = manager.get_pending_issues()
        assert text == ""


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


def test_get_common_commands():
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(tmpdir)
        text = manager.get_common_commands()
        assert "常用命令:" in text
        assert "oc-collab status" in text
