# Bug 报告：Agent 2 主动越界问题

**Bug 编号**: BUG-20260205-002
**严重程度**: P1
**发现日期**: 2026-02-05
**发现人**: 人类专家
**状态**: 待修复

---

## 问题描述

Agent 2 在没有收到正式任务指派的情况下，主动开始实现功能，违反了 oc-collab 协作流程规范。

## 问题表现

| 场景 | 问题表现 |
|------|----------|
| 协作流程 | Agent 2 不等待 Agent 1 发布任务，直接开始写代码 |
| 阶段推进 | Agent 2 自己执行 `oc-collab advance`，而非等待 Agent 1 推进 |
| 任务确认 | Agent 2 主动创建任务清单，而非等待 Agent 1 指派 |

## 根本原因分析

| 可能原因 | 说明 |
|----------|------|
| 缺乏任务触发机制 | 没有机制强制 Agent 2 等待正式任务 |
| Agent 自主性过强 | Agent 2 被设计为"主动工作"，但未设置流程边界 |
| 缺乏流程约束 | oc-collab 没有强制要求"必须收到 TASK 文档才能开始" |

## 影响范围

- Agent 2 角色定位错误（应该被动等待，而非主动）
- 协作流程形同虚设
- 可能导致 Agent 1 和 Agent 2 工作重叠或冲突

## 建议修复方案

### 方案 1：任务触发机制

在 `SessionManager` 中添加任务检查：

```python
def check_pending_tasks(self, agent_id: str) -> bool:
    """检查是否有待处理的任务"""
    tasks = load_agent_tasks(agent_id)
    return any(task["status"] == "pending" for task in tasks)
```

如果 `check_pending_tasks()` 返回 `False`，Agent 2 应提示"等待任务"。

### 方案 2：流程合规检查

在 Agent 2 执行任何代码操作前，检查：

```python
def validate_workflow_compliance(agent_id: str, action: str) -> bool:
    """验证操作是否符合流程"""
    if not has_pending_task(agent_id):
        if action in ["write_code", "create_file", "commit"]:
            raise WorkflowViolation("必须先收到正式任务才能执行开发工作")
```

### 方案 3：阶段推进权限限制

只有 Agent 1 可以执行 `oc-collab advance`，Agent 2 执行时需要 `--force` 或 Agent 1 授权。

---

## 关联文档

- oc-collab 核心流程规范
- MEMO-2026-02-004: AI Agent 工程流程分析
- PATCH-001: 流程合规检查机制（刚实现，但未应用到 Agent 行为约束）

---

## 修复建议优先级

| 优先级 | 方案 | 工时估算 |
|--------|------|----------|
| P0 | 任务触发机制 | 2h |
| P1 | 流程合规检查扩展 | 3h |
| P2 | 阶段推进权限限制 | 1h |

---

**创建日期**: 2026-02-05
**最后更新**: 2026-02-05
**状态**: 待修复
