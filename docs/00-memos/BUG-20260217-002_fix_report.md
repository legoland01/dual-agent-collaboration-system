# BUG解决报告: BUG-20260217-002

**日期**: 2026-02-17  
**状态**: 部分解决

---

## 问题概述

Agent2创建TODO后，Agent1无法自动感知到新TODO。

---

## 解决措施

### 1. StateNotifier修复 ✅

**问题**: `StateNotifier`初始化时未传入`queue_manager`，导致通知无法写入队列

**修复**:
- 文件: `src/cli/enhanced_commands.py`
- 修改: 传入`TodoQueueManager`给`StateNotifier`
- 修改: 传入`to_agent`参数

### 2. switch时显示未读TODO ✅

**问题**: Agent切换时未检查未读TODO

**修复**:
- 文件: `src/cli/main.py`
- 修改: 无论是否切换都显示未读TODO通知

### 3. TODO读取逻辑修复 ✅

**问题**: `TodoQueueManager`读取错误的文件（todo_queue.yaml而非agent_adhoc_todos.yaml）

**修复**:
- 文件: `src/core/todo_queue_manager.py`
- 修改: QUEUE_FILE指向agent_adhoc_todos.yaml
- 修改: from_dict方法支持解析TODO-2to1-xxx格式

### 4. agent_id类型修复 ✅

**问题**: `context.agent`返回int类型，但函数期望str类型

**修复**:
- 文件: `src/cli/startup_commands.py`
- 修改: 添加类型转换

### 5. 后台监听命令 ✅

**问题**: Agent需要手动查询TODO队列

**修复**:
- 文件: `src/cli/agent_commands.py`
- 新增: `agent listen`命令 - 后台轮询TODO队列，发现新TODO时通知

### 6. subprocess自动启动 ❌

**问题**: 在`switch`命令内部尝试启动后台监听进程失败

**状态 - 临时**: 未解决方案是手动启动

---

## 彻底解决方案（待完成）

### 方案A: Prompt声明后自动启动

用户声明Agent身份后自动启动监听：

```
# 用户输入
你是Agent1，请遵守oc-collab规范工作

# 系统响应
✅ 已识别为Agent1，已启动后台监听服务
```

**需要**:
1. 识别用户Prompt中的Agent声明
2. 自动执行 `agent listen` 命令

### 方案B: 每个Agent独立监听进程

每个Agent应有独立的监听进程：

```
Agent1终端: oc-collab agent listen --agent 1
Agent2终端: oc-collab agent listen --agent 2
```

**需要**:
1. 修改listen命令支持--agent参数
2. 不同Agent写入不同日志文件
3. 进程隔离管理

### 方案C: 用户指导

在AGENTS.md中添加启动说明：

```markdown
## 启动流程

1. Agent1终端:
   oc-collab switch 1
   nohup oc-collab agent listen --interval 3 > logs/agent1_listen.log &

2. Agent2终端:
   oc-collab switch 2
   nohup oc-collab agent listen --interval 3 > logs/agent2_listen.log &
```

---

## 已验证功能

✅ Agent2创建TODO → 写入agent_adhoc_todos.yaml  
✅ Agent1切换时 → 显示未读TODO  
✅ 手动启动监听 → 实时通知正常工作  

---

## 设计文档更新

需要更新 `docs/02-design/DETAIL_v2.3.1.md` 补充：

1. Agent间通信机制说明
2. 后台监听服务设计
3. 启动流程说明

---

## 结论

- **当前可用**: 手动启动监听后功能正常
- **需要改进**: 自动启动机制
- **建议**: 采用方案A或方案C作为v2.3.2的优化方向
