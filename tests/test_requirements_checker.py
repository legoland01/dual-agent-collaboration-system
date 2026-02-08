"""RequirementsChecker 测试用例

FR-AUTO-001: CLI自动检查需求文档的完整性，检测缺失项
"""
import pytest
import tempfile
from pathlib import Path
from src.core.requirements_checker import RequirementsChecker, RequirementsCheckerError


class TestRequirementsChecker:
    """RequirementsChecker 测试类"""

    @pytest.fixture
    def temp_docs_dir(self):
        """创建临时文档目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "docs" / "01-requirements"
            docs_dir.mkdir(parents=True)
            yield docs_dir

    @pytest.fixture
    def complete_requirements(self, temp_docs_dir):
        """创建完整的需求文档"""
        doc = temp_docs_dir / "requirements_v2.2.4.md"
        content = """# 需求文档

## 概述
本文档描述v2.2.4功能需求。

## 功能需求
- FR-SKILL-001: Skill强制加载检查
- FR-GIT-002: Git提交前签署验证

## CLI命令清单
- `oc-collab skill check`
- `oc-collab git commit`

## 工时预估
- SkillEnforcer: 2h
- SignoffEnforcer: 2h
- 合计: 4h

## 依赖关系
- Python 3.9+
- PyYAML

## 签署确认
| 角色 | 确认 |
|------|------|
| Agent 1 | ✅ |
| Agent 2 | ✅ |

## 验收标准
- [ ] Skill检查命令可用
- [ ] 签署验证功能正常
- [ ] 单元测试覆盖
"""
        doc.write_text(content)
        return doc

    @pytest.fixture
    def incomplete_requirements(self, temp_docs_dir):
        """创建不完整的需求文档"""
        doc = temp_docs_dir / "requirements_incomplete.md"
        content = """# 需求文档

## 功能需求
- FR-SKILL-001: Skill强制加载检查

## 签署确认
| 角色 | 确认 |
|------|------|
| Agent 1 | ✅ |
"""
        doc.write_text(content)
        return doc

    @pytest.fixture
    def enforcer(self, temp_docs_dir):
        """创建 RequirementsChecker 实例"""
        return RequirementsChecker(str(temp_docs_dir))

    def test_check_completeness_not_found(self, enforcer):
        """TC-REQ-001: 文档不存在"""
        with pytest.raises(RequirementsCheckerError):
            enforcer.check_completeness("/nonexistent.md")

    def test_check_completeness_complete(self, enforcer, complete_requirements):
        """TC-REQ-002: 文档完整"""
        result = enforcer.check_completeness(str(complete_requirements))
        assert result["complete"] == True
        assert result["missing_sections"] == []

    def test_check_completeness_missing_sections(self, enforcer, incomplete_requirements):
        """TC-REQ-003: 缺失章节"""
        result = enforcer.check_completeness(str(incomplete_requirements))
        assert result["complete"] == False
        assert "概述" in result["missing_sections"]
        assert "功能需求" not in result["missing_sections"]

    def test_check_completeness_has_验收标准(self, enforcer, complete_requirements):
        """TC-REQ-004: 验收标准检查"""
        result = enforcer.check_completeness(str(complete_requirements))
        assert result["has_验收标准"] == True
        assert result["验收标准_count"] == 3

    def test_check_completeness_工时计算(self, enforcer, complete_requirements):
        """TC-REQ-005: 工时计算"""
        result = enforcer.check_completeness(str(complete_requirements))
        assert 4 in result["工时明细"]
        assert result["工时_inconsistent"] == False

    def test_generate_report_complete(self, enforcer, complete_requirements):
        """TC-REQ-006: 生成完整报告"""
        report = enforcer.generate_report(str(complete_requirements))
        assert "✅ 文档完整" in report
        assert "需求文档完整性报告" in report

    def test_generate_report_incomplete(self, enforcer, incomplete_requirements):
        """TC-REQ-007: 生成不完整报告"""
        report = enforcer.generate_report(str(incomplete_requirements))
        assert "❌ 文档不完整" in report
        assert "缺失章节" in report
        assert "概述" in report

    def test_list_requirement_docs(self, temp_docs_dir, enforcer, complete_requirements, incomplete_requirements):
        """TC-REQ-008: 列出需求文档"""
        docs = enforcer.list_requirement_docs()
        doc_names = [d.name for d in docs]
        assert "requirements_v2.2.4.md" in doc_names
        assert "requirements_incomplete.md" in doc_names

    def test_required_sections_all(self):
        """TC-REQ-009: 所有必需章节定义"""
        expected = ["概述", "功能需求", "CLI命令清单", "工时预估", "依赖关系", "签署确认"]
        assert RequirementsChecker.REQUIRED_SECTIONS == expected

    def test_check_completeness_工时不一致(self, temp_docs_dir):
        """TC-REQ-010: 工时预估不一致"""
        doc = temp_docs_dir / "requirements_inconsistent.md"
        doc.write_text("""# 需求文档

## 概述
测试

## 功能需求
- FR-001: 测试功能

## 签署确认
| 角色 | 确认 |
|------|------|
| Agent 1 | ✅ |
| Agent 2 | ✅ |

## 工时预估
总计: 5h
- 模块A: 2h
- 模块B: 3h
""")
        checker = RequirementsChecker(str(temp_docs_dir))
        result = checker.check_completeness(str(doc))
        assert result["工时_inconsistent"] == False
