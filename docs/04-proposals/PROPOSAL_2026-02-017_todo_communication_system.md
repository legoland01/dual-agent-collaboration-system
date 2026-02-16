# Proposal: TODO通信系统设计（通信层）

**版本**: v1  
**日期**: 2026-02-15  
**作者**: Consultant (战略规划)  
**状态**: 待评审

---

## 一、背景

### 1.1 问题背景

TODO系统本质上是一个**通信系统**，用于Agent之间（未来也包括人）传递任务信息。

在多Agent场景下，通信系统需要解决：
- 寻址：TODO发给哪个Agent？
- 感知：如何知道有新TODO？
- 确认：如何确认送达？
- 状态同步：状态变更如何同步？

### 1.2 设计原则

**核心原则**：不要自己实现可靠的通信系统，而是依托成熟的现有体系。

---

## 二、分层架构

### 2.1 TODO系统分层

```
┌─────────────────────────────────────────────────┐
│  应用层                                          │
│  (TODO的内容、创建时机、结束条件)                │
├─────────────────────────────────────────────────┤
│  通信层                                          │
│  (TODO的传输、确认、状态同步)                    │
└─────────────────────────────────────────────────┘
```

### 2.2 各层职责

| 层次 | 职责 | 示例 |
|------|------|------|
| **通信层** | 可靠传输、寻址、感知、确认 | Git同步、Webhook推送 |
| **应用层** | 任务内容、模板、创建时机 | TODO字段定义、模板 |

---

## 三、通信层设计

### 3.1 依托现有体系

oc-collab已经依托现有体系：

| 机制 | 依托 | 说明 |
|------|------|------|
| 状态同步 | Git | 利用Git的可靠传输 |
| 事件通知 | Webhook | 感知状态变更 |
| 文件监控 | 文件系统 | 感知文件变化 |

### 3.2 通信能力矩阵

| 能力 | 依托 | 实现方式 |
|------|------|----------|
| **寻址** | Agent ID | TODO中包含target_agent字段 |
| **路由** | 目录服务 | project_state.yaml中的Agent注册表 |
| **感知** | Webhook | 文件变更时推送给相关Agent |
| **确认** | Git commit | commit message中包含ACK |
| **状态同步** | Git | 状态文件同步 |
| **可靠传输** | Git | Git本身保证 |

### 3.3 Git作为通信底层

**优势**：

| Git能力 | 对通信系统的价值 |
|---------|-----------------|
| 可靠传输 | 不丢失数据 |
| 顺序保证 | commit顺序即事件顺序 |
| 版本历史 | 可追溯、可回滚 |
| 冲突处理 | 合并机制解决并发 |
| 离线支持 | 本地先操作，联网后同步 |

### 3.4 需要增强的能力

| 能力 | 现状 | 增强方案 |
|------|------|----------|
| 及时感知 | Git poll | Webhook/文件监控推送 |
| 送达确认 | 无 | commit message中ACK |
| 细粒度事件 | 粗 | 字段级别变更检测 |

---

## 四、多Agent场景

### 4.1 Agent注册表

```yaml
# project_state.yaml
agents:
  agent1:
    role: PRODUCT_MANAGER
    status: active
  agent2:
    role: DEVELOPMENT_LEAD
    status: active
  # 动态新增Agent
  agent3:
    role: FRONTEND_DEV
    reports_to: agent1
    status: active
```

### 4.2 TODO路由

```yaml
- id: TODO-1-025
  content: 实现前端模块X
  target_agent: agent3    # 寻址：发给Agent3
  created_by: agent1
  depends_on:
    - TODO-2-010       # 依赖Agent2的输出
```

### 4.3 感知机制

```
Agent3的工作流程：
│
├── 1. 启动时
│     └── 读取target_agent包含agent3的TODO
│
├── 2. 运行时
│     └── 通过Webhook感知新TODO到达
│
└── 3. 状态变更
      └── 状态变更推送给创建者
```

---

## 五、消息格式设计

### 5.1 TODO消息

```yaml
message:
  id: TODO-1-025
  type: TASK_CREATED
  content: "实现前端模块X"
  target_agent: agent3
  created_by: agent1
  created_at: 2026-02-15T10:00:00
  ack_required: true
```

### 5.2 ACK确认

```yaml
message:
  id: TODO-1-025
  type: TASK_ACKNOWLEDGED
  acknowledged_by: agent3
  acknowledged_at: 2026-02-15T10:05:00
```

### 5.3 状态变更

```yaml
message:
  id: TODO-1-025
  type: STATUS_CHANGED
  old_status: pending
  new_status: in_progress
  changed_by: agent3
  changed_at: 2026-02-15T10:10:00
```

---

## 六、实施计划

### 6.1 L1阶段（v2.3.x - v2.4.x）

| 功能 | 说明 |
|------|------|
| Agent注册表 | 在project_state.yaml中注册Agent |
| 目标Agent字段 | TODO中包含target_agent |
| 送达确认 | commit message中ACK机制 |

### 6.2 L2阶段（v2.4.x - v3.0）

| 功能 | 说明 |
|------|------|
| Webhook感知 | 文件变更时推送给相关Agent |
| 状态变更通知 | 状态变更推送给创建者 |
| 多Agent协调 | depends_on跨Agent依赖 |

### 6.3 L3阶段（v3.0+）

| 功能 | 说明 |
|------|------|
| 人机协作 | 人给Agent分配任务 |
| 审批流 | 任务分配需要审批确认 |
| 可视化 | 通信状态可视化 |

---

## 七、与TCP/IP的类比

| TCP/IP | TODO通信系统 |
|--------|--------------|
| IP地址 | Agent ID |
| 端口 | 任务类型 |
| TCP三次握手 | TODO创建 → ACK确认 → 开始处理 |
| ACK确认 | commit message中的送达回执 |
| 重传机制 | 失败自动重试 |
| 路由表 | Agent注册表 |

---

## 八、预期收益

| 收益 | 说明 |
|------|------|
| 可靠传输 |依托Git，保证不丢失 |
| 可追溯 | 所有变更有历史记录 |
| 多Agent支持 | 支持动态新增Agent |
| 扩展性 | 可叠加更多通信机制 |

---

## 九、风险与应对

| 风险 | 应对 |
|------|------|
| Git冲突频繁 | 优化锁机制，减少并发写入 |
| 感知延迟 | Webhook实时推送 |
| 过度依赖Git | 保持接口抽象，可替换底层 |

---

## 十、结论

**核心思路**：依托Git等成熟体系，不要自己实现可靠的通信系统。

**通信层是基础设施**，在实现多Agent之前必须先解决。

---

**下一步**：
- 评审通过后纳入开发计划
- 优先实现L1阶段的功能

---

**文档版本历史**：

| 版本 | 日期 | 变更 |
|------|------|------|
| v1 | 2026-02-15 | 初始版本 |
