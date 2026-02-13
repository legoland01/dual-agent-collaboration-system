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
from ..core.state_notifier import StateNotifier


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
              help="是否自动检查参数和Skill (默认启用)")
@click.option("--test-mode", is_flag=True, help="测试模式（不创建正式TODO，仅验证参数）")
def todowrite_command(todos: tuple, content: Optional[str], priority: str, agent: Optional[str], auto_check: bool, test_mode: bool):
    """
    创建待办任务。

    示例:
      oc-collab todowrite --content "完成设计" --priority high --agent 2
      oc-collab todowrite --content "测试" --test-mode  # 测试模式，不创建正式TODO
    """
    from ..core.auto_checker import AutoChecker, ValidationError
    from ..core.skill_enforcer import SkillEnforcer

    # v2.2.6: 参数验证
    checker = AutoChecker()
    
    # v2.2.7: BUG-20260210-001 修复 - Skill强制检查
    if auto_check:
        skill_enforcer = SkillEnforcer()
        skill_result = skill_enforcer.check_before_action("todowrite")
        
        if skill_result["missing"]:
            click.echo(f"\n⚠️  缺少相关Skill (todowrite):")
            for skill in skill_result["missing"]:
                click.echo(f"   • {skill}")
            if skill_result["suggestions"]:
                click.echo(f"\n   建议: {skill_result['suggestions'][0]}")
            click.echo("")

        result = checker.check_all(content, agent, priority)
        
        if result["warnings"]:
            for warning in result["warnings"]:
                click.echo(f"⚠️  {warning}")
        
        if not result["valid"]:
            for error in result["errors"]:
                click.echo(f"❌ {error}")
            raise click.ClickException("参数验证失败")

    # v2.2.9: ComplianceEnforcer集成 - Agent1禁止执行todowrite
    from ..core.compliance_enforcer import ComplianceEnforcer
    try:
        context = ContextManager().load_context()
        current_agent_id = context.agent
        enforcer = ComplianceEnforcer(current_agent_id)
        compliance_result = enforcer.check("todowrite")

        if not compliance_result.allowed:
            click.echo(f"\n{compliance_result.message}\n")
            enforcer.record_violation(compliance_result)
            raise click.Abort()
    except ContextNotFoundError:
        pass
    except Exception as e:
        click.echo(f"⚠️ 合规检查跳过: {e}")
    
    # 检查是否有内容可创建
    if not content and not todos:
        raise click.ClickException("请提供 --content 或导入 TODO 文件")

    # 测试模式：只验证，不创建正式TODO
    if test_mode:
        click.echo(f"[TEST] 待办内容验证通过: {content}")
        click.echo(f"[TEST] Agent: {agent}, Priority: {priority}")
        click.echo(f"[TEST] 测试模式下未创建正式TODO")
        return

    sync_manager = TodoSyncManager()

    def _do_todowrite():
        if content:
            agent_id = int(agent) if agent else None
            todo = sync_manager.add_todo(content, agent_id=agent_id, priority=priority)
            click.echo(f"✅ 待办已创建: [{todo.id}] {todo.content}")
            click.echo(f"   优先级: {todo.priority}")
            click.echo(f"   状态: {todo.status}")

            # v2.2.9: StateNotifier集成 - 发送Webhook通知
            from ..core.context_manager import ContextManager, ContextNotFoundError
            try:
                context = ContextManager().load_context()
                current_agent = context.agent
                notifier = StateNotifier()
                if notifier.notify_todo_created(todo.id, todo.content, f"agent{current_agent}"):
                    click.echo("   🔔 Webhook通知已发送")
                else:
                    click.echo("   ℹ️ Webhook未配置（静默跳过）")
            except (ContextNotFoundError, Exception):
                click.echo("   ℹ️ Webhook通知跳过（上下文不存在）")

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

            # v2.2.9: AutoBugDetector集成 - TODO完成时检查文档状态
            if status == "completed":
                from ..core.auto_bug_detector import AutoBugDetector
                from ..core.state_manager import StateManager
                try:
                    project_path = get_project_path()
                    state_manager = StateManager(project_path)
                    detector = AutoBugDetector(state_manager=state_manager)
                    bugs = detector.check_todo_completion(todo_id)
                    if bugs:
                        click.echo(f"\n⚠️  检测到 {len(bugs)} 个问题:")
                        for bug in bugs:
                            file_path = detector.generate_bug_report(bug)
                            click.echo(f"   📄 Bug报告: {bug.bug_id}")
                            click.echo(f"      {bug.description}")
                except Exception as e:
                    click.echo(f"   ℹ️ 自动检查跳过: {e}")

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
