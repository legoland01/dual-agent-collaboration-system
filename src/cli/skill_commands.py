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
from ..core.skill_tester import SkillTester
from ..core.coverage_calculator import CoverageCalculator
from ..core.reference_validator import ReferenceValidator
from ..core.cli_action_validator import CLIActionValidator
from ..core.skill_index import SkillIndex
from ..core.skill_search_engine import SkillSearchEngine
from ..core.index_auto_updater import IndexAutoUpdater

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


@click.command(name="test")
@click.option("--skill", "-s", help="指定测试的Skill ID")
@click.option("--verbose", "-v", is_flag=True, help="输出详细结果")
@click.option("--json", "output_json", is_flag=True, help="JSON格式输出")
@click.option("--fix", "-f", is_flag=True, help="自动修复可修复问题")
def skill_test(skill: Optional[str], verbose: bool, output_json: bool, fix: bool):
    """
    运行Skill内容准确性测试。

    示例:
      oc-collab skill test                    # 测试所有Skill
      oc-collab skill test -s oc_collab_development_guide  # 测试指定Skill
      oc-collab skill test -v                 # 详细输出
      oc-collab skill test --fix              # 自动修复可修复问题
    """
    tester = SkillTester(verbose=verbose, auto_fix=fix)
    
    if fix:
        click.echo("🔧 自动修复模式已启用...")
    
    report = tester.run_all_tests(skill)

    if output_json:
        import json
        output = {
            'timestamp': report.timestamp,
            'total': report.total_skills,
            'passed': report.passed_skills,
            'success_rate': f"{report.success_rate:.1f}%",
            'results': [
                {
                    'skill_id': r.skill_id,
                    'passed': r.passed,
                    'errors': r.error_count,
                    'warnings': r.warning_count,
                    'items': [
                        {
                            'code': item.code,
                            'level': item.level.value,
                            'message': item.message
                        }
                        for item in r.items
                    ]
                }
                for r in report.results
            ]
        }
        click.echo(json.dumps(output, ensure_ascii=False, indent=2))
        return

    click.echo(f"=== Skill测试报告 ===")
    click.echo(f"时间: {report.timestamp}")
    click.echo(f"总计: {report.total_skills}个Skill")
    click.echo(f"通过: {report.passed_skills}个")
    click.echo(f"成功率: {report.success_rate:.1f}%")
    click.echo("")

    for result in report.results:
        status = "✅" if result.passed else "❌"
        click.echo(f"{status} {result.skill_id}")
        if not result.passed and verbose:
            for item in result.items:
                level_icon = "⚠️" if item.level.value == "WARNING" else "❌"
                click.echo(f"   {level_icon} [{item.code}] {item.message}")
                if item.suggestion:
                    click.echo(f"      建议: {item.suggestion}")

    if report.success_rate < 100:
        click.echo(f"\n⚠️  测试未完全通过，请检查以上问题")
        raise click.Abort()


@click.command(name="coverage")
@click.option("--skill", "-s", help="指定统计的Skill ID")
@click.option("--threshold", "-t", type=float, default=95.0, help="覆盖率阈值")
@click.option("--json", "output_json", is_flag=True, help="JSON格式输出")
def skill_coverage(skill: Optional[str], threshold: float, output_json: bool):
    """
    统计Skill内容的切片覆盖率。

    示例:
      oc-collab skill coverage               # 统计所有Skill
      oc-collab skill coverage -s oc_collab_development_guide
      oc-collab skill coverage -t 80         # 设置阈值为80%
    """
    calculator = CoverageCalculator(threshold=threshold)
    reports = calculator.generate_report(skill)

    if output_json:
        import json
        output = {
            'threshold': threshold,
            'total': len(reports),
            'passed': sum(1 for r in reports if r.passed),
            'reports': [
                {
                    'skill_id': r.skill_id,
                    'total_chapters': r.total_chapters,
                    'sliced_chapters': r.sliced_chapters,
                    'coverage_rate': f"{r.coverage_rate:.1f}%",
                    'passed': r.passed
                }
                for r in reports
            ]
        }
        click.echo(json.dumps(output, ensure_ascii=False, indent=2))
        return

    click.echo(f"=== Skill覆盖率报告 (阈值: {threshold}%) ===")
    click.echo(f"总计: {len(reports)}个Skill")
    click.echo("")

    passed_count = 0
    for report in reports:
        status = "✅" if report.passed else "❌"
        click.echo(f"{status} {report.skill_id}")
        click.echo(f"   章节: {report.sliced_chapters}/{report.total_chapters}")
        click.echo(f"   覆盖率: {report.coverage_rate:.1f}%")
        if report.passed:
            passed_count += 1

    click.echo("")
    click.echo(f"通过: {passed_count}/{len(reports)}")

    if passed_count < len(reports):
        click.echo(f"\n⚠️  覆盖率未达标的Skill需要补充切片")


skill_group.add_command(skill_check_command, "check")
skill_group.add_command(skill_status_command, "status")
skill_group.add_command(skill_search, "search")
skill_group.add_command(skill_slice, "slice")
skill_group.add_command(skill_enforce, "enforce")
skill_group.add_command(skill_test, "test")
skill_group.add_command(skill_coverage, "coverage")


@click.command(name="index")
@click.option("--sync", is_flag=True, help="同步更新Skill索引")
def skill_index_cmd(sync):
    """Skill索引管理"""
    if sync:
        index = SkillIndex("config/skill_index.yaml")
        updater = IndexAutoUpdater(index, "skills")
        count = updater.sync_all()
        console.print(f"已同步{count}个Skill到索引")
    else:
        index = SkillIndex("config/skill_index.yaml")
        skills = index.get_all_skills()
        console.print(f"索引中共{len(skills)}个Skill：")
        for s in skills:
            info = index.get_skill_info(s)
            console.print(f"  - {s}: {info.get('description', '') if info else ''}")


@click.command(name="query")
@click.argument("query")
@click.option("--slice", is_flag=True, help="搜索后进入skill slice界面")
@click.option("--verbose", is_flag=True, help="显示匹配关键词详情")
def skill_query_cmd(query, slice, verbose):
    """关键词搜索Skill"""
    index = SkillIndex("config/skill_index.yaml")
    engine = SkillSearchEngine(index)
    
    results = engine.search(query, top_k=5)
    
    if not results:
        console.print(f"未找到匹配'{query}'的Skill")
        return
    
    console.print(f"搜索'{query}'找到{len(results)}个结果：\n")
    
    for i, r in enumerate(results, 1):
        console.print(f"{i}. {r.skill}")
        if verbose:
            console.print(f"   描述: {r.description}")
            console.print(f"   关键词: {', '.join(r.keywords)}")
            console.print(f"   置信度: {r.confidence:.2f}")
        console.print("")
    
    if slice:
        console.print("[进入slice模式...]")


skill_group.add_command(skill_index_cmd, "index")
skill_group.add_command(skill_query_cmd, "query")
