"""
状态更新器

更新 project_state.yaml 中的部署状态
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
import yaml
import logging

logger = logging.getLogger(__name__)


class StateUpdateError(Exception):
    """状态更新异常"""
    pass


class StateUpdater:
    """状态更新器"""

    def __init__(self, state_file: str = "state/project_state.yaml"):
        """
        Args:
            state_file: 状态文件路径
        """
        self.state_file = Path(state_file)

    def update_deployment_status(self, version: str,
                                 pypi_url: str,
                                 git_tag: str,
                                 agent_id: str = "2",
                                 steps: list = None) -> bool:
        """
        更新部署状态

        Args:
            version: 版本号
            pypi_url: PyPI URL
            git_tag: Git标签
            agent_id: 执行部署的Agent ID
            steps: 各步骤状态列表

        Returns:
            是否更新成功
        """
        try:
            state_data = self._read_state()

            version_key = f"v{version}" if not version.startswith("v") else version

            if version_key not in state_data:
                state_data[version_key] = {}

            state_data[version_key]["deployment"] = {
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat() + "Z",
                "version": version,
                "git_tag": git_tag,
                "pypi_url": pypi_url,
                "pypi_version": version,
                "agent_id": agent_id,
                "steps": steps or []
            }

            self._write_state(state_data)

            logger.info(f"部署状态已更新: v{version}")
            return True

        except Exception as e:
            logger.error(f"更新部署状态失败: {e}")
            raise StateUpdateError(f"更新状态失败: {e}")

    def update_deployment_failed(self, version: str,
                                  error: str,
                                  agent_id: str = "2",
                                  steps: list = None) -> bool:
        """
        更新部署失败状态

        Args:
            version: 版本号
            error: 错误信息
            agent_id: 执行部署的Agent ID
            steps: 各步骤状态列表

        Returns:
            是否更新成功
        """
        try:
            state_data = self._read_state()

            version_key = f"v{version}" if not version.startswith("v") else version

            if version_key not in state_data:
                state_data[version_key] = {}

            state_data[version_key]["deployment"] = {
                "status": "failed",
                "failed_at": datetime.utcnow().isoformat() + "Z",
                "version": version,
                "error": error,
                "agent_id": agent_id,
                "steps": steps or []
            }

            self._write_state(state_data)

            logger.info(f"部署失败状态已更新: v{version}")
            return True

        except Exception as e:
            logger.error(f"更新失败状态失败: {e}")
            raise StateUpdateError(f"更新状态失败: {e}")

    def read_state(self) -> dict:
        """
        读取当前状态

        Returns:
            状态数据
        """
        return self._read_state()

    def get_version_status(self, version: str) -> Optional[dict]:
        """
        获取特定版本的部署状态

        Args:
            version: 版本号

        Returns:
            部署状态字典
        """
        state_data = self._read_state()
        version_key = f"v{version}" if not version.startswith("v") else version
        return state_data.get(version_key, {}).get("deployment")

    def _read_state(self) -> dict:
        """读取状态文件"""
        if not self.state_file.exists():
            logger.warning(f"状态文件不存在: {self.state_file}")
            return {}

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"读取状态文件失败: {e}")
            return {}

    def _write_state(self, data: dict):
        """写入状态文件"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        logger.info(f"状态文件已更新: {self.state_file}")


if __name__ == "__main__":
    updater = StateUpdater()

    steps = [
        {"step": "doc_check", "status": "passed"},
        {"step": "version_update", "status": "passed"},
        {"step": "build", "status": "passed"},
        {"step": "pypi_upload", "status": "passed"},
        {"step": "git_push", "status": "passed"},
        {"step": "verify", "status": "passed"}
    ]

    try:
        success = updater.update_deployment_status(
            version="2.2.12",
            pypi_url="https://pypi.org/project/opencode-collaboration/2.2.12/",
            git_tag="v2.2.12",
            agent_id="2",
            steps=steps
        )
        print(f"状态更新结果: {success}")

        status = updater.get_version_status("2.2.12")
        print(f"版本状态: {status}")

    except StateUpdateError as e:
        print(f"错误: {e}")
