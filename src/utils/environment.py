"""环境检测工具模块。"""
import sys
import shutil
from typing import Optional


class EnvironmentError(Exception):
    """环境异常基类。"""
    pass


class PythonNotFoundError(EnvironmentError):
    """Python 解释器未找到异常。"""
    pass


def get_python_command() -> str:
    """检测并返回可用的 Python 命令。

    Returns:
        可用的 Python 命令（优先使用 python3）

    Raises:
        PythonNotFoundError: 未找到 Python 解释器
    """
    if shutil.which("python3"):
        return "python3"
    elif shutil.which("python"):
        return "python"
    else:
        raise PythonNotFoundError("未找到 Python 解释器（python 或 python3）")


def get_python_executable() -> str:
    """返回当前使用的 Python 解释器路径。

    Returns:
        Python 解释器的绝对路径
    """
    return sys.executable


def is_test_environment() -> bool:
    """检测是否在测试环境中运行。

    Returns:
        如果在测试环境中返回 True，否则返回 False
    """
    return "pytest" in sys.modules or "test" in sys.argv[0].lower()


def get_environment_info() -> dict:
    """获取当前环境信息。

    Returns:
        包含环境信息的字典
    """
    return {
        "python_command": get_python_command(),
        "python_executable": get_python_executable(),
        "is_test_environment": is_test_environment(),
        "python_version": sys.version,
        "platform": sys.platform
    }
