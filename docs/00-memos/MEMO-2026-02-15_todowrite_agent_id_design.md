# 设计决策: todowrite如何获取当前agent_id

## 问题
移除`--agent`参数后，todowrite需要知道当前是哪个agent在调用，以便自动设置`agent_id`。

## 解决方案
从`state/project_state.yaml`文件读取当前活跃agent。

**实现位置**: `src/cli/enhanced_commands.py` 第130-142行

**替换代码**:
```python
current_agent_id = None
# 从state文件获取当前活跃agent
try:
    from ..core.state_manager import StateManager
    from pathlib import Path
    project_path = str(Path.cwd())
    state_manager = StateManager(project_path)
    active_agent = state_manager.get_active_agent()
    if active_agent and active_agent != "unknown":
        if "agent" in active_agent:
            current_agent_id = int(active_agent.replace("agent", ""))
        else:
            current_agent_id = int(active_agent)
except Exception:
    pass
```

## 原理
- `oc-collab switch agent` 命令会调用 `state_manager.set_active_agent()` 修改state文件
- `state_manager.get_active_agent()` 会读取state文件中 `current: true` 的agent
- 这样不同agent切换时会读到不同的值
