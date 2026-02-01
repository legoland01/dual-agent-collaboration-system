"""AgentDaemon 单元测试。

测试用例：
- 守护进程配置
- 进程状态检查
- PID 文件管理
"""
import pytest
import tempfile
import os
from pathlib import Path


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
