# 详细设计说明书：oc-collab v2.2.10

**版本**: v1
**创建日期**: 2026-02-14
**作者**: Agent 2 (开发负责人)
**关联概要设计**: OUTLINE_v2.2.10.md
**版本号**: v2.2.10
**状态**: DRAFT → READY

---

## 1. 功能模块映射

### 1.1 映射表

| 功能模块 (概要设计) | 技术模块 (详细设计) | 对应文件 |
|---------------------|---------------------|----------|
| M1: TodoQueueManager | TodoQueueManager | src/core/todo_queue_manager.py |
| M2: StateNotifier写入队列 | StateNotifier (增强) | src/core/state_notifier.py |
| M3: Agent启动自检 | AgentStartupChecker | src/core/agent_startup_checker.py |
| M3: Agent启动自检 | startup_check命令 | src/cli/startup_commands.py |
| M4: CLI todo --unread | todo list命令(增强) | src/cli/todo_commands.py |
| M5: BUG-001修复 | DeployDocSync (增强) | src/core/deploy_doc_sync.py |
| M6: BUG-002修复 | Skill更新 | skills/oc_collab_collaboration_guide/content.md |

### 1.2 新增/变更文件

| 文件路径 | 功能 | 工时 |
|----------|------|------|
| src/core/todo_queue_manager.py | TODO消息队列管理器 | 2h |
| src/core/agent_startup_checker.py | Agent启动自检器 | 4h |
| src/cli/startup_commands.py | startup-check命令 | 1h |
| src/cli/todo_commands.py | todo list --unread增强 | 1h |
| src/core/state_notifier.py | 写入队列功能增强 | 1h |
| src/core/deploy_doc_sync.py | 文档完整性检查增强 | 2h |
| skills更新 | 协作规则澄清 | 2h |

---

## 2. 技术架构

### 2.1 模块架构图

```
v2.2.10 详细架构

┌─────────────────────────────────────────────────────────────────┐
│                        CLI Layer                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────────────────────┐   │
│  │ oc-collab startup │  │ oc-collab todo list              │   │
│  │ -check           │  │  |--unread                       │   │
│  │                  │  │  |--agent 1|2                    │   │
│  │ → AgentStartup   │  │  |--json                         │   │
│  │   Checker        │  │                                  │   │
│  └──────────────────┘  └──────────────────────────────────┘   │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                        Core Layer                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    TodoQueueManager                      │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │ add() / get_unread() / mark_read() / cleanup()│    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              AgentStartupChecker                        │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │ run() / display_notifications() / suggest()    │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 StateNotifier (增强)                     │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │ _write_to_queue()                               │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                        State Layer                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  state/todo_queue.yaml        ← 新增                             │
│  state/webhook_stats.yaml     ← 已有，增强                       │
│  state/project_state.yaml    ← 已有，更新                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 技术选型

| 模块 | 技术/库 | 版本 | 选型依据 |
|------|---------|------|----------|
| CLI框架 | Click | >=8.0 | 现有技术栈 |
| YAML解析 | PyYAML | >=6.0 | 现有依赖 |
| 数据类 | dataclasses | Python 3.7+ | 轻量级 |
| 文件锁 | filelock | >=3.0 | 防止并发写入 |

---

## 3. 核心模块设计

### 3.1 TodoQueueManager 详细设计

```python
# src/core/todo_queue_manager.py

"""
TODO消息队列管理器

功能：
- 管理Agent间TODO通知的本地队列
- 支持按发送者分组存储未读TODO
- 支持标记已读/未读状态
- 自动清理过期TODO
"""

import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
import logging
from filelock import FileLock

logger = logging.getLogger(__name__)


@dataclass
class TodoQueueItem:
    """TODO队列项"""
    id: str
    content: str
    from_agent: str
    to_agent: str
    priority: str  # high, medium, low
    created_at: str
    read: bool = False
    read_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TodoQueueItem':
        return cls(**data)


@dataclass
class TodoQueueStats:
    """队列统计信息"""
    total: int
    unread: int
    by_agent: Dict[str, int]
    by_priority: Dict[str, int]
    last_updated: str


