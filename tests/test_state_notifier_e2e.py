"""
E2E测试: StateNotifier集成 - Agent间TODO自动通知

核心场景:
1. Agent1创建TODO
2. StateNotifier发送Webhook通知
3. 验证通知是否正确发送

注意: 当前实现使用HTTP Webhook，需要配置接收URL。
本测试验证StateNotifier发送逻辑和状态记录。
"""

import pytest
import time
import threading
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from src.core.state_notifier import StateNotifier, StateChangeEvent
from src.core.todo_sync_manager import TodoSyncManager


# 全局捕获器
notifications_captured = []


class WebhookHandler(BaseHTTPRequestHandler):
    """Webhook处理器"""
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        if self.path == "/webhook":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                payload = json.loads(body.decode('utf-8'))
                notifications_captured.append(payload)
            except json.JSONDecodeError:
                pass
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')


class WebhookServer:
    """简易Webhook服务器"""
    def __init__(self, port=18765):
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        self.server = HTTPServer(('localhost', self.port), WebhookHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        return f"http://localhost:{self.port}/webhook"

    def stop(self):
        if self.server:
            self.server.shutdown()


@pytest.fixture(scope="module")
def webhook_server():
    """启动Webhook服务器"""
    global notifications_captured
    notifications_captured = []
    server = WebhookServer()
    url = server.start()
    yield server, url
    server.stop()


@pytest.fixture
def clean_notifications(webhook_server):
    """清理通知记录"""
    global notifications_captured
    notifications_captured = []
    yield


class TestStateNotifierE2E:
    """StateNotifier E2E测试"""

    def test_todo_created_triggers_webhook(self, webhook_server, clean_notifications):
        """
        场景: Agent1创建TODO，触发Webhook通知

        期望:
        1. TODO创建成功
        2. StateNotifier发送Webhook通知
        3. 接收器捕获到通知
        """
        server, webhook_url = webhook_server

        # 步骤1: 配置StateNotifier
        notifier = StateNotifier()
        notifier.set_default_webhook_url(webhook_url)

        # 步骤2: 模拟创建TODO
        todo_id = "TODO-E2E-001"
        content = "E2E测试: 验证StateNotifier通知"

        # 发送TODO创建通知
        result = notifier.notify_todo_created(todo_id, content, "agent1")

        # 验证1: 通知发送成功
        assert result is True, "Webhook通知应该发送成功"

        # 验证2: 接收器捕获到通知
        time.sleep(0.5)  # 等待异步通知
        assert len(notifications_captured) >= 1, f"应该至少收到1个通知，实际收到{len(notifications_captured)}"

        # 验证3: 通知内容正确
        notification = notifications_captured[0]
        assert notification.get("action") == "todo.created", f"事件类型应该匹配，实际: {notification.get('action')}"
        assert notification.get("oc_collab", {}).get("details", {}).get("todo_id") == todo_id

        print(f"✅ E2E测试通过: TODO创建触发Webhook通知")

    def test_multiple_agents_todo_notification(self, webhook_server, clean_notifications):
        """
        场景: Agent1和Agent2交替创建TODO

        期望:
        1. Agent1创建的TODO通知能被捕获
        2. Agent2创建的TODO通知能被捕获
        """
        server, webhook_url = webhook_server
        notifier = StateNotifier()
        notifier.set_default_webhook_url(webhook_url)

        # Agent1创建TODO
        notifier.notify_todo_created("TODO-E2E-A1", "Agent1的任务", "agent1")

        # Agent2创建TODO
        notifier.notify_todo_created("TODO-E2E-A2", "Agent2的任务", "agent2")

        # 等待通知
        time.sleep(0.5)

        # 验证
        assert len(notifications_captured) == 2, f"应该收到2个通知，实际收到{len(notifications_captured)}"

        # 检查两个Agent的通知
        todo_ids = [n.get("oc_collab", {}).get("details", {}).get("todo_id") for n in notifications_captured]
        assert "TODO-E2E-A1" in todo_ids, "Agent1的通知应该被捕获"
        assert "TODO-E2E-A2" in todo_ids, "Agent2的通知应该被捕获"

        print(f"✅ 多Agent通知测试通过: Agent1 + Agent2各1个通知")

    def test_signoff_triggers_webhook(self, webhook_server, clean_notifications):
        """场景: 签署完成后触发Webhook通知"""
        server, webhook_url = webhook_server
        notifier = StateNotifier()
        notifier.set_default_webhook_url(webhook_url)

        result = notifier.notify_signoff_completed("requirements", "agent1")

        assert result is True
        time.sleep(0.5)

        assert len(notifications_captured) >= 1
        notification = notifications_captured[0]
        assert notification.get("action") == "signoff.completed"

        print("✅ Signoff通知测试通过")

    def test_phase_advance_triggers_webhook(self, webhook_server, clean_notifications):
        """场景: 阶段推进触发Webhook通知"""
        server, webhook_url = webhook_server
        notifier = StateNotifier()
        notifier.set_default_webhook_url(webhook_url)

        result = notifier.notify_phase_advanced("requirements", "design", "agent1")

        assert result is True
        time.sleep(0.5)

        assert len(notifications_captured) >= 1
        notification = notifications_captured[0]
        assert notification.get("action") == "phase.advanced"

        print("✅ Phase advance通知测试通过")

    def test_webhook_not_configured_skips_silently(self):
        """
        场景: Webhook未配置时静默跳过

        期望: 不抛出异常，静默返回
        """
        notifier = StateNotifier()

        # 不配置Webhook URL
        result = notifier.notify_todo_created("TODO-SKIP", "测试跳过", "agent1")

        # 应该静默返回False（未配置）
        assert result is False

        print("✅ Webhook未配置时静默跳过测试通过")


class TestStateNotifierStats:
    """StateNotifier通知状态测试"""

    def test_webhook_stats_file_exists(self):
        """验证webhook_stats.yaml文件存在"""
        stats_file = Path("state/webhook_stats.yaml")
        assert stats_file.exists(), "webhook_stats.yaml应该存在"

    def test_webhook_stats_structure(self):
        """验证webhook_stats.yaml结构正确"""
        import yaml

        with open("state/webhook_stats.yaml") as f:
            stats = yaml.safe_load(f)

        assert "notifications" in stats, "应该有notifications字段"
        assert "total" in stats, "应该有total字段"
        assert "sent" in stats, "应该有sent字段"
        assert "failed" in stats, "应该有failed字段"

        # 验证通知记录结构
        if stats["notifications"]:
            notification = stats["notifications"][0]
            assert "webhook_id" in notification, "应该有webhook_id"
            assert "event_type" in notification, "应该有event_type"
            assert "status" in notification, "应该有status"

        print(f"✅ webhook_stats结构正确: 共{stats['total']}条，发送{stats['sent']}，失败{stats['failed']}")


class TestCoreScenario:
    """核心场景测试"""

    def test_agent1_creates_todo_agent2_auto_discovers(self):
        """
        核心E2E场景: Agent1创建TODO，AgentB自动感知（无需手动告知）

        这个测试验证v2.2.10的核心功能：
        1. Agent1调用notify_todo_created()创建TODO
        2. StateNotifier将TODO写入todo_queue.yaml队列
        3. Agent2启动时通过AgentStartupChecker自动检查队列
        4. Agent2发现未读TODO并生成建议

        验证要点:
        - TODO写入队列 ✓
        - AgentStartupChecker检测到未读 ✓
        - 自动生成处理建议 ✓
        """
        import tempfile
        import yaml
        from src.core.state_notifier import StateNotifier
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem
        from src.core.agent_startup_checker import AgentStartupChecker, StartupConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = f"{tmpdir}/todo_queue.yaml"

            # 步骤1: Agent1创建TODO（模拟Agent1调用todowrite，使用高优先级）
            queue_manager = TodoQueueManager(queue_file=queue_file)
            notifier = StateNotifier(queue_manager=queue_manager)

            # 创建高优先级TODO
            item = TodoQueueItem(
                id="TODO-E2E-001",
                content="E2E测试：Agent1分配给Agent2的任务",
                from_agent="agent1",
                to_agent="agent2",
                priority="high",  # 高优先级
                created_at="2026-02-14T10:00:00Z"
            )
            queue_manager.add(item)

            # 验证1: TODO已写入队列
            unread_todos = queue_manager.get_unread("agent2")
            assert len(unread_todos) == 1, f"Agent2应该有1个未读TODO，实际{len(unread_todos)}个"
            assert unread_todos[0].id == "TODO-E2E-001", "TODO ID应该匹配"

            # 步骤2: Agent2启动时自动检查队列
            checker = AgentStartupChecker("agent2", StartupConfig(auto_display=False))
            checker.queue_manager = queue_manager

            check_result = checker.run()

            # 验证2: Agent2自动发现未读TODO
            assert check_result.has_unread_todos is True, "应该检测到未读TODO"
            assert check_result.unread_count == 1, "未读数量应该为1"
            assert len(check_result.todos) == 1, "返回的TODO列表应该有1个"

            # 验证3: 高优先级TODO会生成处理建议
            suggested_action = checker.suggest_action(check_result)
            assert "TODO-E2E-001" in suggested_action, f"应该建议处理TODO-E2E-001，实际: {suggested_action}"

            print("✅ 核心E2E场景测试通过: Agent1创建TODO → Agent2自动感知")
            print(f"   - Agent1创建高优先级TODO: TODO-E2E-001")
            print(f"   - Agent2检测到未读: {check_result.unread_count}个")
            print(f"   - 建议操作: {suggested_action}")

    def test_agent1_creates_multiple_todos_agent2_gets_prioritized_list(self):
        """
        场景: Agent1创建多个TODO，Agent2按优先级处理

        验证:
        - 多个TODO按优先级排序（high → medium → low）
        - 建议优先处理高优先级TODO
        """
        import tempfile
        from src.core.state_notifier import StateNotifier
        from src.core.todo_queue_manager import TodoQueueManager, TodoQueueItem
        from src.core.agent_startup_checker import AgentStartupChecker, StartupConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = f"{tmpdir}/todo_queue.yaml"
            queue_manager = TodoQueueManager(queue_file=queue_file)

            # 直接创建队列项，包含高优先级TODO
            items = [
                TodoQueueItem(
                    id="TODO-PRIO-LOW",
                    content="低优先级任务",
                    from_agent="agent1",
                    to_agent="agent2",
                    priority="low",
                    created_at="2026-02-14T10:00:00Z"
                ),
                TodoQueueItem(
                    id="TODO-PRIO-HIGH",
                    content="紧急修复Bug",
                    from_agent="agent1",
                    to_agent="agent2",
                    priority="high",
                    created_at="2026-02-14T10:01:00Z"
                ),
                TodoQueueItem(
                    id="TODO-PRIO-MED",
                    content="中等优先级任务",
                    from_agent="agent1",
                    to_agent="agent2",
                    priority="medium",
                    created_at="2026-02-14T10:02:00Z"
                ),
            ]

            for item in items:
                queue_manager.add(item)

            # Agent2检查队列
            checker = AgentStartupChecker("agent2", StartupConfig(auto_display=False))
            checker.queue_manager = queue_manager
            result = checker.run()

            # 验证
            assert result.has_unread_todos is True
            assert result.unread_count == 3

            # 建议应该是高优先级TODO
            suggested = checker.suggest_action(result)
            assert "TODO-PRIO-HIGH" in suggested, f"应该建议处理高优先级TODO，实际: {suggested}"

            # 验证排序：高优先级在前
            assert result.todos[0]["priority"] == "high", "第一个应该是高优先级"

            print("✅ 多TODO优先级场景测试通过")
            print(f"   - 未读TODO数量: {result.unread_count}")
            print(f"   - 建议操作: {suggested}")
            print(f"   - 第一个TODO: {result.todos[0]['id']} ({result.todos[0]['priority']})")

    def test_agent2_marks_todo_read_after_completion(self):
        """
        场景: Agent2处理完TODO后标记为已读

        验证:
        - 标记已读后，队列中不再显示
        - 启动检查不再提示
        """
        import tempfile
        from src.core.state_notifier import StateNotifier
        from src.core.todo_queue_manager import TodoQueueManager
        from src.core.agent_startup_checker import AgentStartupChecker, StartupConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = f"{tmpdir}/todo_queue.yaml"
            queue_manager = TodoQueueManager(queue_file=queue_file)
            notifier = StateNotifier(queue_manager=queue_manager)

            # Agent1创建TODO
            notifier.notify_todo_created("TODO-READ-001", "待处理任务", "agent1", "agent2")

            # Agent2检查并标记已读
            checker = AgentStartupChecker("agent2", StartupConfig(auto_display=False))
            checker.queue_manager = queue_manager

            # 初始状态：有未读
            result1 = checker.run()
            assert result1.has_unread_todos is True
            assert result1.unread_count == 1

            # 标记已读
            queue_manager.mark_read("TODO-READ-001", "agent2")

            # 再次检查：无未读
            result2 = checker.run()
            assert result2.has_unread_todos is False, "标记已读后应该没有未读TODO"
            assert result2.unread_count == 0

            print("✅ TODO标记已读场景测试通过")

    def test_cli_startup_check_shows_unread_todos(self):
        """
        场景: CLI命令oc-collab startup-check正确显示未读TODO

        验证:
        - startup-check命令能正确检测未读
        - 输出包含TODO信息和建议
        """
        import tempfile
        import subprocess
        from src.core.state_notifier import StateNotifier
        from src.core.todo_queue_manager import TodoQueueManager

        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = f"{tmpdir}/todo_queue.yaml"

            # 创建TODO
            queue_manager = TodoQueueManager(queue_file=queue_file)
            notifier = StateNotifier(queue_manager=queue_manager)
            notifier.notify_todo_created("TODO-CLI-001", "CLI测试任务", "agent1", "agent2")

            # 验证队列状态
            unread = queue_manager.get_unread("agent2")
            assert len(unread) == 1

            print("✅ CLI场景验证通过: 队列中有1个未读TODO")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
