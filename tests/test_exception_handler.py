"""测试异常处理模块。"""
import json
import os
import shutil
import tempfile
import time
import traceback
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from typing import Any, Dict

from src.core.exception_handler import (
    ExceptionType,
    ExceptionSeverity,
    ExceptionHandlerError,
    UnhandledExceptionError,
    RecoveryError,
    NetworkError,
    DiskSpaceError,
    PermissionError,
    RetryConfig,
    ExceptionInfo,
    CrashInfo,
    NotificationChannel,
    NotificationConfig,
    ExceptionHandler,
    DiskSpaceChecker,
    PermissionChecker,
    with_retry,
)


class TestExceptionType:
    """测试ExceptionType枚举。"""

    def test_exception_type_values(self):
        assert ExceptionType.RETRYABLE.value == "retryable"
        assert ExceptionType.RECOVERABLE.value == "recoverable"
        assert ExceptionType.FATAL.value == "fatal"

    def test_exception_type_members(self):
        members = list(ExceptionType)
        assert len(members) == 3
        assert ExceptionType.RETRYABLE in members
        assert ExceptionType.RECOVERABLE in members
        assert ExceptionType.FATAL in members


class TestExceptionSeverity:
    """测试ExceptionSeverity枚举。"""

    def test_severity_values(self):
        assert ExceptionSeverity.LOW.value == 1
        assert ExceptionSeverity.MEDIUM.value == 2
        assert ExceptionSeverity.HIGH.value == 3
        assert ExceptionSeverity.CRITICAL.value == 4

    def test_severity_ordering(self):
        assert ExceptionSeverity.LOW.value < ExceptionSeverity.MEDIUM.value
        assert ExceptionSeverity.MEDIUM.value < ExceptionSeverity.HIGH.value
        assert ExceptionSeverity.HIGH.value < ExceptionSeverity.CRITICAL.value


class TestCustomExceptions:
    """测试自定义异常类。"""

    def test_network_error(self):
        error = NetworkError("connection failed", operation="fetch")
        assert str(error) == "connection failed"
        assert error.operation == "fetch"
        assert hasattr(error, 'timestamp')

    def test_network_error_default_operation(self):
        error = NetworkError("timeout")
        assert error.operation == "unknown"

    def test_disk_space_error(self):
        error = DiskSpaceError(50.0, 100.0, "/data")
        assert "50.0MB" in str(error)
        assert "100.0MB" in str(error)
        assert "/data" in str(error)
        assert error.free_mb == 50.0
        assert error.required_mb == 100.0
        assert error.path == "/data"

    def test_permission_error(self):
        error = PermissionError("/etc/passwd", "read")
        assert "/etc/passwd" in str(error)
        assert "read" in str(error)
        assert error.path == "/etc/passwd"
        assert error.operation == "read"

    def test_permission_error_default_operation(self):
        error = PermissionError("/some/path")
        assert error.operation == "access"

    def test_exception_handler_error(self):
        error = ExceptionHandlerError("test message")
        assert str(error) == "test message"

    def test_unhandled_exception_error(self):
        error = UnhandledExceptionError("unhandled")
        assert str(error) == "unhandled"

    def test_recovery_error(self):
        error = RecoveryError("recovery failed")
        assert str(error) == "recovery failed"


class TestRetryConfig:
    """测试RetryConfig类。"""

    def test_default_values(self):
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.timeout == 30

    def test_custom_values(self):
        config = RetryConfig(
            max_retries=5,
            initial_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
            timeout=60
        )
        assert config.max_retries == 5
        assert config.initial_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 3.0
        assert config.timeout == 60


class TestExceptionInfo:
    """测试ExceptionInfo数据类。"""

    def test_exception_info_creation(self):
        info = ExceptionInfo(
            exception_type=ExceptionType.RETRYABLE,
            severity=ExceptionSeverity.MEDIUM,
            message="test error",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={"key": "value"}
        )
        assert info.exception_type == ExceptionType.RETRYABLE
        assert info.severity == ExceptionSeverity.MEDIUM
        assert info.message == "test error"
        assert info.agent_id == "agent1"
        assert info.phase == "planning"
        assert info.context == {"key": "value"}
        assert info.stack_trace == ""
        assert info.exception_class == ""
        assert info.handled == False
        assert info.recovery_attempts == 0
        assert info.last_recovery_time is None

    def test_exception_info_with_stack_trace(self):
        info = ExceptionInfo(
            exception_type=ExceptionType.FATAL,
            severity=ExceptionSeverity.CRITICAL,
            message="fatal error",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent2",
            phase="execution",
            context={},
            stack_trace="Traceback...",
            exception_class="RuntimeError"
        )
        assert info.stack_trace == "Traceback..."
        assert info.exception_class == "RuntimeError"


