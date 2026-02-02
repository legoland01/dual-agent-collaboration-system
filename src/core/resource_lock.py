"""资源锁模块 - v2.2.0 M2 资源锁管理

提供文件锁、目录锁、任务锁，防止并发冲突。
"""
import uuid
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
import json
import logging
from datetime import datetime, timedelta
from threading import Lock as ThreadLock


logger = logging.getLogger(__name__)


class LockType(Enum):
    """锁类型枚举。"""
    FILE = "file"
    DIRECTORY = "directory"
    TASK = "task"


class LockStatus(Enum):
    """锁状态枚举。"""
    ACTIVE = "active"
    EXPIRED = "expired"
    RELEASED = "released"
    FORCE_RELEASED = "force_released"


@dataclass
class ResourceLock:
    """资源锁。"""
    lock_id: str
    lock_type: LockType
    resource_path: str
    holder: str
    status: LockStatus = LockStatus.ACTIVE
    timeout_minutes: int = 30
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: str = field(default_factory=lambda: (datetime.now() + timedelta(minutes=30)).isoformat())
    reason: str = ""
    force_release_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lock_id": self.lock_id,
            "lock_type": self.lock_type.value,
            "resource_path": self.resource_path,
            "holder": self.holder,
            "status": self.status.value,
            "timeout_minutes": self.timeout_minutes,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "reason": self.reason,
            "force_release_reason": self.force_release_reason
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceLock":
        return cls(
            lock_id=data["lock_id"],
            lock_type=LockType(data["lock_type"]),
            resource_path=data["resource_path"],
            holder=data["holder"],
            status=LockStatus(data.get("status", "active")),
            timeout_minutes=data.get("timeout_minutes", 30),
            created_at=data.get("created_at", datetime.now().isoformat()),
            expires_at=data.get("expires_at", (datetime.now() + timedelta(minutes=30)).isoformat()),
            reason=data.get("reason", ""),
            force_release_reason=data.get("force_release_reason")
        )

    def is_expired(self) -> bool:
        """检查是否已过期。"""
        try:
            expires = datetime.fromisoformat(self.expires_at)
            return datetime.now() > expires
        except ValueError:
            return True

    def minutes_remaining(self) -> float:
        """获取剩余时间（分钟）。"""
        try:
            expires = datetime.fromisoformat(self.expires_at)
            remaining = expires - datetime.now()
            return remaining.total_seconds() / 60
        except ValueError:
            return 0


class ResourceLockError(Exception):
    """资源锁异常基类。"""
    pass


class LockNotFoundError(ResourceLockError):
    """锁未找到异常。"""
    pass


class LockConflictError(ResourceLockError):
    """锁冲突异常。"""
    pass


class LockTimeoutError(ResourceLockError):
    """锁超时异常。"""
    pass


class PermissionDeniedError(ResourceLockError):
    """权限不足异常。"""
    pass


