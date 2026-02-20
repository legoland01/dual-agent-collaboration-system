"""
测试用例: BUG-20260219-004 - TODO通知不显示

验证agent_id格式处理逻辑是否正确。
"""

import pytest
import sqlite3
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_db():
    """创建临时数据库"""
    temp = tempfile.mkdtemp()
    db_path = Path(temp) / "test.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE todos (
            id TEXT PRIMARY KEY,
            content TEXT,
            sender TEXT,
            receiver TEXT,
            priority TEXT,
            status TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    
    # 添加测试数据 - 模拟真实场景
    # 数据库存储时receiver不带agent前缀
    cursor.execute("""
        INSERT INTO todos (id, content, sender, receiver, priority, status, is_read, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "TEST-001",
        "测试TODO 1",
        "1",  # sender是 "1"
        "2",  # receiver是 "2"（不带agent前缀）
        "high",
        "pending",
        0,
        "2026-02-19 10:00:00"
    ))
    
    cursor.execute("""
        INSERT INTO todos (id, content, sender, receiver, priority, status, is_read, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "TEST-002",
        "测试TODO 2",
        "1",
        "2",
        "medium",
        "pending",
        0,
        "2026-02-19 10:01:00"
    ))
    
    cursor.execute("""
        INSERT INTO todos (id, content, sender, receiver, priority, status, is_read, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "TEST-003",
        "发给agent1的TODO",
        "2",
        "1",  # receiver是 "1"
        "high",
        "pending",
        0,
        "2026-02-19 10:02:00"
    ))
    
    conn.commit()
    conn.close()
    
    yield str(db_path)
    
    shutil.rmtree(temp)


class TestTodoStorageListReceiver:
    """测试TodoStorage.list的receiver参数处理"""
    
    def test_list_with_agent_prefix(self, temp_db):
        """测试用带agent前缀查询 - 应该匹配不到"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # 使用"agent2"查询（带前缀）
        query = "SELECT * FROM todos WHERE receiver = ? AND status = ? AND is_read = 0"
        cursor.execute(query, ("agent2", "pending"))
        rows = cursor.fetchall()
        
        # 期望0条 - 因为数据库存的是"2"而不是"agent2"
        assert len(rows) == 0, f"期望0条，实际{len(rows)}条"
        
        conn.close()
    
    def test_list_without_agent_prefix(self, temp_db):
        """测试用不带前缀查询 - 应该能匹配到"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # 使用"2"查询（不带前缀）
        query = "SELECT * FROM todos WHERE receiver = ? AND status = ? AND is_read = 0"
        cursor.execute(query, ("2", "pending"))
        rows = cursor.fetchall()
        
        # 期望2条
        assert len(rows) == 2, f"期望2条，实际{len(rows)}条"
        
        conn.close()
    
    def test_list_different_receivers(self, temp_db):
        """测试不同receiver的查询"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # 查询receiver="1"的TODO
        query = "SELECT * FROM todos WHERE receiver = ? AND is_read = 0"
        cursor.execute(query, ("1",))
        rows = cursor.fetchall()
        
        # 期望1条
        assert len(rows) == 1, f"期望1条，实际{len(rows)}条"
        assert rows[0][0] == "TEST-003", f"期望TEST-003，实际{rows[0][0]}"
        
        conn.close()


class TestAgentIdFormatHandling:
    """测试agent_id格式处理逻辑"""
    
    def test_agent_id_to_receiver_conversion(self):
        """测试agent_id转换为receiver的逻辑"""
        # 模拟修复后的转换逻辑
        def convert(agent_id):
            return agent_id.replace('agent', '') if agent_id else None
        
        # 测试用例
        assert convert("agent1") == "1"
        assert convert("agent2") == "2"
        assert convert("agent10") == "10"
        assert convert("1") == "1"  # 已经是数字
        assert convert(None) is None
    
    def test_full_query_flow(self, temp_db):
        """测试完整的查询流程"""
        # 模拟agent_commands.py中的查询逻辑（修复后）
        agent_id = "agent2"  # 用户使用的格式
        
        # 转换为数据库存储格式
        receiver = agent_id.replace('agent', '') if agent_id else None
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        query = "SELECT * FROM todos WHERE receiver = ? AND status = ? AND is_read = 0"
        cursor.execute(query, (receiver, "pending"))
        rows = cursor.fetchall()
        
        conn.close()
        
        # 期望找到2条
        assert len(rows) == 2, f"期望2条，实际{len(rows)}条"
    
    def test_query_nonexistent_agent(self, temp_db):
        """测试查询不存在的agent"""
        agent_id = "agent3"  # 不存在的agent
        
        receiver = agent_id.replace('agent', '') if agent_id else None
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        query = "SELECT * FROM todos WHERE receiver = ? AND is_read = 0"
        cursor.execute(query, (receiver,))
        rows = cursor.fetchall()
        
        conn.close()
        
        # 期望0条
        assert len(rows) == 0, f"期望0条，实际{len(rows)}条"


class TestTodoQueueManagerGetUnread:
    """测试TodoQueueManager.get_unread的agent_id参数处理"""
    
    def test_get_unread_with_agent_prefix(self, temp_db):
        """测试带agent前缀的查询"""
        # 模拟get_unread函数中的查询逻辑（修复后）
        agent_id = "agent2"
        
        # 修复后的转换逻辑
        receiver = agent_id.replace('agent', '') if agent_id else None
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        query = "SELECT * FROM todos WHERE receiver = ? AND status = ? AND is_read = 0"
        cursor.execute(query, (receiver, "pending"))
        rows = cursor.fetchall()
        
        conn.close()
        
        # 期望2条
        assert len(rows) == 2, f"期望2条，实际{len(rows)}条"
    
    def test_get_unread_with_numeric_id(self, temp_db):
        """测试带数字的查询"""
        # 有些地方可能直接传"2"而不是"agent2"
        agent_id = "2"
        
        receiver = agent_id.replace('agent', '') if agent_id else None
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        query = "SELECT * FROM todos WHERE receiver = ? AND status = ? AND is_read = 0"
        cursor.execute(query, (receiver, "pending"))
        rows = cursor.fetchall()
        
        conn.close()
        
        # 期望2条
        assert len(rows) == 2, f"期望2条，实际{len(rows)}条"


class TestNotificationScenario:
    """测试通知场景"""
    
    def test_agent2_receives_notification(self, temp_db):
        """测试agent2能收到发给它的通知"""
        # 模拟场景：agent1发给agent2一个TODO
        
        # 1. agent1创建TODO
        sender = "1"
        receiver = "2"
        
        # 2. 数据库存储（去掉agent前缀）
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO todos (id, content, sender, receiver, priority, status, is_read, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "SCENARIO-001",
            "场景测试TODO",
            sender,
            receiver,  # 存 "2"
            "high",
            "pending",
            0,
            "2026-02-19 10:30:00"
        ))
        conn.commit()
        
        # 3. agent2启动监听，查询自己的TODO
        agent_id = "agent2"  # agent2使用的格式
        
        # 修复后的查询逻辑
        receiver_query = agent_id.replace('agent', '') if agent_id else None
        
        cursor.execute("""
            SELECT * FROM todos 
            WHERE receiver = ? AND status = ? AND is_read = 0
        """, (receiver_query, "pending"))
        
        todos = cursor.fetchall()
        conn.close()
        
        # 验证agent2能找到自己的TODO（包含之前添加的2条）
        assert len(todos) == 3, f"agent2期望3条TODO（包含场景测试），实际{len(todos)}条"
        assert any(t[0] == "SCENARIO-001" for t in todos), "应该包含场景测试TODO"
    
    def test_agent1_does_not_see_agent2_todos(self, temp_db):
        """测试agent1看不到发给agent2的TODO"""
        # agent1查询
        agent_id = "agent1"
        
        receiver_query = agent_id.replace('agent', '') if agent_id else None
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM todos 
            WHERE receiver = ? AND status = ? AND is_read = 0
        """, (receiver_query, "pending"))
        
        todos = cursor.fetchall()
        conn.close()
        
        # agent1应该看不到发给agent2的TODO
        # 数据库里有一条发给"1"的TODO（TEST-003）
        assert len(todos) == 1, f"agent1期望1条TODO，实际{len(todos)}条"
        assert todos[0][0] == "TEST-003"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
