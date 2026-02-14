"""TODO相关命令
"""

import click
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.todo_queue_manager import TodoQueueManager, TodoQueueItem
from ..core.context_manager import ContextManager


@click.group("todo")
def todo_group():
    """TODO管理命令组"""
    pass


@todo_group.command("list")
@click.option("--unread", is_flag=True, help="仅显示未读TODO")
@click.option("--agent", type=click.Choice(["1", "2"]), help="按接收者筛选")
@click.option("--priority", type=click.Choice(["high", "medium", "low"]), help="按优先级筛选")
@click.option("--json", is_flag=True, help="JSON格式输出")
def todo_list_command(unread: bool, agent: str, priority: str, json: bool):
    """显示TODO列表

    示例:
      oc-collab todo list                  # 显示所有TODO
      oc-collab todo list --unread        # 仅未读
      oc-collab todo list --unread --agent 2  # 筛选接收者
      oc-collab todo list --unread --json # JSON格式
    """
    try:
        queue_manager = TodoQueueManager()

        if unread:
            agent_id = f"agent{agent}" if agent else None
            todos = queue_manager.get_unread(agent_id, priority)

            if json:
                import json
                output = {
                    "unread_count": len(todos),
                    "todos": [
                        {
                            "id": t.id,
                            "content": t.content,
                            "priority": t.priority,
                            "from_agent": t.from_agent,
                            "created_at": t.created_at
                        }
                        for t in todos
                    ]
                }
                click.echo(json.dumps(output, indent=2, ensure_ascii=False))
                return

            if not todos:
                click.echo("✅ 无未读TODO")
                return

            click.echo(f"\n🔔 未读TODO ({len(todos)}个):")
            click.echo("-" * 60)

            for t in todos:
                priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                icon = priority_icons.get(t.priority, "⚪")
                click.echo(f"  {icon} [{t.id}] {t.content}")
                click.echo(f"      from {t.from_agent} · {t.created_at}")
                click.echo("")

        else:
            agent_id = f"agent{agent}" if agent else None
            todos = queue_manager.get_all(agent_id)

            if json:
                import json
                output = {
                    "total_count": len(todos),
                    "todos": [
                        {
                            "id": t.id,
                            "content": t.content,
                            "priority": t.priority,
                            "from_agent": t.from_agent,
                            "to_agent": t.to_agent,
                            "read": t.read,
                            "created_at": t.created_at
                        }
                        for t in todos
                    ]
                }
                click.echo(json.dumps(output, indent=2, ensure_ascii=False))
                return

            if not todos:
                click.echo("TODO列表为空")
                return

            click.echo(f"\n📋 TODO列表 ({len(todos)}个):")
            click.echo("-" * 60)

            for t in todos:
                status = "✅" if t.read else "📬"
                priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                icon = priority_icons.get(t.priority, "⚪")
                click.echo(f"  {status} {icon} [{t.id}] {t.content}")
                click.echo(f"      {t.from_agent} → {t.to_agent} · {t.created_at}")

    except Exception as e:
        click.echo(f"❌ 获取TODO列表失败: {e}")


@todo_group.command("mark-read")
@click.argument("todo_id")
@click.option("--agent", type=click.Choice(["1", "2"]), help="验证接收者")
def mark_read_command(todo_id: str, agent: str):
    """标记TODO为已读

    示例:
      oc-collab todo mark-read TODO-001
    """
    try:
        queue_manager = TodoQueueManager()
        agent_id = f"agent{agent}" if agent else None

        result = queue_manager.mark_read(todo_id, agent_id)

        if result:
            click.echo(f"✅ TODO {todo_id} 已标记为已读")
        else:
            click.echo(f"❌ TODO {todo_id} 不存在或接收者不匹配")

    except Exception as e:
        click.echo(f"❌ 标记失败: {e}")


@todo_group.command("mark-all-read")
@click.option("--agent", type=click.Choice(["1", "2"]), help="仅标记该接收者的TODO")
def mark_all_read_command(agent: str):
    """标记所有TODO为已读

    示例:
      oc-collab todo mark-all-read        # 标记所有
      oc-collab todo mark-all-read --agent 2  # 仅标记发给Agent2的
    """
    try:
        queue_manager = TodoQueueManager()
        agent_id = f"agent{agent}" if agent else None

        count = queue_manager.mark_all_read(agent_id)

        if count > 0:
            click.echo(f"✅ 已标记 {count} 个TODO为已读")
        else:
            click.echo("✅ 无未读TODO")

    except Exception as e:
        click.echo(f"❌ 标记失败: {e}")


@todo_group.command("stats")
@click.option("--agent", type=click.Choice(["1", "2"]), help="按接收者筛选")
@click.option("--json", is_flag=True, help="JSON格式输出")
def todo_stats_command(agent: str, json: bool):
    """显示TODO统计信息

    示例:
      oc-collab todo stats
      oc-collab todo stats --agent 1
      oc-collab todo stats --json
    """
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


@todo_group.command("cleanup")
@click.option("--days", default=7, help="清理N天前的已读TODO", type=int)
def todo_cleanup_command(days: int):
    """清理过期的已读TODO

    示例:
      oc-collab todo cleanup
      oc-collab todo cleanup --days 14
    """
    try:
        queue_manager = TodoQueueManager()
        count = queue_manager.cleanup(days)
        click.echo(f"✅ 已清理 {count} 个过期TODO")

    except Exception as e:
        click.echo(f"❌ 清理失败: {e}")


@todo_group.command("clear")
@click.option("--agent", type=click.Choice(["1", "2"]), help="仅清空该接收者的TODO")
def todo_clear_command(agent: str):
    """清空TODO队列

    示例:
      oc-collab todo clear         # 清空所有
      oc-collab todo clear --agent 1  # 仅清空发给Agent1的
    """
    try:
        queue_manager = TodoQueueManager()
        agent_id = f"agent{agent}" if agent else None

        count = queue_manager.clear(agent_id)

        if count > 0:
            click.echo(f"✅ 已清空 {count} 个TODO")
        else:
            click.echo("✅ TODO队列已为空")

    except Exception as e:
        click.echo(f"❌ 清空失败: {e}")
