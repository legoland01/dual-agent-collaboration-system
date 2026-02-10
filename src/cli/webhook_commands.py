"""Webhook CLI命令

FR-WEB-001: Webhook基础配置
FR-WEB-002: 事件监听
"""

import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from ..core.webhook_config import WebhookConfigManager, WebhookConfigError
from ..core.event_listener import EventListener, CrashRecoveryPolicy

console = Console()


@click.command(name="init")
@click.option("--force", "-f", is_flag=True, help="强制重新生成配置")
def webhook_init(force: bool):
    """
    初始化Webhook配置。

    示例:
      oc-collab webhook init                 # 初始化配置
      oc-collab webhook init --force         # 强制重新生成
    """
    manager = WebhookConfigManager()

    try:
        if not force and manager.config_file.exists():
            config = manager.load_config()
            console.print("✅ Webhook配置已存在")
            console.print(f"   配置文件: {manager.config_file}")
            console.print(f"   GitHub Secret: {config.github.secret[:8]}...")
            console.print(f"   Gitee Secret: {config.gitee.secret[:8]}...")
            console.print(f"   回调URL: {config.get_callback_url()}")
            return

        config = manager.generate_config(force=force)
        console.print("✅ Webhook配置已生成")
        console.print(f"   配置文件: {manager.config_file}")
        console.print(f"   GitHub Secret: {config.github.secret[:8]}...")
        console.print(f"   Gitee Secret: {config.gitee.secret[:8]}...")
        console.print(f"   回调URL: {config.get_callback_url()}")

        console.print("\n请在GitHub/Gitee的Webhook设置中添加以下信息:")
        console.print(f"   Payload URL: {config.get_callback_url()}")
        console.print(f"   Content type: application/json")
        console.print(f"   Secret: {config.github.secret}")

    except WebhookConfigError as e:
        console.print(f"❌ 配置失败: {e}")
        raise click.Abort()


@click.command(name="status")
def webhook_status():
    """显示Webhook状态"""
    manager = WebhookConfigManager()
    status = manager.get_status()

    table = Table(title="Webhook 配置状态")
    table.add_column("配置项")
    table.add_column("状态")

    table.add_row("配置文件", "✅ 已配置" if status['configured'] else "❌ 未配置")

    if status['configured']:
        table.add_row("GitHub", "✅ 启用" if status['github_enabled'] else "❌ 禁用")
        table.add_row("Gitee", "✅ 启用" if status['gitee_enabled'] else "❌ 禁用")
        table.add_row("端口", str(status['port']))
        if 'callback_url' in status:
            table.add_row("回调URL", status['callback_url'])

    console.print(table)


@click.command(name="start")
@click.option("--port", "-p", type=int, help="监听端口")
@click.option("--no-recovery", is_flag=True, help="禁用崩溃恢复")
def webhook_start(port: Optional[int], no_recovery: bool):
    """
    启动Webhook监听服务。

    示例:
      oc-collab webhook start                # 使用默认配置启动
      oc-collab webhook start -p 9000       # 自定义端口
      oc-collab webhook start --no-recovery # 禁用崩溃恢复
    """
    manager = WebhookConfigManager()

    try:
        if not manager.config_file.exists():
            console.print("❌ 请先运行 'oc-collab webhook init' 初始化配置")
            raise click.Abort()

        config = manager.load_config()

        if port:
            config.server.port = port

        crash_recovery = None if no_recovery else CrashRecoveryPolicy()
        listener = EventListener(config=config, crash_recovery=crash_recovery)

        if listener.start_listening(port=config.server.port):
            console.print("✅ Webhook监听服务已启动")
            console.print(f"   监听地址: 0.0.0.0:{config.server.port}")
            console.print(f"   回调端点: {config.server.endpoint}")

            if crash_recovery:
                console.print(f"   崩溃恢复: 启用 (最多{CrashRecoveryPolicy.MAX_RETRIES}次重试)")

            console.print("\n按 Ctrl+C 停止监听")

            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                listener.stop()
                console.print("\n监听已停止")
        else:
            console.print("❌ 启动监听失败")
            raise click.Abort()

    except WebhookConfigError as e:
        console.print(f"❌ 加载配置失败: {e}")
        raise click.Abort()


@click.command(name="stop")
def webhook_stop():
    """停止Webhook监听服务"""
    from src.core.event_listener import EventListener
    from src.core.webhook_config import WebhookConfigManager

    manager = WebhookConfigManager()

    try:
        config = manager.load_config() if manager.config_file.exists() else None
        listener = EventListener(config=config)

        if listener.is_running():
            listener.stop()
            console.print("✅ Webhook监听服务已停止")
        else:
            console.print("ℹ️  Webhook监听服务未运行")
    except Exception:
        console.print("ℹ️  Webhook监听服务未运行")


@click.group()
def webhook_group():
    """Webhook管理命令"""
    pass


webhook_group.add_command(webhook_init, "init")
webhook_group.add_command(webhook_status, "status")
webhook_group.add_command(webhook_start, "start")
webhook_group.add_command(webhook_stop, "stop")
