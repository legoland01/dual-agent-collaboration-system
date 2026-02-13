# 需求规格说明书：oc-collab v2.2.9

**版本**: v1
**创建日期**: 2026-02-14
**作者**: Agent 1 (产品经理)
**版本号**: 2.2.9
**状态**: DRAFT

---

## 零、核心架构参考

| 功能ID | 功能名称 | 架构模块 | 映射路径 | 优先级 |
|--------|----------|----------|----------|--------|
| F-WEB-INT-001 | StateNotifier集成到todowrite | 10.3 Webhook通知 | 核心架构 → 10.3 | P0 |
| F-WEB-INT-002 | StateNotifier集成到signoff | 10.3 Webhook通知 | 核心架构 → 10.3 | P0 |
| F-WEB-INT-003 | StateNotifier集成到phase_advance | 10.3 Webhook通知 | 核心架构 → 10.3 | P0 |
| F-AUTO-005 | 自动Bug检测机制 | 6.2 签署流程 | 核心架构 → 6.2 | P0 |
| F-COMP-001 | Agent Compliance CLI准入检查 | 6.1 角色边界 | 核心架构 → 6.1 | P0 |
| F-INIT-002 | 规则自动加载 | 9.1 Skill加载 | 核心架构 → 9.1 | P1 |
| F-DEPLOY-002 | 部署文档同步自动化 | 5.1 版本发布 | 核心架构 → 5.1 | P1 |
| F-WEB-006 | Webhook状态通知增强 | 10.3 Webhook通知 | 核心架构 → 10.3 | P2 |

---

## 1. 概述

### 1.1 版本信息

| 项目 | 值 |
|------|-----|
| 前置版本 | v2.2.8 |
| 变更类型 | 功能增强 + Bug修复 |

### 1.2 核心原则

| 原则 | 说明 |
|------|------|
| 范围控制 | 本版本聚焦8个功能，总工时33h |
| CLI边界 | 只做CLI能做的事情 |
| 开发延续 | 补全v2.2.8未竟的Webhook集成 |
| 用户体验 | 减少手动通知负担 |

### 1.3 版本背景

v2.2.8开发了StateNotifier模块，但未集成到工作流。本版本补全集成，并增加合规性和自动化能力。

---

## 2. 功能需求

### 2.1 F-WEB-INT-001: StateNotifier集成到todowrite

**来源**: ANALYSIS_v2.2.9_Requirements_Analysis.md (B-004)

**描述**: todowrite创建TODO后，自动发送Webhook通知

**验收标准**:
- [ ] todowrite执行成功后，StateNotifier.notify_todo_created被调用
- [ ] 通知Payload包含todo_id、content、agent_id
- [ ] Webhook URL已配置时，HTTP POST成功
- [ ] Webhook URL未配置时，不报错（静默跳过）
- [ ] Agent2能通过Webhook收到TODO创建通知

**工时**: 3h

---

### 2.2 F-WEB-INT-002: StateNotifier集成到signoff

**来源**: ANALYSIS_v2.2.9_Requirements_Analysis.md (B-004)

**描述**: signoff签署完成后，自动发送Webhook通知

**验收标准**:
- [ ] signoff命令执行成功后，StateNotifier.notify_signoff_completed被调用
- [ ] 通知Payload包含stage、agent_id
- [ ] Webhook URL已配置时，HTTP POST成功
- [ ] Webhook URL未配置时，不报错（静默跳过）
- [ ] Agent2能通过Webhook收到签署通知

**工时**: 2h

---

### 2.3 F-WEB-INT-003: StateNotifier集成到phase_advance

**来源**: ANALYSIS_v2.2.9_Requirements_Analysis.md (B-004)

**描述**: phase_advance推进阶段后，自动发送Webhook通知

**验收标准**:
- [ ] phase_advance执行成功后，StateNotifier.notify_phase_advanced被调用
- [ ] 通知Payload包含from_phase、to_phase、agent_id
- [ ] Webhook URL已配置时，HTTP POST成功
- [ ] Webhook URL未配置时，不报错（静默跳过）
- [ ] Agent2能通过Webhook收到阶段推进通知

**工时**: 2h

---

### 2.4 F-AUTO-005: 自动Bug检测机制

**来源**: PROPOSAL-2026-02-002 (P-002)

**描述**: 关键操作后自动检测异常并触发Bug报告

**验收标准**:
- [ ] TODO完成时，自动检查文档状态是否更新
- [ ] 评审完成时，自动检查签署是否完成
- [ ] 命令执行后，返回值异常时自动报告Bug
- [ ] 文件编辑后，格式错误时自动报告Bug
- [ ] 自动生成的Bug报告包含：type、description、related_todo
- [ ] Agent意识到"遇到问题应该先报Bug"

**工时**: 8h

---

### 2.5 F-COMP-001: Agent Compliance CLI准入检查

**来源**: PROPOSAL-2026-02-004 (P-004)

**描述**: Agent1无法执行todowrite/todoedit，强制创建TODO

**验收标准**:
- [ ] Agent1执行todowrite时，返回拒绝提示
- [ ] 拒绝提示包含：正确做法（创建TODO）
- [ ] Agent2正常执行todowrite，不受影响
- [ ] 违规行为记录到state/compliance_violations.yaml
- [ ] `oc-collab compliance report`显示合规率

**工时**: 7h

---

### 2.6 F-INIT-002: 规则自动加载

**来源**: PROPOSAL-2026-02-001 (P-001)

**描述**: oc-collab init时自动生成AGENTS.md和skills目录

**验收标准**:
- [ ] `oc-collab init`命令生成AGENTS.md
- [ ] `oc-collab init`命令生成skills/目录（包含全部skill）
- [ ] `oc-collab rules init`命令初始化规则
- [ ] 项目可覆盖默认规则
- [ ] Compaction后规则不丢失

