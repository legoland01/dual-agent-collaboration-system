"""启动检查命令
"""

import click
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.agent_startup_checker import AgentStartupChecker
from ..core.context_manager import ContextManager


@click.command("startup-check")
@click.option("--no-confirm", is_flag=True, help="不要求确认")
@click.option("--quiet", is_flag=True, help="静默模式，只返回状态码")
def startup_check_command(no_confirm: bool, quiet: bool):
    """
    执行Agent启动自检

    检查TODO队列并显示未读任务

    示例:
      oc-collab startup-check
      oc-collab startup-check --no-confirm
    """
    try:
        try:
            context = ContextManager().load_context()
            agent_id = context.agent
        except Exception:
            agent_id = "unknown"

        checker = AgentStartupChecker(agent_id)
        result = checker.run()

        if quiet:
            sys.exit(1 if result.has_unread_todos else 0)

        checker.display_notifications(result)

        if not no_confirm and result.has_unread_todos:
            if not checker.confirm_action():
                click.echo("已取消")
                sys.exit(1)

        action = checker.suggest_action(result)
        if action.startswith("process_todo:"):
            todo_id = action.split(":")[1]
            click.echo(f"\n建议执行: oc-collab todo view {todo_id}")
        elif action == "review_todos":
            click.echo(f"\n建议查看: oc-collab todo list --unread --agent {agent_id[-1]}")

    except Exception as e:
        click.echo(f"❌ 启动检查失败: {e}")
        sys.exit(1)


@click.command("todo-stats")
@click.option("--agent", type=click.Choice(["1", "2"]), help="按接收者筛选")
@click.option("--json", is_flag=True, help="JSON格式输出")
def todo_stats_command(agent: str, json: bool):
    """
    显示TODO队列统计信息

    示例:
      oc-collab todo-stats
      oc-collab todo-stats --agent 1
      oc-collab todo-stats --json
    """
    from ..core.todo_queue_manager import TodoQueueManager

    try:
        queue_manager = TodoQueueManager()
        agent_id = f"agent{agent}" if agent else None
        stats = queue_manager.get_stats(agent_id)

        if json:
            import json
            output = {
                "total": stats.total,
                "unread": stats.unread,
                "by_agent": stats.by_agent,
                "by_priority": stats.by_priority,
                "last_updated": stats.last_updated
            }
            click.echo(json.dumps(output, indent=2, ensure_ascii=False))
            return

        click.echo(f"\n📊 TODO队列统计:")
        click.echo(f"  总数: {stats.total}")
        click.echo(f"  未读: {stats.unread}")
        click.echo(f"  按Agent: agent1={stats.by_agent.get('agent1', 0)}, agent2={stats.by_agent.get('agent2', 0)}")
        click.echo(f"  按优先级: 高={stats.by_priority.get('high', 0)}, 中={stats.by_priority.get('medium', 0)}, 低={stats.by_priority.get('low', 0)}")
        click.echo(f"  最后更新: {stats.last_updated}")
        click.echo("")

    except Exception as e:
        click.echo(f"❌ 获取统计失败: {e}")


@click.command("todo-cleanup")
@click.option("--days", default=7, help="清理N天前的已读TODO", type=int)
def todo_cleanup_command(days: int):
    """
    清理过期的已读TODO

    示例:
      oc-collab todo-cleanup
      oc-collab todo-cleanup --days 14
    """
    from ..core.todo_queue_manager import TodoQueueManager

    try:
        queue_manager = TodoQueueManager()
        count = queue_manager.cleanup(days)
        click.echo(f"✅ 已清理 {count} 个过期TODO")

    except Exception as e:
        click.echo(f"❌ 清理失败: {e}")
