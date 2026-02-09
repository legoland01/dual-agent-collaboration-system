"""SkillSearcher: Skill关键词检索器

FR-SKILL-001: Skill切片检索
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import re


class SkillSearchError(Exception):
    """Skill检索错误"""
    pass


class SkillSearcher:
    """Skill关键词检索器"""

    def __init__(self, skills_dir: Optional[str] = None):
        self.skills_dir = Path(skills_dir) if skills_dir else Path.cwd() / "skills"

    def search(self, keywords: List[str],
               match_mode: str = "any") -> List[Dict[str, Any]]:
        """
        关键词检索

        Args:
            keywords: 关键词列表
            match_mode: 匹配模式 ("any" 或 "all")

        Returns:
            匹配结果列表
        """
        if not self.skills_dir.exists():
            return []

        results = []

        for skill_file in self.skills_dir.glob("**/content.md"):
            score = self._calculate_score(skill_file, keywords, match_mode)

            if score > 0:
                with open(skill_file) as f:
                    content = f.read()

                results.append({
                    "file": str(skill_file),
                    "name": skill_file.parent.name,
                    "score": score,
                    "matched_keywords": self._get_matched_keywords(content, keywords),
                    "excerpt": self._get_excerpt(content, keywords)
                })

        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:10]  # 限制返回数量

    def _calculate_score(self, skill_file: Path, keywords: List[str],
                         match_mode: str) -> int:
        """
        计算匹配分数

        Args:
            skill_file: Skill文件路径
            keywords: 关键词列表
            match_mode: 匹配模式

        Returns:
            匹配分数
        """
        with open(skill_file) as f:
            content = f.read().lower()

        matched = sum(1 for kw in keywords if kw.lower() in content)

        if match_mode == "all":
            return matched if matched == len(keywords) else 0
        else:  # any
            return matched

    def _get_matched_keywords(self, content: str, keywords: List[str]) -> List[str]:
        """获取匹配的关键词"""
        return [kw for kw in keywords if kw.lower() in content.lower()]

    def _get_excerpt(self, content: str, keywords: List[str],
                      context_lines: int = 2) -> str:
        """
        获取匹配上下文摘要

        Args:
            content: Skill内容
            keywords: 关键词列表
            context_lines: 上下文行数

        Returns:
            摘要文本
        """
        lines = content.split('\n')
        excerpts = []

        for i, line in enumerate(lines):
            if any(kw.lower() in line.lower() for kw in keywords):
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                excerpt = '\n'.join(lines[start:end])
                excerpts.append(f"...{excerpt}...")

        return '\n'.join(excerpts[:3])  # 最多3个片段
