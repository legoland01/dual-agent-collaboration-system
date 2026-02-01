"""M4 增强功能测试。

测试用例：
- ConfigHotReloader 配置热重载
- ErrorMessageFormatter 错误消息格式化
- IterationStatusManager 迭代状态管理
- DesignReviewNotifier 评审通知
"""
import pytest
import tempfile
import os
import time
from pathlib import Path
import yaml


class TestConfigReloader:
    """配置热重载测试。"""

    def test_config_reloader_initialization(self):
        """测试配置加载器初始化。"""
        from src.core.config_reloader import ConfigReloader
        reloader = ConfigReloader(config_paths={"test": "config.yaml"})
        assert reloader is not None
        assert reloader.configs == {}
        assert reloader.mtimes == {}

    def test_config_reloader_load_all(self, tmp_path):
        """测试加载所有配置。"""
        from src.core.config_reloader import ConfigReloader
        
        config_file = tmp_path / "test.yaml"
        config_file.write_text("key: value\nname: test")
        
        reloader = ConfigReloader(config_paths={"test": str(config_file)})
        configs = reloader.load_all()
        
        assert "test" in configs
        assert configs["test"]["key"] == "value"
        assert configs["test"]["name"] == "test"

    def test_config_reloader_get(self, tmp_path):
        """测试获取配置。"""
        from src.core.config_reloader import ConfigReloader
        
        config_file = tmp_path / "test.yaml"
        config_file.write_text("version: 1.0.0\ndebug: true")
        
        reloader = ConfigReloader(config_paths={"test": str(config_file)})
        reloader.load_all()
        
        config = reloader.get("test")
        assert config["version"] == "1.0.0"
        assert config["debug"] is True

    def test_config_reloader_add_remove(self, tmp_path):
        """测试添加和移除配置。"""
        from src.core.config_reloader import ConfigReloader
        
        reloader = ConfigReloader(config_paths={})
        
        config_file1 = tmp_path / "config1.yaml"
        config_file1.write_text("id: 1")
        reloader.add_config("config1", str(config_file1))
        
        config_file2 = tmp_path / "config2.yaml"
        config_file2.write_text("id: 2")
        reloader.add_config("config2", str(config_file2))
        
        assert reloader.get("config1")["id"] == 1
        assert reloader.get("config2")["id"] == 2
        
        reloader.remove_config("config1")
        assert reloader.get("config1") is None

    def test_config_reloader_status(self, tmp_path):
        """测试获取状态。"""
        from src.core.config_reloader import ConfigReloader
        
        config_file = tmp_path / "test.yaml"
        config_file.write_text("test: value")
        
        reloader = ConfigReloader(config_paths={"test": str(config_file)})
        reloader.load_all()
        
        status = reloader.get_status()
        assert status["monitoring"] is False
        assert status["config_count"] == 1


