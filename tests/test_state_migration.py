"""StateMigrator 单元测试。

测试用例：
- v1.0 → v2.0 迁移
- v2.0 → v2.1 迁移
- 备份功能
- 迁移完整性验证
- 干运行模式
- 已是最新版本
"""
import pytest
import tempfile
import os
from pathlib import Path
import yaml

from src.core.state_migrator import StateMigrator


class TestStateMigrationV1ToV2:
    """v1.0 → v2.0 迁移测试。"""

    @pytest.fixture
    def v1_state(self):
        """创建 v1.0 格式的 state。"""
        return {
            "version": "1.0",
            "phase": "development",
            "requirements": {
                "status": "approved",
                "pm_signoff": True,
                "dev_signoff": True
            },
            "design": {
                "status": "completed",
                "pm_signoff": True,
                "dev_signoff": True,
                "document": "docs/design.md",
                "review_document": "docs/review.md"
            },
            "test": {"status": "pending"},
            "development": {"status": "in_progress"},
            "deployment": {"status": "pending"}
        }

    def test_phase_migration(self, v1_state):
        """测试 phase 迁移到 project.phase。"""
        migrator = StateMigrator("state/project_state.yaml", dry_run=True)
        
        success, result = migrator.migrate(v1_state)
        
        assert success
        assert "phase" not in result
        assert result["project"]["phase"] == "development"

    def test_requirements_list_conversion(self, v1_state):
        """测试 requirements 转换为列表格式。"""
        migrator = StateMigrator("state/project_state.yaml", dry_run=True)
        
        success, result = migrator.migrate(v1_state)
        
        assert success
        assert isinstance(result["requirements"], list)
        assert len(result["requirements"]) == 1
        assert result["requirements"][0]["status"] == "approved"

    def test_design_list_conversion(self, v1_state):
        """测试 design 转换为列表格式。"""
        migrator = StateMigrator("state/project_state.yaml", dry_run=True)
        
        success, result = migrator.migrate(v1_state)
        
        assert success
        assert isinstance(result["design"], list)
        assert len(result["design"]) == 1
        assert result["design"][0]["status"] == "completed"
        assert result["design"][0]["document"] == "docs/design.md"

    def test_version_updated(self, v1_state):
        """测试版本号更新。"""
        migrator = StateMigrator("state/project_state.yaml", dry_run=True)
        
        success, result = migrator.migrate(v1_state)
        
        assert success
        # StateMigrator 会直接迁移到最新版本
        assert result["version"] == "2.1.0"


class TestStateMigrationV2ToV21:
    """v2.0 → v2.1 迁移测试。"""

    @pytest.fixture
    def v2_state(self):
        """创建 v2.0 格式的 state。"""
        return {
            "version": "2.0",
            "project": {
                "name": "Test Project",
                "type": "PYTHON",
                "phase": "development"
            },
            "requirements": [{"version": "v1", "status": "approved"}],
            "design": [{"version": "v1", "status": "completed"}],
            "test": {"status": "pending"},
            "development": {"status": "in_progress"},
            "deployment": {"status": "pending"}
        }

    def test_agent_constraints_added(self, v2_state):
        """测试添加 agent_constraints 字段。"""
        migrator = StateMigrator("state/project_state.yaml", dry_run=True)
        
        success, result = migrator.migrate(v2_state)
        
        assert success
        assert "agent_constraints" in result
        assert result["agent_constraints"]["version"] == "1.0"
        assert "agent1" in result["agent_constraints"]
        assert "agent2" in result["agent_constraints"]

    def test_iteration_added(self, v2_state):
        """测试添加 iteration 字段。"""
        migrator = StateMigrator("state/project_state.yaml", dry_run=True)
        
        success, result = migrator.migrate(v2_state)
        
        assert success
        assert "iteration" in result
        assert result["iteration"]["current"] == "v2.1.0"
        assert result["iteration"]["status"] == "development"

    def test_version_updated(self, v2_state):
        """测试版本号更新。"""
        migrator = StateMigrator("state/project_state.yaml", dry_run=True)
        
        success, result = migrator.migrate(v2_state)
        
        assert success
        assert result["version"] == "2.1.0"


