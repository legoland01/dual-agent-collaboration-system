"""AutoChecker: todowrite参数自动检查器

FR-AI-001: todowrite自动检查
"""

from typing import Optional, List, Dict, Any


class AutoCheckerError(Exception):
    """AutoChecker 错误"""
    pass


class ValidationError(AutoCheckerError):
    """参数验证错误"""
    pass


class AutoChecker:
    """todowrite 参数自动检查器"""

    VALID_AGENT_IDS = ["1", "2"]
    VALID_PRIORITIES = ["high", "medium", "low"]

    def __init__(self):
        pass

    def validate_content(self, content: Optional[str]) -> str:
        """
        验证待办内容

        Args:
            content: 待办内容

        Returns:
            验证通过的内容

        Raises:
            ValidationError: 内容为空
        """
        if not content or not content.strip():
            raise ValidationError("待办内容不能为空")
        return content.strip()

    def validate_agent_id(self, agent_id: Optional[str]) -> Optional[str]:
        """
        验证 Agent ID

        Args:
            agent_id: Agent编号

        Returns:
            验证通过的Agent ID

        Raises:
            ValidationError: Agent ID 无效
        """
        if agent_id is None:
            return None
        if agent_id not in self.VALID_AGENT_IDS:
            raise ValidationError(f"无效的 Agent ID: {agent_id}，可选值: {self.VALID_AGENT_IDS}")
        return agent_id

    def validate_priority(self, priority: str) -> str:
        """
        验证并规范化优先级

        Args:
            priority: 优先级

        Returns:
            规范化的优先级
        """
        if priority not in self.VALID_PRIORITIES:
            return "medium"  # 默认值
        return priority

    def check_all(self, content: Optional[str],
                  agent_id: Optional[str],
                  priority: str) -> Dict[str, Any]:
        """
        完整参数检查

        Args:
            content: 待办内容
            agent_id: Agent编号
            priority: 优先级

        Returns:
            检查结果字典
        """
        result = {
            "valid": True,
            "content": None,
            "agent_id": None,
            "priority": None,
            "errors": [],
            "warnings": []
        }

        try:
            result["content"] = self.validate_content(content)
        except ValidationError as e:
            result["valid"] = False
            result["errors"].append(str(e))

        try:
            result["agent_id"] = self.validate_agent_id(agent_id)
        except ValidationError as e:
            result["valid"] = False
            result["errors"].append(str(e))

        result["priority"] = self.validate_priority(priority)

        return result
