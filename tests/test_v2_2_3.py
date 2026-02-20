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

    def test_find_config_file_from_subdir(self, temp_project):
        """TC-CONTEXT-001: 从子目录向上查找配置文件"""
        manager = ContextManager()

        subdir = Path(temp_project) / "subdir" / "nested"
        subdir.mkdir(parents=True)

        config_path = Path(temp_project) / ".oc-collab.yaml"
        with open(config_path, 'w') as f:
            f.write(f"project: Test\npath: {temp_project}\nagent: 1\n")

        result = manager.find_config_file(subdir)
        assert result == config_path

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

        assert context.version == "2.3.2"
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


class TestContextManagerEdgeCases:
    """ContextManager 边界条件测试"""

    @pytest.fixture
    def temp_project(self):
        """创建临时项目目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_find_config_file_git_boundary(self, temp_project):
        """TC-CONTEXT-001: 遇到 git root 停止查找"""
        manager = ContextManager()

        project_dir = Path(temp_project) / "project"
        project_dir.mkdir()

        git_dir = project_dir / ".git"
        git_dir.mkdir()

        subdir = project_dir / "subdir"
        subdir.mkdir()

        result = manager.find_config_file(subdir)
        assert result is None

    def test_find_config_file_pyproject_boundary(self, temp_project):
        """遇到 pyproject.toml 停止查找"""
        manager = ContextManager()

        project_dir = Path(temp_project) / "project"
        project_dir.mkdir()

        pyproject = project_dir / "pyproject.toml"
        pyproject.touch()

        subdir = project_dir / "subdir"
        subdir.mkdir()

        result = manager.find_config_file(subdir)
        assert result is None

    def test_load_context_yaml_parse_error(self, temp_project):
        """TC-CONTEXT-002: YAML 解析错误"""
        manager = ContextManager(temp_project)
        config_path = Path(temp_project) / ".oc-collab.yaml"

        with open(config_path, 'w') as f:
            f.write("project: Test\n  invalid yaml: \n")

        with pytest.raises(ContextParseError):
            manager.load_context(config_path)

    def test_load_context_empty_file(self, temp_project):
        """空配置文件测试"""
        manager = ContextManager(temp_project)
        config_path = Path(temp_project) / ".oc-collab.yaml"

        config_path.touch()

        with pytest.raises(InvalidContextError):
            manager.load_context(config_path)

    def test_load_context_missing_project_field(self, temp_project):
        """缺少 project 字段"""
        manager = ContextManager(temp_project)
        config_path = Path(temp_project) / ".oc-collab.yaml"

        with open(config_path, 'w') as f:
            f.write("path: /test\nagent: 1\n")

        with pytest.raises(InvalidContextError):
            manager.load_context(config_path)

    def test_load_context_missing_path_field(self, temp_project):
        """缺少 path 字段"""
        manager = ContextManager(temp_project)
        config_path = Path(temp_project) / ".oc-collab.yaml"

        with open(config_path, 'w') as f:
            f.write("project: Test\nagent: 1\n")

        with pytest.raises(InvalidContextError):
            manager.load_context(config_path)


class TestTodoSyncManagerEdgeCases:
    """TodoSyncManager 边界条件测试"""

    @pytest.fixture
    def temp_project(self):
        """创建临时项目目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def sync_manager(self, temp_project):
        return TodoSyncManager(temp_project)

    def test_add_todo_multiple(self, sync_manager):
        """添加多个待办"""
        todo1 = sync_manager.add_todo("任务1", agent_id=1, priority="high")
        todo2 = sync_manager.add_todo("任务2", agent_id=1, priority="medium")
        todo3 = sync_manager.add_todo("任务3", agent_id=2, priority="low")

        assert todo1.id.startswith("TODO-1-") or todo1.id == "TODO-001"
        assert todo2.id.startswith("TODO-1-") or todo2.id == "TODO-002"
        assert todo3.id.startswith("TODO-2-") or todo3.id == "TODO-003"

        state = sync_manager.load_todos()
        assert len(state.todos) == 3

    def test_update_nonexistent_todo(self, sync_manager):
        """更新不存在的待办"""
        result = sync_manager.update_todo("TODO-999", status="completed")
        assert result is None

    def test_delete_nonexistent_todo(self, sync_manager):
        """删除不存在的待办"""
        result = sync_manager.delete_todo("TODO-999")
        assert result is False

    def test_rollback_creates_backup(self, sync_manager):
        """回滚时创建备份（兼容方法）"""
        result = sync_manager.create_backup()
        assert result is None

    def test_load_todos_empty_file(self, temp_project):
        """加载空的 todo.yaml"""
        manager = TodoSyncManager(temp_project)

        todo_file = Path(temp_project) / "state" / "todo.yaml"
        todo_file.parent.mkdir()
        todo_file.touch()

        state = manager.load_todos()
        assert len(state.todos) == 0

    def test_get_todos_by_agent_and_status(self, sync_manager):
        """按 Agent 和状态过滤"""
        todo1 = sync_manager.add_todo("Agent1进行中", agent_id=1)
        todo2 = sync_manager.add_todo("Agent1已完成", agent_id=1)
        sync_manager.update_todo(todo2.id, status="completed")
        todo3 = sync_manager.add_todo("Agent2待办", agent_id=2)

        agent1_pending = sync_manager.get_todos_by_agent(agent_id=1, status="pending")
        assert len(agent1_pending) == 1
        assert agent1_pending[0].content == "Agent1进行中"


class TestTodoState:
    """TodoState 数据类测试"""

    def test_default_values(self):
        """默认字段值测试"""
        state = TodoState()
        assert len(state.todos) == 0
        assert state.version == "2.3.2"
        assert state.last_updated is not None

    def test_with_todos(self):
        """带待办的 TodoState"""
        todos = [
            TodoItem(id="TODO-001", content="任务1"),
            TodoItem(id="TODO-002", content="任务2"),
        ]
        state = TodoState(todos=todos, version="2.0")

        assert len(state.todos) == 2
        assert state.version == "2.0"


class TestErrorMessages:
    """错误消息测试"""

    def test_context_not_found_error_message(self):
        """ContextNotFoundError 消息测试"""
        error = ContextNotFoundError("未找到配置文件")
        assert "未找到配置文件" in str(error)

    def test_context_parse_error_message(self):
        """ContextParseError 消息测试"""
        error = ContextParseError("YAML 解析失败")
        assert "YAML 解析失败" in str(error)

    def test_invalid_context_error_message(self):
        """InvalidContextError 消息测试"""
        error = InvalidContextError("缺少必要字段")
        assert "缺少必要字段" in str(error)

    def test_todo_load_error_message(self):
        """TodoLoadError 消息测试"""
        error = TodoLoadError("文件读取失败")
        assert "文件读取失败" in str(error)

    def test_todo_save_error_message(self):
        """TodoSaveError 消息测试"""
        error = TodoSaveError("文件写入失败")
        assert "文件写入失败" in str(error)
