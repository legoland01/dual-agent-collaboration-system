"""DesignReviewNotifier 单元测试。"""
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.design_review_notifier import (
    DesignReviewNotifier, Notification, NotificationType, NotificationPriority
)


class TestNotificationType:
    """通知类型枚举测试。"""

    def test_notification_type_values(self):
        """测试通知类型值。"""
        assert NotificationType.DESIGN_REVIEW_COMPLETE.value == "design_review_complete"
        assert NotificationType.REQUIREMENT_CHANGED.value == "requirement_changed"
        assert NotificationType.SIGNOFF_COMPLETE.value == "signoff_complete"


class TestNotificationPriority:
    """通知优先级枚举测试。"""

    def test_notification_priority_values(self):
        """测试通知优先级值。"""
        assert NotificationPriority.LOW.value == "low"
        assert NotificationPriority.NORMAL.value == "normal"
        assert NotificationPriority.HIGH.value == "high"


class TestNotification:
    """通知测试。"""

    def test_notification_creation(self):
        """测试创建通知。"""
        notification = Notification(
            type=NotificationType.DESIGN_REVIEW_COMPLETE,
            title="评审完成",
            message="设计评审已完成",
            sender="system",
            recipients=["agent1", "agent2"]
        )
        assert notification.type == NotificationType.DESIGN_REVIEW_COMPLETE
        assert notification.title == "评审完成"
        assert notification.sender == "system"
        assert len(notification.recipients) == 2

    def test_notification_defaults(self):
        """测试通知默认值。"""
        notification = Notification(
            type=NotificationType.GENERAL,
            title="Test",
            message="Test message",
            sender="test",
            recipients=[]
        )
        assert notification.timestamp is not None
        assert notification.priority == NotificationPriority.NORMAL
        assert notification.action_required is False
        assert notification.action_url == ""

    def test_notification_with_priority(self):
        """测试带优先级的通知。"""
        notification = Notification(
            type=NotificationType.PHASE_ADVANCE,
            title="Urgent",
            message="Urgent message",
            sender="system",
            recipients=["agent1"],
            priority=NotificationPriority.HIGH,
            action_required=True,
            action_url="https://example.com/action"
        )
        assert notification.priority == NotificationPriority.HIGH
        assert notification.action_required is True
        assert notification.action_url == "https://example.com/action"

    def test_notification_to_dict(self):
        """测试通知转换为字典。"""
        notification = Notification(
            type=NotificationType.DESIGN_REVIEW_COMPLETE,
            title="Test",
            message="Test message",
            sender="test",
            recipients=["agent1"]
        )
        result = notification.to_dict()
        
        assert result["type"] == "design_review_complete"
        assert result["title"] == "Test"
        assert result["sender"] == "test"
        assert "timestamp" in result


class TestDesignReviewNotifier:
    """设计评审通知器测试类。"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def notifier(self, temp_dir):
        """创建通知器实例。"""
        return DesignReviewNotifier(project_path=temp_dir)

    def test_init(self, temp_dir):
        """测试初始化。"""
        notifier = DesignReviewNotifier(project_path=temp_dir)
        assert notifier.project_path == Path(temp_dir)
        assert notifier.notification_log == []

    def test_send_notification(self, notifier):
        """测试发送通知。"""
        notification = Notification(
            type=NotificationType.DESIGN_REVIEW_COMPLETE,
            title="评审完成",
            message="设计评审已完成",
            sender="system",
            recipients=["agent1", "agent2"]
        )
        notifier._send_notification(notification)
        
        assert len(notifier.notification_log) == 1

    def test_send_notification_with_priority(self, notifier):
        """测试发送高优先级通知。"""
        notification = Notification(
            type=NotificationType.PHASE_ADVANCE,
            title="阶段推进",
            message="项目阶段已推进",
            sender="system",
            recipients=["agent1"],
            priority=NotificationPriority.HIGH
        )
        notifier._send_notification(notification)
        
        assert len(notifier.notification_log) == 1

    def test_get_other_agent(self, notifier):
        """测试获取另一个Agent。"""
        assert notifier._get_other_agent("agent1") == "agent2"
        assert notifier._get_other_agent("agent2") == "agent1"

    def test_load_notifications_empty(self, notifier):
        """测试加载通知（空）。"""
        notifications = notifier._load_notifications()
        assert notifications == []

    def test_load_notifications_with_file(self, notifier):
        """测试加载通知（带文件）。"""
        notification_file = notifier.project_path / "state" / "notifications.yaml"
        notification_file.parent.mkdir(parents=True, exist_ok=True)
        notification_file.write_text("- type: design_review_complete\n  title: Test\n")
        
        notifications = notifier._load_notifications()
        assert len(notifications) == 1

    def test_notify_design_review_complete(self, notifier):
        """测试评审完成通知。"""
        notifier.notify_design_review_complete(
            reviewer="agent1",
            version="2.1.0"
        )
        
        assert len(notifier.notification_log) == 1
        log_entry = notifier.notification_log[0]
        assert log_entry["type"] == "design_review_complete"
        assert "agent1" in log_entry["message"]
        assert "2.1.0" in log_entry["message"]

    def test_notify_requirement_changed(self, notifier):
        """测试需求变更通知。"""
        notifier.notify_requirement_changed(
            changer="agent1",
            section="功能需求"
        )
        
        assert len(notifier.notification_log) == 1
        log_entry = notifier.notification_log[0]
        assert log_entry["type"] == "requirement_changed"
        assert "agent1" in log_entry["message"]
        assert "功能需求" in log_entry["message"]

    def test_notify_signoff_complete(self, notifier):
        """测试签署完成通知。"""
        notifier.notify_signoff_complete(
            signer="agent1",
            stage="requirements"
        )
        
        assert len(notifier.notification_log) == 1
        log_entry = notifier.notification_log[0]
        assert log_entry["type"] == "signoff_complete"
        assert "agent1" in log_entry["message"]
        assert "requirements" in log_entry["message"]

    def test_notify_phase_advance(self, notifier):
        """测试阶段推进通知。"""
        notifier.notify_phase_advance(
            actor="agent1",
            from_phase="development",
            to_phase="testing"
        )
        
        assert len(notifier.notification_log) == 1
        log_entry = notifier.notification_log[0]
        assert log_entry["type"] == "phase_advance"
        assert "development" in log_entry["message"]
        assert "testing" in log_entry["message"]


class TestDesignReviewNotifierModule:
    """设计评审通知器模块测试。"""

    def test_module_importable(self):
        """测试模块可导入。"""
        from src.core import design_review_notifier
        assert hasattr(design_review_notifier, 'DesignReviewNotifier')
        assert hasattr(design_review_notifier, 'Notification')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
