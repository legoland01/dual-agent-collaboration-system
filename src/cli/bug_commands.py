"""BUG管理CLI命令

v2.3.0: BUG自动关联测试系统
"""
import click
from ..core.bug_test_linker import BugTestLinker
from ..core.test_suggestion_engine import TestSuggestionEngine


@click.group(name="bug")
def bug_group():
    """BUG管理命令组"""
    pass


@bug_group.command(name="link")
@click.argument("bug_id")
@click.argument("test_file")
def bug_link(bug_id: str, test_file: str):
    """关联BUG与测试用例
    
    示例:
      oc-collab bug link BUG-20260215-001 tests/test_example.py
    """
    linker = BugTestLinker()
    
    try:
        result = linker.link(bug_id, test_file)
        if result:
            click.echo(f"✅ 已关联 {bug_id} -> {test_file}")
            tests = linker.get_tests_for_bug(bug_id)
            click.echo(f"   当前关联: {len(tests)} 个测试")
        else:
            click.echo(f"⚠️ 关联失败或已存在")
    except Exception as e:
        click.echo(f"❌ 错误: {e}")


@bug_group.command(name="list")
@click.option("--unlinked", is_flag=True, help="仅显示未关联测试的BUG")
def bug_list(unlinked: bool):
    """列出BUG关联情况
    
    示例:
      oc-collab bug list
      oc-collab bug list --unlinked
    """
    linker = BugTestLinker()
    all_links = linker.get_all_links()
    
    if unlinked:
        unlinked_bugs = linker.get_bugs_without_tests()
        if not unlinked_bugs:
            click.echo("✅ 所有BUG都已关联测试")
            return
        
        click.echo(f"未关联测试的BUG ({len(unlinked_bugs)}个):\n")
        for bug_id in unlinked_bugs:
            click.echo(f"  • {bug_id}")
    else:
        if not all_links:
            click.echo("暂无BUG关联数据")
            return
        
        click.echo(f"BUG关联情况 ({len(all_links)}个):\n")
        for link in all_links:
            bug_id = link.get("bug_id", "")
            tests = link.get("test_files", [])
            status = "✅" if tests else "❌"
            click.echo(f"{status} {bug_id}: {len(tests)} 个测试")


@bug_group.command(name="suggest")
@click.argument("bug_id", required=False)
@click.option("--description", "-d", help="BUG描述")
def bug_suggest(bug_id: str, description: str):
    """建议可能关联的测试用例
    
    示例:
      oc-collab bug suggest BUG-20260215-001 -d "todo同步失败"
      oc-collab bug suggest -d "skill enforce检查失败"
    """
    engine = TestSuggestionEngine()
    
    if not description and not bug_id:
        click.echo("❌ 请提供 --description 或 BUG ID")
        return
    
    suggestions = engine.suggest_tests(description or "", bug_id or "")
    
    if not suggestions:
        click.echo("⚠️ 未找到相关测试建议")
        return
    
    click.echo(f"建议关联的测试 ({len(suggestions)}个):\n")
    for test in suggestions:
        click.echo(f"  • {test}")
