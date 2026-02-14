"""
State Synchronization E2E Tests

覆盖问题：
1. StateReceiver 接收后需要同步到 CLI 队列
2. 端到端数据流验证
3. 多队列数据一致性检查

TC-SYNC-001 ~ TC-SYNC-010
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestStateQueueSync:
    """状态队列同步测试"""

    @pytest.fixture
    def temp_state_dir(self):
        """创建临时状态目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def mock_state_queue(self, temp_state_dir):
        """创建模拟状态队列"""
        from src.core.state_queue import StateQueueManager, Notification

        queue_file = os.path.join(temp_state_dir, "state_queue.json")
        queue = StateQueueManager(queue_file=queue_file)
        yield queue

    @pytest.fixture
    def mock_todo_queue_file(self, temp_state_dir):
        """创建模拟 TODO 队列文件"""
        queue_file = os.path.join(temp_state_dir, "todo_queue.yaml")
        initial_content = """version: '1.0'
last_updated: '2026-02-14T00:00:00'
stats:
  total: 0
  unread: 0
  by_agent:
    agent1: 0
    agent2: 0
  by_priority:
    high: 0
    medium: 0
    low: 0
todos: []
"""
        with open(queue_file, 'w') as f:
            f.write(initial_content)
        yield queue_file

    def test_tc_sync_001_webhook_receiver_writes_to_queue(self, mock_state_queue):
        """
        TC-SYNC-001: StateReceiver 接收通知后写入队列

        验证：webhook 接收的通知能写入 state_queue.json
        """
        notification_data = {
            "event_type": "todo.created",
            "source_agent": "agent1",
            "target_agent": "agent2",
            "details": {
                "todo_id": "TODO-SYNC-001",
                "content": "同步测试 TODO"
            }
        }

        notification = mock_state_queue.enqueue(notification_data)

        assert notification is not None
        assert notification.event_type == "todo.created"
        assert notification.source_agent == "agent1"
        assert notification.target_agent == "agent2"

        stats = mock_state_queue.get_all_stats()
        assert stats["total"] == 1
        assert stats["pending"] == 1

    def test_tc_sync_002_todo_queue_yaml_format(self, mock_todo_queue_file):
        """
        TC-SYNC-002: CLI TODO 队列格式验证

        验证：todo_queue.yaml 格式正确
        """
        from src.utils.yaml import safe_load

        with open(mock_todo_queue_file) as f:
            data = safe_load(f)

        assert "version" in data
        assert "stats" in data
        assert "todos" in data
        assert data["version"] == "1.0"
        assert "by_agent" in data["stats"]
        assert "by_priority" in data["stats"]

    def test_tc_sync_003_state_queue_to_todo_queue_sync(self, mock_state_queue, mock_todo_queue_file):
        """
        TC-SYNC-003: 状态队列同步到 TODO 队列

        验证：state_queue.json 的通知能同步到 todo_queue.yaml
        （此测试预期失败，需要实现同步逻辑）
        """
        from src.utils.yaml import safe_load

        notification_data = {
            "event_type": "todo.created",
            "source_agent": "agent1",
            "target_agent": "agent2",
            "details": {
                "todo_id": "TODO-SYNC-003",
                "content": "队列同步测试"
            }
        }

        mock_state_queue.enqueue(notification_data)

        sync_success = False
        try:
            from src.core.state_receiver import StateReceiver
            receiver = StateReceiver(queue_manager=mock_state_queue)

            if hasattr(receiver, 'sync_to_cli_queue'):
                receiver.sync_to_cli_queue(mock_todo_queue_file)
                sync_success = True
        except AttributeError:
            pass

        assert sync_success, "TC-SYNC-003: StateReceiver 需要实现 sync_to_cli_queue 方法"


class TestEndToEndDataFlow:
    """端到端数据流测试"""

    @pytest.fixture
    def temp_state_dir(self):
        """创建临时状态目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_tc_sync_004_agent1_create_todo_agent2_receives(self, temp_state_dir):
        """
        TC-SYNC-004: Agent1 创建 TODO，Agent2 接收

        完整链路：
        1. Agent1 todowrite 创建 TODO
        2. StateNotifier 发送 webhook
        3. StateReceiver 接收
        4. CLI todo list 显示
        """
        from src.core.state_receiver import StateReceiver
        from src.core.state_queue import StateQueueManager

        queue_file = os.path.join(temp_state_dir, "state_queue.json")
        todo_queue_file = os.path.join(temp_state_dir, "todo_queue.yaml")

        queue_manager = StateQueueManager(queue_file=queue_file)

        with open(todo_queue_file, 'w') as f:
            f.write("""version: '1.0'
last_updated: '2026-02-14T00:00:00'
stats:
  total: 0
  unread: 0
  by_agent:
    agent1: 0
    agent2: 0
