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
    
    def test_instruction_file_generation(self, puller):
        """测试Instruction文件生成 - BUG-20260218-003验证"""
        from pathlib import Path
        
        puller.storage.add({'id': 'INST-001', 'content': '测试Instruction生成', 'sender': '1', 'receiver': '2', 'status': 'pending', 'priority': 'high'})
        todos = puller.storage.list(receiver='2')
        
        # 调用notify_user生成instruction文件
        ok = puller.notify_user(todos)
        assert ok is True
        
        # 验证文件存在
        instruction_path = Path("config/instructions/TODO_NOTIFY.md")
        assert instruction_path.exists(), "Instruction文件未生成"
        
        # 验证内容包含TODO信息
        content = instruction_path.read_text(encoding='utf-8')
        assert 'INST-001' in content, "TODO ID未包含在instruction中"
        assert '测试Instruction生成' in content, "TODO内容未包含在instruction中"
        assert 'question' in content, "Question tool调用示例未包含"
        assert '立即执行' in content, "操作选项未包含"


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


class TestTodoStorageMore:
    """TodoStorage更多测试"""
    
    @pytest.fixture
    def storage(self):
        db = tempfile.mktemp(suffix='.db')
        s = TodoStorage(db)
        yield s
        if os.path.exists(db):
            os.remove(db)
    
    def test_close(self, storage):
        """测试关闭"""
        storage.close()  # 应该不报错
    
    def test_add_with_metadata(self, storage):
        """测试添加带元数据"""
        ok, msg = storage.add({
            'id': 'META-001',
            'content': 'test',
            'sender': '1',
            'receiver': '2',
            'metadata': {'key': 'value'}
        })
        assert ok is True
    
    def test_add_with_all_fields(self, storage):
        """测试添加所有字段"""
        from datetime import datetime
        ok, msg = storage.add({
            'id': 'FULL-001',
            'content': 'test content',
            'status': 'in_progress',
            'priority': 'high',
            'sender': '1',
            'receiver': '2',
            'source': 'BUG',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'is_read': 0,
            'metadata': '{}'
        })
        assert ok is True
    
    def test_update_multiple_fields(self, storage):
        """测试更新多个字段"""
        storage.add({'id': 'MULTI-001', 'content': 'test', 'sender': '1', 'receiver': '2'})
        ok = storage.update('MULTI-001', {
            'status': 'completed',
            'priority': 'low',
            'is_read': 1
        })
        assert ok is True
        todo = storage.get('MULTI-001')
        assert todo['status'] == 'completed'
        assert todo['priority'] == 'low'
    
    def test_list_by_receiver_and_status(self, storage):
        """测试按接收者和状态筛选"""
        storage.add({'id': 'FLT1', 'content': 't1', 'sender': '1', 'receiver': '2', 'status': 'pending'})
        storage.add({'id': 'FLT2', 'content': 't2', 'sender': '1', 'receiver': '2', 'status': 'completed'})
        todos = storage.list(receiver='2', status='pending')
        assert any(t['id'] == 'FLT1' for t in todos)
        assert not any(t['id'] == 'FLT2' for t in todos)
    
    def test_list_empty_result(self, storage):
        """测试空结果"""
        todos = storage.list(receiver='nonexistent')
        assert len(todos) == 0


