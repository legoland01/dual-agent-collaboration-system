"""自动Bug检测机制

F-AUTO-005: 自动Bug检测机制
关键操作后自动检测异常并触发Bug报告
"""
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class BugReport:
    bug_id: str
    bug_type: str
    description: str
    related_todo: Optional[str] = None
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    detected_by: str = "AutoBugDetector"
    status: str = "OPEN"


class BugType:
    DOCUMENT_STATUS_NOT_UPDATED = "DOCUMENT_STATUS_NOT_UPDATED"
    SIGNOFF_INCOMPLETE = "SIGNOFF_INCOMPLETE"
    MISSING_REQUIRED_FILE = "MISSING_REQUIRED_FILE"
    COMMAND_FAILED = "COMMAND_FAILED"
    TODO_ORPHANED = "TODO_ORPHANED"
    PHASE_TRANSITION_INVALID = "PHASE_TRANSITION_INVALID"


class AutoBugDetector:
    """自动Bug检测器"""

    BUG_PATTERNS = {
        BugType.DOCUMENT_STATUS_NOT_UPDATED: [
            r"TODO.*completed.*document.*not.*updated",
            r"document.*status.*not.*updated.*TODO",
        ],
        BugType.SIGNOFF_INCOMPLETE: [
            r"signoff.*incomplete",
            r"missing.*signoff",
        ],
        BugType.MISSING_REQUIRED_FILE: [
            r"required.*file.*missing",
            r"file.*not.*found.*required",
        ],
    }

    def __init__(self, state_manager=None, doc_generator=None):
        self.state_manager = state_manager
        self.doc_generator = doc_generator
        self.memos_path = Path("docs/00-memos/")

    def check_todo_completion(self, todo_id: str) -> List[BugReport]:
        """
        TODO完成时检查文档状态是否更新

        Args:
            todo_id: 已完成的TODO ID

        Returns:
            Bug报告列表
        """
        bugs = []

        if not self.state_manager:
            return bugs

        try:
            state = self.state_manager.load_state()

            if self._is_document_status_outdated(todo_id, state):
                bug = BugReport(
                    bug_id=self._generate_bug_id(),
                    bug_type=BugType.DOCUMENT_STATUS_NOT_UPDATED,
                    description=f"TODO-{todo_id}已完成，但关联文档状态未更新",
                    related_todo=todo_id,
                    detected_by="AutoBugDetector"
                )
                bugs.append(bug)
                logger.warning(f"检测到Bug: {bug.bug_id} - {bug.description}")

        except Exception as e:
            logger.error(f"检查TODO完成状态时出错: {e}")

        return bugs

    def check_signoff_completion(self, stage: str) -> List[BugReport]:
        """
        评审完成时检查签署是否完成

        Args:
            stage: 阶段名称

        Returns:
            Bug报告列表
        """
        bugs = []

        if not self.state_manager:
            return bugs

        try:
            state = self.state_manager.load_state()

            if self._is_signoff_incomplete(stage, state):
                bug = BugReport(
                    bug_id=self._generate_bug_id(),
                    bug_type=BugType.SIGNOFF_INCOMPLETE,
                    description=f"{stage}阶段签署不完整",
                    related_todo=None,
                    detected_by="AutoBugDetector"
                )
                bugs.append(bug)
                logger.warning(f"检测到Bug: {bug.bug_id} - {bug.description}")

        except Exception as e:
            logger.error(f"检查签署状态时出错: {e}")

        return bugs

    def check_command_result(self, command: str, result: Dict) -> List[BugReport]:
        """
        命令执行后检查返回值是否异常

        Args:
            command: 命令名称
            result: 命令执行结果

        Returns:
            Bug报告列表
        """
        bugs = []

        if result.get("success", True) is False or result.get("return_code", 0) != 0:
            error_msg = result.get("error", "")
            
            bug_type = BugType.COMMAND_FAILED
            description = f"命令执行失败: {command}"

            if error_msg:
                description += f" - {error_msg}"

            bug = BugReport(
                bug_id=self._generate_bug_id(),
                bug_type=bug_type,
                description=description,
                related_todo=None,
                detected_by="AutoBugDetector"
            )
            bugs.append(bug)
            logger.warning(f"检测到Bug: {bug.bug_id} - {bug.description}")

        return bugs

    def check_file_edit(self, file_path: str, edit_result: Dict) -> List[BugReport]:
        """
        文件编辑后检查格式错误

        Args:
            file_path: 文件路径
            edit_result: 编辑结果

        Returns:
            Bug报告列表
        """
        bugs = []

        if edit_result.get("format_error"):
            bug = BugReport(
                bug_id=self._generate_bug_id(),
                bug_type=BugType.MISSING_REQUIRED_FILE,
                description=f"文件格式错误: {file_path}",
                related_todo=None,
                detected_by="AutoBugDetector"
            )
            bugs.append(bug)
            logger.warning(f"检测到Bug: {bug.bug_id} - {bug.description}")

        return bugs

    def check_phase_transition(self, from_phase: str, to_phase: str, result: Dict) -> List[BugReport]:
        """
        检查阶段推进是否有效

        Args:
            from_phase: 源阶段
            to_phase: 目标阶段
            result: 推进结果

        Returns:
            Bug报告列表
        """
        bugs = []

        if not result.get("valid", True):
            bug = BugReport(
                bug_id=self._generate_bug_id(),
                bug_type=BugType.PHASE_TRANSITION_INVALID,
                description=f"阶段推进无效: {from_phase} -> {to_phase}",
                related_todo=None,
                detected_by="AutoBugDetector"
            )
            bugs.append(bug)
            logger.warning(f"检测到Bug: {bug.bug_id} - {bug.description}")

        return bugs

    def _is_document_status_outdated(self, todo_id: str, state: Dict) -> bool:
        """
        检查文档状态是否过期

        Args:
            todo_id: TODO ID
            state: 当前状态

        Returns:
            是否存在过期文档
        """
        try:
            todos = state.get("todos", [])
            for todo in todos:
                if todo.get("id") == todo_id and todo.get("status") == "completed":
                    completed_at = todo.get("updated_at") or todo.get("created_at")

                    phase = state.get("phase", "")

                    if phase == "requirements" and not state.get("requirements", {}).get("approved"):
                        return True
                    elif phase == "design" and not state.get("design", {}).get("approved"):
                        return True

        except Exception as e:
            logger.error(f"检查文档状态时出错: {e}")

        return False

    def _is_signoff_incomplete(self, stage: str, state: Dict) -> bool:
        """
        检查签署是否完整

        Args:
            stage: 阶段名称
            state: 当前状态

        Returns:
            签署是否不完整
        """
        try:
            signoffs = state.get("signoffs", {})

            if stage == "requirements":
                pm_signed = signoffs.get("requirements_pm", False)
                dev_signed = signoffs.get("requirements_dev", False)
                return not (pm_signed and dev_signed)
            elif stage == "design":
                pm_signed = signoffs.get("design_pm", False)
                dev_signed = signoffs.get("design_dev", False)
                return not (pm_signed and dev_signed)

        except Exception as e:
            logger.error(f"检查签署状态时出错: {e}")

        return False

    def _generate_bug_id(self) -> str:
        """
        生成Bug ID

        Returns:
            Bug ID字符串
        """
        date = datetime.now().strftime("%Y%m%d")

        existing_bugs = list(self.memos_path.glob(f"BUG-{date}-*.md"))
        bug_num = len(existing_bugs) + 1

        return f"BUG-{date}-{bug_num:03d}"

    def generate_bug_report(self, bug: BugReport) -> str:
        """
        生成Bug报告文件

        Args:
            bug: BugReport对象

        Returns:
            文件路径
        """
        self.memos_path.mkdir(parents=True, exist_ok=True)

        content = f"""# Bug报告: {bug.description}

**Bug编号**: {bug.bug_id}
**发现日期**: {bug.detected_at}
**发现者**: {bug.detected_by}
**状态**: {bug.status}
**类型**: {bug.bug_type}

---

## 1. Bug描述

{bug.description}

## 2. 关联信息

| 字段 | 值 |
|------|-----|
| 关联TODO | {bug.related_todo or "无"} |
| 发现时间 | {bug.detected_at} |
| 发现者 | {bug.detected_by} |

## 3. 复现步骤

1. TODO完成
2. 检查文档状态
3. 发现文档状态未更新

## 4. 影响范围

- TODO跟踪不完整
- 状态不一致

## 5. 建议修复方案

1. 更新关联文档状态
2. 运行同步命令

## 6. 后续行动

| 行动 | 执行人 | 状态 |
|------|--------|------|
| 修复Bug | Agent 2 | 待处理 |
| 验证修复 | Agent 1 | 待处理 |

---

**创建人**: {bug.detected_by}
**日期**: {bug.detected_at}
"""

        file_path = self.memos_path / f"{bug.bug_id}.md"
        file_path.write_text(content, encoding="utf-8")

        logger.info(f"Bug报告已生成: {file_path}")

        return str(file_path)

    def generate_all_bug_reports(self, bugs: List[BugReport]) -> List[str]:
        """
        批量生成Bug报告

        Args:
            bugs: Bug报告列表

        Returns:
            生成的文件路径列表
        """
        files = []

        for bug in bugs:
            file_path = self.generate_bug_report(bug)
            files.append(file_path)

        return files