class TestErrorMessageFormatter:
    """错误消息格式化测试。"""

    def test_formatter_initialization(self):
        """测试格式化器初始化。"""
        from src.core.error_templates import ErrorMessageFormatter
        formatter = ErrorMessageFormatter()
        assert formatter is not None
        assert len(formatter.templates) > 0

    def test_format_git_error(self):
        """测试格式化 Git 错误。"""
        from src.core.error_templates import ErrorMessageFormatter
        formatter = ErrorMessageFormatter()
        
        result = formatter.format(Exception("git fetch failed: connection refused"))
        
        assert result["category"] == "git"
        assert "Git" in result["friendly_message"]

    def test_format_yaml_error(self):
        """测试格式化 YAML 错误。"""
        from src.core.error_templates import ErrorMessageFormatter
        formatter = ErrorMessageFormatter()
        
        result = formatter.format(Exception("YAML parse error: mapping values"))
        
        assert result["category"] == "yaml"

    def test_format_permission_error(self):
        """测试格式化权限错误。"""
        from src.core.error_templates import ErrorMessageFormatter
        formatter = ErrorMessageFormatter()
        
        result = formatter.format(Exception("Permission denied: access denied"))
        
        assert result["category"] == "permission"
        assert "权限" in result["friendly_message"]

    def test_format_file_not_found(self):
        """测试格式化文件不存在错误。"""
        from src.core.error_templates import ErrorMessageFormatter
        formatter = ErrorMessageFormatter()
        
        result = formatter.format(Exception("File not found: /path/to/file"))
        
        assert result["category"] == "file"

    def test_format_unknown_error(self):
        """测试格式化未知错误。"""
        from src.core.error_templates import ErrorMessageFormatter
        formatter = ErrorMessageFormatter()
        
        result = formatter.format(Exception("Some unknown error"))
        
        assert result["category"] == "unknown"
        assert "未知" in result["friendly_message"]

    def test_format_simple(self):
        """测试简单格式化。"""
        from src.core.error_templates import ErrorMessageFormatter
        formatter = ErrorMessageFormatter()
        
        output = formatter.format_simple(Exception("Some unknown error"))
        
        assert "未知" in output
        assert "建议:" in output

    def test_add_custom_template(self):
        """测试添加自定义模板。"""
        from src.core.error_templates import ErrorMessageFormatter, ErrorCategory
        formatter = ErrorMessageFormatter()
        
        initial_count = len(formatter.templates)
        formatter.add_template(
            pattern=r"custom error",
            friendly_message="自定义错误",
            suggestion="请检查自定义配置",
            category=ErrorCategory.STATE
        )
        
        assert len(formatter.templates) == initial_count + 1


class TestIterationStatusManager:
    """迭代状态管理测试。"""

    def test_iteration_status_enum(self):
        """测试迭代状态枚举。"""
        from src.core.iteration_status_manager import IterationStatus, PhaseStatus
        
        assert IterationStatus.PENDING.value == "pending"
        assert IterationStatus.IN_PROGRESS.value == "in_progress"
        assert IterationStatus.COMPLETED.value == "completed"
        assert PhaseStatus.PENDING.value == "pending"

    def test_iteration_state_dataclass(self):
        """测试迭代状态数据类。"""
        from src.core.iteration_status_manager import IterationState
        
        state = IterationState(version="2.1.0")
        assert state.version == "2.1.0"
        assert state.status == "pending"
        assert state.requirements == "pending"

    def test_iteration_status_manager_init(self, tmp_path):
        """测试管理器初始化。"""
        from src.core.iteration_status_manager import IterationStatusManager
        
        state_file = tmp_path / "state.yaml"
        state_file.write_text("version: '2.1.0'")
        
        manager = IterationStatusManager(str(state_file))
        assert manager is not None

    def test_get_progress(self, tmp_path):
        """测试获取进度。"""
        from src.core.iteration_status_manager import IterationStatusManager
        
        state_file = tmp_path / "state.yaml"
        state_content = {
            "version": "2.1.0",
            "iteration": {"current": "v2.1.0", "status": "in_progress"},
            "iterations": {
                "v2.1.0": {
                    "version": "v2.1.0",
                    "status": "in_progress",
                    "requirements": "completed",
                    "design": "in_progress",
                    "development": "pending",
                    "testing": "pending",
                    "deployment": "pending",
                    "history": []
                }
            }
        }
        state_file.write_text(yaml.dump(state_content))
        
        manager = IterationStatusManager(str(state_file))
        progress = manager.get_progress("v2.1.0")
        
        assert progress["version"] == "v2.1.0"
        assert progress["completed_phases"] == 1
        assert progress["progress_percent"] == 20.0

    def test_validate_consistency(self, tmp_path):
        """测试一致性验证。"""
        from src.core.iteration_status_manager import IterationStatusManager
        
        state_file = tmp_path / "state.yaml"
        state_content = {
            "version": "2.1.0",
            "iteration": {"current": "v2.1.0", "status": "in_progress"},
            "iterations": {
                "v2.1.0": {
                    "version": "v2.1.0",
                    "status": "in_progress",
                    "requirements": "completed",
                    "design": "completed",
                    "development": "completed",
                    "testing": "completed",
                    "deployment": "completed",
                    "history": []
                }
            }
        }
        state_file.write_text(yaml.dump(state_content))
        
        manager = IterationStatusManager(str(state_file))
        result = manager.validate_consistency("v2.1.0")
        
        assert result["valid"] is True


