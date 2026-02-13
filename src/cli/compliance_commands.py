"""Compliance CLI命令

F-COMP-001: Agent Compliance CLI准入检查
"""
import click
from rich.console import Console
from rich.table import Table
from ..core.compliance_enforcer import ComplianceEnforcer
from ..core.context_manager import ContextManager, ContextNotFoundError

console = Console()


def get_current_agent_id() -> int:
    """获取当前Agent ID"""
    try:
        context = ContextManager().load_context()
        return context.agent
    except ContextNotFoundError:
        return 1


@click.group()
def compliance_group():
    """合规检查命令组"""
    pass


@click.command(name="check")
def compliance_check_command():
    """
    检查当前Agent的合规状态。

    示例:
        oc-collab compliance check
    """
    agent_id = get_current_agent_id()

    table = Table(title=f"Agent{agent_id} 合规状态")
    table.add_column("检查项", style="cyan")
    table.add_column("状态", style="green")

    enforcer = ComplianceEnforcer(agent_id)

    violations = enforcer.get_violations(f"agent{agent_id}")
    violation_count = len(violations)

    table.add_row("当前Agent", f"Agent {agent_id}")
    table.add_row("违规次数", f"⚠️  {violation_count}" if violation_count > 0 else "✅ 0")
    table.add_row("合规率", f"⚠️  {enforcer.get_compliance_rate():.0%}" if violation_count > 0 else "✅ 100%")

    console.print(table)

    if violation_count > 0:
        console.print("\n最近违规:")
        for v in violations[-5:]:
            console.print(f"  - [{v.get('timestamp', 'N/A')}] {v.get('command', 'N/A')}")


@click.command(name="report")
def compliance_report_command():
    """
    生成合规报告。

    示例:
        oc-collab compliance report
    """
    agent_id = get_current_agent_id()
    enforcer = ComplianceEnforcer(agent_id)

    report = enforcer.generate_report()
    console.print(report)


@click.command(name="violations")
def compliance_violations_command():
    """
    查看违规记录。

    示例:
        oc-collab compliance violations
    """
    agent_id = get_current_agent_id()
    enforcer = ComplianceEnforcer(agent_id)

    violations = enforcer.get_violations()

    if not violations:
        console.print("✅ 无违规记录")
        return

    table = Table(title="违规记录")
    table.add_column("时间", style="cyan")
    table.add_column("Agent", style="magenta")
    table.add_column("命令", style="red")

    for v in violations:
        table.add_row(
            v.get("timestamp", "N/A")[:19],
            v.get("agent_id", "N/A"),
            v.get("command", "N/A")
        )

    console.print(table)


compliance_group.add_command(compliance_check_command, "check")
compliance_group.add_command(compliance_report_command, "report")
compliance_group.add_command(compliance_violations_command, "violations")
