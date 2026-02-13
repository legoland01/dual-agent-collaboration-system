"""Agent Compliance CLI准入检查

F-COMP-001: Agent Compliance CLI准入检查
Agent1无法执行todowrite/todoedit，强制创建TODO
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    AGENT_1 = "agent1"
    AGENT_2 = "agent2"


class CommandType(Enum):
    TODOWRITE = "todowrite"
    TODOEDIT = "todoedit"
    OTHER = "other"


class ComplianceLevel(Enum):
    BLOCK = "block"
    WARN = "warn"
    ALLOW = "allow"


@dataclass
class ComplianceResult:
    allowed: bool
    level: ComplianceLevel
    message: str
    command: str = ""
    agent_id: str = ""


class ComplianceViolation:
    def __init__(self, agent_id: str, command: str, reason: str, timestamp: str = None):
        self.agent_id = agent_id
        self.command = command
        self.reason = reason
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "agent_id": self.agent_id,
            "command": self.command,
            "reason": self.reason
        }


class ComplianceEnforcer:
    """
    Agent Compliance CLI准入检查器

    功能：
    - Agent1禁用todowrite/todoedit
    - 违规记录到state/compliance_violations.yaml
    - 提供合规报告生成
    """

    DISABLED_COMMANDS = {
        AgentRole.AGENT_1: [
            CommandType.TODOWRITE,
            CommandType.TODOEDIT,
        ]
    }

    VIOLATIONS_FILE = "state/compliance_violations.yaml"

    def __init__(self, agent_id: int):
        """
        初始化准入检查器

        Args:
            agent_id: Agent编号 (1或2)
        """
        self.agent_id = agent_id
        self.agent_role = AgentRole.AGENT_1 if agent_id == 1 else AgentRole.AGENT_2
        self.project_path = Path.cwd()
        self.violations_file = self.project_path / self.VIOLATIONS_FILE

    def check(self, command: str) -> ComplianceResult:
        """
        检查命令是否允许执行

        Args:
            command: 命令名称

        Returns:
            ComplianceResult: 检查结果
        """
        command_type = self._parse_command_type(command)

        if self.agent_role == AgentRole.AGENT_2:
            return ComplianceResult(
                allowed=True,
                level=ComplianceLevel.ALLOW,
                message="",
                command=command,
                agent_id=f"agent{self.agent_id}"
            )

        disabled_commands = self.DISABLED_COMMANDS.get(self.agent_role, [])

        if command_type in disabled_commands:
            message = self._get_block_message(command)
            return ComplianceResult(
                allowed=False,
                level=ComplianceLevel.BLOCK,
                message=message,
                command=command,
                agent_id=f"agent{self.agent_id}"
            )

        return ComplianceResult(
            allowed=True,
            level=ComplianceLevel.ALLOW,
            message="",
            command=command,
            agent_id=f"agent{self.agent_id}"
        )

    def _parse_command_type(self, command: str) -> CommandType:
        """
        解析命令类型

        Args:
            command: 命令字符串

        Returns:
            CommandType: 命令类型
        """
        if "todowrite" in command.lower() or ".todowrite" in command.lower():
            return CommandType.TODOWRITE
        elif "todoedit" in command.lower() or ".todoedit" in command.lower():
            return CommandType.TODOEDIT
        else:
            return CommandType.OTHER

    def _get_block_message(self, command: str) -> str:
        """
        获取阻止消息

        Args:
            command: 被阻止的命令

        Returns:
            str: 阻止消息
        """
        if CommandType.TODOWRITE in self.DISABLED_COMMANDS.get(self.agent_role, []):
            return (
                "⛔ Agent1禁止执行todowrite命令。\n"
                "\n"
                "请创建TODO给Agent2执行。\n"
                "\n"
                "正确做法:\n"
                "  oc-collab todowrite --content '任务描述' --agent 2\n"
                "\n"
                "或使用完整格式:\n"
                "  oc-collab todowrite --content '任务描述' --priority high --agent 2"
            )
        elif CommandType.TODOEDIT in self.DISABLED_COMMANDS.get(self.agent_role, []):
            return (
                "⛔ Agent1禁止执行todoedit命令。\n"
                "\n"
                "请创建TODO给Agent2执行。\n"
                "\n"
                "正确做法:\n"
                "  oc-collab todowrite --content '修改TODO内容' --agent 2"
            )

        return f"⛔ Agent1禁止执行此命令: {command}"

    def record_violation(self, result: ComplianceResult):
        """
        记录违规到文件

        Args:
            result: 检查结果
        """
        if not result.allowed:
            violation = ComplianceViolation(
                agent_id=result.agent_id,
                command=result.command,
                reason=result.message
            )
            self._append_violation(violation)
            logger.warning(f"合规违规已记录: {result.command} by {result.agent_id}")

    def _append_violation(self, violation: ComplianceViolation):
        """
        追加违规记录到文件

        Args:
            violation: 违规记录
        """
        violations = self._load_violations()

        violations["violations"].append(violation.to_dict())
        violations["total_violations"] = len(violations["violations"])

        self.violations_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.violations_file, 'w', encoding='utf-8') as f:
            yaml.dump(violations, f, allow_unicode=True, sort_keys=False)

    def _load_violations(self) -> Dict:
        """
        加载违规记录

        Returns:
            Dict: 违规记录字典
        """
        if not self.violations_file.exists():
            return {
                "violations": [],
                "total_violations": 0,
                "last_updated": datetime.now().isoformat()
            }

        try:
            with open(self.violations_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data or {"violations": [], "total_violations": 0}
        except Exception as e:
            logger.error(f"加载违规记录失败: {e}")
            return {"violations": [], "total_violations": 0}

    def get_violations(self, agent_id: Optional[str] = None) -> List[Dict]:
        """
        获取违规记录

        Args:
            agent_id: 可选的Agent过滤

        Returns:
            List[Dict]: 违规记录列表
        """
        violations = self._load_violations().get("violations", [])

        if agent_id:
            violations = [v for v in violations if v.get("agent_id") == agent_id]

        return violations

    def generate_report(self) -> str:
        """
        生成合规报告

        Returns:
            str: Markdown格式报告
        """
        violations = self._load_violations()

        report_lines = [
            "# 合规报告",
            "",
            f"**生成时间**: {datetime.now().isoformat()}",
            f"**总违规数**: {violations.get('total_violations', 0)}",
            "",
            "## 违规详情",
            "",
        ]

        all_violations = violations.get("violations", [])

        if not all_violations:
            report_lines.append("✅ 无违规记录")
        else:
            for i, v in enumerate(all_violations, 1):
                report_lines.append(f"### 违规 #{i}")
                report_lines.append("")
                report_lines.append(f"- **时间**: {v.get('timestamp', 'N/A')}")
                report_lines.append(f"- **Agent**: {v.get('agent_id', 'N/A')}")
                report_lines.append(f"- **命令**: {v.get('command', 'N/A')}")
                report_lines.append("")

        return "\n".join(report_lines)

    def get_compliance_rate(self) -> float:
        """
        计算合规率

        Returns:
            float: 合规率 (0.0 - 1.0)
        """
        total = self._load_violations().get("total_violations", 0)

        if total == 0:
            return 1.0

        agent1_violations = len(self.get_violations("agent1"))

        if agent1_violations == 0:
            return 1.0

        return 0.0
