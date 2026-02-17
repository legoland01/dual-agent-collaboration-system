import click
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.config_manager import ConfigManager


@click.group()
def config():
    """配置管理命令组"""
    pass


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """设置配置"""
    cfg = ConfigManager()
    if cfg.set(key, value):
        click.echo(f"✅ 已设置: {key} = {value}")
    else:
        click.echo(f"❌ 设置失败")
        sys.exit(1)


@config.command("get")
@click.argument("key")
def config_get(key: str):
    """获取配置"""
    cfg = ConfigManager()
    value = cfg.get(key)
    if value is not None:
        click.echo(f"{key} = {value}")
    else:
        click.echo(f"配置不存在: {key}")
        sys.exit(1)


@config.command("list")
def config_list():
    """列出所有配置"""
    cfg = ConfigManager()
    config = cfg.list()
    
    click.echo("当前配置:")
    for key, value in config.items():
        if isinstance(value, dict):
            click.echo(f"\n{key}:")
            for k, v in value.items():
                click.echo(f"  {k} = {v}")
        else:
            click.echo(f"{key} = {value}")


@config.command("delete")
@click.argument("key")
def config_delete(key: str):
    """删除配置"""
    cfg = ConfigManager()
    if cfg.delete(key):
        click.echo(f"✅ 已删除: {key}")
    else:
        click.echo(f"❌ 删除失败: {key}")
        sys.exit(1)


@config.command("reset")
def config_reset():
    """重置为默认配置"""
    cfg = ConfigManager()
    if cfg.reset():
        click.echo("✅ 配置已重置")
    else:
        click.echo("❌ 重置失败")
        sys.exit(1)


if __name__ == '__main__':
    config()
