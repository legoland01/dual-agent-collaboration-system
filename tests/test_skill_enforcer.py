"""SkillEnforcer 测试用例

FR-SKILL-001: 在CLI命令执行前，强制检查相关Skill是否已加载
"""
import pytest
import tempfile
from pathlib import Path
from src.core.skill_enforcer import SkillEnforcer, SkillNotFoundError


class TestSkillEnforcer:
    """SkillEnforcer 测试类"""

    @pytest.fixture
    def temp_skills_dir(self):
        """创建临时技能目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills"
            skills_dir.mkdir()
            yield skills_dir

    @pytest.fixture
    def enforcer(self, temp_skills_dir):
        """创建 SkillEnforcer 实例"""
        return SkillEnforcer(str(temp_skills_dir))

    def test_check_required_skills_no_phase(self, enforcer):
        """TC-SKILL-001: 无效阶段返回空"""
        result, missing = enforcer.check_required_skills("unknown_phase")
        assert result == True
        assert missing == []

    def test_check_required_skills_all_loaded(self, temp_skills_dir, enforcer):
        """TC-SKILL-002: 所有Skill已加载"""
        (temp_skills_dir / "oc_collab_requirements_review_guide").mkdir()
        (temp_skills_dir / "oc_collab_development_guide").mkdir()
        (temp_skills_dir / "oc_collab_test_acceptance_guide").mkdir()
        (temp_skills_dir / "oc_collab_deployment_guide").mkdir()

        for phase in ["requirements_review", "development", "testing", "deployment"]:
            result, missing = enforcer.check_required_skills(phase)
            assert result == True
            assert missing == []

    def test_check_required_skills_none_loaded(self, enforcer):
        """TC-SKILL-003: 无Skill加载"""
        result, missing = enforcer.check_required_skills("requirements_review")
        assert result == False
        assert "oc_collab_requirements_review_guide" in missing

    def test_check_required_skills_partial_loaded(self, temp_skills_dir, enforcer):
        """TC-SKILL-004: 部分Skill加载"""
        (temp_skills_dir / "oc_collab_requirements_review_guide").mkdir()

        result, missing = enforcer.check_required_skills("requirements_review")
        assert result == True

        result, missing = enforcer.check_required_skills("development")
        assert result == False
        assert "oc_collab_development_guide" in missing

    def test_get_load_command(self, enforcer):
        """TC-SKILL-005: 获取加载命令"""
        cmd = enforcer.get_load_command("test_skill")
        assert cmd == "skill load test_skill"

    def test_list_loaded_skills_empty(self, enforcer):
        """TC-SKILL-006: 列出空已加载列表"""
        loaded = enforcer.list_loaded_skills()
        assert loaded == []

    def test_list_loaded_skills_with_content(self, temp_skills_dir, enforcer):
        """TC-SKILL-007: 列出有内容的Skill"""
        skill_path = temp_skills_dir / "oc_collab_test_guide"
        skill_path.mkdir()
        (skill_path / "content.md").write_text("# Test Skill")

        loaded = enforcer.list_loaded_skills()
        assert "oc_collab_test_guide" in loaded

    def test_list_missing_skills_all_missing(self, enforcer):
        """TC-SKILL-008: 列出所有缺失的Skill"""
        missing = enforcer.list_missing_skills()
        assert len(missing) == 4
        assert "oc_collab_requirements_review_guide" in missing
        assert "oc_collab_development_guide" in missing
        assert "oc_collab_test_acceptance_guide" in missing
        assert "oc_collab_deployment_guide" in missing

    def test_list_missing_skills_all_present(self, temp_skills_dir, enforcer):
        """TC-SKILL-009: 列出所有存在的Skill"""
        for phase, skill in SkillEnforcer.REQUIRED_SKILLS.items():
            skill_path = temp_skills_dir / skill
            skill_path.mkdir()

        missing = enforcer.list_missing_skills()
        assert missing == []

    def test_list_missing_skills_partial(self, temp_skills_dir, enforcer):
        """TC-SKILL-010: 部分Skill存在"""
        (temp_skills_dir / "oc_collab_requirements_review_guide").mkdir()
        (temp_skills_dir / "oc_collab_development_guide").mkdir()

        missing = enforcer.list_missing_skills()
        assert "oc_collab_requirements_review_guide" not in missing
        assert "oc_collab_development_guide" not in missing
        assert "oc_collab_test_acceptance_guide" in missing
        assert "oc_collab_deployment_guide" in missing
