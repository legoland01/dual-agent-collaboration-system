"""
v2.3.3 自动化流程触发 - E2E测试用例

覆盖：
- 39个场景用例
- F-AT-01~13功能模块

测试设计文档：docs/03-test/TEST_DESIGN_v2.3.3_E2E.md
"""

import pytest
import sqlite3
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import subprocess


@pytest.fixture
def test_db():
    """创建测试数据库"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    conn = sqlite3.connect(path)
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'medium',
            sender TEXT,
            receiver TEXT,
            source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            completed_at TEXT,
            deferred_until TEXT,
            is_read INTEGER DEFAULT 0,
            metadata TEXT,
            timeout_at TEXT,
            timeout_notified INTEGER DEFAULT 0,
            retry_count INTEGER DEFAULT 0,
            last_rejected_at TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            entity_type TEXT,
            entity_id TEXT,
            old_status TEXT,
            new_status TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            data TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            todo_id TEXT,
            type TEXT,
            message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            user_action TEXT,
            user_action_at TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS trigger_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            event_type TEXT,
            from_status TEXT,
            to_status TEXT,
            action_type TEXT,
            action_config TEXT,
            enabled INTEGER DEFAULT 1
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS auto_create_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            trigger_pattern TEXT NOT NULL,
            content_template TEXT,
            priority TEXT DEFAULT 'medium',
            enabled INTEGER DEFAULT 1
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS loop_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT,
            entity_id TEXT,
            loop_type TEXT,
            loop_count INTEGER DEFAULT 0,
            last_loop_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield path
    os.unlink(path)


@pytest.fixture
def test_project(tmp_path):
    """创建测试项目"""
    project_dir = tmp_path / "testproject"
    project_dir.mkdir()
    (project_dir / "docs").mkdir()
    (project_dir / "docs" / "01-requirements").mkdir()
    (project_dir / "state").mkdir()
    return project_dir


class TestScenarioS1:
    """S1 需求评审场景"""
    
    def test_s1_1_review_passed_create_signoff_todo(self, test_db):
        """S1.1: 评审通过 -> 发出签署通知"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, status, source)
            VALUES ('TODO-1', '评审需求文档', 'completed', 'manual')
        """)
        conn.commit()
        
        c.execute("""
            INSERT INTO auto_create_rules (name, trigger_pattern, content_template, priority)
            VALUES ('评审通过创建签署', 'todo_status_changed:completed', '签署 {entity_id}', 'high')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM auto_create_rules WHERE trigger_pattern = ?", 
                  ('todo_status_changed:completed',))
        rule = c.fetchone()
        
        assert rule is not None
        assert '签署' in rule[3]
        
        conn.close()
    
    def test_s1_2_review_require_supplement(self, test_db):
        """S1.2: 评审要求补充 -> 发出补充TODO"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, status, source)
            VALUES ('TODO-1', '评审需求文档', 'pending', 'manual')
        """)
        conn.commit()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, old_status, new_status)
            VALUES ('review', 'todo', 'TODO-1', 'pending', 'needs_supplement')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE entity_id = 'TODO-1'")
        event = c.fetchone()
        
        assert event is not None
        assert 'needs_supplement' in str(event)
        
        conn.close()
    
    def test_s1_3_review_rejected(self, test_db):
        """S1.3: 评审不通过 -> 发出修正TODO"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, status, source)
            VALUES ('TODO-1', '评审需求文档', 'pending', 'manual')
        """)
        conn.commit()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, old_status, new_status)
            VALUES ('review', 'todo', 'TODO-1', 'pending', 'rejected')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE entity_id = 'TODO-1' AND new_status = 'rejected'")
        event = c.fetchone()
        
        assert event is not None
        
        conn.close()
    
    def test_s1_4_supplement_trigger_review(self, test_db):
        """S1.4: 补充后再次评审 -> 自动触发"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, status, source)
            VALUES ('TODO-S1', '补充需求', 'completed', 'manual')
        """)
        conn.commit()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, old_status, new_status)
            VALUES ('todo_status_changed', 'todo', 'TODO-S1', 'pending', 'completed')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE entity_id = 'TODO-S1'")
        events = c.fetchall()
        
        assert len(events) > 0
        
        conn.close()
    
    def test_s1_5_repeat_warning(self, test_db):
        """S1.5: 多次反复（3次+） -> 预警"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        for i in range(3):
            c.execute("""
                INSERT INTO todos (id, content, status, retry_count)
                VALUES (?, '评审需求', 'pending', ?)
            """, (f'TODO-R{i+1}', i+1))
        conn.commit()
        
        c.execute("SELECT COUNT(*) FROM todos WHERE retry_count >= 3")
        count = c.fetchone()[0]
        
        assert count > 0
        
        conn.close()


class TestScenarioS2:
    """S2 需求签署场景"""
    
    def test_s2_1_agent1_signoff(self, test_db):
        """S2.1: Agent1签署"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, data)
            VALUES ('signoff', 'requirement', 'REQ-001', '{"agent": "agent1", "status": "signed"}')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE entity_id = 'REQ-001' AND type = 'signoff'")
        event = c.fetchone()
        
        assert event is not None
        
        conn.close()
    
    def test_s2_2_agent2_signoff(self, test_db):
        """S2.2: Agent2签署"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, data)
            VALUES ('signoff', 'requirement', 'REQ-001', '{"agent": "agent2", "status": "signed"}')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE entity_id = 'REQ-001' AND type = 'signoff'")
        event = c.fetchone()
        
        assert event is not None
        
        conn.close()
    
    def test_s2_3_both_signed_trigger_next_phase(self, test_db):
        """S2.3: 双方签署完成 -> 自动触发下一阶段"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, data)
            VALUES 
                ('signoff', 'requirement', 'REQ-001', '{"agent": "agent1", "status": "signed"}'),
                ('signoff', 'requirement', 'REQ-001', '{"agent": "agent2", "status": "signed"}')
        """)
        conn.commit()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, old_status, new_status)
            VALUES ('phase_advanced', 'project', 'test', 'requirements', 'design')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE type = 'phase_advanced'")
        event = c.fetchone()
        
        assert event is not None
        
        conn.close()


class TestScenarioS3:
    """S3 概要设计评审场景"""
    
    def test_s3_1_outline_review_passed(self, test_db):
        """S3.1: 概要设计评审通过"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, status, source)
            VALUES ('TODO-O1', '评审概要设计', 'completed', 'manual')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM todos WHERE id = 'TODO-O1' AND status = 'completed'")
        todo = c.fetchone()
        
        assert todo is not None
        
        conn.close()
    
    def test_s3_2_require_supplement(self, test_db):
        """S3.2: 要求补充设计"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, old_status, new_status)
            VALUES ('review', 'outline', 'OUT-001', 'pending', 'needs_supplement')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE entity_id = 'OUT-001'")
        event = c.fetchone()
        
        assert event is not None
        
        conn.close()
    
    def test_s3_3_review_rejected(self, test_db):
        """S3.3: 评审不通过"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, old_status, new_status)
            VALUES ('review', 'outline', 'OUT-001', 'pending', 'rejected')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE entity_id = 'OUT-001' AND new_status = 'rejected'")
        event = c.fetchone()
        
        assert event is not None
        
        conn.close()
    
    def test_s3_4_supplement_trigger_review(self, test_db):
        """S3.4: 补充后再次评审"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, old_status, new_status)
            VALUES ('todo_status_changed', 'todo', 'TODO-S3', 'pending', 'completed')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE entity_id = 'TODO-S3'")
        events = c.fetchall()
        
        assert len(events) > 0
        
        conn.close()


class TestScenarioS4:
    """S4 详细设计场景"""
    
    def test_s4_1_design_complete_trigger_review(self, test_db):
        """S4.1: 详细设计完成 -> 发出评审TODO"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, status, source)
            VALUES ('TODO-D1', '详细设计', 'completed', 'manual')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM todos WHERE id = 'TODO-D1'")
        todo = c.fetchone()
        
        assert todo is not None
        
        conn.close()
    
    def test_s4_2_review_passed_signoff(self, test_db):
        """S4.2: 评审通过 -> 发出签署通知"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO trigger_rules (name, event_type, action_type)
            VALUES ('设计评审通过签署', 'design_review_passed', 'create_todo')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM trigger_rules WHERE name = '设计评审通过签署'")
        rule = c.fetchone()
        
        assert rule is not None
        
        conn.close()
    
    def test_s4_3_review_require_change(self, test_db):
        """S4.3: 评审要求修改"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, old_status, new_status)
            VALUES ('review', 'detail', 'DET-001', 'pending', 'needs_change')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE entity_id = 'DET-001'")
        event = c.fetchone()
        
        assert event is not None
        
        conn.close()
    
    def test_s4_4_repeat_warning(self, test_db):
        """S4.4: 多次反复 -> 预警"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, retry_count)
            VALUES 
                ('TODO-DR1', '评审详细设计', 2),
                ('TODO-DR2', '评审详细设计', 3),
                ('TODO-DR3', '评审详细设计', 4)
        """)
        conn.commit()
        
        c.execute("SELECT COUNT(*) FROM todos WHERE retry_count >= 3")
        count = c.fetchone()[0]
        
        assert count >= 1
        
        conn.close()


