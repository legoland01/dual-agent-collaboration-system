"""需求管理CLI命令

v2.3.0: 需求覆盖率分析系统
"""
import click
from ..core.requirement_test_mapper import RequirementTestMapper
from ..core.requirements_coverage import RequirementsCoverageAnalyzer
from ..core.coverage_checker import CoverageChecker


@click.group(name="requirements")
def requirements_group():
    """需求管理命令组"""
    pass


@requirements_group.command(name="coverage")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
@click.option("--json", is_flag=True, help="JSON格式输出")
def requirements_coverage(verbose: bool, json: bool):
    """检查需求覆盖率
    
    示例:
      oc-collab requirements coverage
      oc-collab requirements coverage --verbose
      oc-collab requirements coverage --json
    """
    analyzer = RequirementsCoverageAnalyzer()
    report = analyzer.analyze_coverage()
    
    if json:
        import json
        output = {
            "total": report.total_requirements,
            "covered": report.covered_requirements,
            "uncovered": report.uncovered_requirements,
            "coverage_percentage": report.coverage_percentage
        }
        click.echo(json.dumps(output, ensure_ascii=False, indent=2))
        return
    
    click.echo(f"=== 需求覆盖率报告 ===\n")
    click.echo(f"总需求数: {report.total_requirements}")
    click.echo(f"已覆盖: {report.covered_requirements}")
    click.echo(f"未覆盖: {len(report.uncovered_requirements)}")
    click.echo(f"覆盖率: {report.coverage_percentage:.1f}%\n")
    
    if verbose and report.uncovered_requirements:
        click.echo("未覆盖的需求:")
        for req_id in report.uncovered_requirements:
            click.echo(f"  ❌ {req_id}")
    
    if report.coverage_percentage < 100:
        click.echo(f"\n⚠️ 覆盖率未达100%，请补充测试")
    else:
        click.echo(f"\n✅ 覆盖率100%")


@requirements_group.command(name="map")
@click.argument("requirement_id")
@click.argument("test_file")
def requirements_map(requirement_id: str, test_file: str):
    """映射需求与测试
    
    示例:
      oc-collab requirements map F-QUAL-001 tests/test_example.py
    """
    mapper = RequirementTestMapper()
    
    result = mapper.map(requirement_id, test_file)
    if result:
        click.echo(f"✅ 已映射 {requirement_id} -> {test_file}")
    else:
        click.echo(f"❌ 映射失败: 测试文件不存在")


@requirements_group.command(name="list")
def requirements_list():
    """列出需求映射情况
    
    示例:
      oc-collab requirements list
    """
    mapper = RequirementTestMapper()
    mappings = mapper.get_all_mappings()
    
    if not mappings:
        click.echo("暂无需求映射数据")
        return
    
    click.echo(f"需求映射情况 ({len(mappings)}个):\n")
    for m in mappings:
        req_id = m.get("requirement_id", "")
        tests = m.get("test_files", [])
        status = "✅" if tests else "❌"
        click.echo(f"{status} {req_id}: {len(tests)} 个测试")
        if tests and len(tests) <= 3:
            for t in tests:
                click.echo(f"    • {t}")
