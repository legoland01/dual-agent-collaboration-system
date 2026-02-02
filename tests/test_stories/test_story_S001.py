"""Story S-001: 用户登录 - E2E 测试

测试用户使用用户名密码登录系统的完整流程。
"""
import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.story_manager import (
    StoryManager,
    UserStory,
    StoryStatus,
    AcceptanceCriteriaStatus
)


class TestUserLoginStory:
    """用户登录故事 E2E 测试。"""

    @pytest.fixture
    def story_manager(self, tmp_path):
        """创建故事管理器。"""
        return StoryManager(str(tmp_path))

    @pytest.fixture
    def login_story(self, story_manager):
        """创建用户登录故事。"""
        story = story_manager.create_story(
            title="用户登录",
            role="终端用户",
            goal="使用用户名密码登录系统",
            value="保护账户安全"
        )
        story_manager.add_precondition(story.story_id, "用户已注册账户")
        story_manager.add_precondition(story.story_id, "用户知道正确的用户名和密码")

        story_manager.add_interaction_step(
            story.story_id,
            "输入用户名和密码",
            "系统验证凭据"
        )
        story_manager.add_interaction_step(
            story.story_id,
            "点击登录按钮",
            "系统重定向到主页"
        )

        story_manager.add_expected_result(
            story.story_id,
            "success",
            "用户成功登录，显示欢迎信息"
        )
        story_manager.add_expected_result(
            story.story_id,
            "failure",
            "用户名或密码错误",
            handling="显示错误提示，不跳转页面"
        )

        story_manager.link_e2e_test(
            story.story_id,
            "test_stories/test_story_S001.py",
            "test_login_success",
            "测试用户登录成功场景"
        )
        story_manager.link_e2e_test(
            story.story_id,
            "test_stories/test_story_S001.py",
            "test_login_failure",
            "测试用户登录失败场景"
        )

        story_manager.add_acceptance_criteria(story.story_id, "AC-001", "使用有效凭据可成功登录")
        story_manager.add_acceptance_criteria(story.story_id, "AC-002", "使用无效凭据显示错误提示")

        return story_manager.get_story(story.story_id)

    def test_story_creation(self, login_story):
        """测试故事创建。"""
        assert login_story.story_id == "S-001"
        assert login_story.title == "用户登录"
        assert login_story.role == "终端用户"
        assert login_story.status == StoryStatus.DRAFT

    def test_preconditions(self, login_story):
        """测试前置条件。"""
        assert len(login_story.preconditions) == 2
        assert "用户已注册账户" in login_story.preconditions

    def test_interaction_steps(self, login_story):
        """测试交互步骤。"""
        assert len(login_story.interaction_steps) == 2
        assert login_story.interaction_steps[0].step_number == 1
        assert login_story.interaction_steps[0].user_action == "输入用户名和密码"

    def test_expected_results(self, login_story):
        """测试预期结果。"""
        assert len(login_story.expected_results) == 2

        success_result = next(
            r for r in login_story.expected_results if r.scenario_type == "success"
        )
        assert success_result.description == "用户成功登录，显示欢迎信息"

        failure_result = next(
            r for r in login_story.expected_results if r.scenario_type == "failure"
        )
        assert failure_result.handling == "显示错误提示，不跳转页面"

    def test_e2e_test_linking(self, login_story):
        """测试 E2E 测试关联。"""
        assert len(login_story.e2e_tests) == 2
        test_names = [t.test_case for t in login_story.e2e_tests]
        assert "test_login_success" in test_names
        assert "test_login_failure" in test_names

    def test_acceptance_criteria(self, login_story):
        """测试验收标准。"""
        assert len(login_story.acceptance_criteria) == 2
        assert login_story.acceptance_criteria[0].criteria_id == "AC-001"
        assert login_story.acceptance_criteria[0].status == AcceptanceCriteriaStatus.PENDING

    def test_markdown_export(self, login_story):
        """测试 Markdown 导出。"""
        md = login_story.to_markdown()

        assert "## Story S-001: 用户登录" in md
        assert "**作为** 终端用户" in md
        assert "**我希望** 使用用户名密码登录系统" in md
        assert "### 前置条件" in md
        assert "### 交互流程" in md
        assert "### 预期结果" in md
        assert "**成功场景**:" in md
        assert "**失败场景**:" in md

    def test_story_status_transition(self, story_manager, login_story):
        """测试故事状态流转。"""
        story = story_manager.get_story("S-001")

        story = story_manager.update_story_status("S-001", StoryStatus.IN_PROGRESS)
        assert story.status == StoryStatus.IN_PROGRESS

        story = story_manager.update_story_status("S-001", StoryStatus.PENDING_ACCEPTANCE)
        assert story.status == StoryStatus.PENDING_ACCEPTANCE

    def test_accept_story(self, story_manager, login_story):
        """测试验收故事。"""
        story = story_manager.accept_story("S-001", evidence="e2e_test_report.md")

        assert story.status == StoryStatus.ACCEPTED
        assert story.evidence == "e2e_test_report.md"