**工时**: 5h

---

### 2.7 F-DEPLOY-002: 部署文档同步自动化

**来源**: BUG-20260214-001 (B-003)

**描述**: 部署前自动检查并同步CHANGELOG和README

**验收标准**:
- [ ] 部署前检查CHANGELOG.md是否包含当前版本
- [ ] 部署前检查README.md是否包含新命令
- [ ] 未同步时，阻止部署并提示
- [ ] 同步后，允许继续部署
- [ ] 文档同步命令可手动执行

**工时**: 3h

---

### 2.8 F-WEB-006: Webhook状态通知增强

**来源**: StateNotifier功能增强

**描述**: Webhook通知增加状态追踪和重试机制

**验收标准**:
- [ ] 通知发送失败时，自动重试1次
- [ ] 重试失败后，记录到日志
- [ ] `oc-collab webhook status`显示通知统计
- [ ] 通知Payload包含唯一ID，便于追踪

**工时**: 3h

---

## 3. CLI 命令清单

### 3.1 新增命令

| 命令 | 说明 | 工时 |
|------|------|------|
| `oc-collab compliance check` | 检查当前Agent合规状态 | 1h |
| `oc-collab compliance report` | 生成合规报告 | 1h |
| `oc-collab rules init [--force]` | 初始化框架规则 | 2h |
| `oc-collab deploy check-docs` | 检查部署文档同步 | 1h |
| `oc-collab webhook status` | 显示Webhook通知统计 | 1h |

### 3.2 变更命令

| 命令 | 变更 | 工时 |
|------|------|------|
| `oc-collab todowrite` | 集成StateNotifier | 3h |
| `oc-collab signoff` | 集成StateNotifier | 2h |
| `oc-collab phase-advance` | 集成StateNotifier | 2h |

### 3.3 变更行为

| 命令 | 变更 | 说明 |
|------|------|------|
| `oc-collab todowrite` | Agent1禁用 | Agent1执行时返回拒绝提示 |
| `oc-collab todoedit` | Agent1禁用 | Agent1执行时返回拒绝提示 |

---

## 4. 工时预估

| 功能ID | 功能名称 | 工时 |
|--------|----------|------|
| F-WEB-INT-001 | StateNotifier集成到todowrite | 3h |
| F-WEB-INT-002 | StateNotifier集成到signoff | 2h |
| F-WEB-INT-003 | StateNotifier集成到phase_advance | 2h |
| F-AUTO-005 | 自动Bug检测机制 | 8h |
| F-COMP-001 | Agent Compliance CLI准入检查 | 7h |
| F-INIT-002 | 规则自动加载 | 5h |
| F-DEPLOY-002 | 部署文档同步自动化 | 3h |
| F-WEB-006 | Webhook状态通知增强 | 3h |
| - | 测试 + 修复 | 预留5h |
| **总计** | | **38h** |

**说明**: 预留5h用于测试和修复，总工时控制在38h内。

---

## 5. 依赖关系

| 功能 | 依赖 | 被依赖 |
|------|------|--------|
| F-WEB-INT-001 | StateNotifier模块(v2.2.8) | - |
| F-WEB-INT-002 | StateNotifier模块(v2.2.8) | - |
| F-WEB-INT-003 | StateNotifier模块(v2.2.8) | - |
| F-AUTO-005 | 无 | - |
| F-COMP-001 | StateManager | - |
| F-INIT-002 | 无 | - |
| F-DEPLOY-002 | 无 | - |
| F-WEB-006 | StateNotifier模块(v2.2.8) | - |

---

## 6. 风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| StateNotifier集成导致性能问题 | 低 | 中 | 异步发送，失败静默 |
| Agent1禁用todowrite影响体验 | 中 | 低 | 提供清晰的错误提示 |
| 自动Bug检测误报 | 中 | 低 | 敏感度可配置 |
| Webhook通知失败率高 | 中 | 低 | 重试机制+日志记录 |

---

## 7. 推迟的功能

本版本无推迟功能。所有v2.2.9规划功能均纳入开发范围。

历史推迟功能记录在 [PARKED_v2.2.9_features.md](PARKED_v2.2.9_features.md)

---

## 8. 签署确认

### Agent 1 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-14 | ✅ |

### Agent 2 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-14 | 技术评审通过（有条件） |

#### 评审意见

**评审结论: 技术评审通过（有条件）**

**1. 阅读理解:**
- 正确理解v2.2.8未竟的StateNotifier集成需求
- F-AUTO-005自动Bug检测意图清晰

**2. 完整性:**
- 8个功能验收标准覆盖正常流程
- ⚠️ 异常流程覆盖不足（StateNotifier失败时、重试策略未明确）

**3. 一致性:**
- 与v2.2.8 StateNotifier设计一致
- ⚠️ F-COMP-001禁用Agent1的todowrite，与现有Skill冲突需确认

**4. 可测试性:**
- 验收标准大多可验证
- ⚠️ F-AUTO-005"自动检测异常"定义模糊

**5. 可行性:**
- 技术方案可行
- ⚠️ 38h工时偏高，建议拆分版本

**6. 逆向挑刺:**
- F-AUTO-005范围过大，可能超出Scope
- Agent1禁用todowrite可能影响协作效率

**7. 评审结论:**
- 技术评审通过（有条件）
- **保留意见**:
  1. 工时需控制在25h内，建议拆分F-AUTO-005到v2.2.10
  2. F-COMP-001禁用规则需与Agent1确认
  3. F-AUTO-005验收标准需更具体

---

**文档版本**: v1
**创建日期**: 2026-02-14
**修订日期**: 2026-02-14
**状态**: REVIEWED
