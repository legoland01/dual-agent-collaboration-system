"""
SkillTester - Skill内容准确性验证模块

验证Skill内容与实际行为的一致性，包括：
- outputs文件存在性验证
- 触发条件匹配验证
- SOP四要素完整性验证
- CLI命令存在性验证
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import yaml
import json
from datetime import datetime


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

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.items if item.level == ValidationLevel.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.items if item.level == ValidationLevel.WARNING)

    def add_item(self, item: ValidationItem):
        self.items.append(item)
        if item.level == ValidationLevel.ERROR:
            self.passed = False


@dataclass
class TestReport:
    timestamp: str
    total_skills: int
    passed_skills: int
    results: List[ValidationResult]

    @property
    def success_rate(self) -> float:
        if self.total_skills == 0:
            return 0.0
        return self.passed_skills / self.total_skills * 100


class SkillTesterError(Exception):
    """SkillTester 错误基类"""
    pass


class SkillLoadError(SkillTesterError):
    """Skill加载错误"""
    pass


class SkillTester:
    """Skill内容准确性测试器"""

    SKILLS_DIR = "skills"

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def _load_skill(self, skill_id: str) -> Tuple[Optional[dict], Optional[str]]:
        skill_path = Path(self.SKILLS_DIR) / skill_id
        skill_json_path = skill_path / "skill.json"

        if not skill_json_path.exists():
            return None, f"Skill目录不存在: {skill_id}"

        try:
            with open(skill_json_path, 'r', encoding='utf-8') as f:
                skill_config = yaml.safe_load(f)
            return skill_config, None
        except Exception as e:
            return None, f"加载skill.json失败: {e}"

    def _load_content(self, skill_id: str) -> Optional[str]:
        content_path = Path(self.SKILLS_DIR) / skill_id / "content.md"
        if not content_path.exists():
            return None
        try:
            return content_path.read_text(encoding='utf-8')
        except Exception:
            return None
        content_path = Path(self.SKILLS_DIR) / skill_id / "content.md"
        if not content_path.exists():
            return None
        return content_path.read_text(encoding='utf-8')

    def validate_outputs_exist(self, skill_id: str) -> ValidationResult:
        result = ValidationResult(skill_id=skill_id)
        skill_config, error = self._load_skill(skill_id)

        if error:
            result.add_item(ValidationItem(
                code="TEST-001",
                level=ValidationLevel.ERROR,
                message=error,
                suggestion="检查skill.json配置是否正确"
            ))
            return result

        outputs = skill_config.get('outputs', [])
        if not outputs:
            result.add_item(ValidationItem(
                code="TEST-005",
                level=ValidationLevel.WARNING,
                message=f"Skill '{skill_id}' 未定义outputs字段",
                suggestion="在skill.json中添加outputs字段，或更新文档"
            ))
            return result

        skill_path = Path(self.SKILLS_DIR) / skill_id
        for output in outputs:
            output_path = skill_path / output
            if not output_path.exists():
                result.add_item(ValidationItem(
                    code="TEST-001",
                    level=ValidationLevel.ERROR,
                    message=f"outputs文件中定义的文件不存在: {output}",
                    file_path=str(skill_path / "skill.json"),
                    suggestion=f"创建文件 {output} 或更新skill.json中的outputs配置"
                ))

        return result

    def validate_triggers_match(self, skill_id: str) -> ValidationResult:
        result = ValidationResult(skill_id=skill_id)
        skill_config, error = self._load_skill(skill_id)

        if error:
            return result

        triggers_raw = skill_config.get('triggers', [])
        content = self._load_content(skill_id)

        if not content:
            return result

        triggers = [str(t) for t in triggers_raw] if triggers_raw else []
        for trigger in triggers:
            if trigger.lower() not in content.lower():  # type: ignore
                result.add_item(ValidationItem(
                    code="TEST-001",
                    level=ValidationLevel.WARNING,
                    message=f"触发条件 '{trigger}' 在content.md中未找到匹配",
                    suggestion="更新触发条件或content.md内容"
                ))

        return result

    def validate_sop_elements(self, skill_id: str) -> ValidationResult:
        result = ValidationResult(skill_id=skill_id)
        content = self._load_content(skill_id)

        if not content:
            result.add_item(ValidationItem(
                code="TEST-004",
                level=ValidationLevel.ERROR,
                message=f"content.md文件不存在: {skill_id}/content.md"
            ))
            return result

        required_elements = {
            '触发条件': r'触发条件|触发关键词|触发场景',
            '操作步骤': r'操作步骤|步骤|Phase|阶段',
            '输出产物': r'输出产物|输出|产物',
            '验收标准': r'验收标准|验收|检查标准'
        }

        for element_name, pattern in required_elements.items():
            if not re.search(pattern, content, re.IGNORECASE):
                result.add_item(ValidationItem(
                    code="TEST-004",
                    level=ValidationLevel.WARNING,
                    message=f"SOP四要素缺失: {element_name}",
                    suggestion=f"在content.md中添加{element_name}章节"
                ))

        return result

    def validate_cli_commands(self, skill_id: str) -> ValidationResult:
        result = ValidationResult(skill_id=skill_id)
        content = self._load_content(skill_id)

        if not content:
            return result

        cli_pattern = r'`oc-collab\s+[\w-]+[^`]*`'
        commands = re.findall(cli_pattern, content)

        if not commands:
            return result

        try:
            from src.cli.main import cli
            all_commands = set()

            def collect_commands(cmd, prefix=""):
                all_commands.add(prefix + cmd.name)
                for sub in cmd.commands.values():
                    collect_commands(sub, prefix + cmd.name + " ")

            collect_commands(cli)

            for cmd_str in commands:
                cmd_name = cmd_str.strip('`').split()[1] if len(cmd_str.strip('`').split()) > 1 else None
                if cmd_name:
                    cmd_found = any(c.endswith(cmd_name) for c in all_commands)
                    if not cmd_found:
                        result.add_item(ValidationItem(
                            code="TEST-003",
                            level=ValidationLevel.ERROR,
                            message=f"CLI命令不存在: {cmd_str}",
                            suggestion="确认命令已实现，或更新skill描述"
                        ))
        except ImportError:
            pass

        return result

    def run_all_tests(self, skill_id: Optional[str] = None) -> TestReport:
        results = []

        if skill_id:
            skill_ids = [skill_id]
        else:
            skills_dir = Path(self.SKILLS_DIR)
            if not skills_dir.exists():
                return TestReport(
                    timestamp=datetime.now().isoformat(),
                    total_skills=0,
                    passed_skills=0,
                    results=[]
                )
            skill_ids = [d.name for d in skills_dir.iterdir() if d.is_dir()]

        for sid in skill_ids:
            result = ValidationResult(skill_id=sid)
            result = self.validate_outputs_exist(sid)
            result = self.validate_triggers_match(sid)
            result = self.validate_sop_elements(sid)
            result = self.validate_cli_commands(sid)
            results.append(result)

        passed_count = sum(1 for r in results if r.passed)

        return TestReport(
            timestamp=datetime.now().isoformat(),
            total_skills=len(results),
            passed_skills=passed_count,
            results=results
        )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Skill内容准确性测试")
    parser.add_argument('--skill', '-s', help='指定测试的Skill ID')
    parser.add_argument('--verbose', '-v', action='store_true', help='输出详细结果')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')

    args = parser.parse_args()

    tester = SkillTester(verbose=args.verbose)
    report = tester.run_all_tests(args.skill)

    if args.json:
        output = {
            'timestamp': report.timestamp,
            'total': report.total_skills,
            'passed': report.passed_skills,
            'success_rate': f"{report.success_rate:.1f}%",
            'results': [
                {
                    'skill_id': r.skill_id,
                    'passed': r.passed,
                    'errors': r.error_count,
                    'warnings': r.warning_count,
                    'items': [
                        {
                            'code': item.code,
                            'level': item.level.value,
                            'message': item.message
                        }
                        for item in r.items
                    ]
                }
                for r in report.results
            ]
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print(f"=== Skill测试报告 ===")
    print(f"时间: {report.timestamp}")
    print(f"总计: {report.total_skills}个Skill")
    print(f"通过: {report.passed_skills}个")
    print(f"成功率: {report.success_rate:.1f}%")
    print("")

    for result in report.results:
        status = "✅" if result.passed else "❌"
        print(f"{status} {result.skill_id}")
        if not result.passed and args.verbose:
            for item in result.items:
                level_icon = "⚠️" if item.level.value == "WARNING" else "❌"
                print(f"   {level_icon} [{item.code}] {item.message}")
                if item.suggestion:
                    print(f"      建议: {item.suggestion}")

    if report.success_rate < 100:
        print(f"\n⚠️ 测试未完全通过，请检查以上问题")
        exit(2)


if __name__ == "__main__":
    main()
