"""Skill CLI命令

FR-SKILL-001: 在CLI命令执行前，强制检查相关Skill是否已加载
FR-SKILL-002: Skill切片检索 (v2.2.6)
FR-SKILL-003: Skill强制查找机制 (v2.2.6)
"""
import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from ..core.skill_enforcer import SkillEnforcer
from ..core.skill_searcher import SkillSearcher
from ..core.skill_slicer import SkillSlicer

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


@click.command(name="search")
@click.option("--keywords", "-k", multiple=True, help="搜索关键词")
@click.option("--match-mode", type=click.Choice(["any", "all"]),
              default="any", help="匹配模式")
def skill_search(keywords: tuple, match_mode: str):
    """
    搜索Skill文档。

    示例:
      oc-collab skill search -k todowrite -k 参数
      oc-collab skill search -k "详细设计" --match-mode all
    """
    if not keywords:
        console.print("❌ 请指定搜索关键词，使用 --keywords 或 -k")
        return

    searcher = SkillSearcher()
    results = searcher.search(list(keywords), match_mode)

    if not results:
        console.print("未找到匹配的Skill")
        return

    console.print(f"找到 {len(results)} 个匹配结果:\n")

    for r in results:
        console.print(f"📄 {r['name']}")
        console.print(f"   匹配关键词: {', '.join(r['matched_keywords'])}")
        console.print(f"   文件: {r['file']}")
        excerpt = r['excerpt'][:200] if r['excerpt'] else "无匹配内容"
        console.print(f"   摘要: {excerpt}...")
        console.print()


@click.command(name="slice")
@click.argument("skill_name")
@click.option("--level", type=click.Choice(["chapter", "section", "subsection"]),
              default="section", help="切片级别")
@click.option("--section-id", "-s", help="指定章节ID")
def skill_slice(skill_name: str, level: str, section_id: Optional[str]):
    """
    查看Skill的特定切片。

    示例:
      oc-collab skill slice oc_collab_detailed_design_guide --level section
      oc-collab skill slice oc_collab_detailed_design_guide --section-id section-2
    """
    slicer = SkillSlicer()

    if section_id:
        content = slicer.get_slice(skill_name, section_id)
        if content:
            console.print(content)
        else:
            console.print(f"❌ 未找到章节: {section_id}")
    else:
        chapters = slicer.list_chapters(skill_name)
        console.print(f"\n📑 {skill_name} 章节列表:\n")

        for ch in chapters:
            prefix = "  " * (ch["level"] - 1)
            lines = len(ch["content"])
            console.print(f"{prefix}• [{ch['id']}] {ch['title']} ({lines}行)")


@click.command(name="enforce")
@click.option("--action", "-a", help="指定行动类型")
@click.option("--before-action", is_flag=True, help="行动前检查")
def skill_enforce(action: Optional[str], before_action: bool):
    """
    Skill强制查找机制。

    示例:
      oc-collab skill enforce --action todowrite
      oc-collab skill enforce --before-action
    """
    enforcer = SkillEnforcer()

    if before_action:
        if not action:
            console.print("❌ 请使用 --action 指定行动类型")
            return

        result = enforcer.check_before_action(action)

        if result["missing"]:
            console.print(f"⚠️  缺少必需的Skill:")
            for skill in result["missing"]:
                console.print(f"   • {skill}")
            console.print(f"\n建议: {'; '.join(result['suggestions'])}")
        else:
            console.print(f"✅ {action} 所需的Skill已全部加载")

    else:
        # 检查所有必需Skill
        console.print("🔍 检查必需Skill...\n")

        all_ok = True
        for phase, skill_name in enforcer.REQUIRED_SKILLS.items():
            skill_path = enforcer.skills_dir / skill_name
            status = "✅" if skill_path.exists() else "❌"
            console.print(f"{status} {phase}: {skill_name}")

            if not skill_path.exists():
                all_ok = False

        if all_ok:
            console.print("\n✅ 所有必需Skill已加载")
        else:
            console.print("\n⚠️ 部分Skill未加载，使用 oc-collab skill enforce --action <行动> 检查")


@click.group()
def skill_group():
    """Skill管理命令"""
    pass


skill_group.add_command(skill_check_command, "check")
skill_group.add_command(skill_status_command, "status")
skill_group.add_command(skill_search, "search")
skill_group.add_command(skill_slice, "slice")
skill_group.add_command(skill_enforce, "enforce")
