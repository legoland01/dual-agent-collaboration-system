"""
CLIActionValidator - CLI命令验证模块

验证Skill中描述的CLI命令是否存在：
- 从content.md提取CLI命令
- 验证命令是否在CLI中注册
"""

import re
from pathlib import Path
from typing import List, Set, Optional
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


class CLIActionValidator:
    """CLI命令验证器"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._all_commands: Optional[Set[str]] = None

    def _get_all_commands(self) -> Set[str]:
        if self._all_commands is not None:
            return self._all_commands

        try:
            from src.cli.main import cli
            commands = set()

            def collect(cmd, prefix=""):
                full_name = (prefix + " " + cmd.name).strip()
                commands.add(full_name)
                commands.add(cmd.name)
                for sub in cmd.commands.values():
                    collect(sub, full_name)

            collect(cli)
            self._all_commands = commands
        except ImportError:
            self._all_commands = set()

        return self._all_commands

    def _load_content(self, skill_id: str) -> Optional[str]:
        content_path = Path("skills") / skill_id / "content.md"
        if not content_path.exists():
            return None
        try:
            return content_path.read_text(encoding='utf-8')
        except Exception:
            return None

    def extract_cli_commands(self, skill_id: str) -> List[str]:
        content = self._load_content(skill_id)
        if not content:
            return []

        cli_pattern = r'`(oc-collab[\s\S]*?)`'
        matches = re.findall(cli_pattern, content, re.IGNORECASE)

        commands = []
        for match in matches:
            cmd = match.strip()
            if cmd:
                commands.append(cmd)

        return commands

    def validate_commands(self, skill_id: str) -> ValidationResult:
        result = ValidationResult(skill_id=skill_id)
        content = self._load_content(skill_id)

        if not content:
            return result

        cli_pattern = r'`(oc-collab[\s\S]*?)`'
        matches = re.findall(cli_pattern, content, re.IGNORECASE)

        if not matches:
            return result

        available_commands = self._get_all_commands()

        for match in matches:
            cmd_str = match.strip()
            parts = cmd_str.split()
            if len(parts) >= 2:
                cmd_name = parts[1]
                full_cmd = cmd_str.replace('oc-collab ', '').split()[0] if len(parts) > 1 else None

                cmd_found = False
                for avail in available_commands:
                    if cmd_name in avail or (full_cmd and full_cmd in avail):
                        cmd_found = True
                        break

                if not cmd_found:
                    line = content.find(match)
                    line_number = content[:line].count('\n') + 1 if line != -1 else None

                    result.add_item(ValidationItem(
                        code="TEST-003",
                        level=ValidationLevel.ERROR,
                        message=f"CLI命令不存在: oc-collab {cmd_name}...",
                        file_path=f"skills/{skill_id}/content.md",
                        line_number=line_number,
                        suggestion="确认命令已实现，或更新skill描述"
                    ))

        return result

    def validate(self, skill_id: str) -> ValidationResult:
        return self.validate_commands(skill_id)

    def run_all_validations(self, skill_id: Optional[str] = None) -> List[ValidationResult]:
        results = []

        if skill_id:
            skill_ids = [skill_id]
        else:
            skills_dir = Path("skills")
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

    parser = argparse.ArgumentParser(description="CLI命令验证")
    parser.add_argument('--skill', '-s', help='指定验证的Skill ID')
    parser.add_argument('--verbose', '-v', action='store_true', help='输出详细结果')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')

    args = parser.parse_args()

    validator = CLIActionValidator(verbose=args.verbose)
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

    print(f"=== CLI命令验证报告 ===")
    print(f"总计: {len(results)}个Skill")

    for result in results:
        status = "✅" if result.passed else "❌"
        print(f"\n{status} {result.skill_id}")
        for item in result.items:
            level_icon = "⚠️" if item.level.value == "WARNING" else "❌"
            print(f"   {level_icon} [{item.code}] {item.message}")


if __name__ == "__main__":
    main()
