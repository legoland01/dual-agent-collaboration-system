"""v2.2.10 单元测试"""

import pytest
from pathlib import Path
import tempfile
import unittest.mock as mock
from datetime import datetime


class TestTodoQueueManager:
    """TodoQueueManager 测试类"""

    def test_add_and_get(self):
        """测试添加和获取"""
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            item = TodoQueueItem(
                id="TODO-TEST-001",
                content="测试TODO",
                from_agent="agent1",
                to_agent="agent2",
                priority="high",
                created_at="2026-02-14T10:00:00Z"
            )

            result = manager.add(item)
            assert result is True

            queue_file = Path(f"{tmpdir}/test_queue.yaml")
            assert queue_file.exists()

    def test_add_duplicate(self):
        """测试添加重复TODO"""
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            item = TodoQueueItem(
                id="TODO-TEST-001",
                content="测试TODO",
                from_agent="agent1",
                to_agent="agent2",
                priority="high",
                created_at="2026-02-14T10:00:00Z"
            )

            manager.add(item)
            result = manager.add(item)
            assert result is False

    def test_mark_read(self):
        """测试标记已读"""
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            item = TodoQueueItem(
                id="TODO-TEST-001",
                content="测试TODO",
                from_agent="agent1",
                to_agent="agent2",
                priority="high",
                created_at="2026-02-14T10:00:00Z"
            )

            manager.add(item)

            result = manager.mark_read("TODO-TEST-001")
            assert result is True

    def test_mark_read_not_found(self):
        """测试标记不存在的TODO"""
        from src.core.todo_queue_manager import TodoQueueManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            result = manager.mark_read("TODO-NOT-EXIST")
            assert result is False

    def test_get_all(self):
        """测试获取所有TODO"""
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            item1 = TodoQueueItem(
                id="TODO-001",
                content="TODO 1",
                from_agent="agent1",
                to_agent="agent2",
                priority="high",
                created_at="2026-02-14T10:00:00Z"
            )
            item2 = TodoQueueItem(
                id="TODO-002",
                content="TODO 2",
                from_agent="agent1",
                to_agent="agent2",
                priority="medium",
                created_at="2026-02-14T10:30:00Z"
            )

            manager.add(item1)
            manager.add(item2)

            all_todos = manager.get_all()
            assert len(all_todos) == 2

    def test_get_all(self):
        """测试获取所有TODO"""
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            item1 = TodoQueueItem(
                id="TODO-001",
                content="TODO 1",
                from_agent="agent1",
                to_agent="agent2",
                priority="high",
                created_at="2026-02-14T10:00:00Z"
            )
            item2 = TodoQueueItem(
                id="TODO-002",
                content="TODO 2",
                from_agent="agent1",
                to_agent="agent2",
                priority="medium",
                created_at="2026-02-14T10:30:00Z"
            )

            manager.add(item1)
            manager.add(item2)

            all_todos = manager.get_all()
            assert len(all_todos) == 2

    def test_get_stats(self):
        """测试获取统计"""
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            stats = manager.get_stats()
            assert stats.total == 0
            assert stats.unread == 0

    def test_cleanup(self):
        """测试清理"""
        from src.core.todo_queue_manager import TodoQueueManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            count = manager.cleanup(days=1)
            assert count == 0

    def test_delete(self):
        """测试删除"""
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            item = TodoQueueItem(
                id="TODO-TEST-001",
                content="测试TODO",
                from_agent="agent1",
                to_agent="agent2",
                priority="high",
                created_at="2026-02-14T10:00:00Z"
            )

            manager.add(item)

            result = manager.delete("TODO-TEST-001")
            assert result is True

            result = manager.delete("TODO-TEST-001")
            assert result is False

    def test_mark_all_read(self):
        """测试标记所有已读"""
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            item1 = TodoQueueItem(
                id="TODO-001",
                content="TODO 1",
                from_agent="agent1",
                to_agent="agent2",
                priority="high",
                created_at="2026-02-14T10:00:00Z"
            )
            item2 = TodoQueueItem(
                id="TODO-002",
                content="TODO 2",
                from_agent="agent1",
                to_agent="agent2",
                priority="medium",
                created_at="2026-02-14T10:30:00Z"
            )

            manager.add(item1)
            manager.add(item2)

            count = manager.mark_all_read()
            assert count == 2

            unread = manager.get_unread()
            assert len(unread) == 0

    def test_clear(self):
        """测试清空队列"""
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            item = TodoQueueItem(
                id="TODO-001",
                content="TODO 1",
                from_agent="agent1",
                to_agent="agent2",
                priority="high",
                created_at="2026-02-14T10:00:00Z"
            )

            manager.add(item)
            count = manager.clear()
            assert count == 1

            all_todos = manager.get_all()
            assert len(all_todos) == 0


