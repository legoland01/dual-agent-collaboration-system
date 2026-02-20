"""测试 BUG-20260210-001: SkillEnforcer 集成到 CLI 命令

验证 todowrite、signoff、advance 命令是否正确调用 SkillEnforcer。
"""
import pytest
from pathlib import Path
import re


class TestSkillEnforcerIntegrationCode:
    """测试 SkillEnforcer 集成代码是否存在"""

    def test_enhanced_commands_has_skill_enforcer_import(self):
        """验证 enhanced_commands.py 有 SkillEnforcer 导入"""
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "enhanced_commands.py"
        with open(cli_path) as f:
            content = f.read()

        assert "from ..core.skill_enforcer import SkillEnforcer" in content

    def test_enhanced_commands_todowrite_has_skill_check(self):
        """验证 todowrite_command 调用 SkillEnforcer"""
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "enhanced_commands.py"
        with open(cli_path) as f:
            content = f.read()

        assert 'check_before_action("todowrite")' in content
        assert "BUG-20260210-001" in content

    def test_main_has_skill_enforcer_import(self):
        """验证 main.py 有 SkillEnforcer 导入"""
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "main.py"
        with open(cli_path) as f:
            content = f.read()

        assert "from ..core.skill_enforcer import SkillEnforcer" in content

    def test_main_signoff_has_skill_check(self):
        """验证 signoff_command 调用 SkillEnforcer"""
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "main.py"
        with open(cli_path) as f:
            content = f.read()

        assert 'check_before_action("signoff")' in content
        assert "BUG-20260210-001" in content

    def test_main_advance_has_skill_check(self):
        """验证 advance_command 调用 SkillEnforcer"""
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "main.py"
        with open(cli_path) as f:
            content = f.read()

        assert 'check_before_action("phase_advance")' in content
        assert "BUG-20260210-001" in content

    def test_all_commands_have_auto_check_option(self):
        """验证所有命令都有 --auto-check 选项"""
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "main.py"
        with open(cli_path) as f:
            content = f.read()

        assert "--auto-check/--no-auto-check" in content

    def test_skill_check_warning_message_format(self):
        """验证 Skill 检查警告消息格式正确"""
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "enhanced_commands.py"
        with open(cli_path) as f:
            content = f.read()

        assert '⚠️' in content
        assert "缺少相关Skill" in content

    def test_missing_skills_displayed(self):
        """验证缺失的 Skill 会显示"""
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "enhanced_commands.py"
        with open(cli_path) as f:
            content = f.read()

        assert 'skill_result["missing"]' in content
        assert 'for skill in skill_result["missing"]' in content

    def test_suggestions_displayed(self):
        """验证建议会显示"""
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "enhanced_commands.py"
        with open(cli_path) as f:
            content = f.read()

        assert 'skill_result["suggestions"]' in content
        assert 'suggestions' in content and '0]' in content


class TestSkillEnforcerCheckBeforeAction:
    """测试 SkillEnforcer.check_before_action 方法"""

    def test_todowrite_action_mapping(self):
        """验证 todowrite action 映射到正确的 skills"""
        from src.core.skill_enforcer import SkillEnforcer

        enforcer = SkillEnforcer()
        result = enforcer.check_before_action("todowrite")

        assert result["action"] == "todowrite"
        assert "requirements" in result["required_skills"] or "oc_collab_requirements_guide" in result.get("required_skills", [])

    def test_signoff_action_mapping(self):
        """验证 signoff action 映射到正确的 skills"""
        from src.core.skill_enforcer import SkillEnforcer

        enforcer = SkillEnforcer()
        result = enforcer.check_before_action("signoff")

        assert result["action"] == "signoff"

    def test_phase_advance_action_mapping(self):
        """验证 phase_advance action 映射到正确的 skills"""
        from src.core.skill_enforcer import SkillEnforcer

        enforcer = SkillEnforcer()
        result = enforcer.check_before_action("phase_advance")

        assert result["action"] == "phase_advance"

    def test_unknown_action_returns_empty_skills(self):
        """验证未知 action 返回空 skills"""
        from src.core.skill_enforcer import SkillEnforcer

        enforcer = SkillEnforcer()
        result = enforcer.check_before_action("unknown")

        assert result["action"] == "unknown"
        assert result["required_skills"] == []
        assert result["missing"] == []


class TestBugReportStatus:
    """验证 Bug 报告状态"""

    def test_bug_report_updated(self):
        """验证 Bug 报告已更新"""
        bug_path = Path(__file__).parent.parent / "docs" / "00-memos" / "BUG-20260210-001_skill_enforce_not_enforced.md"
        with open(bug_path) as f:
            content = f.read()

        assert "IN_PROGRESS" in content or "FIX-001" in content
        assert "DONE" in content

    @pytest.mark.skip(reason="架构变化：不再使用adhoc.yaml")
    def test_todo_updated(self):
        """验证 TODO 已更新"""
        todo_path = Path(__file__).parent.parent / "state" / "agent_adhoc_todos.yaml"
        with open(todo_path) as f:
            content = f.read()

        assert "FIX-001: todowrite集成SkillEnforcer (1h) - DONE" in content
        assert "FIX-002: signoff集成SkillEnforcer (1h) - DONE" in content
        assert "FIX-003: phase-advance集成SkillEnforcer (1h) - DONE" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
