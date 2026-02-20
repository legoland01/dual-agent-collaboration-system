"""
反复预警器模块

监控TODO被拒绝/退回次数，超过阈值后发送预警。
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class RetryWatcher:
    """反复预警器"""
    
    def __init__(self, db_path: str = "state/todos.db", warning_threshold: int = 3):
        self.db_path = db_path
        self.warning_threshold = warning_threshold
        self._ensure_retry_table()
    
    def _ensure_retry_table(self):
        """确保retry_tracking表存在"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS retry_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                todo_id TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0,
                last_retry_at TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(todo_id)
            )
        """)
        conn.commit()
        conn.close()
    
    def record_rejection(self, todo_id: str) -> Dict:
        """记录一次拒绝/退回
        
        Args:
            todo_id: TODO ID
            
        Returns:
            {"retry_count": N, "needs_warning": True/False}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT retry_count FROM retry_tracking WHERE todo_id = ?
        """, (todo_id,))
        
        row = cursor.fetchone()
        
        now = datetime.now().isoformat()
        
        if row:
            new_count = row[0] + 1
            cursor.execute("""
                UPDATE retry_tracking 
                SET retry_count = ?, last_retry_at = ?
                WHERE todo_id = ?
            """, (new_count, now, todo_id))
        else:
            new_count = 1
            cursor.execute("""
                INSERT INTO retry_tracking (todo_id, retry_count, last_retry_at, created_at)
                VALUES (?, ?, ?, ?)
            """, (todo_id, new_count, now, now))
        
        conn.commit()
        conn.close()
        
        return {
            "retry_count": new_count,
            "needs_warning": new_count >= self.warning_threshold
        }
    
    def get_retry_count(self, todo_id: str) -> int:
        """获取重试次数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT retry_count FROM retry_tracking WHERE todo_id = ?
        """, (todo_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else 0
    
    def check_retry_warning(self, todo_id: str) -> Optional[Dict]:
        """检查是否需要预警
        
        Returns:
            预警信息或None
        """
        count = self.get_retry_count(todo_id)
        
        if count >= self.warning_threshold:
            return {
                "warning": True,
                "todo_id": todo_id,
                "retry_count": count,
                "message": f"TODO已被拒绝{count}次，请人工介入确认",
                "threshold": self.warning_threshold
            }
        
        return None
    
    def reset_retry(self, todo_id: str):
        """重置重试计数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM retry_tracking WHERE todo_id = ?", (todo_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_retry_tracking(self) -> List[Dict]:
        """获取所有重试追踪记录"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM retry_tracking ORDER BY last_retry_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


def get_retry_watcher() -> RetryWatcher:
    """获取RetryWatcher单例"""
    return RetryWatcher()
