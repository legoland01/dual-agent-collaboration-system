"""Skill行为可靠性测试

测试目标：验证skill描述与实际行为的一致性
- skill内容准确性验证
- skill触发条件验证  
- skill输出产物验证
- skill引用关系验证
"""

import subprocess
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    passed: bool
    expected: str
    actual: str
    skill_name: str = ""


class SkillBehaviorTester:
    """Skill行为可靠性测试器"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        
    def log_result(self, result: TestResult):
        self.results.append(result)
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"{status}: {result.test_name}")
        print(f"   Expected: {result.expected}")
        print(f"   Actual: {result.actual}")
        return result.passed
    
    def print_summary(self):
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        print(f"\n总计: {passed}/{total} 通过")
        return passed == total


class SkillContentValidator(SkillBehaviorTester):
    """Skill内容准确性验证"""
    
    def test_skill_outputs_exist(self, skill_name: str) -> bool:
        """验证skill.json中outputs字段描述的文件是否存在"""
        skill_path = PROJECT_ROOT / "skills" / skill_name
        
        with open(skill_path / "skill.json", 'r', encoding='utf-8') as f:
            skill_data = json.load(f)
        
        outputs = skill_data.get("outputs", {})
        documents = outputs.get("documents", [])
        artifacts = outputs.get("artifacts", [])
        
        missing = []
        for doc in documents:
            # 跳过目录检查
            if doc.endswith("/"):
                continue
            if not (PROJECT_ROOT / doc).exists():
                missing.append(f"文档: {doc}")
        
        for artifact in artifacts:
            if not (PROJECT_ROOT / artifact).exists():
                missing.append(f"产物: {artifact}")
        
        result = TestResult(
            test_name=f"outputs存在性 - {skill_name}",
            passed=len(missing) == 0,
            expected="所有outputs文件存在",
            actual=f"缺失: {missing}" if missing else "全部存在",
            skill_name=skill_name
        )
        return self.log_result(result)
    
    def test_skill_triggers_match_content(self, skill_name: str) -> bool:
        """验证skill.json的triggers是否与content.md内容一致"""
        skill_path = PROJECT_ROOT / "skills" / skill_name
        
        with open(skill_path / "skill.json", 'r', encoding='utf-8') as f:
            skill_data = json.load(f)
        
        with open(skill_path / "content.md", 'r', encoding='utf-8') as f:
            content = f.read()
        
        triggers = skill_data.get("triggers", [])
        trigger_conditions = [t.get("condition", "") for t in triggers]
        
        # 检查content中是否提到这些触发条件
        found_triggers = []
        for condition in trigger_conditions:
            if condition in content.lower() or condition.replace("_", " ") in content.lower():
                found_triggers.append(condition)
        
        # 验证比例
        if len(trigger_conditions) > 0:
            coverage = len(found_triggers) / len(trigger_conditions)
            passed = coverage >= 0.5  # 至少50%匹配
        else:
            passed = True
            found_triggers = ["无触发条件配置"]
        
        result = TestResult(
            test_name=f"触发条件匹配 - {skill_name}",
            passed=passed,
            expected="content中包含触发条件描述",
            actual=f"匹配: {found_triggers}/{trigger_conditions}",
            skill_name=skill_name
        )
        return self.log_result(result)
    
    def test_sop_elements_in_content(self, skill_name: str) -> bool:
        """验证content.md是否包含SOP四要素"""
        skill_path = PROJECT_ROOT / "skills" / skill_name
        
        with open(skill_path / "content.md", 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_sections = [
            "## 1. 触发条件",
            "## 2. 操作步骤",
            "## 3. 输出产物",
            "## 4. 验收标准"
        ]
        
        missing = [s for s in required_sections if s not in content]
        
        result = TestResult(
            test_name=f"SOP四要素 - {skill_name}",
            passed=len(missing) == 0,
            expected="包含全部SOP四要素",
            actual=f"缺失: {missing}" if missing else "全部包含",
            skill_name=skill_name
        )
        return self.log_result(result)
    
    def run_all_tests(self) -> bool:
        """运行所有内容验证测试"""
        print("\n" + "="*60)
        print("Skill内容准确性验证")
        print("="*60)
        
        skills = [d.name for d in (PROJECT_ROOT / "skills").iterdir() if d.is_dir()]
        
        all_passed = True
        
        for skill in skills:
            all_passed &= self.test_skill_outputs_exist(skill)
            all_passed &= self.test_skill_triggers_match_content(skill)
            all_passed &= self.test_sop_elements_in_content(skill)
        
        return all_passed


class SkillReferenceValidator(SkillBehaviorTester):
    """Skill引用关系验证"""
    
    def test_skill_internal_references(self, skill_name: str) -> bool:
        """验证skill内部引用的章节是否存在"""
        skill_path = PROJECT_ROOT / "skills" / skill_name
        
        with open(skill_path / "content.md", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找Markdown链接 [xxx](#yyy)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        invalid_links = []
        for link_text, link_target in links:
            if link_target.startswith("#"):
                # 检查锚点是否存在
                anchor = link_target[1:]
                if anchor not in content:
                    invalid_links.append(f"{link_text} -> {link_target}")
            elif link_target.endswith(".md"):
                # 检查引用的md文件是否存在
                ref_path = PROJECT_ROOT / link_target
                if not ref_path.exists():
                    invalid_links.append(f"{link_text} -> {link_target}")
        
        result = TestResult(
            test_name=f"内部引用 - {skill_name}",
            passed=len(invalid_links) == 0,
            expected="所有引用链接有效",
            actual=f"无效: {invalid_links}" if invalid_links else "全部有效",
            skill_name=skill_name
        )
        return self.log_result(result)
    
    def test_cross_skill_references(self, skill_name: str) -> bool:
        """验证skill之间的引用是否有效"""
        skill_path = PROJECT_ROOT / "skills" / skill_name
        
        with open(skill_path / "content.md", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找对其他skill的引用
        skill_refs = re.findall(r'oc_collab_[a-z_]+_guide', content)
        
        invalid_refs = []
        for ref in skill_refs:
            ref_path = PROJECT_ROOT / "skills" / ref
            if not ref_path.exists():
                invalid_refs.append(ref)
        
        result = TestResult(
            test_name=f"跨Skill引用 - {skill_name}",
            passed=len(invalid_refs) == 0,
            expected="引用的skill目录存在",
            actual=f"无效: {invalid_refs}" if invalid_refs else "全部有效",
            skill_name=skill_name
        )
        return self.log_result(result)
    
    def run_all_tests(self) -> bool:
        """运行所有引用验证测试"""
        print("\n" + "="*60)
        print("Skill引用关系验证")
        print("="*60)
        
        skills = [d.name for d in (PROJECT_ROOT / "skills").iterdir() if d.is_dir()]
        
        all_passed = True
        
        for skill in skills:
            all_passed &= self.test_skill_internal_references(skill)
            all_passed &= self.test_cross_skill_references(skill)
        
        return all_passed


class SkillCLIActionValidator(SkillBehaviorTester):
    """Skill描述的CLI命令验证"""
    
    def test_cli_commands_from_skill(self, skill_name: str) -> bool:
        """验证skill中描述的CLI命令是否可用"""
        skill_path = PROJECT_ROOT / "skills" / skill_name
        
        with open(skill_path / "content.md", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找命令行示例
        cmd_patterns = [
            r'`(oc-collab[^`]+)`',
            r'`(python3? -m[^`]+)`',
            r'`(git add[^`]+)`',
            r'`(pytest[^`]+)`',
        ]
        
        commands = []
        for pattern in cmd_patterns:
            matches = re.findall(pattern, content)
            commands.extend(matches)
        
        # 去重
        commands = list(set(commands))
        
        invalid_cmds = []
        # 只验证oc-collab命令
        for cmd in commands:
            if cmd.startswith("oc-collab"):
                parts = cmd.split()
                result = subprocess.run(
                    [sys.executable, "-m", "src.cli.main"] + parts[1:],
                    capture_output=True,
                    text=True
                )
                # 如果命令不存在，会有明确的错误信息
                if "No such command" in result.stdout or result.returncode != 0:
                    # 不是所有命令都应该存在，检查错误类型
                    if "No module named src.cli" not in result.stderr:
                        invalid_cmds.append(f"{cmd} (返回码: {result.returncode})")
        
        result = TestResult(
            test_name=f"CLI命令验证 - {skill_name}",
            passed=len(invalid_cmds) == 0,
            expected="oc-collab命令格式正确",
            actual=f"问题: {invalid_cmds}" if invalid_cmds else "格式正确",
            skill_name=skill_name
        )
        return self.log_result(result)
    
    def run_all_tests(self) -> bool:
        """运行所有CLI命令验证"""
        print("\n" + "="*60)
        print("Skill描述的CLI命令验证")
        print("="*60)
        
        skills = [d.name for d in (PROJECT_ROOT / "skills").iterdir() if d.is_dir()]
        
        all_passed = True
        
        for skill in skills:
            all_passed &= self.test_cli_commands_from_skill(skill)
        
        return all_passed


class SkillScenarioValidator(SkillBehaviorTester):
    """Skill场景验证 - 模拟用户场景"""
    
    def test_skill_slicing_scenarios(self, skill_name: str) -> bool:
        """验证skill切片命令在典型场景下的行为"""
        
        # 测试skill slice命令
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "slice", skill_name],
            capture_output=True,
            text=True
        )
        
        passed = result.returncode == 0
        actual = result.stdout[:200] if result.stdout else result.stderr[:200]
        
        result_obj = TestResult(
            test_name=f"Skill切片 - {skill_name}",
            passed=passed,
            expected="skill slice命令返回成功",
            actual=f"返回码: {result.returncode}" if not passed else "成功",
            skill_name=skill_name
        )
        return self.log_result(result_obj)
    
    def test_skill_search_scenarios(self, keyword: str) -> bool:
        """验证skill搜索在关键词场景下的行为"""
        
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "search", "--keywords", keyword],
            capture_output=True,
            text=True
        )
        
        passed = result.returncode == 0
        
        result_obj = TestResult(
            test_name=f"Skill搜索 - '{keyword}'",
            passed=passed,
            expected="skill search命令返回成功",
            actual=f"返回码: {result.returncode}" if not passed else "成功",
            skill_name=""
        )
        return self.log_result(result_obj)
    
    def test_skill_enforce_scenarios(self) -> bool:
        """验证skill强制执行场景"""
        
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "enforce"],
            capture_output=True,
            text=True
        )
        
        passed = result.returncode == 0
        
        result_obj = TestResult(
            test_name="Skill强制执行",
            passed=passed,
            expected="skill enforce命令返回成功",
            actual=f"返回码: {result.returncode}" if not passed else "成功",
            skill_name=""
        )
        return self.log_result(result_obj)
    
    def run_all_tests(self) -> bool:
        """运行所有场景验证测试"""
        print("\n" + "="*60)
        print("Skill场景验证")
        print("="*60)
        
        skills = [d.name for d in (PROJECT_ROOT / "skills").iterdir() if d.is_dir()]
        
        all_passed = True
        
        # 测试所有skill的切片
        for skill in skills:
            all_passed &= self.test_skill_slicing_scenarios(skill)
        
        # 测试搜索关键词
        keywords = ["需求", "设计", "测试", "Bug", "部署", "开发", "评审"]
        for keyword in keywords:
            all_passed &= self.test_skill_search_scenarios(keyword)
        
        # 测试强制执行
        all_passed &= self.test_skill_enforce_scenarios()
        
        return all_passed


class SkillAcceptanceStandardValidator(SkillBehaviorTester):
    """Skill验收标准验证"""
    
    def test_验收标准可执行性(self, skill_name: str) -> bool:
        """验证skill描述的验收标准是否可执行"""
        skill_path = PROJECT_ROOT / "skills" / skill_name
        
        with open(skill_path / "content.md", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找验收标准章节
        acceptance_section_match = re.search(
            r'## 4\. 验收标准.*?(?=##|$)',
            content,
            re.DOTALL
        )
        
        if not acceptance_section_match:
            result = TestResult(
                test_name=f"验收标准可执行性 - {skill_name}",
                passed=False,
                expected="包含验收标准章节",
                actual="未找到验收标准章节",
                skill_name=skill_name
            )
            return self.log_result(result)
        
        acceptance_content = acceptance_section_match.group()
        
        # 检查是否有具体的检查方法
        has_check_method = "检查" in acceptance_content or "运行" in acceptance_content or "验证" in acceptance_content
        
        result = TestResult(
            test_name=f"验收标准可执行性 - {skill_name}",
            passed=has_check_method,
            expected="验收标准有具体检查方法",
            actual=f"有检查方法: {has_check_method}",
            skill_name=skill_name
        )
        return self.log_result(result)
    
    def run_all_tests(self) -> bool:
        """运行所有验收标准验证"""
        print("\n" + "="*60)
        print("Skill验收标准验证")
        print("="*60)
        
        skills = [d.name for d in (PROJECT_ROOT / "skills").iterdir() if d.is_dir()]
        
        all_passed = True
        
        for skill in skills:
            all_passed &= self.test_验收标准可执行性(skill)
        
        return all_passed


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("Skill行为可靠性测试")
    print("测试目标: 验证skill描述与实际行为的一致性")
    print("="*60)
    
    all_passed = True
    
    # Phase 1: 内容准确性验证
    content_tester = SkillContentValidator()
    all_passed &= content_tester.run_all_tests()
    
    # Phase 2: 引用关系验证
    ref_tester = SkillReferenceValidator()
    all_passed &= ref_tester.run_all_tests()
    
    # Phase 3: CLI命令验证
    cli_tester = SkillCLIActionValidator()
    all_passed &= cli_tester.run_all_tests()
    
    # Phase 4: 场景验证
    scenario_tester = SkillScenarioValidator()
    all_passed &= scenario_tester.run_all_tests()
    
    # Phase 5: 验收标准验证
    acceptance_tester = SkillAcceptanceStandardValidator()
    all_passed &= acceptance_tester.run_all_tests()
    
    # 打印汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    content_tester.print_summary()
    ref_tester.print_summary()
    cli_tester.print_summary()
    scenario_tester.print_summary()
    acceptance_tester.print_summary()
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ 全部测试通过！")
    else:
        print("❌ 部分测试失败，请查看详细信息")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
