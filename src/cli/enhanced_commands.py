"""增强的 CLI 命令：项目上下文和待办管理"""
import click
from pathlib import Path
from typing import Optional

from ..core.context_manager import (
    ContextManager,
    ProjectContext,
    ContextNotFoundError,
    ContextParseError,
    InvalidContextError,
)
from ..core.todo_sync_manager import (
    TodoSyncManager,
    TodoState,
)


def get_project_path() -> str:
    """获取项目路径（当前目录或父目录）。"""
    current = Path.cwd()
    if (current / "state" / "project_state.yaml").exists():
        return str(current)
    parent = current.parent
    if (parent / "state" / "project_state.yaml").exists():
        return str(parent)
    return str(current)


@click.command(name=".a")
def show_context_command():
    """显示当前关联的项目信息。"""
    context_manager = ContextManager()

    try:
        context = context_manager.load_context()
        agent_name = context_manager.get_agent_display_name(context.agent)

        click.echo(f"┌───────────┬──────────────┐")
        click.echo(f"│ 项目名称  │ {context.project:<12} │")
        click.echo(f"│ 项目路径  │ {context.path:<12} │")
        click.echo(f"│ 当前Agent│ {agent_name:<12} │")
        click.echo(f"│ 配置版本  │ {context.version:<12} │")
        click.echo(f"└───────────┴──────────────┘")
    except ContextNotFoundError:
        click.echo("❌ 未找到项目配置。")
        click.echo("请先运行 'oc-collab init' 初始化项目。")
    except (ContextParseError, InvalidContextError) as e:
        click.echo(f"❌ 配置错误: {e}")


@click.command(name="todowrite")
@click.argument("todos", nargs=-1)
@click.option("--content", help="待办内容")
@click.option("--priority", type=click.Choice(["high", "medium", "low"]), default="medium")
@click.option("--agent", type=click.Choice(["1", "2"]), help="Agent 编号")
@click.option("--auto-check/--no-auto-check", default=True,
              help="是否自动检查参数 (默认启用)")
def todowrite_command(todos: tuple, content: Optional[str], priority: str, agent: Optional[str], auto_check: bool):
    """
    创建待办任务。

    示例:
      oc-collab todowrite --content "完成设计" --priority high --agent 2
    """
    from ..core.auto_checker import AutoChecker, ValidationError

    sync_manager = TodoSyncManager()

    def _do_todowrite():
        if content:
            agent_id = int(agent) if agent else None

            # v2.2.6: 自动检查
            if auto_check:
                checker = AutoChecker()
                result = checker.check_all(content, agent, priority)

                if result["warnings"]:
                    for warning in result["warnings"]:
                        click.echo(f"⚠️  {warning}")

                if not result["valid"]:
                    for error in result["errors"]:
                        click.echo(f"❌ {error}")
                    raise click.ClickException("参数验证失败")

            todo = sync_manager.add_todo(content, agent_id=agent_id, priority=priority)
            click.echo(f"✅ 待办已创建: [{todo.id}] {todo.content}")
            click.echo(f"   优先级: {todo.priority}")
            click.echo(f"   状态: {todo.status}")

            # v2.2.6: 上下文摘要
            if auto_check:
                from ..core.context_carrier import ContextCarrier
                carrier = ContextCarrier()
                summary = carrier.generate_context_summary(content)
                if summary:
                    click.echo(f"\n{summary}")

        for todo_file in todos:
            path = Path(todo_file)
            if path.exists():
                state = sync_manager.load_todos()
                click.echo(f"✅ 已从 {todo_file} 导入待办")

        click.echo(f"\n✓ 已同步到 {sync_manager.todo_file}")

    if sync_manager.sync_with_rollback(_do_todowrite):
        pass
    else:
        raise click.ClickException("待办创建失败")


@click.command(name="todoedit")
@click.argument("todo_id")
@click.option("--content", help="新的待办内容")
@click.option("--status", type=click.Choice(["pending", "in_progress", "completed", "cancelled"]))
@click.option("--priority", type=click.Choice(["high", "medium", "low"]))
def todoedit_command(todo_id: str, content: Optional[str], status: Optional[str], priority: Optional[str]):
    """
    编辑待办任务。

    示例:
      oc-collab todoedit TODO-001 --status completed
      oc-collab todoedit TODO-001 --priority high --content "新内容"
    """
    if not any([content, status, priority]):
        raise click.ClickException("请指定至少一个要更新的字段")

    sync_manager = TodoSyncManager()

    def _do_todoedit():
        updates = {}
        if content:
            updates["content"] = content
        if status:
            updates["status"] = status
        if priority:
            updates["priority"] = priority

        todo = sync_manager.update_todo(todo_id, **updates)

        if todo:
            click.echo(f"✅ 待办已更新: [{todo.id}] {todo.content}")
            click.echo(f"   状态: {todo.status}")
            click.echo(f"   优先级: {todo.priority}")
            click.echo(f"\n✓ 已同步到 {sync_manager.todo_file}")
        else:
            raise click.ClickException(f"未找到待办: {todo_id}")

    if sync_manager.sync_with_rollback(_do_todoedit):
        pass
    else:
        raise click.ClickException("待办更新失败")


@click.command(name="status")
def status_command():
    """显示当前项目状态和待办摘要。"""
    from ..core.state_manager import StateManager, StateFileNotFoundError
    from ..core.session_manager import SessionManager

    project_path = get_project_path()

    context_manager = ContextManager()
    sync_manager = TodoSyncManager()

    try:
        context = context_manager.load_context()
        agent_name = context_manager.get_agent_display_name(context.agent)
        agent_id = context.agent
    except ContextNotFoundError:
        click.echo("❌ 未找到项目配置。")
        click.echo("请先运行 'oc-collab init' 初始化项目。")
        return
    except (ContextParseError, InvalidContextError) as e:
        click.echo(f"❌ 配置错误: {e}")
        return

    try:
        state_manager = StateManager(project_path)
        state = state_manager.load_state()

        project_info = state.get("project", {})
        current_phase = project_info.get("phase") or state.get("phase", "未知")

        todos = sync_manager.get_todos_by_agent(agent_id=agent_id, status="pending")
        pending_count = len(todos)

        click.echo(f"┌───────────┬──────────────┐")
        click.echo(f"│ 当前阶段  │ {current_phase:<12} │")
        click.echo(f"│ 当前Agent│ {agent_name:<12} │")
        click.echo(f"│ 待办数量  │ {pending_count:<12} │")
        click.echo(f"└───────────┴──────────────┘")

        click.echo()

        if not todos:
            click.echo("暂无待办任务")
        else:
            priority_order = {"high": 0, "medium": 1, "low": 2}
            sorted_todos = sorted(todos, key=lambda t: priority_order.get(t.priority, 3))

            display_todos = sorted_todos[:5]

            click.echo(f"待办任务 ({agent_name}):")
            for todo in display_todos:
                priority_icon = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢",
                }.get(todo.priority, "⚪")

                status_icon = {
                    "pending": " ",
                    "in_progress": "🔄",
                }.get(todo.status, " ")

                click.echo(f"  [{priority_icon}] {status_icon} {todo.id}: {todo.content}")

            if len(todos) > 5:
                click.echo(f"  ... 还有 {len(todos) - 5} 个待办任务")

    except StateFileNotFoundError:
        click.echo("⚠️ 未找到项目状态文件")
