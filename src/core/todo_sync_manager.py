from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
import yaml
import os
import shutil


@dataclass
class TodoItem:
    """待办项"""
    id: str
    content: str
    status: str = "pending"
    priority: str = "medium"
    agent_id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TodoState:
    """待办状态"""
    todos: List[TodoItem] = field(default_factory=list)
    version: str = "1.0"
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


class TodoRollbackError(TodoSyncError):
    """待办回滚错误"""
    pass


class TodoSyncManager:
    """待办同步管理器"""

    TODO_FILENAME = "state/agent_adhoc_todos.yaml"

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.todo_file = self.project_path / self.TODO_FILENAME
        self._backup_file: Optional[Path] = None

    def load_todos(self) -> TodoState:
        """
        加载待办状态

        Returns:
            TodoState 对象

        Raises:
            TodoLoadError: 加载失败
        """
        try:
            if not self.todo_file.exists():
                return TodoState()

            with open(self.todo_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if data is None:
                return TodoState()

            todos = []
            for item in data.get("adhoc_todos", data.get("todos", [])):
                todo = TodoItem(
                    id=item.get("id"),
                    content=item.get("content"),
                    status=item.get("status", "pending"),
                    priority=item.get("priority", "medium"),
                    agent_id=item.get("agent_id") or item.get("to", {}).get("agent_id") if isinstance(item.get("to"), dict) else None,
                    created_at=item.get("created_at"),
                    updated_at=item.get("updated_at"),
                )
                todos.append(todo)

            return TodoState(
                todos=todos,
                version=data.get("version", "1.0"),
                last_updated=data.get("last_updated"),
            )
        except yaml.YAMLError as e:
            raise TodoLoadError(f"解析待办文件失败: {str(e)}")
        except IOError as e:
            raise TodoLoadError(f"读取待办文件失败: {str(e)}")

    def save_todos(self, state: TodoState) -> None:
        """
        保存待办状态

        Args:
            state: TodoState 对象

        Raises:
            TodoSaveError: 保存失败
            ValueError: ID 重复
        """
        # 检查 TODO-ID 唯一性（只检查 TODO- 开头的 ID）
        todo_ids = [todo.id for todo in state.todos if todo.id and todo.id.startswith("TODO-")]
        if len(todo_ids) != len(set(todo_ids)):
            seen = set()
            for todo_id in todo_ids:
                if todo_id in seen:
                    raise ValueError(f"TODO ID 重复: {todo_id}")
                seen.add(todo_id)
        
        try:
            todos_list = [
                {
                    "id": todo.id,
                    "content": todo.content,
                    "status": todo.status,
                    "priority": todo.priority,
                    "agent_id": todo.agent_id,
                    "created_at": todo.created_at,
                    "updated_at": todo.updated_at,
                }
                for todo in state.todos
            ]

            data = {
                "todos": todos_list,
                "total": len(todos_list),
            }

            self.todo_file.parent.mkdir(parents=True, exist_ok=True)

            if self.todo_file.exists():
                self._backup_file = self.todo_file.with_suffix(".bak")
                shutil.copy2(self.todo_file, self._backup_file)

            with open(self.todo_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)

            if self._backup_file and self._backup_file.exists():
                self._backup_file.unlink()
                self._backup_file = None

        except yaml.YAMLError as e:
            raise TodoSaveError(f"序列化待办数据失败: {str(e)}")
        except IOError as e:
            raise TodoSaveError(f"写入待办文件失败: {str(e)}")

    def add_todo(self, content: str, agent_id: Optional[int] = None,
                 priority: str = "medium") -> TodoItem:
        """
        添加待办

        Args:
            content: 待办内容
            agent_id: Agent 编号
            priority: 优先级

        Returns:
            TodoItem 对象

        Raises:
            TodoSaveError: 保存失败
        """
        state = self.load_todos()

        max_id = 0
        for todo in state.todos:
            if todo.id.startswith("TODO-"):
                try:
                    num = int(todo.id.split("-")[1])
                    max_id = max(max_id, num)
                except (ValueError, IndexError):
                    pass

        new_id = f"TODO-{max_id + 1:03d}"

        todo = TodoItem(
            id=new_id,
            content=content,
            agent_id=agent_id,
            priority=priority,
        )

        state.todos.append(todo)

        try:
            self.save_todos(state)
        except TodoSaveError:
            raise

        return todo

    def update_todo(self, todo_id: str, **kwargs) -> Optional[TodoItem]:
        """
        更新待办

        Args:
            todo_id: 待办 ID
            **kwargs: 更新字段

        Returns:
            更新后的 TodoItem，未找到返回 None
        """
        state = self.load_todos()

        for todo in state.todos:
            if todo.id == todo_id:
                for key, value in kwargs.items():
                    if hasattr(todo, key):
                        setattr(todo, key, value)
                todo.updated_at = datetime.now().isoformat()

                try:
                    self.save_todos(state)
                except TodoSaveError:
                    raise

                return todo

        return None

    def delete_todo(self, todo_id: str) -> bool:
        """
        删除待办

        Args:
            todo_id: 待办 ID

        Returns:
            是否删除成功
        """
        state = self.load_todos()

        original_count = len(state.todos)
        state.todos = [todo for todo in state.todos if todo.id != todo_id]

        if len(state.todos) < original_count:
            try:
                self.save_todos(state)
                return True
            except TodoSaveError:
                raise

        return False

    def get_todos_by_agent(self, agent_id: Optional[int] = None,
                           status: Optional[str] = None) -> List[TodoItem]:
        """
        按条件获取待办列表

        Args:
            agent_id: Agent 编号过滤
            status: 状态过滤

        Returns:
            过滤后的待办列表
        """
        state = self.load_todos()

        result = state.todos

        if agent_id is not None:
            result = [todo for todo in result if todo.agent_id == agent_id]

        if status is not None:
            result = [todo for todo in result if todo.status == status]

        return result

    def create_backup(self) -> None:
        """创建备份"""
        if self.todo_file.exists():
            self._backup_file = self.todo_file.with_suffix(".bak")
            shutil.copy2(self.todo_file, self._backup_file)

    def restore_backup(self) -> bool:
        """
        从备份恢复

        Returns:
            是否恢复成功
        """
        if self._backup_file and self._backup_file.exists():
            shutil.copy2(self._backup_file, self.todo_file)
            self._backup_file = None
            return True
        return False

    def rollback(self) -> bool:
        """
        回滚操作

        Returns:
            是否回滚成功
        """
        if self._backup_file and self._backup_file.exists():
            shutil.copy2(self._backup_file, self.todo_file)
            self._backup_file = None
            return True
        return False

    def sync_with_rollback(self, operation: Callable) -> bool:
        """
        带回滚的同步操作

        Args:
            operation: 需要执行的操作函数

        Returns:
            是否执行成功
        """
        try:
            self.create_backup()
            operation()
            return True
        except Exception as e:
            if self.rollback():
                pass
            return False
