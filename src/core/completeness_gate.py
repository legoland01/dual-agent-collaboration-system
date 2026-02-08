"""完整性门禁 - v2.2.2 F-PROC-001.3"""
from pathlib import Path
from typing import Optional
import re

from .compliance_engine import ComplianceEngine, ComplianceResult, ComplianceResultType


class CompletenessGate:
    """完整性门禁"""

    # 主文档命名规则
    MAIN_DOC_PATTERNS = [
        r"requirements_v\d+\.\d+\.\d+\.md$",
        r"design_v\d+\.\d+\.\d+\.md$",
        r"REVIEW_.*\.md$",
    ]

    # 子文档命名规则（不允许单独评审）
    SUB_DOC_PATTERNS = [
        r".*_v[0-9.]+_[a-z]+\d*\.md",
        r"F-[A-Z]+-\d+\.md",
    ]

    ERROR_MESSAGES = {
        "section_only_review": (
            "⛔ 无法评审: 不允许部分评审。"
            "{doc_name} 是一个完整的需求文档。"
            "请评审完整文档"
            "如需对特定章节提出意见，请在完整评审中注明。"
        ),
        "sub_doc_review": (
            "⛔ 无法评审: 不允许评审子文档。"
            "{doc_name} 是从主文档提取的子模块。"
            "请评审主文档"
        ),
    }

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)

    def _get_doc_name(self, doc_path: str) -> str:
        """获取文档名称"""
        return Path(doc_path).name

    def is_main_doc(self, doc_path: str) -> bool:
        """检查是否是主文档（非子模块）"""
        doc_name = self._get_doc_name(doc_path)

        for pattern in self.MAIN_DOC_PATTERNS:
            if re.match(pattern, doc_name):
                return True

        for pattern in self.SUB_DOC_PATTERNS:
            if re.match(pattern, doc_name):
                return False

        return True

    def is_section_only(self, review_scope: str) -> bool:
        """检查是否是仅评审章节"""
        return review_scope is not None and review_scope.strip() != ""

    def check_completeness(
        self, doc_path: str, agent_id: str, review_scope: Optional[str] = None
    ) -> ComplianceResult:
        """
        检查评审完整性

        Args:
            doc_path: 文档路径
            agent_id: Agent ID
            review_scope: 评审范围（None 或空字符串 = 评审完整文档）

        Returns:
            ComplianceResult: 检查结果
        """
        doc_name = self._get_doc_name(doc_path)

        if self.is_section_only(review_scope):
            return ComplianceResult(
                check_type="completeness",
                result_type=ComplianceResultType.DENIED,
                agent_id=agent_id,
                action="review",
                target=doc_path,
                message=self.ERROR_MESSAGES["section_only_review"].format(
                    doc_name=doc_name
                ),
            )

        if not self.is_main_doc(doc_path):
            return ComplianceResult(
                check_type="completeness",
                result_type=ComplianceResultType.DENIED,
                agent_id=agent_id,
                action="review",
                target=doc_path,
                message=self.ERROR_MESSAGES["sub_doc_review"].format(doc_name=doc_name),
            )

        return ComplianceResult(
            check_type="completeness",
            result_type=ComplianceResultType.PASSED,
            agent_id=agent_id,
            action="review",
            target=doc_path,
            message="✅ 完整性检查通过",
        )

    def find_main_doc(self, sub_doc_path: str) -> Optional[str]:
        """
        根据子文档查找主文档

        Args:
            sub_doc_path: 子文档路径

        Returns:
            Optional[str]: 主文档路径，如果未找到返回 None
        """
        sub_doc_name = self._get_doc_name(sub_doc_path)

        if not self.is_main_doc(sub_doc_path):
            main_doc_patterns = [
                ("requirements", r"requirements_v\d+\.\d+\.\d+\.md"),
                ("design", r"design_v\d+\.\d+\.\d+\.md"),
                ("review", r"REVIEW_.*\.md"),
            ]

            for category, pattern in main_doc_patterns:
                if category in sub_doc_name.lower():
                    return pattern

        return sub_doc_path

        return sub_doc_path
