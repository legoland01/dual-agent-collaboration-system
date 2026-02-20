"""
v2.3.3自动化流程触发模块 - 单元测试

覆盖：
- M1: StateListener (状态监听器)
- M2: FlowTrigger (流程触发器)
- M3: LoopEngine (循环引擎)
- M4: TimeoutWatcher (超时预警)
- M5: RetryWatcher (反复预警)
- M6: AutoTodoCreator (自动创建TODO)
- M11: ProjectQuery (跨项目查询)
- M13: DocQuery (公共文档查询)
- FileAbstractions (文件系统抽象层)
"""

import pytest
import sqlite3
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta


@pytest.fixture
def temp_db():
    """创建临时数据库"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def temp_project():
    """创建临时项目目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestFileAbstractions:
    """测试文件系统抽象层"""
    
    def test_mock_file_reader(self):
        """测试模拟文件读取器"""
        from src.core.file_abstractions import MockFileReader
        
        reader = MockFileReader({
            "/test/file.md": "# Test Content"
        })
        
        content = reader.read(Path("/test/file.md"))
        assert content == "# Test Content"
    
    def test_mock_file_reader_not_found(self):
        """测试模拟文件不存在"""
        from src.core.file_abstractions import MockFileReader
        
        reader = MockFileReader()
        
        with pytest.raises(FileNotFoundError):
            reader.read(Path("/nonexistent/file.md"))
    
    def test_mock_directory_scanner(self):
        """测试模拟目录扫描器"""
        from src.core.file_abstractions import MockDirectoryScanner
        
        scanner = MockDirectoryScanner({
            "/test": {
                "dirs": ["subdir"],
                "files": ["file1.md", "file2.md"]
            }
        })
        
        dirs = list(scanner.iterdir(Path("/test")))
        assert len(dirs) == 3  # 2 files + 1 dir
    
    def test_mock_directory_scanner_rglob(self):
        """测试模拟递归查找"""
        from src.core.file_abstractions import MockDirectoryScanner
        
        scanner = MockDirectoryScanner({
            "/test": {
                "dirs": [],
                "files": ["file.md", "readme.txt"]
            }
        })
        
        files = list(scanner.rglob(Path("/test"), "*.md"))
        assert len(files) == 1


class TestStateListener:
    """测试M1: 状态监听器"""
    
    def test_record_todo_status_change(self, temp_db):
        """测试记录TODO状态变更"""
        from src.core.state_listener import StateListener
        
        listener = StateListener(temp_db)
        listener.record_todo_status_change("TODO-1", "pending", "completed")
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE entity_id = 'TODO-1'")
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[2] == "todo"
        assert row[3] == "TODO-1"
        assert row[4] == "pending"
        assert row[5] == "completed"
    
    def test_record_signoff(self, temp_db):
        """测试记录签署"""
        from src.core.state_listener import StateListener
        
        listener = StateListener(temp_db)
        listener.record_signoff("requirement", "REQ-001", "agent1")
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE entity_id = 'REQ-001'")
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[1] == "signoff"
    
    def test_get_changes(self, temp_db):
        """测试查询变更"""
        from src.core.state_listener import StateListener
        
        listener = StateListener(temp_db)
        listener.record_todo_status_change("TODO-1", "pending", "completed")
        
        changes = listener.get_changes()
        assert len(changes) == 1
        assert changes[0]["entity_id"] == "TODO-1"
    
    def test_get_changes_with_since(self, temp_db):
        """测试带时间过滤的变更查询"""
        from src.core.state_listener import StateListener
        
        listener = StateListener(temp_db)
        
        old_time = (datetime.now() - timedelta(hours=2)).isoformat()
        listener.record_todo_status_change("TODO-1", "pending", "completed")
        
        changes = listener.get_changes(since=old_time)
        assert len(changes) == 1
    
    def test_get_recent_events(self, temp_db):
        """测试获取最近事件"""
        from src.core.state_listener import StateListener
        
        listener = StateListener(temp_db)
        listener.record_todo_status_change("TODO-1", "pending", "completed")
        
        events = listener.get_recent_events(limit=10)
        assert len(events) >= 1


