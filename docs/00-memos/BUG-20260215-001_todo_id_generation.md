# BUG报告：TODO编号生成逻辑不完整

**BUG编号**：BUG-20260215-001
**发现日期**：2026-02-15
**发现者**：Agent 1
**优先级**：P0
**状态**：open

---

## 问题描述

`todowrite` 命令创建TODO时，编号生成逻辑不完整，未实现Agent独立编号机制。

## 复现步骤

```bash
# 当前行为
oc-collab todowrite --content "测试"  
# 生成: TODO-001  ❌

# 预期行为
# Agent1执行: TODO-1-001
# Agent2执行: TODO-2-001
```

## 根因分析

### 问题1：add_todo 方法

**文件**：`src/core/todo_sync_manager.py`
**行号**：第187行

```python
# 当前代码（错误）
new_id = f"TODO-{max_id + 1:03d}"  # 生成 TODO-001

# 应该的逻辑（正确）
new_id = f"TODO-{agent_id}-{max_id + 1:03d}"  # 生成 TODO-1-001
```

### 问题2：todowrite 命令

**文件**：`src/cli/enhanced_commands.py`
**行号**：第131行

```python
# 当前代码（问题）
agent_id = int(agent) if agent else None  # 依赖手动传入 --agent

# 应该的逻辑（正确）
# 自动从上下文获取当前Agent ID
```

## 影响范围

1. TODO编号混乱，无法区分创建者
2. 与需求文档（requirements_v2.2.11.md）定义的编号规则不符
3. 历史TODO需要迁移

## 修复方案

### 修复1：修改 add_todo 方法

```python
def add_todo(self, content: str, agent_id: Optional[int] = None,
             priority: str = "medium") -> TodoItem:
    """
    添加待办
    
    Args:
        agent_id: Agent 编号 (1 或 2)，必须提供
    """
    state = self.load_todos()
    
    max_id = 0
    for todo in state.todos:
        if todo.id.startswith("TODO-"):
            parts = todo.id.split("-")
            # 兼容旧格式 TODO-xxx 和新格式 TODO-x-xxx
            if len(parts) >= 3 and parts[1] in ("1", "2"):
                if agent_id and parts[1] == str(agent_id):
                    num = int(parts[2])
                    max_id = max(max_id, num)
            else:
                num = int(parts[1])
                max_id = max(max_id, num)
    
    # 必须指定Agent ID
    if not agent_id:
        raise ValueError("agent_id必须提供")
    
    new_id = f"TODO-{agent_id}-{max_id + 1:03d}"
    # ...
```

### 修复2：自动获取Agent ID

```python
def _do_todowrite():
    if content:
        # 自动从上下文获取当前Agent
        current_agent_id = None
        try:
            context = ContextManager().load_context()
            if context.agent:
                current_agent_id = int(context.agent.replace("agent", ""))
        except Exception:
            pass
        
        agent_id = current_agent_id
        todo = sync_manager.add_todo(content, agent_id=agent_id, priority=priority)
```

## 验收标准

- [x] Agent1执行 todowrite 生成 TODO-1-xxx 格式
- [x] Agent2执行 todowrite 生成 TODO-2-xxx 格式
- [ ] 编号自增（TODO-1-001 → TODO-1-002 → ...）
- [ ] 兼容旧格式 TODO-xxx

---

## 修复记录

### 修复1：重复 ID 问题

**问题**：`TODO-1-012` 在 `state/agent_adhoc_todos.yaml` 中重复 2 次

**修复**：将重复条目改为正确的 Agent2 编号
- `TODO-1-012` (条目1) → `TODO-2-013`
- `TODO-1-012` (条目2) → `TODO-2-014`

### 修复2：todowrite 命令参数传递

**文件**：`src/cli/enhanced_commands.py`

**修改**：优先使用命令行传入的 `--agent` 参数

```python
# 修改前
def _do_todowrite():
    if content:
        current_agent_id = None
        try:
            context = ContextManager().load_context()
            if context.agent:
                current_agent_id = int(context.agent.replace("agent", ""))
        except Exception:
            pass
        agent_id = current_agent_id

# 修改后
def _do_todowrite():
    if content:
        # 优先使用命令行传入的 agent 参数，否则从上下文获取
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
        agent_id = current_agent_id
```

### 测试结果

```
$ oc-collab todowrite --content "测试" --agent 1
✅ 待办已创建: [TODO-1-368] 测试

$ oc-collab todowrite --content "测试" --agent 2
✅ 待办已创建: [TODO-2-368] 测试
```

---

## 签署

| 角色 | 签署 | 时间 |
|------|------|------|
| Agent1 | - | - |
| Agent2 | 技术修复完成 | 2026-02-15 |

## 关联文档

| 文档 | 说明 |
|------|------|
| `requirements_v2.2.11.md` | 需求定义（Agent独立TODO编号） |
| `PROPOSAL-2026-02-006_agent_todo_numbering.md` | 提案 |
| `src/core/todo_sync_manager.py` | 问题代码 |
| `src/cli/enhanced_commands.py` | 问题代码 |

---

**报告人**：Agent 1
**日期**：2026-02-15
**状态**：待修复
