"""阶段自动推进模块。"""
from pathlib import Path
from typing import Dict, Any, Callable, Optional
from datetime import datetime
import logging

from .state_manager import StateManager
from .workflow import WorkflowEngine
from ..utils.date import get_current_time

logger = logging.getLogger(__name__)


class PhaseAdvanceEngine:
    """阶段推进引擎"""

    PHASE_TRANSITIONS: Dict[str, Dict[str, Any]] = {
        "development": {
            "condition": lambda s: s.get("development", {}).get("status") == "completed",
            "next_phase": "testing",
            "description": "开发完成，自动推进到测试阶段"
        },
        "testing": {
            "condition": lambda s: (
                s.get("test", {}).get("pm_signoff") and
                s.get("test", {}).get("dev_signoff")
            ) if s.get("test") else False,
            "next_phase": "deployment",
            "description": "测试签署完成，自动推进到部署阶段"
        },
        "deployment": {
            "condition": lambda s: s.get("deployment", {}).get("status") == "completed",
            "next_phase": "completed",
            "description": "部署完成，项目已完成"
        }
    }

    def __init__(self, project_path: str):
        """
        初始化阶段推进引擎

        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)
        self.state_manager = StateManager(project_path)
        self.workflow_engine = WorkflowEngine(self.state_manager)

    def check_condition(self, phase: str, state: Dict[str, Any]) -> bool:
        """
        检查指定阶段的条件是否满足

        Args:
            phase: 阶段名称
            state: 状态数据

        Returns:
            bool: 条件是否满足
        """
        transition = self.PHASE_TRANSITIONS.get(phase)
        if not transition:
            return False

        condition = transition.get("condition")
        if callable(condition):
            return condition(state)

        return False

    def check_and_advance(self) -> Dict[str, Any]:
        """
        检查条件并推进阶段

        Returns:
            {
                "advanced": bool,
                "from_phase": str,
                "to_phase": str,
                "reason": str,
                "message": str
            }
        """
        state = self.state_manager.load_state()
        current_phase = state.get("phase", "")

        transition = self.PHASE_TRANSITIONS.get(current_phase)

        if not transition:
            return {
                "advanced": False,
                "from_phase": current_phase,
                "to_phase": current_phase,
                "reason": "当前阶段不支持自动推进",
                "message": f"阶段 '{current_phase}' 没有配置自动推进规则"
            }

        condition = transition.get("condition")
        if callable(condition) and condition(state):
            next_phase = transition["next_phase"]
            reason = transition["description"]

            try:
                self.state_manager.update_phase(next_phase)

                self.state_manager.add_history_entry(
                    action="phase_advance",
                    agent_id="system",
                    details=reason
                )

                return {
                    "advanced": True,
                    "from_phase": current_phase,
                    "to_phase": next_phase,
                    "reason": reason,
                    "message": f"✓ 自动推进: {current_phase} → {next_phase}"
                }
            except Exception as e:
                return {
                    "advanced": False,
                    "from_phase": current_phase,
                    "to_phase": next_phase,
                    "reason": str(e),
                    "message": f"推进失败: {e}"
                }

        return {
            "advanced": False,
            "from_phase": current_phase,
            "to_phase": current_phase,
            "reason": "条件未满足",
            "message": f"无法自动推进: 条件未满足"
        }

    def manual_advance(self, target_phase: str = None, force: bool = False) -> Dict[str, Any]:
        """
        手动推进阶段

        Args:
            target_phase: 目标阶段（默认下一阶段）
            force: 是否强制推进

        Returns:
            Dict: 推进结果
        """
        state = self.state_manager.load_state()
        current_phase = state.get("phase", "")

        if target_phase is None:
            transition = self.PHASE_TRANSITIONS.get(current_phase)
            if transition:
                target_phase = transition["next_phase"]
            else:
                return {
                    "success": False,
                    "error": f"阶段 '{current_phase}' 无法自动确定下一阶段"
                }

        if not force:
            transition = self.PHASE_TRANSITIONS.get(current_phase)
            if transition:
                condition = transition.get("condition")
                if callable(condition) and not condition(state):
                    return {
                        "success": False,
                        "error": "条件未满足，请使用 --force 强制推进",
                        "current_phase": current_phase,
                        "target_phase": target_phase
                    }

        try:
            self.state_manager.update_phase(target_phase)

            self.state_manager.add_history_entry(
                action="manual_phase_advance",
                agent_id="user",
                details=f"手动推进: {current_phase} → {target_phase}"
            )

            return {
                "success": True,
                "from_phase": current_phase,
                "to_phase": target_phase,
                "message": f"✓ 已从 {current_phase} 推进到 {target_phase}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "current_phase": current_phase
            }

    def get_phase_info(self, phase: str) -> Dict[str, Any]:
        """
        获取阶段信息

        Args:
            phase: 阶段名称

        Returns:
            Dict: 阶段信息
        """
        state = self.state_manager.load_state()
        current_phase = state.get("phase", "")

        transition = self.PHASE_TRANSITIONS.get(phase, {})
        condition_met = False

        if callable(transition.get("condition")):
            condition_met = transition["condition"](state)

        return {
            "phase": phase,
            "is_current": phase == current_phase,
            "next_phase": transition.get("next_phase"),
            "description": transition.get("description", ""),
            "can_auto_advance": condition_met,
            "condition_description": self._get_condition_description(phase, state)
        }

    def _get_condition_description(self, phase: str, state: Dict[str, Any]) -> str:
        """获取条件描述"""
        descriptions = {
            "development": f"开发状态 = completed (当前: {state.get('development', {}).get('status', 'unknown')})",
            "testing": f"产品经理签署 = {state.get('test', {}).get('pm_signoff', False)}, 开发签署 = {state.get('test', {}).get('dev_signoff', False)}",
            "deployment": f"部署状态 = completed (当前: {state.get('deployment', {}).get('status', 'unknown')})"
        }
        return descriptions.get(phase, "无条件")

    def list_phases(self) -> Dict[str, Any]:
        """列出所有阶段及其状态"""
        state = self.state_manager.load_state()
        current_phase = state.get("phase", "")

        phase_order = [
            "project_init", "requirements_draft", "requirements_review",
            "requirements_approved", "design_draft", "design_review",
            "design_approved", "development", "testing", "deployment", "completed"
        ]

        result = {
            "current_phase": current_phase,
            "phases": []
        }

        for phase in phase_order:
            info = self.get_phase_info(phase)
            info["is_past"] = phase_order.index(phase) < phase_order.index(current_phase)
            result["phases"].append(info)

        return result
