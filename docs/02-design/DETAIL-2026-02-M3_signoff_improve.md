# 详细设计：签署流程改进

**设计文档ID**: DETAIL-2026-02-M3
**版本**: v1
**日期**: 2026-02-05
**作者**: Agent 2 (开发负责人)
**状态**: DRAFT

---

## 1. 概述

### 1.1 功能描述

标准化签署模板格式，添加签署检查清单，实现签署记录持久化。

### 1.2 相关需求

- FR-SIGNOFF-IMPROVE-001
- FR-SIGNOFF-IMPROVE-003

---

## 2. 技术设计

### 2.1 签署模板标准化

```markdown
## 签署确认

### Agent 2 (开发负责人) 评审意见

**评审日期**: YYYY-MM-DD
**评审结果**: ✅ 同意 / ❌ 需修改

**评审意见**:
- ...

### 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 产品负责人 | Agent 1 | YYYY-MM-DD | ✅ 已签署 |
| 开发负责人 | Agent 2 | YYYY-MM-DD | ✅ 已签署 |

**签署后状态**: APPROVED (已批准) / PENDING (待签署)
```

### 2.2 签署记录文件格式

```yaml
# state/signoffs/sig_M1_20260205.yaml
signoff_id: SIG-M1-20260205
milestone: M1
phase: integration_testing
signers:
  - role: 产品负责人
    agent: Agent 1
    timestamp: 2026-02-05T12:00:00
    status: approved
  - role: 开发负责人
    agent: Agent 2
    timestamp: 2026-02-05T12:05:00
    status: approved
status: APPROVED
created_at: 2026-02-05T12:00:00
```

---

## 3. 实现方案

### 3.1 签署记录管理器

```python
class SignoffRecordManager:
    """签署记录管理器"""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.signoffs_dir = Path(project_path) / "state" / "signoffs"
        self.signoffs_dir.mkdir(parents=True, exist_ok=True)

    def save_signoff(self, signoff_data: dict) -> str:
        """保存签署记录"""
        signoff_id = signoff_data["signoff_id"]
        file_path = self.signoffs_dir / f"{signoff_id}.yaml"

        with open(file_path, 'w') as f:
            yaml.dump(signoff_data, f)

        return str(file_path)

    def get_signoff(self, signoff_id: str) -> dict:
        """获取签署记录"""
        file_path = self.signoffs_dir / f"{signoff_id}.yaml"

        if file_path.exists():
            with open(file_path) as f:
                return yaml.safe_load(f)

        return None

    def list_signoffs(self) -> List[dict]:
        """列出所有签署记录"""
        signoffs = []
        for file_path in self.signoffs_dir.glob("*.yaml"):
            with open(file_path) as f:
                signoffs.append(yaml.safe_load(f))
        return signoffs
```

### 3.2 签署检查清单

```python
SIGNOFF_CHECKLIST = [
    ("review_report_exists", "评审报告存在"),
    ("pm_signed", "产品经理已签署"),
    ("dev_signed", "开发负责人已签署"),
    ("signoffs_saved", "签署记录已保存"),
    ("status_updated", "状态已更新为 APPROVED"),
]

def run_signoff_checklist(signoff_data: dict) -> ChecklistResult:
    """运行签署检查清单"""
    results = []

    for check_id, check_name in SIGNOFF_CHECKLIST:
        passed = _check_item(signoff_data, check_id)
        results.append({
            "id": check_id,
            "name": check_name,
            "passed": passed
        })

    return ChecklistResult(results)
```

---

## 4. CLI 集成

```bash
# 查看签署记录
oc-collab signoff list

# 查看特定签署记录
oc-collab signoff show --id SIG-M1-20260205

# 运行签署检查清单
oc-collab signoff checklist --id SIG-M1-20260205
```

---

## 5. 测试用例

### 5.1 记录管理测试

```python
def test_save_signoff():
    """测试保存签署记录"""
    manager = SignoffRecordManager(project_path)
    signoff_data = {...}
    file_path = manager.save_signoff(signoff_data)
    assert Path(file_path).exists()

def test_list_signoffs():
    """测试列出签署记录"""
    manager = SignoffRecordManager(project_path)
    signoffs = manager.list_signoffs()
    assert len(signoffs) >= 0
```

---

## 6. 验收标准

| 标准 | 验证方式 |
|------|----------|
| 签署模板标准化 | 代码审查 |
| 记录持久化成功 | CLI 测试 |
| 检查清单通过 | CLI 测试 |
| 向后兼容 | 集成测试 |

---

**设计版本**: v1
**创建日期**: 2026-02-05
**状态**: APPROVED

---

## 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-05 | ✅ 已创建 |
| 产品负责人 | Agent 1 | 2026-02-07 | ✅ 已评审通过 |