class TestDataMigrationMore:
    """DataMigration更多测试"""
    
    @pytest.fixture
    def migration(self):
        db = tempfile.mktemp(suffix='.db')
        storage = TodoStorage(db)
        m = DataMigrationService(storage)
        yield m
        if os.path.exists(db):
            os.remove(db)
    
    def test_rollback_nonexistent(self, migration):
        """测试回滚不存在的备份"""
        ok = migration.rollback('/nonexistent/backup.yaml')
        assert ok is False
    
    def test_preview_with_data(self, migration):
        """测试预览有数据的YAML"""
        result = migration.preview('state/agent_adhoc_todos.yaml')
        assert 'total' in result
        assert result['total'] > 0
    
    def test_transform_todo(self, migration):
        """测试TODO转换"""
        todo = {'id': 'TEST-001', 'content': 'test', 'status': 'pending', 'priority': 'P0'}
        transformed = migration._transform_todo(todo)
        assert transformed['priority'] == 'high'  # P0 -> high
        assert transformed['sender'] != None
        assert transformed['source'] == 'legacy'
    
    def test_normalize_priority(self, migration):
        """测试优先级标准化"""
        assert migration._normalize_priority('P0') == 'high'
        assert migration._normalize_priority('P1') == 'medium'
        assert migration._normalize_priority('P2') == 'low'
        assert migration._normalize_priority('high') == 'high'
        assert migration._normalize_priority('unknown') == 'medium'
    
    def test_infer_sender_receiver_with_agent_id(self, migration):
        """测试推断sender/receiver-有agent_id"""
        todo = {'id': 'TEST', 'agent_id': '2'}
        sender, receiver = migration._infer_sender_receiver(todo)
        assert sender == '2'
    
    def test_infer_sender_receiver_from_id(self, migration):
        """测试从ID推断"""
        todo = {'id': 'TODO-3-001', 'agent_id': None}
        sender, receiver = migration._infer_sender_receiver(todo)
        assert sender == '3'
    
    def test_infer_sender_receiver_unknown(self, migration):
        """测试未知情况-没有有效ID格式"""
        todo = {}  # 空todo
        sender, receiver = migration._infer_sender_receiver(todo)
        assert sender == 'unknown'


class TestNotificationServiceMore:
    """NotificationService更多测试"""
    
    @pytest.fixture
    def notification(self):
        db = tempfile.mktemp(suffix='.db')
        storage = TodoStorage(db)
        n = NotificationService(storage)
        yield n
        if os.path.exists(db):
            os.remove(db)
    
    def test_notify_with_all_fields(self, notification):
        """测试带完整字段的通知"""
        notif_id = notification.notify({
            'id': 'FULL-001', 
            'content': 'test content',
            'sender': '1',
            'receiver': '2'
        })
        assert notif_id is not None
    
    def test_get_status_no_last_notification(self, notification):
        """测试无最后通知时的状态"""
        status = notification.get_status()
        assert status.get('last_notification') is None
    
    def test_load_config_nonexistent(self, notification):
        """测试加载不存在的配置"""
        notification.config_path = '/nonexistent.yaml'
        config = notification._load_config()
        assert config == {}
    
    def test_ensure_config_dir(self, notification):
        """测试确保配置目录存在"""
        notification._ensure_config_dir()
        import os
        assert os.path.exists('config')
    
    def test_save_config(self, notification):
        """测试保存配置"""
        notification._save_config({'test': 'value'})
        import os
        assert os.path.exists(notification.config_path)


class TestOnlinePullerMore:
    """OnlinePuller更多测试"""
    
    @pytest.fixture
    def puller(self):
        db = tempfile.mktemp(suffix='.db')
        storage = TodoStorage(db)
        monitor = AgentStatusMonitor(db)
        p = OnlinePullerService(storage, monitor)
        yield p
        if os.path.exists(db):
            os.remove(db)
    
    def test_pull_pending_empty(self, puller):
        """测试拉取空的积压"""
        todos = puller.pull_pending('nonexistent')
        assert len(todos) == 0
    
    def test_notify_user_empty(self, puller):
        """测试通知空列表"""
        ok = puller.notify_user([])
        assert ok is True
    
    def test_get_deferred_todos_empty(self, puller):
        """测试获取空延迟列表"""
        todos = puller.get_deferred_todos('nonexistent')
        assert isinstance(todos, list)


class TestConfigManagerMore:
    """ConfigManager更多测试"""
    
    @pytest.fixture
    def config_mgr(self):
        import tempfile
        cfg = tempfile.mktemp(suffix='.yaml')
        mgr = ConfigManager(cfg)
        yield mgr
        if os.path.exists(cfg):
            os.remove(cfg)
    
    def test_delete_existing(self, config_mgr):
        """测试删除存在的配置"""
        config_mgr.set('test.key', 'value')
        ok = config_mgr.delete('test.key')
        assert ok is True
    
    def test_delete_nonexistent(self, config_mgr):
        """测试删除不存在的配置"""
        ok = config_mgr.delete('nonexistent.key')
        assert ok is False
    
    def test_reset(self, config_mgr):
        """测试重置配置"""
        config_mgr.set('custom.setting', 'value')
        ok = config_mgr.reset()
        assert ok is True
        value = config_mgr.get('version')
        assert value == '1.0'
    
    def test_get_raw(self, config_mgr):
        """测试获取原始配置值"""
        config_mgr.set('raw.test', '123')
        value = config_mgr.get_raw('raw.test')
        assert value == '123'
    
    def test_get_raw_with_default(self, config_mgr):
        """测试获取不存在的原始配置"""
        value = config_mgr.get_raw('nonexistent', default='default_val')
        assert value == 'default_val'
    
    def test_get_raw_error(self, config_mgr):
        """测试获取原始配置时的错误处理"""
        config_mgr.set('nested.value', 'test')
        value = config_mgr.get_raw('nested.invalid.path', default='fallback')
        assert value == 'fallback'


