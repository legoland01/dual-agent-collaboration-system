"""
CoverageCalculator - Skill覆盖率统计模块

统计Skill内容的切片覆盖率：
- 计算已切片的章节数
- 计算总章节数
- 生成覆盖率报告
"""

import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class CoverageReport:
    skill_id: str
    timestamp: str
    total_chapters: int
    sliced_chapters: int
    coverage_rate: float
    threshold: float
    passed: bool
    chapter_details: List[Dict] = field(default_factory=list)


@dataclass
class Chapter:
    level: int
    title: str
    content: str
    start_line: int
    end_line: int
    has_slices: bool = False


class CoverageCalculator:
    """Skill覆盖率计算器"""

    SKILLS_DIR = "skills"
    DEFAULT_THRESHOLD = 95.0

    def __init__(self, threshold: float = DEFAULT_THRESHOLD):
        self.threshold = threshold

    def _load_content(self, skill_id: str) -> Optional[str]:
        content_path = Path(self.SKILLS_DIR) / skill_id / "content.md"
        if not content_path.exists():
            return None
        try:
            return content_path.read_text(encoding='utf-8')
        except Exception:
            return None

    def _parse_chapters(self, content: str) -> List[Chapter]:
        lines = content.split('\n')
        chapters = []
        current_chapter = None

        chapter_pattern = r'^(#{1,6})\s+(.+)$'

        for i, line in enumerate(lines):
            match = re.match(chapter_pattern, line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()

                if current_chapter:
                    current_chapter.end_line = i - 1
                    chapters.append(current_chapter)

                current_chapter = Chapter(
                    level=level,
                    title=title,
                    content="",
                    start_line=i,
                    end_line=len(lines) - 1
                )

        if current_chapter:
            chapters.append(current_chapter)

        for i, chapter in enumerate(chapters):
            if i < len(chapters) - 1:
                chapter.content = '\n'.join(lines[chapter.start_line:chapters[i + 1].start_line])
            else:
                chapter.content = '\n'.join(lines[chapter.start_line:])

        return chapters

    def _get_skill_slices(self, skill_id: str) -> List[str]:
        slices_dir = Path(self.SKILLS_DIR) / skill_id / "slices"
        if not slices_dir.exists():
            return []
        return [f.name for f in slices_dir.iterdir() if f.is_file()]

    def _detect_slices(self, content: str) -> List[str]:
        slice_markers = [
            '## 触发条件',
            '## 操作步骤',
            '## 输出产物',
            '## 验收标准',
            '## 快速开始',
            '## 核心原则',
            '## SOP结构概览',
            '## 1. 触发条件',
            '## 2. 操作步骤',
            '## 3. 输出产物',
            '## 4. 验收标准',
        ]

        found_slices = []
        for marker in slice_markers:
            if marker in content:
                found_slices.append(marker.lstrip('# ').strip())

        return found_slices

    def calculate_coverage(self, skill_id: str) -> CoverageReport:
        content = self._load_content(skill_id)

        if not content:
            return CoverageReport(
                skill_id=skill_id,
                timestamp=datetime.now().isoformat(),
                total_chapters=0,
                sliced_chapters=0,
                coverage_rate=0.0,
                threshold=self.threshold,
                passed=False,
                chapter_details=[]
            )

        chapters = self._parse_chapters(content)
        slices = self._get_skill_slices(skill_id)
        detected_slices = self._detect_slices(content)

        sliced_count = len(set(slices) | set(detected_slices))

        coverage_rate = 0.0
        if len(chapters) > 0:
            coverage_rate = (sliced_count / len(chapters)) * 100

        chapter_details = []
        for chapter in chapters:
            has_slice = any(chapter.title in s or s in chapter.content for s in slices)
            chapter.has_slices = has_slice
            chapter_details.append({
                'level': chapter.level,
                'title': chapter.title,
                'has_slice': has_slice
            })

        passed = coverage_rate >= self.threshold

        return CoverageReport(
            skill_id=skill_id,
            timestamp=datetime.now().isoformat(),
            total_chapters=len(chapters),
            sliced_chapters=sliced_count,
            coverage_rate=coverage_rate,
            threshold=self.threshold,
            passed=passed,
            chapter_details=chapter_details
        )

    def check_threshold(self, skill_id: str) -> bool:
        report = self.calculate_coverage(skill_id)
        return report.passed

    def generate_report(self, skill_id: Optional[str] = None) -> List[CoverageReport]:
        reports = []

        if skill_id:
            report = self.calculate_coverage(skill_id)
            reports.append(report)
        else:
            skills_dir = Path(self.SKILLS_DIR)
            if not skills_dir.exists():
                return []
            skill_ids = [d.name for d in skills_dir.iterdir() if d.is_dir()]
            for sid in skill_ids:
                report = self.calculate_coverage(sid)
                reports.append(report)

        return reports


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Skill覆盖率统计")
    parser.add_argument('--skill', '-s', help='指定统计的Skill ID')
    parser.add_argument('--threshold', '-t', type=float, default=95.0, help='覆盖率阈值')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')

    args = parser.parse_args()

    calculator = CoverageCalculator(threshold=args.threshold)
    reports = calculator.generate_report(args.skill)

    if args.json:
        output = {
            'threshold': args.threshold,
            'total': len(reports),
            'passed': sum(1 for r in reports if r.passed),
            'reports': [
                {
                    'skill_id': r.skill_id,
                    'total_chapters': r.total_chapters,
                    'sliced_chapters': r.sliced_chapters,
                    'coverage_rate': f"{r.coverage_rate:.1f}%",
                    'passed': r.passed
                }
                for r in reports
            ]
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print(f"=== Skill覆盖率报告 (阈值: {args.threshold}%) ===")
    print(f"总计: {len(reports)}个Skill")
    print()

    passed_count = 0
    for report in reports:
        status = "✅" if report.passed else "❌"
        print(f"{status} {report.skill_id}")
        print(f"   章节: {report.sliced_chapters}/{report.total_chapters}")
        print(f"   覆盖率: {report.coverage_rate:.1f}%")
        if report.passed:
            passed_count += 1

    print()
    print(f"通过: {passed_count}/{len(reports)}")

    if passed_count < len(reports):
        print(f"\n⚠️ 覆盖率未达标的Skill需要补充切片")


if __name__ == "__main__":
    main()
