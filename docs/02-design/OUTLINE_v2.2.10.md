# v2.2.10 概要设计

**版本**: v1
**日期**: 2026-02-14
**状态**: DRAFT
**关联需求**: requirements_v2.2.10_DRAFT.md

---

## 1. 版本概述

### 1.1 核心目标

```
v2.2.9: StateNotifier发送功能 ✅
v2.2.10: StateNotifier完整实现 ⏳
         └── Agent自动感知TODO ← 核心目标
```

### 1.2 功能概览

| 功能模块 | 功能 | 优先级 | 工时 |
|----------|------|--------|------|
| M1 | TodoQueueManager | P0 | 2h |
| M2 | StateNotifier写入队列 | P0 | 1h |
| M3 | Agent启动自检 | P0 | 4h |
| M4 | CLI todo --unread | P2 | 2h |
| M5 | BUG-20260214-001修复 | P0 | 2h |
| M6 | BUG-20260214-002修复 | P1 | 2h |

**总计**: 13h开发 + 5h测试 + 3h缓冲 = **21h**

---

## 2. 系统架构

### 2.1 架构图

```
v2.2.10 系统架构

┌─────────────────────────────────────────────────────────────────┐
│                        CLI Layer                                  │
├─────────────────────────────────────────────────────────────────┤
│  oc-collab todo list --unread          → 显示未读TODO           │
│  oc-collab todo check                  → 检查队列                │
├─────────────────────────────────────────────────────────────────┤
│                        Core Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  TodoQueueManager                      → 消息队列管理            │
│  StateNotifier (增强)                   → 发送+写入队列          │
│  AgentStartupChecker                   → 启动自检               │
├─────────────────────────────────────────────────────────────────┤
│                        State Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  state/todo_queue.yaml                → TODO消息队列            │
│  state/webhook_stats.yaml              → 通知状态（已有）        │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
Agent1 todowrite
    │
    ├── StateNotifier.notify_todo_created()
    │       │
    │       ├── 发送Webhook
    │       │
    │       └── 写入 todo_queue.yaml ← 新增
    │               │
    │               └── 未读TODO +1
    │
    └── 返回成功

Agent2启动
    │
    ├── AgentStartupChecker.run()
    │       │
    │       ├── 检查 todo_queue.yaml
    │       │
    │       └── 显示未读TODO列表
    │
    └── Agent2执行TODO
```

---

## 3. 模块设计

### 3.1 TodoQueueManager

**文件**: `src/core/todo_queue_manager.py`  
**优先级**: P0  
**工时**: 2h

#### 3.1.1 类设计

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import yaml
from pathlib import Path


@dataclass
class TodoQueueItem:
    """TODO队列项"""
    todo_id: str
    content: str
    from_agent: str
    to_agent: str
    priority: str
    created_at: str
    read: bool = False


class TodoQueueManager:
    """TODO消息队列管理器"""

    QUEUE_FILE = "state/todo_queue.yaml"

    def __init__(self, queue_file: str = None):
        self.queue_file = queue_file or self.QUEUE_FILE

    def add(self, item: TodoQueueItem) -> bool:
        """
        添加TODO到队列

        Returns:
            True: 添加成功
            False: 已存在相同的TODO
        """
        pass

    def get_unread(self, agent_id: str = None) -> List[TodoQueueItem]:
        """
        获取未读TODO

        Args:
            agent_id: 可选，指定接收者筛选

        Returns:
            未读TODO列表
        """
        pass

    def mark_read(self, todo_id: str) -> bool:
        """
        标记TODO为已读

        Returns:
            True: 标记成功
            False: TODO不存在
        """
        pass

    def get_count(self, agent_id: str = None) -> dict:
        """
        获取TODO统计

        Returns:
            {"total": int, "unread": int, "by_priority": dict}
        """
        pass

    def cleanup(self, days: int = 7) -> int:
        """
        清理N天前的已读TODO

        Returns:
            清理数量
        """
        pass
```

#### 3.1.2 数据结构

```yaml
# state/todo_queue.yaml
version: "1.0"
last_updated: "2026-02-14T10:00:00Z"
todos:
  - id: TODO-350
    content: "Agent1创建的任务"
    from_agent: agent1
    to_agent: agent2
    priority: high
    created_at: "2026-02-14T10:00:00Z"
    read: false
  - id: TODO-351
    content: "另一个任务"
    from_agent: agent1
    to_agent: agent2
    priority: medium
    created_at: "2026-02-14T10:30:00Z"
    read: true
