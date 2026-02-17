"""TODO消息队列管理器

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
    priority: str
    created_at: str
    read: bool = False
    read_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TodoQueueItem':
        # 兼容agent_adhoc_todos.yaml格式转换
        # TodoItem: id, content, status, priority, agent_id, created_at, updated_at
        # TodoQueueItem: id, content, from_agent, to_agent, priority, created_at, read, read_at
        
        todo_id = data.get('id', '')
        
        # 首先尝试从TODO ID解析 (如 TODO-2to1-008)
        from_agent = None
        to_agent = None
        
        if 'to' in todo_id:
            # 新格式: TODO-2to1-008
            import re
            match = re.match(r'TODO-(\d+)to(\d+)-(\d+)', todo_id)
            if match:
                from_agent = f'agent{match.group(1)}'
                to_agent = f'agent{match.group(2)}'
        
        # 如果没有解析成功，使用数据中的字段
        if not from_agent:
            from_agent = data.get('from_agent') or data.get('from_agent')
        if not to_agent:
            to_agent = data.get('to_agent') or data.get('to_agent')
        
        # 如果都没有，使用agent_id
        if not from_agent and 'agent_id' in data and data.get('agent_id'):
            from_agent = f"agent{data.get('agent_id')}"
            to_agent = from_agent
        
        if not to_agent:
            to_agent = from_agent or 'agent1'
        
        # status -> read
        read = data.get('status') != 'pending'
        
        return cls(
            id=todo_id,
            content=data.get('content', ''),
            from_agent=from_agent or 'agent1',
            to_agent=to_agent or 'agent1',
            priority=data.get('priority', 'medium'),
            created_at=data.get('created_at') or datetime.now().isoformat(),
            read=read,
            read_at=data.get('updated_at') if read else None
        )


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

    QUEUE_FILE = "state/agent_adhoc_todos.yaml"
    LOCK_FILE = "state/todo_queue.lock"
    LOCK_TIMEOUT = 10
    CLEANUP_DAYS = 7

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
        """加载队列数据"""
        if not self.queue_file.exists():
            return {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "stats": self._init_stats(),
                "todos": []
            }

        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                
                # 兼容agent_adhoc_todos.yaml格式 (直接是todos列表)
                if "todos" in data and isinstance(data["todos"], list):
                    # 检查是否是agent_adhoc_todos格式 (没有version字段)
                    if "version" not in data:
                        return {
                            "version": "1.0",
                            "last_updated": data.get("last_updated", datetime.now().isoformat()),
                            "stats": self._init_stats(),
                            "todos": data["todos"]
                        }
                return data or {
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
        """保存队列数据"""
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
        """重新计算统计信息"""
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
        """添加TODO到队列"""
        try:
            with self.lock:
                data = self._load_queue()
                todos = data.get("todos", [])

                for todo in todos:
                    if todo.get("id") == item.id:
                        logger.debug(f"TODO已存在，跳过: {item.id}")
                        return False

                new_todo = item.to_dict()
                todos.append(new_todo)
                data["todos"] = todos
                data["stats"] = self._recalculate_stats(todos)

                self._save_queue(data)
                logger.info(f"TODO已添加到队列: {item.id}")
                return True

        except Exception as e:
            logger.error(f"添加TODO到队列失败: {e}")
            return False

    def get_unread(self, agent_id: str = None, priority: str = None) -> List[TodoQueueItem]:
        """获取未读TODO"""
        try:
            data = self._load_queue()
            todos = data.get("todos", [])

            result = []
            for todo_data in todos:
                # 先转换为TodoQueueItem获取正确的from/to
                todo_item = TodoQueueItem.from_dict(todo_data)
                
                if todo_item.read:
                    continue

                # 如果是旧格式TODO（没有明确to_agent），直接显示给当前Agent
                # 让Agent自己判断内容是否与自己相关
                if agent_id and not todo_item.to_agent:
                    # 旧格式TODO：没有明确接收者，全部显示
                    pass
                elif agent_id and todo_item.to_agent != agent_id:
                    # 新格式TODO：检查接收者是否匹配
                    continue

                if priority and todo_item.priority != priority:
                    continue

                result.append(todo_item)

            priority_order = {"high": 0, "medium": 1, "low": 2}
            
            def get_sort_key(item):
                priority = item.priority
                created = item.created_at or ""
                return (priority_order.get(priority, 3), created)
            
            result.sort(key=get_sort_key)
            return result

        except Exception as e:
            logger.error(f"获取未读TODO失败: {e}")
            return []

    def get_all(self, agent_id: str = None) -> List[TodoQueueItem]:
        """获取所有TODO"""
        try:
            data = self._load_queue()
            todos = data.get("todos", [])

            if agent_id:
                todos = [t for t in todos if t.get("to_agent") == agent_id]

            todos.sort(key=lambda x: x.get("created_at") or "")
            return [TodoQueueItem.from_dict(t) for t in todos]

        except Exception as e:
            logger.error(f"获取所有TODO失败: {e}")
            return []

    def mark_read(self, todo_id: str, agent_id: str = None) -> bool:
        """标记TODO为已读"""
        try:
            with self.lock:
                data = self._load_queue()
                todos = data.get("todos", [])

                for i, todo in enumerate(todos):
                    if todo.get("id") != todo_id:
                        continue

                    if agent_id and todo.get("to_agent") != agent_id:
                        logger.warning(f"TODO接收者不匹配: {todo_id}")
                        return False

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
        """标记所有TODO为已读"""
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
        """获取队列统计"""
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
                total=0, unread=0,
                by_agent={"agent1": 0, "agent2": 0},
                by_priority={"high": 0, "medium": 0, "low": 0},
                last_updated=""
            )

    def cleanup(self, days: int = None) -> int:
        """清理过期的已读TODO"""
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
        """删除TODO"""
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
        """清空队列"""
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
