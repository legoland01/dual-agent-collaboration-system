"""测试用例：v2.2.6 F-AI 智能TODO系统模块"""

import pytest
from pathlib import Path
from src.core.auto_checker import AutoChecker, ValidationError
from src.core.context_carrier import ContextCarrier, TodoContext
from src.core.conflict_detector import ConflictDetector, ConflictResult


PROJECT_ROOT = Path(__file__).parent.parent


class TestAutoChecker:
    """AutoChecker 测试类"""

    def test_validate_content_success(self):
        """测试正常内容验证"""
        checker = AutoChecker()
        result = checker.validate_content("完成设计文档")
        assert result == "完成设计文档"

    def test_validate_content_empty(self):
        """测试空内容验证"""
        checker = AutoChecker()
        with pytest.raises(ValidationError) as exc_info:
            checker.validate_content("")
        assert "不能为空" in str(exc_info.value)

    def test_validate_content_whitespace_only(self):
        """测试仅空白字符内容"""
        checker = AutoChecker()
        with pytest.raises(ValidationError) as exc_info:
            checker.validate_content("   ")
        assert "不能为空" in str(exc_info.value)

    def test_validate_agent_id_valid(self):
        """测试有效Agent ID"""
        checker = AutoChecker()
        assert checker.validate_agent_id("1") == "1"
        assert checker.validate_agent_id("2") == "2"

    def test_validate_agent_id_invalid(self):
        """测试无效Agent ID"""
        checker = AutoChecker()
        with pytest.raises(ValidationError) as exc_info:
            checker.validate_agent_id("3")
        assert "无效的 Agent ID" in str(exc_info.value)

    def test_validate_agent_id_none(self):
        """测试None Agent ID"""
        checker = AutoChecker()
        assert checker.validate_agent_id(None) is None

    def test_validate_priority_valid(self):
        """测试有效优先级"""
        checker = AutoChecker()
        assert checker.validate_priority("high") == "high"
        assert checker.validate_priority("medium") == "medium"
        assert checker.validate_priority("low") == "low"

    def test_validate_priority_invalid(self):
        """测试无效优先级"""
        checker = AutoChecker()
        assert checker.validate_priority("P0") == "medium"  # 默认值

    def test_check_all_valid(self):
        """测试完整参数检查 - 全部有效"""
        checker = AutoChecker()
        result = checker.check_all("完成设计", "1", "high")

        assert result["valid"] is True
        assert result["content"] == "完成设计"
        assert result["agent_id"] == "1"
        assert result["priority"] == "high"
        assert len(result["errors"]) == 0

    def test_check_all_missing_agent(self):
        """测试完整参数检查 - 缺少agent"""
        checker = AutoChecker()
        result = checker.check_all("完成设计", None, "high")

        assert result["valid"] is True
        assert result["agent_id"] is None
        assert len(result["warnings"]) == 1
        assert "未指定 --agent" in result["warnings"][0]

    def test_check_all_empty_content(self):
        """测试完整参数检查 - 空内容"""
        checker = AutoChecker()
        result = checker.check_all("", "1", "high")

        assert result["valid"] is False
        assert len(result["errors"]) == 1


