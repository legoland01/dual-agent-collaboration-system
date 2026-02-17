import os
import time
import signal
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DaemonError(Exception):
    """守护进程错误"""
    pass


class AgentListenerService:
    """监听进程服务"""
    
    MAX_RESTART_ATTEMPTS = 5
    RESTART_DELAY_SECONDS = 10
    
    def __init__(self, storage, interval: int = 5):
        self.storage = storage
        self.interval = interval
        self._daemon_process = None
        self._restart_count = 0
        self._should_stop = False
        self._pid_file = "state/listener.pid"
    
    def _ensure_state_dir(self):
        """确保state目录存在"""
        Path("state").mkdir(parents=True, exist_ok=True)
    
    def _save_pid(self, pid: int):
        """保存PID到文件"""
        self._ensure_state_dir()
        with open(self._pid_file, 'w') as f:
            f.write(str(pid))
        logger.info(f"PID已保存: {pid}")
    
    def _load_pid(self) -> Optional[int]:
        """从文件加载PID"""
        if os.path.exists(self._pid_file):
            with open(self._pid_file, 'r') as f:
                return int(f.read().strip())
        return None
    
    def _remove_pid_file(self):
        """删除PID文件"""
        if os.path.exists(self._pid_file):
            os.remove(self._pid_file)
    
    def _is_running(self, pid: int) -> bool:
        """检查进程是否运行"""
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    
    def start_daemon(self, interval: Optional[int] = None) -> bool:
        """
        启动守护进程
        Returns: success
        """
        if interval is not None:
            self.interval = interval
        
        # 检查是否已运行
        existing_pid = self._load_pid()
        if existing_pid and self._is_running(existing_pid):
            logger.warning(f"监听进程已在运行，PID: {existing_pid}")
            return False
        
        try:
            # 创建守护进程
            pid = os.fork()
            if pid > 0:
                # 父进程返回
                self._save_pid(pid)
                logger.info(f"守护进程已启动，PID: {pid}")
                return True
            
            # 子进程成为守护进程
            os.setsid()
            os.chdir("/")
            os.umask(0)
            
            # 运行主循环
            self._run_polling_loop()
            
            return True  # 子进程正常退出
        except Exception as e:
            logger.error(f"启动守护进程失败: {e}")
            return False
    
    def _run_polling_loop(self):
        """运行轮询循环"""
        while not self._should_stop:
            try:
                self._check_new_todos()
            except Exception as e:
                logger.error(f"轮询出错: {e}")
                self._handle_crash(e)
            
            time.sleep(self.interval)
    
    def _check_new_todos(self):
        """检查新TODO"""
        # 查找未读的TODO
        unread = self.storage.list(unread_only=True)
        if unread:
            logger.info(f"发现 {len(unread)} 个未读TODO")
            # 这里可以触发通知
            for todo in unread:
                logger.debug(f"新TODO: {todo.get('id')} - {todo.get('content')[:30]}")
    
    def _handle_crash(self, error: Exception):
        """处理进程崩溃"""
        self._restart_count += 1
        
        if self._restart_count <= self.MAX_RESTART_ATTEMPTS:
            logger.warning(
                f"进程崩溃，{self.RESTART_DELAY_SECONDS}秒后重启 "
                f"({self._restart_count}/{self.MAX_RESTART_ATTEMPTS})"
            )
            time.sleep(self.RESTART_DELAY_SECONDS)
        else:
            logger.error(
                f"超过最大重启次数 ({self.MAX_RESTART_ATTEMPTS})，放弃重启"
            )
            self._send_alert()
            self._should_stop = True
    
    def _send_alert(self):
        """发送告警"""
        logger.error("监听进程已停止，请检查日志")
    
    def stop(self) -> bool:
        """
        停止监听
        Returns: success
        """
        pid = self._load_pid()
        if not pid:
            logger.warning("PID文件不存在")
            return False
        
        if not self._is_running(pid):
            logger.warning(f"进程 {pid} 未运行")
            self._remove_pid_file()
            return False
        
        try:
            os.kill(pid, signal.SIGTERM)
            self._remove_pid_file()
            logger.info(f"监听进程已停止，PID: {pid}")
            return True
        except OSError as e:
            logger.error(f"停止进程失败: {e}")
            return False
    
    def check_status(self) -> dict:
        """
        检查监听状态
        Returns: {running: bool, pid: int|None, interval: int}
        """
        pid = self._load_pid()
        running = pid and self._is_running(pid)
        
        return {
            "running": running,
            "pid": pid,
            "interval": self.interval,
            "restart_count": self._restart_count
        }
    
    def restart(self) -> bool:
        """重启守护进程"""
        self.stop()
        time.sleep(1)
        return self.start_daemon()
