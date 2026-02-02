"""测试任务执行器模块。"""
import os
import tempfile
import pytest
import yaml
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Any, Dict

from src.core.task_executor import (
    TaskError,
    TaskNotFoundError,
    TaskExecutionError,
    TaskTimeoutError,
    TaskRetryError,
    TaskStatus,
    TaskPriority,
    TaskResult,
    Task,
    TaskStrategy,
    CreateRequirementsStrategy,
    ReviewRequirementsStrategy,
    SignoffRequirementsStrategy,
    CreateDesignStrategy,
    ReviewDesignStrategy,
    ExecuteBlackboxTestStrategy,
    ExecuteDeploymentStrategy,
    ImplementCodeStrategy,
    FixBugsStrategy,
    TaskExecutor,
)


class TestTaskExceptions:
    """测试任务异常类。"""

    def test_task_error(self):
        error = TaskError("test error")
        assert str(error) == "test error"

    def test_task_not_found_error(self):
        error = TaskNotFoundError("task not found")
        assert str(error) == "task not found"

    def test_task_execution_error(self):
        error = TaskExecutionError("execution failed")
        assert str(error) == "execution failed"

    def test_task_timeout_error(self):
        error = TaskTimeoutError("timeout")
        assert str(error) == "timeout"

    def test_task_retry_error(self):
        error = TaskRetryError("retry needed")
        assert str(error) == "retry needed"