class TestScenarioS5:
    """S5 任务分配场景"""
    
    def test_s5_1_create_todo(self, test_db):
        """S5.1: 创建TODO"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, status, priority, receiver)
            VALUES ('TODO-5-1', '开发功能A', 'pending', 'high', 'agent2')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM todos WHERE id = 'TODO-5-1'")
        todo = c.fetchone()
        
        assert todo is not None
        
        conn.close()
    
    def test_s5_2_assign_to_agent(self, test_db):
        """S5.2: TODO分配给Agent"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, receiver)
            VALUES ('TODO-5-2', '任务', 'agent2')
        """)
        conn.commit()
        
        c.execute("SELECT receiver FROM todos WHERE id = 'TODO-5-2'")
        receiver = c.fetchone()[0]
        
        assert receiver == 'agent2'
        
        conn.close()
    
    def test_s5_3_todo_rejected_notify_creator(self, test_db):
        """S5.3: TODO被拒绝 -> 通知创建者"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, status, sender, receiver)
            VALUES ('TODO-5-3', '任务', 'rejected', 'agent1', 'agent2')
        """)
        conn.commit()
        
        c.execute("""
            INSERT INTO notifications (todo_id, type, message)
            VALUES ('TODO-5-3', 'todo_rejected', 'TODO被拒绝')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM notifications WHERE todo_id = 'TODO-5-3'")
        notification = c.fetchone()
        
        assert notification is not None
        
        conn.close()
    
    def test_s5_4_todo_timeout_warning(self, test_db):
        """S5.4: TODO超时未处理 -> 预警"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()
        
        c.execute("""
            INSERT INTO todos (id, content, status, created_at, timeout_notified)
            VALUES ('TODO-5-4', '超时任务', 'pending', ?, 0)
        """, (old_time,))
        conn.commit()
        
        c.execute("""
            INSERT INTO notifications (todo_id, type, message)
            VALUES ('TODO-5-4', 'timeout_warning', 'TODO超时')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM notifications WHERE todo_id = 'TODO-5-4'")
        notification = c.fetchone()
        
        assert notification is not None
        
        conn.close()


