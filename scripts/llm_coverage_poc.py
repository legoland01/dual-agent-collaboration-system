#!/usr/bin/env python3
"""
需求覆盖率 PoC - LLM 语义匹配版本

目标：使用 LLM 的语义理解能力判断测试是否覆盖需求

用法:
    python scripts/llm_coverage_poc.py
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple


class LLMCoveragePOC:
    """基于 LLM 的需求覆盖率 PoC"""

    def __init__(self, project_root: str = None, llm_client=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.requirements_dir = self.project_root / "docs" / "01-requirements"
        self.tests_dir = self.project_root / "tests"
        self.llm_client = llm_client

    def extract_requirements_with_descriptions(self) -> Dict[str, str]:
        """提取需求文档中的功能描述"""
        requirements = {}
        
        for doc_path in self.requirements_dir.glob("*.md"):
            if doc_path.name.startswith("."):
                continue
            
            try:
                content = doc_path.read_text(encoding='utf-8')
                
                # 提取功能/特性描述 - 改进正则
                patterns = [
                    # 匹配 - 功能: 描述
                    r'-\s+([A-Z]+[\w-]*\d*)\s*[:：]\s*(.+)',
                    # 匹配 **功能** 描述
                    r'\*\*([A-Z]+[\w-]*\d*)\*\*[:：]\s*(.+)',
                    # 匹配 `oc-collab xxx` 命令
                    r'`(oc-collab[^`]+)`',
                    # 匹配 Features 下面的列表项
                    r'\|\s*([A-Z]+[\w-]*\d*)\s*\|.*?\|\s*(.+?)\s*\|',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if len(match) >= 2:
                            req_id = match[0].strip()
                            desc = match[1].strip()
                            # 过滤太短的描述
                            if len(desc) > 5:
                                key = f"{doc_path.name}::{req_id}"
                                requirements[key] = f"{req_id}: {desc}"
                        elif len(match) == 1 and len(match[0]) > 3:
                            key = f"{doc_path.name}::{match[0]}"
                            requirements[key] = match[0]
                            
            except Exception as e:
                print(f"  ⚠️  读取失败 {doc_path}: {e}")
        
        return requirements

    def extract_test_functions(self) -> Dict[str, str]:
        """提取测试函数及其代码"""
        tests = {}
        
        for test_path in self.tests_dir.glob("test_*.py"):
            try:
                content = test_path.read_text(encoding='utf-8')
                
                # 提取测试函数
                pattern = r'def\s+(test_\w+)\(.*?\):\s*["""\'](.*?)["""\']?\s*(.*?)(?=\n(?:    )?def |\nclass |\Z)'
                matches = re.findall(pattern, content, re.DOTALL)
                
                for match in matches:
                    func_name = match[0]
                    docstring = match[1].strip() if match[1] else ""
                    code = match[2].strip()[:500]  # 取前500字符
                    
                    key = f"{test_path.name}::{func_name}"
                    tests[key] = f"{docstring}\n{code}" if docstring else code
                    
            except Exception as e:
                print(f"  ⚠️  读取失败 {test_path}: {e}")
        
        return tests

    def mock_llm_check(self, requirement: str, test_code: str) -> bool:
        """
        模拟 LLM 判断（用于快速测试）
        
        实际实现时应该调用真实的 LLM API
        """
        # 简单的关键词匹配作为模拟
        req_keywords = set(re.findall(r'\w+', requirement.lower()))
        test_keywords = set(re.findall(r'\w+', test_code.lower()))
        
        # 计算交集
        overlap = req_keywords & test_keywords
        
        # 如果有超过3个关键词重叠，认为覆盖
        return len(overlap) > 3

    def check_coverage(self, requirements: Dict[str, str], tests: Dict[str, str]) -> Dict:
        """检查覆盖率"""
        covered = []
        uncovered = []
        
        for req_id, req_desc in requirements.items():
            is_covered = False
            
            for test_name, test_code in tests.items():
                # 使用 LLM 或模拟方法判断
                if self.mock_llm_check(req_desc, test_code):
                    is_covered = True
                    covered.append({
                        "requirement": req_id,
                        "description": req_desc,
                        "test": test_name
                    })
                    break
            
            if not is_covered:
                uncovered.append({
                    "requirement": req_id,
                    "description": req_desc
                })
        
        total = len(requirements)
        coverage_percent = (len(covered) / total * 100) if total > 0 else 0
        
        return {
            "total_requirements": total,
            "covered_count": len(covered),
            "uncovered_count": len(uncovered),
            "coverage_percent": round(coverage_percent, 1),
            "covered": covered[:10],  # 只显示前10个
            "uncovered": uncovered[:10]
        }

    def run(self) -> Dict:
        """运行 PoC"""
        print("=" * 60)
        print("🔍 需求覆盖率 PoC (LLM 语义匹配版)")
        print("=" * 60)
        print()

        # 1. 提取需求
        print("📄 提取需求描述...")
        requirements = self.extract_requirements_with_descriptions()
        print(f"  找到 {len(requirements)} 个需求")
        for req_id, desc in list(requirements.items())[:5]:
            print(f"    - {req_id}: {desc[:50]}...")
        print()

        # 2. 提取测试
        print("🧪 提取测试函数...")
        tests = self.extract_test_functions()
        print(f"  找到 {len(tests)} 个测试函数")
        for test_name in list(tests.keys())[:5]:
            print(f"    - {test_name}")
        print()

        # 3. 检查覆盖
        print("🔬 检查覆盖率...")
        result = self.check_coverage(requirements, tests)
        print()

        # 4. 输出结果
        print("=" * 60)
        print("📈 覆盖率报告")
        print("=" * 60)
        print(f"  总需求数: {result['total_requirements']}")
        print(f"  已覆盖: {result['covered_count']}")
        print(f"  未覆盖: {result['uncovered_count']}")
        print(f"  覆盖率: {result['coverage_percent']}%")
        print()

        if result['uncovered']:
            print("❌ 未覆盖的需求（前10个）:")
            for item in result['uncovered']:
                print(f"   - {item['requirement']}: {item['description'][:60]}...")

        return result


def main():
    """主入口"""
    poc = LLMCoveragePOC()
    result = poc.run()

    # 保存结果
    output_file = Path(__file__).parent / "llm_coverage_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n📄 结果已保存到: {output_file}")


if __name__ == "__main__":
    main()
