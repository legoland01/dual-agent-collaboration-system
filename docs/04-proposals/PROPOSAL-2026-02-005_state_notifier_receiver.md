# Proposal: v2.2.9 StateNotifier 完整实现 - Agent间实时TODO通知

**提案编号**: PROPOSAL-2026-02-005  
**提案人**: Agent 1  
**日期**: 2026-02-14  
**目标版本**: v2.2.10  
**优先级**: P0  
**状态**: READY  
**关联版本**: v2.2.9（StateNotifier基础版）  

---

## 0. 版本脉络 ⭐

### 0.1 功能演进历史

| 版本 | Proposal | 状态 | 核心功能 |
|------|----------|------|----------|
| **v2.2.8** | - | 已发布 | Webhook基础架构（EventDispatcher、StateNotifier骨架） |
| **v2.2.9** | PROPOSAL-2026-02-002 | 已发布 | StateNotifier**发送**功能（Webhook通知、stats记录） |
| **v2.2.10** | **本提案** | 规划中 | StateNotifier**完整**（Agent自动感知、消息队列） |

### 0.2 与v2.2.9的关系

| v2.2.9 StateNotifier | v2.2.10 本提案 |
|----------------------|----------------|
| ✅ 发送Webhook通知 | ✅ 发送 + **写入消息队列** |
| ✅ webhook_stats.yaml记录 | ✅ **新增** todo_queue.yaml |
| ❌ 无接收服务 | ✅ **新增** 接收+感知 |
| ❌ Agent无法自动感知 | ✅ **新增** Agent2启动自检 |

### 0.3 关联文档

| 文档 | 说明 |
|------|------|
| `docs/02-design/DETAIL_v2.2.9.md` | v2.2.9详细设计（StateNotifier基础） |
| `src/core/state_notifier.py` | StateNotifier实现（v2.2.9） |
| `state/webhook_stats.yaml` | 通知状态记录（v2.2.9） |

---

## 1. 问题背景

### 1.1 v2.2.9的StateNotifier实现现状

| 功能 | 实现状态 | 说明 |
|------|----------|------|
| StateNotifier发送Webhook | ✅ 已完成 | todowrite/signoff/phase_advance都会发送 |
| webhook_stats.yaml记录 | ✅ 已完成 | 所有通知有状态追踪 |
| **Webhook接收服务** | ❌ **缺失** | 没有接收器来通知对方Agent |
| **Agent实时感知** | ❌ **缺失** | Agent2无法自动知道有新TODO |
| **CLI通知** | ❌ **缺失** | 没有提示用户有新TODO |

### 1.2 当前流程的问题

```
v2.2.9 当前流程（不完整）：

Agent1 创建TODO
    │
    ├── ✅ StateNotifier发送HTTP POST到配置的URL
    │
    ├── ✅ webhook_stats.yaml记录
    │
    └── ❌ 没有接收服务 → Agent2不知道有新TODO
                    → 需要用户转述
```

**核心问题**：StateNotifier**只实现了发送**，没有实现**接收和通知**。

### 1.3 用户期望 vs 现实

| 用户期望 | 现实 |
|----------|------|
| Agent1创建TODO后，Agent2自动知道 | ❌ Agent2需要用户告知 |
| Agent2能实时看到新TODO | ❌ 需要主动查询 |
| 双方Agent能自动协作 | ❌ 仍需用户转述 |

---

## 2. 解决方案

### 2.1 核心思路

```
v2.2.10 完整流程（目标）：

Agent1 创建TODO
    │
    ├── ✅ StateNotifier发送HTTP POST
    │
    ├── ✅ webhook_stats.yaml记录
    │
    ├── ✅ WebhookReceiver接收通知
    │       │
    │       └── 本地消息队列/状态文件
    │
    └── ✅ Agent2自动感知（CLI提示/状态查询）
                │
                └── Agent2看到提示："收到新TODO: TODO-XXX"
```

### 2.2 实现方案

#### 方案A：本地消息队列（推荐）

**核心**：使用本地文件作为消息队列，Agent启动时检查

```
state/
├── todo_queue.yaml          # TODO消息队列
│   └── pending_todos/      # 待处理的TODO
│       └── agent1/         # 按发送者分组
│           └── TODO-XXX/
│               ├── content: "任务描述"
│               ├── from: "agent1"
│               └── timestamp: "..."
├── webhook_stats.yaml       # 通知状态（已有）
└── todo_state.yaml          # TODO状态（已有）
```

**优点**：
- 实现简单，不依赖网络
- 兼容现有架构
- 易于调试

**缺点**：
- 需要Agent主动检查（可定时任务）

#### 方案B：Webhook接收服务

**核心**：实现HTTP服务器接收Webhook通知