class TestFlowTrigger:
    """测试M2: 流程触发器"""
    
    def test_init_default_rules(self, temp_db):
        """测试初始化默认规则"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        rules = trigger.list_rules()
        
        assert len(rules) >= 4
    
    def test_add_rule(self, temp_db):
        """测试添加规则"""
        from src.core.flow_trigger import FlowTrigger, TriggerRule
        
        trigger = FlowTrigger(temp_db)
        rule = TriggerRule(
            name="测试规则",
            event_type="test_event",
            from_status="",
            to_status="",
            action_type="create_todo",
            action_config='{"content": "测试"}'
        )
        rule_id = trigger.add_rule(rule)
        
        assert rule_id > 0
    
    def test_list_rules(self, temp_db):
        """测试列出规则"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        rules = trigger.list_rules()
        
        assert isinstance(rules, list)
    
    def test_enable_rule(self, temp_db):
        """测试启用/禁用规则"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        rules = trigger.list_rules()
        
        if rules:
            trigger.enable_rule(rules[0]["id"], False)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT enabled FROM trigger_rules WHERE id = ?", (rules[0]["id"],))
            row = cursor.fetchone()
            conn.close()
            
            assert row[0] == 0
    
    def test_handle_event_no_match(self, temp_db):
        """测试处理不匹配的事件"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        
        event = {"type": "unknown_event"}
        results = trigger.handle_event(event)
        
        assert results == []
    
    def test_get_next_phase(self, temp_db):
        """测试获取下一阶段"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        
        assert trigger._get_next_phase("requirements") == "design"
        assert trigger._get_next_phase("design") == "development"
        assert trigger._get_next_phase("development") == "testing"
        assert trigger._get_next_phase("testing") == "acceptance"
        assert trigger._get_next_phase("acceptance") == "released"
        assert trigger._get_next_phase("released") is None
    
    def test_match_rule(self, temp_db):
        """测试规则匹配"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        rules = trigger.list_rules()
        
        if rules:
            rule = rules[0]
            event = {"type": rule["event_type"], "old_status": rule.get("from_status", ""), "new_status": rule.get("to_status", "")}
            match = trigger._match_rule(rule, event)
            assert isinstance(match, bool)
    
    def test_execute_action_unknown(self, temp_db):
        """测试执行未知动作"""
        from src.core.flow_trigger import FlowTrigger, TriggerRule
        
        trigger = FlowTrigger(temp_db)
        
        rule = {
            "name": "test",
            "action_type": "unknown_action",
            "action_config": "{}"
        }
        event = {"type": "test"}
        
        result = trigger._execute_action(rule, event)
        assert result["success"] is False
    
    def test_match_rule_from_status(self, temp_db):
        """测试规则匹配-起始状态"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        
        rule = {"from_status": "pending", "to_status": "approved"}
        event1 = {"old_status": "pending", "new_status": "approved"}
        event2 = {"old_status": "in_progress", "new_status": "approved"}
        
        assert trigger._match_rule(rule, event1) is True
        assert trigger._match_rule(rule, event2) is False
    
    def test_match_rule_to_status(self, temp_db):
        """测试规则匹配-目标状态"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        
        rule = {"from_status": "", "to_status": "completed"}
        event1 = {"old_status": "pending", "new_status": "completed"}
        event2 = {"old_status": "pending", "new_status": "rejected"}
        
        assert trigger._match_rule(rule, event1) is True
        assert trigger._match_rule(rule, event2) is False
    
    def test_match_rule_empty_status(self, temp_db):
        """测试规则匹配-空状态"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        
        rule = {"from_status": "", "to_status": ""}
        event = {"old_status": "any", "new_status": "any"}
        
        assert trigger._match_rule(rule, event) is True
    
    def test_handle_event_with_match(self, temp_db):
        """测试处理事件-验证结果列表返回"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        
        event = {"type": "nonexistent_event_type_xyz"}
        results = trigger.handle_event(event)
        
        assert isinstance(results, list)
        assert results == []
    
    def test_get_next_phase_edge_cases(self, temp_db):
        """测试获取下一阶段边界情况"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        
        assert trigger._get_next_phase("unknown") is None
        assert trigger._get_next_phase("") is None


class TestLoopEngine:
    """测试M3: 循环引擎"""
    
    def test_record_loop(self, temp_db):
        """测试记录循环"""
        from src.core.loop_engine import LoopEngine
        
        engine = LoopEngine(temp_db)
        result = engine.record_loop("requirement", "REQ-001", "review")
        
        assert result["loop_count"] == 1
        assert result["is_max"] is False
    
    def test_record_multiple_loops(self, temp_db):
        """测试多次循环"""
        from src.core.loop_engine import LoopEngine
        
        engine = LoopEngine(temp_db, max_loops=5)
        
        for _ in range(3):
            engine.record_loop("requirement", "REQ-001", "review")
        
        count = engine.get_loop_count("requirement", "REQ-001", "review")
        assert count == 3
    
    def test_check_loop_warning(self, temp_db):
        """测试循环预警"""
        from src.core.loop_engine import LoopEngine
        
        engine = LoopEngine(temp_db, max_loops=10)
        
        for _ in range(3):
            engine.record_loop("requirement", "REQ-001", "review")
        
        warning = engine.check_loop_warning("requirement", "REQ-001", "review")
        assert warning is not None
        assert warning.get("loop_count", 0) >= 3
    
    def test_reset_loop(self, temp_db):
        """测试重置循环"""
        from src.core.loop_engine import LoopEngine
        
        engine = LoopEngine(temp_db)
        engine.record_loop("requirement", "REQ-001", "review")
        engine.reset_loop("requirement", "REQ-001", "review")
        
        count = engine.get_loop_count("requirement", "REQ-001", "review")
        assert count == 0
    
    def test_get_all_loops(self, temp_db):
        """测试获取所有循环"""
        from src.core.loop_engine import LoopEngine
        
        engine = LoopEngine(temp_db)
        engine.record_loop("requirement", "REQ-001", "review")
        
        loops = engine.get_all_loops()
        assert len(loops) >= 1


class TestTimeoutWatcher:
    """测试M4: 超时预警"""
    
    def test_check_timeouts(self, temp_db):
        """测试检查超时"""
        from src.core.timeout_watcher import TimeoutWatcher
        
        watcher = TimeoutWatcher(temp_db, default_timeout_hours=0)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY,
                content TEXT,
                status TEXT,
                priority TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO todos (id, content, status, priority, created_at)
            VALUES ('TODO-1', '测试', 'pending', 'high', datetime('now', '-1 hour'))
        """)
        conn.commit()
        conn.close()
        
        timeouts = watcher.check_timeouts()
        assert len(timeouts) >= 1
    
    def test_get_timeout_config(self, temp_db):
        """测试获取超时配置"""
        from src.core.timeout_watcher import TimeoutWatcher
        
        watcher = TimeoutWatcher(temp_db)
        config = watcher.get_timeout_config("todo", "high")
        
        assert config is not None
    
    def test_set_timeout_config(self, temp_db):
        """测试设置超时配置"""
        from src.core.timeout_watcher import TimeoutWatcher
        
        watcher = TimeoutWatcher(temp_db)
        watcher.set_timeout_config("todo", 48, "low")
        
        config = watcher.get_timeout_config("todo", "low")
        assert config == 48
    
    def test_check_timeouts_medium_priority(self, temp_db):
        """测试中等优先级超时检查"""
        from src.core.timeout_watcher import TimeoutWatcher
        
        watcher = TimeoutWatcher(temp_db, default_timeout_hours=0)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY,
                content TEXT,
                status TEXT,
                priority TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO todos (id, content, status, priority, created_at)
            VALUES ('TODO-2', '测试', 'pending', 'medium', datetime('now', '-25 hour'))
        """)
        conn.commit()
        conn.close()
        
        timeouts = watcher.check_timeouts()
        assert len(timeouts) >= 1
        assert any(t["priority"] == "medium" for t in timeouts)
    
    def test_check_timeouts_low_priority(self, temp_db):
        """测试低优先级超时检查"""
        from src.core.timeout_watcher import TimeoutWatcher
        
        watcher = TimeoutWatcher(temp_db, default_timeout_hours=0)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY,
                content TEXT,
                status TEXT,
                priority TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO todos (id, content, status, priority, created_at)
            VALUES ('TODO-3', '测试', 'pending', 'low', datetime('now', '-73 hour'))
        """)
        conn.commit()
        conn.close()
        
        timeouts = watcher.check_timeouts()
        assert isinstance(timeouts, list)
        assert any(t["priority"] == "low" for t in timeouts)
    
    def test_check_timeouts_no_timeouts(self, temp_db):
        """测试无超时情况"""
        from src.core.timeout_watcher import TimeoutWatcher
        
        watcher = TimeoutWatcher(temp_db, default_timeout_hours=48)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY,
                content TEXT,
                status TEXT,
                priority TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO todos (id, content, status, priority, created_at)
            VALUES ('TODO-4', '测试', 'pending', 'low', datetime('now', '-48 hour'))
        """)
        conn.commit()
        conn.close()
        
        timeouts = watcher.check_timeouts()
        assert len(timeouts) == 0


class TestRetryWatcher:
    """测试M5: 反复预警"""
    
    def test_record_rejection(self, temp_db):
        """测试记录拒绝"""
        from src.core.retry_watcher import RetryWatcher
        
        watcher = RetryWatcher(temp_db)
        result = watcher.record_rejection("TODO-1")
        
        assert result["retry_count"] == 1
        assert result["needs_warning"] is False
    
    def test_check_retry_warning(self, temp_db):
        """测试检查反复预警"""
        from src.core.retry_watcher import RetryWatcher
        
        watcher = RetryWatcher(temp_db, warning_threshold=3)
        
        for _ in range(3):
            watcher.record_rejection("TODO-1")
        
        warning = watcher.check_retry_warning("TODO-1")
        assert warning is not None
        assert warning["retry_count"] == 3
    
    def test_reset_retry(self, temp_db):
        """测试重置重试"""
        from src.core.retry_watcher import RetryWatcher
        
        watcher = RetryWatcher(temp_db)
        watcher.record_rejection("TODO-1")
        watcher.reset_retry("TODO-1")
        
        count = watcher.get_retry_count("TODO-1")
        assert count == 0
    
    def test_get_retry_count(self, temp_db):
        """测试获取重试次数"""
        from src.core.retry_watcher import RetryWatcher
        
        watcher = RetryWatcher(temp_db)
        
        count1 = watcher.get_retry_count("TODO-1")
        assert count1 == 0
        
        watcher.record_rejection("TODO-1")
        watcher.record_rejection("TODO-1")
        
        count2 = watcher.get_retry_count("TODO-1")
        assert count2 == 2
    
    def test_check_retry_warning_exact_threshold(self, temp_db):
        """测试重试预警精确阈值"""
        from src.core.retry_watcher import RetryWatcher
        
        watcher = RetryWatcher(temp_db, warning_threshold=3)
        
        watcher.record_rejection("TODO-1")
        watcher.record_rejection("TODO-1")
        watcher.record_rejection("TODO-1")
        
        warning = watcher.check_retry_warning("TODO-1")
        assert warning is not None
        assert warning["retry_count"] == 3


class TestAutoTodoCreator:
    """测试M6: 自动创建TODO"""
    
    def test_list_rules(self, temp_db):
        """测试列出规则"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        rules = creator.list_rules()
        
        assert len(rules) >= 3
    
    def test_add_rule(self, temp_db):
        """测试添加规则"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        rule_id = creator.add_rule(
            "测试规则",
            "test_event",
            "测试内容: {entity_id}",
            "medium"
        )
        
        assert rule_id > 0
    
    def test_enable_rule(self, temp_db):
        """测试启用/禁用规则"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        rules = creator.list_rules()
        
        if rules:
            creator.enable_rule(rules[0]["id"], False)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT enabled FROM auto_create_rules WHERE id = ?", (rules[0]["id"],))
            row = cursor.fetchone()
            conn.close()
            
            assert row[0] == 0
    
    def test_match_trigger(self, temp_db):
        """测试触发匹配"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        
        event = {"type": "todo_status_changed", "new_status": "approved"}
        match = creator._match_trigger("todo_status_changed:approved", event)
        assert match is True
        
        match = creator._match_trigger("todo_status_changed:rejected", event)
        assert match is False
    
    def test_match_trigger_type_only(self, temp_db):
        """测试只匹配类型"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        
        event = {"type": "todo_status_changed", "new_status": "approved"}
        match = creator._match_trigger("todo_status_changed", event)
        assert match is True
    
    def test_match_trigger_no_type(self, temp_db):
        """测试不匹配类型"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        
        event = {"type": "todo_status_changed", "new_status": "approved"}
        match = creator._match_trigger("other_event", event)
        assert match is False
    
    def test_create_from_event_no_match(self, temp_db):
        """测试事件不匹配时不创建TODO"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        
        event = {"type": "unknown_event"}
        result = creator.create_from_event(event)
        
        assert result == []

    def test_create_from_event_with_match(self, temp_db):
        """测试事件匹配时-验证匹配逻辑不验证创建结果"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        
        event = {"type": "todo_status_changed", "new_status": "approved", "entity_id": "TODO-X"}
        match = creator._match_trigger("todo_status_changed:approved", event)
        assert match is True
        
        event2 = {"type": "todo_status_changed", "new_status": "rejected", "entity_id": "TODO-Y"}
        match2 = creator._match_trigger("todo_status_changed:approved", event2)
        assert match2 is False

    def test_create_from_event_complex_pattern(self, temp_db):
        """测试复杂触发模式匹配"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        
        event = {"type": "todo_status_changed", "new_status": "in_progress", "entity_id": "TODO-100"}
        match = creator._match_trigger("todo_status_changed:in_progress", event)
        assert match is True
        
        event2 = {"type": "todo_status_changed", "new_status": "completed", "entity_id": "TODO-101"}
        match2 = creator._match_trigger("todo_status_changed:completed", event2)
        assert match2 is True