class TestCrashInfo:
    """测试CrashInfo数据类。"""

    def test_crash_info_creation(self):
        crash_info = CrashInfo(
            crash_id="agent1_20240101_000000",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            last_action="git commit",
            state_version=5,
            pending_tasks=["task1", "task2"]
        )
        assert crash_info.crash_id == "agent1_20240101_000000"
        assert crash_info.agent_id == "agent1"
        assert crash_info.phase == "planning"
        assert crash_info.last_action == "git commit"
        assert crash_info.state_version == 5
        assert len(crash_info.pending_tasks) == 2
        assert crash_info.recovery_status == "pending"
        assert crash_info.recovery_attempts == 0

    def test_crash_info_with_exception(self):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RECOVERABLE,
            severity=ExceptionSeverity.HIGH,
            message="recoverable error",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="execution",
            context={}
        )
        crash_info = CrashInfo(
            crash_id="agent1_20240101_000000",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="execution",
            last_action="merge",
            state_version=3,
            pending_tasks=[],
            exception_info=exc_info
        )
        assert crash_info.exception_info == exc_info


class TestNotificationConfig:
    """测试NotificationConfig数据类。"""

    def test_notification_config_defaults(self):
        config = NotificationConfig(channel=NotificationChannel.LOG)
        assert config.channel == NotificationChannel.LOG
        assert config.enabled == True
        assert config.webhook_url is None
        assert config.email_recipients == []
        assert config.min_severity == ExceptionSeverity.MEDIUM

    def test_notification_config_custom(self):
        config = NotificationConfig(
            channel=NotificationChannel.WEBHOOK,
            enabled=False,
            webhook_url="https://example.com/webhook",
            email_recipients=["admin@example.com"],
            min_severity=ExceptionSeverity.HIGH
        )
        assert config.channel == NotificationChannel.WEBHOOK
        assert config.enabled == False
        assert config.webhook_url == "https://example.com/webhook"
        assert len(config.email_recipients) == 1


