# 详细设计：动态 Checklist 机制

**设计文档ID**: DETAIL-2026-02-002
**需求ID**: MEMO-2026-02-004-ADDENDUM
**创建日期**: 2026-02-05

---

## 1. 设计概述

实现动态 checklist 生成器，在评审时根据文档内容自动生成针对性检查项。

### 1.1 组件架构

```
src/
├── cli/
│   └── main.py              # 修改 review 命令，添加 --checklist 选项
└── core/
    └── checklist_generator.py  # 新建动态 checklist 生成器
```

### 1.2 类设计

```python
class CheckItem:
    """检查项"""
    - id: str
    - title: str
    - description: str
    - status: str  # pending, passed, failed, warning
    - details: str

class ChecklistGenerator:
    """动态 checklist 生成器"""
    - project_path: str
    
    + generate_requirements_checklist(doc_path: str) -> List[CheckItem]
    + generate_design_checklist(doc_path: str) -> List[CheckItem]
    + generate_test_checklist(doc_path: str) -> List[CheckItem]
    + check_traceability(doc_type: str) -> List[CheckItem]
```

---

## 2. 核心实现

### 2.1 CheckItem 类

```python
# src/core/checklist_generator.py
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class CheckStatus(Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class CheckItem:
    """检查项"""
    id: str
    title: str
    description: str
    status: CheckStatus = CheckStatus.PENDING
    details: str = ""
    requirements_id: Optional[str] = None
```

### 2.2 ChecklistGenerator 类

