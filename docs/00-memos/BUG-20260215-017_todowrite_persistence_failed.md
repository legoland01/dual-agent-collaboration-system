# Bug报告: todowrite命令无法持久化TODO

**Bug ID**: BUG-20260215-017
**严重程度**: P0
**状态**: Open
**发现时间**: 2026-02-15
**发现者**: Agent 1

---

## 问题描述

执行`oc-collab todowrite`命令后，TODO未被持久化到`state/agent_adhoc_todos.yaml`。

## 复现步骤

1. Agent2执行`oc-collab todowrite "任务" --agent 2`（错误用法：`--agent_id 2`）
2. 观察：命令执行成功但TODO ID格式错误
3. 验证：生成TODO-1-xxx而非TODO-2-xxx，导致ID冲突

## 根因分析

**问题1：参数名错误**
- CLI参数定义：`--agent` (第57行)
- 调用时错误使用：`--agent_id`
- 结果：参数被忽略，agent_id默认为None

**问题2：ID生成逻辑**
- 当agent_id=None时，生成格式为`TODO-xxx`（无Agent前缀）
- 但YAML中已有相同ID，导致冲突

**问题代码**：
- CLI参数：`@click.option("--agent", ...)`
- 实际调用传入：`agent_id=2`（错误的参数名）

## 修复建议

1. 确认正确参数名：`--agent`（不是`--agent_id`）
2. 或添加参数别名支持`--agent-id`

## 修复记录

**修复时间**: 2026-02-15
**修复内容**: 添加 `--agent-id` 作为 `--agent` 的别名

修改文件: `src/cli/enhanced_commands.py` 第57行

```python
# 修改前
@click.option("--agent", type=click.Choice(["1", "2"]), help="Agent 编号")

# 修改后
@click.option("--agent", "--agent-id", "-a", type=click.Choice(["1", "2"]), help="Agent 编号")
```

---

**状态**: Closed
**优先级**: P0
