"""SignoffEngine 单元测试。

测试用例：
- 签署配置
- 签署操作
- 拒签操作
- 签署状态检查
"""
import pytest
from unittest.mock import Mock, patch


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
        
        assert engine.state_manager == state_manager
        assert engine.workflow_engine == workflow_engine

    def test_stage_config(self):
        """测试阶段配置。"""
        from src.core.signoff import SignoffEngine
        
        config = SignoffEngine.STAGE_CONFIG
        
        assert "requirements" in config
        assert "design" in config
        assert "test" in config

    def test_get_stage_data_dict(self):
        """测试获取阶段数据（字典格式）。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        state = {"requirements": {"status": "pending"}}
        result = engine._get_stage_data("requirements", state)
        
        assert result == {"status": "pending"}

    def test_get_stage_data_list_design(self):
        """测试获取设计阶段数据（列表格式）。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        state = {"design": [
            {"name": "设计文档1", "status": "in_progress"},
            {"name": "设计文档2", "status": "completed"}
        ]}
        result = engine._get_stage_data("design", state)
        
        assert result["name"] == "设计文档1"
        assert result["status"] == "in_progress"

    def test_get_stage_data_empty(self):
        """测试获取空阶段数据。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        state = {}
        result = engine._get_stage_data("requirements", state)
        
        assert result == {}

    def test_get_stage_data_unknown_stage(self):
        """测试获取未知阶段数据。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        state = {"unknown": {}}
        result = engine._get_stage_data("unknown", state)
        
        assert result == {}

    def test_save_stage_data_dict(self):
        """测试保存阶段数据（字典格式）。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        state = {"requirements": {}}
        engine._save_stage_data("requirements", state, {"status": "review"})
        
        assert state["requirements"]["status"] == "review"

    def test_can_sign_unknown_stage(self):
        """测试未知阶段不能签署。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        can_sign, message = engine.can_sign("unknown", "agent1")
        
        assert can_sign is False
        assert "未知" in message

    def test_can_sign_wrong_status(self):
        """测试状态不对不能签署。"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"status": "pending"}
        }
        
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)
        
        can_sign, message = engine.can_sign("requirements", "agent1")
        
        assert can_sign is False
        assert "不允许签署" in message

    def test_can_sign_already_signed(self):
        """测试已经签署不能再次签署。"""
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
        """测试可以签署的情况。"""
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


class TestSignoffEngineExtended:
    """SignoffEngine 扩展测试。"""

    def test_save_stage_data_list(self):
        """测试保存设计阶段数据（列表格式）。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        state = {"design": [
            {"name": "设计文档1", "status": "in_progress"},
            {"name": "设计文档2", "status": "completed"}
        ]}
        engine._save_stage_data("design", state, {"name": "设计文档1", "status": "approved"})

        assert state["design"][0]["status"] == "approved"

    def test_get_stage_data_list_completed(self):
        """测试获取已完成状态的设计文档。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        state = {"design": [
            {"name": "设计文档1", "status": "draft"},
            {"name": "设计文档2", "status": "completed"}
        ]}
        result = engine._get_stage_data("design", state)

        assert result["name"] == "设计文档2"
        assert result["status"] == "completed"

    def test_get_stage_data_list_approved(self):
        """测试获取已批准状态的设计文档。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        state = {"design": [
            {"name": "设计文档1", "status": "draft"},
            {"name": "设计文档2", "status": "approved"}
        ]}
        result = engine._get_stage_data("design", state)

        assert result["name"] == "设计文档2"
        assert result["status"] == "approved"

    def test_get_signoff_summary_unknown_stage(self):
        """测试获取未知阶段的签署摘要。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        result = engine.get_signoff_summary("unknown")

        assert "error" in result

    def test_get_signoff_summary_with_data(self):
        """测试获取签署摘要（带数据）。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"pm_signoff": True, "dev_signoff": True}
        }
        workflow_engine = Mock()

        engine = SignoffEngine(state_manager, workflow_engine)

        result = engine.get_signoff_summary("requirements")

        assert result["pm_signoff"] is True
        assert result["dev_signoff"] is True
        assert result["both_signed"] is True

    def test_check_all_signed_empty_stages(self):
        """测试检查所有阶段签署（空列表）。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        result = engine.check_all_signed([])

        assert result is True

    def test_check_all_signed_with_rejection(self):
        """测试检查所有阶段签署（包含拒签）。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"pm_signoff": True, "dev_signoff": False, "pm_rejected": False, "dev_rejected": True}
        }
        workflow_engine = Mock()

        engine = SignoffEngine(state_manager, workflow_engine)

        result = engine.check_all_signed(["requirements"])

        assert result is False

    def test_can_sign_test_status_in_progress(self):
        """测试测试阶段状态为进行中时可以签署。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        state_manager.load_state.return_value = {
            "test": {"status": "in_progress"}
        }
        workflow_engine = Mock()

        engine = SignoffEngine(state_manager, workflow_engine)

        can_sign, message = engine.can_sign("test", "agent1")

        assert can_sign is True

    def test_get_stage_data_design_empty_list(self):
        """测试设计阶段空列表。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        state = {"design": []}
        result = engine._get_stage_data("design", state)

        assert result == {}

    def test_get_stage_data_design_first_fallback(self):
        """测试设计阶段找不到进行中时返回第一个。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        state = {"design": [{"name": "设计1", "status": "draft"}]}
        result = engine._get_stage_data("design", state)

        assert result["name"] == "设计1"


class TestSignoffReject:
    """签署拒签测试。"""

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
        assert len(result["reason"]) >= 10

    def test_reject_reason_too_short(self):
        """测试拒签原因太短。"""
        from src.core.signoff import SignoffEngine, RejectionError

        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        with pytest.raises(RejectionError):
            engine.reject("requirements", "agent1", "太短")


class TestSignoffSummary:
    """签署摘要测试。"""

    def test_get_signoff_summary_unknown_stage(self):
        """测试获取未知阶段的签署摘要。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        result = engine.get_signoff_summary("unknown")

        assert "error" in result

    def test_get_signoff_summary_with_data(self):
        """测试获取签署摘要（带数据）。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"pm_signoff": True, "dev_signoff": True}
        }
        workflow_engine = Mock()

        engine = SignoffEngine(state_manager, workflow_engine)

        result = engine.get_signoff_summary("requirements")

        assert result["pm_signoff"] is True
        assert result["dev_signoff"] is True
        assert result["both_signed"] is True

    def test_get_signoff_summary_with_rejection(self):
        """测试获取签署摘要（带拒签）。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {
                "pm_signoff": True,
                "dev_signoff": False,
                "pm_rejected": False,
                "dev_rejected": True
            }
        }
        workflow_engine = Mock()

        engine = SignoffEngine(state_manager, workflow_engine)

        result = engine.get_signoff_summary("requirements")

        assert result["dev_rejected"] is True
        assert result["both_signed"] is False


