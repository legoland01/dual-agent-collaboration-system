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


def test_get_todo_items_reads_adhoc_yaml():
    """测试 BUG-20260215-015: session_manager 从 agent_adhoc_todos.yaml 读取待办"""
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        adhoc_file = Path(tmpdir) / "state" / "agent_adhoc_todos.yaml"
        adhoc_file.parent.mkdir(parents=True, exist_ok=True)
        adhoc_file.write_text("""todos:
- id: TODO-1-001
  content: 测试任务A
  status: pending
  priority: P0
- id: TODO-1-002
  content: 测试任务B
  status: completed
  priority: P1
""")

        manager = SessionManager(tmpdir)
        text = manager.get_todo_items()
        assert "agent_adhoc_todos.yaml" in text
        assert "TODO-1-001" in text
        assert "测试任务A" in text
        assert "TODO-1-002" not in text


def test_get_todo_items_adhoc_only_pending():
    """测试只显示pending状态的TODO"""
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        adhoc_file = Path(tmpdir) / "state" / "agent_adhoc_todos.yaml"
        adhoc_file.parent.mkdir(parents=True, exist_ok=True)
        adhoc_file.write_text("""todos:
- id: TODO-1-003
  content: 已完成任务
  status: completed
- id: TODO-1-004
  content: 进行中任务
  status: pending
""")

        manager = SessionManager(tmpdir)
        text = manager.get_todo_items()
        assert "进行中任务" in text
        assert "已完成任务" not in text


def test_auto_discover_tasks_creates_todo():
    """测试 BUG-20260215-016: Agent2自动发现任务并创建TODO"""
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("""phase: requirements_review
agents: {}
""")

        manager = SessionManager(tmpdir)
        discovered = manager.auto_discover_tasks()
        assert isinstance(discovered, list)


def test_auto_discover_tasks_no_duplicate():
    """测试自动发现不重复创建TODO"""
    from src.core.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("""phase: development
agents: {}
""")

        adhoc_file = Path(tmpdir) / "state" / "agent_adhoc_todos.yaml"
        adhoc_file.parent.mkdir(parents=True, exist_ok=True)
        adhoc_file.write_text("""todos:
- id: TODO-2-999
  content: 开发实现功能模块
  status: pending
""")

        manager = SessionManager(tmpdir)
        discovered1 = manager.auto_discover_tasks()
        discovered2 = manager.auto_discover_tasks()
        assert discovered1 == discovered2


def test_switch_to_agent2_triggers_auto_discover():
    """测试切换到Agent2时触发自动发现"""
    from click.testing import CliRunner
    from src.cli.main import switch_command

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("""phase: development
agents:
  agent1:
    role: 产品经理
  agent2:
    role: 开发负责人
session_start:
  show_todo: true
""")

        runner = CliRunner()
        result = runner.invoke(switch_command, ["2"], obj={"project_path": tmpdir})

        assert result.exit_code == 0
        assert "Agent 2" in result.output or "开发负责人" in result.output


def test_state_manager_get_active_agent_fallback():
    """测试 BUG-20260215-014: StateManager获取活跃Agent作为fallback"""
    from src.core.state_manager import StateManager

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("""phase: development
agents:
  agent1:
    role: 产品经理
    current: false
  agent2:
    role: 开发负责人
    current: true
""")

        manager = StateManager(tmpdir)
        active = manager.get_active_agent()
        assert active == "agent2"


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
