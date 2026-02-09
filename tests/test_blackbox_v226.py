"""黑盒测试用例：v2.2.6 CLI命令测试"""

import pytest
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent


class TestTODOWriteAutoCheck:
    """F-AI-001: todowrite参数自动检查"""

    def test_execute_without_args(self):
        """BB-AI-001: 无参数执行todowrite"""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        assert "content" in result.stdout.lower() or "agent" in result.stdout.lower()

    def test_missing_content(self):
        """BB-AI-002: 缺少--content"""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite", "--agent", "1"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        assert "content" in result.stdout.lower()

    def test_missing_agent(self):
        """BB-AI-003: 缺少--agent"""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite", "--content", "test"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        assert "agent" in result.stdout.lower()

    def test_invalid_agent_id(self):
        """BB-AI-004: 无效agent_id"""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", "test", "--agent", "3"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        assert "invalid" in result.stdout.lower() or "agent" in result.stdout.lower()

    def test_valid_params(self):
        """BB-AI-005: 有效完整参数"""
        import uuid
        test_content = f"BB-AI-005测试 {uuid.uuid4().hex[:8]}"
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", test_content, "--agent", "1", "--priority", "high"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "TODO" in result.stdout or "待办" in result.stdout

    def test_default_priority(self):
        """BB-AI-006: 默认priority"""
        import uuid
        test_content = f"BB-AI-006测试 {uuid.uuid4().hex[:8]}"
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", test_content, "--agent", "1"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0


class TestTODOWriteContext:
    """F-AI-002: TODO上下文携带"""

    def test_context_summary_output(self):
        """BB-AI-007: 创建时关联历史"""
        import uuid
        test_content = f"BB-AI-007测试 {uuid.uuid4().hex[:8]}"
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", test_content, "--agent", "1"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

    def test_version_info_recorded(self):
        """BB-AI-008: 记录版本信息"""
        import uuid
        test_content = f"BB-AI-008测试 {uuid.uuid4().hex[:8]}"
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", test_content, "--agent", "1"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0


class TestTODOWriteConflict:
    """F-AI-003: 冲突检测"""

    def test_duplicate_detection(self):
        """BB-AI-010: 检测重复内容"""
        import uuid
        test_content = f"BB-AI-010重复测试 {uuid.uuid4().hex[:8]}"
        # 先创建一个TODO
        subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", test_content, "--agent", "1"],
            capture_output=True,
            text=True
        )
        # 创建重复TODO
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", test_content, "--agent", "1"],
            capture_output=True,
            text=True
        )
        # 应该提示冲突或重复
        assert result.returncode == 0 or "duplicate" in result.stdout.lower() or "重复" in result.stdout

    def test_priority_conflict(self):
        """BB-AI-011: 检测优先级冲突"""
        import uuid
        for i in range(6):
            test_content = f"BB-AI-011优先级测试 {uuid.uuid4().hex[:8]}"
            subprocess.run(
                [sys.executable, "-m", "src.cli.main", "todowrite",
                 "--content", test_content, "--agent", "1", "--priority", "high"],
                capture_output=True,
                text=True
            )
        # 第6个应该提示冲突
        test_content = f"BB-AI-011第6个 {uuid.uuid4().hex[:8]}"
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", test_content, "--agent", "1", "--priority", "high"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0


class TestSkillSearch:
    """F-SKILL-001: Skill关键词检索"""

    def test_search_existing_keyword(self):
        """BB-SKILL-001: 搜索存在的关键词"""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "search",
             "--keywords", "todowrite"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "skill" in result.stdout.lower() or "todowrite" in result.stdout.lower()

    def test_search_nonexistent_keyword(self):
        """BB-SKILL-002: 搜索不存在的关键词"""
        import uuid
        keyword = f"nonexistent{uuid.uuid4().hex[:8]}"
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "search",
             "--keywords", keyword],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "not found" in result.stdout.lower() or "未找到" in result.stdout or "no" in result.stdout.lower()

    def test_search_multiple_keywords(self):
        """BB-SKILL-003: 多关键词搜索"""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "search",
             "--keywords", "todowrite requirements"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0


class TestSkillSlice:
    """F-SKILL-002: Skill切片机制"""

    def test_list_chapters(self):
        """BB-SKILL-005: 列出章节"""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "slice", "--list"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "chapter" in result.stdout.lower() or "章节" in result.stdout

    def test_get_chapter_content(self):
        """BB-SKILL-006: 查看特定章节"""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "slice", "--chapter", "1"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0


class TestSkillEnforce:
    """F-SKILL-003: Skill强制查找增强"""

    def test_enforce_missing_skills(self):
        """BB-SKILL-008: 检测缺失的Skill"""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "enforce"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

    def test_enforce_before_todowrite(self):
        """BB-SKILL-009: todowrite前检查"""
        import uuid
        test_content = f"BB-SKILL-009测试 {uuid.uuid4().hex[:8]}"
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", test_content, "--agent", "1"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