```python
import re
from pathlib import Path
from typing import List, Dict, Optional
from .checklist_generator_types import CheckItem, CheckStatus


class ChecklistGenerator:
    """动态 checklist 生成器"""

    BASE_CHECKS = [
        ("format", "格式正确", "文档格式符合模板要求"),
        ("version", "版本信息", "文档包含版本号和更新日期"),
        ("completeness", "完整性", "所有章节内容完整"),
    ]

    def __init__(self, project_path: str):
        self.project_path = project_path

    def extract_requirements(self, doc_path: str) -> List[Dict]:
        """从需求文档中提取需求列表"""
        requirements = []
        try:
            with open(doc_path, 'r') as f:
                content = f.read()

            pattern = r'(FR|UR|NFR)-[\w-]+'
            req_ids = re.findall(pattern, content)
            unique_ids = list(set(req_ids))

            for req_id in unique_ids:
                requirements.append({
                    "id": req_id,
                    "description": f"需求 {req_id}"
                })
        except Exception:
            pass

        return requirements

    def find_orphan_items(self, doc_type: str) -> List[str]:
        """查找未关联的条目"""
        orphans = []

        if doc_type == "requirements":
            req_pattern = r'(FR|UR|NFR)-[\w-]+'
            design_pattern = r'DETAIL-[\d-]+'

            req_docs = list((Path(self.project_path) / "docs" / "01-requirements").glob("*.md"))
            design_docs = list((Path(self.project_path) / "docs" / "02-design").glob("*.md"))

            for req_doc in req_docs:
                with open(req_doc) as f:
                    content = f.read()
                    reqs = set(re.findall(req_pattern, content))
                    designs = set(re.findall(design_pattern, content))

                    for req in reqs:
                        if not any(req in content for content in [open(d).read() for d in design_docs]):
                            if req not in orphans:
                                orphans.append(req)

        return orphans

    def generate_requirements_checklist(self, doc_path: str) -> List[CheckItem]:
        """生成需求文档检查清单"""
        checklist = []

        for check_id, title, description in self.BASE_CHECKS:
            checklist.append(CheckItem(
                id=f"req_base_{check_id}",
                title=title,
                description=description
            ))

        requirements = self.extract_requirements(doc_path)

        for req in requirements:
            checklist.extend([
                CheckItem(
                    id=f"req_{req['id']}_unique",
                    title=f"需求 {req['id']} - 唯一ID",
                    description="需求是否有唯一标识",
                    requirements_id=req['id']
                ),
                CheckItem(
                    id=f"req_{req['id']}_acceptance",
                    title=f"需求 {req['id']} - 验收标准",
                    description="需求是否有明确的验收标准",
                    requirements_id=req['id']
                ),
                CheckItem(
                    id=f"req_{req['id']}_description",
                    title=f"需求 {req['id']} - 详细描述",
                    description="需求描述是否完整",
                    requirements_id=req['id']
                ),
                CheckItem(
                    id=f"req_{req['id']}_design",
                    title=f"需求 {req['id']} - 设计关联",
                    description="是否有对应的设计文档",
                    requirements_id=req['id']
                ),
                CheckItem(
                    id=f"req_{req['id']}_test",
                    title=f"需求 {req['id']} - 测试关联",
                    description="是否有对应的测试用例",
                    requirements_id=req['id']
                ),
            ])

        orphans = self.find_orphan_items("requirements")
        if orphans:
            checklist.append(CheckItem(
                id="req_traceability",
                title="追溯性",
                description=f"发现 {len(orphans)} 个未关联的需求，需要处理",
                status=CheckStatus.WARNING,
                details=", ".join(orphans)
            ))

        return checklist

    def generate_design_checklist(self, doc_path: str) -> List[CheckItem]:
        """生成设计文档检查清单"""
        checklist = []

        for check_id, title, description in self.BASE_CHECKS:
            checklist.append(CheckItem(
                id=f"design_base_{check_id}",
                title=title,
                description=description
            ))

        checklist.extend([
            CheckItem(
                id="design_requirements_link",
                title="需求关联",
                description="设计是否关联到具体需求"
            ),
            CheckItem(
                id="design_implementation",
                title="实现方案",
                description="实现方案是否具体可行"
            ),
            CheckItem(
                id="design_edge_cases",
                title="边界条件",
                description="是否覆盖所有边界情况"
            ),
        ])

        return checklist

    def generate_test_checklist(self, doc_path: str) -> List[CheckItem]:
        """生成测试文档检查清单"""
        checklist = []

        for check_id, title, description in self.BASE_CHECKS:
            checklist.append(CheckItem(
                id=f"test_base_{check_id}",
                title=title,
                description=description
            ))

        checklist.extend([
            CheckItem(
                id="test_requirements_link",
                title="需求覆盖",
                description="测试是否覆盖所有需求"
            ),
            CheckItem(
                id="test_coverage",
                title="测试覆盖率",
                description="测试覆盖率是否达到标准"
            ),
        ])

        return checklist

    def render_checklist(self, checklist: List[CheckItem], title: str) -> str:
        """渲染 checklist 为字符串"""
        lines = [f"┌─ {title} ─", "│"]

        passed = sum(1 for item in checklist if item.status == CheckStatus.PASSED)
        failed = sum(1 for item in checklist if item.status == CheckStatus.FAILED)
        warnings = sum(1 for item in checklist if item.status == CheckStatus.WARNING)

        lines.append(f"│ 通过项: {passed}")
        lines.append(f"│ 未通过项: {failed}")
        lines.append(f"│ 警告项: {warnings}")
        lines.append("│")

        for item in checklist:
            status_icon = {
                CheckStatus.PENDING: "○",
                CheckStatus.PASSED: "✓",
                CheckStatus.FAILED: "✗",
                CheckStatus.WARNING: "⚠",
            }[item.status]

            lines.append(f"│ {status_icon} {item.title}")
            if item.details:
                for detail_line in item.details.split('\n')[:2]:
                    lines.append(f"│   {detail_line}")

        lines.append("│")
        lines.append("└" + "─" * 40)

        return '\n'.join(lines)
```

### 2.3 CLI 集成

修改 `src/cli/main.py` 中的 `review_command`:

