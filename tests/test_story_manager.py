"""v2.2.0 M4 Story Manager 测试用例

基于 src/core/story_manager.py
"""
import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.story_manager import (
    StoryManager,
    UserStory,
    InteractionStep,
    ExpectedResult,
    E2ETestCoverage,
    AcceptanceCriteria,
    StoryStatus,
    AcceptanceCriteriaStatus,
    StoryNotFoundError
)


class TestStoryManagerBasic:
    """故事管理器基础测试。"""

    def test_initialize_story_manager(self, tmp_path):
        """测试初始化故事管理器。"""
        manager = StoryManager(str(tmp_path))

        assert manager.project_path == tmp_path
        assert manager.stories_file == tmp_path / "stories.yaml"

    def test_create_story(self, tmp_path):
        """测试创建用户故事。"""
        manager = StoryManager(str(tmp_path))
        story = manager.create_story(
            title="用户登录",
            role="终端用户",
            goal="使用用户名密码登录系统",
            value="保护账户安全"
        )

        assert story is not None
        assert story.story_id == "S-001"
        assert story.title == "用户登录"
        assert story.role == "终端用户"
        assert story.goal == "使用用户名密码登录系统"
        assert story.value == "保护账户安全"
        assert story.status == StoryStatus.DRAFT

    def test_create_multiple_stories(self, tmp_path):
        """测试创建多个用户故事。"""
        manager = StoryManager(str(tmp_path))
        manager.create_story(title="Story 1", role="用户", goal="目标1", value="价值1")
        manager.create_story(title="Story 2", role="管理员", goal="目标2", value="价值2")

        assert len(manager.stories) == 2
        assert "S-001" in manager.stories
        assert "S-002" in manager.stories

    def test_list_stories(self, tmp_path):
        """测试列出用户故事。"""
        manager = StoryManager(str(tmp_path))
        manager.create_story(title="Story 1", role="用户", goal="目标1", value="价值1")
        manager.create_story(title="Story 2", role="管理员", goal="目标2", value="价值2")

        stories = manager.list_stories()
        assert len(stories) == 2

    def test_get_story(self, tmp_path):
        """测试获取用户故事。"""
        manager = StoryManager(str(tmp_path))
        created = manager.create_story(
            title="用户登录",
            role="终端用户",
            goal="使用用户名密码登录系统",
            value="保护账户安全"
        )

        retrieved = manager.get_story("S-001")
        assert retrieved.story_id == created.story_id
        assert retrieved.title == created.title


