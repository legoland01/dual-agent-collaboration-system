# 详细设计：session_start 功能

**设计文档ID**: DETAIL-2026-02-001
**需求ID**: BUG-20260203-001
**创建日期**: 2026-02-05

---

## 1. 设计概述

实现 Agent 会话起始引导功能，在 Agent 切换或状态查看时自动显示欢迎信息和上下文。

### 1.1 组件架构

```
src/
├── cli/
│   └── main.py           # 修改 switch, status 命令
└── core/
    └── session_manager.py # 新建会话管理器
state/
├── project_state.yaml     # 添加 session_start 配置
└── memory/
    └── pending.yaml       # 遗留问题（已存在）
```

### 1.2 类设计

```python
class SessionManager:
    """会话管理器"""
    - project_path: str
    - state_manager: StateManager
    - config: SessionConfig

    + get_welcome_message(agent_id: str) -> str
    + get_responsibilities(agent_id: str) -> List[str]
    + get_todo_items() -> List[str]
    + get_pending_issues() -> List[str]
    + show_welcome(agent_id: str) -> None
```

---

## 2. 核心实现

### 2.1 SessionManager 类

```python
# src/core/session_manager.py
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .state_manager import StateManager

console = Console()

AGENT_ROLES = {
    "agent1": {
        "role": "产品经理",
        "responsibilities": [
            "编写和评审需求文档",
            "定义验收标准",
            "签署需求确认",
            "评审设计文档",
            "评审测试报告"
        ]
    },
    "agent2": {
        "role": "开发负责人",
        "responsibilities": [
            "评审需求文档",
            "编写详细设计",
            "代码实现",
            "编写单元测试",
            "签署技术确认"
        ]
    }
}

COMMON_COMMANDS = [
    ("oc-collab status", "查看项目状态"),
    ("oc-collab todo", "查看待办事项"),
    ("oc-collab review", "评审文档"),
    ("oc-collab signoff", "签署确认"),
    ("oc-collab history", "查看协作历史"),
    ("oc-collab switch <1|2>", "切换Agent角色")
]


class SessionConfig:
    """会话配置"""
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.enabled = True
        self.show_responsibilities = True
        self.show_todo = True
        self.show_pending = True
        self.load_config()

    def load_config(self):
        state_file = Path(self.project_path) / "state" / "project_state.yaml"
        if state_file.exists():
            import yaml
            with open(state_file) as f:
                state = yaml.safe_load(f) or {}
            session_config = state.get("session_start", {})
            self.enabled = session_config.get("enabled", True)
            self.show_responsibilities = session_config.get("show_responsibilities", True)
            self.show_todo = session_config.get("show_todo", True)
            self.show_pending = session_config.get("show_pending", True)


class SessionManager:
    """会话管理器 - 管理 Agent 会话起始引导"""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.state_manager = StateManager(project_path)
        self.config = SessionConfig(project_path)

    def get_project_info(self) -> dict:
        """获取项目信息"""
        try:
            state = self.state_manager.load_state()
            metadata = state.get("metadata", {})
            project_info = state.get("project", {})

            return {
                "name": metadata.get("project_name") or project_info.get("name", "未配置"),
                "phase": project_info.get("phase") or state.get("phase", "未知"),
                "milestone": state.get("current_milestone", "待定义")
            }
        except Exception:
            return {"name": "未配置", "phase": "未知", "milestone": "待定义"}

    def get_agent_info(self, agent_id: str) -> dict:
        """获取 Agent 信息"""
        agent_config = AGENT_ROLES.get(agent_id, {
            "role": "未知",
            "responsibilities": []
        })

        state = self.state_manager.load_state()
        agents = state.get("agents", {})
        agent_state = agents.get(agent_id, {})

        return {
            "id": agent_id,
            "role": agent_config["role"],
            "current_task": agent_state.get("current_task", ""),
            "responsibilities": agent_config["responsibilities"]
        }

    def get_responsibilities_text(self, agent_id: str) -> str:
        """获取职责文本"""
        agent = self.get_agent_info(agent_id)
        if not self.config.show_responsibilities:
            return ""

        lines = ["你的职责:"]
        for resp in agent["responsibilities"]:
            lines.append(f"  - {resp}")
        return "\n".join(lines)

    def get_todo_items(self) -> str:
        """获取待办事项"""
        if not self.config.show_todo:
            return ""

        try:
            from .auto_engine import TodoCommandExecutor
            executor = TodoCommandExecutor(self.project_path)
            todo_list = executor.get_todo_list()

            if not todo_list:
                return "待办事项:\n  暂无待办事项"

            lines = ["待办事项:"]
            for item in todo_list[:5]:
                task = item.get("task", "")
                lines.append(f"  [ ] {task}")
            return "\n".join(lines)
        except Exception:
            return "待办事项:\n  暂无待办事项"

    def get_pending_issues(self) -> str:
        """获取遗留问题"""
        if not self.config.show_pending:
            return ""

        pending_file = Path(self.project_path) / "state" / "memory" / "pending.yaml"
        if not pending_file.exists():
            return "上次会话遗留:\n  无遗留问题"

        try:
            import yaml
            with open(pending_file) as f:
                pending = yaml.safe_load(f) or []

            if not pending:
                return "上次会话遗留:\n  无遗留问题"

            lines = ["上次会话遗留:"]
            for item in pending[:5]:
                desc = item.get("description", item)
                lines.append(f"  - {desc}")
            return "\n".join(lines)
        except Exception:
            return "上次会话遗留:\n  无遗留问题"

    def get_common_commands(self) -> str:
        """获取常用命令"""
        lines = ["常用命令:"]
        for cmd, desc in COMMON_COMMANDS:
            lines.append(f"  - {cmd}: {desc}")
        return "\n".join(lines)

    def get_welcome_message(self, agent_id: str) -> str:
        """生成欢迎信息"""
        if not self.config.enabled:
            return ""

        project = self.get_project_info()
        agent = self.get_agent_info(agent_id)

        parts = [
            f"=== Agent {agent_id.replace('agent', '')} ({agent['role']}) ===",
            "",
            f"当前项目: {project['name']}",
            f"当前阶段: {project['phase']}",
            f"当前里程碑: {project['milestone']}",
            ""
        ]

        resp_text = self.get_responsibilities_text(agent_id)
        if resp_text:
            parts.append(resp_text)
            parts.append("")

        todo_text = self.get_todo_items()
        if todo_text:
            parts.append(todo_text)
            parts.append("")

        pending_text = self.get_pending_issues()
        if pending_text:
            parts.append(pending_text)
            parts.append("")

        parts.append(self.get_common_commands())

        return "\n".join(parts)

    def show_welcome(self, agent_id: str):
        """显示欢迎信息"""
        message = self.get_welcome_message(agent_id)
        if message:
            console.print(Panel(
                Text(message, justify="left"),
                title="会话引导",
                style="blue"
            ))
```

