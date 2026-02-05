# BUGFIX 需求：session_start 功能实现

**Bug ID**: BUG-20260203-001
**严重程度**: P0
**状态**: 待实现
**需求版本**: v1
**创建日期**: 2026-02-05

---

## 1. 背景

在 v2.2.0 需求文档（requirements_v2.2.0.md）中，有"周期性回顾提醒"功能（FR-MEMORY-003），但未被实现。Agent 在新会话开始时不知道 oc-collab 的存在，不知道自己的角色和职责。

详见 MEMO-2026-02-004。

---

## 2. 需求描述

### 2.1 功能概述

在 Agent 切换或新会话开始时，系统自动显示欢迎信息和上下文引导。

### 2.2 触发条件

| 触发场景 | 触发方式 |
|----------|----------|
| Agent 切换 | `oc-collab switch <agent_id>` |
| 查看状态 | `oc-collab status` |
| 会话开始 | 新会话首次执行任何命令 |

### 2.3 输出格式

```
=== Agent {agent_id} ({agent_role}) ===

当前项目: {project_name}
当前阶段: {current_phase}
当前里程碑: {current_milestone}

你的职责:
{responsibilities}

待办事项:
{todo_items}

上次会话遗留:
{pending_issues}

常用命令:
{common_commands}
```

### 2.4 数据来源

| 数据项 | 来源 |
|--------|------|
| agent_id | state/project_state.yaml |
| agent_role | state/project_state.yaml |
| project_name | state/project_state.yaml |
| current_phase | state/project_state.yaml |
| current_milestone | state/project_state.yaml |
| responsibilities | docs/00-memos/AGENT_ROLES.md |
| todo_items | state/todo.yaml 或 oc-collab todo |
| pending_issues | state/memory/pending.yaml |
| common_commands | 硬编码或配置 |

---

## 3. 验收标准

| 验证项 | 验收条件 | 优先级 |
|--------|----------|--------|
| Agent 切换后显示欢迎信息 | `oc-collab switch 2` 输出包含 Agent 信息 | P0 |
| 显示当前 Agent 职责 | 输出包含职责说明 | P0 |
| 显示待办事项 | 输出包含待办列表 | P0 |
| 显示上次遗留问题 | 输出包含遗留问题 | P1 |
| 状态命令集成 | `oc-collab status` 自动显示欢迎信息 | P1 |
| 配置可定制 | 欢迎信息可配置开关 | P2 |

---

## 4. 约束条件

1. 兼容现有 `oc-collab status` 命令
2. 不破坏现有功能
3. 性能影响最小化（< 100ms）
4. 优雅降级（配置文件缺失时显示基础信息）

---

## 5. 相关文档

| 文档 | 说明 |
|------|------|
| MEMO-2026-02-004 | 问题分析与解决方案 |
| state/project_state.yaml | 项目状态配置 |
