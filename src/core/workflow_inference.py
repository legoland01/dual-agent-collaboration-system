"""主动流程推理引擎模块。"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """合规级别"""
    VALID = "valid"
    WARNING = "warning"
    VIOLATION = "violation"


@dataclass
class ComplianceResult:
    """合规检查结果"""
    valid: bool
    level: ComplianceLevel
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class InferenceResult:
    """流程推理结果"""
    current_phase: str
    next_phases: List[str]
    suggestion: str
    compliance_check: ComplianceResult
    unknown: bool = False


class WorkflowInferenceEngine:
    """主动流程推理引擎"""

    PHASE_SEQUENCE = {
        "requirements": ["design", "development", "testing"],
        "design": ["development", "testing"],
        "development": ["testing"],
        "testing": ["deployment"],
    }

    PHASE_NEXT = {
        "requirements": "设计阶段",
        "design": "开发阶段",
        "development": "测试阶段",
        "testing": "部署阶段",
    }

    def __init__(self, project_path: str, state_manager):
        """初始化流程推理引擎"""
        self.project_path = project_path
        self.state_manager = state_manager

    def infer_next_action(self) -> InferenceResult:
        """根据当前状态推理下一步应该执行的操作"""
        try:
            current_state = self.state_manager.load_state()
            phase = current_state.get("phase", current_state.get("project", {}).get("phase", "unknown"))

            if phase == "unknown":
                return InferenceResult(
                    current_phase="unknown",
                    next_phases=[],
                    suggestion="请先初始化项目: oc-collab project init",
                    compliance_check=ComplianceResult(
                        valid=False,
                        level=ComplianceLevel.VIOLATION,
                        violations=["无法确定当前流程状态"],
                        suggestions=["请先初始化项目"]
                    ),
                    unknown=True
                )

            next_phases = self.PHASE_SEQUENCE.get(phase, [])

            compliance = self._run_compliance_check(phase, current_state)

            if next_phases:
                suggestion = f"当前阶段: {phase}\n建议: 进入 {self.PHASE_NEXT.get(phase, phase)}"
            else:
                suggestion = f"当前阶段: {phase}\n可选: 无（流程已完成）"

            return InferenceResult(
                current_phase=phase,
                next_phases=next_phases,
                suggestion=suggestion,
                compliance_check=compliance
            )

        except Exception as e:
            logger.error(f"流程推理失败: {e}")
            return InferenceResult(
                current_phase="unknown",
                next_phases=[],
                suggestion=f"推理失败: {e}",
                compliance_check=ComplianceResult(
                    valid=False,
                    level=ComplianceLevel.VIOLATION,
                    violations=[str(e)],
                    suggestions=["请检查项目状态"]
                ),
                unknown=True
            )

    def _run_compliance_check(self, phase: str, current_state: Dict[str, Any]) -> ComplianceResult:
        """运行合规检查"""
        violations = []
        warnings = []
        suggestions = []

        if phase == "unknown":
            violations.append("无法确定当前流程状态")
            suggestions.append("请先初始化项目")

        if phase == "requirements":
            requirements_status = current_state.get("requirements", {})
            if isinstance(requirements_status, dict):
                if not requirements_status.get("pm_signoff") or not requirements_status.get("dev_signoff"):
                    violations.append("需求阶段尚未完成签署")
                    suggestions.append("请先完成需求评审和签署")

        elif phase == "design":
            design_status = current_state.get("design", {})
            if isinstance(design_status, dict):
                if not design_status.get("pm_signoff") or not design_status.get("dev_signoff"):
                    violations.append("设计阶段尚未完成签署")
                    suggestions.append("请先完成设计评审和签署")
            elif isinstance(design_status, list):
                if not design_status:
                    violations.append("没有设计文档")
                    suggestions.append("请先创建设计文档")

        return ComplianceResult(
            valid=len(violations) == 0,
            level=ComplianceLevel.VIOLATION if violations else ComplianceLevel.VALID,
            violations=violations,
            warnings=warnings,
            suggestions=suggestions
        )

    def validate_phase_transition(self, from_phase: str, to_phase: str) -> ComplianceResult:
        """验证阶段转换是否合规"""
        valid_transitions = self.PHASE_SEQUENCE.get(from_phase, [])

        if to_phase not in valid_transitions:
            return ComplianceResult(
                valid=False,
                level=ComplianceLevel.VIOLATION,
                violations=[f"阶段顺序不正确: {from_phase} → {to_phase}"],
                suggestions=[f"从 {from_phase} 阶段只能转换到: {', '.join(valid_transitions)}"]
            )

        return ComplianceResult(
            valid=True,
            level=ComplianceLevel.VALID,
            violations=[],
            suggestions=[f"✓ {from_phase} → {to_phase} 符合流程规范"]
        )

    def get_workflow_status(self) -> str:
        """获取工作流状态"""
        result = self.infer_next_action()
        return f"[{result.current_phase.upper()}] - {result.suggestion}"
