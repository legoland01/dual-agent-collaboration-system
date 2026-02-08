"""测试合规检查引擎 - v2.2.2"""
import pytest
import tempfile
from pathlib import Path

from src.core.compliance_engine import ComplianceEngine, ComplianceResult, ComplianceResultType


@pytest.fixture
def temp_project():
    """创建临时项目目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestComplianceEngine:
    """合规检查引擎测试"""

    def test_init_creates_state_file(self, temp_project):
        """测试初始化创建状态文件"""
        engine = ComplianceEngine(str(temp_project))
        assert (temp_project / "state" / "compliance_results.yaml").exists()

    def test_check_role_boundary_unknown_type(self, temp_project):
        """测试未知检查类型"""
        engine = ComplianceEngine(str(temp_project))
        result = engine.check("unknown", "agent1", "view", "docs/test.md")
        assert result.result_type == ComplianceResultType.WARNING
        assert "未知检查类型" in result.message

    def test_check_role_boundary(self, temp_project):
        """测试角色边界检查"""
        engine = ComplianceEngine(str(temp_project))
        result = engine.check_role_boundary("agent1", "view", "docs/01-requirements/test.md")
        assert result.check_type == "role_boundary"
        assert result.agent_id == "agent1"

    def test_check_doc_state(self, temp_project):
        """测试文档状态检查"""
        engine = ComplianceEngine(str(temp_project))
        result = engine.check_doc_state("edit", "docs/test.md", "agent1")
        assert result.check_type == "doc_state"
        assert result.agent_id == "agent1"

    def test_check_completeness(self, temp_project):
        """测试完整性检查"""
        engine = ComplianceEngine(str(temp_project))
        result = engine.check_completeness("requirements_v2.2.0.md", "agent1")
        assert result.check_type == "completeness"
        assert result.agent_id == "agent1"

    def test_save_and_get_results(self, temp_project):
        """测试保存和获取结果"""
        engine = ComplianceEngine(str(temp_project))

        result = ComplianceResult(
            check_type="role_boundary",
            result_type=ComplianceResultType.PASSED,
            agent_id="agent1",
            action="view",
            target="docs/test.md",
            message="✅ 测试通过"
        )
        engine.save_result(result)

        results = engine.get_results(limit=10)
        assert len(results) == 1
        assert results[0]["check_type"] == "role_boundary"

    def test_get_results_with_filter(self, temp_project):
        """测试筛选结果"""
        engine = ComplianceEngine(str(temp_project))

        result1 = ComplianceResult(
            check_type="role_boundary",
            result_type=ComplianceResultType.PASSED,
            agent_id="agent1",
            action="view",
            target="docs/test.md",
            message="✅ 通过"
        )
        result2 = ComplianceResult(
            check_type="doc_state",
            result_type=ComplianceResultType.PASSED,
            agent_id="agent1",
            action="edit",
            target="docs/test.md",
            message="✅ 通过"
        )
        engine.save_result(result1)
        engine.save_result(result2)

        role_results = engine.get_results(limit=10, check_type="role_boundary")
        assert len(role_results) == 1
        assert role_results[0]["check_type"] == "role_boundary"


class TestComplianceResult:
    """合规检查结果测试"""

    def test_to_dict(self):
        """测试转换为字典"""
        result = ComplianceResult(
            check_type="role_boundary",
            result_type=ComplianceResultType.PASSED,
            agent_id="agent1",
            action="view",
            target="docs/test.md",
            message="✅ 通过",
            details={"key": "value"}
        )
        data = result.to_dict()

        assert data["check_type"] == "role_boundary"
        assert data["result_type"] == "passed"
        assert data["agent_id"] == "agent1"
        assert data["details"]["key"] == "value"

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "check_type": "role_boundary",
            "result_type": "denied",
            "agent_id": "agent2",
            "action": "edit",
            "target": "src/code.py",
            "message": "❌ 拒绝",
            "details": {},
            "timestamp": "2024-01-01T00:00:00"
        }
        result = ComplianceResult.from_dict(data)

        assert result.check_type == "role_boundary"
        assert result.result_type == ComplianceResultType.DENIED
        assert result.agent_id == "agent2"
