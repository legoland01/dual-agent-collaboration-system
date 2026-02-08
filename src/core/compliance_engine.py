"""合规检查引擎 - v2.2.2"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ComplianceResultType(Enum):
    PASSED = "passed"
    DENIED = "denied"
    WARNING = "warning"


@dataclass
class ComplianceResult:
    """合规检查结果"""
    check_type: str
    result_type: ComplianceResultType
    agent_id: str
    action: str
    target: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "check_type": self.check_type,
            "result_type": self.result_type.value,
            "agent_id": self.agent_id,
            "action": self.action,
            "target": self.target,
            "message": self.message,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComplianceResult":
        return cls(
            check_type=data["check_type"],
            result_type=ComplianceResultType(data["result_type"]),
            agent_id=data["agent_id"],
            action=data["action"],
            target=data["target"],
            message=data["message"],
            details=data.get("details", {}),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )


class ComplianceEngine:
    """合规检查引擎 - 统一入口"""

    CHECK_TYPES = {
        "role_boundary": "角色边界检查",
        "doc_state": "文档状态检查",
        "completeness": "完整性检查",
    }

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.compliance_results_file = self.project_path / "state" / "compliance_results.yaml"

        self._ensure_compliance_results_file()

    def _ensure_compliance_results_file(self):
        """确保合规检查结果文件存在"""
        state_dir = self.project_path / "state"
        state_dir.mkdir(exist_ok=True)
        if not self.compliance_results_file.exists():
            self.compliance_results_file.write_text("compliance_results: []\n")

    def check(
        self,
        check_type: str,
        agent_id: str,
        action: str,
        target: str,
    ) -> ComplianceResult:
        """执行合规检查"""
        if check_type not in self.CHECK_TYPES:
            return ComplianceResult(
                check_type=check_type,
                result_type=ComplianceResultType.WARNING,
                agent_id=agent_id,
                action=action,
                target=target,
                message=f"⚠️ 未知检查类型: {check_type}",
            )

        if check_type == "role_boundary":
            from .role_boundary_checker import RoleBoundaryChecker
            checker = RoleBoundaryChecker(str(self.project_path))
            return checker.check(agent_id, action, target)

        elif check_type == "doc_state":
            from .document_state_binder import DocumentStateBinder
            binder = DocumentStateBinder(str(self.project_path))
            return binder.check(action, target, agent_id)

        elif check_type == "completeness":
            from .completeness_gate import CompletenessGate
            gate = CompletenessGate(str(self.project_path))
            return gate.check_completeness(target, agent_id)

        return ComplianceResult(
            check_type=check_type,
            result_type=ComplianceResultType.WARNING,
            agent_id=agent_id,
            action=action,
            target=target,
            message=f"⚠️ 检查类型暂未实现: {check_type}",
        )

    def check_role_boundary(
        self, agent_id: str, action: str, target: str
    ) -> ComplianceResult:
        """检查角色边界"""
        return self.check("role_boundary", agent_id, action, target)

    def check_doc_state(
        self, action: str, target: str, agent_id: str
    ) -> ComplianceResult:
        """检查文档状态"""
        return self.check("doc_state", agent_id, action, target)

    def check_completeness(
        self, target: str, agent_id: str
    ) -> ComplianceResult:
        """检查完整性"""
        return self.check("completeness", agent_id, "review", target)

    def save_result(self, result: ComplianceResult):
        """保存检查结果"""
        import yaml

        try:
            data = yaml.safe_load(self.compliance_results_file.read_text())
            results = data.get("compliance_results", [])
            results.append(result.to_dict())

            with open(self.compliance_results_file, "w") as f:
                yaml.safe_dump({"compliance_results": results}, f, allow_unicode=True)

            logger.info(f"合规检查结果已保存: {result.check_type} - {result.result_type.value}")
        except Exception as e:
            logger.error(f"保存合规检查结果失败: {e}")

    def get_results(
        self, limit: int = 10, check_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取最近的合规检查结果"""
        import yaml

        try:
            data = yaml.safe_load(self.compliance_results_file.read_text())
            results = data.get("compliance_results", [])

            if check_type:
                results = [r for r in results if r.get("check_type") == check_type]

            return sorted(results, key=lambda x: x.get("timestamp", ""), reverse=True)[
                :limit
            ]
        except Exception as e:
            logger.error(f"读取合规检查结果失败: {e}")
            return []

    def clear_results(self):
        """清空合规检查结果"""
        self._ensure_compliance_results_file()
        logger.info("合规检查结果已清空")
