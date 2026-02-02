"""v2.2.0 M2 Project Manager 测试用例

基于 src/core/project_manager.py
"""
import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.project_manager import (
    ProjectManager,
    ProjectTask,
    Feature,
    TaskStatus,
    DependencyType,
    FeatureNotFoundError,
    TaskNotFoundError,
    CircularDependencyError
)


class TestProjectManagerBasic:
    """项目管理器基础测试。"""

    def test_initialize_project_manager(self, tmp_path):
        """测试初始化项目管理器。"""
        pm = ProjectManager(str(tmp_path))
        
        assert pm.project_path == tmp_path
        assert pm.project_file == tmp_path / "project_data.yaml"

    def test_create_feature(self, tmp_path):
        """测试创建 Feature。"""
        pm = ProjectManager(str(tmp_path))
        feature = pm.create_feature(
            title="用户认证模块",
            description="用户登录、注册功能",
            default_agent="agent_backend_go"
        )
        
        assert feature is not None
        assert feature.feature_id == "FEATURE-001"
        assert feature.title == "用户认证模块"
        assert feature.default_agent == "agent_backend_go"

    def test_list_features(self, tmp_path):
        """测试列出 Feature。"""
        pm = ProjectManager(str(tmp_path))
        pm.create_feature(title="Feature 1")
        pm.create_feature(title="Feature 2")
        
        features = pm.list_features()
        assert len(features) == 2

    def test_get_feature(self, tmp_path):
        """测试获取 Feature。"""
        pm = ProjectManager(str(tmp_path))
        feature = pm.create_feature(title="Test Feature")
        
        retrieved = pm.get_feature("FEATURE-001")
        assert retrieved.feature_id == feature.feature_id


class TestTaskManagement:
    """任务管理测试。"""

    @pytest.fixture
    def pm(self, tmp_path):
        pm = ProjectManager(str(tmp_path))
        pm.create_feature(title="Test Feature")
        return pm

    def test_create_task(self, pm):
        """测试创建任务。"""
        task = pm.create_task(
            feature_id="FEATURE-001",
            title="设计 API",
            description="设计用户认证 API",
            assignee="agent_backend_go"
        )
        
        assert task is not None
        assert task.task_id == "TASK-001"
        assert task.title == "设计 API"
        assert task.assignee == "agent_backend_go"

    def test_create_task_with_dependencies(self, pm):
        """测试创建带依赖的任务。"""
        task1 = pm.create_task(
            feature_id="FEATURE-001",
            title="任务 1"
        )
        task2 = pm.create_task(
            feature_id="FEATURE-001",
            title="任务 2",
            dependencies=[task1.task_id]
        )
        
        assert task2.task_id == "TASK-002"
        assert task1.task_id in task2.dependencies

    def test_get_task(self, pm):
        """测试获取任务。"""
        pm.create_task(feature_id="FEATURE-001", title="Test Task")
        
        task = pm.get_task("FEATURE-001", "TASK-001")
        assert task.task_id == "TASK-001"

    def test_list_tasks(self, pm):
        """测试列出任务。"""
        pm.create_task(feature_id="FEATURE-001", title="Task 1")
        pm.create_task(feature_id="FEATURE-001", title="Task 2")
        
        tasks = pm.list_tasks(feature_id="FEATURE-001")
        assert len(tasks) == 2

    def test_update_task_status(self, pm):
        """测试更新任务状态。"""
        pm.create_task(feature_id="FEATURE-001", title="Task")
        
        task = pm.update_task_status(
            "FEATURE-001",
            "TASK-001",
            TaskStatus.IN_PROGRESS
        )
        
        assert task.status == TaskStatus.IN_PROGRESS

    def test_assign_task(self, pm):
        """测试分配任务。"""
        pm.create_task(feature_id="FEATURE-001", title="Task")
        
        task = pm.assign_task("FEATURE-001", "TASK-001", "agent_frontend_react")
        
        assert task.assignee == "agent_frontend_react"


