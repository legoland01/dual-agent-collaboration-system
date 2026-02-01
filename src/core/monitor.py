"""监控告警模块。

功能：
1. 资源监控 - CPU、内存、磁盘使用率
2. 告警机制 - 基于阈值的告警通知
3. 状态报告 - 生成系统状态报告
"""
import time
import logging
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import psutil


logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """告警级别。"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class Alert:
    """告警信息。"""
    level: AlertLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    metric: str = ""
    value: float = 0.0
    threshold: float = 0.0
    
    def __str__(self):
        return f"[{self.level.value}] {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {self.message}"


class ResourceMonitor:
    """资源监控器。"""
    
    def __init__(
        self,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 85.0,
        disk_threshold: float = 90.0,
        sample_interval: int = 10
    ):
        """初始化。
        
        Args:
            cpu_threshold: CPU 使用率阈值 (%)
            memory_threshold: 内存使用率阈值 (%)
            disk_threshold: 磁盘使用率阈值 (%)
            sample_interval: 采样间隔 (秒)
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.sample_interval = sample_interval
        
        self.alerts: List[Alert] = []
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        self.stats = {
            "cpu_samples": [],
            "memory_samples": [],
            "disk_samples": [],
            "restart_count": 0,
            "git_operations": 0,
            "exception_count": 0
        }
        
        self._stop_event = threading.Event()
        self._monitor_thread: Optional[threading.Thread] = None
        self._cpu_percent = psutil.cpu_percent(interval=None)
    
    def get_current_stats(self) -> Dict:
        """获取当前资源使用情况。"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "cpu_count": psutil.cpu_count(),
            "memory_used_gb": psutil.virtual_memory().used / (1024**3),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "boot_time": psutil.boot_time()
        }
    
    def check_thresholds(self) -> List[Alert]:
        """检查阈值，返回告警列表。"""
        alerts = []
        stats = self.get_current_stats()
        
        if stats["cpu_percent"] > self.cpu_threshold:
            alert = Alert(
                level=AlertLevel.WARNING,
                message=f"CPU 使用率 {stats['cpu_percent']:.1f}% (阈值: {self.cpu_threshold}%)",
                metric="cpu_percent",
                value=stats["cpu_percent"],
                threshold=self.cpu_threshold
            )
            alerts.append(alert)
        
        if stats["memory_percent"] > self.memory_threshold:
            alert = Alert(
                level=AlertLevel.WARNING,
                message=f"内存使用率 {stats['memory_percent']:.1f}% (阈值: {self.memory_threshold}%)",
                metric="memory_percent",
                value=stats["memory_percent"],
                threshold=self.memory_threshold
            )
            alerts.append(alert)
        
        if stats["disk_percent"] > self.disk_threshold:
            alert = Alert(
                level=AlertLevel.WARNING,
                message=f"磁盘使用率 {stats['disk_percent']:.1f}% (阈值: {self.disk_threshold}%)",
                metric="disk_percent",
                value=stats["disk_percent"],
                threshold=self.disk_threshold
            )
            alerts.append(alert)
        
        self.alerts.extend(alerts)
        
        for alert in alerts:
            self._notify_alert(alert)
        
        return alerts
    
    def register_alert_callback(self, callback: Callable[[Alert], None]):
        """注册告警回调。"""
        self.alert_callbacks.append(callback)
    
    def _notify_alert(self, alert: Alert):
        """发送告警通知。"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"告警回调执行失败: {e}")
    
    def get_recent_alerts(self, count: int = 10) -> List[Alert]:
        """获取最近告警。"""
        return self.alerts[-count:]
    
    def clear_old_alerts(self, hours: int = 24) -> int:
        """清理旧告警。"""
        cutoff = datetime.now() - timedelta(hours=hours)
        old_count = len(self.alerts)
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff]
        return old_count - len(self.alerts)
    
    def get_status_report(self) -> Dict:
        """生成状态报告。"""
        current = self.get_current_stats()
        
        status = "healthy"
        if current["cpu_percent"] > self.cpu_threshold:
            status = "warning"
        if current["memory_percent"] > self.memory_threshold:
            status = "warning"
        if current["disk_percent"] > self.disk_threshold:
            status = "critical"
        
        return {
            "status": status,
            "resources": {
                "cpu": f"{current['cpu_percent']:.1f}%",
                "memory": f"{current['memory_percent']:.1f}%",
                "disk": f"{current['disk_percent']:.1f}%"
            },
            "stats": {
                "restart_count": self.stats["restart_count"],
                "git_operations": self.stats["git_operations"],
                "exception_count": self.stats["exception_count"]
            },
            "recent_alerts": len(self.alerts[-10:]),
            "alerts": [str(a) for a in self.alerts[-5:]]
        }
    
    def increment_restart_count(self):
        """增加重启计数。"""
        self.stats["restart_count"] += 1
    
    def increment_git_operations(self):
        """增加 Git 操作计数。"""
        self.stats["git_operations"] += 1
    
    def increment_exception_count(self):
        """增加异常计数。"""
        self.stats["exception_count"] += 1
    
    def start_monitoring(self):
        """开始监控循环。"""
        if self._monitor_thread is not None and self._monitor_thread.is_alive():
            return
        
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("资源监控已启动")
    
    def stop_monitoring(self):
        """停止监控循环。"""
        self._stop_event.set()
        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None
        logger.info("资源监控已停止")
    
    def _monitor_loop(self):
        """监控循环。"""
        while not self._stop_event.is_set():
            try:
                self.check_thresholds()
            except Exception as e:
                logger.error(f"监控检查失败: {e}")
            
            self._stop_event.wait(timeout=self.sample_interval)
    
    def get_cpu_percent(self) -> float:
        """获取 CPU 使用率（非阻塞）。"""
        return psutil.cpu_percent(interval=None)


def get_system_info() -> Dict:
    """获取系统信息。"""
    return {
        "cpu_count": psutil.cpu_count(),
        "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
        "memory": {
            "total_gb": psutil.virtual_memory().total / (1024**3),
            "available_gb": psutil.virtual_memory().available / (1024**3),
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total_gb": psutil.disk_usage('/').total / (1024**3),
            "free_gb": psutil.disk_usage('/').free / (1024**3),
            "percent": psutil.disk_usage('/').percent
        },
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    monitor = ResourceMonitor(cpu_threshold=80.0, memory_threshold=85.0, disk_threshold=90.0)
    
    print("系统信息:")
    print(get_system_info())
    
    print("\n当前状态:")
    print(monitor.get_current_stats())
    
    print("\n状态报告:")
    print(monitor.get_status_report())
    
    print("\n阈值检查:")
    alerts = monitor.check_thresholds()
    for alert in alerts:
        print(f"  {alert}")
