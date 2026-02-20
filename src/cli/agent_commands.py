"""Agent管理命令"""

import click
import sys
import time
import subprocess
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.agent_registry import AgentRegistry
from ..core.todo_queue_manager import TodoQueueManager
from ..core.context_manager import ContextManager, ContextNotFoundError
from ..core.todo_storage import TodoStorage
from ..core.agent_listener import AgentListenerService


@click.group("agent")
def agent_group():
    """Agent管理命令组"""
    pass


@agent_group.command("register")
@click.option("--id", "agent_id", required=True, help="Agent ID")
@click.option("--role", required=True, help="角色 (PRODUCT_MANAGER/DEVELOPMENT_LEAD/FRONTEND_DEV/BACKEND_DEV/QA_ENGINEER)")
@click.option("--team", default="internal", help="团队")
def agent_register_command(agent_id: str, role: str, team: str):
    """注册Agent
    
    示例:
      oc-collab agent register --id agent3 --role FRONTEND_DEV --team frontend
    """
    try:
        registry = AgentRegistry()
        
        result = registry.register(agent_id, role, team)
        
        if result:
            click.echo(f"✅ Agent {agent_id} 注册成功 (role: {role}, team: {team})")
        else:
            click.echo(f"❌ 注册失败: 无效的角色 {role}")
            click.echo(f"有效角色: PRODUCT_MANAGER, DEVELOPMENT_LEAD, FRONTEND_DEV, BACKEND_DEV, QA_ENGINEER")
    
    except Exception as e:
        click.echo(f"❌ 注册失败: {e}")


@agent_group.command("auto-register")
def agent_auto_register_command():
    """自动注册Agent（从环境变量或Git config）
    
    示例:
      oc-collab agent auto-register
    """
    try:
        registry = AgentRegistry()
        
        result = registry.auto_register()
        
        if result:
            agent_id = registry.get_current_agent_id()
            click.echo(f"✅ Agent {agent_id} 自动注册成功")
        else:
            click.echo("❌ 自动注册失败: 无法获取Agent ID")
            click.echo("请设置环境变量 OC_AGENT_ID 或配置 Git config user.email")
    
    except Exception as e:
        click.echo(f"❌ 自动注册失败: {e}")


@agent_group.command("list")
@click.option("--json", is_flag=True, help="JSON格式输出")
def agent_list_command(json: bool):
    """列出所有Agent
    
    示例:
      oc-collab agent list
      oc-collab agent list --json
    """
    try:
        registry = AgentRegistry()
        
        agents = registry.list_agents()
        
        if not agents:
            click.echo("❌ 未找到已注册的Agent")
            return
        
        if json:
            import json
            click.echo(json.dumps(agents, indent=2, ensure_ascii=False))
        else:
            click.echo(f"\n🤖 Agent列表 ({len(agents)}个):")
            click.echo("-" * 60)
            
            for agent in agents:
                click.echo(f"  ID: {agent.get('id')}")
                click.echo(f"  角色: {agent.get('role')}")
                click.echo(f"  团队: {agent.get('team')}")
                click.echo(f"  状态: {agent.get('status')}")
                if agent.get('registered_at'):
                    click.echo(f"  注册时间: {agent.get('registered_at')}")
                click.echo("")
    
    except Exception as e:
        click.echo(f"❌ 查询失败: {e}")


@agent_group.command("unregister")
@click.argument("agent_id")
def agent_unregister_command(agent_id: str):
    """注销Agent
    
    示例:
      oc-collab agent unregister agent3
    """
    try:
        registry = AgentRegistry()
        
        if not registry.can_unregister(agent_id):
            click.echo(f"❌ 注销失败: Agent {agent_id} 有待处理的TODO")
            return
        
        result = registry.unregister(agent_id)
        
        if result:
            click.echo(f"✅ Agent {agent_id} 已注销")
        else:
            click.echo(f"❌ 注销失败: Agent {agent_id} 不存在")
    
    except Exception as e:
        click.echo(f"❌ 注销失败: {e}")


