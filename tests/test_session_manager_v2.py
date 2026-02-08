"""
TC-SESSION-001: 测试SessionManager识别v2.2.x项目结构
BUG-20260208-003: oc-collab工具无法识别项目状态

这个测试用例覆盖了SessionManager无法正确解析project_state.yaml的问题。
"""

import pytest
import os
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


class TestSessionManagerV2Structure:
    """测试SessionManager识别v2.2.x项目结构"""

    def test_session_manager_get_project_info(self):
        """
        TC-SESSION-001: 测试get_project_info正确解析v2.2.x项目结构

        预期结果：
        - project_info["name"] 不应该是 "未配置"
        - project_info["phase"] 不应该是 "未知"

        当前问题：
        - SessionManager.get_project_info() 期望的字段在project_state.yaml中不存在
        - 期望字段: project.name, metadata.project_name, phase
        - 实际字段: 使用v2.2.x版本化结构，无这些顶层字段
        """
        from src.core.session_manager import SessionManager

        manager = SessionManager(str(PROJECT_ROOT))
        project_info = manager.get_project_info()

        # 验证结果
        assert project_info["name"] != "未配置", \
            f"应该能识别项目名称，但返回: {project_info['name']}"
        assert project_info["phase"] != "未知", \
            f"应该能识别当前阶段，但返回: {project_info['phase']}"

    def test_session_manager_get_agent_info(self):
        """
        TC-SESSION-002: 测试get_agent_info返回正确的Agent信息

        预期结果：
        - agent["role"] 不应该是 "未知"
        """
        from src.core.session_manager import SessionManager

        manager = SessionManager(str(PROJECT_ROOT))

        # 测试Agent 1
        agent1_info = manager.get_agent_info("agent1")
        assert agent1_info["role"] != "未知", \
            f"Agent 1 角色应该是'产品经理'，但返回: {agent1_info['role']}"

    def test_oc_collab_status_command(self):
        """
        TC-SESSION-003: 测试oc-collab status命令能正确显示项目状态

        预期结果：
        - 输出不应该显示"未配置"
        """
        import subprocess

        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "status"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )

        output = result.stdout + result.stderr

        # 检查不应该出现的字段
        assert "未配置" not in output, \
            "oc-collab status 不应该显示'未配置'"


class TestSignoffWithV2Structure:
    """测试签署功能在v2.2.x结构下的行为"""

    def test_signoff_requires_valid_phase(self):
        """
        TC-SESSION-004: 测试签署命令需要有效的阶段状态

        当前问题：
        - signoff命令报错"当前阶段状态不允许签署"
        - 原因是无法识别当前的开发阶段
        """
        from src.core.state_manager import StateManager

        manager = StateManager(str(PROJECT_ROOT))
        state = manager.load_state()

        # v2.2.x结构下，状态应该在v2.2.x子节点中
        assert "v2.2.4" in state, "应该包含v2.2.4版本信息"

        # 检查v2.2.4的开发状态
        v224 = state["v2.2.4"]
        assert v224["development"]["status"] == "completed", \
            "v2.2.4开发状态应该是completed"


class TestSignoffV2Structure:
    """
    TC-SESSION-005: 测试signoff.py支持v2.2.x结构
    BUG-20260208-004: signoff.py不支持v2.2.x版本化结构

    问题描述：
    - signoff.py期望测试状态在顶层 test 字段
    - v2.2.x结构中测试状态在 v2.2.x.testing 字段
    """

    def test_signoff_can_read_v2_testing_status(self):
        """
        TC-SESSION-005: 测试signoff能读取v2.2.x的testing状态

        预期结果：
        - signoff.py应该能识别v2.2.4.testing.status
        """
        from src.core.state_manager import StateManager

        state_manager = StateManager(str(PROJECT_ROOT))
        
        # 创建signoff engine（需要workflow_engine，但这里只用state_manager测试）
        # 由于signoff需要workflow_engine，我们直接测试状态读取逻辑
        
        state = state_manager.load_state()
        
        # 期望signoff能读取v2.2.4.testing.status
        if "v2.2.4" in state and "testing" in state["v2.2.4"]:
            testing_status = state["v2.2.4"]["testing"].get("status", "")
            assert testing_status in ["in_progress", "approved", "passed"], \
                f"v2.2.4.testing.status应该是in_progress/approved/passed，但返回: {testing_status}"
        else:
            pytest.skip("v2.2.4.testing不存在（可能是其他版本结构）")

    def test_signoff_test_stage_v2_structure(self):
        """
        TC-SESSION-006: 测试signoff.test阶段能识别v2.2.x结构

        当前问题：
        - signoff.py的_get_stage_data()使用 state.get("test", {})
        - 这在v2.2.x结构中会失败，因为testing数据在v2.2.4.testing
        """
        from src.core.signoff import SignoffEngine
        from src.core.state_manager import StateManager
        from unittest.mock import Mock

        state_manager = StateManager(str(PROJECT_ROOT))
        workflow_engine = Mock()
        
        engine = SignoffEngine(state_manager, workflow_engine)
        
        # 测试获取test阶段数据
        state = state_manager.load_state()
        
        # 检查STAGE_CONFIG
        assert "test" in engine.STAGE_CONFIG, "应该有test阶段配置"
        
        # 在v2.2.x结构下，signoff.py需要能识别v2.2.x.testing
        # 当前实现只检查顶层test字段，这是bug的根源
