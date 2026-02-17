import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """数据库错误"""
    pass


class TodoStorage:
    """SQLite存储层"""
    
    def __init__(self, db_path: str = "state/todos.db"):
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_db()
    
    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """初始化数据库和表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 创建todos表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled', 'deferred')),
                priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
                sender TEXT,
                receiver TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                completed_at TIMESTAMP,
                deferred_until TIMESTAMP,
                is_read INTEGER DEFAULT 0,
                metadata TEXT
            )
        """)
        
        # 创建agent_status表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_status (
                agent_id TEXT PRIMARY KEY,
                status TEXT DEFAULT 'offline' CHECK(status IN ('online', 'offline')),
                last_seen_at TIMESTAMP,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建notifications表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                todo_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_action TEXT,
                user_action_at TIMESTAMP,
                response_time_seconds INTEGER
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_receiver ON todos(receiver)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_status ON todos(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_sender ON todos(sender)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_created_at ON todos(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_deferred_until ON todos(deferred_until)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_todo_id ON notifications(todo_id)")
        
        conn.commit()
        conn.close()
        logger.info(f"数据库初始化完成: {self.db_path}")
    
    def add(self, todo: dict) -> tuple[bool, str]:
        """
        添加TODO
        Args:
            todo: TODO字典
        Returns:
            (success, todo_id/error_message)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO todos (
                    id, content, status, priority, sender, receiver, source,
                    created_at, updated_at, is_read, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                todo.get('id'),
                todo.get('content'),
                todo.get('status', 'pending'),
                todo.get('priority', 'medium'),
                todo.get('sender'),
                todo.get('receiver'),
                todo.get('source', 'MANUAL'),
                todo.get('created_at', datetime.now().isoformat()),
                todo.get('updated_at', datetime.now().isoformat()),
                todo.get('is_read', 0),
                json.dumps(todo.get('metadata', {}))
            ))
            conn.commit()
            todo_id = todo.get('id') or 'unknown'
            return True, todo_id
        except sqlite3.IntegrityError:
            todo_id = todo.get('id') or 'unknown'
            return False, f"TODO {todo_id} 已存在"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()
    
    def get(self, todo_id: str) -> Optional[dict]:
        """获取单个TODO"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def list(
        self,
        receiver: Optional[str] = None,
        status: Optional[str] = None,
        unread_only: bool = False
    ) -> List[dict]:
        """列出TODO"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM todos WHERE 1=1"
        params = []
        
        if receiver:
            query += " AND receiver = ?"
            params.append(receiver)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if unread_only:
            query += " AND is_read = 0"
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update(self, todo_id: str, updates: dict) -> bool:
        """更新TODO"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        set_clauses = []
        params = []
        
        for key, value in updates.items():
            if key == 'metadata':
                set_clauses.append("metadata = ?")
                params.append(json.dumps(value))
            else:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            return False
        
        set_clauses.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(todo_id)
        
        query = f"UPDATE todos SET {', '.join(set_clauses)} WHERE id = ?"
        
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            logger.error(f"更新TODO失败: {e}")
            return False
        finally:
            conn.close()
    
    def delete(self, todo_id: str) -> bool:
        """删除TODO"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def mark_read(self, todo_id: str) -> bool:
        """标记为已读"""
        return self.update(todo_id, {'is_read': 1})
    
    def mark_unread(self, todo_id: str) -> bool:
        """标记为未读"""
        return self.update(todo_id, {'is_read': 0})
    
    def count_unread(self, receiver: str) -> int:
        """统计未读TODO数量"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM todos WHERE receiver = ? AND is_read = 0",
            (receiver,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_next_id(self, receiver: str) -> int:
        """获取下一个TODO编号"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 查找该receiver的最大编号
        pattern = f"TODO-{receiver}to%-"
        cursor.execute("""
            SELECT id FROM todos 
            WHERE id LIKE ? 
            ORDER BY id DESC LIMIT 1
        """, (pattern,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # 解析编号
            last_id = row[0]
            try:
                num = int(last_id.split('-')[-1])
                return num + 1
            except:
                return 1
        return 1
    
    def close(self):
        """关闭连接（实际不需要，SQLite自动管理）"""
        pass
