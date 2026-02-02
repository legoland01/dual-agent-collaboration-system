"""ProcessSupervisor 单元测试。

测试用例：
- 监管配置
- 进程启动和停止
- 重启机制
"""
import pytest
import tempfile
import time
from pathlib import Path
from datetime import datetime


class TestSupervisorConfig:
    """SupervisorConfig 测试。"""

    def test_default_config(self):
        """测试默认配置。"""
        from src.core.supervisor import SupervisorConfig

        config = SupervisorConfig()
        assert config.max_restarts == 5
        assert config.time_window == 3600
        assert config.backoff_factor == 2.0
        assert config.max_backoff == 60.0
        assert config.initial_delay == 1.0

    def test_custom_config(self):
        """测试自定义配置。"""
        from src.core.supervisor import SupervisorConfig

        config = SupervisorConfig(
            max_restarts=10,
            time_window=7200,
            backoff_factor=3.0,
            max_backoff=120.0,
            initial_delay=0.5
        )
        assert config.max_restarts == 10
        assert config.time_window == 7200
        assert config.backoff_factor == 3.0
        assert config.max_backoff == 120.0
        assert config.initial_delay == 0.5


class TestProcessSupervisor:
    """ProcessSupervisor 测试。"""

    def test_initialization(self, tmp_path):
        """测试初始化。"""
        from src.core.supervisor import ProcessSupervisor, SupervisorConfig

        config = SupervisorConfig()
        supervisor = ProcessSupervisor(str(tmp_path), config)

        assert supervisor.project_path == tmp_path
        assert supervisor.config == config
        assert supervisor.restart_count == 0
        assert supervisor.is_running is False
        assert supervisor.process is None

    def test_initialization_default_config(self, tmp_path):
        """测试使用默认配置初始化。"""
        from src.core.supervisor import ProcessSupervisor

        supervisor = ProcessSupervisor(str(tmp_path))

        assert supervisor.config is not None
        assert supervisor.config.max_restarts == 5

    def test_get_status_not_running(self, tmp_path):
        """测试获取未运行进程的状态。"""
        from src.core.supervisor import ProcessSupervisor

        supervisor = ProcessSupervisor(str(tmp_path))
        status = supervisor.get_status()

        assert status["is_running"] is False
        assert status["restart_count"] == 0

    def test_get_status_running(self, tmp_path):
        """测试获取运行中进程的状态。"""
        from src.core.supervisor import ProcessSupervisor

        supervisor = ProcessSupervisor(str(tmp_path))
        supervisor.is_running = True
        supervisor.restart_count = 3
        supervisor.start_time = datetime.now()

        status = supervisor.get_status()

        assert status["is_running"] is True
        assert status["restart_count"] == 3

    def test_stop_not_running(self, tmp_path):
        """测试停止未运行的进程。"""
        from src.core.supervisor import ProcessSupervisor

        supervisor = ProcessSupervisor(str(tmp_path))
        result = supervisor.stop()

        assert result is True
        assert supervisor.is_running is False

    def test_increment_restart_count(self, tmp_path):
        """测试增加重启计数。"""
        from src.core.supervisor import ProcessSupervisor

        supervisor = ProcessSupervisor(str(tmp_path))
        assert supervisor.restart_count == 0

        supervisor.restart_count += 1
        assert supervisor.restart_count == 1

        supervisor.restart_count += 1
        assert supervisor.restart_count == 2

    def test_should_start_under_limit(self, tmp_path):
        """测试在限制内应该启动。"""
        from src.core.supervisor import ProcessSupervisor, SupervisorConfig

        config = SupervisorConfig(max_restarts=3)
        supervisor = ProcessSupervisor(str(tmp_path), config)
        supervisor.restart_count = 2

        assert supervisor.should_start() is True

    def test_should_start_at_limit(self, tmp_path):
        """测试达到限制时不应该启动。"""
        from src.core.supervisor import ProcessSupervisor, SupervisorConfig

        config = SupervisorConfig(max_restarts=3)
        supervisor = ProcessSupervisor(str(tmp_path), config)
        supervisor.restart_count = 3

        assert supervisor.should_start() is False

    def test_should_start_over_limit(self, tmp_path):
        """测试超过限制时不应该启动。"""
        from src.core.supervisor import ProcessSupervisor, SupervisorConfig

        config = SupervisorConfig(max_restarts=3)
        supervisor = ProcessSupervisor(str(tmp_path), config)
        supervisor.restart_count = 5

        assert supervisor.should_start() is False


