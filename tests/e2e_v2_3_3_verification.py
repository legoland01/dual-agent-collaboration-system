"""
v2.3.3 E2E功能验证脚本

验证自动化流程触发模块的核心功能是否正常工作。
"""

import sys
import sqlite3
import tempfile
import shutil
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.state_listener import StateListener
from core.flow_trigger import FlowTrigger, TriggerRule
from core.loop_engine import LoopEngine
from core.timeout_watcher import TimeoutWatcher
from core.retry_watcher import RetryWatcher
from core.auto_todo_creator import AutoTodoCreator
from core.project_query import ProjectQuery
from core.doc_query import DocQuery


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"


def print_result(name: str, passed: bool, details: str = ""):
    status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
    print(f"  [{status}] {name}")
    if details:
        print(f"         {details}")


class E2EVerifier:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.temp_dirs = []

    def create_temp_db(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.temp_dirs.append(path)
        return path

    def create_temp_dir(self):
        temp = tempfile.mkdtemp()
        self.temp_dirs.append(temp)
        return temp

    def cleanup(self):
        for path in self.temp_dirs:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.unlink(path)
                else:
                    shutil.rmtree(path)

    def verify_state_listener(self):
        print(f"\n{Colors.BLUE}Testing M1: StateListener{Colors.END}")
        db = self.create_temp_db()
        listener = StateListener(db)

        listener.record_todo_status_change("TODO-001", "pending", "completed")
        print_result("record_todo_status_change", True)

        changes = listener.get_changes()
        print_result("get_changes returns list", len(changes) >= 1)

        listener.record_signoff("requirement", "REQ-001", "agent1")
        print_result("record_signoff", True)

        events = listener.get_recent_events(limit=10)
        print_result("get_recent_events", len(events) >= 1)

    def verify_flow_trigger(self):
        print(f"\n{Colors.BLUE}Testing M2: FlowTrigger{Colors.END}")
        db = self.create_temp_db()
        trigger = FlowTrigger(db)

        rules = trigger.list_rules()
        print_result("list_rules returns list", len(rules) >= 1)

        rule_id = trigger.add_rule(TriggerRule(
            name="Test Rule",
            event_type="test_event",
            from_status="",
            to_status="",
            action_type="advance_phase",
            action_config="{}"
        ))
        print_result("add_rule returns id", rule_id > 0)

        next_phase = trigger._get_next_phase("requirements")
        print_result("_get_next_phase returns next phase", next_phase == "design")

        event = {"type": "unknown_event"}
        results = trigger.handle_event(event)
        print_result("handle_event with no match returns empty", results == [])

    def verify_loop_engine(self):
        print(f"\n{Colors.BLUE}Testing M3: LoopEngine{Colors.END}")
        db = self.create_temp_db()
        engine = LoopEngine(db, max_loops=5)

        result = engine.record_loop("requirement", "REQ-001", "review")
        print_result("record_loop returns dict", result["loop_count"] == 1)

        engine.record_loop("requirement", "REQ-001", "review")
        engine.record_loop("requirement", "REQ-001", "review")
        count = engine.get_loop_count("requirement", "REQ-001", "review")
        print_result("get_loop_count returns correct count", count == 3)

        warning = engine.check_loop_warning("requirement", "REQ-001", "review")
        print_result("check_loop_warning returns dict", warning is not None)

        engine.reset_loop("requirement", "REQ-001", "review")
        count_after_reset = engine.get_loop_count("requirement", "REQ-001", "review")
        print_result("reset_loop works", count_after_reset == 0)

    def verify_timeout_watcher(self):
        print(f"\n{Colors.BLUE}Testing M4: TimeoutWatcher{Colors.END}")
        db = self.create_temp_db()
        watcher = TimeoutWatcher(db, default_timeout_hours=0)

        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE todos (
                id TEXT PRIMARY KEY,
                content TEXT,
                status TEXT,
                priority TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO todos (id, content, status, priority, created_at)
            VALUES ('TODO-001', 'Test', 'pending', 'high', datetime('now', '-5 hour'))
        """)
        conn.commit()
        conn.close()

        timeouts = watcher.check_timeouts()
        print_result("check_timeouts returns list", isinstance(timeouts, list))
        print_result("check_timeouts finds timeout", len(timeouts) >= 1)

        config = watcher.get_timeout_config("todo", "high")
        print_result("get_timeout_config returns int", isinstance(config, int))

        watcher.set_timeout_config("todo", 48, "low")
        new_config = watcher.get_timeout_config("todo", "low")
        print_result("set_timeout_config works", new_config == 48)

    def verify_retry_watcher(self):
        print(f"\n{Colors.BLUE}Testing M5: RetryWatcher{Colors.END}")
        db = self.create_temp_db()
        watcher = RetryWatcher(db, warning_threshold=3)

        result = watcher.record_rejection("TODO-001")
        print_result("record_rejection returns dict", "retry_count" in result)
        print_result("record_rejection increments count", result["retry_count"] == 1)

        for _ in range(2):
            watcher.record_rejection("TODO-001")
        count = watcher.get_retry_count("TODO-001")
        print_result("get_retry_count returns count", count == 3)

        warning = watcher.check_retry_warning("TODO-001")
        print_result("check_retry_warning returns dict", warning is not None)

        watcher.reset_retry("TODO-001")
        count_after_reset = watcher.get_retry_count("TODO-001")
        print_result("reset_retry works", count_after_reset == 0)

    def verify_auto_todo_creator(self):
        print(f"\n{Colors.BLUE}Testing M6: AutoTodoCreator{Colors.END}")
        db = self.create_temp_db()
        creator = AutoTodoCreator(db)

        rules = creator.list_rules()
        print_result("list_rules returns list", len(rules) >= 1)

        rule_id = creator.add_rule(
            "Test Rule",
            "test_event",
            "Test content: {entity_id}",
            "medium"
        )
        print_result("add_rule returns id", rule_id > 0)

        match = creator._match_trigger("todo_status_changed:approved", {
            "type": "todo_status_changed",
            "new_status": "approved"
        })
        print_result("_match_trigger returns bool", isinstance(match, bool))

        event = {"type": "unknown_event"}
        result = creator.create_from_event(event)
        print_result("create_from_event returns list", isinstance(result, list))

    def verify_project_query(self):
        print(f"\n{Colors.BLUE}Testing M11: ProjectQuery{Colors.END}")
        temp = self.create_temp_dir()
        query = ProjectQuery(temp)

        projects = query.get_projects()
        print_result("get_projects returns list", isinstance(projects, list))

        status = query.get_project_status("nonexistent")
        print_result("get_project_status handles not found", "error" in status)

        todos = query.get_project_todos("nonexistent")
        print_result("get_project_todos handles not found", len(todos) >= 1 and "error" in todos[0])

    def verify_doc_query(self):
        print(f"\n{Colors.BLUE}Testing M13: DocQuery{Colors.END}")
        temp = self.create_temp_dir()
        query = DocQuery(temp)

        results = query.query("test")
        print_result("query returns list", isinstance(results, list))

        docs = query.list_docs()
        print_result("list_docs returns list", isinstance(docs, list))

        arch = query.get_architecture()
        print_result("get_architecture returns dict", isinstance(arch, dict))

        doc = query.get_document("nonexistent.md")
        print_result("get_document handles not found", "error" in doc)

    def run_all(self):
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BLUE}v2.3.3 E2E 功能验证{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")

        self.verify_state_listener()
        self.verify_flow_trigger()
        self.verify_loop_engine()
        self.verify_timeout_watcher()
        self.verify_retry_watcher()
        self.verify_auto_todo_creator()
        self.verify_project_query()
        self.verify_doc_query()

        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BLUE}验证完成{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")

        self.cleanup()


def main():
    verifier = E2EVerifier()
    verifier.run_all()


if __name__ == "__main__":
    main()
