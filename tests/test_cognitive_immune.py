"""CognitiveImmuneSystem 单元测试。"""
import pytest
import tempfile
import os
from pathlib import Path


class TestImmuneResponse:
    """ImmuneResponse 测试。"""

    def test_immune_response_creation(self):
        """测试免疫响应创建。"""
        from src.core.cognitive_immune import ImmuneResponse

        response = ImmuneResponse(
            detected=True,
            response_type="confusion",
            message="检测到困惑信号",
            suggestions=["建议1", "建议2"]
        )

        assert response.detected is True
        assert response.response_type == "confusion"
        assert len(response.suggestions) == 2


class TestConfusionDetector:
    """ConfusionDetector 测试。"""

    def setup_method(self):
        """创建临时目录。"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """清理临时目录。"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_confusion_signal(self):
        """测试检测困惑信号。"""
        from src.core.cognitive_immune import ConfusionDetector

        detector = ConfusionDetector()
        response = detector.detect("我不明白这个任务是什么")

        assert response.detected is True
        assert response.response_type == "confusion"

    def test_detect_multiple_confusion_signals(self):
        """测试检测多个困惑信号。"""
        from src.core.cognitive_immune import ConfusionDetector

        detector = ConfusionDetector()
        response = detector.detect("我有点困惑，这个怎么做？应该怎么做？")

        assert response.detected is True

    def test_no_confusion_signal(self):
        """测试未检测到困惑信号。"""
        from src.core.cognitive_immune import ConfusionDetector

        detector = ConfusionDetector()
        response = detector.detect("我来实现这个功能，代码已经写好了")

        assert response.detected is False
        assert response.response_type == "none"

    def test_is_confused(self):
        """测试快速检查困惑信号。"""
        from src.core.cognitive_immune import ConfusionDetector

        detector = ConfusionDetector()

        assert detector.is_confused("我不明白") is True
        assert detector.is_confused("代码已完成") is False


class TestResponsibilityDetector:
    """ResponsibilityDetector 测试。"""

    def test_check_responsibility_agent1_forbidden(self):
        """测试 Agent1 禁止操作。"""
        from src.core.cognitive_immune import ResponsibilityDetector

        detector = ResponsibilityDetector()
        can_do, message = detector.check_responsibility("agent1", "直接修改代码")

        assert can_do is False
        assert "职责范围" in message

    def test_check_responsibility_agent2_allowed(self):
        """测试 Agent2 允许操作。"""
        from src.core.cognitive_immune import ResponsibilityDetector

        detector = ResponsibilityDetector()
        can_do, message = detector.check_responsibility("agent2", "编写单元测试")

        assert can_do is True

    def test_check_responsibility_unknown_agent(self):
        """测试未知 Agent。"""
        from src.core.cognitive_immune import ResponsibilityDetector

        detector = ResponsibilityDetector()
        can_do, message = detector.check_responsibility("agent3", "执行操作")

        assert can_do is False
        assert "未知 Agent" in message

    def test_get_responsibilities_agent1(self):
        """测试获取 Agent1 职责。"""
        from src.core.cognitive_immune import ResponsibilityDetector

        detector = ResponsibilityDetector()
        resp = detector.get_responsibilities("agent1")

        assert "产品经理" in resp["roles"]
        assert len(resp["responsibilities"]) > 0

    def test_get_responsibilities_unknown(self):
        """测试获取未知 Agent 职责。"""
        from src.core.cognitive_immune import ResponsibilityDetector

        detector = ResponsibilityDetector()
        resp = detector.get_responsibilities("unknown")

        assert resp == {}


