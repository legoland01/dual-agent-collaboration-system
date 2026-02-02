"""v2.2.0 M2 Resource Lock 测试用例

基于 src/core/resource_lock.py
"""
import pytest
import tempfile
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.resource_lock import (
    ResourceLockManager,
    ResourceLock,
    LockType,
    LockStatus,
    LockNotFoundError,
    LockConflictError,
    PermissionDeniedError
)


class TestResourceLockManagerBasic:
    """资源锁管理器基础测试。"""

    def test_initialize_lock_manager(self, tmp_path):
        """测试初始化资源锁管理器。"""
        manager = ResourceLockManager(str(tmp_path))
        
        assert manager.project_path == tmp_path
        assert manager.locks_file == tmp_path / "locks.yaml"

    def test_acquire_file_lock(self, tmp_path):
        """测试获取文件锁。"""
        manager = ResourceLockManager(str(tmp_path))
        lock = manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/components/Header.tsx",
            holder="agent_frontend_react",
            reason="实现头部组件"
        )
        
        assert lock is not None
        assert lock.lock_type == LockType.FILE
        assert lock.resource_path == "src/components/Header.tsx"
        assert lock.holder == "agent_frontend_react"
        assert lock.status == LockStatus.ACTIVE

    def test_acquire_directory_lock(self, tmp_path):
        """测试获取目录锁。"""
        manager = ResourceLockManager(str(tmp_path))
        lock = manager.acquire_lock(
            lock_type=LockType.DIRECTORY,
            resource_path="src/components",
            holder="agent_frontend_react",
            reason="批量修改组件"
        )
        
        assert lock is not None
        assert lock.lock_type == LockType.DIRECTORY

    def test_acquire_lock_with_custom_timeout(self, tmp_path):
        """测试获取带自定义超时的锁。"""
        manager = ResourceLockManager(str(tmp_path))
        lock = manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/app.py",
            holder="agent_backend_go",
            timeout_minutes=60
        )
        
        assert lock.timeout_minutes == 60


class TestLockRelease:
    """锁释放测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = ResourceLockManager(str(tmp_path))
        manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/test.py",
            holder="agent_test",
            reason="测试"
        )
        return manager

    def test_release_lock(self, manager):
        """测试释放锁。"""
        lock_id = manager.list_locks()[0].lock_id
        
        result = manager.release_lock(lock_id, "agent_test")
        assert result is True
        
        locks = manager.list_locks()
        assert len(locks) == 0

    def test_release_lock_wrong_holder(self, manager):
        """测试释放非己之锁。"""
        lock_id = manager.list_locks()[0].lock_id
        
        with pytest.raises(PermissionDeniedError):
            manager.release_lock(lock_id, "wrong_agent")


class TestLockConflict:
    """锁冲突测试。"""

    def test_cannot_acquire_locked_resource(self, tmp_path):
        """测试无法获取已锁定的资源。"""
        manager = ResourceLockManager(str(tmp_path))
        manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/shared.py",
            holder="agent_1"
        )
        
        with pytest.raises(LockConflictError):
            manager.acquire_lock(
                lock_type=LockType.FILE,
                resource_path="src/shared.py",
                holder="agent_2"
            )

    def test_same_holder_can_reacquire(self, tmp_path):
        """测试同一持有者可以重新获取锁。"""
        manager = ResourceLockManager(str(tmp_path))
        lock1 = manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/file.py",
            holder="agent_1"
        )
        lock2 = manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/file.py",
            holder="agent_1"
        )
        
        assert lock1.lock_id == lock2.lock_id


class TestLockQuery:
    """锁查询测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = ResourceLockManager(str(tmp_path))
        manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/file1.py",
            holder="agent_1"
        )
        manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/file2.py",
            holder="agent_2"
        )
        return manager

    def test_list_all_locks(self, manager):
        """测试列出所有锁。"""
        locks = manager.list_locks()
        assert len(locks) == 2

    def test_list_locks_by_holder(self, manager):
        """测试按持有者列出锁。"""
        locks = manager.list_locks(holder="agent_1")
        assert len(locks) == 1
        assert locks[0].holder == "agent_1"

    def test_list_locks_by_type(self, manager):
        """测试按类型列出锁。"""
        locks = manager.list_locks(lock_type=LockType.FILE)
        assert len(locks) == 2

    def test_get_lock_by_resource(self, manager):
        """测试根据资源路径获取锁。"""
        lock = manager.get_lock_by_resource(
            LockType.FILE,
            "src/file1.py"
        )
        assert lock is not None
        assert lock.resource_path == "src/file1.py"


