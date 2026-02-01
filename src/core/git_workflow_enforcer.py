"""Git 工作流强制约束模块。

功能：
1. 验证 Agent 通过 Git pull 获取最新文件
2. 强制执行 Git 操作
3. 检测工作流违规
"""
import subprocess
import logging
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import os


logger = logging.getLogger(__name__)


@dataclass
class WorkflowViolation:
    """工作流违规。"""
    agent_id: str
    action: str
    reason: str
    suggestion: str
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "agent_id": self.agent_id,
            "action": self.action,
            "reason": self.reason,
            "suggestion": self.suggestion
        }


class GitWorkflowEnforcer:
    """Git 工作流强制执行器。"""
    
    REQUIRED_GIT_OPERATIONS = [
        "READ_REQUIREMENTS",
        "READ_DESIGN",
        "READ_TEST_REPORT",
        "READ_SIGNOFF",
        "READ_CODE",
    ]
    
    def __init__(self, project_path: str = "."):
        """初始化。
        
        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)
    
    def is_git_repository(self) -> bool:
        """检查是否为 Git 仓库。"""
        return (self.project_path / ".git").exists()
    
    def get_git_root(self) -> Optional[Path]:
        """获取 Git 根目录。"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None
    
    def verify_git_pull(self, agent_id: str, file_path: str) -> Tuple[bool, Optional[WorkflowViolation]]:
        """验证 Agent 是否通过 Git pull 获取最新文件。
        
        Args:
            agent_id: Agent ID
            file_path: 要读取的文件路径
            
        Returns:
            (是否通过, 违规信息)
        """
        abs_path = self.project_path / file_path
        
        if not abs_path.exists():
            return True, None
        
        local_content = self._read_local_file(str(abs_path))
        
        git_content = self._git_show(f"HEAD:{file_path}")
        
        if git_content is None:
            logger.warning(f"文件不在 Git 中: {file_path}")
            return True, None
        
        if local_content != git_content:
            return False, WorkflowViolation(
                agent_id=agent_id,
                action="READ_FILE",
                reason=f"本地文件与 Git HEAD 不一致",
                suggestion="请先执行 'git pull' 获取最新版本"
            )
        
        return True, None
    
    def verify_git_status(self, agent_id: str) -> Tuple[bool, Optional[WorkflowViolation]]:
        """验证工作区是否干净。
        
        Args:
            agent_id: Agent ID
            
        Returns:
            (是否干净, 违规信息)
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.stdout.strip():
                return False, WorkflowViolation(
                    agent_id=agent_id,
                    action="GIT_STATUS",
                    reason="工作区有未提交的更改",
                    suggestion="请先提交或暂存更改"
                )
            
            return True, None
        
        except subprocess.TimeoutExpired:
            return False, WorkflowViolation(
                agent_id=agent_id,
                action="GIT_STATUS",
                reason="Git 命令超时",
                suggestion="检查网络连接和 Git 配置"
            )
    
    def enforce_git_operation(self, agent_id: str, operation: str) -> Tuple[bool, Optional[WorkflowViolation]]:
        """强制执行 Git 操作。
        
        Args:
            agent_id: Agent ID
            operation: 操作类型
            
        Returns:
            (是否通过, 违规信息)
        """
        if operation in self.REQUIRED_GIT_OPERATIONS:
            success, error = self._run_git_pull()
            if not success:
                return False, WorkflowViolation(
                    agent_id=agent_id,
                    action=operation,
                    reason="Git pull 失败",
                    suggestion=str(error) if error else "请检查 Git 配置"
                )
        
        return True, None
    
    def check_file_in_git(self, file_path: str) -> bool:
        """检查文件是否在 Git 版本控制中。"""
        try:
            result = subprocess.run(
                ["git", "ls-files", "--error-unmatch", file_path],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_file_version(self, file_path: str) -> Optional[str]:
        """获取文件的 Git HEAD 版本哈希。"""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H", "--", file_path],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None
    
    def get_commit_info(self, commit_hash: str = "HEAD") -> Dict[str, Any]:
        """获取提交信息。"""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H%n%an%n%ae%n%ad%n%s", "--date=iso",
                 commit_hash],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                return {
                    "hash": lines[0] if len(lines) > 0 else "",
                    "author": lines[1] if len(lines) > 1 else "",
                    "email": lines[2] if len(lines) > 2 else "",
                    "date": lines[3] if len(lines) > 3 else "",
                    "message": '\n'.join(lines[4:]) if len(lines) > 4 else ""
                }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return {}
    
    def _run_git_pull(self) -> Tuple[bool, Optional[Exception]]:
        """执行 git pull。"""
        try:
            result = subprocess.run(
                ["git", "pull", "--ff-only"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Git pull 成功: {result.stdout}")
                return True, None
            else:
                logger.error(f"Git pull 失败: {result.stderr}")
                return False, Exception(result.stderr)
        
        except subprocess.TimeoutExpired:
            error = Exception("Git pull 超时")
            logger.error(str(error))
            return False, error
    
    def _read_local_file(self, file_path: str) -> str:
        """读取本地文件内容。"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (IOError, UnicodeDecodeError) as e:
            logger.warning(f"读取文件失败: {file_path}, {e}")
            return ""
    
    def _git_show(self, file_path: str) -> Optional[str]:
        """从 Git 获取文件内容。"""
        try:
            result = subprocess.run(
                ["git", "show", file_path],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.debug(f"Git show 失败: {result.stderr}")
                return None
        
        except subprocess.TimeoutExpired:
            logger.warning(f"Git show 超时: {file_path}")
            return None


class GitConfigChecker:
    """Git 配置检查器。"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
    
    def check_git_installed(self) -> bool:
        """检查 Git 是否安装。"""
        try:
            subprocess.run(
                ["git", "--version"],
                capture_output=True,
                timeout=5
            )
            return True
        except FileNotFoundError:
            return False
    
    def check_git_configured(self) -> Tuple[bool, str]:
        """检查 Git 是否已配置。"""
        try:
            result = subprocess.run(
                ["git", "config", "--global", "--list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "user.name" in result.stdout and "user.email" in result.stdout:
                return True, "Git 已配置用户信息"
            else:
                return False, "Git 未配置用户信息 (user.name/user.email)"
        except FileNotFoundError:
            return False, "Git 未安装"
    
    def check_remote_configured(self) -> Tuple[bool, str]:
        """检查远程仓库是否配置。"""
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout.strip():
                return True, f"远程仓库已配置: {result.stdout.strip()}"
            else:
                return False, "未配置远程仓库"
        except subprocess.TimeoutExpired:
            return False, "Git 命令超时"
    
    def get_full_status(self) -> Dict[str, Any]:
        """获取完整的 Git 状态。"""
        enforcer = GitWorkflowEnforcer(str(self.project_path))
        
        return {
            "git_installed": self.check_git_installed(),
            "git_configured": self.check_git_configured()[0],
            "is_repository": enforcer.is_git_repository(),
            "remote_configured": self.check_remote_configured()[0],
            "git_root": str(enforcer.get_git_root()) if enforcer.get_git_root() else None
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    checker = GitConfigChecker(".")
    print("Git 配置检查:")
    status = checker.get_full_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\nGit 工作流强制执行:")
    enforcer = GitWorkflowEnforcer(".")
    is_clean, violation = enforcer.verify_git_status("test_agent")
    print(f"  工作区干净: {is_clean}")
    if violation:
        print(f"  违规: {violation.reason}")
