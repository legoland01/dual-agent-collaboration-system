"""文档状态绑定器 - v2.2.2 F-PROC-001.2"""
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from datetime import datetime

from .compliance_engine import ComplianceEngine, ComplianceResult, ComplianceResultType


class DocumentStateBinder:
    """文档状态绑定器"""

    # 文档状态机
    DOCUMENT_STATES = {
        "DRAFT": {
            "transitions": ["REVIEW_PENDING"],
            "agent1_actions": ["edit", "submit_review", "view"],
            "agent2_actions": ["view"],
        },
        "REVIEW_PENDING": {
            "transitions": ["REVIEWED", "DRAFT"],
            "agent1_actions": ["view"],
            "agent2_actions": ["review", "signoff", "view"],
        },
        "REVIEWED": {
            "transitions": ["APPROVED", "REVIEW_PENDING"],
            "agent1_actions": ["confirm", "signoff", "view"],
            "agent2_actions": ["view"],
        },
        "APPROVED": {
            "transitions": ["ARCHIVED"],
            "agent1_actions": ["view"],
            "agent2_actions": ["view"],
        },
        "ARCHIVED": {
            "transitions": [],
            "agent1_actions": ["view"],
            "agent2_actions": ["view"],
        },
    }

    ERROR_MESSAGES = {
        "draft_no_review": (
            "⛔ 无法发起评审: 文档状态为 DRAFT，请先确认为可评审版本。"
            "当前状态: DRAFT"
            "要求状态: REVIEW_PENDING 或 APPROVED"
            "提示: 使用 oc-collab doc status 查看文档状态"
        ),
        "reviewed_no_re_review": (
            "⛔ 无法重复评审: 文档已由 Agent2 评审并签署。"
            "当前状态: REVIEWED"
            "提示: 请 Agent1 确认并签署"
        ),
        "archived_no_edit": (
            "⛔ 无法编辑: 文档已归档。"
            "当前状态: ARCHIVED"
            "提示: 归档文档不可修改"
        ),
        "action_not_allowed": (
            "⛔ 操作不允许: {agent_id} 无法执行 '{action}' 操作。"
            "当前状态: {state}"
        ),
    }

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.states = self.DOCUMENT_STATES
        self.states_file = self.project_path / "state" / "document_states.yaml"
        self._ensure_states_file()

    def _ensure_states_file(self):
        """确保文档状态文件存在"""
        state_dir = self.project_path / "state"
        state_dir.mkdir(exist_ok=True)
        if not self.states_file.exists():
            self.states_file.write_text("document_states: {}\n")

    def _get_doc_state_path(self, doc_path: str) -> str:
        """获取文档相对路径"""
        doc_path = Path(doc_path)
        if doc_path.is_absolute():
            try:
                return str(doc_path.relative_to(self.project_path))
            except ValueError:
                return str(doc_path)
        return str(doc_path)

    def _load_states(self) -> Dict[str, Dict]:
        """加载文档状态"""
        try:
            data = yaml.safe_load(self.states_file.read_text())
            return data.get("document_states", {})
        except Exception as e:
            print(f"⚠️ 加载文档状态失败: {e}")
            return {}

    def _save_states(self, states: Dict[str, Dict]):
        """保存文档状态"""
        serializable_states = {}
        for key, value in states.items():
            serializable_states[str(key)] = value
        with open(self.states_file, "w") as f:
            yaml.safe_dump({"document_states": serializable_states}, f, allow_unicode=True)

    def get_doc_state(self, doc_path: str) -> str:
        """获取文档状态"""
        doc_key = self._get_doc_state_path(doc_path)
        states = self._load_states()
        return states.get(doc_key, {}).get("state", "DRAFT")

    def check(
        self, action: str, target: str, agent_id: str
    ) -> ComplianceResult:
        """
        检查状态转换是否合法

        Args:
            action: 操作类型
            target: 文档路径
            agent_id: Agent ID

        Returns:
            ComplianceResult: 检查结果
        """
        current_state = self.get_doc_state(target)

        if current_state not in self.states:
            return ComplianceResult(
                check_type="doc_state",
                result_type=ComplianceResultType.WARNING,
                agent_id=agent_id,
                action=action,
                target=target,
                message=f"⚠️ 未知文档状态: {current_state}",
            )

        state_config = self.states[current_state]
        allowed_actions = state_config.get(f"{agent_id}_actions", [])

        if action not in allowed_actions:
            if current_state == "DRAFT" and action == "submit_review":
                return ComplianceResult(
                    check_type="doc_state",
                    result_type=ComplianceResultType.DENIED,
                    agent_id=agent_id,
                    action=action,
                    target=target,
                    message=self.ERROR_MESSAGES["draft_no_review"],
                )
            elif current_state == "REVIEWED" and action == "review":
                return ComplianceResult(
                    check_type="doc_state",
                    result_type=ComplianceResultType.DENIED,
                    agent_id=agent_id,
                    action=action,
                    target=target,
                    message=self.ERROR_MESSAGES["reviewed_no_re_review"],
                )
            elif current_state == "ARCHIVED" and action in ["edit", "submit_review"]:
                return ComplianceResult(
                    check_type="doc_state",
                    result_type=ComplianceResultType.DENIED,
                    agent_id=agent_id,
                    action=action,
                    target=target,
                    message=self.ERROR_MESSAGES["archived_no_edit"],
                )
            else:
                return ComplianceResult(
                    check_type="doc_state",
                    result_type=ComplianceResultType.DENIED,
                    agent_id=agent_id,
                    action=action,
                    target=target,
                    message=self.ERROR_MESSAGES["action_not_allowed"].format(
                        agent_id=agent_id, action=action, state=current_state
                    ),
                )

        return ComplianceResult(
            check_type="doc_state",
            result_type=ComplianceResultType.PASSED,
            agent_id=agent_id,
            action=action,
            target=target,
            message=f"✅ 文档状态检查通过 (状态: {current_state})",
        )

    def can_review(self, doc_path: str, agent_id: str) -> bool:
        """检查是否可以评审"""
        result = self.check("review", doc_path, agent_id)
        return result.result_type == ComplianceResultType.PASSED

    def can_edit(self, doc_path: str, agent_id: str) -> bool:
        """检查是否可以编辑"""
        result = self.check("edit", doc_path, agent_id)
        return result.result_type == ComplianceResultType.PASSED

    def set_state(
        self, doc_path: str, state: str, updated_by: str
    ) -> bool:
        """
        设置文档状态

        Args:
            doc_path: 文档路径
            state: 新状态
            updated_by: 更新者

        Returns:
            bool: 是否成功
        """
        if state not in self.DOCUMENT_STATES:
            print(f"⚠️ 无效状态: {state}")
            return False

        doc_key = self._get_doc_state_path(doc_path)
        states = self._load_states()

        current_state = states.get(doc_key, {}).get("state", "DRAFT")
        allowed_transitions = self.DOCUMENT_STATES.get(current_state, {}).get(
            "transitions", []
        )

        if state not in allowed_transitions:
            print(
                f"⚠️ 不允许的状态转换: {current_state} -> {state}"
            )
            return False

        states[doc_key] = {
            "state": state,
            "updated_by": updated_by,
            "updated_at": datetime.now().isoformat(),
        }

        self._save_states(states)
        print(f"✅ 文档状态已更新: {doc_key} -> {state}")
        return True

    def get_all_states(self) -> Dict[str, Dict]:
        """获取所有文档状态"""
        return self._load_states()
