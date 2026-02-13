"""Webhook状态通知增强

F-WEB-006: Webhook状态通知增强
增加状态追踪和重试机制
"""
import uuid
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import requests
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class WebhookNotification:
    """Webhook通知"""
    webhook_id: str
    event_type: str
    payload: Dict
    status: str = "pending"
    retry_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    sent_at: Optional[str] = None
    failed_at: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class WebhookStats:
    """Webhook统计"""
    total: int = 0
    sent: int = 0
    failed: int = 0
    retried: int = 0
    pending: int = 0


class WebhookEnhancer:
    """Webhook增强器"""

    STATS_FILE = "state/webhook_stats.yaml"

    def __init__(self, project_path: Optional[str] = None):
        """
        初始化Webhook增强器

        Args:
            project_path: 项目路径，默认当前目录
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.stats_file = self.project_path / self.STATS_FILE
        self.max_retries = 1
        self.retry_delay = 1

    def generate_webhook_id(self) -> str:
        """
        生成唯一Webhook ID

        Returns:
            str: UUID格式的Webhook ID
        """
        return str(uuid.uuid4())

    def send_with_retry(
        self,
        webhook_url: str,
        payload: Dict,
        event_type: str,
    ) -> WebhookNotification:
        """
        发送Webhook通知（带重试机制）

        Args:
            webhook_url: 目标URL
            payload: 通知内容
            event_type: 事件类型

        Returns:
            WebhookNotification: 通知结果
        """
        notification = WebhookNotification(
            webhook_id=self.generate_webhook_id(),
            event_type=event_type,
            payload=payload,
        )

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code in (200, 201, 204):
                notification.status = "sent"
                notification.sent_at = datetime.now().isoformat()
                logger.info(f"Webhook发送成功: {notification.webhook_id}")
            else:
                notification.status = "failed"
                notification.failed_at = datetime.now().isoformat()
                notification.error_message = f"HTTP {response.status_code}"
                logger.error(f"Webhook发送失败: {notification.webhook_id} - {notification.error_message}")

        except requests.RequestException as e:
            if notification.retry_count < self.max_retries:
                notification.retry_count += 1
                notification.status = "retried"
                logger.warning(f"Webhook重试 {notification.retry_count}/{self.max_retries}: {notification.webhook_id}")

                import time
                time.sleep(self.retry_delay)

                try:
                    response = requests.post(
                        webhook_url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=10,
                    )
                    if response.status_code in (200, 201, 204):
                        notification.status = "sent"
                        notification.sent_at = datetime.now().isoformat()
                        logger.info(f"Webhook重试成功: {notification.webhook_id}")
                    else:
                        notification.status = "failed"
                        notification.failed_at = datetime.now().isoformat()
                        notification.error_message = f"HTTP {response.status_code}"
                except Exception:
                    notification.status = "failed"
                    notification.failed_at = datetime.now().isoformat()
                    notification.error_message = str(e)
            else:
                notification.status = "failed"
                notification.failed_at = datetime.now().isoformat()
                notification.error_message = str(e)
                logger.error(f"Webhook发送失败: {notification.webhook_id} - {notification.error_message}")

        self._save_notification(notification)

        return notification

    def _save_notification(self, notification: WebhookNotification):
        """
        保存通知记录

        Args:
            notification: 通知对象
        """
        stats = self._load_stats()

        stats["notifications"].append({
            "webhook_id": notification.webhook_id,
            "event_type": notification.event_type,
            "status": notification.status,
            "retry_count": notification.retry_count,
            "created_at": notification.created_at,
            "sent_at": notification.sent_at,
            "failed_at": notification.failed_at,
            "error_message": notification.error_message,
        })

        stats["total"] += 1
        if notification.status == "sent":
            stats["sent"] += 1
        elif notification.status == "failed":
            stats["failed"] += 1
        elif notification.status == "retried":
            stats["retried"] += 1

        self._save_stats(stats)

    def _load_stats(self) -> Dict:
        """
        加载统计数据

        Returns:
            Dict: 统计数据
        """
        if not self.stats_file.exists():
            return {
                "notifications": [],
                "total": 0,
                "sent": 0,
                "failed": 0,
                "retried": 0,
                "last_updated": datetime.now().isoformat(),
            }

        try:
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {
                    "notifications": [],
                    "total": 0,
                    "sent": 0,
                    "failed": 0,
                    "retried": 0,
                }
        except Exception as e:
            logger.error(f"加载Webhook统计失败: {e}")
            return {
                "notifications": [],
                "total": 0,
                "sent": 0,
                "failed": 0,
                "retried": 0,
            }

    def _save_stats(self, stats: Dict):
        """
        保存统计数据

        Args:
            stats: 统计数据
        """
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)

        stats["last_updated"] = datetime.now().isoformat()

        with open(self.stats_file, 'w', encoding='utf-8') as f:
            yaml.dump(stats, f, allow_unicode=True, sort_keys=False)

    def get_stats(self) -> WebhookStats:
        """
        获取Webhook统计

        Returns:
            WebhookStats: 统计信息
        """
        stats = self._load_stats()

        return WebhookStats(
            total=stats.get("total", 0),
            sent=stats.get("sent", 0),
            failed=stats.get("failed", 0),
            retried=stats.get("retried", 0),
            pending=stats.get("total", 0) - stats.get("sent", 0) - stats.get("failed", 0),
        )

    def get_notification(self, webhook_id: str) -> Optional[Dict]:
        """
        获取单个通知详情

        Args:
            webhook_id: Webhook ID

        Returns:
            Optional[Dict]: 通知详情
        """
        stats = self._load_stats()

        for notification in stats.get("notifications", []):
            if notification.get("webhook_id") == webhook_id:
                return notification

        return None

    def get_recent_notifications(self, limit: int = 10) -> list:
        """
        获取最近的n条通知

        Args:
            limit: 返回数量限制

        Returns:
            list: 通知列表
        """
        stats = self._load_stats()

        notifications = stats.get("notifications", [])
        return sorted(notifications, key=lambda x: x.get("created_at", ""), reverse=True)[:limit]

    def format_payload_with_id(self, payload: Dict, webhook_id: str, event_type: str) -> Dict:
        """
        格式化为带ID的Payload

        Args:
            payload: 原始Payload
            webhook_id: 通知ID
            event_type: 事件类型

        Returns:
            Dict: 增强后的Payload
        """
        return {
            **payload,
            "webhook_id": webhook_id,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
        }