### 2.2 CLI 集成

修改 `src/cli/main.py`:

```python
# 在文件开头添加
from ..core.session_manager import SessionManager


# 修改 switch_command 函数
@main.command("switch")
@click.argument("agent_id", type=click.IntRange(1, 2))
@click.option("--welcome/--no-welcome", "-w", default=True, help="显示欢迎信息")
def switch_command(agent_id: int, welcome: bool):
    """切换Agent角色。"""
    try:
        project_path = get_project_path()
        state_manager = StateManager(project_path)

        current_agent = state_manager.get_active_agent()
        if current_agent == f"agent{agent_id}":
            click.echo(f"已经是 Agent {agent_id}")
            return

        state_manager.set_active_agent(f"agent{agent_id}")

        agent_info = state_manager.load_state()["agents"][f"agent{agent_id}"]

        if welcome:
            session_manager = SessionManager(project_path)
            session_manager.show_welcome(f"agent{agent_id}")
        else:
            click.echo(f"已切换到 Agent {agent_id} ({agent_info['role']})")

    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


# 修改 status_command 函数 - 在末尾添加欢迎信息
@main.command("status")
def status_command():
    """查看当前协作状态。"""
    try:
        # ... 现有代码 ...

        # 添加会话引导
        active_agent = state_manager.get_active_agent()
        session_manager = SessionManager(project_path)
        session_manager.show_welcome(active_agent)

    except StateFileNotFoundError:
        click.echo("错误: 未找到项目状态文件，请先初始化项目")
        sys.exit(1)
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)
```

### 2.3 项目状态配置

更新 `state/project_state.yaml`:

```yaml
session_start:
  enabled: true
  show_responsibilities: true
  show_todo: true
  show_pending: true
```

---

## 3. 测试用例

### 3.1 单元测试

```python
# tests/test_session_manager.py
import pytest
from pathlib import Path
from src.core.session_manager import SessionManager, SessionConfig


def test_session_config_defaults():
    """测试默认配置"""
    config = SessionConfig("/tmp/test_project")
    assert config.enabled is True
    assert config.show_responsibilities is True


def test_get_agent_info():
    """测试获取 Agent 信息"""
    manager = SessionManager("/tmp/test_project")
    info = manager.get_agent_info("agent1")
    assert "role" in info
    assert "responsibilities" in info


def test_get_welcome_message():
    """测试欢迎信息生成"""
    manager = SessionManager("/tmp/test_project")
    message = manager.get_welcome_message("agent1")
    assert "Agent 1" in message
    assert "当前项目" in message
```

---

## 4. 验收验证

| 验证项 | 验证命令 | 预期输出 |
|--------|----------|----------|
| Agent 切换显示欢迎 | `oc-collab switch 2` | 包含 Agent 信息、职责、待办 |
| 隐藏欢迎信息 | `oc-collab switch 2 --no-welcome` | 仅显示切换确认 |
| 状态命令集成 | `oc-collab status` | 在状态表格后显示欢迎信息 |
| 配置文件生效 | 修改 enabled=false | 不显示欢迎信息 |

---

**设计版本**: v1
**创建日期**: 2026-02-05
**状态**: 待实现
