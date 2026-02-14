"""Agent启动自检器

功能：
- Agent启动时自动检查todo_queue.yaml
- 显示未读TODO列表
- 提示按优先级执行
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from .todo_queue_manager import TodoQueueManager, TodoQueueItem

logger = logging.getLogger(__name__)


@dataclass
class StartupCheckResult:
    """启动检查结果"""
    has_unread_todos: bool
    unread_count: int
    todos: List[Dict[str, Any]]
    message: str
    suggestions: List[str]


@dataclass
class StartupConfig:
    """启动检查配置"""
    auto_display: bool = True
    require_confirmation: bool = True
    priority_order: List[str] = None

    def __post_init__(self):
        if self.priority_order is None:
            self.priority_order = ["high", "medium", "low"]


class AgentStartupChecker:
    """Agent启动自检器"""

    def __init__(self, agent_id: str, config: StartupConfig = None):
        """
        初始化启动检查器

        Args:
            agent_id: Agent ID
            config: 配置
        """
        self.agent_id = agent_id
        self.config = config or StartupConfig()
        self.queue_manager = TodoQueueManager()

    def run(self) -> StartupCheckResult:
        """
        执行启动检查

        Returns:
            StartupCheckResult: 检查结果
        """
        try:
            unread = self.queue_manager.get_unread(self.agent_id)

            if not unread:
                return StartupCheckResult(
                    has_unread_todos=False,
                    unread_count=0,
                    todos=[],
                    message="✅ 无未读TODO",
                    suggestions=["继续当前工作"]
                )

            todos = [self._format_todo(t) for t in unread]
            suggestions = self._generate_suggestions(unread)
            priority_counts = self._count_by_priority(unread)
            message = self._generate_message(priority_counts)

            return StartupCheckResult(
                has_unread_todos=True,
                unread_count=len(unread),
                todos=todos,
                message=message,
                suggestions=suggestions
            )

        except Exception as e:
            logger.error(f"启动检查失败: {e}")
            return StartupCheckResult(
                has_unread_todos=False,
                unread_count=0,
                todos=[],
                message=f"❌ 检查失败: {e}",
                suggestions=["手动检查: oc-collab todo list --unread"]
            )

    def _format_todo(self, todo: TodoQueueItem) -> Dict[str, Any]:
        """格式化TODO"""
        priority_icons = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        icon = priority_icons.get(todo.priority, "⚪")

        return {
            "id": todo.id,
            "content": todo.content,
            "priority": todo.priority,
            "priority_icon": icon,
            "from_agent": todo.from_agent,
            "created_at": todo.created_at,
            "age": self._get_age(todo.created_at)
        }

    def _get_age(self, created_at: str) -> str:
        """获取TODO年龄"""
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            now = datetime.now()
            delta = now - created

            if delta.days > 0:
                return f"{delta.days}天前"
            elif delta.seconds > 3600:
                return f"{delta.seconds // 3600}小时前"
            elif delta.seconds > 60:
                return f"{delta.seconds // 60}分钟前"
            else:
                return "刚刚"
        except:
            return "未知"

    def _count_by_priority(self, todos: List[TodoQueueItem]) -> Dict[str, int]:
        """按优先级统计"""
        counts = {"high": 0, "medium": 0, "low": 0}
        for todo in todos:
            counts[todo.priority] = counts.get(todo.priority, 0) + 1
        return counts

    def _generate_message(self, counts: Dict[str, int]) -> str:
        """生成消息"""
        parts = []
        if counts.get("high", 0) > 0:
            parts.append(f"🔴 高优先: {counts['high']}个")
        if counts.get("medium", 0) > 0:
            parts.append(f"🟡 中优先: {counts['medium']}个")
        if counts.get("low", 0) > 0:
            parts.append(f"🟢 低优先: {counts['low']}个")

        return "未读TODO: " + " | ".join(parts)

    def _generate_suggestions(self, todos: List[TodoQueueItem]) -> List[str]:
        """生成建议"""
        suggestions = []

        high_todos = [t for t in todos if t.priority == "high"]
        if high_todos:
            first = high_todos[0]
            suggestions.append(f"建议先处理: {first.id} - {first.content[:30]}...")

        suggestions.append(f"查看全部: oc-collab todo list --unread --agent {self.agent_id[-1]}")
        suggestions.append("全部完成后: oc-collab todo mark-all-read")

        return suggestions

    def display_notifications(self, result: StartupCheckResult):
        """显示通知"""
        print("\n" + "=" * 60)

        if not result.has_unread_todos:
            print(result.message)
            print("=" * 60 + "\n")
            return

        print(f"\n🔔 你有 {result.unread_count} 个未读TODO\n")
        print(result.message)
        print("-" * 60)

        for todo in result.todos:
            print(f"  {todo['priority_icon']} [{todo['id']}] {todo['content']}")
            print(f"     from {todo['from_agent']} · {todo['age']}")

        print("-" * 60)
        print("\n建议:")
        for i, suggestion in enumerate(result.suggestions, 1):
            print(f"  {i}. {suggestion}")

        print("\n" + "=" * 60 + "\n")

    def suggest_action(self, result: StartupCheckResult) -> str:
        """建议action"""
        if not result.has_unread_todos:
            return "continue"

        high_todos = [t for t in result.todos if t["priority"] == "high"]
        if high_todos:
            return f"process_todo:{high_todos[0]['id']}"

        return "review_todos"

    def confirm_action(self) -> bool:
        """确认操作"""
        try:
            response = input("\n是否继续? (y/n): ").strip().lower()
            return response in ["y", "yes", "是", "1"]
        except EOFError:
            return True