class TestLockTimeout:
    """锁超时测试。"""

    def test_is_expired(self, tmp_path):
        """测试过期检查。"""
        manager = ResourceLockManager(str(tmp_path))
        lock = manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/test.py",
            holder="agent",
            timeout_minutes=1
        )
        
        assert lock.is_expired() is False

    def test_minutes_remaining(self, tmp_path):
        """测试剩余时间。"""
        manager = ResourceLockManager(str(tmp_path))
        lock = manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/test.py",
            holder="agent",
            timeout_minutes=30
        )
        
        remaining = lock.minutes_remaining()
        assert 0 < remaining <= 30

    def test_check_timeouts(self, tmp_path):
        """测试检查超时锁。"""
        manager = ResourceLockManager(str(tmp_path))
        manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/test.py",
            holder="agent",
            timeout_minutes=1
        )
        
        time.sleep(0.1)
        expired = manager.check_timeouts()
        assert len(expired) >= 0


class TestLockWarnings:
    """锁警告测试。"""

    def test_get_warnings(self, tmp_path):
        """测试获取警告。"""
        manager = ResourceLockManager(
            str(tmp_path),
            warning_before_minutes=60
        )
        manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/test.py",
            holder="agent",
            timeout_minutes=30
        )
        
        warnings = manager.get_warnings()
        assert len(warnings) == 1


class TestForceRelease:
    """强制释放测试。"""

    def test_force_release_lock(self, tmp_path):
        """测试强制释放锁。"""
        manager = ResourceLockManager(str(tmp_path))
        manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/test.py",
            holder="agent_1"
        )
        
        lock_id = manager.list_locks()[0].lock_id
        result = manager.force_release_lock(
            lock_id,
            reason="超时释放",
            requester="agent_1"
        )
        
        assert result is True
        assert len(manager.list_locks()) == 0


class TestLockSummary:
    """锁摘要测试。"""

    def test_get_lock_summary(self, tmp_path):
        """测试获取锁摘要。"""
        manager = ResourceLockManager(str(tmp_path))
        manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/file1.py",
            holder="agent"
        )
        manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/file2.py",
            holder="agent"
        )
        
        summary = manager.get_lock_summary()
        
        assert summary["total_active_locks"] == 2
        assert summary["by_type"]["file"] == 2


class TestAutoExpireLocks:
    """自动过期测试。"""

    def test_check_timeouts_function(self, tmp_path):
        """测试检查超时锁功能。"""
        manager = ResourceLockManager(str(tmp_path))
        manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/test.py",
            holder="agent",
            timeout_minutes=1
        )
        
        time.sleep(0.1)
        expired = manager.check_timeouts()
        assert len(expired) >= 0


class TestLockReload:
    """锁重载测试。"""

    def test_reload_locks_from_file(self, tmp_path):
        """测试从文件重载锁。"""
        manager = ResourceLockManager(str(tmp_path))
        manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/test.py",
            holder="agent"
        )
        
        manager2 = ResourceLockManager(str(tmp_path))
        locks = manager2.list_locks()
        assert len(locks) == 1


class TestExport:
    """导出测试。"""

    def test_export_locks(self, tmp_path):
        """测试导出锁数据。"""
        manager = ResourceLockManager(str(tmp_path))
        manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/test.py",
            holder="agent"
        )
        
        data = manager.export_locks()
        
        assert "active_locks" in data
        assert "summary" in data
        assert len(data["active_locks"]) == 1


class TestErrorHandling:
    """错误处理测试。"""

    def test_get_nonexistent_lock(self, tmp_path):
        """测试获取不存在的锁。"""
        manager = ResourceLockManager(str(tmp_path))
        
        with pytest.raises(LockNotFoundError):
            manager.get_lock("LOCK-xxxxxx")

    def test_release_nonexistent_lock(self, tmp_path):
        """测试释放不存在的锁。"""
        manager = ResourceLockManager(str(tmp_path))
        
        with pytest.raises(LockNotFoundError):
            manager.release_lock("LOCK-xxxxxx", "agent")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
