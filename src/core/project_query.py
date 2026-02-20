"""
跨项目信息查询模块

支持内部子系统查询其他项目状态/TODO。
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .file_abstractions import FileReader, DirectoryScanner, RealFileReader, RealDirectoryScanner


class ProjectQuery:
    """跨项目查询"""
    
    def __init__(self, base_path: str = ".", 
                 file_reader: Optional[FileReader] = None,
                 dir_scanner: Optional[DirectoryScanner] = None):
        self.base_path = Path(base_path)
        self.file_reader = file_reader or RealFileReader()
        self.dir_scanner = dir_scanner or RealDirectoryScanner()
    
    def get_projects(self) -> List[Dict]:
        """获取所有项目列表"""
        projects = []
        
        base = Path(self.base_path)
        if not base.exists():
            return []
        
        project_dirs = [
            d for d in self.dir_scanner.iterdir(base) 
            if d.is_dir() and (d / "state").exists()
        ]
        
        for project_dir in project_dirs:
            state_dir = project_dir / "state"
            todos_db = state_dir / "todos.db"
            
            if todos_db.exists():
                project_info = {
                    "name": project_dir.name,
                    "path": str(project_dir),
                    "has_todos_db": True
                }
                
                conn = sqlite3.connect(str(todos_db))
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM todos")
                todo_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM todos WHERE status = 'pending'")
                pending_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM todos WHERE status = 'completed'")
                completed_count = cursor.fetchone()[0]
                
                conn.close()
                
                project_info["todo_count"] = todo_count
                project_info["pending_count"] = pending_count
                project_info["completed_count"] = completed_count
                
                projects.append(project_info)
        
        return projects
    
    def get_project_status(self, project_name: str) -> Dict:
        """获取项目状态"""
        project_path = self.base_path / project_name
        todos_db = project_path / "state" / "todos.db"
        
        if not todos_db.exists():
            return {"error": f"Project {project_name} not found"}
        
        conn = sqlite3.connect(str(todos_db))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM todos")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM todos WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM todos WHERE status = 'in_progress'")
        in_progress = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM todos WHERE status = 'completed'")
        completed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM todos WHERE status = 'cancelled'")
        cancelled = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM todos WHERE status = 'deferred'")
        deferred = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "project": project_name,
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled,
            "deferred": deferred,
            "completion_rate": round(completed / total * 100, 2) if total > 0 else 0
        }
    
    def get_project_todos(self, project_name: str, status: Optional[str] = None) -> List[Dict]:
        """获取项目TODO列表"""
        project_path = self.base_path / project_name
        todos_db = project_path / "state" / "todos.db"
        
        if not todos_db.exists():
            return [{"error": f"Project {project_name} not found"}]
        
        conn = sqlite3.connect(str(todos_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT id, content, status, priority, sender, receiver, created_at
                FROM todos WHERE status = ?
                ORDER BY created_at DESC
            """, (status,))
        else:
            cursor.execute("""
                SELECT id, content, status, priority, sender, receiver, created_at
                FROM todos ORDER BY created_at DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_changes(self, project_name: str, since: Optional[str] = None) -> Dict:
        """查询项目变更（用于PM-Agent轮询）"""
        project_path = self.base_path / project_name
        todos_db = project_path / "state" / "todos.db"
        
        if not todos_db.exists():
            return {"error": f"Project {project_name} not found"}
        
        conn = sqlite3.connect(str(todos_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM events"
        params = []
        
        if since:
            query += " WHERE timestamp > ?"
            params.append(since)
        
        query += " ORDER BY timestamp DESC LIMIT 100"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        changes = []
        for row in rows:
            changes.append({
                "type": row["type"],
                "entity_type": row["entity_type"],
                "entity_id": row["entity_id"],
                "old_status": row["old_status"],
                "new_status": row["new_status"],
                "timestamp": row["timestamp"]
            })
        
        return {
            "project": project_name,
            "changes": changes,
            "count": len(changes)
        }
    
    def get_progress(self, project_name: str) -> Dict:
        """查询项目进度（用于Dashboard）"""
        project_status = self.get_project_status(project_name)
        
        if "error" in project_status:
            return project_status
        
        total = project_status["total"]
        completed = project_status["completed"]
        
        return {
            "project": project_name,
            "total": total,
            "completed": completed,
            "in_progress": project_status["in_progress"],
            "pending": project_status["pending"],
            "progress_percentage": round(completed / total * 100, 2) if total > 0 else 0,
            "status_breakdown": {
                "pending": project_status["pending"],
                "in_progress": project_status["in_progress"],
                "completed": completed,
                "cancelled": project_status["cancelled"],
                "deferred": project_status["deferred"]
            }
        }


def get_project_query() -> ProjectQuery:
    """获取ProjectQuery单例"""
    return ProjectQuery()
