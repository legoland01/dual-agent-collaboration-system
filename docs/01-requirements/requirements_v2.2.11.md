# 需求规格说明书：oc-collab v2.2.11

**版本**: v2  
**创建日期**: 2026-02-14  
**作者**: Agent 1 (产品经理)  
**版本号**: 2.2.11  
**状态**: APPROVED

---

## 1. 概述

### 1.1 版本信息

| 项目 | 值 |
|------|-----|
| 前置版本 | v2.2.10 |
| 变更类型 | Bug修复 + 功能增强 |

### 1.2 核心原则

| 原则 | 说明 |
|------|------|
| 范围控制 | 本版本聚焦3个核心功能，总工时 ≤ 40h |
| 可靠性优先 | 解决协作流程中的痛点问题 |
| CLI边界 | 只做CLI能做的事情 |

### 1.3 本周期主题

**主题**: 协作流程可靠性增强

聚焦解决：
1. TODO编号冲突问题
2. Skill不遵循问题
3. StateNotifier不完整问题

---

## 2. 功能需求

### 2.1 F-TODO-001: Agent独立TODO编号机制

**来源**: BUG-20260214-007, PROPOSAL-2026-02-006

**描述**: 每个Agent维护独立的TODO编号，彻底解决编号冲突问题。编号规则见 `oc_collab_todo_dependency_check` skill v1.1。

**验收标准**:
- [ ] Agent1创建TODO使用编号格式 TODO-1-XXX
- [ ] Agent2创建TODO使用编号格式 TODO-2-XXX
- [ ] todowrite自动识别当前Agent并生成正确编号
- [ ] 两个Agent同时创建不会冲突
- [ ] 现有TODO可以迁移到新格式
- [ ] 历史TODO编号保持兼容
- [ ] 提供迁移脚本，自动重编号现有TODO
- [ ] 迁移前自动备份state/agent_adhoc_todos.yaml
- [ ] 迁移失败时可回滚到备份文件

**依赖**: `oc_collab_todo_dependency_check` skill v1.1+

**工时**: 8h

---

### 2.2 F-SKILL-001: Skill强制执行+Compliance

**来源**: BUG-20260214-005, PROPOSAL-2026-02-004, PROPOSAL-2026-02-007

**描述**: 将Skill检查集成到CLI命令中，无法绕过；支持TODO中嵌入Skill切片

**验收标准**:
- [ ] todowrite执行前强制检查相关Skill
- [ ] signoff执行前强制检查相关Skill
- [ ] 移除--auto-check可选参数
- [ ] Skill模板可以一键导入
- [ ] 符合AGENTS.md规则要求
- [ ] todowrite支持 `--embed-skill` 参数，自动从Skill提取关键规则嵌入TODO
- [ ] 嵌入的Skill切片包含：操作步骤、禁止项、验收标准
- [ ] Agent收到带Skill切片的TODO时，无需主动查询即可执行

**工时**: 12h

---

### 2.3 F-NOTIF-001: StateNotifier Receiver

**来源**: PROPOSAL-2026-02-005

**描述**: 实现StateNotifier完整功能，让notification真正可用

**验收标准**:
- [ ] HTTP接收器可以接收Webhook通知
- [ ] 消息队列持久化存储（JSON文件），支持重启后恢复
- [ ] Agent启动时检查未读通知
- [ ] CLI提示用户有新通知
- [ ] 通知状态可追踪（已读/未读/已处理）
- [ ] 队列支持重试机制，处理失败的通知

**工时**: 10h

---

## 3. CLI 命令清单

### 3.1 变更命令

| 命令 | 变更 | 工时 |
|------|------|------|
| `oc-collab todowrite` | 强制Skill检查，Agent独立编号 | 3h |
| `oc-collab signoff` | 强制Skill检查 | 2h |
| `oc-collab todo list` | Agent独立编号显示 | 2h |

### 3.2 新增命令

| 命令 | 说明 | 工时 |
|------|------|------|
| `oc-collab init --skill-template <standard>` | 导入Skill模板 | 2h |

---

## 4. 工时预估

| 功能 | 工时 |
|------|------|
| F-TODO-001 | 8h |
| F-SKILL-001 | 12h |
| F-NOTIF-001 | 10h |
| CLI命令 | 5h |
| 测试验收 | 5h |
| **总计** | **40h** |

---

## 5. 依赖关系

| 功能 | 依赖 | 被依赖 |
|------|------|--------|
| F-TODO-001 | StateNotifier (v2.2.8) | - |
| F-SKILL-001 | SkillEnforcer (v2.2.6) | - |
| F-NOTIF-001 | StateNotifier (v2.2.8) | - |

---

## 6. 风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 现有项目迁移失败 | 低 | 高 | 提供迁移脚本和备份机制 |
| CLI命令行为变更 | 中 | 中 | 保留兼容性 |
| Skill模板不完整 | 低 | 中 | 分阶段创建 |

---

## 7. 推迟的功能

以下功能推迟到后续版本：

| 功能 | 来源 | 推迟原因 |
|------|------|----------|
| 逆向验证评审 | F-REVIEW-001 | v3.0考虑 |
| 部署自动化 | F-AUTO-001 | v3.0考虑 |

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

### 评审条件（已确认）

| # | 条件 | 确认内容 | 状态 |
|---|------|----------|------|
| 1 | 定义Skill识别规则 | F-SKILL-001增加Skill嵌入TODO规范 | ✅ 已满足 |
| 2 | 确认队列持久化需求 | F-NOTIF-001增加JSON文件持久化、重试机制 | ✅ 已满足 |
| 3 | 补充迁移回滚策略 | F-TODO-001增加备份+回滚机制 | ✅ 已满足 |

---

## 9. 关联文档

| 文档 | 说明 |
|------|------|
| docs/01-requirements/ANALYSIS_v2.2.11_Requirements_Analysis.md | 需求分析报告 |
| docs/04-proposals/PROPOSAL-2026-02-006_agent_todo_numbering.md | Agent独立TODO编号提案 |
| docs/04-proposals/PROPOSAL-2026-02-007_skill_enforcement.md | Skill强制执行提案 |
| docs/04-proposals/PROPOSAL-2026-02-005_state_notifier_receiver.md | StateNotifier Receiver提案 |
| docs/06-roadmap/ROADMAP_oc-collab.md | 产品路线图 |

---

**文档版本**: v2
**创建日期**: 2026-02-14
**修订日期**: 2026-02-14
**状态**: APPROVED