class TestStoryFiltering:
    """故事过滤测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = StoryManager(str(tmp_path))
        manager.create_story(title="S1", role="用户", goal="目标1", value="价值1", version="v2.2.0")
        manager.create_story(title="S2", role="管理员", goal="目标2", value="价值2", version="v2.2.0")
        manager.create_story(title="S3", role="用户", goal="目标3", value="价值3", version="v2.1.0")
        return manager

    def test_list_by_version(self, manager):
        """测试按版本列出故事。"""
        stories = manager.list_stories(version="v2.2.0")
        assert len(stories) == 2

    def test_list_by_status(self, manager):
        """测试按状态列出故事。"""
        stories = manager.list_stories(status=StoryStatus.DRAFT)
        assert len(stories) == 3


class TestStoryModification:
    """故事修改测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = StoryManager(str(tmp_path))
        manager.create_story(
            title="用户登录",
            role="终端用户",
            goal="使用用户名密码登录系统",
            value="保护账户安全"
        )
        return manager

    def test_add_precondition(self, manager):
        """测试添加前置条件。"""
        story = manager.add_precondition("S-001", "用户已注册账户")

        assert len(story.preconditions) == 1
        assert "用户已注册账户" in story.preconditions

    def test_add_multiple_preconditions(self, manager):
        """测试添加多个前置条件。"""
        manager.add_precondition("S-001", "用户已注册账户")
        manager.add_precondition("S-001", "用户知道正确的用户名和密码")

        story = manager.get_story("S-001")
        assert len(story.preconditions) == 2

    def test_add_interaction_step(self, manager):
        """测试添加交互步骤。"""
        story = manager.add_interaction_step(
            story_id="S-001",
            user_action="输入用户名和密码",
            system_response="系统验证凭据"
        )

        assert len(story.interaction_steps) == 1
        step = story.interaction_steps[0]
        assert step.step_number == 1
        assert step.user_action == "输入用户名和密码"
        assert step.system_response == "系统验证凭据"

    def test_add_multiple_interaction_steps(self, manager):
        """测试添加多个交互步骤。"""
        manager.add_interaction_step("S-001", "输入用户名和密码", "系统验证凭据")
        manager.add_interaction_step("S-001", "点击登录按钮", "系统重定向到主页")

        story = manager.get_story("S-001")
        assert len(story.interaction_steps) == 2
        assert story.interaction_steps[0].step_number == 1
        assert story.interaction_steps[1].step_number == 2

    def test_add_expected_result_success(self, manager):
        """测试添加成功场景预期结果。"""
        story = manager.add_expected_result(
            story_id="S-001",
            scenario_type="success",
            description="用户成功登录，显示欢迎信息"
        )

        assert len(story.expected_results) == 1
        assert story.expected_results[0].scenario_type == "success"

    def test_add_expected_result_failure(self, manager):
        """测试添加失败场景预期结果。"""
        story = manager.add_expected_result(
            story_id="S-001",
            scenario_type="failure",
            description="用户名或密码错误",
            handling="显示错误提示，不跳转页面"
        )

        assert len(story.expected_results) == 1
        assert story.expected_results[0].scenario_type == "failure"
        assert story.expected_results[0].handling == "显示错误提示，不跳转页面"


class TestStoryE2ETest:
    """故事 E2E 测试关联测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = StoryManager(str(tmp_path))
        manager.create_story(
            title="用户登录",
            role="终端用户",
            goal="使用用户名密码登录系统",
            value="保护账户安全"
        )
        return manager

    def test_link_e2e_test(self, manager):
        """测试关联 E2E 测试用例。"""
        story = manager.link_e2e_test(
            story_id="S-001",
            test_file="test_stories/test_story_S001.py",
            test_case="test_login_success",
            description="测试用户登录成功场景"
        )

        assert len(story.e2e_tests) == 1
        test = story.e2e_tests[0]
        assert test.test_file == "test_stories/test_story_S001.py"
        assert test.test_case == "test_login_success"
        assert test.description == "测试用户登录成功场景"

    def test_link_multiple_e2e_tests(self, manager):
        """测试关联多个 E2E 测试用例。"""
        manager.link_e2e_test(
            "S-001",
            "test_stories/test_story_S001.py",
            "test_login_success",
            "测试用户登录成功场景"
        )
        manager.link_e2e_test(
            "S-001",
            "test_stories/test_story_S001.py",
            "test_login_failure",
            "测试用户登录失败场景"
        )

        story = manager.get_story("S-001")
        assert len(story.e2e_tests) == 2


class TestStoryAcceptance:
    """故事验收测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = StoryManager(str(tmp_path))
        manager.create_story(
            title="用户登录",
            role="终端用户",
            goal="使用用户名密码登录系统",
            value="保护账户安全"
        )
        manager.add_acceptance_criteria("S-001", "AC-001", "使用有效凭据可成功登录")
        manager.add_acceptance_criteria("S-001", "AC-002", "使用无效凭据显示错误提示")
        return manager

    def test_add_acceptance_criteria(self, manager):
        """测试添加验收标准。"""
        story = manager.get_story("S-001")

        assert len(story.acceptance_criteria) == 2
        assert story.acceptance_criteria[0].criteria_id == "AC-001"
        assert story.acceptance_criteria[0].status == AcceptanceCriteriaStatus.PENDING

    def test_update_acceptance_status(self, manager):
        """测试更新验收标准状态。"""
        story = manager.update_acceptance_status(
            story_id="S-001",
            criteria_id="AC-001",
            status=AcceptanceCriteriaStatus.PASSED
        )

        assert story.acceptance_criteria[0].status == AcceptanceCriteriaStatus.PASSED

    def test_accept_story(self, manager):
        """测试标记故事验收通过。"""
        story = manager.accept_story("S-001", evidence="test_report.md")

        assert story.status == StoryStatus.ACCEPTED
        assert story.evidence == "test_report.md"

    def test_update_story_status(self, manager):
        """测试更新故事状态。"""
        story = manager.update_story_status("S-001", StoryStatus.IN_PROGRESS)

        assert story.status == StoryStatus.IN_PROGRESS


