"""异常处理模块。"""
import traceback
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import threading
import time


logger = logging.getLogger(__name__)


class ExceptionType(Enum):
    """异常类型枚举。"""
    RETRYABLE = "retryable"
    RECOVERABLE = "recoverable"
    FATAL = "fatal"


class ExceptionSeverity(Enum):
    """异常严重程度枚举。"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ExceptionHandlerError(Exception):
    """异常处理器异常基类。"""
    pass


class UnhandledExceptionError(ExceptionHandlerError):
    """未处理异常。"""
    pass


class RecoveryError(ExceptionHandlerError):
    """恢复异常。"""
    pass


class NetworkError(Exception):
    """网络异常。"""
    
    def __init__(self, message: str, operation: str = "unknown"):
        super().__init__(message)
        self.operation = operation
        self.timestamp = time.time()


class DiskSpaceError(Exception):
    """磁盘空间异常。"""
    
    def __init__(self, free_mb: float, required_mb: float, path: str = "/"):
        super().__init__(f"磁盘空间不足: {free_mb:.1f}MB < {required_mb}MB ({path})")
        self.free_mb = free_mb
        self.required_mb = required_mb
        self.path = path


class PermissionError(Exception):
    """权限异常。"""
    
    def __init__(self, path: str, operation: str = "access"):
        super().__init__(f"无权限访问: {path} ({operation})")
        self.path = path
        self.operation = operation


class RetryConfig:
    """重试配置。"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        timeout: int = 30
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.timeout = timeout


@dataclass
class ExceptionInfo:
    """异常信息。"""
    exception_type: ExceptionType
    severity: ExceptionSeverity
    message: str
    timestamp: str
    agent_id: str
    phase: str
    context: Dict[str, Any]
    stack_trace: str = ""
    exception_class: str = ""
    handled: bool = False
    recovery_attempts: int = 0
    last_recovery_time: Optional[str] = None


@dataclass
class CrashInfo:
    """崩溃信息。"""
    crash_id: str
    timestamp: str
    agent_id: str
    phase: str
    last_action: str
    state_version: int
    pending_tasks: List[str]
    exception_info: Optional[ExceptionInfo] = None
    recovery_status: str = "pending"
    recovery_attempts: int = 0


class NotificationChannel(Enum):
    """通知渠道枚举。"""
    LOG = "log"
    FILE = "file"
    WEBHOOK = "webhook"
    EMAIL = "email"


@dataclass
class NotificationConfig:
    """通知配置。"""
    channel: NotificationChannel
    enabled: bool = True
    webhook_url: Optional[str] = None
    email_recipients: List[str] = field(default_factory=list)
    min_severity: ExceptionSeverity = ExceptionSeverity.MEDIUM