class TestAgentStartupChecker:
    """AgentStartupChecker 测试类"""

    def test_init(self):
        """测试初始化"""
        from src.core.agent_startup_checker import AgentStartupChecker, StartupConfig

        checker = AgentStartupChecker("agent1", StartupConfig(auto_display=False))
        assert checker.agent_id == "agent1"

    def test_run_no_unread(self):
        """测试无未读"""
        from src.core.agent_startup_checker import AgentStartupChecker, StartupConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            from src.core.todo_queue_manager import TodoQueueManager
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            checker = AgentStartupChecker("agent1", StartupConfig(auto_display=False))
            checker.queue_manager = manager

            result = checker.run()
            assert result.has_unread_todos is False

    def test_run_with_unread(self):
        """测试有未读"""
        from src.core.agent_startup_checker import AgentStartupChecker, StartupConfig
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            item = TodoQueueItem(
                id="TODO-001",
                content="高优先级任务",
                from_agent="agent1",
                to_agent="agent2",
                priority="high",
                created_at="2026-02-14T10:00:00Z"
            )
            manager.add(item)

            checker = AgentStartupChecker("agent2", StartupConfig(auto_display=False))
            checker.queue_manager = manager

            result = checker.run()
            assert result.has_unread_todos is True
            assert result.unread_count == 1
            assert result.todos[0]["id"] == "TODO-001"

    def test_suggest_action_with_unread(self):
        """测试建议行动（有未读）"""
        from src.core.agent_startup_checker import AgentStartupChecker, StartupConfig
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            item = TodoQueueItem(
                id="TODO-001",
                content="高优先级任务",
                from_agent="agent1",
                to_agent="agent2",
                priority="high",
                created_at="2026-02-14T10:00:00Z"
            )
            manager.add(item)

            checker = AgentStartupChecker("agent2", StartupConfig(auto_display=False))
            checker.queue_manager = manager

            result = checker.run()
            action = checker.suggest_action(result)
            assert action == "process_todo:TODO-001"

    def test_suggest_action_no_unread(self):
        """测试建议行动（无未读）"""
        from src.core.agent_startup_checker import AgentStartupChecker, StartupConfig
        from src.core.todo_queue_manager import TodoQueueManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            checker = AgentStartupChecker("agent1", StartupConfig(auto_display=False))
            checker.queue_manager = manager

            result = checker.run()
            action = checker.suggest_action(result)
            assert action == "continue"

    def test_suggest_action_medium_priority(self):
        """测试建议行动（中优先级优先）"""
        from src.core.agent_startup_checker import AgentStartupChecker, StartupConfig
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")

            item = TodoQueueItem(
                id="TODO-002",
                content="中优先级任务",
                from_agent="agent1",
                to_agent="agent2",
                priority="medium",
                created_at="2026-02-14T10:00:00Z"
            )
            manager.add(item)

            checker = AgentStartupChecker("agent2", StartupConfig(auto_display=False))
            checker.queue_manager = manager

            result = checker.run()
            action = checker.suggest_action(result)
            assert action == "review_todos"

    def test_run_exception_handling(self):
        """测试异常处理"""
        from src.core.agent_startup_checker import AgentStartupChecker, StartupConfig
        import unittest.mock as mock

        checker = AgentStartupChecker("agent1", StartupConfig(auto_display=False))
        checker.queue_manager = mock.MagicMock()
        checker.queue_manager.get_unread.side_effect = Exception("Test error")

        result = checker.run()
        assert result.has_unread_todos is False
        assert "检查失败" in result.message

    def test_display_notifications_no_unread(self):
        """测试显示通知（无未读）"""
        from src.core.agent_startup_checker import AgentStartupChecker, StartupConfig, StartupCheckResult

        checker = AgentStartupChecker("agent1", StartupConfig(auto_display=False))
        result = StartupCheckResult(
            has_unread_todos=False,
            unread_count=0,
            todos=[],
            message="✅ 无未读TODO",
            suggestions=["继续当前工作"]
        )
        checker.display_notifications(result)

    def test_display_notifications_with_unread(self):
        """测试显示通知（有未读）"""
        from src.core.agent_startup_checker import AgentStartupChecker, StartupConfig, StartupCheckResult

        checker = AgentStartupChecker("agent1", StartupConfig(auto_display=False))
        result = StartupCheckResult(
            has_unread_todos=True,
            unread_count=2,
            todos=[
                {
                    "id": "TODO-001",
                    "content": "测试TODO",
                    "priority": "high",
                    "priority_icon": "🔴",
                    "from_agent": "agent1",
                    "created_at": "2026-02-14T10:00:00Z",
                    "age": "刚刚"
                }
            ],
            message="未读TODO: 🔴 高优先: 1个",
            suggestions=["建议先处理: TODO-001 - 测试TODO..."]
        )
        checker.display_notifications(result)