class TestStoryMarkdown:
    """故事 Markdown 生成测试。"""

    @pytest.fixture
    def story(self):
        story = UserStory(
            story_id="S-001",
            title="用户登录",
            role="终端用户",
            goal="使用用户名密码登录系统",
            value="保护账户安全"
        )
        story.preconditions = ["用户已注册账户", "用户知道正确的用户名和密码"]
        story.interaction_steps = [
            InteractionStep(step_number=1, user_action="输入用户名和密码", system_response="系统验证凭据"),
            InteractionStep(step_number=2, user_action="点击登录按钮", system_response="系统重定向到主页")
        ]
        story.expected_results = [
            ExpectedResult(scenario_type="success", description="用户成功登录，显示欢迎信息"),
            ExpectedResult(scenario_type="failure", description="用户名或密码错误", handling="显示错误提示")
        ]
        return story

    def test_to_markdown(self, story):
        """测试转换为 Markdown 格式。"""
        md = story.to_markdown()

        assert "## Story S-001: 用户登录" in md
        assert "**作为** 终端用户" in md
        assert "**我希望** 使用用户名密码登录系统" in md
        assert "**以便** 保护账户安全" in md
        assert "### 前置条件" in md
        assert "用户已注册账户" in md
        assert "### 交互流程" in md
        assert "| 步骤 | 用户操作 | 系统响应 |" in md
        assert "### 预期结果" in md
        assert "**成功场景**:" in md
        assert "**失败场景**:" in md

    def test_to_markdown_with_e2e_tests(self, story):
        """测试带 E2E 测试的 Markdown 转换。"""
        story.e2e_tests = [
            E2ETestCoverage(
                test_file="test_stories/test_story_S001.py",
                test_case="test_login_success",
                description="测试用户登录成功场景"
            )
        ]
        story.acceptance_criteria = [
            AcceptanceCriteria(criteria_id="AC-001", description="使用有效凭据可成功登录")
        ]

        md = story.to_markdown()

        assert "### E2E 测试覆盖" in md
        assert "### 验收标准" in md
        assert "test_login_success" in md


class TestStorySummary:
    """故事摘要测试。"""

    def test_get_story_summary(self, tmp_path):
        """测试获取故事摘要。"""
        manager = StoryManager(str(tmp_path))
        manager.create_story(title="S1", role="用户", goal="目标1", value="价值1")
        manager.create_story(title="S2", role="管理员", goal="目标2", value="价值2")

        summary = manager.get_story_summary()

        assert summary["total_stories"] == 2
        assert summary["by_status"]["draft"] == 2
        assert summary["accepted_count"] == 0
        assert summary["pending_count"] == 0

    def test_get_story_summary_with_accepted(self, tmp_path):
        """测试获取已验收故事的摘要。"""
        manager = StoryManager(str(tmp_path))
        manager.create_story(title="S1", role="用户", goal="目标1", value="价值1")
        manager.create_story(title="S2", role="管理员", goal="目标2", value="价值2")
        manager.accept_story("S-001", evidence="test_report.md")

        summary = manager.get_story_summary()

        assert summary["total_stories"] == 2
        assert summary["accepted_count"] == 1
        assert summary["pending_count"] == 0


class TestExport:
    """导出测试。"""

    def test_export_stories(self, tmp_path):
        """测试导出故事数据。"""
        manager = StoryManager(str(tmp_path))
        manager.create_story(
            title="用户登录",
            role="终端用户",
            goal="使用用户名密码登录系统",
            value="保护账户安全"
        )

        data = manager.export_stories()

        assert "stories" in data
        assert "summary" in data
        assert len(data["stories"]) == 1