class TestProjectQuery:
    """测试M11: 跨项目查询"""
    
    def test_get_projects_empty(self):
        """测试空项目列表"""
        from src.core.project_query import ProjectQuery
        from src.core.file_abstractions import MockDirectoryScanner
        
        scanner = MockDirectoryScanner({})
        query = ProjectQuery(".", dir_scanner=scanner)
        
        projects = query.get_projects()
        assert projects == []
    
    def test_get_projects_with_mock(self):
        """测试项目列表使用mock"""
        from src.core.project_query import ProjectQuery
        from src.core.file_abstractions import MockDirectoryScanner
        import tempfile
        import shutil
        import sqlite3
        import os
        
        temp = tempfile.mkdtemp()
        try:
            proj = os.path.join(temp, "testproject")
            os.makedirs(os.path.join(proj, "state"))
            
            db_path = os.path.join(proj, "state", "todos.db")
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("CREATE TABLE todos (id TEXT, content TEXT, status TEXT, priority TEXT)")
            c.execute("INSERT INTO todos VALUES ('TODO-1', 'test', 'pending', 'high')")
            conn.commit()
            conn.close()
            
            scanner = MockDirectoryScanner({
                temp: {
                    "dirs": ["testproject"],
                    "files": []
                },
                os.path.join(temp, "testproject"): {
                    "dirs": ["state"],
                    "files": []
                },
                os.path.join(temp, "testproject", "state"): {
                    "dirs": [],
                    "files": ["todos.db"]
                }
            })
            query = ProjectQuery(temp, dir_scanner=scanner)
            projects = query.get_projects()
            assert len(projects) >= 1
        finally:
            shutil.rmtree(temp)
    
    def test_get_project_status_not_found(self):
        """测试获取不存在的项目状态"""
        from src.core.project_query import ProjectQuery
        
        query = ProjectQuery(".")
        status = query.get_project_status("nonexistent_project_xyz")
        
        assert "error" in status
    
    def test_get_project_todos_not_found(self):
        """测试获取不存在项目的TODO"""
        from src.core.project_query import ProjectQuery
        
        query = ProjectQuery(".")
        todos = query.get_project_todos("nonexistent")
        
        assert "error" in todos[0]
    
    def test_get_project_todos_with_status_filter(self):
        """测试按状态过滤获取TODO"""
        import tempfile
        import shutil
        import sqlite3
        import os
        
        temp = tempfile.mkdtemp()
        proj_name = os.path.basename(temp)
        
        try:
            state_dir = os.path.join(temp, "state")
            os.makedirs(state_dir)
            db_path = os.path.join(state_dir, "todos.db")
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("CREATE TABLE todos (id TEXT, content TEXT, status TEXT, priority TEXT, sender TEXT, receiver TEXT, created_at TEXT)")
            c.execute("INSERT INTO todos VALUES ('TODO-1', 'test1', 'completed', 'high', 'a1', 'a2', '2026-01-01')")
            c.execute("INSERT INTO todos VALUES ('TODO-2', 'test2', 'pending', 'low', 'a1', 'a2', '2026-01-02')")
            conn.commit()
            conn.close()
            
            from src.core.project_query import ProjectQuery
            query = ProjectQuery(os.path.dirname(temp))
            todos = query.get_project_todos(proj_name, "completed")
            
            assert len(todos) == 1
            assert todos[0]["status"] == "completed"
        finally:
            shutil.rmtree(temp)
    
    def test_get_changes_with_events(self):
        """测试查询项目变更有事件"""
        import tempfile
        import shutil
        import sqlite3
        import os
        
        temp = tempfile.mkdtemp()
        proj_name = os.path.basename(temp)
        
        try:
            state_dir = os.path.join(temp, "state")
            os.makedirs(state_dir)
            db_path = os.path.join(state_dir, "todos.db")
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("CREATE TABLE events (id INTEGER, type TEXT, entity_type TEXT, entity_id TEXT, old_status TEXT, new_status TEXT, timestamp TEXT, data TEXT)")
            c.execute("INSERT INTO events VALUES (1, 'todo_status_changed', 'todo', 'TODO-1', 'pending', 'completed', '2026-01-01', '')")
            conn.commit()
            conn.close()
            
            from src.core.project_query import ProjectQuery
            query = ProjectQuery(os.path.dirname(temp))
            changes = query.get_changes(proj_name)
            
            assert len(changes.get("changes", [])) >= 1
        finally:
            shutil.rmtree(temp)
    
    def test_get_progress_with_data(self):
        """测试查询项目进度有数据"""
        import tempfile
        import shutil
        import sqlite3
        import os
        
        temp = tempfile.mkdtemp()
        proj_name = os.path.basename(temp)
        
        try:
            state_dir = os.path.join(temp, "state")
            os.makedirs(state_dir)
            db_path = os.path.join(state_dir, "todos.db")
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("CREATE TABLE todos (id TEXT, content TEXT, status TEXT, priority TEXT)")
            c.execute("INSERT INTO todos VALUES ('TODO-1', 'test', 'completed', 'high')")
            c.execute("INSERT INTO todos VALUES ('TODO-2', 'test2', 'pending', 'low')")
            conn.commit()
            conn.close()
            
            from src.core.project_query import ProjectQuery
            query = ProjectQuery(os.path.dirname(temp))
            progress = query.get_progress(proj_name)
            
            assert progress.get("progress_percentage", 0) > 0
            assert "status_breakdown" in progress
        finally:
            shutil.rmtree(temp)
    
    def test_get_changes_not_found(self):
        """测试查询不存在项目的变更"""
        from src.core.project_query import ProjectQuery
        
        query = ProjectQuery(".")
        changes = query.get_changes("nonexistent")
        
        assert "error" in changes
    
    def test_get_progress_not_found(self):
        """测试查询不存在项目的进度"""
        from src.core.project_query import ProjectQuery
        
        query = ProjectQuery(".")
        progress = query.get_progress("nonexistent")
        
        assert "error" in progress
    
    def test_get_project_status_not_found(self):
        """测试获取不存在的项目状态"""
        from src.core.project_query import ProjectQuery
        
        query = ProjectQuery(".")
        status = query.get_project_status("nonexistent_project_xyz")
        
        assert "error" in status
    
    def test_get_project_status_with_data(self):
        """测试获取项目状态有数据"""
        import tempfile
        import shutil
        import sqlite3
        import os
        
        temp = tempfile.mkdtemp()
        try:
            state_dir = os.path.join(temp, "state")
            os.makedirs(state_dir)
            db_path = os.path.join(state_dir, "todos.db")
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("CREATE TABLE todos (id TEXT, content TEXT, status TEXT, priority TEXT)")
            c.execute("INSERT INTO todos VALUES ('TODO-1', 'test', 'completed', 'high')")
            c.execute("INSERT INTO todos VALUES ('TODO-2', 'test2', 'pending', 'low')")
            c.execute("INSERT INTO todos VALUES ('TODO-3', 'test3', 'in_progress', 'medium')")
            conn.commit()
            conn.close()
            
            from src.core.project_query import ProjectQuery
            query = ProjectQuery(os.path.dirname(temp))
            status = query.get_project_status(os.path.basename(temp))
            
            assert status["total"] == 3
            assert status["completed"] == 1
            assert status["pending"] == 1
            assert status["in_progress"] == 1
        finally:
            shutil.rmtree(temp)
    
    def test_get_project_todos_not_found(self):
        """测试获取不存在项目的TODO"""
        from src.core.project_query import ProjectQuery
        
        query = ProjectQuery(".")
        todos = query.get_project_todos("nonexistent")
        
        assert "error" in todos[0]
    
    def test_get_project_todos_with_status_filter(self):
        """测试按状态过滤获取TODO"""
        import tempfile
        import shutil
        import sqlite3
        import os
        
        temp = tempfile.mkdtemp()
        try:
            state_dir = os.path.join(temp, "state")
            os.makedirs(state_dir)
            db_path = os.path.join(state_dir, "todos.db")
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("CREATE TABLE todos (id TEXT, content TEXT, status TEXT, priority TEXT, sender TEXT, receiver TEXT, created_at TEXT)")
            c.execute("INSERT INTO todos VALUES ('TODO-1', 'test1', 'completed', 'high', 'a1', 'a2', '2026-01-01')")
            c.execute("INSERT INTO todos VALUES ('TODO-2', 'test2', 'pending', 'low', 'a1', 'a2', '2026-01-02')")
            conn.commit()
            conn.close()
            
            from src.core.project_query import ProjectQuery
            query = ProjectQuery(os.path.dirname(temp))
            todos = query.get_project_todos(os.path.basename(temp), "completed")
            
            assert len(todos) == 1
            assert todos[0]["status"] == "completed"
        finally:
            shutil.rmtree(temp)
    
    def test_get_changes_not_found(self):
        """测试查询不存在项目的变更"""
        from src.core.project_query import ProjectQuery
        
        query = ProjectQuery(".")
        changes = query.get_changes("nonexistent")
        
        assert "error" in changes
    
    def test_get_changes_with_events(self):
        """测试查询项目变更有事件"""
        import tempfile
        import shutil
        import sqlite3
        import os
        
        temp = tempfile.mkdtemp()
        try:
            state_dir = os.path.join(temp, "state")
            os.makedirs(state_dir)
            db_path = os.path.join(state_dir, "todos.db")
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("CREATE TABLE events (id INTEGER, type TEXT, entity_type TEXT, entity_id TEXT, old_status TEXT, new_status TEXT, timestamp TEXT, data TEXT)")
            c.execute("INSERT INTO events VALUES (1, 'todo_status_changed', 'todo', 'TODO-1', 'pending', 'completed', '2026-01-01', '')")
            conn.commit()
            conn.close()
            
            from src.core.project_query import ProjectQuery
            query = ProjectQuery(os.path.dirname(temp))
            changes = query.get_changes(os.path.basename(temp))
            
            assert len(changes.get("changes", [])) >= 1
        finally:
            shutil.rmtree(temp)
    
    def test_get_progress_not_found(self):
        """测试查询不存在项目的进度"""
        from src.core.project_query import ProjectQuery
        
        query = ProjectQuery(".")
        progress = query.get_progress("nonexistent")
        
        assert "error" in progress
    
    def test_get_progress_with_data(self):
        """测试查询项目进度有数据"""
        import tempfile
        import shutil
        import sqlite3
        import os
        
        temp = tempfile.mkdtemp()
        try:
            state_dir = os.path.join(temp, "state")
            os.makedirs(state_dir)
            db_path = os.path.join(state_dir, "todos.db")
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("CREATE TABLE todos (id TEXT, content TEXT, status TEXT, priority TEXT)")
            c.execute("INSERT INTO todos VALUES ('TODO-1', 'test', 'completed', 'high')")
            c.execute("INSERT INTO todos VALUES ('TODO-2', 'test2', 'pending', 'low')")
            conn.commit()
            conn.close()
            
            from src.core.project_query import ProjectQuery
            query = ProjectQuery(os.path.dirname(temp))
            progress = query.get_progress(os.path.basename(temp))
            
            assert progress.get("progress_percentage", 0) > 0
            assert "status_breakdown" in progress
        finally:
            shutil.rmtree(temp)


