"""
TODO ACK确认管理模块

管理TODO的确认状态，支持自动和手动ACK。
"""

from typing import Optional
from datetime import datetime


class ACKConfirm:
    """TODO ACK确认管理"""
    
    def __init__(self, db_path: str = "state/todos.db", state_file: str = None):
        """
        Args:
            db_path: SQLite数据库路径
            state_file: 状态文件路径（兼容参数）
        """
        self.db_path = db_path or state_file or "state/todos.db"
    
    def acknowledge(self, todo_id: str, agent_id: str) -> bool:
        """
        确认TODO
        
        Args:
            todo_id: TODO编号
            agent_id: 确认者ID
        
        Returns:
            是否成功
        """
        try:
            from .todo_storage import TodoStorage
            storage = TodoStorage(self.db_path)
            
            success = storage.update(todo_id, {
                'acknowledged': True,
                'acknowledged_by': agent_id,
                'acknowledged_at': datetime.now().isoformat()
            })
            
            return success
            
        except Exception as e:
            print(f"ACK确认失败: {e}")
            return False

    def is_acknowledged(self, todo_id: str) -> bool:
        """
        检查TODO是否已确认
        
        Args:
            todo_id: TODO编号
        
        Returns:
            是否已确认
        """
        try:
            from .todo_storage import TodoStorage
            storage = TodoStorage(self.db_path)
            
            todo = storage.get(todo_id)
            if not todo:
                return False
            
            return todo.get('acknowledged', False)
            
        except Exception:
            return False
