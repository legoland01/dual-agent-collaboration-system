"""TODO消息队列管理器 - SQLite版本

功能：
- 管理Agent间TODO通知的本地队列
- 支持按发送者分组存储未读TODO
- 支持标记已读/未读状态
- 自动清理过期TODO
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class TodoQueueItem:
    """TODO队列项"""
    id: str
    content: str
    from_agent: str
    to_agent: str
    priority: str
    created_at: str
    read: bool = False
    read_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TodoQueueItem':
        todo_id = data.get('id', '')
        
        from_agent = None
        to_agent = None
        
        if 'to' in str(todo_id):
            match = re.match(r'TODO-(\d+)to(\d+)-(\d+)', str(todo_id))
            if match:
                from_agent = f'agent{match.group(1)}'
                to_agent = f'agent{match.group(2)}'
        
        if not from_agent:
            from_agent = data.get('from_agent') or data.get('sender') or data.get('from')
        if not to_agent:
            to_agent = data.get('to_agent') or data.get('receiver') or data.get('to')
        
        if not from_agent and 'agent_id' in data and data.get('agent_id'):
            from_agent = f"agent{data.get('agent_id')}"
            to_agent = from_agent
        
        if not to_agent:
            to_agent = from_agent or 'agent1'
        
        read = data.get('status', 'pending') != 'pending'
        
        return cls(
            id=todo_id,
            content=data.get('content', ''),
            from_agent=from_agent or 'agent1',
            to_agent=to_agent or 'agent1',
            priority=data.get('priority', 'medium'),
            created_at=data.get('created_at') or datetime.now().isoformat(),
            read=read,
            read_at=data.get('updated_at') if read else None
        )


@dataclass
class TodoQueueStats:
    """队列统计信息"""
    total: int
    unread: int
    by_agent: Dict[str, int]
    by_priority: Dict[str, int]
    last_updated: str


class TodoQueueManager:
    """TODO消息队列管理器 - 使用SQLite"""

    DB_FILENAME = "state/todos.db"

    def __init__(self, db_path: str = None, queue_file: str = None):
        self.db_path = db_path or queue_file or self.DB_FILENAME
        self._storage = None

    def _get_storage(self):
        if self._storage is None:
            from .todo_storage import TodoStorage
            self._storage = TodoStorage(self.db_path)
        return self._storage

    def add(self, item: TodoQueueItem) -> bool:
        """添加TODO到队列"""
        try:
            storage = self._get_storage()
            
            existing = storage.get(item.id)
            if existing:
                logger.debug(f"TODO已存在，跳过: {item.id}")
                return False

            todo_dict = {
                'id': item.id,
                'content': item.content,
                'sender': item.from_agent.replace('agent', ''),
                'receiver': item.to_agent.replace('agent', ''),
                'priority': item.priority,
                'status': 'completed' if item.read else 'pending',
                'created_at': item.created_at,
                'updated_at': item.read_at or datetime.now().isoformat(),
            }
            
            success, _ = storage.add(todo_dict)
            if success:
                logger.info(f"TODO已添加到队列: {item.id}")
            return success

        except Exception as e:
            logger.error(f"添加TODO到队列失败: {e}")
            return False

    def get_unread(self, agent_id: str = None, priority: str = None) -> List[TodoQueueItem]:
        """获取未读TODO"""
        try:
            storage = self._get_storage()
            
            # 去掉agent前缀，因为存储时也去掉了前缀
            receiver = agent_id.replace('agent', '') if agent_id else None
            
            rows = storage.list(receiver=receiver, status='pending')
            
            result = []
            for row in rows:
                item = TodoQueueItem.from_dict(row)
                
                if priority and item.priority != priority:
                    continue
                
                result.append(item)

            priority_order = {"high": 0, "medium": 1, "low": 2}
            result.sort(key=lambda x: (priority_order.get(x.priority, 3), x.created_at or ""))
            return result

        except Exception as e:
            logger.error(f"获取未读TODO失败: {e}")
            return []

    def get_all(self, agent_id: str = None) -> List[TodoQueueItem]:
        """获取所有TODO"""
        try:
            storage = self._get_storage()
            rows = storage.list()
            
            agent_num = agent_id.replace('agent', '') if agent_id else None
            
            result = []
            for row in rows:
                item = TodoQueueItem.from_dict(row)
                if agent_num:
                    receiver = item.to_agent.replace('agent', '')
                    if receiver != agent_num:
                        continue
                result.append(item)

            result.sort(key=lambda x: x.created_at or "")
            return result

        except Exception as e:
            logger.error(f"获取所有TODO失败: {e}")
            return []

    def mark_read(self, todo_id: str, agent_id: str = None) -> bool:
        """标记TODO为已读"""
        try:
            storage = self._get_storage()
            success = storage.update(todo_id, {'status': 'completed'})
            if success:
                logger.info(f"TODO已标记为已读: {todo_id}")
            return success

        except Exception as e:
            logger.error(f"标记TODO已读失败: {e}")
            return False

    def mark_all_read(self, agent_id: str = None) -> int:
        """标记所有TODO为已读"""
        try:
            storage = self._get_storage()
            agent_num = agent_id.replace('agent', '') if agent_id else None
            
            rows = storage.list(receiver=agent_num)
            count = 0
            
            for row in rows:
                if row.get('status') == 'pending':
                    if storage.update(row['id'], {'status': 'completed'}):
                        count += 1
            
            logger.info(f"已标记{count}个TODO为已读")
            return count

        except Exception as e:
            logger.error(f"标记所有TODO已读失败: {e}")
            return 0

    def get_stats(self, agent_id: str = None) -> TodoQueueStats:
        """获取队列统计"""
        try:
            storage = self._get_storage()
            rows = storage.list()
            
            agent_num = agent_id.replace('agent', '') if agent_id else None
            
            if agent_num:
                rows = [r for r in rows if r.get('receiver') == agent_num]

            total = len(rows)
            unread = sum(1 for r in rows if r.get('status') == 'pending')
            
            by_agent = {"agent1": 0, "agent2": 0}
            by_priority = {"high": 0, "medium": 0, "low": 0}
            
            for r in rows:
                receiver = r.get('receiver')
                if receiver in by_agent:
                    by_agent[f"agent{receiver}"] += 1
                
                priority = r.get('priority', 'medium')
                if priority in by_priority:
                    by_priority[priority] += 1

            return TodoQueueStats(
                total=total,
                unread=unread,
                by_agent=by_agent,
                by_priority=by_priority,
                last_updated=datetime.now().isoformat()
            )

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return TodoQueueStats(
                total=0, unread=0,
                by_agent={"agent1": 0, "agent2": 0},
                by_priority={"high": 0, "medium": 0, "low": 0},
                last_updated=""
            )

    def cleanup(self, days: int = None) -> int:
        """清理过期的已读TODO"""
        return 0

    def delete(self, todo_id: str) -> bool:
        """删除TODO"""
        try:
            storage = self._get_storage()
            success = storage.delete(todo_id)
            if success:
                logger.info(f"TODO已删除: {todo_id}")
            return success

        except Exception as e:
            logger.error(f"删除TODO失败: {e}")
            return False

    def clear(self, agent_id: str = None) -> int:
        """清空队列"""
        try:
            storage = self._get_storage()
            rows = storage.list()
            
            agent_num = agent_id.replace('agent', '') if agent_id else None
            count = 0
            
            for row in rows:
                if agent_num and row.get('receiver') != agent_num:
                    continue
                if storage.delete(row['id']):
                    count += 1
            
            logger.info(f"已清空{count}个TODO")
            return count

        except Exception as e:
            logger.error(f"清空队列失败: {e}")
            return 0