class TestStateMigrationBackup:
    """备份功能测试。"""

    def test_backup_created(self, tmp_path):
        """测试迁移前创建备份。"""
        state_path = tmp_path / "state.yaml"
        backup_dir = tmp_path / "backups"
        
        # 创建测试 state
        state = {
            "version": "1.0",
            "phase": "development",
            "requirements": {"status": "approved"},
            "design": {"status": "completed"},
            "test": {"status": "pending"},
            "development": {"status": "in_progress"},
            "deployment": {"status": "pending"}
        }
        with open(state_path, 'w') as f:
            yaml.dump(state, f)
        
        # 执行迁移（带备份）
        migrator = StateMigrator(str(state_path), backup_dir=str(backup_dir), dry_run=False)
        success, result = migrator.migrate(state)
        
        assert success
        
        # 检查备份文件
        backup_files = list(backup_dir.glob("state_*.yaml"))
        assert len(backup_files) == 1

    def test_no_backup_in_dry_run(self, tmp_path):
        """测试干运行模式不创建备份。"""
        state_path = tmp_path / "state.yaml"
        backup_dir = tmp_path / "backups"
        
        state = {
            "version": "1.0",
            "phase": "development",
            "requirements": {"status": "approved"},
            "design": {"status": "completed"},
            "test": {"status": "pending"},
            "development": {"status": "in_progress"},
            "deployment": {"status": "pending"}
        }
        with open(state_path, 'w') as f:
            yaml.dump(state, f)
        
        # 干运行模式
        migrator = StateMigrator(str(state_path), backup_dir=str(backup_dir), dry_run=True)
        success, result = migrator.migrate(state)
        
        assert success
        assert not backup_dir.exists()


class TestStateMigrationIntegrity:
    """迁移完整性验证测试。"""

    def test_migration_integrity_valid(self, tmp_path):
        """测试有效迁移的完整性验证。"""
        state_path = tmp_path / "state.yaml"
        
        state = {
            "version": "1.0",
            "phase": "development",
            "requirements": {"status": "approved"},
            "design": {"status": "completed"},
            "test": {"status": "pending"},
            "development": {"status": "in_progress"},
            "deployment": {"status": "pending"}
        }
        
        migrator = StateMigrator(str(state_path), dry_run=True)
        success, result = migrator.migrate(state)
        
        assert success
        assert "project" in result
        assert "requirements" in result
        assert "design" in result
        assert "test" in result
        assert "development" in result
        assert "deployment" in result


class TestStateMigrationNoMigration:
    """无需迁移测试。"""

    def test_latest_version_no_migration(self):
        """测试已是最新版本无需迁移。"""
        state = {
            "version": "2.1.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{}],
            "design": [{}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        migrator = StateMigrator("state/project_state.yaml", dry_run=True)
        
        assert migrator.needs_migration(state) is False
        
        success, result = migrator.migrate(state)
        assert success
        # 状态不应被修改
        assert result["version"] == "2.1.0"


class TestStateMigrationDryRun:
    """干运行模式测试。"""

    def test_dry_run_does_not_modify(self, tmp_path):
        """测试干运行模式不修改文件。"""
        state_path = tmp_path / "state.yaml"
        
        original_state = {
            "version": "1.0",
            "phase": "development",
            "requirements": {"status": "approved"},
            "design": {"status": "completed"},
            "test": {"status": "pending"},
            "development": {"status": "in_progress"},
            "deployment": {"status": "pending"}
        }
        with open(state_path, 'w') as f:
            yaml.dump(original_state, f)
        
        # 读取原始内容
        with open(state_path, 'r') as f:
            original_content = f.read()
        
        # 干运行
        migrator = StateMigrator(str(state_path), dry_run=True)
        success, result = migrator.migrate(original_state)
        
        assert success
        
        # 文件不应被修改
        with open(state_path, 'r') as f:
            new_content = f.read()
        
        assert original_content == new_content


class TestStateMigrationV11:
    """v1.1 迁移测试。"""

    def test_v1_1_migrates_to_v21(self):
        """测试 v1.1 迁移到 v2.1。"""
        state = {
            "version": "1.1",
            "phase": "development",
            "requirements": {"status": "approved"},
            "design": {"status": "completed"},
            "test": {"status": "pending"},
            "development": {"status": "in_progress"},
            "deployment": {"status": "pending"}
        }
        
        migrator = StateMigrator("state/project_state.yaml", dry_run=True)
        success, result = migrator.migrate(state)
        
        assert success
        # 直接迁移到最新版本
        assert result["version"] == "2.1.0"


class TestStateMigrationPaths:
    """迁移路径测试。"""

    def test_direct_v2_to_v21(self):
        """测试直接从 v2.0 迁移到 v2.1。"""
        state = {
            "version": "2.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{}],
            "design": [{}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        migrator = StateMigrator("state/project_state.yaml", dry_run=True)
        success, result = migrator.migrate(state)
        
        assert success
        assert result["version"] == "2.1.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
