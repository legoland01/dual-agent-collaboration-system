from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TodoItem:
    """待办项"""
    id: str
    content: str
    status: str = "pending"
    priority: str = "medium"
    agent_id: Optional[int] = None
    receiver: Optional[str] = None
    sender: Optional[str] = None
    source: str = "MANUAL"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_read: int = 0


@dataclass
class TodoState:
    """待办状态"""
    todos: List[TodoItem] = field(default_factory=list)
    version: str = "2.3.2"
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class TodoSyncError(Exception):
    """待办同步错误"""
    pass


class TodoLoadError(TodoSyncError):
    """待办加载错误"""
    pass


class TodoSaveError(TodoSyncError):
    """待办保存错误"""
    pass


class TodoSyncManager:
    """待办同步管理器 - 使用SQLite存储"""

    DB_FILENAME = "state/todos.db"

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.db_path = str(self.project_path / self.DB_FILENAME)
        self._storage = None

    def _get_storage(self):
        """获取SQLite存储层"""
        if self._storage is None:
            from .todo_storage import TodoStorage
            self._storage = TodoStorage(self.db_path)
        return self._storage

    def load_todos(self) -> TodoState:
        """
        加载待办状态

        Returns:
            TodoState 对象

        Raises:
            TodoLoadError: 加载失败
        """
        try:
            storage = self._get_storage()
            rows = storage.list()
            
            todos = []
            for row in rows:
                todo = TodoItem(
                    id=row['id'],
                    content=row['content'],
                    status=row['status'],
                    priority=row.get('priority', 'medium'),
                    agent_id=row.get('agent_id'),
                    receiver=row.get('receiver'),
                    sender=row.get('sender'),
                    source=row.get('source', 'MANUAL'),
                    created_at=row.get('created_at', datetime.now().isoformat()),
                    updated_at=row.get('updated_at', datetime.now().isoformat()),
                    is_read=row.get('is_read', 0),
                )
                todos.append(todo)
            
            return TodoState(todos=todos)
        except Exception as e:
            raise TodoLoadError(f"加载待办失败: {e}")

    def add_todo(self, content: str, agent_id: Optional[int] = None,
                 priority: str = "medium", todo_id: Optional[str] = None,
                 receiver: Optional[str] = None, source: str = "MANUAL") -> TodoItem:
        """
        添加待办

        Args:
            content: 待办内容
            agent_id: Agent 编号 (1 或 2)
            priority: 优先级
            todo_id: 指定TODO ID
            receiver: 接收者

        Returns:
            TodoItem 对象

        Raises:
            TodoSaveError: 保存失败
        """
        storage = self._get_storage()

        max_id = 0
        existing = storage.list()
        
        prefix = f"TODO-{agent_id}"
        if receiver:
            prefix = f"TODO-{agent_id}to{receiver}"
        
        for item in existing:
            item_id = item['id']
            if item_id.startswith(prefix):
                try:
                    parts = item_id.split("-")
                    num = int(parts[-1])
                    max_id = max(max_id, num)
                except (ValueError, IndexError):
                    pass

        if todo_id:
            new_id = todo_id
        elif agent_id:
            new_id = f"{prefix}-{max_id + 1:03d}"
        else:
            new_id = f"TODO-{max_id + 1:03d}"

        now = datetime.now().isoformat()
        
        if receiver is None and agent_id is not None:
            receiver = str(agent_id)
        
        todo_dict = {
            'id': new_id,
            'content': content,
            'status': 'pending',
            'priority': priority,
            'agent_id': agent_id,
            'receiver': receiver,
            'sender': str(agent_id) if agent_id else None,
            'source': source,
            'created_at': now,
            'updated_at': now,
            'is_read': 0,
        }

        success, result = storage.add(todo_dict)
        if not success:
            raise TodoSaveError(f"保存待办失败: {result}")

        return TodoItem(**todo_dict)

    def update_todo(self, todo_id: str, **kwargs) -> Optional[TodoItem]:
        """更新待办"""
        storage = self._get_storage()
        
        updates = {}
        for key, value in kwargs.items():
            if key == 'status':
                updates['status'] = value
            elif key == 'priority':
                updates['priority'] = value
            elif key == 'content':
                updates['content'] = value
            elif key == 'is_read':
                updates['is_read'] = value
        
        if updates:
            storage.update(todo_id, updates)
        
        row = storage.get(todo_id)
        if row:
            return TodoItem(
                id=row['id'],
                content=row['content'],
                status=row['status'],
                priority=row.get('priority', 'medium'),
                receiver=row.get('receiver'),
                sender=row.get('sender'),
                source=row.get('source', 'MANUAL'),
                created_at=row.get('created_at', ''),
                updated_at=row.get('updated_at', ''),
                is_read=row.get('is_read', 0),
            )
        return None

    def delete_todo(self, todo_id: str) -> bool:
        """删除待办"""
        storage = self._get_storage()
        return storage.delete(todo_id)

    def get_todo(self, todo_id: str) -> Optional[TodoItem]:
        """获取单个待办"""
        storage = self._get_storage()
        row = storage.get(todo_id)
        if row:
            return TodoItem(
                id=row['id'],
                content=row['content'],
                status=row['status'],
                priority=row.get('priority', 'medium'),
                receiver=row.get('receiver'),
                sender=row.get('sender'),
                source=row.get('source', 'MANUAL'),
                created_at=row.get('created_at', ''),
                updated_at=row.get('updated_at', ''),
                is_read=row.get('is_read', 0),
            )
        return None

    def list_todos(self, receiver: Optional[str] = None, 
                   status: Optional[str] = None) -> List[TodoItem]:
        """列出待办"""
        storage = self._get_storage()
        rows = storage.list(receiver=receiver, status=status)
        
        return [
            TodoItem(
                id=row['id'],
                content=row['content'],
                status=row['status'],
                priority=row.get('priority', 'medium'),
                receiver=row.get('receiver'),
                sender=row.get('sender'),
                source=row.get('source', 'MANUAL'),
                created_at=row.get('created_at', ''),
                updated_at=row.get('updated_at', ''),
                is_read=row.get('is_read', 0),
            )
            for row in rows
        ]

    def mark_read(self, todo_id: str) -> bool:
        """标记为已读"""
        storage = self._get_storage()
        return storage.mark_read(todo_id)

    def mark_unread(self, todo_id: str) -> bool:
        """标记为未读"""
        storage = self._get_storage()
        return storage.mark_unread(todo_id)

    def count_unread(self, receiver: str) -> int:
        """统计未读待办数量"""
        storage = self._get_storage()
        return storage.count_unread(receiver)

    def save_todos(self, state: TodoState) -> None:
        """保存待办状态（兼容接口，实际不执行任何操作）"""
        pass

    @property
    def todo_file(self):
        """兼容属性 - 返回数据库路径"""
        return self.db_path

    def sync_with_rollback(self, func: callable) -> bool:
        """兼容方法 - 执行函数并处理异常"""
        try:
            func()
            return True
        except Exception:
            return False

    def rollback(self) -> bool:
        """
        回滚操作（兼容方法）
        
        Returns:
            False: 无需回滚
        """
        return False

    def create_backup(self) -> Optional[str]:
        """
        创建备份（兼容方法）
        
        Returns:
            备份文件路径，如果没有备份则返回None
        """
        return None

    def get_todos_by_agent(self, agent_id: Optional[int] = None, 
                          status: Optional[str] = None) -> List[TodoItem]:
        """获取指定Agent的待办"""
        todos = self.list_todos(receiver=str(agent_id) if agent_id else None, 
                               status=status)
        return todos