class TestMultipleStories:
    """多故事 E2E 测试。"""

    @pytest.fixture
    def story_manager(self, tmp_path):
        return StoryManager(str(tmp_path))

    def test_create_multiple_stories(self, story_manager):
        """测试创建多个故事。"""
        story1 = story_manager.create_story(
            title="用户登录",
            role="终端用户",
            goal="登录系统",
            value="保护账户"
        )
        story2 = story_manager.create_story(
            title="用户注册",
            role="访客",
            goal="注册新账户",
            value="开始使用系统"
        )
        story3 = story_manager.create_story(
            title="密码重置",
            role="忘记密码用户",
            goal="重置密码",
            value="恢复账户访问"
        )

        assert len(story_manager.stories) == 3
        assert story1.story_id == "S-001"
        assert story2.story_id == "S-002"
        assert story3.story_id == "S-003"

        stories = story_manager.list_stories()
        assert len(stories) == 3

    def test_filter_stories_by_status(self, story_manager):
        """测试按状态过滤故事。"""
        story_manager.create_story(title="S1", role="用户", goal="目标1", value="价值1")
        story_manager.create_story(title="S2", role="用户", goal="目标2", value="价值2")
        story_manager.accept_story("S-001", evidence="report.md")

        draft_stories = story_manager.list_stories(status=StoryStatus.DRAFT)
        accepted_stories = story_manager.list_stories(status=StoryStatus.ACCEPTED)

        assert len(draft_stories) == 1
        assert len(accepted_stories) == 1
        assert draft_stories[0].story_id == "S-002"

    def test_filter_stories_by_version(self, story_manager):
        """测试按版本过滤故事。"""
        story_manager.create_story(
            title="S1", role="用户", goal="目标1", value="价值1", version="v2.2.0"
        )
        story_manager.create_story(
            title="S2", role="用户", goal="目标2", value="价值2", version="v2.1.0"
        )

        v220_stories = story_manager.list_stories(version="v2.2.0")
        v210_stories = story_manager.list_stories(version="v2.1.0")

        assert len(v220_stories) == 1
        assert len(v210_stories) == 1


class TestStoryPersistence:
    """故事持久化 E2E 测试。"""

    def test_save_and_reload_stories(self, tmp_path):
        """测试保存和重新加载故事。"""
        manager1 = StoryManager(str(tmp_path))
        manager1.create_story(title="S1", role="用户", goal="目标1", value="价值1")
        manager1.create_story(title="S2", role="管理员", goal="目标2", value="价值2")
        manager1.accept_story("S-001", evidence="test.md")

        manager2 = StoryManager(str(tmp_path))

        assert len(manager2.stories) == 2
        assert manager2.get_story("S-001").status == StoryStatus.ACCEPTED

    def test_data_integrity_after_reload(self, tmp_path):
        """测试重新加载后数据完整性。"""
        manager1 = StoryManager(str(tmp_path))
        story = manager1.create_story(
            title="用户登录",
            role="终端用户",
            goal="登录系统",
            value="安全访问"
        )
        manager1.add_precondition(story.story_id, "用户已注册")
        manager1.add_interaction_step(story.story_id, "输入凭据", "系统验证")
        manager1.add_expected_result(story.story_id, "success", "登录成功")
        manager1.add_acceptance_criteria(story.story_id, "AC-001", "登录成功")

        manager2 = StoryManager(str(tmp_path))
        reloaded_story = manager2.get_story("S-001")

        assert reloaded_story.title == "用户登录"
        assert len(reloaded_story.preconditions) == 1
        assert len(reloaded_story.interaction_steps) == 1
        assert len(reloaded_story.expected_results) == 1
        assert len(reloaded_story.acceptance_criteria) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
