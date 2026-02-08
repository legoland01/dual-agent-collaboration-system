"""
测试用例：复现 BUG-20260208-007 todowrite无法可靠创建TODO
"""

import pytest
import subprocess
import yaml
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
TODO_FILE = PROJECT_ROOT / "state" / "agent_adhoc_todos.yaml"


class TestTodoWritePersistence:
    """测试 todowrite 命令的持久化能力"""

    def test_todowrite创建todo并保存到文件(self):
        """
        TC-BUG-007-001: todowrite应该正确创建TODO并保存到文件

        预期结果：
        - 命令执行成功
        - 文件被修改
        - TODO存在于文件中
        - git status显示文件已修改
        """
        # 获取执行前的状态
        with open(TODO_FILE) as f:
            data_before = yaml.safe_load(f)
        todos_before = len(data_before.get("adhoc_todos", []))

        # 执行 todowrite
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "todowrite",
             "--content", "测试todowrite持久化", "--priority", "high", "--agent", "2"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )

        print(f"命令输出: {result.stdout}")
        print(f"命令错误: {result.stderr}")
        print(f"返回码: {result.returncode}")

        # 验证1：命令成功
        assert result.returncode == 0, f"todowrite失败: {result.stderr}"

        # 验证2：文件被修改
        with open(TODO_FILE) as f:
            data_after = yaml.safe_load(f)
        todos_after = len(data_after.get("adhoc_todos", []))
        assert todos_after > todos_before, \
            f"文件未变化: 执行前={todos_before}, 执行后={todos_after}"

        # 验证3：TODO存在于文件中
        todo_contents = [t.get("content", "") for t in data_after.get("adhoc_todos", [])]
        assert any("测试todowrite持久化" in str(c) for c in todo_contents), \
            f"TODO不存在于文件中: {todo_contents}"

        # 验证4：git status显示文件已修改
        result3 = subprocess.run(
            ["git", "status", "--porcelain", str(TODO_FILE)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        print(f"git status: {result3.stdout}")
        assert "M" in result3.stdout or "A" in result3.stdout, \
            f"git status未显示文件修改: {result3.stdout}"

    def test_sync_with_rollback成功场景(self):
        """
        TC-BUG-007-002: 测试 sync_with_rollback 方法成功场景
        """
        from src.core.todo_sync_manager import TodoSyncManager, TodoItem

        manager = TodoSyncManager(str(PROJECT_ROOT))

        # 获取初始状态
        with open(TODO_FILE) as f:
            data_before = yaml.safe_load(f)
        todos_before = len(data_before.get("adhoc_todos", []))

        # 成功操作
        def success_operation():
            state = manager.load_todos()
            new_todo = TodoItem(
                id="TEST-SUCCESS",
                content="测试sync_with_rollback成功场景",
                priority="high",
            )
            state.todos.append(new_todo)
            manager.save_todos(state)

        result = manager.sync_with_rollback(success_operation)
        print(f"sync_with_rollback结果: {result}")

        assert result is True, "sync_with_rollback应该返回True"

        # 验证：文件已更新
        with open(TODO_FILE) as f:
            data_after = yaml.safe_load(f)
        todos_after = len(data_after.get("adhoc_todos", []))
        assert todos_after > todos_before, \
            f"成功操作后文件应该被修改: {todos_before} -> {todos_after}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
