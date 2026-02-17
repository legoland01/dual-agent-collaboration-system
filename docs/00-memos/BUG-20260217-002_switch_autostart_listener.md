# BUG报告: BUG-20260217-002

**日期**: 2026-02-17  
**报告人**: Agent1 (产品经理)  
**优先级**: P1  
**状态**: 部分解决

---

## 问题描述

### 现象1: Agent切换后未读TODO不显示

**问题**: Agent2创建TODO后，切换到Agent1时显示"已经是 Agent 1"，未显示未读TODO通知。

**根因**: `switch_command` 在检测到已是目标Agent时直接return，未执行后续的通知检查逻辑。

**状态**: ✅ 已解决 - 调整了代码顺序，无论是否切换都会检查未读TODO并显示。

---

### 现象2: switch命令无法自动启动后台监听进程

**问题**: 尝试在 `oc-collab switch` 命令内部使用 `subprocess.Popen` 或 `os.system` 启动 `agent listen` 后台进程时，进程无法成功启动。

**复现步骤**:
1. 执行 `oc-collab switch 1`
2. 代码中尝试调用 `subprocess.Popen(cmd, shell=True)` 启动监听
3. 验证：`ps aux | grep agent listen` 无结果

**实际行为**:
- 手动在命令行执行 `nohup oc-collab agent listen &` 可以成功启动
- 在Python代码内部调用subprocess启动失败

**状态**: ❌ 未完全解决

---

## 临时解决方案

由于subprocess在CLI内部启动失败，提供手动启动方案：

```bash
# 每个Agent终端需要手动启动监听
nohup oc-collab agent listen --interval 3 > logs/agent_listen.log 2>&1 &
```

**已实现功能**:
- ✅ `agent listen` 命令正常工作
- ✅ 手动启动后，Agent间TODO实时通知正常
- ✅ `switch` 时显示未读TODO通知

---

## 待解决

1. **彻底解决subprocess启动问题**: 研究为何CLI内部无法启动后台进程
2. **自动启动方案**: 用户声明Agent身份后自动启动监听
3. **多Agent监听隔离**: 每个Agent应该有独立的监听进程和日志

---

## 相关文件修改

- `src/cli/agent_commands.py`: 新增 `listen` 命令
- `src/cli/main.py`: switch时显示未读TODO通知
- `src/core/todo_queue_manager.py`: 修复TODO读取逻辑
- `src/core/state_notifier.py`: 修复queue_manager传入
- `src/cli/enhanced_commands.py`: StateNotifier集成修复
- `src/cli/startup_commands.py`: 修复agent_id类型

---

## 影响范围

- F-TODO-002: TODO接收方自动感知 - 部分解决
- 需要用户手动启动监听才能完全生效
