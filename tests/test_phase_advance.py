"""PhaseAdvance 单元测试。"""
import pytest
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.phase_advance import PhaseAdvanceEngine


class TestPhaseAdvanceEngine:
    """阶段推进引擎测试类。"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def phase_advance(self, temp_dir):
        """创建阶段推进引擎实例。"""
        return PhaseAdvanceEngine(temp_dir)
    
    def test_init(self, phase_advance, temp_dir):
        """测试初始化。"""
        assert phase_advance.project_path == Path(temp_dir)
        assert phase_advance.state_manager is not None
        assert phase_advance.workflow_engine is not None
    
    def test_phase_transitions_defined(self):
        """测试阶段转换定义。"""
        transitions = PhaseAdvanceEngine.PHASE_TRANSITIONS
        assert "development" in transitions
        assert "testing" in transitions
        assert "deployment" in transitions
    
    def test_phase_transition_structure(self):
        """测试阶段转换结构。"""
        transition = PhaseAdvanceEngine.PHASE_TRANSITIONS["development"]
        assert "condition" in transition
        assert "next_phase" in transition
        assert "description" in transition
        assert transition["next_phase"] == "testing"
    
    def test_get_pending_bugs_empty(self, phase_advance, temp_dir):
        """测试获取空bug列表。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        
        bugs = phase_advance.get_pending_bugs()
        assert bugs == []
    
    def test_get_pending_bugs_with_data(self, phase_advance, temp_dir):
        """测试获取bug列表（有数据）。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        state = sm.load_state()
        state["test"] = {"issues_to_fix": ["bug1", "bug2"]}
        sm.save_state(state)
        
        bugs = phase_advance.get_pending_bugs()
        assert len(bugs) == 2
    
    def test_check_condition_development_not_met(self, phase_advance, temp_dir):
        """测试开发阶段条件不满足。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        state = sm.load_state()
        state["development"] = {"status": "in_progress"}
        sm.save_state(state)
        
        result = phase_advance.check_condition("development", state)
        assert result is False
    
    def test_check_condition_development_met(self, phase_advance, temp_dir):
        """测试开发阶段条件满足。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        state = sm.load_state()
        state["development"] = {"status": "completed"}
        sm.save_state(state)
        
        result = phase_advance.check_condition("development", state)
        assert result is True
    
    def test_check_condition_testing_not_met(self, phase_advance, temp_dir):
        """测试测试阶段条件不满足。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        state = sm.load_state()
        state["test"] = {"pm_signoff": False, "dev_signoff": False}
        sm.save_state(state)
        
        result = phase_advance.check_condition("testing", state)
        assert result is False
    
    def test_check_condition_testing_met(self, phase_advance, temp_dir):
        """测试测试阶段条件满足。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        state = sm.load_state()
        state["test"] = {"pm_signoff": True, "dev_signoff": True}
        sm.save_state(state)
        
        result = phase_advance.check_condition("testing", state)
        assert result is True
    
    def test_check_condition_unknown_phase(self, phase_advance):
        """测试未知阶段。"""
        result = phase_advance.check_condition("unknown_phase", {})
        assert result is False
    
    def test_check_and_advance_no_transition(self, phase_advance, temp_dir):
        """测试不支持自动推进的阶段。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        
        result = phase_advance.check_and_advance()
        
        assert result["advanced"] is False
        assert "不支持自动推进" in result["reason"]
    
    def test_check_and_advance_condition_not_met(self, phase_advance, temp_dir):
        """测试条件不满足时不推进。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        sm.update_phase("development")
        state = sm.load_state()
        state["development"] = {"status": "in_progress"}
        sm.save_state(state)
        
        result = phase_advance.check_and_advance()
        
        assert result["advanced"] is False
        assert "条件未满足" in result["reason"]
    
    def test_check_and_advance_success(self, phase_advance, temp_dir):
        """测试自动推进成功。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        sm.update_phase("development")
        state = sm.load_state()
        state["development"] = {"status": "completed"}
        sm.save_state(state)
        
        result = phase_advance.check_and_advance()
        
        assert result["advanced"] is True
        assert result["from_phase"] == "development"
        assert result["to_phase"] == "testing"
    
    def test_manual_advance_no_target(self, phase_advance, temp_dir):
        """测试手动推进（无目标阶段）。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        
        result = phase_advance.manual_advance()
        
        assert result["success"] is False
        assert "无法自动确定下一阶段" in result["error"]
    
    def test_manual_advance_condition_not_met(self, phase_advance, temp_dir):
        """测试手动推进条件不满足。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        sm.update_phase("development")
        state = sm.load_state()
        state["development"] = {"status": "in_progress"}
        sm.save_state(state)
        
        result = phase_advance.manual_advance(target_phase="testing")
        
        assert result["success"] is False
        assert "条件未满足" in result["error"]
    
    def test_manual_advance_force(self, phase_advance, temp_dir):
        """测试强制手动推进。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        sm.update_phase("development")
        
        result = phase_advance.manual_advance(target_phase="testing", force=True)
        
        assert result["success"] is True
        assert result["to_phase"] == "testing"
    
    def test_get_phase_info(self, phase_advance, temp_dir):
        """测试获取阶段信息。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        
        info = phase_advance.get_phase_info("development")
        
        assert info["phase"] == "development"
        assert "next_phase" in info
        assert "description" in info
    
    def test_list_phases(self, phase_advance, temp_dir):
        """测试列出所有阶段。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        
        result = phase_advance.list_phases()
        
        assert "current_phase" in result
        assert "phases" in result
        assert len(result["phases"]) == 11
    
    def test_detect_test_activate_agent_bugs_not_testing_phase(self, phase_advance, temp_dir):
        """测试非测试阶段不触发bug检测。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        sm.update_phase("development")
        
        result = phase_advance.detect_test_activate_agent_bugs_and2()
        
        assert result["triggered"] is False
        assert "testing" in result["reason"]
    
    def test_detect_test_activate_agent_no_bugs(self, phase_advance, temp_dir):
        """测试无bug时不触发。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        sm.update_phase("testing")
        
        result = phase_advance.detect_test_activate_agent_bugs_and2()
        
        assert result["triggered"] is False
        assert "无待修复的 bug" in result["reason"]
    
    def test_detect_test_activate_agent_with_bugs(self, phase_advance, temp_dir):
        """测试有bug时触发。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        sm.update_phase("testing")
        state = sm.load_state()
        state["test"] = {"issues_to_fix": ["bug1", "bug2"]}
        sm.save_state(state)
        
        result = phase_advance.detect_test_activate_agent_bugs_and2()
        
        assert result["triggered"] is True
        assert result["bugs_found"] == 2
        
        new_state = sm.load_state()
        assert new_state["phase"] == "development"
    
    def test_condition_description(self, phase_advance, temp_dir):
        """测试条件描述。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        
        desc = phase_advance._get_condition_description("development", {})
        assert "completed" in desc
    
    def test_detect_test_activate_agent_with_agents(self, phase_advance, temp_dir):
        """测试有bug时触发并激活agent。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        sm.update_phase("testing")
        state = sm.load_state()
        state["test"] = {"issues_to_fix": ["bug1", "bug2"]}
        state["project"] = {
            "agents": {
                "agent1": {"name": "Agent 1", "current": False},
                "agent2": {"name": "Agent 2", "current": False}
            }
        }
        sm.save_state(state)
        
        result = phase_advance.detect_test_activate_agent_bugs_and2()
        
        assert result["triggered"] is True
        assert result["bugs_found"] == 2
        
        new_state = sm.load_state()
        assert new_state["phase"] == "development"
        assert new_state["project"]["agents"]["agent1"]["current"] is False
        assert new_state["project"]["agents"]["agent2"]["current"] is True
    
    def test_detect_test_activate_agent_exception(self, phase_advance, temp_dir):
        """测试bug检测异常处理。"""
        from src.core.state_manager import StateManager
        from unittest.mock import patch, MagicMock
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        sm.update_phase("testing")
        state = sm.load_state()
        state["test"] = {"issues_to_fix": ["bug1"]}
        state["project"] = {"agents": {"agent2": {"current": False}}}
        sm.save_state(state)
        
        with patch.object(phase_advance.state_manager, 'save_state', side_effect=Exception("Disk error")):
            result = phase_advance.detect_test_activate_agent_bugs_and2()
        
        assert result["triggered"] is False
        assert "error" in result
    
    def test_check_and_advance_exception(self, phase_advance, temp_dir):
        """测试自动推进异常处理。"""
        from src.core.state_manager import StateManager
        from unittest.mock import patch, MagicMock
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        sm.update_phase("development")
        state = sm.load_state()
        state["development"] = {"status": "completed"}
        sm.save_state(state)
        
        with patch.object(phase_advance.state_manager, 'update_phase', side_effect=Exception("Database error")):
            result = phase_advance.check_and_advance()
        
        assert result["advanced"] is False
        assert "reason" in result or "message" in result
    
    def test_manual_advance_exception(self, phase_advance, temp_dir):
        """测试手动推进异常处理。"""
        from src.core.state_manager import StateManager
        from unittest.mock import patch
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        sm.update_phase("development")
        
        with patch.object(phase_advance.state_manager, 'update_phase', side_effect=Exception("Database error")):
            result = phase_advance.manual_advance(target_phase="testing", force=True)
        
        assert result["success"] is False
        assert "error" in result
    
    def test_check_condition_non_callable_condition(self, phase_advance, temp_dir):
        """测试非可调用条件。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        
        transition = phase_advance.PHASE_TRANSITIONS["development"]
        original_condition = transition["condition"]
        transition["condition"] = "not a callable"
        
        try:
            result = phase_advance.check_condition("development", {})
            assert result is False
        finally:
            transition["condition"] = original_condition
    
    def test_manual_advance_determines_next_phase(self, phase_advance, temp_dir):
        """测试手动推进自动确定下一阶段。"""
        from src.core.state_manager import StateManager
        sm = StateManager(temp_dir)
        sm.init_state("Test", "PYTHON")
        sm.update_phase("development")
        
        result = phase_advance.manual_advance(force=True)
        
        assert result["success"] is True
        assert result["to_phase"] == "testing"


class TestPhaseAdvanceModule:
    """阶段推进模块测试。"""

    def test_module_importable(self):
        """测试模块可导入。"""
        from src.core import phase_advance
        assert hasattr(phase_advance, 'PhaseAdvanceEngine')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
