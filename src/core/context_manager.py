from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
import yaml
import os


@dataclass
class ProjectContext:
    """项目上下文"""
    project: str
    path: str
    agent: int
    version: str = "2.2.3"
    created_at: Optional[str] = None
    last_updated: Optional[str] = None


class ContextError(Exception):
    """上下文错误"""
    pass


class ContextNotFoundError(ContextError):
    """上下文文件未找到"""
    pass


class ContextParseError(ContextError):
    """上下文文件解析错误"""
    pass


class InvalidContextError(ContextError):
    """上下文内容无效"""
    pass


class ContextManager:
    """上下文管理器"""

    CONFIG_FILENAME = ".oc-collab.yaml"

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()

    def find_config_file(self, start_path: Optional[Path] = None) -> Optional[Path]:
        """
        向上查找 .oc-collab.yaml 文件

        Args:
            start_path: 起始路径，默认为当前目录

        Returns:
            找到的配置文件路径，未找到返回 None
        """
        current = start_path or self.project_path

        for parent in [current] + list(current.parents):
            config_path = parent / self.CONFIG_FILENAME
            if config_path.exists() and config_path.is_file():
                return config_path

            if (parent / ".git").exists():
                break
            if (parent / "pyproject.toml").exists():
                break

        return None

    def load_context(self, config_path: Optional[Path] = None) -> ProjectContext:
        """
        加载项目上下文

        Args:
            config_path: 配置文件路径，为空则自动查找

        Returns:
            ProjectContext 对象

        Raises:
            ContextNotFoundError: 未找到配置文件
            ContextParseError: YAML 解析失败
            InvalidContextError: 必要字段缺失
        """
        if config_path is None:
            config_path = self.find_config_file()
            if config_path is None:
                raise ContextNotFoundError(
                    f"未找到 {self.CONFIG_FILENAME} 文件。"
                    f"请先运行 'oc-collab init' 初始化项目。"
                )

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ContextParseError(
                f"解析 {self.CONFIG_FILENAME} 失败: {str(e)}"
            )

        if data is None:
            raise InvalidContextError(
                f"{self.CONFIG_FILENAME} 文件为空。"
            )

        required_fields = ["project", "path", "agent"]
        for field in required_fields:
            if field not in data:
                raise InvalidContextError(
                    f"{self.CONFIG_FILENAME} 缺少必要字段: {field}"
                )

        if data["agent"] not in [1, 2]:
            raise InvalidContextError(
                f"agent 值无效: {data['agent']}，应为 1 或 2"
            )

        return ProjectContext(
            project=data["project"],
            path=data["path"],
            agent=data["agent"],
            version=data.get("version", "2.2.3"),
            created_at=data.get("created_at"),
            last_updated=data.get("last_updated"),
        )

    def save_context(self, context: ProjectContext, config_path: Optional[Path] = None) -> None:
        """
        保存项目上下文

        Args:
            context: ProjectContext 对象
            config_path: 配置文件路径
        """
        if config_path is None:
            config_path = self.project_path / self.CONFIG_FILENAME

        from datetime import datetime

        data = {
            "project": context.project,
            "path": str(context.path),
            "agent": context.agent,
            "version": context.version,
            "created_at": context.created_at or datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    def resolve_project_path(self, context: ProjectContext) -> Path:
        """
        解析项目绝对路径

        Args:
            context: ProjectContext 对象

        Returns:
            Path 对象
        """
        return Path(context.path)

    def get_agent_display_name(self, agent_id: int) -> str:
        """获取 Agent 显示名称"""
        return "Agent 1" if agent_id == 1 else "Agent 2"
