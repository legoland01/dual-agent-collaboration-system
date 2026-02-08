"""测试完整性门禁 - v2.2.2 F-PROC-001.3"""
import pytest
import tempfile
from pathlib import Path

from src.core.completeness_gate import CompletenessGate
from src.core.compliance_engine import ComplianceResultType


@pytest.fixture
def temp_project():
    """创建临时项目目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def gate(temp_project):
    """创建完整性门禁"""
    return CompletenessGate(str(temp_project))


class TestCompletenessGate:
    """完整性门禁测试"""

    def test_main_doc_patterns(self, gate):
        """测试主文档模式"""
        assert gate.is_main_doc("requirements_v2.2.0.md") is True
        assert gate.is_main_doc("design_v1.0.md") is True
        assert gate.is_main_doc("REVIEW_v2.2.0.md") is True

    def test_sub_doc_patterns(self, gate):
        """测试子文档模式"""
        assert gate.is_main_doc("requirements_v2.2.0_scope.md") is False
        assert gate.is_main_doc("F-FOO-001.md") is False
        assert gate.is_main_doc("requirements_v2.2.0.001_ch01.md") is False

    def test_check_complete_review_passes(self, gate):
        """测试完整评审通过"""
        result = gate.check_completeness("requirements_v2.2.0.md", "agent1", None)
        assert result.result_type == ComplianceResultType.PASSED

    def test_check_complete_review_with_scope_fails(self, gate):
        """测试部分评审失败"""
        result = gate.check_completeness("requirements_v2.2.0.md", "agent1", "第1-3章")
        assert result.result_type == ComplianceResultType.DENIED
        assert "部分评审" in result.message

    def test_check_sub_doc_review_fails(self, gate):
        """测试子文档评审失败"""
        result = gate.check_completeness("F-FOO-001.md", "agent1", None)
        assert result.result_type == ComplianceResultType.DENIED
        assert "子文档" in result.message

    def test_section_only_detection(self, gate):
        """测试章节检测"""
        assert gate.is_section_only(None) is False
        assert gate.is_section_only("") is False
        assert gate.is_section_only("第1章") is True
        assert gate.is_section_only("  ") is False

    def test_find_main_doc_for_requirements(self, gate):
        """测试查找需求主文档"""
        main_doc = gate.find_main_doc("requirements_v2.2.0_scope.md")
        assert main_doc is not None
        assert "requirements" in main_doc

    def test_find_main_doc_for_review(self, gate):
        """测试查找评审主文档"""
        main_doc = gate.find_main_doc("REVIEW_v2.2.0.md")
        assert main_doc == "REVIEW_v2.2.0.md"

    def test_get_doc_name(self, gate):
        """测试获取文档名称"""
        assert gate._get_doc_name("/path/to/requirements_v2.2.0.md") == "requirements_v2.2.0.md"
        assert gate._get_doc_name("design_v1.0.md") == "design_v1.0.md"

    def test_check_design_doc_passes(self, gate):
        """测试设计文档评审通过"""
        result = gate.check_completeness("design_v1.0.md", "agent2", None)
        assert result.result_type == ComplianceResultType.PASSED

    def test_check_review_doc_passes(self, gate):
        """测试评审文档评审通过"""
        result = gate.check_completeness("REVIEW_v2.2.0.md", "agent1", None)
        assert result.result_type == ComplianceResultType.PASSED
