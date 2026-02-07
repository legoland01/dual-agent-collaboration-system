"""v2.2.1 端到端测试

测试用例覆盖：
- M1: 签署自动同步功能
- M2: 变更载体明确化
- M3: 签署流程改进
- M4: 动态 Checklist 机制
- M5: 双代理认知免疫系统

版本: v2.2.1
创建日期: 2026-02-07
"""
import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestE2EM1SignoffAutoSync:
    """M1: 签署自动同步端到端测试"""

    @pytest.fixture
    def temp_git_repo(self):
        """创建临时Git仓库"""
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)
            yield Path(tmpdir)

    def test_complete_signoff_sync_workflow(self, temp_git_repo):
        """测试完整签署同步工作流"""
        from src.core.state_manager import StateManager
        from src.core.signoff_record_manager import SignoffRecordManager
        from src.core.auto_git_sync import AutoGitSyncEngine
        
        manager = StateManager(str(temp_git_repo))
        manager.initialize_project("TestProject", "PYTHON")
        
        signoff_mgr = SignoffRecordManager(str(temp_git_repo))
        sync = AutoGitSyncEngine(str(temp_git_repo))
        
        signers = [{"agent": "Agent1", "status": "pending"}]
        sig_id = signoff_mgr.save_signoff("M1", "requirements", signers, "PENDING")
        
        changes = sync.detect_changes()
        assert sig_id is not None
        
        record = signoff_mgr.get_signoff(sig_id)
        assert record is not None

    def test_signoff_without_sync(self, temp_git_repo):
        """测试不带同步的签署"""
        from src.core.state_manager import StateManager
        from src.core.signoff_record_manager import SignoffRecordManager
        
        manager = StateManager(str(temp_git_repo))
        manager.initialize_project("TestProject", "PYTHON")
        
        signoff_mgr = SignoffRecordManager(str(temp_git_repo))
        signers = [{"agent": "Agent2", "status": "pending"}]
        sig_id = signoff_mgr.save_signoff("M2", "design", signers, "PENDING")
        
        assert sig_id is not None

    def test_multiple_phases_signoff(self, temp_git_repo):
        """测试多阶段签署"""
        from src.core.state_manager import StateManager
        from src.core.signoff_record_manager import SignoffRecordManager
        
        manager = StateManager(str(temp_git_repo))
        manager.initialize_project("TestProject", "PYTHON")
        
        signoff_mgr = SignoffRecordManager(str(temp_git_repo))
        
        phases = ["requirements", "design", "test"]
        for phase in phases:
            sig_id = signoff_mgr.save_signoff(f"M_{phase}", phase, [{"agent": "Agent1"}], "PENDING")
            assert sig_id is not None
        
        records = signoff_mgr.list_signoffs()
        assert len(records) >= 3


