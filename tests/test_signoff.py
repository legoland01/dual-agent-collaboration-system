"""SignoffEngine 单元测试。

测试用例：
- 签署异常
- 签署引擎初始化
- 阶段配置
- 签署操作
"""
import pytest
from unittest.mock import Mock, MagicMock


class TestSignoffExceptions:
    """签署异常测试。"""

    def test_signoff_error(self):
        """测试签署异常。"""
        from src.core.signoff import SignoffError
        
        error = SignoffError("Test error")
        assert "Test error" in str(error)

    def test_permission_denied_error(self):
        """测试权限不足异常。"""
        from src.core.signoff import PermissionDeniedError
        
        error = PermissionDeniedError("Permission denied")
        assert "Permission denied" in str(error)

    def test_invalid_state_error(self):
        """测试状态无效异常。"""
        from src.core.signoff import InvalidStateError
        
        error = InvalidStateError("Invalid state")
        assert "Invalid state" in str(error)

    def test_duplicate_signoff_error(self):
        """测试重复签署异常。"""
        from src.core.signoff import DuplicateSignoffError
        
        error = DuplicateSignoffError("Already signed")
        assert "Already signed" in str(error)

    def test_rejection_error(self):
        """测试拒签异常。"""
        from src.core.signoff import RejectionError
        
        error = RejectionError("Rejected")
        assert "Rejected" in str(error)


class TestSignoffEngine:
    """SignoffEngine 测试。"""

    def test_initialization(self):
        """测试初始化。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        
        engine = SignoffEngine(state_manager, workflow_engine)
        
        assert engine.state_manager is state_manager
        assert engine.workflow_engine is workflow_engine

    def test_stage_config(self):
        """测试阶段配置。"""
        from src.core.signoff import SignoffEngine
        
        assert "requirements" in SignoffEngine.STAGE_CONFIG
        assert "design" in SignoffEngine.STAGE_CONFIG
        assert "test" in SignoffEngine.STAGE_CONFIG
        
        req_config = SignoffEngine.STAGE_CONFIG["requirements"]
        assert req_config["agent1_role"] == "产品经理"
        assert req_config["agent2_role"] == "开发"
        assert req_config["status_field"] == "requirements"

    def test_get_stage_data_dict(self):
        """测试获取阶段数据（字典格式）。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        state = {"requirements": {"status": "approved"}}
        data = engine._get_stage_data("requirements", state)
        
        assert data["status"] == "approved"

    def test_get_stage_data_list_design(self):
        """测试获取设计阶段数据（列表格式）。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        state = {
            "design": [
                {"version": "v1", "status": "pending"},
                {"version": "v2", "status": "in_progress"}
            ]
        }
        data = engine._get_stage_data("design", state)
        
        assert data["version"] == "v2"
        assert data["status"] == "in_progress"

    def test_get_stage_data_empty(self):
        """测试获取空阶段数据。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        state = {}
        data = engine._get_stage_data("requirements", state)
        
        assert data == {}

    def test_get_stage_data_unknown_stage(self):
        """测试获取未知阶段数据。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        state = {"unknown": {}}
        data = engine._get_stage_data("unknown", state)
        
        assert data == {}

    def test_save_stage_data_dict(self):
        """测试保存阶段数据（字典格式）。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        state = {"requirements": {"status": "pending"}}
        engine._save_stage_data("requirements", state, {"status": "approved"})
        
        assert state["requirements"]["status"] == "approved"

    def test_can_sign_unknown_stage(self):
        """测试未知阶段不能签署。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        can_sign, message = engine.can_sign("unknown_stage", "agent1")
        
        assert can_sign is False
        assert "未知" in message

    def test_can_sign_wrong_status(self):
        """测试状态不允许签署。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        state_manager.load_state.return_value = {"requirements": {"status": "pending"}}
        
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        can_sign, message = engine.can_sign("requirements", "agent1")
        
        assert can_sign is False
        assert "状态不允许" in message

    def test_can_sign_already_signed(self):
        """测试已签署不能重复签署。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"status": "review", "agent1_signoff": True}
        }
        
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        can_sign, message = engine.can_sign("requirements", "agent1")
        
        assert can_sign is False
        assert "已经签署过" in message

    def test_can_sign_valid(self):
        """测试可以签署。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"status": "review"}
        }
        
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        can_sign, message = engine.can_sign("requirements", "agent1")
        
        assert can_sign is True
        assert message == ""


class TestSignoffOperations:
    """签署操作测试。"""

    def test_sign_success(self):
        """测试签署成功。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"status": "review"}
        }
        state_manager.add_history = Mock()
        
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        result = engine.sign("requirements", "agent1", "同意")
        
        assert result["stage"] == "requirements"
        assert result["agent"] == "agent1"
        assert result["signed"] is True
        assert result["comment"] == "同意"
        state_manager.add_history.assert_called_once()

    def test_sign_fail(self):
        """测试签署失败。"""
        from src.core.signoff import SignoffEngine, SignoffError
        
        state_manager = Mock()
        state_manager.load_state.return_value = {"requirements": {"status": "pending"}}
        
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        with pytest.raises(SignoffError):
            engine.sign("requirements", "agent1", "不同意")

    def test_reject_success(self):
        """测试拒签成功。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"status": "review"}
        }
        state_manager.add_history = Mock()
        
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        result = engine.reject("requirements", "agent1", "代码需要修改完善逻辑")
        
        assert result["stage"] == "requirements"
        assert result["agent"] == "agent1"
        assert result["rejected"] is True
        assert result["reason"] == "代码需要修改完善逻辑"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