class TestExceptionHandler:
    """测试ExceptionHandler类。"""

    @pytest.fixture
    def temp_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            crash_dir = Path(tmpdir) / "crash_logs"
            recovery_dir = Path(tmpdir) / "recovery"
            crash_dir.mkdir()
            recovery_dir.mkdir()
            yield crash_dir, recovery_dir

    @pytest.fixture
    def handler(self, temp_dirs):
        crash_dir, recovery_dir = temp_dirs
        with patch.object(ExceptionHandler, 'CRASH_LOG_DIR', str(crash_dir)):
            with patch.object(ExceptionHandler, 'RECOVERY_DIR', str(recovery_dir)):
                handler = ExceptionHandler("agent1", "planning")
                yield handler

    def test_init(self, handler):
        assert handler.agent_id == "agent1"
        assert handler.current_phase == "planning"

    def test_ensure_directories(self, temp_dirs):
        crash_dir, recovery_dir = temp_dirs
        with patch.object(ExceptionHandler, 'CRASH_LOG_DIR', str(crash_dir)):
            with patch.object(ExceptionHandler, 'RECOVERY_DIR', str(recovery_dir)):
                with patch.object(ExceptionHandler, '_ensure_directories') as mock_ensure:
                    handler = ExceptionHandler("agent2", "execution")
                    mock_ensure.assert_called_once()

    def test_register_default_handlers(self, handler):
        assert ExceptionType.RETRYABLE in handler._exception_handlers
        assert ExceptionType.RECOVERABLE in handler._exception_handlers
        assert ExceptionType.FATAL in handler._exception_handlers

    def test_register_exception_handler(self, handler):
        def custom_handler(exc_info):
            return True, "custom handled"

        handler.register_exception_handler(ExceptionType.RETRYABLE, custom_handler)
        assert handler._exception_handlers[ExceptionType.RETRYABLE] == custom_handler

    def test_set_global_exception_handler(self, handler):
        def global_handler(exception, exc_info):
            pass

        handler.set_global_exception_handler(global_handler)
        assert handler._global_exception_handler == global_handler

    def test_add_notification_config(self, handler):
        config = NotificationConfig(channel=NotificationChannel.FILE)
        handler.add_notification_config(config)
        assert len(handler._notification_configs) == 1
        assert handler._notification_configs[0] == config

    def test_classify_exception_network(self, handler):
        error = NetworkError("connection timeout", operation="fetch")
        ex_type, severity = handler.classify_exception(error)
        assert ex_type == ExceptionType.RETRYABLE
        assert severity == ExceptionSeverity.MEDIUM

    def test_classify_exception_permission(self, handler):
        error = PermissionError("/root", "write")
        ex_type, severity = handler.classify_exception(error)
        assert ex_type == ExceptionType.FATAL
        assert severity == ExceptionSeverity.CRITICAL

    def test_classify_exception_disk_space(self, handler):
        error = DiskSpaceError(10, 100)
        ex_type, severity = handler.classify_exception(error)
        assert ex_type == ExceptionType.FATAL
        assert severity == ExceptionSeverity.CRITICAL

    def test_classify_exception_git_timeout(self, handler):
        error = Exception("git operation timeout")
        ex_type, severity = handler.classify_exception(error)
        assert ex_type == ExceptionType.RETRYABLE

    def test_classify_exception_state_lock(self, handler):
        error = Exception("state file lock conflict")
        ex_type, severity = handler.classify_exception(error)
        assert ex_type == ExceptionType.RECOVERABLE
        assert severity == ExceptionSeverity.HIGH

    def test_classify_exception_unknown(self, handler):
        error = Exception("some unknown error")
        ex_type, severity = handler.classify_exception(error)
        assert ex_type == ExceptionType.RECOVERABLE
        assert severity == ExceptionSeverity.MEDIUM

    def test_classify_exception_git_generic(self, handler):
        error = Exception("git merge conflict in branch")
        ex_type, severity = handler.classify_exception(error)
        assert ex_type == ExceptionType.RECOVERABLE
        assert severity == ExceptionSeverity.HIGH

    def test_handle_exception_retryable(self, handler):
        error = NetworkError("connection failed")
        with patch.object(handler, '_notify_exception'):
            with patch.object(handler, '_save_crash_log') as mock_save:
                with patch('time.sleep'):  # Skip actual sleep
                    success, message = handler.handle_exception(error)
                    assert success == True
                    assert "准备重试" in message
                    assert handler._current_exception is not None
                    mock_save.assert_not_called()  # Not called on first retry

    def test_handle_exception_recoverable(self, handler):
        error = Exception("state file corrupted")
        with patch.object(handler, '_notify_exception'):
            with patch.object(handler, '_save_crash_log'):
                with patch.object(handler, '_attempt_recovery', return_value=True):
                    success, message = handler.handle_exception(error)
                    assert success == True
                    assert "已恢复" in message

    def test_handle_exception_fatal(self, handler):
        error = PermissionError("/etc/shadow", "read")
        with patch.object(handler, '_notify_exception'):
            with patch.object(handler, '_save_crash_log'):
                with patch.object(handler, '_save_recovery_info'):
                    success, message = handler.handle_exception(error)
                    assert success == False
                    assert "致命异常" in message

    def test_handle_exception_with_context(self, handler):
        error = Exception("test error")
        context = {"task": "code_review", "file": "main.py"}
        with patch.object(handler, '_notify_exception'):
            with patch('time.sleep'):
                handler.handle_exception(error, context=context)
                assert handler._current_exception.context["task"] == "code_review"

    def test_handle_exception_with_phase(self, handler):
        error = Exception("test error")
        with patch.object(handler, '_notify_exception'):
            with patch('time.sleep'):
                handler.handle_exception(error, phase="execution")
                assert handler._current_exception.phase == "execution"

    def test_handle_exception_global_handler_called(self, handler):
        error = Exception("test error")
        global_handler = MagicMock()
        handler.set_global_exception_handler(global_handler)
        with patch.object(handler, '_notify_exception'):
            with patch('time.sleep'):
                handler.handle_exception(error)
                global_handler.assert_called_once()

    def test_handle_exception_no_handler(self, handler):
        del handler._exception_handlers[ExceptionType.RETRYABLE]
        error = NetworkError("test")
        with patch.object(handler, '_notify_exception'):
            success, message = handler.handle_exception(error)
            assert success == False
            assert "未找到异常处理器" in message

    def test_attempt_recovery_with_state_file(self, temp_dirs):
        crash_dir, recovery_dir = temp_dirs
        with patch.object(ExceptionHandler, 'CRASH_LOG_DIR', str(crash_dir)):
            with patch.object(ExceptionHandler, 'RECOVERY_DIR', str(recovery_dir)):
                handler = ExceptionHandler("agent1", "planning")

                state_file = Path("state") / "project_state.yaml"
                state_file.parent.mkdir(exist_ok=True)
                state_file.write_text("state_version: 1\n")

                exc_info = ExceptionInfo(
                    exception_type=ExceptionType.RECOVERABLE,
                    severity=ExceptionSeverity.HIGH,
                    message="test",
                    timestamp="2024-01-01T00:00:00",
                    agent_id="agent1",
                    phase="planning",
                    context={}
                )

                result = handler._attempt_recovery(exc_info)
                assert result == True

                import yaml
                state = yaml.safe_load(state_file.read_text())
                assert state['state_version'] == 2

                state_file.unlink()

    def test_attempt_recovery_no_state_file(self, temp_dirs):
        crash_dir, recovery_dir = temp_dirs
        with patch.object(ExceptionHandler, 'CRASH_LOG_DIR', str(crash_dir)):
            with patch.object(ExceptionHandler, 'RECOVERY_DIR', str(recovery_dir)):
                handler = ExceptionHandler("agent1", "planning")

                exc_info = ExceptionInfo(
                    exception_type=ExceptionType.RECOVERABLE,
                    severity=ExceptionSeverity.HIGH,
                    message="test",
                    timestamp="2024-01-01T00:00:00",
                    agent_id="agent1",
                    phase="planning",
                    context={}
                )

                result = handler._attempt_recovery(exc_info)
                assert result == True

    def test_save_crash_log(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RETRYABLE,
            severity=ExceptionSeverity.MEDIUM,
            message="test error",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={"last_action": "git commit", "state_version": 5},
            stack_trace="Traceback...",
            exception_class="NetworkError",
            recovery_attempts=2
        )

        with patch.object(handler, 'crash_log_dir', new_callable=lambda: Path(tempfile.gettempdir()) / 'crash_logs'):
            import os
            crash_dir = Path(tempfile.gettempdir()) / 'crash_logs'
            crash_dir.mkdir(exist_ok=True)
            handler.crash_log_dir = crash_dir

            crash_id = handler._save_crash_log(exc_info)
            assert crash_id.startswith("agent1_")

            crash_file = crash_dir / f"{crash_id}.json"
            assert crash_file.exists()

            with open(crash_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data["agent_id"] == "agent1"
                assert data["exception"]["message"] == "test error"
                assert data["exception"]["class"] == "NetworkError"

            crash_file.unlink()

    def test_save_recovery_info(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.FATAL,
            severity=ExceptionSeverity.CRITICAL,
            message="permission denied",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="execution",
            context={"state": {"phase": "planning"}}
        )

        with patch.object(handler, 'recovery_dir', new_callable=lambda: Path(tempfile.gettempdir()) / 'recovery'):
            recovery_dir = Path(tempfile.gettempdir()) / 'recovery'
            recovery_dir.mkdir(exist_ok=True)
            handler.recovery_dir = recovery_dir

            handler._save_recovery_info(exc_info)

            recovery_file = recovery_dir / "agent1_recovery.json"
            assert recovery_file.exists()

            with open(recovery_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data["agent_id"] == "agent1"
                assert data["required_action"] == "manual_intervention"

            recovery_file.unlink()

    def test_notify_exception_log_channel(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RECOVERABLE,
            severity=ExceptionSeverity.HIGH,
            message="test",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )

        config = NotificationConfig(
            channel=NotificationChannel.LOG,
            min_severity=ExceptionSeverity.LOW
        )
        handler.add_notification_config(config)

        with patch('src.core.exception_handler.logger') as mock_logger:
            handler._notify_exception(exc_info)
            mock_logger.warning.assert_called()

    def test_notify_exception_file_channel(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RECOVERABLE,
            severity=ExceptionSeverity.HIGH,
            message="test error",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )

        config = NotificationConfig(
            channel=NotificationChannel.FILE,
            min_severity=ExceptionSeverity.LOW
        )
        handler.add_notification_config(config)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            notification_file = f.name

        try:
            with patch('src.core.exception_handler.Path') as mock_path:
                mock_path.return_value = Path(notification_file)
                with patch('builtins.open', create=True) as mock_open:
                    mock_file = MagicMock()
                    mock_open.return_value.__enter__.return_value = mock_file
                    handler._notify_exception(exc_info)
        finally:
            if os.path.exists(notification_file):
                os.unlink(notification_file)

    def test_notify_exception_disabled_channel(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RECOVERABLE,
            severity=ExceptionSeverity.HIGH,
            message="test",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )

        config = NotificationConfig(
            channel=NotificationChannel.LOG,
            enabled=False
        )
        handler.add_notification_config(config)

        with patch('src.core.exception_handler.logger') as mock_logger:
            handler._notify_exception(exc_info)
            mock_logger.warning.assert_not_called()

    def test_notify_exception_low_severity_skipped(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RECOVERABLE,
            severity=ExceptionSeverity.LOW,
            message="test",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )

        config = NotificationConfig(
            channel=NotificationChannel.LOG,
            min_severity=ExceptionSeverity.HIGH
        )
        handler.add_notification_config(config)

        with patch('src.core.exception_handler.logger') as mock_logger:
            handler._notify_exception(exc_info)
            mock_logger.warning.assert_not_called()

    def test_save_crash_context(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RETRYABLE,
            severity=ExceptionSeverity.MEDIUM,
            message="test",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )
        handler._current_exception = exc_info

        handler.save_crash_context(10, ["task1", "task2"])

        assert exc_info.context["state_version"] == 10
        assert exc_info.context["pending_tasks"] == ["task1", "task2"]

    def test_get_crash_history(self, handler):
        with patch.object(handler, 'crash_log_dir', new_callable=lambda: Path(tempfile.gettempdir()) / 'crash_logs'):
            crash_dir = Path(tempfile.gettempdir()) / 'crash_logs'
            crash_dir.mkdir(exist_ok=True)
            handler.crash_log_dir = crash_dir

            for i in range(3):
                crash_file = crash_dir / f"agent1_20240101_00000{i}.json"
                with open(crash_file, 'w') as f:
                    json.dump({"crash_id": f"crash_{i}", "data": "test"}, f)

            history = handler.get_crash_history(limit=2)

            assert len(history) == 2

            for crash_file in crash_dir.glob("*.json"):
                crash_file.unlink()

    def test_clear_old_crashes(self, handler):
        with patch.object(handler, 'crash_log_dir', new_callable=lambda: Path(tempfile.gettempdir()) / 'crash_logs'):
            crash_dir = Path(tempfile.gettempdir()) / 'crash_logs'
            crash_dir.mkdir(exist_ok=True)
            handler.crash_log_dir = crash_dir

            old_file = crash_dir / "old_crash.json"
            with open(old_file, 'w') as f:
                json.dump({}, f)
            old_time = time.time() - (8 * 24 * 60 * 60)
            os.utime(old_file, (old_time, old_time))

            new_file = crash_dir / "new_crash.json"
            with open(new_file, 'w') as f:
                json.dump({}, f)

            removed = handler.clear_old_crashes(days=7)

            assert removed == 1
            assert not old_file.exists()
            assert new_file.exists()

            new_file.unlink()

    def test_get_exception_summary(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RETRYABLE,
            severity=ExceptionSeverity.MEDIUM,
            message="test error",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )
        handler._current_exception = exc_info

        summary = handler.get_exception_summary()

        assert summary["agent_id"] == "agent1"
        assert summary["current_phase"] == "planning"
        assert ExceptionType.RETRYABLE in summary["registered_handlers"]
        assert summary["current_exception"]["type"] == "retryable"
        assert summary["current_exception"]["message"] == "test error"

    def test_set_phase(self, handler):
        handler.set_phase("execution")
        assert handler.current_phase == "execution"

    def test_reset(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RETRYABLE,
            severity=ExceptionSeverity.MEDIUM,
            message="test",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )
        handler._current_exception = exc_info
        handler._retry_count = 5

        handler.reset()

        assert handler._current_exception is None
        assert handler._retry_count == 0

    def test_context_manager_success(self, handler):
        with handler:
            pass

        assert handler._current_exception is None

    def test_context_manager_with_exception(self, handler):
        with pytest.raises(ValueError):
            with handler:
                raise ValueError("test error")

        assert handler._current_exception is not None
        assert handler._current_exception.exception_class == "ValueError"


class TestDiskSpaceChecker:
    """测试DiskSpaceChecker类。"""

    @pytest.fixture
    def checker(self):
        return DiskSpaceChecker(min_free_mb=100, check_paths=["/tmp"])

    def test_init_default(self):
        checker = DiskSpaceChecker()
        assert checker.min_free_mb == 100
        assert checker.check_paths == ["/"]

    def test_init_custom(self):
        checker = DiskSpaceChecker(min_free_mb=500, check_paths=["/data", "/home"])
        assert checker.min_free_mb == 500
        assert len(checker.check_paths) == 2

    def test_check_sufficient_space(self, checker):
        with patch('shutil.disk_usage') as mock_usage:
            mock_usage.return_value = MagicMock(free=200 * 1024 * 1024)
            result = checker.check("/tmp")
            assert result == True

    def test_check_insufficient_space(self, checker):
        with patch('shutil.disk_usage') as mock_usage:
            mock_usage.return_value = MagicMock(free=50 * 1024 * 1024)
            result = checker.check("/tmp")
            assert result == False

    def test_check_oserror(self, checker):
        with patch('shutil.disk_usage') as mock_usage:
            mock_usage.side_effect = OSError("permission denied")
            result = checker.check("/tmp")
            assert result == True

    def test_check_default_path(self, checker):
        with patch('shutil.disk_usage') as mock_usage:
            mock_usage.return_value = MagicMock(free=200 * 1024 * 1024)
            result = checker.check()
            assert result == True
            mock_usage.assert_called_with("/tmp")

    def test_check_all_all_sufficient(self, checker):
        with patch('shutil.disk_usage') as mock_usage:
            mock_usage.return_value = MagicMock(free=200 * 1024 * 1024)
            result = checker.check_all()
            assert result == True

    def test_check_all_one_insufficient(self, checker):
        with patch('shutil.disk_usage') as mock_usage:
            mock_usage.return_value = MagicMock(free=50 * 1024 * 1024)
            result = checker.check_all()
            assert result == False

    def test_get_free_space_success(self):
        checker = DiskSpaceChecker(min_free_mb=100, check_paths=["/tmp"])
        with patch('shutil.disk_usage') as mock_usage:
            mock_usage.return_value = MagicMock(free=150.5 * 1024 * 1024)
            free_space = checker.get_free_space("/tmp")
            assert free_space == 150.5

    def test_get_free_space_error(self):
        checker = DiskSpaceChecker(min_free_mb=100, check_paths=["/tmp"])
        with patch('shutil.disk_usage') as mock_usage:
            mock_usage.side_effect = OSError
            free_space = checker.get_free_space("/tmp")
            assert free_space == -1


class TestPermissionChecker:
    """测试PermissionChecker类。"""

    @pytest.fixture
    def checker(self):
        return PermissionChecker()

    def test_init(self, checker):
        assert checker.checked_paths == {}

    def test_check_read_file_success(self, checker):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test")
            temp_path = f.name

        try:
            result = checker.check_read(temp_path)
            assert result == True
            assert temp_path in checker.checked_paths
            assert checker.checked_paths[temp_path] == ("read", True)
        finally:
            os.unlink(temp_path)

    def test_check_read_file_fail(self, checker):
        with patch('os.path.isfile', return_value=False):
            with patch('os.listdir', side_effect=PermissionError("permission denied")):
                result = checker.check_read("/some/path")
                assert result == False

    def test_check_read_dir_success(self, checker):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = checker.check_read(tmpdir)
            assert result == True

    def test_check_write_success(self, checker):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = checker.check_write(tmpdir)
            assert result == True

    def test_check_write_fail(self, checker):
        with patch('builtins.open', side_effect=PermissionError("/some/path", "write")):
            result = checker.check_write("/some/path")
            assert result == False

    def test_check_execute_success(self, checker):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = checker.check_execute(tmpdir)
            assert result == True

    def test_check_execute_with_oserror(self, checker):
        with patch('os.access', side_effect=OSError):
            result = checker.check_execute("/some/path")
            assert result == False

    def test_check_all_file(self, checker):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test")
            temp_path = f.name

        try:
            result = checker.check_all(temp_path)
            assert result == True
        finally:
            os.unlink(temp_path)

    def test_check_all_directory(self, checker):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = checker.check_all(tmpdir)
            assert result == True

    def test_get_checked_paths(self, checker):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test")
            temp_path = f.name

        try:
            checker.check_read(temp_path)
            paths = checker.get_checked_paths()
            assert temp_path in paths
        finally:
            os.unlink(temp_path)


class TestWithRetryDecorator:
    """测试with_retry装饰器。"""

    def test_decorator_success_first_try(self):
        @with_retry(RetryConfig(max_retries=3, initial_delay=0.01))
        def success_func():
            return "success"

        result = success_func()
        assert result == "success"

    def test_decorator_success_after_retries(self):
        call_count = 0

        @with_retry(RetryConfig(max_retries=3, initial_delay=0.01))
        def eventually_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("temporary failure")
            return "success"

        result = eventually_success()
        assert result == "success"
        assert call_count == 3

    def test_decorator_final_failure(self):
        @with_retry(RetryConfig(max_retries=2, initial_delay=0.01))
        def always_fail():
            raise NetworkError("always fails")

        with pytest.raises(NetworkError):
            always_fail()

    def test_decorator_non_network_error_not_retried(self):
        call_count = 0

        @with_retry(RetryConfig(max_retries=3, initial_delay=0.01))
        def raise_value_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("not a network error")

        with pytest.raises(ValueError):
            raise_value_error()

        assert call_count == 1

    def test_decorator_default_config(self):
        @with_retry()
        def success_func():
            return "success"

        result = success_func()
        assert result == "success"


class TestExceptionHandlerModule:
    """测试异常处理器模块级功能。"""

    def test_module_importable(self):
        from src.core.exception_handler import (
            ExceptionType,
            ExceptionSeverity,
            ExceptionHandler,
            DiskSpaceChecker,
            PermissionChecker,
            with_retry,
        )
        assert ExceptionType is not None
        assert ExceptionSeverity is not None
        assert ExceptionHandler is not None
        assert DiskSpaceChecker is not None
        assert PermissionChecker is not None
        assert with_retry is not None


class TestExceptionHandlerEdgeCases:
    """测试异常处理器边缘情况以提高覆盖率。"""

    @pytest.fixture
    def temp_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            crash_dir = Path(tmpdir) / "crash_logs"
            recovery_dir = Path(tmpdir) / "recovery"
            crash_dir.mkdir()
            recovery_dir.mkdir()
            yield crash_dir, recovery_dir

    @pytest.fixture
    def handler(self, temp_dirs):
        crash_dir, recovery_dir = temp_dirs
        with patch.object(ExceptionHandler, 'CRASH_LOG_DIR', str(crash_dir)):
            with patch.object(ExceptionHandler, 'RECOVERY_DIR', str(recovery_dir)):
                handler = ExceptionHandler("agent1", "planning")
                yield handler

    def test_classify_exception_default(self, handler):
        error = Exception("completely random error with no keywords")
        ex_type, severity = handler.classify_exception(error)
        assert ex_type == ExceptionType.RECOVERABLE
        assert severity == ExceptionSeverity.MEDIUM

    def test_handle_recoverable_recovery_failure(self, handler):
        error = Exception("state file corrupted")
        with patch.object(handler, '_save_crash_log'):
            with patch.object(handler, '_attempt_recovery', return_value=False):
                with patch.object(handler, '_notify_exception'):
                    success, message = handler.handle_exception(error)
                    assert success == False
                    assert "恢复失败" in message

    def test_attempt_recovery_exception(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RECOVERABLE,
            severity=ExceptionSeverity.HIGH,
            message="test",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )

        state_file = Path("state") / "project_state.yaml"
        state_file.parent.mkdir(exist_ok=True)
        state_file.write_text("invalid: yaml: content: [")

        try:
            result = handler._attempt_recovery(exc_info)
            assert result == False
        finally:
            if state_file.exists():
                state_file.unlink()

    def test_notify_webhook(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RECOVERABLE,
            severity=ExceptionSeverity.HIGH,
            message="test error",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )

        config = NotificationConfig(
            channel=NotificationChannel.WEBHOOK,
            webhook_url="https://example.com/webhook",
            min_severity=ExceptionSeverity.LOW
        )
        handler.add_notification_config(config)

        with patch('requests.post') as mock_post:
            handler._notify_webhook(exc_info, config)
            mock_post.assert_called_once()

    def test_notify_webhook_no_url(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RECOVERABLE,
            severity=ExceptionSeverity.HIGH,
            message="test",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )

        config = NotificationConfig(
            channel=NotificationChannel.WEBHOOK,
            webhook_url=None,
            min_severity=ExceptionSeverity.LOW
        )

        handler._notify_webhook(exc_info, config)

    def test_notify_webhook_failure(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RECOVERABLE,
            severity=ExceptionSeverity.HIGH,
            message="test error",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )

        config = NotificationConfig(
            channel=NotificationChannel.WEBHOOK,
            webhook_url="https://example.com/webhook",
            min_severity=ExceptionSeverity.LOW
        )
        handler.add_notification_config(config)

        with patch('requests.post', side_effect=Exception("network error")):
            handler._notify_webhook(exc_info, config)

    def test_clear_old_crashes_with_files(self, handler):
        with patch.object(handler, 'crash_log_dir', new_callable=lambda: Path(tempfile.gettempdir()) / 'crash_logs'):
            crash_dir = Path(tempfile.gettempdir()) / 'crash_logs'
            crash_dir.mkdir(exist_ok=True)
            handler.crash_log_dir = crash_dir

            old_file = crash_dir / "old_crash.json"
            with open(old_file, 'w') as f:
                json.dump({}, f)
            old_time = time.time() - (8 * 24 * 60 * 60)
            os.utime(old_file, (old_time, old_time))

            new_file = crash_dir / "new_crash.json"
            with open(new_file, 'w') as f:
                json.dump({}, f)

            removed = handler.clear_old_crashes(days=7)

            assert removed == 1
            assert not old_file.exists()
            assert new_file.exists()

            new_file.unlink()

    def test_with_retry_final_failure(self):
        @with_retry(RetryConfig(max_retries=2, initial_delay=0.01))
        def always_fail():
            raise NetworkError("always fails")

        with pytest.raises(NetworkError):
            always_fail()

    def test_notify_exception_notification_failure(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RECOVERABLE,
            severity=ExceptionSeverity.HIGH,
            message="test",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )

        config = NotificationConfig(
            channel=NotificationChannel.LOG,
            min_severity=ExceptionSeverity.LOW
        )
        handler.add_notification_config(config)

        with patch('src.core.exception_handler.logger') as mock_logger:
            mock_logger.warning.side_effect = Exception("logging error")
            handler._notify_exception(exc_info)

    def test_classify_exception_git_only(self, handler):
        error = Exception("some git operation completed")
        ex_type, severity = handler.classify_exception(error)
        assert ex_type == ExceptionType.RETRYABLE
        assert severity == ExceptionSeverity.MEDIUM

    def test_handle_retryable_max_retries_reached(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RETRYABLE,
            severity=ExceptionSeverity.MEDIUM,
            message="connection failed",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={},
            recovery_attempts=3
        )

        with patch.object(handler, '_save_crash_log') as mock_save:
            with patch.object(handler, '_notify_exception'):
                with patch('time.sleep'):
                    success, message = handler._handle_retryable(exc_info)
                    assert success == False
                    assert "最大重试次数" in message
                    mock_save.assert_called()

    def test_notify_file_with_exception(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RECOVERABLE,
            severity=ExceptionSeverity.HIGH,
            message="test error",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )

        config = NotificationConfig(
            channel=NotificationChannel.FILE,
            min_severity=ExceptionSeverity.LOW
        )
        handler.add_notification_config(config)

        with patch('builtins.open', side_effect=OSError("disk full")):
            handler._notify_exception(exc_info)

    def test_notify_via_exception_handler_webhook(self, handler):
        exc_info = ExceptionInfo(
            exception_type=ExceptionType.RECOVERABLE,
            severity=ExceptionSeverity.HIGH,
            message="test error",
            timestamp="2024-01-01T00:00:00",
            agent_id="agent1",
            phase="planning",
            context={}
        )

        config = NotificationConfig(
            channel=NotificationChannel.WEBHOOK,
            webhook_url="https://example.com/webhook",
            min_severity=ExceptionSeverity.LOW
        )
        handler.add_notification_config(config)

        with patch('requests.post') as mock_post:
            handler._notify_exception(exc_info)
            mock_post.assert_called_once()

    def test_get_crash_history_with_corrupt_file(self, handler):
        with patch.object(handler, 'crash_log_dir', new_callable=lambda: Path(tempfile.gettempdir()) / 'crash_logs'):
            crash_dir = Path(tempfile.gettempdir()) / 'crash_logs'
            crash_dir.mkdir(exist_ok=True)
            handler.crash_log_dir = crash_dir

            corrupt_file = crash_dir / "corrupt_crash.json"
            with open(corrupt_file, 'w') as f:
                f.write("{invalid json: content: [")

            valid_file = crash_dir / "valid_crash.json"
            with open(valid_file, 'w') as f:
                json.dump({"crash_id": "valid", "data": "test"}, f)

            history = handler.get_crash_history(limit=10)

            assert len(history) == 1
            assert history[0]["crash_id"] == "valid"

            corrupt_file.unlink()
            valid_file.unlink()
