"""测试角色边界检查器 - v2.2.2 F-PROC-001.1"""
import pytest
import tempfile
from pathlib import Path

from src.core.role_boundary_checker import RoleBoundaryChecker
from src.core.compliance_engine import ComplianceResultType


@pytest.fixture
def temp_project():
    """创建临时项目目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def checker(temp_project):
    """创建角色边界检查器"""
    return RoleBoundaryChecker(str(temp_project))


class TestRoleBoundaryChecker:
    """角色边界检查器测试"""

    def test_agent1_can_view_requirements(self, checker):
        """测试 Agent1 可以查看需求文档"""
        result = checker.check("agent1", "view", "docs/01-requirements/test.md")
        assert result.result_type == ComplianceResultType.PASSED

    def test_agent1_cannot_edit_design(self, checker):
        """测试 Agent1 不能编辑设计文档"""
        result = checker.check("agent1", "edit", "docs/02-design/test.md")
        assert result.result_type == ComplianceResultType.DENIED
        assert "权限拒绝" in result.message

    def test_agent1_cannot_edit_code(self, checker):
        """测试 Agent1 不能编辑代码"""
        result = checker.check("agent1", "edit", "src/code.py")
        assert result.result_type == ComplianceResultType.DENIED
        assert "权限拒绝" in result.message

    def test_agent2_can_edit_design(self, checker):
        """测试 Agent2 可以编辑设计文档"""
        result = checker.check("agent2", "edit", "docs/02-design/test.md")
        assert result.result_type == ComplianceResultType.PASSED

    def test_agent2_can_edit_code(self, checker):
        """测试 Agent2 可以编辑代码"""
        result = checker.check("agent2", "edit", "src/code.py")
        assert result.result_type == ComplianceResultType.PASSED

    def test_agent2_cannot_edit_requirements(self, checker):
        """测试 Agent2 不能编辑需求文档"""
        result = checker.check("agent2", "edit", "docs/01-requirements/test.md")
        assert result.result_type == ComplianceResultType.DENIED

    def test_unknown_agent_returns_warning(self, checker):
        """测试未知 Agent 返回警告"""
        result = checker.check("agent3", "view", "docs/test.md")
        assert result.result_type == ComplianceResultType.WARNING
        assert "未知 Agent ID" in result.message

    def test_path_matches_exact(self, checker):
        """测试精确路径匹配"""
        assert checker._path_matches("docs/01-requirements/test.md", "docs/01-requirements/")
        assert checker._path_matches("docs/01-requirements/sub/test.md", "docs/01-requirements/")

    def test_path_matches_wildcard(self, checker):
        """测试通配符匹配"""
        assert checker._path_matches("docs/02-design/test.md", "docs/02-*")

    def test_is_denied_dir(self, checker):
        """测试被拒绝的目录"""
        assert checker.is_denied_dir("agent1", "docs/02-design/test.md")
        assert not checker.is_denied_dir("agent1", "docs/01-requirements/test.md")
        assert not checker.is_denied_dir("agent2", "docs/02-design/test.md")

    def test_is_allowed_action(self, checker):
        """测试允许的操作"""
        assert checker.is_allowed_action("agent1", "view")
        assert checker.is_allowed_action("agent1", "create")
        assert checker.is_allowed_action("agent2", "edit")

    def test_get_role_permissions(self, checker):
        """测试获取角色权限"""
        permissions = checker.get_role_permissions("agent1")
        assert "allowed_dirs" in permissions
        assert "denied_dirs" in permissions

        permissions = checker.get_role_permissions("agent2")
        assert "allowed_dirs" in permissions
