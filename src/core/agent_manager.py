"""Agent 管理模块 - v2.2.0 M1 多 Agent 动态管理

提供 Agent 角色体系、动态添加、职责约束等功能。
"""
import os
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml
import json
import logging


logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Agent 类型枚举。"""
    PRODUCT_MANAGER = "product_manager"
    DEVELOPMENT_LEAD = "development_lead"
    FRONTEND_DEV = "frontend_dev"
    BACKEND_DEV = "backend_dev"
    DESIGNER = "designer"
    TESTER = "tester"


class ActionType(Enum):
    """操作类型枚举。"""
    CREATE_REQUIREMENTS = "CREATE_REQUIREMENTS"
    REVIEW_DESIGN = "REVIEW_DESIGN"
    SIGN_OFF = "SIGN_OFF"
    MANAGE_PROJECT = "MANAGE_PROJECT"
    WRITE_CODE = "WRITE_CODE"
    CREATE_DESIGN = "CREATE_DESIGN"
    CODE_REVIEW = "CODE_REVIEW"
    WRITE_CODE_FRONTEND = "WRITE_CODE_FRONTEND"
    WRITE_CODE_BACKEND = "WRITE_CODE_BACKEND"
    REVIEW_DESIGN_FRONTEND = "REVIEW_DESIGN_FRONTEND"
    API_DESIGN = "API_DESIGN"
    UPLOAD_DESIGN = "UPLOAD_DESIGN"
    EXECUTE_TEST = "EXECUTE_TEST"


@dataclass
class AgentConfig:
    """Agent 配置。"""
    agent_id: str
    agent_type: AgentType
    name: str
    role: str
    responsibilities: List[str]
    forbidden: List[str]
    tech_stack: Optional[str] = None
    created_at: str = field(default_factory=lambda: str(uuid.uuid4()))
    last_active: Optional[str] = None
    status: str = "active"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "name": self.name,
            "role": self.role,
            "responsibilities": self.responsibilities,
            "forbidden": self.forbidden,
            "tech_stack": self.tech_stack,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfig":
        """从字典创建。"""
        return cls(
            agent_id=data["agent_id"],
            agent_type=AgentType(data["agent_type"]),
            name=data["name"],
            role=data["role"],
            responsibilities=data["responsibilities"],
            forbidden=data["forbidden"],
            tech_stack=data.get("tech_stack"),
            created_at=data.get("created_at", str(uuid.uuid4())),
            last_active=data.get("last_active"),
            status=data.get("status", "active")
        )


AGENT_ROLE_CONFIG: Dict[AgentType, Dict[str, Any]] = {
    AgentType.PRODUCT_MANAGER: {
        "role": "产品经理/项目经理",
        "allowed": [
            ActionType.CREATE_REQUIREMENTS,
            ActionType.REVIEW_DESIGN,
            ActionType.SIGN_OFF,
            ActionType.MANAGE_PROJECT
        ],
        "forbidden": [
            ActionType.WRITE_CODE,
            ActionType.CREATE_DESIGN
        ],
        "required": True,
        "initial_count": 1
    },
    AgentType.DEVELOPMENT_LEAD: {
        "role": "开发负责人",
        "allowed": [
            ActionType.CREATE_DESIGN,
            ActionType.WRITE_CODE,
            ActionType.CODE_REVIEW
        ],
        "forbidden": [
        ],
        "required": True,
        "initial_count": 1
    },
    AgentType.FRONTEND_DEV: {
        "role": "前端开发",
        "allowed": [
            ActionType.WRITE_CODE_FRONTEND,
            ActionType.REVIEW_DESIGN_FRONTEND
        ],
        "forbidden": [
            ActionType.WRITE_CODE_BACKEND,
            ActionType.CREATE_REQUIREMENTS
        ],
        "required": False,
        "initial_count": 0
    },
    AgentType.BACKEND_DEV: {
        "role": "后端开发",
        "allowed": [
            ActionType.WRITE_CODE_BACKEND,
            ActionType.API_DESIGN
        ],
        "forbidden": [
            ActionType.WRITE_CODE_FRONTEND,
            ActionType.CREATE_REQUIREMENTS
        ],
        "required": False,
        "initial_count": 0
    },
    AgentType.DESIGNER: {
        "role": "UI/UE 设计",
        "allowed": [
            ActionType.CREATE_DESIGN,
            ActionType.UPLOAD_DESIGN,
            ActionType.REVIEW_DESIGN
        ],
        "forbidden": [
            ActionType.WRITE_CODE,
            ActionType.CREATE_REQUIREMENTS
        ],
        "required": False,
        "initial_count": 0
    },
    AgentType.TESTER: {
        "role": "测试",
        "allowed": [
            ActionType.EXECUTE_TEST,
            ActionType.REVIEW_DESIGN
        ],
        "forbidden": [
            ActionType.WRITE_CODE,
            ActionType.CREATE_REQUIREMENTS,
            ActionType.CREATE_DESIGN
        ],
        "required": False,
        "initial_count": 0
    }
}


class AgentManagerError(Exception):
    """Agent 管理异常基类。"""
    pass


class AgentNotFoundError(AgentManagerError):
    """Agent 未找到异常。"""
    pass


class AgentTypeNotSupportedError(AgentManagerError):
    """Agent 类型不支持异常。"""
    pass


class AgentConstraintViolationError(AgentManagerError):
    """Agent 约束违反异常。"""
    pass


class AgentManager:
    """Agent 管理器。"""
    
    DEFAULT_AGENTS_DIR = "agents"
    AGENT_CONFIG_FILE = "agent_config.yaml"
    
    def __init__(self, project_path: str, agents_dir: Optional[str] = None):
        """初始化 Agent 管理器。
        
        Args:
            project_path: 项目路径
            agents_dir: Agent 配置目录，默认为 project_path/agents
        """
        self.project_path = Path(project_path)
        self.agents_dir = self.project_path / (agents_dir or self.DEFAULT_AGENTS_DIR)
        self.agents: Dict[str, AgentConfig] = {}
        self._ensure_agents_directory()
    
    def _ensure_agents_directory(self) -> None:
        """确保 Agent 目录存在。"""
        self.agents_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_agent_id(self, agent_type: AgentType, tech_stack: Optional[str] = None) -> str:
        """生成 Agent ID。
        
        Args:
            agent_type: Agent 类型
            tech_stack: 技术栈（可选）
            
        Returns:
            Agent ID
        """
        base_name = agent_type.value
        if tech_stack:
            base_name = f"{base_name}_{tech_stack}"
        existing_count = sum(
            1 for a in self.agents.values() 
            if a.agent_type == agent_type and (a.tech_stack or "") == (tech_stack or "")
        )
        return f"agent_{base_name}_{existing_count + 1}"
    
    def _create_default_agents(self) -> List[AgentConfig]:
        """创建默认的 Agent 列表。
        
        Returns:
            默认 Agent 列表
        """
        agents = []
        
        for agent_type, config in AGENT_ROLE_CONFIG.items():
            for i in range(config["initial_count"]):
                agent_id = self._generate_agent_id(agent_type)
                agent = AgentConfig(
                    agent_id=agent_id,
                    agent_type=agent_type,
                    name=f"{config['role']} {i + 1}",
                    role=config["role"],
                    responsibilities=config["role"].split("/"),
                    forbidden=[a.value for a in config["forbidden"]],
                    tech_stack=None
                )
                agents.append(agent)
        
        return agents
    
    def initialize_agents(self, custom_agents: Optional[List[AgentConfig]] = None) -> List[AgentConfig]:
        """初始化 Agent。
        
        Args:
            custom_agents: 自定义 Agent 列表
            
        Returns:
            初始化后的 Agent 列表
        """
        if custom_agents:
            agents = custom_agents
        else:
            agents = self._create_default_agents()
        
        for agent in agents:
            self.agents[agent.agent_id] = agent
            self._save_agent_config(agent)
        
        logger.info(f"初始化了 {len(agents)} 个 Agent")
        return agents
    
    def _save_agent_config(self, agent: AgentConfig) -> None:
        """保存 Agent 配置。
        
        Args:
            agent: Agent 配置
        """
        config_file = self.agents_dir / f"{agent.agent_id}.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(agent.to_dict(), f, allow_unicode=True)
    
    def load_agents(self) -> List[AgentConfig]:
        """加载所有 Agent 配置。
        
        Returns:
            Agent 配置列表
        """
        self.agents.clear()
        
        for config_file in self.agents_dir.glob("*.yaml"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if data:
                    agent = AgentConfig.from_dict(data)
                    self.agents[agent.agent_id] = agent
            except Exception as e:
                logger.warning(f"加载 Agent 配置失败: {config_file}, 错误: {e}")
        
        return list(self.agents.values())
    
    def add_agent(
        self,
        agent_type: AgentType,
        tech_stack: Optional[str] = None,
        name: Optional[str] = None
    ) -> AgentConfig:
        """添加新 Agent。
        
        Args:
            agent_type: Agent 类型
            tech_stack: 技术栈（可选）
            name: Agent 名称（可选）
            
        Returns:
            新创建的 Agent 配置
            
        Raises:
            AgentTypeNotSupportedError: Agent 类型不支持
        """
        if agent_type not in AGENT_ROLE_CONFIG:
            raise AgentTypeNotSupportedError(f"不支持的 Agent 类型: {agent_type}")
        
        role_config = AGENT_ROLE_CONFIG[agent_type]
        agent_id = self._generate_agent_id(agent_type, tech_stack)
        
        agent = AgentConfig(
            agent_id=agent_id,
            agent_type=agent_type,
            name=name or f"{role_config['role']} {len([a for a in self.agents.values() if a.agent_type == agent_type]) + 1}",
            role=role_config["role"],
            responsibilities=role_config["role"].split("/"),
            forbidden=[a.value for a in role_config["forbidden"]],
            tech_stack=tech_stack
        )
        
        self.agents[agent.agent_id] = agent
        self._save_agent_config(agent)
        
        logger.info(f"添加了新 Agent: {agent_id} ({agent_type.value})")
        return agent
    
    def remove_agent(self, agent_id: str) -> bool:
        """移除 Agent。
        
        Args:
            agent_id: Agent ID
            
        Returns:
            是否成功移除
            
        Raises:
            AgentNotFoundError: Agent 未找到
        """
        if agent_id not in self.agents:
            raise AgentNotFoundError(f"Agent 未找到: {agent_id}")
        
        agent = self.agents.pop(agent_id)
        config_file = self.agents_dir / f"{agent_id}.yaml"
        
        if config_file.exists():
            config_file.unlink()
        
        logger.info(f"移除了 Agent: {agent_id}")
        return True
    
    def get_agent(self, agent_id: str) -> AgentConfig:
        """获取 Agent 配置。
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent 配置
            
        Raises:
            AgentNotFoundError: Agent 未找到
        """
        if agent_id not in self.agents:
            raise AgentNotFoundError(f"Agent 未找到: {agent_id}")
        return self.agents[agent_id]
    
    def list_agents(self, agent_type: Optional[AgentType] = None, status: Optional[str] = None) -> List[AgentConfig]:
        """列出 Agent。
        
        Args:
            agent_type: Agent 类型过滤
            status: 状态过滤
            
        Returns:
            Agent 配置列表
        """
        agents = list(self.agents.values())
        
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]
        
        if status:
            agents = [a for a in agents if a.status == status]
        
        return agents
    
    def check_action_allowed(self, agent_id: str, action: ActionType) -> bool:
        """检查 Agent 是否允许执行某个操作。
        
        Args:
            agent_id: Agent ID
            action: 操作类型
            
        Returns:
            是否允许
            
        Raises:
            AgentNotFoundError: Agent 未找到
        """
        agent = self.get_agent(agent_id)
        
        if action.value in agent.forbidden:
            return False
        
        if agent.agent_type in AGENT_ROLE_CONFIG:
            role_config = AGENT_ROLE_CONFIG[agent.agent_type]
            return action in role_config["allowed"]
        
        return True
    
    def get_allowed_actions(self, agent_id: str) -> Set[ActionType]:
        """获取 Agent 允许的操作列表。
        
        Args:
            agent_id: Agent ID
            
        Returns:
            允许的操作集合
            
        Raises:
            AgentNotFoundError: Agent 未找到
        """
        agent = self.get_agent(agent_id)
        
        if agent.agent_type in AGENT_ROLE_CONFIG:
            return set(AGENT_ROLE_CONFIG[agent.agent_type]["allowed"])
        
        return set()
    
    def get_forbidden_actions(self, agent_id: str) -> Set[ActionType]:
        """获取 Agent 被禁止的操作列表。
        
        Args:
            agent_id: Agent ID
            
        Returns:
            被禁止的操作集合
            
        Raises:
            AgentNotFoundError: Agent 未找到
        """
        agent = self.get_agent(agent_id)
        return set(ActionType(a) for a in agent.forbidden)
    
    def update_agent_status(self, agent_id: str, status: str) -> AgentConfig:
        """更新 Agent 状态。
        
        Args:
            agent_id: Agent ID
            status: 新状态
            
        Returns:
            更新后的 Agent 配置
            
        Raises:
            AgentNotFoundError: Agent 未找到
        """
        agent = self.get_agent(agent_id)
        agent.status = status
        self._save_agent_config(agent)
        
        return agent
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """获取 Agent 管理摘要。
        
        Returns:
            摘要信息
        """
        agent_counts = {}
        for agent_type in AgentType:
            count = len(self.list_agents(agent_type=agent_type))
            agent_counts[agent_type.value] = count
        
        return {
            "total_agents": len(self.agents),
            "by_type": agent_counts,
            "agents_dir": str(self.agents_dir)
        }
    
    def export_config(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """导出 Agent 管理配置。
        
        Args:
            output_path: 输出路径（可选）
            
        Returns:
            配置字典
        """
        config = {
            "project_path": str(self.project_path),
            "agents_dir": str(self.agents_dir),
            "agents": [agent.to_dict() for agent in self.agents.values()],
            "agent_types": {
                at.value: {
                    "role": AGENT_ROLE_CONFIG[at]["role"],
                    "required": AGENT_ROLE_CONFIG[at]["required"]
                }
                for at in AgentType
            }
        }
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
        
        return config


if __name__ == "__main__":
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = AgentManager(tmpdir)
        
        agents = manager.initialize_agents()
        print(f"初始化了 {len(agents)} 个 Agent")
        
        for agent in agents:
            print(f"  - {agent.agent_id}: {agent.role}")
        
        new_agent = manager.add_agent(AgentType.FRONTEND_DEV, "react")
        print(f"\n添加了新 Agent: {new_agent.agent_id}")
        
        summary = manager.get_agent_summary()
        print(f"\nAgent 摘要: {summary}")
