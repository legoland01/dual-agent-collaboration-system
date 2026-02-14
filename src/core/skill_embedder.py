"""
Skill嵌入器

将Skill规则嵌入到TODO内容中。
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SkillEmbedder:
    """Skill嵌入器"""

    def __init__(self, skill_loader: Optional["SkillLoader"] = None, max_length: int = 500):
        """
        Args:
            skill_loader: Skill加载器
            max_length: 最大嵌入长度
        """
        self.skill_loader = skill_loader
        self.max_length = max_length

    def embed(self, content: str, skill_name: str) -> str:
        """
        嵌入Skill规则到TODO内容

        Args:
            content: 原始内容
            skill_name: Skill名称

        Returns:
            str: 嵌入后的内容

        Raises:
            SkillNotFoundError: Skill不存在
            SkillEmbedError: 嵌入失败
        """
        if not self.skill_loader:
            raise SkillEmbedError("SkillLoader未初始化")

        skill = self.skill_loader.load_skill(skill_name)
        if not skill:
            raise SkillNotFoundError(f"Skill不存在: {skill_name}")

        try:
            # 提取关键规则
            key_rules = self._extract_key_rules(skill)

            # 截断如果过长
            if len(key_rules) > self.max_length:
                key_rules = key_rules[:self.max_length] + "..."

            # 嵌入格式
            embedded = f"{content}\n\n[Skill: {skill_name}]\n{key_rules}"

            return embedded

        except Exception as e:
            raise SkillEmbedError(f"嵌入Skill失败: {e}")

    def _extract_key_rules(self, skill: dict) -> str:
        """提取Skill关键规则"""
        content = skill.get("content", "")
        if not content:
            return ""

        lines = content.split("\n")
        key_parts = []

        for line in lines:
            stripped = line.strip()
            # 提取步骤、SOP等关键部分
            if stripped.startswith(("1.", "2.", "3.", "- ", "• ")):
                key_parts.append(stripped)

            # 提取关键章节标题
            if stripped.startswith("#") and len(stripped) < 50:
                key_parts.append(stripped)

        return "\n".join(key_parts[:15])  # 最多15条

    def embed_summary(self, content: str, skill_name: str, max_length: int = 200) -> str:
        """
        嵌入Skill摘要（较短版本）

        Args:
            content: 原始内容
            skill_name: Skill名称
            max_length: 最大长度

        Returns:
            str: 嵌入摘要后的内容
        """
        if not self.skill_loader:
            return content

        skill = self.skill_loader.load_skill(skill_name)
        if not skill:
            return content

        summary = skill.get("summary", "") or skill.get("description", "")
        if not summary:
            return content

        # 截断摘要
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return f"{content}\n\n[{skill_name}] {summary}"


class SkillNotFoundError(Exception):
    """Skill未找到异常"""

    def __init__(self, message: str):
        super().__init__(message)


class SkillEmbedError(Exception):
    """Skill嵌入异常"""

    def __init__(self, message: str):
        super().__init__(message)
