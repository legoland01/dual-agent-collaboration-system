"""SignoffRecordManager 单元测试。"""
import pytest
import tempfile
import os
from pathlib import Path


class TestSignoffRecord:
    """SignoffRecord 测试。"""

    def test_signoff_record_to_dict(self):
        """测试签署记录转字典。"""
        from src.core.signoff_record_manager import SignoffRecord

        record = SignoffRecord(
            signoff_id="SIG-M1-20260207",
            milestone="M1",
            phase="requirements",
            signers=[{"agent": "agent1", "status": "approved"}],
            status="APPROVED",
            created_at="2026-02-07T00:00:00"
        )

        result = record.to_dict()
        assert result["signoff_id"] == "SIG-M1-20260207"
        assert result["milestone"] == "M1"
        assert len(result["signers"]) == 1


class TestSignoffRecordManager:
    """SignoffRecordManager 测试。"""

    def setup_method(self):
        """创建临时目录。"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """清理临时目录。"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """测试初始化。"""
        from src.core.signoff_record_manager import SignoffRecordManager

        manager = SignoffRecordManager(self.temp_dir)
        assert manager.project_path == Path(self.temp_dir)
        assert (manager.signoffs_dir).exists()

    def test_save_signoff(self):
        """测试保存签署记录。"""
        from src.core.signoff_record_manager import SignoffRecordManager

        manager = SignoffRecordManager(self.temp_dir)
        signoff_id = manager.save_signoff(
            milestone="M1",
            phase="requirements",
            signers=[{"agent": "agent1", "status": "approved"}],
            status="APPROVED"
        )

        assert signoff_id.startswith("SIG-M1-")
        assert (manager.signoffs_dir / f"{signoff_id}.yaml").exists()

    def test_get_signoff(self):
        """测试获取签署记录。"""
        from src.core.signoff_record_manager import SignoffRecordManager

        manager = SignoffRecordManager(self.temp_dir)
        signoff_id = manager.save_signoff(
            milestone="M1",
            phase="requirements",
            signers=[{"agent": "agent1", "status": "approved"}],
            status="APPROVED"
        )

        record = manager.get_signoff(signoff_id)
        assert record is not None
        assert record["milestone"] == "M1"
        assert record["phase"] == "requirements"

    def test_get_signoff_not_exists(self):
        """测试获取不存在的签署记录。"""
        from src.core.signoff_record_manager import SignoffRecordManager

        manager = SignoffRecordManager(self.temp_dir)
        record = manager.get_signoff("SIG-NOTEXIST-20260207")

        assert record is None

    def test_list_signoffs(self):
        """测试列出所有签署记录。"""
        from src.core.signoff_record_manager import SignoffRecordManager

        manager = SignoffRecordManager(self.temp_dir)
        manager.save_signoff("M1", "requirements", [], "PENDING")
        manager.save_signoff("M2", "design", [], "PENDING")

        signoffs = manager.list_signoffs()
        assert len(signoffs) == 2

    def test_update_signoff_status(self):
        """测试更新签署状态。"""
        from src.core.signoff_record_manager import SignoffRecordManager

        manager = SignoffRecordManager(self.temp_dir)
        signoff_id = manager.save_signoff("M1", "requirements", [], "PENDING")

        manager.update_signoff_status(signoff_id, "APPROVED")

        record = manager.get_signoff(signoff_id)
        assert record["status"] == "APPROVED"

    def test_check_all_signed(self):
        """测试检查所有签署者都已签署。"""
        from src.core.signoff_record_manager import SignoffRecordManager

        manager = SignoffRecordManager(self.temp_dir)
        signoff_id = manager.save_signoff(
            "M1",
            "requirements",
            [
                {"agent": "agent1", "status": "approved"},
                {"agent": "agent2", "status": "approved"}
            ],
            "PENDING"
        )

        result = manager.check_all_signed(signoff_id)
        assert result is True

    def test_check_all_signed_not_complete(self):
        """测试检查所有签署者未都签署。"""
        from src.core.signoff_record_manager import SignoffRecordManager

        manager = SignoffRecordManager(self.temp_dir)
        signoff_id = manager.save_signoff(
            "M1",
            "requirements",
            [
                {"agent": "agent1", "status": "approved"},
                {"agent": "agent2", "status": "pending"}
            ],
            "PENDING"
        )

        result = manager.check_all_signed(signoff_id)
        assert result is False

    def test_update_signoff_status_with_signer(self):
        """测试更新签署者状态。"""
        from src.core.signoff_record_manager import SignoffRecordManager

        manager = SignoffRecordManager(self.temp_dir)
        signoff_id = manager.save_signoff(
            "M1",
            "requirements",
            [{"agent": "agent1", "status": "pending"}],
            "PENDING"
        )

        manager.update_signoff_status(
            signoff_id,
            "PENDING",
            {"agent": "agent1", "status": "approved"}
        )

        record = manager.get_signoff(signoff_id)
        assert record["signers"][0]["status"] == "approved"

    def test_check_all_signed_empty_signers(self):
        """测试检查空签署者列表。"""
        from src.core.signoff_record_manager import SignoffRecordManager

        manager = SignoffRecordManager(self.temp_dir)
        signoff_id = manager.save_signoff(
            "M1",
            "requirements",
            [],
            "PENDING"
        )

        result = manager.check_all_signed(signoff_id)
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
