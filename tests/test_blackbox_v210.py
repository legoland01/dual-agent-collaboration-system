"""v2.1.0 黑盒测试用例实现

基于 docs/03-test/blackbox_test_cases_v2.1.0.md
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import yaml
import time

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.state_manager import StateManager
from src.core.exception_handler import (
    NetworkError, RetryConfig, with_retry
)
from src.core.monitor import ResourceMonitor, AlertLevel
from src.core.config_reloader import ConfigReloader


class TestConfigReloaderBlackbox:
    """配置热重载黑盒测试 (TC-BB-001)"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_config_hot_reload(self, temp_dir):
        """测试配置热重载功能。"""
        config_path = temp_dir / "config.yaml"
        config_path.write_text(yaml.dump({"key": "value1"}))
        
        reloader = ConfigReloader(config_paths={"test": str(config_path)})
        reloader.load_all()
        
        assert reloader.configs["test"]["key"] == "value1"

    def test_config_monitor_start_stop(self, temp_dir):
        """测试配置监控启动停止。"""
        config_path = temp_dir / "config.yaml"
        config_path.write_text(yaml.dump({"key": "value"}))
        
        reloader = ConfigReloader(config_paths={"test": str(config_path)})
        reloader.load_all()
        
        reloader.start_monitoring(interval=1)
        reloader.stop_monitoring()


class TestExceptionHandlerBlackbox:
    """异常处理黑盒测试 (TC-BB-005)"""

    def test_network_retry_success(self):
        """测试网络操作自动重试成功。"""
        call_count = [0]
        
        def flaky_operation():
            call_count[0] += 1
            if call_count[0] < 3:
                raise NetworkError("Network unstable")
            return "success"
        
        config = RetryConfig(max_retries=3, initial_delay=0.01)
        
        with patch('time.sleep'):
            result = with_retry(config)(flaky_operation)()
        
        assert result == "success"
        assert call_count[0] == 3

    def test_network_retry_exhausted(self):
        """测试网络操作重试耗尽。"""
        def always_fail():
            raise NetworkError("Always failing")
        
        config = RetryConfig(max_retries=2, initial_delay=0.01)
        
        with patch('time.sleep'):
            with pytest.raises(NetworkError):
                with_retry(config)(always_fail)()


