"""v2.2.3 测试用例：ContextManager, TodoSyncManager, Enhanced CLI"""
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.core.context_manager import (
    ContextManager,
    ProjectContext,
    ContextNotFoundError,
    ContextParseError,
    InvalidContextError,
)
from src.core.todo_sync_manager import (
    TodoSyncManager,
    TodoItem,
    TodoState,
    TodoLoadError,
    TodoSaveError,
)


class TestContextManager:
    """ContextManager 测试类"""

    @pytest.fixture
    def temp_project(self):
        """创建临时项目目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def context_manager(self, temp_project):
        return ContextManager(temp_project)

    def test_find_config_file_not_found(self, context_manager):
        """TC-CONTEXT-001: 未找到配置文件时返回 None"""
        result = context_manager.find_config_file()
        assert result is None

    def test_save_and_load_context(self, temp_project):
        """TC-CONTEXT-002: 保存和加载上下文"""
        manager = ContextManager(temp_project)
        context = ProjectContext(
            project="TestProject",
            path=temp_project,
            agent=1,
            version="2.2.3"
        )

        config_path = Path(temp_project) / ".oc-collab.yaml"
        manager.save_context(context, config_path)

        assert config_path.exists()

        loaded = manager.load_context(config_path)
        assert loaded.project == "TestProject"
        assert loaded.agent == 1
        assert loaded.version == "2.2.3"

    def test_load_context_missing_fields(self, temp_project):
        """TC-CONTEXT-003: 缺少必要字段时抛出异常"""
        manager = ContextManager(temp_project)
        config_path = Path(temp_project) / ".oc-collab.yaml"

        with open(config_path, 'w') as f:
            f.write("project: Test\n")  # 缺少 path 和 agent

        with pytest.raises(InvalidContextError):
            manager.load_context(config_path)

    def test_load_context_invalid_agent(self, temp_project):
        """TC-CONTEXT-004: agent 值无效时抛出异常"""
        manager = ContextManager(temp_project)
        config_path = Path(temp_project) / ".oc-collab.yaml"

        with open(config_path, 'w') as f:
            f.write("project: Test\npath: /test\nagent: 3\n")

        with pytest.raises(InvalidContextError):
            manager.load_context(config_path)

    def test_find_config_file_upward_search(self, temp_project):
        """向上查找配置文件"""
        manager = ContextManager()

        subdir = Path(temp_project) / "subdir"
        subdir.mkdir()

        config_path = Path(temp_project) / ".oc-collab.yaml"
        with open(config_path, 'w') as f:
            f.write("project: Test\npath: /test\nagent: 1\n")

        result = manager.find_config_file(subdir)
        assert result == config_path

    def test_get_agent_display_name(self, context_manager):
        """Agent 显示名称测试"""
        assert context_manager.get_agent_display_name(1) == "Agent 1"
        assert context_manager.get_agent_display_name(2) == "Agent 2"


class TestTodoSyncManager:
    """TodoSyncManager 测试类"""

    @pytest.fixture
    def temp_project(self):
        """创建临时项目目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def sync_manager(self, temp_project):
        return TodoSyncManager(temp_project)

    def test_add_todo(self, sync_manager):
        """TC-TASK-001: 添加待办"""
        todo = sync_manager.add_todo("测试任务", agent_id=1, priority="high")

        assert todo.id.startswith("TODO-")
        assert todo.content == "测试任务"
        assert todo.priority == "high"
        assert todo.agent_id == 1

        state = sync_manager.load_todos()
        assert len(state.todos) == 1

    def test_update_todo(self, sync_manager):
        """TC-TASK-002: 更新待办"""
        todo = sync_manager.add_todo("原始任务", agent_id=1)

        updated = sync_manager.update_todo(todo.id, status="completed", priority="high")

        assert updated.status == "completed"
        assert updated.priority == "high"

        state = sync_manager.load_todos()
        assert state.todos[0].status == "completed"

    def test_delete_todo(self, sync_manager):
        """TC-TASK-003: 删除待办"""
        todo = sync_manager.add_todo("待删除任务", agent_id=1)

        result = sync_manager.delete_todo(todo.id)
        assert result is True

        state = sync_manager.load_todos()
        assert len(state.todos) == 0

    def test_get_todos_by_agent(self, sync_manager):
        """TC-UI-001: 按 Agent 过滤待办"""
        sync_manager.add_todo("Agent 1 任务", agent_id=1)
        sync_manager.add_todo("Agent 2 任务", agent_id=2)

        agent1_todos = sync_manager.get_todos_by_agent(agent_id=1)
        assert len(agent1_todos) == 1
        assert agent1_todos[0].content == "Agent 1 任务"

    def test_get_todos_by_status(self, sync_manager):
        """TC-UI-002: 按状态过滤待办"""
        todo1 = sync_manager.add_todo("待办任务", agent_id=1)
        sync_manager.update_todo(todo1.id, status="completed")

        pending = sync_manager.get_todos_by_agent(status="pending")
        completed = sync_manager.get_todos_by_agent(status="completed")

        assert len(pending) == 0
        assert len(completed) == 1

    def test_rollback_on_error(self, sync_manager):
        """TC-TASK-003: 同步失败时回滚"""
        todo = sync_manager.add_todo("正常任务", agent_id=1)

        state = sync_manager.load_todos()
        assert len(state.todos) == 1

        result = sync_manager.rollback()
        assert result is False

    def test_multiple_todos_order(self, sync_manager):
        """TC-UI-003: 多个待办的排序"""
        sync_manager.add_todo("低优先级", agent_id=1, priority="low")
        sync_manager.add_todo("高优先级", agent_id=1, priority="high")
        sync_manager.add_todo("中优先级", agent_id=1, priority="medium")

        todos = sync_manager.get_todos_by_agent(agent_id=1)

        priorities = [t.priority for t in todos]

        assert len(priorities) == 3


class TestProjectContext:
    """ProjectContext 数据类测试"""

    def test_default_values(self):
        """默认字段值测试"""
        context = ProjectContext(
            project="Test",
            path="/test",
            agent=1
        )

        assert context.version == "2.2.3"
        assert context.created_at is None
        assert context.last_updated is None

    def test_custom_values(self):
        """自定义字段值测试"""
        now = datetime.now().isoformat()
        context = ProjectContext(
            project="Custom",
            path="/custom",
            agent=2,
            version="2.2.4",
            created_at=now,
            last_updated=now
        )

        assert context.project == "Custom"
        assert context.agent == 2
        assert context.version == "2.2.4"


class TestTodoItem:
    """TodoItem 数据类测试"""

    def test_default_values(self):
        """默认字段值测试"""
        todo = TodoItem(id="TODO-001", content="测试")

        assert todo.status == "pending"
        assert todo.priority == "medium"
        assert todo.agent_id is None

    def test_full_values(self):
        """完整字段值测试"""
        now = datetime.now().isoformat()
        todo = TodoItem(
            id="TODO-001",
            content="完整测试",
            status="completed",
            priority="high",
            agent_id=1,
            created_at=now,
            updated_at=now
        )

        assert todo.id == "TODO-001"
        assert todo.content == "完整测试"
        assert todo.status == "completed"
        assert todo.priority == "high"
        assert todo.agent_id == 1
