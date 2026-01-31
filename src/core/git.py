"""Git集成模块。"""
import subprocess
from pathlib import Path
from typing import List, Optional


class GitError(Exception):
    """Git操作异常基类。"""
    pass


class GitNotInstalledError(GitError):
    """Git未安装异常。"""
    pass


class GitRepositoryError(GitError):
    """Git仓库异常。"""
    pass


class GitOperationError(GitError):
    """Git操作失败异常。"""
    pass


class GitConflictError(GitError):
    """Git合并冲突异常。"""
    pass


class GitHelper:
    """Git操作助手。"""
    
    def __init__(self, project_path: str):
        """初始化Git助手。"""
        self.project_path = Path(project_path)
        self._ensure_git_installed()
    
    def _ensure_git_installed(self) -> None:
        """检查Git是否已安装。"""
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise GitNotInstalledError("Git未安装或无法访问")
    
    def _run_git_command(self, *args, check: bool = True) -> subprocess.CompletedProcess:
        """运行Git命令。"""
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            if "conflict" in error_msg.lower():
                raise GitConflictError(error_msg)
            raise GitOperationError(f"Git命令执行失败: {error_msg}")
    
    def is_repository(self) -> bool:
        """检查是否为Git仓库。"""
        try:
            self._run_git_command("rev-parse", "--is-inside-work-tree", check=False)
            return True
        except GitOperationError:
            return False
    
    def init_repository(self) -> None:
        """初始化Git仓库。"""
        if not self.is_repository():
            self._run_git_command("init")
    
    def pull(self) -> bool:
        """拉取远程变更。"""
        try:
            self._run_git_command("pull")
            return True
        except GitConflictError:
            raise
        except GitOperationError:
            return False
    
    def push(self, message: str) -> None:
        """提交并推送。"""
        self._run_git_command("add", "-A")
        self._run_git_command("commit", "-m", message)
        self._run_git_command("push")
    
    def create_branch(self, branch_name: str) -> None:
        """创建分支。"""
        self._run_git_command("checkout", "-b", branch_name)
    
    def switch_branch(self, branch_name: str) -> None:
        """切换分支。"""
        self._run_git_command("checkout", branch_name)
    
    def branch_exists(self, branch_name: str) -> bool:
        """检查分支是否存在。"""
        try:
            self._run_git_command("rev-parse", "--verify", f"refs/heads/{branch_name}", check=False)
            return True
        except GitOperationError:
            return False
    
    def create_tag(self, tag_name: str, message: str = "") -> None:
        """创建标签。"""
        if message:
            self._run_git_command("tag", "-a", tag_name, "-m", message)
        else:
            self._run_git_command("tag", tag_name)
    
    def get_current_branch(self) -> str:
        """获取当前分支名称。"""
        result = self._run_git_command("rev-parse", "--abbrev-ref", "HEAD")
        return result.stdout.strip()
    
    def get_remote_url(self) -> Optional[str]:
        """获取远程仓库URL。"""
        try:
            result = self._run_git_command("remote", "get-url", "origin", check=False)
            return result.stdout.strip() if result.stdout else None
        except GitOperationError:
            return None
    
    def has_local_changes(self) -> bool:
        """检查是否有未提交的本地修改。"""
        result = self._run_git_command("status", "--porcelain", check=False)
        return bool(result.stdout.strip())
    
    def get_commit_hash(self, branch: str = "HEAD") -> str:
        """获取提交哈希。"""
        result = self._run_git_command("rev-parse", branch)
        return result.stdout.strip()
    
    def get_commit_message(self, commit_hash: str = "HEAD") -> str:
        """获取提交信息。"""
        result = self._run_git_command("log", "-1", "--format=%s", commit_hash)
        return result.stdout.strip()
    
    def get_all_branches(self) -> List[str]:
        """获取所有本地分支。"""
        result = self._run_git_command("branch", "--list")
        return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    
    def get_all_tags(self) -> List[str]:
        """获取所有标签。"""
        result = self._run_git_command("tag", "-l")
        return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    
    def delete_branch(self, branch_name: str) -> None:
        """删除分支。"""
        self._run_git_command("branch", "-d", branch_name)
    
    def delete_tag(self, tag_name: str) -> None:
        """删除标签。"""
        self._run_git_command("tag", "-d", tag_name)
