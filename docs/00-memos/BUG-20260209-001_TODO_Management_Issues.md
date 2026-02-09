# Bug 报告：TODO管理问题

**Bug ID**: BUG-20260209-001
**严重程度**: P1
**状态**: 待修复
**发现人**: Agent 1
**发现日期**: 2026-02-09

---

## Bug描述

### 问题1：无必要地增加大量TODO

**表现形式**：
- Agent 1 创建了 TODO-072~076（5个开发TODO）
- 每个功能单独一个TODO
- 但这应该是Agent 2自己的任务分解工作

**正确做法**：
- 应该只创建一个开发TODO（如TODO-077）
- 让Agent 2自己分解任务

### 问题2：覆盖掉现存的TODO

**表现形式**：
- 原来存在 TODO-072: 测试todowrite持久化
- Agent 1 创建新TODO时没有先检查
- 导致生成了重复的TODO-072，内容被覆盖

**影响**：
- 原始TODO-072被覆盖
- 需要回滚和修复
- 增加了维护成本

---

## 根因分析

### 问题1：角色边界不清

**原因**：
- Agent 1 替Agent 2做了任务分解
- 但任务分解应该是开发负责人的职责

**应该的做法**：
```
Agent 1: 创建"v2.2.5开发"TODO
    │
Agent 2: 收到TODO后自己分解为子任务
    │
Agent 2: 逐个完成并更新状态
```

### 问题2：创建TODO前未检查

**原因**：
- Agent 1 创建TODO前没有执行检查步骤
- 没有先查看现有的TODO列表

**应该的做法**：
```
创建TODO前：
1. 先查看现有TODO：oc-collab todo
2. 检查是否有重复
3. 再决定是否创建新TODO
```

---

## 解决方案

### 方案1：Skill中增加检查规则

**在 requirements_guide 中增加**：
```
## 创建TODO检查规则

### 创建前检查

1. 先查看现有TODO
   oc-collab todo

2. 检查是否有重复
   - 同一个人
   - 类似内容
   - 相关联的任务

3. 再决定是否创建新TODO

### 禁止行为

❌ 不要替其他Agent分解任务
❌ 不要创建大量重复TODO
❌ 不要覆盖已有的TODO
```

### 方案2：增加创建TODO的强制步骤

**在协作规范中增加**：
```
## TODO创建流程

### 步骤1: 检查
   oc-collab todo

### 步骤2: 确认
   确认没有重复后再创建

### 步骤3: 创建
   oc-collab todowrite --content "..." --priority P0 --agent X

### 步骤4: 验证
   再次执行 oc-collab todo 确认TODO已创建
```

---

## 影响范围

| 影响 | 严重程度 |
|------|----------|
| TODO列表混乱 | 中 |
| 任务追踪困难 | 中 |
| Agent协作效率降低 | 低 |

---

## 后续行动

| 行动 | 执行人 | 状态 |
|------|--------|------|
| 在Skill中增加TODO检查规则 | Agent 1 | 待处理 |
| 更新协作规范 | Agent 1 | 待处理 |
| 清理重复TODO | Agent 1 | 已完成 |

---

## 相关文档

- `state/agent_adhoc_todos.yaml` - TODO文件
- `skills/oc_collab_requirements_guide` - 需求指南
- `skills/oc_collab_collaboration_guide` - 协作指南

---

**创建人**: Agent 1
**日期**: 2026-02-09
**状态**: 待修复
