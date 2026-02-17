# Proposal: TODO系统独立（全局共享）

**提案编号**: PROPOSAL_2026-02-027  
**日期**: 2026-02-17  
**作者**: Consultant (战略规划)  
**状态**: DRAFT

---

## 一、背景

### 1.1 问题

当前oc-collab中TODO系统存在以下问题：
- TODO只在单项目内使用
- 不支持跨项目任务分发
- Agent需要手动切换项目
- 无法感知其他项目Agent的状态

### 1.2 研究结论

根据`RESEARCH_Multi_Project_Collaboration.md`的研究结论：
- TODO系统应该独立出来，作为全局共享服务
- 支持跨项目任务传递
- 支持Agent注册和状态感知

---

## 二、架构设计

### 2.1 新的架构分层

```
┌─────────────────────────────────────────────┐
│            PM-Agent (单点入口)               │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│            TODO系统（全局独立）               │
│  - Agent注册表                               │
│  - 跨项目路由                                │
│  - 积压队列                                  │
└────────────────────┬────────────────────────┘
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│oc-collab │   │oc-collab │   │oc-collab │
│ 项目A    │   │ 项目B    │   │ 项目C    │
└──────────┘   └──────────┘   └──────────┘
```

### 2.2 TODO系统核心功能

| 功能 | 说明 |
|------|------|
| **Agent注册** | Agent启动时自动注册（ID、项目、状态） |
| **跨项目路由** | sender-to-receiver规则自动寻址 |
| **积压队列** | Agent离线时保存TODO |
| **上线拉取** | Agent上线后先处理积压 |

---

## 三、详细设计

### 3.1 Agent注册

**注册信息**：
```yaml
agent_registry:
  agent1@项目A:
    id: agent1
    project: 项目A
    role: PRODUCT_MANAGER
    status: online
    registered_at: 2026-02-17T12:00:00
  agent2@项目B:
    id: agent2
    project: 项目B
    role: DEVELOPMENT_LEAD
    status: offline
```

### 3.2 TODO路由

**编号格式**：
- 项目内: `TODO-1-001`（Agent1创建）
- 跨项目: `TODO-A1→B2-001`（项目A的Agent1给项目B的Agent2）

**路由规则**：
```
1. TODO系统接收请求
2. 解析sender和receiver
3. 查表：receiver是否online
4. online → 立即推送
5. offline → 存入积压队列
```

### 3.3 积压队列

```yaml
backlog_queue:
  agent2@项目B:
    - todo_id: TODO-A1→B2-001
      sender: agent1@项目A
      created_at: 2026-02-17T12:00:00
    - todo_id: TODO-A1→B2-002
      sender: agent1@项目A
      created_at: 2026-02-17T12:05:00
```

---

## 四、与oc-collab的关系

### 4.1 oc-collab的职责

| 职责 | 说明 |
|------|------|
| 项目内流程 | Agent1+2的工作流 |
| 签署 | 阶段门禁 |
| Skill | 工作标准 |
| Git/部署 | 自动化 |

### 4.2 TODO系统的职责

| 职责 | 说明 |
|------|------|
| Agent注册 | 管理所有Agent状态 |
| 任务传递 | 跨项目TODO分发 |
| 积压管理 | 离线消息保存 |

### 4.3 整合方式

Agent session启动时：
1. 自动连接TODO服务
2. 注册到Agent注册表
3. 拉取积压队列中的TODO
4. 开始处理任务

---

## 五、实施计划

### v2.3.1: 核心功能

| 功能 | 工时 | 优先级 |
|------|------|--------|
| Agent注册表 | 3h | P0 |
| 跨项目路由 | 4h | P0 |
| 积压队列 | 3h | P1 |

### v2.3.2: CLI整合

| 功能 | 工时 | 优先级 |
|------|------|--------|
| 自动注册 | 3h | P0 |
| 状态感知 | 2h | P1 |
| 上线拉取 | 2h | P1 |

---

## 六、风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| TODO服务单点故障 | 全局影响 | 后期考虑高可用 |
| 网络延迟 | 实时性 | 本地缓存优化 |
| 离线时间过长 | 积压过多 | 定期清理机制 |

---

## 七、关联文档

| 文档 | 说明 |
|------|------|
| RESEARCH_Multi_Project_Collaboration.md | 研究结论 |
| ROADMAP_oc-collab.md | 版本规划 |

---

**提案状态**: DRAFT
