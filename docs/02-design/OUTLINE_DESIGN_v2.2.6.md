# 概要设计说明书：oc-collab v2.2.6

**版本**: v1
**创建日期**: 2026-02-09
**作者**: Agent 1 (产品经理)
**关联需求**: requirements_v2.2.6.md
**版本号**: v2.2.6
**状态**: DRAFT

---

## 1. 功能模块概览

### 1.1 v2.2.6 功能模块图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        oc-collab v2.2.6 智能辅助架构                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                     CLI 命令层 (v2.2.6 新增/增强)                            │ │
│  ├─────────────────────────────────────────────────────────────────────────────┤ │
│  │  原有命令                        │ 新增命令                                  │ │
│  │  ├─ init, status, .a           │ ├─ skill search --keywords <kw>        │ │
│  │  ├─ review, signoff, todo       │ ├─ skill slice --level <chapter>       │ │
│  │  ├─ phase-advance, git          │ ├─ skill enforce --before-action       │ │
│  │  └─ todowrite (增强)            │ └─ todowrite --auto-check (增强)       │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                              │
│                                    ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                         核心功能模块                                          │ │
│  │                                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐│ │
│  │  │  【v2.2.6新增】智能辅助模块                                             ││ │
│  │  │  ├─ AutoChecker: todowrite参数自动检查 [v2.2.6]                       ││ │
│  │  │  ├─ ContextCarrier: TODO上下文携带 [v2.2.6]                           ││ │
│  │  │  ├─ ConflictDetector: 冲突检测 [v2.2.6]                               ││ │
│  │  │  └─ SkillSearcher: Skill检索增强 [v2.2.6]                             ││ │
│  │  └─────────────────────────────────────────────────────────────────────────┘│ │
│  │                                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐│ │
│  │  │  现有模块（本次有修改）                                                  ││ │
│  │  │  ├─ TodoSyncManager: todowrite增强 [v2.2.6]                           ││ │
│  │  │  └─ SkillManager: Skill检索增强 [v2.2.6]                              ││ │
│  │  └─────────────────────────────────────────────────────────────────────────┘│ │
│  │                                                                              │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 v2.2.6 功能清单

| 功能模块 | 功能 | 类型 | 工时 | 状态 |
|----------|------|------|------|------|
| 智能辅助模块 | AutoChecker (todowrite参数检查) | 新增 | 2h | 待开发 |
| 智能辅助模块 | ContextCarrier (上下文携带) | 新增 | 2h | 待开发 |
| 智能辅助模块 | ConflictDetector (冲突检测) | 新增 | 2h | 待开发 |
| Skill模块 | SkillSearcher (检索增强) | 新增 | 3h | 待开发 |
| Skill模块 | SkillSlicer (切片机制) | 新增 | 3h | 待开发 |
| Skill模块 | SkillEnforcer (强制查找) | 新增 | 3h | 待开发 |
| Skill更新 | F-PROC (行为规范) | Skill | 2h | 待更新 |

---

## 2. 详细设计任务分配

### 2.1 Agent 2 负责（详细设计）

| 功能 | 详细设计文档 | 工时 |
|------|-------------|------|
| AutoChecker | DETAIL-2026-02-F-AI_AutoChecker.md | 2h |
| ContextCarrier | DETAIL-2026-02-F-AI_ContextCarrier.md | 2h |
| ConflictDetector | DETAIL-2026-02-F-AI_ConflictDetector.md | 2h |
| SkillSearcher | DETAIL-2026-02-F-SKILL_SkillSearcher.md | 3h |
| SkillSlicer | DETAIL-2026-02-F-SKILL_SkillSlicer.md | 3h |
| SkillEnforcer | DETAIL-2026-02-F-SKILL_SkillEnforcer.md | 3h |

### 2.2 Agent 1 负责（Skill更新）

| 功能 | 目标文档 | 工时 |
|------|---------|------|
| F-PROC-001 | oc_collab_collaboration_guide | 1h |
| F-PROC-002 | oc_collab_collaboration_guide | 1h |

---

## 3. 依赖关系

### 3.1 模块依赖

```
AutoChecker ──┬──→ TodoSyncManager
              │
ContextCarrier ──→ TodoSyncManager, ProjectContext
              │
ConflictDetector ──→ TodoSyncManager
              │
SkillSearcher ──┬──→ SkillManager
                │
SkillSlicer ─────→ SkillManager
                │
SkillEnforcer ──→ REQUIRED_SKILLS, skills/  # v2.2.4已有，不依赖ActionDetector
```

### 3.2 外部依赖

- 无外部依赖
- 所有功能可在当前代码库内实现

---

## 4. 测试策略

### 4.1 测试分工

| 测试类型 | 执行人 | 范围 |
|----------|--------|------|
| 白盒测试 | Agent 2 | AutoChecker, ContextCarrier, SkillSearcher等 |
| 黑盒测试 | Agent 1 | CLI命令完整流程 |

### 4.2 验收测试

- 每个功能独立验收
- 支持独立发布

---

## 5. 里程碑

| 里程碑 | 内容 | 时间点 |
|--------|------|--------|
| M1 | todowrite参数检查 + 上下文携带 | 第1-3天 |
| M2 | Skill检索 + 强制查找 | 第4-6天 |
| M3 | Agent行为规范（Skill更新） | 第7天 |
| M4 | 测试验收 | 第8天 |

---

**创建人**: Agent 1
**日期**: 2026-02-09
**状态**: DRAFT → 待Agent1确认

---

## Agent 2 评审意见（2026-02-09）

### 阅读理解
- ✅ 模块图清晰
- ✅ 任务分配明确

### 完整性
- ✅ 依赖关系完整
- ✅ 里程碑合理

### 一致性
- ✅ 与需求文档对齐

### 待确认
- SkillEnforcer → REQUIRED_SKILLS, skills/ 替代 ActionDetector ✅ 已修正

### 结论
✅ 技术评审通过（有条件）
- 条件：确认 SkillEnforcer 依赖修正为 REQUIRED_SKILLS, skills/ 目录

---

**Agent 1 修正（2026-02-09）**：
- ActionDetector 模块不存在，已修正依赖关系
- v2.2.4 SkillEnforcer 实际依赖 REQUIRED_SKILLS 字典 + skills/ 目录
