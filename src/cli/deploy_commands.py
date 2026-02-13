"""Deploy CLI命令

F-DEPLOY-002: 部署文档同步自动化
"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from ..core.deploy_doc_sync import DeployDocSync

console = Console()


@click.group()
def deploy_group():
    """部署相关命令"""
    pass


@click.command(name="check-docs")
@click.option("--version", "-v", help="版本号", required=True)
@click.option("--changes", "-c", multiple=True, help="变更描述")
def deploy_check_docs(version: str, changes: tuple):
    """
    检查部署文档同步状态。

    示例:
        oc-collab deploy check-docs --version 2.2.9
        oc-collab deploy check-docs -v 2.2.9 -c "新增合规检查命令" -c "修复Bug"
    """
    sync = DeployDocSync()

    check_result = sync.check_docs_sync(version)

    table = Table(title=f"部署文档检查 (版本: {version})")
    table.add_column("检查项", style="cyan")
    table.add_column("状态", style="magenta")
    table.add_column("说明", style="green")

    for check in check_result["checks"]:
        status = "✅" if check["passed"] else "❌"
        table.add_row(
            check["name"],
            status,
            check["message"]
        )

    console.print(table)

    if not check_result["ready"]:
        console.print("\n[bold]建议操作:[/bold]")
        for check in check_result["checks"]:
            if not check["passed"] and check.get("suggestion"):
                console.print(f"  • {check['name']}: {check['suggestion']}")

        console.print(Panel(
            "请运行 'oc-collab deploy sync-docs' 同步文档，或手动更新文档后重新检查",
            title="下一步操作",
            style="yellow"
        ))
    else:
        console.print(Panel(
            "✅ 部署文档已同步，可以继续部署",
            title="检查通过",
            style="green"
        ))


@click.command(name="sync-docs")
@click.option("--version", "-v", help="版本号", required=True)
@click.option("--changes", "-c", multiple=True, help="变更描述", default=[])
def deploy_sync_docs(version: str, changes: tuple):
    """
    同步部署文档。

    示例:
        oc-collab deploy sync-docs --version 2.2.9
        oc-collab deploy sync-docs -v 2.2.9 -c "新增合规检查命令" -c "修复Bug"
    """
    sync = DeployDocSync()

    changes_list = list(changes) if changes else []

    changelog_success = sync.sync_changelog(version, changes_list)
    readme_success = sync.sync_readme([])

    if changelog_success and readme_success:
        console.print(Panel(
            f"✅ 部署文档已同步 (版本: {version})",
            title="同步完成",
            style="green"
        ))
    else:
        console.print(Panel(
            "❌ 部署文档同步失败",
            title="同步失败",
            style="red"
        ))
        if not changelog_success:
            console.print("  • CHANGELOG.md同步失败")
        if not readme_success:
            console.print("  • README.md同步失败")


deploy_group.add_command(deploy_check_docs, "check-docs")
deploy_group.add_command(deploy_sync_docs, "sync-docs")
