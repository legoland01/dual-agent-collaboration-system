"""StateReceiver CLI命令

F-NOTIF-001: StateNotifier Receiver CLI命令
"""

import click
import os
import signal
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table

console = Console()

PID_FILE = Path("state/state_receiver.pid")
DEFAULT_PORT = 8081


def get_pid() -> Optional[int]:
    """获取保存的PID"""
    try:
        if PID_FILE.exists():
            return int(PID_FILE.read_text().strip())
    except Exception:
        pass
    return None


def is_running(pid: int) -> bool:
    """检查进程是否在运行"""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def save_pid(pid: int):
    """保存PID"""
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(pid))


def remove_pid():
    """删除PID文件"""
    if PID_FILE.exists():
        PID_FILE.unlink()


@click.command(name="init")
def state_init():
    """
    初始化StateReceiver配置。

    示例:
      oc-collab state init
    """
    from ..core.state_queue import StateQueueManager

    try:
        queue_manager = StateQueueManager()
        stats = queue_manager.get_all_stats()
        console.print("✅ StateReceiver队列已初始化")
        console.print(f"   队列文件: {queue_manager.queue_file}")
        console.print(f"   待处理: {stats['pending']}")
        console.print(f"   已完成: {stats['read']}")
    except Exception as e:
        console.print(f"❌ 初始化失败: {e}")
        raise click.Abort()


@click.command(name="status")
def state_status():
    """显示StateReceiver状态"""
    from ..core.state_queue import StateQueueManager

    pid = get_pid()
    running = pid and is_running(pid)

    table = Table(title="StateReceiver 状态")
    table.add_column("配置项")
    table.add_column("状态")

    table.add_row("服务进程", "✅ 运行中" if running else "❌ 未运行")
    if running:
        table.add_row("PID", str(pid))

    try:
        queue_manager = StateQueueManager()
        stats = queue_manager.get_all_stats()
        table.add_row("待处理通知", str(stats.get('pending', 0)))
        table.add_row("已完成通知", str(stats.get('read', 0)))
        table.add_row("队列文件", str(queue_manager.queue_file))
    except Exception as e:
        table.add_row("队列状态", f"❌ 错误: {e}")

    console.print(table)

    if running:
        console.print(f"\nℹ️  健康检查: curl http://localhost:{DEFAULT_PORT}/webhook/state/health")


@click.command(name="start")
@click.option("--port", "-p", type=int, default=DEFAULT_PORT, help="监听端口")
@click.option("--daemon", "-d", is_flag=True, help="后台运行")
def state_start(port: int, daemon: bool):
    """
    启动StateReceiver服务。

    示例:
      oc-collab state start              # 使用默认配置启动
      oc-collab state start -p 9000    # 自定义端口
      oc-collab state start -d          # 后台运行
    """
    from ..core.state_receiver import StateReceiver
    from ..core.state_queue import StateQueueManager
    import threading

    pid = get_pid()
    if pid and is_running(pid):
        console.print(f"❌ StateReceiver已在运行 (PID: {pid})")
        raise click.Abort()

    try:
        queue_manager = StateQueueManager()
        receiver = StateReceiver(queue_manager=queue_manager)

        if daemon:
            import subprocess
            cmd = [sys.executable, "-c", f"""
import sys
sys.path.insert(0, '{Path(__file__).parent.parent.parent}')
from src.core.state_receiver import StateReceiver
from src.core.state_queue import StateQueueManager
qm = StateQueueManager()
r = StateReceiver(qm)
r.run(port={port})
"""]
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            save_pid(proc.pid)
            console.print(f"✅ StateReceiver已启动 (PID: {proc.pid})")
            console.print(f"   监听地址: 0.0.0.0:{port}")
            console.print(f"   端点: POST /webhook/state")
        else:
            console.print(f"✅ StateReceiver启动中...")
            console.print(f"   监听地址: 0.0.0.0:{port}")
            console.print(f"   端点: POST /webhook/state")
            console.print(f"   健康检查: GET /webhook/state/health")
            console.print(f"\n按 Ctrl+C 停止服务")

            def signal_handler(sig, frame):
                console.print("\n服务已停止")
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            receiver.run(host="0.0.0.0", port=port)

    except Exception as e:
        console.print(f"❌ 启动失败: {e}")
        raise click.Abort()


@click.command(name="stop")
def state_stop():
    """停止StateReceiver服务"""
    pid = get_pid()

    if not pid:
        console.print("ℹ️  StateReceiver未运行")
        return

    if not is_running(pid):
        console.print("ℹ️  PID文件存在但进程已停止，清理中...")
        remove_pid()
        return

    try:
        os.kill(pid, signal.SIGTERM)
        remove_pid()
        console.print(f"✅ StateReceiver已停止 (PID: {pid})")
    except OSError as e:
        if e.errno == 3:
            console.print("ℹ️  进程已不存在，清理PID文件")
            remove_pid()
        else:
            console.print(f"❌ 停止失败: {e}")
            raise click.Abort()


@click.command(name="queue")
@click.argument("agent_id", required=False)
def state_queue(agent_id: Optional[str]):
    """
    查看通知队列。

    示例:
      oc-collab state queue              # 查看所有通知
      oc-collab state queue agent1       # 查看指定Agent的通知
    """
    from ..core.state_queue import StateQueueManager
    from ..core.state_manager import StateManager

    try:
        queue_manager = StateQueueManager()

        if agent_id:
            stats = queue_manager.get_stats(agent_id)
            notifications = queue_manager.get_unread(agent_id)
        else:
            stats = queue_manager.get_all_stats()
            notifications = queue_manager.get_all_unread()

        table = Table(title=f"通知队列 {'(Agent: ' + agent_id + ')' if agent_id else ''}")
        table.add_column("ID")
        table.add_column("事件类型")
        table.add_column("来源")
        table.add_column("目标")
        table.add_column("状态")

        for n in notifications:
            table.add_row(
                n.id,
                n.event_type,
                n.source_agent,
                n.target_agent,
                n.status
            )

        console.print(table)
        console.print(f"\n统计: 待处理 {stats.get('pending', 0)}, 已完成 {stats.get('read', 0)}")

    except Exception as e:
        console.print(f"❌ 查询失败: {e}")
        raise click.Abort()


@click.command(name="mark-read")
@click.argument("notification_id")
def state_mark_read(notification_id: str):
    """
    标记通知为已读。

    示例:
      oc-collab state mark-read abc12345
    """
    from ..core.state_queue import StateQueueManager

    try:
        queue_manager = StateQueueManager()
        if queue_manager.mark_read(notification_id):
            console.print(f"✅ 通知 {notification_id} 已标记为已读")
        else:
            console.print(f"❌ 未找到通知: {notification_id}")
            raise click.Abort()
    except Exception as e:
        console.print(f"❌ 操作失败: {e}")
        raise click.Abort()


@click.group()
def state_group():
    """StateReceiver管理命令"""
    pass


state_group.add_command(state_init, "init")
state_group.add_command(state_status, "status")
state_group.add_command(state_start, "start")
state_group.add_command(state_stop, "stop")
state_group.add_command(state_queue, "queue")
state_group.add_command(state_mark_read, "mark-read")