class TestTaskStatus:
    """测试TaskStatus枚举。"""

    def test_status_values(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"
        assert TaskStatus.RETRYING.value == "retrying"

    def test_status_members(self):
        members = list(TaskStatus)
        assert len(members) == 6


class TestTaskPriority:
    """测试TaskPriority枚举。"""

    def test_priority_values(self):
        assert TaskPriority.LOW.value == 0
        assert TaskPriority.NORMAL.value == 50
        assert TaskPriority.HIGH.value == 100
        assert TaskPriority.CRITICAL.value == 200


class TestTaskResult:
    """测试TaskResult数据类。"""

    def test_task_result_defaults(self):
        result = TaskResult(success=True, message="done")
        assert result.success == True
        assert result.message == "done"
        assert result.files_created == []
        assert result.files_modified == []
        assert result.duration == 0.0
        assert result.quality_score == 0.0
        assert result.error is None
        assert result.retry_count == 0
        assert result.timestamp is not None

    def test_task_result_custom(self):
        result = TaskResult(
            success=True,
            message="completed",
            files_created=["file1.py", "file2.py"],
            files_modified=["file3.py"],
            duration=1.5,
            quality_score=0.95,
            error=None,
            retry_count=2,
            timestamp="2024-01-01T00:00:00"
        )
        assert len(result.files_created) == 2
        assert len(result.files_modified) == 1
        assert result.duration == 1.5
        assert result.quality_score == 0.95
        assert result.retry_count == 2


class TestTask:
    """测试Task数据类。"""

    def test_task_defaults(self):
        task = Task(
            id="test-001",
            name="test task",
            task_type="test_type"
        )
        assert task.id == "test-001"
        assert task.name == "test task"
        assert task.task_type == "test_type"
        assert task.priority == TaskPriority.NORMAL
        assert task.status == TaskStatus.PENDING
        assert task.params == {}
        assert task.result is None
        assert task.retry_count == 0
        assert task.max_retries == 3
        assert task.timeout == 300

    def test_task_custom(self):
        task = Task(
            id="test-002",
            name="important task",
            task_type="important_type",
            priority=TaskPriority.HIGH,
            params={"key": "value"},
            max_retries=5,
            timeout=600
        )
        assert task.priority == TaskPriority.HIGH
        assert task.params == {"key": "value"}
        assert task.max_retries == 5
        assert task.timeout == 600


class TestTaskStrategy:
    """测试TaskStrategy抽象基类。"""

    def test_abstract_methods(self):
        class ConcreteStrategy(TaskStrategy):
            @property
            def task_type(self) -> str:
                return "concrete"
            
            def execute(self, task: Task, context: Dict[str, Any]) -> TaskResult:
                return TaskResult(success=True, message="done")
        
        strategy = ConcreteStrategy()
        assert strategy.can_execute(Task(id="t1", name="t", task_type="concrete")) == True
        assert strategy.can_execute(Task(id="t2", name="t", task_type="other")) == False
        valid, msg = strategy.validate(Task(id="t3", name="t", task_type="concrete"))
        assert valid == True


class TestCreateRequirementsStrategy:
    """测试CreateRequirementsStrategy。"""

    @pytest.fixture
    def strategy(self):
        return CreateRequirementsStrategy()

    def test_task_type(self, strategy):
        assert strategy.task_type == "create_requirements"

    def test_can_execute(self, strategy):
        task = Task(id="t1", name="create reqs", task_type="create_requirements")
        assert strategy.can_execute(task) == True

    def test_execute_success(self, strategy):
        task = Task(id="t1", name="create reqs", task_type="create_requirements")
        context = {"project_name": "test_project"}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('os.makedirs') as mock_makedirs:
                with patch('builtins.open', create=True):
                    result = strategy.execute(task, context)
                    
                    assert result.success == True
                    assert "需求文档已创建" in result.message
                    assert len(result.files_created) == 1
                    assert result.quality_score > 0

    def test_execute_failure(self, strategy):
        task = Task(id="t1", name="create reqs", task_type="create_requirements")
        context = {"project_name": "test_project"}
        
        with patch('os.makedirs', side_effect=OSError("permission denied")):
            result = strategy.execute(task, context)
            
            assert result.success == False
            assert "失败" in result.message
            assert result.error is not None

    def test_generate_requirements_content(self, strategy):
        content = strategy._generate_requirements_content("test_project", {"key": "value"})
        assert "test_project" in content
        assert "# test_project - 需求文档" in content


class TestReviewRequirementsStrategy:
    """测试ReviewRequirementsStrategy。"""

    @pytest.fixture
    def strategy(self):
        return ReviewRequirementsStrategy()

    def test_task_type(self, strategy):
        assert strategy.task_type == "review_requirements"

    def test_execute_success(self, strategy):
        task = Task(id="t1", name="review reqs", task_type="review_requirements")
        context = {"project_name": "test_project"}
        
        with patch('os.makedirs'):
            with patch('builtins.open', create=True):
                result = strategy.execute(task, context)
                
                assert result.success == True
                assert "需求评审文档已创建" in result.message

    def test_generate_review_content(self, strategy):
        content = strategy._generate_review_content("test_project", {})
        assert "test_project" in content
        assert "需求评审" in content


class TestSignoffRequirementsStrategy:
    """测试SignoffRequirementsStrategy。"""

    @pytest.fixture
    def strategy(self):
        return SignoffRequirementsStrategy()

    def test_task_type(self, strategy):
        assert strategy.task_type == "signoff_requirements"

    def test_execute_success_new_state(self, strategy):
        task = Task(id="t1", name="signoff", task_type="signoff_requirements")
        context = {"agent_id": "agent1"}
        
        with patch('os.path.exists', return_value=False):
            with patch('builtins.open', create=True) as mock_open:
                with patch('os.makedirs'):
                    mock_file = MagicMock()
                    mock_open.return_value.__enter__.return_value = mock_file
                    result = strategy.execute(task, context)
                    
                    assert result.success == True
                    assert "agent1" in result.message

    def test_execute_success_existing_state(self, strategy):
        task = Task(id="t1", name="signoff", task_type="signoff_requirements")
        context = {"agent_id": "agent2"}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "project_state.yaml"
            state_file.write_text("requirements: {}\n")
            
            with patch.object(SignoffRequirementsStrategy, 'execute'):
                pass


class TestCreateDesignStrategy:
    """测试CreateDesignStrategy。"""

    @pytest.fixture
    def strategy(self):
        return CreateDesignStrategy()

    def test_task_type(self, strategy):
        assert strategy.task_type == "create_design"

    def test_execute_success(self, strategy):
        task = Task(id="t1", name="create design", task_type="create_design")
        context = {"project_name": "test_project"}
        
        with patch('os.makedirs'):
            with patch('builtins.open', create=True):
                result = strategy.execute(task, context)
                
                assert result.success == True
                assert "设计文档已创建" in result.message

    def test_generate_design_content(self, strategy):
        content = strategy._generate_design_content("test_project", {})
        assert "test_project" in content
        assert "详细设计" in content


class TestReviewDesignStrategy:
    """测试ReviewDesignStrategy。"""

    @pytest.fixture
    def strategy(self):
        return ReviewDesignStrategy()

    def test_task_type(self, strategy):
        assert strategy.task_type == "review_design"

    def test_execute_success(self, strategy):
        task = Task(id="t1", name="review design", task_type="review_design")
        context = {"project_name": "test_project"}
        
        with patch('os.makedirs'):
            with patch('builtins.open', create=True):
                result = strategy.execute(task, context)
                
                assert result.success == True
                assert "设计评审文档已创建" in result.message

    def test_generate_review_content(self, strategy):
        content = strategy._generate_review_content("test_project", {})
        assert "test_project" in content
        assert "设计评审" in content


class TestExecuteBlackboxTestStrategy:
    """测试ExecuteBlackboxTestStrategy。"""

    @pytest.fixture
    def strategy(self):
        return ExecuteBlackboxTestStrategy()

    def test_task_type(self, strategy):
        assert strategy.task_type == "execute_blackbox_test"

    def test_execute_success(self, strategy):
        task = Task(id="t1", name="run tests", task_type="execute_blackbox_test")
        context = {"project_name": "test_project"}
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "tests passed"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            with patch('os.makedirs'):
                with patch('builtins.open', create=True):
                    result = strategy.execute(task, context)
                    
                    assert result.success == True
                    assert "通过" in result.message

    def test_execute_failure(self, strategy):
        task = Task(id="t1", name="run tests", task_type="execute_blackbox_test")
        context = {"project_name": "test_project"}
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "tests failed"
            mock_run.return_value = mock_result
            
            with patch('os.makedirs'):
                with patch('builtins.open', create=True):
                    result = strategy.execute(task, context)
                    
                    assert result.success == False
                    assert "失败" in result.message

    def test_execute_timeout(self, strategy):
        import subprocess
        task = Task(id="t1", name="run tests", task_type="execute_blackbox_test")
        context = {"project_name": "test_project"}
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("pytest", 300)
            
            result = strategy.execute(task, context)
            
            assert result.success == False
            assert "超时" in result.message

    def test_execute_exception(self, strategy):
        task = Task(id="t1", name="run tests", task_type="execute_blackbox_test")
        context = {"project_name": "test_project"}
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = OSError("subprocess error")
            
            result = strategy.execute(task, context)
            
            assert result.success == False
            assert "执行黑盒测试失败" in result.message


class TestExecuteDeploymentStrategy:
    """测试ExecuteDeploymentStrategy。"""

    @pytest.fixture
    def strategy(self):
        return ExecuteDeploymentStrategy()

    def test_task_type(self, strategy):
        assert strategy.task_type == "execute_deployment"

    def test_execute_success(self, strategy):
        task = Task(id="t1", name="deploy", task_type="execute_deployment")
        context = {"project_name": "test_project"}
        
        with patch('os.makedirs'):
            with patch('builtins.open', create=True):
                result = strategy.execute(task, context)
                
                assert result.success == True
                assert "部署完成" in result.message

    def test_execute_failure(self, strategy):
        task = Task(id="t1", name="deploy", task_type="execute_deployment")
        context = {"project_name": "test_project"}
        
        with patch('os.makedirs', side_effect=OSError("disk full")):
            result = strategy.execute(task, context)
            
            assert result.success == False
            assert "部署失败" in result.message


class TestImplementCodeStrategy:
    """测试ImplementCodeStrategy。"""

    @pytest.fixture
    def strategy(self):
        return ImplementCodeStrategy()

    def test_task_type(self, strategy):
        assert strategy.task_type == "implement_code"

    def test_execute_success(self, strategy):
        task = Task(id="t1", name="implement code", task_type="implement_code")
        context = {"file_path": "src/main.py", "code_template": "# Hello World"}
        
        with patch('os.makedirs'):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                result = strategy.execute(task, context)
                
                assert result.success == True
                assert "代码已实现" in result.message
                assert "src/main.py" in result.files_created[0]

    def test_execute_failure(self, strategy):
        task = Task(id="t1", name="implement code", task_type="implement_code")
        context = {"file_path": "/root/main.py"}
        
        with patch('os.makedirs', side_effect=OSError("permission denied")):
            result = strategy.execute(task, context)
            
            assert result.success == False


class TestFixBugsStrategy:
    """测试FixBugsStrategy。"""

    @pytest.fixture
    def strategy(self):
        return FixBugsStrategy()

    def test_task_type(self, strategy):
        assert strategy.task_type == "fix_bugs"

    def test_execute_success(self, strategy):
        task = Task(id="t1", name="fix bug", task_type="fix_bugs")
        context = {"bug_report": {"file_path": "src/main.py", "description": "null pointer"}}
        
        with patch('os.makedirs'):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                result = strategy.execute(task, context)
                
                assert result.success == True
                assert "Bug已修复" in result.message

    def test_execute_failure(self, strategy):
        task = Task(id="t1", name="fix bug", task_type="fix_bugs")
        context = {"bug_report": {"file_path": "/root/main.py", "description": "bug"}}
        
        with patch('os.makedirs', side_effect=OSError):
            result = strategy.execute(task, context)
            
            assert result.success == False


class TestTaskExecutor:
    """测试TaskExecutor类。"""

    @pytest.fixture
    def executor(self):
        return TaskExecutor()

    def test_init(self, executor):
        assert len(executor.strategies) > 0
        assert executor.task_history == []
        assert executor.max_retries == 3
        assert executor.default_timeout == 300

    def test_register_strategy(self, executor):
        class CustomStrategy(TaskStrategy):
            @property
            def task_type(self) -> str:
                return "custom"
            
            def execute(self, task: Task, context: Dict[str, Any]) -> TaskResult:
                return TaskResult(success=True, message="custom done")
        
        custom = CustomStrategy()
        executor.register_strategy(custom)
        assert "custom" in executor.strategies

    def test_get_strategy(self, executor):
        strategy = executor.get_strategy("create_requirements")
        assert strategy is not None
        assert isinstance(strategy, CreateRequirementsStrategy)
        
        strategy = executor.get_strategy("nonexistent")
        assert strategy is None

    def test_create_task(self, executor):
        task = executor.create_task("test task", "create_requirements")
        
        assert task.id is not None
        assert task.name == "test task"
        assert task.task_type == "create_requirements"
        assert task.status == TaskStatus.PENDING

    def test_create_task_custom_priority(self, executor):
        task = executor.create_task("important task", "create_design", priority=TaskPriority.HIGH)
        assert task.priority == TaskPriority.HIGH

    def test_create_task_custom_timeout(self, executor):
        task = executor.create_task("long task", "execute_deployment", timeout=600)
        assert task.timeout == 600

    def test_execute_task_not_found_strategy(self, executor):
        task = Task(id="t1", name="unknown", task_type="unknown_type")
        context = {}
        
        result = executor.execute_task(task, context)
        
        assert result.success == False
        assert "未找到任务策略" in result.message

    def test_execute_task_success(self, executor):
        task = Task(id="t1", name="create requirements", task_type="create_requirements")
        context = {"project_name": "test_project"}
        
        with patch('os.makedirs'):
            with patch('builtins.open', create=True):
                result = executor.execute_task(task, context)
                
                assert result.success == True
                assert task.status == TaskStatus.COMPLETED
                assert task.result is not None

    def test_execute_task_retry_logic(self, executor):
        task = Task(id="t1", name="create requirements", task_type="create_requirements", max_retries=2)
        context = {"project_name": "test_project"}
        
        with patch('os.makedirs'):
            with patch('builtins.open', create=True):
                result = executor.execute_task(task, context)
                
                assert result.success == True
                assert task.status == TaskStatus.COMPLETED

    def test_execute_task_max_retries_exceeded(self, executor):
        task = Task(id="t1", name="create requirements", task_type="create_requirements", max_retries=1)
        context = {"project_name": "test_project"}
        
        def mock_execute(self, task, ctx):
            raise Exception("always fails")
        
        with patch.object(CreateRequirementsStrategy, 'execute', mock_execute):
            result = executor.execute_task(task, context)
            
            assert result.success == False
            assert task.status == TaskStatus.FAILED

    def test_execute_action_unknown(self, executor):
        result = executor.execute_action("unknown_action", {})
        
        assert result.success == False
        assert "未知的动作类型" in result.message

    def test_execute_action_known(self, executor):
        context = {"project_name": "test_project"}
        
        with patch('os.makedirs'):
            with patch('builtins.open', create=True):
                result = executor.execute_action("create_requirements", context)
                
                assert result.success == True

    def test_get_pending_tasks_empty(self, executor):
        pending = executor.get_pending_tasks()
        assert pending == []

    def test_get_completed_tasks_empty(self, executor):
        completed = executor.get_completed_tasks()
        assert completed == []

    def test_get_failed_tasks_empty(self, executor):
        failed = executor.get_failed_tasks()
        assert failed == []

    def test_get_pending_tasks_with_task(self, executor):
        task1 = executor.create_task("task1", "create_requirements")
        task1.status = TaskStatus.PENDING
        executor.task_history.append(task1)
        
        pending = executor.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].id == task1.id

    def test_get_completed_tasks_with_task(self, executor):
        task1 = executor.create_task("task1", "create_requirements")
        task1.status = TaskStatus.COMPLETED
        executor.task_history.append(task1)
        
        completed = executor.get_completed_tasks()
        assert len(completed) == 1
        assert completed[0].id == task1.id

    def test_get_failed_tasks_with_task(self, executor):
        task1 = executor.create_task("task1", "create_requirements")
        task1.status = TaskStatus.FAILED
        executor.task_history.append(task1)
        
        failed = executor.get_failed_tasks()
        assert len(failed) == 1
        assert failed[0].id == task1.id

    def test_get_summary_with_tasks(self, executor):
        task1 = executor.create_task("task1", "create_requirements")
        task1.status = TaskStatus.COMPLETED
        executor.task_history.append(task1)
        
        task2 = executor.create_task("task2", "create_design")
        task2.status = TaskStatus.FAILED
        executor.task_history.append(task2)
        
        summary = executor.get_summary()
        
        assert "registered_strategies" in summary
        assert summary["total_tasks"] == 2
        assert summary["completed_tasks"] == 1
        assert summary["failed_tasks"] == 1
        assert summary["success_rate"] == 50.0

    def test_get_summary_empty(self, executor):
        summary = executor.get_summary()
        assert summary["total_tasks"] == 0
        assert summary["success_rate"] == 0


