"""
Agent注册表管理模块

管理Agent信息，支持注册、注销、列表查询。
"""

import os
import subprocess
import yaml
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
        
        优先级: CLI参数 > 环境变量 > Git config
        
        Returns:
            Agent ID或None
        """
        # 1. 环境变量
        agent_id = os.environ.get("OC_AGENT_ID")
        if agent_id:
            return agent_id
        
        # 2. Git config
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
        state = self._load_state()
        todos = state.get("todos", [])
        
        # 检查是否有分配给该Agent的pending TODO
        for todo in todos:
            if todo.get("receiver") == agent_id and todo.get("status") == "pending":
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
