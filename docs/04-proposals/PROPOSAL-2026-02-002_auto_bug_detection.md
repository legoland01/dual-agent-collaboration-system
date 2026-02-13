# Proposal: oc-collab Agent自动Bug报告机制

**提案人**: Agent 1  
**日期**: 2026-02-13  
**目标版本**: v2.2.8 或 v2.2.9  
**状态**: 待评审

---

## 1. 问题背景

### 1.1 当前Bug报告模式

| 模式 | 说明 | 问题 |
|------|------|------|
| 被动报告 | 用户发现问题后指令Agent报告 | 滞后、依赖外部 |
| 手动报告 | Agent发现问题后手动创建Bug报告 | 依赖Agent自觉 |
| 意识驱动 | Agent"应该"主动发现问题 | 不可靠 |

### 1.2 核心问题

**Agent无法自动发现问题的原因**：

| 原因 | 说明 |
|------|------|
| 无监控机制 | Agent不持续监控系统状态 |
| 无异常检测 | Agent不知道什么是"异常" |
| 无主动意识 | Agent只在被指令时行动 |

### 1.3 用户期望

> "难道不是每次你遇到oc-collab的问题就首先应该报一个bug然后按照标准流程去解决它吗？"

**期望行为**：
- 遇到问题 → 立即报告Bug
- Bug报告 → 调查分析 → 修复/指派
- 而不是忽略问题或等待指令

---

## 2. 解决方案

### 2.1 核心思路

让Agent在**关键操作后自动触发Bug检查**，而不是依赖"主动意识"。

```
操作完成 → 自动检查 → 异常发现 → 自动报告Bug
```

### 2.2 方案：自动化Bug检测工作流

#### 2.2.1 触发机制

| 触发点 | 检查项 | 预期行为 |
|--------|--------|----------|
| TODO完成时 | 文档状态是否更新 | 未更新 → 报告Bug |
| 评审完成时 | 签署是否完成 | 未签署 → 报告Bug |
| 文件编辑后 | 格式是否正确 | 格式错误 → 报告Bug |
| 命令执行后 | 返回值是否符合预期 | 返回值异常 → 报告Bug |
| Skill执行后 | 产出是否符合预期 | 产出缺失 → 报告Bug |

#### 2.2.2 检查规则

```python
# 伪代码：自动Bug检测逻辑

class AutoBugDetector:
    """自动Bug检测器"""

    def check_after_todo_completion(self, todo):
        """TODO完成后检查"""
        # 检查1: 关联文档状态是否更新
        if todo.requires_doc_update:
            doc = get_doc(todo.requirements_doc)
            if doc.status != todo.expected_doc_status:
                report_bug(
                    type="DOCUMENT_STATUS_NOT_UPDATED",
                    description=f"TODO-{todo.id}完成但文档未更新",
                    related_todo=todo.id,
                    expected_status=todo.expected_doc_status,
                    actual_status=doc.status
                )

        # 检查2: 签署是否完成
        if todo.requires_signoff:
            if not todo.signoff_completed:
                report_bug(
                    type="SIGNOFF_INCOMPLETE",
                    description=f"TODO-{todo.id}要求签署但未完成",
                    related_todo=todo.id
                )

    def check_after_file_edit(self, file_path, operation):
        """文件编辑后检查"""
        # 检查1: 文件格式是否正确
        if is_yaml_file(file_path):
            if not validate_yaml_syntax(file_path):
                report_bug(
                    type="YAML_FORMAT_ERROR",
                    description=f"文件格式错误: {file_path}",
                    file_path=file_path
                )

        # 检查2: 必需字段是否存在
        if is_todo_file(file_path):
            if not validate_required_fields(file_path):
                report_bug(
                    type="TODO_FIELD_MISSING",
                    description=f"TODO文件缺少必需字段: {file_path}",
                    file_path=file_path
                )
```

#### 2.2.3 Bug报告模板

自动生成的Bug报告应包含：

```markdown
# Auto-Bug Report

**Bug编号**: AUTO-[timestamp]
**发现日期**: [datetime]
**发现者**: Auto-Bug Detector
**触发点**: [TODO完成/文件编辑/命令执行]
**状态**: AUTO_GENERATED

---

## 1. Bug描述

[自动描述问题]

## 2. 上下文信息

| 字段 | 值 |
|------|-----|
| 触发操作 | [操作类型] |
| 关联文件 | [文件路径] |
| 关联TODO | [TODO编号] |
| 预期行为 | [应该怎样] |
| 实际行为 | [实际怎样] |

## 3. 建议处理方式

| 处理方式 | 说明 |
|----------|------|
| [ ] 自动修复 | [是否可自动修复] |
| [ ] 人工修复 | 需要Agent处理 |
| [ ] 指派修复 | 指派给特定Agent |

---

**系统生成**: 无需人工创建Bug报告
**处理建议**: 直接进入Bug调查阶段
```

### 2.3 方案：关键操作埋点

在oc-collab关键操作处埋点，自动检测异常：

| 操作 | 埋点 | 检测异常 |
|------|------|----------|
| todowrite | 写入前/写入后 | 写入失败、格式错误 |
| todoread | 读取后 | 解析失败、字段缺失 |
| edit | 编辑后 | 格式错误、匹配失败 |
| signoff | 签署后 | 状态未更新、签署不完整 |
| skill search | 搜索后 | 无结果（可能不是异常） |

