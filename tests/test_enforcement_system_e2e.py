"""v2.2.4 Enforcement System 端到端测试

集成测试：SkillEnforcer, SignoffEnforcer, RequirementsChecker, PhaseAdvance
"""
import pytest
import tempfile
import subprocess
from pathlib import Path


class TestEnforcementSystemE2E:
    """Enforcement System 端到端测试"""

    @pytest.fixture
    def project_setup(self):
        """创建临时项目环境"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            (project_path / "state").mkdir()
            (project_path / "skills").mkdir()
            (project_path / "docs" / "01-requirements").mkdir(parents=True)
            (project_path / "src").mkdir()

            state_file = project_path / "state" / "project_state.yaml"
            state_file.write_text("""current_agent: agent1
v2.2.4:
  development:
    status: in_progress
    started_at: '2026-02-08T20:00:00'
  phase: development
""")
            yield project_path

    def test_cli_skill_check_command(self, project_setup):
        """TC-E2E-001: CLI skill check 命令"""
        import sys
        sys.path.insert(0, str(project_setup))
        from src.cli.skill_commands import skill_check_command
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(skill_check_command)
        assert result.exit_code == 0

    def test_cli_check_requirements_command(self, project_setup):
        """TC-E2E-002: CLI check requirements 命令"""
        import sys
        sys.path.insert(0, str(project_setup))
        from src.cli.check_commands import check_requirements_command
        from click.testing import CliRunner

        req_doc = project_setup / "docs" / "01-requirements" / "requirements_v2.2.4.md"
        req_doc.write_text("""# 需求文档

## 概述
测试

## 功能需求
- FR-001: 测试

## CLI命令清单
- cmd1

## 工时预估
- 1h

## 依赖关系
- 无

## 签署确认
| 角色 | 确认 |
|------|------|
| Agent 1 | ✅ |
| Agent 2 | ✅ |
""")
        runner = CliRunner()
        result = runner.invoke(check_requirements_command, [str(req_doc)])
        assert result.exit_code == 0

    def test_skill_and_signoff_integration(self, project_setup):
        """TC-E2E-003: Skill与Signoff集成"""
        from src.core.skill_enforcer import SkillEnforcer
        from src.core.signoff_enforcer import SignoffEnforcer

        skill_enforcer = SkillEnforcer(str(project_setup / "skills"))
        signoff_enforcer = SignoffEnforcer(str(project_setup / "state"))

        skill_result, _ = skill_enforcer.check_required_skills("development")
        assert skill_result == False

    def test_requirements_checker_with_signoff(self, project_setup):
        """TC-E2E-004: RequirementsChecker与签署验证集成"""
        from src.core.requirements_checker import RequirementsChecker

        checker = RequirementsChecker(str(project_setup / "docs" / "01-requirements"))

        req_doc = project_setup / "docs" / "01-requirements" / "test.md"
        req_doc.write_text("""# 测试

## 概述
测试

## 签署确认
| 角色 | 确认 |
|------|------|
| Agent 1 | ✅ |
""")

        result = checker.check_completeness(str(req_doc))
        assert result["complete"] == False
        assert "功能需求" in result["missing_sections"]

    def test_phase_advance_with_prerequisites(self, project_setup):
        """TC-E2E-005: PhaseAdvance前置条件检查"""
        from src.core.phase_advance import PhaseAdvanceEngine

        engine = PhaseAdvanceEngine(str(project_setup))

        state_file = project_setup / "state" / "project_state.yaml"
        state_file.write_text("""current_agent: agent1
phase: development
development:
  status: completed
test:
  pm_signoff: false
  dev_signoff: false
""")

        result = engine.check_condition("development", {"development": {"status": "completed"}})
        assert result == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
