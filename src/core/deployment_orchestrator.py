"""
部署编排器

协调部署全流程：检查 → 版本管理 → 构建 → 上传 → Git推送 → 验证 → 状态更新
"""

from typing import Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class DeploymentStep:
    """部署步骤"""
    name: str
    description: str
    execute: Callable
    status: str = "pending"
    message: str = ""
    timestamp: Optional[str] = None


@dataclass
class DeploymentResult:
    """部署结果"""
    success: bool
    version: str
    steps: list = field(default_factory=list)
    error: Optional[str] = None
    pypi_url: Optional[str] = None
    git_tag: Optional[str] = None


class DeploymentError(Exception):
    """部署异常"""
    pass


class DeploymentOrchestrator:
    """部署编排器 - 协调部署全流程"""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        """
        Args:
            dry_run: 预览模式，不执行实际变更
            verbose: 输出详细日志
        """
        self.dry_run = dry_run
        self.verbose = verbose
        self.steps: list[DeploymentStep] = []
        self.results: list[DeploymentStep] = []

    def add_step(self, name: str, description: str, execute: Callable):
        """添加部署步骤"""
        step = DeploymentStep(
            name=name,
            description=description,
            execute=execute
        )
        self.steps.append(step)

    def run(self, version: Optional[str] = None,
             skip_git: bool = False,
             skip_pypi: bool = False,
             verify_only: bool = False) -> DeploymentResult:
        """
        执行完整部署流程

        Args:
            version: 指定版本号，None则自动读取
            skip_git: 跳过Git推送步骤
            skip_pypi: 跳过PyPI上传步骤
            verify_only: 仅执行验证

        Returns:
            DeploymentResult: 部署结果
        """
        self.results = []
        result = DeploymentResult(
            success=False,
            version=version or "unknown"
        )

        if self.dry_run:
            logger.info("[DRY-RUN] 部署预览模式")
            self._dry_run_execute()
            return result

        for step in self.steps:
            if verify_only and "verify" not in step.name.lower():
                continue
            if skip_git and "git" in step.name.lower():
                continue
            if skip_pypi and "pypi" in step.name.lower():
                continue

            try:
                self._execute_step(step)
                result.steps.append({
                    "name": step.name,
                    "status": step.status,
                    "message": step.message
                })
            except Exception as e:
                step.status = "failed"
                step.message = str(e)
                result.steps.append({
                    "name": step.name,
                    "status": "failed",
                    "message": str(e)
                })
                result.error = str(e)
                logger.error(f"步骤 {step.name} 失败: {e}")
                return result

        result.success = True
        return result

    def _execute_step(self, step: DeploymentStep):
        """执行单个步骤"""
        step.status = "running"
        step.timestamp = datetime.utcnow().isoformat()

        if self.verbose:
            logger.info(f"执行步骤: {step.name} - {step.description}")

        try:
            result = step.execute()
            step.status = "passed"
            step.message = result or "执行成功"
            if self.verbose:
                logger.info(f"步骤 {step.name} 完成: {step.message}")
        except Exception as e:
            step.status = "failed"
            step.message = str(e)
            raise DeploymentError(f"{step.name} 失败: {e}")

    def _dry_run_execute(self):
        """预览模式 - 只显示不执行"""
        for step in self.steps:
            logger.info(f"[DRY-RUN] 步骤 {step.name}: {step.description}")
            self.results.append({
                "name": step.name,
                "status": "skipped",
                "message": "(预览模式，跳过执行)"
            })

    def get_step_status(self, name: str) -> Optional[DeploymentStep]:
        """获取步骤状态"""
        for step in self.steps:
            if step.name == name:
                return step
        return None


if __name__ == "__main__":
    orchestrator = DeploymentOrchestrator(dry_run=True)

    def dummy_step():
        return "模拟执行"

    orchestrator.add_step("doc_check", "检查文档同步", dummy_step)
    orchestrator.add_step("version_update", "更新版本号", dummy_step)

    result = orchestrator.run()
    print(f"结果: {result}")
