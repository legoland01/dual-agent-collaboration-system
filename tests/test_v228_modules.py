"""v2.2.8 单元测试"""

import pytest
from pathlib import Path
import tempfile
import shutil


class TestEventDispatcher:
    """EventDispatcher 测试类"""

    def test_register_multiple_event_types(self):
        from src.core.event_dispatcher import EventDispatcher

        dispatcher = EventDispatcher()

        def callback1(event):
            return True

        def callback2(event):
            return True

        dispatcher.register_callback(callback1, ["push", "pull_request"], "multi")
        assert "push" in dispatcher._callbacks
        assert "pull_request" in dispatcher._callbacks
        assert callback1 in dispatcher._callbacks["push"]
        assert callback1 in dispatcher._callbacks["pull_request"]

    def test_register_callback_with_default_name(self):
        from src.core.event_dispatcher import EventDispatcher

        dispatcher = EventDispatcher()

        def my_test_callback(event):
            return True

        callback_id = dispatcher.register_callback(my_test_callback)
        assert callback_id == "my_test_callback"

    def test_dispatch_to_wildcard_callbacks(self):
        from src.core.event_dispatcher import EventDispatcher, DispatchEvent

        dispatcher = EventDispatcher()
        results = []

        def wildcard_callback(event):
            results.append("wildcard")
            return True

        dispatcher.register_callback(wildcard_callback, None, "wildcard")

        event = DispatchEvent(event_type="push", source="github", payload={})
        result = dispatcher.dispatch(event)

        assert len(result.callbacks_results) == 1
        assert result.callbacks_results[0]["callback_name"] == "wildcard"

    def test_dispatch_multiple_callbacks_same_event(self):
        from src.core.event_dispatcher import EventDispatcher, DispatchEvent

        dispatcher = EventDispatcher()
        call_order = []

        def callback1(event):
            call_order.append("callback1")
            return True

        def callback2(event):
            call_order.append("callback2")
            return True

        dispatcher.register_callback(callback1, ["push"], "cb1")
        dispatcher.register_callback(callback2, ["push"], "cb2")

        event = DispatchEvent(event_type="push", source="github", payload={})
        result = dispatcher.dispatch(event)

        assert len(result.callbacks_results) == 2
        assert call_order == ["callback1", "callback2"]

    def test_dispatch_event_without_callbacks(self):
        from src.core.event_dispatcher import EventDispatcher, DispatchEvent

        dispatcher = EventDispatcher()

        event = DispatchEvent(event_type="push", source="github", payload={})
        result = dispatcher.dispatch(event)

        assert len(result.callbacks_results) == 0

    def test_unregister_nonexistent(self):
        from src.core.event_dispatcher import EventDispatcher

        dispatcher = EventDispatcher()

        result = dispatcher.unregister_callback("nonexistent")
        assert result is False

    def test_callback_duration_recorded(self):
        from src.core.event_dispatcher import EventDispatcher, DispatchEvent
        import time

        dispatcher = EventDispatcher()

        def slow_callback(event):
            time.sleep(0.01)
            return True

        dispatcher.register_callback(slow_callback, ["push"], "slow")

        event = DispatchEvent(event_type="push", source="github", payload={})
        result = dispatcher.dispatch(event)

        assert len(result.callbacks_results) == 1
        assert result.callbacks_results[0]["duration_ms"] > 0

    def test_register_callback(self):
        from src.core.event_dispatcher import EventDispatcher, DispatchEvent

        dispatcher = EventDispatcher()

        def test_callback(event):
            return True

        callback_id = dispatcher.register_callback(test_callback, ["push"], "test")
        assert callback_id == "test"
        assert "push" in dispatcher._callbacks
        assert test_callback in dispatcher._callbacks["push"]

    def test_register_wildcard(self):
        from src.core.event_dispatcher import EventDispatcher

        dispatcher = EventDispatcher()

        def wildcard_callback(event):
            return True

        callback_id = dispatcher.register_callback(wildcard_callback, None, "wildcard")
        assert callback_id == "wildcard"
        assert "*" in dispatcher._callbacks

    def test_register_duplicate(self):
        from src.core.event_dispatcher import EventDispatcher

        dispatcher = EventDispatcher()

        def callback1(event):
            return True

        def callback2(event):
            return True

        dispatcher.register_callback(callback1, ["push"], "test")
        with pytest.raises(ValueError):
            dispatcher.register_callback(callback2, ["push"], "test")

    def test_dispatch_event(self):
        from src.core.event_dispatcher import EventDispatcher, DispatchEvent

        dispatcher = EventDispatcher()
        results = []

        def callback1(event):
            results.append("callback1")
            return True

        dispatcher.register_callback(callback1, ["push"], "cb1")

        event = DispatchEvent(
            event_type="push",
            source="github",
            payload={"test": "data"}
        )

        result = dispatcher.dispatch(event)

        assert result.event_type == "push"
        assert len(result.callbacks_results) == 1
        assert result.callbacks_results[0]["callback_name"] == "cb1"
        assert result.callbacks_results[0]["success"] is True

    def test_dispatch_with_error(self):
        from src.core.event_dispatcher import EventDispatcher, DispatchEvent

        dispatcher = EventDispatcher()

        def error_callback(event):
            raise ValueError("Test error")

        dispatcher.register_callback(error_callback, ["push"], "error_cb")

        event = DispatchEvent(event_type="push", source="github", payload={})
        result = dispatcher.dispatch(event)

        assert len(result.callbacks_results) == 1
        assert result.callbacks_results[0]["success"] is False
        assert "Test error" in result.callbacks_results[0]["error"]

    def test_unregister_callback(self):
        from src.core.event_dispatcher import EventDispatcher

        dispatcher = EventDispatcher()

        def callback(event):
            return True

        dispatcher.register_callback(callback, ["push"], "test")
        assert dispatcher.unregister_callback("test") is True
        assert "test" not in dispatcher._callback_names.values()
        assert dispatcher.unregister_callback("nonexistent") is False

    def test_clear_callbacks(self):
        from src.core.event_dispatcher import EventDispatcher

        dispatcher = EventDispatcher()

        def callback(event):
            return True

        dispatcher.register_callback(callback, ["push"], "test")
        dispatcher.clear_callbacks()

        assert len(dispatcher._callbacks) == 0
        assert len(dispatcher._callback_names) == 0

    def test_get_registered_callbacks(self):
        from src.core.event_dispatcher import EventDispatcher

        dispatcher = EventDispatcher()

        def callback1(event):
            return True

        def callback2(event):
            return True

        dispatcher.register_callback(callback1, ["push"], "cb1")
        dispatcher.register_callback(callback2, ["pull_request"], "cb2")

        registered = dispatcher.get_registered_callbacks()

        assert "push" in registered
        assert "cb1" in registered["push"]
        assert "pull_request" in registered
        assert "cb2" in registered["pull_request"]


