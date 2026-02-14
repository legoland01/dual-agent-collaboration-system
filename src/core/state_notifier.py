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
    """状态通知器（增强版，支持队列写入）"""

    def __init__(self, webhook_config=None, dispatcher=None, queue_manager=None):
        """初始化状态通知器

        Args:
            webhook_config: WebhookConfig实例
            dispatcher: EventDispatcher实例（可选）
            queue_manager: TodoQueueManager实例（可选）
        """
        self.config = webhook_config
        self.dispatcher = dispatcher
        self.queue_manager = queue_manager
        self._default_webhook_url: Optional[str] = None
        self._use_enhancer: bool = True

    def set_default_webhook_url(self, url: str):
        """设置默认Webhook URL"""
        self._default_webhook_url = url

    def enable_enhancer(self, enabled: bool = True):
        """启用/禁用Webhook增强器"""
        self._use_enhancer = enabled

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

        if self._use_enhancer:
            return self._notify_with_enhancer(event.event_type, payload, target_url)

        return self._notify_direct(event.event_type, payload, target_url)

    def _notify_with_enhancer(self, event_type: str, payload: Dict, target_url: str) -> bool:
        """使用Webhook增强器发送通知"""
        try:
            from src.core.webhook_enhancer import WebhookEnhancer
            enhancer = WebhookEnhancer()

            enhanced_payload = enhancer.format_payload_with_id(
                payload,
                enhancer.generate_webhook_id(),
                event_type
            )

            notification = enhancer.send_with_retry(target_url, enhanced_payload, event_type)

            return notification.status == "sent"

        except ImportError:
            logger.warning("WebhookEnhancer不可用，使用直接发送")
            return self._notify_direct(event_type, payload, target_url)
        except Exception as e:
            logger.error(f"WebhookEnhancer发送失败: {e}")
            return self._notify_direct(event_type, payload, target_url)

    def _notify_direct(self, event_type: str, payload: Dict, target_url: str) -> bool:
        """直接发送通知（无增强）"""
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
                logger.info(f"状态变更通知已发送: {event_type}")
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

    def notify_todo_created(self, todo_id: str, content: str, agent_id: str, to_agent: str = None) -> bool:
        """通知TODO创建（增强版，支持写入队列）"""
        event = StateChangeEvent(
            event_type="todo.created",
            agent_id=agent_id,
            details={"todo_id": todo_id, "content": content}
        )
        
        webhook_result = self.notify(event)
        
        if self.queue_manager and to_agent:
            try:
                from .todo_queue_manager import TodoQueueItem
                queue_item = TodoQueueItem(
                    id=todo_id,
                    content=content,
                    from_agent=agent_id,
                    to_agent=to_agent,
                    priority="medium",
                    created_at=datetime.now().isoformat(),
                    read=False
                )
                queue_result = self.queue_manager.add(queue_item)
                logger.info(f"TODO已写入队列: {todo_id}")
            except Exception as e:
                logger.error(f"写入队列失败: {e}")
                queue_result = False
        else:
            queue_result = None

        return webhook_result or (queue_result if queue_result is not None else False)

    def notify_todo_completed(self, todo_id: str, content: str, agent_id: str, to_agent: str = None) -> bool:
        """通知TODO完成（增强版，支持标记队列）"""
        event = StateChangeEvent(
            event_type="todo.completed",
            agent_id=agent_id,
            details={"todo_id": todo_id, "content": content}
        )
        
        webhook_result = self.notify(event)
        
        if self.queue_manager and to_agent:
            try:
                self.queue_manager.mark_read(todo_id, to_agent)
                logger.info(f"TODO已标记为已读: {todo_id}")
            except Exception as e:
                logger.error(f"标记队列失败: {e}")

        return webhook_result

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