```

---

### 3.2 StateNotifier增强

**文件**: `src/core/state_notifier.py` (增强)  
**优先级**: P0  
**工时**: 1h

#### 3.2.1 新增功能

```python
class StateNotifier:
    """状态通知器（增强版）"""

    def __init__(self, webhook_config=None, dispatcher=None,
                 queue_manager: TodoQueueManager = None):
        self.queue_manager = queue_manager
        # ... 现有代码

    def notify_todo_created(self, todo_id: str, content: str,
                           agent_id: str) -> bool:
        """
        通知TODO创建（增强版）

        1. 发送Webhook通知
        2. 写入todo_queue.yaml
        """
        # 1. 发送Webhook（原有逻辑）
        webhook_result = self._notify_webhook(...)

        # 2. 写入队列（新增）
        queue_result = self._write_to_queue(...)

        return webhook_result or queue_result

    def _write_to_queue(self, todo_id: str, content: str,
                        agent_id: str) -> bool:
        """写入TODO队列"""
        pass
```

---

### 3.3 Agent启动自检

**文件**: `src/core/agent_startup_checker.py`  
**优先级**: P0  
**工时**: 4h

#### 3.3.1 类设计

```python
from dataclasses import dataclass
from typing import List, Optional
import click


@dataclass
class StartupCheckResult:
    """启动检查结果"""
    has_unread_todos: bool
    unread_count: int
    todos: List[dict]
    message: str


