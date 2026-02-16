# Proposal: TODO系统整合设计

**提案编号**: PROPOSAL_2026-02-021  
**日期**: 2026-02-16  
**作者**: Consultant (战略规划)  
**状态**: DRAFT

---

## 一、整合背景

### 1.1 现有提案

| 提案 | 内容 | 状态 |
|------|------|------|
| PROPOSAL_2026-02-016 | TODO应用层优化（编号、来源、模板） | 待评审 |
| PROPOSAL_2026-02-017 | TODO通信层设计（寻址、感知、ACK） | 待评审 |

### 1.2 整合目的

- 合并两个分散提案，形成完整TODO系统设计
- 补充与刚性框架的整合关系
- 明确TODO在系统中的定位

---

## 二、TODO系统定位

### 2.1 在系统中的位置

```
┌─────────────────────────────────────────────────────────────┐
│                    PM-Agent (L3)                           │
│                  项目管理、进度视图                          │
├─────────────────────────────────────────────────────────────┤
│                 刚性框架 (L1-L2)                            │
│              里程碑锁、审批权、审计                          │
├─────────────────────────────────────────────────────────────┤
│                     TODO系统                                │
│           应用层 + 通信层 + 刚性约束                         │
├─────────────────────────────────────────────────────────────┤
│                     基础模块                                │
│         Git同步、Webhook通知、状态管理                       │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 TODO系统的三重身份

| 身份 | 说明 |
|------|------|
| **通信工具** | Agent之间传递任务信息 |
| **流程载体** | 承载流程状态和进度 |
| **审计对象** | 受刚性框架约束 |

---

## 三、功能架构

### 3.1 分层设计

```
┌─────────────────────────────────────────────────────────────┐
│                      应用层                                  │
│  ┌─────────────┬─────────────┬─────────────┐               │
│  │ 编号系统    │ 来源标签    │ 模板系统    │               │
│  │ 1to2-xxx   │ REQ/BUG    │ 自动填充    │               │
│  └─────────────┴─────────────┴─────────────┘               │
├─────────────────────────────────────────────────────────────┤
│                      通信层                                  │
│  ┌─────────────┬─────────────┬─────────────┐               │
│  │ 寻址路由    │ 感知推送    │ ACK确认    │               │
│  │ target      │ Webhook    │ commit     │               │
│  └─────────────┴─────────────┴─────────────┘               │
├─────────────────────────────────────────────────────────────┤
│                     刚性约束层                              │
│  ┌─────────────┬─────────────┬─────────────┐               │
│  │ 依赖强检    │ 生命周期   │ 审计日志    │               │
│  │ 前置阻断    │ 状态机    │ 完整记录    │               │
│  └─────────────┴─────────────┴─────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、应用层设计

### 4.1 编号系统：创建者→接收者

**格式**：`TODO-XtoY-xxx`

| 部分 | 含义 |
|------|------|
| X | 创建者Agent ID |
| to | 分隔符 |
| Y | 接收者Agent ID |
| xxx | 序号 |

**示例**：

| 编号 | 含义 |
|------|------|
| TODO-1to2-001 | Agent1创建，分配给Agent2 |
| TODO-2to1-001 | Agent2创建，分配给Agent1 |
| TODO-1to1-001 | Agent1创建，自己执行 |

**向后兼容**：
- 旧格式`TODO-1-xxx`视为`TODO-1to1-xxx`

### 4.2 来源标签

**目的**：区分TODO从哪里来

```yaml
- id: TODO-1to2-022
  content: 修复BUG-20260215-014
  source: BUG        # 来源类型
```

**来源类型**：

| 来源 | 说明 |
|------|------|
| REQUIREMENT | 来自需求文档 |
| BUG | 来自BUG报告 |
| FEEDBACK | 来自客户/用户反馈 |
| MANUAL | 手动创建 |

### 4.3 模板系统

**模板示例**：

```yaml
# 需求任务模板
type: REQUIREMENT
template:
  - id: TODO-{creator}to{receiver}-{seq}
    content: "实现{需求ID}: {需求描述}"
    source: REQUIREMENT
    priority: {priority}
    acceptance_criteria: "{继承的验收标准}"

# BUG修复模板  
type: BUG_FIX
template:
  - id: TODO-{creator}to{receiver}-{seq}
    content: "修复{BUG-ID}: {标题}"
    source: BUG
    priority: {severity}
    root_cause: ""
    fix_plan: ""
    test_case: ""
```

