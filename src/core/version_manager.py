"""
版本号管理器

读取和更新 pyproject.toml 中的版本号
"""

import re
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class VersionError(Exception):
    """版本号异常"""
    pass


class VersionManager:
    """版本号管理器"""

    VERSION_PATTERN = r"^\d+\.\d+\.\d+$"

    def __init__(self, pyproject_path: str = "pyproject.toml"):
        """
        Args:
            pyproject_path: pyproject.toml 文件路径
        """
        self.pyproject_path = Path(pyproject_path)

    def get_current_version(self) -> str:
        """
        读取当前版本号

        Returns:
            版本号字符串

        Raises:
            VersionError: 文件不存在或版本号格式错误
        """
        if not self.pyproject_path.exists():
            raise VersionError(f"文件不存在: {self.pyproject_path}")

        content = self.pyproject_path.read_text()

        version = self._extract_version(content)
        if not version:
            raise VersionError("无法找到版本号")

        logger.info(f"当前版本号: {version}")
        return version

    def update_version(self, new_version: str) -> bool:
        """
        更新版本号

        Args:
            new_version: 新版本号，如 "2.2.12"

        Returns:
            是否更新成功

        Raises:
            VersionError: 版本号格式无效
        """
        if not self._validate_version(new_version):
            raise VersionError(f"无效版本号格式: {new_version}，请使用 x.y.z 格式")

        if not self.pyproject_path.exists():
            raise VersionError(f"文件不存在: {self.pyproject_path}")

        content = self.pyproject_path.read_text()

        updated_content = self._replace_version(content, new_version)

        self.pyproject_path.write_text(updated_content)
        logger.info(f"版本号已更新: {new_version}")
        return True

    def update_version_increment(self) -> str:
        """
        递增版本号（最后一位+1）

        Returns:
            新的版本号

        Raises:
            VersionError: 版本号格式错误
        """
        current = self.get_current_version()
        parts = current.split(".")
        if len(parts) != 3:
            raise VersionError(f"无效版本号格式: {current}")

        parts[2] = str(int(parts[2]) + 1)
        new_version = ".".join(parts)

        self.update_version(new_version)
        return new_version

    def validate_version(self, version: str) -> tuple[bool, str]:
        """
        验证版本号格式

        Args:
            version: 版本号字符串

        Returns:
            (是否有效, 错误消息)
        """
        if not version or not isinstance(version, str):
            return False, "版本号不能为空"

        if not re.match(self.VERSION_PATTERN, version):
            return False, f"版本号格式无效: {version}，请使用 x.y.z 格式"

        return True, ""

    def _validate_version(self, version: str) -> bool:
        """验证版本号格式"""
        return bool(re.match(self.VERSION_PATTERN, version))

    def _extract_version(self, content: str) -> Optional[str]:
        """从内容中提取版本号"""
        patterns = [
            r'version\s*=\s*["\'](\d+\.\d+\.\d+)["\']',
            r'^version\s*=\s*(\d+\.\d+\.\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                return match.group(1)
        return None

    def _replace_version(self, content: str, new_version: str) -> str:
        """替换版本号"""
        patterns = [
            (r'(version\s*=\s*")(\d+\.\d+\.\d+)(")', r'\g<1>' + new_version + r'\g<3>'),
            (r"(version\s*=\s*')(\d+\.\d+\.\d+)(')", r'\g<1>' + new_version + r'\g<3>'),
            (r'(^version\s*=\s*)(\d+\.\d+\.\d+)', r'\g<1>' + new_version),
        ]

        for pattern, replacement in patterns:
            content = re.sub(
                pattern,
                replacement,
                content,
                flags=re.MULTILINE
            )
        return content


if __name__ == "__main__":
    vm = VersionManager()

    print(f"当前版本: {vm.get_current_version()}")

    try:
        vm.validate_version("2.2.12")
        print("版本号验证通过")
    except VersionError as e:
        print(f"错误: {e}")