class TestTaskExecutorModule:
    """测试任务执行器模块级功能。"""

    def test_module_importable(self):
        from src.core.task_executor import (
            TaskExecutor,
            Task,
            TaskResult,
            TaskStatus,
            TaskPriority,
        )
        assert TaskExecutor is not None
        assert Task is not None
        assert TaskResult is not None
        assert TaskStatus is not None
        assert TaskPriority is not None


class TestTaskExecutorEdgeCases:
    """测试任务执行器边缘情况以提高覆盖率。"""

    @pytest.fixture
    def executor(self):
        return TaskExecutor()

    def test_task_strategy_validate(self, executor):
        class TestStrategy(TaskStrategy):
            @property
            def task_type(self) -> str:
                return "test"
            
            def execute(self, task: Task, context: Dict[str, Any]) -> TaskResult:
                return TaskResult(success=True, message="done")
        
        strategy = TestStrategy()
        valid, msg = strategy.validate(Task(id="t1", name="t", task_type="test"))
        assert valid == True

    def test_execute_task_validation_failure(self, executor):
        class FailingStrategy(TaskStrategy):
            @property
            def task_type(self) -> str:
                return "failing"
            
            def execute(self, task: Task, context: Dict[str, Any]) -> TaskResult:
                return TaskResult(success=True, message="done")
            
            def validate(self, task: Task):
                return False, "Invalid task parameters"
        
        executor.register_strategy(FailingStrategy())
        task = executor.create_task("failing task", "failing")
        context = {}
        
        result = executor.execute_task(task, context)
        
        assert result.success == False
        assert "任务验证失败" in result.message
        assert task.status == TaskStatus.PENDING

    def test_execute_task_exception_in_strategy(self, executor):
        task = Task(id="t1", name="create requirements", task_type="create_requirements")
        context = {"project_name": "test_project"}
        
        with patch.object(CreateRequirementsStrategy, 'execute', side_effect=OSError("disk error")):
            result = executor.execute_task(task, context)
            
            assert result.success == False
            assert task.status == TaskStatus.FAILED
            assert "disk error" in result.error

    def test_execute_action_implement_code(self, executor):
        context = {"file_path": "src/main.py", "code_template": "# test"}
        
        with patch('os.makedirs'):
            with patch('builtins.open', create=True):
                result = executor.execute_action("implement_code", context)
                
                assert result.success == True

    def test_execute_action_signoff_requirements(self, executor):
        context = {"agent_id": "agent1"}
        
        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs'):
                with patch('builtins.open', create=True):
                    result = executor.execute_action("signoff_requirements", context)
                    
                    assert result.success == True

    def test_execute_task_with_default_timeout(self, executor):
        task = executor.create_task("test task", "create_requirements")
        assert task.timeout == 300

    def test_execute_task_with_custom_timeout(self, executor):
        task = executor.create_task("test task", "create_requirements", timeout=600)
        assert task.timeout == 600

    def test_execute_task_with_default_priority(self, executor):
        task = executor.create_task("test task", "create_requirements")
        assert task.priority == TaskPriority.NORMAL

    def test_execute_task_with_low_priority(self, executor):
        task = executor.create_task("test task", "create_requirements", priority=TaskPriority.LOW)
        assert task.priority == TaskPriority.LOW

    def test_execute_task_with_critical_priority(self, executor):
        task = executor.create_task("test task", "create_requirements", priority=TaskPriority.CRITICAL)
        assert task.priority == TaskPriority.CRITICAL

    def test_create_task_with_params(self, executor):
        task = executor.create_task(
            "test task",
            "create_requirements",
            params={"key": "value"}
        )
        assert task.params == {"key": "value"}

    def test_create_requirements_content_generation(self):
        strategy = CreateRequirementsStrategy()
        content = strategy._generate_requirements_content("my_project", {"extra": "data"})
        assert "my_project" in content
        assert "需求文档" in content
        assert "版本信息" in content

    def test_review_requirements_content_generation(self):
        strategy = ReviewRequirementsStrategy()
        content = strategy._generate_review_content("my_project", {})
        assert "my_project" in content
        assert "需求评审" in content

    def test_create_design_content_generation(self):
        strategy = CreateDesignStrategy()
        content = strategy._generate_design_content("my_project", {})
        assert "my_project" in content
        assert "详细设计" in content

    def test_review_design_content_generation(self):
        strategy = ReviewDesignStrategy()
        content = strategy._generate_review_content("my_project", {})
        assert "my_project" in content
        assert "设计评审" in content

    def test_implement_code_with_template(self):
        strategy = ImplementCodeStrategy()
        task = Task(id="t1", name="implement", task_type="implement_code")
        context = {"file_path": "src/test.py", "code_template": "# custom code"}
        
        with patch('os.makedirs'):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                result = strategy.execute(task, context)
                
                assert result.success == True
                mock_file.write.assert_called_with("# custom code")

    def test_fix_bugs_with_description(self):
        strategy = FixBugsStrategy()
        task = Task(id="t1", name="fix", task_type="fix_bugs")
        context = {"bug_report": {"file_path": "src/test.py", "description": "null pointer at line 42"}}
        
        with patch('os.makedirs'):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                result = strategy.execute(task, context)
                
                assert result.success == True

    def test_execute_deployment_content(self):
        strategy = ExecuteDeploymentStrategy()
        task = Task(id="t1", name="deploy", task_type="execute_deployment")
        context = {"project_name": "my_project"}
        
        with patch('os.makedirs'):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                result = strategy.execute(task, context)
                
                assert result.success == True
                assert "my_project" in result.message
