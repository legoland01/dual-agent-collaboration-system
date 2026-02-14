# PROPOSAL-2026-02-009: StateReceiver与CLI队列集成改进

**Date**: 2026-02-14
**Author**: Agent2
**Status**: DRAFT

---

## 1. 问题背景

### 1.1 发现的问题

v2.2.11 部署后验证 StateReceiver 功能时发现：

| 问题 | 描述 | 发现阶段 |
|------|------|----------|
| 队列独立 | StateReceiver 使用 `state/state_queue.json`，CLI 使用 `state/todo_queue.yaml` | 部署后验证 |
| 无同步机制 | 接收的通知不会自动同步到 CLI 的 TODO 队列 | 部署后验证 |
| 测试覆盖不足 | E2E 测试未验证"发送方 → 接收方 → CLI 查询"完整链路 | 部署后验证 |

### 1.2 影响

- Agent1 创建 TODO 后，Agent2 无法通过 `oc-collab todo list` 看到
- StateReceiver 只接收不联动，沦为"黑洞"
- 设计/评审/测试三阶段均未发现此问题

---

## 2. 改进目标

### 2.1 功能目标

| 目标 | 描述 | 优先级 |
|------|------|--------|
| G1 | StateReceiver 接收的通知自动同步到 CLI TODO 队列 | P0 |
| G2 | `oc-collab todo list` 能显示所有来源的 TODO | P0 |
| G3 | 统一队列存储，避免数据分散 | P1 |

### 2.2 质量目标

| 目标 | 描述 | 优先级 |
|------|------|--------|
| Q1 | 设计阶段必须包含"数据流图" | P0 |
| Q2 | E2E 测试覆盖完整链路 | P0 |
| Q3 | 评审检查项增加"状态同步验证" | P1 |

---

## 3. 解决方案

### 3.1 架构改进

#### 方案A：StateReceiver 同步到 CLI 队列（推荐）

```
Agent1 todowrite → StateNotifier → webhook → StateReceiver → 写入 todo_queue.yaml → CLI 显示
```

**优点**：改动最小，只需要在 StateReceiver 添加写入逻辑

**缺点**：StateReceiver 依赖 CLI 的队列格式

#### 方案B：统一队列管理层

```
StateReceiver → QueueManager → 统一存储 → CLI/API 读取
```

**优点**：架构清晰，职责分离

**缺点**：需要重构，影响范围大

**推荐方案A**

### 3.2 数据流图

```
┌─────────────┐     webhook      ┌──────────────┐     同步      ┌─────────────┐
│   Agent1    │ ──────────────▶ │ StateReceiver │ ───────────▶ │ CLI Queue   │
│  (sender)   │                 │  (:8081)     │              │(todo_queue) │
└─────────────┘                 └──────────────┘              └─────────────┘
                                        │                          │
                                        │                          │
                                        ▼                          ▼
                               ┌──────────────┐          ┌─────────────┐
                               │ StateQueue    │          │ CLI Display │
                               │(state_queue) │          │oc-collab    │
                               └──────────────┘          │todo list    │
                                                         └─────────────┘
```

### 3.3 实现步骤

#### Phase 1: 队列同步 (P0)

1. 修改 `StateReceiver`
   - 添加 `sync_to_cli_queue()` 方法
   - 接收通知后同时写入 `todo_queue.yaml`

2. 修改 `TodoQueueManager`
   - 添加 `from_webhook()` 工厂方法
   - 支持从 StateReceiver 格式转换

3. 单元测试
   - `test_state_receiver_sync_to_cli`
   - `test_queue_format_conversion`

#### Phase 2: CLI 显示改进 (P0)

1. 修改 `oc-collab todo list`
   - 合并显示 `todo_queue.yaml` 和 `state_queue.json` 的 TODO

2. 修改 `oc-collab todo stats`
   - 统计所有来源的 TODO

#### Phase 3: 设计与评审改进 (P1)

1. 更新 `oc_collab_detailed_design_guide`
   - 增加"数据流图"必需章节
   - 增加"状态存储关系"必需章节

2. 更新 `oc_collab_test_acceptance_guide`
   - 增加"状态同步验证"测试用例

---

## 4. 影响分析

### 4.1 受影响模块

| 模块 | 影响 | 风险 |
|------|------|------|
| `src/core/state_receiver.py` | 需要修改 | 低 |
| `src/core/todo_queue_manager.py` | 需要修改 | 低 |
| `src/cli/todo_commands.py` | 需要修改 | 低 |

### 4.3 兼容性

- 向前兼容：现有 CLI 命令行为不变
- 向后兼容：不影响已存储的历史数据

---

## 5. 资源估算

| 任务 | 工时 | 优先级 |
|------|------|--------|
| 队列同步实现 | 2h | P0 |
| CLI 显示改进 | 1h | P0 |
| 单元测试 | 2h | P0 |
| E2E 测试 | 1h | P0 |
| Skill 更新 | 1h | P1 |
| **总计** | **7h** | |

---

## 6. 验收标准

### 6.1 功能验收

- [ ] Agent1 创建 TODO，Agent2 `todo list` 能看到
- [ ] StateReceiver 接收的通知同时写入两个队列
- [ ] 统计数据准确反映所有来源的 TODO

### 6.2 质量验收

- [ ] 设计文档包含数据流图
- [ ] E2E 测试覆盖完整链路
- [ ] Skill 更新完成

---

## 7. 开放问题

| 编号 | 问题 | 负责人 | 状态 |
|------|------|--------|------|
| Q1 | 队列格式是否需要统一？ | Agent1 | 待讨论 |
| Q2 | StateReceiver 是否需要独立的 CLI 命令？ | Agent2 | 待讨论 |

---

## 8. 签署确认

### Agent2 (技术评审)

| 状态 | 签名 | 日期 |
|------|------|------|
| 技术评审通过 | | |
| 技术评审通过（有条件） | | |
| 需修改 | | |

### Agent1 (创建/确认)

| 状态 | 签名 | 日期 |
|------|------|------|
| 创建 | | |
| 确认修改 | | |
| 不同意 | | |

---

## 附录

### A. 相关文档

- `docs/02-design/DETAIL_v2.2.11.md` - v2.2.11 详细设计
- `src/core/state_receiver.py` - StateReceiver 源码
- `src/core/todo_queue_manager.py` - TodoQueueManager 源码

### B. 变更历史

| 日期 | 作者 | 描述 |
|------|------|------|
| 2026-02-14 | Agent2 | 初始版本 |
