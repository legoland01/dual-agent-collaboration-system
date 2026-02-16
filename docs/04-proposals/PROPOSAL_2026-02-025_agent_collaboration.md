# Proposal: Agent协作规范

**提案编号**: PROPOSAL_2026-02-025  
**日期**: 2026-02-16  
**作者**: Consultant (战略规划)  
**状态**: DRAFT

---

## 一、背景

### 1.1 Agent职责定义

| Agent | 核心职责 | 边界 |
|-------|----------|------|
| Agent1 | 需求分析、方案设计、验收 | 不直接改代码 |
| Agent2 | 代码实现、Bug修复、部署 | 不跳过签署 |

### 1.2 当前问题

| 问题 | 说明 |
|------|------|
| 职责模糊 | Agent1有时参与代码实现 |
| 权限越界 | Agent2跳过签署直接部署 |
| 沟通不畅 | TODO描述不清晰 |

---

## 二、协作流程

### 2.1 标准流程

```
┌─────────────┐     TODO      ┌─────────────┐
│  Agent1    │ ───────────→  │  Agent2    │
│ (需求/设计) │               │ (实现/部署) │
└─────────────┘               └─────────────┘
       ↑                           │
       │      签署完成              │ 完成
       │      里程碑推进            │ 标记完成
       │                           ↓
       │                    ┌─────────────┐
       └──────────────────── │  Agent1    │
         验收通过             │ (验收)     │
                            └─────────────┘
```

### 2.2 核心规则

| 规则 | Agent1 | Agent2 |
|------|--------|--------|
| 创建TODO | ✅ | ✅ |
| 改代码 | ❌ | ✅ |
| 部署 | ❌ | ✅ |
| 签署需求 | ✅ | ❌ |
| 签署设计 | ✅ | ✅ |
| 签署开发 | ❌ | ✅ |
| 签署测试 | ✅ | ❌ |
| 验收自己代码 | ❌ | ❌ |

### 2.3 禁止行为

| 禁止行为 | 刚性响应 |
|----------|----------|
| Agent1直接改代码 | R1-阻断 |
| Agent2跳过签署 | R1-阻断 |
| Agent自己验收自己 | R1-阻断 |
| 跳过里程碑 | R1-阻断 |

---

## 三、TODO协作

### 3.1 TODO生命周期

```
Agent1创建 → Agent2确认 → Agent2执行 → Agent1验收 → Agent1关闭
   (draft)   (pending)   (in_progress)  (completed)   (closed)
```

### 3.2 状态流转权限

| 状态 | 可由谁变更 |
|------|------------|
| draft → pending | 创建者 |
| pending → in_progress | target_agent |
| in_progress → completed | target_agent |
| completed → closed | 创建者 |
| * → cancelled | 创建者或PM-Agent |

---

## 四、与刚性框架整合

### 4.1 权限校验

```python
def update_todo_status(todo_id, new_status, actor):
    todo = get_todo(todo_id)
    
    # RF-001: 自验收阻断
    if new_status == 'completed' and actor == todo.created_by:
        raise PermissionError("禁止自验收")
    
    # 权限校验
    if not can_transition(todo.status, new_status, actor):
        raise PermissionError("无权限变更状态")
```

### 4.2 审计记录

| 事件 | 记录内容 |
|------|----------|
| TODO创建 | 创建者、内容、target |
| TODO开始 | 开始时间、接收确认 |
| TODO完成 | 完成时间、证据 |
| 验收 | 验收人、验收结果 |

---

## 五、实施计划

| 版本 | 功能 | 工时 |
|------|------|------|
| v2.2 | 职责定义 | 2h |
| v2.2 | 禁止行为定义 | 2h |
| v2.5 | 权限校验(R1) | 6h |
| v2.5 | 审计记录 | 4h |

---

## 六、关联

| 关联 | 说明 |
|------|------|
| TODO系统 | TODO状态流转 |
| 刚性框架 | 权限强制 |
| 签署流程 | 里程碑签署 |
| PM-Agent | 异常处理 |

---

**提案状态**: DRAFT
