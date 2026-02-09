"""SkillSlicer: Skill切片器

FR-SKILL-002: Skill切片检索
"""

from pathlib import Path
from typing import Optional, List, Dict, Any, TypedDict


class Chapter(TypedDict):
    """章节信息"""
    id: str
    title: str
    content: List[str]
    level: int
    line_number: int


class SkillSlicer:
    """Skill切片器"""

    SLICE_LEVELS = {
        "chapter": "# ",      # 一级标题
        "section": "## ",     # 二级标题
        "subsection": "### "  # 三级标题
    }

    def __init__(self, skills_dir: Optional[str] = None):
        self.skills_dir = Path(skills_dir) if skills_dir else Path.cwd() / "skills"

    def list_chapters(self, skill_name: str) -> List[Chapter]:
        """
        列出Skill的所有章节

        Args:
            skill_name: Skill名称

        Returns:
            章节列表
        """
        skill_file = self.skills_dir / skill_name / "content.md"

        if not skill_file.exists():
            return []

        with open(skill_file) as f:
            content = f.read()

        chapters: List[Chapter] = []
        current_chapter: Chapter = {
            "id": "intro",
            "title": "简介",
            "content": [],
            "level": 0,
            "line_number": 0
        }

        lines = content.split('\n')
        for i, line in enumerate(lines):
            level = self._get_heading_level(line)

            if level > 0:
                if current_chapter["content"]:
                    chapters.append(current_chapter)

                current_chapter = {
                    "id": f"section-{len(chapters)+1}",
                    "title": line.lstrip("# ").strip(),
                    "content": [],
                    "level": level,
                    "line_number": i + 1
                }
            else:
                current_chapter["content"].append(line)

        if current_chapter["content"]:
            chapters.append(current_chapter)

        return chapters

    def _get_heading_level(self, line: str) -> int:
        """
        获取标题级别

        Args:
            line: 文本行

        Returns:
            标题级别 (0=非标题, 1=#, 2=##, etc.)
        """
        stripped = line.lstrip()

        if not stripped.startswith("#"):
            return 0

        level = 0
        for char in stripped:
            if char == "#":
                level += 1
            else:
                break

        return level

    def get_slice(self, skill_name: str, section_id: str,
                  include_subsections: bool = True) -> str:
        """
        获取指定切片

        Args:
            skill_name: Skill名称
            section_id: 章节ID
            include_subsections: 是否包含子章节

        Returns:
            切片内容
        """
        chapters = self.list_chapters(skill_name)

        for chapter in chapters:
            if chapter["id"] == section_id:
                if include_subsections:
                    return self._combine_section(chapters, chapter)
                else:
                    return "\n".join(chapter["content"])

        return ""

    def _combine_section(self, all_chapters: List[Chapter],
                        target: Chapter) -> str:
        """
        合并章节及其子章节

        Args:
            all_chapters: 所有章节
            target: 目标章节

        Returns:
            合并后的内容
        """
        result = [f"# {target['title']}"]
        result.extend(target["content"])

        if target["level"] > 0:
            for chapter in all_chapters:
                if chapter["level"] > target["level"] and chapter["level"] <= target["level"] + 1:
                    if chapter["title"] != target["title"]:
                        result.extend(["", f"## {chapter['title']}"])
                        result.extend(chapter["content"])

        return "\n".join(result)
