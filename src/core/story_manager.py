"""用户故事管理模块 - v2.2.0 M4 用户故事管理

提供用户故事创建、列表、详情、关联测试、验收确认等功能。
"""
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


class StoryStatus(Enum):
    """用户故事状态枚举。"""
    DRAFT = "draft"           # 草稿
    IN_PROGRESS = "in_progress"  # 进行中
    PENDING_ACCEPTANCE = "pending_acceptance"  # 待验收
    ACCEPTED = "accepted"     # 已验收
    ARCHIVED = "archived"     # 已归档


class AcceptanceCriteriaStatus(Enum):
    """验收标准状态枚举。"""
    PENDING = "pending"       # 待验收
    PASSED = "passed"         # 通过
    FAILED = "failed"         # 失败


@dataclass
class InteractionStep:
    """交互步骤。"""
    step_number: int
    user_action: str
    system_response: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "user_action": self.user_action,
            "system_response": self.system_response
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InteractionStep":
        return cls(
            step_number=data["step_number"],
            user_action=data["user_action"],
            system_response=data["system_response"]
        )


@dataclass
class AcceptanceCriteria:
    """验收标准。"""
    criteria_id: str
    description: str
    status: AcceptanceCriteriaStatus = AcceptanceCriteriaStatus.PENDING
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "criteria_id": self.criteria_id,
            "description": self.description,
            "status": self.status.value,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AcceptanceCriteria":
        return cls(
            criteria_id=data["criteria_id"],
            description=data["description"],
            status=AcceptanceCriteriaStatus(data.get("status", "pending")),
            notes=data.get("notes", "")
        )


@dataclass
class E2ETestCoverage:
    """E2E 测试覆盖。"""
    test_file: str
    test_case: str
    description: str
    status: str = "pending"  # pending, passed, failed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_file": self.test_file,
            "test_case": self.test_case,
            "description": self.description,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "E2ETestCoverage":
        return cls(
            test_file=data["test_file"],
            test_case=data["test_case"],
            description=data["description"],
            status=data.get("status", "pending")
        )


@dataclass
class ExpectedResult:
    """预期结果。"""
    scenario_type: str  # success, failure
    description: str
    handling: Optional[str] = None  # For failure scenarios

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_type": self.scenario_type,
            "description": self.description,
            "handling": self.handling
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExpectedResult":
        return cls(
            scenario_type=data["scenario_type"],
            description=data["description"],
            handling=data.get("handling")
        )


