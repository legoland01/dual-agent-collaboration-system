"""
自动创建TODO模块

根据事件自动创建关联TODO。
"""

import sqlite3
import json
from typing import Dict, List, Optional


class AutoTodoCreator:
    """自动创建TODO"""
    
    def __init__(self, db_path: str = "state/todos.db"):
        self.db_path = db_path
        self._ensure_auto_create_rules_table()
    
    def _ensure_auto_create_rules_table(self):
        """确保auto_create_rules表存在"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auto_create_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                trigger_event TEXT NOT NULL,
                template_content TEXT NOT NULL,
                priority TEXT DEFAULT 'medium',
                receiver TEXT,
                enabled INTEGER DEFAULT 1
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM auto_create_rules")
        if cursor.fetchone()[0] == 0:
            default_rules = [
                {
                    "name": "评审通过后创建签署TODO",
                    "trigger_event": "todo_status_changed:approved",
                    "template_content": "签署 {entity_id}",
                    "priority": "high"
                },
                {
                    "name": "Bug修复完成后创建验收TODO",
                    "trigger_event": "todo_status_changed:completed+bug",
                    "template_content": "验收Bug: {entity_id}",
                    "priority": "high"
                },
                {
                    "name": "测试完成后创建验收TODO",
                    "trigger_event": "todo_status_changed:completed+test",
                    "template_content": "验收: {entity_id}",
                    "priority": "medium"
                }
            ]
            
            for rule in default_rules:
                cursor.execute("""
                    INSERT INTO auto_create_rules (name, trigger_event, template_content, priority)
                    VALUES (?, ?, ?, ?)
                """, (rule["name"], rule["trigger_event"], rule["template_content"], rule["priority"]))
        
        conn.commit()
        conn.close()
    
    def create_from_event(self, event: Dict) -> List[Dict]:
        """根据事件自动创建TODO
        
        Args:
            event: 事件字典
            
        Returns:
            创建的TODO列表
        """
        created_todos = []
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM auto_create_rules WHERE enabled = 1")
        rules = cursor.fetchall()
        conn.close()
        
        for rule in rules:
            if self._match_trigger(rule["trigger_event"], event):
                todo = self._create_todo_from_rule(rule, event)
                if todo:
                    created_todos.append(todo)
        
        return created_todos
    
    def _match_trigger(self, trigger_event: str, event: Dict) -> bool:
        """检查触发事件是否匹配"""
        parts = trigger_event.split(":")
        event_type = parts[0]
        
        if event.get("type") != event_type:
            return False
        
        if len(parts) > 1:
            condition = parts[1]
            
            if "+" in condition:
                conditions = condition.split("+")
                for c in conditions:
                    if c not in event.get("entity_id", "").lower():
                        return False
            else:
                if condition not in event.get("new_status", ""):
                    return False
        
        return True
    
    def _create_todo_from_rule(self, rule, event: Dict) -> Optional[Dict]:
        """根据规则创建TODO"""
        from ..core.todo_sync_manager import TodoSyncManager
        
        content = rule["template_content"].format(
            entity_id=event.get("entity_id", ""),
            old_status=event.get("old_status", ""),
            new_status=event.get("new_status", "")
        )
        
        sync_manager = TodoSyncManager()
        todo = sync_manager.add_todo(
            content=content,
            priority=rule["priority"]
        )
        
        if todo:
            return {
                "todo_id": todo.id,
                "content": todo.content,
                "priority": todo.priority
            }
        
        return None
    
    def add_rule(self, name: str, trigger_event: str, template_content: str, 
                 priority: str = "medium", receiver: Optional[str] = None) -> int:
        """添加自动创建规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO auto_create_rules (name, trigger_event, template_content, priority, receiver)
            VALUES (?, ?, ?, ?, ?)
        """, (name, trigger_event, template_content, priority, receiver))
        
        rule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return rule_id
    
    def list_rules(self) -> List[Dict]:
        """列出所有规则"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM auto_create_rules")
        rules = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return rules
    
    def enable_rule(self, rule_id: int, enabled: bool = True):
        """启用/禁用规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE auto_create_rules SET enabled = ? WHERE id = ?", (1 if enabled else 0, rule_id))
        conn.commit()
        conn.close()


def get_auto_todo_creator() -> AutoTodoCreator:
    """获取AutoTodoCreator单例"""
    return AutoTodoCreator()
