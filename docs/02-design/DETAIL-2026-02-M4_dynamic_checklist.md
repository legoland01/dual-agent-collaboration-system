# 详细设计：动态 Checklist 机制（扩展）

**设计文档ID**: DETAIL-2026-02-M4
**版本**: v1
**日期**: 2026-02-05
**作者**: Agent 2 (开发负责人)
**状态**: DRAFT

---

## 1. 概述

### 1.1 功能描述

扩展现有的 `checklist_generator.py`，增加需求追溯检查、任务范围检查、质量门禁检查。

### 1.2 相关需求

- FR-CHECKLIST-001
- FR-CHECKLIST-002
- FR-CHECKLIST-003
- FR-CHECKLIST-004

### 1.3 与上一轮的关系

| 上一轮实现 | 本轮扩展 |
|------------|----------|
| 基础检查项生成 | 需求追溯检查 |
| 文档分析 | 任务范围检查 |
| - | 质量门禁检查 |

---

## 2. 技术设计

### 2.1 检查项类型

```python
class ChecklistType(Enum):
    BASE_CHECK = "基础检查"
    REQUIREMENTS_TRACE = "需求追溯"
    TASK_SCOPE = "任务范围"
    QUALITY_GATE = "质量门禁"
```

### 2.2 检查规则配置

```python
CHECKLIST_RULES = {
    "requirements_to_design": True,
    "design_to_code": True,
    "code_to_test": True,
    "test_coverage_threshold": 0.80,
    "test_pass_rate_threshold": 1.00,
}
```

---

## 3. 实现方案

### 3.1 扩展 ChecklistGenerator

```python
class ExtendedChecklistGenerator(ChecklistGenerator):
    """扩展的动态检查项生成器"""

    def __init__(self, project_path: str):
        super().__init__(project_path)
        self.rules = self._load_rules()

    def generate_full_checklist(self, stage: str) -> List[CheckItem]:
        """生成完整检查清单"""
        checklist = []

        # 1. 基础检查
        checklist.extend(self.generate_base_checklist())

        # 2. 阶段专项检查
        if stage == "requirements":
            checklist.extend(self.generate_requirements_checklist())
        elif stage == "design":
            checklist.extend(self.generate_design_checklist())
        elif stage == "test":
            checklist.extend(self.generate_test_checklist())

        # 3. 需求追溯检查
        checklist.extend(self.generate_traceability_checklist())

        # 4. 任务范围检查
        checklist.extend(self.generate_task_scope_checklist())

        # 5. 质量门禁检查
        checklist.extend(self.generate_quality_gate_checklist())

        return checklist

    def generate_traceability_checklist(self) -> List[CheckItem]:
        """生成需求追溯检查"""
        checklist = []

        # 检查需求到设计的追溯
        requirements = self.extract_requirements_from_docs()
        for req in requirements:
            design = self.find_design_for_requirement(req)
            if design:
                checklist.append(CheckItem(
                    id=f"trace_{req.id}",
                    title=f"需求追溯 - {req.id} → {design.id}",
                    description="需求必须有对应的设计文档",
                    status=CheckStatus.PASSED
                ))
            else:
                checklist.append(CheckItem(
                    id=f"trace_{req.id}",
                    title=f"需求追溯 - {req.id}",
                    description="需求缺少对应的设计文档",
                    status=CheckStatus.FAILED
                ))

        return checklist

    def generate_quality_gate_checklist(self) -> List[CheckItem]:
        """生成质量门禁检查"""
        checklist = []

        # 测试覆盖率检查
        coverage = self.get_test_coverage()
        if coverage >= self.rules["test_coverage_threshold"]:
            checklist.append(CheckItem(
                id="quality_coverage",
                title=f"测试覆盖率 - {coverage:.0%} >= {self.rules['test_coverage_threshold']:.0%}",
                description="测试覆盖率达标",
                status=CheckStatus.PASSED
            ))
        else:
            checklist.append(CheckItem(
                id="quality_coverage",
                title=f"测试覆盖率 - {coverage:.0%} < {self.rules['test_coverage_threshold']:.0%}",
                description="测试覆盖率未达标",
                status=CheckStatus.FAILED
            ))

        # 测试通过率检查
        pass_rate = self.get_test_pass_rate()
        if pass_rate >= self.rules["test_pass_rate_threshold"]:
            checklist.append(CheckItem(
                id="quality_pass_rate",
                title=f"测试通过率 - {pass_rate:.0%} >= {self.rules['test_pass_rate_threshold']:.0%}",
                description="测试通过率达标",
                status=CheckStatus.PASSED
            ))

        return checklist
```

### 3.2 CLI 集成

```bash
# 评审并显示完整检查清单
oc-collab review requirements --checklist

# 只显示检查清单
oc-collab checklist show --phase requirements

# 检查特定任务范围
oc-collab checklist verify --task TASK-001

# 检查质量门禁
oc-collab checklist quality
```

---

## 4. 与 Ad-hoc Items 集成

```python
def generate_adhoc_checklist(self) -> List[CheckItem]:
    """生成 Ad-hoc Items 检查"""
    checklist = []

    adhoc_items = self.load_adhoc_items()
    pending_items = [item for item in adhoc_items if item.status != "confirmed"]

    if pending_items:
        checklist.append(CheckItem(
            id="adhoc_pending",
            title=f"待确认的 Ad-hoc Items - {len(pending_items)} 个",
            description="请确认所有 Ad-hoc Items 后再签署",
            status=CheckStatus.WARNING,
            details=self.format_items(pending_items)
        ))

    return checklist
```

---

## 5. 测试用例

### 5.1 追溯测试

```python
def test_requirements_traceability():
    """测试需求追溯检查"""
    generator = ExtendedChecklistGenerator(project_path)
    checklist = generator.generate_traceability_checklist()

    assert len(checklist) > 0
    assert any("追溯" in item.title for item in checklist)
```

### 5.2 质量门禁测试

```python
def test_quality_gate_coverage():
    """测试质量门禁覆盖率检查"""
    generator = ExtendedChecklistGenerator(project_path)
    checklist = generator.generate_quality_gate_checklist()

    assert len(checklist) > 0
    assert any("覆盖率" in item.title for item in checklist)
```

---

## 6. 验收标准

| 标准 | 验证方式 |
|------|----------|
| --checklist 选项生效 | CLI 测试 |
| 需求追溯检查完整 | 集成测试 |
| 任务范围检查准确 | 集成测试 |
| 质量门禁指标达标 | 自动化测试 |

---

**设计版本**: v1
**创建日期**: 2026-02-05
**状态**: DRAFT
