"""升级命令 - 自升级到最新版本"""
import subprocess
import sys
import click


@click.command(name="upgrade")
def upgrade_command():
    """
    升级 oc-collab 到最新版本。

    示例:
      oc-collab upgrade
    """
    click.echo("🔄 正在检查新版本...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "opencode-collaboration"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            click.echo("✅ 升级成功!")
            click.echo("请重启终端以使用新版本。")
        else:
            click.echo(f"❌ 升级失败: {result.stderr}")

    except Exception as e:
        click.echo(f"❌ 升级失败: {e}")