class TestContextCarrier:
    """ContextCarrier 测试类"""

    def test_generate_context_summary_no_history(self):
        """测试无历史时摘要生成"""
        carrier = ContextCarrier(str(PROJECT_ROOT))

        with pytest.MonkeyPatch.context() as m:
            m.setattr(carrier, 'load_history', lambda n: [])

            summary = carrier.generate_context_summary("新任务")

            assert "新任务" in summary
            assert "暂无历史任务" in summary

    def test_generate_context_summary_with_history(self):
        """测试有历史时摘要生成"""
        carrier = ContextCarrier(str(PROJECT_ROOT))

        with pytest.MonkeyPatch.context() as m:
            m.setattr(carrier, 'load_history', lambda n: [
                {"id": "TODO-001", "content": "旧任务1", "status": "completed"},
                {"id": "TODO-002", "content": "旧任务2", "status": "completed"}
            ])

            summary = carrier.generate_context_summary("新任务")

            assert "新任务" in summary
            assert "历史任务" in summary
            assert "TODO-002" in summary

    def test_get_version_info_no_state(self):
        """测试无状态文件时版本信息"""
        carrier = ContextCarrier("/tmp/nonexistent")

        with pytest.MonkeyPatch.context() as m:
            m.setattr(carrier, 'state_file', Path("/tmp/nonexistent/state.yaml"))

            info = carrier.get_version_info()
            assert info["version"] == "unknown"

    def test_build_context(self):
        """测试构建上下文"""
        carrier = ContextCarrier(str(PROJECT_ROOT))

        with pytest.MonkeyPatch.context() as m:
            m.setattr(carrier, 'load_history', lambda n: [])
            m.setattr(carrier, 'get_version_info', lambda: {"version": "2.2.6", "phase": "development"})

            context = carrier.build_context("TODO-001", "测试任务", "1", "high")

            assert isinstance(context, TodoContext)
            assert context.todo_id == "TODO-001"
            assert context.content == "测试任务"
            assert context.agent_id == "1"
            assert context.priority == "high"


class TestConflictDetector:
    """ConflictDetector 测试类"""

    def test_detect_duplicate_no_duplicate(self):
        """测试无重复检测"""
        detector = ConflictDetector(str(PROJECT_ROOT))

        todos = [
            {"id": "TODO-001", "content": "任务1", "status": "pending"},
            {"id": "TODO-002", "content": "任务2", "status": "pending"}
        ]

        result = detector.detect_duplicate("新任务", todos)
        assert len(result) == 0

    def test_detect_duplicate_found(self):
        """测试发现重复"""
        detector = ConflictDetector(str(PROJECT_ROOT))

        todos = [
            {"id": "TODO-001", "content": "重复任务", "status": "pending"}
        ]

        result = detector.detect_duplicate("重复任务", todos)
        assert len(result) == 1
        assert result[0]["type"] == "duplicate"

    def test_detect_duplicate_completed_excluded(self):
        """测试已完成任务不计入重复"""
        detector = ConflictDetector(str(PROJECT_ROOT))

        todos = [
            {"id": "TODO-001", "content": "已完成任务", "status": "completed"}
        ]

        result = detector.detect_duplicate("已完成任务", todos)
        assert len(result) == 0

    def test_detect_priority_conflict_no_conflict(self):
        """测试无优先级冲突"""
        detector = ConflictDetector(str(PROJECT_ROOT))

        todos = [
            {"id": "TODO-001", "content": "任务1", "status": "pending", "priority": "high"},
            {"id": "TODO-002", "content": "任务2", "status": "pending", "priority": "medium"}
        ]

        result = detector.detect_priority_conflict("high", todos)
        assert len(result) == 0

    def test_detect_priority_conflict_found(self):
        """测试发现优先级冲突"""
        detector = ConflictDetector(str(PROJECT_ROOT))

        todos = [
            {"id": "TODO-001", "content": f"任务{i}", "status": "pending", "priority": "high"}
            for i in range(6)
        ]

        result = detector.detect_priority_conflict("high", todos)
        assert len(result) == 1
        assert result[0]["type"] == "priority"

    def test_detect_all_no_conflict(self):
        """测试完整冲突检测 - 无冲突"""
        detector = ConflictDetector(str(PROJECT_ROOT))

        with pytest.MonkeyPatch.context() as m:
            m.setattr(detector, 'load_todos', lambda: [
                {"id": "TODO-001", "content": "任务1", "status": "pending", "priority": "medium"}
            ])

            result = detector.detect_all("新任务", "high", "1")

            assert result.has_conflict is False
            assert len(result.conflicts) == 0

    def test_detect_all_with_conflict(self):
        """测试完整冲突检测 - 有冲突"""
        detector = ConflictDetector(str(PROJECT_ROOT))

        with pytest.MonkeyPatch.context() as m:
            m.setattr(detector, 'load_todos', lambda: [
                {"id": "TODO-001", "content": "重复任务", "status": "pending", "priority": "high"}
            ])

            result = detector.detect_all("重复任务", "high", "1")

            assert result.has_conflict is True
            assert len(result.conflicts) == 1
            assert len(result.suggestions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
