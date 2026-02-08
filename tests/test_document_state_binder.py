"""测试文档状态绑定器 - v2.2.2 F-PROC-001.2"""
import pytest
import tempfile
import shutil
from pathlib import Path

from src.core.document_state_binder import DocumentStateBinder
from src.core.compliance_engine import ComplianceResultType


@pytest.fixture
def temp_project():
    """创建临时项目目录"""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture
def binder(temp_project):
    """创建文档状态绑定器"""
    return DocumentStateBinder(str(temp_project))


class TestDocumentStateBinder:
    """文档状态绑定器测试"""

    def test_init_creates_states_file(self, temp_project):
        """测试初始化创建状态文件"""
        binder = DocumentStateBinder(str(temp_project))
        assert (temp_project / "state" / "document_states.yaml").exists()

    def test_default_state_is_draft(self, temp_project):
        """测试默认状态为 DRAFT"""
        binder = DocumentStateBinder(str(temp_project))
        state = binder.get_doc_state("docs/test.md")
        assert state == "DRAFT"

    def test_draft_agent1_can_edit(self, temp_project):
        """测试 DRAFT 状态下 Agent1 可以编辑"""
        binder = DocumentStateBinder(str(temp_project))
        result = binder.check("edit", "docs/test.md", "agent1")
        assert result.result_type == ComplianceResultType.PASSED

    def test_draft_agent2_cannot_edit(self, temp_project):
        """测试 DRAFT 状态下 Agent2 不能编辑"""
        binder = DocumentStateBinder(str(temp_project))
        result = binder.check("edit", "docs/test.md", "agent2")
        assert result.result_type == ComplianceResultType.DENIED

    def test_draft_agent1_can_submit_review(self, temp_project):
        """测试 DRAFT 状态下 Agent1 可以提交评审"""
        binder = DocumentStateBinder(str(temp_project))
        result = binder.check("submit_review", "docs/test.md", "agent1")
        assert result.result_type == ComplianceResultType.PASSED

    def test_review_pending_agent2_can_review(self, temp_project):
        """测试 REVIEW_PENDING 状态下 Agent2 可以评审"""
        binder = DocumentStateBinder(str(temp_project))
        binder.set_state("docs/test.md", "REVIEW_PENDING", "agent1")
        result = binder.check("review", "docs/test.md", "agent2")
        assert result.result_type == ComplianceResultType.PASSED

    def test_reviewed_agent1_can_confirm(self, temp_project):
        """测试 REVIEWED 状态下 Agent1 可以确认"""
        binder = DocumentStateBinder(str(temp_project))
        binder.set_state("docs/test.md", "DRAFT", "agent1")
        binder.set_state("docs/test.md", "REVIEW_PENDING", "agent1")
        binder.set_state("docs/test.md", "REVIEWED", "agent2")
        result = binder.check("confirm", "docs/test.md", "agent1")
        assert result.result_type == ComplianceResultType.PASSED

    def test_archived_cannot_edit(self, temp_project):
        """测试 ARCHIVED 状态下不能编辑"""
        binder = DocumentStateBinder(str(temp_project))
        binder.set_state("docs/test.md", "DRAFT", "agent1")
        binder.set_state("docs/test.md", "REVIEW_PENDING", "agent1")
        binder.set_state("docs/test.md", "REVIEWED", "agent2")
        binder.set_state("docs/test.md", "APPROVED", "agent1")
        binder.set_state("docs/test.md", "ARCHIVED", "agent1")
        result = binder.check("edit", "docs/test.md", "agent1")
        assert result.result_type == ComplianceResultType.DENIED
        assert "已归档" in result.message

    def test_invalid_state_transition_fails(self, temp_project):
        """测试无效状态转换失败"""
        binder = DocumentStateBinder(str(temp_project))
        binder.set_state("docs/test.md", "DRAFT", "agent1")
        result = binder.set_state("docs/test.md", "APPROVED", "agent1")
        assert result is False

    def test_valid_state_transition_succeeds(self, temp_project):
        """测试有效状态转换成功"""
        binder = DocumentStateBinder(str(temp_project))
        binder.set_state("docs/test.md", "DRAFT", "agent1")
        result = binder.set_state("docs/test.md", "REVIEW_PENDING", "agent1")
        assert result is True

    def test_can_review(self, temp_project):
        """测试是否可以评审"""
        binder = DocumentStateBinder(str(temp_project))
        binder.set_state("docs/test.md", "REVIEW_PENDING", "agent1")
        assert binder.can_review("docs/test.md", "agent2") is True

    def test_can_edit(self, temp_project):
        """测试是否可以编辑"""
        binder = DocumentStateBinder(str(temp_project))
        assert binder.can_edit("docs/test.md", "agent1") is True

    def test_get_all_states(self, temp_project):
        """测试获取所有状态"""
        binder = DocumentStateBinder(str(temp_project))
        binder.set_state("docs/test2.md", "REVIEW_PENDING", "agent1")
        states = binder.get_all_states()
        assert len(states) == 1
        assert states["docs/test2.md"]["state"] == "REVIEW_PENDING"

    def test_relative_path_handling(self, temp_project):
        """测试相对路径处理"""
        binder = DocumentStateBinder(str(temp_project))
        result = binder.check("edit", "./docs/test.md", "agent1")
        assert result.result_type == ComplianceResultType.PASSED