### 2.4 方案：创建AutoBugDetector Skill

创建一个专门负责自动Bug检测的Skill：

```yaml
# skills/oc_collab_auto_bug_detector/skill.json
{
  "id": "oc_collab_auto_bug_detector",
  "name": "OC-Collab 自动Bug检测",
  "version": "1.0",
  "triggers": [
    {
      "condition": "todo_completed",
      "priority": "high",
      "description": "TODO完成后自动触发Bug检测"
    },
    {
      "condition": "file_edited",
      "priority": "high",
      "description": "文件编辑后自动触发Bug检测"
    },
    {
      "condition": "command_executed",
      "priority": "medium",
      "description": "命令执行后自动触发Bug检测"
    }
  ]
}
```

---

## 3. 实现方案

### 3.1 方案A：轻量级（推荐起步）

**核心**：在todowrite工具中增加后置检查

```python
# src/utils/todo_bug_checker.py

class TodoBugChecker:
    """TODO相关Bug自动检测"""

    def check_after_create(self, todo_id):
        """创建TODO后检查"""
        # 检查1: 是否有重复ID
        if self._is_duplicate_id(todo_id):
            self._report_bug("DUPLICATE_TODO_ID", todo_id)

        # 检查2: 必需字段是否完整
        if not self._has_required_fields(todo_id):
            self._report_bug("TODO_MISSING_FIELDS", todo_id)

    def check_after_complete(self, todo_id):
        """完成TODO后检查"""
        todo = self._get_todo(todo_id)

        # 检查1: 关联文档状态
        if todo.requires_doc_approval:
            doc = self._get_doc(todo.requirements_doc)
            if doc.status != "APPROVED":
                self._report_bug(
                    "DOC_NOT_APPROVED_AFTER_TODO",
                    todo_id=todo_id,
                    doc_path=todo.requirements_doc,
                    expected_status="APPROVED",
                    actual_status=doc.status
                )

        # 检查2: 签署是否完成
        if todo.requires_signoff:
            if not todo.signoff_completed:
                self._report_bug(
                    "SIGNOFF_MISSING_AFTER_TODO",
                    todo_id=todo_id
                )
```

**优点**：
- 改动小，只需修改todowrite
- 立即可用
- 容易验证

**缺点**：
- 只覆盖TODO相关场景
- 需要持续扩展覆盖其他场景

### 3.2 方案B：完整方案

**核心**：创建独立的AutoBugDetector模块

```
src/
├── core/
│   ├── auto_bug_detector.py    # 自动Bug检测核心
│   ├── bug_checker.py          # 具体检查规则
│   └── bug_reporter.py         # 自动报告生成
│
├── utils/
│   └── bug_check_hooks.py      # 埋点钩子
```

**优点**：
- 覆盖全面
- 可扩展
- 独立测试

**缺点**：
- 改动大
- 需要更多时间

---

## 4. 验收标准

- [ ] TODO完成后自动检查文档状态
- [ ] 文件编辑后自动检查格式
- [ ] Bug自动生成并报告
- [ ] Agent无需手动创建Bug报告
- [ ] Bug报告包含完整上下文信息

---

## 5. 工时估算

| 阶段 | 任务 | 工时 |
|------|------|------|
| 需求分析 | AutoBugDetector需求 | 1h |
| 概要设计 | 模块架构设计 | 2h |
| 详细设计 | 检查规则设计 | 2h |
| 开发 | todowrite后置检查 | 2h |
| 开发 | edit后置检查 | 2h |
| 开发 | 自动报告生成 | 2h |
| 测试 | 单元测试 | 2h |
| **合计** | | **13h** |

---

## 6. 与其他Bug的关联

### 6.1 BUG-20260213-002: 完成工作后未参考Skill

**当前问题**：Agent完成工作后没有自检

**本提案方案**：自动检查代替自觉

| 旧方案 | 新方案 |
|--------|--------|
| "改进自身行为" | 系统自动检查 |
| 依赖Agent自觉 | 强制检查机制 |
| 不可靠 | 可靠 |

### 6.2 BUG-20260213-003: edit工具使用不当

**当前问题**：edit工具使用不当

**本提案方案**：edit后自动验证

| 旧方案 | 新方案 |
|--------|--------|
| "改进工作习惯" | 系统自动验证 |
| 依赖Agent谨慎 | 工具自动校验 |
| 不可靠 | 可靠 |

---

## 7. 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 误报 | 产生大量无效Bug | 精细化检查规则 |
| 性能 | 检测影响命令执行 | 异步执行检测 |
| 复杂度 | 检测逻辑复杂 | 渐进式实现 |

---

## 8. 结论

本提案旨在解决**Agent无法自动发现问题**的根本问题。

**核心思想**：用**系统机制**代替**Agent自觉**

| 维度 | 当前 | 改进后 |
|------|------|--------|
| Bug发现 | 被动/手动 | 自动 |
| 自检机制 | 依赖自觉 | 系统强制 |
| 问题处理 | 等待指令 | 自动报告 |

---

**创建人**: Agent 1  
**日期**: 2026-02-13  
**状态**: 待评审
