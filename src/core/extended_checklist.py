"""扩展的动态检查项生成器模块。"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import yaml


class CheckStatus(Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class CheckItem:
    id: str
    title: str
    description: str
    status: CheckStatus = CheckStatus.PENDING
    details: str = ""
    requirements_id: Optional[str] = None


class ExtendedChecklistGenerator:
    """扩展的动态检查项生成器"""

    BASE_CHECKS = [
        ("format", "格式正确", "文档格式符合模板要求"),
        ("version", "版本信息", "文档包含版本号和更新日期"),
        ("completeness", "完整性", "所有章节内容完整"),
    ]

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def extract_requirements(self, doc_path: str) -> List[Dict]:
        """从文档中提取需求列表"""
        requirements = []
        try:
            with open(doc_path, 'r') as f:
                content = f.read()

            import re
            pattern = r'(?:FR|UR|NFR|BUG)-[A-Za-z0-9][A-Za-z0-9-]*'
            matches = re.findall(pattern, content)

            unique_ids = list(dict.fromkeys(matches))
            for req_id in unique_ids:
                requirements.append({"id": req_id, "description": f"需求 {req_id}"})
        except Exception:
            pass

        return requirements

    def get_test_coverage(self) -> float:
        """获取测试覆盖率"""
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "-m", "pytest", "--cov=src", "--cov-report=term-missing"],
                capture_output=True,
                text=True,
                cwd=self.project_path
            )
            for line in result.stdout.split('\n'):
                if 'TOTAL' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        return float(parts[-2].replace('%', '').replace('XX', '0')) / 100
        except Exception:
            pass
        return 0.0

    def generate_base_checklist(self) -> List[CheckItem]:
        """生成基础检查清单"""
        checklist = []
        for check_id, title, description in self.BASE_CHECKS:
            checklist.append(CheckItem(
                id=f"base_{check_id}",
                title=title,
                description=description
            ))
        return checklist

    def generate_requirements_checklist(self, doc_path: str) -> List[CheckItem]:
        """生成需求文档检查清单"""
        checklist = self.generate_base_checklist()

        requirements = self.extract_requirements(doc_path)
        for req in requirements:
            checklist.extend([
                CheckItem(
                    id=f"req_{req['id']}_unique",
                    title=f"需求 {req['id']} - 唯一ID",
                    description="需求是否有唯一标识",
                    requirements_id=req['id']
                ),
                CheckItem(
                    id=f"req_{req['id']}_acceptance",
                    title=f"需求 {req['id']} - 验收标准",
                    description="需求是否有明确的验收标准",
                    requirements_id=req['id']
                ),
            ])

        return checklist

    def generate_traceability_checklist(self) -> List[CheckItem]:
        """生成需求追溯检查清单"""
        checklist = []

        req_dir = self.project_path / "docs" / "01-requirements"
        design_dir = self.project_path / "docs" / "02-design"

        if not req_dir.exists() or not design_dir.exists():
            return checklist

        import re
        req_pattern = r'(?:FR|UR|NFR|BUG)-[A-Za-z0-9][A-Za-z0-9-]*'

        design_contents = {}
        for design_file in design_dir.glob("*.md"):
            with open(design_file) as f:
                design_contents[design_file.name] = f.read()

        for req_file in req_dir.glob("*.md"):
            with open(req_file) as f:
                content = f.read()
                reqs = set(re.findall(req_pattern, content))

                for req in reqs:
                    found = False
                    for design_content in design_contents.values():
                        if req in design_content:
                            found = True
                            break

                    checklist.append(CheckItem(
                        id=f"trace_{req}",
                        title=f"追溯检查 - {req}",
                        description=f"需求 {req} 是否有对应设计" if not found else f"需求 {req} 已有对应设计",
                        status=CheckStatus.FAILED if not found else CheckStatus.PASSED,
                        details=f"未找到 {req} 对应的设计文档" if not found else ""
                    ))

        return checklist

    def generate_quality_gate_checklist(self) -> List[CheckItem]:
        """生成质量门禁检查清单"""
        checklist = []

        coverage = self.get_test_coverage()
        COVERAGE_THRESHOLD = 0.80

        checklist.append(CheckItem(
            id="quality_coverage",
            title=f"测试覆盖率 - {coverage:.0%}",
            description=f"覆盖率 >= {COVERAGE_THRESHOLD:.0%}" if coverage >= COVERAGE_THRESHOLD else f"覆盖率 < {COVERAGE_THRESHOLD:.0%}",
            status=CheckStatus.PASSED if coverage >= COVERAGE_THRESHOLD else CheckStatus.FAILED
        ))

        return checklist

    def generate_full_checklist(self, stage: str, doc_path: str = None) -> List[CheckItem]:
        """生成完整检查清单"""
        checklist = []

        checklist.extend(self.generate_base_checklist())

        if stage == "requirements" and doc_path:
            checklist.extend(self.generate_requirements_checklist(doc_path))

        checklist.extend(self.generate_traceability_checklist())
        checklist.extend(self.generate_quality_gate_checklist())

        return checklist

    def render_checklist(self, checklist: List[CheckItem], title: str) -> str:
        """渲染检查清单为字符串"""
        lines = [f"┌─ {title} ─", "│"]

        passed = sum(1 for item in checklist if item.status == CheckStatus.PASSED)
        failed = sum(1 for item in checklist if item.status == CheckStatus.FAILED)
        warnings = sum(1 for item in checklist if item.status == CheckStatus.WARNING)

        lines.append(f"│ 通过项: {passed}")
        lines.append(f"│ 未通过项: {failed}")
        lines.append(f"│ 警告项: {warnings}")
        lines.append("│")

        status_icons = {
            CheckStatus.PENDING: "○",
            CheckStatus.PASSED: "✓",
            CheckStatus.FAILED: "✗",
            CheckStatus.WARNING: "⚠",
        }

        for item in checklist:
            icon = status_icons.get(item.status, "○")
            lines.append(f"│ {icon} {item.title}")
            if item.details:
                for detail_line in item.details.split('\n')[:2]:
                    lines.append(f"│   {detail_line}")

        lines.append("│")
        lines.append("└" + "─" * 40)

        return '\n'.join(lines)
