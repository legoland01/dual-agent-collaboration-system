"""
超时预警器模块

监控TODO处理时间，超时后发送预警通知。
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class TimeoutWatcher:
    """超时预警器"""
    
    def __init__(self, db_path: str = "state/todos.db", default_timeout_hours: int = 24):
        self.db_path = db_path
        self.default_timeout_hours = default_timeout_hours
        self._ensure_timeout_config_table()
    
    def _ensure_timeout_config_table(self):
        """确保超时配置表存在"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeout_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                priority TEXT,
                timeout_hours INTEGER NOT NULL,
                enabled INTEGER DEFAULT 1,
                UNIQUE(entity_type, priority)
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM timeout_config")
        if cursor.fetchone()[0] == 0:
            default_configs = [
                {"entity_type": "todo", "priority": "high", "timeout_hours": 4},
                {"entity_type": "todo", "priority": "medium", "timeout_hours": 24},
                {"entity_type": "todo", "priority": "low", "timeout_hours": 72},
            ]
            for config in default_configs:
                cursor.execute("""
                    INSERT INTO timeout_config (entity_type, priority, timeout_hours)
                    VALUES (?, ?, ?)
                """, (config["entity_type"], config["priority"], config["timeout_hours"]))
        
        conn.commit()
        conn.close()
    
    def check_timeouts(self) -> List[Dict]:
        """检查超时TODO
        
        Returns:
            超时TODO列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.*, tc.timeout_hours 
            FROM todos t
            LEFT JOIN timeout_config tc ON tc.entity_type = 'todo' AND (tc.priority = t.priority OR tc.priority IS NULL)
            WHERE t.status = 'pending'
        """)
        
        todos = cursor.fetchall()
        conn.close()
        
        now = datetime.now()
        timeout_todos = []
        
        for todo in todos:
            created_at = datetime.fromisoformat(todo["created_at"])
            timeout_hours = todo["timeout_hours"] or self.default_timeout_hours
            timeout_time = created_at + timedelta(hours=timeout_hours)
            
            if now >= timeout_time:
                timeout_todos.append({
                    "todo_id": todo["id"],
                    "content": todo["content"],
                    "priority": todo["priority"],
                    "created_at": todo["created_at"],
                    "timeout_hours": timeout_hours,
                    "overdue_hours": (now - timeout_time).total_seconds() / 3600
                })
        
        return timeout_todos
    
    def get_timeout_config(self, entity_type: str, priority: Optional[str] = None) -> Optional[int]:
        """获取超时配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if priority:
            cursor.execute("""
                SELECT timeout_hours FROM timeout_config 
                WHERE entity_type = ? AND priority = ? AND enabled = 1
            """, (entity_type, priority))
        else:
            cursor.execute("""
                SELECT timeout_hours FROM timeout_config 
                WHERE entity_type = ? AND priority IS NULL AND enabled = 1
            """, (entity_type,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def set_timeout_config(self, entity_type: str, timeout_hours: int, priority: Optional[str] = None):
        """设置超时配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO timeout_config (entity_type, priority, timeout_hours, enabled)
            VALUES (?, ?, ?, 1)
        """, (entity_type, priority, timeout_hours))
        
        conn.commit()
        conn.close()
    
    def notify_timeout(self, todo_id: str) -> Dict:
        """发送超时预警
        
        Returns:
            通知结果
        """
        from ..core.state_notifier import StateNotifier
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        todo = cursor.fetchone()
        conn.close()
        
        if not todo:
            return {"success": False, "message": "TODO not found"}
        
        notifier = StateNotifier()
        result = notifier.notify_todo_timeout(todo_id, todo["content"])
        
        return result


def get_timeout_watcher() -> TimeoutWatcher:
    """获取TimeoutWatcher单例"""
    return TimeoutWatcher()
