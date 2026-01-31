"""CLI主入口模块。"""
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from ..core.state_manager import StateManager, StateFileNotFoundError
from ..core.detector import detect_project_type
from ..core.git import GitHelper, GitNotInstalledError
from ..core.workflow import WorkflowEngine
from ..core.signoff import SignoffEngine


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
        
        table.add_row("项目名称", state["project"]["name"])
        table.add_row("项目类型", state["project"]["type"])
        table.add_row("当前阶段", state["phase"])
        
        active_agent = state_manager.get_active_agent()
        table.add_row("当前Agent", f"Agent {active_agent} ({state['agents'][active_agent]['role']})")
        
        console.print(table)
        
        console.print("\n[bold]签署状态[/bold]")
        req_status = state_manager.get_signoff_status("requirements")
        console.print(f"需求签署 - 产品经理: {'✓' if req_status['pm_signoff'] else '✗'}, 开发: {'✓' if req_status['dev_signoff'] else '✗'}")
        
    except StateFileNotFoundError:
        click.echo("错误: 未找到项目状态文件，请先初始化项目")
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


@main.command("sync")
def sync_command():
    """同步远程变更。"""
    try:
        project_path = get_project_path()
        git_helper = GitHelper(project_path)
        
        if git_helper.has_local_changes():
            click.echo("警告: 有未提交的本地修改，请先提交或暂存")
            sys.exit(1)
        
        if git_helper.pull():
            click.echo("已同步远程变更")
        else:
            click.echo("同步失败")
            
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
