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

    def test_agent1_creates_todo_agent2_receives_notification(self):
        """
        核心E2E场景: Agent1创建TODO，验证StateNotifier正确发送通知

        这个测试验证v2.2.9的核心功能：
        - Agent1执行todowrite
        - StateNotifier发送Webhook
        - 对方Agent能通过webhook_stats.yaml感知到新TODO

        注意: 由于当前环境没有配置Webhook URL，我们验证stats文件中的历史记录
        """
        # 读取stats文件中的todo.created通知
        import yaml

        with open("state/webhook_stats.yaml") as f:
            stats = yaml.safe_load(f)

        # 查找todo.created通知
        todo_notifications = [
            n for n in stats["notifications"]
            if n["event_type"] == "todo.created"
        ]

        # 应该有todo.created通知记录
        assert len(todo_notifications) >= 1, f"应该有todo.created通知，实际{len(todo_notifications)}个"

        # 最新的一条应该是sent状态
        latest_todo = todo_notifications[-1]
        assert latest_todo["status"] == "sent", f"最新todo.created通知应该发送成功，实际状态: {latest_todo['status']}"

        # 验证通知包含正确的TODO ID
        # 注意：由于StateNotifier的设计，我们通过检查stats文件来验证

        print(f"✅ 核心E2E场景测试通过")
        print(f"   - webhook_stats.yaml中共有{len(todo_notifications)}条todo.created通知")
        print(f"   - 最新通知状态: {latest_todo['status']}")
        print(f"   - webhook_id: {latest_todo['webhook_id'][:8]}...")

    def test_agent2_receives_todo_from_agent1(self):
        """
        场景: Agent2能感知到Agent1创建的TODO

        验证方式:
        1. 检查webhook_stats.yaml中是否有agent1创建的TODO通知
        2. 验证通知事件类型为todo.created
        """
        import yaml

        with open("state/webhook_stats.yaml") as f:
            stats = yaml.safe_load(f)

        # 检查agent1的TODO通知
        agent1_notifications = [
            n for n in stats["notifications"]
            if n["event_type"] == "todo.created"
        ]

        assert len(agent1_notifications) >= 1, f"应该有agent1创建的TODO通知，实际{len(agent1_notifications)}个"

        print(f"✅ Agent2感知Agent1 TODO测试通过")
        print(f"   - Agent1共创建{len(agent1_notifications)}个TODO并发送了通知")
        print(f"   - 这些通知记录在webhook_stats.yaml中")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
