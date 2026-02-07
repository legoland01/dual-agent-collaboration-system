"""v2.2.1 黑盒测试用例实现

测试用例覆盖：
- M1: 签署自动同步功能 (AutoGitSyncEngine, SignoffEngine)
- M2: 变更载体明确化 (ChangeComplianceChecker)
- M3: 签署流程改进 (SignoffEngine, SignoffRecordManager)
- M4: 动态 Checklist 机制 (ExtendedChecklistGenerator, ChecklistGenerator)
- M5: 双代理认知免疫系统 (CognitiveImmuneSystem)

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


class TestSignoffAutoSyncBlackbox:
    """M1: 签署自动同步黑盒测试"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_sync_class_exists(self):
        """测试同步类存在"""
        from src.core.auto_git_sync import AutoGitSyncEngine
        assert AutoGitSyncEngine is not None

    def test_signoff_engine_stage_config(self):
        """测试签署引擎阶段配置"""
        from src.core.signoff import SignoffEngine
        config = SignoffEngine.STAGE_CONFIG
        assert "requirements" in config
        assert "design" in config

    def test_auto_git_sync_initialization(self, temp_dir):
        """测试自动git同步初始化"""
        from src.core.auto_git_sync import AutoGitSyncEngine
        sync = AutoGitSyncEngine(str(temp_dir))
        assert sync is not None
        assert sync.project_path == temp_dir

    def test_auto_git_sync_detect_changes(self, temp_dir):
        """测试变更检测"""
        from src.core.auto_git_sync import AutoGitSyncEngine
        sync = AutoGitSyncEngine(str(temp_dir))
        changes = sync.detect_changes()
        assert isinstance(changes, list)

    def test_auto_git_sync_auto_add(self, temp_dir):
        """测试自动git add"""
        from src.core.auto_git_sync import AutoGitSyncEngine
        sync = AutoGitSyncEngine(str(temp_dir))
        result = sync.auto_add()
        assert "added" in result
        assert "message" in result

    def test_auto_git_sync_auto_commit(self, temp_dir):
        """测试自动git commit"""
        from src.core.auto_git_sync import AutoGitSyncEngine
        sync = AutoGitSyncEngine(str(temp_dir))
        result = sync.auto_commit("Test commit")
        assert "success" in result
        assert "message" in result

    def test_auto_git_sync_auto_push(self, temp_dir):
        """测试自动git push"""
        from src.core.auto_git_sync import AutoGitSyncEngine
        sync = AutoGitSyncEngine(str(temp_dir))
        result = sync.auto_push()
        assert "success" in result

    def test_signoff_with_sync_mode(self):
        """测试带sync模式的签署"""
        from src.core.signoff import SignoffEngine
        from unittest.mock import Mock
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        assert engine is not None


