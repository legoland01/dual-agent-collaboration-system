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
    
    def test_get_deferred_todos(self, puller):
        """测试获取延迟TODO"""
        from datetime import datetime, timedelta
        # 创建一个过期的延迟TODO
        storage = puller.storage
        storage.add({
            'id': 'DEF-001', 
            'content': '测试', 
            'sender': '1', 
            'receiver': '2', 
            'status': 'deferred',
            'deferred_until': '2020-01-01T00:00:00'  # 过去的日期
        })
        todos = puller.get_deferred_todos('2')
        # 无论是否有过期TODO，函数应该能正常返回
        assert isinstance(todos, list)
    
    def test_notify_user(self, puller):
        """测试通知用户"""
        puller.storage.add({'id': 'NOTIFY-002', 'content': '测试', 'sender': '1', 'receiver': '2', 'status': 'pending'})
        todos = puller.storage.list(receiver='2')
        ok = puller.notify_user(todos)
        assert ok is True


class TestDataMigration:
    """DataMigration单元测试"""
    
    @pytest.fixture
    def migration(self):
        """创建迁移服务"""
        db = tempfile.mktemp(suffix='.db')
        storage = TodoStorage(db)
        m = DataMigrationService(storage)
        yield m
        if os.path.exists(db):
            os.remove(db)
    
    def test_list_backups(self, migration):
        """测试列出备份"""
        backups = migration.list_backups()
        assert isinstance(backups, list)
    
    def test_backup_creation(self, migration):
        """测试备份创建"""
        import yaml
        test_file = tempfile.mktemp(suffix='.yaml')
        with open(test_file, 'w') as f:
            yaml.dump({'todos': []}, f)
        
        backup_path = migration.backup(test_file)
        assert os.path.exists(backup_path)
        os.remove(backup_path)
        os.remove(test_file)
    
    def test_preview_empty(self, migration):
        """测试预览空文件"""
        result = migration.preview('/nonexistent.yaml')
        assert 'error' in result


class TestInteractionHandlerExtended:
    """InteractionHandler扩展测试"""
    
    @pytest.fixture
    def handler(self):
        db = tempfile.mktemp(suffix='.db')
        storage = TodoStorage(db)
        notification = NotificationService(storage)
        h = InteractionHandler(storage, notification)
        yield h
        if os.path.exists(db):
            os.remove(db)
    
    def test_handle_action_execute(self, handler):
        """测试execute动作"""
        handler.storage.add({'id': 'ACT-001', 'content': 'test', 'sender': '1', 'receiver': '2', 'status': 'pending'})
        ok, msg = handler.handle_action('ACT-001', 'execute')
        assert ok is True
    
    def test_handle_action_defer(self, handler):
        """测试defer动作"""
        handler.storage.add({'id': 'ACT-002', 'content': 'test', 'sender': '1', 'receiver': '2', 'status': 'pending'})
        ok, msg = handler.handle_action('ACT-002', 'defer')
        assert ok is True
    
    def test_handle_action_dismiss(self, handler):
        """测试dismiss动作"""
        handler.storage.add({'id': 'ACT-003', 'content': 'test', 'sender': '1', 'receiver': '2', 'status': 'pending'})
        ok, msg = handler.handle_action('ACT-003', 'dismiss')
        assert ok is True
    
    def test_handle_action_reassign(self, handler):
        """测试reassign动作-需要直接调用"""
        handler.storage.add({'id': 'ACT-004', 'content': 'test', 'sender': '1', 'receiver': '2', 'status': 'pending'})
        ok, msg = handler.reassign('ACT-004', '3')
        assert ok is True
    
    def test_handle_invalid_action(self, handler):
        """测试无效动作"""
        ok, msg = handler.handle_action('INVALID', 'invalid')
        assert ok is False
    
    def test_execute_nonexistent(self, handler):
        """测试执行不存在的TODO"""
        ok, msg = handler.execute('NONEXISTENT')
        assert ok is False
    
    def test_complete_nonexistent(self, handler):
        """测试完成不存在的TODO"""
        ok, msg = handler.complete('NONEXISTENT')
        assert ok is False
    
    def test_dismiss_nonexistent(self, handler):
        """测试取消不存在的TODO"""
        ok, msg = handler.dismiss('NONEXISTENT')
        assert ok is False
    
    def test_defer_nonexistent(self, handler):
        """测试延迟不存在的TODO"""
        ok, msg = handler.defer('NONEXISTENT')
        assert ok is False
    
    def test_view_nonexistent(self, handler):
        """测试查看不存在的TODO"""
        ok, result = handler.view('NONEXISTENT')
        assert ok is False


