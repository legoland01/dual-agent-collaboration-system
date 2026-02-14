"""
完整部署CLI命令

提供 oc-collab deploy full 命令（执行完整部署流程）
"""

import click
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rprint

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.deployment_orchestrator import DeploymentOrchestrator, DeploymentStep
from src.core.version_manager import VersionManager, VersionError
from src.core.package_builder import PackageBuilder, BuildError
from src.core.pypi_uploader import PyPIUploader, UploadError
from src.core.git_pusher import GitPusher, GitError
from src.core.deploy_verifier import DeployVerifier, VerificationError
from src.core.state_updater import StateUpdater, StateUpdateError

console = Console()


@click.command(name="full")
@click.option("--version", "-v", type=str, help="指定版本号（默认自动读取）")
@click.option("--dry-run", is_flag=True, help="预览模式，不执行实际变更")
@click.option("--skip-git", is_flag=True, help="跳过Git推送步骤")
@click.option("--skip-pypi", is_flag=True, help="跳过PyPI上传步骤")
@click.option("--verify-only", is_flag=True, help="仅执行验证")
@click.option("--verbose", "-V", is_flag=True, help="输出详细日志")
def deploy_full(version: Optional[str],
                dry_run: bool,
                skip_git: bool,
                skip_pypi: bool,
                verify_only: bool,
                verbose: bool):
    """
    执行完整部署流程

    示例:\n
      oc-collab deploy full           # 执行完整部署\n
      oc-collab deploy full --dry-run      # 预览模式\n
      oc-collab deploy full --version 2.2.12  # 指定版本\n
      oc-collab deploy full --skip-git     # 跳过Git\n
      oc-collab deploy full --verify-only  # 仅验证
    """
    rprint("[bold]🚀 开始部署流程[/bold]")

    orchestrator = DeploymentOrchestrator(dry_run=dry_run, verbose=verbose)

    version = version or _get_current_version()

    if not dry_run and not verify_only:
        rprint(f"📦 版本: [cyan]{version}[/cyan]")

    _setup_deployment_steps(orchestrator, version, dry_run, verbose)

    try:
        result = orchestrator.run(
            version=version,
            skip_git=skip_git,
            skip_pypi=skip_pypi,
            verify_only=verify_only
        )

        if dry_run:
            _display_dry_run_preview(orchestrator, version)
            return

        if result.success:
            _display_success(result, version)
        else:
            _display_failure(result)

    except Exception as e:
        rprint(f"[red]❌ 部署失败: {e}[/red]")
        raise click.Abort()


def _get_current_version() -> str:
    """获取当前版本号"""
    try:
        vm = VersionManager()
        return vm.get_current_version()
    except VersionError:
        return "unknown"


def _setup_deployment_steps(orchestrator: DeploymentOrchestrator,
                           version: str,
                           dry_run: bool,
                           verbose: bool):
    """设置部署步骤"""

    def doc_check_step():
        return _check_documents(verbose)

    def state_check_step():
        return _check_test_status(verbose)

    def version_step():
        vm = VersionManager()
        if dry_run:
            return f"[DRY-RUN] 会更新版本到 {version}"
        vm.update_version(version)
        return f"版本已更新: {version}"

    def build_step():
        builder = PackageBuilder()
        if dry_run:
            return "[DRY-RUN] 会执行 python -m build"
        builder.clean()
        builder.build()
        success, artifacts = builder.verify_build()
        return f"构建完成: {len(artifacts)} 个产物"

    def pypi_step():
        uploader = PyPIUploader()
        if dry_run:
            return "[DRY-RUN] 会执行 twine upload"
        if skip_git and skip_pypi:
            return "跳过 PyPI 上传"
        success, msg = uploader.upload()
        return msg

    def git_step():
        pusher = GitPusher()
        if dry_run:
            return "[DRY-RUN] 会执行 git add/commit/tag/push"
        if skip_pypi:
            return "跳过 Git 推送"
        pusher.commit_and_push(version, dry_run=dry_run)
        pusher.create_tag(version, dry_run=dry_run)
        return "Git 操作完成"

    def verify_step():
        verifier = DeployVerifier()
        if dry_run:
            return "[DRY-RUN] 会验证 PyPI 发布"
        success, result = verifier.verify_complete(version)
        return f"验证完成: {'成功' if success else '失败'}"

    def state_step():
        updater = StateUpdater()
        if dry_run:
            return "[DRY-RUN] 会更新 project_state.yaml"
        pypi_url = f"https://pypi.org/project/opencode-collaboration/{version}/"
        updater.update_deployment_status(
            version=version,
            pypi_url=pypi_url,
            git_tag=f"v{version}",
            agent_id="2"
        )
        return "状态已更新"

    orchestrator.add_step("doc_check", "检查文档同步", doc_check_step)
    orchestrator.add_step("state_check", "检查测试状态", state_check_step)
    orchestrator.add_step("version_update", "更新版本号", version_step)
    orchestrator.add_step("build", "执行包构建", build_step)
    orchestrator.add_step("pypi_upload", "上传到 PyPI", pypi_step)
    orchestrator.add_step("git_push", "Git 推送", git_step)
    orchestrator.add_step("verify", "验证发布", verify_step)
    orchestrator.add_step("state_update", "更新项目状态", state_step)