class TestDependencyManagement:
    """依赖管理测试。"""

    @pytest.fixture
    def pm(self, tmp_path):
        pm = ProjectManager(str(tmp_path))
        pm.create_feature(title="Test Feature")
        return pm

    def test_check_dependencies_resolved(self, pm):
        """测试检查依赖是否已解决。"""
        task1 = pm.create_task(feature_id="FEATURE-001", title="Task 1")
        pm.create_task(
            feature_id="FEATURE-001",
            title="Task 2",
            dependencies=[task1.task_id]
        )
        
        can_start, unresolved = pm.check_dependencies_resolved(
            "FEATURE-001",
            "TASK-002"
        )
        
        assert can_start is False
        assert task1.task_id in unresolved

    def test_check_dependencies_resolved_when_completed(self, pm):
        """测试依赖完成后的检查。"""
        task1 = pm.create_task(feature_id="FEATURE-001", title="Task 1")
        pm.create_task(
            feature_id="FEATURE-001",
            title="Task 2",
            dependencies=[task1.task_id]
        )
        pm.update_task_status("FEATURE-001", "TASK-001", TaskStatus.COMPLETED)
        
        can_start, unresolved = pm.check_dependencies_resolved(
            "FEATURE-001",
            "TASK-002"
        )
        
        assert can_start is True
        assert len(unresolved) == 0


class TestCircularDependency:
    """循环依赖检测测试。"""

    def test_no_circular_dependency(self, tmp_path):
        """测试无循环依赖。"""
        pm = ProjectManager(str(tmp_path))
        pm.create_feature(title="Test Feature")
        
        pm.create_task(feature_id="FEATURE-001", title="Task 1")
        pm.create_task(
            feature_id="FEATURE-001",
            title="Task 2",
            dependencies=["TASK-001"]
        )
        pm.create_task(
            feature_id="FEATURE-001",
            title="Task 3",
            dependencies=["TASK-002"]
        )
        
        cycles = pm.detect_circular_dependencies()
        assert len(cycles) == 0

    def test_cyclic_detection_available(self, tmp_path):
        """测试循环依赖检测功能可用。"""
        pm = ProjectManager(str(tmp_path))
        pm.create_feature(title="Test Feature")
        pm.create_task(feature_id="FEATURE-001", title="Task 1")
        pm.create_task(feature_id="FEATURE-001", title="Task 2")
        
        result = pm.detect_circular_dependencies()
        assert isinstance(result, list)


class TestProgressSummary:
    """进度摘要测试。"""

    def test_get_progress_summary(self, tmp_path):
        """测试获取进度摘要。"""
        pm = ProjectManager(str(tmp_path))
        pm.create_feature(title="Feature 1")
        
        pm.create_task(feature_id="FEATURE-001", title="Task 1")
        pm.create_task(feature_id="FEATURE-001", title="Task 2")
        pm.update_task_status("FEATURE-001", "TASK-001", TaskStatus.COMPLETED)
        
        progress = pm.get_progress_summary()
        
        assert progress["total_features"] == 1
        assert progress["total_tasks"] == 2
        assert progress["completed_tasks"] == 1
        assert progress["completion_rate"] == 50.0


class TestExport:
    """导出测试。"""

    def test_export_project(self, tmp_path):
        """测试导出项目数据。"""
        pm = ProjectManager(str(tmp_path))
        pm.create_feature(title="Feature 1")
        pm.create_task(feature_id="FEATURE-001", title="Task 1")
        
        data = pm.export_project()
        
        assert "features" in data
        assert "progress" in data
        assert len(data["features"]) == 1


class TestErrorHandling:
    """错误处理测试。"""

    def test_feature_not_found(self, tmp_path):
        """测试 Feature 未找到。"""
        pm = ProjectManager(str(tmp_path))
        
        with pytest.raises(FeatureNotFoundError):
            pm.get_feature("FEATURE-999")

    def test_task_not_found(self, tmp_path):
        """测试任务未找到。"""
        pm = ProjectManager(str(tmp_path))
        pm.create_feature(title="Feature 1")
        
        with pytest.raises(TaskNotFoundError):
            pm.get_task("FEATURE-001", "TASK-999")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
