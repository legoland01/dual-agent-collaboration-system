# Bug报告: session_manager待办显示不从agent_adhoc_todos.yaml读取

**Bug ID**: BUG-20260215-015
**严重程度**: P1
**状态**: Open
**发现时间**: 2026-02-15
**发现者**: Agent 1

---

## 问题描述

用户通过`todowrite`或手动编辑创建的TODO不会显示在`oc-collab status`的待办事项中。原因是session_manager使用的是静态的TODO_MAP，而非读取`agent_adhoc_todos.yaml`。

## 复现步骤

1. 执行`oc-collab todowrite "测试TODO" --agent 1`
2. 查看YAML：`state/agent_adhoc_todos.yaml`中已创建TODO
3. 执行`oc-collab status`
4. 观察：待办事项显示"暂无待办事项"

## 根因分析

代码位置：`src/core/session_manager.py` 第147-165行

```python
def get_todo_items(self) -> str:
    # ...
    from .auto_engine import TodoCommandExecutor
    executor = TodoCommandExecutor(self.project_path)
    todo_list = executor.get_todo_list()  # 读的是静态TODO_MAP，不是YAML文件
```

**问题**：
- `TodoCommandExecutor.get_todo_list()`使用静态phase→todo映射
- 不读取`state/agent_adhoc_todos.yaml`
- 导致手动创建的TODO无法在status中显示

## 期望行为

- `oc-collab status`应显示`agent_adhoc_todos.yaml`中的所有pending TODO
- 或者提供单独的命令查看

## 修复建议

方案1：修改`get_todo_items()`直接读取YAML
```python
def get_todo_items(self) -> str:
    from .todo_sync_manager import TodoSyncManager
    sync = TodoSyncManager()
    todos = sync.get_todos_by_agent(agent_id=self.current_agent, status="pending")
    # 显示todos
```

方案2：新增`oc-collab todo list`命令显示adhoc todos

---

**状态**: Open
**优先级**: P1
