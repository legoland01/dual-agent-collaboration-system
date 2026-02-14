"""
PyPI上传器

上传包到 PyPI
"""

import subprocess
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class UploadError(Exception):
    """上传异常"""
    pass


class PyPIUploader:
    """PyPI上传器"""

    def __init__(self, dist_dir: str = "dist"):
        """
        Args:
            dist_dir: 构建产物目录
        """
        self.dist_dir = Path(dist_dir)

    def upload(self, dry_run: bool = False) -> tuple[bool, str]:
        """
        上传到PyPI

        Args:
            dry_run: 预览模式

        Returns:
            (是否成功, 消息)
        """
        if dry_run:
            logger.info("[DRY-RUN] 跳过 PyPI 上传")
            return True, "(预览模式，跳过上传)"

        artifacts = list(self.dist_dir.glob("*"))
        if not artifacts:
            raise UploadError("构建产物目录为空，请先执行构建")

        try:
            logger.info(f"开始上传 {len(artifacts)} 个文件到 PyPI...")

            result = subprocess.run(
                ["twine", "upload", str(self.dist_dir / "*")],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                error_msg = result.stderr or "未知错误"
                if "File already exists" in error_msg:
                    raise UploadError(f"包已存在，请使用新版本号: {error_msg}")
                raise UploadError(f"上传失败: {error_msg}")

            logger.info("上传成功")
            return True, f"成功上传 {len(artifacts)} 个文件"

        except FileNotFoundError:
            raise UploadError("twine 命令未找到，请确保已安装 twine: pip install twine")

    def check_package_exists(self, package_name: str, version: str) -> tuple[bool, str]:
        """
        检查包是否已存在

        Args:
            package_name: 包名
            version: 版本号

        Returns:
            (是否存在, 消息)
        """
        import requests

        url = f"https://pypi.org/pypi/{package_name}/{version}/json"

        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                return True, f"包 {package_name}={version} 已存在"

            return False, f"包 {package_name}={version} 不存在"

        except requests.RequestException as e:
            return False, f"检查失败: {e}"

    def get_package_info(self, package_name: str, version: str = None) -> Optional[dict]:
        """
        获取包信息

        Args:
            package_name: 包名
            version: 版本号，None获取最新版本

        Returns:
            包信息字典
        """
        import requests

        version_path = f"/{version}" if version else ""
        url = f"https://pypi.org/pypi/{package_name}{version_path}/json"

        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()

            return None

        except requests.RequestException as e:
            logger.error(f"获取包信息失败: {e}")
            return None


if __name__ == "__main__":
    uploader = PyPIUploader()

    try:
        success, msg = uploader.upload(dry_run=True)
        print(f"预览结果: {success}, {msg}")

        exists, msg = uploader.check_package_exists("opencode-collaboration", "2.2.11")
        print(f"检查结果: {exists}, {msg}")

    except UploadError as e:
        print(f"错误: {e}")
