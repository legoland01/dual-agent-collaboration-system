# 概要设计说明书：oc-collab v2.2.11

**版本**: v1
**创建日期**: 2026-02-14
**作者**: Agent 1 (产品经理)
**版本号**: v2.2.11
**状态**: DRAFT

---

## 1. 功能模块概览

### 1.1 功能模块清单

| 模块 | 子功能 | 描述 | 优先级 |
|------|--------|------|--------|
| **M1: TODO编号管理** | 独立编号机制 | Agent1使用TODO-1-XXX，Agent2使用TODO-2-XXX | P0 |
| **M1: TODO编号管理** | 迁移工具 | 自动将现有TODO迁移到新格式 | P0 |
| **M1: TODO编号管理** | 备份回滚 | 迁移前备份，失败时可回滚 | P0 |
| **M2: Skill强制执行** | 命令集成检查 | todowrite/signoff执行前强制检查Skill | P0 |
| **M2: Skill强制执行** | 移除--auto-check | 将可选参数改为强制行为 | P0 |
| **M2: Skill强制执行** | Skill模板导入 | init命令支持一键导入Skill模板 | P1 |
| **M2: Skill强制执行** | Skill嵌入TODO | todowrite支持--embed-skill参数嵌入Skill规则 | P0 |
| **M3: StateNotifier Receiver** | HTTP接收器 | 提供Webhook端点接收外部通知 | P0 |
| **M3: StateNotifier Receiver** | 队列持久化 | JSON文件持久化存储，支持重启恢复 | P0 |
| **M3: StateNotifier Receiver** | 启动检查 | Agent启动时检查未读通知 | P0 |
| **M3: StateNotifier Receiver** | 重试机制 | 处理失败的通知自动重试 | P1 |

### 1.2 功能模块图

```
oc-collab CLI
├── 命令层
│   ├── todowrite ──┬──→ SkillEnforcer ──→ StateNotifier
│   │               │        ↓
│   │               └──→ 编号生成器 ──→ TodoStore
│   │
│   ├── signoff ──────→ SkillEnforcer ──→ StateNotifier
│   │
│   ├── todo list ────→ 编号格式化
│   │
│   └── init ──────────→ Skill模板库
│
├── 通知层
│   ├── StateNotifier ──→ HTTP接收器 → 队列持久化
│   │        ↓
│   └── Agent启动检查器 → CLI提示
│
└── 存储层
    ├── TodoStore (YAML)
    ├── StateQueue (JSON)
    └── Skill库
```

---

## 2. 功能模块关系

### 2.1 调用关系

| 调用方 | 被调用方 | 说明 |
|--------|----------|------|
| todowrite | SkillEnforcer | 执行前检查相关Skill |
| todowrite | 编号生成器 | 生成Agent独立编号 |
| todowrite | TodoStore | 持久化TODO |
| todowrite | StateNotifier | 发送TODO创建通知 |
| signoff | SkillEnforcer | 执行前检查相关Skill |
| signoff | StateNotifier | 发送签署完成通知 |
| init | Skill模板库 | 导入预定义Skill |
| Agent启动检查器 | StateQueue | 检查未读通知 |
| Agent启动检查器 | CLI提示 | 显示通知数量 |

### 2.2 数据依赖

| 数据提供方 | 数据使用方 | 数据类型 |
|------------|------------|----------|
| TodoStore | todowrite | TODO列表 (YAML) |
| TodoStore | todo list | 格式化显示 |
| StateQueue | StateNotifier | 待处理通知 (JSON) |
| Skill库 | SkillEnforcer | Skill定义 |
| Skill库 | todowrite | Skill切片嵌入 |

### 2.3 时序关系

| 功能A | 功能B | 说明 |
|-------|-------|------|
| 编号生成器 | TodoStore | 编号生成后才能持久化 |
| SkillEnforcer | todowrite | Skill检查通过后才能执行 |
| 队列持久化 | StateNotifier | 持久化完成后才能标记发送成功 |
| Skill模板导入 | Skill库 | 导入后Skill才能被引用 |

---

## 3. 产品路线图定位

### 3.1 路线图位置

| 版本 | 功能 | 状态 |
|------|------|------|
| v2.2.8 | StateNotifier基础、EventDispatcher | 已完成 |
| v2.2.9 | StateNotifier集成todowrite/signoff | 已完成 |
| v2.2.10 | StateNotifier队列、Agent启动检查器 | 已完成 |
| **v2.2.11** | **TODO编号独立、Skill强制执行、Receiver** | **当前版本** |
| v2.2.12 | 逆向验证评审 | 待开发 |
| v2.3.0 | 多Agent自动化协同 | 待开发 |

### 3.2 本版本解决的问题

**核心价值**: 解决双Agent协作流程中的可靠性和规范性问题

| 问题 | 解决方案 |
|------|----------|
| TODO编号冲突导致YAML损坏 | Agent独立编号格式 |
| Skill查询规则不遵循 | 命令集成强制检查 |
| StateNotifier无法接收外部通知 | HTTP接收器+持久化队列 |

### 3.3 与前后版本关系

| 前置版本 | 功能依赖 | 后置版本 |
|----------|----------|----------|
| v2.2.10 | StateNotifier队列基础 | v2.2.12 |
| v2.2.10 | Agent启动检查器 | - |
| v2.2.6 | SkillEnforcer | - |

---

## 4. 用户故事/场景

### 4.1 用户故事