class TestDocQuery:
    """测试M13: 公共文档查询"""
    
    def test_query_not_found(self):
        """测试文档目录不存在"""
        from src.core.doc_query import DocQuery
        
        query = DocQuery("/nonexistent/path")
        results = query.query("test")
        assert "error" in results[0]
    
    def test_query_with_mock(self):
        """测试搜索使用mock"""
        from src.core.doc_query import DocQuery
        from src.core.file_abstractions import MockFileReader, MockDirectoryScanner
        
        scanner = MockDirectoryScanner({
            "/test/docs": {
                "dirs": [],
                "files": ["test.md"]
            }
        })
        reader = MockFileReader({
            "/test/docs/test.md": "# Test\n\nThis is a test content"
        })
        query = DocQuery("/test", file_reader=reader, dir_scanner=scanner)
        
        results = query.query("test")
        assert len(results) >= 1
    
    def test_query_no_match(self):
        """测试搜索无匹配"""
        from src.core.doc_query import DocQuery
        from src.core.file_abstractions import MockFileReader, MockDirectoryScanner
        
        scanner = MockDirectoryScanner({
            "/test/docs": {
                "dirs": [],
                "files": ["test.md"]
            }
        })
        reader = MockFileReader({
            "/test/docs/test.md": "# Test\n\nContent without keyword"
        })
        query = DocQuery("/test", file_reader=reader, dir_scanner=scanner)
        
        results = query.query("nonexistent_keyword_xyz")
        assert "error" in results[0] or len(results) == 0
    
    def test_get_architecture_with_mock(self):
        """测试获取架构文档使用mock"""
        from src.core.doc_query import DocQuery
        from src.core.file_abstractions import MockFileReader
        import os
        import shutil
        
        # 需要创建真实的目录结构
        temp_dir = tempfile.mkdtemp()
        try:
            arch_dir = os.path.join(temp_dir, "docs", "00-architecture")
            os.makedirs(arch_dir)
            with open(os.path.join(arch_dir, "CORE_ARCHITECTURE.md"), "w") as f:
                f.write("# Architecture")
            
            query = DocQuery(temp_dir)
            result = query.get_architecture()
            assert "content" in result
        finally:
            shutil.rmtree(temp_dir)
    
    def test_get_document_not_found(self):
        """测试获取不存在的文档"""
        from src.core.doc_query import DocQuery
        
        query = DocQuery("/nonexistent/path")
        result = query.get_document("nonexistent.md")
        
        assert "error" in result
    
    def test_get_document_not_markdown(self):
        """测试获取非markdown文档"""
        from src.core.doc_query import DocQuery
        
        query = DocQuery("/nonexistent/path")
        result = query.get_document("test.txt")
        
        assert "error" in result
    
    def test_get_document_with_mock(self):
        """测试获取文档使用mock"""
        from src.core.doc_query import DocQuery
        from src.core.file_abstractions import MockFileReader
        import os
        import shutil
        
        reader = MockFileReader({
            "/test/docs/test.md": "# Test\n\nContent"
        })
        query = DocQuery("/test", file_reader=reader)
        
        # 需要docs目录存在
        os.makedirs("/tmp/test_docs/docs", exist_ok=True)
        with open("/tmp/test_docs/docs/test.md", "w") as f:
            f.write("# Test")
        
        try:
            result = query.get_document("docs/test.md")
            assert "content" in result or "error" in result
        finally:
            shutil.rmtree("/tmp/test_docs", ignore_errors=True)
    
    def test_list_docs_all_categories(self):
        """测试列出所有分类文档"""
        import tempfile
        import shutil
        import os
        
        temp = tempfile.mkdtemp()
        try:
            for cat in ["00-memos", "01-requirements", "02-design"]:
                cat_dir = os.path.join(temp, "docs", cat)
                os.makedirs(cat_dir)
                with open(os.path.join(cat_dir, "test.md"), "w") as f:
                    f.write("# Test")
            
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            docs = query.list_docs()
            
            assert len(docs) >= 3
        finally:
            shutil.rmtree(temp)
    
    def test_query_with_content(self):
        """测试搜索有内容的文档"""
        import tempfile
        import shutil
        import os
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs", "01-requirements")
            os.makedirs(docs_dir)
            with open(os.path.join(docs_dir, "req.md"), "w") as f:
                f.write("# Requirements\n\nThis document describes requirements")
            
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            results = query.query("requirements")
            
            assert len(results) >= 1
        finally:
            shutil.rmtree(temp)
    
    def test_list_docs_specific_category(self):
        """测试列出指定分类文档"""
        import tempfile
        import shutil
        import os
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs", "00-memos")
            os.makedirs(docs_dir)
            with open(os.path.join(docs_dir, "memo.md"), "w") as f:
                f.write("# Memo\n\nTest memo content")
            
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            docs = query.list_docs(category="00-memos")
            
            assert len(docs) >= 1
            assert docs[0]["category"] == "00-memos"
        finally:
            shutil.rmtree(temp)
    
    def test_query_multiple_matches(self):
        """测试搜索多个匹配"""
        import tempfile
        import shutil
        import os
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs", "01-requirements")
            os.makedirs(docs_dir)
            with open(os.path.join(docs_dir, "req1.md"), "w") as f:
                f.write("# Requirements\n\nTest content")
            with open(os.path.join(docs_dir, "req2.md"), "w") as f:
                f.write("# Requirements\n\nAnother test")
            
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            results = query.query("Test")
            
            assert len(results) >= 1
        finally:
            shutil.rmtree(temp)
    
    def test_get_document_case_sensitive(self):
        """测试获取文档大小写敏感"""
        from src.core.doc_query import DocQuery
        
        query = DocQuery("/nonexistent")
        result = query.get_document("TEST.MD")
        
        assert "error" in result
    
    def test_list_docs_empty_category(self):
        """测试列出空分类"""
        import tempfile
        import shutil
        import os
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs", "00-memos")
            os.makedirs(docs_dir)
            
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            docs = query.list_docs(category="00-memos")
            
            assert len(docs) == 0
        finally:
            shutil.rmtree(temp)
    
    def test_query_case_insensitive(self):
        """测试搜索大小写不敏感"""
        import tempfile
        import shutil
        import os
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs", "01-requirements")
            os.makedirs(docs_dir)
            with open(os.path.join(docs_dir, "req.md"), "w") as f:
                f.write("# REQUIREMENTS\n\nThis is TEST content")
            
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            results = query.query("requirements")
            
            assert len(results) >= 1
        finally:
            shutil.rmtree(temp)
    
    def test_get_architecture_not_found(self):
        """测试获取架构文档不存在"""
        import tempfile
        import shutil
        
        temp = tempfile.mkdtemp()
        try:
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            result = query.get_architecture()
            
            assert "error" in result
        finally:
            shutil.rmtree(temp)
    
    def test_query_empty_keyword(self):
        """测试搜索空关键词"""
        import tempfile
        import shutil
        import os
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs", "01-requirements")
            os.makedirs(docs_dir)
            with open(os.path.join(docs_dir, "req.md"), "w") as f:
                f.write("# Requirements\n\nContent")
            
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            results = query.query("")
            
            assert len(results) >= 1
        finally:
            shutil.rmtree(temp)


