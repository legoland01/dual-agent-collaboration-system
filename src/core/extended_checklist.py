"""扩展检查项生成器模块。"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import yaml
import re
import os


class ChecklistType(Enum):
    """检查项类型枚举"""
    BASE_CHECK = "基础检查"
    REQUIREMENTS_TRACE = "需求追溯"
    TASK_SCOPE = "任务范围"
    QUALITY_GATE = "质量门禁"


@dataclass
class CheckItem:
    """检查项"""
    id: str
    type: str
    description: str
    severity: str
    status: str = "pending"
    details: Optional[str] = None


class ExtendedChecklistGenerator:
    """扩展的动态检查项生成器"""

    PRD_PATTERN = r'(?:FR|UR|NFR|BUG)-[\w]+(?:[-][\w]+)*'

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        """加载检查规则"""
        config_file = self.project_path / "config.yaml"
        if config_file.exists():
            with open(config_file) as f:
                config = yaml.safe_load(f) or {}
            return config.get("checklist_rules", {})
        return {
            "requirements_to_design": True,
            "design_to_code": True,
            "code_to_test": True,
            "test_coverage_threshold": 0.80,
            "test_pass_rate_threshold": 1.00,
        }

    def generate_full_checklist(self, stage: str) -> List[CheckItem]:
        """生成完整检查清单"""
        checklist = []

        checklist.extend(self._generate_base_checklist())

        if stage == "requirements":
            checklist.extend(self._generate_requirements_checklist())
        elif stage == "design":
            checklist.extend(self._generate_design_checklist())
        elif stage == "test":
            checklist.extend(self._generate_test_checklist())

        checklist.extend(self._generate_traceability_checklist())
        checklist.extend(self._generate_task_scope_checklist())
        checklist.extend(self._generate_quality_gate_checklist())

        return checklist

    def _generate_base_checklist(self) -> List[CheckItem]:
        """生成基础检查项"""
        return [
            CheckItem(
                id="BASE-001",
                type=ChecklistType.BASE_CHECK.value,
                description="所有文件已保存",
                severity="info"
            ),
            CheckItem(
                id="BASE-002",
                type=ChecklistType.BASE_CHECK.value,
                description="代码无语法错误",
                severity="error"
            )
        ]

    def _generate_requirements_checklist(self) -> List[CheckItem]:
        """生成需求阶段检查项"""
        return [
            CheckItem(
                id="REQ-001",
                type="需求检查",
                description="需求文档已评审",
                severity="warning"
            ),
            CheckItem(
                id="REQ-002",
                type="需求检查",
                description="所有功能点有唯一ID",
                severity="error"
            )
        ]

    def _generate_design_checklist(self) -> List[CheckItem]:
        """生成设计阶段检查项"""
        return [
            CheckItem(
                id="DES-001",
                type="设计检查",
                description="设计文档符合模板规范",
                severity="info"
            ),
            CheckItem(
                id="DES-002",
                type="设计检查",
                description="技术方案已评估可行性",
                severity="warning"
            )
        ]

    def _generate_test_checklist(self) -> List[CheckItem]:
        """生成测试阶段检查项"""
        return [
            CheckItem(
                id="TEST-001",
                type="测试检查",
                description="测试用例覆盖所有功能点",
                severity="error"
            ),
            CheckItem(
                id="TEST-002",
                type="测试检查",
                description="测试通过率100%",
                severity="error"
            )
        ]

    def _generate_traceability_checklist(self) -> List[CheckItem]:
        """生成需求追溯检查"""
        checklist = []
        prd_files = list(self.project_path.glob("docs/**/*requirements*.md"))

        if not prd_files:
            checklist.append(CheckItem(
                id="TRACE-001",
                type=ChecklistType.REQUIREMENTS_TRACE.value,
                description="未找到需求文档",
                severity="warning"
            ))
            return checklist

        for prd_file in prd_files[:3]:
            with open(prd_file) as f:
                content = f.read()

            prd_ids = re.findall(self.PRD_PATTERN, content)
            if prd_ids:
                checklist.append(CheckItem(
                    id=f"TRACE-{prd_file.stem[:3].upper()}-001",
                    type=ChecklistType.REQUIREMENTS_TRACE.value,
                    description=f"需求文档 {prd_file.name} 包含 {len(set(prd_ids))} 个需求ID",
                    severity="info"
                ))

        return checklist

    def _generate_task_scope_checklist(self) -> List[CheckItem]:
        """生成任务范围检查"""
        return [
            CheckItem(
                id="SCOPE-001",
                type=ChecklistType.TASK_SCOPE.value,
                description="任务范围已明确定义",
                severity="warning"
            ),
            CheckItem(
                id="SCOPE-002",
                type=ChecklistType.TASK_SCOPE.value,
                description="已完成范围内所有功能",
                severity="error"
            ),
            CheckItem(
                id="SCOPE-003",
                type=ChecklistType.TASK_SCOPE.value,
                description="无范围蔓延迹象",
                severity="warning"
            )
        ]

    def _generate_quality_gate_checklist(self) -> List[CheckItem]:
        """生成质量门禁检查"""
        checklist = []

        coverage_threshold = self.rules.get("test_coverage_threshold", 0.80)
        checklist.append(CheckItem(
            id="QUAL-001",
            type=ChecklistType.QUALITY_GATE.value,
            description=f"测试覆盖率 >= {coverage_threshold:.0%}",
            severity="error"
        ))

        pass_rate = self.rules.get("test_pass_rate_threshold", 1.00)
        checklist.append(CheckItem(
            id="QUAL-002",
            type=ChecklistType.QUALITY_GATE.value,
            description=f"测试通过率 >= {pass_rate:.0%}",
            severity="error"
        ))

        checklist.append(CheckItem(
            id="QUAL-003",
            type=ChecklistType.QUALITY_GATE.value,
            description="代码符合项目规范",
            severity="warning"
        ))

        return checklist
