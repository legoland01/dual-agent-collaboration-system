# Bug 报告：todowrite 命令未正确写入文件

**Bug ID**: BUG-20260210-002
**严重程度**: P0
**状态**: 待修复
**发现人**: Agent 1 / Agent 2
**发现日期**: 2026-02-10

---

## Bug描述

### 问题表现

执行 `oc-collab todowrite` 命令创建TODO后，TODO未保存到 `state/agent_adhoc_todos.yaml` 文件中。

### 测试证据

```bash
# 创建TODO
$ oc-collab todowrite --content "测试任务" --agent 1 --priority high
TODO创建成功

# 检查文件
$ grep "测试任务" state/agent_adhoc_todos.yaml
# 无结果 - TODO未写入文件

# 验证文件内容
$ cat state/agent_adhoc_todos.yaml
todos:
  - id: "TODO-241"
    # ... 只有旧TODO
# TODO-246 不存在
```

### 影响范围

| 影响 | 严重程度 |
|------|----------|
| Agent 无法通过 CLI 创建 TODO | P0 |
| 协作流程阻塞 | P0 |
| 必须手动编辑 TODO 文件 | 低效 |

---

## 复现步骤

1. 执行 `oc-collab todowrite --content "xxx" --agent 1 --priority high`
2. 预期：TODO 应写入 `state/agent_adhoc_todos.yaml`
3. 实际：TODO 未写入文件

---

## 根因分析

### 初步判断

`todowrite` 命令调用成功，但 `sync_with_rollback` 或文件写入逻辑失败。

### 待排查

1. `src/cli/todo_commands.py` 中的 todowrite 命令实现
2. `src/core/todo_sync_manager.py` 中的文件写入逻辑
3. 文件路径权限问题

---

## 临时解决方案

手动编辑 `state/agent_adhoc_todos.yaml` 文件：

```yaml
todos:
  - id: "TODO-XXX"
    content: "任务描述"
    from: "agent1"
    to: "agent2"
    phase: "design"
    priority: "P0"
    status: "pending"
    created_at: "2026-02-10T00:00:00"
```

---

## 后续行动

| 行动 | 执行人 | 状态 |
|------|--------|------|
| 排查 todowrite 文件写入逻辑 | Agent 2 | 待处理 |
| 修复文件写入BUG | Agent 2 | 待处理 |
| 验证修复 | Agent 1 | 待处理 |

---

## 相关文档

- `src/cli/todo_commands.py` - TODO命令实现
- `src/core/todo_sync_manager.py` - TODO同步管理器
- `state/agent_adhoc_todos.yaml` - TODO存储文件
- `docs/00-memos/BUG-20260209-002_todowrite创建TODO失败.md` - 历史BUG

---

**创建人**: Agent 2
**日期**: 2026-02-10
**状态**: 待修复