@dataclass
class UserStory:
    """用户故事。"""
    story_id: str
    title: str
    role: str  # 用户角色
    goal: str  # 希望完成什么
    value: str  # 以便获得什么价值
    preconditions: List[str] = field(default_factory=list)
    interaction_steps: List[InteractionStep] = field(default_factory=list)
    expected_results: List[ExpectedResult] = field(default_factory=list)
    e2e_tests: List[E2ETestCoverage] = field(default_factory=list)
    acceptance_criteria: List[AcceptanceCriteria] = field(default_factory=list)
    status: StoryStatus = StoryStatus.DRAFT
    version: str = "v2.2.0"
    evidence: Optional[str] = None  # 验收证据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "story_id": self.story_id,
            "title": self.title,
            "role": self.role,
            "goal": self.goal,
            "value": self.value,
            "preconditions": self.preconditions,
            "interaction_steps": [s.to_dict() for s in self.interaction_steps],
            "expected_results": [r.to_dict() for r in self.expected_results],
            "e2e_tests": [t.to_dict() for t in self.e2e_tests],
            "acceptance_criteria": [c.to_dict() for c in self.acceptance_criteria],
            "status": self.status.value,
            "version": self.version,
            "evidence": self.evidence,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserStory":
        return cls(
            story_id=data["story_id"],
            title=data["title"],
            role=data["role"],
            goal=data["goal"],
            value=data["value"],
            preconditions=data.get("preconditions", []),
            interaction_steps=[
                InteractionStep.from_dict(s) for s in data.get("interaction_steps", [])
            ],
            expected_results=[
                ExpectedResult.from_dict(r) for r in data.get("expected_results", [])
            ],
            e2e_tests=[
                E2ETestCoverage.from_dict(t) for t in data.get("e2e_tests", [])
            ],
            acceptance_criteria=[
                AcceptanceCriteria.from_dict(c) for c in data.get("acceptance_criteria", [])
            ],
            status=StoryStatus(data.get("status", "draft")),
            version=data.get("version", "v2.2.0"),
            evidence=data.get("evidence"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )

    def to_markdown(self) -> str:
        """转换为 Markdown 格式。"""
        lines = [
            f"## Story {self.story_id}: {self.title}",
            "",
            "### 用户目标",
            f"**作为** {self.role}",
            f"**我希望** {self.goal}",
            f"**以便** {self.value}",
            ""
        ]

        if self.preconditions:
            lines.extend(["### 前置条件", ""])
            for precondition in self.preconditions:
                lines.append(f"- {precondition}")
            lines.append("")

        if self.interaction_steps:
            lines.extend(["### 交互流程", ""])
            lines.append("| 步骤 | 用户操作 | 系统响应 |")
            lines.append("|------|----------|----------|")
            for step in self.interaction_steps:
                lines.append(f"| {step.step_number} | {step.user_action} | {step.system_response} |")
            lines.append("")

        if self.expected_results:
            lines.append("### 预期结果")
            for result in self.expected_results:
                if result.scenario_type == "success":
                    lines.append("**成功场景**:")
                else:
                    lines.append("**失败场景**:")
                lines.append(f"- {result.description}")
                if result.handling:
                    lines.append(f"  - 处理方式: {result.handling}")
            lines.append("")

        if self.e2e_tests:
            lines.extend(["### E2E 测试覆盖", ""])
            lines.append("| 测试用例 | 说明 |")
            lines.append("|----------|------|")
            for test in self.e2e_tests:
                lines.append(f"| {test.test_case} | {test.description} |")
            lines.append("")

        if self.acceptance_criteria:
            lines.extend(["### 验收标准", ""])
            for criteria in self.acceptance_criteria:
                checkbox = "[x]" if criteria.status == AcceptanceCriteriaStatus.PASSED else "[ ]"
                lines.append(f"- {checkbox} {criteria.description}")
            lines.append("")

        return "\n".join(lines)


class StoryManagerError(Exception):
    """用户故事管理异常基类。"""
    pass


class StoryNotFoundError(StoryManagerError):
    """用户故事未找到异常。"""
    pass


class StoryManager:
    """用户故事管理器。"""

    STORIES_FILE = "stories.yaml"

    def __init__(
        self,
        project_path: str,
        stories_file: Optional[str] = None
    ):
        """初始化用户故事管理器。

        Args:
            project_path: 项目路径
            stories_file: 故事数据文件
        """
        self.project_path = Path(project_path)
        self.stories_file = self.project_path / (stories_file or self.STORIES_FILE)
        self.stories: Dict[str, UserStory] = {}
        self._ensure_directories()
        self._load_stories()

    def _ensure_directories(self) -> None:
        """确保目录存在。"""
        self.project_path.mkdir(parents=True, exist_ok=True)

    def _load_stories(self) -> None:
        """加载故事数据。"""
        if self.stories_file.exists():
            try:
                with open(self.stories_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if data and "stories" in data:
                    for story_data in data.get("stories", []):
                        story = UserStory.from_dict(story_data)
                        self.stories[story.story_id] = story
            except Exception as e:
                logger.warning(f"加载用户故事数据失败: {e}")

    def _save_stories(self) -> None:
        """保存故事数据。"""
        data = {
            "stories": [s.to_dict() for s in self.stories.values()],
            "updated_at": datetime.now().isoformat()
        }
        with open(self.stories_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)

    def create_story(
        self,
        title: str,
        role: str,
        goal: str,
        value: str,
        version: Optional[str] = None
    ) -> UserStory:
        """创建用户故事。

        Args:
            title: 故事标题
            role: 用户角色
            goal: 希望完成什么
            value: 以便获得什么价值
            version: 关联版本

        Returns:
            创建的用户故事
        """
        story_id = f"S-{len(self.stories) + 1:03d}"
        story = UserStory(
            story_id=story_id,
            title=title,
            role=role,
            goal=goal,
            value=value,
            version=version or "v2.2.0"
        )
        self.stories[story_id] = story
        self._save_stories()
        logger.info(f"创建用户故事: {story_id} - {title}")
        return story

    def get_story(self, story_id: str) -> UserStory:
        """获取用户故事。

        Args:
            story_id: 故事 ID

        Returns:
            用户故事

        Raises:
            StoryNotFoundError: 故事未找到
        """
        if story_id not in self.stories:
            raise StoryNotFoundError(f"用户故事未找到: {story_id}")
        return self.stories[story_id]

    def list_stories(
        self,
        status: Optional[StoryStatus] = None,
        version: Optional[str] = None
    ) -> List[UserStory]:
        """列出用户故事。

        Args:
            status: 状态过滤
            version: 版本过滤

        Returns:
            用户故事列表
        """
        stories = list(self.stories.values())

        if status:
            stories = [s for s in stories if s.status == status]
        if version:
            stories = [s for s in stories if s.version == version]

        return sorted(stories, key=lambda s: s.story_id)

    def add_precondition(self, story_id: str, precondition: str) -> UserStory:
        """添加前置条件。

        Args:
            story_id: 故事 ID
            precondition: 前置条件

        Returns:
            更新后的故事

        Raises:
            StoryNotFoundError: 故事未找到
        """
        story = self.get_story(story_id)
        story.preconditions.append(precondition)
        story.updated_at = datetime.now().isoformat()
        self._save_stories()
        logger.info(f"添加前置条件: {story_id} - {precondition[:50]}...")
        return story

    def add_interaction_step(
        self,
        story_id: str,
        user_action: str,
        system_response: str
    ) -> UserStory:
        """添加交互步骤。

        Args:
            story_id: 故事 ID
            user_action: 用户操作
            system_response: 系统响应

        Returns:
            更新后的故事

        Raises:
            StoryNotFoundError: 故事未找到
        """
        story = self.get_story(story_id)
        step = InteractionStep(
            step_number=len(story.interaction_steps) + 1,
            user_action=user_action,
            system_response=system_response
        )
        story.interaction_steps.append(step)
        story.updated_at = datetime.now().isoformat()
        self._save_stories()
        logger.info(f"添加交互步骤: {story_id} - 步骤 {step.step_number}")
        return story

    def add_expected_result(
        self,
        story_id: str,
        scenario_type: str,
        description: str,
        handling: Optional[str] = None
    ) -> UserStory:
        """添加预期结果。

        Args:
            story_id: 故事 ID
            scenario_type: 场景类型 (success/failure)
            description: 描述
            handling: 处理方式（失败场景）

        Returns:
            更新后的故事

        Raises:
            StoryNotFoundError: 故事未找到
        """
        story = self.get_story(story_id)
        result = ExpectedResult(
            scenario_type=scenario_type,
            description=description,
            handling=handling
        )
        story.expected_results.append(result)
        story.updated_at = datetime.now().isoformat()
        self._save_stories()
        logger.info(f"添加预期结果: {story_id} - {scenario_type}")
        return story

    def link_e2e_test(
        self,
        story_id: str,
        test_file: str,
        test_case: str,
        description: str
    ) -> UserStory:
        """关联 E2E 测试用例。

        Args:
            story_id: 故事 ID
            test_file: 测试文件
            test_case: 测试用例名
            description: 说明

        Returns:
            更新后的故事

        Raises:
            StoryNotFoundError: 故事未找到
        """
        story = self.get_story(story_id)
        test = E2ETestCoverage(
            test_file=test_file,
            test_case=test_case,
            description=description
        )
        story.e2e_tests.append(test)
        story.updated_at = datetime.now().isoformat()
        self._save_stories()
        logger.info(f"关联E2E测试: {story_id} - {test_case}")
        return story

    def add_acceptance_criteria(
        self,
        story_id: str,
        criteria_id: str,
        description: str
    ) -> UserStory:
        """添加验收标准。

        Args:
            story_id: 故事 ID
            criteria_id: 标准 ID
            description: 标准描述

        Returns:
            更新后的故事

        Raises:
            StoryNotFoundError: 故事未找到
        """
        story = self.get_story(story_id)
        criteria = AcceptanceCriteria(
            criteria_id=criteria_id,
            description=description
        )
        story.acceptance_criteria.append(criteria)
        story.updated_at = datetime.now().isoformat()
        self._save_stories()
        logger.info(f"添加验收标准: {story_id} - {criteria_id}")
        return story

    def update_acceptance_status(
        self,
        story_id: str,
        criteria_id: str,
        status: AcceptanceCriteriaStatus,
        notes: Optional[str] = None
    ) -> UserStory:
        """更新验收标准状态。

        Args:
            story_id: 故事 ID
            criteria_id: 标准 ID
            status: 新状态
            notes: 备注

        Returns:
            更新后的故事

        Raises:
            StoryNotFoundError: 故事未找到
        """
        story = self.get_story(story_id)
        for criteria in story.acceptance_criteria:
            if criteria.criteria_id == criteria_id:
                criteria.status = status
                if notes:
                    criteria.notes = notes
                break
        story.updated_at = datetime.now().isoformat()
        self._save_stories()
        logger.info(f"更新验收状态: {story_id} - {criteria_id} -> {status.value}")
        return story

    def accept_story(self, story_id: str, evidence: str) -> UserStory:
        """标记故事验收通过。

        Args:
            story_id: 故事 ID
            evidence: 验收证据

        Returns:
            更新后的故事

        Raises:
            StoryNotFoundError: 故事未找到
        """
        story = self.get_story(story_id)
        story.status = StoryStatus.ACCEPTED
        story.evidence = evidence
        story.updated_at = datetime.now().isoformat()
        self._save_stories()
        logger.info(f"验收通过: {story_id}")
        return story

    def update_story_status(
        self,
        story_id: str,
        status: StoryStatus
    ) -> UserStory:
        """更新故事状态。

        Args:
            story_id: 故事 ID
            status: 新状态

        Returns:
            更新后的故事

        Raises:
            StoryNotFoundError: 故事未找到
        """
        story = self.get_story(story_id)
        story.status = status
        story.updated_at = datetime.now().isoformat()
        self._save_stories()
        logger.info(f"更新状态: {story_id} -> {status.value}")
        return story

    def get_story_summary(self) -> Dict[str, Any]:
        """获取故事管理摘要。

        Returns:
            摘要信息
        """
        by_status = {}
        by_version = {}

        for story in self.stories.values():
            by_status[story.status.value] = by_status.get(story.status.value, 0) + 1
            by_version[story.version] = by_version.get(story.version, 0) + 1

        return {
            "total_stories": len(self.stories),
            "by_status": by_status,
            "by_version": by_version,
            "accepted_count": len([s for s in self.stories.values() if s.status == StoryStatus.ACCEPTED]),
            "pending_count": len([s for s in self.stories.values() if s.status == StoryStatus.PENDING_ACCEPTANCE])
        }

    def export_stories(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """导出故事数据。

        Args:
            output_path: 输出路径（可选）

        Returns:
            故事数据字典
        """
        data = {
            "stories": [s.to_dict() for s in self.stories.values()],
            "summary": self.get_story_summary(),
            "exported_at": datetime.now().isoformat()
        }

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True)

        return data


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = StoryManager(tmpdir)

        story = manager.create_story(
            title="用户登录",
            role="终端用户",
            goal="使用用户名密码登录系统",
            value="保护账户安全"
        )
        print(f"创建用户故事: {story.story_id}")

        manager.add_precondition(story.story_id, "用户已注册账户")
        manager.add_precondition(story.story_id, "用户知道正确的用户名和密码")

        manager.add_interaction_step(
            story.story_id,
            "输入用户名和密码",
            "系统验证凭据"
        )
        manager.add_interaction_step(
            story.story_id,
            "点击登录按钮",
            "系统重定向到主页"
        )

        manager.add_expected_result(
            story.story_id,
            "success",
            "用户成功登录，显示欢迎信息"
        )
        manager.add_expected_result(
            story.story_id,
            "failure",
            "用户名或密码错误",
            handling="显示错误提示，不跳转页面"
        )

        manager.link_e2e_test(
            story.story_id,
            "test_stories/test_story_S001.py",
            "test_login_success",
            "测试用户登录成功场景"
        )
        manager.link_e2e_test(
            story.story_id,
            "test_stories/test_story_S001.py",
            "test_login_failure",
            "测试用户登录失败场景"
        )

        manager.add_acceptance_criteria(story.story_id, "AC-001", "使用有效凭据可成功登录")
        manager.add_acceptance_criteria(story.story_id, "AC-002", "使用无效凭据显示错误提示")

        print(f"\n用户故事 Markdown:\n{story.to_markdown()}")

        summary = manager.get_story_summary()
        print(f"\n摘要: {summary}")