class TestDesignReviewNotifier:
    """设计评审通知测试。"""

    def test_notification_enum(self):
        """测试通知类型枚举。"""
        from src.core.design_review_notifier import NotificationType, NotificationPriority
        
        assert NotificationType.DESIGN_REVIEW_COMPLETE.value == "design_review_complete"
        assert NotificationPriority.HIGH.value == "high"

    def test_notification_dataclass(self):
        """测试通知数据类。"""
        from src.core.design_review_notifier import Notification, NotificationType
        
        notification = Notification(
            type=NotificationType.DESIGN_REVIEW_COMPLETE,
            title="测试通知",
            message="这是一条测试消息",
            sender="agent1",
            recipients=["agent2"]
        )
        
        assert notification.title == "测试通知"
        assert notification.sender == "agent1"
        assert notification.action_required is False

    def test_notifier_initialization(self, tmp_path):
        """测试通知器初始化。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        
        notifier = DesignReviewNotifier(str(tmp_path))
        assert notifier is not None
        assert notifier.notification_log == []

    def test_notify_design_review_complete(self, tmp_path):
        """测试设计评审完成通知。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        
        notifier = DesignReviewNotifier(str(tmp_path))
        notifier.notify_design_review_complete("agent1", "2.1.0")
        
        assert len(notifier.notification_log) == 1
        log = notifier.notification_log[0]
        assert log["type"] == "design_review_complete"
        assert log["recipients"] == ["agent2"]

    def test_notify_signoff_complete(self, tmp_path):
        """测试签署完成通知。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        
        notifier = DesignReviewNotifier(str(tmp_path))
        notifier.notify_signoff_complete("agent2", "requirements")
        
        assert len(notifier.notification_log) == 1
        log = notifier.notification_log[0]
        assert "requirements" in log["message"]

    def test_notify_phase_advance(self, tmp_path):
        """测试阶段推进通知。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        
        notifier = DesignReviewNotifier(str(tmp_path))
        notifier.notify_phase_advance("agent1", "requirements", "design")
        
        assert len(notifier.notification_log) == 1
        log = notifier.notification_log[0]
        assert "requirements" in log["message"]
        assert "design" in log["message"]

    def test_get_notifications(self, tmp_path):
        """测试获取通知。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        
        notifier = DesignReviewNotifier(str(tmp_path))
        
        (tmp_path / "state").mkdir(exist_ok=True)
        
        notifier.notify_design_review_complete("agent1", "2.1.0")
        notifier.notify_signoff_complete("agent2", "design")
        
        notifications = notifier.get_notifications()
        assert len(notifications) == 2

    def test_get_notification_summary(self, tmp_path):
        """测试获取通知摘要。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        
        notifier = DesignReviewNotifier(str(tmp_path))
        
        (tmp_path / "state").mkdir(exist_ok=True)
        
        notifier.notify_design_review_complete("agent1", "2.1.0")
        
        summary = notifier.get_notification_summary()
        assert summary["total"] == 1
        assert "design_review_complete" in summary["by_type"]


class TestM4Integration:
    """M4 集成测试。"""

    def test_all_modules_importable(self):
        """测试所有模块可导入。"""
        from src.core.config_reloader import ConfigReloader
        from src.core.error_templates import ErrorMessageFormatter
        from src.core.iteration_status_manager import IterationStatusManager
        from src.core.design_review_notifier import DesignReviewNotifier
        
        assert ConfigReloader is not None
        assert ErrorMessageFormatter is not None
        assert IterationStatusManager is not None
        assert DesignReviewNotifier is not None

    def test_config_reloader_with_error_formatting(self, tmp_path):
        """测试配置加载器与错误格式化集成。"""
        from src.core.config_reloader import ConfigReloader, ConfigReloadError
        from src.core.error_templates import ErrorMessageFormatter
        
        formatter = ErrorMessageFormatter()
        
        reloader = ConfigReloader(config_paths={"nonexistent": "/nonexistent/path.yaml"})
        
        try:
            reloader.load_all()
        except ConfigReloadError:
            result = formatter.format(ConfigReloadError("Config load failed"))
            assert result["category"] in ["file", "unknown"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
