"""v2.2.9 单元测试"""

import pytest
from pathlib import Path
import tempfile
import shutil
import unittest.mock as mock


class TestWebhookEnhancer:
    """WebhookEnhancer 测试类"""

    def test_generate_webhook_id(self):
        from src.core.webhook_enhancer import WebhookEnhancer

        enhancer = WebhookEnhancer()
        webhook_id = enhancer.generate_webhook_id()

        assert webhook_id is not None
        assert len(webhook_id) == 36

    def test_send_with_retry_success(self):
        from src.core.webhook_enhancer import WebhookEnhancer

        enhancer = WebhookEnhancer()

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            notification = enhancer.send_with_retry(
                "http://localhost:8080/webhook",
                {"test": "data"},
                "test.event"
            )

        assert notification.status == "sent"
        assert notification.event_type == "test.event"

    def test_send_with_retry_failure(self):
        from src.core.webhook_enhancer import WebhookEnhancer
        import requests

        enhancer = WebhookEnhancer()

        with mock.patch('requests.post') as mock_post:
            mock_post.side_effect = requests.ConnectionError("Connection failed")
            notification = enhancer.send_with_retry(
                "http://localhost:8080/webhook",
                {"test": "data"},
                "test.event"
            )

        assert notification.status == "failed"

    def test_get_stats(self):
        from src.core.webhook_enhancer import WebhookEnhancer

        enhancer = WebhookEnhancer()
        stats = enhancer.get_stats()

        assert stats is not None
        assert hasattr(stats, 'total')
        assert hasattr(stats, 'sent')
        assert hasattr(stats, 'failed')


