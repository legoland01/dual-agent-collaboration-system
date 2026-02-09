"""ConflictDetector: TODO冲突检测器

FR-AI-003: TODO冲突检测
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import yaml


@dataclass
class ConflictResult:
    """冲突检测结果"""
    has_conflict: bool
    conflicts: List[Dict[str, Any]]
    suggestions: List[str]


class ConflictDetector:
    """TODO冲突检测器"""

    CONFLICT_TYPES = {
        "duplicate": "重复内容",
        "priority": "优先级冲突",
        "dependency": "依赖冲突",
        "circular": "循环依赖"
    }

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.todo_file = self.project_path / "state" / "agent_adhoc_todos.yaml"

    def load_todos(self) -> List[Dict[str, Any]]:
        """加载所有TODO"""
        if not self.todo_file.exists():
            return []

        with open(self.todo_file) as f:
            data = yaml.safe_load(f)

        return data.get("adhoc_todos", [])

    def detect_duplicate(self, content: str, todos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检测重复内容

        Args:
            content: 新TODO内容
            todos: 现有TODO列表

        Returns:
            重复列表
        """
        duplicates = []
        content_lower = content.lower()

        for todo in todos:
            if todo.get("status") in ["completed", "cancelled"]:
                continue

            todo_content = todo.get("content", "").lower()
            if content_lower == todo_content:
                duplicates.append({
                    "type": "duplicate",
                    "todo_id": todo.get("id"),
                    "content": todo.get("content"),
                    "message": f"与现有TODO重复: {todo.get('id')}"
                })

        return duplicates

    def detect_priority_conflict(self, priority: str,
                                 todos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检测优先级冲突

        Args:
            priority: 新TODO优先级
            todos: 现有TODO列表

        Returns:
            冲突列表
        """
        conflicts = []

        # 检查是否有大量相同优先级的未完成任务
        priority_count = sum(
            1 for t in todos
            if t.get("priority") == priority
            and t.get("status") not in ["completed", "cancelled"]
        )

        if priority_count >= 5:
            conflicts.append({
                "type": "priority",
                "message": f"当前有{priority_count}个相同优先级({priority})的未完成任务"
            })

        return conflicts

    def detect_all(self, content: str, priority: str,
                   agent_id: Optional[str]) -> ConflictResult:
        """
        完整冲突检测

        Args:
            content: 新TODO内容
            priority: 优先级
            agent_id: Agent编号

        Returns:
            ConflictResult 对象
        """
        todos = self.load_todos()

        all_conflicts = []

        # 检测重复
        duplicates = self.detect_duplicate(content, todos)
        all_conflicts.extend(duplicates)

        # 检测优先级冲突
        priority_conflicts = self.detect_priority_conflict(priority, todos)
        all_conflicts.extend(priority_conflicts)

        # 生成建议
        suggestions = []
        if all_conflicts:
            suggestions.append("建议检查现有TODO，避免重复创建")
            if agent_id:
                suggestions.append(f"可以分配给 Agent {agent_id} 执行")

        return ConflictResult(
            has_conflict=len(all_conflicts) > 0,
            conflicts=all_conflicts,
            suggestions=suggestions
        )
