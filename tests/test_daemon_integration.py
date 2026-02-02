"""AgentDaemon 集成测试 - 测试实际的守护进程化功能。"""
import pytest
import os
import sys
import time
import signal
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestDaemonScript:
    """守护进程脚本测试。"""

    def test_daemon_run_main_calls_function(self, tmp_path):
        """测试_run_main调用主函数。"""
        from src.core.daemon import AgentDaemon

        daemon = AgentDaemon(str(tmp_path))
        daemon._ensure_directories()

        function_called = []

        def my_func():
            function_called.append(True)

        with patch.object(daemon, '_log'):
            daemon._run_main(my_func, (), {})

        assert len(function_called) == 1

    def test_daemon_run_main_exception_handling(self, tmp_path):
        """测试_run_main处理异常。"""
        from src.core.daemon import AgentDaemon

        daemon = AgentDaemon(str(tmp_path))
        daemon._ensure_directories()

        def failing_func():
            raise ValueError("Test error")

        with patch.object(daemon, '_log') as mock_log:
            with pytest.raises(ValueError):
                daemon._run_main(failing_func, (), {})

        calls = [str(call) for call in mock_log.call_args_list]
        assert any("异常" in str(call) for call in calls)

    def test_daemon_run_main_finally_cleanup(self, tmp_path):
        """测试_run_main的finally块会清理。"""
        from src.core.daemon import AgentDaemon

        daemon = AgentDaemon(str(tmp_path))
        daemon._ensure_directories()

        (tmp_path / "state").mkdir(exist_ok=True)
        pid_file = tmp_path / "state" / "agent.pid"
        pid_file.write_text("12345")

        def failing_func():
            raise ValueError("Test error")

        with patch.object(daemon, '_log'):
            with pytest.raises(ValueError):
                daemon._run_main(failing_func, (), {})

        assert not pid_file.exists()

    def test_become_daemon_setsid(self, tmp_path):
        """测试_become_daemon调用setsid。"""
        from src.core.daemon import AgentDaemon

        daemon = AgentDaemon(str(tmp_path))
        daemon._ensure_directories()

        mock_devnull = MagicMock()
        mock_devnull.fileno.return_value = 5

        mock_log_file = MagicMock()
        mock_log_file.fileno.return_value = 6

        with patch('os.setsid') as mock_setsid:
            with patch('os.chdir'):
                with patch('os.umask'):
                    with patch('sys.stdout.flush'):
                        with patch('sys.stderr.flush'):
                            with patch('sys.stdin.fileno', return_value=0):
                                with patch('builtins.open', side_effect=[mock_devnull, mock_log_file]):
                                    with patch('os.dup2', return_value=None):
                                        daemon._become_daemon()

        mock_setsid.assert_called_once()

    def test_become_daemon_chdir(self, tmp_path):
        """测试_become_daemon改变工作目录。"""
        from src.core.daemon import AgentDaemon

        daemon = AgentDaemon(str(tmp_path))
        daemon._ensure_directories()

        mock_devnull = MagicMock()
        mock_devnull.fileno.return_value = 5

        mock_log_file = MagicMock()
        mock_log_file.fileno.return_value = 6

        with patch('os.setsid'):
            with patch('os.chdir') as mock_chdir:
                with patch('os.umask'):
                    with patch('sys.stdout.flush'):
                        with patch('sys.stderr.flush'):
                            with patch('sys.stdin.fileno', return_value=0):
                                with patch('builtins.open', side_effect=[mock_devnull, mock_log_file]):
                                    with patch('os.dup2', return_value=None):
                                        daemon._become_daemon()

        mock_chdir.assert_called_once_with(str(tmp_path))

    def test_become_daemon_umask(self, tmp_path):
        """测试_become_daemon设置umask。"""
        from src.core.daemon import AgentDaemon

        daemon = AgentDaemon(str(tmp_path))
        daemon._ensure_directories()

        mock_devnull = MagicMock()
        mock_devnull.fileno.return_value = 5

        mock_log_file = MagicMock()
        mock_log_file.fileno.return_value = 6

        with patch('os.setsid'):
            with patch('os.chdir'):
                with patch('os.umask') as mock_umask:
                    with patch('sys.stdout.flush'):
                        with patch('sys.stderr.flush'):
                            with patch('sys.stdin.fileno', return_value=0):
                                with patch('builtins.open', side_effect=[mock_devnull, mock_log_file]):
                                    with patch('os.dup2', return_value=None):
                                        daemon._become_daemon()

        mock_umask.assert_called_once_with(0o022)

    def test_setup_signal_handlers(self, tmp_path):
        """测试_setup_signal_handlers注册信号处理器。"""
        from src.core.daemon import AgentDaemon

        daemon = AgentDaemon(str(tmp_path))

        with patch('signal.signal') as mock_signal:
            daemon._setup_signal_handlers()

        assert mock_signal.call_count == 3
        sigs = [call[0][0] for call in mock_signal.call_args_list]
        assert signal.SIGTERM in sigs
        assert signal.SIGINT in sigs
        assert signal.SIGHUP in sigs

    def test_handle_terminate_logs_and_exits(self, tmp_path):
        """测试_handle_terminate记录日志并退出。"""
        from src.core.daemon import AgentDaemon

        daemon = AgentDaemon(str(tmp_path))
        (tmp_path / "state").mkdir()
        pid_file = tmp_path / "state" / "agent.pid"
        pid_file.write_text("12345")

        with patch('sys.exit') as mock_exit:
            daemon._handle_terminate(signal.SIGTERM, None)

        mock_exit.assert_called_once_with(0)
        assert not pid_file.exists()

    def test_log_writes_to_file(self, tmp_path):
        """测试_log写入日志文件。"""
        from src.core.daemon import AgentDaemon

        daemon = AgentDaemon(str(tmp_path))
        daemon._ensure_directories()

        daemon._log("Test message")

        log_content = (tmp_path / "logs" / "agent_daemon.log").read_text()
        assert "Test message" in log_content
        assert "[" in log_content
        assert "]" in log_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
