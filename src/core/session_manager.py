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
            try:
                import yaml
                with open(state_file) as f:
                    state = yaml.safe_load(f) or {}
                session_config = state.get("session_start", {})
                self.enabled = session_config.get("enabled", True)
                self.show_responsibilities = session_config.get("show_responsibilities", True)
                self.show_todo = session_config.get("show_todo", True)
                self.show_pending = session_config.get("show_pending", True)
            except Exception:
                pass


class SessionManager:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.state_manager = StateManager(project_path)
        self.config = SessionConfig(project_path)

    def get_project_info(self) -> dict:
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
        agent_config = AGENT_ROLES.get(agent_id, {
            "role": "未知",
            "responsibilities": []
        })

        try:
            state = self.state_manager.load_state()
            agents = state.get("agents", {})
            agent_state = agents.get(agent_id, {})
        except KeyError:
            agent_state = {}
        except Exception:
            agent_state = {}

        return {
            "id": agent_id,
            "role": agent_config["role"],
            "current_task": agent_state.get("current_task", ""),
            "responsibilities": agent_config["responsibilities"]
        }

    def get_responsibilities_text(self, agent_id: str) -> str:
        agent = self.get_agent_info(agent_id)
        if not self.config.show_responsibilities:
            return ""

        lines = ["你的职责:"]
        for resp in agent["responsibilities"]:
            lines.append(f"  - {resp}")
        return "\n".join(lines)

    def get_todo_items(self) -> str:
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
        lines = ["常用命令:"]
        for cmd, desc in COMMON_COMMANDS:
            lines.append(f"  - {cmd}: {desc}")
        return "\n".join(lines)

    def get_welcome_message(self, agent_id: str) -> str:
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
        message = self.get_welcome_message(agent_id)
        if message:
            console.print(Panel(
                Text(message, justify="left"),
                title="会话引导",
                style="blue"
            ))