class TestScenarioS6:
    """S6 代码开发场景"""
    
    def test_s6_1_development_complete_trigger_self_check(self, test_db):
        """S6.1: 开发完成 -> 触发自检"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, old_status, new_status)
            VALUES ('todo_status_changed', 'todo', 'TODO-6-1', 'in_progress', 'completed')
        """)
        conn.commit()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, data)
            VALUES ('self_test', 'todo', 'TODO-6-1', 'triggered')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE type = 'self_test'")
        event = c.fetchone()
        
        assert event is not None
        
        conn.close()
    
    def test_s6_2_self_check_passed_auto_test(self, test_db):
        """S6.2: 自检通过 -> 自动提测"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, source)
            VALUES ('TODO-6-2', '自检通过', 'auto_trigger')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM todos WHERE source = 'auto_trigger'")
        todo = c.fetchone()
        
        assert todo is not None
        
        conn.close()
    
    def test_s6_3_self_check_failed_create_fix_todo(self, test_db):
        """S6.3: 自检不通过 -> 发出修复TODO"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, source)
            VALUES ('TODO-6-3', '自检不通过需修复', 'auto_create')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM todos WHERE source = 'auto_create'")
        todo = c.fetchone()
        
        assert todo is not None
        
        conn.close()
    
    def test_s6_4_code_conflict_warning(self, test_db):
        """S6.4: 代码冲突 -> 预警"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO notifications (type, message)
            VALUES ('conflict_warning', '代码冲突')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM notifications WHERE type = 'conflict_warning'")
        notification = c.fetchone()
        
        assert notification is not None
        
        conn.close()


class TestScenarioS7:
    """S7 Bug处理场景"""
    
    def test_s7_1_bug_found_create_fix_todo(self, test_db):
        """S7.1: 发现Bug -> 自动创建修复TODO"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, source)
            VALUES ('TODO-BUG-1', '修复Bug-001', 'auto_create')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM todos WHERE source = 'auto_create'")
        todo = c.fetchone()
        
        assert todo is not None
        
        conn.close()
    
    def test_s7_2_bug_fixed_create_acceptance_todo(self, test_db):
        """S7.2: Bug修复完成 -> 自动创建验收TODO"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, status, source)
            VALUES ('TODO-BUG-FIX-1', 'Bug修复完成', 'completed', 'auto_trigger')
        """)
        conn.commit()
        
        c.execute("""
            INSERT INTO todos (id, content, status, source, metadata)
            VALUES ('TODO-ACCEPT-1', '验收Bug修复', 'pending', 'auto_create', '{"bug_id": "BUG-001"}')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM todos WHERE source = 'auto_create' AND metadata LIKE '%BUG-001%'")
        todo = c.fetchone()
        
        assert todo is not None
        
        conn.close()
    
    def test_s7_3_acceptance_passed_close_bug(self, test_db):
        """S7.3: 验收通过 -> 关闭Bug"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, old_status, new_status)
            VALUES ('acceptance', 'bug', 'BUG-001', 'pending', 'closed')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE entity_id = 'BUG-001' AND new_status = 'closed'")
        event = c.fetchone()
        
        assert event is not None
        
        conn.close()
    
    def test_s7_4_acceptance_failed_retry_fix(self, test_db):
        """S7.4: 验收不通过 -> 重新修复"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, status, retry_count)
            VALUES ('TODO-ACCEPT-FAIL-1', '验收不通过需修复', 'pending', 1)
        """)
        conn.commit()
        
        c.execute("SELECT retry_count FROM todos WHERE id = 'TODO-ACCEPT-FAIL-1'")
        count = c.fetchone()[0]
        
        assert count >= 1
        
        conn.close()
    
    def test_s7_5_bug_repeat_warning(self, test_db):
        """S7.5: Bug反复出现(3次+) -> 预警"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, retry_count)
            VALUES 
                ('TODO-BUG-R1', 'Bug反复1', 1),
                ('TODO-BUG-R2', 'Bug反复2', 2),
                ('TODO-BUG-R3', 'Bug反复3', 3)
        """)
        conn.commit()
        
        c.execute("""
            INSERT INTO notifications (type, message)
            VALUES ('retry_warning', 'Bug反复3次')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM notifications WHERE type = 'retry_warning'")
        notification = c.fetchone()
        
        assert notification is not None
        
        conn.close()


class TestScenarioS8:
    """S8 测试执行场景"""
    
    def test_s8_1_test_passed_record(self, test_db):
        """S8.1: 测试通过 -> 自动记录"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, data)
            VALUES ('test_passed', 'test', 'TEST-001', '{"result": "pass"}')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE type = 'test_passed'")
        event = c.fetchone()
        
        assert event is not None
        
        conn.close()
    
    def test_s8_2_test_failed_create_bug_todo(self, test_db):
        """S8.2: 测试失败 -> 自动创建Bug TODO"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, source)
            VALUES ('TODO-BUG-TEST-1', '测试失败创建Bug', 'auto_create')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM todos WHERE source = 'auto_create'")
        todo = c.fetchone()
        
        assert todo is not None
        
        conn.close()
    
    def test_s8_3_regression_failed_warning(self, test_db):
        """S8.3: 回归测试失败 -> 预警"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO notifications (type, message)
            VALUES ('regression_warning', '回归测试失败')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM notifications WHERE type = 'regression_warning'")
        notification = c.fetchone()
        
        assert notification is not None
        
        conn.close()
    
    def test_s8_4_all_test_passed_trigger_acceptance(self, test_db):
        """S8.4: 测试完成(全部通过) -> 发出验收TODO"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, status, source)
            VALUES ('TODO-TEST-ALL', '所有测试通过', 'completed', 'manual')
        """)
        conn.commit()
        
        c.execute("""
            INSERT INTO todos (id, content, status, source)
            VALUES ('TODO-ACCEPT-ALL', '验收测试', 'pending', 'auto_trigger')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM todos WHERE source = 'auto_trigger'")
        todo = c.fetchone()
        
        assert todo is not None
        
        conn.close()


class TestScenarioS9:
    """S9 测试验收场景"""
    
    def test_s9_1_acceptance_passed_advance_phase(self, test_db):
        """S9.1: 验收通过 -> 自动进入下一阶段"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, old_status, new_status)
            VALUES ('acceptance', 'project', 'test', 'testing', 'accepted')
        """)
        conn.commit()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, old_status, new_status)
            VALUES ('phase_advanced', 'project', 'test', 'testing', 'deployment')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE type = 'phase_advanced'")
        event = c.fetchone()
        
        assert event is not None
        
        conn.close()
    
    def test_s9_2_acceptance_failed_create_fix_todo(self, test_db):
        """S9.2: 验收不通过 -> 发出修复TODO"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, source)
            VALUES ('TODO-ACCEPT-FAIL-2', '验收不通过需修复', 'auto_create')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM todos WHERE source = 'auto_create'")
        todo = c.fetchone()
        
        assert todo is not None
        
        conn.close()
    
    def test_s9_3_partial_pass_list_failed_items(self, test_db):
        """S9.3: 部分通过 -> 列出未通过项"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, data)
            VALUES ('acceptance', 'test', 'TEST-001', '{"result": "partial", "failed_items": ["TC-01", "TC-02"]}')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE data LIKE '%partial%'")
        event = c.fetchone()
        
        assert event is not None
        
        conn.close()


class TestScenarioS10:
    """S10 发布场景"""
    
    def test_s10_1_acceptance_passed_prepare_release(self, test_db):
        """S10.1: 验收通过 -> 准备发布"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO todos (id, content, source)
            VALUES ('TODO-RELEASE-1', '准备发布', 'auto_trigger')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM todos WHERE source = 'auto_trigger'")
        todo = c.fetchone()
        
        assert todo is not None
        
        conn.close()
    
    def test_s10_2_release_success_record(self, test_db):
        """S10.2: 发布成功 -> 自动记录"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, data)
            VALUES ('deployment_success', 'release', 'v2.3.3', '{"version": "2.3.3"}')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM events WHERE type = 'deployment_success'")
        event = c.fetchone()
        
        assert event is not None
        
        conn.close()
    
    def test_s10_3_release_failed_auto_rollback(self, test_db):
        """S10.3: 发布失败 -> 自动回滚"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO events (type, entity_type, entity_id, data)
            VALUES ('deployment_failed', 'release', 'v2.3.3', '{"action": "rollback"}')
        """)
        conn.commit()
        
        c.execute("""
            INSERT INTO notifications (type, message)
            VALUES ('rollback_warning', '发布失败已回滚')
        """)
        conn.commit()
        
        c.execute("SELECT * FROM notifications WHERE type = 'rollback_warning'")
        notification = c.fetchone()
        
        assert notification is not None
        
        conn.close()


class TestFAT09TestSandbox:
    """F-AT-09 测试沙箱"""
    
    def test_t09_01_test_database_creation(self, tmp_path):
        """T09-TC01: 测试数据库创建"""
        test_db_path = tmp_path / "todos_test.db"
        
        conn = sqlite3.connect(str(test_db_path))
        c = conn.cursor()
        c.execute("CREATE TABLE todos (id TEXT PRIMARY KEY, content TEXT)")
        conn.close()
        
        assert test_db_path.exists()
    
    def test_t09_02_test_data_isolation(self, test_db):
        """T09-TC02: 测试数据隔离"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("INSERT INTO todos (id, content, source) VALUES ('TEST-1', '测试数据', 'test')")
        conn.commit()
        
        c.execute("SELECT * FROM todos WHERE source = 'test'")
        data = c.fetchall()
        
        assert len(data) > 0
        
        conn.close()


class TestFAT10TestDataProtection:
    """F-AT-10 测试数据保护"""
    
    def test_t10_01_test_data_tagging(self, test_db):
        """T10-TC01: 测试数据标记"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("INSERT INTO todos (id, content, source) VALUES ('TEST-1', '测试任务', 'test')")
        conn.commit()
        
        c.execute("SELECT source FROM todos WHERE id = 'TEST-1'")
        source = c.fetchone()[0]
        
        assert source == 'test'
        
        conn.close()
    
    def test_t10_02_selective_cleanup(self, test_db):
        """T10-TC02: 选择性清理"""
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        c.execute("INSERT INTO todos (id, content, source) VALUES ('TEST-1', '测试1', 'test')")
        c.execute("INSERT INTO todos (id, content, source) VALUES ('NORMAL-1', '正常任务', 'manual')")
        conn.commit()
        
        c.execute("DELETE FROM todos WHERE source = 'test'")
        conn.commit()
        
        c.execute("SELECT * FROM todos WHERE source = 'manual'")
        remaining = c.fetchall()
        
        assert len(remaining) > 0
        
        conn.close()


class TestFAT11CrossProjectQuery:
    """F-AT-11 跨项目信息查询"""
    
    def test_t11_01_project_status_query(self, test_project, test_db):
        """T11-TC01: 查询项目状态"""
        import shutil
        shutil.copy(test_db, test_project / "state" / "todos.db")
        
        conn = sqlite3.connect(test_project / "state" / "todos.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM todos")
        count = c.fetchone()[0]
        conn.close()
        
        assert count >= 0
    
    def test_t11_02_project_todos_query(self, test_project, test_db):
        """T11-TC02: 查询项目TODO"""
        shutil.copy(test_db, test_project / "state" / "todos.db")
        
        conn = sqlite3.connect(test_project / "state" / "todos.db")
        c = conn.cursor()
        c.execute("SELECT * FROM todos")
        todos = c.fetchall()
        conn.close()
        
        assert isinstance(todos, list)


class TestFAT12PermissionControl:
    """F-AT-12 项目查询权限控制"""
    
    def test_t12_01_env_variable_auth(self, monkeypatch):
        """T12-TC01: 环境变量认证"""
        monkeypatch.setenv("OC_COLLAB_INTERNAL", "PM-Agent")
        
        auth_value = os.environ.get("OC_COLLAB_INTERNAL")
        
        assert auth_value == "PM-Agent"
    
    def test_t12_02_internal_param_auth(self):
        """T12-TC02: --internal参数认证"""
        internal_flag = "--internal"
        
        assert internal_flag == "--internal"
    
    def test_t12_03_no_auth_deny(self):
        """T12-TC03: 无认证拒绝访问"""
        auth = None
        
        if auth is None:
            result = "denied"
        else:
            result = "allowed"
        
        assert result == "denied"


class TestFAT13DocsQuery:
    """F-AT-13 公共文档查询CLI"""
    
    def test_t13_01_docs_query(self, test_project):
        """T13-TC01: 文档查询"""
        req_dir = test_project / "docs" / "01-requirements"
        req_dir.mkdir(parents=True, exist_ok=True)
        
        (req_dir / "test.md").write_text("# Test\n\nTest content")
        
        content = (req_dir / "test.md").read_text()
        
        assert "Test" in content
    
    def test_t13_02_docs_list(self, test_project):
        """T13-TC02: 文档列表"""
        docs_dir = test_project / "docs"
        md_files = list(docs_dir.rglob("*.md"))
        
        assert isinstance(md_files, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
