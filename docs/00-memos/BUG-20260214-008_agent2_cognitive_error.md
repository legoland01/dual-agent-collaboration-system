# BUG-20260214-008: Agent2对系统架构认知错误

**发现日期**: 2026-02-14  
**发现人**: Agent 1  
**严重度**: P0 (阻塞协作流程)  
**状态**: OPEN  
**涉及Agent**: Agent 2

---

## 问题描述

Agent2在处理BUG-003（todowrite调用失败）和BUG-007（TODO编号冲突）时，**声称todowrite是opencode系统的指令，无法修改**。

**实际情况**：todowrite是oc-collab框架的自定义命令，位于oc-collab源码中，**完全可修改**。

---

## Agent2的原话

```
Agent2: "todowrite是opencode的指令，有问题无法更改"
```

---

## 代码证据

### 证据1: todowrite定义位置

**文件**: `src/cli/enhanced_commands.py`  
**行号**: 53

```python
@click.command(name="todowrite")
@click.argument("todos", nargs=-1)
@click.option("--content", help="待办内容")
@click.option("--priority", type=click.Choice(["high", "medium", "low"]), default="medium")
@click.option("--agent", type=click.Choice(["1", "2"]), help="Agent 编号")
@click.option("--auto-check/--no-auto-check", default=True,
              help="是否自动检查参数和Skill (默认启用)")
@click.option("--test-mode", is_flag=True, help="测试模式")
def todowrite_command(todos: tuple, content: Optional[str], priority: str, agent: Optional[str], auto_check: bool, test_mode: bool):
```

**结论**: `@click.command` 装饰器定义，这是oc-collab CLI的自定义命令。

### 证据2: todowrite实现文件

**文件**: `src/core/todo_sync_manager.py`

```
TodoSyncManager - 这是oc-collab自己实现的管理器
├── load_todos() - 加载TODO
├── save_todos() - 保存TODO
├── add_todo() - 添加TODO
├── update_todo() - 更新TODO
└── delete_todo() - 删除TODO
```

**结论**: 整个TODO管理系统是oc-collab自定义实现，不是opencode的。

### 证据3: CLI注册

**文件**: `src/cli/main.py:28`

```python
from .enhanced_commands import (
    show_context_command,
    todowrite_command,  # ← oc-collab导入
    todoedit_command,
    status_command,
)
```

**结论**: todowrite_command 是oc-collab的enhanced_commands模块导出的函数。

---

## todowrite 与 opencode 的关系

| 组件 | 归属 | 说明 |
|------|------|------|
| **opencode** | 通用框架 | 提供基础CLI框架(`click`)和Agent交互机制 |
| **oc-collab** | 协作框架 | 自定义`todowrite`命令实现协作功能 |

```
用户 → opencode CLI → oc-collab todowrite_command → todo_sync_manager → state/agent_adhoc_todos.yaml
```

---

## 影响范围

| 影响项 | 说明 |
|--------|------|
| BUG-003无法修复 | todowrite调用失败需要修改代码 |
| BUG-007无法修复 | TODO编号冲突需要修改编号逻辑 |
| v2.2.11无法推进 | Agent2拒绝修改oc-collab代码 |
| 协作流程阻塞 | 所有需要修改todo相关代码的任务都受影响 |

---

## 根因分析

Agent2对系统架构的理解存在**根本性错误**：

| 错误认知 | 实际情况 |
|----------|----------|
| "todowrite是opencode的指令" | todowrite是oc-collab的自定义命令 |
| "无法修改" | 位于src/cli/enhanced_commands.py，可直接修改 |
| "需要联系opencode团队" | 无需，这是oc-collab的内部代码 |

---

## 解决方案

### 立即行动

| 步骤 | 操作 | 负责人 |
|------|------|--------|
| 1 | Agent2阅读代码证据 | Agent2 |
| 2 | Agent2确认todowrite是oc-collab代码 | Agent2 |
| 3 | Agent2开始修复BUG-003和BUG-007 | Agent2 |

### 代码修改建议

todowrite命令的修改位置：`src/cli/enhanced_commands.py`

需要修改的功能：
1. **Skill强制检查**（移除--auto-check，改为强制）
2. **TODO编号逻辑**（实现Agent独立编号）
3. **写入前验证**（ID唯一性检查）

---

## 验证方法

```bash
# 1. 确认todowrite是oc-collab命令
grep -n "def todowrite_command" src/cli/enhanced_commands.py
# 应该找到: def todowrite_command

# 2. 确认文件归属
ls -la src/cli/enhanced_commands.py
# 文件属于oc-collab项目

# 3. 尝试修改
# Agent2可以直接编辑此文件
```

---

## 对话记录

| 时间 | 发言人 | 内容 |
|------|--------|------|
| 2026-02-14 | Agent2 | "todowrite是opencode的指令，有问题无法更改" |
| 2026-02-14 | Agent1 | (提供代码证据，但Agent2拒绝) |
| 2026-02-14 | Agent1 | 创建此Bug Report |

---

## 关联文档

| 文档 | 说明 |
|------|------|
| `src/cli/enhanced_commands.py` | todowrite命令定义 |
| `src/core/todo_sync_manager.py` | TODO管理实现 |
| `docs/00-memos/BUG-20260214-003_todowrite_call_failed.md` | todowrite调用失败 |
| `docs/00-memos/BUG-20260214-007_todo_ownership_conflict.md` | TODO编号冲突 |
| `docs/00-memos/ANALYSIS_20260214_todo_yaml_relationship.md` | 专题分析 |

---

## 后续行动

1. **Agent2必须评审此Bug Report**
2. **Agent2必须在评审后开始代码修改**
3. **如果Agent2继续拒绝，需升级到设计Review**

---

**发现人**: Agent 1  
**日期**: 2026-02-14  
**状态**: OPEN