```python
@main.command("review")
@click.argument("stage", type=click.Choice(["requirements", "design", "test"]))
@click.option("--file", "-f", help="指定评审文件路径")
@click.option("--checklist", "-c", is_flag=True, default=False, help="显示动态检查清单")
@click.option("--new", is_flag=True, default=False)
@click.option("--list", "-l", is_flag=True, default=False)
def review_command(stage: str, file: str, checklist: bool, new: bool, list: bool):
    """管理评审流程。"""
    try:
        project_path = get_project_path()
        state_manager = StateManager(project_path)
        workflow_engine = WorkflowEngine(state_manager)

        if checklist:
            from ..core.checklist_generator import ChecklistGenerator, CheckStatus

            generator = ChecklistGenerator(project_path)

            if stage == "requirements":
                if file:
                    doc_path = file
                else:
                    req_dir = Path(project_path) / "docs" / "01-requirements"
                    doc_path = str(sorted(req_dir.glob("*.md"))[-1] if req_dir.exists() else "")

                if doc_path and Path(doc_path).exists():
                    checklist_items = generator.generate_requirements_checklist(doc_path)
                    rendered = generator.render_checklist(checklist_items, f"{stage.upper()} 评审 Checklist")
                    console.print(Panel(rendered, title="动态检查清单", style="green"))
                else:
                    click.echo("错误: 未找到需求文档")

            elif stage == "design":
                if file:
                    doc_path = file
                else:
                    design_dir = Path(project_path) / "docs" / "02-design"
                    doc_path = str(sorted(design_dir.glob("*.md"))[-1] if design_dir.exists() else "")

                if doc_path and Path(doc_path).exists():
                    checklist_items = generator.generate_design_checklist(doc_path)
                    rendered = generator.render_checklist(checklist_items, f"{stage.upper()} 评审 Checklist")
                    console.print(Panel(rendered, title="动态检查清单", style="green"))
                else:
                    click.echo("错误: 未找到设计文档")

            elif stage == "test":
                if file:
                    doc_path = file
                else:
                    test_dir = Path(project_path) / "docs" / "03-test"
                    doc_path = str(sorted(test_dir.glob("*.md"))[-1] if test_dir.exists() else "")

                if doc_path and Path(doc_path).exists():
                    checklist_items = generator.generate_test_checklist(doc_path)
                    rendered = generator.render_checklist(checklist_items, f"{stage.upper()} 评审 Checklist")
                    console.print(Panel(rendered, title="动态检查清单", style="green"))
                else:
                    click.echo("错误: 未找到测试文档")

        if new:
            workflow_engine.start_review(stage)
            click.echo(f"已发起 {stage} 评审")

        if list:
            history = state_manager.get_history()
            console.print(f"\n[bold]{stage.upper()} 评审历史[/bold]")
            for item in history[:10]:
                if "review" in item["action"] or "signoff" in item["action"]:
                    console.print(f"- {item['timestamp']}: Agent {item['agent']} - {item['details']}")

    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)
```

---

## 3. 测试用例

```python
# tests/test_checklist_generator.py
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


def test_generate_requirements_checklist():
    from src.core.checklist_generator import ChecklistGenerator

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ChecklistGenerator(tmpdir)

        doc = Path(tmpdir) / "requirements.md"
        doc.write_text("## FR-001 用户登录\n用户应该能够登录系统。")

        checklist = generator.generate_requirements_checklist(str(doc))
        assert len(checklist) > 0
        assert any("FR-001" in item.id for item in checklist)


def test_render_checklist():
    from src.core.checklist_generator import ChecklistGenerator, CheckItem

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
```

---

## 4. 验收验证

| 验证项 | 验证命令 |
|--------|----------|
| review 命令支持 --checklist 选项 | `oc-collab review requirements --checklist` |
| 生成动态 checklist | 检查输出是否包含动态生成的检查项 |
| 追溯性检查 | 检查是否能发现未关联的需求 |

---

**设计版本**: v1
**创建日期**: 2026-02-05
**状态**: 待实现
