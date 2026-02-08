"""Skill CLI命令

FR-SKILL-001: 在CLI命令执行前，强制检查相关Skill是否已加载
"""
import click
from rich.console import Console
from rich.table import Table
from ..core.skill_enforcer import SkillEnforcer

console = Console()


@click.command(name="check")
def skill_check_command():
    """检查Skill加载状态"""
    enforcer = SkillEnforcer()

    loaded = enforcer.list_loaded_skills()
    missing = enforcer.list_missing_skills()

    table = Table(title="Skill 加载状态")
    table.add_column("状态", style="green" if not missing else "red")
    table.add_column("Skill 名称")

    for skill in loaded:
        table.add_row("✅ 已加载", skill)

    for skill in missing:
        table.add_row("❌ 缺失", skill)

    console.print(table)

    if missing:
        console.print("\n缺失的Skill加载命令:")
        for skill in missing:
            console.print(f"  skill load {skill}")

    if not missing:
        console.print("\n✅ 所有必需Skill已加载")


@click.command(name="status")
def skill_status_command():
    """显示Skill状态摘要"""
    enforcer = SkillEnforcer()

    loaded = enforcer.list_loaded_skills()
    missing = enforcer.list_missing_skills()

    console.print(f"已加载: {len(loaded)}")
    console.print(f"缺失: {len(missing)}")

    if missing:
        console.print("\n缺失列表:")
        for skill in missing:
            console.print(f"  - {skill}")


@click.group()
def skill_group():
    """Skill管理命令"""
    pass


skill_group.add_command(skill_check_command, "check")
skill_group.add_command(skill_status_command, "status")
