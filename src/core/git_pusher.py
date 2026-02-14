"""
Git推送器

执行 git add, commit, tag, push
"""

import subprocess
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class GitError(Exception):
    """Git异常"""
    pass


class GitPusher:
    """Git推送器"""

    def __init__(self, project_dir: str = "."):
        """
        Args:
            project_dir: 项目目录
        """
        self.project_dir = Path(project_dir)

    def _run_git(self, *args) -> tuple[bool, str]:
        """
        执行 git 命令

        Args:
            *args: git 命令参数

        Returns:
            (是否成功, 输出信息)
        """
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return False, result.stderr.strip()

            return True, result.stdout.strip()

        except FileNotFoundError:
            raise GitError("git 命令未找到")

    def commit_and_push(self, version: str, files: list = None, dry_run: bool = False) -> tuple[bool, str]:
        """
        执行 git add, commit, push

        Args:
            version: 版本号
            files: 要提交的文件列表
            dry_run: 预览模式

        Returns:
            (是否成功, 消息)
        """
        if dry_run:
            return True, f"(预览模式) 会提交 {files or ['变更文件']}"

        files = files or ["."]

        for f in files:
            success, msg = self._run_git("add", f)
            if not success:
                raise GitError(f"git add {f} 失败: {msg}")

        commit_msg = f"release: v{version}"

        success, msg = self._run_git("commit", "-m", commit_msg)
        if not success:
            if "nothing to commit" in msg.lower():
                return True, "没有需要提交的变更"
            raise GitError(f"git commit 失败: {msg}")

        success, msg = self._run_git("push")
        if not success:
            raise GitError(f"git push 失败: {msg}")

        return True, f"已提交并推送: {commit_msg}"

    def create_tag(self, version: str, message: str = None, dry_run: bool = False) -> tuple[bool, str]:
        """
        创建版本标签

        Args:
            version: 版本号
            message: 标签消息
            dry_run: 预览模式

        Returns:
            (是否成功, 消息)
        """
        tag_name = f"v{version}"
        tag_message = message or f"Release v{version}"

        if dry_run:
            return True, f"(预览模式) 会创建标签: {tag_name}"

        success, msg = self._run_git("tag", "-a", tag_name, "-m", tag_message)
        if not success:
            if "already exists" in msg.lower():
                return False, f"标签 {tag_name} 已存在"
            raise GitError(f"创建标签失败: {msg}")

        success, msg = self._run_git("push", "origin", tag_name)
        if not success:
            return False, f"推送标签失败: {msg}"

        return True, f"已创建并推送标签: {tag_name}"

    def push_tag(self, version: str, dry_run: bool = False) -> tuple[bool, str]:
        """
        推送版本标签

        Args:
            version: 版本号
            dry_run: 预览模式

        Returns:
            (是否成功, 消息)
        """
        tag_name = f"v{version}"

        if dry_run:
            return True, f"(预览模式) 会推送标签: {tag_name}"

        success, msg = self._run_git("push", "origin", tag_name)
        if not success:
            raise GitError(f"推送标签失败: {msg}")

        return True, f"已推送标签: {tag_name}"

    def get_remote_url(self) -> Optional[str]:
        """
        获取远程仓库URL

        Returns:
            远程仓库URL
        """
        success, msg = self._run_git("remote", "get-url", "origin")
        if success:
            return msg
        return None

    def check_remote_access(self) -> tuple[bool, str]:
        """
        检查远程仓库访问权限

        Returns:
            (是否有权限, 消息)
        """
        remote_url = self.get_remote_url()
        if not remote_url:
            return False, "未找到远程仓库 origin"

        success, msg = self._run_git("ls-remote", "origin")
        if not success:
            return False, f"无法访问远程仓库: {msg}"

        return True, f"远程仓库可访问: {remote_url}"


if __name__ == "__main__":
    pusher = GitPusher()

    try:
        success, msg = pusher.check_remote_access()
        print(f"远程检查: {success}, {msg}")

        success, msg = pusher.create_tag("2.2.12", dry_run=True)
        print(f"创建标签预览: {success}, {msg}")

    except GitError as e:
        print(f"错误: {e}")
