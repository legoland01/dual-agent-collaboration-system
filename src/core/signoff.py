"""签署引擎模块。"""
from typing import Tuple, Optional
from dataclasses import dataclass
import re


class SignoffError(Exception):
    """签署异常基类。"""
    pass


class PermissionDeniedError(SignoffError):
    """权限不足异常。"""
    pass


class InvalidStateError(SignoffError):
    """状态无效异常。"""
    pass


class DuplicateSignoffError(SignoffError):
    """重复签署异常。"""
    pass


class RejectionError(SignoffError):
    """拒签异常。"""
    pass


@dataclass
class SignoffResult:
    """签署结果"""
    success: bool
    message: str
    synced: bool = False
    sync_error: Optional[str] = None


@dataclass
class SyncResult:
    """同步结果"""
    success: bool
    message: str


class SignoffEngine:
    """签署引擎。"""
    
    STAGE_CONFIG = {
        "requirements": {
            "agent1_role": "产品经理",
            "agent2_role": "开发",
            "status_field": "requirements"
        },
        "design": {
            "agent1_role": "产品经理",
            "agent2_role": "开发",
            "status_field": "design"
        },
        "test": {
            "agent1_role": "产品经理",
            "agent2_role": "开发",
            "status_field": "test"
        }
    }
    
    def __init__(self, state_manager, workflow_engine):
        """初始化签署引擎。"""
        self.state_manager = state_manager
        self.workflow_engine = workflow_engine
    
    def _get_stage_data(self, stage: str, state: dict) -> dict:
        """获取阶段数据（处理 design 列表和 v2.2.x 版本化结构）。"""
        config = self.STAGE_CONFIG.get(stage, {})
        status_field = config.get("status_field", stage)

        # 首先检查顶层字段（兼容旧结构）
        stage_data = state.get(status_field, {})

        # 如果顶层没有数据，检查 v2.2.x 版本结构
        if not stage_data or not isinstance(stage_data, dict):
            version_keys = [k for k in state.keys() if re.match(r'^v2\.\d+', k)]
            if version_keys:
                latest_version = sorted(version_keys, key=lambda x: [int(n) for n in re.findall(r'\d+', x)])[-1]
                version_data = state.get(latest_version, {})
                
                # test 阶段在 v2.2.x 中可能使用 "testing" 字段名
                if stage == "test":
                    stage_data = version_data.get("testing", version_data.get("test", {}))
                else:
                    stage_data = version_data.get(stage, {})

        # design 阶段是列表，需要找到当前进行中的设计文档
        if stage == "design" and isinstance(stage_data, list):
            for doc in stage_data:
                if isinstance(doc, dict) and doc.get("status") in ["in_progress", "completed", "approved"]:
                    return doc
            if stage_data and isinstance(stage_data[0], dict):
                return stage_data[0]
            return {}

        return stage_data if isinstance(stage_data, dict) else {}
    
    def _save_stage_data(self, stage: str, state: dict, stage_data: dict):
        """保存阶段数据（处理 design 列表和 v2.2.x 版本化结构）。"""
        config = self.STAGE_CONFIG.get(stage, {})
        status_field = config.get("status_field", stage)
        
        # test 阶段需要保存到 v2.2.x.testing
        if stage == "test":
            version_keys = [k for k in state.keys() if re.match(r'^v2\.\d+', k)]
            if version_keys:
                latest_version = sorted(version_keys, key=lambda x: [int(n) for n in re.findall(r'\d+', x)])[-1]
                version_data = state.get(latest_version, {})
                if "testing" in version_data:
                    version_data["testing"] = stage_data
                    self.state_manager.save_state(state)
                    return
        
        # design 阶段是列表，需要找到并更新对应的设计文档
        if stage == "design" and isinstance(state.get(status_field), list):
            for i, doc in enumerate(state[status_field]):
                if isinstance(doc, dict) and doc.get("status") in ["in_progress", "completed", "approved"]:
                    state[status_field][i] = stage_data
                    return
        else:
            state[status_field] = stage_data
    
    def can_sign(self, stage: str, agent: str) -> Tuple[bool, str]:
        """检查是否可以进行签署。"""
        if stage not in self.STAGE_CONFIG:
            return False, f"未知的签署阶段: {stage}"
        
        state = self.state_manager.load_state()
        stage_data = self._get_stage_data(stage, state)
        
        required_status = {
            "requirements": "review",
            "design": "review",
            "test": "in_progress"
        }
        
        current_status = stage_data.get("status", "")
        
        if not current_status:
            return True, ""
        
        if current_status not in [required_status.get(stage, ""), "approved", "passed"]:
            return False, f"当前阶段状态不允许签署: {current_status}"
        
        signoff_key = f"{agent}_signoff"
        if stage_data.get(signoff_key, False):
            return False, f"{agent}已经签署过"
        
        return True, ""
    
    def sign(self, stage: str, agent: str, comment: str = "") -> dict:
        """执行签署操作。"""
        can_sign, message = self.can_sign(stage, agent)
        if not can_sign:
            raise SignoffError(message)
        
        state = self.state_manager.load_state()
        stage_data = self._get_stage_data(stage, state)
        
        signoff_key = f"{agent}_signoff"
        stage_data[signoff_key] = True
        
        self._save_stage_data(stage, state, stage_data)
        
        self.state_manager.add_history(
            action="signoff",
            agent=agent,
            details=f"签署{stage}阶段: {comment}"
        )
        
        return {
            "stage": stage,
            "agent": agent,
            "signed": True,
            "comment": comment
        }
    
    def reject(self, stage: str, agent: str, reason: str) -> dict:
        """处理拒签。"""
        if len(reason) < 10:
            raise RejectionError("拒签原因必须不少于10个字符")
        
        state = self.state_manager.load_state()
        stage_data = self._get_stage_data(stage, state)
        
        stage_data[f"{agent}_signoff"] = False
        stage_data[f"{agent}_rejected"] = True
        stage_data[f"{agent}_rejection_reason"] = reason
        
        self._save_stage_data(stage, state, stage_data)
        
        self.state_manager.add_history(
            action="reject",
            agent=agent,
            details=f"拒签{stage}阶段，原因为: {reason}"
        )
        
        return {
            "stage": stage,
            "agent": agent,
            "rejected": True,
            "reason": reason
        }
    
    def get_signoff_summary(self, stage: str) -> dict:
        """获取签署摘要。"""
        if stage not in self.STAGE_CONFIG:
            return {"error": f"未知的签署阶段: {stage}"}
        
        state = self.state_manager.load_state()
        stage_data = self._get_stage_data(stage, state)
        
        return {
            "stage": stage,
            "pm_signoff": stage_data.get("pm_signoff", False),
            "dev_signoff": stage_data.get("dev_signoff", False),
            "both_signed": stage_data.get("pm_signoff", False) and stage_data.get("dev_signoff", False),
            "pm_rejected": stage_data.get("pm_rejected", False),
            "dev_rejected": stage_data.get("dev_rejected", False)
        }
    
    def check_all_signed(self, stages: list = None) -> bool:
        """检查是否所有阶段都已签署。"""
        if stages is None:
            stages = ["requirements", "design"]
        
        for stage in stages:
            summary = self.get_signoff_summary(stage)
            if "error" in summary:
                continue
            if not summary.get("both_signed", False):
                return False
        
        return True
    
    def signoff_with_sync(self, stage: str, agent: str, comment: str = "", git_helper=None) -> SignoffResult:
        """执行签署并同步到远程"""
        try:
            sign_result = self.sign(stage, agent, comment)
            
            synced = False
            sync_error = None
            
            if git_helper:
                try:
                    git_helper.push()
                    synced = True
                except Exception as e:
                    sync_error = str(e)
            
            message = f"签署成功: {stage} 阶段"
            if synced:
                message += "\n✓ 已同步到远程仓库"
            elif sync_error:
                message += f"\n⚠ 同步失败: {sync_error}"
            
            return SignoffResult(
                success=True,
                message=message,
                synced=synced,
                sync_error=sync_error
            )
        except SignoffError as e:
            return SignoffResult(
                success=False,
                message=f"签署失败: {e}"
            )
    
    def auto_trigger_signoff(self, stage: str, test_results: dict) -> dict:
        """测试通过后自动触发signoff流程
        
        Args:
            stage: 阶段名 (requirements/design/test)
            test_results: 测试结果 {"passed": int, "failed": int, "coverage": float}
            
        Returns:
            触发结果 {"triggered": bool, "action": str, "message": str}
        """
        if test_results.get("failed", 0) > 0:
            return {
                "triggered": False,
                "action": "none",
                "message": f"测试有{test_results['failed']}个失败，无法触发signoff"
            }
        
        if test_results.get("passed", 0) == 0:
            return {
                "triggered": False,
                "action": "none",
                "message": "没有通过的测试"
            }
        
        coverage = test_results.get("coverage", 0)
        min_coverage = test_results.get("min_coverage", 80)
        
        if coverage < min_coverage:
            return {
                "triggered": False,
                "action": "none",
                "message": f"代码覆盖率{coverage}%低于最低要求{min_coverage}%"
            }
        
        summary = self.get_signoff_summary(stage)
        if summary.get("both_signed"):
            return {
                "triggered": False,
                "action": "none",
                "message": f"{stage}阶段已经完成签署"
            }
        
        pending_signers = []
        if not summary.get("pm_signoff"):
            pending_signers.append("agent1")
        if not summary.get("dev_signoff"):
            pending_signers.append("agent2")
        
        return {
            "triggered": True,
            "action": "create_signoff_todo",
            "stage": stage,
            "pending_signers": pending_signers,
            "test_results": test_results,
            "message": f"测试通过，准备签署{stage}阶段，待签署: {', '.join(pending_signers)}"
        }
    
    def create_signoff_todo_from_test(self, stage: str, test_results: dict, todo_manager=None) -> dict:
        """根据测试结果创建signoff TODO
        
        Args:
            stage: 阶段名
            test_results: 测试结果
            todo_manager: TodoSyncManager实例
            
        Returns:
            创建结果
        """
        trigger_result = self.auto_trigger_signoff(stage, test_results)
        
        if not trigger_result.get("triggered"):
            return trigger_result
        
        if not todo_manager:
            from .todo_sync_manager import TodoSyncManager
            todo_manager = TodoSyncManager()
        
        created_todos = []
        
        for signer in trigger_result.get("pending_signers", []):
            signer_num = signer.replace("agent", "")
            receiver_num = "1" if signer == "agent2" else "2"
            
            todo_content = f"""签署确认: {stage}阶段

测试结果:
- 通过: {test_results.get('passed', 0)}
- 失败: {test_results.get('failed', 0)}
- 覆盖率: {test_results.get('coverage', 0)}%

请执行: oc-collab signoff {stage}"""
            
            todo = todo_manager.add_todo(
                todo_content,
                agent_id=signer_num,
                priority="high",
                receiver=receiver_num
            )
            
            if todo:
                created_todos.append({
                    "todo_id": todo.id,
                    "signer": signer,
                    "stage": stage
                })
        
        return {
            "triggered": True,
            "action": "created_todos",
            "todos": created_todos,
            "message": f"已创建{len(created_todos)}个signoff TODO"
        }
