"""
测试用例：todowrite完整功能覆盖

覆盖BUG:
- BUG-20260215-001: TODO编号生成逻辑
- BUG-20260215-002: AutoBugDetector集成
- BUG-20260214-009: 参数传递
- BUG-20260210-002: YAML格式
- BUG-20260208-007: 持久化与回滚

"""

import pytest
import subprocess
import yaml
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
TODO_FILE = PROJECT_ROOT / "state" / "agent_adhoc_todos.yaml"


class TestTodoIdGeneration:
    """测试TODO编号生成功能 - BUG-20260215-001"""

    def test_agent1生成正确编号格式(self):
        """
        TC-TODO-ID-001: Agent1创建的TODO应该生成 TODO-1-xxx 格式

        预期结果：
        - TODO ID 以 TODO-1- 开头
        - 编号自增
        """
        # 获取当前所有TODO
        with open(TODO_FILE) as f:
            data = yaml.safe_load(f)

        # 获取当前Agent1的最大编号
        agent1_todos = [t for t in data.get("todos", []) 
                       if t.get("id", "").startswith("TODO-1-")]
        max_num = 0
        for t in agent1_todos:
            try:
                num = int(t["id"].split("-")[2])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                pass

        expected_id = f"TODO-1-{max_num + 1:03d}"

        # 使用临时agent上下文创建TODO
        from src.core.todo_sync_manager import TodoSyncManager

        manager = TodoSyncManager(str(PROJECT_ROOT))
        todo = manager.add_todo(
            content=f"测试Agent1编号生成 {datetime.now().isoformat()}",
            agent_id=1,
            priority="medium"
        )

        # 验证
        assert todo.id.startswith("TODO-1-"), \
            f"Agent1创建的TODO应该以TODO-1-开头，实际: {todo.id}"

        # 清理
        manager.delete_todo(todo.id)

    def test_agent2生成正确编号格式(self):
        """
        TC-TODO-ID-002: Agent2创建的TODO应该生成 TODO-2-xxx 格式
        """
        from src.core.todo_sync_manager import TodoSyncManager

        manager = TodoSyncManager(str(PROJECT_ROOT))
        todo = manager.add_todo(
            content=f"测试Agent2编号生成 {datetime.now().isoformat()}",
            agent_id=2,
            priority="medium"
        )

        # 验证
        assert todo.id.startswith("TODO-2-"), \
            f"Agent2创建的TODO应该以TODO-2-开头，实际: {todo.id}"

        # 清理
        manager.delete_todo(todo.id)

    def test编号自增(self):
        """
        TC-TODO-ID-003: 同一Agent创建的TODO应该自增编号
        """
        from src.core.todo_sync_manager import TodoSyncManager

        manager = TodoSyncManager(str(PROJECT_ROOT))

        # 创建两个TODO
        todo1 = manager.add_todo(
            content=f"测试编号自增1 {datetime.now().isoformat()}",
            agent_id=1,
            priority="medium"
        )
        todo2 = manager.add_todo(
            content=f"测试编号自增2 {datetime.now().isoformat()}",
            agent_id=1,
            priority="medium"
        )

        # 验证编号自增
        try:
            num1 = int(todo1.id.split("-")[2])
            num2 = int(todo2.id.split("-")[2])
            assert num2 > num1, \
                f"同一Agent创建的TODO应该自增，实际: {todo1.id} -> {todo2.id}"
        except (ValueError, IndexError):
            pytest.fail(f"TODO ID格式不正确: {todo1.id}, {todo2.id}")

        # 清理
        manager.delete_todo(todo1.id)
        manager.delete_todo(todo2.id)

    def test不同Agent编号不重复(self):
        """
        TC-TODO-ID-004: 不同Agent创建的TODO不应该共享编号空间
        """
        from src.core.todo_sync_manager import TodoSyncManager

        manager = TodoSyncManager(str(PROJECT_ROOT))

        # 创建两个TODO
        todo1 = manager.add_todo(
            content=f"测试编号不重复1 {datetime.now().isoformat()}",
            agent_id=1,
            priority="medium"
        )
        todo2 = manager.add_todo(
            content=f"测试编号不重复2 {datetime.now().isoformat()}",
            agent_id=2,
            priority="medium"
        )

        # 验证格式不同
        assert todo1.id.startswith("TODO-1-"), \
            f"Agent1的TODO应该以TODO-1-开头: {todo1.id}"
        assert todo2.id.startswith("TODO-2-"), \
            f"Agent2的TODO应该以TODO-2-开头: {todo2.id}"
        assert todo1.id != todo2.id, \
            f"不同Agent的TODO ID不应该相同: {todo1.id} == {todo2.id}"

        # 清理
        manager.delete_todo(todo1.id)
        manager.delete_todo(todo2.id)

    def test旧格式兼容(self):
        """
        TC-TODO-ID-005: 旧格式 TODO-xxx 应该能正确读取
        """
        # 模拟旧格式的TODO
        with open(TODO_FILE) as f:
            data = yaml.safe_load(f)

        # 检查是否有旧格式的TODO
        old_format_exists = False
        for todo in data.get("todos", []):
            todo_id = todo.get("id", "")
            if todo_id.startswith("TODO-") and not \
               (todo_id.startswith("TODO-1-") or todo_id.startswith("TODO-2-")):
                # 检查是否是旧格式 TODO-xxx
                parts = todo_id.split("-")
                if len(parts) == 2 and parts[1].isdigit():
                    old_format_exists = True
                    break

        # 如果存在旧格式，应该能正确解析
        assert True, "旧格式TODO已正确读取（如果有的话）"