def _check_documents(verbose: bool) -> str:
    """检查文档同步"""
    import os

    required_docs = ["CHANGELOG.md", "README.md"]
    missing = []

    for doc in required_docs:
        if os.path.exists(doc):
            if verbose:
                rprint(f"  ✅ {doc} 存在")
        else:
            missing.append(doc)
            rprint(f"  ❌ {doc} 不存在")

    if missing:
        raise click.ClickException(f"文档缺失: {', '.join(missing)}")

    return "文档检查通过"


def _check_test_status(verbose: bool) -> str:
    """检查测试状态"""
    import yaml

    state_file = Path("state/project_state.yaml")
    if not state_file.exists():
        return "跳过状态检查（无状态文件）"

    try:
        with open(state_file) as f:
            state = yaml.safe_load(f)

        if "testing" in state:
            test_status = state["testing"].get("status", "unknown")
            if verbose:
                rprint(f"  测试状态: {test_status}")

            if test_status != "completed" and test_status != "APPROVED":
                raise click.ClickException(f"测试未完成，当前状态: {test_status}")

    except Exception as e:
        rprint(f"  ⚠️  无法读取测试状态: {e}")

    return "测试状态检查通过"


def _display_dry_run_preview(orchestrator: DeploymentOrchestrator, version: str):
    """显示预览模式输出"""
    rprint("\n[bold yellow]🔍 预览模式[/bold yellow]")
    rprint(f"版本: [cyan]{version}[/cyan]")
    rprint("\n[bold]部署步骤:[/bold]")

    for i, step in enumerate(orchestrator.steps, 1):
        rprint(f"  {i}. [cyan]{step.name}[/cyan] - {step.description}")

    rprint("\n[bold yellow]以上步骤将在执行时运行[/bold yellow]")


def _display_success(result, version: str):
    """显示成功结果"""
    rprint("\n[bold green]✅ 部署成功[/bold green]")
    rprint(f"版本: [cyan]{version}[/cyan]")

    table = Table(title="部署步骤")
    table.add_column("步骤")
    table.add_column("状态")

    for step in result.steps:
        status_icon = "✅" if step["status"] == "passed" else "❌"
        table.add_row(step["name"], f"{status_icon} {step['status']}")

    console.print(table)

    rprint(f"\n📦 PyPI: [link=https://pypi.org/project/opencode-collaboration/{version}/]https://pypi.org/project/opencode-collaboration/{version}/[/link]")
    rprint(f"🏷️ Git Tag: [bold]v{version}[/bold]")


def _display_failure(result):
    """显示失败结果"""
    rprint("\n[bold red]❌ 部署失败[/bold red]")

    if result.error:
        rprint(f"错误: [red]{result.error}[/red]")

    table = Table(title="失败的步骤")
    table.add_column("步骤")
    table.add_column("状态")
    table.add_column("消息")

    for step in result.steps:
        if step["status"] == "failed":
            table.add_row(
                step["name"],
                "❌ failed",
                step.get("message", "")
            )

    console.print(table)
