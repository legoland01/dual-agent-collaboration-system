# 需求规格说明书：oc-collab v2.2.4

**版本**: v2
**创建日期**: 2026-02-08
**作者**: Agent 1 (产品经理)
**版本号**: v2.2.4
**状态**: READY

---

## 1. 概述

### 1.1 版本信息

| 项目 | 值 |
|------|-----|
| 前置版本 | v2.2.3 |
| 变更类型 | 功能增强 |
| 分析报告 | ANALYSIS_v2.2.4_Requirements_Analysis.md |

### 1.2 核心原则

| 原则 | 说明 |
|------|------|
| 范围控制 | 本版本聚焦6个核心功能，总工时14h |
| 强制约束 | Skill + 代码配合，实现强制检查机制 |
| Git统一 | 所有Git操作通过CLI统一入口 |

### 1.3 版本目标

v2.2.4 目标：从"框架"升级为"系统"

核心改进：
1. 强制约束机制（Skill + 代码配合）
2. Git操作统一入口
3. 完整性自动检查

---

## 2. 功能需求

### 2.1 FR-SKILL-001: Skill强制加载检查

**来源**: Q-001 (PROPOSAL_v2.2.3_Skill_Based_Review)

**描述**: 在CLI命令执行前，强制检查相关Skill是否已加载

**验收标准**:
- [ ] 新Session执行`oc-collab`命令时，自动检测需要的Skill
- [ ] Skill未加载时，提示用户并提供加载命令
- [ ] 提供`oc-collab skill check`命令手动检查
- [ ] 单元测试覆盖边界情况（无Skill、部分加载、全加载）

**工时**: 2h

---

### 2.2 FR-GIT-001: Git提交命令

**来源**: Q-002 (PROPOSAL_v2.2.3_Git_Commit_Command)

**描述**: 提供统一的Git提交入口，规范commit message格式

**验收标准**:
- [ ] `oc-collab git commit`命令引导用户选择变更类型
- [ ] 自动生成符合规范的commit message
- [ ] 支持`--all`参数提交所有变更
- [ ] 支持`--message`参数直接指定消息
- [ ] 执行前验证状态（无未追踪文件、无冲突）

**工时**: 3h

---

### 2.3 FR-GIT-002: 强制签署检查

**来源**: Q-002 (PROPOSAL_v2.2.3_Git_Commit_Command)

**描述**: Git提交前强制验证签署是否完整

**验收标准**:
- [ ] `oc-collab git commit`执行前检查相关签署
- [ ] 签署不完整时拒绝提交，提示缺失项
- [ ] 支持`--force`参数跳过检查（仅紧急情况）
- [ ] 记录强制签署检查日志

**工时**: 2h

---

### 2.4 FR-AUTO-001: 需求完整性检查

**来源**: Q-004 (MEMO-2026-02-007)

**描述**: CLI自动检查需求文档的完整性，检测缺失项

**验收标准**:
- [ ] `oc-collab check requirements`命令检查需求文档
- [ ] 验证必须章节是否齐全（概述、功能需求、CLI清单、工时、依赖、签署）
- [ ] 验证验收标准是否完整（每个功能至少有3项）
- [ ] 验证工时预估总和与明细一致
- [ ] 输出完整性报告，标记缺失项

**工时**: 3h

---

### 2.5 FR-AUTO-002: 阶段推进门槛

**来源**: Q-005 (MEMO-2026-02-007)

**描述**: 阶段推进时强制验证前置条件

**验收标准**:
- [ ] `oc-collab phase advance`命令推进阶段
- [ ] 推进前检查前置条件（签署、测试、文档）
- [ ] 验证当前阶段所有任务已完成
- [ ] 条件不满足时阻止推进并说明原因
- [ ] 支持`--force`参数强制推进（记录日志）

**工时**: 2h

---

### 2.6 FR-AUTO-003: 评审结果执行

**来源**: Q-012 (MEMO-2026-02-008)

**描述**: 评审结论强制关联state状态，防止违规推进

**验收标准**:
- [ ] Critical Review结论为"不通过"时，锁定需求状态
- [ ] 锁定状态下无法进入下一阶段
- [ ] `oc-collab review resolve`命令处理锁定
- [ ] 记录评审结果与状态变更的关联

**工时**: 2h

---

