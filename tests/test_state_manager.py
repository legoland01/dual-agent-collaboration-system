"""状态管理器单元测试。"""
import os
import tempfile
import time
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.state_manager import (
    StateManager,
    StateManagerError,
    StateFileNotFoundError,
    StateValidationError,
    StateConflictError,
    StateLockError,
    StateLockInfo,
)


class TestStateManagerExceptions:
    """测试状态管理器异常类。"""

    def test_state_manager_error(self):
        error = StateManagerError("test error")
        assert str(error) == "test error"

    def test_state_file_not_found_error(self):
        error = StateFileNotFoundError("file not found")
        assert str(error) == "file not found"

    def test_state_validation_error(self):
        error = StateValidationError("validation failed")
        assert str(error) == "validation failed"

    def test_state_conflict_error(self):
        error = StateConflictError("conflict")
        assert str(error) == "conflict"

    def test_state_lock_error(self):
        error = StateLockError("lock error")
        assert str(error) == "lock error"


class TestStateLockInfo:
    """测试StateLockInfo数据类。"""

    def test_lock_info_defaults(self):
        lock = StateLockInfo(
            lock_id="test-lock",
            version=1,
            created_at=time.time()
        )
        assert lock.lock_id == "test-lock"
        assert lock.version == 1
        assert lock.created_at > 0
        assert lock.owner == ""

    def test_lock_info_custom(self):
        lock = StateLockInfo(
            lock_id="test-lock",
            version=5,
            created_at=time.time(),
            owner="agent1"
        )
        assert lock.owner == "agent1"