class TestStateNotifier:
    """StateNotifier 测试类"""

    def test_notify_with_dispatcher_integration(self):
        from src.core.state_notifier import StateNotifier, StateChangeEvent
        from src.core.event_dispatcher import EventDispatcher
        import unittest.mock as mock

        dispatcher = EventDispatcher()
        notifier = StateNotifier(dispatcher=dispatcher)

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            event = StateChangeEvent(
                event_type="todo.created",
                agent_id="agent1",
                details={"todo_id": "TODO-001"}
            )
            notifier.set_default_webhook_url("http://localhost:8080/webhook")
            result = notifier.notify(event)

        assert result is True
        mock_post.assert_called_once()

    def test_notify_with_http_failure(self):
        from src.core.state_notifier import StateNotifier, StateChangeEvent
        import unittest.mock as mock

        notifier = StateNotifier()
        notifier.set_default_webhook_url("http://localhost:8080/webhook")

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 500
            event = StateChangeEvent(
                event_type="todo.created",
                agent_id="agent1",
                details={"todo_id": "TODO-001"}
            )
            result = notifier.notify(event)

        assert result is False

    def test_notify_with_connection_error(self):
        from src.core.state_notifier import StateNotifier, StateChangeEvent
        import requests
        import unittest.mock as mock

        notifier = StateNotifier()
        notifier.set_default_webhook_url("http://localhost:8080/webhook")

        with mock.patch('requests.post') as mock_post:
            mock_post.side_effect = requests.ConnectionError("Connection failed")
            event = StateChangeEvent(
                event_type="todo.created",
                agent_id="agent1",
                details={"todo_id": "TODO-001"}
            )
            result = notifier.notify(event)

        assert result is False

    def test_format_payload_with_special_chars(self):
        from src.core.state_notifier import StateNotifier, StateChangeEvent

        notifier = StateNotifier()
        event = StateChangeEvent(
            event_type="phase.advanced",
            agent_id="agent1",
            details={"from": "requirements", "to": "design"}
        )

        payload = notifier._format_payload(event)

        assert payload["action"] == "phase.advanced"
        assert payload["ref"] == "refs/heads/state-phase-advanced"
        assert payload["oc_collab"]["details"]["from"] == "requirements"
        assert payload["oc_collab"]["details"]["to"] == "design"

    def test_notify_todo_created(self):
        from src.core.state_notifier import StateNotifier
        import unittest.mock as mock

        notifier = StateNotifier()
        notifier.set_default_webhook_url("http://localhost:8080/webhook")

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            result = notifier.notify_todo_created("TODO-001", "Test task", "agent1")

        assert result is True
        mock_post.assert_called_once()

    def test_notify_todo_completed(self):
        from src.core.state_notifier import StateNotifier
        import unittest.mock as mock

        notifier = StateNotifier()
        notifier.set_default_webhook_url("http://localhost:8080/webhook")

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            result = notifier.notify_todo_completed("TODO-001", "Test task", "agent1")

        assert result is True

    def test_notify_signoff_completed(self):
        from src.core.state_notifier import StateNotifier

        notifier = StateNotifier()

        result = notifier.notify_signoff_completed("requirements", "agent1")
        assert result is False

    def test_notify_phase_advanced(self):
        from src.core.state_notifier import StateNotifier

        notifier = StateNotifier()

        result = notifier.notify_phase_advanced("design", "development", "agent1")
        assert result is False

    def test_notify_bug_fixed(self):
        from src.core.state_notifier import StateNotifier

        notifier = StateNotifier()

        result = notifier.notify_bug_fixed("BUG-001", "Test bug", "agent1")
        assert result is False


