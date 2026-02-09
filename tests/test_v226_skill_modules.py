"""测试用例：v2.2.6 F-SKILL Skill检索增强模块"""

import pytest
from pathlib import Path
from src.core.skill_searcher import SkillSearcher
from src.core.skill_slicer import SkillSlicer
from src.core.skill_enforcer import SkillEnforcer


PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


class TestSkillSearcher:
    """SkillSearcher 测试类"""

    def test_search_no_keywords(self):
        """测试无关键词搜索"""
        searcher = SkillSearcher(str(SKILLS_DIR))

        with pytest.MonkeyPatch.context() as m:
            m.setattr(searcher, 'skills_dir', Path("/tmp/nonexistent"))

            result = searcher.search(["todowrite"], "any")
            assert result == []

    def test_search_single_keyword(self):
        """测试单关键词搜索"""
        searcher = SkillSearcher(str(SKILLS_DIR))
        result = searcher.search(["todowrite"], "any")

        assert isinstance(result, list)
        # 期望找到包含 todowrite 的 skill
        matched_names = [r["name"] for r in result]
        assert any("todowrite" in name.lower() or "todo" in name.lower()
                   for name in matched_names)

    def test_search_match_mode_any(self):
        """测试 any 匹配模式"""
        searcher = SkillSearcher(str(SKILLS_DIR))
        result = searcher.search(["todowrite", "参数"], "any")

        assert isinstance(result, list)

    def test_search_match_mode_all(self):
        """测试 all 匹配模式"""
        searcher = SkillSearcher(str(SKILLS_DIR))
        result = searcher.search(["todowrite", "参数"], "all")

        assert isinstance(result, list)

    def test_search_results_sorted(self):
        """测试搜索结果按分数排序"""
        searcher = SkillSearcher(str(SKILLS_DIR))
        result = searcher.search(["todo"], "any")

        if len(result) > 1:
            scores = [r["score"] for r in result]
            assert scores == sorted(scores, reverse=True)

    def test_search_results_limited(self):
        """测试搜索结果限制"""
        searcher = SkillSearcher(str(SKILLS_DIR))
        result = searcher.search(["test"], "any")

        assert len(result) <= 10

    def test_get_matched_keywords(self):
        """测试获取匹配的关键词"""
        searcher = SkillSearcher(str(SKILLS_DIR))
        content = "This is a test content with TODO and todowrite"
        keywords = ["test", "TODO"]

        matched = searcher._get_matched_keywords(content, keywords)
        assert "test" in matched

    def test_calculate_score(self):
        """测试分数计算"""
        searcher = SkillSearcher(str(SKILLS_DIR))

        skill_file = SKILLS_DIR / "oc_collab_todowrite_guide" / "content.md"

        if skill_file.exists():
            score = searcher._calculate_score(skill_file, ["test"], "any")
            assert score >= 0


class TestSkillSlicer:
    """SkillSlicer 测试类"""

    def test_list_chapters_exists(self):
        """测试列出存在的Skill章节"""
        slicer = SkillSlicer(str(SKILLS_DIR))
        chapters = slicer.list_chapters("oc_collab_todowrite_guide")

        assert isinstance(chapters, list)

    def test_list_chapters_not_exists(self):
        """测试列出不存在的Skill"""
        slicer = SkillSlicer(str(SKILLS_DIR))
        chapters = slicer.list_chapters("nonexistent_skill")

        assert chapters == []

    def test_get_heading_level_hash(self):
        """测试标题级别识别 - #"""
        slicer = SkillSlicer()
        assert slicer._get_heading_level("# 一级标题") == 1
        assert slicer._get_heading_level("## 二级标题") == 2
        assert slicer._get_heading_level("### 三级标题") == 3

    def test_get_heading_level_normal(self):
        """测试标题级别识别 - 普通文本"""
        slicer = SkillSlicer()
        assert slicer._get_heading_level("普通文本行") == 0
        assert slicer._get_heading_level("   缩进的普通文本") == 0

    def test_get_slice_exists(self):
        """测试获取存在的切片"""
        slicer = SkillSlicer(str(SKILLS_DIR))
        chapters = slicer.list_chapters("oc_collab_todowrite_guide")

        if chapters:
            first_section = chapters[0]["id"]
            content = slicer.get_slice("oc_collab_todowrite_guide", first_section)

            assert isinstance(content, str)
            assert len(content) > 0

    def test_get_slice_not_exists(self):
        """测试获取不存在的切片"""
        slicer = SkillSlicer(str(SKILLS_DIR))
        content = slicer.get_slice("oc_collab_todowrite_guide", "nonexistent")

        assert content == ""


class TestSkillEnforcer:
    """SkillEnforcer 测试类 - v2.2.6增强"""

    def test_required_skills_v226(self):
        """测试v2.2.6新增的必需Skill"""
        enforcer = SkillEnforcer(str(SKILLS_DIR))

        assert "requirements" in enforcer.REQUIRED_SKILLS
        assert "design" in enforcer.REQUIRED_SKILLS

    def test_optional_skills(self):
        """测试可选Skill"""
        enforcer = SkillEnforcer(str(SKILLS_DIR))

        assert "bug_management" in enforcer.OPTIONAL_SKILLS
        assert "collaboration" in enforcer.OPTIONAL_SKILLS

    def test_check_before_action_todowrite(self):
        """测试todowrite行动前检查"""
        enforcer = SkillEnforcer(str(SKILLS_DIR))
        result = enforcer.check_before_action("todowrite")

        assert "action" in result
        assert result["action"] == "todowrite"
        assert "required_skills" in result
        assert "suggestions" in result

    def test_check_before_action_signoff(self):
        """测试signoff行动前检查"""
        enforcer = SkillEnforcer(str(SKILLS_DIR))
        result = enforcer.check_before_action("signoff")

        assert result["action"] == "signoff"

    def test_check_before_action_unknown(self):
        """测试未知行动类型"""
        enforcer = SkillEnforcer(str(SKILLS_DIR))
        result = enforcer.check_before_action("unknown_action")

        assert result["action"] == "unknown_action"
        assert result["required_skills"] == []

    def test_list_loaded_skills(self):
        """测试列出已加载的Skill"""
        enforcer = SkillEnforcer(str(SKILLS_DIR))
        loaded = enforcer.list_loaded_skills()

        assert isinstance(loaded, list)

    def test_list_missing_skills(self):
        """测试列出缺失的Skill"""
        enforcer = SkillEnforcer(str(SKILLS_DIR))
        missing = enforcer.list_missing_skills()

        assert isinstance(missing, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