## 3. CLI 命令清单

### 3.1 新增命令

| 命令 | 说明 | 工时 |
|------|------|------|
| `oc-collab skill check` | 检查Skill加载状态 | 2h |
| `oc-collab git commit` | 统一Git提交入口 | 3h |
| `oc-collab git commit --force` | 跳过签署检查 | 0h (FR-GIT-002) |
| `oc-collab check requirements` | 检查需求完整性 | 3h |
| `oc-collab phase advance` | 阶段推进（含门槛检查） | 2h |
| `oc-collab review resolve` | 解除评审锁定 | 2h |

### 3.2 变更命令

| 命令 | 变更 |
|------|------|
| 无 | - |

---

## 4. 工时预估

| 功能 | 工时 |
|------|------|
| FR-SKILL-001: Skill强制加载检查 | 2h |
| FR-GIT-001: Git提交命令 | 3h |
| FR-GIT-002: 强制签署检查 | 2h |
| FR-AUTO-001: 需求完整性检查 | 3h |
| FR-AUTO-002: 阶段推进门槛 | 2h |
| FR-AUTO-003: 评审结果执行 | 2h |
| **小计** | **14h** |
| 测试 + 修复 | 3h |
| **总计** | **17h** |

---

## 5. 依赖关系

### 5.1 功能依赖

| 功能 | 依赖 | 说明 |
|------|------|------|
| FR-SKILL-001 | src/cli/main.py | CLI入口 |
| FR-GIT-001 | src/core/git.py, src/core/state_manager.py | Git操作 + 签署检查 |
| FR-GIT-002 | src/core/state_manager.py | 签署状态验证 |
| FR-AUTO-001 | src/core/state_manager.py | 状态检查 |
| FR-AUTO-002 | src/core/state_manager.py | 阶段状态验证 |
| FR-AUTO-003 | src/core/state_manager.py | 评审状态管理 |

### 5.2 调用关系

```
FR-GIT-001 (Git提交命令)
    ├── 调用 src/core/git.py 执行实际提交
    └── 调用 FR-GIT-002 进行签署检查
```

---

## 6. 风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| Skill加载检查误判 | 中 | 中 | 提供手动跳过参数，增加单元测试覆盖 |
| Git提交与IDE冲突 | 低 | 中 | 明确CLI仅作封装，不替代原生Git |
| 阶段推进门槛过严 | 中 | 低 | 提供`--force`强制推进，记录审计日志 |

---

## 7. Skill更新（无需代码）

以下功能已用Skill覆盖，无需代码开发：

| 功能 | Skill | 状态 |
|------|-------|------|
| 实质性评审检查 | oc_collab_requirements_review_guide | ✅ 已覆盖 |
| 评审优先级规则 | oc_collab_requirements_review_guide | ✅ 已覆盖 |
| Agent职责边界 | oc_collab_requirements_guide | ✅ 已覆盖 |
| 协作流程规范 | oc_collab_collaboration_guide | ✅ 已覆盖 |
| 需求编写模板 | oc_collab_requirements_guide | ✅ 已覆盖 |
| 测试验收流程 | oc_collab_test_acceptance_guide | ✅ 已覆盖 |
| 开发指南 | oc_collab_development_guide | ✅ 已覆盖 |
| 需求-代码追溯 | oc_collab_development_guide | ✅ 已覆盖 |
| 文档同步规范 | oc_collab_test_acceptance_guide | ✅ 已覆盖 |

---

## 8. 推迟的功能

以下功能推迟到v2.3.0：

| 功能 | 原因 |
|------|------|
| 需求版本自动管理 | 手动管理当前可行 |
| 推迟功能自动转移 | 优先级低 |
| Skill版本管理 | 当前手动记录足够 |
| 多场景评审 | 单一场景当前够用 |

---

## 9. 签署确认

### Agent 1 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-08 | ✅ |

### Agent 2 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | | ⏳ |

---

## 版本历史

| 版本 | 日期 | 作者 | 变更 |
|------|------|------|------|
| v1 | 2026-02-08 | Agent 1 | 初始版本 |
| v2 | 2026-02-08 | Agent 1 | 自检修复：依赖关系重构 |

---

**文档版本**: v2
**创建日期**: 2026-02-08
**修订日期**: 2026-02-08
**状态**: READY
