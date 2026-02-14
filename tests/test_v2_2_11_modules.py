"""
v2.2.11 单元测试

测试TODO编号、Skill强制执行、StateNotifier Receiver模块。
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path


class TestTodoIdGenerator:
    """TodoIdGenerator 测试"""

    def test_generate_unique_ids(self):
        """测试生成唯一ID"""
        from src.core.todo_id_generator import TodoIdGenerator

        with tempfile.TemporaryDirectory() as tmpdir:
            gen = TodoIdGenerator('1', f'{tmpdir}/counter.yaml')

            ids = [gen.generate() for _ in range(3)]

            assert ids == ['TODO-1-001', 'TODO-1-002', 'TODO-1-003']
            assert len(set(ids)) == 3  # 确保唯一

    def test_agent_prefix(self):
        """测试Agent前缀"""
        from src.core.todo_id_generator import TodoIdGenerator

        with tempfile.TemporaryDirectory() as tmpdir:
            gen1 = TodoIdGenerator('1', f'{tmpdir}/counter1.yaml')
            gen2 = TodoIdGenerator('2', f'{tmpdir}/counter2.yaml')

            id1 = gen1.generate()
            id2 = gen2.generate()

            assert id1.startswith('TODO-1-')
            assert id2.startswith('TODO-2-')

    def test_counter_persistence(self):
        """测试计数器持久化"""
        from src.core.todo_id_generator import TodoIdGenerator

        with tempfile.TemporaryDirectory() as tmpdir:
            counter_file = f'{tmpdir}/counter.yaml'

            # 第一次生成
            gen1 = TodoIdGenerator('1', counter_file)
            gen1.generate()
            gen1.generate()

            # 重新创建生成器
            gen2 = TodoIdGenerator('1', counter_file)
            next_id = gen2.generate()

            assert next_id == 'TODO-1-003'


class TestTodoMigrator:
    """TodoMigrator 测试"""

    def test_migrate_single_todo(self):
        """测试迁移单个TODO"""
        from src.core.todo_migrator import TodoMigrator

        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = f'{tmpdir}/todos.yaml'
            backup_file = f'{tmpdir}/todos_backup.yaml'

            # 创建测试数据
            with open(source_file, 'w') as f:
                yaml.dump({
                    'todos': [
                        {'id': 'TODO-001', 'content': '测试1'},
                        {'id': 'TODO-002', 'content': '测试2'}
                    ]
                }, f)

            migrator = TodoMigrator(source_file, backup_file)
            result = migrator.migrate({
                'TODO-001': '1',
                'TODO-002': '2'
            })

            assert result.migrated_count == 2
            assert len(result.errors) == 0

            # 验证迁移结果
            with open(source_file) as f:
                data = yaml.safe_load(f)

            assert data['todos'][0]['id'] == 'TODO-1-001'
            assert data['todos'][1]['id'] == 'TODO-2-002'

    def test_backup_created(self):
        """测试备份创建"""
        from src.core.todo_migrator import TodoMigrator

        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = f'{tmpdir}/todos.yaml'

            with open(source_file, 'w') as f:
                yaml.dump({'todos': [{'id': 'TODO-001', 'content': '测试'}]}, f)

            migrator = TodoMigrator(source_file)
            migrator.migrate({'TODO-001': '1'})

            assert Path(migrator.backup_file).exists()

    def test_rollback(self):
        """测试回滚"""
        from src.core.todo_migrator import TodoMigrator

        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = f'{tmpdir}/todos.yaml'

            with open(source_file, 'w') as f:
                yaml.dump({'todos': [{'id': 'TODO-001', 'content': '测试'}]}, f)

            migrator = TodoMigrator(source_file)
            migrator.migrate({'TODO-001': '1'})
            result = migrator.rollback()

            assert result is True

            with open(source_file) as f:
                data = yaml.safe_load(f)

            assert data['todos'][0]['id'] == 'TODO-001'  # 回滚到原始ID


class TestSkillEnforcerEnhanced:
    """SkillEnforcerEnhanced 测试"""

    def test_no_skill_required(self):
        """测试无需Skill检查"""
        from src.core.skill_enforcer import SkillEnforcerEnhanced

        enforcer = SkillEnforcerEnhanced()
        result = enforcer.check('unknown_command')

        assert result.passed is True

    def test_missing_skill_raises_error(self):
        """测试缺少Skill时抛出异常"""
        from src.core.skill_enforcer import SkillEnforcerEnhanced, SkillRequiredError

        class MockSkillLoader:
            def get_loaded_skills(self):
                return {}

        enforcer = SkillEnforcerEnhanced(MockSkillLoader())

        with pytest.raises(SkillRequiredError) as exc_info:
            enforcer.check('todowrite')

        assert 'todowrite' in str(exc_info.value)
        assert 'oc_collab_todo_execution' in str(exc_info.value)

    def test_skill_loaded(self):
        """测试已加载Skill通过检查"""
        from src.core.skill_enforcer import SkillEnforcerEnhanced

        class MockSkillLoader:
            def get_loaded_skills(self):
                return {'oc_collab_todo_execution': {}}

        enforcer = SkillEnforcerEnhanced(MockSkillLoader())
        result = enforcer.check('todowrite')

        assert result.passed is True


class TestSkillEmbedder:
    """SkillEmbedder 测试"""

    def test_embed_success(self):
        """测试成功嵌入"""
        from src.core.skill_embedder import SkillEmbedder

        class MockSkillLoader:
            def load_skill(self, name):
                return {
                    'content': '''
# Skill内容

1. 第一步
2. 第二步
3. 第三步
- 要点1
- 要点2
                    '''
                }

        embedder = SkillEmbedder(MockSkillLoader(), max_length=200)
        result = embedder.embed('测试内容', 'test_skill')

        assert '测试内容' in result
        assert '[Skill: test_skill]' in result

    def test_embed_nonexistent_skill(self):
        """测试嵌入不存在的Skill"""
        from src.core.skill_embedder import SkillEmbedder, SkillNotFoundError

        class MockSkillLoader:
            def load_skill(self, name):
                return None

        embedder = SkillEmbedder(MockSkillLoader())

        with pytest.raises(SkillNotFoundError):
            embedder.embed('测试内容', 'nonexistent')

    def test_embed_summary(self):
        """测试嵌入摘要"""
        from src.core.skill_embedder import SkillEmbedder

        class MockSkillLoader:
            def load_skill(self, name):
                return {'summary': '这是一个测试摘要'}

        embedder = SkillEmbedder(MockSkillLoader())
        result = embedder.embed_summary('测试内容', 'test_skill')

        assert '测试内容' in result
        assert '测试摘要' in result


class TestStateQueueManager:
    """StateQueueManager 测试"""

    def test_enqueue(self):
        """测试入队列"""
        from src.core.state_queue import StateQueueManager

        with tempfile.TemporaryDirectory() as tmpdir:
            qm = StateQueueManager(f'{tmpdir}/queue.json')

            notification = qm.enqueue({
                'event_type': 'todo.created',
                'source_agent': 'agent1',
                'target_agent': 'agent2',
                'payload': {'todo_id': 'TODO-1-001'}
            })

            assert notification.id is not None
            assert notification.event_type == 'todo.created'
            assert notification.target_agent == 'agent2'

    def test_get_unread(self):
        """测试获取未读"""
        from src.core.state_queue import StateQueueManager

        with tempfile.TemporaryDirectory() as tmpdir:
            qm = StateQueueManager(f'{tmpdir}/queue.json')

            qm.enqueue({
                'event_type': 'todo.created',
                'source_agent': 'agent1',
                'target_agent': 'agent2',
                'payload': {}
            })

            unread = qm.get_unread('agent2')
            assert len(unread) == 1

            unread_other = qm.get_unread('agent1')
            assert len(unread_other) == 0

    def test_mark_read(self):
        """测试标记已读"""
        from src.core.state_queue import StateQueueManager

        with tempfile.TemporaryDirectory() as tmpdir:
            qm = StateQueueManager(f'{tmpdir}/queue.json')

            notification = qm.enqueue({
                'event_type': 'todo.created',
                'source_agent': 'agent1',
                'target_agent': 'agent2',
                'payload': {}
            })

            result = qm.mark_read(notification.id)
            assert result is True

            unread = qm.get_unread('agent2')
            assert len(unread) == 0

    def test_mark_all_read(self):
        """测试标记所有已读"""
        from src.core.state_queue import StateQueueManager

        with tempfile.TemporaryDirectory() as tmpdir:
            qm = StateQueueManager(f'{tmpdir}/queue.json')

            qm.enqueue({
                'event_type': 'todo.created',
                'source_agent': 'agent1',
                'target_agent': 'agent2',
                'payload': {}
            })
            qm.enqueue({
                'event_type': 'todo.created',
                'source_agent': 'agent1',
                'target_agent': 'agent2',
                'payload': {}
            })

            count = qm.mark_all_read('agent2')
            assert count == 2

    def test_get_stats(self):
        """测试获取统计"""
        from src.core.state_queue import StateQueueManager

        with tempfile.TemporaryDirectory() as tmpdir:
            qm = StateQueueManager(f'{tmpdir}/queue.json')

            qm.enqueue({
                'event_type': 'todo.created',
                'source_agent': 'agent1',
                'target_agent': 'agent2',
                'payload': {}
            })

            stats = qm.get_stats('agent2')
            assert stats['total'] == 1
            assert stats['pending'] == 1
            assert stats['read'] == 0

    def test_cleanup(self):
        """测试清理"""
        from src.core.state_queue import StateQueueManager
        from datetime import datetime, timedelta

        with tempfile.TemporaryDirectory() as tmpdir:
            qm = StateQueueManager(f'{tmpdir}/queue.json')

            # 创建一个旧通知（修改时间戳为过去）
            data = qm._load()
            data["notifications"].append({
                'id': 'old-notif',
                'event_type': 'old',
                'source_agent': 'agent1',
                'target_agent': 'agent2',
                'payload': {},
                'timestamp': (datetime.utcnow() - timedelta(days=8)).isoformat(),
                'status': 'pending'
            })
            qm._save(data)

            # 设置max_age_days=7，8天前的应该被清理
            removed = qm.cleanup(max_age_days=7)
            assert removed >= 1


class TestStateReceiver:
    """StateReceiver 测试"""

    def test_health_check(self):
        """测试健康检查"""
        from src.core.state_receiver import StateReceiver
        from src.core.state_queue import StateQueueManager
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            qm = StateQueueManager(f'{tmpdir}/queue.json')
            receiver = StateReceiver(qm)

            client = receiver.app.test_client()
            response = client.get('/webhook/state/health')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'healthy'

    def test_webhook_accepted(self):
        """测试Webhook接收"""
        from src.core.state_receiver import StateReceiver
        from src.core.state_queue import StateQueueManager
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            qm = StateQueueManager(f'{tmpdir}/queue.json')
            receiver = StateReceiver(qm)

            client = receiver.app.test_client()
            response = client.post(
                '/webhook/state',
                json={
                    'event_type': 'todo.created',
                    'source_agent': 'agent1',
                    'target_agent': 'agent2',
                    'payload': {'todo_id': 'TODO-1-001'}
                }
            )

            assert response.status_code == 202
            data = json.loads(response.data)
            assert data['status'] == 'accepted'
            assert 'notification_id' in data

    def test_webhook_missing_fields(self):
        """测试Webhook缺少字段"""
        from src.core.state_receiver import StateReceiver
        from src.core.state_queue import StateQueueManager
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            qm = StateQueueManager(f'{tmpdir}/queue.json')
            receiver = StateReceiver(qm)

            client = receiver.app.test_client()
            response = client.post(
                '/webhook/state',
                json={'event_type': 'test'}  # 缺少必需字段
            )

            assert response.status_code == 400

    def test_queue_endpoint(self):
        """测试队列查询端点"""
        from src.core.state_receiver import StateReceiver
        from src.core.state_queue import StateQueueManager
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            qm = StateQueueManager(f'{tmpdir}/queue.json')
            receiver = StateReceiver(qm)

            qm.enqueue({
                'event_type': 'todo.created',
                'source_agent': 'agent1',
                'target_agent': 'agent2',
                'payload': {}
            })

            client = receiver.app.test_client()
            response = client.get('/webhook/state/queue?agent_id=agent2')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['stats']['pending'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
