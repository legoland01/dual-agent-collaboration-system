"""设计评审通知模块。

功能：
1. 评审完成后自动通知相关 Agent
2. 需求变更时通知相关 Agent
3. 签署完成时通知
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """通知类型。"""
    DESIGN_REVIEW_COMPLETE = "design_review_complete"
    REQUIREMENT_CHANGED = "requirement_changed"
    SIGNOFF_COMPLETE = "signoff_complete"
    PHASE_ADVANCE = "phase_advance"
    GENERAL = "general"


class NotificationPriority(Enum):
    """通知优先级。"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """通知。"""
    type: NotificationType
    title: str
    message: str
    sender: str
    recipients: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: NotificationPriority = NotificationPriority.NORMAL
    action_required: bool = False
    action_url: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "sender": self.sender,
            "recipients": self.recipients,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "action_required": self.action_required,
            "action_url": self.action_url
        }


class DesignReviewNotifier:
    """设计评审通知器。"""
    
    def __init__(self, project_path: str = "."):
        """初始化。
        
        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)
        self.notification_log: List[Dict] = []
        self.notification_file = self.project_path / "state" / "notifications.yaml"
    
    def _get_other_agent(self, agent_id: str) -> str:
        """获取另一个 Agent ID。"""
        return "agent1" if agent_id == "agent2" else "agent2"
    
    def _send_notification(self, notification: Notification):
        """发送通知。"""
        self.notification_log.append(notification.to_dict())
        
        logger.info(
            f"通知已发送 - 类型: {notification.type.value}, "
            f"发送给: {notification.recipients}, "
            f"标题: {notification.title}"
        )
        
        self._save_notification(notification)
    
    def _save_notification(self, notification: Notification):
        """保存通知到文件。"""
        notifications = self._load_notifications()
        notifications.append(notification.to_dict())
        
        try:
            import yaml
            with open(self.notification_file, 'w', encoding='utf-8') as f:
                yaml.dump(notifications, f, allow_unicode=True, sort_keys=False)
        except IOError as e:
            logger.error(f"保存通知失败: {e}")
    
    def _load_notifications(self) -> List[Dict]:
        """加载通知历史。"""
        if self.notification_file.exists():
            try:
                import yaml
                with open(self.notification_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or []
            except (IOError, yaml.YAMLError):
                pass
        return []
    
    def notify_design_review_complete(self, reviewer: str, version: str):
        """通知设计评审完成。
        
        Args:
            reviewer: 评审人 ID
            version: 设计版本
        """
        notification = Notification(
            type=NotificationType.DESIGN_REVIEW_COMPLETE,
            title="设计评审完成",
            message=f"Agent {reviewer} 已完成 v{version} 详细设计的评审。",
            sender=reviewer,
            recipients=[self._get_other_agent(reviewer)],
            action_required=True,
            action_url="docs/02-design/detailed_design_v2.1.0.md"
        )
        
        self._send_notification(notification)
    
    def notify_requirement_changed(self, changer: str, section: str):
        """通知需求变更。
        
        Args:
            changer: 变更人 ID
            section: 变更的章节
        """
        notification = Notification(
            type=NotificationType.REQUIREMENT_CHANGED,
            title="需求文档更新",
            message=f"Agent {changer} 更新了需求文档的 {section} 章节。",
            sender=changer,
            recipients=[self._get_other_agent(changer)],
            action_required=True,
            action_url="docs/01-requirements/requirements_v2.1.0.md"
        )
        
        self._send_notification(notification)
    
    def notify_signoff_complete(self, signer: str, stage: str):
        """通知签署完成。
        
        Args:
            signer: 签署人 ID
            stage: 签署的阶段
        """
        notification = Notification(
            type=NotificationType.SIGNOFF_COMPLETE,
            title=f"{stage} 阶段签署",
            message=f"Agent {signer} 已签署 {stage} 阶段。",
            sender=signer,
            recipients=[self._get_other_agent(signer)],
            action_required=False
        )
        
        self._send_notification(notification)
    
    def notify_phase_advance(self, actor: str, from_phase: str, to_phase: str):
        """通知阶段推进。
        
        Args:
            actor: 操作人 ID
            from_phase: 原始阶段
            to_phase: 目标阶段
        """
        notification = Notification(
            type=NotificationType.PHASE_ADVANCE,
            title="阶段推进",
            message=f"Agent {actor} 已将项目从 {from_phase} 推进到 {to_phase}。",
            sender=actor,
            recipients=[self._get_other_agent(actor)],
            action_required=False
        )
        
        self._send_notification(notification)
    
    def notify_general(self, title: str, message: str, sender: str, priority: NotificationPriority = NotificationPriority.NORMAL):
        """发送一般通知。
        
        Args:
            title: 通知标题
            message: 通知内容
            sender: 发送人 ID
            priority: 优先级
        """
        notification = Notification(
            type=NotificationType.GENERAL,
            title=title,
            message=message,
            sender=sender,
            recipients=[self._get_other_agent(sender)],
            priority=priority
        )
        
        self._send_notification(notification)
    
    def get_notifications(self, agent_id: str = None, limit: int = 10) -> List[Dict]:
        """获取通知历史。
        
        Args:
            agent_id: 筛选特定 Agent 的通知
            limit: 返回数量限制
            
        Returns:
            通知列表
        """
        notifications = self._load_notifications()
        
        if agent_id:
            notifications = [
                n for n in notifications
                if agent_id in n.get("recipients", []) or n.get("sender") == agent_id
            ]
        
        return notifications[-limit:]
    
    def get_unread_count(self, agent_id: str) -> int:
        """获取未读通知数量。"""
        notifications = self._load_notifications()
        return len([
            n for n in notifications
            if agent_id in n.get("recipients", []) and n.get("priority") in ["high", "urgent"]
        ])
    
    def clear_notifications(self, before_date: datetime = None) -> int:
        """清理旧通知。
        
        Args:
            before_date: 清理此日期之前的通知
            
        Returns:
            清理的通知数量
        """
        notifications = self._load_notifications()
        cutoff = before_date or datetime.now()
        
        original_count = len(notifications)
        notifications = [
            n for n in notifications
            if datetime.fromisoformat(n["timestamp"]) > cutoff
        ]
        
        if len(notifications) < original_count:
            try:
                import yaml
                with open(self.notification_file, 'w', encoding='utf-8') as f:
                    yaml.dump(notifications, f, allow_unicode=True, sort_keys=False)
            except IOError as e:
                logger.error(f"保存通知失败: {e}")
        
        return original_count - len(notifications)
    
    def get_notification_summary(self) -> Dict:
        """获取通知摘要。"""
        notifications = self._load_notifications()
        
        by_type = {}
        by_priority = {}
        
        for n in notifications:
            n_type = n.get("type", "unknown")
            n_priority = n.get("priority", "normal")
            by_type[n_type] = by_type.get(n_type, 0) + 1
            by_priority[n_priority] = by_priority.get(n_priority, 0) + 1
        
        return {
            "total": len(notifications),
            "by_type": by_type,
            "by_priority": by_priority,
            "action_required": len([n for n in notifications if n.get("action_required")])
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    notifier = DesignReviewNotifier(".")
    
    print("发送测试通知:")
    
    notifier.notify_design_review_complete("agent1", "2.1.0")
    notifier.notify_signoff_complete("agent2", "requirements")
    notifier.notify_phase_advance("agent1", "requirements", "design")
    
    print("\n通知摘要:")
    print(notifier.get_notification_summary())
    
    print("\n通知历史:")
    for n in notifier.get_notifications():
        print(f"  [{n['type']}] {n['title']}")
