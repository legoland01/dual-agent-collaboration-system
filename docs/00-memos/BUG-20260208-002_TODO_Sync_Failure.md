# Bug 报告：TODO任务不同步问题

**Bug ID**: BUG-20260208-002
**严重程度**: P0 - 阻塞
**状态**: 待修复
**发现人**: Agent 1
**发现日期**: 2026-02-08

---

## Bug描述

### 表现形式

| 场景 | 问题 |
|------|------|
| Agent1创建TODO | `todowrite` 返回任务ID，命令执行成功 |
| Agent2查看 | `cat state/agent_adhoc_todos.yaml` 没有新任务 |
| 跨会话 | TODO丢失，Agent2无法看到 |

### 重现场景

```bash
# Agent1 创建TODO
$ todowrite --content "评审 v2.2.4 需求分析报告" --priority P0 --agent 2
✅ 待办已创建: [TODO-060] 评审 v2.2.4 需求分析报告
✓ 已同步到 state/agent_adhoc_todos.yaml

# Agent2 检查（不同步）
$ cat state/agent_adhoc_todos.yaml
# 没有 TODO-060！
```

### 影响范围

| 影响 | 严重程度 |
|------|----------|
| Agent2看不到任务 | P0 - 阻塞协作 |
| TODO追踪失效 | P0 - 流程中断 |
| Compaction前TODO丢失 | P0 - 历史断裂 |

---

## 问题分析

### 现象分类

| 创建方式 | 是否同步到 agent_adhoc_todos.yaml |
|----------|--------------------------------|
| `oc-collab todowrite` | ❓ 待调查 |
| `todowrite` 工具 | ❓ 待调查 |
| 手动编辑 | ✅ 同步 |

### 相关文件

| 文件 | 用途 | 同步状态 |
|------|------|----------|
| `state/agent_adhoc_todos.yaml` | 任务追踪（应该同步） | ❌ 未同步 |
| `state/todo.yaml` | 待办管理（v2.2.3新功能） | ✅ 正常 |
| `src/cli/enhanced_commands.py` | todowrite命令实现 | ❓ 待调查 |
| `tools/todowrite.py` | todowrite工具 | ❓ 待调查 |

### 关键线索

1. **两个TODO文件并存**：`todo.yaml` vs `agent_adhoc_todos.yaml`
2. **工具可能写错文件**：todowrite工具可能写入了`todo.yaml`而非`agent_adhoc_todos.yaml`
3. **CLI命令和工具不一致**：可能使用不同的存储位置

---

## Agent2 调查方向

### 1. todowrite工具调用链

```bash
# 检查工具实现
cat tools/todowrite.py
# 是否正确写入 state/agent_adhoc_todos.yaml ？
```

### 2. CLI命令实现

```bash
# 检查CLI命令
cat src/cli/enhanced_commands.py | grep -A20 "def todowrite"
# 写入哪个文件？
```

### 3. 文件关系

```bash
# 检查两个文件的内容
cat state/todo.yaml
cat state/agent_adhoc_todos.yaml
# 是否应该合并？还是二选一？
```

### 4. 同步机制

```bash
# 检查是否有自动同步逻辑
grep -r "sync" src/cli/enhanced_commands.py
# 检查 todo.yaml 和 agent_adhoc_todos.yaml 的同步逻辑
```

---

## 预期行为

```bash
# Agent1 创建TODO
$ todowrite --content "评审需求分析报告" --priority P0 --agent 2
✅ 待办已创建: [TODO-060] 评审需求分析报告

# Agent2 检查
$ cat state/agent_adhoc_todos.yaml
# 应该看到 TODO-060
```

---

## 临时解决方案（手动）

```bash
# 1. Agent1 手动创建TODO
# 编辑 state/agent_adhoc_todos.yaml

# 2. 或者使用 CLI 命令（如果可用）
oc-collab todowrite --content "评审需求分析报告" --priority P0 --agent 2
```

---

## 根本解决方案（待Agent2调查）

| 方案 | 说明 |
|------|------|
| **方案A** | 统一TODO存储位置，合并两个文件 |
| **方案B** | 修复todowrite工具，正确写入agent_adhoc_todos.yaml |
| **方案C** | 删除冗余，保留一个TODO文件 |

---

## 时间线

| 日期 | 事件 |
|------|------|
| 2026-02-08 | Agent1 发现问题，创建Bug报告 |
| 2026-02-08 | Agent2 待调查 |
| - | Agent2 待修复 |
| - | Agent1 待验证 |

---

## 关联文档

| 文档 | 说明 |
|------|------|
| `skills/oc_collab_collaboration_guide/` | TODO任务管理规范 |
| `src/cli/enhanced_commands.py` | todowrite命令 |
| `tools/todowrite.py` | todowrite工具 |

---

**创建人**: Agent 1
**日期**: 2026-02-08
**状态**: 待修复
