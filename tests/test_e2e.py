"""端到端测试。

测试用例：
- 完整工作流测试
- 并发操作测试
- 异常场景测试
"""
import pytest
import tempfile
import os
import time
from pathlib import Path
import yaml

from src.core.state_validator import StateValidator
from src.core.state_migrator import StateMigrator
from src.core.exception_handler import (
    ExceptionHandler,
    ExceptionType,
    ExceptionSeverity,
    DiskSpaceChecker,
    PermissionChecker,
    NetworkError,
    DiskSpaceError,
    PermissionError,
    RetryConfig,
    with_retry
)


class TestExceptionHandling:
    """异常处理测试。"""

    def test_exception_classification_network(self):
        """测试网络异常分类。"""
        handler = ExceptionHandler(agent_id="test_agent")
        exc = NetworkError("Connection timeout", "git fetch")
        exc_type, severity = handler.classify_exception(exc)
        assert exc_type == ExceptionType.RETRYABLE

    def test_exception_classification_disk(self):
        """测试磁盘异常分类。"""
        handler = ExceptionHandler(agent_id="test_agent")
        exc = DiskSpaceError(50.0, 100.0, "/tmp")
        exc_type, severity = handler.classify_exception(exc)
        assert exc_type == ExceptionType.FATAL

    def test_exception_classification_permission(self):
        """测试权限异常分类。"""
        handler = ExceptionHandler(agent_id="test_agent")
        exc = PermissionError("/etc/passwd", "read")
        exc_type, severity = handler.classify_exception(exc)
        assert exc_type == ExceptionType.FATAL

    def test_exception_handler_registration(self):
        """测试异常处理器注册。"""
        handler = ExceptionHandler(agent_id="test_agent")
        
        def custom_handler(exc_info):
            pass
        
        handler.register_exception_handler(ExceptionType.RETRYABLE, custom_handler)
        assert ExceptionType.RETRYABLE in handler._exception_handlers

    def test_exception_handler_summary(self):
        """测试异常处理器统计摘要。"""
        handler = ExceptionHandler(agent_id="test_agent")
        summary = handler.get_exception_summary()
        
        assert "agent_id" in summary
        assert "current_phase" in summary
        assert "registered_handlers" in summary


class TestDiskSpaceChecker:
    """磁盘空间检查器测试。"""

    def test_sufficient_space(self):
        """测试空间充足情况。"""
        checker = DiskSpaceChecker(min_free_mb=1)
        assert checker.check() is True

    def test_low_space_warning(self):
        """测试空间不足警告。"""
        checker = DiskSpaceChecker(min_free_mb=999999999)
        result = checker.check()
        assert result is False

    def test_check_all_paths(self):
        """测试检查所有路径。"""
        checker = DiskSpaceChecker(min_free_mb=1, check_paths=["/", "/tmp"])
        assert checker.check_all() is True

    def test_get_free_space(self):
        """测试获取可用空间。"""
        checker = DiskSpaceChecker()
        free_space = checker.get_free_space()
        assert free_space > 0


class TestPermissionChecker:
    """权限检查器测试。"""

    def test_read_permission(self):
        """测试读权限检查。"""
        checker = PermissionChecker()
        assert checker.check_read(__file__) is True

    def test_write_permission(self):
        """测试写权限检查。"""
        checker = PermissionChecker()
        with tempfile.TemporaryDirectory() as tmpdir:
            assert checker.check_write(tmpdir) is True

    def test_check_all_permissions(self):
        """测试所有权限检查。"""
        checker = PermissionChecker()
        with tempfile.TemporaryDirectory() as tmpdir:
            assert checker.check_all(tmpdir) is True

    def test_invalid_path(self):
        """测试无效路径。"""
        checker = PermissionChecker()
        result = checker.check_read("/nonexistent/path/file.txt")
        assert result is False


class TestRetryDecorator:
    """重试装饰器测试。"""

    def test_retry_success(self):
        """测试重试成功。"""
        call_count = [0]
        
        @with_retry(RetryConfig(max_retries=2, initial_delay=0.01))
        def succeed_after_one():
            call_count[0] += 1
            if call_count[0] < 2:
                raise NetworkError("Temporary failure")
            return "success"
        
        result = succeed_after_one()
        assert result == "success"
        assert call_count[0] == 2

    def test_retry_exhausted(self):
        """测试重试耗尽。"""
        call_count = [0]
        
        @with_retry(RetryConfig(max_retries=2, initial_delay=0.01))
        def always_fail():
            call_count[0] += 1
            raise NetworkError("Always fails")
        
        with pytest.raises(NetworkError):
            always_fail()
        
        assert call_count[0] == 3

    def test_no_retry_on_other_exceptions(self):
        """测试其他异常不重试。"""
        call_count = [0]
        
        @with_retry(RetryConfig(max_retries=2, initial_delay=0.01))
        def raise_value_error():
            call_count[0] += 1
            raise ValueError("Not a network error")
        
        with pytest.raises(ValueError):
            raise_value_error()
        
        assert call_count[0] == 1


