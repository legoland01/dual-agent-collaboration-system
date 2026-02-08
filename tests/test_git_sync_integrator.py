"""测试 Git 同步集成器 - v2.2.2 F-GIT-001"""
import pytest
import tempfile
import subprocess
from pathlib import Path
import os

from src.core.git_sync_integrator import GitSyncIntegrator, SyncResult


@pytest.fixture
def temp_git_project():
    """创建临时 Git 项目"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], capture_output=True)
        yield Path(tmpdir)
        os.chdir(Path.cwd())


@pytest.fixture
def integrator(temp_git_project):
    """创建 Git 同步集成器"""
    return GitSyncIntegrator(str(temp_git_project))


class TestGitSyncIntegrator:
    """Git 同步集成器测试"""

    def test_init(self, temp_git_project):
        """测试初始化"""
        integrator = GitSyncIntegrator(str(temp_git_project))
        assert integrator.project_path == temp_git_project

    def test_detect_changes_empty(self, integrator):
        """测试无变更检测"""
        changes = integrator.detect_changes()
        assert changes == []

    def test_detect_changes(self, integrator, temp_git_project):
        """测试变更检测"""
        (temp_git_project / "test.txt").write_text("test content")
        subprocess.run(["git", "add", "test.txt"], capture_output=True)
        changes = integrator.detect_changes()
        assert len(changes) == 1
        assert "test.txt" in changes[0]

    def test_auto_add(self, integrator, temp_git_project):
        """测试自动添加"""
        (temp_git_project / "test.txt").write_text("test content")
        result = integrator.auto_add()
        assert result.success is True
        assert len(result.details["added"]) == 1

    def test_auto_add_no_changes(self, integrator):
        """测试无变更添加"""
        result = integrator.auto_add()
        assert result.success is True
        assert "无变更" in result.message

    def test_auto_commit_empty(self, integrator):
        """测试空提交"""
        result = integrator.auto_commit("test commit")
        assert result.success is True

    def test_auto_commit_with_changes(self, integrator, temp_git_project):
        """测试带变更提交"""
        (temp_git_project / "test.txt").write_text("test content")
        integrator.auto_add()
        result = integrator.auto_commit("test commit")
        assert result.success is True
        assert "提交成功" in result.message or "无需提交" in result.message

    def test_auto_push_empty(self, integrator, temp_git_project):
        """测试空推送（无远程仓库时预期失败）"""
        integrator.auto_commit("initial")
        result = integrator.auto_push()
        assert result.success is False or "up-to-date" in result.message.lower()

    def test_sync_state(self, integrator, temp_git_project):
        """测试状态同步"""
        (temp_git_project / "state.yaml").write_text("key: value")
        integrator.auto_add()
        result = integrator.sync_state()
        assert result.success is True

    def test_check_unsynced(self, integrator, temp_git_project):
        """测试未同步检查"""
        (temp_git_project / "test.txt").write_text("test")
        integrator.auto_add()
        unsynced = integrator.check_unsynced()
        assert len(unsynced) >= 1

    def test_get_sync_status_synced(self, integrator):
        """测试同步状态 - 已同步"""
        status = integrator.get_sync_status()
        assert status["status"] == "synced"
        assert status["unsynced_count"] == 0

    def test_get_sync_status_unsynced(self, integrator, temp_git_project):
        """测试同步状态 - 未同步"""
        (temp_git_project / "test.txt").write_text("test")
        status = integrator.get_sync_status()
        assert status["status"] == "unsynced"
        assert status["unsynced_count"] > 0

    def test_warn_unsynced_empty(self, integrator):
        """测试无未同步警告"""
        warning = integrator.warn_unsynced()
        assert warning == ""

    def test_warn_unsynced_with_changes(self, integrator, temp_git_project):
        """测试有未同步警告"""
        (temp_git_project / "test.txt").write_text("test")
        warning = integrator.warn_unsynced()
        assert "警告" in warning
        assert "test.txt" in warning


class TestSyncResult:
    """同步结果测试"""

    def test_sync_result_creation(self):
        """测试创建同步结果"""
        result = SyncResult(
            success=True,
            message="测试成功",
            details={"key": "value"}
        )
        assert result.success is True
        assert result.message == "测试成功"
        assert result.details["key"] == "value"

    def test_sync_result_to_dict(self):
        """测试转换为字典"""
        result = SyncResult(
            success=True,
            message="测试成功",
            details={"key": "value"}
        )
        data = result.to_dict()
        assert data["success"] is True
        assert data["message"] == "测试成功"
        assert data["details"]["key"] == "value"