class ResourceLockManager:
    """资源锁管理器。"""

    DEFAULT_TIMEOUTS = {
        LockType.FILE: 30,
        LockType.DIRECTORY: 120,
        LockType.TASK: 1440
    }

    def __init__(
        self,
        project_path: str,
        locks_file: Optional[str] = None,
        warning_before_minutes: int = 5
    ):
        """初始化资源锁管理器。

        Args:
            project_path: 项目路径
            locks_file: 锁数据文件
            warning_before_minutes: 超时前警告时间（分钟）
        """
        self.project_path = Path(project_path)
        self.locks_file = self.project_path / (locks_file or "locks.yaml")
        self.warning_before_minutes = warning_before_minutes
        self.locks: Dict[str, ResourceLock] = {}
        self._lock = ThreadLock()
        self._load_locks()

    def _load_locks(self) -> None:
        """加载锁数据。"""
        if self.locks_file.exists():
            try:
                with open(self.locks_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if data and "locks" in data:
                    for lock_data in data.get("locks", []):
                        lock = ResourceLock.from_dict(lock_data)
                        if lock.status == LockStatus.ACTIVE and not lock.is_expired():
                            self.locks[lock.lock_id] = lock
            except Exception as e:
                logger.warning(f"加载锁数据失败: {e}")

    def _save_locks(self) -> None:
        """保存锁数据。"""
        data = {
            "locks": [lock.to_dict() for lock in self.locks.values()],
            "updated_at": datetime.now().isoformat()
        }
        with open(self.locks_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)

    def acquire_lock(
        self,
        lock_type: LockType,
        resource_path: str,
        holder: str,
        timeout_minutes: Optional[int] = None,
        reason: str = ""
    ) -> ResourceLock:
        """获取锁。

        Args:
            lock_type: 锁类型
            resource_path: 资源路径
            holder: 持有者
            timeout_minutes: 超时时间（分钟）
            reason: 锁定原因

        Returns:
            创建的锁

        Raises:
            LockConflictError: 资源已被锁定
        """
        with self._lock:
            existing_lock = self._find_active_lock(lock_type, resource_path)
            if existing_lock:
                if existing_lock.holder == holder:
                    return existing_lock
                raise LockConflictError(
                    f"资源已被锁定: {resource_path} (持有者: {existing_lock.holder})"
                )
            
            timeout = timeout_minutes or self.DEFAULT_TIMEOUTS[lock_type]
            lock_id = f"LOCK-{uuid.uuid4().hex[:8]}"
            
            lock = ResourceLock(
                lock_id=lock_id,
                lock_type=lock_type,
                resource_path=resource_path,
                holder=holder,
                timeout_minutes=timeout,
                reason=reason
            )
            
            self.locks[lock_id] = lock
            self._save_locks()
            logger.info(f"获取锁: {lock_id} - {resource_path} by {holder}")
            return lock

    def release_lock(self, lock_id: str, holder: str) -> bool:
        """释放锁。

        Args:
            lock_id: 锁 ID
            holder: 释放者

        Returns:
            是否成功释放

        Raises:
            LockNotFoundError: 锁未找到
            PermissionDeniedError: 无权释放
        """
        with self._lock:
            if lock_id not in self.locks:
                raise LockNotFoundError(f"锁未找到: {lock_id}")
            
            lock = self.locks[lock_id]
            if lock.holder != holder:
                raise PermissionDeniedError(
                    f"无权释放锁: {lock_id} (持有者: {lock.holder})"
                )
            
            lock.status = LockStatus.RELEASED
            del self.locks[lock_id]
            self._save_locks()
            logger.info(f"释放锁: {lock_id}")
            return True

    def force_release_lock(
        self,
        lock_id: str,
        reason: str,
        requester: str
    ) -> bool:
        """强制释放锁（仅 Agent 1 可用）。

        Args:
            lock_id: 锁 ID
            reason: 强制释放原因
            requester: 请求者

        Returns:
            是否成功释放

        Raises:
            LockNotFoundError: 锁未找到
        """
        with self._lock:
            if lock_id not in self.locks:
                raise LockNotFoundError(f"锁未找到: {lock_id}")
            
            lock = self.locks[lock_id]
            lock.status = LockStatus.FORCE_RELEASED
            lock.force_release_reason = f"{reason} (by {requester})"
            del self.locks[lock_id]
            self._save_locks()
            logger.info(f"强制释放锁: {lock_id} - {reason}")
            return True

    def get_lock(self, lock_id: str) -> ResourceLock:
        """获取锁信息。

        Args:
            lock_id: 锁 ID

        Returns:
            锁信息

        Raises:
            LockNotFoundError: 锁未找到
        """
        if lock_id not in self.locks:
            raise LockNotFoundError(f"锁未找到: {lock_id}")
        return self.locks[lock_id]

    def get_lock_by_resource(
        self,
        lock_type: LockType,
        resource_path: str
    ) -> Optional[ResourceLock]:
        """根据资源路径获取锁。

        Args:
            lock_type: 锁类型
            resource_path: 资源路径

        Returns:
            锁信息，未找到返回 None
        """
        return self._find_active_lock(lock_type, resource_path)

    def _find_active_lock(
        self,
        lock_type: LockType,
        resource_path: str
    ) -> Optional[ResourceLock]:
        """查找活跃锁。"""
        for lock in self.locks.values():
            if lock.lock_type == lock_type and lock.resource_path == resource_path:
                if not lock.is_expired():
                    return lock
        return None

    def list_locks(
        self,
        holder: Optional[str] = None,
        lock_type: Optional[LockType] = None,
        status: Optional[LockStatus] = None
    ) -> List[ResourceLock]:
        """列出锁。

        Args:
            holder: 持有者过滤
            lock_type: 锁类型过滤
            status: 状态过滤

        Returns:
            锁列表
        """
        locks = list(self.locks.values())
        
        if holder:
            locks = [l for l in locks if l.holder == holder]
        if lock_type:
            locks = [l for l in locks if l.lock_type == lock_type]
        if status:
            locks = [l for l in locks if l.status == status]
        
        return sorted(locks, key=lambda l: l.created_at, reverse=True)

    def check_timeouts(self) -> List[ResourceLock]:
        """检查超时锁。

        Returns:
            超时的锁列表
        """
        expired_locks = []
        for lock in self.locks.values():
            if lock.is_expired():
                expired_locks.append(lock)
        return expired_locks

    def get_warnings(self) -> List[ResourceLock]:
        """获取即将超时的锁警告。

        Returns:
            即将超时的锁列表
        """
        warnings = []
        for lock in self.locks.values():
            remaining = lock.minutes_remaining()
            if 0 < remaining <= self.warning_before_minutes:
                warnings.append(lock)
        return warnings

    def auto_expire_locks(self) -> List[str]:
        """自动过期处理超时的锁。

        Returns:
            过期的锁 ID 列表
        """
        expired_ids = []
        for lock_id in list(self.locks.keys()):
            lock = self.locks[lock_id]
            if lock.is_expired():
                lock.status = LockStatus.EXPIRED
                expired_ids.append(lock_id)
                logger.warning(f"锁已过期自动释放: {lock_id} - {lock.resource_path}")
        
        for lock_id in expired_ids:
            del self.locks[lock_id]
        
        if expired_ids:
            self._save_locks()
        
        return expired_ids

    def get_lock_summary(self) -> Dict[str, Any]:
        """获取锁管理摘要。

        Returns:
            摘要信息
        """
        active_locks = self.list_locks(status=LockStatus.ACTIVE)
        warnings = self.get_warnings()
        
        by_type = {}
        for lock_type in LockType:
            by_type[lock_type.value] = len([
                l for l in active_locks if l.lock_type == lock_type
            ])
        
        return {
            "total_active_locks": len(active_locks),
            "by_type": by_type,
            "warnings": len(warnings),
            "locks_file": str(self.locks_file)
        }

    def export_locks(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """导出锁数据。

        Args:
            output_path: 输出路径（可选）

        Returns:
            锁数据字典
        """
        data = {
            "active_locks": [lock.to_dict() for lock in self.locks.values()],
            "summary": self.get_lock_summary(),
            "exported_at": datetime.now().isoformat()
        }
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True)
        
        return data


if __name__ == "__main__":
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ResourceLockManager(tmpdir)
        
        lock1 = manager.acquire_lock(
            lock_type=LockType.FILE,
            resource_path="src/components/Header.tsx",
            holder="agent_frontend_react",
            timeout_minutes=30,
            reason="实现头部组件"
        )
        print(f"获取锁: {lock1.lock_id}")
        
        summary = manager.get_lock_summary()
        print(f"锁摘要: {summary}")
        
        remaining = lock1.minutes_remaining()
        print(f"剩余时间: {remaining:.1f} 分钟")
        
        manager.release_lock(lock1.lock_id, "agent_frontend_react")
        print(f"释放锁: {lock1.lock_id}")
