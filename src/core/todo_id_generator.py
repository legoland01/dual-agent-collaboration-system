"""
TODO编号生成器

提供Agent独立的TODO编号生成功能。
"""

from pathlib import Path
from typing import Optional
import yaml
import logging

logger = logging.getLogger(__name__)


class TodoIdGenerator:
    """Agent独立TODO编号生成器"""

    def __init__(self, agent_id: str, counter_file: Optional[str] = None):
        """
        Args:
            agent_id: Agent标识 ("1" 或 "2")
            counter_file: 计数器文件路径，为None则使用默认路径
        """
        self.agent_id = agent_id
        if counter_file:
            self.counter_file = Path(counter_file)
        else:
            self.counter_file = Path(f"state/.todo_counter_{agent_id}.yaml")
        self.counter = self._load_counter()

    def _load_counter(self) -> int:
        """加载计数器"""
        try:
            if self.counter_file.exists():
                with open(self.counter_file) as f:
                    data = yaml.safe_load(f)
                    return data.get("counter", 0)
            return 0
        except Exception as e:
            logger.error(f"加载计数器失败: {e}")
            return 0

    def _save_counter(self):
        """保存计数器"""
        try:
            with open(self.counter_file, "w") as f:
                yaml.dump({
                    "counter": self.counter,
                    "agent_id": self.agent_id
                }, f)
        except Exception as e:
            logger.error(f"保存计数器失败: {e}")
            raise

    def generate(self) -> str:
        """
        生成TODO编号

        Returns:
            TODO-1-001 或 TODO-2-001 格式
        """
        self.counter += 1
        self._save_counter()
        return f"TODO-{self.agent_id}-{self.counter:03d}"

    def get_next_number(self) -> int:
        """获取下一个编号"""
        return self.counter + 1

    def get_current_number(self) -> int:
        """获取当前编号"""
        return self.counter


class TodoIdConflictError(Exception):
    """TODO编号冲突异常"""

    def __init__(self, message: str, existing_id: str):
        super().__init__(message)
        self.existing_id = existing_id