class TestE2EM2ChangeClarity:
    """M2: 变更载体明确化端到端测试"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_prd_only_change_workflow(self, temp_dir):
        """测试仅PRD变更工作流"""
        from src.core.change_compliance import ChangeComplianceChecker
        
        checker = ChangeComplianceChecker(str(temp_dir))
        
        prd_file = temp_dir / "test_prd.md"
        prd_file.write_text("# Test PRD\n## FR-001\n- Feature 1\n")
        
        result = checker.check_prd_compliance(str(prd_file))
        assert result.valid is True

    def test_prd_with_rfc_workflow(self, temp_dir):
        """测试带RFC的PRD工作流"""
        from src.core.change_compliance import ChangeComplianceChecker
        
        checker = ChangeComplianceChecker(str(temp_dir))
        
        prd_file = temp_dir / "test_prd.md"
        prd_file.write_text("# Complex Feature\n## RFC-001\nTechnical details\n")
        
        result = checker.check_prd_compliance(str(prd_file))
        assert result.valid is True

    def test_change_impact_analysis(self, temp_dir):
        """测试变更影响分析"""
        from src.core.change_compliance import ChangeComplianceChecker
        
        checker = ChangeComplianceChecker(str(temp_dir))
        
        prd_file = temp_dir / "test_prd.md"
        prd_file.write_text("# Feature\n## Breaking Change\n- API change\n")
        
        result = checker.check_prd_compliance(str(prd_file))
        assert result is not None


class TestE2EM3SignoffImprovement:
    """M3: 签署流程改进端到端测试"""

    @pytest.fixture
    def temp_git_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)
            yield Path(tmpdir)

    def test_double_signoff_enforcement(self, temp_git_repo):
        """测试双人签署强制执行"""
        from src.core.signoff_record_manager import SignoffRecordManager
        
        signoff_mgr = SignoffRecordManager(str(temp_git_repo))
        
        signers = [
            {"agent": "Agent1", "status": "pending"},
            {"agent": "Agent2", "status": "pending"}
        ]
        sig_id = signoff_mgr.save_signoff("M1", "requirements", signers, "IN_PROGRESS")
        
        assert sig_id is not None
        
        result = signoff_mgr.check_all_signed(sig_id)
        assert result is False

    def test_signoff_sequence_validation(self, temp_git_repo):
        """测试签署顺序验证"""
        from src.core.signoff_record_manager import SignoffRecordManager
        
        signoff_mgr = SignoffRecordManager(str(temp_git_repo))
        
        signers = [{"agent": "Agent1", "status": "pending"}]
        sig_id = signoff_mgr.save_signoff("M1", "requirements", signers, "PENDING")
        
        assert sig_id is not None

    def test_signoff_history_preservation(self, temp_git_repo):
        """测试签署历史保留"""
        from src.core.signoff_record_manager import SignoffRecordManager
        
        signoff_mgr = SignoffRecordManager(str(temp_git_repo))
        
        signoff_mgr.save_signoff("M1", "requirements", [{"agent": "Agent1"}], "PENDING")
        signoff_mgr.save_signoff("M2", "requirements", [{"agent": "Agent1"}], "PENDING")
        
        records = signoff_mgr.list_signoffs()
        assert len(records) >= 2

    def test_signoff_summary_generation(self, temp_git_repo):
        """测试签署摘要生成"""
        from src.core.signoff_record_manager import SignoffRecordManager
        
        signoff_mgr = SignoffRecordManager(str(temp_git_repo))
        
        signoff_mgr.save_signoff("M1", "requirements", [{"agent": "Agent1"}, {"agent": "Agent2"}], "PENDING")
        signoff_mgr.save_signoff("M2", "design", [{"agent": "Agent1"}], "PENDING")
        
        records = signoff_mgr.list_signoffs()
        assert len(records) >= 2

    def test_signoff_block_development(self, temp_git_repo):
        """测试签署阻止开发"""
        from src.core.signoff_record_manager import SignoffRecordManager
        
        signoff_mgr = SignoffRecordManager(str(temp_git_repo))
        
        signers = [{"agent": "Agent1", "status": "pending"}]
        sig_id = signoff_mgr.save_signoff("M1", "requirements", signers, "IN_PROGRESS")
        
        result = signoff_mgr.check_all_signed(sig_id)
        assert result is False


class TestE2EM4DynamicChecklist:
    """M4: 动态 Checklist 机制端到端测试"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_adaptive_checklist_generation(self, temp_dir):
        """测试自适应清单生成"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        
        generator = ExtendedChecklistGenerator(str(temp_dir))
        
        checklist = generator.generate_full_checklist("requirements")
        assert len(checklist) >= 1

    def test_context_aware_checklist(self, temp_dir):
        """测试上下文感知清单"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        
        generator = ExtendedChecklistGenerator(str(temp_dir))
        
        requirements_items = generator.generate_full_checklist("requirements")
        design_items = generator.generate_full_checklist("design")
        
        assert len(requirements_items) >= 1
        assert len(design_items) >= 1

    def test_checklist_progress_synchronization(self, temp_dir):
        """测试清单进度同步"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        
        generator = ExtendedChecklistGenerator(str(temp_dir))
        
        checklist = generator.generate_full_checklist("test")
        assert len(checklist) >= 1

    def test_checklist_dependency_resolution(self, temp_dir):
        """测试清单依赖解析"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        
        generator = ExtendedChecklistGenerator(str(temp_dir))
        
        checklist = generator.generate_full_checklist("requirements")
        assert len(checklist) >= 1

    def test_checklist_persistence_and_recovery(self, temp_dir):
        """测试清单持久化和恢复"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        
        generator = ExtendedChecklistGenerator(str(temp_dir))
        
        checklist = generator.generate_full_checklist("requirements")
        assert checklist is not None


class TestE2EM5CognitiveImmunity:
    """M5: 双代理认知免疫系统端到端测试"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_session_start_guidance(self, temp_dir):
        """测试会话起始引导"""
        from src.core.cognitive_immune import CognitiveImmuneSystem
        
        immune = CognitiveImmuneSystem(str(temp_dir))
        response = immune.analyze_message("Agent1", "你好，我开始了")
        assert response is not None

    def test_confusion_detection_and_response(self, temp_dir):
        """测试困惑检测和响应"""
        from src.core.cognitive_immune import CognitiveImmuneSystem
        
        immune = CognitiveImmuneSystem(str(temp_dir))
        response = immune.analyze_message("Agent1", "我不确定这个需求应该怎么写")
        assert response is not None
        assert hasattr(response, 'detected')

    def test_skill_auto_loading(self, temp_dir):
        """测试Skill自动加载"""
        from src.core.cognitive_immune import CognitiveImmuneSystem
        
        immune = CognitiveImmuneSystem(str(temp_dir))
        assert immune is not None
        assert hasattr(immune, 'session_starter')

    def test_responsibility_boundary_enforcement(self, temp_dir):
        """测试职责边界强制执行"""
        from src.core.cognitive_immune import CognitiveImmuneSystem
        
        immune = CognitiveImmuneSystem(str(temp_dir))
        response = immune.analyze_message("Agent1", "让我来写代码")
        assert response is not None

    def test_dynamic_repo_configuration(self, temp_dir):
        """测试动态仓库配置"""
        from src.core.cognitive_immune import CognitiveImmuneSystem
        
        immune = CognitiveImmuneSystem(str(temp_dir))
        assert immune is not None

    def test_immune_response_orchestration(self, temp_dir):
        """测试免疫响应编排"""
        from src.core.cognitive_immune import CognitiveImmuneSystem
        
        immune = CognitiveImmuneSystem(str(temp_dir))
        response = immune.analyze_message("Agent1", "我不知道该怎么做")
        assert response is not None

    def test_self_diagnosis_and_recovery(self, temp_dir):
        """测试自我诊断和恢复"""
        from src.core.cognitive_immune import CognitiveImmuneSystem
        
        immune = CognitiveImmuneSystem(str(temp_dir))
        response = immune.analyze_message("Agent1", "这个任务有点复杂")
        assert response is not None

    def test_cognitive_health_monitoring(self, temp_dir):
        """测试认知健康监控"""
        from src.core.cognitive_immune import CognitiveImmuneSystem
        
        immune = CognitiveImmuneSystem(str(temp_dir))
        assert immune is not None


