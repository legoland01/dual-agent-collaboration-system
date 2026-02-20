"""
状态变更监听器模块

负责监听并记录状态变更事件，为自动流程触发提供事件源。
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class StateChangeEvent:
    """状态变更事件"""
    id: Optional[int] = None
    type: str = ""
    entity_type: str = ""
    entity_id: str = ""
    old_status: str = ""
    new_status: str = ""
    timestamp: str = ""
    data: str = ""


class StateListener:
    """状态变更监听器"""
    
    def __init__(self, db_path: str = "state/todos.db"):
        self.db_path = db_path
        self._ensure_events_table()
    
    def _ensure_events_table(self):
        """确保events表存在"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                old_status TEXT,
                new_status TEXT,
                timestamp TEXT NOT NULL,
                data TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def record_todo_status_change(self, todo_id: str, old_status: str, new_status: str):
        """记录TODO状态变更"""
        event = {
            "type": "todo_status_changed",
            "entity_type": "todo",
            "entity_id": todo_id,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": datetime.now().isoformat()
        }
        self._add_event(event)
    
    def record_phase_advance(self, old_phase: str, new_phase: str, project_id: str = "default"):
        """记录阶段推进"""
        event = {
            "type": "phase_advanced",
            "entity_type": "project",
            "entity_id": project_id,
            "old_status": old_phase,
            "new_status": new_phase,
            "timestamp": datetime.now().isoformat()
        }
        self._add_event(event)
    
    def record_signoff(self, entity_type: str, entity_id: str, signer: str):
        """记录签署操作"""
        event = {
            "type": "signoff",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "old_status": "",
            "new_status": "signed",
            "timestamp": datetime.now().isoformat(),
            "data": json.dumps({"signer": signer})
        }
        self._add_event(event)
    
    def _add_event(self, event: Dict):
        """添加事件到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO events (type, entity_type, entity_id, old_status, new_status, timestamp, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event.get("type", ""),
            event.get("entity_type", ""),
            event.get("entity_id", ""),
            event.get("old_status", ""),
            event.get("new_status", ""),
            event.get("timestamp", datetime.now().isoformat()),
            event.get("data", "")
        ))
        conn.commit()
        conn.close()
    
    def get_changes(self, since: Optional[str] = None, event_type: Optional[str] = None) -> List[Dict]:
        """查询变更记录（供PM-Agent等外部系统调用）
        
        Args:
            since: ISO格式时间戳，如 "2026-02-19T10:00:00Z"
            event_type: 事件类型过滤
            
        Returns:
            变更列表 [{"type": "todo", "id": "TODO-1", "old_status": "...", "new_status": "...", "timestamp": "..."}]
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        
        if since:
            query += " AND timestamp > ?"
            params.append(since)
        
        if event_type:
            query += " AND type = ?"
            params.append(event_type)
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return self._format_changes(rows)
    
    def _format_changes(self, rows) -> List[Dict]:
        """格式化变更数据"""
        changes = []
        for row in rows:
            change = {
                "type": row["type"],
                "entity_type": row["entity_type"],
                "entity_id": row["entity_id"],
                "old_status": row["old_status"],
                "new_status": row["new_status"],
                "timestamp": row["timestamp"]
            }
            if row["data"]:
                change["data"] = row["data"]
            changes.append(change)
        return changes
    
    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        """获取最近的事件"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM events 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return self._format_changes(rows)


def get_state_listener() -> StateListener:
    """获取StateListener单例"""
    return StateListener()