class TestDataMigrationMoreTests:
    """DataMigration更多测试"""
    
    @pytest.fixture
    def migration(self):
        import tempfile
        db = tempfile.mktemp(suffix='.db')
        storage = TodoStorage(db)
        m = DataMigrationService(storage)
        yield m
        if os.path.exists(db):
            os.remove(db)
    
    def test_migrate_nonexistent_file(self, migration):
        """测试迁移不存在的文件"""
        ok, msg = migration.migrate('/nonexistent.yaml')
        assert ok is False
        assert '不存在' in msg
    
    def test_migrate_invalid_yaml(self, migration):
        """测试迁移无效YAML"""
        import tempfile
        invalid_yaml = tempfile.mktemp(suffix='.yaml')
        with open(invalid_yaml, 'w') as f:
            f.write('invalid: content')
        ok, msg = migration.migrate(invalid_yaml)
        os.remove(invalid_yaml)
        assert ok is False
    
    def test_migrate_valid_yaml(self, migration):
        """测试迁移有效YAML"""
        import tempfile
        valid_yaml = tempfile.mktemp(suffix='.yaml')
        with open(valid_yaml, 'w') as f:
            f.write("""
todos:
  - id: TODO-1-001
    content: Test TODO 1
    status: pending
    priority: high
  - id: TODO-1-002
    content: Test TODO 2
    status: completed
    priority: low
""")
        ok, msg = migration.migrate(valid_yaml)
        os.remove(valid_yaml)
        assert ok is True
        assert '成功' in msg
    
    def test_preview_with_invalid_file(self, migration):
        """测试预览不存在的文件"""
        result = migration.preview('/nonexistent.yaml')
        assert 'error' in result
    
    def test_rollback_with_existing_db(self, migration):
        """测试回滚存在的数据库"""
        import tempfile
        import os
        db_path = "state/todos.db"
        os.makedirs("state", exist_ok=True)
        storage = TodoStorage(db_path)
        storage.add({'id': 'TEST-001', 'content': 'test', 'sender': '1', 'receiver': '2'})
        
        temp_yaml = tempfile.mktemp(suffix='.yaml')
        with open(temp_yaml, 'w') as f:
            f.write("todos: []")
        
        migration.storage = storage
        backup_path = migration.backup(temp_yaml)
        
        ok = migration.rollback(backup_path)
        assert ok is True
        
        os.remove(temp_yaml)
        if os.path.exists(db_path):
            os.remove(db_path)
    
    def test_rollback_nonexistent_backup(self, migration):
        """测试回滚不存在的备份"""
        ok = migration.rollback('/nonexistent/backup.yaml')
        assert ok is False
    
    def test_list_backups_empty(self, migration):
        """测试列出空备份"""
        backups = migration.list_backups()
        assert isinstance(backups, list)


class TestNotificationServiceExtended:
    """NotificationService扩展测试"""
    
    @pytest.fixture
    def notification(self):
        import tempfile
        db = tempfile.mktemp(suffix='.db')
        storage = TodoStorage(db)
        n = NotificationService(storage)
        yield n
        if os.path.exists(db):
            os.remove(db)
    
    def test_generate_instruction_default_path(self, notification):
        """测试生成默认路径的instruction"""
        ok = notification.generate_instruction()
        assert ok is True
        import os
        assert os.path.exists(notification.instruction_path)
    
    def test_generate_instruction_custom_path(self, notification):
        """测试生成自定义路径的instruction"""
        custom_path = tempfile.mktemp(suffix='.md')
        ok = notification.generate_instruction(custom_path)
        assert ok is True
        if os.path.exists(custom_path):
            os.remove(custom_path)
    
    def test_enable(self, notification):
        """测试启用通知"""
        ok = notification.enable()
        assert ok is True
        status = notification.get_status()
        assert status['enabled'] is True
    
    def test_disable(self, notification):
        """测试禁用通知"""
        notification.enable()
        ok = notification.disable()
        assert ok is True
        status = notification.get_status()
        assert status['enabled'] is False
    
    def test_get_status_with_notification(self, notification):
        """测试有通知时的状态"""
        notification.notify({'id': 'TEST-001'})
        status = notification.get_status()
        assert status['last_notification'] is not None


