"""Git 同步集成器 - v2.2.2 F-GIT-001"""
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import logging

logger = logging.getLogger(__name__)


class SyncResult:
    """同步结果"""

    def __init__(
        self,
        success: bool,
        message: str,
        details: Dict = None,
    ):
        self.success = success
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "details": self.details,
        }


class GitSyncIntegrator:
    """Git 同步集成器 - 集成已有的 auto_git_sync.py"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)

    def _run_git_command(self, command: List[str]) -> tuple[bool, str]:
        """运行 Git 命令"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self.project_path,
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    def detect_changes(self) -> List[str]:
        """检测变更文件"""
        success, output = self._run_git_command(
            ["git", "status", "--porcelain"]
        )
        if not success:
            return []

        lines = output.strip().split("\n")
        return [line[3:] for line in lines if line]

    def auto_add(self) -> SyncResult:
        """自动 git add"""
        changes = self.detect_changes()
        if not changes:
            return SyncResult(
                success=True,
                message="无变更",
                details={"added": []},
            )

        for f in changes:
            success, output = self._run_git_command(["git", "add", f])
            if not success:
                return SyncResult(
                    success=False,
                    message=f"git add 失败: {output}",
                    details={"file": f},
                )

        return SyncResult(
            success=True,
            message=f"已添加 {len(changes)} 个文件",
            details={"added": changes},
        )

    def auto_commit(self, message: str = "自动同步变更") -> SyncResult:
        """自动 commit"""
        success, output = self._run_git_command(
            ["git", "commit", "-m", message]
        )

        if not success:
            if "nothing to commit" in output.lower():
                return SyncResult(
                    success=True,
                    message="无需提交（无变更）",
                    details={},
                )
            return SyncResult(
                success=False,
                message=f"git commit 失败: {output}",
                details={},
            )

        return SyncResult(
            success=True,
            message="提交成功",
            details={},
        )

    def auto_push(self) -> SyncResult:
        """自动 push"""
        success, output = self._run_git_command(["git", "push"])

        if not success:
            if "everything up-to-date" in output.lower():
                return SyncResult(
                    success=True,
                    message="已是最新，无需推送",
                    details={},
                )
            return SyncResult(
                success=False,
                message=f"git push 失败: {output}",
                details={},
            )

        return SyncResult(
            success=True,
            message="推送成功",
            details={},
        )

    def sync_all(self) -> SyncResult:
        """完整同步 (add + commit + push)"""
        add_result = self.auto_add()
        if not add_result.success and "无变更" not in add_result.message:
            return SyncResult(
                success=False,
                message=f"同步失败: {add_result.message}",
                details={"step": "add", "error": add_result.message},
            )

        commit_result = self.auto_commit()
        if not commit_result.success:
            return SyncResult(
                success=False,
                message=f"同步失败: {commit_result.message}",
                details={"step": "commit", "error": commit_result.message},
            )

        push_result = self.auto_push()
        if not push_result.success:
            return SyncResult(
                success=False,
                message=f"同步失败: {push_result.message}",
                details={"step": "push", "error": push_result.message},
            )

        return SyncResult(
            success=True,
            message="✅ Git 同步完成",
            details={
                "add": add_result.message,
                "commit": commit_result.message,
                "push": push_result.message,
            },
        )

    def sync_state(self) -> SyncResult:
        """同步状态文件 (add + commit)"""
        add_result = self.auto_add()
        if not add_result.success and "无变更" not in add_result.message:
            return SyncResult(
                success=False,
                message=f"同步失败: {add_result.message}",
                details={"step": "add", "error": add_result.message},
            )

        commit_result = self.auto_commit("[oc-collab] 状态更新")
        if not commit_result.success:
            return SyncResult(
                success=False,
                message=f"同步失败: {commit_result.message}",
                details={"step": "commit", "error": commit_result.message},
            )

        return SyncResult(
            success=True,
            message="✅ 状态已同步",
            details={
                "add": add_result.message,
                "commit": commit_result.message,
            },
        )

    def check_unsynced(self) -> List[str]:
        """检查未同步的文件"""
        return self.detect_changes()

    def warn_unsynced(self) -> str:
        """生成未同步警告消息"""
        unsynced = self.check_unsynced()
        if not unsynced:
            return ""

        warning = "⚠️  警告: 您有未同步的修改。\n"
        for f in unsynced:
            warning += f"  - {f}\n"
        warning += "\n建议: 执行 oc-collab git sync 同步"

        return warning

    def get_sync_status(self) -> Dict[str, str]:
        """获取同步状态"""
        unsynced = self.check_unsynced()
        return {
            "status": "unsynced" if unsynced else "synced",
            "unsynced_count": len(unsynced),
            "files": ", ".join(unsynced) if unsynced else "",
        }