### 4.4 事件驱动自动创建

**触发事件与自动创建**：

| 触发事件 | 自动创建 |
|----------|----------|
| 需求文档签署通过 | 开发任务TODO |
| 设计文档签署通过 | 实现任务TODO |
| BUG创建 | 修复任务TODO |
| 任务完成 | 自动建议下一步任务 |

---

## 五、通信层设计

### 5.1 核心能力矩阵

| 能力 | 依托 | 实现方式 |
|------|------|----------|
| **寻址** | Agent ID | TODO中包含target_agent字段 |
| **路由** | 目录服务 | project_state.yaml中Agent注册表 |
| **感知** | Webhook | 文件变更推送给相关Agent |
| **确认** | Git commit | commit message中ACK |
| **状态同步** | Git | 状态文件同步 |
| **可靠传输** | Git | Git本身保证 |

### 5.2 Agent注册表

```yaml
# project_state.yaml
agents:
  agent1:
    role: PRODUCT_MANAGER
    status: active
  agent2:
    role: DEVELOPMENT_LEAD
    status: active
```

### 5.3 消息格式

**TODO创建**：

```yaml
message:
  id: TODO-1to2-025
  type: TASK_CREATED
  content: "实现前端模块X"
  target_agent: agent2
  created_by: agent1
  created_at: 2026-02-16T10:00:00
  ack_required: true
```

**ACK确认**：

```yaml
message:
  id: TODO-1to2-025
  type: TASK_ACKNOWLEDGED
  acknowledged_by: agent2
  acknowledged_at: 2026-02-16T10:05:00
```

**状态变更**：

```yaml
message:
  id: TODO-1to2-025
  type: STATUS_CHANGED
  old_status: pending
  new_status: completed
  changed_by: agent2
  changed_at: 2026-02-16T11:00:00
```

---

## 六、刚性约束层设计

### 6.1 与刚性框架的关系

TODO系统受刚性框架约束：

| 刚性规则 | TODO约束 |
|----------|----------|
| RF-001 自验收 | TODO完成不能由创建者标记 |
| RF-002 里程碑跳过 | TODO依赖未完成则里程碑不能推进 |
| RF-003 共谋 | 审批需要交叉验证 |
| RF-004 数据伪造 | TODO内容需符合模板规范 |

### 6.2 依赖强检

**前置依赖校验**：

```python
def complete_milestone(milestone):
    # 检查所有关联TODO是否完成
    for todo in get_todos_for_milestone(milestone):
        if todo.status != "completed":
            raise MilestoneBlockedError(
                f"前置TODO未完成: {todo.id}"
            )
```

### 6.3 生命周期状态机

```
┌──────────┐     assign     ┌────────────┐     complete     ┌──────────┐
│  draft   │ ──────────────→│   pending  │ ──────────────→ │completed│
└──────────┘                └────────────┘                  └──────────┘
     ↑                         │                              │
     │                         │ cancel                        │
     └─────────────────────────┴──────────────────────────────┘
```

**刚性约束**：
- `pending → completed` 只能由target_agent操作
- `pending → completed` 需要验收证据（CI日志、测试报告）
- 创建者不能自己完成自己创建的TODO（RF-001）

### 6.4 审计日志

```yaml
# audit_log.yaml
- timestamp: 2026-02-16T10:00:00
  event: TODO_CREATED
  todo_id: TODO-1to2-025
  actor: agent1
  target: agent2

- timestamp: 2026-02-16T11:00:00
  event: TODO_COMPLETED
  todo_id: TODO-1to2-025
  actor: agent2
  evidence: ci_log_url
```

---

## 七、数据模型

### 7.1 TODO字段定义

```yaml
todo:
  # 标识
  id: TODO-1to2-025           # 编号（创建者to接收者）
  
  # 通信
  target_agent: agent2          # 接收者
  created_by: agent1            # 创建者
  ack_required: true           # 是否需要确认
  
  # 应用
  content: "实现XX功能"        # 内容
  source: REQUIREMENT          # 来源
  priority: high               # 优先级
  type: REQUIREMENT            # 类型
  
  # 流程
  status: pending              # 状态
  depends_on:                 # 前置依赖
    - TODO-1to2-010
  milestones:                 # 关联里程碑
    - development
  
  # 验收
  acceptance_criteria: ""      # 验收标准
  evidence: ""                # 完成证据
  
  # 模板
  template: REQUIREMENT        # 使用的模板
  
  # 时间
  created_at: 2026-02-16T10:00:00
  updated_at: 2026-02-16T11:00:00
  completed_at: 
  due_at:                     # 截止时间（SLA）
```