class ExceptionHandler:
    """异常处理器。"""
    
    CRASH_LOG_DIR = "state/crash_logs"
    RECOVERY_DIR = "state/recovery"
    
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 5
    
    def __init__(self, agent_id: str, phase: str = "unknown"):
        """初始化异常处理器。"""
        self.agent_id = agent_id
        self.current_phase = phase
        self.crash_log_dir = Path(self.CRASH_LOG_DIR)
        self.recovery_dir = Path(self.RECOVERY_DIR)
        self._ensure_directories()
        
        self._exception_handlers: Dict[ExceptionType, Callable] = {}
        self._global_exception_handler: Optional[Callable] = None
        self._notification_configs: List[NotificationConfig] = []
        
        self._current_exception: Optional[ExceptionInfo] = None
        self._retry_count: int = 0
        
        self._register_default_handlers()
    
    def _ensure_directories(self) -> None:
        """确保必要目录存在。"""
        self.crash_log_dir.mkdir(parents=True, exist_ok=True)
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
    
    def _register_default_handlers(self) -> None:
        """注册默认异常处理器。"""
        self._exception_handlers[ExceptionType.RETRYABLE] = self._handle_retryable
        self._exception_handlers[ExceptionType.RECOVERABLE] = self._handle_recoverable
        self._exception_handlers[ExceptionType.FATAL] = self._handle_fatal
    
    def register_exception_handler(
        self,
        exception_type: ExceptionType,
        handler: Callable[[ExceptionInfo], Tuple[bool, str]]
    ) -> None:
        """注册异常处理器。"""
        self._exception_handlers[exception_type] = handler
        logger.info(f"已注册异常处理器: {exception_type.value}")
    
    def set_global_exception_handler(
        self,
        handler: Callable[[Exception, ExceptionInfo], None]
    ) -> None:
        """设置全局异常处理器。"""
        self._global_exception_handler = handler
    
    def add_notification_config(self, config: NotificationConfig) -> None:
        """添加通知配置。"""
        self._notification_configs.append(config)

    def configure_notifications(
        self,
        webhook_url: str = None,
        email: str = None,
        enabled: bool = True
    ) -> None:
        """配置通知。"""
        email_recipients = [email] if email else []
        channel = NotificationChannel.WEBHOOK if webhook_url else (NotificationChannel.EMAIL if email else NotificationChannel.LOG)
        config = NotificationConfig(
            channel=channel,
            enabled=enabled,
            webhook_url=webhook_url,
            email_recipients=email_recipients,
            min_severity=ExceptionSeverity.MEDIUM
        )
        self._notification_configs = [config]
        self._notification_config = config
    
    def classify_exception(self, exception: Exception) -> Tuple[ExceptionType, ExceptionSeverity]:
        """分类异常。"""
        exception_class = type(exception).__name__
        exception_message = str(exception)
        
        retryable_patterns = [
            "network", "timeout", "connection", "retry",
            "git fetch", "git pull"
        ]
        
        recoverable_patterns = [
            "state", "lock", "conflict", "version",
            "yaml", "parse"
        ]
        
        fatal_patterns = [
            "permission", "disk", "memory", "keyboardinterrupt",
            "keyboard_interrupt", "sigterm", "git not found"
        ]
        
        exception_str = f"{exception_class} {exception_message}".lower()
        
        for pattern in retryable_patterns:
            if pattern in exception_str:
                return ExceptionType.RETRYABLE, ExceptionSeverity.MEDIUM
        
        for pattern in recoverable_patterns:
            if pattern in exception_str:
                return ExceptionType.RECOVERABLE, ExceptionSeverity.HIGH
        
        for pattern in fatal_patterns:
            if pattern in exception_str:
                return ExceptionType.FATAL, ExceptionSeverity.CRITICAL
        
        if "git" in exception_str:
            return ExceptionType.RETRYABLE, ExceptionSeverity.MEDIUM
        
        return ExceptionType.RECOVERABLE, ExceptionSeverity.MEDIUM
    
    def handle_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        phase: Optional[str] = None
    ) -> Tuple[bool, str]:
        """处理异常。"""
        exception_type, severity = self.classify_exception(exception)
        
        exc_info = ExceptionInfo(
            exception_type=exception_type,
            severity=severity,
            message=str(exception),
            timestamp=datetime.now().isoformat(),
            agent_id=self.agent_id,
            phase=phase or self.current_phase,
            context=context or {},
            stack_trace=traceback.format_exc(),
            exception_class=type(exception).__name__
        )
        
        self._current_exception = exc_info
        
        if self._global_exception_handler:
            self._global_exception_handler(exception, exc_info)
        
        handler = self._exception_handlers.get(exception_type)
        if handler:
            return handler(exc_info)
        
        return False, f"未找到异常处理器: {exception_type.value}"
    
    def _handle_retryable(self, exc_info: ExceptionInfo) -> Tuple[bool, str]:
        """处理可重试异常。"""
        max_retries = self.DEFAULT_MAX_RETRIES
        
        if exc_info.recovery_attempts < max_retries:
            exc_info.recovery_attempts += 1
            delay = self.DEFAULT_RETRY_DELAY * (2 ** (exc_info.recovery_attempts - 1))
            
            logger.warning(
                f"可重试异常 (尝试 {exc_info.recovery_attempts}/{max_retries}): "
                f"{exc_info.message}, {delay}秒后重试"
            )
            
            time.sleep(delay)
            
            self._notify_exception(exc_info)
            
            return True, f"准备重试 ({exc_info.recovery_attempts}/{max_retries})"
        else:
            logger.error(f"可重试异常达到最大重试次数: {exc_info.message}")
            self._save_crash_log(exc_info)
            return False, "达到最大重试次数，需要手动干预"
    
    def _handle_recoverable(self, exc_info: ExceptionInfo) -> Tuple[bool, str]:
        """处理可恢复异常。"""
        logger.warning(f"可恢复异常: {exc_info.message}")
        
        self._save_crash_log(exc_info)
        
        recovery_success = self._attempt_recovery(exc_info)
        
        if recovery_success:
            self._notify_exception(exc_info)
            return True, "已恢复"
        
        return False, "恢复失败，需要手动干预"
    
    def _handle_fatal(self, exc_info: ExceptionInfo) -> Tuple[bool, str]:
        """处理致命异常。"""
        logger.error(f"致命异常: {exc_info.message}")
        
        self._save_crash_log(exc_info)
        
        self._save_recovery_info(exc_info)
        
        self._notify_exception(exc_info)
        
        return False, "致命异常，需要手动干预"
    
    def _attempt_recovery(self, exc_info: ExceptionInfo) -> bool:
        """尝试恢复。"""
        try:
            state_file = Path("state/project_state.yaml")
            
            if state_file.exists():
                import yaml
                with open(state_file, 'r') as f:
                    state = yaml.safe_load(f)
                
                if state and 'state_version' in state:
                    state['state_version'] += 1
                    
                    with open(state_file, 'w') as f:
                        yaml.dump(state, f)
                    
                    logger.info("状态版本已递增，恢复成功")
                    return True
            
            return True
            
        except Exception as e:
            logger.error(f"恢复尝试失败: {e}")
            return False
    
    def _save_crash_log(self, exc_info: ExceptionInfo) -> str:
        """保存崩溃日志。"""
        crash_id = f"{self.agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        crash_info = CrashInfo(
            crash_id=crash_id,
            timestamp=exc_info.timestamp,
            agent_id=exc_info.agent_id,
            phase=exc_info.phase,
            last_action=exc_info.context.get("last_action", "unknown"),
            state_version=exc_info.context.get("state_version", 0),
            pending_tasks=exc_info.context.get("pending_tasks", []),
            exception_info=exc_info
        )
        
        crash_file = self.crash_log_dir / f"{crash_id}.json"
        
        with open(crash_file, 'w', encoding='utf-8') as f:
            json.dump({
                "crash_id": crash_info.crash_id,
                "timestamp": crash_info.timestamp,
                "agent_id": crash_info.agent_id,
                "phase": crash_info.phase,
                "last_action": crash_info.last_action,
                "state_version": crash_info.state_version,
                "pending_tasks": crash_info.pending_tasks,
                "exception": {
                    "type": exc_info.exception_type.value,
                    "severity": exc_info.severity.value,
                    "message": exc_info.message,
                    "class": exc_info.exception_class,
                    "stack_trace": exc_info.stack_trace,
                    "recovery_attempts": exc_info.recovery_attempts
                },
                "recovery_status": crash_info.recovery_status,
                "recovery_attempts": crash_info.recovery_attempts
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"崩溃日志已保存: {crash_file}")
        
        return crash_id
    
    def _save_recovery_info(self, exc_info: ExceptionInfo) -> None:
        """保存恢复信息。"""
        recovery_info = {
            "agent_id": self.agent_id,
            "phase": exc_info.phase,
            "timestamp": exc_info.timestamp,
            "exception": {
                "type": exc_info.exception_type.value,
                "message": exc_info.message
            },
            "required_action": "manual_intervention",
            "last_state": exc_info.context.get("state", {})
        }
        
        recovery_file = self.recovery_dir / f"{self.agent_id}_recovery.json"
        
        with open(recovery_file, 'w', encoding='utf-8') as f:
            json.dump(recovery_info, f, ensure_ascii=False, indent=2)
        
        logger.info(f"恢复信息已保存: {recovery_file}")
    
    def _notify_exception(self, exc_info: ExceptionInfo) -> None:
        """发送异常通知。"""
        for config in self._notification_configs:
            if not config.enabled:
                continue
            
            if exc_info.severity.value < config.min_severity.value:
                continue
            
            try:
                if config.channel == NotificationChannel.LOG:
                    self._notify_log(exc_info)
                elif config.channel == NotificationChannel.FILE:
                    self._notify_file(exc_info, config)
                elif config.channel == NotificationChannel.WEBHOOK:
                    self._notify_webhook(exc_info, config)
            except Exception as e:
                logger.error(f"通知发送失败: {e}")
    
    def _notify_log(self, exc_info: ExceptionInfo) -> None:
        """日志通知。"""
        log_method = logger.error if exc_info.severity == ExceptionSeverity.CRITICAL else logger.warning
        log_method(
            f"异常通知 - 类型: {exc_info.exception_type.value}, "
            f"严重程度: {exc_info.severity.name}, "
            f"消息: {exc_info.message}"
        )
    
    def _notify_file(self, exc_info: ExceptionInfo, config: NotificationConfig) -> None:
        """文件通知。"""
        notification_file = Path("state/notifications.log")
        with open(notification_file, 'a', encoding='utf-8') as f:
            f.write(
                f"[{exc_info.timestamp}] "
                f"[{exc_info.agent_id}] "
                f"[{exc_info.exception_type.value}] "
                f"{exc_info.message}\n"
            )
    
    def _notify_webhook(self, exc_info: ExceptionInfo, config: NotificationConfig) -> None:
        """Webhook通知。"""
        import requests
        
        if not config.webhook_url:
            return
        
        payload = {
            "event": "exception",
            "agent_id": exc_info.agent_id,
            "phase": exc_info.phase,
            "exception_type": exc_info.exception_type.value,
            "severity": exc_info.severity.name,
            "message": exc_info.message,
            "timestamp": exc_info.timestamp
        }
        
        try:
            requests.post(config.webhook_url, json=payload, timeout=5)
        except Exception as e:
            logger.error(f"Webhook通知失败: {e}")
    
    def save_crash_context(self, state_version: int, pending_tasks: List[str]) -> None:
        """保存崩溃上下文。"""
        if self._current_exception:
            self._current_exception.context["state_version"] = state_version
            self._current_exception.context["pending_tasks"] = pending_tasks
    
    def get_crash_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取崩溃历史。"""
        crash_files = sorted(
            self.crash_log_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )[:limit]
        
        crashes = []
        for crash_file in crash_files:
            try:
                with open(crash_file, 'r', encoding='utf-8') as f:
                    crash_data = json.load(f)
                    crashes.append(crash_data)
            except Exception as e:
                logger.warning(f"读取崩溃日志失败: {crash_file}, {e}")
        
        return crashes
    
    def clear_old_crashes(self, days: int = 7) -> int:
        """清理旧崩溃日志。"""
        import time
        
        cutoff = time.time() - (days * 24 * 60 * 60)
        removed = 0
        
        for crash_file in self.crash_log_dir.glob("*.json"):
            if crash_file.stat().st_mtime < cutoff:
                crash_file.unlink()
                removed += 1
        
        logger.info(f"已清理 {removed} 个旧崩溃日志")
        return removed
    
    def get_exception_summary(self) -> Dict[str, Any]:
        """获取异常处理器摘要。"""
        return {
            "agent_id": self.agent_id,
            "current_phase": self.current_phase,
            "registered_handlers": list(self._exception_handlers.keys()),
            "notification_channels": [c.channel.value for c in self._notification_configs],
            "current_exception": {
                "type": self._current_exception.exception_type.value if self._current_exception else None,
                "message": self._current_exception.message if self._current_exception else None,
                "severity": self._current_exception.severity.name if self._current_exception else None
            } if self._current_exception else None,
            "retry_count": self._retry_count,
            "crash_logs_count": len(list(self.crash_log_dir.glob("*.json")))
        }
    
    def set_phase(self, phase: str) -> None:
        """设置当前阶段。"""
        self.current_phase = phase
    
    def reset(self) -> None:
        """重置异常处理器。"""
        self._current_exception = None
        self._retry_count = 0
    
    def __enter__(self):
        """上下文管理器入口。"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口。"""
        if exc_type:
            self.handle_exception(exc_val)
        return False


class DiskSpaceChecker:
    """磁盘空间检查器。"""
    
    def __init__(self, min_free_mb: int = 100, check_paths: list = None):
        """初始化。
        
        Args:
            min_free_mb: 最小可用空间 (MB)，默认 100MB
            check_paths: 检查的路径列表
        """
        self.min_free_mb = min_free_mb
        self.check_paths = check_paths or ["/"]
    
    def check(self, path: str = None) -> bool:
        """检查磁盘空间。
        
        Args:
            path: 要检查的路径，默认检查第一个配置路径
            
        Returns:
            空间是否充足
        """
        check_path = path or self.check_paths[0]
        
        try:
            stat = shutil.disk_usage(check_path)
            free_mb = stat.free / (1024 * 1024)
            
            if free_mb < self.min_free_mb:
                logger.warning(
                    f"磁盘空间不足: {free_mb:.1f}MB "
                    f"(阈值: {self.min_free_mb}MB, 路径: {check_path})"
                )
                return False
            
            logger.debug(f"磁盘空间充足: {free_mb:.1f}MB")
            return True
        
        except OSError as e:
            logger.error(f"检查磁盘空间失败: {e}")
            return True
    
    def check_all(self) -> bool:
        """检查所有配置的路径。"""
        for path in self.check_paths:
            if not self.check(path):
                return False
        return True
    
    def get_free_space(self, path: str = None) -> float:
        """获取指定路径的可用空间 (MB)。"""
        check_path = path or self.check_paths[0]
        
        try:
            stat = shutil.disk_usage(check_path)
            return stat.free / (1024 * 1024)
        except OSError:
            return -1


class PermissionChecker:
    """权限检查器。"""
    
    def __init__(self):
        """初始化。"""
        self.checked_paths = {}
    
    def check_read(self, path: str) -> bool:
        """检查读权限。"""
        try:
            if not os.path.exists(path):
                self.checked_paths[path] = ("read", False)
                return False
            if os.path.isfile(path):
                with open(path, 'r'):
                    pass
            else:
                os.listdir(path)
            self.checked_paths[path] = ("read", True)
            return True
        except (PermissionError, OSError) as e:
            logger.error(f"无读权限: {path} - {e}")
            self.checked_paths[path] = ("read", False)
            return False

    def check_write(self, path: str) -> bool:
        """检查写权限。"""
        try:
            if os.path.isfile(path):
                parent_dir = os.path.dirname(path)
            elif os.path.isdir(path):
                parent_dir = path
            else:
                parent_dir = os.path.dirname(path)
            if not parent_dir or not os.path.exists(parent_dir):
                self.checked_paths[path] = ("write", False)
                return False
            test_file = os.path.join(parent_dir, ".write_test")
            with open(test_file, 'w') as f:
                f.write("")
            os.remove(test_file)
            self.checked_paths[path] = ("write", True)
            return True
        except (PermissionError, OSError) as e:
            logger.error(f"无写权限: {path} - {e}")
            self.checked_paths[path] = ("write", False)
            return False
    
    def check_execute(self, path: str) -> bool:
        """检查执行权限。"""
        try:
            os.access(path, os.X_OK)
            self.checked_paths[path] = ("execute", True)
            return True
        except OSError as e:
            logger.error(f"无执行权限: {path} - {e}")
            self.checked_paths[path] = ("execute", False)
            return False
    
    def check_all(self, path: str) -> bool:
        """检查所有权限。"""
        if os.path.isfile(path):
            return self.check_read(path) and self.check_execute(path)
        else:
            return self.check_read(path) and self.check_write(path)
    
    def get_checked_paths(self) -> dict:
        """获取已检查的路径结果。"""
        return self.checked_paths.copy()


def with_retry(config: RetryConfig = None):
    """装饰器：添加重试逻辑。
    
    Args:
        config: 重试配置，默认使用 RetryConfig()
    
    Example:
        @with_retry(RetryConfig(max_retries=3, initial_delay=1.0))
        def git_fetch():
            # Git 操作
            pass
    """
    from functools import wraps
    
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except NetworkError as e:
                    last_exception = e
                    
                    if attempt < config.max_retries:
                        delay = min(
                            config.initial_delay * (config.exponential_base ** attempt),
                            config.max_delay
                        )
                        
                        logger.warning(
                            f"网络操作失败，{delay:.1f}秒后重试 "
                            f"(尝试 {attempt + 1}/{config.max_retries + 1}): {e}"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"网络操作最终失败: {e}")
                        raise
            
            raise last_exception
        
        return wrapper
    return decorator