| ID | 故事描述 | 验收标准 | 优先级 |
|----|----------|----------|--------|
| US-001 | 作为Agent1，我希望能创建TODO而不与Agent2冲突 | 使用TODO-1-XXX格式，Agent2使用TODO-2-XXX | P0 |
| US-002 | 作为Agent2，我希望收到TODO时能直接看到Skill规范 | todowrite --embed-skill自动嵌入规则 | P0 |
| US-003 | 作为Agent1，我希望强制检查Skill遵循情况 | todowrite执行前自动检查，无--auto-check可选 | P0 |
| US-004 | 作为Agent，我希望系统能持久化通知队列 | 重启后未读通知不丢失 | P0 |
| US-005 | 作为Agent，我希望迁移TODO时能备份回滚 | 迁移失败时可恢复到备份 | P0 |

### 4.2 使用场景

| 场景 | 触发条件 | 主要步骤 | 预期结果 |
|------|----------|----------|----------|
| **场景1: TODO创建** | Agent执行todowrite创建任务 | 1. 执行todowrite --content "xxx"<br>2. 系统自动生成TODO-1-XXX格式<br>3. 检查相关Skill<br>4. 持久化到YAML<br>5. 发送StateNotifier通知 | TODO创建成功，编号唯一 |
| **场景2: Skill嵌入** | Agent使用todowrite --embed-skill | 1. 执行todowrite --content "xxx" --embed-skill skill_name<br>2. 系统提取Skill关键规则<br>3. 嵌入TODO内容<br>4. 持久化 | TODO包含Skill规范内容 |
| **场景3: 签署检查** | Agent执行signoff签署 | 1. 执行signoff --phase xxx<br>2. 系统检查相关Skill<br>3. Skill检查通过才能签署 | 签署前强制Skill检查 |
| **场景4: 外部通知接收** | 外部系统发送Webhook | 1. POST /webhook/state发送到HTTP端点<br>2. 解析通知内容<br>3. 持久化到队列<br>4. 标记发送方成功 | 通知进入待处理队列 |
| **场景5: Agent启动** | Agent启动CLI | 1. 检查StateQueue未读通知<br>2. 显示通知数量<br>3. 提示用户查看 | CLI显示通知提示 |
| **场景6: TODO迁移** | 管理员执行迁移脚本 | 1. 备份现有YAML<br>2. 解析所有TODO<br>3. 添加Agent前缀<br>4. 验证无冲突<br>5. 保存新格式 | 迁移成功，无数据丢失 |

---

## 5. 外部接口定义

### 5.1 与外部系统的交互

| 外部系统 | 接口类型 | 数据方向 | 说明 |
|----------|----------|----------|------|
| Claude AI | 消息传递 | 双向 | todowrite生成TODO发送给AI |
| GitHub | Webhook | 入站 | StateNotifier接收外部通知 |
| 用户终端 | CLI | 双向 | 命令行交互 |

### 5.2 StateNotifier Receiver接口

```json
// HTTP POST /webhook/state
{
  "event_type": "state_change",
  "source_agent": "agent1",
  "target_agent": "agent2",
  "payload": {
    "todo_id": "TODO-1-001",
    "action": "created",
    "content": "评审v2.2.11需求文档",
    "priority": "P0",
    "skill_ref": "oc_collab_requirements_review_guide"
  },
  "timestamp": "2026-02-14T10:00:00Z",
  "hmac_signature": "sha256=..."
}
```

### 5.3 StateQueue数据格式

```json
// state/state_queue.json
{
  "queue_id": "q-001",
  "notifications": [
    {
      "id": "notif-001",
      "status": "pending",
      "retry_count": 0,
      "max_retries": 3,
      "received_at": "2026-02-14T10:00:00Z",
      "payload": {
        "type": "todo_created",
        "data": { ... }
      }
    }
  ],
  "last_updated": "2026-02-14T10:00:00Z"
}
```

### 5.4 TODO编号格式

```
Agent1创建: TODO-1-001, TODO-1-002, ...
Agent2创建: TODO-2-001, TODO-2-002, ...
迁移格式:   TODO-XXX → TODO-[agent_id]-XXX
```

---

## 6. 约束与假设

### 6.1 产品约束

| 约束类型 | 约束内容 | 影响范围 |
|----------|----------|----------|
| 范围控制 | 本版本只做CLI能做的事情，不做Web UI | 功能边界 |
| 兼容性 | 现有TODO编号保持兼容（无需强制迁移） | 迁移策略 |
| 性能 | 单次操作响应时间 < 1s | 用户体验 |
| 可靠性 | 队列持久化必须成功，失败时告警 | 通知系统 |

### 6.2 技术假设

| 假设 | 验证方式 | 不成立时的应对 |
|------|----------|----------------|
| JSON文件持久化足够可靠 | 测试重启恢复 | 升级为SQLite |
| 单实例运行 | 检查state文件锁 | 支持多实例需改用数据库 |
| HMAC签名验证由发送方负责 | 文档说明 | 增加本地签名验证选项 |
| Skill切片嵌入不超过TODO长度限制 | 测试验证 | 截断或分片 |

### 6.3 风险点

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 现有TODO迁移冲突 | 低 | 高 | 提供备份+手动修复 |
| CLI行为变更导致现有脚本失效 | 中 | 中 | 保留兼容性参数 |
| StateQueue文件损坏 | 低 | 高 | 自动重建+告警 |

---

## 7. 签署确认

### Agent 1 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-14 | ✅ |

### Agent 2 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-14 | 技术评审通过 |

---

**文档版本**: v1
**创建日期**: 2026-02-14
**修订日期**: 2026-02-14
**状态**: APPROVED
