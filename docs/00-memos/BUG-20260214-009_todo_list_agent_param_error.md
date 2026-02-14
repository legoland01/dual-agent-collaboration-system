# BUG-20260214-009: oc-collab todo list --agent 参数处理错误

**发现日期**: 2026-02-14  
**发现人**: Agent 1  
**严重度**: P1  
**状态**: OPEN  
**复现版本**: v2.2.10

---

## 问题描述

执行 `oc-collab todo list --agent 2` 命令时，报错：

```
❌ 获取TODO列表失败: local variable 'agent_id' referenced before assignment
```

---

## 复现步骤

```bash
oc-collab todo list --agent 2
```

---

## 根因分析

**文件**: `src/cli/todo_commands.py`  
**行号**: 74

```python
# 问题代码
else:
    todos = queue_manager.get_all(agent_id if agent else None)
    #                         ^^^^^^^^
    # 问题: agent_id 在 else 分支中未定义
```

**原因**：
- 在 `if unread:` 分支中定义了 `agent_id = f"agent{agent}" if agent else None`
- 但在 `else:` 分支中直接使用了 `agent_id`，而没有重新定义
- 当用户执行 `--agent 2 --unread` 时不会报错（因为走 if 分支）
- 但执行 `--agent 2` 不带 `--unread` 时会报错（因为走 else 分支，`agent_id` 未定义）

---

## 影响范围

| 场景 | 命令 | 结果 |
|------|------|------|
| 查看所有TODO | `oc-collab todo list` | ✅ 正常 |
| 查看未读 | `oc-collab todo list --unread` | ✅ 正常 |
| 查看Agent2的未读 | `oc-collab todo list --unread --agent 2` | ✅ 正常 |
| 查看Agent2的所有TODO | `oc-collab todo list --agent 2` | ❌ 报错 |
| 查看Agent1的所有TODO | `oc-collab todo list --agent 1` | ❌ 报错 |

---

## 修复建议

**文件**: `src/cli/todo_commands.py`  
**行号**: 73-74

```python
# 修改前
else:
    todos = queue_manager.get_all(agent_id if agent else None)

# 修改后
else:
    agent_id = f"agent{agent}" if agent else None
    todos = queue_manager.get_all(agent_id)
```

---

## 验收标准

- [ ] `oc-collab todo list --agent 2` 正常显示Agent2的TODO
- [ ] `oc-collab todo list --agent 1` 正常显示Agent1的TODO
- [ ] `oc-collab todo list --unread --agent 2` 继续正常

---

## 关联

- **发现场景**: v2.2.10验收测试 (TEST_REPORT_v2.2.10_acceptance.md)
- **测试文件**: `src/cli/todo_commands.py`

---

**发现人**: Agent 1  
**日期**: 2026-02-14  
**状态**: OPEN
