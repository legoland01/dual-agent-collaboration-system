from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import requests
import logging

logger = logging.getLogger(__name__)


@dataclass
class StateChangeEvent:
    """状态变更事件"""
    event_type: str
    agent_id: str
    details: dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class StateNotifier:
    """状态通知器"""

    def __init__(self, webhook_config=None, dispatcher=None):
        """初始化状态通知器

        Args:
            webhook_config: WebhookConfig实例
            dispatcher: EventDispatcher实例（可选）
        """
        self.config = webhook_config
        self.dispatcher = dispatcher
        self._default_webhook_url: Optional[str] = None

    def set_default_webhook_url(self, url: str):
        """设置默认Webhook URL"""
        self._default_webhook_url = url

    def notify(self, event: StateChangeEvent, webhook_url: Optional[str] = None) -> bool:
        """发送状态变更通知

        Args:
            event: 状态变更事件
            webhook_url: 目标Webhook URL，默认使用配置的URL

        Returns:
            是否发送成功
        """
        target_url = webhook_url or self._default_webhook_url
        if not target_url:
            logger.warning("未配置Webhook URL，跳过通知")
            return False

        payload = self._format_payload(event)

        try:
            if self.dispatcher:
                from src.core.event_dispatcher import DispatchEvent
                dispatch_event = DispatchEvent(
                    event_type="state_notification",
                    source="oc-collab",
                    payload=payload
                )
                self.dispatcher.dispatch(dispatch_event)

            response = requests.post(
                target_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code in (200, 201, 204):
                logger.info(f"状态变更通知已发送: {event.event_type}")
                return True
            else:
                logger.error(f"状态变更通知发送失败: {response.status_code}")
                return False

        except requests.RequestException as e:
            logger.error(f"状态变更通知发送异常: {e}")
            return False

    def _format_payload(self, event: StateChangeEvent) -> dict:
        """格式化为GitHub兼容的Webhook Payload"""
        return {
            "action": event.event_type,
            "sender": {
                "login": event.agent_id
            },
            "repository": {
                "full_name": "oc-collab/state-notification"
            },
            "oc_collab": {
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "details": event.details
            },
            "ref": f"refs/heads/state-{event.event_type.replace('.', '-')}"
        }

    def notify_todo_created(self, todo_id: str, content: str, agent_id: str) -> bool:
        """通知TODO创建"""
        event = StateChangeEvent(
            event_type="todo.created",
            agent_id=agent_id,
            details={"todo_id": todo_id, "content": content}
        )
        return self.notify(event)

    def notify_todo_completed(self, todo_id: str, content: str, agent_id: str) -> bool:
        """通知TODO完成"""
        event = StateChangeEvent(
            event_type="todo.completed",
            agent_id=agent_id,
            details={"todo_id": todo_id, "content": content}
        )
        return self.notify(event)

    def notify_signoff_completed(self, stage: str, agent_id: str) -> bool:
        """通知签署完成"""
        event = StateChangeEvent(
            event_type="signoff.completed",
            agent_id=agent_id,
            details={"stage": stage}
        )
        return self.notify(event)

    def notify_phase_advanced(self, from_phase: str, to_phase: str, agent_id: str) -> bool:
        """通知阶段推进"""
        event = StateChangeEvent(
            event_type="phase.advanced",
            agent_id=agent_id,
            details={"from": from_phase, "to": to_phase}
        )
        return self.notify(event)

    def notify_bug_fixed(self, bug_id: str, description: str, agent_id: str) -> bool:
        """通知Bug修复"""
        event = StateChangeEvent(
            event_type="bug.fixed",
            agent_id=agent_id,
            details={"bug_id": bug_id, "description": description}
        )
        return self.notify(event)
