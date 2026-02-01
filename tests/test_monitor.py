"""Monitor 单元测试。"""
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.monitor import (
    ResourceMonitor, Alert, AlertLevel
)


class TestAlertLevel:
    """告警级别测试。"""

    def test_alert_level_values(self):
        """测试告警级别值。"""
        assert AlertLevel.INFO.value == "INFO"
        assert AlertLevel.WARNING.value == "WARNING"
        assert AlertLevel.ERROR.value == "ERROR"
        assert AlertLevel.CRITICAL.value == "CRITICAL"


class TestAlert:
    """告警测试。"""

    def test_alert_defaults(self):
        """测试告警默认值。"""
        alert = Alert(
            level=AlertLevel.WARNING,
            message="Test alert"
        )
        assert alert.timestamp is not None
        assert alert.metric == ""
        assert alert.value == 0.0
        assert alert.threshold == 0.0

    def test_alert_str(self):
        """测试告警字符串表示。"""
        alert = Alert(
            level=AlertLevel.WARNING,
            message="CPU high",
            metric="cpu_percent",
            value=85.0,
            threshold=80.0
        )
        alert_str = str(alert)
        assert "WARNING" in alert_str
        assert "CPU high" in alert_str

    def test_alert_with_all_fields(self):
        """测试完整告警。"""
        now = datetime.now()
        alert = Alert(
            level=AlertLevel.ERROR,
            message="Memory critical",
            timestamp=now,
            metric="memory_percent",
            value=95.0,
            threshold=85.0
        )
        assert alert.level == AlertLevel.ERROR
        assert alert.message == "Memory critical"
        assert alert.timestamp == now
        assert alert.value == 95.0


