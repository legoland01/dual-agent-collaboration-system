"""自动升级机制

启动时检测并升级到最新版本
"""
import subprocess
import sys
import json
import urllib.request
from packaging import version
from typing import Optional


def get_installed_version() -> str:
    """获取当前安装版本"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "opencode-collaboration"],
            capture_output=True,
            text=True
        )
        for line in result.stdout.split("\n"):
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "0.0.0"


def get_latest_version_from_pypi() -> Optional[str]:
    """从 PyPI 获取最新版本"""
    try:
        url = "https://pypi.org/pypi/opencode-collaboration/json"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            return data["info"]["version"]
    except Exception:
        return None


def should_upgrade() -> tuple[bool, str, str]:
    """
    检查是否需要升级

    Returns:
        (是否需要升级, 当前版本, 最新版本)
    """
    current = get_installed_version()
    latest = get_latest_version_from_pypi()

    if latest is None:
        return False, current, "unknown"

    try:
        if version.parse(current) < version.parse(latest):
            return True, current, latest
    except Exception:
        pass

    return False, current, latest


def check_and_upgrade():
    """
    检测版本，如需要则升级

    启动时调用此函数，会在需要时自动升级
    """
    needs_upgrade, current, latest = should_upgrade()

    if needs_upgrade:
        print(f"🔄 检测到新版本 v{latest}（当前 v{current}），正在升级...")
        print()

        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "opencode-collaboration"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ 升级成功!")
            print()
            print("请新开一个终端窗口以使用新版本")
            print(f"   当前版本: v{current} → 最新版本: v{latest}")
            sys.exit(0)
        else:
            print(f"❌ 升级失败: {result.stderr}")
            print("   可手动执行: pip install --upgrade opencode-collaboration")


def check_only() -> tuple[bool, str, str]:
    """
    仅检测版本，不升级

    Returns:
        (是否需要升级, 当前版本, 最新版本)
    """
    return should_upgrade()


if __name__ == "__main__":
    check_and_upgrade()