class TestAutoBugDetector:
    """AutoBugDetector 测试类"""

    def test_init_with_state_manager(self):
        from src.core.auto_bug_detector import AutoBugDetector

        class MockStateManager:
            def load_state(self):
                return {"todos": []}

        detector = AutoBugDetector(state_manager=MockStateManager())
        assert detector.state_manager is not None

    def test_init_without_state_manager(self):
        from src.core.auto_bug_detector import AutoBugDetector

        detector = AutoBugDetector()
        assert detector.state_manager is None

    def test_check_command_result_success(self):
        from src.core.auto_bug_detector import AutoBugDetector

        detector = AutoBugDetector()
        result = detector.check_command_result("test_command", {"success": True, "return_code": 0})

        assert result == []

    def test_check_command_result_failure(self):
        from src.core.auto_bug_detector import AutoBugDetector

        detector = AutoBugDetector()
        result = detector.check_command_result(
            "test_command",
            {"success": False, "error": "Test error", "return_code": 1}
        )

        assert len(result) == 1
        assert result[0].bug_type == "COMMAND_FAILED"

    def test_generate_bug_report(self):
        from src.core.auto_bug_detector import AutoBugDetector, BugReport

        detector = AutoBugDetector()
        bug = BugReport(
            bug_id="BUG-20260214-001",
            bug_type="COMMAND_FAILED",
            description="Test bug description",
            related_todo="TODO-001"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            detector.memos_path = Path(tmpdir)
            file_path = detector.generate_bug_report(bug)

            assert Path(file_path).exists()
            assert "BUG-20260214-001" in Path(file_path).name


class TestComplianceEnforcer:
    """ComplianceEnforcer 测试类"""

    def test_init_agent1(self):
        from src.core.compliance_enforcer import ComplianceEnforcer, AgentRole

        enforcer = ComplianceEnforcer(agent_id=1)
        assert enforcer.agent_role == AgentRole.AGENT_1

    def test_init_agent2(self):
        from src.core.compliance_enforcer import ComplianceEnforcer, AgentRole

        enforcer = ComplianceEnforcer(agent_id=2)
        assert enforcer.agent_role == AgentRole.AGENT_2

    def test_check_agent1_todowrite_blocked(self):
        from src.core.compliance_enforcer import ComplianceEnforcer

        enforcer = ComplianceEnforcer(agent_id=1)
        result = enforcer.check("todowrite")

        assert result.allowed is False
        assert "Agent1禁止执行todowrite" in result.message

    def test_check_agent2_todowrite_allowed(self):
        from src.core.compliance_enforcer import ComplianceEnforcer

        enforcer = ComplianceEnforcer(agent_id=2)
        result = enforcer.check("todowrite")

        assert result.allowed is True

    def test_check_other_command_agent1(self):
        from src.core.compliance_enforcer import ComplianceEnforcer

        enforcer = ComplianceEnforcer(agent_id=1)
        result = enforcer.check("some_other_command")

        assert result.allowed is True

    def test_get_violations(self):
        from src.core.compliance_enforcer import ComplianceEnforcer

        enforcer = ComplianceEnforcer(agent_id=1)
        violations = enforcer.get_violations()

        assert isinstance(violations, list)

    def test_generate_report(self):
        from src.core.compliance_enforcer import ComplianceEnforcer

        enforcer = ComplianceEnforcer(agent_id=1)
        report = enforcer.generate_report()

        assert report is not None
        assert "合规报告" in report


class TestRulesAutoLoader:
    """RulesAutoLoader 测试类"""

    def test_init_with_project_path(self):
        from src.core.rules_auto_loader import RulesAutoLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            loader = RulesAutoLoader(project_path=tmpdir)
            assert loader.project_path == Path(tmpdir)

    def test_init_default_path(self):
        from src.core.rules_auto_loader import RulesAutoLoader

        loader = RulesAutoLoader()
        assert loader.project_path == Path.cwd()

    def test_load_default_rules(self):
        from src.core.rules_auto_loader import RulesAutoLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            loader = RulesAutoLoader(project_path=tmpdir)
            result = loader.load_default_rules(force=True)

            assert "loaded" in result
            assert "skipped" in result

    def test_check_rules_status(self):
        from src.core.rules_auto_loader import RulesAutoLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            loader = RulesAutoLoader(project_path=tmpdir)
            status = loader.check_rules_status()

            assert "initialized" in status
            assert "missing" in status


class TestDeployDocSync:
    """DeployDocSync 测试类"""

    def test_init_with_project_path(self):
        from src.core.deploy_doc_sync import DeployDocSync

        with tempfile.TemporaryDirectory() as tmpdir:
            sync = DeployDocSync(project_path=tmpdir)
            assert sync.project_path == Path(tmpdir)

    def test_init_default_path(self):
        from src.core.deploy_doc_sync import DeployDocSync

        sync = DeployDocSync()
        assert sync.project_path == Path.cwd()

    def test_check_docs_sync_v228(self):
        from src.core.deploy_doc_sync import DeployDocSync

        sync = DeployDocSync()
        result = sync.check_docs_sync("2.2.8")

        assert "checks" in result
        assert "ready" in result

    def test_sync_changelog(self):
        from src.core.deploy_doc_sync import DeployDocSync

        with tempfile.TemporaryDirectory() as tmpdir:
            sync = DeployDocSync(project_path=tmpdir)
            success = sync.sync_changelog("2.2.9", ["Test change"])

            assert success is True
            assert sync.changelog_path.exists()


class TestStateNotifierWebhookIntegration:
    """StateNotifier Webhook集成测试类"""

    def test_todowrite_sends_webhook(self):
        from src.core.state_notifier import StateNotifier, StateChangeEvent
        import unittest.mock as mock

        notifier = StateNotifier()

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            notifier.set_default_webhook_url("http://localhost:8080/webhook")

            event = StateChangeEvent(
                event_type="todo.created",
                agent_id="agent1",
                details={"todo_id": "TODO-001", "content": "Test task"}
            )
            result = notifier.notify(event)

        assert result is True
        mock_post.assert_called_once()

    def test_signoff_sends_webhook(self):
        from src.core.state_notifier import StateNotifier, StateChangeEvent
        import unittest.mock as mock

        notifier = StateNotifier()

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            notifier.set_default_webhook_url("http://localhost:8080/webhook")

            event = StateChangeEvent(
                event_type="signoff.completed",
                agent_id="agent1",
                details={"phase": "requirements", "signer": "agent2"}
            )
            result = notifier.notify(event)

        assert result is True
        mock_post.assert_called_once()

    def test_phase_advance_sends_webhook(self):
        from src.core.state_notifier import StateNotifier, StateChangeEvent
        import unittest.mock as mock

        notifier = StateNotifier()

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            notifier.set_default_webhook_url("http://localhost:8080/webhook")

            event = StateChangeEvent(
                event_type="phase.advanced",
                agent_id="agent1",
                details={"from": "requirements", "to": "design"}
            )
            result = notifier.notify(event)

        assert result is True
        mock_post.assert_called_once()


class TestCLIComplianceEnforcement:
    """CLI合规性强制测试类"""

    def test_agent1_todowrite_blocked(self):
        from src.core.compliance_enforcer import ComplianceEnforcer

        enforcer = ComplianceEnforcer(agent_id=1)
        result = enforcer.check("oc-collab todowrite --content 'test'")

        assert result.allowed is False

    def test_agent2_todowrite_allowed(self):
        from src.core.compliance_enforcer import ComplianceEnforcer

        enforcer = ComplianceEnforcer(agent_id=2)
        result = enforcer.check("oc-collab todowrite --content 'test'")

        assert result.allowed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
