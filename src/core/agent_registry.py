"""
Agent注册表管理模块

管理Agent信息，支持注册、注销、列表查询。
"""

import os
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class AgentRegistry:
    """Agent注册表管理"""
    
    VALID_ROLES = [
        "PRODUCT_MANAGER",
        "DEVELOPMENT_LEAD",
        "FRONTEND_DEV",
        "BACKEND_DEV",
        "QA_ENGINEER"
    ]
    
    def __init__(self, state_file: str = "state/project_state.yaml"):
        """
        Args:
            state_file: 状态文件路径
        """
        self.state_file = state_file
        self._ensure_state_file()
    
    def _get_identity_file(self) -> Path:
        """获取agent identity文件路径"""
        state_dir = Path(self.state_file).parent
        return state_dir / "agent.identity"
    
    def set_agent_identity(self, agent_id: str, lock: bool = True) -> bool:
        """
        设置当前Agent身份并锁定
        
        Args:
            agent_id: Agent ID
            lock: 是否锁定身份（锁定后无法更改）
        
        Returns:
            是否成功
        """
        identity_file = self._get_identity_file()
        identity_file.parent.mkdir(parents=True, exist_ok=True)
        
        content = {
            "agent_id": agent_id,
            "locked": lock,
            "set_at": datetime.now().isoformat()
        }
        
        with open(identity_file, 'w') as f:
            yaml.safe_dump(content, f)
        
        return True
    
    def unlock_agent_identity(self) -> bool:
        """解锁Agent身份"""
        identity_file = self._get_identity_file()
        if identity_file.exists():
            with open(identity_file, 'r') as f:
                content = yaml.safe_load(f) or {}
            content["locked"] = False
            with open(identity_file, 'w') as f:
                yaml.safe_dump(content, f)
        return True
    
    def is_identity_locked(self) -> bool:
        """检查身份是否锁定"""
        identity_file = self._get_identity_file()
        if identity_file.exists():
            with open(identity_file, 'r') as f:
                content = yaml.safe_load(f) or {}
            return content.get("locked", False)
        return False
    
    def _ensure_state_file(self):
        """确保状态文件存在"""
        if not os.path.exists(self.state_file):
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            self._save_state({"agents": {}})
    
    def _load_state(self) -> Dict:
        """加载状态"""
        try:
            with open(self.state_file, 'r') as f:
                return yaml.safe_load(f) or {"agents": {}}
        except Exception:
            return {"agents": {}}
    
    def _save_state(self, state: Dict):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            yaml.safe_dump(state, f)
    
    def get_current_agent_id(self) -> Optional[str]:
        """
        获取当前Agent ID
        
        优先级: 
        1. agent.identity文件 (锁定状态)
        2. 环境变量 OC_AGENT_ID
        3. project_state.yaml中的current_agent
        4. Git config
        
        Returns:
            Agent ID或None
        """
        # 1. agent.identity文件 (最优先)
        identity_file = self._get_identity_file()
        if identity_file.exists():
            try:
                with open(identity_file, 'r') as f:
                    content = yaml.safe_load(f) or {}
                agent_id = content.get("agent_id")
                if agent_id:
                    return agent_id
            except Exception as e:
                print(f"Warning: Failed to read identity file: {e}")
        
        # 2. 环境变量
        agent_id = os.environ.get("OC_AGENT_ID")
        if agent_id:
            return agent_id
        
        # 3. project_state.yaml中的current_agent
        try:
            state_path = Path(self.state_file)
            if state_path.exists():
                with open(state_path, 'r') as f:
                    state = yaml.safe_load(f)
                current = state.get("current_agent")
                if current:
                    return current
        except Exception:
            pass
        
        # 3. Git config
        try:
            result = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout:
                email = result.stdout.strip()
                # 从email提取agent_id，如 "agent1@opencode.ai" -> "agent1"
                return email.split("@")[0]
        except Exception:
            pass
        
        return None
    
    def register(self, agent_id: str, role: str, team: str = "internal") -> bool:
        """
        注册Agent
        
        Args:
            agent_id: Agent ID
            role: 角色
            team: 团队
        
        Returns:
            是否成功
        """
        if role not in self.VALID_ROLES:
            return False
        
        state = self._load_state()
        
        if "agents" not in state:
            state["agents"] = {}
        
        state["agents"][agent_id] = {
            "id": agent_id,
            "role": role,
            "team": team,
            "status": "active",
            "registered_at": datetime.now().isoformat()
        }
        
        self._save_state(state)
        return True
    
    def auto_register(self) -> bool:
        """
        自动注册
        
        Returns:
            是否成功
        """
        agent_id = self.get_current_agent_id()
        if not agent_id:
            return False
        
        # 默认角色
        role = "DEVELOPMENT_LEAD"
        
        return self.register(agent_id, role)
    
    def list_agents(self) -> List[Dict]:
        """
        列出所有Agent
        
        Returns:
            Agent列表
        """
        state = self._load_state()
        return list(state.get("agents", {}).values())
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """
        获取Agent信息
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Agent信息或None
        """
        state = self._load_state()
        return state.get("agents", {}).get(agent_id)
    
    def can_unregister(self, agent_id: str) -> bool:
        """
        检查是否可以注销
        
        Args:
            agent_id: Agent ID
        
        Returns:
            是否可以注销（有pending TODO时返回False）
        """
        from .todo_sync_manager import TodoSyncManager
        sync_manager = TodoSyncManager()
        todo_state = sync_manager.load_todos()
        todos = todo_state.todos
        
        for todo in todos:
            if todo.receiver == agent_id and todo.status == "pending":
                return False
        
        return True
    
    def unregister(self, agent_id: str) -> bool:
        """
        注销Agent
        
        Args:
            agent_id: Agent ID
        
        Returns:
            是否成功
        """
        if not self.can_unregister(agent_id):
            return False
        
        state = self._load_state()
        if agent_id in state.get("agents", {}):
            del state["agents"][agent_id]
            self._save_state(state)
            return True
        return False