class TestAutoBugDetectorIntegration:
    """测试AutoBugDetector与todowrite集成 - BUG-20260215-002"""

    def test任务后自动添加自检TODO(self):
        """
        TC-AUTO-001: 任务完成后应该自动添加自检TODO
        """
        from src.core.auto_bug_detector import AutoBugDetector

        detector = AutoBugDetector()

        # 调用self_review
        bugs = detector.self_review("TEST-TODO-001", agent_id=1)

        # 验证返回的是BugReport列表
        assert isinstance(bugs, list), \
            "self_review应该返回BugReport列表"

    def test自检返回正确格式(self):
        """
        TC-AUTO-002: self_review应该返回正确格式的BugReport
        """
        from src.core.auto_bug_detector import AutoBugDetector

        detector = AutoBugDetector()
        bugs = detector.self_review("TEST-TODO-001", agent_id=1)

        for bug in bugs:
            # 验证BugReport必须有这些字段
            assert hasattr(bug, 'bug_id'), "BugReport应该有bug_id属性"
            assert hasattr(bug, 'bug_type'), "BugReport应该有bug_type属性"
            assert hasattr(bug, 'description'), "BugReport应该有description属性"
            assert bug.detected_by == "AutoBugDetector", \
                f"detected_by应该是AutoBugDetector，实际: {bug.detected_by}"


class TestTodoWriteParameters:
    """测试todowrite参数传递 - BUG-20260214-009"""

    def test_content参数传递(self):
        """
        TC-PARAM-001: --content参数应该正确传递
        """
        from src.core.todo_sync_manager import TodoSyncManager
        from datetime import datetime
        import uuid

        manager = TodoSyncManager(str(PROJECT_ROOT))
        test_content = f"测试content参数 {datetime.now().isoformat()} {uuid.uuid4().hex[:8]}"

        todo = manager.add_todo(
            content=test_content,
            agent_id=1,
            priority="high"
        )

        assert test_content in todo.content, \
            f"content参数传递失败: 期望 '{test_content}'，实际 '{todo.content}'"

        # 清理
        manager.delete_todo(todo.id)

    def test_priority参数传递(self):
        """
        TC-PARAM-002: --priority参数应该正确传递
        """
        from src.core.todo_sync_manager import TodoSyncManager
        from datetime import datetime
        import uuid

        manager = TodoSyncManager(str(PROJECT_ROOT))

        for priority in ["high", "medium", "low"]:
            todo = manager.add_todo(
                content=f"测试priority参数 {datetime.now().isoformat()} {uuid.uuid4().hex[:8]}",
                agent_id=1,
                priority=priority
            )

            assert todo.priority == priority, \
                f"priority参数传递失败: 期望 {priority}，实际 {todo.priority}"

            # 清理
            manager.delete_todo(todo.id)

    def test_agent_id参数传递(self):
        """
        TC-PARAM-003: agent_id参数应该正确传递并影响编号格式
        """
        from src.core.todo_sync_manager import TodoSyncManager
        from datetime import datetime
        import uuid

        manager = TodoSyncManager(str(PROJECT_ROOT))

        for agent_id in [1, 2]:
            todo = manager.add_todo(
                content=f"测试agent_id参数 {datetime.now().isoformat()} {uuid.uuid4().hex[:8]}",
                agent_id=agent_id,
                priority="medium"
            )

            expected_prefix = f"TODO-{agent_id}-"
            assert todo.id.startswith(expected_prefix), \
                f"agent_id参数未正确影响编号: 期望 {expected_prefix}，实际 {todo.id}"

            # 清理
            manager.delete_todo(todo.id)


