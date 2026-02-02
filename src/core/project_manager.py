"""项目管理模块 - v2.2.0 M2 项目管理

提供任务分配、依赖管理、进度可视化等功能。
"""
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml
import json
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态枚举。"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class DependencyType(Enum):
    """依赖类型枚举。"""
    PRECEDING = "preceding"  # 前置依赖
    PARALLEL = "parallel"    # 并行依赖
    REFERENCE = "reference"  # 参考依赖


@dataclass
class TaskDependency:
    """任务依赖。"""
    task_id: str
    dependency_type: DependencyType
    description: str = ""


@dataclass
class ProjectTask:
    """任务。"""
    task_id: str
    feature_id: str
    title: str
    description: str = ""
    assignee: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "feature_id": self.feature_id,
            "title": self.title,
            "description": self.description,
            "assignee": self.assignee,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectTask":
        return cls(
            task_id=data["task_id"],
            feature_id=data["feature_id"],
            title=data["title"],
            description=data.get("description", ""),
            assignee=data.get("assignee"),
            status=TaskStatus(data.get("status", "pending")),
            dependencies=data.get("dependencies", []),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            completed_at=data.get("completed_at")
        )


@dataclass
class Feature:
    """功能模块。"""
    feature_id: str
    title: str
    description: str = ""
    default_agent: Optional[str] = None
    status: str = "pending"
    tasks: List[ProjectTask] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "title": self.title,
            "description": self.description,
            "default_agent": self.default_agent,
            "status": self.status,
            "tasks": [t.to_dict() for t in self.tasks],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Feature":
        return cls(
            feature_id=data["feature_id"],
            title=data["title"],
            description=data.get("description", ""),
            default_agent=data.get("default_agent"),
            status=data.get("status", "pending"),
            tasks=[ProjectTask.from_dict(t) for t in data.get("tasks", [])],
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )


class ProjectManagerError(Exception):
    """项目管理异常基类。"""
    pass


class FeatureNotFoundError(ProjectManagerError):
    """Feature 未找到异常。"""
    pass


class TaskNotFoundError(ProjectManagerError):
    """任务未找到异常。"""
    pass


class CircularDependencyError(ProjectManagerError):
    """循环依赖异常。"""
    pass