class TodoQueueManager:
    """TODO消息队列管理器"""

    QUEUE_FILE = "state/todo_queue.yaml"
    LOCK_FILE = "state/todo_queue.lock"
    LOCK_TIMEOUT = 10  # 秒
    CLEANUP_DAYS = 7  # 默认清理7天前的已读项

    def __init__(self, queue_file: str = None, lock_timeout: int = None):
        """
        初始化队列管理器

        Args:
            queue_file: 队列文件路径
            lock_timeout: 锁超时时间(秒)
        """
        self.queue_file = Path(queue_file) if queue_file else Path(self.QUEUE_FILE)
        self.lock_file = Path(str(self.queue_file) + ".lock")
        self.lock = FileLock(self.lock_file, timeout=lock_timeout or self.LOCK_TIMEOUT)
        self.lock_timeout = lock_timeout or self.LOCK_TIMEOUT

    def _load_queue(self) -> Dict[str, Any]:
        """
        加载队列数据

        Returns:
            队列数据字典
        """
        if not self.queue_file.exists():
            return {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "stats": {
                    "total": 0,
                    "unread": 0,
                    "by_agent": {"agent1": 0, "agent2": 0},
                    "by_priority": {"high": 0, "medium": 0, "low": 0}
                },
                "todos": []
            }

        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {
                    "version": "1.0",
                    "last_updated": datetime.now().isoformat(),
                    "stats": self._init_stats(),
                    "todos": []
                }
        except Exception as e:
            logger.error(f"加载队列文件失败: {e}")
            return {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "stats": self._init_stats(),
                "todos": []
            }

    def _save_queue(self, data: Dict[str, Any]):
        """
        保存队列数据

        Args:
            data: 队列数据
        """
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        data["last_updated"] = datetime.now().isoformat()
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    def _init_stats(self) -> Dict[str, Any]:
        """初始化统计信息"""
        return {
            "total": 0,
            "unread": 0,
            "by_agent": {"agent1": 0, "agent2": 0},
            "by_priority": {"high": 0, "medium": 0, "low": 0}
        }

    def _recalculate_stats(self, todos: List[Dict]) -> Dict[str, Any]:
        """
        重新计算统计信息

        Args:
            todos: TODO列表

        Returns:
            统计信息字典
        """
        stats = self._init_stats()
        stats["total"] = len(todos)

        for todo in todos:
            if not todo.get("read", False):
                stats["unread"] += 1

            agent = todo.get("to_agent", "unknown")
            if agent in stats["by_agent"]:
                stats["by_agent"][agent] += 1

            priority = todo.get("priority", "medium")
            if priority in stats["by_priority"]:
                stats["by_priority"][priority] += 1

        return stats

    def add(self, item: TodoQueueItem) -> bool:
        """
        添加TODO到队列

        Args:
            item: TODO队列项

        Returns:
            True: 添加成功
            False: 已存在相同的TODO
        """
        try:
            with self.lock:
                data = self._load_queue()
                todos = data.get("todos", [])

                # 检查是否已存在
                for todo in todos:
                    if todo.get("id") == item.id:
                        logger.debug(f"TODO已存在，跳过: {item.id}")
                        return False

                # 添加新TODO
                new_todo = item.to_dict()
                todos.append(new_todo)
                data["todos"] = todos

                # 更新统计
                data["stats"] = self._recalculate_stats(todos)

                self._save_queue(data)
                logger.info(f"TODO已添加到队列: {item.id}")
                return True

        except Exception as e:
            logger.error(f"添加TODO到队列失败: {e}")
            return False

    def get_unread(self, agent_id: str = None, priority: str = None) -> List[TodoQueueItem]:
        """
        获取未读TODO

        Args:
            agent_id: 可选，指定接收者筛选
            priority: 可选，指定优先级筛选

        Returns:
            未读TODO列表（按优先级和时间排序）
        """
        try:
            data = self._load_queue()
            todos = data.get("todos", [])

            result = []
            for todo_data in todos:
                if todo_data.get("read", False):
                    continue

                # 筛选接收者
                if agent_id and todo_data.get("to_agent") != agent_id:
                    continue

                # 筛选优先级
                if priority and todo_data.get("priority") != priority:
                    continue

                result.append(TodoQueueItem.from_dict(todo_data))

            # 按优先级和时间排序（高优先级的在前，相同优先级按时间倒序）
            priority_order = {"high": 0, "medium": 1, "low": 2}
            result.sort(key=lambda x: (priority_order.get(x.priority, 3), -x.created_at))

            return result

        except Exception as e:
            logger.error(f"获取未读TODO失败: {e}")
            return []

    def get_all(self, agent_id: str = None) -> List[TodoQueueItem]:
        """
        获取所有TODO

        Args:
            agent_id: 可选，指定接收者筛选

        Returns:
            TODO列表（按时间倒序）
        """
        try:
            data = self._load_queue()
            todos = data.get("todos", [])

            if agent_id:
                todos = [t for t in todos if t.get("to_agent") == agent_id]

            # 按时间倒序
            todos.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            return [TodoQueueItem.from_dict(t) for t in todos]

        except Exception as e:
            logger.error(f"获取所有TODO失败: {e}")
            return []

    def mark_read(self, todo_id: str, agent_id: str = None) -> bool:
        """
        标记TODO为已读

        Args:
            todo_id: TODO ID
            agent_id: 可选，验证接收者

        Returns:
            True: 标记成功
            False: TODO不存在
        """
        try:
            with self.lock:
                data = self._load_queue()
                todos = data.get("todos", [])

                for i, todo in enumerate(todos):
                    if todo.get("id") != todo_id:
                        continue

                    # 验证接收者
                    if agent_id and todo.get("to_agent") != agent_id:
                        logger.warning(f"TODO接收者不匹配: {todo_id}")
                        return False

                    # 标记为已读
                    todos[i]["read"] = True
                    todos[i]["read_at"] = datetime.now().isoformat()
                    data["todos"] = todos
                    data["stats"] = self._recalculate_stats(todos)

                    self._save_queue(data)
                    logger.info(f"TODO已标记为已读: {todo_id}")
                    return True

                logger.warning(f"TODO不存在: {todo_id}")
                return False

        except Exception as e:
            logger.error(f"标记TODO已读失败: {e}")
            return False

    def mark_all_read(self, agent_id: str = None) -> int:
        """
        标记所有TODO为已读

        Args:
            agent_id: 可选，仅标记该接收者的TODO

        Returns:
            标记数量
        """
        try:
            with self.lock:
                data = self._load_queue()
                todos = data.get("todos", [])
                now = datetime.now().isoformat()

                count = 0
                for i, todo in enumerate(todos):
                    if todo.get("read", False):
                        continue

                    if agent_id and todo.get("to_agent") != agent_id:
                        continue

                    todos[i]["read"] = True
                    todos[i]["read_at"] = now
                    count += 1

                if count > 0:
                    data["todos"] = todos
                    data["stats"] = self._recalculate_stats(todos)
                    self._save_queue(data)

                logger.info(f"已标记{count}个TODO为已读")
                return count

        except Exception as e:
            logger.error(f"标记所有TODO已读失败: {e}")
            return 0

    def get_stats(self, agent_id: str = None) -> TodoQueueStats:
        """
        获取队列统计

        Args:
            agent_id: 可选，指定接收者

        Returns:
            统计信息
        """
        try:
            data = self._load_queue()
            todos = data.get("todos", [])

            if agent_id:
                todos = [t for t in todos if t.get("to_agent") == agent_id]

            return TodoQueueStats(
                total=len(todos),
                unread=sum(1 for t in todos if not t.get("read", False)),
                by_agent=data["stats"].get("by_agent", {"agent1": 0, "agent2": 0}),
                by_priority=data["stats"].get("by_priority", {"high": 0, "medium": 0, "low": 0}),
                last_updated=data.get("last_updated", "")
            )

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return TodoQueueStats(
                total=0,
                unread=0,
                by_agent={"agent1": 0, "agent2": 0},
                by_priority={"high": 0, "medium": 0, "low": 0},
                last_updated=""
            )

    def cleanup(self, days: int = None) -> int:
        """
        清理过期的已读TODO

        Args:
            days: 保留天数，默认7天

        Returns:
            清理数量
        """
        try:
            days = days or self.CLEANUP_DAYS
            cutoff = datetime.now() - timedelta(days=days)

            with self.lock:
                data = self._load_queue()
                todos = data.get("todos", [])

                original_count = len(todos)
                todos = [
                    t for t in todos
                    if not (t.get("read", False) and t.get("read_at") and
                           datetime.fromisoformat(t["read_at"]) > cutoff)
                ]

                removed = original_count - len(todos)

                if removed > 0:
                    data["todos"] = todos
                    data["stats"] = self._recalculate_stats(todos)
                    self._save_queue(data)
                    logger.info(f"已清理{removed}个过期TODO")

                return removed

        except Exception as e:
            logger.error(f"清理过期TODO失败: {e}")
            return 0

    def delete(self, todo_id: str) -> bool:
        """
        删除TODO

        Args:
            todo_id: TODO ID

        Returns:
            True: 删除成功
            False: TODO不存在
        """
        try:
            with self.lock:
                data = self._load_queue()
                todos = data.get("todos", [])

                original_count = len(todos)
                todos = [t for t in todos if t.get("id") != todo_id]

                if len(todos) == original_count:
                    logger.warning(f"TODO不存在: {todo_id}")
                    return False

                data["todos"] = todos
                data["stats"] = self._recalculate_stats(todos)
                self._save_queue(data)

                logger.info(f"已删除TODO: {todo_id}")
                return True

        except Exception as e:
            logger.error(f"删除TODO失败: {e}")
            return False

    def clear(self, agent_id: str = None) -> int:
        """
        清空队列

        Args:
            agent_id: 可选，仅清空该接收者的TODO

        Returns:
            清空数量
        """
        try:
            with self.lock:
                data = self._load_queue()
                todos = data.get("todos", [])

                if agent_id:
                    remaining = [t for t in todos if t.get("to_agent") != agent_id]
                    cleared = len(todos) - len(remaining)
                    todos = remaining
                else:
                    cleared = len(todos)
                    todos = []

                if cleared > 0:
                    data["todos"] = todos
                    data["stats"] = self._recalculate_stats(todos)
                    self._save_queue(data)
                    logger.info(f"已清空{cleared}个TODO")

                return cleared

        except Exception as e:
            logger.error(f"清空队列失败: {e}")
            return 0