class TestErrorHandling:
    """错误处理测试。"""

    def test_get_nonexistent_story(self, tmp_path):
        """测试获取不存在的故事。"""
        manager = StoryManager(str(tmp_path))

        with pytest.raises(StoryNotFoundError):
            manager.get_story("S-999")

    def test_add_precondition_to_nonexistent_story(self, tmp_path):
        """测试向不存在的故事添加前置条件。"""
        manager = StoryManager(str(tmp_path))

        with pytest.raises(StoryNotFoundError):
            manager.add_precondition("S-001", "前置条件")

    def test_accept_nonexistent_story(self, tmp_path):
        """测试验收不存在的故事。"""
        manager = StoryManager(str(tmp_path))

        with pytest.raises(StoryNotFoundError):
            manager.accept_story("S-001", evidence="test.md")


class TestStoryDataClass:
    """故事数据类测试。"""

    def test_user_story_to_dict(self):
        """测试故事转字典。"""
        story = UserStory(
            story_id="S-001",
            title="用户登录",
            role="终端用户",
            goal="使用用户名密码登录系统",
            value="保护账户安全"
        )

        data = story.to_dict()

        assert data["story_id"] == "S-001"
        assert data["title"] == "用户登录"
        assert data["role"] == "终端用户"
        assert data["status"] == "draft"

    def test_user_story_from_dict(self):
        """测试从字典创建故事。"""
        data = {
            "story_id": "S-001",
            "title": "用户登录",
            "role": "终端用户",
            "goal": "使用用户名密码登录系统",
            "value": "保护账户安全",
            "preconditions": [],
            "interaction_steps": [],
            "expected_results": [],
            "e2e_tests": [],
            "acceptance_criteria": [],
            "status": "draft",
            "version": "v2.2.0"
        }

        story = UserStory.from_dict(data)

        assert story.story_id == "S-001"
        assert story.title == "用户登录"

    def test_interaction_step_to_dict(self):
        """测试交互步骤转字典。"""
        step = InteractionStep(
            step_number=1,
            user_action="输入用户名",
            system_response="显示密码输入框"
        )

        data = step.to_dict()

        assert data["step_number"] == 1
        assert data["user_action"] == "输入用户名"
        assert data["system_response"] == "显示密码输入框"

    def test_expected_result_to_dict(self):
        """测试预期结果转字典。"""
        result = ExpectedResult(
            scenario_type="success",
            description="用户成功登录"
        )

        data = result.to_dict()

        assert data["scenario_type"] == "success"
        assert data["description"] == "用户成功登录"

    def test_e2e_test_coverage_to_dict(self):
        """测试 E2E 测试覆盖转字典。"""
        test = E2ETestCoverage(
            test_file="test_login.py",
            test_case="test_success",
            description="测试登录成功"
        )

        data = test.to_dict()

        assert data["test_file"] == "test_login.py"
        assert data["test_case"] == "test_success"

    def test_acceptance_criteria_to_dict(self):
        """测试验收标准转字典。"""
        criteria = AcceptanceCriteria(
            criteria_id="AC-001",
            description="使用有效凭据可成功登录"
        )

        data = criteria.to_dict()

        assert data["criteria_id"] == "AC-001"
        assert data["description"] == "使用有效凭据可成功登录"
        assert data["status"] == "pending"


class TestPersistence:
    """持久化测试。"""

    def test_save_and_load_stories(self, tmp_path):
        """测试保存和加载故事。"""
        manager1 = StoryManager(str(tmp_path))
        manager1.create_story(title="S1", role="用户", goal="目标1", value="价值1")
        manager1.create_story(title="S2", role="管理员", goal="目标2", value="价值2")

        manager2 = StoryManager(str(tmp_path))

        assert len(manager2.stories) == 2
        assert "S-001" in manager2.stories
        assert "S-002" in manager2.stories


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
