# 详细设计：变更载体明确化

**设计文档ID**: DETAIL-2026-02-M2
**版本**: v1
**日期**: 2026-02-05
**作者**: Agent 2 (开发负责人)
**状态**: DRAFT

---

## 1. 概述

### 1.1 功能描述

明确 PRD 与 RFC 的角色分工，检测变更流程合规性，检测冲突。

### 1.2 相关需求

- FR-CHANGE-CLARITY-001

---

## 2. 技术设计

### 2.1 变更载体规则

| 场景 | 变更载体 | 是否需要签署流程 |
|------|----------|------------------|
| 需求新增/重大变更 | PRD | ✅ |
| 需求澄清/技术方案 | RFC | ✅ |
| PRD 已包含 RFC 内容 | PRD | ✅ PRD 评审即有效 |

### 2.2 合规检测规则

```python
CHANGE_COMPLIANCE_RULES = {
    "prd_change_requires_signoff": True,
    "rfc_optional_when_prd_complete": True,
    "conflict_detection": True,
}
```

---

## 3. 实现方案

### 3.1 核心类设计

```python
class ChangeComplianceChecker:
    """变更合规检查器"""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.state_manager = StateManager(project_path)

    def check_prd_compliance(self, prd_file: str) -> ComplianceResult:
        """检查 PRD 合规性"""
        pass

    def check_rfc_compliance(self, rfc_file: str) -> ComplianceResult:
        """检查 RFC 合规性"""
        pass

    def detect_conflicts(self, prd_file: str, rfc_file: str) -> List[Conflict]:
        """检测冲突"""
        pass
```

### 3.2 冲突检测

```python
class ConflictType(Enum):
    CONTENT_CONFLICT = "内容冲突"
    STATUS_CONFLICT = "状态冲突"
    VERSION_CONFLICT = "版本冲突"

def detect_content_conflict(prd_content: str, rfc_content: str) -> List[str]:
    """检测内容冲突"""
    conflicts = []
    prd_keywords = extract_keywords(prd_content)
    rfc_keywords = extract_keywords(rfc_content)

    for kw in prd_keywords:
        if kw in rfc_keywords:
            # 检查描述是否一致
            if get_description(prd_content, kw) != get_description(rfc_content, kw):
                conflicts.append(f"关键词 '{kw}' 描述不一致")

    return conflicts
```

### 3.3 CLI 命令

```bash
# 检查 PRD 合规性
oc-collab compliance check --file requirements_v2.2.1.md

# 检查 RFC 合规性
oc-collab compliance check --file RFC-2026-02-001.md

# 检测冲突
oc-collab compliance detect --prd requirements_v2.2.1.md --rfc RFC-2026-02-001.md

# 查看变更载体规则
oc-collab compliance rules
```

### 3.4 违规处理

```python
class ViolationAction(Enum):
    WARN = "提醒"
    BLOCK = "阻止"
    ALLOW = "允许"

def handle_violation(violation_type: str, context: dict) -> ViolationAction:
    """处理流程违规"""
    if violation_type == "UNSIGNED_PRD":
        return ViolationAction.WARN  # 提醒 PRD 未签署，需人工确认
    elif violation_type == "DEV_BEFORE_SIGNOFF":
        return ViolationAction.WARN  # 提醒开发前需签署
    elif violation_type == "SKIP_REVIEW":
        return ViolationAction.WARN  # 提醒需评审
```

**错误消息示例**:
```
⚠️ 警告：PRD 尚未签署
当前版本: v2.2.1
建议：请确认是否继续开发
操作: (c) 继续 / (q) 取消
```

---

## 4. 测试用例

### 4.1 合规测试

```python
def test_prd_requires_signoff():
    """测试 PRD 必须签署"""
    checker = ChangeComplianceChecker(project_path)
    result = checker.check_prd_compliance("requirements_unsigned.md")
    assert result.violated is True
    assert "PRD 必须签署" in result.message

def test_rfc_optional_when_prd_complete():
    """测试 PRD 完整时 RFC 可选"""
    checker = ChangeComplianceChecker(project_path)
    result = checker.check_rfc_compliance("rfc.md")
    assert result.warning is True
    assert "PRD 已包含" in result.message
```

---

## 5. 验收标准

| 标准 | 验证方式 |
|------|----------|
| PRD 合规检测 | CLI 测试 |
| RFC 合规检测 | CLI 测试 |
| 冲突检测准确 | 集成测试 |
| 错误消息清晰 | 代码审查 |

---

**设计版本**: v1
**创建日期**: 2026-02-05
**状态**: DRAFT