class TestFullWorkflow:
    """完整工作流测试。"""

    def test_complete_state_validation_workflow(self, tmp_path):
        """测试完整状态验证工作流。"""
        state_file = tmp_path / "project_state.yaml"
        
        state = {
            "version": "2.1.0",
            "project": {
                "name": "Test Project",
                "type": "PYTHON",
                "phase": "development"
            },
            "requirements": [{"version": "v1", "status": "approved"}],
            "design": [{"version": "v1", "status": "completed"}],
            "test": {"status": "pending"},
            "development": {"status": "in_progress"},
            "deployment": {"status": "pending"}
        }
        
        with open(state_file, 'w') as f:
            yaml.dump(state, f)
        
        validator = StateValidator()
        results = validator.validate(state)
        
        assert validator.is_valid()
        
        migrator = StateMigrator(str(state_file), dry_run=True)
        success, migrated = migrator.migrate(state)
        assert success

    def test_state_migration_workflow(self, tmp_path):
        """测试状态迁移工作流。"""
        state_file = tmp_path / "project_state.yaml"
        
        v1_state = {
            "version": "1.0",
            "phase": "development",
            "requirements": {"status": "approved"},
            "design": {"status": "completed"},
            "test": {"status": "pending"},
            "development": {"status": "in_progress"},
            "deployment": {"status": "pending"}
        }
        
        with open(state_file, 'w') as f:
            yaml.dump(v1_state, f)
        
        migrator = StateMigrator(str(state_file), dry_run=True)
        success, result = migrator.migrate(v1_state)
        
        assert success
        assert result["version"] == "2.1.0"
        assert "project" in result
        assert "iteration" in result

    def test_exception_handling_in_workflow(self, tmp_path):
        """测试工作流中的异常处理。"""
        state_file = tmp_path / "project_state.yaml"
        
        state = {
            "version": "2.0.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{}],
            "design": [{}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        with open(state_file, 'w') as f:
            yaml.dump(state, f)
        
        exception_handler = ExceptionHandler(agent_id="test_agent")
        
        with pytest.raises(NetworkError):
            def failing_operation():
                raise NetworkError("Network is down")
            
            exception_handler.handle_exception(failing_operation())

    def test_disk_check_before_write(self, tmp_path):
        """测试写入前磁盘检查。"""
        checker = DiskSpaceChecker(min_free_mb=1)
        
        assert checker.check() is True
        
        test_file = tmp_path / "test.txt"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        assert test_file.exists()


class TestConcurrentOperations:
    """并发操作测试。"""

    def test_multiple_validators(self):
        """测试多个验证器并行。"""
        validators = [StateValidator() for _ in range(5)]
        
        state = {
            "version": "2.0.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{}],
            "design": [{}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        for v in validators:
            results = v.validate(state)
            assert v.is_valid()

    def test_multiple_migrators(self):
        """测试多个迁移器并行。"""
        state = {
            "version": "2.1.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{}],
            "design": [{}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        migrators = [StateMigrator("state/project_state.yaml", dry_run=True) for _ in range(3)]
        
        for m in migrators:
            success, result = m.migrate(state)
            assert success
            assert result["version"] == "2.1.0"

    def test_multiple_exception_handlers(self):
        """测试多个异常处理器并行。"""
        handlers = [ExceptionHandler(agent_id=f"agent_{i}") for i in range(3)]
        
        for h in handlers:
            h.set_phase("testing")
            summary = h.get_exception_summary()
            assert summary["current_phase"] == "testing"

    def test_parallel_disk_and_permission_checks(self, tmp_path):
        """测试并行磁盘和权限检查。"""
        import concurrent.futures
        
        checker = DiskSpaceChecker(min_free_mb=1)
        perm_checker = PermissionChecker()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future1 = executor.submit(checker.check)
                future2 = executor.submit(perm_checker.check_all, tmpdir)
                
                result1 = future1.result()
                result2 = future2.result()
            
            assert result1 is True
            assert result2 is True


class TestExceptionHandlerIntegration:
    """异常处理集成测试。"""

    def test_context_manager_usage(self):
        """测试上下文管理器使用。"""
        handler = ExceptionHandler(agent_id="test_agent")
        
        with handler:
            pass
        
        assert handler.get_exception_summary()["agent_id"] == "test_agent"

    def test_notification_config(self):
        """测试通知配置。"""
        from src.core.exception_handler import NotificationConfig, NotificationChannel
        
        config = NotificationConfig(
            channel=NotificationChannel.LOG,
            min_severity=ExceptionSeverity.HIGH
        )
        
        handler = ExceptionHandler(agent_id="test_agent")
        handler.add_notification_config(config)
        
        assert len(handler._notification_configs) == 1

    def test_crash_history(self):
        """测试崩溃历史。"""
        handler = ExceptionHandler(agent_id="test_agent")
        
        history = handler.get_crash_history(limit=10)
        
        assert isinstance(history, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
