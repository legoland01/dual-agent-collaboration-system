"""AgentDaemon 单元测试。

测试用例：
- 守护进程配置
- 进程状态检查
- PID 文件管理
- 守护进程化
"""
import pytest
import tempfile
import os
import signal
import time
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestDaemonConfig:
    """DaemonConfig 测试。"""

    def test_default_config(self):
        """测试默认配置。"""
        from src.core.daemon import DaemonConfig
        
        config = DaemonConfig()
        assert config.pid_file == "state/agent.pid"
        assert config.log_file == "logs/agent_daemon.log"
        assert config.work_dir == "."
        assert config.umask == 0o022

    def test_custom_config(self):
        """测试自定义配置。"""
        from src.core.daemon import DaemonConfig
        
        config = DaemonConfig(
            pid_file="/tmp/agent.pid",
            log_file="/tmp/agent.log",
            work_dir="/tmp",
            umask=0o077
        )
        assert config.pid_file == "/tmp/agent.pid"
        assert config.log_file == "/tmp/agent.log"
        assert config.work_dir == "/tmp"
        assert config.umask == 0o077


class TestAgentDaemon:
    """AgentDaemon 测试。"""

    def test_initialization(self, tmp_path):
        """测试初始化。"""
        from src.core.daemon import AgentDaemon, DaemonConfig
        
        config = DaemonConfig()
        daemon = AgentDaemon(str(tmp_path), config)
        
        assert daemon.project_path == tmp_path
        assert daemon.config == config
        assert daemon.pid_file == tmp_path / "state/agent.pid"
        assert daemon.log_file == tmp_path / "logs/agent_daemon.log"

    def test_initialization_default_config(self, tmp_path):
        """测试使用默认配置初始化。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        
        assert daemon.config is not None
        assert daemon.config.pid_file == "state/agent.pid"

    def test_is_running_no_pid_file(self, tmp_path):
        """测试无 PID 文件时返回未运行。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        assert daemon.pid_file.exists() is False
        assert daemon.is_running() is False

    def test_is_running_invalid_pid(self, tmp_path):
        """测试无效 PID 时返回未运行。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text("99999999\n")
        
        daemon = AgentDaemon(str(tmp_path))
        result = daemon.is_running()
        
        assert result is False

    def test_get_running_pid_no_file(self, tmp_path):
        """测试无 PID 文件时返回 None。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        pid = daemon.get_running_pid()
        
        assert pid is None

    def test_get_running_pid_invalid(self, tmp_path):
        """测试无效 PID 文件时返回 None。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text("invalid\n")
        
        daemon = AgentDaemon(str(tmp_path))
        pid = daemon.get_running_pid()
        
        assert pid is None

    def test_get_running_pid_valid_format(self, tmp_path):
        """测试有效格式的 PID 文件。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text("12345\n")
        
        daemon = AgentDaemon(str(tmp_path))
        pid = daemon.get_running_pid()
        
        assert pid == 12345

    def test_stop_not_running(self, tmp_path):
        """测试停止未运行的进程。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        result = daemon.stop()
        
        assert result is False

    def test_get_status_not_running(self, tmp_path):
        """测试获取未运行进程的状态。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        status = daemon.get_status()
        
        assert status["running"] is False
        assert status["pid"] is None

    def test_get_status_running(self, tmp_path):
        """测试获取运行中进程的状态。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text("99999\n")
        
        daemon = AgentDaemon(str(tmp_path))
        status = daemon.get_status()
        
        assert status["running"] is False
        assert status["pid"] == 99999


class TestDaemonExceptions:
    """守护进程异常测试。"""

    def test_daemonize_error(self):
        """测试守护进程化异常。"""
        from src.core.daemon import DaemonizeError
        
        error = DaemonizeError("Test error")
        assert "Test error" in str(error)

    def test_process_exists_error(self):
        """测试进程已存在异常。"""
        from src.core.daemon import ProcessExistsError
        
        error = ProcessExistsError("Process running")
        assert "Process running" in str(error)


class TestAgentDaemonExtended:
    """AgentDaemon 扩展测试。"""

    @pytest.fixture
    def tmp_path(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_daemonize_process_exists(self, tmp_path):
        """测试守护进程化时进程已存在。"""
        from src.core.daemon import AgentDaemon, ProcessExistsError
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text("12345\n")
        
        daemon = AgentDaemon(str(tmp_path))
        
        with patch.object(daemon, 'is_running', return_value=True):
            with pytest.raises(ProcessExistsError) as exc_info:
                daemon.daemonize(lambda: None)
            
            assert "PID: 12345" in str(exc_info.value)

    def test_daemonize_fork_failure(self, tmp_path):
        """测试守护进程化时 fork 失败。"""
        from src.core.daemon import AgentDaemon, DaemonizeError
        
        daemon = AgentDaemon(str(tmp_path))
        
        with patch('os.fork', side_effect=OSError("Cannot fork")):
            with pytest.raises(DaemonizeError) as exc_info:
                daemon.daemonize(lambda: None)
            
            assert "Fork 失败" in str(exc_info.value)

    def test_daemonize_success_parent(self, tmp_path):
        """测试守护进程化成功（父进程返回子进程 PID）。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        
        with patch('os.fork', return_value=12345):
            with patch.object(daemon, '_become_daemon'):
                with patch.object(daemon, '_setup_signal_handlers'):
                    with patch.object(daemon, '_write_pid'):
                        with patch.object(daemon, '_run_main'):
                            result = daemon.daemonize(lambda: None)
            
            assert result == 12345

    def test_daemonize_success_child(self, tmp_path):
        """测试守护进程化成功（子进程继续执行）。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        main_func = MagicMock()
        
        def mock_run_main(func, args, kwargs):
            func(*args, **kwargs)
        
        with patch('os.fork', return_value=0):
            with patch.object(daemon, '_become_daemon'):
                with patch.object(daemon, '_setup_signal_handlers'):
                    with patch.object(daemon, '_write_pid'):
                        with patch.object(daemon, '_run_main', side_effect=mock_run_main):
                            daemon.daemonize(main_func, "arg1", kwarg="value")
        
        main_func.assert_called_once_with("arg1", kwarg="value")

    def test_is_running_with_valid_process(self, tmp_path):
        """测试检查运行中进程（有效 PID）。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        current_pid = os.getpid()
        (tmp_path / "state" / "agent.pid").write_text(f"{current_pid}\n")
        
        daemon = AgentDaemon(str(tmp_path))
        result = daemon.is_running()
        
        assert result is True

    def test_is_running_process_not_found(self, tmp_path):
        """测试检查不存在的进程。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text("999999\n")
        
        daemon = AgentDaemon(str(tmp_path))
        result = daemon.is_running()
        
        assert result is False

    def test_is_running_permission_denied(self, tmp_path):
        """测试检查进程时的权限错误。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text("1\n")
        
        daemon = AgentDaemon(str(tmp_path))
        
        with patch('os.kill', side_effect=PermissionError("Permission denied")):
            result = daemon.is_running()
        
        assert result is False

    def test_stop_running_process(self, tmp_path):
        """测试停止运行中的进程。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text("99999\n")
        
        daemon = AgentDaemon(str(tmp_path))
        
        def mock_kill(pid, sig):
            if sig == signal.SIGTERM:
                raise ProcessLookupError()
        
        with patch('os.kill', side_effect=mock_kill):
            with patch('time.sleep'):
                result = daemon.stop(timeout=1.0)
        
        assert result is True

    def test_stop_timeout_and_kill(self, tmp_path):
        """测试停止进程超时后发送 SIGKILL。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text("99999\n")
        
        daemon = AgentDaemon(str(tmp_path))
        
        with patch('os.kill'):
            with patch('time.time', side_effect=[0, 0, 0, 2.0]):
                with patch('time.sleep'):
                    result = daemon.stop(timeout=1.0)
        
        assert result is True

    def test_stop_permission_denied(self, tmp_path):
        """测试停止进程时权限被拒绝。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text("99999\n")
        
        daemon = AgentDaemon(str(tmp_path))
        
        with patch('os.kill', side_effect=PermissionError("Permission denied")):
            result = daemon.stop()
        
        assert result is False

    def test_cleanup_no_file(self, tmp_path):
        """测试清理不存在的 PID 文件。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        
        daemon.cleanup()

    def test_cleanup_remove_file(self, tmp_path):
        """测试清理时删除 PID 文件。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text("12345\n")
        
        daemon = AgentDaemon(str(tmp_path))
        assert daemon.pid_file.exists()
        
        daemon.cleanup()
        
        assert not daemon.pid_file.exists()

    def test_get_status_with_log(self, tmp_path):
        """测试获取状态时包含日志信息。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "logs").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text("99999\n")
        (tmp_path / "logs" / "agent_daemon.log").write_text("line1\nline2\nline3\n")
        
        daemon = AgentDaemon(str(tmp_path))
        status = daemon.get_status()
        
        assert status["pid"] == 99999
        assert status["running"] is False

    def test_get_status_log_read_error(self, tmp_path):
        """测试获取状态时日志读取错误。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "logs").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text("99999\n")
        
        daemon = AgentDaemon(str(tmp_path))
        status = daemon.get_status()
        
        assert status["pid"] == 99999

    def test_ensure_directories(self, tmp_path):
        """测试确保目录存在。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        assert not (tmp_path / "state").exists()
        assert not (tmp_path / "logs").exists()
        
        daemon._ensure_directories()
        
        assert (tmp_path / "state").exists()
        assert (tmp_path / "logs").exists()

    def test_become_daemon(self, tmp_path):
        """测试成为守护进程（跳过 dup2 测试）。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        
        with patch('os.setsid'):
            with patch('os.chdir'):
                with patch('os.umask'):
                    with patch('sys.stdout.flush'):
                        with patch('sys.stderr.flush'):
                            pass

    def test_setup_signal_handlers(self, tmp_path):
        """测试设置信号处理器。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        
        with patch('signal.signal') as mock_signal:
            daemon._setup_signal_handlers()
            
            assert mock_signal.call_count == 3
            calls = mock_signal.call_args_list
            assert calls[0][0][0] == signal.SIGTERM
            assert calls[1][0][0] == signal.SIGINT
            assert calls[2][0][0] == signal.SIGHUP

    def test_handle_terminate(self, tmp_path):
        """测试处理终止信号。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        
        with patch.object(daemon, 'cleanup'):
            with pytest.raises(SystemExit):
                daemon._handle_terminate(signal.SIGTERM, None)

    def test_write_pid(self, tmp_path):
        """测试写入 PID。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        daemon._ensure_directories()
        
        daemon._write_pid()
        
        content = daemon.pid_file.read_text().strip()
        assert content == str(os.getpid())

    def test_run_main_success(self, tmp_path):
        """测试运行主函数成功。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        func = MagicMock()
        
        with patch.object(daemon, '_log') as mock_log:
            daemon._run_main(func, (), {})
        
        func.assert_called_once_with()
        assert mock_log.call_count == 2

    def test_run_main_exception(self, tmp_path):
        """测试运行主函数时异常。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        func = MagicMock(side_effect=ValueError("Test error"))
        
        with patch.object(daemon, '_log') as mock_log:
            with pytest.raises(ValueError):
                daemon._run_main(func, (), {})
            
            log_messages = [str(c) for c in mock_log.call_args_list]
            assert any("守护进程异常" in msg for msg in log_messages)

    def test_log(self, tmp_path):
        """测试日志写入。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        daemon._ensure_directories()
        
        daemon._log("Test message")
        
        content = daemon.log_file.read_text()
        assert "Test message" in content
        assert "[" in content

    def test_log_write_error(self, tmp_path):
        """测试日志写入错误。"""
        from src.core.daemon import AgentDaemon
        
        daemon = AgentDaemon(str(tmp_path))
        
        with patch('builtins.open', side_effect=OSError("Cannot write")):
            daemon._log("Test message")

    def test_create_daemon(self, tmp_path):
        """测试创建守护进程实例。"""
        from src.core.daemon import create_daemon, AgentDaemon
        
        daemon = create_daemon(str(tmp_path))
        
        assert isinstance(daemon, AgentDaemon)
        assert daemon.project_path == tmp_path

    def test_is_running_calls_kill(self, tmp_path):
        """测试 is_running 调用 os.kill。"""
        from src.core.daemon import AgentDaemon
        
        (tmp_path / "state").mkdir(exist_ok=True)
        (tmp_path / "state" / "agent.pid").write_text(f"{os.getpid()}\n")
        
        daemon = AgentDaemon(str(tmp_path))
        daemon.is_running()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
