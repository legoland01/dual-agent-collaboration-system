"""ExtendedChecklistGenerator 单元测试。"""
import pytest
import tempfile
import os
from pathlib import Path
import yaml


class TestCheckItem:
    """CheckItem 测试。"""

    def test_checkitem_creation(self):
        """测试检查项创建。"""
        from src.core.extended_checklist import CheckItem

        item = CheckItem(
            id="TEST-001",
            type="测试检查",
            description="测试用例",
            severity="error"
        )

        assert item.id == "TEST-001"
        assert item.type == "测试检查"
        assert item.severity == "error"
        assert item.status == "pending"


class TestExtendedChecklistGenerator:
    """ExtendedChecklistGenerator 测试。"""

    def setup_method(self):
        """创建临时目录。"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """清理临时目录。"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """测试初始化。"""
        from src.core.extended_checklist import ExtendedChecklistGenerator

        generator = ExtendedChecklistGenerator(self.temp_dir)
        assert generator.project_path == Path(self.temp_dir)
        assert "test_coverage_threshold" in generator.rules

    def test_initialization_with_config(self):
        """测试带配置的初始化。"""
        from src.core.extended_checklist import ExtendedChecklistGenerator

        config_file = Path(self.temp_dir) / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({"checklist_rules": {"test_coverage_threshold": 0.90}}, f)

        generator = ExtendedChecklistGenerator(self.temp_dir)
        assert generator.rules["test_coverage_threshold"] == 0.90

    def test_generate_base_checklist(self):
        """测试生成基础检查项。"""
        from src.core.extended_checklist import ExtendedChecklistGenerator

        generator = ExtendedChecklistGenerator(self.temp_dir)
        checklist = generator._generate_base_checklist()

        assert len(checklist) == 2
        assert checklist[0].id == "BASE-001"
        assert checklist[1].id == "BASE-002"

    def test_generate_full_checklist_requirements(self):
        """测试生成完整检查清单（需求阶段）。"""
        from src.core.extended_checklist import ExtendedChecklistGenerator

        generator = ExtendedChecklistGenerator(self.temp_dir)
        checklist = generator.generate_full_checklist("requirements")

        assert len(checklist) >= 8
        ids = [item.id for item in checklist]
        assert "BASE-001" in ids
        assert "REQ-001" in ids

    def test_generate_full_checklist_design(self):
        """测试生成完整检查清单（设计阶段）。"""
        from src.core.extended_checklist import ExtendedChecklistGenerator

        generator = ExtendedChecklistGenerator(self.temp_dir)
        checklist = generator.generate_full_checklist("design")

        ids = [item.id for item in checklist]
        assert "DES-001" in ids

    def test_generate_full_checklist_test(self):
        """测试生成完整检查清单（测试阶段）。"""
        from src.core.extended_checklist import ExtendedChecklistGenerator

        generator = ExtendedChecklistGenerator(self.temp_dir)
        checklist = generator.generate_full_checklist("test")

        ids = [item.id for item in checklist]
        assert "TEST-001" in ids

    def test_generate_traceability_checklist_no_prd(self):
        """测试生成需求追溯检查（无PRD文件）。"""
        from src.core.extended_checklist import ExtendedChecklistGenerator

        generator = ExtendedChecklistGenerator(self.temp_dir)
        checklist = generator._generate_traceability_checklist()

        assert len(checklist) == 1
        assert checklist[0].id == "TRACE-001"
        assert "未找到需求文档" in checklist[0].description

    def test_generate_traceability_checklist_with_prd(self):
        """测试生成需求追溯检查（带PRD文件）。"""
        from src.core.extended_checklist import ExtendedChecklistGenerator

        docs_dir = Path(self.temp_dir) / "docs"
        docs_dir.mkdir(exist_ok=True)

        prd_file = docs_dir / "requirements_v1.md"
        with open(prd_file, 'w') as f:
            f.write("# 需求文档\n\nFR-001: 功能需求1\nFR-002: 功能需求2\n")

        generator = ExtendedChecklistGenerator(self.temp_dir)
        checklist = generator._generate_traceability_checklist()

        assert len(checklist) >= 1
        assert len(checklist[0].id) > 0

    def test_generate_task_scope_checklist(self):
        """测试生成任务范围检查。"""
        from src.core.extended_checklist import ExtendedChecklistGenerator

        generator = ExtendedChecklistGenerator(self.temp_dir)
        checklist = generator._generate_task_scope_checklist()

        assert len(checklist) == 3
        ids = [item.id for item in checklist]
        assert "SCOPE-001" in ids
        assert "SCOPE-002" in ids
        assert "SCOPE-003" in ids

    def test_generate_quality_gate_checklist(self):
        """测试生成质量门禁检查。"""
        from src.core.extended_checklist import ExtendedChecklistGenerator

        generator = ExtendedChecklistGenerator(self.temp_dir)
        checklist = generator._generate_quality_gate_checklist()

        assert len(checklist) == 3
        ids = [item.id for item in checklist]
        assert "QUAL-001" in ids
        assert "QUAL-002" in ids
        assert "QUAL-003" in ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