class TestProcessSupervisorExtended:
    """ProcessSupervisor 扩展测试。"""

    def test_record_restart(self, tmp_path):
        """测试记录重启。"""
        from src.core.supervisor import ProcessSupervisor

        supervisor = ProcessSupervisor(str(tmp_path))
        assert supervisor.last_restart is None

        supervisor._record_restart()

        assert supervisor.last_restart is not None
        assert isinstance(supervisor.last_restart, datetime)

    def test_should_start_time_window_passed(self, tmp_path):
        """测试时间窗口过后重置计数。"""
        from src.core.supervisor import ProcessSupervisor, SupervisorConfig
        from datetime import timedelta

        config = SupervisorConfig(max_restarts=3, time_window=1)
        supervisor = ProcessSupervisor(str(tmp_path), config)
        supervisor.restart_count = 3
        supervisor.last_restart = datetime.now() - timedelta(seconds=2)

        assert supervisor.should_start() is True
        assert supervisor.restart_count == 0

    def test_stop_with_running_process(self, tmp_path):
        """测试停止运行中的进程。"""
        from src.core.supervisor import ProcessSupervisor
        from unittest.mock import MagicMock

        supervisor = ProcessSupervisor(str(tmp_path))
        mock_process = MagicMock()
        mock_process.terminate.return_value = None
        mock_process.wait.return_value = None
        supervisor.process = mock_process

        result = supervisor.stop(timeout=5)

        assert result is True
        assert supervisor.is_running is False
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()

    def test_stop_timeout(self, tmp_path):
        """测试停止超时后杀死进程。"""
        from src.core.supervisor import ProcessSupervisor
        from unittest.mock import MagicMock
        import subprocess

        supervisor = ProcessSupervisor(str(tmp_path))
        mock_process = MagicMock()
        mock_process.wait.side_effect = subprocess.TimeoutExpired("cmd", 5)
        mock_process.kill.return_value = None
        supervisor.process = mock_process

        result = supervisor.stop(timeout=5)

        assert result is True
        mock_process.kill.assert_called_once()

    def test_stop_exception(self, tmp_path):
        """测试停止时发生异常。"""
        from src.core.supervisor import ProcessSupervisor
        from unittest.mock import MagicMock

        supervisor = ProcessSupervisor(str(tmp_path))
        mock_process = MagicMock()
        mock_process.terminate.side_effect = OSError("Permission denied")
        supervisor.process = mock_process

        result = supervisor.stop(timeout=5)

        assert result is False

    def test_get_status_with_config(self, tmp_path):
        """测试获取状态时包含配置信息。"""
        from src.core.supervisor import ProcessSupervisor, SupervisorConfig

        config = SupervisorConfig(max_restarts=10, time_window=7200, backoff_factor=3.0)
        supervisor = ProcessSupervisor(str(tmp_path), config)

        status = supervisor.get_status()

        assert status["config"]["max_restarts"] == 10
        assert status["config"]["time_window"] == 7200
        assert status["config"]["backoff_factor"] == 3.0

    def test_create_wrapper_script(self, tmp_path):
        """测试创建包装脚本。"""
        from src.core.supervisor import ProcessSupervisor

        supervisor = ProcessSupervisor(str(tmp_path))

        def dummy_func():
            pass

        script_path = supervisor._create_wrapper_script(dummy_func, ("arg1", "arg2"), {"option": "value"})

        assert Path(script_path).exists()
        content = Path(script_path).read_text()
        assert "oc-collab" in content
        assert "agent" in content

    def test_run_process_stderr_output(self, tmp_path):
        """测试运行进程时的stderr输出。"""
        from src.core.supervisor import ProcessSupervisor
        from unittest.mock import patch, MagicMock

        supervisor = ProcessSupervisor(str(tmp_path))

        def dummy_func():
            pass

        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"", b"Error message")
        mock_process.returncode = 0

        with patch('subprocess.Popen', return_value=mock_process):
            exit_code = supervisor._run_process(dummy_func, (), {})

        assert exit_code == 0

    def test_run_process_stderr_empty(self, tmp_path):
        """测试运行进程时stderr为空。"""
        from src.core.supervisor import ProcessSupervisor
        from unittest.mock import patch, MagicMock

        supervisor = ProcessSupervisor(str(tmp_path))

        def dummy_func():
            pass

        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"output", b"")
        mock_process.returncode = 0

        with patch('subprocess.Popen', return_value=mock_process):
            exit_code = supervisor._run_process(dummy_func, (), {})

        assert exit_code == 0

    def test_run_process_stderr_decode_error(self, tmp_path):
        """测试运行进程时stderr解码错误。"""
        from src.core.supervisor import ProcessSupervisor
        from unittest.mock import patch, MagicMock

        supervisor = ProcessSupervisor(str(tmp_path))

        def dummy_func():
            pass

        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"output", b"\xff\xfe")
        mock_process.returncode = 0

        with patch('subprocess.Popen', return_value=mock_process):
            exit_code = supervisor._run_process(dummy_func, (), {})

        assert exit_code == 0

    def test_run_process_stderr_non_empty_with_decode_error(self, tmp_path):
        """测试运行进程时stderr解码时发生异常。"""
        from src.core.supervisor import ProcessSupervisor
        from unittest.mock import patch, MagicMock

        supervisor = ProcessSupervisor(str(tmp_path))

        def dummy_func():
            pass

        mock_stderr = MagicMock()
        mock_stderr.decode.side_effect = Exception("Decode error")

        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"output", mock_stderr)
        mock_process.returncode = 0

        with patch('subprocess.Popen', return_value=mock_process):
            with patch.object(supervisor, '_log'):
                exit_code = supervisor._run_process(dummy_func, (), {})

        assert exit_code == 0

    def test_start_success(self, tmp_path):
        """测试启动成功。"""
        from src.core.supervisor import ProcessSupervisor
        from unittest.mock import patch

        supervisor = ProcessSupervisor(str(tmp_path))

        def success_func():
            pass

        with patch.object(supervisor, '_run_process', return_value=0):
            result = supervisor.start(success_func)

        assert result["success"] is True
        assert result["exits"] == 0

    def test_start_with_error_max_restarts(self, tmp_path):
        """测试启动时发生错误后达到最大重启次数。"""
        from src.core.supervisor import ProcessSupervisor, SupervisorConfig
        from unittest.mock import patch

        config = SupervisorConfig(max_restarts=5, initial_delay=0.01, time_window=3600)
        supervisor = ProcessSupervisor(str(tmp_path), config)
        supervisor.last_restart = None

        def error_func():
            raise RuntimeError("Test error")

        with patch.object(supervisor, '_run_process', side_effect=RuntimeError("Test error")):
            with patch.object(supervisor, '_should_start', side_effect=[True, True, True, True, True, False]):
                result = supervisor.start(error_func)

        assert result["error"] == "超过最大重启次数"

    def test_start_max_restarts(self, tmp_path):
        """测试达到最大重启次数。"""
        from src.core.supervisor import ProcessSupervisor, SupervisorConfig
        from unittest.mock import patch

        config = SupervisorConfig(max_restarts=2, initial_delay=0.01)
        supervisor = ProcessSupervisor(str(tmp_path), config)

        def always_fail():
            pass

        with patch.object(supervisor, '_run_process', return_value=1):
            with patch.object(supervisor, '_should_start', side_effect=[True, True, False]):
                result = supervisor.start(always_fail)

        assert result["error"] == "超过最大重启次数"

    def test_create_supervisor(self, tmp_path):
        """测试创建监管器工厂函数。"""
        from src.core.supervisor import create_supervisor, ProcessSupervisor

        supervisor = create_supervisor(str(tmp_path))
        assert isinstance(supervisor, ProcessSupervisor)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