class TestSignoffCheckAllSigned:
    """检查所有签署测试。"""

    def test_check_all_signed_empty_stages(self):
        """测试检查所有阶段签署（空列表）。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        result = engine.check_all_signed([])

        assert result is True

    def test_check_all_signed_with_stages(self):
        """测试检查所有阶段签署（指定阶段）。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"pm_signoff": True, "dev_signoff": True}
        }
        workflow_engine = Mock()

        engine = SignoffEngine(state_manager, workflow_engine)

        result = engine.check_all_signed(["requirements"])

        assert result is True

    def test_check_all_signed_with_rejection(self):
        """测试检查所有阶段签署（包含拒签）。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {
                "pm_signoff": True,
                "dev_signoff": False,
                "pm_rejected": False,
                "dev_rejected": True
            }
        }
        workflow_engine = Mock()

        engine = SignoffEngine(state_manager, workflow_engine)

        result = engine.check_all_signed(["requirements"])

        assert result is False

    def test_check_all_signed_with_unknown_stage(self):
        """测试检查所有阶段签署（包含未知阶段）。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        result = engine.check_all_signed(["unknown_stage"])

        assert result is True

    def test_check_all_signed_default_stages(self):
        """测试检查所有阶段签署（默认阶段列表）。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"pm_signoff": True, "dev_signoff": True},
            "design": {"pm_signoff": True, "dev_signoff": True}
        }
        workflow_engine = Mock()

        engine = SignoffEngine(state_manager, workflow_engine)

        result = engine.check_all_signed()

        assert result is True


class TestSignoffWithSync:
    """签署同步功能测试。"""

    def test_signoff_with_sync_success(self):
        """测试签署并同步成功。"""
        from src.core.signoff import SignoffEngine, SignoffResult

        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"status": "review"}
        }
        state_manager.add_history = Mock()

        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        git_helper = Mock()
        git_helper.push.return_value = None

        result = engine.signoff_with_sync("requirements", "agent1", "同意", git_helper)

        assert result.success is True
        assert result.synced is True
        assert "已同步到远程仓库" in result.message
        git_helper.push.assert_called_once()

    def test_signoff_with_sync_git_failed(self):
        """测试签署成功但同步失败。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"status": "review"}
        }
        state_manager.add_history = Mock()

        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        git_helper = Mock()
        git_helper.push.side_effect = Exception("Network error")

        result = engine.signoff_with_sync("requirements", "agent1", "同意", git_helper)

        assert result.success is True
        assert result.synced is False
        assert result.sync_error == "Network error"
        assert "同步失败" in result.message

    def test_signoff_with_sync_no_git_helper(self):
        """测试没有 Git helper 时签署成功。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"status": "review"}
        }
        state_manager.add_history = Mock()

        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        result = engine.signoff_with_sync("requirements", "agent1", "同意", git_helper=None)

        assert result.success is True
        assert result.synced is False
        assert result.sync_error is None

    def test_signoff_with_sync_sign_fail(self):
        """测试签署失败时返回失败结果。"""
        from src.core.signoff import SignoffEngine

        state_manager = Mock()
        state_manager.load_state.return_value = {
            "requirements": {"status": "pending"}
        }

        workflow_engine = Mock()
        engine = SignoffEngine(state_manager, workflow_engine)

        git_helper = Mock()

        result = engine.signoff_with_sync("requirements", "agent1", "同意", git_helper)

        assert result.success is False
        assert "签署失败" in result.message
        assert result.synced is False
        git_helper.push.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
