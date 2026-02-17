"""
TODO编号生成器

提供Agent独立的TODO编号生成功能，支持多Agent编号格式。
"""

import os
import re
import fcntl
from pathlib import Path
from typing import Optional, Dict
import yaml
import logging

logger = logging.getLogger(__name__)


class TodoIdGenerator:
    """Agent独立TODO编号生成器，支持多Agent编号格式"""

    DEFAULT_COUNTERS = {
        "1to1": 0,
        "1to2": 0,
        "2to1": 0,
        "2to2": 0,
    }

    def __init__(self, agent_id: Optional[str] = None, counter_file: Optional[str] = None, state_file: str = "state/project_state.yaml"):
        """
        Args:
            agent_id: Agent标识 ("1" 或 "2")，新格式不需要
            counter_file: 旧格式计数器文件路径（兼容用）
            state_file: 新格式状态文件路径
        """
        self.agent_id = agent_id
        self.counter_file = Path(counter_file) if counter_file else None
        self.state_file = state_file or "state/project_state.yaml"
        self.lock_file = "state/.todo_id.lock"
        
        # 新格式初始化
        self._ensure_state_file()

    def _ensure_state_file(self):
        """确保状态文件存在并包含计数器"""
        state = self._load_state()
        if "todo_id_counters" not in state:
            state["todo_id_counters"] = self.DEFAULT_COUNTERS.copy()
            self._save_state(state)

    def _load_state(self) -> Dict:
        """加载状态"""
        if not os.path.exists(self.state_file):
            return {"todo_id_counters": self.DEFAULT_COUNTERS.copy()}
        try:
            with open(self.state_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError:
            return {"todo_id_counters": self.DEFAULT_COUNTERS.copy()}

    def _save_state(self, state: Dict):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            yaml.safe_dump(state, f)

    def generate(self, creator: Optional[str] = None, receiver: Optional[str] = None) -> str:
        """
        生成TODO编号（新格式）
        
        Args:
            creator: 创建者Agent ID (如 "1", "2")
            receiver: 接收者Agent ID (如 "1", "2")
        
        Returns:
            TODO编号 (如 "TODO-1to2-001")
        """
        # 如果没有传creator/receiver，使用旧格式兼容
        if creator is None and receiver is None:
            return self._generate_legacy()
        
        key = f"{creator}to{receiver}"
        
        os.makedirs(os.path.dirname(self.lock_file), exist_ok=True)
        with open(self.lock_file, 'a') as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                state = self._load_state()
                counters = state.get("todo_id_counters", self.DEFAULT_COUNTERS)
                
                if key not in counters:
                    counters[key] = 0
                
                counters[key] += 1
                seq = counters[key]
                
                state["todo_id_counters"] = counters
                self._save_state(state)
                
                return f"TODO-{creator}to{receiver}-{seq:03d}"
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    def _generate_legacy(self) -> str:
        """旧格式生成（兼容）"""
        if not self.counter_file:
            self.counter_file = Path(f"state/.todo_counter_{self.agent_id}.yaml")
        
        counter = self._load_counter()
        counter += 1
        self._save_counter(counter)
        return f"TODO-{self.agent_id}-{counter:03d}"

    def _load_counter(self) -> int:
        """加载旧格式计数器"""
        try:
            if self.counter_file and self.counter_file.exists():
                with open(self.counter_file) as f:
                    data = yaml.safe_load(f)
                    return data.get("counter", 0)
            return 0
        except Exception as e:
            logger.error(f"加载计数器失败: {e}")
            return 0

    def _save_counter(self, counter: int):
        """保存旧格式计数器"""
        if not self.counter_file:
            return
        try:
            with open(self.counter_file, "w") as f:
                yaml.dump({
                    "counter": counter,
                    "agent_id": self.agent_id
                }, f)
        except Exception as e:
            logger.error(f"保存计数器失败: {e}")
            raise

    def parse(self, todo_id: str) -> Optional[Dict]:
        """
        解析TODO编号
        
        Args:
            todo_id: TODO编号
        
        Returns:
            dict{creator, receiver, seq, is_legacy} 或 None
        """
        # 新格式: TODO-1to2-001
        match = re.match(r'TODO-(\d+)to(\d+)-(\d+)', todo_id)
        if match:
            return {
                "creator": match.group(1),
                "receiver": match.group(2),
                "seq": int(match.group(3)),
                "is_legacy": False
            }
        
        # 旧格式: TODO-1-001
        match = re.match(r'TODO-(\d+)-(\d+)', todo_id)
        if match:
            return {
                "creator": match.group(1),
                "receiver": match.group(1),  # 旧格式视为给自己
                "seq": int(match.group(2)),
                "is_legacy": True
            }
        
        return None

    def is_legacy_format(self, todo_id: str) -> bool:
        """判断是否旧格式"""
        parsed = self.parse(todo_id)
        return parsed.get("is_legacy", False) if parsed else False

    def get_next_number(self) -> int:
        """获取下一个编号（旧格式兼容）"""
        return self._load_counter() + 1

    def get_current_number(self) -> int:
        """获取当前编号（旧格式兼容）"""
        return self._load_counter()


class TodoIdConflictError(Exception):
    """TODO编号冲突异常"""

    def __init__(self, message: str, existing_id: str):
        super().__init__(message)
        self.existing_id = existing_id