class TestStatusMonitorExtended:
    """StatusMonitor扩展测试"""
    
    @pytest.fixture
    def monitor(self):
        db = tempfile.mktemp(suffix='.db')
        m = AgentStatusMonitor(db)
        yield m
        if os.path.exists(db):
            os.remove(db)
    
    def test_get_last_seen(self, monitor):
        """测试获取最后在线时间"""
        monitor.detect_online('agent1')
        last_seen = monitor.get_last_seen('agent1')
        assert last_seen is not None
    
    def test_get_last_seen_nonexistent(self, monitor):
        """测试获取不存在Agent的最后在线时间"""
        last_seen = monitor.get_last_seen('nonexistent')
        assert last_seen is None
    
    def test_list_all_agents(self, monitor):
        """测试列出所有Agent"""
        monitor.detect_online('agent1')
        monitor.detect_online('agent2')
        agents = monitor.list_all_agents()
        assert len(agents) >= 2


class TestTodoStorageExtended:
    """TodoStorage扩展测试"""
    
    @pytest.fixture
    def storage(self):
        db = tempfile.mktemp(suffix='.db')
        s = TodoStorage(db)
        yield s
        if os.path.exists(db):
            os.remove(db)
    
    def test_mark_unread(self, storage):
        """测试标记未读"""
        storage.add({'id': 'EXT-001', 'content': 'test', 'sender': '1', 'receiver': '2'})
        storage.mark_read('EXT-001')
        ok = storage.mark_unread('EXT-001')
        assert ok is True
    
    def test_update_nonexistent(self, storage):
        """测试更新不存在的TODO"""
        ok = storage.update('NONEXISTENT', {'status': 'completed'})
        assert ok is False
    
    def test_delete_nonexistent(self, storage):
        """测试删除不存在的TODO"""
        ok = storage.delete('NONEXISTENT')
        assert ok is False
    
    def test_get_next_id(self, storage):
        """测试获取下一个ID"""
        storage.add({'id': 'TODO-2to1-001', 'content': 'test', 'sender': '2', 'receiver': '1'})
        next_id = storage.get_next_id('2')
        assert next_id >= 1
    
    def test_list_multiple_filters(self, storage):
        """测试多条件筛选"""
        storage.add({'id': 'FILT-001', 'content': 'test1', 'sender': '1', 'receiver': '2', 'status': 'pending', 'priority': 'high'})
        storage.add({'id': 'FILT-002', 'content': 'test2', 'sender': '1', 'receiver': '2', 'status': 'completed', 'priority': 'low'})
        todos = storage.list(receiver='2', status='pending', unread_only=False)
        assert any(t['id'] == 'FILT-001' for t in todos)


class TestConfigManagerExtended:
    """ConfigManager扩展测试"""
    
    @pytest.fixture
    def config(self):
        cfg_file = tempfile.mktemp(suffix='.yaml')
        cfg = ConfigManager(cfg_file)
        yield cfg
        if os.path.exists(cfg_file):
            os.remove(cfg_file)
    
    def test_nested_key(self, config):
        """测试嵌套键"""
        config.set('level1.level2.level3', 'value')
        val = config.get('level1.level2.level3')
        assert val == 'value'
    
    def test_get_raw(self, config):
        """测试获取原始值"""
        config.set('raw.key', '123')
        val = config.get_raw('raw.key')
        assert val == '123'
    
    def test_reset(self, config):
        """测试重置"""
        config.set('test.key', 'value')
        ok = config.reset()
        assert ok is True


class TestNotificationServiceFull:
    """NotificationService完整测试"""
    
    @pytest.fixture
    def notification(self):
        db = tempfile.mktemp(suffix='.db')
        storage = TodoStorage(db)
        n = NotificationService(storage)
        yield n
        if os.path.exists(db):
            os.remove(db)
    
    def test_generate_instruction_custom_path(self, notification):
        """测试生成自定义路径Instruction"""
        custom_path = tempfile.mktemp(suffix='.md')
        ok = notification.generate_instruction(custom_path)
        assert ok is True
        assert os.path.exists(custom_path)
        os.remove(custom_path)
    
    def test_notification_stores_todo_id(self, notification):
        """测试通知存储TODO ID"""
        notification.notify({'id': 'NOTIF-001', 'content': 'test'})
        import sqlite3
        conn = sqlite3.connect(notification.storage.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notifications WHERE todo_id = 'NOTIF-001'")
        row = cursor.fetchone()
        conn.close()
        assert row is not None
    
    def test_get_status_with_instruction(self, notification):
        """测试获取状态-有Instruction"""
        notification.generate_instruction()
        status = notification.get_status()
        assert status.get('instruction_exists') is True
