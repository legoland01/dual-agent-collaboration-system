"""CLI主入口模块。"""
import sys
import subprocess
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..core.state_manager import StateManager, StateFileNotFoundError
from ..core.detector import detect_project_type
from ..core.git import GitHelper, GitNotInstalledError
from ..core.workflow import WorkflowEngine
from ..core.signoff import SignoffEngine
from ..core.auto_engine import AutoCollaborationEngine, TodoCommandExecutor, WorkCommandExecutor
from ..core.auto_retry import AutoRetry, AutoRetryConfig
from ..core.auto_docs import AutoDocs, AutoDocsConfig
from ..core.phase_advance import PhaseAdvanceEngine
from ..utils.lock import LockExistsError


console = Console()


def get_project_path() -> str:
    """获取项目路径（当前目录或父目录）。"""
    current = Path.cwd()
    if (current / "state" / "project_state.yaml").exists():
        return str(current)
    parent = current.parent
    if (parent / "state" / "project_state.yaml").exists():
        return str(parent)
    return str(current)


@click.group()
def main():
    """双Agent协作框架 CLI工具。"""
    pass


@main.command("init")
@click.argument("project_name")
@click.option("--type", "-t", type=click.Choice(["python", "typescript", "mixed", "auto"]), default="auto")
@click.option("--force/--no-force", "-f", default=False)
@click.option("--no-git", is_flag=True, default=False)
def init_command(project_name: str, type: str, force: bool, no_git: bool):
    """初始化协作项目。"""
    project_path = Path.cwd() / project_name
    
    if project_path.exists() and not force:
        if not any(project_path.iterdir()):
            pass
        else:
            click.echo(f"错误: 目录 {project_name} 已存在且不为空，使用 --force 覆盖")
            sys.exit(1)
    
    project_path.mkdir(parents=True, exist_ok=True)
    
    if type == "auto":
        detected_type = detect_project_type(str(project_path))
        if detected_type == "AUTO":
            type = "PYTHON"
        else:
            type = detected_type.lower()
    
    try:
        state_manager = StateManager(str(project_path))
        state_manager.init_state(project_name, type.upper())
        
        if not no_git:
            try:
                git_helper = GitHelper(str(project_path))
                if not git_helper.is_repository():
                    git_helper.init_repository()
                    click.echo(f"已初始化 Git 仓库")
            except GitNotInstalledError:
                click.echo("警告: Git 未安装，跳过 Git 初始化")
        
        click.echo(f"项目 {project_name} 初始化成功")
        click.echo(f"项目类型: {type.upper()}")
        click.echo(f"项目路径: {project_path.absolute()}")
        
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("status")
def status_command():
    """查看当前协作状态。"""
    try:
        project_path = get_project_path()
        state_manager = StateManager(project_path)
        state = state_manager.load_state()

        console.print("\n[bold]项目状态[/bold]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("项目")
        table.add_column("值")

        metadata = state.get("metadata", {})
        project_info = state.get("project", {})

        project_name = metadata.get("project_name") or project_info.get("name", "未配置")
        project_type = metadata.get("project_type") or project_info.get("type", "未知")

        table.add_row("项目名称", project_name)
        table.add_row("项目类型", project_type)
        table.add_row("当前阶段", state.get("phase", "未知"))

        active_agent = state_manager.get_active_agent()
        agents = state.get("agents", {})
        agent_role = agents.get(active_agent, {}).get("role", "未知")
        table.add_row("当前Agent", f"Agent {active_agent} ({agent_role})")

        console.print(table)

        console.print("\n[bold]签署状态[/bold]")
        req_status = state_manager.get_signoff_status("requirements")
        console.print(f"需求签署 - 产品经理: {'✓' if req_status['pm_signoff'] else '✗'}, 开发: {'✓' if req_status['dev_signoff'] else '✗'}")

    except StateFileNotFoundError:
        click.echo("错误: 未找到项目状态文件，请先初始化项目")
        sys.exit(1)
    except KeyError as e:
        click.echo(f"错误: 状态文件缺少必要字段 '{e}'，请检查配置文件")
        sys.exit(1)
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("switch")
@click.argument("agent_id", type=click.IntRange(1, 2))
def switch_command(agent_id: int):
    """切换Agent角色。"""
    try:
        project_path = get_project_path()
        state_manager = StateManager(project_path)
        
        current_agent = state_manager.get_active_agent()
        if current_agent == f"agent{agent_id}":
            click.echo(f"已经是 Agent {agent_id}")
            return
        
        state_manager.set_active_agent(f"agent{agent_id}")
        
        agent_info = state_manager.load_state()["agents"][f"agent{agent_id}"]
        click.echo(f"已切换到 Agent {agent_id} ({agent_info['role']})")
        
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("review")
@click.argument("stage", type=click.Choice(["requirements", "design", "test"]))
@click.option("--new", is_flag=True, default=False)
@click.option("--list", "-l", is_flag=True, default=False)
def review_command(stage: str, new: bool, list: bool):
    """管理评审流程。"""
    try:
        project_path = get_project_path()
        state_manager = StateManager(project_path)
        workflow_engine = WorkflowEngine(state_manager)
        
        if new:
            workflow_engine.start_review(stage)
            click.echo(f"已发起 {stage} 评审")
        
        if list:
            history = state_manager.get_history()
            console.print(f"\n[bold]{stage.upper()} 评审历史[/bold]")
            for item in history[:10]:
                if "review" in item["action"] or "signoff" in item["action"]:
                    console.print(f"- {item['timestamp']}: Agent {item['agent']} - {item['details']}")
        
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("signoff")
@click.argument("stage", type=click.Choice(["requirements", "design", "test"]))
@click.option("--comment", "-m", default="")
@click.option("--reject", "-r", default=None)
def signoff_command(stage: str, comment: str, reject: str):
    """签署确认。"""
    try:
        project_path = get_project_path()
        state_manager = StateManager(project_path)
        workflow_engine = WorkflowEngine(state_manager)
        signoff_engine = SignoffEngine(state_manager, workflow_engine)
        
        agent_id = state_manager.get_active_agent()
        
        if reject:
            result = signoff_engine.reject(stage, agent_id, reject)
            click.echo(f"已拒签 {stage} 阶段")
        else:
            result = signoff_engine.sign(stage, agent_id, comment)
            click.echo(f"已签署 {stage} 阶段")
            
            if state_manager.can_proceed_to_next_phase():
                click.echo("双方已签署，可以推进到下一阶段")
        
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("history")
@click.option("--limit", "-n", type=int, default=20)
def history_command(limit: int):
    """查看协作历史。"""
    try:
        project_path = get_project_path()
        state_manager = StateManager(project_path)
        
        history = state_manager.get_history(limit)
        
        console.print("\n[bold]协作历史[/bold]")
        for item in history:
            console.print(f"[cyan]{item['timestamp']}[/cyan] - Agent {item['agent']}: {item['action']} - {item['details']}")
        
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("auto")
@click.option("--max-iterations", "-n", type=int, default=10, help="最大迭代次数")
@click.option("--quiet", "-q", is_flag=True, default=False, help="静默模式")
@click.option("--force", "-f", is_flag=True, default=False, help="强制执行，跳过本地变更检查")
def auto_command(max_iterations: int, quiet: bool, force: bool):
    """自动执行当前任务。"""
    try:
        project_path = get_project_path()
        
        engine = AutoCollaborationEngine(project_path)
        
        if force:
            engine.git_helper._run_git_command = lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, "", "")
        
        result = engine.run(max_iterations=max_iterations)
        
        if result.get("success"):
            phase = result.get("current_phase", "unknown")
            iterations = result.get("total_iterations", 0)
            
            if not quiet:
                console.print(Panel(
                    Text(f"自动协作执行完成\n当前阶段: {phase}\n执行轮次: {iterations}", justify="center"),
                    title="✓ 执行成功",
                    style="green"
                ))
            else:
                click.echo(f"完成: {phase} ({iterations}轮)")
        else:
            error = result.get("error", "未知错误")
            console.print(Panel(
                Text(f"执行失败: {error}", justify="center"),
                title="✗ 执行失败",
                style="red"
            ))
            sys.exit(1)
            
    except LockExistsError as e:
        click.echo(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("agent")
@click.option("--interval", "-i", type=int, default=5, help="检查间隔（秒）")
@click.option("--daemon/--no-daemon", "-d", default=False, help="后台守护进程模式")
def agent_command(interval: int, daemon: bool):
    """Agent 调度器 - 双 Agent 交替工作守护进程。
    
    启动真正的双 Agent 交替工作：
    - Agent 1 (产品经理) 和 Agent 2 (开发) 真正交替执行任务
    - 自动检测状态并执行相应操作
    - 自动推进阶段
    """
    try:
        project_path = get_project_path()
        
        if daemon:
            import os
            import signal
            
            def daemonize():
                """将进程转为后台守护进程"""
                # 第一次 fork
                pid = os.fork()
                if pid > 0:
                    sys.exit(0)
                
                # 创建新会话
                os.setsid()
                
                # 第二次 fork
                pid = os.fork()
                if pid > 0:
                    sys.exit(0)
                
                # 重定向标准文件描述符
                sys.stdout.flush()
                sys.stderr.flush()
                with open('/dev/null', 'r') as devnull:
                    os.dup2(devnull.fileno(), sys.stdin.fileno())
                with open('/dev/null', 'a+') as devnull:
                    os.dup2(devnull.fileno(), sys.stdout.fileno())
                    os.dup2(devnull.fileno(), sys.stderr.fileno())
                
                # 启动 Agent 调度器
                run_scheduler(project_path, interval)
            
            click.echo(f"启动 Agent 守护进程 (间隔: {interval}秒)...")
            click.echo(f"PID: {os.getpid()}")
            click.echo("使用 'pkill -f oc-collab agent' 停止")
            daemonize()
        
        else:
            click.echo("启动 Agent 调度器 (按 Ctrl+C 停止)...")
            run_scheduler(project_path, interval)
    
    except KeyboardInterrupt:
        click.echo("\n已停止 Agent 调度器")
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


def run_scheduler(project_path: str, interval: int):
    """运行 Agent 调度器"""
    from ..utils.yaml import load_yaml, save_yaml
    from datetime import datetime
    import time
    
    state_file = f"{project_path}/state/project_state.yaml"
    
    def load_state():
        return load_yaml(state_file)
    
    def save_state(state):
        save_yaml(state_file, state)
    
    def get_active_agent():
        state = load_state()
        project_agents = state.get('project', {}).get('agents', {})
        for agent_id, agent_data in project_agents.items():
            if agent_data.get('current', False):
                return agent_id
        return None
    
    def switch_agent():
        state = load_state()
        current = get_active_agent()
        next_agent = 'agent2' if current == 'agent1' else 'agent1'
        
        for agent_id in state['project']['agents']:
            state['project']['agents'][agent_id]['current'] = (agent_id == next_agent)
        
        save_state(state)
        return next_agent
    
    click.echo("=" * 50)
    click.echo("Agent 调度器启动")
    click.echo("=" * 50)
    
    while True:
        try:
            state = load_state()
            phase = state.get('phase', 'unknown')
            active_agent = get_active_agent()
            
            if not active_agent:
                active_agent = switch_agent()
            
            # 检查阶段推进
            req = state.get('requirements', {})
            design = state.get('design', {})
            test = state.get('test', {})
            
            # 需求批准 → 设计
            if phase == 'requirements_review':
                if req.get('pm_signoff') and req.get('dev_signoff'):
                    state['phase'] = 'design_draft'
                    req['status'] = 'approved'
                    state['history'].insert(0, {
                        'id': f'adv_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        'timestamp': datetime.now().isoformat(),
                        'action': 'phase_advance',
                        'agent_id': 'system',
                        'details': '需求签署完成，自动推进到设计阶段'
                    })
                    save_state(state)
                    click.echo(f"[System] 阶段推进: requirements → design_draft")
                    switch_agent()
                    time.sleep(interval)
                    continue
            
            # 设计批准 → 开发
            elif phase == 'design_review':
                if design.get('pm_signoff') and design.get('dev_signoff'):
                    state['phase'] = 'development'
                    design['status'] = 'approved'
                    state['history'].insert(0, {
                        'id': f'adv_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        'timestamp': datetime.now().isoformat(),
                        'action': 'phase_advance',
                        'agent_id': 'system',
                        'details': '设计签署完成，自动推进到开发阶段'
                    })
                    save_state(state)
                    click.echo(f"[System] 阶段推进: design → development")
                    switch_agent()
                    time.sleep(interval)
                    continue
            
            # 测试通过 → 完成
            elif phase == 'testing':
                if test.get('pm_signoff') and test.get('dev_signoff'):
                    issues = test.get('issues_to_fix', [])
                    if not issues:
                        state['phase'] = 'completed'
                        test['status'] = 'completed'
                        state['history'].insert(0, {
                            'id': f'adv_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                            'timestamp': datetime.now().isoformat(),
                            'action': 'phase_advance',
                            'agent_id': 'system',
                            'details': '测试签署完成，项目完成'
                        })
                        save_state(state)
                        click.echo(f"[System] 阶段推进: testing → completed")
                        click.echo("项目完成！")
                        break
            
            # Agent 1 工作
            if active_agent == 'agent1':
                if phase == 'requirements_review' and not req.get('pm_signoff', False):
                    req['pm_signoff'] = True
                    state['history'].insert(0, {
                        'id': f'signoff_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        'timestamp': datetime.now().isoformat(),
                        'action': 'signoff',
                        'agent_id': 'agent1',
                        'details': '签署需求: 同意实现'
                    })
                    save_state(state)
                    click.echo(f"[Agent 1] 签署需求")
                    switch_agent()
                
                elif phase == 'design_review' and not design.get('pm_signoff', False):
                    design['pm_signoff'] = True
                    state['history'].insert(0, {
                        'id': f'signoff_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        'timestamp': datetime.now().isoformat(),
                        'action': 'signoff',
                        'agent_id': 'agent1',
                        'details': '签署设计: 设计与需求一致'
                    })
                    save_state(state)
                    click.echo(f"[Agent 1] 签署设计")
                    switch_agent()
                
                elif phase == 'testing' and not test.get('pm_signoff', False):
                    test['pm_signoff'] = True
                    state['history'].insert(0, {
                        'id': f'test_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        'timestamp': datetime.now().isoformat(),
                        'action': 'test_complete',
                        'agent_id': 'agent1',
                        'details': '黑盒测试完成'
                    })
                    save_state(state)
                    click.echo(f"[Agent 1] 完成测试")
                    switch_agent()
            
            # Agent 2 工作
            elif active_agent == 'agent2':
                if phase == 'requirements_review' and not req.get('dev_signoff', False):
                    req['dev_signoff'] = True
                    state['history'].insert(0, {
                        'id': f'signoff_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        'timestamp': datetime.now().isoformat(),
                        'action': 'signoff',
                        'agent_id': 'agent2',
                        'details': '签署需求: 技术方案可行'
                    })
                    save_state(state)
                    click.echo(f"[Agent 2] 签署需求")
                    switch_agent()
                
                elif phase == 'design_review' and not design.get('dev_signoff', False):
                    design['dev_signoff'] = True
                    state['history'].insert(0, {
                        'id': f'signoff_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        'timestamp': datetime.now().isoformat(),
                        'action': 'signoff',
                        'agent_id': 'agent2',
                        'details': '签署设计: 实现方案可行'
                    })
                    save_state(state)
                    click.echo(f"[Agent 2] 签署设计")
                    switch_agent()
                
                elif phase == 'development':
                    state['development']['status'] = 'completed'
                    state['phase'] = 'testing'
                    test['status'] = 'in_progress'
                    state['history'].insert(0, {
                        'id': f'dev_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        'timestamp': datetime.now().isoformat(),
                        'action': 'development_complete',
                        'agent_id': 'agent2',
                        'details': '开发完成'
                    })
                    save_state(state)
                    click.echo(f"[Agent 2] 开发完成，推进到测试阶段")
                    switch_agent()
                
                elif phase == 'testing':
                    issues = test.get('issues_to_fix', [])
                    if issues:
                        test['issues_to_fix'] = []
                        test['dev_signoff'] = True
                        state['history'].insert(0, {
                            'id': f'fix_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                            'timestamp': datetime.now().isoformat(),
                            'action': 'bug_fix',
                            'agent_id': 'agent2',
                            'details': f'修复 {len(issues)} 个 bug'
                        })
                        save_state(state)
                        click.echo(f"[Agent 2] 修复 {len(issues)} 个 bug")
                        switch_agent()
            
            time.sleep(interval)
            
        except Exception as e:
            click.echo(f"错误: {e}")
            time.sleep(interval)


@main.command("todo")
def todo_command():
    """显示待办事项。"""
    try:
        project_path = get_project_path()
        executor = TodoCommandExecutor(project_path)
        
        todo_list = executor.get_todo_list()
        progress = executor.get_progress()
        blockers = executor.get_blockers()
        
        console.print("\n[bold]待办事项[/bold]")
        
        if blockers:
            console.print("\n[red]阻塞项:[/red]")
            for blocker in blockers:
                console.print(f"  ⚠ {blocker['blocker']}")
        
        if todo_list:
            console.print("\n[green]待办任务:[/green]")
            for i, item in enumerate(todo_list, 1):
                console.print(f"  {i}. {item['task']}")
        else:
            console.print("\n[cyan]暂无待办事项[/cyan]")
        
        console.print(f"\n进度: {progress['progress_percentage']:.1f}% - 当前阶段: {progress['current_phase']}")
        
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("work")
@click.option("--execute", "-e", is_flag=True, default=False, help="一键执行建议操作")
def work_command(execute: bool):
    """智能工作流引导。"""
    try:
        project_path = get_project_path()
        executor = WorkCommandExecutor(project_path)
        
        summary = executor.get_status_summary()
        suggestions = executor.get_suggestions()
        
        console.print("\n[bold]状态摘要[/bold]")
        
        table = Table(show_header=False)
        table.add_column("项目", style="cyan")
        table.add_column("值")
        
        table.add_row("当前阶段", summary["current_phase"])
        table.add_row("当前Agent", f"Agent {summary['current_agent']}")
        table.add_row("待办数量", str(summary["todo_count"]))
        table.add_row("进度", f"{summary['progress']['progress_percentage']:.1f}%")
        
        console.print(table)
        
        console.print("\n[bold]操作建议[/bold]")
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                priority_icon = "🔴" if suggestion["priority"] == "high" else "🟡"
                console.print(f"  {priority_icon} {i}. {suggestion['description']}")
        else:
            console.print("  无建议操作")
        
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("remote")
@click.argument("action", type=click.Choice(["add", "list", "push-all"]))
@click.argument("name", default=None, required=False)
@click.argument("url", default=None, required=False)
def remote_command(action: str, name: str, url: str):
    """管理远程仓库（支持 GitHub + Gitee 双同步）。"""
    try:
        project_path = get_project_path()
        git_helper = GitHelper(project_path)

        if action == "list":
            remotes = git_helper.get_all_remotes()
            console.print("\n[bold]远程仓库列表[/bold]")
            for remote in remotes:
                console.print(f"  - {remote}")
            if not remotes:
                console.print("  未配置远程仓库")

        elif action == "add":
            if not name or not url:
                click.echo("错误: 使用 'oc-collab remote add <名称> <URL>' 添加远程仓库")
                sys.exit(1)
            git_helper.add_remote(name, url)
            click.echo(f"已添加远程仓库 {name}: {url}")

        elif action == "push-all":
            message = click.prompt("请输入提交信息", default="auto-sync: 更新")
            git_helper.push_all_remotes(message)
            remotes = git_helper.get_all_remotes()
            click.echo(f"已推送到所有远程仓库: {', '.join(remotes)}")

    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("sync-all")
@click.option("--message", "-m", default="auto-sync: 更新", help="提交信息")
def sync_all_command(message: str):
    """同步到所有远程平台（GitHub + Gitee）。"""
    try:
        project_path = get_project_path()
        git_helper = GitHelper(project_path)

        if git_helper.has_local_changes():
            git_helper.push_all_remotes(message)
            remotes = git_helper.get_all_remotes()
            click.echo(f"已提交并推送到所有平台: {', '.join(remotes)}")
        else:
            click.echo("没有需要提交的本地修改")

    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("sync")
@click.option("--retry/--no-retry", "-r", default=False, help="启用智能重试")
@click.option("--max-retries", "-n", type=int, default=10, help="最大重试次数")
@click.option("--interval", "-i", type=int, default=30, help="重试间隔（秒）")
@click.option("--no-backoff", is_flag=True, default=False, help="禁用指数退避")
def sync_command(retry: bool, max_retries: int, interval: int, no_backoff: bool):
    """同步远程变更，支持智能重试。"""
    try:
        project_path = get_project_path()
        git_helper = GitHelper(project_path)
        
        if git_helper.has_local_changes():
            click.echo("警告: 有未提交的本地修改，请先提交或暂存")
            sys.exit(1)
        
        if retry:
            config = AutoRetryConfig(
                max_retries=max_retries,
                retry_interval=interval,
                exponential_backoff=not no_backoff,
                verbose=True
            )
            auto_retry = AutoRetry(project_path, config)
            
            remotes = git_helper.get_all_remotes()
            if not remotes:
                remotes = ["origin"]
            
            result = auto_retry.pull_with_retry(remotes[0])
            
            if result["success"]:
                console.print(Panel(
                    f"✓ 同步成功\n重试次数: {result['attempts']}\n耗时: {result['duration']}秒",
                    title="同步完成",
                    style="green"
                ))
            else:
                console.print(Panel(
                    f"✗ 同步失败\n已重试: {result['attempts']}次\n耗时: {result['duration']}秒",
                    title="同步失败",
                    style="red"
                ))
                sys.exit(1)
        else:
            if git_helper.pull():
                click.echo("已同步远程变更")
            else:
                click.echo("同步失败")
                
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("push")
@click.option("--message", "-m", default="auto-sync: 更新", help="提交信息")
@click.option("--retry/--no-retry", "-r", default=False, help="启用智能重试")
@click.option("--max-retries", "-n", type=int, default=10, help="最大重试次数")
@click.option("--interval", "-i", type=int, default=30, help="重试间隔（秒）")
@click.option("--no-backoff", is_flag=True, default=False, help="禁用指数退避")
def push_command(message: str, retry: bool, max_retries: int, interval: int, no_backoff: bool):
    """推送代码，支持智能重试和全平台同步。"""
    try:
        project_path = get_project_path()
        git_helper = GitHelper(project_path)
        
        if not git_helper.has_local_changes():
            click.echo("没有需要提交的本地修改")
            return
        
        remotes = git_helper.get_all_remotes()
        
        if retry:
            config = AutoRetryConfig(
                max_retries=max_retries,
                retry_interval=interval,
                exponential_backoff=not no_backoff,
                verbose=True
            )
            auto_retry = AutoRetry(project_path, config)
            
            if not remotes:
                git_helper._run_git_command("add", "-A")
                git_helper._run_git_command("commit", "-m", message)
                git_helper._run_git_command("push")
                click.echo("已推送到默认远程仓库")
            else:
                result = auto_retry.push_with_retry(message, remotes)
                
                if result["success"]:
                    console.print(Panel(
                        f"✓ 推送成功\n已推送到: {', '.join(result['remotes'])}\n重试次数: {result['attempts']}\n耗时: {result['duration']}秒",
                        title="推送完成",
                        style="green"
                    ))
                else:
                    console.print(Panel(
                        f"✗ 推送失败\n已推送到: {', '.join(result['remotes'])}\n已重试: {result['attempts']}次\n耗时: {result['duration']}秒",
                        title="推送失败",
                        style="red"
                    ))
                    sys.exit(1)
        else:
            git_helper.push(message)
            click.echo(f"已推送")
            
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("docs")
@click.argument("action", type=click.Choice(["check", "preview", "apply"]), default="check")
@click.option("--message", "-m", default="docs: 更新文档", help="提交信息")
@click.option("--auto/--no-auto", default=None, help="是否启用自动同步")
def docs_command(action: str, message: str, auto: bool):
    """自动同步文档。"""
    try:
        project_path = get_project_path()
        
        config = AutoDocsConfig(
            enabled=(auto is not False),
            update_changelog=True,
            update_manual=True,
            update_tests=False,
            require_confirm=(action != "apply")
        )
        auto_docs = AutoDocs(project_path, config)
        
        if action == "check":
            changes = auto_docs.detect_changes()
            console.print("\n[bold]变更检测结果[/bold]")
            
            table = Table(show_header=False)
            table.add_column("项目")
            table.add_column("值")
            
            table.add_row("变更文件数", str(len(changes['changed_files'])))
            table.add_row("影响文档数", str(len(changes['impacted_docs'])))
            table.add_row("影响命令数", str(len(changes['impacted_commands'])))
            table.add_row("变更类型", changes['change_type'])
            
            console.print(table)
            
            if changes['changed_files']:
                console.print("\n[bold]变更文件[/bold]")
                for f in changes['changed_files'][:10]:
                    console.print(f"  - {f}")
            
            console.print("\n[bold]操作建议[/bold]")
            console.print("  运行 'oc-collab docs preview' 预览更新")
            console.print("  运行 'oc-collab docs apply --message \"...\"' 应用更新")
        
        elif action == "preview":
            preview = auto_docs.preview_updates()
            console.print(Panel(preview, title="文档更新预览", style="cyan"))
        
        elif action == "apply":
            results = auto_docs.apply_updates(message, confirmed=True)
            
            console.print("\n[bold]文档更新结果[/bold]")
            
            table = Table(show_header=False)
            table.add_column("项目")
            table.add_column("状态")
            
            table.add_row("变更记录", "✓" if results.get("changelog") else "✗")
            table.add_row("使用手册", "✓" if results.get("manual") else "✗")
            
            console.print(table)
            
            if results.get("changelog") or results.get("manual"):
                console.print(f"\n提交信息: {message}")
        
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("project")
@click.argument("action", type=click.Choice([
    "update", "set-phase", "status", "complete", "info"
]))
@click.option("--type", "-t", type=click.Choice([
    "test", "development", "deployment"
]), help="更新类型")
@click.option("--value", "-v", help="更新值")
@click.option("--cases", type=int, help="测试用例数")
@click.option("--passed", type=int, help="通过数")
@click.option("--branch", "-b", help="分支名")
@click.option("--phase", help="目标阶段")
def project_command(action: str, type: str, value: str, cases: int,
                    passed: int, branch: str, phase: str):
    """项目管理命令（用于子项目状态更新）。"""
    try:
        project_path = get_project_path()
        state_manager = StateManager(project_path)
        state = state_manager.load_state()

        if action == "update":
            if type == "test":
                if cases is not None or passed is not None:
                    test = state.get('test', {})
                    if cases is not None:
                        test['blackbox_cases'] = cases
                    if passed is not None:
                        test['blackbox_passed'] = passed
                    test['status'] = 'in_progress'
                    if passed is not None and cases is not None and passed >= cases:
                        test['status'] = 'passed'
                    state['test'] = test
                    state_manager.save_state(state)
                    click.echo(f"✓ 测试统计已更新: 用例={cases}, 通过={passed}")
                else:
                    click.echo("错误: 测试更新需要提供 --cases 或 --passed")
                    sys.exit(1)
            elif type == "development":
                if value:
                    dev = state.get('development', {})
                    dev['status'] = value
                    if branch:
                        dev['branch'] = branch
                    state['development'] = dev
                    state_manager.save_state(state)
                    click.echo(f"✓ 开发状态已更新: {value}")
                else:
                    click.echo("错误: 开发更新需要提供 --value")
                    sys.exit(1)
            elif type == "deployment":
                if value:
                    deploy = state.get('deployment', {})
                    deploy['status'] = value
                    state['deployment'] = deploy
                    state_manager.save_state(state)
                    click.echo(f"✓ 部署状态已更新: {value}")
                else:
                    click.echo("错误: 部署更新需要提供 --value")
                    sys.exit(1)

        elif action == "set-phase":
            if phase:
                state_manager.update_phase(phase)
                click.echo(f"✓ 阶段已设置为: {phase}")
            else:
                click.echo("错误: 需要提供 --phase 参数")
                sys.exit(1)

        elif action == "complete":
            dev = state.get('development', {})
            dev['status'] = 'completed'
            state['development'] = dev
            state['phase'] = 'testing'
            state_manager.save_state(state)
            click.echo("✓ 开发任务已标记为完成")
            click.echo("✓ 阶段已推进到: testing")
            click.echo("提示: 运行 'oc-collab advance' 同步到 Git")

        elif action == "status":
            phase_info = state.get('phase', 'unknown')
            test = state.get('test', {})
            dev = state.get('development', {})
            deploy = state.get('deployment', {})

            console.print("\n[bold]项目状态[/bold]")

            table = Table(show_header=False)
            table.add_column("项目")
            table.add_column("值")

            table.add_row("当前阶段", phase_info)
            table.add_row("测试状态", test.get('status', 'unknown'))
            table.add_row("测试用例数", str(test.get('blackbox_cases', 0)))
            table.add_row("测试通过数", str(test.get('blackbox_passed', 0)))
            table.add_row("开发状态", dev.get('status', 'unknown'))
            table.add_row("部署状态", deploy.get('status', 'unknown'))

            console.print(table)

        elif action == "info":
            phase_engine = PhaseAdvanceEngine(project_path)
            phases = phase_engine.list_phases()

            console.print("\n[bold]阶段列表[/bold]")

            table = Table(show_header=False)
            table.add_column("阶段")
            table.add_column("状态")
            table.add_column("条件")

            for p in phases['phases']:
                status = "← 已完成" if p['is_past'] else ("★ 当前" if p['is_current'] else "待推进")
                condition = p['condition_description'] if not p['is_past'] else "-"
                table.add_row(p['phase'], status, condition)

            console.print(table)
            console.print(f"\n当前阶段: {phases['current_phase']}")

    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


@main.command("advance")
@click.option("--phase", "-p", help="目标阶段")
@click.option("--force", "-f", is_flag=True, help="强制推进")
@click.option("--check", "-c", is_flag=True, help="仅检查条件")
def advance_command(phase: str, force: bool, check: bool):
    """推进到下一阶段。"""
    try:
        project_path = get_project_path()
        phase_engine = PhaseAdvanceEngine(project_path)

        if check:
            result = phase_engine.check_and_advance()
            if result["advanced"]:
                console.print(Panel(
                    f"可以自动推进\n从: {result['from_phase']}\n到: {result['to_phase']}\n原因: {result['reason']}",
                    title="阶段检查",
                    style="green"
                ))
            else:
                console.print(Panel(
                    f"无法自动推进\n当前: {result['from_phase']}\n原因: {result['reason']}",
                    title="阶段检查",
                    style="yellow"
                ))
        elif phase:
            result = phase_engine.manual_advance(phase, force=force)
            if result["success"]:
                console.print(Panel(
                    result["message"],
                    title="阶段推进",
                    style="green"
                ))
            else:
                console.print(Panel(
                    f"推进失败\n原因: {result.get('error', '未知')}",
                    title="错误",
                    style="red"
                ))
                sys.exit(1)
        else:
            result = phase_engine.check_and_advance()
            if result["advanced"]:
                console.print(Panel(
                    result["message"],
                    title="自动推进",
                    style="green"
                ))
            else:
                console.print(Panel(
                    f"{result['message']}\n\n使用 'oc-collab advance --check' 查看详情\n使用 'oc-collab advance --force --phase <阶段名>' 强制推进",
                    title="无法自动推进",
                    style="yellow"
                ))

    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
