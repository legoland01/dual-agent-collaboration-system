"""ChangeComplianceChecker 单元测试。"""
import pytest
import tempfile
import os
from pathlib import Path


class TestComplianceResult:
    """ComplianceResult 测试。"""

    def test_compliance_result_valid(self):
        """测试有效结果。"""
        from src.core.change_compliance import ComplianceResult

        result = ComplianceResult(valid=True)
        assert result.valid is True
        assert result.violations == []
        assert result.warnings == []
        assert result.suggestions == []

    def test_compliance_result_with_violations(self):
        """测试带违规的结果。"""
        from src.core.change_compliance import ComplianceResult

        result = ComplianceResult(
            valid=False,
            violations=["缺少签署确认"],
            warnings=["需求 ID 未找到"],
            suggestions=["请添加签署表格"]
        )
        assert result.valid is False
        assert len(result.violations) == 1


class TestChangeComplianceChecker:
    """ChangeComplianceChecker 测试。"""

    def test_initialization(self):
        """测试初始化。"""
        from src.core.change_compliance import ChangeComplianceChecker

        checker = ChangeComplianceChecker("/tmp/test_project")
        assert str(checker.project_path) == "/tmp/test_project"

    def test_check_prd_compliance_file_not_exists(self):
        """测试 PRD 文件不存在。"""
        from src.core.change_compliance import ChangeComplianceChecker

        checker = ChangeComplianceChecker("/tmp")
        result = checker.check_prd_compliance("/nonexistent/prd.md")

        assert result.valid is False
        assert len(result.violations) == 1
        assert "不存在" in result.violations[0]

    def test_check_prd_compliance_missing_signoff(self):
        """测试 PRD 缺少签署确认章节。"""
        from src.core.change_compliance import ChangeComplianceChecker

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# PRD 文档\n\n## 功能描述\n")
            temp_path = f.name

        try:
            checker = ChangeComplianceChecker("/tmp")
            result = checker.check_prd_compliance(temp_path)

            assert result.valid is True
            assert any("缺少签署确认章节" in v for v in result.violations)
        finally:
            os.unlink(temp_path)

    def test_check_prd_compliance_with_signoff(self):
        """测试 PRD 包含签署确认章节。"""
        from src.core.change_compliance import ChangeComplianceChecker

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# PRD 文档\n\n## 签署确认\n")
            temp_path = f.name

        try:
            checker = ChangeComplianceChecker("/tmp")
            result = checker.check_prd_compliance(temp_path)

            assert result.valid is True
            assert "缺少签署确认章节" not in result.violations
        finally:
            os.unlink(temp_path)

    def test_check_rfc_compliance_file_not_exists(self):
        """测试 RFC 文件不存在。"""
        from src.core.change_compliance import ChangeComplianceChecker

        checker = ChangeComplianceChecker("/tmp")
        result = checker.check_rfc_compliance("/nonexistent/rfc.md")

        assert result.valid is False
        assert len(result.violations) == 1
        assert "不存在" in result.violations[0]

    def test_detect_conflicts_no_conflict(self):
        """测试未检测到冲突。"""
        from src.core.change_compliance import ChangeComplianceChecker

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# PRD\n\nFR-001: 功能需求")
            prd_path = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# RFC\n\nRFC-001: 技术方案")
            rfc_path = f.name

        try:
            checker = ChangeComplianceChecker("/tmp")
            conflicts = checker.detect_conflicts(prd_path, rfc_path)

            assert conflicts == []
        finally:
            os.unlink(prd_path)
            os.unlink(rfc_path)

    def test_detect_conflicts_with_conflict(self):
        """测试检测到冲突。"""
        from src.core.change_compliance import ChangeComplianceChecker

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# PRD\n\nFR-001: 功能需求")
            prd_path = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# RFC\n\nRFC-001: 技术方案\nFR-001: 实现细节")
            rfc_path = f.name

        try:
            checker = ChangeComplianceChecker("/tmp")
            conflicts = checker.detect_conflicts(prd_path, rfc_path)

            assert len(conflicts) > 0
            assert conflicts[0].type == "内容冲突"
        finally:
            os.unlink(prd_path)
            os.unlink(rfc_path)

    def test_handle_violation_missing_signoff(self):
        """测试处理缺少签署违规。"""
        from src.core.change_compliance import ChangeComplianceChecker

        checker = ChangeComplianceChecker("/tmp")
        result = checker.handle_violation("missing_signoff")

        assert result["action"] == "block"
        assert result["severity"] == "error"

    def test_handle_violation_unknown_type(self):
        """测试处理未知违规类型。"""
        from src.core.change_compliance import ChangeComplianceChecker

        checker = ChangeComplianceChecker("/tmp")
        result = checker.handle_violation("unknown_type")

        assert result["action"] == "unknown"
        assert result["severity"] == "error"

    def test_handle_violation_rfc_already_in_prd(self):
        """测试处理 RFC 已在 PRD 中的违规。"""
        from src.core.change_compliance import ChangeComplianceChecker

        checker = ChangeComplianceChecker("/tmp")
        result = checker.handle_violation("rfc_already_in_prd")

        assert result["action"] == "suggest"
        assert result["severity"] == "info"

    def test_check_rfc_compliance_with_prd(self):
        """测试 RFC 合规检查（带 PRD）。"""
        from src.core.change_compliance import ChangeComplianceChecker

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# RFC\n\nRFC-001: 技术方案\n")
            rfc_path = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# PRD\n\nRFC-001: 需求概述\n")
            prd_path = f.name

        try:
            checker = ChangeComplianceChecker("/tmp")
            result = checker.check_rfc_compliance(rfc_path, prd_path)

            assert result.valid is True
        finally:
            os.unlink(rfc_path)
            os.unlink(prd_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