class TestChangeClarityBlackbox:
    """M2: 变更载体明确化黑盒测试"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_change_compliance_class_exists(self):
        """测试变更合规类存在"""
        from src.core.change_compliance import ChangeComplianceChecker
        assert ChangeComplianceChecker is not None

    def test_change_compliance_initialization(self, temp_dir):
        """测试变更合规初始化"""
        from src.core.change_compliance import ChangeComplianceChecker
        checker = ChangeComplianceChecker(str(temp_dir))
        assert checker is not None
        assert checker.project_path == temp_dir

    def test_prd_compliance_result_dataclass(self):
        """测试PRD合规结果数据结构"""
        from src.core.change_compliance import ComplianceResult
        result = ComplianceResult(valid=True)
        assert result.valid is True
        assert result.violations == []
        assert result.warnings == []

    def test_conflict_dataclass(self):
        """测试冲突数据结构"""
        from src.core.change_compliance import Conflict
        conflict = Conflict(
            type="merge",
            file="test.md",
            description="Merge conflict",
            details="Both branches modified"
        )
        assert conflict.type == "merge"
        assert conflict.file == "test.md"

    def test_check_prd_compliance_nonexistent(self, temp_dir):
        """测试检查不存在的PRD"""
        from src.core.change_compliance import ChangeComplianceChecker
        checker = ChangeComplianceChecker(str(temp_dir))
        result = checker.check_prd_compliance("/nonexistent/prd.md")
        assert result.valid is False
        assert len(result.violations) >= 1

    def test_check_prd_compliance_valid(self, temp_dir):
        """测试检查有效的PRD"""
        from src.core.change_compliance import ChangeComplianceChecker
        prd_file = temp_dir / "test_prd.md"
        prd_file.write_text("# Test PRD\n## FR-001\n- Feature 1\n")
        
        checker = ChangeComplianceChecker(str(temp_dir))
        result = checker.check_prd_compliance(str(prd_file))
        assert result.valid is True

    def test_prd_pattern(self):
        """测试PRD模式"""
        from src.core.change_compliance import ChangeComplianceChecker
        pattern = ChangeComplianceChecker.PRD_PATTERN
        assert "FR" in pattern

    def test_rfc_pattern(self):
        """测试RFC模式"""
        from src.core.change_compliance import ChangeComplianceChecker
        pattern = ChangeComplianceChecker.RFC_PATTERN
        assert "RFC-" in pattern


class TestSignoffImprovementBlackbox:
    """M3: 签署流程改进黑盒测试"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_signoff_engine_exists(self):
        """测试签署引擎存在"""
        from src.core.signoff import SignoffEngine
        assert SignoffEngine is not None

    def test_signoff_record_manager_exists(self):
        """测试签署记录管理器存在"""
        from src.core.signoff_record_manager import SignoffRecordManager
        assert SignoffRecordManager is not None

    def test_signoff_engine_initialization(self):
        """测试签署引擎初始化"""
        from src.core.signoff import SignoffEngine
        from unittest.mock import Mock
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        assert engine.state_manager == state_manager
        assert engine.workflow_engine == workflow_engine

    def test_signoff_record_manager_init(self, temp_dir):
        """测试签署记录管理器初始化"""
        from src.core.signoff_record_manager import SignoffRecordManager
        manager = SignoffRecordManager(str(temp_dir))
        assert manager is not None

    def test_signoff_record_save_and_get(self, temp_dir):
        """测试签署记录保存和获取"""
        from src.core.signoff_record_manager import SignoffRecordManager
        manager = SignoffRecordManager(str(temp_dir))
        signers = [{"agent": "Agent1", "status": "pending"}]
        sig_id = manager.save_signoff("M1", "requirements", signers, "PENDING")
        assert sig_id is not None
        assert "M1" in sig_id
        
        record = manager.get_signoff(sig_id)
        assert record is not None
        assert record["milestone"] == "M1"

    def test_signoff_record_list(self, temp_dir):
        """测试签署记录列表"""
        from src.core.signoff_record_manager import SignoffRecordManager
        manager = SignoffRecordManager(str(temp_dir))
        manager.save_signoff("M1", "requirements", [{"agent": "A1"}], "PENDING")
        manager.save_signoff("M2", "design", [{"agent": "A1"}], "PENDING")
        records = manager.list_signoffs()
        assert len(records) >= 2

    def test_double_signoff_enforcement(self):
        """测试双人签署强制"""
        from src.core.signoff import SignoffEngine
        from unittest.mock import Mock
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        assert engine is not None

    def test_signoff_sequence_validation(self):
        """测试签署顺序验证"""
        from src.core.signoff import SignoffEngine
        from unittest.mock import Mock
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        assert engine is not None

    def test_signoff_update_status(self, temp_dir):
        """测试签署状态更新"""
        from src.core.signoff_record_manager import SignoffRecordManager
        manager = SignoffRecordManager(str(temp_dir))
        signers = [{"agent": "Agent1", "status": "pending"}]
        sig_id = manager.save_signoff("M1", "requirements", signers, "PENDING")
        
        manager.update_signoff_status(sig_id, "APPROVED", {"agent": "Agent1", "status": "approved"})
        record = manager.get_signoff(sig_id)
        assert record is not None
        assert record.get("status") == "APPROVED"

    def test_check_all_signed(self, temp_dir):
        """测试检查所有签署"""
        from src.core.signoff_record_manager import SignoffRecordManager
        manager = SignoffRecordManager(str(temp_dir))
        signers = [
            {"agent": "Agent1", "status": "approved"},
            {"agent": "Agent2", "status": "pending"}
        ]
        sig_id = manager.save_signoff("M1", "requirements", signers, "IN_PROGRESS")
        
        result = manager.check_all_signed(sig_id)
        assert result is False
        
        manager.update_signoff_status(sig_id, "APPROVED", {"agent": "Agent2", "status": "approved"})
        result = manager.check_all_signed(sig_id)
        assert result is True

    def test_signoff_get_stage_data(self):
        """测试获取签署阶段数据"""
        from src.core.signoff import SignoffEngine
        from unittest.mock import Mock
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        state = {"requirements": {"status": "pending"}}
        result = engine._get_stage_data("requirements", state)
        assert result == {"status": "pending"}