class TestSessionStarter:
    """SessionStarter 测试。"""

    def setup_method(self):
        """创建临时目录。"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """清理临时目录。"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_welcome_message_agent1(self):
        """测试生成欢迎消息（Agent1）。"""
        from src.core.cognitive_immune import SessionStarter

        starter = SessionStarter(self.temp_dir)
        message = starter.get_welcome_message("agent1")

        assert "agent1" in message
        assert "职责" in message
        assert "oc-collab status" in message

    def test_get_welcome_message_agent2(self):
        """测试生成欢迎消息（Agent2）。"""
        from src.core.cognitive_immune import SessionStarter

        starter = SessionStarter(self.temp_dir)
        message = starter.get_welcome_message("agent2")

        assert "agent2" in message
        assert "编写单元测试" in message

    def test_display_welcome(self):
        """测试显示欢迎消息。"""
        from src.core.cognitive_immune import SessionStarter

        starter = SessionStarter(self.temp_dir)
        message = starter.display_welcome("agent1")

        assert "=== agent1 ===" in message

    def test_get_responsibilities(self):
        """测试获取职责定义。"""
        from src.core.cognitive_immune import SessionStarter

        starter = SessionStarter(self.temp_dir)
        resp = starter._get_responsibilities("agent1")

        assert "编写需求文档" in resp["responsibilities"][0]


class TestSkillLoader:
    """SkillLoader 测试。"""

    def setup_method(self):
        """创建临时目录。"""
        self.temp_dir = tempfile.mkdtemp()
        self.skills_dir = Path(self.temp_dir) / "skills"
        self.skills_dir.mkdir()

    def teardown_method(self):
        """清理临时目录。"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_collaboration_guide_not_exists(self):
        """测试加载不存在的协作指南。"""
        from src.core.cognitive_immune import SkillLoader

        loader = SkillLoader(self.temp_dir)
        result = loader.load_collaboration_guide()

        assert result["loaded"] is False
        assert "不存在" in result["message"]

    def test_load_collaboration_guide_exists(self):
        """测试加载存在的协作指南。"""
        from src.core.cognitive_immune import SkillLoader

        guide_file = self.skills_dir / "collaboration_guide.md"
        with open(guide_file, 'w') as f:
            f.write("# 协作指南\n\n## Agent 职责\n")

        loader = SkillLoader(self.temp_dir)
        result = loader.load_collaboration_guide()

        assert result["loaded"] is True
        assert "协作指南" in result["content"]

    def test_list_skills_empty(self):
        """测试列出空 Skills。"""
        from src.core.cognitive_immune import SkillLoader

        loader = SkillLoader(self.temp_dir)
        skills = loader.list_skills()

        assert skills == []

    def test_list_skills_with_content(self):
        """测试列出 Skills（带内容）。"""
        from src.core.cognitive_immune import SkillLoader

        guide_file = self.skills_dir / "collaboration_guide.md"
        with open(guide_file, 'w') as f:
            f.write("# 协作指南")

        loader = SkillLoader(self.temp_dir)
        skills = loader.list_skills()

        assert "collaboration_guide.md" in skills


class TestCognitiveImmuneSystem:
    """CognitiveImmuneSystem 测试。"""

    def setup_method(self):
        """创建临时目录。"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """清理临时目录。"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_analyze_message_confusion(self):
        """测试分析消息（困惑）。"""
        from src.core.cognitive_immune import CognitiveImmuneSystem

        system = CognitiveImmuneSystem(self.temp_dir)
        response = system.analyze_message("agent1", "我不明白这个任务")

        assert response.detected is True
        assert len(response.suggestions) > 0

    def test_analyze_message_normal(self):
        """测试分析消息（正常）。"""
        from src.core.cognitive_immune import CognitiveImmuneSystem

        system = CognitiveImmuneSystem(self.temp_dir)
        response = system.analyze_message("agent2", "我来实现这个功能")

        assert response.detected is False


class TestSkillLoaderWithError:
    """SkillLoader 错误处理测试。"""

    def setup_method(self):
        """创建临时目录。"""
        self.temp_dir = tempfile.mkdtemp()
        self.skills_dir = Path(self.temp_dir) / "skills"
        self.skills_dir.mkdir()

    def teardown_method(self):
        """清理临时目录。"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_collaboration_guide_with_error(self):
        """测试加载协作指南时出错。"""
        from src.core.cognitive_immune import SkillLoader

        guide_file = self.skills_dir / "collaboration_guide.md"
        with open(guide_file, 'w') as f:
            f.write("# 协作指南")

        import shutil
        shutil.rmtree(self.skills_dir)

        loader = SkillLoader(self.temp_dir)
        result = loader.load_collaboration_guide()

        assert result["loaded"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