class TestTodoStorageErrorHandling:
    """TodoStorage错误处理测试"""
    
    @pytest.fixture
    def storage(self):
        db = tempfile.mktemp(suffix='.db')
        s = TodoStorage(db)
        yield s
        if os.path.exists(db):
            os.remove(db)
    
    def test_add_duplicate_id(self, storage):
        """测试添加重复ID"""
        storage.add({'id': 'DUPE-001', 'content': 'test', 'sender': '1', 'receiver': '2'})
        ok, msg = storage.add({'id': 'DUPE-001', 'content': 'test2', 'sender': '1', 'receiver': '2'})
        assert ok is False
        assert '已存在' in msg
    
    def test_list_with_filters(self, storage):
        """测试带过滤条件的列表"""
        storage.add({'id': 'FILT-001', 'content': 'test', 'sender': '1', 'receiver': '2', 'status': 'pending'})
        storage.add({'id': 'FILT-002', 'content': 'test', 'sender': '1', 'receiver': '2', 'status': 'completed'})
        todos = storage.list(status='pending', receiver='2')
        assert len(todos) >= 1
    
    def test_get_nonexistent(self, storage):
        """测试获取不存在的TODO"""
        todo = storage.get('NONEXISTENT')
        assert todo is None
    
    def test_list_unread_only(self, storage):
        """测试只列出未读"""
        storage.add({'id': 'UNREAD-001', 'content': 'test', 'sender': '1', 'receiver': '2', 'is_read': 0})
        storage.add({'id': 'UNREAD-002', 'content': 'test', 'sender': '1', 'receiver': '2', 'is_read': 1})
        todos = storage.list(unread_only=True)
        assert any(t['id'] == 'UNREAD-001' for t in todos)
    
    def test_list_by_receiver_only(self, storage):
        """测试按receiver筛选"""
        storage.add({'id': 'REC-001', 'content': 'test', 'sender': '5', 'receiver': '8'})
        todos = storage.list(receiver='8')
        assert len(todos) >= 1
    
    def test_update_with_metadata(self, storage):
        """测试更新metadata"""
        storage.add({'id': 'META-001', 'content': 'test', 'sender': '1', 'receiver': '2'})
        ok = storage.update('META-001', {'metadata': {'key': 'value'}})
        assert ok is True
    
    def test_update_empty_dict(self, storage):
        """测试更新空字典"""
        storage.add({'id': 'EMPTY-001', 'content': 'test', 'sender': '1', 'receiver': '2'})
        ok = storage.update('EMPTY-001', {})
        assert ok is False
    
    def test_get_next_id_with_malformed(self, storage):
        """测试获取下一个ID时处理格式错误的ID"""
        storage.add({'id': 'TODO-abc', 'content': 'test', 'sender': '1', 'receiver': '2'})
        next_id = storage.get_next_id('1')
        assert next_id >= 1


class TestNotificationServiceException:
    """NotificationService异常测试"""
    
    @pytest.fixture
    def notification(self):
        import tempfile
        db = tempfile.mktemp(suffix='.db')
        storage = TodoStorage(db)
        n = NotificationService(storage)
        yield n
        if os.path.exists(db):
            os.remove(db)
    
    def test_generate_instruction_exception(self, notification):
        """测试生成instruction时的异常"""
        import os
        original_open = open
        def mock_open(*args, **kwargs):
            if 'TODO_NOTIFY.md' in str(args[0]):
                raise OSError("Mock IO error")
            return original_open(*args, **kwargs)
        import builtins
        builtins.open = mock_open
        try:
            ok = notification.generate_instruction('/invalid/path/that/cannot/be/created/TODO_NOTIFY.md')
            assert ok is False
        finally:
            builtins.open = original_open