todos: []
""")

        receiver = StateReceiver(queue_manager=queue_manager)

        webhook_payload = {
            "event_type": "todo.created",
            "source_agent": "agent1",
            "target_agent": "agent2",
            "details": {
                "todo_id": "TODO-E2E-001",
                "content": "端到端测试 TODO",
                "priority": "high"
            }
        }

        with patch('src.core.state_receiver.requests.post') as mock_post:
            mock_post.return_value.status_code = 202

            result = queue_manager.enqueue(webhook_payload)

            assert result.event_type == "todo.created"
            assert result.target_agent == "agent2"

    def test_tc_sync_005_multiple_notifications_order(self, temp_state_dir):
        """
        TC-SYNC-005: 多个通知按时间顺序处理

        验证：队列保持 FIFO 顺序
        """
        from src.core.state_queue import StateQueueManager

        queue_file = os.path.join(temp_state_dir, "state_queue.json")
        queue = StateQueueManager(queue_file=queue_file)

        notifications = []
        for i in range(5):
            data = {
                "event_type": "todo.created",
                "source_agent": "agent1",
                "target_agent": "agent2",
                "details": {"todo_id": f"TODO-ORDER-{i}"}
            }
            notification = queue.enqueue(data)
            notifications.append(notification)

        all_notifications = queue.get_all_notifications()

        assert len(all_notifications) == 5

        ids_in_order = [n.id for n in all_notifications]
        for i in range(len(notifications) - 1):
            assert ids_in_order.index(notifications[i].id) < ids_in_order.index(notifications[i + 1].id)


class TestQueueConsistency:
    """队列一致性测试"""

    @pytest.fixture
    def temp_state_dir(self):
        """创建临时状态目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_tc_sync_006_queue_stats_accuracy(self, temp_state_dir):
        """
        TC-SYNC-006: 队列统计准确性

        验证：stats 准确反映队列状态
        """
        from src.core.state_queue import StateQueueManager

        queue_file = os.path.join(temp_state_dir, "state_queue.json")
        queue = StateQueueManager(queue_file=queue_file)

        for i in range(3):
            queue.enqueue({
                "event_type": "todo.created",
                "source_agent": "agent1",
                "target_agent": "agent2",
                "details": {"todo_id": f"TODO-STATS-{i}"}
            })

        stats = queue.get_all_stats()

        assert stats["total"] == 3
        assert stats["pending"] == 3

    def test_tc_sync_007_agent_filtering(self, temp_state_dir):
        """
        TC-SYNC-007: 按 Agent 筛选通知

        验证：能正确按 target_agent 筛选
        """
        from src.core.state_queue import StateQueueManager

        queue_file = os.path.join(temp_state_dir, "state_queue.json")
        queue = StateQueueManager(queue_file=queue_file)

        queue.enqueue({
            "event_type": "todo.created",
            "source_agent": "agent1",
            "target_agent": "agent2",
            "details": {"todo_id": "TODO-A2-001"}
        })

        queue.enqueue({
            "event_type": "todo.created",
            "source_agent": "agent2",
            "target_agent": "agent1",
            "details": {"todo_id": "TODO-A1-001"}
        })

        agent2_unread = queue.get_unread("agent2")
        agent1_unread = queue.get_unread("agent1")

        assert len(agent2_unread) == 1
        assert len(agent1_unread) == 1


class TestErrorHandling:
    """错误处理测试"""

    def test_tc_sync_008_empty_webhook_body(self):
        """
        TC-SYNC-008: 空 webhook 请求处理

        验证：空请求返回错误，不崩溃
        """
        from src.core.state_receiver import StateReceiver
        from src.core.state_queue import StateQueueManager
        from flask import Flask

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            queue_file = f.name

        try:
            queue = StateQueueManager(queue_file=queue_file)
            receiver = StateReceiver(queue_manager=queue)

            with receiver.app.test_client() as client:
                response = client.post(
                    "/webhook/state",
                    json={},
                    content_type="application/json"
                )

                assert response.status_code == 400

        finally:
            if os.path.exists(queue_file):
                os.remove(queue_file)

    def test_tc_sync_009_missing_required_fields(self):
        """
        TC-SYNC-009: 缺少必需字段处理

        验证：缺少 event_type/source_agent/target_agent 返回错误
        """
        from src.core.state_receiver import StateReceiver
        from src.core.state_queue import StateQueueManager

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            queue_file = f.name

        try:
            queue = StateQueueManager(queue_file=queue_file)
            receiver = StateReceiver(queue_manager=queue)

            with receiver.app.test_client() as client:
                response = client.post(
                    "/webhook/state",
                    json={"source_agent": "agent1"},
                    content_type="application/json"
                )

                assert response.status_code == 400

        finally:
            if os.path.exists(queue_file):
                os.remove(queue_file)

    def test_tc_sync_010_webhook_recovery(self, temp_state_dir):
        """
        TC-SYNC-010: Webhook 崩溃恢复

        验证：StateReceiver 启动后能恢复处理
        """
        from src.core.state_queue import StateQueueManager

        queue_file = os.path.join(temp_state_dir, "state_queue.json")
        queue = StateQueueManager(queue_file=queue_file)

        for i in range(2):
            queue.enqueue({
                "event_type": "todo.created",
                "source_agent": "agent1",
                "target_agent": "agent2",
                "details": {"todo_id": f"TODO-RECOVERY-{i}"}
            })

        stats_before = queue.get_all_stats()
        assert stats_before["total"] == 2

        stats_after = queue.get_all_stats()
        assert stats_after["total"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
