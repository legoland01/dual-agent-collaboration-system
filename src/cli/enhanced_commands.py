"""增强的 CLI 命令：项目上下文和待办管理"""
import click
import sys
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
@click.option("--test-mode", is_flag=True, help="测试模式（不创建正式TODO，仅验证参数）")
@click.option("--to", "--receiver", "receiver", help="接收者Agent ID (如 1, 2)")
@click.option("--source", "-s", "source", default="MANUAL", help="来源标签 (REQUIREMENT/BUG/FEEDBACK/MANUAL)")
@click.option("--type", "template_type", help="模板类型 (REQUIREMENT/BUG_FIX/MANUAL)")
def todowrite_command(todos: tuple, content: Optional[str], priority: str, test_mode: bool, receiver: Optional[str], source: str, template_type: Optional[str]):
    """
    创建待办任务。

    示例:
      oc-collab todowrite --content "完成设计" --priority high
      oc-collab todowrite --content "测试" --test-mode  # 测试模式，不创建正式TODO
    """
    from ..core.auto_checker import AutoChecker, ValidationError
    from ..core.skill_enforcer import SkillEnforcer

    # v2.2.6: 参数验证
    checker = AutoChecker()
    
    # v2.2.7: BUG-20260210-001 修复 - Skill强制检查（v2.2.11要求移除--auto-check）
    skill_enforcer = SkillEnforcer()
    skill_result = skill_enforcer.check_before_action("todowrite")
    
    if skill_result["missing"]:
        click.echo(f"\n⚠️  缺少相关Skill (todowrite):")
        for skill in skill_result["missing"]:
            click.echo(f"   • {skill}")
        if skill_result["suggestions"]:
            click.echo(f"\n   建议: {skill_result['suggestions'][0]}")
        click.echo("")

    result = checker.check_all(content, None, priority)
    
    if result["warnings"]:
        for warning in result["warnings"]:
            click.echo(f"⚠️  {warning}")
    
    if not result["valid"]:
        for error in result["errors"]:
            click.echo(f"❌ {error}")
        sys.exit(1)

    # v2.3.1: ComplianceChecker集成 - 替换旧的ComplianceEnforcer
    from ..core.compliance_checker import ComplianceChecker
    try:
        context = ContextManager().load_context()
        current_agent_id = context.agent
        checker = ComplianceChecker(str(current_agent_id))
        
        # 检查TODO创建是否符合规则（在TODO创建后检查）
        # 合规检查将在TODO生成后进行，此处先跳过，由todowrite内部调用check_todo_create
        # 如果需要预先检查，可以在这里添加逻辑
    except ContextNotFoundError:
        click.echo("⚠️ 无法获取Agent上下文，建议先运行 'oc-collab switch 1' 或 'oc-collab switch 2' 切换Agent")
        click.echo("   为确保角色合规，请明确指定当前Agent身份")
    except Exception as e:
        click.echo(f"⚠️ 合规检查降级: {e}")
    
    # 检查是否有内容可创建
    if not content and not todos:
        click.echo("❌ 请提供 --content 或导入 TODO 文件")
        sys.exit(1)

    # 测试模式：只验证，不创建正式TODO
    if test_mode:
        click.echo(f"[TEST] 待办内容验证通过: {content}")
        click.echo(f"[TEST] Priority: {priority}")
        click.echo(f"[TEST] 测试模式下未创建正式TODO")
        sys.exit(0)

    sync_manager = TodoSyncManager()

    def _do_todowrite():
        if content:
            current_agent_id = None
            # 从ContextManager获取当前Agent上下文
            if not current_agent_id:
                try:
                    from ..core.context_manager import ContextManager, ContextNotFoundError
                    context = ContextManager().load_context()
                    if context.agent:
                        agent_str = str(context.agent)
                        if "agent" in agent_str:
                            current_agent_id = int(agent_str.replace("agent", ""))
                        else:
                            current_agent_id = int(agent_str)
                except Exception:
                    pass

            agent_id = current_agent_id
            
            # v2.3.1: 使用新格式生成TODO编号
            todo_content = content
            new_format_id = None
            if receiver:
                from ..core.todo_id_generator import TodoIdGenerator
                id_gen = TodoIdGenerator()
                new_format_id = id_gen.generate(str(agent_id), receiver)
            
            # v2.3.1: 来源标签处理（添加到内容前缀）
            if source and source != "MANUAL":
                todo_content = f"[{source}] {todo_content}"
            
            # v2.3.1: 传递new_format_id给add_todo
            todo = sync_manager.add_todo(todo_content, agent_id=agent_id, priority=priority, todo_id=new_format_id)
            
            # v2.3.1: 合规检查 - 验证TODO格式和创建者/接收者关系
            try:
                from ..core.context_manager import ContextManager as CM
                from ..core.compliance_checker import ComplianceChecker
                context = CM().load_context()
                current_agent_id = context.agent
                checker = ComplianceChecker(str(current_agent_id))
                
                todo_data = {
                    "id": new_format_id or todo.id,
                    "content": todo.content,
                    "creator": str(current_agent_id),
                    "receiver": receiver
                }
                allowed, error_msg = checker.check_todo_create(todo_data)
                if not allowed:
                    # 删除刚创建的TODO
                    sync_manager.delete_todo(todo.id)
                    click.echo(f"❌ 合规检查失败: {error_msg}")
                    sys.exit(3)
            except Exception as e:
                click.echo(f"⚠️ 合规检查异常: {e}")
            
            # 提取新格式ID用于显示
            if new_format_id:
                click.echo(f"✅ 待办已创建: [{new_format_id}] {content}")
                click.echo(f"   优先级: {priority}")
                click.echo(f"   状态: pending")
            else:
                click.echo(f"✅ 待办已创建: [{todo.id}] {todo.content}")
                click.echo(f"   优先级: {todo.priority}")
                click.echo(f"   状态: {todo.status}")

            # v2.2.9: StateNotifier集成 - 发送Webhook通知
            from ..core.context_manager import ContextManager, ContextNotFoundError
            from ..core.state_notifier import StateNotifier
            from ..core.todo_queue_manager import TodoQueueManager
            try:
                context = ContextManager().load_context()
                current_agent = context.agent
                
                # 初始化StateNotifier并传入queue_manager
                queue_manager = TodoQueueManager()
                notifier = StateNotifier(queue_manager=queue_manager)
                
                # 计算接收者
                receiver_agent = f"agent{receiver}" if receiver else f"agent{agent_id}"
                
                result = notifier.notify_todo_created(todo.id, todo.content, f"agent{current_agent}", to_agent=receiver_agent)
                if result:
                    click.echo("   🔔 通知已发送")
                else:
                    click.echo("   ⚠️ Webhook未配置，通知功能不可用")
                    click.echo("      如需启用通知，请配置 config/webhook.yaml")
            except Exception as e:
                click.echo(f"   ⚠️ 通知失败: {e}")

            # v2.2.15: AutoBugDetector集成 - 任务后自检
            # 注意：不再自动从StateManager获取Agent，必须显式switch
            agent_detected = False

            # 执行自检
            if agent_id:
                from ..core.auto_bug_detector import AutoBugDetector
                try:
                    detector = AutoBugDetector()
                    bugs = detector.self_review(todo.id, agent_id)
                    if bugs:
                        click.echo(f"\n⚠️  自检发现问题:")
                        for bug in bugs:
                            file_path = detector.generate_bug_report(bug)
                            click.echo(f"   📄 Bug报告: {bug.bug_id}")
                            click.echo(f"      {bug.description}")
                            click.echo(f"      📄 {file_path}")
                            click.echo(f"      ✅ 自动创建修复TODO: {bug.bug_id}")
                            fix_todo = sync_manager.add_todo(
                                f"修复{bug.bug_id}: {bug.description[:50]}...",
                                agent_id=2,
                                priority="high"
                            )
                            click.echo(f"      📋 {fix_todo.id} 已创建")
                except Exception as e:
                    click.echo(f"   ⚠️ 自检执行失败: {e}")
            else:
                # 明确提示跳过原因
                if agent_detected:
                    click.echo("   ℹ️ 无活跃Agent，跳过自检")
                else:
                    click.echo("   ℹ️ 无法确定Agent，跳过自检（可使用 --agent 指定）")

            # v2.2.6: 上下文摘要（始终启用）
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
        sys.exit(0)
    else:
        click.echo("❌ 待办创建失败")
        sys.exit(2)


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
