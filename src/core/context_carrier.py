"""ContextCarrier: TODO上下文携带器

FR-AI-002: TODO上下文携带
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import yaml


@dataclass
class TodoContext:
    """TODO上下文"""
    todo_id: str
    content: str
    created_at: str
    agent_id: Optional[str]
    priority: str
    history: List[str] = field(default_factory=list)
    related_todos: List[str] = field(default_factory=list)


class ContextCarrier:
    """TODO上下文携带器"""

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.db_path = str(self.project_path / "state" / "todos.db")
        self.state_file = self.project_path / "state" / "project_state.yaml"

    def load_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """加载历史TODO记录"""
        try:
            from .todo_storage import TodoStorage
            storage = TodoStorage(self.db_path)
            todos = storage.list(status="completed")
            return todos[-limit:]
        except Exception:
            return []

    def generate_context_summary(self, new_todo_content: str) -> str:
        """
        生成上下文摘要

        Args:
            new_todo_content: 新TODO内容

        Returns:
            上下文摘要字符串
        """
        history = self.load_history(limit=5)

        if not history:
            return f"📋 新任务: {new_todo_content}\n   (暂无历史任务)"

        summary_lines = [f"📋 新任务: {new_todo_content}"]

        if history:
            summary_lines.append("   📜 历史任务:")
            for h in reversed(history):
                content = h.get("content", "")[:50]
                status = h.get("status", "")
                summary_lines.append(f"      • [{status}] {content}")

        return "\n".join(summary_lines)

    def get_version_info(self) -> Dict[str, str]:
        """
        获取版本信息

        Returns:
            版本信息字典
        """
        if not self.state_file.exists():
            return {"version": "unknown"}

        with open(self.state_file) as f:
            state = yaml.safe_load(f)

        return {
            "version": state.get("v2.2.5", {}).get("deployment", {}).get("version", "unknown"),
            "phase": state.get("current_phase", "unknown")
        }

    def build_context(self, todo_id: str, content: str,
                      agent_id: Optional[str], priority: str) -> TodoContext:
        """
        构建完整上下文

        Args:
            todo_id: TODO ID
            content: TODO内容
            agent_id: Agent编号
            priority: 优先级

        Returns:
            TodoContext 对象
        """
        history = self.load_history(limit=5)
        history_ids = [h.get("id") for h in history]

        version_info = self.get_version_info()

        return TodoContext(
            todo_id=todo_id,
            content=content,
            created_at=datetime.now().isoformat(),
            agent_id=agent_id,
            priority=priority,
            history=history_ids,
            related_todos=[]
        )
