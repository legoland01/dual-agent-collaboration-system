"""
ReferenceValidator - Skill引用关系验证模块

验证Skill内部和跨Skill的引用关系：
- 内部Markdown链接验证
- 跨Skill引用验证
- 文档内锚点验证
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class ValidationLevel(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationItem:
    code: str
    level: ValidationLevel
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    skill_id: str
    items: List[ValidationItem] = field(default_factory=list)
    passed: bool = True

    def add_item(self, item: ValidationItem):
        self.items.append(item)
        if item.level == ValidationLevel.ERROR:
            self.passed = False


class ReferenceValidator:
    """Skill引用关系验证器"""

    SKILLS_DIR = "skills"

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def _extract_links(self, content: str) -> List[Tuple[str, str, int]]:
        links = []
        markdown_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        for match in re.finditer(markdown_link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            line = content[:match.start()].count('\n') + 1
            links.append((text, url, line))

        return links

    def _extract_anchors(self, content: str) -> List[str]:
        anchor_pattern = r'##+\s+\[?([^\]]+)\]?(?:\{#[^}]+\})?'
        return re.findall(anchor_pattern, content)

    def _load_content(self, skill_id: str) -> Optional[str]:
        content_path = Path(self.SKILLS_DIR) / skill_id / "content.md"
        if not content_path.exists():
            return None
        try:
            return content_path.read_text(encoding='utf-8')
        except Exception:
            return None

    def validate_internal_links(self, skill_id: str) -> ValidationResult:
        result = ValidationResult(skill_id=skill_id)
        content = self._load_content(skill_id)

        if not content:
            return result

        links = self._extract_links(content)
        skill_path = Path(self.SKILLS_DIR) / skill_id

        for link_text, link_url, line in links:
            if link_url.startswith('#'):
                anchor = link_url[1:]
                anchors = self._extract_anchors(content)
                if anchor not in anchors:
                    result.add_item(ValidationItem(
                        code="TEST-002",
                        level=ValidationLevel.ERROR,
                        message=f"内部锚点不存在: #{link_text}",
                        file_path=str(skill_path / "content.md"),
                        line_number=line,
                        suggestion=f"创建锚点 '{anchor}' 或更新链接"
                    ))
            elif not link_url.startswith(('http', 'https', 'mailto', '#')):
                target_path = skill_path / link_url
                if not target_path.exists():
                    result.add_item(ValidationItem(
                        code="TEST-002",
                        level=ValidationLevel.ERROR,
                        message=f"内部链接文件不存在: {link_url}",
                        file_path=str(skill_path / "content.md"),
                        line_number=line,
                        suggestion=f"创建文件 {link_url} 或更新链接"
                    ))

        return result

    def validate_cross_skill_refs(self, skill_id: str) -> ValidationResult:
        result = ValidationResult(skill_id=skill_id)
        content = self._load_content(skill_id)

        if not content:
            return result

        links = self._extract_links(content)
        skills_path = Path(self.SKILLS_DIR)

        for link_text, link_url, line in links:
            if 'skills/' in link_url or link_url.startswith('/skills/'):
                parts = link_url.replace('/content.md', '').split('/')
                if 'skills' in parts:
                    idx = parts.index('skills')
                    target_skill = parts[idx + 1] if idx + 1 < len(parts) else None
                    if target_skill and target_skill != skill_id:
                        target_path = skills_path / target_skill
                        if not target_path.exists():
                            result.add_item(ValidationItem(
                                code="TEST-002",
                                level=ValidationLevel.ERROR,
                                message=f"跨Skill引用不存在: {link_text}",
                                file_path=str(skills_path / skill_id / "content.md"),
                                line_number=line,
                                suggestion=f"确认Skill '{target_skill}' 存在，或更新链接"
                            ))

        return result

    def validate_anchors(self, skill_id: str) -> ValidationResult:
        result = ValidationResult(skill_id=skill_id)
        content = self._load_content(skill_id)

        if not content:
            return result

        anchors = self._extract_anchors(content)

        if not anchors:
            result.add_item(ValidationItem(
                code="TEST-002",
                level=ValidationLevel.WARNING,
                message="文档中未找到任何锚点（标题）",
                suggestion="确保文档有清晰的章节结构"
            ))

        return result

    def validate(self, skill_id: str) -> ValidationResult:
        result = ValidationResult(skill_id=skill_id)
        result = self.validate_internal_links(skill_id)
        result = self.validate_cross_skill_refs(skill_id)
        result = self.validate_anchors(skill_id)
        return result

    def run_all_validations(self, skill_id: Optional[str] = None) -> List[ValidationResult]:
        results = []

        if skill_id:
            skill_ids = [skill_id]
        else:
            skills_dir = Path(self.SKILLS_DIR)
            if not skills_dir.exists():
                return []
            skill_ids = [d.name for d in skills_dir.iterdir() if d.is_dir()]

        for sid in skill_ids:
            result = self.validate(sid)
            results.append(result)

        return results


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Skill引用关系验证")
    parser.add_argument('--skill', '-s', help='指定验证的Skill ID')
    parser.add_argument('--verbose', '-v', action='store_true', help='输出详细结果')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')

    args = parser.parse_args()

    validator = ReferenceValidator(verbose=args.verbose)
    results = validator.run_all_validations(args.skill)

    if args.json:
        output = {
            'total': len(results),
            'passed': sum(1 for r in results if r.passed),
            'results': [
                {
                    'skill_id': r.skill_id,
                    'passed': r.passed,
                    'items': [
                        {
                            'code': item.code,
                            'level': item.level.value,
                            'message': item.message
                        }
                        for item in r.items
                    ]
                }
                for r in results
            ]
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print(f"=== 引用验证报告 ===")
    print(f"总计: {len(results)}个Skill")

    for result in results:
        status = "✅" if result.passed else "❌"
        print(f"\n{status} {result.skill_id}")
        for item in result.items:
            level_icon = "⚠️" if item.level.value == "WARNING" else "❌"
            print(f"   {level_icon} [{item.code}] {item.message}")
            if item.suggestion:
                print(f"      建议: {item.suggestion}")


if __name__ == "__main__":
    main()
