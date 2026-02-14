"""
状态队列管理器

管理通知的持久化和查询。
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import json
import uuid
import logging

logger = logging.getLogger(__name__)


@dataclass
class Notification:
    """通知"""
    id: str
    event_type: str
    source_agent: str
    target_agent: str
    payload: dict
    timestamp: str
    status: str = "pending"
    retry_count: int = 0
    max_retries: int = 3


class StateQueueManager:
    """状态队列管理器"""

    def __init__(self, queue_file: str = "state/state_queue.json"):
        """
        Args:
            queue_file: 队列文件路径
        """
        self.queue_file = Path(queue_file)
        self._ensure_queue_file()

    def _ensure_queue_file(self):
        """确保队列文件存在"""
        try:
            if not self.queue_file.parent.exists():
                self.queue_file.parent.mkdir(parents=True)

            if not self.queue_file.exists():
                self._save({
                    "queue_id": str(uuid.uuid4()),
                    "notifications": [],
                    "last_updated": None
                })
        except Exception as e:
            logger.error(f"初始化队列文件失败: {e}")

    def _load(self) -> dict:
        """加载队列"""
        try:
            with open(self.queue_file) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载队列失败: {e}")
            return {"queue_id": "", "notifications": [], "last_updated": None}

    def _save(self, data: dict):
        """保存队列"""
        try:
            data["last_updated"] = datetime.utcnow().isoformat()
            with open(self.queue_file, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存队列失败: {e}")

    def enqueue(self, data: dict) -> Notification:
        """
        入队列

        Args:
            data: 通知数据

        Returns:
            Notification: 创建的通知
        """
        queue = self._load()

        notification = Notification(
            id=str(uuid.uuid4())[:8],
            event_type=data.get("event_type", "unknown"),
            source_agent=data.get("source_agent", "unknown"),
            target_agent=data.get("target_agent", "unknown"),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            status="pending"
        )

        queue["notifications"].append(notification.__dict__)
        self._save(queue)

        logger.info(f"通知已入队列: {notification.id}")
        return notification

    def get_unread(self, agent_id: str) -> list[Notification]:
        """
        获取未读通知

        Args:
            agent_id: Agent ID

        Returns:
            list[Notification]: 未读通知列表
        """
        queue = self._load()
        return [
            Notification(**n) for n in queue["notifications"]
            if n["target_agent"] == agent_id and n["status"] == "pending"
        ]

    def get_all_unread(self) -> list[Notification]:
        """获取所有未读通知"""
        queue = self._load()
        return [
            Notification(**n) for n in queue["notifications"]
            if n["status"] == "pending"
        ]

    def mark_read(self, notification_id: str) -> bool:
        """
        标记为已读

        Args:
            notification_id: 通知ID

        Returns:
            bool: 是否成功
        """
        queue = self._load()

        for n in queue["notifications"]:
            if n["id"] == notification_id:
                n["status"] = "read"
                self._save(queue)
                logger.info(f"通知已标记为已读: {notification_id}")
                return True

        return False

    def mark_all_read(self, agent_id: str) -> int:
        """
        标记所有通知为已读

        Args:
            agent_id: Agent ID

        Returns:
            int: 标记数量
        """
        queue = self._load()
        count = 0

        for n in queue["notifications"]:
            if n["target_agent"] == agent_id and n["status"] == "pending":
                n["status"] = "read"
                count += 1

        if count > 0:
            self._save(queue)
            logger.info(f"已标记{count}个通知为已读")

        return count

    def get_stats(self, agent_id: str) -> dict:
        """
        获取统计信息

        Args:
            agent_id: Agent ID

        Returns:
            dict: 统计信息
        """
        queue = self._load()
        agent_notifications = [n for n in queue["notifications"] if n["target_agent"] == agent_id]

        return {
            "total": len(agent_notifications),
            "pending": len([n for n in agent_notifications if n["status"] == "pending"]),
            "read": len([n for n in agent_notifications if n["status"] == "read"])
        }

    def get_all_stats(self) -> dict:
        """获取所有统计信息"""
        queue = self._load()
        notifications = queue["notifications"]

        return {
            "total": len(notifications),
            "pending": len([n for n in notifications if n["status"] == "pending"]),
            "read": len([n for n in notifications if n["status"] == "read"]),
            "queue_id": queue.get("queue_id", "")
        }

    def cleanup(self, max_age_days: int = 7) -> int:
        """
        清理旧通知

        Args:
            max_age_days: 最大保留天数

        Returns:
            int: 清理数量
        """
        queue = self._load()
        cutoff = datetime.utcnow().timestamp() - (max_age_days * 86400)

        original_count = len(queue["notifications"])
        queue["notifications"] = [
            n for n in queue["notifications"]
            if datetime.fromisoformat(n["timestamp"]).timestamp() > cutoff
        ]

        removed = original_count - len(queue["notifications"])
        if removed > 0:
            self._save(queue)
            logger.info(f"已清理{removed}个旧通知")

        return removed

    def rebuild(self) -> bool:
        """
        重建队列文件

        Returns:
            bool: 是否成功
        """
        try:
            queue = self._load()
            self._save({
                "queue_id": queue.get("queue_id", str(uuid.uuid4())),
                "notifications": queue.get("notifications", []),
                "last_updated": datetime.utcnow().isoformat()
            })
            logger.info("队列文件已重建")
            return True
        except Exception as e:
            logger.error(f"重建队列失败: {e}")
            return False