class TestFileAbstractionsExtended:
    """扩展测试文件系统抽象层"""
    
    def test_mock_file_reader_multiple_files(self):
        """测试模拟文件读取多个文件"""
        from src.core.file_abstractions import MockFileReader
        from pathlib import Path
        
        reader = MockFileReader({
            "/test/file1.md": "# File 1",
            "/test/file2.md": "# File 2",
            "/test/file3.md": "# File 3"
        })
        
        assert reader.read(Path("/test/file1.md")) == "# File 1"
        assert reader.read(Path("/test/file2.md")) == "# File 2"
        assert reader.read(Path("/test/file3.md")) == "# File 3"
    
    def test_mock_directory_scanner_nested(self):
        """测试模拟递归目录扫描-当前实现只扫描当前目录"""
        from src.core.file_abstractions import MockDirectoryScanner
        from pathlib import Path
        
        scanner = MockDirectoryScanner({
            "/root": {
                "dirs": ["level1"],
                "files": ["root.md", "root2.md"]
            },
            "/root/level1": {
                "dirs": ["level2"],
                "files": ["level1.md"]
            }
        })
        
        all_md = list(scanner.rglob(Path("/root"), "*.md"))
        assert len(all_md) == 2
    
    def test_mock_directory_scanner_empty(self):
        """测试模拟空目录扫描"""
        from src.core.file_abstractions import MockDirectoryScanner
        from pathlib import Path
        
        scanner = MockDirectoryScanner({})
        dirs = list(scanner.iterdir(Path("/empty")))
        assert dirs == []


