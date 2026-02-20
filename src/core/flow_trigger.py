"""
流程触发器模块

根据配置规则，在状态变更后自动触发下一流程。
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass


@dataclass
class TriggerRule:
    """触发规则"""
    id: Optional[int] = None
    name: str = ""
    event_type: str = ""
    from_status: str = ""
    to_status: str = ""
    action_type: str = ""
    action_config: str = ""
    enabled: bool = True


class FlowTrigger:
    """流程触发器"""
    
    def __init__(self, db_path: str = "state/todos.db"):
        self.db_path = db_path
        self._ensure_trigger_rules_table()
        self._init_default_rules()
    
    def _ensure_trigger_rules_table(self):
        """确保trigger_rules表存在"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trigger_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                from_status TEXT,
                to_status TEXT,
                action_type TEXT NOT NULL,
                action_config TEXT,
                enabled INTEGER DEFAULT 1
            )
        """)
        conn.commit()
        conn.close()
    
    def _init_default_rules(self):
        """初始化默认触发规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM trigger_rules")
        if cursor.fetchone()[0] == 0:
            default_rules = [
                {
                    "name": "评审通过后自动创建签署TODO",
                    "event_type": "todo_status_changed",
                    "from_status": "pending",
                    "to_status": "approved",
                    "action_type": "create_todo",
                    "action_config": json.dumps({
                        "content": "签署 {entity_id}",
                        "priority": "high"
                    })
                },
                {
                    "name": "签署完成后自动推进阶段",
                    "event_type": "signoff",
                    "from_status": "",
                    "to_status": "signed",
                    "action_type": "advance_phase",
                    "action_config": json.dumps({})
                },
                {
                    "name": "Bug修复完成后自动创建验收TODO",
                    "event_type": "todo_status_changed",
                    "from_status": "in_progress",
                    "to_status": "completed",
                    "action_type": "create_todo",
                    "action_config": json.dumps({
                        "content": "验收Bug: {entity_id}",
                        "priority": "high"
                    })
                },
                {
                    "name": "测试通过后自动进入下一阶段",
                    "event_type": "todo_status_changed",
                    "from_status": "pending",
                    "to_status": "completed",
                    "action_type": "advance_phase",
                    "action_config": json.dumps({})
                }
            ]
            
            for rule in default_rules:
                cursor.execute("""
                    INSERT INTO trigger_rules (name, event_type, from_status, to_status, action_type, action_config)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    rule["name"],
                    rule["event_type"],
                    rule["from_status"],
                    rule["to_status"],
                    rule["action_type"],
                    rule["action_config"]
                ))
            
            conn.commit()
        
        conn.close()
    
    def handle_event(self, event: Dict) -> List[Dict]:
        """处理事件，触发相应规则
        
        Args:
            event: 事件字典
            
        Returns:
            触发结果列表
        """
        results = []
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM trigger_rules 
            WHERE enabled = 1 
            AND event_type = ?
        """, (event.get("type", ""),))
        
        rules = cursor.fetchall()
        conn.close()
        
        for rule in rules:
            if self._match_rule(rule, event):
                result = self._execute_action(rule, event)
                results.append(result)
        
        return results
    
    def _match_rule(self, rule, event: Dict) -> bool:
        """检查规则是否匹配"""
        if rule["from_status"] and rule["from_status"] != event.get("old_status", ""):
            return False
        if rule["to_status"] and rule["to_status"] != event.get("new_status", ""):
            return False
        return True
    
    def _execute_action(self, rule, event: Dict) -> Dict:
        """执行触发动作"""
        action_type = rule["action_type"]
        action_config = json.loads(rule["action_config"]) if rule["action_config"] else {}
        
        if action_type == "create_todo":
            return self._action_create_todo(action_config, event)
        elif action_type == "advance_phase":
            return self._action_advance_phase(action_config, event)
        else:
            return {"success": False, "message": f"Unknown action type: {action_type}"}
    
    def _action_create_todo(self, config: Dict, event: Dict) -> Dict:
        """创建TODO动作"""
        from ..core.todo_sync_manager import TodoSyncManager
        
        content = config.get("content", "").format(
            entity_id=event.get("entity_id", ""),
            old_status=event.get("old_status", ""),
            new_status=event.get("new_status", "")
        )
        priority = config.get("priority", "medium")
        
        sync_manager = TodoSyncManager()
        todo = sync_manager.add_todo(
            content=content,
            priority=priority
        )
        
        return {
            "success": True,
            "action": "create_todo",
            "todo_id": todo.id if todo else None
        }
    
    def _action_advance_phase(self, config: Dict, event: Dict) -> Dict:
        """推进阶段动作"""
        from ..core.state_manager import StateManager
        
        state_manager = StateManager()
        
        current_phase = state_manager.get_current_phase()
        next_phase = self._get_next_phase(current_phase)
        
        if next_phase:
            state_manager.advance_phase(next_phase)
            return {
                "success": True,
                "action": "advance_phase",
                "from_phase": current_phase,
                "to_phase": next_phase
            }
        
        return {
            "success": False,
            "message": "No next phase available"
        }
    
    def _get_next_phase(self, current_phase: str) -> Optional[str]:
        """获取下一阶段"""
        phase_map = {
            "requirements": "design",
            "design": "development",
            "development": "testing",
            "testing": "acceptance",
            "acceptance": "released"
        }
        return phase_map.get(current_phase)
    
    def add_rule(self, rule: TriggerRule) -> int:
        """添加触发规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO trigger_rules (name, event_type, from_status, to_status, action_type, action_config)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            rule.name,
            rule.event_type,
            rule.from_status,
            rule.to_status,
            rule.action_type,
            rule.action_config
        ))
        
        rule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return rule_id
    
    def list_rules(self) -> List[Dict]:
        """列出所有触发规则"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM trigger_rules")
        rules = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return rules
    
    def enable_rule(self, rule_id: int, enabled: bool = True):
        """启用/禁用规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE trigger_rules SET enabled = ? WHERE id = ?", (1 if enabled else 0, rule_id))
        conn.commit()
        conn.close()


def get_flow_trigger() -> FlowTrigger:
    """获取FlowTrigger单例"""
    return FlowTrigger()
