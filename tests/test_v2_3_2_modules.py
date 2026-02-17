"""v2.3.2核心模块单元测试"""

import pytest
import os
import tempfile
from src.core.todo_storage import TodoStorage
from src.core.data_migration import DataMigrationService
from src.core.config_manager import ConfigManager
from src.core.status_monitor import AgentStatusMonitor
from src.core.notification import NotificationService
from src.core.interaction_handler import InteractionHandler
from src.core.online_puller import OnlinePullerService


class TestTodoStorage:
    """TodoStorage单元测试"""
    
    @pytest.fixture
    def storage(self):
        """创建临时数据库"""
        db = tempfile.mktemp(suffix='.db')
        s = TodoStorage(db)
        yield s
        if os.path.exists(db):
            os.remove(db)
    
    def test_add_todo(self, storage):
        """测试添加TODO"""
        ok, msg = storage.add({
            'id': 'TEST-001',
            'content': '测试内容',
            'sender': '1',
            'receiver': '2'
        })
        assert ok is True
        assert 'TEST-001' in msg
    
    def test_get_todo(self, storage):
        """测试获取TODO"""
        storage.add({
            'id': 'TEST-002',
            'content': '测试内容',
            'sender': '1',
            'receiver': '2'
        })
        todo = storage.get('TEST-002')
        assert todo is not None
        assert todo['content'] == '测试内容'
    
    def test_list_todos(self, storage):
        """测试列表"""
        storage.add({'id': 'TEST-003', 'content': '测试1', 'sender': '1', 'receiver': '2'})
        storage.add({'id': 'TEST-004', 'content': '测试2', 'sender': '1', 'receiver': '2'})
        todos = storage.list()
        assert len(todos) >= 2
    
    def test_update_todo(self, storage):
        """测试更新"""
        storage.add({'id': 'TEST-005', 'content': '测试', 'sender': '1', 'receiver': '2'})
        ok = storage.update('TEST-005', {'status': 'completed'})
        assert ok is True
        todo = storage.get('TEST-005')
        assert todo['status'] == 'completed'
    
    def test_delete_todo(self, storage):
        """测试删除"""
        storage.add({'id': 'TEST-006', 'content': '测试', 'sender': '1', 'receiver': '2'})
        ok = storage.delete('TEST-006')
        assert ok is True
        todo = storage.get('TEST-006')
        assert todo is None
    
    def test_mark_read(self, storage):
        """测试标记已读"""
        storage.add({'id': 'TEST-007', 'content': '测试', 'sender': '1', 'receiver': '2'})
        ok = storage.mark_read('TEST-007')
        assert ok is True
        todo = storage.get('TEST-007')
        assert todo['is_read'] == 1
    
    def test_count_unread(self, storage):
        """测试未读统计"""
        storage.add({'id': 'TEST-008', 'content': '测试', 'sender': '1', 'receiver': '2'})
        storage.add({'id': 'TEST-009', 'content': '测试', 'sender': '1', 'receiver': '2', 'is_read': 1})
        count = storage.count_unread('2')
        assert count >= 1
    
    def test_list_by_status(self, storage):
        """测试状态筛选"""
        storage.add({'id': 'TEST-010', 'content': '测试', 'sender': '1', 'receiver': '2', 'status': 'pending'})
        storage.add({'id': 'TEST-011', 'content': '测试', 'sender': '1', 'receiver': '2', 'status': 'completed'})
        todos = storage.list(status='pending')
        assert any(t['id'] == 'TEST-010' for t in todos)


class TestConfigManager:
    """ConfigManager单元测试"""
    
    @pytest.fixture
    def config(self):
        """创建临时配置"""
        cfg_file = tempfile.mktemp(suffix='.yaml')
        cfg = ConfigManager(cfg_file)
        yield cfg
        if os.path.exists(cfg_file):
            os.remove(cfg_file)
    
    def test_set_get(self, config):
        """测试设置和获取"""
        config.set('test.key', 'value')
        val = config.get('test.key')
        assert val == 'value'
    
    def test_get_default(self, config):
        """测试默认值"""
        val = config.get('nonexistent', 'default')
        assert val == 'default'
    
    def test_list(self, config):
        """测试列表"""
        config.set('a.b', '1')
        config.set('a.c', '2')
        cfg = config.list()
        assert 'a' in cfg
    
    def test_delete(self, config):
        """测试删除"""
        config.set('delete.key', 'value')
        ok = config.delete('delete.key')
        assert ok is True
        val = config.get('delete.key')
        assert val is None