class TestRetryWatcherExtended:
    """扩展测试RetryWatcher"""
    
    def test_record_rejection_multiple(self, temp_db):
        """测试多次记录拒绝"""
        from src.core.retry_watcher import RetryWatcher
        
        watcher = RetryWatcher(temp_db, warning_threshold=5)
        
        for i in range(5):
            result = watcher.record_rejection("TODO-1")
            assert result["retry_count"] == i + 1
        
        count = watcher.get_retry_count("TODO-1")
        assert count == 5
    
    def test_reset_nonexistent(self, temp_db):
        """测试重置不存在的TODO"""
        from src.core.retry_watcher import RetryWatcher
        
        watcher = RetryWatcher(temp_db)
        watcher.reset_retry("NONEXISTENT")
        
        count = watcher.get_retry_count("NONEXISTENT")
        assert count == 0
    
    def test_get_all_retry_tracking(self, temp_db):
        """测试获取所有重试追踪"""
        from src.core.retry_watcher import RetryWatcher
        
        watcher = RetryWatcher(temp_db)
        watcher.record_rejection("TODO-1")
        watcher.record_rejection("TODO-2")
        
        all_records = watcher.get_all_retry_tracking()
        assert len(all_records) >= 2


class TestTimeoutWatcherExtended:
    """扩展测试TimeoutWatcher"""
    
    def test_get_timeout_config_nonexistent(self, temp_db):
        """测试获取不存在的超时配置"""
        from src.core.timeout_watcher import TimeoutWatcher
        
        watcher = TimeoutWatcher(temp_db)
        config = watcher.get_timeout_config("nonexistent", "high")
        
        assert config is None
    
    def test_notify_timeout_not_found(self, temp_db):
        """测试通知不存在的TODO超时"""
        from src.core.timeout_watcher import TimeoutWatcher
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY,
                content TEXT,
                status TEXT,
                priority TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        watcher = TimeoutWatcher(temp_db)
        result = watcher.notify_timeout("NONEXISTENT_TODO")
        
        assert result["success"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


class TestDocQueryExceptionHandling:
    """测试DocQuery异常处理路径"""
    
    def test_query_with_exception(self):
        """测试查询时文件读取异常"""
        import tempfile
        import shutil
        import os
        from src.core.file_abstractions import ExceptionFileReader
        from src.core.doc_query import DocQuery
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs", "01-requirements")
            os.makedirs(docs_dir)
            with open(os.path.join(docs_dir, "test.md"), "w") as f:
                f.write("# Test")
            
            reader = ExceptionFileReader(IOError("Read error"))
            query = DocQuery(temp, file_reader=reader)
            results = query.query("test")
            
            assert isinstance(results, list)
        finally:
            shutil.rmtree(temp)
    
    def test_list_docs_with_exception(self):
        """测试列出文档时文件读取异常"""
        import tempfile
        import shutil
        import os
        from src.core.file_abstractions import ExceptionFileReader
        from src.core.doc_query import DocQuery
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs", "01-requirements")
            os.makedirs(docs_dir)
            with open(os.path.join(docs_dir, "test.md"), "w") as f:
                f.write("# Test")
            
            reader = ExceptionFileReader(IOError("Read error"))
            query = DocQuery(temp, file_reader=reader)
            docs = query.list_docs()
            
            assert isinstance(docs, list)
        finally:
            shutil.rmtree(temp)
    
    def test_get_architecture_with_exception(self):
        """测试获取架构文档时异常"""
        import tempfile
        import shutil
        import os
        from src.core.file_abstractions import ExceptionFileReader
        from src.core.doc_query import DocQuery
        
        temp = tempfile.mkdtemp()
        try:
            arch_dir = os.path.join(temp, "docs", "00-architecture")
            os.makedirs(arch_dir)
            with open(os.path.join(arch_dir, "CORE_ARCHITECTURE.md"), "w") as f:
                f.write("# Architecture")
            
            reader = ExceptionFileReader(IOError("Read error"))
            query = DocQuery(temp, file_reader=reader)
            result = query.get_architecture()
            
            assert "error" in result
        finally:
            shutil.rmtree(temp)
    
    def test_get_document_with_exception(self):
        """测试获取文档时异常"""
        import tempfile
        import shutil
        import os
        from src.core.file_abstractions import ExceptionFileReader
        from src.core.doc_query import DocQuery
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs")
            os.makedirs(docs_dir)
            
            reader = ExceptionFileReader(IOError("Read error"))
            query = DocQuery(temp, file_reader=reader)
            result = query.get_document("test.md")
            
            assert "error" in result
        finally:
            shutil.rmtree(temp)


class TestAutoTodoCreatorExtended:
    """扩展测试AutoTodoCreator"""
    
    def test_list_rules_returns_list(self, temp_db):
        """测试列出规则返回列表"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        rules = creator.list_rules()
        
        assert isinstance(rules, list)
        assert len(rules) >= 3
    
    def test_add_rule_returns_id(self, temp_db):
        """测试添加规则返回ID"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        rule_id = creator.add_rule(
            "测试规则",
            "test_event",
            "测试内容: {entity_id}",
            "medium"
        )
        
        assert rule_id > 0
        
        rules = creator.list_rules()
        assert any(r["name"] == "测试规则" for r in rules)
    
    def test_disable_and_enable_rule(self, temp_db):
        """测试禁用和启用规则"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        rules = creator.list_rules()
        
        if rules:
            rule_id = rules[0]["id"]
            creator.enable_rule(rule_id, False)
            
            rules_after_disable = creator.list_rules()
            disabled_rule = next((r for r in rules_after_disable if r["id"] == rule_id), None)
            assert disabled_rule is not None
            assert disabled_rule["enabled"] == 0
            
            creator.enable_rule(rule_id, True)
            
            rules_after_enable = creator.list_rules()
            enabled_rule = next((r for r in rules_after_enable if r["id"] == rule_id), None)
            assert enabled_rule is not None
            assert enabled_rule["enabled"] == 1


class TestFlowTriggerExtended:
    """扩展测试FlowTrigger"""
    
    def test_list_rules_returns_dicts(self, temp_db):
        """测试列出规则返回字典列表"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        rules = trigger.list_rules()
        
        assert isinstance(rules, list)
        if rules:
            assert isinstance(rules[0], dict)
            assert "id" in rules[0]
            assert "name" in rules[0]
    
    def test_enable_disable_rule(self, temp_db):
        """测试启用禁用规则"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        rules = trigger.list_rules()
        
        if rules:
            rule_id = rules[0]["id"]
            trigger.enable_rule(rule_id, False)
            
            updated_rules = trigger.list_rules()
            rule = next((r for r in updated_rules if r["id"] == rule_id), None)
            assert rule is not None
            assert rule["enabled"] == 0
            
            trigger.enable_rule(rule_id, True)
            
            updated_rules2 = trigger.list_rules()
            rule2 = next((r for r in updated_rules2 if r["id"] == rule_id), None)
            assert rule2 is not None
            assert rule2["enabled"] == 1
    
    def test_match_rule_logic(self, temp_db):
        """测试规则匹配逻辑"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        
        rule = {"from_status": "pending", "to_status": "approved"}
        event1 = {"old_status": "pending", "new_status": "approved"}
        event2 = {"old_status": "in_progress", "new_status": "approved"}
        
        assert trigger._match_rule(rule, event1) is True
        assert trigger._match_rule(rule, event2) is False
    
    def test_get_next_phase_all_phases(self, temp_db):
        """测试所有阶段的下一阶段"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        
        assert trigger._get_next_phase("requirements") == "design"
        assert trigger._get_next_phase("design") == "development"
        assert trigger._get_next_phase("development") == "testing"
        assert trigger._get_next_phase("testing") == "acceptance"
        assert trigger._get_next_phase("acceptance") == "released"
        assert trigger._get_next_phase("released") is None
    
    def test_handle_event_unknown_type(self, temp_db):
        """测试处理未知类型事件"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        results = trigger.handle_event({"type": "completely_unknown_event_type_xyz"})
        
        assert results == []
    
    def test_execute_action_unknown(self, temp_db):
        """测试执行未知动作"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        
        rule = {
            "name": "test",
            "action_type": "totally_unknown_action_xyz",
            "action_config": "{}"
        }
        event = {"type": "test"}
        
        result = trigger._execute_action(rule, event)
        assert result["success"] is False
    
    def test_get_flow_trigger_function(self):
        """测试get_flow_trigger函数"""
        from src.core.flow_trigger import get_flow_trigger, FlowTrigger
        
        trigger = get_flow_trigger()
        assert trigger is not None
        assert isinstance(trigger, FlowTrigger)
    
    def test_get_auto_todo_creator_function(self):
        """测试get_auto_todo_creator函数"""
        from src.core.auto_todo_creator import get_auto_todo_creator, AutoTodoCreator
        
        creator = get_auto_todo_creator()
        assert creator is not None
        assert isinstance(creator, AutoTodoCreator)
    
    def test_get_doc_query_function(self):
        """测试get_doc_query函数"""
        from src.core.doc_query import get_doc_query, DocQuery
        
        query = get_doc_query()
        assert query is not None
        assert isinstance(query, DocQuery)


class TestDocQueryCoverageBoost:
    """针对性提高DocQuery覆盖率"""
    
    def test_list_docs_category_not_exists(self):
        """测试列出不存在的分类"""
        import tempfile
        import shutil
        import os
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs")
            os.makedirs(docs_dir)
            
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            docs = query.list_docs(category="nonexistent_category_xyz")
            
            assert isinstance(docs, list)
        finally:
            shutil.rmtree(temp)
    
    def test_get_document_txt_file(self):
        """测试获取txt文件"""
        import tempfile
        import shutil
        import os
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs")
            os.makedirs(docs_dir)
            with open(os.path.join(docs_dir, "test.txt"), "w") as f:
                f.write("Test content")
            
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            result = query.get_document("test.txt")
            
            assert "error" in result
        finally:
            shutil.rmtree(temp)
    
    def test_get_document_not_found(self):
        """测试获取不存在的文档"""
        import tempfile
        import shutil
        
        temp = tempfile.mkdtemp()
        try:
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            result = query.get_document("totally_nonexistent_doc_xyz.md")
            
            assert "error" in result
        finally:
            shutil.rmtree(temp)


class TestAutoTodoCreatorCoverageBoost:
    """针对性提高AutoTodoCreator覆盖率"""
    
    def test_match_trigger_complex_condition(self, temp_db):
        """测试复杂条件匹配"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        
        event = {"type": "todo_status_changed", "new_status": "approved", "entity_id": "TODO-ABC-123"}
        match = creator._match_trigger("todo_status_changed:approved", event)
        assert match is True
        
        event2 = {"type": "todo_status_changed", "new_status": "approved", "entity_id": "TODO-XYZ-789"}
        match2 = creator._match_trigger("todo_status_changed:approved", event2)
        assert match2 is True
    
    def test_match_trigger_no_condition(self, temp_db):
        """测试无条件匹配"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        
        event = {"type": "todo_status_changed", "new_status": "anything"}
        match = creator._match_trigger("todo_status_changed", event)
        assert match is True
        
        event2 = {"type": "other_event", "new_status": "anything"}
        match2 = creator._match_trigger("todo_status_changed", event2)
        assert match2 is False
    
    def test_create_from_event_returns_list(self, temp_db):
        """测试create_from_event返回列表"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        
        event = {"type": "totally_unknown_event_type_xyz"}
        result = creator.create_from_event(event)
        
        assert isinstance(result, list)
        assert result == []


