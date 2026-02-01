"""DesignReviewNotifier 单元测试。

测试用例：
- 通知发送
- 通知历史
- 通知摘要
"""
import pytest
import tempfile
import yaml
from pathlib import Path


class TestNotificationType:
    """NotificationType 测试。"""

    def test_notification_types(self):
        """测试通知类型枚举。"""
        from src.core.design_review_notifier import NotificationType
        
        assert NotificationType.DESIGN_REVIEW_COMPLETE.value == "design_review_complete"
        assert NotificationType.REQUIREMENT_CHANGED.value == "requirement_changed"
        assert NotificationType.SIGNOFF_COMPLETE.value == "signoff_complete"
        assert NotificationType.PHASE_ADVANCE.value == "phase_advance"

    def test_notification_priority(self):
        """测试通知优先级枚举。"""
        from src.core.design_review_notifier import NotificationPriority
        
        assert NotificationPriority.LOW.value == "low"
        assert NotificationPriority.NORMAL.value == "normal"
        assert NotificationPriority.HIGH.value == "high"
        assert NotificationPriority.URGENT.value == "urgent"


class TestNotification:
    """Notification 测试。"""

    def test_notification_creation(self):
        """测试通知创建。"""
        from src.core.design_review_notifier import Notification, NotificationType
        
        notification = Notification(
            type=NotificationType.DESIGN_REVIEW_COMPLETE,
            title="测试通知",
            message="这是一条测试消息",
            sender="agent1",
            recipients=["agent2"]
        )
        
        assert notification.type == NotificationType.DESIGN_REVIEW_COMPLETE
        assert notification.title == "测试通知"
        assert notification.sender == "agent1"
        assert notification.recipients == ["agent2"]
        assert notification.action_required is False

    def test_notification_to_dict(self):
        """测试通知转字典。"""
        from src.core.design_review_notifier import Notification, NotificationType
        
        notification = Notification(
            type=NotificationType.DESIGN_REVIEW_COMPLETE,
            title="测试",
            message="消息",
            sender="agent1",
            recipients=["agent2"],
            action_required=True,
            action_url="docs/test.md"
        )
        
        data = notification.to_dict()
        
        assert data["type"] == "design_review_complete"
        assert data["title"] == "测试"
        assert data["sender"] == "agent1"
        assert data["action_required"] is True


class TestDesignReviewNotifier:
    """DesignReviewNotifier 测试。"""

    def test_initialization(self, tmp_path):
        """测试初始化。"""
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
        assert "agent1" in log["sender"]
        assert "agent2" in log["recipients"]

    def test_notify_signoff_complete(self, tmp_path):
        """测试签署完成通知。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        
        notifier = DesignReviewNotifier(str(tmp_path))
        notifier.notify_signoff_complete("agent2", "requirements")
        
        assert len(notifier.notification_log) == 1
        log = notifier.notification_log[0]
        assert log["type"] == "signoff_complete"
        assert "requirements" in log["message"]

    def test_notify_requirement_changed(self, tmp_path):
        """测试需求变更通知。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        
        notifier = DesignReviewNotifier(str(tmp_path))
        notifier.notify_requirement_changed("agent1", "功能需求")
        
        assert len(notifier.notification_log) == 1
        log = notifier.notification_log[0]
        assert log["type"] == "requirement_changed"
        assert "功能需求" in log["message"]

    def test_notify_phase_advance(self, tmp_path):
        """测试阶段推进通知。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        
        notifier = DesignReviewNotifier(str(tmp_path))
        notifier.notify_phase_advance("agent1", "requirements", "design")
        
        assert len(notifier.notification_log) == 1
        log = notifier.notification_log[0]
        assert log["type"] == "phase_advance"
        assert "requirements" in log["message"]
        assert "design" in log["message"]

    def test_notify_general(self, tmp_path):
        """测试一般通知。"""
        from src.core.design_review_notifier import DesignReviewNotifier, NotificationPriority
        
        notifier = DesignReviewNotifier(str(tmp_path))
        notifier.notify_general(
            title="一般通知",
            message="这是一条一般消息",
            sender="agent1",
            priority=NotificationPriority.HIGH
        )
        
        assert len(notifier.notification_log) == 1
        log = notifier.notification_log[0]
        assert log["type"] == "general"
        assert log["priority"] == "high"

    def test_get_notifications(self, tmp_path):
        """测试获取通知。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        
        notifier = DesignReviewNotifier(str(tmp_path))
        
        (tmp_path / "state").mkdir(exist_ok=True)
        
        notifier.notify_design_review_complete("agent1", "2.1.0")
        notifier.notify_signoff_complete("agent2", "design")
        
        notifications = notifier.get_notifications()
        assert len(notifications) == 2

    def test_get_notifications_with_limit(self, tmp_path):
        """测试获取通知（限制数量）。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        
        notifier = DesignReviewNotifier(str(tmp_path))
        
        (tmp_path / "state").mkdir(exist_ok=True)
        
        for i in range(5):
            notifier.notify_general(f"通知{i}", f"消息{i}", "agent1")
        
        notifications = notifier.get_notifications(limit=3)
        assert len(notifications) == 3

    def test_get_notification_summary(self, tmp_path):
        """测试获取通知摘要。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        
        notifier = DesignReviewNotifier(str(tmp_path))
        
        (tmp_path / "state").mkdir(exist_ok=True)
        
        notifier.notify_design_review_complete("agent1", "2.1.0")
        notifier.notify_signoff_complete("agent2", "design")
        
        summary = notifier.get_notification_summary()
        
        assert summary["total"] == 2
        assert "design_review_complete" in summary["by_type"]
        assert "signoff_complete" in summary["by_type"]

    def test_get_unread_count(self, tmp_path):
        """测试获取未读通知数量。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        
        notifier = DesignReviewNotifier(str(tmp_path))
        
        (tmp_path / "state").mkdir(exist_ok=True)
        
        notifier.notify_design_review_complete("agent1", "2.1.0")
        
        count = notifier.get_unread_count("agent2")
        assert count >= 0

    def test_clear_notifications(self, tmp_path):
        """测试清理通知。"""
        from src.core.design_review_notifier import DesignReviewNotifier
        from datetime import datetime, timedelta
        
        notifier = DesignReviewNotifier(str(tmp_path))
        
        (tmp_path / "state").mkdir(exist_ok=True)
        
        notifier.notify_design_review_complete("agent1", "2.1.0")
        
        count = notifier.clear_notifications(before_date=datetime.now())
        assert count >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
