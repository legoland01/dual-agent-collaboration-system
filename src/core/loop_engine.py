"""
循环引擎模块

处理循环路径：补充后再次评审、修正后再次评审等场景。
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional


class LoopEngine:
    """循环引擎"""
    
    def __init__(self, db_path: str = "state/todos.db", max_loops: int = 10):
        self.db_path = db_path
        self.max_loops = max_loops
        self._ensure_loop_table()
    
    def _ensure_loop_table(self):
        """确保loop_tracking表存在"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loop_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                loop_type TEXT NOT NULL,
                loop_count INTEGER DEFAULT 0,
                last_loop_at TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(entity_type, entity_id, loop_type)
            )
        """)
        conn.commit()
        conn.close()
    
    def record_loop(self, entity_type: str, entity_id: str, loop_type: str = "review") -> Dict:
        """记录一次循环
        
        Args:
            entity_type: 实体类型 (requirement, design, bug等)
            entity_id: 实体ID
            loop_type: 循环类型 (review, fix等)
            
        Returns:
            {"loop_count": N, "is_max": True/False}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT loop_count FROM loop_tracking
            WHERE entity_type = ? AND entity_id = ? AND loop_type = ?
        """, (entity_type, entity_id, loop_type))
        
        row = cursor.fetchone()
        
        now = datetime.now().isoformat()
        
        if row:
            new_count = row[0] + 1
            cursor.execute("""
                UPDATE loop_tracking 
                SET loop_count = ?, last_loop_at = ?
                WHERE entity_type = ? AND entity_id = ? AND loop_type = ?
            """, (new_count, now, entity_type, entity_id, loop_type))
        else:
            new_count = 1
            cursor.execute("""
                INSERT INTO loop_tracking (entity_type, entity_id, loop_count, loop_type, last_loop_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (entity_type, entity_id, new_count, loop_type, now, now))
        
        conn.commit()
        conn.close()
        
        return {
            "loop_count": new_count,
            "is_max": new_count >= self.max_loops,
            "needs_warning": new_count >= 3
        }
    
    def get_loop_count(self, entity_type: str, entity_id: str, loop_type: str = "review") -> int:
        """获取循环次数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT loop_count FROM loop_tracking
            WHERE entity_type = ? AND entity_id = ? AND loop_type = ?
        """, (entity_type, entity_id, loop_type))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else 0
    
    def reset_loop(self, entity_type: str, entity_id: str, loop_type: str = "review"):
        """重置循环计数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM loop_tracking
            WHERE entity_type = ? AND entity_id = ? AND loop_type = ?
        """, (entity_type, entity_id, loop_type))
        
        conn.commit()
        conn.close()
    
    def check_loop_warning(self, entity_type: str, entity_id: str, loop_type: str = "review") -> Optional[Dict]:
        """检查是否需要预警
        
        Returns:
            预警信息或None
        """
        count = self.get_loop_count(entity_type, entity_id, loop_type)
        
        if count >= 3:
            return {
                "warning": True,
                "loop_count": count,
                "message": f"循环次数已达{count}次，请人工介入确认",
                "threshold": 3
            }
        
        if count >= self.max_loops:
            return {
                "warning": True,
                "loop_count": count,
                "message": f"已达到最大循环次数({self.max_loops})，请人工处理",
                "threshold": self.max_loops,
                "is_max": True
            }
        
        return None
    
    def get_all_loops(self) -> List[Dict]:
        """获取所有循环追踪记录"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM loop_tracking ORDER BY last_loop_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


def get_loop_engine() -> LoopEngine:
    """获取LoopEngine单例"""
    return LoopEngine()
