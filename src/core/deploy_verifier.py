"""
部署验证器

验证 PyPI 发布结果
"""

import subprocess
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class VerificationError(Exception):
    """验证异常"""
    pass


class DeployVerifier:
    """部署验证器"""

    def __init__(self, package_name: str = "opencode-collaboration"):
        """
        Args:
            package_name: 包名
        """
        self.package_name = package_name

    def verify_pypi(self, version: str) -> tuple[bool, dict]:
        """
        验证PyPI发布结果

        Args:
            version: 版本号

        Returns:
            (是否成功, 验证结果详情)
        """
        import requests

        url = f"https://pypi.org/pypi/{self.package_name}/{version}/json"

        try:
            logger.info(f"验证 PyPI 发布: {url}")

            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()

                info = data.get("info", {})
                result = {
                    "exists": True,
                    "version": info.get("version"),
                    "package": info.get("name"),
                    "summary": info.get("summary"),
                    "author": info.get("author"),
                    "upload_time": info.get("upload_time"),
                    "urls": [f["filename"] for f in data.get("urls", [])]
                }

                logger.info(f"PyPI 验证成功: {result['version']}")
                return True, result

            else:
                logger.warning(f"PyPI 包未找到: {response.status_code}")
                return False, {"error": f"HTTP {response.status_code}"}

        except requests.RequestException as e:
            logger.error(f"PyPI 验证失败: {e}")
            return False, {"error": str(e)}

    def pip_install_test(self, version: str) -> tuple[bool, str]:
        """
        pip安装测试

        Args:
            version: 版本号

        Returns:
            (是否成功, 消息)
        """
        package_spec = f"{self.package_name}=={version}"

        try:
            logger.info(f"测试 pip 安装: {package_spec}")

            result = subprocess.run(
                ["pip", "install", "--dry-run", package_spec],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                msg = f"pip install {package_spec} (dry-run) 成功"
                logger.info(msg)
                return True, msg

            else:
                msg = f"pip install 失败: {result.stderr}"
                logger.warning(msg)
                return False, msg

        except Exception as e:
            msg = f"pip install 测试失败: {e}"
            logger.error(msg)
            return False, msg

    def verify_complete(self, version: str) -> tuple[bool, dict]:
        """
        完整验证流程

        Args:
            version: 版本号

        Returns:
            (是否成功, 验证结果)
        """
        result = {
            "version": version,
            "pypi": {"exists": False},
            "pip_install": {"success": False}
        }

        success, pypi_result = self.verify_pypi(version)
        result["pypi"] = pypi_result

        if success:
            success, pip_msg = self.pip_install_test(version)
            result["pip_install"]["success"] = success
            result["pip_install"]["message"] = pip_msg

        all_success = success and result["pip_install"]["success"]

        return all_success, result


if __name__ == "__main__":
    verifier = DeployVerifier()

    success, result = verifier.verify_complete("2.2.11")
    print(f"验证结果: {success}")
    print(f"详情: {result}")
