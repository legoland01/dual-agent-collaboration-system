"""
测试用例：FR-OWNER-001 文件Owner机制
"""
import pytest
import yaml
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
OWNER_FILE = PROJECT_ROOT / ".file_owners.yaml"


class TestFileOwnerManager:
    """测试 FileOwnerManager 功能"""

    def setup_method(self):
        """每个测试前备份并清理 Owner 文件"""
        self.backup = None
        if OWNER_FILE.exists():
            with open(OWNER_FILE) as f:
                self.backup = f.read()
            OWNER_FILE.unlink()

    def teardown_method(self):
        """每个测试后恢复 Owner 文件"""
        if self.backup is not None:
            with open(OWNER_FILE, 'w') as f:
                f.write(self.backup)
        elif OWNER_FILE.exists():
            OWNER_FILE.unlink()

    def test_record_file_creation(self):
        """TC-OWNER-001: 记录文件创建者"""
        from src.core.file_owner import FileOwnerManager

        manager = FileOwnerManager(str(PROJECT_ROOT))
        
        # 记录创建者
        result = manager.record_file_creation(
            "src/core/test_file.py", 
            "agent1"
        )
        
        assert result is True, "应该成功记录创建者"
        
        # 验证 Owner
        owner = manager.get_file_owner("src/core/test_file.py")
        assert owner == "agent1", f"Owner 应该是 agent1，实际是 {owner}"

    def test_get_file_owner_not_exists(self):
        """TC-OWNER-002: 获取不存在的文件 Owner"""
        from src.core.file_owner import FileOwnerManager

        manager = FileOwnerManager(str(PROJECT_ROOT))
        
        owner = manager.get_file_owner("nonexistent/file.py")
        assert owner is None, "不存在的文件应该返回 None"

    def test_owner_can_modify(self):
        """TC-OWNER-003: Owner 可以修改自己的文件"""
        from src.core.file_owner import FileOwnerManager

        manager = FileOwnerManager(str(PROJECT_ROOT))
        
        # 记录创建者
        manager.record_file_creation("src/core/test.py", "agent1")
        
        # Owner 修改
        can_modify, reason = manager.can_modify("src/core/test.py", "agent1")
        assert can_modify is True, "Owner 应该能修改自己的文件"
        assert reason == "", "原因应该为空"

    def test_non_owner_cannot_modify(self):
        """TC-OWNER-004: 非 Owner 不能修改文件"""
        from src.core.file_owner import FileOwnerManager

        manager = FileOwnerManager(str(PROJECT_ROOT))
        
        # 记录创建者为 agent1
        manager.record_file_creation("src/core/test.py", "agent1")
        
        # agent2 尝试修改
        can_modify, reason = manager.can_modify("src/core/test.py", "agent2")
        assert can_modify is False, "非 Owner 不应该能修改文件"
        assert "agent1" in reason, "拒绝原因应该包含 Owner"

    def test_transfer_owner(self):
        """TC-OWNER-005: Owner 转移"""
        from src.core.file_owner import FileOwnerManager

        manager = FileOwnerManager(str(PROJECT_ROOT))
        
        # 记录创建者为 agent1
        manager.record_file_creation("src/core/test.py", "agent1")
        
        # 转移给 agent2
        result = manager.transfer_owner("src/core/test.py", "agent1", "agent2")
        assert result is True, "转移应该成功"
        
        # 验证新 Owner
        owner = manager.get_file_owner("src/core/test.py")
        assert owner == "agent2", f"Owner 应该是 agent2，实际是 {owner}"

    def test_transfer_owner_wrong_from(self):
        """TC-OWNER-006: 错误的原 Owner 无法转移"""
        from src.core.file_owner import FileOwnerManager

        manager = FileOwnerManager(str(PROJECT_ROOT))
        
        # 记录创建者为 agent1
        manager.record_file_creation("src/core/test.py", "agent1")
        
        # agent2 尝试转移（失败）
        result = manager.transfer_owner("src/core/test.py", "agent2", "agent1")
        assert result is False, "错误的原 Owner 不应该能转移"

    def test_transfer_nonexistent_file(self):
        """TC-OWNER-007: 转移不存在的文件"""
        from src.core.file_owner import FileOwnerManager

        manager = FileOwnerManager(str(PROJECT_ROOT))
        
        result = manager.transfer_owner("nonexistent/file.py", "agent1", "agent2")
        assert result is False, "不存在的文件转移应该失败"

    def test_get_owner_status(self):
        """TC-OWNER-008: 获取 Owner 统计"""
        from src.core.file_owner import FileOwnerManager

        manager = FileOwnerManager(str(PROJECT_ROOT))
        
        # 创建多个文件
        manager.record_file_creation("src/file1.py", "agent1")
        manager.record_file_creation("src/file2.py", "agent1")
        manager.record_file_creation("docs/doc1.md", "agent2")
        
        # 获取统计
        status = manager.get_owner_status()
        
        assert status["total_files"] == 3, f"应该有 3 个文件，实际 {status['total_files']}"
        assert "agent1" in status["agent_files"], "应该有 agent1 的文件"
        assert "agent2" in status["agent_files"], "应该有 agent2 的文件"
        assert len(status["agent_files"]["agent1"]) == 2, "agent1 应该有 2 个文件"

    def test_record_duplicate_file(self):
        """TC-OWNER-009: 重复记录同一文件"""
        from src.core.file_owner import FileOwnerManager

        manager = FileOwnerManager(str(PROJECT_ROOT))
        
        # 第一次记录
        result1 = manager.record_file_creation("src/core/test.py", "agent1")
        
        # 第二次记录（应该失败）
        result2 = manager.record_file_creation("src/core/test.py", "agent2")
        
        assert result1 is True, "第一次记录应该成功"
        assert result2 is False, "重复记录应该失败"
        
        # Owner 应该是第一个
        owner = manager.get_file_owner("src/core/test.py")
        assert owner == "agent1", "Owner 应该是第一个记录者"

    def test_get_file_owner_info(self):
        """TC-OWNER-010: 获取文件 Owner 详细信息"""
        from src.core.file_owner import FileOwnerManager

        manager = FileOwnerManager(str(PROJECT_ROOT))
        
        # 记录创建者
        manager.record_file_creation("src/core/test.py", "agent1")
        
        # 获取详细信息
        info = manager.get_file_owner_info("src/core/test.py")
        
        assert "owner" in info, "应该有 owner 字段"
        assert info["owner"] == "agent1", f"owner 应该是 agent1"
        assert "created_at" in info, "应该有 created_at 字段"
        assert "created_by" in info, "应该有 created_by 字段"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