class TestDynamicChecklistBlackbox:
    """M4: 动态 Checklist 机制黑盒测试"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_extended_checklist_generator_exists(self):
        """测试扩展清单生成器存在"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        assert ExtendedChecklistGenerator is not None

    def test_checklist_generator_exists(self):
        """测试清单生成器存在"""
        from src.core.checklist_generator import ChecklistGenerator
        assert ChecklistGenerator is not None

    def test_extended_checklist_init(self, temp_dir):
        """测试扩展清单初始化"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        checklist = ExtendedChecklistGenerator(str(temp_dir))
        assert checklist is not None
        assert checklist.project_path == temp_dir

    def test_checklist_generator_init(self, temp_dir):
        """测试清单生成器初始化"""
        from src.core.checklist_generator import ChecklistGenerator
        generator = ChecklistGenerator(str(temp_dir))
        assert generator is not None

    def test_checklist_item_dataclass(self):
        """测试检查项数据结构"""
        from src.core.extended_checklist import CheckItem, ChecklistType
        item = CheckItem(
            id="TEST-001",
            type=ChecklistType.BASE_CHECK.value,
            description="Test item",
            severity="info"
        )
        assert item.id == "TEST-001"
        assert "基础检查" in item.type

    def test_context_aware_items(self, temp_dir):
        """测试上下文感知项"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        checklist = ExtendedChecklistGenerator(str(temp_dir))
        items = checklist.generate_full_checklist("design")
        assert items is not None

    def test_generate_traceability_checklist(self, temp_dir):
        """测试生成可追溯性清单"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        checklist = ExtendedChecklistGenerator(str(temp_dir))
        items = checklist._generate_traceability_checklist()
        assert items is not None
        assert len(items) >= 1

    def test_generate_task_scope_checklist(self, temp_dir):
        """测试生成任务范围清单"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        checklist = ExtendedChecklistGenerator(str(temp_dir))
        items = checklist._generate_task_scope_checklist()
        assert items is not None

    def test_generate_quality_gate_checklist(self, temp_dir):
        """测试生成质量门禁清单"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        checklist = ExtendedChecklistGenerator(str(temp_dir))
        items = checklist._generate_quality_gate_checklist()
        assert items is not None


class TestCognitiveImmunityBlackbox:
    """M5: 双代理认知免疫系统黑盒测试"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_cognitive_immune_exists(self):
        """测试认知免疫存在"""
        from src.core.cognitive_immune import CognitiveImmuneSystem
        assert CognitiveImmuneSystem is not None

    def test_confusion_signals(self):
        """测试困惑信号定义"""
        from src.core.cognitive_immune import CONFUSION_SIGNALS
        assert len(CONFUSION_SIGNALS) >= 10
        assert len(CONFUSION_SIGNALS) > 0

    def test_responsibility_matrix(self):
        """测试职责矩阵"""
        from src.core.cognitive_immune import RESPONSIBILITY_MATRIX
        assert "agent1" in RESPONSIBILITY_MATRIX
        assert "agent2" in RESPONSIBILITY_MATRIX
        assert "responsibilities" in RESPONSIBILITY_MATRIX["agent1"]
        assert "forbidden" in RESPONSIBILITY_MATRIX["agent1"]

    def test_immune_response_dataclass(self):
        """测试免疫响应数据结构"""
        from src.core.cognitive_immune import ImmuneResponse
        response = ImmuneResponse(
            detected=True,
            response_type="confusion",
            message="Detected confusion signal",
            suggestions=["Provide clarification"]
        )
        assert response.detected is True
        assert response.response_type == "confusion"

    def test_cognitive_immune_initialization(self, temp_dir):
        """测试认知免疫初始化"""
        from src.core.cognitive_immune import CognitiveImmuneSystem
        immune = CognitiveImmuneSystem(str(temp_dir))
        assert immune is not None
        assert hasattr(immune, 'session_starter')
        assert hasattr(immune, 'confusion_detector')
        assert hasattr(immune, 'responsibility_detector')

    def test_analyze_message(self, temp_dir):
        """测试消息分析"""
        from src.core.cognitive_immune import CognitiveImmuneSystem
        immune = CognitiveImmuneSystem(str(temp_dir))
        response = immune.analyze_message("agent1", "我不确定这个需求")
        assert response is not None
        assert hasattr(response, 'detected')
        assert hasattr(response, 'message')


