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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
