#!/usr/bin/env python3
"""
需求覆盖率 PoC 脚本

目标：确保需求文档中的功能描述在 E2E 测试中得到覆盖

用法:
    python scripts/requirements_coverage_poc.py
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple


class RequirementsCoveragePOC:
    """需求覆盖率 PoC"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.requirements_dir = self.project_root / "docs" / "01-requirements"
        self.tests_dir = self.project_root / "tests"

    def extract_commands_from_file(self, file_path: Path) -> Set[str]:
        """从文件提取所有 oc-collab 命令"""
        commands = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 匹配反引号中的命令: `oc-collab ...`
                pattern = r'`(oc-collab[^`]+)`'
                matches = re.findall(pattern, content)
                for match in matches:
                    # 清理命令
                    cmd = match.strip()
                    if cmd.startswith('oc-collab'):
                        commands.add(cmd)
        except Exception as e:
            print(f"  ⚠️  读取失败 {file_path}: {e}")
        return commands

    def extract_commands_from_tests(self, test_path: Path) -> Set[str]:
        """从测试文件提取执行的命令"""
        commands = set()
        try:
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # 方法1: 匹配 Click runner.invoke 函数调用 (函数名_command)
                pattern1 = r'runner\.invoke\([\w]+\.([\w_]+)_command'
                matches1 = re.findall(pattern1, content)
                for match in matches1:
                    commands.add(f'oc-collab {match}')

                # 方法2: 匹配 Click runner.invoke 直接函数名
                pattern2 = r'runner\.invoke\(([\w_]+),?'
                matches2 = re.findall(pattern2, content)
                for match in matches2:
                    if not match.endswith('_command'):  # 避免重复
                        commands.add(f'oc-collab {match}')

                # 方法3: 匹配 main() 或 cli() 调用子命令
                pattern3 = r'(?:main|cli)\([\'"]([\w-]+)[\'"]'
                matches3 = re.findall(pattern3, content)
                for match in matches3:
                    commands.add(f'oc-collab {match}')

                # 方法4: 匹配 webhook_group, state_group 等组命令
                pattern4 = r'(webhook|state|skill|compliance|deploy|todo|signoff)_group'
                matches4 = re.findall(pattern4, content)
                for match in matches4:
                    commands.add(f'oc-collab {match}')

        except Exception as e:
            print(f"  ⚠️  读取失败 {test_path}: {e}")
        return commands

    def extract_keywords_from_requirements(self, file_path: Path) -> Set[str]:
        """从需求文档提取关键词"""
        keywords = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 匹配功能描述中的关键短语
                patterns = [
                    r'(?:功能|命令|特性)[:\s]+([A-Z][a-z]+(?:\s+[a-z]+){0,5})',
                    r'(?:使用|执行|运行)[:\s]+`([^`]+)`',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        keywords.add(match.strip())
        except Exception as e:
            print(f"  ⚠️  读取失败 {file_path}: {e}")
        return keywords

    def scan_requirements(self) -> Dict[str, Set[str]]:
        """扫描所有需求文档，提取命令"""
        all_commands = {}
        print("📄 扫描需求文档...")
        for doc_path in self.requirements_dir.glob("*.md"):
            if doc_path.name.startswith("."):
                continue
            commands = self.extract_commands_from_file(doc_path)
            if commands:
                all_commands[doc_path.name] = commands
                print(f"  {doc_path.name}: {len(commands)} 个命令")
        return all_commands

    def scan_tests(self) -> Set[str]:
        """扫描所有测试文件，提取命令"""
        print("🧪 扫描测试文件...")
        all_commands = set()
        for test_path in self.tests_dir.glob("test_e2e*.py"):
            commands = self.extract_commands_from_tests(test_path)
            all_commands.update(commands)
            print(f"  {test_path.name}: {len(commands)} 个命令")
        return all_commands

    def calculate_coverage(
        self,
        requirements_commands: Dict[str, Set[str]],
        test_commands: Set[str]
    ) -> Dict:
        """计算覆盖率"""
        # 收集所有需求中的命令
        all_req_commands = set()
        for commands in requirements_commands.values():
            all_req_commands.update(commands)

        # 计算覆盖
        covered = all_req_commands & test_commands
        uncovered = all_req_commands - test_commands

        coverage_percent = (
            (len(covered) / len(all_req_commands) * 100)
            if all_req_commands else 0
        )

        return {
            "total_requirements": len(all_req_commands),
            "covered_count": len(covered),
            "uncovered_count": len(uncovered),
            "coverage_percent": round(coverage_percent, 1),
            "covered_items": list(covered),
            "uncovered_items": list(uncovered),
            "by_document": {
                doc: {
                    "commands": list(commands),
                    "covered": list(commands & test_commands),
                    "uncovered": list(commands - test_commands)
                }
                for doc, commands in requirements_commands.items()
            }
        }

    def run(self) -> Dict:
        """运行 PoC"""
        print("=" * 60)
        print("🔍 需求覆盖率 PoC")
        print("=" * 60)
        print()

        # 扫描
        requirements_commands = self.scan_requirements()
        print()
        test_commands = self.scan_tests()
        print()

        # 计算
        print("📊 计算覆盖率...")
        result = self.calculate_coverage(requirements_commands, test_commands)
        print()

        # 输出
        print("=" * 60)
        print("📈 覆盖率报告")
        print("=" * 60)
        print(f"  需求命令总数: {result['total_requirements']}")
        print(f"  已覆盖: {result['covered_count']}")
        print(f"  未覆盖: {result['uncovered_count']}")
        print(f"  覆盖率: {result['coverage_percent']}%")
        print()

        if result['uncovered_items']:
            print("❌ 未覆盖的需求:")
            for cmd in result['uncovered_items']:
                print(f"   - {cmd}")
        else:
            print("✅ 所有需求都已覆盖!")
        print()

        return result


def main():
    """主入口"""
    poc = RequirementsCoveragePOC()
    result = poc.run()

    # 保存结果
    output_file = Path(__file__).parent / "coverage_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"📄 结果已保存到: {output_file}")


if __name__ == "__main__":
    main()