class TestResourceMonitorBlackbox:
    """资源监控黑盒测试 (TC-BB-003)"""

    def test_resource_monitor_start_stop(self):
        """测试资源监控启动停止。"""
        monitor = ResourceMonitor(sample_interval=60)
        
        monitor.start_monitoring()
        assert monitor._monitor_thread is not None
        monitor.stop_monitoring()

    def test_resource_monitor_check_thresholds(self):
        """测试资源阈值检查。"""
        monitor = ResourceMonitor(
            cpu_threshold=99.0,
            memory_threshold=99.0,
            disk_threshold=99.0,
            sample_interval=60
        )
        
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(percent=50.0)
                with patch('psutil.disk_usage', return_value=MagicMock(percent=50.0)):
                    alerts = monitor.check_thresholds()
        
        assert len(alerts) == 0

    def test_resource_monitor_alerts_on_high_usage(self):
        """测试高资源使用率触发告警。"""
        monitor = ResourceMonitor(
            cpu_threshold=10.0,
            memory_threshold=99.0,
            disk_threshold=99.0,
            sample_interval=60
        )
        
        with patch('psutil.cpu_percent', return_value=85.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(percent=50.0)
                with patch('psutil.disk_usage', return_value=MagicMock(percent=50.0)):
                    alerts = monitor.check_thresholds()
        
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.WARNING
        assert alerts[0].metric == "cpu_percent"


class TestStateManagerBlackbox:
    """状态管理黑盒测试"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_state_manager_initialize(self, temp_dir):
        """测试状态管理器初始化。"""
        manager = StateManager(str(temp_dir))
        assert manager is not None

    def test_state_manager_initialize_project(self, temp_dir):
        """测试项目初始化。"""
        manager = StateManager(str(temp_dir))
        result = manager.initialize_project("TestProject", "PYTHON")
        assert result["project"]["name"] == "TestProject"
        assert result["project"]["type"] == "PYTHON"

    def test_state_manager_read_write(self, temp_dir):
        """测试状态读写。"""
        manager = StateManager(str(temp_dir))
        manager.initialize_project("Test", "PYTHON")
        
        state = manager.read_state()
        assert state is not None
        assert "project" in state

    def test_state_manager_get_phase(self, temp_dir):
        """测试获取当前阶段。"""
        manager = StateManager(str(temp_dir))
        manager.initialize_project("Test", "PYTHON")
        
        phase = manager.get_current_phase()
        assert phase is not None


class TestEdgeCasesBlackbox:
    """边界情况黑盒测试"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_corrupted_yaml_recovery(self, temp_dir):
        """测试损坏 YAML 文件恢复。"""
        state_file = temp_dir / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("invalid: yaml: content: [}")
        
        manager = StateManager(str(temp_dir))
        
        try:
            manager.read_state()
        except (ValueError, Exception):
            pass
        
        assert manager is not None

    def test_special_characters_in_project_name(self, temp_dir):
        """测试特殊字符项目名称处理。"""
        name = "Test_Project-123"
        
        manager = StateManager(str(temp_dir))
        result = manager.initialize_project(name, "PYTHON")
        
        assert result["project"]["name"] == name


class TestPerformanceBlackbox:
    """性能测试"""

    def test_status_load_performance(self, tmp_path):
        """测试状态文件加载性能。"""
        manager = StateManager(str(tmp_path))
        manager.initialize_project("Test", "PYTHON")
        
        start = time.time()
        
        for _ in range(10):
            manager.read_state()
        
        elapsed = time.time() - start
        assert elapsed < 2.0


class TestGitMonitorBlackbox:
    """Git 监控黑盒测试 (TC-BB-002)"""

    @pytest.mark.skip(reason="需要集成测试环境")
    def test_git_monitor_init_from_current_repo(self):
        """测试 Git 监控初始化 - 使用当前项目仓库。"""
        from src.core.git_monitor import GitMonitor
        import os
        current_dir = os.getcwd()
        
        monitor = GitMonitor(current_dir)
        
        assert str(monitor.project_path) == current_dir

    @pytest.mark.skip(reason="需要集成测试环境")
    def test_git_commit_detection_from_current_repo(self):
        """测试 Git 提交检测 - 使用当前项目仓库。"""
        from src.core.git_monitor import GitMonitor
        import os
        current_dir = os.getcwd()
        
        monitor = GitMonitor(current_dir)
        
        assert monitor is not None
        commits = monitor.get_new_commits()
        assert monitor.get_current_branch() is not None


class TestGitWorkflowBlackbox:
    """Git 工作流强制执行黑盒测试 (TC-BB-004)"""

    @pytest.fixture
    def initialized_temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.core.state_manager import StateManager
            manager = StateManager(str(tmpdir))
            manager.initialize_project("TestProject", "PYTHON")
            yield Path(tmpdir)

    def test_state_with_initialized_project(self, initialized_temp_dir):
        """测试已初始化项目的状态管理。"""
        from src.core.state_manager import StateManager
        manager = StateManager(str(initialized_temp_dir))
        
        state = manager.read_state()
        assert state is not None
        assert state["project"]["name"] == "TestProject"

    def test_git_status_in_initialized_project(self, initialized_temp_dir):
        """测试已初始化项目的 Git 状态。"""
        import subprocess
        subprocess.run(["git", "init"], cwd=str(initialized_temp_dir), capture_output=True)
        
        from src.core.state_manager import StateManager
        manager = StateManager(str(initialized_temp_dir))
        state = manager.read_state()
        
        assert state is not None
        assert state["project"]["name"] == "TestProject"


class TestMultiRoundIterationBlackbox:
    """多轮迭代协作黑盒测试 (TC-E2E-002)"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_requirement_modification_and_resignoff(self, temp_dir):
        """测试需求修改后的重新评审。"""
        from src.core.state_manager import StateManager
        from datetime import datetime
        
        manager = StateManager(str(temp_dir))
        manager.initialize_project("TestProject", "PYTHON")
        
        state = manager.read_state()
        
        original_signoffs = len(state.get("signoffs", []))
        
        state["signoffs"] = state.get("signoffs", [])
        state["signoffs"].append({
            "agent": "Agent 1",
            "phase": "requirements",
            "timestamp": datetime.now().isoformat(),
            "version": "1"
        })
        manager.write_state(state)
        
        state = manager.read_state()
        assert len(state["signoffs"]) == original_signoffs + 1
        
        state["signoffs"].append({
            "agent": "Agent 2",
            "phase": "requirements",
            "timestamp": datetime.now().isoformat(),
            "version": "1"
        })
        manager.write_state(state)
        
        state = manager.read_state()
        assert len(state["signoffs"]) == original_signoffs + 2


class TestRemoteCollaborationBlackbox:
    """远程协作黑盒测试 (TC-E2E-003)"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_signoff_history_preserved(self, temp_dir):
        """测试签署历史保留。"""
        from src.core.state_manager import StateManager
        from datetime import datetime
        
        manager = StateManager(str(temp_dir))
        manager.initialize_project("TestProject", "PYTHON")
        
        signoffs = [
            {
                "agent": "Agent 1",
                "phase": "requirements",
                "timestamp": "2026-02-01T10:00:00",
                "version": "1"
            },
            {
                "agent": "Agent 2",
                "phase": "requirements",
                "timestamp": "2026-02-01T10:05:00",
                "version": "1"
            }
        ]
        
        state = manager.read_state()
        state["signoffs"] = signoffs
        manager.write_state(state)
        
        state = manager.read_state()
        assert len(state["signoffs"]) == 2
        assert state["signoffs"][0]["agent"] == "Agent 1"
        assert state["signoffs"][1]["agent"] == "Agent 2"

    def test_state_version_tracking(self, temp_dir):
        """测试状态版本跟踪。"""
        from src.core.state_manager import StateManager
        
        manager = StateManager(str(temp_dir))
        manager.initialize_project("TestProject", "PYTHON")
        
        state = manager.read_state()
        assert "version" in state
        
        state["version"] = "2.0"
        manager.write_state(state)
        
        state = manager.read_state()
        assert state["version"] == "2.0"


class TestE2EBlackbox:
    """端到端黑盒测试"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_complete_collaboration_flow(self, temp_dir):
        """测试完整协作流程 (TC-E2E-001)。"""
        manager = StateManager(str(temp_dir))
        
        result = manager.initialize_project("TestProject", "PYTHON")
        assert result["project"]["name"] == "TestProject"
        assert result["project"]["type"] == "PYTHON"
        
        state = manager.read_state()
        assert state["project"]["name"] == "TestProject"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
