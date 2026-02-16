# BUG报告：todowrite创建TODO时编号规则不清晰

**Bug ID**: BUG-20260215-018
**严重程度**: P0
**状态**: open
**发现时间**: 2026-02-15
**发现者**: Agent1

---

## 问题描述

Agent1使用todowrite创建TODO时，传递了错误的 `--agent` 参数，导致生成了错误的编号格式。

**错误操作**：
```bash
todowrite --content "开始v2.3.0开发阶段" --agent 2
```
结果生成了 `TODO-2-381`（应为 `TODO-1-376`）

**预期操作**：
```bash
todowrite --content "开始v2.3.0开发阶段"
```
工具自动识别当前Agent（Agent1），自动生成 `TODO-1-376`

---

## 5-Why 根因分析

### Why 1: 为什么创建了TODO-2-381而不是TODO-1-376？
- 因为传了 `--agent 2` 参数

### Why 2: 为什么传了 --agent 2？
- 以为 `--agent` 是指定TODO分配给谁（to_agent）
- 实际上 `--agent` 是告诉工具"我是哪个Agent"（用于生成编号）

### Why 3: 为什么理解错误？
- 没有仔细阅读工具的帮助文档
- 查了skill但没有对照工具实际行为验证
- skill描述与工具实际行为有理解偏差

### Why 4: 为什么没有验证工具行为？
- 过于自信
- 没有建立"先测试再正式使用"的习惯

### Why 5: 根本原因是什么？
**两个层面的问题**：

1. **语义歧义**: `--agent` 参数的语义不清晰
   - 意图：让工具知道"当前操作者是谁"用于生成编号
   - 实际：容易被误解为"把TODO分配给谁"

2. **缺少验证**: 工具没有验证传入的 `--agent` 是否与当前Agent匹配
   - Agent1运行时可以传 `--agent 2`
   - 工具接受了，但这是错误操作

---

## 问题分析

### 工具当前行为（代码验证）

`src/cli/enhanced_commands.py` 第131-142行：
```python
current_agent_id = None
if agent:
    current_agent_id = int(agent)
else:
    try:
        context = ContextManager().load_context()
        if context.agent:
            current_agent_id = int(context.agent.replace("agent", ""))
    except Exception:
        pass
```

- 如果传了 `--agent`，直接使用传入值
- 如果没传，自动从Context获取

### 问题所在

1. **参数语义不清**: `--agent` 容易被误解
2. **无验证机制**: 不检查传入的agent是否与当前Context一致
3. **skill与实现脱节**: skill写了规则，但工具实现允许绕过

---

## 修复方案

### 方案A：强制自动获取（推荐）
**移除 `--agent` 参数**，工具完全自动从Context获取当前Agent

- 优点：彻底解决人为错误
- 改动：删除enhanced_commands.py第57行的 `--agent` 参数

### 方案B：验证一致性
**保留参数但增加验证**，检查传入agent与Context是否一致

- 如果传入 `--agent 2` 但Context是 `agent1`，报错
- 优点：保留灵活性
- 改动：在todowrite_command中添加一致性检查

### 方案C：语义重命名
**重命名参数** `--agent` → `--as-agent`

- 明确表示"以xx身份操作"而非"分配给xx"
- 配合方案B使用

---

## 影响范围

- 所有Agent创建TODO时都可能犯同样错误
- 当前v2.2.x所有版本

## 相关文档

- skill: `oc_collab_todo_dependency_check` 第9.1节
- 代码: `src/cli/enhanced_commands.py`, `src/core/todo_sync_manager.py`

---

**创建时间**: 2026-02-15
**更新时间**: 2026-02-15
**状态**: open
**发现时间**: 2026-02-15
**发现者**: Agent1

---

## 问题描述

Agent1使用todowrite创建TODO时，手动指定了错误的编号格式。

**错误操作**：
- Agent1创建了一个TODO，编号为 `TODO-2-381`（应为 `TODO-1-376`）

**根本原因**：
1. 没有先查skill确认编号规则
2. 手动指定了编号，而不是让工具自动生成

## 问题分析

### 预期行为
- Agent1运行 `todowrite --content "xxx"`
- 工具自动识别当前Agent（Agent1）
- 自动生成正确编号 `TODO-1-376`

### 实际行为
- Agent1手动传入了 `--id TODO-2-381`
- 工具没有验证编号格式是否匹配当前Agent

## 复现步骤

1. Agent1执行：`todowrite --id TODO-2-381 --content "xxx"`
2. 工具接受了错误的编号格式
3. 没有报错或自动纠正

## 期望修复

1. **方案A**：todowrite自动获取当前Agent ID，忽略用户传入的 `--id` 参数
2. **方案B**：todowrite验证用户传入的 `--id` 是否与当前Agent匹配，不匹配则报错或自动纠正
3. **方案C**：移除 `--id` 参数，强制用户使用自动编号

## 影响范围

- 所有Agent创建TODO时都可能犯同样错误
- 可能导致编号混乱

## 相关文档

- skill: `oc_collab_todo_dependency_check` 第9.1节明确写明了编号格式

---

**创建时间**: 2026-02-15
**状态**: open
