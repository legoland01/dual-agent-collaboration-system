"""
TODO ACK确认管理模块

管理TODO的确认状态，支持自动和手动ACK。
"""

import os
import subprocess
import yaml
from typing import Optional, Dict
from datetime import datetime


class ACKConfirm:
    """TODO ACK确认管理"""
    
    def __init__(self, state_file: str = "state/project_state.yaml"):
        """
        Args:
            state_file: 状态文件路径
        """
        self.state_file = state_file
    
    def _load_state(self) -> Dict:
        """加载状态"""
        try:
            with open(self.state_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    
    def _save_state(self, state: Dict):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            yaml.safe_dump(state, f)
    
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
            # 生成commit message
            commit_msg = f"[ACK] {todo_id} acknowledged by {agent_id}"
            
            # 执行commit
            subprocess.run(
                ["git", "commit", "--allow-empty", "-m", commit_msg],
                check=True,
                capture_output=True
            )
            
            # 更新project_state.yaml中的TODO状态
            state = self._load_state()
            todos = state.get("todos", [])
            
            for todo in todos:
                if todo.get("id") == todo_id:
                    todo["acknowledged"] = True
                    todo["acknowledged_by"] = agent_id
                    todo["acknowledged_at"] = datetime.now().isoformat()
                    todo["status"] = "acknowledged"
                    break
            
            state["todos"] = todos
            self._save_state(state)
            
            return True
        except (subprocess.CalledProcessError, IOError):
            return False
    
    def is_acknowledged(self, todo_id: str) -> bool:
        """
        检查是否已确认
        
        Args:
            todo_id: TODO编号
        
        Returns:
            是否已确认
        """
        state = self._load_state()
        todos = state.get("todos", [])
        
        for todo in todos:
            if todo.get("id") == todo_id:
                return todo.get("acknowledged", False)
        
        return False
    
    def get_ack_status(self, todo_id: str) -> Dict:
        """
        获取确认状态
        
        Args:
            todo_id: TODO编号
        
        Returns:
            确认状态详情
        """
        state = self._load_state()
        todos = state.get("todos", [])
        
        for todo in todos:
            if todo.get("id") == todo_id:
                return {
                    "acknowledged": todo.get("acknowledged", False),
                    "acknowledged_by": todo.get("acknowledged_by"),
                    "acknowledged_at": todo.get("acknowledged_at"),
                    "status": todo.get("status", "pending")
                }
        
        return {
            "acknowledged": False,
            "acknowledged_by": None,
            "acknowledged_at": None,
            "status": "not_found"
        }
    
    def auto_ack_on_show(self, todo_id: str, viewer_id: str) -> bool:
        """
        查看TODO详情时自动ACK
        
        Args:
            todo_id: TODO编号
            viewer_id: 查看者ID
        
        Returns:
            是否成功执行ACK
        """
        state = self._load_state()
        todos = state.get("todos", [])
        
        for todo in todos:
            if todo.get("id") == todo_id:
                # 检查todo的receiver是否等于viewer_id
                if todo.get("receiver") == viewer_id and not todo.get("acknowledged", False):
                    return self.acknowledge(todo_id, viewer_id)
                break
        
        return False
