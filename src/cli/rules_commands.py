"""Rules CLI命令

F-INIT-001: oc-collab rules init/status
F-INIT-002: oc-collab rules init --auto-load (规则自动加载)
"""

import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from ..core.rules_initializer import RulesInitializer
from ..core.rules_auto_loader import RulesAutoLoader

console = Console()


@click.command(name="init")
@click.option("--force", "-f", is_flag=True, help="强制覆盖已存在的文件")
@click.option("--auto-load", "-a", is_flag=True, help="自动加载默认Skill和规则")
def rules_init(force: bool, auto_load: bool):
    """
    初始化框架规则。

    示例:
      oc-collab rules init                 # 初始化规则
      oc-collab rules init --force         # 强制覆盖
      oc-collab rules init --auto-load     # 自动加载默认Skill
      oc-collab rules init --force --auto-load  # 强制覆盖+自动加载
    """
    initializer = RulesInitializer()

    try:
        result = initializer.init(force=force)

        if result.success:
            console.print("✅ 规则初始化成功")
            if result.created_files:
                console.print(f"\n[bold]已创建文件:[/bold]")
                for f in result.created_files:
                    console.print(f"  - {f}")
            if result.skipped_files:
                console.print(f"\n[bold]已跳过文件:[/bold]")
                for f in result.skipped_files:
                    console.print(f"  - {f}")
        else:
            console.print("❌ 规则初始化失败")
            for error in result.errors:
                console.print(f"  - {error}")
            raise click.Abort()

        # v2.2.9: 自动加载默认Skill
        if auto_load:
            console.print("\n[bold]自动加载默认Skill...[/bold]")
            auto_loader = RulesAutoLoader()
            load_result = auto_loader.load_default_rules(force=force)

            if load_result["loaded"]:
                console.print(f"\n[bold]已加载:[/bold]")
                for item in load_result["loaded"]:
                    console.print(f"  ✓ {item}")

            if load_result["skipped"]:
                console.print(f"\n[bold]已跳过:[/bold]")
                for item in load_result["skipped"]:
                    console.print(f"  ⊘ {item}")

            if load_result["errors"]:
                console.print(f"\n[bold]加载失败:[/bold]")
                for error in load_result["errors"]:
                    console.print(f"  ✗ {error}")

    except Exception as e:
        console.print(f"❌ 初始化失败: {e}")
        raise click.Abort()


@click.command(name="status")
def rules_status():
    """检查规则初始化状态"""
    initializer = RulesInitializer()

    try:
        status = initializer.check_status()

        table = Table(title="规则初始化状态")
        table.add_column("项目")
        table.add_column("状态")

        initialized_count = len(status.get("initialized", []))
        missing_count = len(status.get("missing", []))

        table.add_row("已初始化", f"✅ {initialized_count}")
        table.add_row("缺失", f"❌ {missing_count}")

        if status.get("initialized"):
            console.print("\n[bold]已初始化:[/bold]")
            for f in status["initialized"]:
                console.print(f"  ✓ {f}")

        if status.get("missing"):
            console.print("\n[bold]缺失:[/bold]")
            for f in status["missing"]:
                console.print(f"  ✗ {f}")

        console.print(table)

    except Exception as e:
        console.print(f"❌ 获取状态失败: {e}")
        raise click.Abort()


@click.group()
def rules_group():
    """规则管理命令"""
    pass


rules_group.add_command(rules_init, "init")
rules_group.add_command(rules_status, "status")
