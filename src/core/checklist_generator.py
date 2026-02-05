import re
from pathlib import Path
from typing import List, Dict, Optional
from .checklist_generator_types import CheckItem, CheckStatus


class ChecklistGenerator:
    """动态 checklist 生成器"""

    BASE_CHECKS = [
        ("format", "格式正确", "文档格式符合模板要求"),
        ("version", "版本信息", "文档包含版本号和更新日期"),
        ("completeness", "完整性", "所有章节内容完整"),
    ]

    def __init__(self, project_path: str):
        self.project_path = project_path

    def extract_requirements(self, doc_path: str) -> List[Dict]:
        """从需求文档中提取需求列表"""
        requirements = []
        try:
            with open(doc_path, 'r') as f:
                content = f.read()

            pattern = r'(?:FR|UR|NFR|BUG)-[A-Za-z0-9][A-Za-z0-9-]*'
            matches = re.findall(pattern, content)

            unique_ids = list(dict.fromkeys(matches))

            for req_id in unique_ids:
                requirements.append({
                    "id": req_id,
                    "description": f"需求 {req_id}"
                })
        except Exception:
            pass

        return requirements

    def find_orphan_items(self, doc_type: str) -> List[str]:
        """查找未关联的条目"""
        orphans = []

        if doc_type == "requirements":
            req_pattern = r'(?:FR|UR|NFR|BUG)-[A-Za-z0-9][A-Za-z0-9-]*'
            design_pattern = r'(?:FR|UR|NFR|BUG)-[A-Za-z0-9][A-Za-z0-9-]*'

            req_dir = Path(self.project_path) / "docs" / "01-requirements"
            design_dir = Path(self.project_path) / "docs" / "02-design"

            if not req_dir.exists() or not design_dir.exists():
                return []

            req_docs = list(req_dir.glob("*.md"))
            design_docs = list(design_dir.glob("*.md"))

            design_contents = {}
            for design_doc in design_docs:
                with open(design_doc) as f:
                    design_contents[design_doc.name] = f.read()

            for req_doc in req_docs:
                with open(req_doc) as f:
                    content = f.read()
                    reqs = set(re.findall(req_pattern, content))

                    for req in reqs:
                        found = False
                        for design_content in design_contents.values():
                            if req in design_content:
                                found = True
                                break
                        if not found and req not in orphans:
                            orphans.append(req)

        return orphans

    def generate_requirements_checklist(self, doc_path: str) -> List[CheckItem]:
        """生成需求文档检查清单"""
        checklist = []

        for check_id, title, description in self.BASE_CHECKS:
            checklist.append(CheckItem(
                id=f"req_base_{check_id}",
                title=title,
                description=description
            ))

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
                CheckItem(
                    id=f"req_{req['id']}_description",
                    title=f"需求 {req['id']} - 详细描述",
                    description="需求描述是否完整",
                    requirements_id=req['id']
                ),
                CheckItem(
                    id=f"req_{req['id']}_design",
                    title=f"需求 {req['id']} - 设计关联",
                    description="是否有对应的设计文档",
                    requirements_id=req['id']
                ),
                CheckItem(
                    id=f"req_{req['id']}_test",
                    title=f"需求 {req['id']} - 测试关联",
                    description="是否有对应的测试用例",
                    requirements_id=req['id']
                ),
            ])

        orphans = self.find_orphan_items("requirements")
        if orphans:
            checklist.append(CheckItem(
                id="req_traceability",
                title="追溯性",
                description=f"发现 {len(orphans)} 个未关联的需求，需要处理",
                status=CheckStatus.WARNING,
                details=", ".join(orphans)
            ))

        return checklist

    def generate_design_checklist(self, doc_path: str) -> List[CheckItem]:
        """生成设计文档检查清单"""
        checklist = []

        for check_id, title, description in self.BASE_CHECKS:
            checklist.append(CheckItem(
                id=f"design_base_{check_id}",
                title=title,
                description=description
            ))

        checklist.extend([
            CheckItem(
                id="design_requirements_link",
                title="需求关联",
                description="设计是否关联到具体需求"
            ),
            CheckItem(
                id="design_implementation",
                title="实现方案",
                description="实现方案是否具体可行"
            ),
            CheckItem(
                id="design_edge_cases",
                title="边界条件",
                description="是否覆盖所有边界情况"
            ),
        ])

        return checklist

    def generate_test_checklist(self, doc_path: str) -> List[CheckItem]:
        """生成测试文档检查清单"""
        checklist = []

        for check_id, title, description in self.BASE_CHECKS:
            checklist.append(CheckItem(
                id=f"test_base_{check_id}",
                title=title,
                description=description
            ))

        checklist.extend([
            CheckItem(
                id="test_requirements_link",
                title="需求覆盖",
                description="测试是否覆盖所有需求"
            ),
            CheckItem(
                id="test_coverage",
                title="测试覆盖率",
                description="测试覆盖率是否达到标准"
            ),
        ])

        return checklist

    def render_checklist(self, checklist: List[CheckItem], title: str) -> str:
        """渲染 checklist 为字符串"""
        lines = [f"┌─ {title} ─", "│"]

        passed = sum(1 for item in checklist if item.status == CheckStatus.PASSED)
        failed = sum(1 for item in checklist if item.status == CheckStatus.FAILED)
        warnings = sum(1 for item in checklist if item.status == CheckStatus.WARNING)

        lines.append(f"│ 通过项: {passed}")
        lines.append(f"│ 未通过项: {failed}")
        lines.append(f"│ 警告项: {warnings}")
        lines.append("│")

        for item in checklist:
            status_icon = {
                CheckStatus.PENDING: "○",
                CheckStatus.PASSED: "✓",
                CheckStatus.FAILED: "✗",
                CheckStatus.WARNING: "⚠",
            }[item.status]

            lines.append(f"│ {status_icon} {item.title}")
            if item.details:
                for detail_line in item.details.split('\n')[:2]:
                    lines.append(f"│   {detail_line}")

        lines.append("│")
        lines.append("└" + "─" * 40)

        return '\n'.join(lines)