### 7.2 状态枚举

| 状态 | 说明 | 可转换到 |
|------|------|----------|
| draft | 草稿 | pending |
| pending | 待处理 | completed, cancelled |
| in_progress | 处理中 | completed, cancelled |
| completed | 已完成 | closed |
| cancelled | 已取消 | - |
| closed | 已关闭 | - |

---

## 八、实施计划

### 8.1 版本规划

| 版本 | 内容 | 优先级 |
|------|------|--------|
| **v2.3.1** | TODO编号优化 + 来源标签 | P0 |
| **v2.3.2** | TODO模板系统 | P1 |
| **v2.4** | 通信层增强（ACK、Webhook） | P1 |
| **v2.5** | 刚性约束整合 | P0 |

### 8.2 详细计划

#### v2.3.1 (P0)

| 功能 | 说明 | 工时 |
|------|------|------|
| TODO编号优化 | 1to2-xxx格式 | 4h |
| 向后兼容 | 旧格式兼容 | 2h |
| 来源标签 | source字段 | 3h |
| 筛选支持 | 按来源筛选 | 2h |

#### v2.3.2 (P1)

| 功能 | 说明 | 工时 |
|------|------|------|
| 模板定义 | 模板YAML定义 | 4h |
| 自动填充 | 事件触发填充 | 4h |
| 模板管理 | CRUD支持 | 3h |

#### v2.4 (P1)

| 功能 | 说明 | 工时 |
|------|------|------|
| Agent注册表 | project_state.yaml | 3h |
| ACK确认 | commit message ACK | 3h |
| Webhook感知 | 实时推送 | 6h |
| 状态变更通知 | 推送给创建者 | 4h |

#### v2.5 (P0)

| 功能 | 说明 | 工时 |
|------|------|------|
| 依赖强检 | 前置未完成阻断 | 6h |
| 生命周期约束 | 状态机强制 | 4h |
| 审计日志 | 完整记录 | 6h |
| 自验收阻断 | 创建者不能完成自己的TODO | 4h |

---

## 九、与刚性框架的集成点

### 9.1 集成矩阵

| 刚性规则 | TODO集成点 | 实现方式 |
|----------|------------|----------|
| RF-001 自验收 | 完成校验 | actor != created_by |
| RF-002 里程碑跳过 | 依赖检查 | depends_on全部completed |
| RF-003 共谋 | 审批校验 | 需要验收证据 |
| RF-004 数据伪造 | 模板校验 | 内容符合模板规范 |

### 9.2 响应处理

| 场景 | 刚性响应 | TODO行为 |
|------|----------|----------|
| 自验收尝试 | R1-阻止 | 提示"不能完成自己创建的TODO" |
| 依赖未完成 | R1-阻止 | 提示"前置TODO未完成" |
| 无验收证据 | R2-警告 | 允许但记录日志 |
| 模板不匹配 | R2-警告 | 允许但记录 |

---

## 十、预期收益

| 收益 | 说明 |
|------|------|
| **消除歧义** | 编号明确体现创建者和接收者 |
| **可追溯** | TODO来源清晰，可追溯任务来源 |
| **可靠通信** | ACK机制确保送达 |
| **流程可控** | 刚性约束防止流程失范 |
| **审计完整** | 所有操作有记录可查 |

---

## 十一、风险与应对

| 风险 | 应对措施 |
|------|----------|
| 编号格式变化大 | 向后兼容旧格式 |
| 自动创建过于频繁 | 可配置开关 |
| 刚性约束过严 | 保留豁免通道 |
| 通信延迟 | Webhook实时推送 |

---

## 十二、关联文档

| 文档 | 关系 |
|------|------|
| PROPOSAL_2026-02-016 | 应用层设计（本文整合） |
| PROPOSAL_2026-02-017 | 通信层设计（本文整合） |
| PROPOSAL_2026-02-020 | 刚性框架实施 |
| CORE_ARCHITECTURE | TODO系统架构 |
| ROADMAP_oc-collab | 版本规划 |

---

**提案状态**: DRAFT  
**下一步**: Agent1评审 → 合并分散提案 → 纳入开发计划