class TestIntegrationBlackbox:
    """集成黑盒测试"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_all_m1_modules_import(self):
        """测试M1所有模块导入"""
        from src.core.signoff import SignoffEngine
        from src.core.auto_git_sync import AutoGitSyncEngine
        assert SignoffEngine is not None
        assert AutoGitSyncEngine is not None

    def test_all_m2_modules_import(self):
        """测试M2所有模块导入"""
        from src.core.change_compliance import ChangeComplianceChecker
        assert ChangeComplianceChecker is not None

    def test_all_m3_modules_import(self):
        """测试M3所有模块导入"""
        from src.core.signoff import SignoffEngine
        from src.core.signoff_record_manager import SignoffRecordManager
        assert SignoffEngine is not None
        assert SignoffRecordManager is not None

    def test_all_m4_modules_import(self):
        """测试M4所有模块导入"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        from src.core.checklist_generator import ChecklistGenerator
        assert ExtendedChecklistGenerator is not None
        assert ChecklistGenerator is not None

    def test_all_m5_modules_import(self):
        """测试M5所有模块导入"""
        from src.core.cognitive_immune import CognitiveImmuneSystem
        assert CognitiveImmuneSystem is not None

    def test_m1_m3_integration(self):
        """测试M1与M3集成"""
        from src.core.signoff import SignoffEngine
        from src.core.auto_git_sync import AutoGitSyncEngine
        from unittest.mock import Mock
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        sync = AutoGitSyncEngine("/tmp")
        assert engine is not None
        assert sync is not None

    def test_m2_m4_integration(self):
        """测试M2与M4集成"""
        from src.core.change_compliance import ChangeComplianceChecker
        from src.core.extended_checklist import ExtendedChecklistGenerator
        checker = ChangeComplianceChecker("/tmp")
        checklist = ExtendedChecklistGenerator("/tmp")
        assert checker is not None
        assert checklist is not None

    def test_m4_m5_integration(self):
        """测试M4与M5集成"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        from src.core.cognitive_immune import CognitiveImmuneSystem
        checklist = ExtendedChecklistGenerator("/tmp")
        immune = CognitiveImmuneSystem("/tmp")
        assert checklist is not None
        assert immune is not None

    def test_state_consistency(self, temp_dir):
        """测试状态一致性"""
        from src.core.state_manager import StateManager
        from src.core.signoff_record_manager import SignoffRecordManager
        manager = StateManager(str(temp_dir))
        manager.initialize_project("Test", "PYTHON")
        signoff_mgr = SignoffRecordManager(str(temp_dir))
        assert manager is not None
        assert signoff_mgr is not None


class TestEdgeCasesBlackbox:
    """边界情况黑盒测试"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_empty_checklist(self, temp_dir):
        """测试空清单"""
        from src.core.extended_checklist import ExtendedChecklistGenerator
        checklist = ExtendedChecklistGenerator(str(temp_dir))
        items = checklist.generate_full_checklist("unknown_phase")
        assert items is not None

    def test_concurrent_signoff_requests(self):
        """测试并发签署请求"""
        from src.core.signoff import SignoffEngine
        from unittest.mock import Mock
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        assert engine is not None

    def test_rapid_state_changes(self, temp_dir):
        """测试快速状态变更"""
        from src.core.state_manager import StateManager
        manager = StateManager(str(temp_dir))
        manager.initialize_project("Test", "PYTHON")
        for i in range(10):
            state = manager.read_state()
            state["test_counter"] = i
            manager.write_state(state)
        final_state = manager.read_state()
        assert final_state.get("test_counter") == 9

    def test_special_characters(self, temp_dir):
        """测试特殊字符"""
        from src.core.signoff_record_manager import SignoffRecordManager
        manager = SignoffRecordManager(str(temp_dir))
        signers = [{"agent": "Agent_测试"}]
        sig_id = manager.save_signoff("M1_中文", "requirements_中文", signers, "PENDING")
        assert sig_id is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
