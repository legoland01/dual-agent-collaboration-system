import os
import time
import signal
import logging
import json
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
        
        # 检查触发文件
        self._check_trigger_files()
    
    def _check_trigger_files(self):
        """检查并处理触发文件"""
        import time
        state_dir = Path("state")
        if not state_dir.exists():
            return
        
        trigger_files = list(state_dir.glob("trigger_*.json"))
        if not trigger_files:
            return
        
        # 按修改时间排序，处理最早的
        trigger_files.sort(key=lambda f: f.stat().st_mtime)
        
        for trigger_file in trigger_files:
            try:
                with open(trigger_file, 'r') as f:
                    trigger_data = json.load(f)
                
                action = trigger_data.get("action")
                agent_id = trigger_data.get("agent_id")
                
                if action == "notify_todo":
                    logger.info(f"收到来自PM-Agent的触发: agent={agent_id}")
                    # TODO: 暂时注释掉自动发送查看TODO，避免干扰其他窗口
                    # 需要解决精确发送窗口问题后才能启用
                    # self._activate_iterm2_notify(agent_id)
                    pass
                    # 等待足够长让OpenCode处理
                    time.sleep(0.3)
                
                # 处理完成后删除触发文件
                trigger_file.unlink()
                logger.info(f"触发文件已处理: {trigger_file.name}")
                
            except Exception as e:
                logger.error(f"处理触发文件失败: {e}")
    
    def _activate_iterm2_notify(self, target_agent: str = "agent2"):
        """通过OpenCode API发送查看TODO - 发两次确保提交"""
        import requests
        import json
        import os
        import time
        from pathlib import Path
        
        project_path = os.getcwd()
        
        logger.info(f"目标agent: {target_agent}")
        
        # 查找最新的session（按时间倒序）
        import sqlite3
        session_id = None
        db_path = Path.home() / ".local/share/opencode/opencode.db"
        if db_path.exists():
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM session WHERE directory = ? ORDER BY time_updated DESC LIMIT 1",
                (project_path,)
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                session_id = row[0]
                logger.info(f"找到最新session: {session_id}")
        
        if not session_id:
            logger.error("找不到session ID")
            return
        
        # 遍历所有端口尝试，找到能处理目标session的端口
        import subprocess
        result = subprocess.run(['lsof', '-i', '-n'], capture_output=True, text=True)
        ports = set()
        for line in result.stdout.split('\n'):
            if 'opencode' in line and 'LISTEN' in line:
                for part in line.split():
                    if ':' in part:
                        try:
                            port = int(part.split(':')[-1])
                            if port > 1000:
                                ports.add(str(port))
                        except:
                            pass
        
        if not ports:
            logger.error("找不到OpenCode端口")
            return
        
        logger.info(f"尝试端口: {ports}")
        
        # 找到项目下的所有session
        session_ids = []
        if db_path.exists():
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM session WHERE directory = ? ORDER BY time_updated DESC LIMIT 10",
                (project_path,)
            )
            session_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
        
        logger.info(f"尝试sessions: {session_ids}")
        
        # 尝试每个端口和session组合，用异步发送不等待响应
        success = False
        for port in ports:
            for sid in session_ids:
                api_url = f"http://127.0.0.1:{port}/session/{sid}/message"
                
                payload1 = {"parts": [{"type": "text", "text": "查看TODO"}]}
                payload2 = {"parts": [{"type": "text", "text": " "}]}
                
                try:
                    # 异步发送，不等待响应
                    import threading
                    def send():
                        try:
                            requests.post(api_url, json=payload1, timeout=1)
                            time.sleep(0.2)
                            requests.post(api_url, json=payload2, timeout=1)
                        except:
                            pass
                    
                    thread = threading.Thread(target=send)
                    thread.daemon = True
                    thread.start()
                    
                    logger.info(f"已发送: port={port}, session={sid}")
                    success = True
                    break
                except Exception as e:
                    pass
            if success:
                break
        
        if not success:
            logger.error("所有组合都失败")
    
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
