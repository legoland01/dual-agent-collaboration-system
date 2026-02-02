"""工作流引擎单元测试。"""
import tempfile
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.state_manager import StateManager
from src.core.workflow import (
    WorkflowEngine, 
    WorkflowError, 
    IllegalPhaseTransitionError
)


class TestWorkflowExceptions:
    """工作流异常测试。"""

    def test_workflow_error(self):
        """测试工作流异常。"""
        error = WorkflowError("Test error")
        assert "Test error" in str(error)

    def test_illegal_phase_transition_error(self):
        """测试非法阶段转换异常。"""
        error = IllegalPhaseTransitionError("Invalid transition")
        assert "Invalid transition" in str(error)


class TestWorkflowEngine:
    """工作流引擎测试类。"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def state_manager(self, temp_dir):
        """创建状态管理器实例。"""
        sm = StateManager(temp_dir)
        sm.init_state("TestProject", "PYTHON")
        return sm
    
    @pytest.fixture
    def workflow_engine(self, state_manager):
        """创建工作流引擎实例。"""
        return WorkflowEngine(state_manager)
    
    def test_transitions_constant(self):
        """测试转换常量。"""
        assert "project_init" in WorkflowEngine.TRANSITIONS
        assert "completed" in WorkflowEngine.TRANSITIONS
        assert WorkflowEngine.TRANSITIONS["completed"] == []
    
    def test_phase_order_constant(self):
        """测试阶段顺序常量。"""
        assert len(WorkflowEngine.PHASE_ORDER) == 11
        assert WorkflowEngine.PHASE_ORDER[0] == "project_init"
        assert WorkflowEngine.PHASE_ORDER[-1] == "completed"
    
    def test_initialization(self, workflow_engine):
        """测试初始化。"""
        assert workflow_engine.state_manager is not None
    
    def test_can_transition_valid(self, workflow_engine):
        """测试合法状态转换。"""
        assert workflow_engine.can_transition("project_init", "requirements_draft") is True
    
    def test_can_transition_invalid(self, workflow_engine):
        """测试非法状态转换。"""
        assert workflow_engine.can_transition("project_init", "development") is False
    
    def test_can_transition_unknown_phase(self, workflow_engine):
        """测试未知阶段的状态转换。"""
        assert workflow_engine.can_transition("unknown_phase", "development") is False
    
    def test_get_valid_next_phases(self, workflow_engine):
        """测试获取合法下一阶段。"""
        valid = workflow_engine.get_valid_next_phases("project_init")
        assert "requirements_draft" in valid
    
    def test_get_valid_next_phases_completed(self, workflow_engine):
        """测试已完成阶段的下一阶段。"""
        valid = workflow_engine.get_valid_next_phases("completed")
        assert valid == []
    
    def test_get_valid_next_phases_unknown(self, workflow_engine):
        """测试未知阶段的下一阶段。"""
        valid = workflow_engine.get_valid_next_phases("unknown")
        assert valid == []
    
    def test_get_next_phase_single(self, workflow_engine):
        """测试获取单个下一阶段。"""
        next_phase = workflow_engine.get_next_phase("project_init")
        assert next_phase == "requirements_draft"
    
    def test_get_next_phase_multiple(self, workflow_engine):
        """测试获取多个下一阶段。"""
        next_phase = workflow_engine.get_next_phase("requirements_review")
        assert next_phase is None
    
    def test_get_next_phase_completed(self, workflow_engine):
        """测试已完成阶段的下一阶段。"""
        next_phase = workflow_engine.get_next_phase("completed")
        assert next_phase is None
    
    def test_transition_to(self, workflow_engine):
        """测试执行状态转换。"""
        result = workflow_engine.transition_to("requirements_draft")
        
        assert result["from"] == "project_init"
        assert result["to"] == "requirements_draft"
    
    def test_transition_to_invalid(self, workflow_engine):
        """测试执行非法状态转换。"""
        with pytest.raises(IllegalPhaseTransitionError):
            workflow_engine.transition_to("development")
    
    def test_transition_to_preserves_phase(self, workflow_engine):
        """测试非法转换不改变阶段。"""
        current = workflow_engine.state_manager.get_current_phase()
        
        try:
            workflow_engine.transition_to("development")
        except IllegalPhaseTransitionError:
            pass
        
        assert workflow_engine.state_manager.get_current_phase() == current
    
    def test_start_review_requirements(self, workflow_engine):
        """测试发起需求评审。"""
        workflow_engine.transition_to("requirements_draft")
        workflow_engine.start_review("requirements")
        
        phase = workflow_engine.state_manager.get_current_phase()
        assert phase == "requirements_review"
    
    def test_start_review_design(self, workflow_engine):
        """测试发起设计评审。"""
        workflow_engine.state_manager.update_phase("design_draft")
        workflow_engine.start_review("design")
        
        phase = workflow_engine.state_manager.get_current_phase()
        assert phase == "design_review"
    
    def test_start_review_unknown(self, workflow_engine):
        """测试发起未知评审。"""
        with pytest.raises(WorkflowError):
            workflow_engine.start_review("unknown")
    
    def test_approve_stage_requirements(self, workflow_engine):
        """测试批准需求阶段。"""
        workflow_engine.transition_to("requirements_draft")
        workflow_engine.transition_to("requirements_review")
        workflow_engine.state_manager.update_signoff("requirements", "pm", True)
        workflow_engine.state_manager.update_signoff("requirements", "dev", True)
        
        result = workflow_engine.approve_stage("requirements")
        assert result is True
        
        phase = workflow_engine.state_manager.get_current_phase()
        assert phase == "requirements_approved"
    
    def test_approve_stage_design(self, workflow_engine):
        """测试批准设计阶段。"""
        workflow_engine.state_manager.update_phase("design_review")
        workflow_engine.state_manager.update_signoff("design", "pm", True)
        workflow_engine.state_manager.update_signoff("design", "dev", True)
        
        result = workflow_engine.approve_stage("design")
        assert result is True
        
        phase = workflow_engine.state_manager.get_current_phase()
        assert phase == "design_approved"
    
    def test_approve_stage_not_ready(self, workflow_engine):
        """测试未满足条件时批准失败。"""
        workflow_engine.state_manager.update_phase("requirements_review")
        
        result = workflow_engine.approve_stage("requirements")
        assert result is False
    
    def test_approve_stage_unknown(self, workflow_engine):
        """测试批准未知阶段。"""
        with pytest.raises(WorkflowError):
            workflow_engine.approve_stage("unknown")
    
    def test_handle_rejection_requirements(self, workflow_engine):
        """测试处理需求拒签。"""
        workflow_engine.state_manager.update_phase("requirements_review")
        workflow_engine.handle_rejection("requirements_review", "需要修改")
        
        phase = workflow_engine.state_manager.get_current_phase()
        assert phase == "requirements_draft"
    
    def test_handle_rejection_design(self, workflow_engine):
        """测试处理设计拒签。"""
        workflow_engine.state_manager.update_phase("design_review")
        workflow_engine.handle_rejection("design_review", "需要修改")
        
        phase = workflow_engine.state_manager.get_current_phase()
        assert phase == "design_draft"
    
    def test_handle_rejection_unknown(self, workflow_engine):
        """测试处理未知拒签。"""
        with pytest.raises(WorkflowError):
            workflow_engine.handle_rejection("development", "需要修改")
    
    def test_get_phase_progress_valid(self, workflow_engine):
        """测试获取有效阶段进度。"""
        progress = workflow_engine.get_phase_progress("project_init")
        
        assert progress["current_phase"] == "project_init"
        assert progress["progress_percentage"] == 0.0
        assert progress["current_step"] == 1
        assert progress["total_steps"] == 11
        assert "requirements_draft" in progress["remaining_phases"]
    
    def test_get_phase_progress_completed(self, workflow_engine):
        """测试获取已完成阶段进度。"""
        progress = workflow_engine.get_phase_progress("completed")
        
        assert progress["current_phase"] == "completed"
        assert progress["progress_percentage"] == 100.0
        assert progress["current_step"] == 11
        assert progress["total_steps"] == 11
        assert progress["remaining_phases"] == []
    
    def test_get_phase_progress_unknown(self, workflow_engine):
        """测试获取未知阶段进度。"""
        progress = workflow_engine.get_phase_progress("unknown_phase")
        
        assert "error" in progress
    
    def test_is_phase_completed_before(self, workflow_engine):
        """测试当前阶段之前的阶段已完成。"""
        workflow_engine.state_manager.update_phase("development")
        
        assert workflow_engine.is_phase_completed("project_init") is True
        assert workflow_engine.is_phase_completed("requirements_draft") is True
    
    def test_is_phase_completed_current(self, workflow_engine):
        """测试当前阶段未完成。"""
        workflow_engine.state_manager.update_phase("development")
        
        assert workflow_engine.is_phase_completed("development") is False
    
    def test_is_phase_completed_future(self, workflow_engine):
        """测试未来阶段未完成。"""
        workflow_engine.state_manager.update_phase("development")
        
        assert workflow_engine.is_phase_completed("testing") is False
        assert workflow_engine.is_phase_completed("deployment") is False
    
    def test_is_phase_completed_unknown(self, workflow_engine):
        """测试未知阶段返回False。"""
        assert workflow_engine.is_phase_completed("unknown_phase") is False
    
    def test_get_workflow_summary(self, workflow_engine):
        """测试获取工作流摘要。"""
        summary = workflow_engine.get_workflow_summary()
        
        assert "current_phase" in summary
        assert "phase_progress" in summary
        assert "requirements_signoff" in summary
        assert "can_proceed" in summary
    
    def test_transition_with_back(self, workflow_engine):
        """测试可退回的阶段转换。"""
        workflow_engine.state_manager.update_phase("requirements_review")
        
        result = workflow_engine.transition_to("requirements_draft")
        assert result["from"] == "requirements_review"
        assert result["to"] == "requirements_draft"
    
    def test_transition_development_to_testing(self, workflow_engine):
        """测试开发到测试阶段转换。"""
        workflow_engine.state_manager.update_phase("development")
        
        result = workflow_engine.transition_to("testing")
        assert result["to"] == "testing"
    
    def test_full_workflow_path(self, workflow_engine):
        """测试完整工作流路径。"""
        phases = [
            "requirements_draft",
            "requirements_review",
            "requirements_approved",
            "design_draft",
            "design_review",
            "design_approved",
            "development",
            "testing",
            "deployment",
            "completed"
        ]
        
        for phase in phases:
            workflow_engine.transition_to(phase)
        
        assert workflow_engine.state_manager.get_current_phase() == "completed"
    
    def test_review_cycle_increment(self, workflow_engine):
        """测试评审周期递增。"""
        workflow_engine.transition_to("requirements_draft")
        workflow_engine.start_review("requirements")
        
        state = workflow_engine.state_manager.load_state()
        assert state.get('requirements', {}).get('review_cycles', 0) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
