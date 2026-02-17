from typing import Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class InteractionHandler:
    """TODO交互处理"""
    
    def __init__(self, storage, notification):
        self.storage = storage
        self.notification = notification
    
    def handle_action(self, todo_id: str, action: str) -> Tuple[bool, str]:
        """
        处理用户操作
        Actions: execute, defer, dismiss, view, reassign
        Returns: (success, message)
        """
        action_map = {
            'execute': self.execute,
            'defer': self.defer,
            'dismiss': self.dismiss,
            'reassign': self.reassign,
            'view': self.view
        }
        
        handler = action_map.get(action)
        if not handler:
            return False, f"未知操作: {action}"
        
        return handler(todo_id)
    
    def execute(self, todo_id: str) -> Tuple[bool, str]:
        """立即执行 - 标记为进行中"""
        todo = self.storage.get(todo_id)
        if not todo:
            return False, f"TODO不存在: {todo_id}"
        
        success = self.storage.update(todo_id, {
            'status': 'in_progress',
            'updated_at': datetime.now().isoformat()
        })
        
        if success:
            return True, f"TODO {todo_id} 已开始执行"
        return False, "更新失败"
    
    def defer(self, todo_id: str, delay_minutes: int = 0) -> Tuple[bool, str]:
        """
        留待空闲 - 移入延迟队列
        delay_minutes: 延迟分钟数，0表示用户确认后处理
        """
        todo = self.storage.get(todo_id)
        if not todo:
            return False, f"TODO不存在: {todo_id}"
        
        if delay_minutes > 0:
            deferred_until = (datetime.now() + timedelta(minutes=delay_minutes)).isoformat()
        else:
            deferred_until = None  # 用户确认后处理
        
        updates = {
            'status': 'deferred',
            'deferred_until': deferred_until,
            'updated_at': datetime.now().isoformat()
        }
        
        success = self.storage.update(todo_id, updates)
        
        if success:
            return True, f"TODO {todo_id} 已延迟处理"
        return False, "更新失败"
    
    def dismiss(self, todo_id: str, reason: Optional[str] = None) -> Tuple[bool, str]:
        """不用执行 - 标记为cancelled"""
        todo = self.storage.get(todo_id)
        if not todo:
            return False, f"TODO不存在: {todo_id}"
        
        success = self.storage.update(todo_id, {
            'status': 'cancelled',
            'updated_at': datetime.now().isoformat()
        })
        
        if success:
            msg = f"TODO {todo_id} 已取消"
            if reason:
                msg += f": {reason}"
            else:
                reason = ""
            return True, msg
        return False, "更新失败"
    
    def reassign(self, todo_id: str, new_receiver: str) -> Tuple[bool, str]:
        """转给其他Agent"""
        todo = self.storage.get(todo_id)
        if not todo:
            return False, f"TODO不存在: {todo_id}"
        
        success = self.storage.update(todo_id, {
            'receiver': new_receiver,
            'updated_at': datetime.now().isoformat()
        })
        
        if success:
            return True, f"TODO {todo_id} 已转给 {new_receiver}"
        return False, "更新失败"
    
    def view(self, todo_id: str) -> Tuple[bool, dict]:
        """查看详情"""
        todo = self.storage.get(todo_id)
        if not todo:
            return False, {}
        
        # 标记为已读
        self.storage.mark_read(todo_id)
        
        return True, todo
    
    def complete(self, todo_id: str) -> Tuple[bool, str]:
        """完成TODO"""
        todo = self.storage.get(todo_id)
        if not todo:
            return False, f"TODO不存在: {todo_id}"
        
        success = self.storage.update(todo_id, {
            'status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        })
        
        if success:
            return True, f"TODO {todo_id} 已完成"
        return False, "更新失败"