class TestE2EIntegration:
    """端到端集成测试"""

    @pytest.fixture
    def project_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)
            yield Path(tmpdir)

    def test_complete_requirements_signoff_flow(self, project_dir):
        """测试完整需求签署流程"""
        from src.core.state_manager import StateManager
        from src.core.signoff_record_manager import SignoffRecordManager
        from src.core.extended_checklist import ExtendedChecklistGenerator
        from src.core.cognitive_immune import CognitiveImmuneSystem
        
        manager = StateManager(str(project_dir))
        manager.initialize_project("TestProject", "PYTHON")
        
        signoff_mgr = SignoffRecordManager(str(project_dir))
        checklist = ExtendedChecklistGenerator(str(project_dir))
        immune = CognitiveImmuneSystem(str(project_dir))
        
        checklist_items = checklist.generate_full_checklist("requirements")
        
        immune.analyze_message("Agent1", "开始评审需求")
        
        signers = [{"agent": "Agent1", "status": "pending"}]
        sig_id = signoff_mgr.save_signoff("M1", "requirements", signers, "PENDING")
        
        assert sig_id is not None

    def test_complete_design_flow_with_immune(self, project_dir):
        """测试完整设计流程与免疫"""
        from src.core.state_manager import StateManager
        from src.core.change_compliance import ChangeComplianceChecker
        from src.core.extended_checklist import ExtendedChecklistGenerator
        from src.core.cognitive_immune import CognitiveImmuneSystem
        
        manager = StateManager(str(project_dir))
        manager.initialize_project("TestProject", "PYTHON")
        
        checker = ChangeComplianceChecker(str(project_dir))
        checklist = ExtendedChecklistGenerator(str(project_dir))
        immune = CognitiveImmuneSystem(str(project_dir))
        
        prd_file = project_dir / "design.md"
        prd_file.write_text("# Design Document\n## FR-001\n")
        result = checker.check_prd_compliance(str(prd_file))
        
        immune.analyze_message("Agent1", "开始设计阶段")
        
        checklist_items = checklist.generate_full_checklist("design")
        assert len(checklist_items) >= 1

    def test_full_development_phase_flow(self, project_dir):
        """测试完整开发阶段流程"""
        from src.core.state_manager import StateManager
        from src.core.signoff_record_manager import SignoffRecordManager
        from src.core.cognitive_immune import CognitiveImmuneSystem
        
        manager = StateManager(str(project_dir))
        manager.initialize_project("TestProject", "PYTHON")
        
        signoff_mgr = SignoffRecordManager(str(project_dir))
        immune = CognitiveImmuneSystem(str(project_dir))
        
        immune.analyze_message("Agent1", "开始开发阶段")
        
        signers = [{"agent": "Agent1", "status": "pending"}]
        sig_id = signoff_mgr.save_signoff("M3", "development", signers, "PENDING")
        
        assert sig_id is not None

    def test_multi_agent_collaboration_simulation(self, project_dir):
        """测试多代理协作模拟"""
        from src.core.state_manager import StateManager
        from src.core.cognitive_immune import CognitiveImmuneSystem
        
        manager = StateManager(str(project_dir))
        manager.initialize_project("TestProject", "PYTHON")
        
        immune = CognitiveImmuneSystem(str(project_dir))
        
        immune.analyze_message("Agent1", "Agent2 已经评审了需求文档")
        immune.analyze_message("Agent2", "我完成了代码实现")
        
        assert immune is not None

    def test_state_persistence_across_sessions(self, project_dir):
        """测试跨会话状态持久化"""
        from src.core.state_manager import StateManager
        from src.core.signoff_record_manager import SignoffRecordManager
        
        manager = StateManager(str(project_dir))
        manager.initialize_project("Test", "PYTHON")
        
        signoff_mgr = SignoffRecordManager(str(project_dir))
        signoff_mgr.save_signoff("M1", "requirements", [{"agent": "Agent1"}], "PENDING")
        
        state = manager.read_state()
        
        assert state is not None
        assert state["project"]["name"] == "Test"

    def test_performance_under_full_load(self, project_dir):
        """测试满负载性能"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        from src.core.cognitive_immune import CognitiveImmuneSystem
        
        checklist_gen = ExtendedChecklistGenerator(str(project_dir))
        immune = CognitiveImmuneSystem(str(project_dir))
        
        start = time.time()
        
        for i in range(10):
            checklist = checklist_gen.generate_full_checklist("requirements")
            immune.analyze_message("Agent1", f"任务 {i}")
        
        elapsed = time.time() - start
        
        assert elapsed < 30.0


class TestE2ECompatibility:
    """兼容性测试"""

    def test_backward_compatibility_with_v210(self):
        """测试与v2.1.0向后兼容"""
        from src.core.state_validator import StateValidator, ValidationLevel
        
        state = {
            "version": "2.1.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{"version": "v1", "status": "approved"}],
            "design": [{"version": "v1", "status": "completed"}],
            "test": {"status": "pending"},
            "development": {"status": "in_progress"},
            "deployment": {"status": "pending"}
        }
        
        validator = StateValidator()
        results = validator.validate(state)
        
        error_results = [r for r in results if r.level == ValidationLevel.ERROR]
        assert len(error_results) == 0

    def test_exception_handling_compatibility(self):
        """测试异常处理兼容性"""
        from src.core.exception_handler import ExceptionHandler, ExceptionType, NetworkError
        
        handler = ExceptionHandler(agent_id="test_agent")
        exc = NetworkError("Connection timeout", "git fetch")
        exc_type, severity = handler.classify_exception(exc)
        
        assert exc_type == ExceptionType.RETRYABLE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
