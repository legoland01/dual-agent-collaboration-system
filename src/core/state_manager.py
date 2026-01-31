"""状态管理器模块。"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ..utils.yaml import load_yaml, save_yaml
from ..utils.date import get_current_time


class StateManagerError(Exception):
    """状态管理器异常基类。"""
    pass


class StateFileNotFoundError(StateManagerError):
    """状态文件不存在异常。"""
    pass


class StateValidationError(StateManagerError):
    """状态验证异常。"""
    pass


class StateManager:
    """状态管理器。"""
    
    STATE_FILE = "state/project_state.yaml"
    
    def __init__(self, project_path: str):
        """初始化状态管理器。"""
        self.project_path = Path(project_path)
        self.state_file = self.project_path / self.STATE_FILE
    
    def load_state(self) -> Dict[str, Any]:
        """加载状态文件。"""
        if not self.state_file.exists():
            raise StateFileNotFoundError(f"状态文件不存在: {self.state_file}")
        
        state = load_yaml(str(self.state_file))
        if not isinstance(state, dict):
            raise StateValidationError("状态文件格式错误")
        
        return state
    
    def save_state(self, state: Dict[str, Any]) -> None:
        """保存状态文件。"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        save_yaml(str(self.state_file), state)
    
    def init_state(self, project_name: str, project_type: str) -> Dict[str, Any]:
        """初始化状态文件。"""
        state = {
            "version": "1.0.0",
            "project": {
                "name": project_name,
                "type": project_type,
                "created_at": get_current_time(),
                "updated_at": get_current_time()
            },
            "phase": "project_init",
            "agents": {
                "agent1": {"role": "产品经理", "current": True},
                "agent2": {"role": "开发", "current": False}
            },
            "requirements": {
                "version": "",
                "status": "pending",
                "pm_signoff": False,
                "dev_signoff": False,
                "review_cycles": 0
            },
            "design": {
                "version": "",
                "status": "pending",
                "pm_signoff": False,
                "dev_signoff": False
            },
            "test": {
                "version": "",
                "status": "pending",
                "blackbox_cases": 0,
                "whitebox_passed": 0,
                "blackbox_passed": 0
            },
            "development": {
                "status": "not_started",
                "branch": "",
                "last_updated": ""
            },
            "deployment": {
                "status": "pending",
                "version": "",
                "last_updated": ""
            },
            "history": []
        }
        self.save_state(state)
        return state
    
    def update_phase(self, phase: str) -> Dict[str, Any]:
        """更新当前阶段。"""
        state = self.load_state()
        state["phase"] = phase
        state["updated_at"] = get_current_time()
        self.save_state(state)
        return state
    
    def update_signoff(self, stage: str, agent: str, signed: bool, comment: str = "") -> Dict[str, Any]:
        """更新签署状态。"""
        state = self.load_state()
        stage_data = state.get(stage, {})
        
        signoff_key = f"{agent}_signoff"
        date_key = f"{agent}_signoff_date"
        
        if signoff_key in stage_data:
            stage_data[signoff_key] = signed
        if date_key in stage_data:
            stage_data[date_key] = get_current_time() if signed else ""
        
        state["updated_at"] = get_current_time()
        self.save_state(state)
        return state
    
    def get_current_phase(self) -> str:
        """获取当前阶段。"""
        state = self.load_state()
        return state.get("phase", "unknown")
    
    def get_signoff_status(self, stage: str) -> Dict[str, Any]:
        """获取签署状态。"""
        state = self.load_state()
        stage_data = state.get(stage, {})
        return {
            "pm_signoff": stage_data.get("pm_signoff", False),
            "dev_signoff": stage_data.get("dev_signoff", False)
        }
    
    def get_active_agent(self) -> str:
        """获取当前活跃的Agent。"""
        state = self.load_state()
        for agent_id, agent_data in state.get("agents", {}).items():
            if agent_data.get("current", False):
                return agent_id
        return "unknown"
    
    def set_active_agent(self, agent_id: str) -> Dict[str, Any]:
        """设置活跃的Agent。"""
        state = self.load_state()
        for id in state.get("agents", {}):
            state["agents"][id]["current"] = (id == agent_id)
        state["updated_at"] = get_current_time()
        self.save_state(state)
        return state
    
    def add_history(self, action: str, agent: str, details: str) -> None:
        """添加协作历史记录。"""
        state = self.load_state()
        history = state.get("history", [])
        history.insert(0, {
            "timestamp": get_current_time(),
            "agent": agent,
            "action": action,
            "details": details
        })
        state["history"] = history
        state["updated_at"] = get_current_time()
        self.save_state(state)
    
    def get_history(self, limit: int = 20) -> list:
        """获取协作历史。"""
        state = self.load_state()
        return state.get("history", [])[:limit]
    
    def update_requirements_version(self, version: str) -> None:
        """更新需求版本号。"""
        state = self.load_state()
        state["requirements"]["version"] = version
        state["requirements"]["status"] = "draft"
        state["updated_at"] = get_current_time()
        self.save_state(state)
    
    def update_design_version(self, version: str) -> None:
        """更新设计版本号。"""
        state = self.load_state()
        state["design"]["version"] = version
        state["design"]["status"] = "draft"
        state["updated_at"] = get_current_time()
        self.save_state(state)
    
    def increment_review_cycle(self) -> None:
        """增加评审轮次。"""
        state = self.load_state()
        current = state.get("requirements", {}).get("review_cycles", 0)
        state["requirements"]["review_cycles"] = current + 1
        state["updated_at"] = get_current_time()
        self.save_state(state)
    
    def can_proceed_to_next_phase(self) -> bool:
        """检查是否可以推进到下一阶段。"""
        state = self.load_state()
        phase = state.get("phase", "")
        
        if phase == "requirements_review":
            req = state.get("requirements", {})
            return req.get("pm_signoff", False) and req.get("dev_signoff", False)
        elif phase == "design_review":
            design = state.get("design", {})
            return design.get("pm_signoff", False) and design.get("dev_signoff", False)
        
        return False
