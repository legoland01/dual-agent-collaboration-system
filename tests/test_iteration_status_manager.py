"""IterationStatusManager 单元测试。

测试用例：
- 迭代状态管理
- 阶段状态更新
- 进度计算
"""
import pytest
import tempfile
import yaml
from pathlib import Path


class TestIterationStatusManager:
    """IterationStatusManager 测试。"""

    def test_iteration_status_enum(self):
        """测试迭代状态枚举。"""
        from src.core.iteration_status_manager import IterationStatus, PhaseStatus
        
        assert IterationStatus.PENDING.value == "pending"
        assert IterationStatus.IN_PROGRESS.value == "in_progress"
        assert IterationStatus.COMPLETED.value == "completed"
        assert IterationStatus.ARCHIVED.value == "archived"

    def test_phase_status_enum(self):
        """测试阶段状态枚举。"""
        from src.core.iteration_status_manager import PhaseStatus
        
        assert PhaseStatus.PENDING.value == "pending"
        assert PhaseStatus.IN_PROGRESS.value == "in_progress"
        assert PhaseStatus.COMPLETED.value == "completed"
        assert PhaseStatus.APPROVED.value == "approved"

    def test_iteration_state_dataclass(self):
        """测试迭代状态数据类。"""
        from src.core.iteration_status_manager import IterationState
        
        state = IterationState(version="v2.1.0")
        assert state.version == "v2.1.0"
        assert state.status == "pending"
        assert state.requirements == "pending"
        assert state.development == "pending"
        assert state.testing == "pending"
        assert state.deployment == "pending"

    def test_initialization(self, tmp_path):
        """测试初始化。"""
        from src.core.iteration_status_manager import IterationStatusManager
        
        state_file = tmp_path / "state.yaml"
        state_file.write_text("version: '2.1.0'")
        
        manager = IterationStatusManager(str(state_file))
        assert manager is not None
        assert manager.state_path == str(state_file)

    def test_get_current_iteration(self, tmp_path):
        """测试获取当前迭代。"""
        from src.core.iteration_status_manager import IterationStatusManager
        
        state_file = tmp_path / "state.yaml"
        state_content = {
            "version": "2.1.0",
            "iteration": {"current": "v2.1.0", "status": "in_progress"}
        }
        state_file.write_text(yaml.dump(state_content))
        
        manager = IterationStatusManager(str(state_file))
        assert manager.current_iteration == "v2.1.0"

    def test_get_iteration_state(self, tmp_path):
        """测试获取迭代状态。"""
        from src.core.iteration_status_manager import IterationStatusManager
        
        state_file = tmp_path / "state.yaml"
        state_content = {
            "version": "2.1.0",
            "iteration": {"current": "v2.1.0", "status": "in_progress"},
            "iterations": {
                "v2.1.0": {
                    "version": "v2.1.0",
                    "status": "in_progress",
                    "requirements": "completed",
                    "design": "in_progress",
                    "development": "pending",
                    "testing": "pending",
                    "deployment": "pending",
                    "history": []
                }
            }
        }
        state_file.write_text(yaml.dump(state_content))
        
        manager = IterationStatusManager(str(state_file))
        state = manager.get_iteration_state("v2.1.0")
        
        assert state is not None
        assert state.version == "v2.1.0"
        assert state.requirements == "completed"

    def test_get_progress(self, tmp_path):
        """测试获取进度。"""
        from src.core.iteration_status_manager import IterationStatusManager
        
        state_file = tmp_path / "state.yaml"
        state_content = {
            "version": "2.1.0",
            "iteration": {"current": "v2.1.0", "status": "in_progress"},
            "iterations": {
                "v2.1.0": {
                    "version": "v2.1.0",
                    "status": "in_progress",
                    "requirements": "completed",
                    "design": "completed",
                    "development": "pending",
                    "testing": "pending",
                    "deployment": "pending",
                    "history": []
                }
            }
        }
        state_file.write_text(yaml.dump(state_content))
        
        manager = IterationStatusManager(str(state_file))
        progress = manager.get_progress("v2.1.0")
        
        assert progress["version"] == "v2.1.0"
        assert progress["completed_phases"] == 2
        assert progress["progress_percent"] == 40.0

    def test_update_phase_status(self, tmp_path):
        """测试更新阶段状态。"""
        from src.core.iteration_status_manager import IterationStatusManager
        
        state_file = tmp_path / "state.yaml"
        state_content = {
            "version": "2.1.0",
            "iteration": {"current": "v2.1.0", "status": "in_progress"},
            "iterations": {
                "v2.1.0": {
                    "version": "v2.1.0",
                    "status": "in_progress",
                    "requirements": "in_progress",
                    "design": "pending",
                    "development": "pending",
                    "testing": "pending",
                    "deployment": "pending",
                    "history": []
                }
            }
        }
        state_file.write_text(yaml.dump(state_content))
        
        manager = IterationStatusManager(str(state_file))
        result = manager.update_phase_status("requirements", "completed", "v2.1.0")
        
        assert result is True
        state = manager.get_iteration_state("v2.1.0")
        assert state.requirements == "completed"

    def test_reset_phase(self, tmp_path):
        """测试重置阶段状态。"""
        from src.core.iteration_status_manager import IterationStatusManager
        
        state_file = tmp_path / "state.yaml"
        state_content = {
            "version": "2.1.0",
            "iteration": {"current": "v2.1.0", "status": "in_progress"},
            "iterations": {
                "v2.1.0": {
                    "version": "v2.1.0",
                    "status": "in_progress",
                    "requirements": "completed",
                    "design": "pending",
                    "development": "pending",
                    "testing": "pending",
                    "deployment": "pending",
                    "history": []
                }
            }
        }
        state_file.write_text(yaml.dump(state_content))
        
        manager = IterationStatusManager(str(state_file))
        manager.reset_phase("requirements", "v2.1.0")
        
        state = manager.get_iteration_state("v2.1.0")
        assert state.requirements == "pending"

    def test_complete_iteration(self, tmp_path):
        """测试完成迭代。"""
        from src.core.iteration_status_manager import IterationStatusManager
        
        state_file = tmp_path / "state.yaml"
        state_content = {
            "version": "2.1.0",
            "iteration": {"current": "v2.1.0", "status": "in_progress"},
            "iterations": {
                "v2.1.0": {
                    "version": "v2.1.0",
                    "status": "in_progress",
                    "requirements": "completed",
                    "design": "completed",
                    "development": "completed",
                    "testing": "completed",
                    "deployment": "completed",
                    "history": []
                }
            }
        }
        state_file.write_text(yaml.dump(state_content))
        
        manager = IterationStatusManager(str(state_file))
        result = manager.complete_iteration("v2.1.0")
        
        assert result is True
        state = manager.get_iteration_state("v2.1.0")
        assert state.status == "completed"

    def test_validate_consistency(self, tmp_path):
        """测试一致性验证。"""
        from src.core.iteration_status_manager import IterationStatusManager
        
        state_file = tmp_path / "state.yaml"
        state_content = {
            "version": "2.1.0",
            "iteration": {"current": "v2.1.0", "status": "in_progress"},
            "iterations": {
                "v2.1.0": {
                    "version": "v2.1.0",
                    "status": "in_progress",
                    "requirements": "completed",
                    "design": "completed",
                    "development": "completed",
                    "testing": "completed",
                    "deployment": "completed",
                    "history": []
                }
            }
        }
        state_file.write_text(yaml.dump(state_content))
        
        manager = IterationStatusManager(str(state_file))
        result = manager.validate_consistency("v2.1.0")
        
        assert result["valid"] is True
        assert result["version"] == "v2.1.0"

    def test_get_all_iterations(self, tmp_path):
        """测试获取所有迭代。"""
        from src.core.iteration_status_manager import IterationStatusManager
        
        state_file = tmp_path / "state.yaml"
        state_content = {
            "version": "2.1.0",
            "iteration": {"current": "v2.1.0", "status": "in_progress"},
            "iterations": {
                "v2.0.0": {"version": "v2.0.0", "status": "completed"},
                "v2.1.0": {"version": "v2.1.0", "status": "in_progress"}
            }
        }
        state_file.write_text(yaml.dump(state_content))
        
        manager = IterationStatusManager(str(state_file))
        iterations = manager.get_all_iterations()
        
        assert len(iterations) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
