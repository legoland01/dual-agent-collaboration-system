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
        result = searcher.search(["todo"], "any")

        assert isinstance(result, list)
        assert len(result) > 0  # 确保找到至少一个结果

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

    def test_combine_section_with_subsections(self):
        """测试合并章节及其子章节"""
        slicer = SkillSlicer(str(SKILLS_DIR))
        chapters = slicer.list_chapters("oc_collab_todowrite_guide")

        if len(chapters) > 1:
            # 获取第一个有子章节的章节
            for ch in chapters:
                if ch["level"] == 1:
                    result = slicer._combine_section(chapters, ch)
                    assert isinstance(result, str)
                    assert "# " in result  # 应该包含标题
                    break

    def test_combine_section_single_level(self):
        """测试单级章节合并"""
        slicer = SkillSlicer(str(SKILLS_DIR))

        # Mock一个简单的章节结构
        test_chapters = [
            {"id": "s1", "title": "章节1", "content": ["内容1"], "level": 1},
            {"id": "s2", "title": "章节2", "content": ["内容2"], "level": 1},
        ]

        result = slicer._combine_section(test_chapters, test_chapters[0])
        assert "章节1" in result
        assert "内容1" in result

    def test_combine_section_with_child(self):
        """测试有子章节的情况"""
        slicer = SkillSlicer(str(SKILLS_DIR))

        # Mock一个有层级关系的章节结构
        test_chapters = [
            {"id": "p1", "title": "父章节", "content": ["父内容"], "level": 1},
            {"id": "c1", "title": "子章节", "content": ["子内容"], "level": 2},
        ]

        result = slicer._combine_section(test_chapters, test_chapters[0])
        assert "父章节" in result
        assert "子章节" in result

    def test_get_slice_with_subsections(self):
        """测试获取包含子章节的切片"""
        slicer = SkillSlicer(str(SKILLS_DIR))
        chapters = slicer.list_chapters("oc_collab_todowrite_guide")

        if len(chapters) >= 2:
            # 获取第一个章节，包含子章节
            first_id = chapters[0]["id"]
            content = slicer.get_slice("oc_collab_todowrite_guide", first_id, include_subsections=True)

            if content:
                assert isinstance(content, str)

    def test_get_slice_without_subsections(self):
        """测试只获取章节本身"""
        slicer = SkillSlicer(str(SKILLS_DIR))
        chapters = slicer.list_chapters("oc_collab_todowrite_guide")

        if chapters:
            first_id = chapters[0]["id"]
            content = slicer.get_slice("oc_collab_todowrite_guide", first_id, include_subsections=False)

            if content:
                assert isinstance(content, str)

    def test_list_chapters_with_only_intro(self):
        """测试只有简介的Skill（无标题）"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "test_skill")
            os.makedirs(skill_dir)

            # 创建一个只有简介内容的文件
            with open(os.path.join(skill_dir, "content.md"), "w") as f:
                f.write("这是一个只有简介内容的Skill文件。\n")
                f.write("没有标题。\n")

            slicer = SkillSlicer(tmpdir)
            chapters = slicer.list_chapters("test_skill")

            # 应该返回一个intro章节
            assert len(chapters) >= 1
            assert chapters[0]["id"] == "intro"

    def test_list_chapters_multiple_levels(self):
        """测试多级标题解析"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "test_skill")
            os.makedirs(skill_dir)

            # 创建有多级标题的文件
            with open(os.path.join(skill_dir, "content.md"), "w") as f:
                f.write("# 一级标题\n")
                f.write("内容1\n")
                f.write("## 二级标题\n")
                f.write("内容2\n")
                f.write("### 三级标题\n")
                f.write("内容3\n")

            slicer = SkillSlicer(tmpdir)
            chapters = slicer.list_chapters("test_skill")

            # 应该解析出3个章节
            assert len(chapters) >= 3

            # 验证标题级别
            levels = [ch["level"] for ch in chapters]
            assert 1 in levels
            assert 2 in levels
            assert 3 in levels

    def test_get_slice_level_1_parent(self):
        """测试获取一级标题（父章节）"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "test_skill")
            os.makedirs(skill_dir)

            # 创建文件
            with open(os.path.join(skill_dir, "content.md"), "w") as f:
                f.write("# 父章节\n")
                f.write("父内容\n")
                f.write("## 子章节1\n")
                f.write("子内容1\n")
                f.write("## 子章节2\n")
                f.write("子内容2\n")

            slicer = SkillSlicer(tmpdir)
            chapters = slicer.list_chapters("test_skill")

            if len(chapters) >= 2:
                # 获取第一个章节（包含子章节）
                content = slicer.get_slice("test_skill", chapters[0]["id"], include_subsections=True)
                assert "父章节" in content
                assert "子章节" in content

    def test_get_slice_no_subsections_true(self):
        """测试不包含子章节时直接返回内容"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "test_skill")
            os.makedirs(skill_dir)

            # 创建文件
            with open(os.path.join(skill_dir, "content.md"), "w") as f:
                f.write("# 章节1\n")
                f.write("内容1\n")
                f.write("# 章节2\n")
                f.write("内容2\n")

            slicer = SkillSlicer(tmpdir)
            chapters = slicer.list_chapters("test_skill")

            if len(chapters) >= 2:
                # 获取第二个章节，不包含子章节
                content = slicer.get_slice("test_skill", chapters[1]["id"], include_subsections=False)
                assert "内容2" in content


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