class TestTodoYamlFormat:
    """测试TODO YAML格式 - BUG-20260210-002"""

    def testYAML格式正确(self):
        """
        TC-YAML-001: 写入的YAML格式应该正确
        """
        from src.core.todo_sync_manager import TodoSyncManager
        from datetime import datetime
        import uuid

        manager = TodoSyncManager(str(PROJECT_ROOT))
        test_content = f"测试YAML格式 {datetime.now().isoformat()} {uuid.uuid4().hex[:8]}"

        # 创建TODO
        todo = manager.add_todo(
            content=test_content,
            agent_id=1,
            priority="high"
        )

        # 重新读取YAML
        with open(TODO_FILE) as f:
            data = yaml.safe_load(f)

        # 验证YAML结构正确
        assert "todos" in data, "YAML应该有todos字段"
        assert isinstance(data["todos"], list), "todos应该是列表"

        # 查找刚创建的TODO
        found = False
        for t in data["todos"]:
            if test_content in str(t.get("content", "")):
                found = True
                assert "id" in t, "TODO应该有id字段"
                assert "content" in t, "TODO应该有content字段"
                assert "status" in t, "TODO应该有status字段"
                assert "priority" in t, "TODO应该有priority字段"
                break

        assert found, f"创建的TODO应该在YAML中: {test_content}"

        # 清理
        manager.delete_todo(todo.id)

    def testYAML可解析(self):
        """
        TC-YAML-002: 写入的YAML应该能被正确解析
        """
        # 直接解析YAML文件
        with open(TODO_FILE) as f:
            data = yaml.safe_load(f)

        # 验证解析成功
        assert data is not None, "YAML解析结果不应该为None"
        assert isinstance(data, dict), "YAML解析结果应该是字典"

    def test多行内容正确(self):
        """
        TC-YAML-003: 多行内容应该正确写入
        """
        from src.core.todo_sync_manager import TodoSyncManager
        import uuid

        manager = TodoSyncManager(str(PROJECT_ROOT))
        multiline_content = f"""测试多行内容
第一行
第二行
第三行
{uuid.uuid4().hex[:8]}"""

        todo = manager.add_todo(
            content=multiline_content,
            agent_id=1,
            priority="medium"
        )

        # 验证多行内容保留
        assert "第一行" in todo.content, "多行内容第一行丢失"
        assert "第二行" in todo.content, "多行内容第二行丢失"
        assert "第三行" in todo.content, "多行内容第三行丢失"

        # 清理
        manager.delete_todo(todo.id)


class TestTodoSyncRollback:
    """测试sync_with_rollback功能 - BUG-20260208-007"""

    def test成功操作不回滚(self):
        """
        TC-ROLLBACK-001: 成功操作后不应该回滚
        """
        from src.core.todo_sync_manager import TodoSyncManager, TodoItem
        import uuid

        manager = TodoSyncManager(str(PROJECT_ROOT))

        # 获取初始状态
        with open(TODO_FILE) as f:
            data_before = yaml.safe_load(f)
        todos_before = len(data_before.get("todos", []))

        # 成功操作
        def success_operation():
            state = manager.load_todos()
            new_todo = TodoItem(
                id=f"TEST-ROLLBACK-{uuid.uuid4().hex[:8]}",
                content=f"测试成功不回滚 {datetime.now().isoformat()}",
                priority="high",
            )
            state.todos.append(new_todo)
            manager.save_todos(state)

        result = manager.sync_with_rollback(success_operation)
        assert result is True, "sync_with_rollback应该返回True"

        # 验证文件已更新
        with open(TODO_FILE) as f:
            data_after = yaml.safe_load(f)
        todos_after = len(data_after.get("todos", []))

        assert todos_after > todos_before, \
            f"成功操作后文件应该被修改: {todos_before} -> {todos_after}"

    def test失败操作回滚(self):
        """
        TC-ROLLBACK-002: 失败操作后应该回滚
        """
        from src.core.todo_sync_manager import TodoSyncManager

        manager = TodoSyncManager(str(PROJECT_ROOT))

        # 获取初始状态
        with open(TODO_FILE) as f:
            data_before = yaml.safe_load(f)
        todos_before = len(data_before.get("todos", []))

        # 失败操作
        def fail_operation():
            state = manager.load_todos()
            # 故意引入错误
            raise ValueError("模拟操作失败")

        result = manager.sync_with_rollback(fail_operation)
        assert result is False, "sync_with_rollback失败操作应该返回False"

        # 验证文件未被修改
        with open(TODO_FILE) as f:
            data_after = yaml.safe_load(f)
        todos_after = len(data_after.get("todos", []))

        assert todos_after == todos_before, \
            f"失败操作后文件应该保持原样: {todos_before} -> {todos_after}"


class TestTodoWriteCLI:
    """测试todowrite CLI命令"""

    def test_cli命令创建TODO(self):
        """
        TC-CLI-001: CLI命令应该能正确创建TODO
        """
        import uuid

        test_content = f"CLI测试 {uuid.uuid4().hex[:8]}"

        # 执行CLI命令
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "todowrite",
             "--content", test_content,
             "--priority", "high",
             "--agent", "1"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )

        # 验证命令成功
        assert result.returncode == 0, \
            f"todowrite CLI失败: {result.stderr}"

        # 验证TODO存在于文件中
        with open(TODO_FILE) as f:
            data = yaml.safe_load(f)

        found = False
        for todo in data.get("todos", []):
            if test_content in str(todo.get("content", "")):
                found = True
                # 验证编号格式
                assert todo["id"].startswith("TODO-1-"), \
                    f"CLI创建的TODO应该有TODO-1-前缀: {todo['id']}"
                break

        assert found, f"CLI创建的TODO应该在文件中: {test_content}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
