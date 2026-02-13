# 概要设计说明书：oc-collab v2.2.9

**版本**: v1
**创建日期**: 2026-02-14
**作者**: Agent 1 (产品经理)
**版本号**: 2.2.9
**状态**: DRAFT

---

## 1. 功能模块概览

### 1.1 功能模块清单

| 模块 | 子功能 | 描述 | 优先级 |
|------|--------|------|--------|
| **Webhook集成** | StateNotifier集成todowrite | 自动发送TODO创建通知 | P0 |
| **Webhook集成** | StateNotifier集成signoff | 自动发送签署完成通知 | P0 |
| **Webhook集成** | StateNotifier集成phase_advance | 自动发送阶段推进通知 | P0 |
| **自动化能力** | 自动Bug检测机制 | 关键操作后自动检测异常 | P0 |
| **合规性增强** | Agent Compliance CLI准入 | Agent1禁用todowrite/todoedit | P0 |
| **规则管理** | 规则自动加载 | init时生成AGENTS.md和skills | P1 |
| **部署增强** | 部署文档同步自动化 | 部署前检查CHANGELOG/README | P1 |
| **Webhook增强** | Webhook状态通知增强 | 重试机制+状态追踪 | P2 |

### 1.2 功能模块图

```
┌─────────────────────────────────────────────────────────────────┐
│                      v2.2.9 功能架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐                                               │
│  │  StateNotifier │ ◄──┬── todowrite集成 (P0)                      │
│  │   (核心引擎)   │    ├── signoff集成 (P0)                       │
│  └──────┬───────┘    └── phase_advance集成 (P0)                  │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Webhook通知增强 (P2)                          │   │
│  │         重试机制 + 状态追踪 + Payload增强                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Agent Compliance (P0)                        │   │
│  │        Agent1 todowrite/todoedit 准入检查                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              自动Bug检测机制 (P0)                           │   │
│  │      TODO完成/评审完成/命令执行 → 异常检测 → Bug报告         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────┐    ┌─────────────────────────────────────┐   │
│  │ 规则自动加载 │    │ 部署文档同步 (P1)                    │   │
│  │   (P1)      │    │ CHANGELOG/README 自动检查             │   │
│  └──────────────┘    └─────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 功能模块关系

### 2.1 调用关系

| 调用方 | 被调用方 | 说明 |
|--------|----------|------|
| todowrite | StateNotifier | 创建TODO后发送通知 |
| signoff | StateNotifier | 签署完成后发送通知 |
| phase_advance | StateNotifier | 阶段推进后发送通知 |
| compliance_check | StateNotifier | 发送合规检查通知 |
| auto_bug_detector | StateNotifier | Bug报告发送通知 |
| deploy_check | compliance_violations | 检查合规违规记录 |

### 2.2 数据依赖

| 数据提供方 | 数据使用方 | 数据类型 |
|------------|----------|----------|
| StateNotifier | Webhook | 通知Payload (JSON) |
| compliance_engine | StateNotifier | 违规记录 |
| auto_bug_detector | docs/00-memos/ | Bug报告 |
| deploy_check | CHANGELOG/README | 版本记录 |

### 2.3 时序关系

| 功能A | 功能B | 说明 |
|-------|-------|------|
| StateNotifier | Webhook增强 | 先有StateNotifier，再增强 |
| Agent Compliance | 自动Bug检测 | 合规违规触发Bug报告 |
| 规则自动加载 | Agent Compliance | 规则加载后启用合规检查 |
| 部署文档同步 | 版本发布 | 先同步文档，再发布 |

---

## 3. 产品路线图定位

### 3.1 路线图位置

| 版本 | 功能 | 状态 |
|------|------|------|
| v2.2.8 | Webhook基础 (EventDispatcher/StateNotifier/HMACValidator) | 已完成 |
| **v2.2.9** | **Webhook集成 + 合规增强 + 自动化** | **当前版本** |
| v2.3.0 | Agent协作增强（待定） | 待开发 |
| v3.0 | 逆向验证评审/Agent身份识别等 | 远期规划 |

### 3.2 本版本解决的问题

**核心价值**：
```
补全v2.2.8未竟的Webhook集成
+ 强制执行Agent角色边界
+ 建立"遇到问题先报Bug"的意识
```

**关键改进**：
- Agent1给Agent2发Todo后，Agent2自动收到Webhook通知
- Agent1无法执行todowrite（强制创建TODO）
- 关键操作后自动检测异常并生成Bug报告

---

## 4. 用户故事/场景

### 4.1 用户故事

| ID | 故事描述 | 验收标准 | 优先级 |
|----|----------|----------|--------|
| US-001 | Agent1创建TODO，Agent2自动收到通知 | Webhook通知包含todo_id和content | P0 |
| US-002 | Agent1签署评审，Agent2自动收到通知 | Webhook通知包含stage和agent_id | P0 |
| US-003 | Agent1尝试执行todowrite，被拒绝 | 返回清晰提示，强制创建TODO | P0 |
| US-004 | Agent1尝试执行todoedit，被拒绝 | 返回清晰提示，强制创建TODO | P0 |
| US-005 | TODO完成但文档未更新，自动报Bug | Bug报告包含type和description | P0 |
| US-006 | oc-collab init时自动生成规则 | AGENTS.md和skills目录已生成 | P1 |
| US-007 | 部署前自动检查文档同步 | 未同步则阻止部署 | P1 |
| US-008 | Webhook通知失败时自动重试 | 重试1次后记录日志 | P2 |

### 4.2 使用场景

| 场景 | 触发条件 | 主要步骤 | 预期结果 |
|------|----------|----------|----------|
| **S-001: Agent1发Todo** | Agent1执行todowrite | 1. todowrite执行<br>2. StateNotifier发送通知<br>3. Agent2收到Webhook | Agent2收到TODO创建通知 |
| **S-002: Agent1被禁用** | Agent1执行todowrite | 1. Agent1执行命令<br>2. 合规检查拦截<br>3. 返回拒绝提示 | Agent1看到"请创建TODO"提示 |
| **S-003: 自动报Bug** | TODO完成但文档未更新 | 1. TODO完成检查<br>2. 文档状态验证<br>3. 自动生成Bug报告 | Bug报告出现在docs/00-memos/ |
| **S-004: 部署前检查** | 执行deploy命令 | 1. 检查CHANGELOG<br>2. 检查README<br>3. 未同步则阻止 | 提示同步文档后才能部署 |

---

## 5. 外部接口定义

### 5.1 与外部系统的交互

| 外部系统 | 接口类型 | 数据方向 | 说明 |
|----------|----------|----------|------|
| GitHub/Gitee | Webhook | 双向 | 接收push事件，发送通知 |
| Claude AI | API | 单向 | Agent调用 |

### 5.2 数据交换格式

**StateNotifier通知Payload**:

```json
{
  "event_type": "todo_created|signoff_completed|phase_advanced|bug_detected",
  "timestamp": "2026-02-14T00:00:00Z",
  "agent_id": "agent1|agent2",
  "data": {
    "todo_id": "TODO-xxx",
    "content": "xxx",
    "stage": "requirements|design|development|testing|deployment",
    "from_phase": "testing",
    "to_phase": "deployment",
    "bug_type": "DOCUMENT_STATUS_NOT_UPDATED",
    "description": "xxx"
  },
  "webhook_id": "uuid-v4"
}
```

---

## 6. 约束与假设

### 6.1 产品约束

| 约束类型 | 约束内容 | 影响范围 |
|----------|----------|----------|
| 性能 | Webhook通知 < 100ms | StateNotifier集成 |
| 可用性 | 未配置Webhook时不报错 | 所有集成点 |
| 安全性 | HMAC签名验证 | Webhook通知 |

### 6.2 技术假设

| 假设 | 验证方式 | 不成立时的应对 |
|------|----------|----------------|
| Webhook URL已配置 | webhook status命令检查 | 静默跳过，不报错 |
| HMAC密钥已生成 | webhook init检查 | 静默跳过 |
| skills目录存在 | init命令检查 | 自动创建 |

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

**评审结论: 技术评审通过**

**1. 阅读理解:**
- 8个功能模块清晰，用户故事和验收标准完整
- StateNotifier集成逻辑正确

**2. 完整性:**
- 功能模块图完整，调用/数据/时序关系明确
- 外部接口定义清晰（Webhook Payload格式）

**3. 一致性:**
- 与v2.2.9需求文档一致
- 合规性增强与F-COMP-001匹配

**4. 可测试性:**
- 用户故事有验收标准
- 场景有预期结果

**5. 可行性:**
- StateNotifier已实现，技术可行
- F-AUTO-005自动Bug检测范围可能过大

**6. 逆向挑刺:**
- Agent1禁用todowrite可能影响协作效率
- F-AUTO-005验收标准需在详细设计中细化

**7. 评审结论:**
- 技术评审通过
- **保留意见**:
  1. F-AUTO-005详细设计时需明确"异常检测"边界
  2. 合规禁用规则需确保有清晰的错误提示

---

**文档版本**: v1
**创建日期**: 2026-02-14
**状态**: APPROVED