class ProjectManager:
    """项目管理器。"""

    DEFAULT_PROJECT_FILE = "project_data.yaml"

    def __init__(self, project_path: str, project_file: Optional[str] = None):
        """初始化项目管理器。

        Args:
            project_path: 项目路径
            project_file: 项目数据文件
        """
        self.project_path = Path(project_path)
        self.project_file = self.project_path / (project_file or self.DEFAULT_PROJECT_FILE)
        self.features: Dict[str, Feature] = {}
        self._load_project()

    def _load_project(self) -> None:
        """加载项目数据。"""
        if self.project_file.exists():
            try:
                with open(self.project_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if data and "features" in data:
                    for feature_data in data.get("features", []):
                        feature = Feature.from_dict(feature_data)
                        self.features[feature.feature_id] = feature
            except Exception as e:
                logger.warning(f"加载项目数据失败: {e}")

    def _save_project(self) -> None:
        """保存项目数据。"""
        data = {
            "features": [f.to_dict() for f in self.features.values()],
            "updated_at": datetime.now().isoformat()
        }
        with open(self.project_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)

    def create_feature(
        self,
        title: str,
        description: str = "",
        default_agent: Optional[str] = None
    ) -> Feature:
        """创建 Feature。

        Args:
            title: Feature 标题
            description: 描述
            default_agent: 默认负责 Agent

        Returns:
            创建的 Feature
        """
        feature_id = f"FEATURE-{len(self.features) + 1:03d}"
        feature = Feature(
            feature_id=feature_id,
            title=title,
            description=description,
            default_agent=default_agent
        )
        self.features[feature_id] = feature
        self._save_project()
        logger.info(f"创建 Feature: {feature_id} - {title}")
        return feature

    def get_feature(self, feature_id: str) -> Feature:
        """获取 Feature。

        Args:
            feature_id: Feature ID

        Returns:
            Feature

        Raises:
            FeatureNotFoundError: Feature 未找到
        """
        if feature_id not in self.features:
            raise FeatureNotFoundError(f"Feature 未找到: {feature_id}")
        return self.features[feature_id]

    def list_features(self, status: Optional[str] = None) -> List[Feature]:
        """列出 Feature。

        Args:
            status: 状态过滤

        Returns:
            Feature 列表
        """
        features = list(self.features.values())
        if status:
            features = [f for f in features if f.status == status]
        return features

    def create_task(
        self,
        feature_id: str,
        title: str,
        description: str = "",
        assignee: Optional[str] = None,
        dependencies: Optional[List[str]] = None
    ) -> ProjectTask:
        """创建任务。

        Args:
            feature_id: 所属 Feature ID
            title: 任务标题
            description: 描述
            assignee: 执行者
            dependencies: 依赖任务 ID 列表

        Returns:
            创建的任务

        Raises:
            FeatureNotFoundError: Feature 未找到
        """
        feature = self.get_feature(feature_id)
        
        task_id = f"TASK-{len(feature.tasks) + 1:03d}"
        task = ProjectTask(
            task_id=task_id,
            feature_id=feature_id,
            title=title,
            description=description,
            assignee=assignee,
            dependencies=dependencies or []
        )
        
        feature.tasks.append(task)
        feature.updated_at = datetime.now().isoformat()
        self._save_project()
        logger.info(f"创建任务: {task_id} - {title}")
        return task

    def get_task(self, feature_id: str, task_id: str) -> ProjectTask:
        """获取任务。

        Args:
            feature_id: Feature ID
            task_id: 任务 ID

        Returns:
            任务

        Raises:
            TaskNotFoundError: 任务未找到
        """
        feature = self.get_feature(feature_id)
        for task in feature.tasks:
            if task.task_id == task_id:
                return task
        raise TaskNotFoundError(f"任务未找到: {task_id}")

    def list_tasks(
        self,
        feature_id: Optional[str] = None,
        assignee: Optional[str] = None,
        status: Optional[TaskStatus] = None
    ) -> List[ProjectTask]:
        """列出任务。

        Args:
            feature_id: Feature 过滤
            assignee: 执行者过滤
            status: 状态过滤

        Returns:
            任务列表
        """
        tasks = []
        for feature in self.features.values():
            if feature_id and feature.feature_id != feature_id:
                continue
            for task in feature.tasks:
                if assignee and task.assignee != assignee:
                    continue
                if status and task.status != status:
                    continue
                tasks.append(task)
        return tasks

    def update_task_status(
        self,
        feature_id: str,
        task_id: str,
        status: TaskStatus
    ) -> ProjectTask:
        """更新任务状态。

        Args:
            feature_id: Feature ID
            task_id: 任务 ID
            status: 新状态

        Returns:
            更新后的任务

        Raises:
            TaskNotFoundError: 任务未找到
        """
        task = self.get_task(feature_id, task_id)
        old_status = task.status
        task.status = status
        task.updated_at = datetime.now().isoformat()
        
        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now().isoformat()
        
        self._save_project()
        logger.info(f"任务状态更新: {task_id} {old_status.value} -> {status.value}")
        return task

    def assign_task(
        self,
        feature_id: str,
        task_id: str,
        assignee: str
    ) -> ProjectTask:
        """分配任务。

        Args:
            feature_id: Feature ID
            task_id: 任务 ID
            assignee: 新执行者

        Returns:
            更新后的任务
        """
        task = self.get_task(feature_id, task_id)
        task.assignee = assignee
        task.updated_at = datetime.now().isoformat()
        self._save_project()
        logger.info(f"任务分配: {task_id} -> {assignee}")
        return task

    def detect_circular_dependencies(self) -> List[List[str]]:
        """检测循环依赖。

        Returns:
            循环依赖链列表，每个链是任务 ID 列表
        """
        cycles = []
        visited = set()
        recursion_stack = set()

        def dfs(task_id: str, path: List[str]) -> None:
            if task_id in recursion_stack:
                cycle_start = path.index(task_id)
                cycles.append(path[cycle_start:] + [task_id])
                return
            
            if task_id in visited:
                return
            
            visited.add(task_id)
            recursion_stack.add(task_id)
            path.append(task_id)
            
            for feature in self.features.values():
                for task in feature.tasks:
                    if task.task_id != task_id:
                        continue
                    for dep_id in task.dependencies:
                        if dep_id not in visited:
                            dfs(dep_id, path.copy())
            
            recursion_stack.remove(task_id)
            path.pop()

        for feature in self.features.values():
            for task in feature.tasks:
                if task.task_id not in visited:
                    dfs(task.task_id, [])

        return cycles

    def check_dependencies_resolved(
        self,
        feature_id: str,
        task_id: str
    ) -> tuple[bool, List[str]]:
        """检查任务依赖是否已解决。

        Args:
            feature_id: Feature ID
            task_id: 任务 ID

        Returns:
            (是否可开始, 未解决的依赖列表)
        """
        task = self.get_task(feature_id, task_id)
        unresolved = []
        
        for dep_id in task.dependencies:
            dep_task = None
            for feature in self.features.values():
                for t in feature.tasks:
                    if t.task_id == dep_id:
                        dep_task = t
                        break
                if dep_task:
                    break
            
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                unresolved.append(dep_id)
        
        return len(unresolved) == 0, unresolved

    def get_progress_summary(self) -> Dict[str, Any]:
        """获取进度摘要。

        Returns:
            进度摘要
        """
        total_tasks = 0
        completed_tasks = 0
        in_progress_tasks = 0
        blocked_tasks = 0
        by_assignee = {}

        for feature in self.features.values():
            for task in feature.tasks:
                total_tasks += 1
                if task.status == TaskStatus.COMPLETED:
                    completed_tasks += 1
                elif task.status == TaskStatus.IN_PROGRESS:
                    in_progress_tasks += 1
                elif task.status == TaskStatus.BLOCKED:
                    blocked_tasks += 1
                
                if task.assignee:
                    if task.assignee not in by_assignee:
                        by_assignee[task.assignee] = {"total": 0, "completed": 0, "in_progress": 0}
                    by_assignee[task.assignee]["total"] += 1
                    if task.status == TaskStatus.COMPLETED:
                        by_assignee[task.assignee]["completed"] += 1
                    elif task.status == TaskStatus.IN_PROGRESS:
                        by_assignee[task.assignee]["in_progress"] += 1

        return {
            "total_features": len(self.features),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "blocked_tasks": blocked_tasks,
            "completion_rate": round(completed_tasks / total_tasks * 100, 2) if total_tasks > 0 else 0,
            "by_assignee": by_assignee
        }

    def export_project(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """导出项目数据。

        Args:
            output_path: 输出路径（可选）

        Returns:
            项目数据字典
        """
        data = {
            "features": [f.to_dict() for f in self.features.values()],
            "progress": self.get_progress_summary(),
            "exported_at": datetime.now().isoformat()
        }
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True)
        
        return data


if __name__ == "__main__":
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        pm = ProjectManager(tmpdir)
        
        feature = pm.create_feature(
            title="用户认证模块",
            description="用户登录、注册、登出功能",
            default_agent="agent_backend_go"
        )
        print(f"创建 Feature: {feature.feature_id}")
        
        task1 = pm.create_task(
            feature_id=feature.feature_id,
            title="设计用户认证 API",
            assignee="agent_backend_go"
        )
        print(f"创建任务: {task1.task_id}")
        
        task2 = pm.create_task(
            feature_id=feature.feature_id,
            title="实现 JWT 认证",
            assignee="agent_backend_go",
            dependencies=[task1.task_id]
        )
        print(f"创建任务: {task2.task_id}")
        
        progress = pm.get_progress_summary()
        print(f"进度: {progress}")