@agent_group.command("listen")
@click.option("--interval", "-i", default=1, help="轮询间隔（秒）", type=int)
@click.option("--daemon", "-d", is_flag=True, help="后台运行")
@click.option("--stop", is_flag=True, help="停止监听守护进程")
@click.option("--status", is_flag=True, help="查看监听守护进程状态")
def agent_listen_command(interval: int, daemon: bool, stop: bool, status: bool):
    """监听TODO队列，发现新TODO时自动通知
    
    示例:
      oc-collab agent listen              # 前台监听
      oc-collab agent listen --interval 5 # 5秒间隔
      oc-collab agent listen --daemon     # 后台监听
      oc-collab agent listen --stop       # 停止监听
      oc-collab agent listen --status     # 查看状态
    """
    project_path = Path(__file__).parent.parent.parent
    log_dir = project_path / "logs"
    log_file = log_dir / "agent_listen.log"
    pid_file = log_dir / "agent_listen.pid"
    
    # 处理 --stop 选项
    if stop:
        if pid_file.exists():
            with open(pid_file) as f:
                pid = int(f.read().strip())
            try:
                import signal
                os.kill(pid, signal.SIGTERM)
                click.echo(f"✅ 已发送停止信号到进程 {pid}")
                pid_file.unlink()
            except ProcessLookupError:
                click.echo(f"⚠️ 进程 {pid} 不存在")
            except PermissionError:
                click.echo(f"❌ 无权限停止进程 {pid}")
        else:
            click.echo("⚠️ 未找到监听进程PID文件，可能未在后台运行")
        return
    
    # 处理 --status 选项
    if status:
        if pid_file.exists():
            with open(pid_file) as f:
                pid = int(f.read().strip())
            try:
                import signal
                os.kill(pid, 0)
                click.echo(f"🔔 监听进程运行中 (PID: {pid})")
                if log_file.exists():
                    with open(log_file) as f:
                        lines = f.readlines()
                        if lines:
                            click.echo(f"   最后活动: {lines[-1].strip()[:80]}")
            except ProcessLookupError:
                click.echo("⚠️ 进程已停止，但PID文件未清理")
                pid_file.unlink()
        else:
            click.echo("ℹ️ 监听进程未运行")
        return
    
    # 正常的监听逻辑
    try:
        context = ContextManager().load_context()
        agent_id = context.agent
        if isinstance(agent_id, int):
            agent_id = f"agent{agent_id}"
    except Exception:
        click.echo("❌ 无法获取Agent上下文，请先运行 'oc-collab switch 1' 或 'oc-collab switch 2'")
        sys.exit(1)
    
    click.echo(f"🔔 开始监听 {agent_id} 的TODO队列（间隔 {interval} 秒）")
    click.echo("   按 Ctrl+C 停止")
    click.echo("")
    
    # 优先使用SQLite存储，回退到YAML
    storage = None
    queue_manager = None
    try:
        storage = TodoStorage()
        todos = storage.list(receiver=agent_id, status='pending', unread_only=True)
        has_sqlite = True
    except:
        queue_manager = TodoQueueManager()
        has_sqlite = False
    
    listener = AgentListenerService(storage, interval=interval)
    seen_ids = set()
    
    def poll_loop():
        """轮询循环"""
        while True:
            try:
                listener._check_trigger_files()
                
                if has_sqlite:
                    # 使用SQLite - 去掉agent前缀，因为数据库存储时不带前缀
                    receiver = agent_id.replace('agent', '') if agent_id else None
                    todos = storage.list(receiver=receiver, status='pending', unread_only=True)
                    new_todos = [t for t in todos if t.get('id') not in seen_ids]
                else:
                    # 使用YAML
                    unread = queue_manager.get_unread(agent_id)
                    new_todos = [t for t in unread if t.id not in seen_ids]
                
                if new_todos:
                    # 系统通知（跨平台）
                    for t in new_todos:
                        tid = t.get('id') or t.id
                        tcontent = t.get('content') or ''
                        tsender = t.get('sender') or t.from_agent or 'unknown'
                        title = f"新TODO: {tid}"
                        message = f"来自: {tsender}\n{tcontent[:100]}"
                        # 使用 Automator 创建通知
                        script = f'display notification "{message}" with title "{title}"'
                        os.system(f'/usr/bin/osascript -e \'{script}\' &')
                    
                    # 高亮输出到日志
                    for t in new_todos:
                        tid = t.get('id') or t.id
                        tcontent = t.get('content') or ''
                        tsender = t.get('sender') or t.from_agent or 'unknown'
                        click.echo(click.style(f"\n📬 [{datetime.now().strftime('%H:%M:%S')}] 新TODO: [{tid}] {tcontent[:50]}...", fg='green', bold=True))
                        click.echo(click.style(f"   来自: {tsender}", fg='cyan'))
                        seen_ids.add(tid)
                    click.echo("")
                    
            except Exception as e:
                click.echo(f"⚠️ 轮询错误: {e}")
            
            time.sleep(interval)
    
    if daemon:
        # 后台模式 - 使用subprocess
        project_path = Path(__file__).parent.parent.parent
        log_dir = project_path / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "agent_listen.log"
        
        cmd = [sys.executable, "-m", "src.cli.agent_commands", "agent", "listen", "--interval", str(interval)]
        
        try:
            with open(log_file, "a") as f:
                proc = subprocess.Popen(
                    cmd,
                    cwd=str(project_path),
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    start_new_session=True
                )
            
            click.echo(f"✅ 后台监听已启动 (PID: {proc.pid})")
            click.echo(f"   日志: {log_file}")
        except Exception as e:
            click.echo(f"❌ 后台启动失败: {e}")
    else:
        try:
            poll_loop()
        except KeyboardInterrupt:
            click.echo("\n\n⏹️ 监听已停止")
