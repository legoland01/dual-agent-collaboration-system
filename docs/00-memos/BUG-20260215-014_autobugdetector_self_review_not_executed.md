# Bug报告: AutoBugDetector自检未执行

**Bug ID**: BUG-20260215-014
**严重程度**: P0
**状态**: Open
**发现时间**: 2026-02-15
**发现者**: Agent 1

---

## 问题描述

AutoBugDetector自检功能集成到todowrite命令后，当未指定`--agent`参数且无`.context.yaml`时，agent_id为None，导致自检代码不执行。

## 复现步骤

1. 无`.context.yaml`文件
2. 执行`oc-collab todowrite "测试任务" --status completed`
3. 观察：自检未触发，无Bug报告生成

## 根因分析

代码位置：`src/cli/enhanced_commands.py` 第162行

```python
if agent_id:  # 当agent_id=None时，条件不满足
    detector = AutoBugDetector()
    bugs = detector.self_review(todo.id, agent_id)
    # 自检代码不会执行
```

**问题**：
- 当`agent_id=None`时，`if agent_id:`为False
- 自检代码被跳过
- 应该从state获取当前活跃Agent作为默认值

## 期望行为

- 无显式指定时，应从`state_manager.get_active_agent()`获取默认Agent
- 或者至少记录警告日志

## 修复建议

```python
# 修复方案
if agent_id is None:
    from ..core.state_manager import StateManager
    state_manager = StateManager(project_path)
    active = state_manager.get_active_agent()
    agent_id = int(active.replace("agent", ""))

if agent_id:
    # 自检代码
```

---

**状态**: Open
**优先级**: P0
