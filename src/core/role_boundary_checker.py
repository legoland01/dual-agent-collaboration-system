"""角色边界检查器 - v2.2.2 F-PROC-001.1"""
from pathlib import Path
from typing import Dict, List, Optional
import re

from .compliance_engine import ComplianceEngine, ComplianceResult, ComplianceResultType
from .file_owner import FileOwnerManager


class RoleBoundaryChecker:
    """角色边界检查器"""

    # 角色权限配置
    ROLE_PERMISSIONS = {
        "agent1": {
            "allowed_dirs": [
                "docs/01-requirements/",
                "docs/03-test/",
                "docs/04-deployment/",
                "docs/06-proposals/",
                "docs/00-architecture/",
                "docs/00-retrospective/",
                "docs/00-memos/",
                "docs/00-tracking/",
            ],
            "denied_dirs": [
                "docs/02-design/",
                "src/",
                "tests/",
            ],
            "denied_actions": [
                "signoff_own_doc",
            ],
            "allowed_actions": [
                "create",
                "edit",
                "view",
                "submit_review",
            ],
        },
        "agent2": {
            "allowed_dirs": [
                "docs/02-design/",
                "src/",
                "tests/",
                "docs/02-design/",
            ],
            "denied_dirs": [
                "docs/01-requirements/",
            ],
            "allowed_actions": [
                "create",
                "edit",
                "view",
                "review",
                "signoff",
            ],
            "denied_actions": [
                "signoff_own_doc",
            ],
        },
    }

    ERROR_MESSAGES = {
        "agent1_denied_design": (
            "⛔ 权限拒绝: Agent1 无法操作设计文档。"
            "你的角色权限: 产品经理 (需求定义、评审发起、验收确认)"
            "如需创建设计文档，请由 Agent2 执行。"
        ),
        "agent1_denied_code": (
            "⛔ 权限拒绝: Agent1 无法操作代码文件。"
            "你的角色权限: 产品经理"
            "如需修改代码，请由 Agent2 执行。"
        ),
        "agent2_denied_requirements": (
            "⛔ 权限拒绝: Agent2 无法修改需求文档。"
            "你的角色权限: 开发 (评审，设计、实现、签署)"
            "如需修改需求，请由 Agent1 执行。"
        ),
        "agent2_signoff_own_doc": (
            "⛔ 权限拒绝: Agent2 无法签署自己创建的需求文档。"
            "理由: 避免利益冲突"
        ),
        "action_denied": (
            "⛔ 权限拒绝: {agent_id} 无法执行 '{action}' 操作。"
        ),
    }

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.permissions = self.ROLE_PERMISSIONS
        self.file_owner_manager = FileOwnerManager(str(self.project_path))

    def check(
        self, agent_id: str, action: str, target: str
    ) -> ComplianceResult:
        """
        检查角色边界

        Args:
            agent_id: Agent ID (agent1/agent2)
            action: 操作类型 (create/edit/delete/signoff)
            target: 目标路径

        Returns:
            ComplianceResult: 检查结果
        """
        if agent_id not in self.permissions:
            return ComplianceResult(
                check_type="role_boundary",
                result_type=ComplianceResultType.WARNING,
                agent_id=agent_id,
                action=action,
                target=target,
                message=f"⚠️ 未知 Agent ID: {agent_id}",
            )

        permissions = self.permissions[agent_id]

        # 检查是否是被拒绝的操作
        denied_actions = permissions.get("denied_actions", [])
        if action in denied_actions:
            if action == "signoff_own_doc":
                return ComplianceResult(
                    check_type="role_boundary",
                    result_type=ComplianceResultType.DENIED,
                    agent_id=agent_id,
                    action=action,
                    target=target,
                    message=self.ERROR_MESSAGES.get(
                        f"{agent_id}_signoff_own_doc",
                        self.ERROR_MESSAGES["action_denied"].format(
                            agent_id=agent_id, action=action
                        ),
                    ),
                )

        # 检查目录权限
        denied_dirs = permissions.get("denied_dirs", [])
        for denied_dir in denied_dirs:
            if self._path_matches(target, denied_dir):
                # 首先检查文件Owner
                owner = self.file_owner_manager.get_file_owner(target)
                if owner and owner != agent_id:
                    return ComplianceResult(
                        check_type="role_boundary",
                        result_type=ComplianceResultType.DENIED,
                        agent_id=agent_id,
                        action=action,
                        target=target,
                        message=f"⛔ 权限拒绝: 文件Owner是 {owner}，{agent_id} 无权修改",
                    )
                
                # Owner为空或匹配，返回原来的错误消息
                if "design" in denied_dir:
                    return ComplianceResult(
                        check_type="role_boundary",
                        result_type=ComplianceResultType.DENIED,
                        agent_id=agent_id,
                        action=action,
                        target=target,
                        message=self.ERROR_MESSAGES.get(
                            f"{agent_id}_denied_design",
                            self.ERROR_MESSAGES["action_denied"].format(
                                agent_id=agent_id, action=action
                            ),
                        ),
                    )
                elif "src" in denied_dir:
                    return ComplianceResult(
                        check_type="role_boundary",
                        result_type=ComplianceResultType.DENIED,
                        agent_id=agent_id,
                        action=action,
                        target=target,
                        message=self.ERROR_MESSAGES.get(
                            f"{agent_id}_denied_src",
                            self.ERROR_MESSAGES["action_denied"].format(
                                agent_id=agent_id, action=action
                            ),
                        ),
                    )
                elif "requirements" in denied_dir:
                    return ComplianceResult(
                        check_type="role_boundary",
                        result_type=ComplianceResultType.DENIED,
                        agent_id=agent_id,
                        action=action,
                        target=target,
                        message=self.ERROR_MESSAGES.get(
                            f"{agent_id}_denied_requirements",
                            self.ERROR_MESSAGES["action_denied"].format(
                                agent_id=agent_id, action=action
                            ),
                        ),
                    )
                else:
                    return ComplianceResult(
                        check_type="role_boundary",
                        result_type=ComplianceResultType.DENIED,
                        agent_id=agent_id,
                        action=action,
                        target=target,
                        message=self.ERROR_MESSAGES["action_denied"].format(
                            agent_id=agent_id, action=action
                        ),
                    )

        # 检查操作是否被允许
        allowed_actions = permissions.get("allowed_actions", [])
        if action not in allowed_actions and action not in denied_actions:
            return ComplianceResult(
                check_type="role_boundary",
                result_type=ComplianceResultType.DENIED,
                agent_id=agent_id,
                action=action,
                target=target,
                message=self.ERROR_MESSAGES["action_denied"].format(
                    agent_id=agent_id, action=action
                ),
            )

        # 通过所有检查
        return ComplianceResult(
            check_type="role_boundary",
            result_type=ComplianceResultType.PASSED,
            agent_id=agent_id,
            action=action,
            target=target,
            message="✅ 角色边界检查通过",
        )

    def _path_matches(self, target: str, pattern: str) -> bool:
        """检查目标路径是否匹配模式"""
        target = target.lstrip("./")
        pattern = pattern.rstrip("/")

        target_parts = target.split("/")
        pattern_parts = pattern.split("/")

        if len(pattern_parts) > len(target_parts):
            return False

        for i, pattern_part in enumerate(pattern_parts):
            if "*" in pattern_part:
                regex = "^" + pattern_part.replace("*", ".*") + "$"
                if not re.match(regex, target_parts[i]):
                    return False
            else:
                if target_parts[i] != pattern_part:
                    return False

        return True

    def is_denied_dir(self, agent_id: str, path: str) -> bool:
        """检查路径是否被拒绝"""
        if agent_id not in self.permissions:
            return False

        denied_dirs = self.permissions[agent_id].get("denied_dirs", [])
        for denied_dir in denied_dirs:
            if self._path_matches(path, denied_dir):
                return True
        return False

    def is_allowed_action(self, agent_id: str, action: str) -> bool:
        """检查操作是否被允许"""
        if agent_id not in self.permissions:
            return False

        allowed_actions = self.permissions[agent_id].get("allowed_actions", [])
        denied_actions = self.permissions[agent_id].get("denied_actions", [])

        return action in allowed_actions and action not in denied_actions

    def get_role_permissions(self, agent_id: str) -> Dict[str, List[str]]:
        """获取角色的权限列表"""
        return self.permissions.get(agent_id, {})