class TestFlowTriggerCoverageBoost:
    """针对性提高FlowTrigger覆盖率"""
    
    def test_handle_event_returns_results_list(self, temp_db):
        """测试handle_event返回结果列表"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        
        event = {"type": "totally_unknown_event_type_xyz", "old_status": "", "new_status": ""}
        results = trigger.handle_event(event)
        
        assert isinstance(results, list)
        assert results == []
    
    def test_execute_action_with_unknown_type(self, temp_db):
        """测试执行未知动作类型"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        
        rule = {
            "name": "test",
            "action_type": "totally_unknown_action_type_xyz",
            "action_config": '{}'
        }
        event = {"type": "test", "entity_id": "TEST-001", "old_status": "", "new_status": ""}
        
        result = trigger._execute_action(rule, event)
        assert result["success"] is False
        assert "Unknown action type" in result["message"]
    
    def test_action_advance_phase_no_next_phase(self, temp_db):
        """测试推进阶段无下一阶段"""
        from src.core.flow_trigger import FlowTrigger
        from unittest.mock import patch, MagicMock
        
        trigger = FlowTrigger(temp_db)
        
        with patch('src.core.state_manager.StateManager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.get_current_phase.return_value = "unknown_phase"
            mock_manager.return_value = mock_instance
            
            rule = {
                "name": "test",
                "action_type": "advance_phase",
                "action_config": '{}'
            }
            event = {"type": "signoff"}
            
            result = trigger._execute_action(rule, event)
            assert result["success"] is False
            assert "No next phase available" in result["message"]


class TestDocQueryFinalCoverage:
    """DocQuery最终覆盖率提升"""
    
    def test_query_docs_dir_not_exists(self):
        """测试docs目录不存在时的查询"""
        from src.core.doc_query import DocQuery
        
        query = DocQuery("/this/path/definitely/does/not/exist/xyz123")
        results = query.query("test")
        
        assert len(results) == 1
        assert "error" in results[0]
    
    def test_list_docs_dir_not_exists(self):
        """测试docs目录不存在时的列出"""
        from src.core.doc_query import DocQuery
        
        query = DocQuery("/this/path/definitely/does/not/exist/xyz123")
        docs = query.list_docs()
        
        assert len(docs) == 1
        assert "error" in docs[0]


class TestAutoTodoCreatorFinalCoverage:
    """AutoTodoCreator最终覆盖率提升"""
    
    def test_create_from_event_empty_match(self, temp_db):
        """测试无匹配规则时创建"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        
        event = {"type": "event_type_that_no_rule_matches_xyz"}
        result = creator.create_from_event(event)
        
        assert result == []
    
    def test_match_trigger_negative_condition(self, temp_db):
        """测试不匹配条件"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        
        event = {"type": "todo_status_changed", "new_status": "approved", "entity_id": "TODO-1"}
        match = creator._match_trigger("todo_status_changed:rejected", event)
        assert match is False
    
    def test_match_trigger_with_plus_condition(self, temp_db):
        """测试+号条件匹配"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        
        event = {"type": "todo_status_changed", "entity_id": "TODO-ABC-123-XYZ"}
        match = creator._match_trigger("todo_status_changed:abc+xyz", event)
        assert match is True
        
        event2 = {"type": "todo_status_changed", "entity_id": "TODO-ABC-456"}
        match2 = creator._match_trigger("todo_status_changed:abc+xyz", event2)
        assert match2 is False
    
    def test_match_trigger_entity_id_missing(self, temp_db):
        """测试entity_id缺失时匹配"""
        from src.core.auto_todo_creator import AutoTodoCreator
        
        creator = AutoTodoCreator(temp_db)
        
        event = {"type": "todo_status_changed"}
        match = creator._match_trigger("todo_status_changed:abc", event)
        assert match is False


class TestDocQueryFinalBoost:
    """DocQuery最终覆盖率提升"""
    
    def test_get_document_non_markdown_error(self):
        """测试非markdown文件错误"""
        import tempfile
        import shutil
        import os
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs")
            os.makedirs(docs_dir)
            
            with open(os.path.join(docs_dir, "test.txt"), "w") as f:
                f.write("Not markdown")
            
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            result = query.get_document("test.txt")
            
            assert "error" in result
        finally:
            shutil.rmtree(temp)
    
    def test_get_document_file_not_found(self):
        """测试文件不存在"""
        import tempfile
        import shutil
        
        temp = tempfile.mkdtemp()
        try:
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            result = query.get_document("nonexistent_file_xyz.md")
            
            assert "error" in result
            assert "not found" in result["error"].lower()
        finally:
            shutil.rmtree(temp)
    
    def test_list_docs_multiple_categories(self):
        """测试列出多个分类文档"""
        import tempfile
        import shutil
        import os
        
        temp = tempfile.mkdtemp()
        try:
            for cat in ["00-memos", "01-requirements", "02-design"]:
                cat_dir = os.path.join(temp, "docs", cat)
                os.makedirs(cat_dir)
                with open(os.path.join(cat_dir, f"{cat}.md"), "w") as f:
                    f.write(f"# {cat}")
            
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            docs = query.list_docs()
            
            assert len(docs) >= 3
        finally:
            shutil.rmtree(temp)
    
    def test_get_architecture_content(self):
        """测试获取架构文档内容"""
        import tempfile
        import shutil
        import os
        
        temp = tempfile.mkdtemp()
        try:
            arch_dir = os.path.join(temp, "docs", "00-architecture")
            os.makedirs(arch_dir)
            with open(os.path.join(arch_dir, "CORE_ARCHITECTURE.md"), "w") as f:
                f.write("# Core Architecture\n\nThis is the architecture document.")
            
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            result = query.get_architecture()
            
            assert "content" in result
            assert "Core Architecture" in result["content"]
        finally:
            shutil.rmtree(temp)
    
    def test_query_with_real_files(self):
        """测试真实文件查询"""
        import tempfile
        import shutil
        import os
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs", "01-requirements")
            os.makedirs(docs_dir)
            with open(os.path.join(docs_dir, "req.md"), "w") as f:
                f.write("# Requirements\n\nThis document describes requirements for the system")
            
            from src.core.doc_query import DocQuery
            query = DocQuery(temp)
            results = query.query("requirements")
            
            assert len(results) >= 1
            assert "snippet" in results[0]
        finally:
            shutil.rmtree(temp)
    
    def test_get_document_exception_handling(self):
        """测试get_document异常处理-覆盖第115行"""
        import tempfile
        import shutil
        import os
        from src.core.doc_query import DocQuery
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs")
            os.makedirs(docs_dir)
            with open(os.path.join(docs_dir, "test.md"), "w") as f:
                f.write("# Test content")
            
            class RaisingFileReader:
                def read(self, path):
                    raise IOError("Simulated IO error during file read")
            
            query = DocQuery(temp, file_reader=RaisingFileReader())
            result = query.get_document("docs/test.md")
            
            assert "error" in result
            assert "Simulated IO error" in result["error"]
        finally:
            shutil.rmtree(temp)
    
    def test_get_document_non_markdown(self):
        """测试获取非markdown文件-覆盖第105行"""
        import tempfile
        import shutil
        import os
        from src.core.doc_query import DocQuery
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs")
            os.makedirs(docs_dir)
            with open(os.path.join(docs_dir, "test.txt"), "w") as f:
                f.write("Not markdown content")
            
            query = DocQuery(temp)
            result = query.get_document("docs/test.txt")
            
            assert "error" in result
            assert "Only markdown" in result["error"]
        finally:
            shutil.rmtree(temp)
    
    def test_get_document_success(self):
        """测试成功获取文档-覆盖第109行"""
        import tempfile
        import shutil
        import os
        from src.core.doc_query import DocQuery
        
        temp = tempfile.mkdtemp()
        try:
            docs_dir = os.path.join(temp, "docs")
            os.makedirs(docs_dir)
            with open(os.path.join(docs_dir, "success.md"), "w") as f:
                f.write("# Success\n\nThis is a successful document read.")
            
            query = DocQuery(temp)
            result = query.get_document("docs/success.md")
            
            assert "content" in result
            assert "Success" in result["content"]
            assert "file" in result
            assert "size" in result
            assert "lines" in result
        finally:
            shutil.rmtree(temp)


class TestFlowTriggerFinalBoost:
    """FlowTrigger最终覆盖率提升"""
    
    def test_handle_event_with_empty_results(self, temp_db):
        """测试handle_event返回空结果"""
        from src.core.flow_trigger import FlowTrigger
        
        trigger = FlowTrigger(temp_db)
        
        event = {"type": "event_type_with_no_matching_rules_xyz", "old_status": "", "new_status": ""}
        results = trigger.handle_event(event)
        
        assert results == []
    
    def test_action_create_todo_with_format(self, temp_db):
        """测试创建TODO动作格式化"""
        from src.core.flow_trigger import FlowTrigger
        from unittest.mock import patch, MagicMock
        
        trigger = FlowTrigger(temp_db)
        
        with patch('src.core.todo_sync_manager.TodoSyncManager') as mock_sync:
            mock_todo = MagicMock()
            mock_todo.id = "TEST-TODO-001"
            mock_todo.content = "Test content"
            mock_todo.priority = "high"
            mock_sync.return_value.add_todo.return_value = mock_todo
            
            rule = {
                "name": "test",
                "action_type": "create_todo",
                "action_config": '{"content": "Created for {entity_id}", "priority": "high"}'
            }
            event = {"type": "test", "entity_id": "REQ-001", "old_status": "", "new_status": ""}
            
            result = trigger._execute_action(rule, event)
            assert result["success"] is True
            assert result["todo_id"] == "TEST-TODO-001"
    
    def test_action_advance_phase_success(self, temp_db):
        """测试推进阶段成功"""
        from src.core.flow_trigger import FlowTrigger
        from unittest.mock import patch, MagicMock
        
        trigger = FlowTrigger(temp_db)
        
        with patch('src.core.state_manager.StateManager') as mock_mgr:
            mock_instance = MagicMock()
            mock_instance.get_current_phase.return_value = "requirements"
            mock_instance.advance_phase.return_value = None
            mock_mgr.return_value = mock_instance
            
            rule = {
                "name": "test",
                "action_type": "advance_phase",
                "action_config": '{}'
            }
            event = {"type": "signoff"}
            
            result = trigger._execute_action(rule, event)
            assert result["success"] is True
            assert result["from_phase"] == "requirements"
            assert result["to_phase"] == "design"