```
src/
└── core/
    └── webhook_receiver.py   # HTTP接收服务
        └── 监听 /webhook 端口
            └── 收到通知后写入todo_queue.yaml
```

**优点**：
- 真正的实时通知
- 兼容外部Webhook

**缺点**：
- 实现复杂
- 需要处理并发、网络问题

### 2.3 推荐方案：方案A + 定时检查

**组合方案**：
- 轻量级：Agent启动时检查todo_queue.yaml
- 可选：后台定时检查（如每30秒）

```
Agent启动时
    │
    ├── 检查 todo_queue.yaml
    │       │
    │       └── 有未读TODO → 显示提示
    │               │
    │               └── Agent2执行TODO
    │
    └── 清空已读队列（或标记已读）
```

---

## 3. 功能模块

### 3.1 新增模块

| 模块 | 文件 | 功能 | 工时 |
|------|------|------|------|
| TodoQueueManager | core/todo_queue_manager.py | TODO消息队列管理 | 2h |
| TodoReceiver | core/todo_receiver.py | 接收并处理TODO通知 | 2h |
| CLI通知增强 | cli/main.py | Agent启动时显示未读TODO | 1h |
| 后台检查（可选） | core/daemon.py | 定时检查新TODO | 2h |

### 3.2 增强现有模块

| 模块 | 变更 | 工时 |
|------|------|------|
| StateNotifier | 发送后写入todo_queue.yaml | 1h |
| CLI增强 | Agent1发送后提示；Agent2启动时检查 | 1h |

### 3.3 数据结构设计

```yaml
# state/todo_queue.yaml
version: "1.0"
pending_todos:
  agent1:
    - id: TODO-350
      content: "Agent1创建的任务"
      from: agent1
      to: agent2
      priority: high
      created_at: "2026-02-14T10:00:00Z"
      read: false
read_todos:
  - id: TODO-349
    content: "已读的任务"
    read_at: "2026-02-14T10:30:00Z"
```

---

## 4. 用户场景

| 场景 | 操作 | 系统行为 |
|------|------|----------|
| **Agent1创建TODO** | `oc-collab todowrite --content "任务" --agent 2` | ✅ 发送通知，写入队列 |
| **Agent2启动** | 新会话开始 | ✅ 显示未读TODO提示 |
| **Agent2执行TODO** | 收到TODO后执行 | ✅ 完成后标记已读 |
| **Agent2查看未读** | `oc-collab todo list --unread` | ✅ 显示所有未读TODO |

---

## 5. 优先级

| 优先级 | Feature | 说明 |
|--------|---------|------|
| **P0** | TodoQueueManager | 基础消息队列 |
| **P0** | StateNotifier写入队列 | 发送后写入队列 |
| **P0** | Agent2启动时检查 | 自动感知未读TODO |
| **P1** | `oc-collab todo list --unread` | 查询未读TODO |
| **P2** | 后台定时检查 | 实时性增强 |

---

## 6. 依赖

- 无外部依赖
- 复用现有state/目录结构
- StateNotifier（v2.2.9已实现）

---

## 7. 验收标准

- [ ] Agent1创建TODO后，todo_queue.yaml有记录
- [ ] Agent2启动时显示未读TODO
- [ ] `oc-collab todo list --unread` 正常显示
- [ ] TODO处理后自动标记已读
- [ ] 向后兼容，不影响现有功能

---

## 8. 工时估算

| 任务 | 工时 |
|------|------|
| TodoQueueManager | 2h |
| StateNotifier增强（写入队列） | 1h |
| Agent2启动时检查未读TODO | 2h |
| CLI通知增强 | 1h |
| `todo list --unread` 命令 | 2h |
| 单元测试 | 2h |
| **总计** | **10h** |

---

## 9. 与v2.2.9的关系

| v2.2.9功能 | v2.2.10增强 |
|------------|-------------|
| StateNotifier发送 | StateNotifier发送**+写入队列** |
| webhook_stats.yaml | **新增** todo_queue.yaml |
| 无 | **Agent2启动时检查未读** |
| 无 | **todo list --unread** |

---

## 10. 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 队列文件损坏 | 丢失通知 | 添加备份和恢复机制 |
| 并发写入冲突 | 数据不一致 | 文件锁机制 |
| 消息积压 | 性能问题 | 定期清理已读消息 |

---

## 11. 后续迭代（v2.2.11+）

| 功能 | 说明 |
|------|------|
| 后台定时检查 | 每30秒检查一次 |
| WebhookReceiver | HTTP接收外部通知 |
| 推送通知 | 支持Pushbullet等推送服务 |
| 可视化面板 | Web界面显示协作状态 |

---

**提案人**: Agent 1  
**日期**: 2026-02-14  
**状态**: READY