class TestStateNotifier:
    """StateNotifier 测试类"""

    def test_init_with_queue_manager(self):
        """测试初始化"""
        from src.core.state_notifier import StateNotifier

        notifier = StateNotifier()
        assert notifier.queue_manager is None

    def test_init_with_queue_manager_param(self):
        """测试带queue_manager初始化"""
        from src.core.state_notifier import StateNotifier
        from src.core.todo_queue_manager import TodoQueueManager

        with tempfile.TemporaryDirectory() as tmpdir:
            queue_manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")
            notifier = StateNotifier(queue_manager=queue_manager)
            assert notifier.queue_manager is not None

    def test_set_default_webhook_url(self):
        """测试设置默认URL"""
        from src.core.state_notifier import StateNotifier

        notifier = StateNotifier()
        notifier.set_default_webhook_url("http://localhost:8080/webhook")
        assert notifier._default_webhook_url == "http://localhost:8080/webhook"

    def test_enable_enhancer(self):
        """测试增强器开关"""
        from src.core.state_notifier import StateNotifier

        notifier = StateNotifier()
        notifier.enable_enhancer(False)
        assert notifier._use_enhancer is False

    def test_notify_todo_created_without_webhook(self):
        """测试通知TODO创建（无webhook）"""
        from src.core.state_notifier import StateNotifier
        from src.core.todo_queue_manager import TodoQueueManager

        with tempfile.TemporaryDirectory() as tmpdir:
            queue_manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")
            notifier = StateNotifier(queue_manager=queue_manager)

            result = notifier.notify_todo_created(
                "TODO-001",
                "测试TODO",
                "agent1",
                "agent2"
            )

            assert result is True

            unread = queue_manager.get_unread("agent2")
            assert len(unread) == 1
            assert unread[0].id == "TODO-001"

    def test_notify_todo_completed(self):
        """测试通知TODO完成"""
        from src.core.state_notifier import StateNotifier
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            queue_manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")
            notifier = StateNotifier(queue_manager=queue_manager)

            item = TodoQueueItem(
                id="TODO-001",
                content="测试TODO",
                from_agent="agent1",
                to_agent="agent2",
                priority="high",
                created_at="2026-02-14T10:00:00Z"
            )
            queue_manager.add(item)

            result = notifier.notify_todo_completed(
                "TODO-001",
                "测试TODO",
                "agent1",
                "agent2"
            )

            unread = queue_manager.get_unread("agent2")
            assert len(unread) == 0

    def test_format_payload(self):
        """测试payload格式化"""
        from src.core.state_notifier import StateNotifier, StateChangeEvent

        notifier = StateNotifier()
        event = StateChangeEvent(
            event_type="test.event",
            agent_id="agent1",
            details={"key": "value"}
        )
        payload = notifier._format_payload(event)

        assert payload["action"] == "test.event"
        assert payload["sender"]["login"] == "agent1"
        assert payload["oc_collab"]["event_type"] == "test.event"

    def test_notify_with_webhook_configured(self):
        """测试notify方法（有webhook配置）"""
        from src.core.state_notifier import StateNotifier, StateChangeEvent
        import unittest.mock as mock

        notifier = StateNotifier()
        notifier.set_default_webhook_url("http://localhost:8080/webhook")
        notifier.enable_enhancer(False)

        event = StateChangeEvent(
            event_type="test.event",
            agent_id="agent1",
            details={"key": "value"}
        )

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            result = notifier.notify(event)
            assert result is True
            mock_post.assert_called_once()

    def test_notify_with_enhancer(self):
        """测试notify方法（使用enhancer）"""
        from src.core.state_notifier import StateNotifier, StateChangeEvent
        import unittest.mock as mock

        notifier = StateNotifier()
        notifier.set_default_webhook_url("http://localhost:8080/webhook")
        notifier.enable_enhancer(True)

        event = StateChangeEvent(
            event_type="test.event",
            agent_id="agent1",
            details={"key": "value"}
        )

        with mock.patch('src.core.webhook_enhancer.WebhookEnhancer') as mock_enhancer_class:
            mock_enhancer = mock.MagicMock()
            mock_enhancer.format_payload_with_id.return_value = {"action": "test"}
            mock_enhancer.generate_webhook_id.return_value = "test-id"
            mock_enhancer.send_with_retry.return_value = mock.MagicMock(status="sent")
            mock_enhancer_class.return_value = mock_enhancer

            result = notifier.notify(event)
            assert result is True

    def test_notify_request_exception(self):
        """测试notify方法（请求异常）"""
        from src.core.state_notifier import StateNotifier, StateChangeEvent
        import unittest.mock as mock
        import requests

        notifier = StateNotifier()
        notifier.set_default_webhook_url("http://localhost:8080/webhook")
        notifier.enable_enhancer(False)

        event = StateChangeEvent(
            event_type="test.event",
            agent_id="agent1",
            details={"key": "value"}
        )

        with mock.patch('requests.post') as mock_post:
            mock_post.side_effect = requests.RequestException("Connection error")
            result = notifier.notify(event)
            assert result is False

    def test_notify_todo_created_with_queue(self):
        """测试notify_todo_created（带queue_manager）"""
        from src.core.state_notifier import StateNotifier
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem

        with tempfile.TemporaryDirectory() as tmpdir:
            queue_manager = TodoQueueManager(queue_file=f"{tmpdir}/test_queue.yaml")
            notifier = StateNotifier(queue_manager=queue_manager)
            notifier.set_default_webhook_url("http://localhost:8080/webhook")

            with mock.patch('requests.post') as mock_post:
                mock_post.return_value.status_code = 200
                result = notifier.notify_todo_created(
                    "TODO-QUEUE-001",
                    "队列测试TODO",
                    "agent1",
                    "agent2"
                )
                assert result is True

                unread = queue_manager.get_unread("agent2")
                assert len(unread) == 1
                assert unread[0].id == "TODO-QUEUE-001"

    def test_notify_signoff_completed(self):
        """测试notify_signoff_completed"""
        from src.core.state_notifier import StateNotifier, StateChangeEvent
        import unittest.mock as mock

        notifier = StateNotifier()
        notifier.set_default_webhook_url("http://localhost:8080/webhook")
        notifier.enable_enhancer(False)

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            result = notifier.notify_signoff_completed("review", "agent1")
            assert result is True

    def test_notify_phase_advanced(self):
        """测试notify_phase_advanced"""
        from src.core.state_notifier import StateNotifier
        import unittest.mock as mock

        notifier = StateNotifier()
        notifier.set_default_webhook_url("http://localhost:8080/webhook")
        notifier.enable_enhancer(False)

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            result = notifier.notify_phase_advanced("dev", "test", "agent1")
            assert result is True

    def test_notify_bug_fixed(self):
        """测试notify_bug_fixed"""
        from src.core.state_notifier import StateNotifier
        import unittest.mock as mock

        notifier = StateNotifier()
        notifier.set_default_webhook_url("http://localhost:8080/webhook")
        notifier.enable_enhancer(False)

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            result = notifier.notify_bug_fixed("BUG-001", "Test fix", "agent1")
            assert result is True


class TestStartupCommands:
    """CLI命令测试类"""

    def test_import_commands(self):
        """测试导入"""
        from src.cli.startup_commands import startup_check_command, todo_stats_command
        assert startup_check_command is not None
        assert todo_stats_command is not None

    def test_import_todo_commands(self):
        """测试导入todo命令"""
        from src.cli.todo_commands import todo_group
        assert todo_group is not None

    def test_import_skill_check_commands(self):
        """测试导入skill-check命令"""
        from src.cli.skill_check_commands import skill_check_group
        assert skill_check_group is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
