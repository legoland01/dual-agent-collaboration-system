"""部署文档同步自动化

F-DEPLOY-002: 部署文档同步自动化
部署前自动检查并同步CHANGELOG和README
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class DeployDocSync:
    """部署文档同步器"""

    REQUIRED_DOCS = [
        "CHANGELOG.md",
        "README.md",
        "skills/*/content.md",
        "docs/00-architecture/*.md",
    ]

    def __init__(self, project_path: Optional[str] = None):
        """
        初始化部署文档同步器

        Args:
            project_path: 项目路径，默认当前目录
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.changelog_path = self.project_path / "CHANGELOG.md"
        self.readme_path = self.project_path / "README.md"
        self.pyproject_path = self.project_path / "pyproject.toml"
        self.docs_path = self.project_path / "docs"
        self.skills_path = self.project_path / "skills"

    def check_completeness(self) -> Dict:
        """
        检查文档完整性（v2.2.10增强）

        Returns:
            {"complete": bool, "missing": list, "present": list}
        """
        missing = []
        present = []

        for pattern in self.REQUIRED_DOCS:
            if pattern.endswith("/*.md"):
                base_dir = pattern.replace("/*.md", "")
                check_path = self.project_path / base_dir
                if check_path.exists():
                    md_files = list(check_path.glob("*.md"))
                    if md_files:
                        present.append(f"{base_dir}/*.md ({len(md_files)} files)")
                    else:
                        missing.append(pattern)
                else:
                    missing.append(pattern)
            else:
                doc_path = self.project_path / pattern
                if doc_path.exists():
                    present.append(pattern)
                else:
                    missing.append(pattern)

        return {
            "complete": len(missing) == 0,
            "missing": missing,
            "present": present
        }

    def check_docs_sync(self, version: str) -> Dict:
        """
        检查部署文档是否已同步

        Args:
            version: 版本号

        Returns:
            Dict: 检查结果
        """
        result = {
            "ready": True,
            "checks": [],
            "errors": [],
        }

        changelog_check = self._check_changelog(version)
        result["checks"].append(changelog_check)
        if not changelog_check["passed"]:
            result["ready"] = False

        readme_check = self._check_readme()
        result["checks"].append(readme_check)
        if not readme_check["passed"]:
            result["ready"] = False

        pyproject_check = self._check_pyproject(version)
        result["checks"].append(pyproject_check)
        if not pyproject_check["passed"]:
            result["ready"] = False

        return result

    def _check_changelog(self, version: str) -> Dict:
        """
        检查CHANGELOG.md是否包含当前版本

        Args:
            version: 版本号

        Returns:
            Dict: 检查结果
        """
        if not self.changelog_path.exists():
            return {
                "name": "CHANGELOG.md",
                "passed": False,
                "message": "文件不存在",
                "suggestion": "创建CHANGELOG.md文件",
            }

        content = self.changelog_path.read_text(encoding="utf-8")

        version_patterns = [
            f"## {version}",
            f"v{version}",
            version,
        ]

        for pattern in version_patterns:
            if pattern in content:
                return {
                    "name": "CHANGELOG.md",
                    "passed": True,
                    "message": f"版本 {version} 已记录",
                }

        return {
            "name": "CHANGELOG.md",
            "passed": False,
            "message": f"版本 {version} 未记录",
            "suggestion": f"在CHANGELOG.md中添加 {version} 的变更记录",
        }

    def _check_readme(self) -> Dict:
        """
        检查README.md是否包含新命令

        Returns:
            Dict: 检查结果
        """
        if not self.readme_path.exists():
            return {
                "name": "README.md",
                "passed": False,
                "message": "文件不存在",
                "suggestion": "创建README.md文件",
            }

        content = self.readme_path.read_text(encoding="utf-8")

        if "oc-collab" in content:
            return {
                "name": "README.md",
                "passed": True,
                "message": "CLI命令已记录",
            }

        return {
            "name": "README.md",
            "passed": False,
            "message": "CLI命令未记录",
            "suggestion": "在README.md中添加oc-collab命令说明",
        }

    def _check_pyproject(self, version: str) -> Dict:
        """
        检查pyproject.toml版本号

        Args:
            version: 版本号

        Returns:
            Dict: 检查结果
        """
        if not self.pyproject_path.exists():
            return {
                "name": "pyproject.toml",
                "passed": True,
                "message": "文件不存在，跳过检查",
            }

        content = self.pyproject_path.read_text(encoding="utf-8")

        version_patterns = [
            f'version = "{version}"',
            f"version = '{version}'",
            f"version = {version}",
        ]

        for pattern in version_patterns:
            if pattern in content:
                return {
                    "name": "pyproject.toml",
                    "passed": True,
                    "message": f"版本 {version} 已配置",
                }

        return {
            "name": "pyproject.toml",
            "passed": False,
            "message": f"版本 {version} 未配置",
            "suggestion": f"更新pyproject.toml中的版本号为 {version}",
        }

    def sync_changelog(self, version: str, changes: List[str]) -> bool:
        """
        同步CHANGELOG.md

        Args:
            version: 版本号
            changes: 变更列表

        Returns:
            bool: 是否成功
        """
        try:
            if not self.changelog_path.exists():
                self.changelog_path.write_text("# Changelog\n\n", encoding="utf-8")

            existing_content = self.changelog_path.read_text(encoding="utf-8")

            new_entry = f"## {version}\n\n"
            for change in changes:
                new_entry += f"- {change}\n"
            new_entry += "\n"

            new_content = new_entry + existing_content

            self.changelog_path.write_text(new_content, encoding="utf-8")

            logger.info(f"CHANGELOG.md已更新: 版本 {version}")

            return True

        except Exception as e:
            logger.error(f"更新CHANGELOG.md失败: {e}")
            return False

    def generate_readme_entry(self, commands: List[Dict]) -> str:
        """
        生成README.md命令条目

        Args:
            commands: 命令列表 [{"name": "命令名", "desc": "描述"}]

        Returns:
            str: Markdown格式条目
        """
        entry = "## 新增命令\n\n"
        entry += "| 命令 | 描述 |\n"
        entry += "|------|-------|\n"

        for cmd in commands:
            entry += f"| `{cmd['name']}` | {cmd['desc']} |\n"

        entry += "\n"
        return entry

    def sync_readme(self, commands: List[Dict]) -> bool:
        """
        同步README.md

        Args:
            commands: 命令列表

        Returns:
            bool: 是否成功
        """
        try:
            if not self.readme_path.exists():
                self.readme_path.write_text("# oc-collab\n\n", encoding="utf-8")

            existing_content = self.readme_path.read_text(encoding="utf-8")

            new_entry = self.generate_readme_entry(commands)

            if "## 新增命令" in existing_content:
                existing_content = re.sub(
                    r"## 新增命令\n\n\|.*\|\n(\|.*\|\n)*",
                    new_entry,
                    existing_content
                )
            else:
                existing_content += "\n" + new_entry

            self.readme_path.write_text(existing_content, encoding="utf-8")

            logger.info("README.md已更新")

            return True

        except Exception as e:
            logger.error(f"更新README.md失败: {e}")
            return False

    def check_and_sync(self, version: str, changes: List[str], commands: List[Dict]) -> Dict:
        """
        检查并同步部署文档

        Args:
            version: 版本号
            changes: 变更列表
            commands: 新增命令列表

        Returns:
            Dict: 操作结果
        """
        result = {
            "ready": True,
            "actions": [],
            "errors": [],
        }

        check_result = self.check_docs_sync(version)
        result["ready"] = check_result["ready"]

        if not check_result["ready"]:
            result["actions"].append({
                "action": "sync",
                "target": "all",
                "success": self.sync_all(version, changes, commands),
            })

        return result

    def sync_all(self, version: str, changes: List[str], commands: List[Dict]) -> bool:
        """
        同步所有部署文档

        Args:
            version: 版本号
            changes: 变更列表
            commands: 新增命令列表

        Returns:
            bool: 是否成功
        """
        changelog_success = self.sync_changelog(version, changes)
        readme_success = self.sync_readme(commands)

        return changelog_success and readme_success
