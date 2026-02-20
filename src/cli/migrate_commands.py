import click
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.todo_storage import TodoStorage
from src.core.data_migration import DataMigrationService


@click.group()
def migrate():
    """YAML到SQLite迁移命令组"""
    pass


@migrate.command()
@click.option('--force', is_flag=True, help='强制执行，不确认')
def to_sqlite(force):
    """将YAML数据迁移到SQLite（仅用于旧项目迁移）"""
    click.echo("开始迁移...")
    
    storage = TodoStorage()
    migration = DataMigrationService(storage)
    
    # 旧项目迁移专用路径
    yaml_path = "state/agent_adhoc_todos.yaml"
    
    if not os.path.exists(yaml_path):
        click.echo(f"✅ YAML文件不存在，无需迁移: {yaml_path}")
        return
    
    if not force:
        click.confirm(f"确认将 {yaml_path} 迁移到 SQLite？", abort=True)
    
    ok, msg = migration.migrate(yaml_path)
    
    if ok:
        click.echo(f"✅ {msg}")
    else:
        click.echo(f"❌ 迁移失败: {msg}")
        sys.exit(1)


@migrate.command()
def preview():
    """预览迁移结果，不执行（仅用于旧项目）"""
    click.echo("预览迁移...")
    
    storage = TodoStorage()
    migration = DataMigrationService(storage)
    
    yaml_path = "state/agent_adhoc_todos.yaml"
    result = migration.preview(yaml_path)
    
    if "error" in result:
        click.echo(f"❌ {result['error']}")
        return
    
    click.echo(f"共 {result['total']} 条TODO将迁移")
    click.echo("\n预览前10条:")
    
    for i, todo in enumerate(result.get('todos', []), 1):
        click.echo(f"  {i}. [{todo.get('id')}] {todo.get('content')[:40]}")
        click.echo(f"     sender={todo.get('sender')}, receiver={todo.get('receiver')}")


@migrate.command()
@click.option('--backup', required=True, help='备份文件路径')
def rollback(backup):
    """回滚迁移"""
    click.echo("回滚迁移...")
    
    storage = TodoStorage()
    migration = DataMigrationService(storage)
    
    if migration.rollback(backup):
        click.echo("✅ 回滚完成")
    else:
        click.echo("❌ 回滚失败")
        sys.exit(1)


@migrate.command()
def list_backups():
    """列出可用备份"""
    click.echo("可用备份:")
    
    storage = TodoStorage()
    migration = DataMigrationService(storage)
    
    backups = migration.list_backups()
    
    if not backups:
        click.echo("  无备份文件")
        return
    
    for b in backups:
        click.echo(f"  - {b}")


@migrate.command()
def status():
    """查看迁移状态"""
    yaml_path = "state/agent_adhoc_todos.yaml"
    db_path = "state/todos.db"
    
    yaml_exists = os.path.exists(yaml_path)
    db_exists = os.path.exists(db_path)
    
    click.echo("迁移状态:")
    click.echo(f"  YAML文件: {'存在' if yaml_exists else '不存在'}")
    click.echo(f"  SQLite数据库: {'存在' if db_exists else '不存在'}")
    
    if db_exists:
        storage = TodoStorage()
        todos = storage.list()
        click.echo(f"  数据库中TODO数量: {len(todos)}")


if __name__ == '__main__':
    migrate()
