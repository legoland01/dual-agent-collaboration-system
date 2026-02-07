"""变更合规检查器模块。"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import re
import logging


logger = logging.getLogger(__name__)


@dataclass
class ComplianceResult:
    """合规检查结果"""
    valid: bool
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class Conflict:
    """冲突信息"""
    type: str
    file: str
    description: str
    details: str


class ChangeComplianceChecker:
    """变更合规检查器"""

    PRD_PATTERN = r'(?:FR|UR|NFR|BUG)-[\w]+(?:[-][\w]+)*'
    RFC_PATTERN = r'RFC-[\d]+'

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def check_prd_compliance(self, prd_file: str) -> ComplianceResult:
        """检查 PRD 合规性"""
        result = ComplianceResult(valid=True)

        if not Path(prd_file).exists():
            result.valid = False
            result.violations.append(f"PRD 文件不存在: {prd_file}")
            return result

        with open(prd_file, 'r') as f:
            content = f.read()

        if "## 签署确认" not in content:
            result.violations.append("PRD 缺少签署确认章节")
            result.suggestions.append("请添加签署确认表格")

        prd_ids = re.findall(self.PRD_PATTERN, content)
        if prd_ids:
            result.warnings.append(f"发现 {len(set(prd_ids))} 个需求 ID，建议检查追溯性")

        return result

    def check_rfc_compliance(self, rfc_file: str, prd_file: Optional[str] = None) -> ComplianceResult:
        """检查 RFC 合规性"""
        result = ComplianceResult(valid=True)

        if not Path(rfc_file).exists():
            result.valid = False
            result.violations.append(f"RFC 文件不存在: {rfc_file}")
            return result

        with open(rfc_file, 'r') as f:
            content = f.read()

        rfc_ids = re.findall(self.RFC_PATTERN, content)
        if rfc_ids:
            result.suggestions.append(f"发现 {len(set(rfc_ids))} 个 RFC 引用")

        if prd_file and Path(prd_file).exists():
            with open(prd_file, 'r') as f:
                prd_content = f.read()

            if content.strip()[-100:] in prd_content[-200:]:
                result.warnings.append("RFC 内容可能已包含在 PRD 中，可作为记录无需单独评审")

        return result

    def detect_conflicts(self, prd_file: str, rfc_file: str) -> List[Conflict]:
        """检测 PRD 与 RFC 之间的冲突"""
        conflicts = []

        if not Path(prd_file).exists() or not Path(rfc_file).exists():
            return conflicts

        with open(prd_file, 'r') as f:
            prd_content = f.read()

        with open(rfc_file, 'r') as f:
            rfc_content = f.read()

        prd_ids = set(re.findall(self.PRD_PATTERN, prd_content))
        rfc_refs = set(re.findall(self.RFC_PATTERN, rfc_content))

        for prd_id in prd_ids:
            for rfc_ref in rfc_refs:
                if prd_id in rfc_content and prd_id not in rfc_ref:
                    conflicts.append(Conflict(
                        type="内容冲突",
                        file=f"PRD vs RFC",
                        description=f"需求 {prd_id} 在 RFC 中被引用，但 RFC 编号不一致",
                        details=f"PRD 引用: {prd_id}, RFC 内容: 包含 {prd_id}"
                    ))

        return conflicts

    def handle_violation(self, violation_type: str) -> Dict[str, str]:
        """处理违规行为"""
        violation_handlers = {
            "missing_signoff": {
                "action": "block",
                "message": "缺少签署确认章节，无法继续",
                "severity": "error"
            },
            "missing_requirements_id": {
                "action": "warn",
                "message": "未找到需求 ID，请检查文档格式",
                "severity": "warning"
            },
            "conflict_detected": {
                "action": "block",
                "message": "检测到内容冲突，请先解决冲突",
                "severity": "error"
            },
            "rfc_already_in_prd": {
                "action": "suggest",
                "message": "RFC 内容可能已包含在 PRD 中，可考虑合并",
                "severity": "info"
            }
        }

        return violation_handlers.get(violation_type, {
            "action": "unknown",
            "message": f"未知的违规类型: {violation_type}",
            "severity": "error"
        })
