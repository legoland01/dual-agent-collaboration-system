"""v2.2.0 M1 Agent Manager 测试用例

基于 src/core/agent_manager.py
"""
import pytest
import tempfile
from pathlib import Path
import yaml
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.agent_manager import (
    AgentManager,
    AgentType,
    ActionType,
    AgentConfig,
    AgentNotFoundError,
    AgentTypeNotSupportedError,
    AgentConstraintViolationError
)


class TestAgentManagerBasic:
    """Agent 管理器基础测试。"""

    def test_initialize_agent_manager(self, tmp_path):
        """测试初始化 Agent 管理器。"""
        manager = AgentManager(str(tmp_path))
        
        assert manager.project_path == tmp_path
        assert manager.agents_dir == tmp_path / "agents"
        assert manager.agents_dir.exists()

    def test_initialize_default_agents(self, tmp_path):
        """测试初始化默认 Agent。"""
        manager = AgentManager(str(tmp_path))
        agents = manager.initialize_agents()
        
        assert len(agents) == 2
        
        agent_ids = [a.agent_id for a in agents]
        assert "agent_product_manager_1" in agent_ids
        assert "agent_development_lead_1" in agent_ids

    def test_load_agents(self, tmp_path):
        """测试加载 Agent 配置。"""
        manager = AgentManager(str(tmp_path))
        manager.initialize_agents()
        
        manager2 = AgentManager(str(tmp_path))
        agents = manager2.load_agents()
        
        assert len(agents) == 2


class TestAgentAddition:
    """Agent 动态添加测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = AgentManager(str(tmp_path))
        manager.initialize_agents()
        return manager

    def test_add_frontend_agent(self, manager):
        """测试添加前端 Agent。"""
        new_agent = manager.add_agent(AgentType.FRONTEND_DEV, "react")
        
        assert new_agent is not None
        assert new_agent.agent_type == AgentType.FRONTEND_DEV
        assert new_agent.tech_stack == "react"

    def test_add_backend_agent(self, manager):
        """测试添加后端 Agent。"""
        new_agent = manager.add_agent(AgentType.BACKEND_DEV, "go")
        
        assert new_agent is not None
        assert new_agent.agent_type == AgentType.BACKEND_DEV
        assert new_agent.tech_stack == "go"

    def test_add_designer(self, manager):
        """测试添加设计师。"""
        new_agent = manager.add_agent(AgentType.DESIGNER)
        
        assert new_agent is not None
        assert new_agent.agent_type == AgentType.DESIGNER

    def test_list_agents(self, manager):
        """测试列出 Agent。"""
        manager.add_agent(AgentType.FRONTEND_DEV, "react")
        
        all_agents = manager.list_agents()
        assert len(all_agents) == 3
        
        frontend_agents = manager.list_agents(agent_type=AgentType.FRONTEND_DEV)
        assert len(frontend_agents) == 1


class TestAgentConstraints:
    """Agent 职责约束测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = AgentManager(str(tmp_path))
        manager.initialize_agents()
        return manager

    def test_product_manager_constraints(self, manager):
        """测试产品经理约束。"""
        pm_agent = manager.get_agent("agent_product_manager_1")
        
        assert "WRITE_CODE" in pm_agent.forbidden
        assert "CREATE_DESIGN" in pm_agent.forbidden

    def test_development_lead_constraints(self, manager):
        """测试开发负责人约束。"""
        dev_agent = manager.get_agent("agent_development_lead_1")
        
        assert "CREATE_REQUIREMENTS" not in dev_agent.responsibilities

    def test_check_action_allowed(self, manager):
        """测试检查操作是否允许。"""
        pm_agent = manager.get_agent("agent_product_manager_1")
        
        assert manager.check_action_allowed(pm_agent.agent_id, ActionType.CREATE_REQUIREMENTS) is True
        assert manager.check_action_allowed(pm_agent.agent_id, ActionType.WRITE_CODE) is False

    def test_get_allowed_actions(self, manager):
        """测试获取允许的操作列表。"""
        pm_agent = manager.get_agent("agent_product_manager_1")
        
        allowed = manager.get_allowed_actions(pm_agent.agent_id)
        assert ActionType.CREATE_REQUIREMENTS in allowed
        assert ActionType.SIGN_OFF in allowed

    def test_get_forbidden_actions(self, manager):
        """测试获取禁止的操作列表。"""
        pm_agent = manager.get_agent("agent_product_manager_1")
        
        forbidden = manager.get_forbidden_actions(pm_agent.agent_id)
        assert ActionType.WRITE_CODE in forbidden


