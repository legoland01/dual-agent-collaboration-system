import sqlite3
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AgentStatusMonitor:
    """Agent状态感知"""
    
    def __init__(self, db_path: str = "state/todos.db"):
        self.db_path = db_path
        self._ensure_db()
    
    def _ensure_db(self):
        """确保数据库存在"""
        if not Path(self.db_path).exists():
            # 创建空数据库
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _ensure_table(self):
        """确保表存在"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_status (
                agent_id TEXT PRIMARY KEY,
                status TEXT DEFAULT 'offline',
                last_seen_at TIMESTAMP,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def detect_online(self, agent_id: str) -> bool:
        """检测Agent上线"""
        self._ensure_table()
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO agent_status (agent_id, status, last_seen_at, registered_at)
            VALUES (?, 'online', ?, COALESCE((SELECT registered_at FROM agent_status WHERE agent_id = ?), ?))
        """, (agent_id, now, agent_id, now))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Agent {agent_id} 上线")
        return True
    
    def detect_offline(self, agent_id: str) -> bool:
        """检测Agent下线"""
        self._ensure_table()
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE agent_status 
            SET status = 'offline', last_seen_at = ?
            WHERE agent_id = ?
        """, (now, agent_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Agent {agent_id} 下线")
        return True
    
    def get_last_seen(self, agent_id: str) -> Optional[datetime]:
        """获取最后在线时间"""
        self._ensure_table()
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT last_seen_at FROM agent_status WHERE agent_id = ?",
            (agent_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row and row['last_seen_at']:
            return datetime.fromisoformat(row['last_seen_at'])
        return None
    
    def is_online(self, agent_id: str) -> bool:
        """检查Agent是否在线"""
        self._ensure_table()
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT status FROM agent_status WHERE agent_id = ?",
            (agent_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        return row and row['status'] == 'online'
    
    def list_online_agents(self) -> List[str]:
        """列出所有在线Agent"""
        self._ensure_table()
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT agent_id FROM agent_status WHERE status = 'online'"
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [row['agent_id'] for row in rows]
    
    def list_all_agents(self) -> List[dict]:
        """列出所有Agent"""
        self._ensure_table()
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM agent_status ORDER BY last_seen_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
