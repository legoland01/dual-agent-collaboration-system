"""
包构建器

执行 python -m build
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BuildError(Exception):
    """构建异常"""
    pass


class PackageBuilder:
    """包构建器"""

    def __init__(self, dist_dir: str = "dist", build_dir: str = "build", egg_info_dir: str = None):
        """
        Args:
            dist_dir: 构建产物目录
            build_dir: 构建临时目录
            egg_info_dir: egg-info目录
        """
        self.dist_dir = Path(dist_dir)
        self.build_dir = Path(build_dir)
        self.egg_info_dir = Path(egg_info_dir) if egg_info_dir else Path("*.egg-info")

    def clean(self) -> bool:
        """
        清理旧的构建产物

        Returns:
            是否清理成功
        """
        try:
            removed = []

            if self.dist_dir.exists():
                shutil.rmtree(self.dist_dir)
                removed.append(str(self.dist_dir))

            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
                removed.append(str(self.build_dir))

            for egg_info in Path(".").glob("*.egg-info"):
                shutil.rmtree(egg_info)
                removed.append(str(egg_info))

            logger.info(f"清理完成: {', '.join(removed)}")
            return True

        except Exception as e:
            logger.error(f"清理失败: {e}")
            raise BuildError(f"清理构建目录失败: {e}")

    def build(self) -> bool:
        """
        执行构建

        Returns:
            是否构建成功

        Raises:
            BuildError: 构建失败
        """
        try:
            logger.info("开始构建包...")

            result = subprocess.run(
                ["python", "-m", "build"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"构建失败: {result.stderr}")
                raise BuildError(f"构建失败: {result.stderr}")

            logger.info("构建成功")
            return True

        except FileNotFoundError:
            raise BuildError("python -m build 命令未找到，请确保已安装 build 包")

    def verify_build(self) -> tuple[bool, list[str]]:
        """
        验证构建产物

        Returns:
            (是否成功, 构建产物列表)
        """
        artifacts = []

        if not self.dist_dir.exists():
            return False, artifacts

        for artifact in self.dist_dir.iterdir():
            if artifact.is_file():
                artifacts.append(artifact.name)

        logger.info(f"构建产物: {artifacts}")

        wheel_exists = any(f.endswith(".whl") for f in artifacts)
        tarball_exists = any(f.endswith(".tar.gz") for f in artifacts)

        if wheel_exists and tarball_exists:
            return True, artifacts

        return False, artifacts


if __name__ == "__main__":
    builder = PackageBuilder()

    try:
        builder.clean()
        print("清理完成")

        builder.build()
        print("构建完成")

        success, artifacts = builder.verify_build()
        print(f"验证结果: {success}, 产物: {artifacts}")

    except BuildError as e:
        print(f"错误: {e}")
