# BUG报告：AutoBugDetector未检测TODO编号违反规则

**BUG编号**：BUG-20260215-002
**发现日期**：2026-02-15
**发现者**：Agent 1
**优先级**：P1
**状态**：open

---

## 问题描述

Agent1发现并创建了BUG-20260215-001（TODO编号生成逻辑不完整），但AutoBugDetector未能自动检测并报告此问题。

## 复现场景

1. Agent1手动编辑 `agent_adhoc_todos.yaml`，创建 TODO-1-014
2. 此操作未触发 AutoBugDetector
3. BUG由Agent1人工发现，非系统自动检测

## 根因分析

### AutoBugDetector当前触发条件

| 触发点 | 检查内容 | 状态 |
|--------|----------|------|
| `todoedit --status completed` | TODO完成时文档状态 | ✅ 已实现 |
| `signoff --phase` | 评审完成时签署状态 | ✅ 已实现 |
| `phase --next` | 阶段推进有效性 | ✅ 已实现 |
| `todowrite` | TODO编号格式规则 | ❌ 未实现 |

### 问题类型判断

**❌ 不是实现问题**：AutoBugDetector代码正确，实现了设计的功能

**⚠️ 是需求未定义清楚**：

1. **需求文档未明确要求**：
   - `PROPOSAL-2026-02-002_auto_bug_detection.md` 中，AutoBugDetector未涵盖"TODO编号验证"
   - `requirements_v2.2.9.md` 中，F-AUTO-005 未定义此场景

2. **v2.2.11新增的Agent独立TODO编号机制**：
   - 需求已明确定义 TODO-1-xxx / TODO-2-xxx 格式
   - 但未同步扩展 AutoBugDetector 的检测范围

## 修复方案

### 方案1：扩展AutoBugDetector需求（推荐）

在 `PROPOSAL-2026-02-002_auto_bug_detection.md` 中增加：

```
【新增检测场景】
- 检测TODO编号格式是否符合 Agent-1-xxx / Agent-2-xxx 规则
- 检测TODO内容是否违反协作规则
```

### 方案2：作为独立功能开发

创建新功能 F-AUTO-006: TODO编号验证器

---

## 关联文档

| 文档 | 说明 |
|------|------|
| `BUG-20260215-001_todo_id_generation.md` | 原始BUG |
| `PROPOSAL-2026-02-002_auto_bug_detection.md` | AutoBugDetector需求 |
| `requirements_v2.2.11.md` | Agent独立TODO编号需求 |

---

**报告人**：Agent 1
**日期**：2026-02-15
**状态**：待处理
