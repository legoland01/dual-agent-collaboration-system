"""Skill检查命令 - BUG-20260214-005 修复

功能：
- 检查当前加载的Skill
- 检查缺失的必需Skill
- 提供加载建议
"""

import click
from pathlib import Path
from typing import List


@click.group("skill")
def skill_check_group():
    """Skill管理命令组"""
    pass


@skill_check_group.command("check")
@click.option("--phase", type=click.Choice(["requirements", "design", "development", "testing", "deployment"]),
              help="指定阶段检查相关Skill")
@click.option("--missing", is_flag=True, help="只显示缺失的Skill")
@click.option("--json", is_flag=True, help="JSON格式输出")
def skill_check_command(phase: str, missing: bool, json: bool):
    """
    检查Skill加载状态

    示例:
      oc-collab skill check                    # 检查所有Skill
      oc-collab skill check --missing        # 只显示缺失的
      oc-collab skill check --phase development  # 检查开发相关
      oc-collab skill check --json           # JSON格式输出
    """
    from ..core.skill_enforcer import SkillEnforcer

    enforcer = SkillEnforcer()

    loaded_skills = enforcer.list_loaded_skills()
    missing_skills = enforcer.list_missing_skills()

    if json:
        import json
        output = {
            "loaded": loaded_skills,
            "missing": missing_skills,
            "count": {
                "loaded": len(loaded_skills),
                "missing": len(missing_skills)
            }
        }
        click.echo(json.dumps(output, indent=2, ensure_ascii=False))
        return

    click.echo("\n🔍 Skill状态检查")
    click.echo("=" * 60)

    # 显示加载的Skill
    click.echo(f"\n✅ 已加载 ({len(loaded_skills)}个):")
    if loaded_skills:
        for skill in sorted(loaded_skills):
            click.echo(f"   • {skill}")
    else:
        click.echo("   (无)")

    # 显示缺失的Skill
    if missing or len(missing_skills) > 0:
        click.echo(f"\n❌ 缺失 ({len(missing_skills)}个):")
        if missing_skills:
            for skill in sorted(missing_skills):
                click.echo(f"   • {skill}")
                load_cmd = enforcer.get_load_command(skill)
                click.echo(f"      → 加载: oc-collab {load_cmd}")
        else:
            click.echo("   (无)")
    else:
        click.echo(f"\n❌ 缺失 ({len(missing_skills)}个): (使用 --missing 查看)")

    # 阶段相关检查
    if phase:
        phase_skills = enforcer.REQUIRED_SKILLS.get(phase, "")
        if phase_skills:
            phase_missing = [s for s in missing_skills if s == phase_skills]
            click.echo(f"\n📋 {phase}阶段相关Skill:")
            if phase_missing:
                click.echo(f"   ⚠️  缺失: {phase_missing[0]}")
                click.echo(f"      → 建议加载后再执行{phase}相关操作")
            else:
                click.echo(f"   ✅ {phase_skills} 已加载")

    click.echo("\n" + "=" * 60)


@skill_check_group.command("status")
def skill_status_command():
    """
    显示Skill合规状态摘要
    """
    from ..core.skill_enforcer import SkillEnforcer
    from ..core.context_manager import ContextManager

    enforcer = SkillEnforcer()

    try:
        context = ContextManager().load_context()
        agent_id = context.agent
    except:
        agent_id = "unknown"

    loaded = enforcer.list_loaded_skills()
    missing = enforcer.list_missing_skills()

    click.echo(f"\n🤖 Agent {agent_id} Skill状态")
    click.echo("=" * 60)

    # 根据Agent角色显示建议
    if agent_id == "agent1":
        key_skills = ["oc_collab_requirements_guide", "oc_collab_requirements_review_guide"]
        click.echo("\n📋 Agent1 关键Skill:")
    else:
        key_skills = ["oc_collab_development_guide", "oc_collab_design_guide"]
        click.echo("\n📋 Agent2 关键Skill:")

    for skill in key_skills:
        if skill in missing:
            click.echo(f"   ❌ {skill} (缺失)")
        elif skill in loaded:
            click.echo(f"   ✅ {skill}")
        else:
            click.echo(f"   ⚪ {skill} (可选)")

    click.echo("\n💡 提示: 执行任务前请确保相关Skill已加载")
    click.echo("   → 使用: oc-collab skill check --missing")
    click.echo("=" * 60 + "\n")


@skill_check_group.command("verify")
@click.argument("action")
def skill_verify_command(action: str):
    """
    验证执行特定操作前是否已加载相关Skill

    示例:
      oc-collab skill verify todowrite
      oc-collab skill verify signoff
      oc-collab skill verify review
    """
    from ..core.skill_enforcer import SkillEnforcer

    enforcer = SkillEnforcer()
    result = enforcer.check_before_action(action)

    click.echo(f"\n🔍 执行 '{action}' 前的Skill检查")
    click.echo("=" * 60)

    # 必需Skill
    if result["required_skills"]:
        click.echo(f"\n📌 必需Skill:")
        for skill in result["required_skills"]:
            if skill in result["missing"]:
                click.echo(f"   ❌ {skill} (未加载)")
            else:
                click.echo(f"   ✅ {skill}")
    else:
        click.echo(f"\n📌 必需Skill: (无)")

    # 可选Skill
    if result["optional_skills"]:
        click.echo(f"\n📌 可选Skill:")
        for skill in result["optional_skills"]:
            click.echo(f"   ⚪ {skill}")

    # 建议
    if result["missing"]:
        click.echo(f"\n⚠️  缺失 {len(result['missing'])} 个必需Skill")
        for skill in result["missing"]:
            click.echo(f"   → 加载: oc-collab skill load {skill}")
        click.echo("\n💡 建议先加载缺失的Skill再执行操作")
    else:
        click.echo(f"\n✅ 所有必需Skill已加载，可以执行 '{action}'")

    click.echo("=" * 60 + "\n")