class TestHMACValidator:
    """HMACValidator 测试类"""

    def test_validate_github_invalid_signature_format(self):
        from src.core.hmac_validator import HMACValidator

        validator = HMACValidator("secret")

        result = validator.validate_github(b"data", "sha1=wrong_format")

        assert result.is_valid is False
        assert "sha256=" in result.error

    def test_validate_github_signature_mismatch(self):
        import hmac
        import hashlib
        from src.core.hmac_validator import HMACValidator

        secret = "test_secret"
        validator = HMACValidator(secret)

        wrong_sig = "sha256=" + hmac.new(
            b"wrong_secret",
            b"data",
            hashlib.sha256
        ).hexdigest()

        result = validator.validate_github(b"data", wrong_sig)

        assert result.is_valid is False
        assert "mismatch" in result.error.lower()

    def test_validate_gitee_missing_token(self):
        from src.core.hmac_validator import HMACValidator

        validator = HMACValidator("secret")

        result = validator.validate_gitee(b"data", "")

        assert result.is_valid is False
        assert "Missing" in result.error

    def test_validate_gitee_token_mismatch(self):
        from src.core.hmac_validator import HMACValidator

        validator = HMACValidator("correct_token")

        result = validator.validate_gitee(b"data", "wrong_token")

        assert result.is_valid is False
        assert "mismatch" in result.error.lower()

    def test_skip_verification_via_env(self):
        import os
        from src.core.hmac_validator import HMACValidator

        os.environ["OC_COLLAB_WEBHOOK_SKIP_VERIFY"] = "true"
        try:
            validator = HMACValidator("any_secret")

            result = validator.validate_github(b"data", "invalid_sig")
            assert result.is_valid is True

            result = validator.validate_gitee(b"data", "wrong_token")
            assert result.is_valid is True
        finally:
            del os.environ["OC_COLLAB_WEBHOOK_SKIP_VERIFY"]

    def test_validate_github_valid(self):
        import hmac
        import hashlib
        from src.core.hmac_validator import HMACValidator

        secret = "test_secret"
        validator = HMACValidator(secret)

        body = b'{"test": "data"}'
        signature = "sha256=" + hmac.new(
            secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()

        result = validator.validate_github(body, signature)

        assert result.is_valid is True
        assert result.platform.value == "github"

    def test_validate_github_invalid(self):
        from src.core.hmac_validator import HMACValidator

        secret = "test_secret"
        validator = HMACValidator(secret)

        body = b'{"test": "data"}'

        result = validator.validate_github(body, "sha256=invalid_signature")

        assert result.is_valid is False
        assert result.platform.value == "github"

    def test_validate_github_missing_signature(self):
        from src.core.hmac_validator import HMACValidator

        validator = HMACValidator("secret")

        result = validator.validate_github(b"data", "")

        assert result.is_valid is False
        assert "Missing" in result.error

    def test_validate_gitee_valid(self):
        from src.core.hmac_validator import HMACValidator

        secret = "test_token"
        validator = HMACValidator(secret)

        result = validator.validate_gitee(b"data", "test_token")

        assert result.is_valid is True
        assert result.platform.value == "gitee"

    def test_validate_gitee_invalid(self):
        from src.core.hmac_validator import HMACValidator

        validator = HMACValidator("secret")

        result = validator.validate_gitee(b"data", "wrong_token")

        assert result.is_valid is False
        assert result.platform.value == "gitee"

    def test_skip_verification(self):
        from src.core.hmac_validator import HMACValidator

        validator = HMACValidator("secret", skip_verification=True)

        result = validator.validate_github(b"data", "invalid")
        assert result.is_valid is True

        result = validator.validate_gitee(b"data", "wrong")
        assert result.is_valid is True

    def test_validate_request_github(self):
        import hmac
        import hashlib
        from src.core.hmac_validator import HMACValidator

        secret = "test_secret"
        validator = HMACValidator(secret)

        body = b'{"test": "data"}'
        signature = "sha256=" + hmac.new(
            secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()

        headers = {"X-Hub-Signature-256": signature}
        result, platform = validator.validate_request(body, headers)

        assert result.is_valid is True
        assert platform.value == "github"

    def test_validate_request_gitee(self):
        from src.core.hmac_validator import HMACValidator

        validator = HMACValidator("token")

        headers = {"X-Gitee-Token": "token"}
        result, platform = validator.validate_request(b"data", headers)

        assert result.is_valid is True
        assert platform.value == "gitee"

    def test_validate_request_no_header(self):
        from src.core.hmac_validator import HMACValidator

        validator = HMACValidator("secret")

        result, platform = validator.validate_request(b"data", {})

        assert result.is_valid is False
        assert platform is None


class TestRulesInitializer:
    """RulesInitializer 测试类"""

    def test_init_nested_dirs(self):
        from src.core.rules_initializer import RulesInitializer

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "nested").mkdir()
            initializer = RulesInitializer(tmpdir)

            Path(tmpdir, "AGENTS.md").write_text("test")

            result = initializer.init()

            assert result.success is True

    def test_init_multiple_times_idempotent(self):
        from src.core.rules_initializer import RulesInitializer

        with tempfile.TemporaryDirectory() as tmpdir:
            initializer = RulesInitializer(tmpdir)

            result1 = initializer.init()
            result2 = initializer.init()

            assert result1.success is True
            assert result2.success is True
            assert len(result2.created_files) < len(result1.created_files)

    def test_init_creates_dirs(self):
        from src.core.rules_initializer import RulesInitializer

        with tempfile.TemporaryDirectory() as tmpdir:
            initializer = RulesInitializer(tmpdir)
            result = initializer.init()

            assert result.success is True
            assert "skills/" in result.created_files
            assert "docs/00-memos/" in result.created_files

    def test_init_creates_files(self):
        from src.core.rules_initializer import RulesInitializer

        with tempfile.TemporaryDirectory() as tmpdir:
            initializer = RulesInitializer(tmpdir)
            result = initializer.init()

            assert "AGENTS.md" in result.created_files
            assert "skills/oc_collab_deployment_guide/content.md" in result.created_files

    def test_init_skips_existing(self):
        from src.core.rules_initializer import RulesInitializer

        with tempfile.TemporaryDirectory() as tmpdir:
            initializer = RulesInitializer(tmpdir)

            Path(tmpdir, "AGENTS.md").write_text("existing")

            result = initializer.init()

            assert "AGENTS.md" in result.skipped_files

    def test_init_force_overwrites(self):
        from src.core.rules_initializer import RulesInitializer

        with tempfile.TemporaryDirectory() as tmpdir:
            initializer = RulesInitializer(tmpdir)

            Path(tmpdir, "AGENTS.md").write_text("existing")

            result = initializer.init(force=True)

            assert "AGENTS.md" in result.created_files

    def test_check_status(self):
        from src.core.rules_initializer import RulesInitializer

        with tempfile.TemporaryDirectory() as tmpdir:
            initializer = RulesInitializer(tmpdir)
            initializer.init()

            status = initializer.check_status()

            assert "AGENTS.md" in status["initialized"]
            assert "skills/" in status["initialized"]

    def test_reset_requires_force(self):
        from src.core.rules_initializer import RulesInitializer

        with tempfile.TemporaryDirectory() as tmpdir:
            initializer = RulesInitializer(tmpdir)
            initializer.init()

            result = initializer.reset()

            assert result.success is False

    def test_reset_with_force(self):
        from src.core.rules_initializer import RulesInitializer

        with tempfile.TemporaryDirectory() as tmpdir:
            initializer = RulesInitializer(tmpdir)
            initializer.init()

            result = initializer.reset(force=True)

            assert result.success is True
            assert len(result.created_files) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