```

### 3.2 AgentStartupChecker 详细设计

```python
# src/core/agent_startup_checker.py

"""
Agent启动自检器

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

            # 构建TODO列表
            todos = [self._format_todo(t) for t in unread]

            # 生成建议
            suggestions = self._generate_suggestions(unread)

            # 优先级排序
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

        # 检查高优先级
        high_todos = [t for t in todos if t.priority == "high"]
        if high_todos:
            first = high_todos[0]
            suggestions.append(f"建议先处理: {first.id} - {first.content[:30]}...")

        # 建议查看全部
        suggestions.append(f"查看全部: oc-collab todo list --unread --agent {self.agent_id[-1]}")

        # 标记全部已读
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
        """
        建议action

        Returns:
            建议的action字符串
        """
        if not result.has_unread_todos:
            return "continue"

        high_todos = [t for t in result.todos if t["priority"] == "high"]
        if high_todos:
            return f"process_todo:{high_todos[0]['id']}"

        return "review_todos"

    def confirm_action(self) -> bool:
        """
        确认操作

        Returns:
            True: 继续
            False: 退出
        """
        try:
            response = input("\n是否继续? (y/n): ").strip().lower()
            return response in ["y", "yes", "是", "1"]
        except EOFError:
            return True
```

### 3.3 CLI命令设计

#### 3.3.1 startup-check 命令

```python
# src/cli/startup_commands.py

"""
启动检查命令
"""

import click
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.agent_startup_checker import AgentStartupChecker
from ..core.context_manager import ContextManager


@click.command("startup-check")
@click.option("--no-confirm", is_flag=True, help="不要求确认")
@click.option("--quiet", is_flag=True, help="静默模式，只返回状态码")
def startup_check_command(no_confirm: bool, quiet: bool):
    """
    执行Agent启动自检

    检查TODO队列并显示未读任务

    示例:
      oc-collab startup-check
      oc-collab startup-check --no-confirm
    """
    try:
        # 获取Agent ID
        try:
            context = ContextManager().load_context()
            agent_id = context.agent
        except Exception:
            agent_id = "unknown"

        # 执行检查
        checker = AgentStartupChecker(agent_id)
        result = checker.run()

        if quiet:
            sys.exit(1 if result.has_unread_todos else 0)

        # 显示结果
        checker.display_notifications(result)

        # 确认操作
        if not no_confirm and result.has_unread_todos:
            if not checker.confirm_action():
                click.echo("已取消")
                sys.exit(1)

        action = checker.suggest_action(result)
        if action.startswith("process_todo:"):
            todo_id = action.split(":")[1]
            click.echo(f"\n建议执行: oc-collab todo view {todo_id}")
        elif action == "review_todos":
            click.echo(f"\n建议查看: oc-collab todo list --unread --agent {agent_id[-1]}")

    except Exception as e:
        click.echo(f"❌ 启动检查失败: {e}")
        sys.exit(1)
```

#### 3.3.2 todo list --unread 增强

```python
# src/cli/todo_commands.py (增强)

# 在原有todo_list_command基础上增加 --unread 选项

@click.command("list")
@click.option("--unread", is_flag=True, help="仅显示未读TODO")
@click.option("--agent", type=click.Choice(["1", "2"]), help="按接收者筛选")
@click.option("--priority", type=click.Choice(["high", "medium", "low"]), help="按优先级筛选")
@click.option("--json", is_flag=True, help="JSON格式输出")
@click.option("--stats", is_flag=True, help="显示统计信息")
def todo_list_command(unread: bool, agent: str, priority: str, json: bool, stats: bool):
    """
    显示TODO列表

    示例:
      oc-collab todo list                  # 显示所有TODO
      oc-collab todo list --unread        # 仅未读
      oc-collab todo list --unread --agent 2  # 筛选接收者
      oc-collab todo list --unread --json # JSON格式
    """
    from ..core.todo_queue_manager import TodoQueueManager

    try:
        queue_manager = TodoQueueManager()

        if unread:
            agent_id = f"agent{agent}" if agent else None
            todos = queue_manager.get_unread(agent_id, priority)

            if json:
                import json as json_module
                output = {
                    "unread_count": len(todos),
                    "todos": [
                        {
                            "id": t.id,
                            "content": t.content,
                            "priority": t.priority,
                            "from_agent": t.from_agent,
                            "created_at": t.created_at
                        }
                        for t in todos
                    ]
                }
                click.echo(json_module.dumps(output, indent=2, ensure_ascii=False))
                return

            if stats:
                stat_obj = queue_manager.get_stats(agent_id)
                click.echo(f"\n📊 统计信息:")
                click.echo(f"  总数: {stat_obj.total}")
                click.echo(f"  未读: {stat_obj.unread}")
                click.echo(f"  按Agent: agent1={stat_obj.by_agent.get('agent1', 0)}, agent2={stat_obj.by_agent.get('agent2', 0)}")
                click.echo(f"  按优先级: 高={stat_obj.by_priority.get('high', 0)}, 中={stat_obj.by_priority.get('medium', 0)}, 低={stat_obj.by_priority.get('low', 0)}")
                click.echo("")

            if not todos:
                click.echo("✅ 无未读TODO")
                return

            click.echo(f"\n🔔 未读TODO ({len(todos)}个):")
            click.echo("-" * 60)

            for t in todos:
                priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                icon = priority_icons.get(t.priority, "⚪")
                click.echo(f"  {icon} [{t.id}] {t.content}")
                click.echo(f"      from {t.from_agent} · {t.created_at}")
                click.echo("")

        else:
            todos = queue_manager.get_all(agent_id if agent else None)

            if json:
                import json as json_module
                output = {
                    "total_count": len(todos),
                    "todos": [
                        {
                            "id": t.id,
                            "content": t.content,
                            "priority": t.priority,
                            "from_agent": t.from_agent,
                            "to_agent": t.to_agent,
                            "read": t.read,
                            "created_at": t.created_at
                        }
                        for t in todos
                    ]
                }
                click.echo(json_module.dumps(output, indent=2, ensure_ascii=False))
                return

            if not todos:
                click.echo("TODO列表为空")
                return

            click.echo(f"\n📋 TODO列表 ({len(todos)}个):")
            click.echo("-" * 60)

            for t in todos:
                status = "✅" if t.read else "📬"
                priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                icon = priority_icons.get(t.priority, "⚪")
                click.echo(f"  {status} {icon} [{t.id}] {t.content}")
                click.echo(f"      {t.from_agent} → {t.to_agent} · {t.created_at}")

    except Exception as e:
        click.echo(f"❌ 获取TODO列表失败: {e}")
```

### 3.4 StateNotifier 增强设计

```python
# src/core/state_notifier.py (增强)

# 在StateNotifier类中添加写入队列功能

class StateNotifier:
    """状态通知器（增强版）"""

    def __init__(self, webhook_config=None, dispatcher=None,
                 queue_manager: TodoQueueManager = None):
        # ... 现有代码 ...
        self.queue_manager = queue_manager

    def notify_todo_created(self, todo_id: str, content: str,
                           agent_id: str, to_agent: str = None) -> bool:
        """
        通知TODO创建（增强版）

        1. 发送Webhook通知
        2. 写入todo_queue.yaml

        Args:
            todo_id: TODO ID
            content: TODO内容
            agent_id: 发送者
            to_agent: 接收者

        Returns:
            发送结果
        """
        # 1. 发送Webhook（原有逻辑）
        webhook_result = self._notify_webhook_todo_created(todo_id, content, agent_id)

        # 2. 写入队列（新增）
        if self.queue_manager:
            queue_item = TodoQueueItem(
                id=todo_id,
                content=content,
                from_agent=agent_id,
                to_agent=to_agent or "agent2",
                priority="medium",
                created_at=datetime.now().isoformat(),
                read=False
            )
            queue_result = self.queue_manager.add(queue_item)
        else:
            queue_result = None

        return webhook_result or (queue_result if queue_result is not None else False)

    def notify_todo_completed(self, todo_id: str, content: str,
                             agent_id: str, to_agent: str = None) -> bool:
        """通知TODO完成（增强版）"""
        webhook_result = self._notify_webhook_todo_completed(todo_id, content, agent_id)

        if self.queue_manager and to_agent:
            # 标记队列中的TODO为已读
            self.queue_manager.mark_read(todo_id, to_agent)

        return webhook_result

    def _notify_webhook_todo_created(self, todo_id: str, content: str,
                                    agent_id: str) -> bool:
        """发送Webhook通知 - TODO创建"""
        # 现有逻辑
        pass

    def _notify_webhook_todo_completed(self, todo_id: str, content: str,
                                       agent_id: str) -> bool:
        """发送Webhook通知 - TODO完成"""
        # 现有逻辑
        pass
```

---

## 4. 数据结构

### 4.1 todo_queue.yaml Schema

```yaml
# state/todo_queue.yaml

version: "1.0"
last_updated: "2026-02-14T10:00:00Z"

stats:
  total: 10
  unread: 3
  by_agent:
    agent1: 5
    agent2: 5
  by_priority:
    high: 2
    medium: 5
    low: 3

todos:
  - id: "TODO-350"
    content: "Agent1创建的任务"
    from_agent: "agent1"
    to_agent: "agent2"
    priority: "high"
    created_at: "2026-02-14T10:00:00Z"
    read: false
    read_at: null

  - id: "TODO-351"
    content: "另一个任务"
    from_agent: "agent1"
    to_agent: "agent2"
    priority: "medium"
    created_at: "2026-02-14T10:30:00Z"
    read: true
    read_at: "2026-02-14T11:00:00Z"
```

### 4.2 优先级定义

| 优先级 | 值 | 说明 |
|--------|-----|------|
| high | high | 高优先级，需要立即处理 |
| medium | medium | 中优先级，正常处理 |
| low | low | 低优先级，有空时处理 |

---

## 5. 接口设计

### 5.1 CLI命令

| 命令 | 选项 | 功能 |
|------|------|------|
| `oc-collab startup-check` | [--no-confirm] [--quiet] | Agent启动自检 |
| `oc-collab todo list` | [--unread] [--agent] [--priority] [--json] | 显示TODO列表 |
| `oc-collab todo mark-read` | \<id\> | 标记TODO已读 |
| `oc-collab todo mark-all-read` | [--agent] | 标记所有已读 |
| `oc-collab todo stats` | [--agent] | 显示统计信息 |

### 5.2 内部API

| 类 | 方法 | 功能 | 工时 |
|----|------|------|------|
| TodoQueueManager | `add(item)` | 添加TODO | 0.5h |
| TodoQueueManager | `get_unread(agent, priority)` | 获取未读 | 0.5h |
| TodoQueueManager | `mark_read(todo_id, agent)` | 标记已读 | 0.5h |
| TodoQueueManager | `get_stats(agent)` | 获取统计 | 0.5h |
| TodoQueueManager | `cleanup(days)` | 清理过期 | 0.5h |
| AgentStartupChecker | `run()` | 执行检查 | 1h |
| AgentStartupChecker | `display_notifications()` | 显示通知 | 0.5h |
| StateNotifier | `_write_to_queue()` | 写入队列 | 0.5h |

---

## 6. 测试设计

### 6.1 单元测试

| 测试用例 | 输入 | 预期输出 | 优先级 |
|----------|------|----------|--------|
| TodoQueueManager.add | 有效TODO | 添加成功，返回True | P0 |
| TodoQueueManager.add | 重复TODO | 返回False，跳过 | P0 |
| TodoQueueManager.add | 空队列 | 创建队列文件 | P0 |
| TodoQueueManager.get_unread | agent_id=None | 返回所有未读 | P0 |
| TodoQueueManager.get_unread | agent_id="agent2" | 返回agent2的未读 | P0 |
| TodoQueueManager.get_unread | priority="high" | 返回高优先级未读 | P1 |
| TodoQueueManager.mark_read | 存在的todo_id | 标记成功，返回True | P0 |
| TodoQueueManager.mark_read | 不存在的todo_id | 返回False | P1 |
| TodoQueueManager.mark_all_read | agent_id=None | 标记所有未读为已读 | P0 |
| TodoQueueManager.get_stats | 无筛选 | 返回完整统计 | P1 |
| TodoQueueManager.cleanup | days=7 | 清理7天前的已读 | P1 |
| AgentStartupChecker.run | 有未读TODO | 返回通知列表 | P0 |
| AgentStartupChecker.run | 无未读TODO | 返回空列表 | P0 |
| AgentStartupChecker.display | 有效结果 | 正确格式化输出 | P1 |

### 6.2 集成测试

| 测试场景 | 测试步骤 | 预期结果 |
|----------|----------|----------|
| todowrite后队列写入 | 1. 执行todowrite<br>2. 检查队列文件 | TODO写入队列 |
| 启动自检显示 | 1. 运行startup-check<br>2. 验证输出格式 | 正确显示未读列表 |
| 标记已读同步 | 1. 标记TODO已读<br>2. 验证队列状态 | read=True |

---

## 7. 依赖

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | >=3.9 | 运行环境 |
| PyYAML | >=6.0 | YAML解析 |
| Click | >=8.0 | CLI框架 |
| filelock | >=3.0 | 文件锁 |

---

## 8. 工时估算

| 模块 | 开发 | 测试 | 缓冲 | 小计 |
|------|------|------|------|------|
| M1: TodoQueueManager | 2h | 1h | 0.5h | 3.5h |
| M2: StateNotifier增强 | 1h | 0.5h | 0h | 1.5h |
| M3: Agent启动自检 | 4h | 2h | 1h | 7h |
| M4: CLI todo --unread | 2h | 1h | 0.5h | 3.5h |
| M5: BUG-001修复 | 2h | 1h | 0.5h | 3.5h |
| M6: BUG-002修复 | 2h | 0h | 0.5h | 2.5h |
| **合计** | **13h** | **5.5h** | **3h** | **21.5h** |

---

## 9. 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 队列文件损坏 | 丢失通知 | 备份机制 + 恢复逻辑 |
| 并发写入冲突 | 数据不一致 | FileLock文件锁 |
| Agent不自检 | 功能无效 | CLI兜底查询 todo list --unread |
| 队列文件过大 | 性能下降 | 自动清理过期TODO |

---

## 10. 签署记录

| 角色 | 签署人 | 日期 | 状态 |
|------|--------|------|------|
| Agent 2 | 创建 | 2026-02-14 | ✅ |
| Agent 1 | 评审 | 2026-02-14 | ✅ **通过** |

**评审意见**：
- 实现方案完整可行
- 与概要设计完全对应
- 代码设计清晰
- 测试用例覆盖完整
- 工时估算合理（21.5h）

---

**文档版本**: v1
**创建日期**: 2026-02-14
**修订日期**: 2026-02-14
**状态**: APPROVED
