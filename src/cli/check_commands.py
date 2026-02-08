"""Check CLI命令

FR-AUTO-001: CLI自动检查需求文档的完整性，检测缺失项
"""
import click
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from ..core.requirements_checker import RequirementsChecker

console = Console()


@click.command(name="requirements")
@click.argument("doc_path", required=False, type=click.Path(exists=False))
def check_requirements_command(doc_path: str):
    """检查需求文档完整性

    \b
    示例:
        oc-collab check requirements
        oc-collab check requirements docs/01-requirements/requirements_v2.2.4.md
    """
    checker = RequirementsChecker()

    if not doc_path:
        docs = checker.list_requirement_docs()
        if not docs:
            console.print("❌ 未找到需求文档")
            return

        console.print(f"找到 {len(docs)} 个需求文档:")
        for doc in docs:
            console.print(f"  - {doc}")
        console.print("\n使用 oc-collab check requirements <文档路径> 检查完整性")
        return

    doc = Path(doc_path)
    if not doc.exists():
        console.print(f"❌ 文档不存在: {doc_path}")
        return

    report = checker.generate_report(str(doc))
    console.print(Markdown(report))


@click.command(name="completeness")
@click.argument("doc_path", required=False)
def check_completeness_command(doc_path: str):
    """检查文档完整性（简要输出）"""
    checker = RequirementsChecker()

    if not doc_path:
        docs = checker.list_requirement_docs()
        if not docs:
            console.print("❌ 未找到需求文档")
            return
        doc = docs[0]
    else:
        doc = Path(doc_path)
        if not doc.exists():
            console.print(f"❌ 文档不存在: {doc_path}")
            return

    result = checker.check_completeness(str(doc))

    if result["complete"]:
        console.print(f"✅ {doc.name} 完整")
    else:
        console.print(f"❌ {doc.name} 不完整")
        if result["missing_sections"]:
            console.print(f"  缺失章节: {', '.join(result['missing_sections'])}")
        if result["工时_inconsistent"]:
            console.print("  ⚠️ 工时预估不一致")


@click.group()
def check_group():
    """检查命令组"""
    pass


check_group.add_command(check_requirements_command, "requirements")
check_group.add_command(check_completeness_command, "completeness")
