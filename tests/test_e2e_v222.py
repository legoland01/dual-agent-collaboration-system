"""v2.2.2 端到端测试

测试用例覆盖：
- F-PROC-001: 协作规范强制执行
- F-GIT-001: Git 同步集成

版本: v2.2.2
创建日期: 2026-02-08
"""

import pytest
import tempfile
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestE2EGitSyncIntegration:
    """F-GIT-001: Git 同步集成端到端测试"""

    @pytest.fixture
    def temp_git_repo(self):
        """创建临时Git仓库"""
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)
            yield Path(tmpdir)

    def test_git_sync_integrator_init(self, temp_git_repo):
        """GitSyncIntegrator 初始化"""
        from src.core.git_sync_integrator import GitSyncIntegrator
        integrator = GitSyncIntegrator(str(temp_git_repo))
        assert integrator is not None

    def test_detect_changes_empty(self, temp_git_repo):
        """检测无变更"""
        from src.core.git_sync_integrator import GitSyncIntegrator
        integrator = GitSyncIntegrator(str(temp_git_repo))
        changes = integrator.detect_changes()
        assert len(changes) == 0

    def test_detect_changes(self, temp_git_repo):
        """检测变更"""
        from src.core.git_sync_integrator import GitSyncIntegrator
        integrator = GitSyncIntegrator(str(temp_git_repo))
        test_file = temp_git_repo / "test.txt"
        test_file.write_text("test content")
        changes = integrator.detect_changes()
        assert len(changes) > 0

    def test_auto_add(self, temp_git_repo):
        """自动添加"""
        from src.core.git_sync_integrator import GitSyncIntegrator
        integrator = GitSyncIntegrator(str(temp_git_repo))
        test_file = temp_git_repo / "test.txt"
        test_file.write_text("test content")
        result = integrator.auto_add()
        assert result.success is True

    def test_sync_state(self, temp_git_repo):
        """同步状态"""
        from src.core.git_sync_integrator import GitSyncIntegrator
        integrator = GitSyncIntegrator(str(temp_git_repo))
        state_file = temp_git_repo / "state/test.yaml"
        state_file.parent.mkdir(exist_ok=True)
        state_file.write_text("test: modified")
        result = integrator.sync_state()
        assert result is not None

    def test_check_unsynced(self, temp_git_repo):
        """检查未同步"""
        from src.core.git_sync_integrator import GitSyncIntegrator
        integrator = GitSyncIntegrator(str(temp_git_repo))
        test_file = temp_git_repo / "unsynced.txt"
        test_file.write_text("unsynced content")
        unsynced = integrator.check_unsynced()
        assert len(unsynced) > 0

    def test_warn_unsynced_with_changes(self, temp_git_repo):
        """未同步警告"""
        from src.core.git_sync_integrator import GitSyncIntegrator
        integrator = GitSyncIntegrator(str(temp_git_repo))
        test_file = temp_git_repo / "unsynced.txt"
        test_file.write_text("unsynced content")
        warning = integrator.warn_unsynced()
        assert warning is not None


class TestE2EDocumentStateBinder:
    """文档状态绑定测试"""

    @pytest.fixture
    def temp_project(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "state").mkdir(exist_ok=True)
            yield Path(tmpdir)

    def test_document_state_binder_init(self, temp_project):
        """DocumentStateBinder 初始化"""
        from src.core.document_state_binder import DocumentStateBinder
        binder = DocumentStateBinder(str(temp_project))
        assert binder is not None

    def test_get_doc_state_new(self, temp_project):
        """获取新文档状态"""
        from src.core.document_state_binder import DocumentStateBinder
        binder = DocumentStateBinder(str(temp_project))
        state = binder.get_doc_state("test.md")
        assert state == "DRAFT"

    def test_can_review_draft(self, temp_project):
        """DRAFT 状态不可评审"""
        from src.core.document_state_binder import DocumentStateBinder
        binder = DocumentStateBinder(str(temp_project))
        can_review = binder.can_review("test.md", "agent1")
        assert can_review is False


class TestE2ECompletenessGate:
    """完整性门禁测试"""

    @pytest.fixture
    def temp_project(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_completeness_gate_init(self, temp_project):
        """CompletenessGate 初始化"""
        from src.core.completeness_gate import CompletenessGate
        gate = CompletenessGate(str(temp_project))
        assert gate is not None

    def test_main_doc_patterns(self, temp_project):
        """主文档识别"""
        from src.core.completeness_gate import CompletenessGate
        gate = CompletenessGate(str(temp_project))
        assert gate.is_main_doc("requirements_v2.2.2.md") is True
        assert gate.is_main_doc("F-PROC-001.md") is False

    def test_section_only_detection(self, temp_project):
        """部分评审检测"""
        from src.core.completeness_gate import CompletenessGate
        gate = CompletenessGate(str(temp_project))
        assert gate.is_section_only("--section-only \"第2章\"") is True


class TestE2ERoleBoundaryChecker:
    """角色边界检查测试"""

    @pytest.fixture
    def temp_project(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_role_boundary_checker_init(self, temp_project):
        """RoleBoundaryChecker 初始化"""
        from src.core.role_boundary_checker import RoleBoundaryChecker
        checker = RoleBoundaryChecker(str(temp_project))
        assert checker is not None
        assert checker.permissions is not None

    def test_is_denied_dir(self, temp_project):
        """路径拒绝检查"""
        from src.core.role_boundary_checker import RoleBoundaryChecker
        checker = RoleBoundaryChecker(str(temp_project))
        # Agent1 不能操作 design 目录
        result = checker.is_denied_dir("agent1", "docs/02-design/test.md")
        assert result is True


class TestE2EComplianceEngine:
    """合规引擎测试"""

    @pytest.fixture
    def temp_project(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_compliance_engine_init(self, temp_project):
        """合规引擎初始化"""
        from src.core.compliance_engine import ComplianceEngine
        engine = ComplianceEngine(str(temp_project))
        assert engine is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