class TestAgentRemoval:
    """Agent 移除测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = AgentManager(str(tmp_path))
        manager.initialize_agents()
        manager.add_agent(AgentType.FRONTEND_DEV, "react")
        return manager

    def test_remove_agent(self, manager):
        """测试移除 Agent。"""
        frontend_agents = manager.list_agents(agent_type=AgentType.FRONTEND_DEV)
        assert len(frontend_agents) == 1
        
        result = manager.remove_agent(frontend_agents[0].agent_id)
        assert result is True
        
        frontend_agents = manager.list_agents(agent_type=AgentType.FRONTEND_DEV)
        assert len(frontend_agents) == 0

    def test_remove_nonexistent_agent(self, manager):
        """测试移除不存在的 Agent。"""
        with pytest.raises(AgentNotFoundError):
            manager.remove_agent("nonexistent_agent")


class TestAgentStatus:
    """Agent 状态管理测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = AgentManager(str(tmp_path))
        manager.initialize_agents()
        return manager

    def test_update_agent_status(self, manager):
        """测试更新 Agent 状态。"""
        pm_agent = manager.get_agent("agent_product_manager_1")
        
        updated = manager.update_agent_status(pm_agent.agent_id, "busy")
        
        assert updated.status == "busy"


class TestAgentConfig:
    """Agent 配置测试。"""

    def test_agent_config_to_dict(self):
        """测试 Agent 配置转换为字典。"""
        config = AgentConfig(
            agent_id="test_agent",
            agent_type=AgentType.FRONTEND_DEV,
            name="Test Frontend",
            role="前端开发",
            responsibilities=["前端开发", "代码评审"],
            forbidden=["CREATE_REQUIREMENTS", "WRITE_CODE_BACKEND"],
            tech_stack="react"
        )
        
        data = config.to_dict()
        
        assert data["agent_id"] == "test_agent"
        assert data["agent_type"] == "frontend_dev"
        assert data["tech_stack"] == "react"

    def test_agent_config_from_dict(self):
        """测试从字典创建 Agent 配置。"""
        data = {
            "agent_id": "test_agent",
            "agent_type": "backend_dev",
            "name": "Test Backend",
            "role": "后端开发",
            "responsibilities": ["API设计"],
            "forbidden": ["CREATE_REQUIREMENTS"],
            "tech_stack": "go"
        }
        
        config = AgentConfig.from_dict(data)
        
        assert config.agent_id == "test_agent"
        assert config.agent_type == AgentType.BACKEND_DEV
        assert config.tech_stack == "go"


class TestAgentSummary:
    """Agent 摘要测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = AgentManager(str(tmp_path))
        manager.initialize_agents()
        manager.add_agent(AgentType.FRONTEND_DEV, "react")
        manager.add_agent(AgentType.BACKEND_DEV, "go")
        return manager

    def test_get_agent_summary(self, manager):
        """测试获取 Agent 摘要。"""
        summary = manager.get_agent_summary()
        
        assert summary["total_agents"] == 4
        assert summary["by_type"]["product_manager"] == 1
        assert summary["by_type"]["development_lead"] == 1
        assert summary["by_type"]["frontend_dev"] == 1
        assert summary["by_type"]["backend_dev"] == 1


class TestAgentManagerExport:
    """Agent 管理器导出测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = AgentManager(str(tmp_path))
        manager.initialize_agents()
        return manager

    def test_export_config(self, manager):
        """测试导出配置。"""
        config = manager.export_config()
        
        assert "project_path" in config
        assert "agents" in config
        assert "agent_types" in config
        assert len(config["agents"]) == 2

    def test_export_to_file(self, manager, tmp_path):
        """测试导出到文件。"""
        output_path = tmp_path / "agent_config_export.yaml"
        config = manager.export_config(str(output_path))
        
        assert output_path.exists()
        
        with open(output_path, 'r') as f:
            exported = yaml.safe_load(f)
        
        assert len(exported["agents"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