class TestResourceMonitor:
    """资源监控器测试类。"""

    @pytest.fixture
    def monitor(self):
        """创建资源监控器实例。"""
        return ResourceMonitor(
            cpu_threshold=80.0,
            memory_threshold=85.0,
            disk_threshold=90.0,
            sample_interval=10
        )

    def test_init_defaults(self):
        """测试默认初始化。"""
        monitor = ResourceMonitor()
        assert monitor.cpu_threshold == 80.0
        assert monitor.memory_threshold == 85.0
        assert monitor.disk_threshold == 90.0
        assert monitor.sample_interval == 10
        assert monitor.alerts == []
        assert monitor.stats["restart_count"] == 0

    def test_init_custom_thresholds(self):
        """测试自定义阈值初始化。"""
        monitor = ResourceMonitor(
            cpu_threshold=70.0,
            memory_threshold=80.0,
            disk_threshold=85.0,
            sample_interval=5
        )
        assert monitor.cpu_threshold == 70.0
        assert monitor.memory_threshold == 80.0
        assert monitor.disk_threshold == 85.0
        assert monitor.sample_interval == 5

    def test_get_current_stats(self, monitor):
        """测试获取当前统计信息。"""
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(
                    percent=60.0,
                    used=8 * (1024**3),
                    total=16 * (1024**3)
                )
                with patch('psutil.disk_usage', return_value=MagicMock(percent=40.0)):
                    with patch('psutil.cpu_count', return_value=4):
                        with patch('psutil.boot_time', return_value=1234567890):
                            stats = monitor.get_current_stats()
                            
                            assert stats["cpu_percent"] == 50.0
                            assert stats["memory_percent"] == 60.0
                            assert stats["disk_percent"] == 40.0
                            assert stats["cpu_count"] == 4
                            assert stats["memory_used_gb"] == 8.0

    def test_check_thresholds_no_alerts(self, monitor):
        """测试阈值检查（无告警）。"""
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(percent=60.0)
                with patch('psutil.disk_usage', return_value=MagicMock(percent=40.0)):
                    alerts = monitor.check_thresholds()
                    
                    assert len(alerts) == 0

    def test_check_thresholds_cpu_alert(self, monitor):
        """测试CPU阈值告警。"""
        with patch('psutil.cpu_percent', return_value=85.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(percent=60.0)
                with patch('psutil.disk_usage', return_value=MagicMock(percent=40.0)):
                    alerts = monitor.check_thresholds()
                    
                    assert len(alerts) == 1
                    assert alerts[0].metric == "cpu_percent"
                    assert alerts[0].value == 85.0

    def test_check_thresholds_memory_alert(self, monitor):
        """测试内存阈值告警。"""
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(percent=90.0)
                with patch('psutil.disk_usage', return_value=MagicMock(percent=40.0)):
                    alerts = monitor.check_thresholds()
                    
                    assert len(alerts) == 1
                    assert alerts[0].metric == "memory_percent"
                    assert alerts[0].value == 90.0

    def test_check_thresholds_disk_alert(self, monitor):
        """测试磁盘阈值告警。"""
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(percent=60.0)
                with patch('psutil.disk_usage', return_value=MagicMock(percent=95.0)):
                    alerts = monitor.check_thresholds()
                    
                    assert len(alerts) == 1
                    assert alerts[0].metric == "disk_percent"
                    assert alerts[0].value == 95.0

    def test_check_thresholds_multiple_alerts(self, monitor):
        """测试多阈值告警。"""
        with patch('psutil.cpu_percent', return_value=85.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(percent=90.0)
                with patch('psutil.disk_usage', return_value=MagicMock(percent=95.0)):
                    alerts = monitor.check_thresholds()
                    
                    assert len(alerts) == 3

    def test_register_alert_callback(self, monitor):
        """测试注册告警回调。"""
        callback = MagicMock()
        monitor.register_alert_callback(callback)
        
        assert callback in monitor.alert_callbacks

    def test_notify_alert(self, monitor):
        """测试告警通知。"""
        callback = MagicMock()
        monitor.register_alert_callback(callback)
        
        alert = Alert(level=AlertLevel.WARNING, message="Test")
        monitor._notify_alert(alert)
        
        callback.assert_called_once_with(alert)

    def test_notify_alert_callback_error(self, monitor):
        """测试告警通知回调错误。"""
        def bad_callback(alert):
            raise Exception("Callback error")
        
        monitor.register_alert_callback(bad_callback)
        
        alert = Alert(level=AlertLevel.WARNING, message="Test")
        # Should not raise exception
        monitor._notify_alert(alert)

    def test_get_recent_alerts(self, monitor):
        """测试获取最近告警。"""
        for i in range(15):
            monitor.alerts.append(Alert(
                level=AlertLevel.INFO,
                message=f"Alert {i}"
            ))
        
        recent = monitor.get_recent_alerts(10)
        
        assert len(recent) == 10

    def test_get_recent_alerts_default_count(self, monitor):
        """测试获取最近告警（默认数量）。"""
        for i in range(15):
            monitor.alerts.append(Alert(
                level=AlertLevel.INFO,
                message=f"Alert {i}"
            ))
        
        recent = monitor.get_recent_alerts()
        
        assert len(recent) == 10

    def test_clear_old_alerts(self, monitor):
        """测试清理旧告警。"""
        now = datetime.now()
        
        old_alert = Alert(level=AlertLevel.INFO, message="Old")
        old_alert.timestamp = now - timedelta(hours=48)
        
        new_alert = Alert(level=AlertLevel.INFO, message="New")
        
        monitor.alerts = [old_alert, new_alert]
        
        cleared = monitor.clear_old_alerts(hours=24)
        
        assert cleared == 1
        assert len(monitor.alerts) == 1
        assert monitor.alerts[0].message == "New"

    def test_clear_old_alerts_no_old(self, monitor):
        """测试无旧告警可清理。"""
        now = datetime.now()
        
        for i in range(5):
            alert = Alert(level=AlertLevel.INFO, message=f"Alert {i}")
            alert.timestamp = now - timedelta(hours=1)
            monitor.alerts.append(alert)
        
        cleared = monitor.clear_old_alerts(hours=24)
        
        assert cleared == 0
        assert len(monitor.alerts) == 5

    def test_get_status_report(self, monitor):
        """测试获取状态报告。"""
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(
                    percent=60.0,
                    used=8 * (1024**3),
                    total=16 * (1024**3)
                )
                with patch('psutil.disk_usage', return_value=MagicMock(percent=40.0)):
                    with patch('psutil.cpu_count', return_value=4):
                        with patch('psutil.boot_time', return_value=1234567890):
                            report = monitor.get_status_report()
                            
                            assert "status" in report
                            assert "resources" in report
                            assert "stats" in report
                            assert "recent_alerts" in report
                            assert report["resources"]["cpu"] == "50.0%"
                            assert report["stats"]["restart_count"] == 0

    def test_get_status_report_warning_cpu(self, monitor):
        """测试获取状态报告（CPU警告）。"""
        with patch('psutil.cpu_percent', return_value=85.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(percent=60.0)
                with patch('psutil.disk_usage', return_value=MagicMock(percent=40.0)):
                    with patch('psutil.cpu_count', return_value=4):
                        with patch('psutil.boot_time', return_value=1234567890):
                            report = monitor.get_status_report()
                            
                            assert report["status"] == "warning"

    def test_get_status_report_warning_memory(self, monitor):
        """测试获取状态报告（内存警告）。"""
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(percent=90.0)
                with patch('psutil.disk_usage', return_value=MagicMock(percent=40.0)):
                    with patch('psutil.cpu_count', return_value=4):
                        with patch('psutil.boot_time', return_value=1234567890):
                            report = monitor.get_status_report()
                            
                            assert report["status"] == "warning"

    def test_get_status_report_critical(self, monitor):
        """测试获取状态报告（磁盘严重）。"""
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(percent=60.0)
                with patch('psutil.disk_usage', return_value=MagicMock(percent=95.0)):
                    with patch('psutil.cpu_count', return_value=4):
                        with patch('psutil.boot_time', return_value=1234567890):
                            report = monitor.get_status_report()
                            
                            assert report["status"] == "critical"

    def test_increment_restart_count(self, monitor):
        """测试增加重启计数。"""
        assert monitor.stats["restart_count"] == 0
        
        monitor.increment_restart_count()
        
        assert monitor.stats["restart_count"] == 1

    def test_increment_git_operations(self, monitor):
        """测试增加Git操作计数。"""
        assert monitor.stats["git_operations"] == 0
        
        monitor.increment_git_operations()
        
        assert monitor.stats["git_operations"] == 1

    def test_increment_exception_count(self, monitor):
        """测试增加异常计数。"""
        assert monitor.stats["exception_count"] == 0
        
        monitor.increment_exception_count()
        
        assert monitor.stats["exception_count"] == 1

    def test_start_monitoring(self, monitor):
        """测试开始监控。"""
        monitor.start_monitoring()
        
        assert monitor._monitor_thread is not None
        assert monitor._monitor_thread.is_alive()
        
        monitor.stop_monitoring()

    def test_start_monitoring_already_running(self, monitor):
        """测试开始监控（已在运行）。"""
        monitor._monitor_thread = MagicMock()
        monitor._monitor_thread.is_alive.return_value = True
        
        monitor.start_monitoring()
        
        assert monitor._monitor_thread is not None

    def test_stop_monitoring(self, monitor):
        """测试停止监控。"""
        monitor._running = True
        monitor._monitor_thread = MagicMock()
        monitor._monitor_thread.is_alive.return_value = False
        
        monitor.stop_monitoring()
        
        assert monitor._monitor_thread is None

    def test_monitor_loop(self, monitor):
        """测试监控循环。"""
        call_count = 0
        
        def mock_check_thresholds():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                monitor._stop_event.set()
        
        monitor._stop_event = MagicMock()
        monitor._stop_event.is_set.side_effect = lambda: call_count >= 2
        monitor._stop_event.wait.return_value = None
        
        with patch.object(monitor, 'check_thresholds', side_effect=mock_check_thresholds):
            monitor._monitor_loop()
        
        assert call_count >= 1

    def test_monitor_loop_exception(self, monitor):
        """测试监控循环异常处理。"""
        call_count = 0
        
        def mock_check_thresholds():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                monitor._stop_event.set()
            raise Exception("Test error")
        
        monitor._stop_event = MagicMock()
        monitor._stop_event.is_set.side_effect = lambda: call_count >= 2
        monitor._stop_event.wait.return_value = None
        
        with patch.object(monitor, 'check_thresholds', side_effect=mock_check_thresholds):
            monitor._monitor_loop()

    def test_get_cpu_percent(self, monitor):
        """测试获取CPU使用率。"""
        with patch('psutil.cpu_percent', return_value=75.0):
            percent = monitor.get_cpu_percent()
            assert percent == 75.0


class TestGetSystemInfo:
    """系统信息测试类。"""

    def test_get_system_info(self):
        """测试获取系统信息。"""
        from src.core.monitor import get_system_info
        
        with patch('psutil.cpu_count', return_value=8):
            with patch('psutil.cpu_freq') as mock_freq:
                mock_freq.return_value = MagicMock(
                    current=2400.0,
                    min=800.0,
                    max=3600.0
                )
                with patch('psutil.virtual_memory') as mock_mem:
                    mock_mem.return_value = MagicMock(
                        total=16 * (1024**3),
                        available=8 * (1024**3),
                        percent=50.0
                    )
                    with patch('psutil.disk_usage') as mock_disk:
                        mock_disk.return_value = MagicMock(
                            total=500 * (1024**3),
                            free=200 * (1024**3),
                            percent=60.0
                        )
                        with patch('psutil.boot_time', return_value=1234567890):
                            info = get_system_info()
                            
                            assert "cpu_count" in info
                            assert "cpu_freq" in info
                            assert "memory" in info
                            assert "disk" in info
                            assert "boot_time" in info
                            assert info["cpu_count"] == 8

    def test_get_system_info_no_cpu_freq(self):
        """测试获取系统信息（无CPU频率）。"""
        from src.core.monitor import get_system_info
        
        with patch('psutil.cpu_count', return_value=4):
            with patch('psutil.cpu_freq', return_value=None):
                with patch('psutil.virtual_memory') as mock_mem:
                    mock_mem.return_value = MagicMock(
                        total=8 * (1024**3),
                        available=4 * (1024**3),
                        percent=50.0
                    )
                    with patch('psutil.disk_usage') as mock_disk:
                        mock_disk.return_value = MagicMock(
                            total=256 * (1024**3),
                            free=128 * (1024**3),
                            percent=50.0
                        )
                        with patch('psutil.boot_time', return_value=1234567890):
                            info = get_system_info()
                            
                            assert info["cpu_freq"] == {}


class TestMonitorModule:
        """测试模块可导入。"""
        from src.core import monitor
        assert hasattr(monitor, 'ResourceMonitor')
        assert hasattr(monitor, 'Alert')
        assert hasattr(monitor, 'AlertLevel')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
