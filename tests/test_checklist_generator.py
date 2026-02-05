import pytest
import tempfile
from pathlib import Path


def test_extract_requirements():
    from src.core.checklist_generator import ChecklistGenerator

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ChecklistGenerator(tmpdir)

        doc = Path(tmpdir) / "requirements.md"
        doc.write_text("""
# 需求文档

## FR-001 用户登录
用户应该能够登录系统。

## FR-002 用户注册
新用户应该能够注册账号。
        """)

        reqs = generator.extract_requirements(str(doc))
        assert len(reqs) == 2
        assert any(r["id"] == "FR-001" for r in reqs)
        assert any(r["id"] == "FR-002" for r in reqs)


def test_extract_requirements_with_bug_id():
    from src.core.checklist_generator import ChecklistGenerator

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ChecklistGenerator(tmpdir)

        doc = Path(tmpdir) / "requirements.md"
        doc.write_text("## BUG-20260203-001 Session Start\n修复 session_start 功能缺失。")

        reqs = generator.extract_requirements(str(doc))
        assert len(reqs) == 1
        assert reqs[0]["id"] == "BUG-20260203-001"


def test_generate_requirements_checklist():
    from src.core.checklist_generator import ChecklistGenerator

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ChecklistGenerator(tmpdir)

        doc = Path(tmpdir) / "requirements.md"
        doc.write_text("## FR-001 用户登录\n用户应该能够登录系统。")

        checklist = generator.generate_requirements_checklist(str(doc))
        assert len(checklist) > 0
        assert any("FR-001" in item.id for item in checklist)
        assert any("唯一ID" in item.title for item in checklist)
        assert any("验收标准" in item.title for item in checklist)


def test_generate_design_checklist():
    from src.core.checklist_generator import ChecklistGenerator

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ChecklistGenerator(tmpdir)

        doc = Path(tmpdir) / "design.md"
        doc.write_text("# 设计文档")

        checklist = generator.generate_design_checklist(str(doc))
        assert len(checklist) > 0
        assert any("需求关联" in item.title for item in checklist)
        assert any("实现方案" in item.title for item in checklist)


def test_generate_test_checklist():
    from src.core.checklist_generator import ChecklistGenerator

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ChecklistGenerator(tmpdir)

        doc = Path(tmpdir) / "test.md"
        doc.write_text("# 测试文档")

        checklist = generator.generate_test_checklist(str(doc))
        assert len(checklist) > 0
        assert any("需求覆盖" in item.title for item in checklist)
        assert any("测试覆盖率" in item.title for item in checklist)


def test_render_checklist():
    from src.core.checklist_generator import ChecklistGenerator, CheckItem, CheckStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ChecklistGenerator(tmpdir)

        checklist = [
            CheckItem(id="test1", title="检查项1", description="测试", status=CheckStatus.PASSED),
            CheckItem(id="test2", title="检查项2", description="测试", status=CheckStatus.FAILED),
        ]

        rendered = generator.render_checklist(checklist, "测试")
        assert "检查项1" in rendered
        assert "检查项2" in rendered
        assert "✓" in rendered
        assert "✗" in rendered
        assert "通过项: 1" in rendered
        assert "未通过项: 1" in rendered


def test_find_orphan_items():
    from src.core.checklist_generator import ChecklistGenerator

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ChecklistGenerator(tmpdir)

        req_dir = Path(tmpdir) / "docs" / "01-requirements"
        design_dir = Path(tmpdir) / "docs" / "02-design"
        req_dir.mkdir(parents=True)
        design_dir.mkdir(parents=True)

        req_doc = req_dir / "requirements.md"
        req_doc.write_text("## FR-001 用户登录\nFR-002 用户注册")

        design_doc = design_dir / "design.md"
        design_doc.write_text("# 设计文档\nFR-001 有关联")

        orphans = generator.find_orphan_items("requirements")
        assert "FR-002" in orphans


def test_find_orphan_items_no_orphans():
    from src.core.checklist_generator import ChecklistGenerator

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ChecklistGenerator(tmpdir)

        req_dir = Path(tmpdir) / "docs" / "01-requirements"
        design_dir = Path(tmpdir) / "docs" / "02-design"
        req_dir.mkdir(parents=True)
        design_dir.mkdir(parents=True)

        req_doc = req_dir / "requirements.md"
        req_doc.write_text("## FR-001 用户登录")

        design_doc = design_dir / "design.md"
        design_doc.write_text("# 设计文档\nFR-001 有关联")

        orphans = generator.find_orphan_items("requirements")
        assert len(orphans) == 0