class TestStateManager:
    """状态管理器测试类。"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def state_manager(self, temp_dir):
        """创建状态管理器实例。"""
        return StateManager(temp_dir)
    
    def test_init(self, state_manager, temp_dir):
        """测试初始化。"""
        assert str(state_manager.project_path) == temp_dir
        assert "project_state.yaml" in str(state_manager.state_file)
        assert ".state_lock" in str(state_manager.lock_file)
        assert state_manager.lock_owner == "system"
        assert state_manager._current_lock is None
    
    def test_init_state(self, state_manager):
        """测试初始化状态。"""
        state = state_manager.init_state("TestProject", "PYTHON")
        
        assert state["project"]["name"] == "TestProject"
        assert state["project"]["type"] == "PYTHON"
        assert state["phase"] == "project_init"
        assert state["agents"]["agent1"]["current"] == True
        assert state["agents"]["agent2"]["current"] == False
    
    def test_init_state_creates_files(self, state_manager):
        """测试初始化创建文件。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        assert state_manager.state_file.exists()
        assert state_manager.history_dir.exists()
    
    def test_load_state(self, state_manager):
        """测试加载状态。"""
        state_manager.init_state("TestProject", "PYTHON")
        state = state_manager.load_state()
        
        assert state["project"]["name"] == "TestProject"
        assert state["project"]["type"] == "PYTHON"
    
    def test_load_state_file_not_found(self, temp_dir):
        """测试加载不存在的状态文件。"""
        state_manager = StateManager(temp_dir)
        with pytest.raises(StateFileNotFoundError):
            state_manager.load_state()
    
    def test_update_phase(self, state_manager):
        """测试更新阶段。"""
        state_manager.init_state("TestProject", "PYTHON")
        state = state_manager.update_phase("requirements_draft")
        
        assert state["phase"] == "requirements_draft"
    
    def test_update_signoff(self, state_manager):
        """测试更新签署状态。"""
        state_manager.init_state("TestProject", "PYTHON")
        state = state_manager.update_signoff("requirements", "pm", True, "确认需求")
        
        assert state["requirements"]["pm_signoff"] == True
    
    def test_get_current_phase(self, state_manager):
        """测试获取当前阶段。"""
        state_manager.init_state("TestProject", "PYTHON")
        phase = state_manager.get_current_phase()
        
        assert phase == "project_init"
    
    def test_get_current_phase_not_initialized(self, temp_dir):
        """测试未初始化时获取阶段。"""
        state_manager = StateManager(temp_dir)
        phase = state_manager.get_current_phase()
        
        assert phase == "not_initialized"
    
    def test_get_signoff_status(self, state_manager):
        """测试获取签署状态。"""
        state_manager.init_state("TestProject", "PYTHON")
        status = state_manager.get_signoff_status("requirements")
        
        assert status["pm_signoff"] == False
        assert status["dev_signoff"] == False
    
    def test_set_active_agent(self, state_manager):
        """测试设置活跃Agent。"""
        state_manager.init_state("TestProject", "PYTHON")
        state = state_manager.set_active_agent("agent2")
        
        assert state["agents"]["agent2"]["current"] == True
        assert state["agents"]["agent1"]["current"] == False
    
    def test_add_history(self, state_manager):
        """测试添加历史记录。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.add_history("init", "agent1", "初始化项目")
        
        history = state_manager.get_history()
        assert len(history) == 1
        assert history[0]["action"] == "init"
    
    def test_increment_review_cycle(self, state_manager):
        """测试增加评审轮次。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.increment_review_cycle()
        
        state = state_manager.load_state()
        assert state["requirements"]["review_cycles"] == 1
    
    def test_can_proceed_to_next_phase(self, state_manager):
        """测试是否可以推进到下一阶段。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        assert state_manager.can_proceed_to_next_phase() == False
    
    def test_can_proceed_to_next_phase_requirements_signed(self, state_manager):
        """测试需求签署后可以推进。"""
        state_manager.init_state("TestProject", "PYTHON")
        state = state_manager.load_state()
        state["phase"] = "requirements_review"
        state["requirements"]["pm_signoff"] = True
        state["requirements"]["dev_signoff"] = True
        state_manager.save_state(state)
        
        assert state_manager.can_proceed_to_next_phase() == True
    
    def test_can_proceed_to_next_phase_design_signed(self, state_manager):
        """测试设计签署后可以推进。"""
        state_manager.init_state("TestProject", "PYTHON")
        state = state_manager.load_state()
        state["phase"] = "design_review"
        state["design"]["pm_signoff"] = True
        state["design"]["dev_signoff"] = True
        state_manager.save_state(state)
        
        assert state_manager.can_proceed_to_next_phase() == True
    
    def test_get_active_agent(self, state_manager):
        """测试获取活跃Agent。"""
        state_manager.init_state("TestProject", "PYTHON")
        agent = state_manager.get_active_agent()
        
        assert agent == "agent1"
    
    def test_get_active_agent_not_found(self, temp_dir):
        """测试获取活跃Agent（未找到）。"""
        state_manager = StateManager(temp_dir)
        agent = state_manager.get_active_agent()
        
        assert agent == "unknown"
    
    def test_update_requirements_version(self, state_manager):
        """测试更新需求版本号。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.update_requirements_version("v1.0")
        
        state = state_manager.load_state()
        assert state["requirements"]["version"] == "v1.0"
        assert state["requirements"]["status"] == "draft"
    
    def test_update_design_version(self, state_manager):
        """测试更新设计版本号。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.update_design_version("v1.0")
        
        state = state_manager.load_state()
        assert state["design"]["version"] == "v1.0"
        assert state["design"]["status"] == "draft"
    
    def test_read_state(self, state_manager):
        """测试读取状态。"""
        state_manager.init_state("TestProject", "PYTHON")
        state = state_manager.read_state()
        
        assert state["project"]["name"] == "TestProject"
    
    def test_write_state(self, state_manager):
        """测试写入状态。"""
        state_manager.init_state("TestProject", "PYTHON")
        state = state_manager.read_state()
        state["phase"] = "execution"
        
        result = state_manager.write_state(state, action="test")
        
        assert result == True
        updated = state_manager.read_state()
        assert updated["phase"] == "execution"
        assert updated["metadata"]["last_action"] == "test"
    
    def test_transition_phase_success(self, state_manager):
        """测试阶段转换成功。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        success, new_state = state_manager.transition_phase(
            from_phase="project_init",
            to_phase="requirements",
            agent_id="agent1"
        )
        
        assert success == True
        assert new_state["phase"] == "requirements"
    
    def test_transition_phase_wrong_phase(self, state_manager):
        """测试阶段转换（当前阶段错误）。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        success, result = state_manager.transition_phase(
            from_phase="wrong_phase",
            to_phase="requirements",
            agent_id="agent1"
        )
        
        assert success == False
        assert "当前阶段不是" in result["error"]
    
    def test_acquire_lock(self, state_manager):
        """测试获取锁。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        result = state_manager.acquire_lock()
        
        assert result == True
        assert state_manager._current_lock is not None
    
    def test_acquire_lock_with_expected_version(self, state_manager):
        """测试获取锁（指定版本）。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        result = state_manager.acquire_lock(expected_version=1)
        
        assert result == True
    
    def test_acquire_lock_wrong_version(self, state_manager):
        """测试获取锁（版本不匹配）。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.acquire_lock()
        
        result = state_manager.acquire_lock(expected_version=999)
        assert result == False
    
    def test_release_lock(self, state_manager):
        """测试释放锁。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.acquire_lock()
        
        result = state_manager.release_lock()
        
        assert result == True
        assert state_manager._current_lock is None
    
    def test_release_lock_no_lock(self, state_manager):
        """测试释放锁（无锁）。"""
        result = state_manager.release_lock()
        assert result == False
    
    def test_is_locked(self, state_manager):
        """测试检查锁状态。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.acquire_lock()
        
        result = state_manager.is_locked()
        assert result == True
    
    def test_is_locked_false(self, state_manager):
        """测试检查锁状态（无锁）。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        result = state_manager.is_locked()
        assert result == False
    
    def test_is_locked_expired(self, state_manager):
        """测试检查锁状态（已过期）。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.acquire_lock()
        
        state_manager.LOCK_TIMEOUT = 0
        result = state_manager.is_locked()
        assert result == False
    
    def test_get_state_version(self, state_manager):
        """测试获取状态版本。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        version = state_manager.get_state_version()
        assert version == 1
    
    def test_get_history(self, state_manager):
        """测试获取历史记录。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.add_history("test", "agent1", "test details")
        
        history = state_manager.get_history()
        assert len(history) == 1
    
    def test_get_history_with_limit(self, state_manager):
        """测试获取历史记录（带限制）。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        for i in range(10):
            state_manager.add_history(f"action_{i}", "agent1", f"details_{i}")
        
        history = state_manager.get_history(limit=5)
        assert len(history) == 5
    
    def test_save_state(self, state_manager):
        """测试保存状态。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.save_state({"test": "data"})
        
        loaded = state_manager.load_state()
        assert loaded["test"] == "data"
    
    def test_add_history_entry(self, state_manager):
        """测试添加历史条目。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.add_history_entry("test_action", "agent1", "test details")
        
        history = state_manager.get_history()
        assert len(history) == 1
        assert history[0]["action"] == "test_action"
        assert history[0]["agent_id"] == "agent1"
    
    def test_transition_phase_adds_history(self, state_manager):
        """测试阶段转换添加历史记录。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        state_manager.transition_phase(
            from_phase="project_init",
            to_phase="requirements",
            agent_id="agent1"
        )
        
        history = state_manager.get_history()
        assert len(history) == 1
        assert history[0]["action"] == "phase_transition"
    
    def test_update_signoff_with_date(self, state_manager):
        """测试更新签署状态（带日期）。"""
        state_manager.init_state("TestProject", "PYTHON")
        state = state_manager.load_state()
        state["requirements"]["pm_signoff_date"] = ""
        state_manager.save_state(state)
        
        state = state_manager.update_signoff("requirements", "pm", True, "approved")
        
        assert state["requirements"]["pm_signoff"] == True
        assert state["requirements"]["pm_signoff_date"] != ""
    
    def test_can_proceed_not_signed(self, state_manager):
        """测试不能推进（未签署）。"""
        state_manager.init_state("TestProject", "PYTHON")
        state = state_manager.load_state()
        state["phase"] = "requirements_review"
        state["requirements"]["pm_signoff"] = False
        state_manager.save_state(state)
        
        assert state_manager.can_proceed_to_next_phase() == False
    
    def test_state_manager_error_class(self):
        """测试错误类继承。"""
        error = StateManagerError("test")
        assert isinstance(error, Exception)
        
        error = StateFileNotFoundError("test")
        assert isinstance(error, StateManagerError)
        
        error = StateValidationError("test")
        assert isinstance(error, StateManagerError)
        
        error = StateConflictError("test")
        assert isinstance(error, StateManagerError)
        
        error = StateLockError("test")
        assert isinstance(error, StateManagerError)
    
    def test_state_lock_info_as_dict(self, temp_dir):
        """测试StateLockInfo数据类。"""
        lock = StateLockInfo(
            lock_id="test-id",
            version=1,
            created_at=1234567890.0,
            owner="test-owner"
        )
        
        assert lock.lock_id == "test-id"
        assert lock.version == 1
        assert lock.created_at == 1234567890.0
        assert lock.owner == "test-owner"
    
    def test_write_state_failure(self, state_manager):
        """测试写入状态失败。"""
        with patch.object(state_manager, '_write_state_file', side_effect=Exception("write error")):
            result = state_manager.write_state({"test": "data"})
            assert result == False
    
    def test_read_state_invalid_format(self, state_manager):
        """测试读取无效格式的状态文件。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.state_file.write_text("[not valid yaml at all")
        
        with pytest.raises((StateValidationError, ValueError)):
            state_manager._read_state_file()
    
    def test_clear_lock(self, state_manager):
        """测试清除锁。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.acquire_lock()
        
        state_manager._clear_lock()
        
        assert state_manager.lock_file.exists() == False
    
    def test_read_lock_file_not_exists(self, state_manager):
        """测试读取不存在的锁文件。"""
        result = state_manager._read_lock_file()
        assert result is None
    
    def test_read_lock_file_exists(self, state_manager):
        """测试读取存在的锁文件。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.acquire_lock()
        
        result = state_manager._read_lock_file()
        assert result is not None
        assert result.lock_id == state_manager._current_lock.lock_id
    
    def test_increment_version(self, state_manager):
        """测试递增版本号。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        new_version = state_manager._increment_version()
        
        assert new_version == 2
    
    def test_ensure_history_dir(self, state_manager):
        """测试确保历史目录存在。"""
        assert state_manager.history_dir.exists() == False
        state_manager._ensure_history_dir()
        assert state_manager.history_dir.exists()
    
    def test_write_state_file(self, state_manager):
        """测试写入状态文件。"""
        state_manager._write_state_file({"test": "data"})
        assert state_manager.state_file.exists()
    
    def test_get_state_version_not_found(self, temp_dir):
        """测试获取状态版本（未找到）。"""
        state_manager = StateManager(temp_dir)
        version = state_manager._get_state_version()
        assert version == 0
    
    def test_transition_phase_exception(self, state_manager):
        """测试阶段转换异常。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        with patch.object(state_manager, '_read_state_file', side_effect=Exception("read error")):
            success, result = state_manager.transition_phase(
                from_phase="project_init",
                to_phase="requirements",
                agent_id="agent1"
            )
            assert success == False
    
    def test_transition_phase_max_retries(self, state_manager):
        """测试阶段转换最大重试次数。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        with patch.object(StateManager, 'acquire_lock', return_value=False):
            success, result = state_manager.transition_phase(
                from_phase="project_init",
                to_phase="requirements",
                agent_id="agent1"
            )
            assert success == False
            assert "多次版本冲突" in result["error"]
    
    def test_add_history_entry_exception(self, state_manager):
        """测试添加历史记录异常。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        with patch.object(state_manager, '_read_state_file', side_effect=Exception("read error")):
            state_manager.add_history_entry("test", "agent1", "details")  # Should not raise
    
    def test_clear_lock_exception(self, state_manager):
        """测试清除锁异常。"""
        state_manager.init_state("TestProject", "PYTHON")
        state_manager.acquire_lock()
        
        with patch('os.unlink', side_effect=OSError("permission denied")):
            state_manager._clear_lock()  # Should not raise, just log warning
    
    def test_read_lock_file_exception(self, temp_dir):
        """测试读取锁文件异常。"""
        state_manager = StateManager(temp_dir)
        
        with patch('src.utils.yaml.load_yaml', side_effect=OSError("file error")):
            result = state_manager._read_lock_file()
            assert result is None
    
    def test_transition_phase_conflict(self, state_manager):
        """测试阶段转换冲突。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        with patch.object(StateManager, 'acquire_lock', return_value=False):
            success, result = state_manager.transition_phase(
                from_phase="project_init",
                to_phase="requirements",
                agent_id="agent1"
            )
            assert success == False
    
    def test_write_state_exception(self, state_manager):
        """测试写入状态异常。"""
        state_manager.init_state("TestProject", "PYTHON")
        
        with patch.object(state_manager, '_write_state_file', side_effect=Exception("write error")):
            result = state_manager.write_state({"test": "data"})
            assert result == False
