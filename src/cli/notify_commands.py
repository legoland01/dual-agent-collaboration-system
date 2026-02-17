"""通知相关命令 - 用于测试的CLI工具

用于自动化测试：模拟用户对TODO通知的操作回复

注意：此CLI工具在v2.3.2 SQLite版本中完整支持所有操作。
当前YAML版本仅支持view操作。
"""

import click
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.todo_queue_manager import TodoQueueManager


@click.group("notify")
def notify_group():
    """通知管理命令组"""
    pass


@notify_group.command("reply")
@click.option("--todo-id", required=True, help="TODO ID")
@click.option("--action", 
              type=click.Choice(["execute", "defer", "dismiss", "view"]), 
              required=True, 
              help="用户操作")
@click.option("--reason", default=None, help="拒绝原因（dismiss时使用）")
@click.option("--delay-minutes", type=int, default=0, help="延迟分钟数（defer时使用）")
def notify_reply_command(todo_id: str, action: str, reason: str, delay_minutes: int):
    """模拟用户对TODO通知的操作回复（测试用）
    
    用于E2E测试中模拟用户选择操作
    
    注意：当前YAML版本(execute/defer/dismiss需v2.3.2 SQLite版本)
    
    示例:
      oc-collab notify reply --todo-id TODO-1to2-001 --action view
      oc-collab notify reply --todo-id TODO-1to2-001 --action execute
      oc-collab notify reply --todo-id TODO-1to2-001 --action defer --delay-minutes 30
      oc-collab notify reply --todo-id TODO-1to2-001 --action dismiss --reason "不需要做"
    """
    queue_manager = TodoQueueManager()
    
    # 获取TODO
    todos = queue_manager.get_all()
    todo = None
    for t in todos:
        if t.id == todo_id:
            todo = t
            break
    
    if not todo:
        click.echo(f"❌ TODO不存在: {todo_id}")
        return
    
    # 查看详情
    if action == "view":
        click.echo(f"📋 TODO详情: {todo_id}")
        click.echo(f"   内容: {todo.content}")
        click.echo(f"   优先级: {todo.priority}")
        click.echo(f"   发送者: {todo.from_agent}")
        click.echo(f"   接收者: {todo.to_agent}")
        click.echo(f"   已读: {todo.read}")
        click.echo(f"   创建时间: {todo.created_at}")
        return
    
    # execute/defer/dismiss 需要v2.3.2 SQLite版本支持
    if action == "execute":
        click.echo(f"✅ 已执行: {todo_id}")
        click.echo(f"   操作: 标记为 in_progress")
        click.echo(f"   注意: 需要v2.3.2 SQLite版本支持")
        
    elif action == "defer":
        click.echo(f"✅ 已推迟: {todo_id}")
        click.echo(f"   操作: 标记为 deferred")
        click.echo(f"   延迟: {delay_minutes}分钟")
        click.echo(f"   注意: 需要v2.3.2 SQLite版本支持")
        
    elif action == "dismiss":
        click.echo(f"✅ 已拒绝: {todo_id}")
        click.echo(f"   操作: 标记为 cancelled")
        if reason:
            click.echo(f"   原因: {reason}")
        click.echo(f"   注意: 需要v2.3.2 SQLite版本支持")


@notify_group.command("status")
def notify_status_command():
    """查看通知状态
    
    示例:
      oc-collab notify status
    """
    queue_manager = TodoQueueManager()
    todos = queue_manager.get_all()
    
    read_count = sum(1 for t in todos if t.read)
    unread_count = len(todos) - read_count
    
    click.echo("\n📊 TODO状态统计:")
    click.echo(f"  未读: {unread_count}")
    click.echo(f"  已读: {read_count}")
    click.echo(f"  总计: {len(todos)}")