class TestAgentStatusMonitor:
    """AgentStatusMonitor单元测试"""
    
    @pytest.fixture
    def monitor(self):
        """创建监控"""
        db = tempfile.mktemp(suffix='.db')
        m = AgentStatusMonitor(db)
        yield m
        if os.path.exists(db):
            os.remove(db)
    
    def test_detect_online(self, monitor):
        """测试上线检测"""
        ok = monitor.detect_online('agent1')
        assert ok is True
        assert monitor.is_online('agent1') is True
    
    def test_detect_offline(self, monitor):
        """测试下线检测"""
        monitor.detect_online('agent1')
        ok = monitor.detect_offline('agent1')
        assert ok is True
        assert monitor.is_online('agent1') is False
    
    def test_list_online_agents(self, monitor):
        """测试列出在线Agent"""
        monitor.detect_online('agent1')
        monitor.detect_online('agent2')
        agents = monitor.list_online_agents()
        assert 'agent1' in agents
        assert 'agent2' in agents


class TestInteractionHandler:
    """InteractionHandler单元测试"""
    
    @pytest.fixture
    def handler(self):
        """创建处理器"""
        db = tempfile.mktemp(suffix='.db')
        storage = TodoStorage(db)
        notification = NotificationService(storage)
        h = InteractionHandler(storage, notification)
        yield h
        if os.path.exists(db):
            os.remove(db)
    
    def test_execute(self, handler):
        """测试执行"""
        handler.storage.add({'id': 'EXEC-001', 'content': '测试', 'sender': '1', 'receiver': '2'})
        ok, msg = handler.execute('EXEC-001')
        assert ok is True
        assert 'EXEC-001' in msg
    
    def test_complete(self, handler):
        """测试完成"""
        handler.storage.add({'id': 'COMP-001', 'content': '测试', 'sender': '1', 'receiver': '2'})
        ok, msg = handler.complete('COMP-001')
        assert ok is True
    
    def test_dismiss(self, handler):
        """测试取消"""
        handler.storage.add({'id': 'DIS-001', 'content': '测试', 'sender': '1', 'receiver': '2'})
        ok, msg = handler.dismiss('DIS-001')
        assert ok is True
    
    def test_defer(self, handler):
        """测试延迟"""
        handler.storage.add({'id': 'DEF-001', 'content': '测试', 'sender': '1', 'receiver': '2'})
        ok, msg = handler.defer('DEF-001', 30)
        assert ok is True
    
    def test_view(self, handler):
        """测试查看"""
        handler.storage.add({'id': 'VIEW-001', 'content': '测试', 'sender': '1', 'receiver': '2'})
        ok, result = handler.view('VIEW-001')
        assert ok is True
        assert result['id'] == 'VIEW-001'


class TestOnlinePuller:
    """OnlinePuller单元测试"""
    
    @pytest.fixture
    def puller(self):
        """创建拉取器"""
        db = tempfile.mktemp(suffix='.db')
        storage = TodoStorage(db)
        monitor = AgentStatusMonitor(db)
        p = OnlinePullerService(storage, monitor)
        yield p
        if os.path.exists(db):
            os.remove(db)
    
    def test_pull_pending(self, puller):
        """测试拉取积压TODO"""
        puller.storage.add({'id': 'PULL-001', 'content': '测试', 'sender': '1', 'receiver': '2', 'status': 'pending'})
        todos = puller.pull_pending('2')
        assert len(todos) >= 1
    
    def test_check_and_notify(self, puller):
        """测试检查并通知"""
        puller.storage.add({'id': 'NOTIFY-001', 'content': '测试', 'sender': '1', 'receiver': '2', 'status': 'pending'})
        ok = puller.check_and_notify('2')
        assert ok is True