class AgentStartupChecker:
    """Agent启动自检器"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.queue_manager = TodoQueueManager()

    def run(self) -> StartupCheckResult:
        """
        执行启动检查

        Returns:
            StartupCheckResult
        """
        pass

    def display_notifications(self, result: StartupCheckResult):
        """
        显示通知

        输出示例:
        ┌─────────────────────────────────────┐
        │ 🔔 你有 3 个未读TODO                │
        ├─────────────────────────────────────┤
        │ [高] TODO-350: Agent1的任务         │
        │ [中] TODO-351: 另一个任务           │
        │ [低] TODO-352: 第三任务              │
        └─────────────────────────────────────┘
        """
        pass

    def suggest_action(self, result: StartupCheckResult) -> str:
        """
        建议行动

        Returns:
            建议的action字符串
        """
        pass
```

#### 3.3.2 CLI集成

```python
# src/cli/startup_commands.py

@click.command("startup-check")
def startup_check_command():
    """
    执行Agent启动自检

    示例:
      oc-collab startup-check
    """
    from ..core.agent_startup_checker import AgentStartupChecker
    from ..core.context_manager import ContextManager

    try:
        context = ContextManager().load_context()
        agent_id = context.agent

        checker = AgentStartupChecker(agent_id)
        result = checker.run()

        checker.display_notifications(result)

    except Exception as e:
        click.echo(f"❌ 启动检查失败: {e}")
```

---

### 3.4 CLI todo list --unread

**文件**: `src/cli/todo_commands.py`  
**优先级**: P2  
**工时**: 2h

#### 3.4.1 新增命令

```python
@click.command("list")
@click.option("--unread", is_flag=True, help="仅显示未读TODO")
@click.option("--agent", type=click.Choice(["1", "2"]),
              help="按接收者筛选")
@click.option("--json", is_flag=True, help="JSON格式输出")
def todo_list_command(unread: bool, agent: str, json: bool):
    """
    显示TODO列表

    示例:
      oc-collab todo list                  # 显示所有TODO
      oc-collab todo list --unread        # 仅未读
      oc-collab todo list --unread --agent 2  # 筛选接收者
      oc-collab todo list --unread --json # JSON格式
    """
    pass
```

---

### 3.5 BUG修复

#### 3.5.1 部署文档同步修复 (F-BUG-001)

**文件**: `src/core/deploy_doc_sync.py` (增强)  
**工时**: 2h

```python
class DeployDocSync:
    """部署文档同步（增强版）"""

    REQUIRED_DOCS = [
        "CHANGELOG.md",
        "README.md",
        "skills/*/content.md",
        "docs/00-architecture/*.md",
    ]

    def check_completeness(self) -> dict:
        """
        检查文档完整性

        Returns:
            {"complete": bool, "missing": list, "present": list}
        """
        pass

    def sync_all(self) -> bool:
        """
        同步所有文档

        Returns:
            True: 成功
            False: 失败
        """
        pass
```

#### 3.5.2 Agent1开发TODO规则澄清 (F-BUG-002)

**文件**: `skills/oc_collab_collaboration_guide/content.md` (更新)  
**工时**: 2h

---

## 4. 数据结构

### 4.1 todo_queue.yaml

```yaml
# state/todo_queue.yaml
version: "1.0"
last_updated: "2026-02-14T10:00:00Z"
stats:
  total: 10
  unread: 3
  by_agent:
    agent1: 5
    agent2: 5
todos:
  - id: "TODO-350"
    content: "Agent1创建的任务"
    from_agent: "agent1"
    to_agent: "agent2"
    priority: "high"
    created_at: "2026-02-14T10:00:00Z"
    read: false
    read_at: null
  - id: "TODO-351"
    content: "另一个任务"
    from_agent: "agent1"
    to_agent: "agent2"
    priority: "medium"
    created_at: "2026-02-14T10:30:00Z"
    read: true
    read_at: "2026-02-14T11:00:00Z"
```

---

## 5. 接口设计

### 5.1 新增CLI命令

| 命令 | 参数 | 功能 |
|------|------|------|
| `oc-collab startup-check` | 无 | Agent启动自检 |
| `oc-collab todo list --unread` | [--agent] [--json] | 显示未读TODO |

### 5.2 内部API

| 类 | 方法 | 功能 |
|-----|------|------|
| TodoQueueManager | `add(item)` | 添加TODO |
| TodoQueueManager | `get_unread(agent_id)` | 获取未读 |
| TodoQueueManager | `mark_read(todo_id)` | 标记已读 |
| AgentStartupChecker | `run()` | 执行检查 |
| AgentStartupChecker | `display_notifications()` | 显示通知 |

---

## 6. 测试设计

### 6.1 测试用例

| 用例 | 输入 | 预期输出 |
|------|------|----------|
| TodoQueueManager.add | 有效TODO | 添加成功 |
| TodoQueueManager.add | 重复TODO | 返回False |
| TodoQueueManager.get_unread | agent_id=None | 返回所有未读 |
| TodoQueueManager.get_unread | agent_id="agent2" | 返回agent2的未读 |
| TodoQueueManager.mark_read | 存在的todo_id | 标记成功 |
| AgentStartupChecker.run | 有未读TODO | 显示通知 |
| AgentStartupChecker.run | 无未读TODO | 显示"无未读" |

### 6.2 测试优先级

| 优先级 | 测试项 |
|---------|--------|
| P0 | TodoQueueManager核心功能 |
| P0 | Agent启动自检 |
| P1 | CLI todo list --unread |
| P1 | BUG修复验证 |

---

## 7. 依赖

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | >=3.9 | 运行环境 |
| PyYAML | >=6.0 | YAML解析 |
| Click | >=8.0 | CLI框架 |
| StateNotifier | v2.2.9 | 基础功能 |

---

## 8. 工时估算

| 模块 | 开发 | 测试 | 缓冲 | 小计 |
|------|------|------|------|------|
| M1 TodoQueueManager | 2h | 1h | 0.5h | 3.5h |
| M2 StateNotifier增强 | 1h | 0.5h | 0h | 1.5h |
| M3 Agent启动自检 | 4h | 2h | 1h | 7h |
| M4 CLI todo --unread | 2h | 1h | 0.5h | 3.5h |
| M5 BUG-001修复 | 2h | 1h | 0.5h | 3.5h |
| M6 BUG-002修复 | 2h | 0h | 0.5h | 2.5h |
| **合计** | **13h** | **5.5h** | **3h** | **21.5h** |

---

## 9. 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 队列文件损坏 | 丢失通知 | 备份 + 恢复机制 |
| 并发写入冲突 | 数据不一致 | 文件锁 |
| Agent不自检 | 功能无效 | CLI兜底查询 |

---

## 10. 签署记录

| 角色 | 签署人 | 日期 | 状态 |
|------|--------|------|------|
| Agent 1 | 创建 | 2026-02-14 | ✅ |
| Agent 2 | 技术评审 | 2026-02-14 | ✅ 已通过7视角评审 |
| **Agent 1** | **确认签署** | **2026-02-14** | **✅ 通过** |

**签署说明**:
- Agent2技术评审：✅ 已通过7视角评审
- Agent1确认签署：✅ 设计完整，同意进入开发阶段

---

**文档版本**: v1
**创建日期**: 2026-02-14
**修订日期**: 2026-02-14
**状态**: APPROVED
