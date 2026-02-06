# 需求规格说明书：oc-collab v2.2.1

**版本**: v3
**创建日期**: 2026-02-02
**作者**: Agent 1 (产品经理)
**版本号**: 2.2.1
**状态**: DRAFT (草稿) → 待 Agent 2 评审

---

## 1. 概述

### 1.1 版本信息

| 项目 | 值 |
|------|-----|
| 当前版本 | v2.2.0 |
| 上一版本 | v2.1.0 |
| 变更类型 | 缺陷修复 + 功能增强 + 协作机制改进 |

### 1.2 变更动机

v2.2.0 发布后，发现以下问题需要修复：

| 问题来源 | 问题描述 | 严重程度 | 修复方式 |
|----------|----------|----------|----------|
| Agent 2 | 签署后不自动同步 | LOW | 功能增强 |
| Agent 1 | 签署流程不规范 | P1 | 流程改进 |
| **协作实践** | **Agent 新会话不知道 oc-collab 存在** | **P0** | **v2.2.0 BUG 修复 - 会话起始引导** |
| 协作实践 | Agent 搞不清角色和职责 | P1 | Skill 自动加载 |
| 协作实践 | 不知道另一个 Agent 在做什么 | P1 | 困惑信号检测 |
| 协作实践 | 独自决策，跳过协作流程 | P1 | 职责边界提醒 |
| 协作实践 | 不知道项目的仓库配置 | P2 | 动态仓库配置 |
| **协作实践** | **变更载体不明确** | **P2** | **明确 PRD/RFC 角色分工** |
| **协作实践** | **Agent 间任务管理混乱** | **P2** | **任务单 + 范围检查** |

### 1.3 主要变更

1. **签署自动同步**: `oc-collab signoff` 添加 `--sync` 选项
2. **签署流程改进**: 规范化签署模板和检查清单
3. **会话起始引导**: Agent 新会话自动显示角色职责和使用指南
4. **变更载体明确化**: 明确 PRD 与 RFC 的角色分工（可只用 PRD 承载变更，无需 RFC）
5. **任务管理机制**: 任务单 + 版本范围检查 + Agent 自主验证
6. **双代理认知免疫系统**:
   - 困惑信号检测
   - 协作指南 Skill 自动加载
   - 职责边界提醒
   - 动态仓库配置

---

## 2. 功能需求

### 2.1 状态合规检查

**需求编号**: FR-STATE-001

**问题背景**:
当前 oc-collab 的文档状态（如 DRAFT/READY/APPROVED）只存在于文档标题中的人工标记，系统无法自动识别和控制文档状态。这导致以下问题：
- DRAFT 状态的文档可能被错误地送入评审
- 签署流程无法自动检查前置条件
- 质量门禁依赖人工检查，容易遗漏

**解决方案**:

#### 2.1.1 文档状态机

**描述**: oc-collab 管理所有文档的状态，状态流转由系统自动控制。

**状态定义**:
| 状态 | 说明 | 允许的操作 |
|------|------|------------|
| DRAFT | 草稿阶段 | 编辑 |
| READY | 待评审 | 评审、编辑 |
| IN_REVIEW | 评审中 | 评审 |
| APPROVED | 已批准 | 签署、后续流程 |
| REJECTED | 已拒绝 | 编辑、重新提交 |

**状态流转规则**:
```
DRAFT → READY: 解除草稿状态（人工指令）
READY → IN_REVIEW: 开始评审（评审命令）
IN_REVIEW → APPROVED: 评审通过（签署）
IN_REVIEW → REJECTED: 评审拒绝（拒签）
REJECTED → DRAFT: 打回草稿（重新编辑）
```

#### 2.1.2 自动状态检查

**描述**: 在执行评审、签署等关键命令前，系统自动检查前置文档状态。

**检查规则**:
```python
STATE_COMPLIANCE_RULES = {
    "review_requires_ready": True,      # 评审前必须 READY
    "signoff_requires_approved": True,  # 签署前必须 APPROVED
    "draft_cannot_review": True,        # DRAFT 状态不能评审
    "draft_cannot_signoff": True,       # DRAFT 状态不能签署
}
```

**触发命令**:
| 命令 | 检查项 | 不通过处理 |
|------|--------|------------|
| oc-collab review | 文档状态必须为 READY | 阻止并提示 |
| oc-collab signoff | 文档状态必须为 APPROVED | 阻止并提示 |
| oc-collab phase-advance | 前置阶段必须 APPROVED | 阻止并提示 |

**错误消息示例**:
```
❌ 无法执行评审：文档处于 DRAFT 状态
   当前状态: DRAFT
   所需状态: READY
   操作: 请先解除 DRAFT 状态（oc-collab document release）

❌ 无法执行签署：文档处于 IN_REVIEW 状态
   当前状态: IN_REVIEW
   所需状态: APPROVED
   操作: 请等待评审完成
```

#### 2.1.3 数据存储

**描述**: 文档状态存储在 `state/document_states.yaml` 统一管理。

**存储格式**:
```yaml
# state/document_states.yaml
documents:
  - id: requirements_v2.2.1
    path: docs/01-requirements/requirements_v2.2.1_READY.md
    status: READY
    updated_at: 2026-02-05T12:00:00
    history:
      - status: DRAFT
        timestamp: 2026-02-02T10:00:00
      - status: READY
        timestamp: 2026-02-05T12:00:00
```

**审计追踪**:
- 状态变更自动记录 `timestamp` 和变更原因
- 支持 `oc-collab document history --file xxx` 查看历史

```bash
# 解除 DRAFT 状态，进入 READY
oc-collab document release --file requirements_v2.2.1.md

# 查看文档状态
oc-collab document status --file requirements_v2.2.1.md

# 查看所有文档状态
oc-collab document list --show-status
```

#### 2.1.4 验收标准

| 标准 | 验证方式 |
|------|----------|
| 文档状态机正确 | 状态流转测试 |
| DRAFT 状态不能评审 | CLI 测试 |
| DRAFT 状态不能签署 | CLI 测试 |
| 错误消息清晰 | 代码审查 |

---

### 2.2 签署自动同步

**需求编号**: FR-SIGNOFF-AUTO-001

**问题背景**:
签署流程当前存在手动步骤，容易遗漏同步操作。签署后不会自动同步到远程，可能导致本地签署完成但远程没有更新的问题。

**当前流程**:
```bash
oc-collab signoff requirements  # 只更新本地 state
# 需要手动执行：
oc-collab push                  # 才推送到远程
```

**解决方案**:

#### 2.1.1 `--sync` 选项

**描述**: 在 `oc-collab signoff` 命令中添加 `--sync` 选项，签署后自动同步到远程。

**命令格式**:
```bash
oc-collab signoff requirements --sync
oc-collab signoff design --sync
oc-collab signoff milestone --name M5 --sync
```

**行为**:
1. 执行签署操作
2. 更新本地 state 文件
3. 自动执行 `oc-collab push`
4. 显示同步结果

**输出示例**:
```
✓ 签署成功: M5 里程碑
✓ 已同步到远程仓库
提交: abc1234
```

#### 2.1.2 `auto_sync` 配置

**描述**: 在配置文件中设置 `auto_sync: true`，默认行为自动同步。

**配置格式** (`config.yaml`):
```yaml
signoff:
  auto_sync: true  # 签署后自动推送到远程
```

**优先级**: `--sync` 命令行选项 > 配置文件 > 默认行为

**默认行为**: 不自动同步（需要显式指定 `--sync` 或配置 `auto_sync: true`）

#### 2.3.1 签署模板标准化

**描述**: 在评审报告中标准化签署模板格式。

**模板格式**:
```markdown
## 签署确认

### Agent 2 (开发负责人) 评审意见

**评审日期**: YYYY-MM-DD
**评审结果**: ✅ 同意 / ❌ 需修改

**评审意见**:
- ...

### 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 产品负责人 | Agent 1 | YYYY-MM-DD | ✅ 已签署 |
| 开发负责人 | Agent 2 | YYYY-MM-DD | ✅ 已签署 |

**签署后状态**: APPROVED (已批准) / PENDING (待签署)
```

#### 2.3.2 签署检查清单

**描述**: Agent 1 在完成评审后应检查：

- [ ] 报告中是否有签署确认表格
- [ ] 表格中 Agent 1 是否已签署
- [ ] 表格中 Agent 2 是否已签署
- [ ] 签署记录是否保存到 `state/signoffs/`
- [ ] 签署后状态是否为 "APPROVED"

#### 2.3.3 签署记录持久化

**描述**: 签署记录应保存到 `state/signoffs/` 目录。

**文件格式**:
```yaml
# state/signoffs/sig_M1_20260202.yaml
signoff_id: SIG-M1-20260202
milestone: M1
phase: integration_testing
signers:
  - role: 产品负责人
    agent: Agent 1
    timestamp: 2026-02-02T12:00:00
    status: approved
  - role: 开发负责人
    agent: Agent 2
    timestamp: 2026-02-02T12:05:00
    status: approved
status: APPROVED
created_at: 2026-02-02T12:00:00
```

#### 2.3.4 签署流程改进验收标准

| FR 编号 | 验收标准 | 验证方式 |
|---------|----------|----------|
| FR-SIGNOFF-IMPROVE-001 | 签署模板格式正确 | 代码审查 |
| FR-SIGNOFF-IMPROVE-001 | 签署检查清单可执行 | CLI 测试 |
| FR-SIGNOFF-IMPROVE-003 | 签署记录正确保存到 state/signoffs/ | 集成测试 |
| FR-SIGNOFF-IMPROVE-003 | 签署记录可查询 | CLI 测试 |

---

### 2.4 签署记录持久化

**需求编号**: FR-SIGNOFF-IMPROVE-003

**描述**: 签署记录应保存到 `state/signoffs/` 目录。

**文件命名规范**: `sig_{milestone}_{timestamp}.yaml`

**文件格式** (`state/signoffs/sig_M1_20260202.yaml`):
```yaml
signoff_id: SIG-M1-20260202
milestone: M1
phase: integration_testing
signers:
  - role: 产品负责人
    agent: Agent 1
    timestamp: 2026-02-02T12:00:00
    status: approved
  - role: 开发负责人
    agent: Agent 2
    timestamp: 2026-02-02T12:05:00
    status: approved
status: APPROVED
created_at: 2026-02-02T12:00:00
```

**签署记录查询命令**:
```bash
# 查询所有签署记录
oc-collab signoff list

# 查询特定里程碑的签署记录
oc-collab signoff list --milestone M1

# 查看签署记录详情
oc-collab signoff show --id SIG-M1-20260202
```

---

### 2.4 变更载体明确化

**需求编号**: FR-CHANGE-CLARITY-001

**问题背景**:
在 financial_case_generator_system 项目中，出现变更载体不明确的问题：
- PRD 变更已评审签署，但 RFC 文档存在但无需单独评审
- Agent 不知道应该用 PRD 还是 RFC 承载变更
- 没有明确规则处理 PRD 和 RFC 的关系

**核心原则**：**需求变更仍需要流程**，但 RFC 不一定是独立流程。

**解决方案**:

#### 2.4.1 PRD 与 RFC 角色分工

**变更载体规则**:
| 场景 | 变更载体 | 是否需要签署流程 | 说明 |
|------|----------|------------------|------|
| 需求新增/重大变更 | PRD | ✅ 需要 | PRD 是变更的**主要载体**，必须评审签署 |
| 需求澄清/技术方案 | RFC | ✅ 需要 | RFC 是变更的**辅助载体**，独立议题需要评审 |
| PRD 已包含 RFC 内容 | PRD | ✅ PRD 评审即有效 | RFC 可作为**变更记录**，无需单独评审 |

**流程规则**:
```
需求变更 → PRD 更新 → PRD 评审签署 → 完成 ✅
            ↓
        (可选) RFC 创建 → 作为变更记录，无评审要求
```

**示例**:
| 场景 | PRD | RFC | 处理方式 |
|------|-----|-----|----------|
| 新增功能需求 | ✅ 第2.4节 | 可选 | PRD 评审签署即可 |
| 技术方案讨论 | ❌ | ✅ RFC-001 | RFC 评审签署 |
| PRD 已包含 RFC 内容 | ✅ | ✅ | PRD 评审有效，RFC 可作为记录 |

#### 2.4.2 流程合规检测

**描述**: 检测变更流程是否符合规范（**需求变更必须走流程**）。

**检测规则**:
```python
CHANGE_COMPLIANCE_RULES = {
    "prd_change_requires_signoff": True,   # PRD 变更必须签署
    "rfc_optional_when_prd_complete": True, # PRD 完整时 RFC 可选（作为记录）
    "conflict_detection": True,             # 检测 PRD/RFC 冲突
}
```

**检测场景**:
| 场景 | 检测逻辑 | 处理方式 |
|------|----------|----------|
| PRD 新增/修改 | 检查是否完成签署 | 未签署则**阻止开发** ⭐ |
| RFC 独立议题 | 检查是否完成签署 | 未签署则提醒 |
| PRD 与 RFC 冲突 | 检测内容一致性 | 提示冲突，人工解决 |

#### 2.4.3 冲突检测与解决

**冲突类型**:
| 冲突类型 | 示例 | 检测方式 |
|----------|------|----------|
| 内容冲突 | PRD 和 RFC 描述不一致 | 关键词对比 |
| 状态冲突 | PRD 已签署，RFC 待评审 | 状态对比 |
| 版本冲突 | 不同版本的内容混用 | 版本号检查 |

**冲突解决流程**:
```
冲突检测 → 冲突报告 → 人工确认 → 更新文档 → 重新签署（如需要）
```

**冲突报告示例**:
```
⚠️  检测到冲突

冲突类型: 内容不一致
文件: PRD v3.0 第2.4节 vs RFC-2026-02-001
差异: 
  - PRD: "主入口待设计"
  - RFC: "主入口已完成设计"

建议: 
  1. 检查哪个版本是最新的
  2. 更新落后的一方
  3. 如有重大变更，重新签署
```

#### 2.4.4 流程违规处理

**违规场景**:
| 违规场景 | 检测方式 | 处理方式 |
|----------|----------|----------|
| PRD 变更未签署 | 检查签署状态 | **提醒 + 确认** ⭐ |
| 基于未签署 PRD 开发 | 检查开发时间 vs 签署时间 | 提醒 + 确认 |
| 跳过评审直接开发 | 检查 RFC/PRD 状态 | 提醒 + 确认 |

**违规处理原则**:
- **PRD 未签署 = 提醒，但允许继续**（避免过度约束）
- **RFC 未签署 = 提醒，但允许继续**（软性约束）

**冲突检测处理**:
- 关键词对比可能产生误报，检测结果仅供参考
- 最终由人工判断并解决冲突

**违规处理代码**:
```python
def handle_violation(violation_type: str, context: dict) -> ViolationAction:
    """处理流程违规"""
    if violation_type == "UNSIGNED_PRD":
        return ViolationAction.WARN  # 提醒 PRD 未签署，需人工确认
    elif violation_type == "DEV_BEFORE_SIGNOFF":
        return ViolationAction.WARN  # 提醒开发前需签署
    elif violation_type == "SKIP_REVIEW":
        return ViolationAction.WARN  # 提醒需评审
```

**错误消息示例**:
```
⚠️ 警告：PRD 尚未签署
当前版本: v2.2.1
建议：请确认是否继续开发
操作: (c) 继续 / (q) 取消
```

#### 2.4.5 变更载体明确化验收标准

| FR 编号 | 验收标准 | 验证方式 |
|---------|----------|----------|
| FR-CHANGE-CLARITY-001 | PRD/RFC 角色分工明确 | 代码审查 |
| FR-CHANGE-CLARITY-001 | 流程合规检测可执行 | CLI 测试 |
| FR-CHANGE-CLARITY-001 | 冲突检测可执行 | CLI 测试 |
| FR-CHANGE-CLARITY-001 | 违规处理逻辑正确 | 代码审查 |

---

## 3. Ad-hoc To-do Items 机制

### 3.1 本质与定位

**需求编号**: FR-ADHOC-001

**问题背景**:
oc-collab 核心流程（需求→设计→开发→测试）提供了标准化的协作框架，但实际开发过程中常有需要 Agent 之间直接传达的特别要求，如跨阶段的评审请求、特殊情况处理、突发问题沟通等。这些需求无法完全标准化，但又必须得到执行落实。

**核心概念**:
```
┌─────────────────────────────────────────────────────────────┐
│  oc-collab 核心流程                                          │
│  ├── 需求阶段 → 评审                                         │
│  ├── 设计阶段 → 评审                                         │
│  ├── 开发阶段 → 实现                                         │
│  └── 测试阶段 → 验收                                         │
│                                                              │
│  Ad-hoc To-do Items（补充机制）                              │
│  └── 任意节点 → Agent 之间的一次性特别要求                     │
└─────────────────────────────────────────────────────────────┘
```

**Ad-hoc To-do Items = Agent 之间的一次性工作要求**

| 特性 | 说明 |
|------|------|
| 定位 | 核心流程之外的"灵活补充机制" |
| 触发 | 贯穿整个开发过程，任何阶段均可发布 |
| 范围 | 可跨版本、跨里程碑，一次性执行 |
| 发起者 | 任意 Agent |
| 执行者 | 指定的一个或多个 Agent |

### 3.2 与 oc-collab 核心流程的关系

| 类型 | 示例 | 说明 |
|------|------|------|
| oc-collab 核心流程 | 需求评审、设计评审、测试验收 | 标准化、流程化 |
| Ad-hoc To-do Items | "请评审这个 MEMO"、"确认这个 Bug 修复" | 灵活的、一次性的特别要求 |

**与现有 `todo` 命令的关系**:
| 命令 | 范围 | 生命周期 | 用途 |
|------|------|----------|------|
| `oc-collab todo` | 核心流程任务 | phase 内 | 跟踪当前阶段的任务 |
| `oc-collab todo make` | Ad-hoc 任务 | 跨版本 | Agent 之间的特别要求 |

**命令区分**:
- `todo`: 管理核心流程中的任务（如"实现功能 X"、"修复 Bug Y"）
- `todo make`: 创建 Ad-hoc Items（如"请评审这个 MEMO"）

### 3.3 生命周期管理

**状态流转**:
```
pending → in_progress → completed → confirmed
   ↓           ↓              ↓           ↓
  待执行     执行中         已完成       已确认
```

**状态说明**:
| 状态 | 说明 | 触发条件 |
|------|------|----------|
| pending | 待执行 | 发布时自动设置 |
| in_progress | 执行中 | 执行者标记开始执行 |
| completed | 已完成 | 执行者标记完成 |
| confirmed | 已确认 | 发布者确认后关闭 |

### 3.4 数据结构

**文件格式** (`state/agent_adhoc_todos.yaml`):
```yaml
adhoc_todos:
  - id: TODO-001
    from: agent1
    to: [agent2]
    description: 请评审 MEMO-2026-02-004
    status: pending  # pending/in_progress/completed/confirmed
    created_at: 2026-02-05T12:00:00
    started_at: null
    completed_at: null
    confirmed_at: null
```

### 3.5 命令设计

```bash
# 发布 Ad-hoc To-do Item
oc-collab todo make --to agent2 --desc "请评审 MEMO-2026-02-004"

# 查看分配给我的 Items
oc-collab todo list --assigned-to agent2

# 查看我发布的 Items
oc-collab todo list --from agent1

# 标记开始执行
oc-collab todo start --id TODO-001

# 标记完成
oc-collab todo complete --id TODO-001

# 确认完成（发布者操作）
oc-collab todo confirm --id TODO-001

# 检查发布的所有 Items（签署前自动触发）
oc-collab todo check --from agent1
```

### 3.6 与动态 Checklist 集成

**需求编号**: FR-ADHOC-002

**描述**: Ad-hoc To-do Items 与动态 checklist 集成，在签署前强制检查所有发布的 Items 是否已完成。

**动态 Checklist 集成方式**:
| 检查项 | 说明 | 触发条件 |
|--------|------|----------|
| 需求追溯 | 需求→设计→代码→测试关联 | 签署前 |
| **Ad-hoc To-do Items** | 查看我发布的 Items | 签署前 |
| 质量门禁 | 测试覆盖率、Bug 修复 | 签署前 |

**签署前检查输出示例**:
```
=== Dynamic Checklist ===

【需求追溯检查】
✓ FR-SIGNOFF-001 → DETAIL-2026-02-001 ✅
...

【Ad-hoc To-do Items 检查】
✓ TODO-001: "评审 MEMO-2026-02-004" (Agent 2) [已完成-待确认]
⚠ TODO-002: "确认 Bug 修复" (Agent 2) [已确认] ✅
  请确认 TODO-001 后再签署

【质量门禁检查】
✓ 测试覆盖率: 91% >= 80% ✅
...

=== 检查未通过 ===
请确认所有 Ad-hoc To-do Items 后再签署。
```

### 3.7 版本合规检查机制

**需求编号**: FR-ADHOC-003

**核心原则**: Ad-hoc To-do Items 本身不关联版本，但在执行时必须通过版本合规检查。

**版本合规检查**:
```
开发阶段检查点（任何时候）
        │
        ├── 检查所有指令是否合规：
        │   ├── 来自需求文档的 → ✅ 已签署则合规
        │   ├── 来自 Ad-hoc To-do Items 的 → 检查版本
        │   ├── 来自其他文档的 → 检查版本
        │   └── 来自人的输入的 → 检查版本
        │
        └── 不合规 → 阻止执行
```

**双重检查机制**:
| 检查点 | 说明 | 目的 |
|--------|------|------|
| 执行前检查 | Agent 执行 Ad-hoc Item 前 | 阻止不符合当前版本的指令 |
| 签署前检查 | 动态 checklist 中的独立检查项 | 确认所有工作符合当前版本 |

**执行前检查输出示例**:
```
=== 版本合规检查（执行前）===
⚠️ 此 Ad-hoc Item 可能超出当前版本范围
当前版本: v2.2.0
建议: 请确认是否继续执行
```

### 3.8 验收标准

| 标准 | 验证方式 |
|------|----------|
| Ad-hoc Item 可发布 | CLI 测试 |
| 生命周期状态流转正确 | CLI 测试 |
| 动态 checklist 集成 | CLI 测试 |
| 版本合规检查 | 集成测试 |
| 发布者确认机制 | CLI 测试 |

---

## 4. 动态 Checklist 机制

**需求编号**: FR-CHECKLIST-001

**问题背景**:
当前签署前的检查流程依赖人工记忆和手动验证，容易遗漏重要检查项。传统静态 checklist 无法适应不同项目阶段和交付物的变化，导致质量门控失效。

**解决方案**:

### 4.1 动态检查项生成

**FR-CHECKLIST-001**: 动态检查项生成器

**描述**: 根据评审对象的实际内容，由系统自动生成针对性的检查项，而非使用固定模板。

**命令格式**:
```bash
oc-collab review requirements --checklist
oc-collab review design --checklist
oc-collab review milestone --name M1 --checklist
```

**检查项类型**:
| 类型 | 检查项 | 触发条件 |
|------|--------|----------|
| 需求追溯 | 需求→设计→代码→测试关联 | 签署前 |
| Ad-hoc To-do Items | 查看发布的 Items | 签署前 |
| 质量门禁 | 测试覆盖率、Bug 修复 | 签署前 |

### 4.2 需求追溯检查

**FR-CHECKLIST-002**: 需求追溯完整性检查

**描述**: 检查需求、设计、代码、测试之间的追溯关联。

**检查规则**:
```python
TRACEABILITY_RULES = {
    "requirements_to_design": True,   # 需求必须有对应的设计文档
    "design_to_code": True,           # 设计必须有对应的实现
    "code_to_test": True,            # 代码必须有对应的测试
    "test_coverage_threshold": 0.80, # 测试覆盖率阈值
}
```

**检查示例**:
```
✓ [ ] 需求追溯 - FR-SIGNOFF-001 → DETAIL-2026-02-001
✓ [ ] 设计追溯 - DETAIL-2026-02-001 → src/core/signoff.py
✓ [ ] 代码追溯 - src/core/signoff.py → tests/test_signoff.py
⚠️ [ ] 测试覆盖 - 73% < 80% 阈值
```

### 4.3 任务范围检查

**FR-CHECKLIST-003**: 任务范围验证

**描述**: 在签署前验证任务是否在当前版本范围内。

**检查规则**:
```
签署前检查：
  1. 任务是否关联到当前版本的需求？
  2. 任务是否与当前 phase 匹配？
  3. 任务类型是否正确？

如果检查不通过，系统应阻止签署或给出警告。
```

### 4.4 质量门禁检查

**FR-CHECKLIST-004**: 质量门禁检查

**描述**: 在签署前检查质量指标是否达标。

**检查指标**:
| 指标 | 阈值 | 检查方式 |
|------|------|----------|
| 测试覆盖率 | ≥80% | pytest-cov |
| 测试通过率 | 100% | pytest |
| Bug 修复 | 无未关闭的 P0/P1 Bug | issue tracker |
| 代码规范 | 无 lint 错误 | ruff/mypy |

### 4.5 验收标准

| FR 编号 | 验收标准 | 验证方式 |
|---------|----------|----------|
| FR-CHECKLIST-001 | review 命令可带 --checklist 选项 | CLI 测试 |
| FR-CHECKLIST-002 | 需求追溯检查完整 | 集成测试 |
| FR-CHECKLIST-003 | 任务范围检查准确 | 集成测试 |
| FR-CHECKLIST-004 | 质量门禁指标达标 | 自动化测试 |
| 整体 | 动态 checklist 覆盖率 100% | 代码审查 |

### 4.6 命令设计

```bash
# 评审需求并显示动态检查项
oc-collab review requirements --checklist

# 评审里程碑并显示动态检查项
oc-collab review milestone --name M1 --checklist

# 只显示检查项，不执行评审
oc-collab checklist show --phase requirements

# 检查任务范围
oc-collab checklist verify --task TASK-001
```

### 4.7 输出示例

```bash
$ oc-collab review requirements --checklist

=== 动态检查项 ===

【需求追溯检查】
✓ FR-SIGNOFF-001 → DETAIL-2026-02-001 ✅
✓ FR-SIGNOFF-002 → DETAIL-2026-02-002 ✅
⚠️ FR-TASK-001 → 无对应设计文档 ❌

【任务范围检查】
✓ TASK-001 [v2.2.1] 关联到当前版本 ✅
✓ TASK-002 [v2.2.1] 关联到当前版本 ✅

【质量门禁检查】
✓ 测试覆盖率: 91% >= 80% ✅
✓ 测试通过率: 20/20 = 100% ✅
✓ 无未关闭的 P0/P1 Bug ✅

=== 检查结果: 3/4 通过, 1 警告 ===
建议: FR-TASK-001 缺少对应的设计文档，请在签署前补充。
```

---

## 5. 双代理认知免疫系统

**需求编号**: FR-COGNITIVE

**问题背景**:
AI Agent 与人类协作者有本质区别：Agent 不会主动检查问题、不会质疑不完整、不会发现缺失。这导致 v2.2.0 出现严重的协作问题：
- Agent 不知道 oc-collab 的存在
- Agent 不知道自己的角色和职责
- Agent 会丢失协作意识，独自决策
- Agent 无法在会话开始时获取必要上下文

**核心概念**:
```
┌─────────────────────────────────────────────────────────────┐
│  双代理认知免疫系统                                         │
│  ├── 会话起始引导（session_start）                          │
│  ├── 困惑信号检测                                           │
│  ├── 协作指南 Skill 自动加载                                │
│  └── 职责边界提醒                                           │
└─────────────────────────────────────────────────────────────┘
```

### 5.1 会话起始引导（Session Start）

**需求编号**: FR-COGNITIVE-001

**问题背景**:
Agent 每次新会话开始时，无法获得必要的上下文信息（项目状态、当前阶段、待办任务），导致协作混乱。

**解决方案**:
Agent 切换或会话开始时，自动显示上下文信息。

**命令格式**:
```bash
oc-collab status
```

**输出示例**:
```
=== Agent 2 (开发负责人) ===

当前项目: dual-agent-collaboration-system
当前阶段: requirements_review
当前里程碑: v2.2.1

你的职责:
  - 评审需求文档
  - 编写详细设计
  - 签署确认

待办事项:
  [ ] 评审 requirements_v2.2.1_DRAFT.md
  [ ] 签署需求确认

常用命令:
  - oc-collab status    查看状态
  - oc-collab review    评审
  - oc-collab signoff   签署
```

**验收标准**:

| 标准 | 验证方式 |
|------|----------|
| Agent 切换后显示上下文 | CLI 测试 |
| 显示当前 Agent 职责 | 输出检查 |
| 显示待办事项 | 输出检查 |

---

### 5.2 困惑信号检测

**需求编号**: FR-COGNITIVE-002

**问题背景**:
Agent 在协作过程中可能会出现困惑，但系统无法识别和提醒，导致：
- Agent 独自决策，跳过协作流程
- Agent 忘记遵循 oc-collab 规范
- Agent 不知道另一个 Agent 在做什么

**解决方案**:
检测 Agent 的困惑信号，主动提醒。

**检测场景**:

| 困惑信号 | 检测方式 | 提醒 |
|----------|----------|------|
| 跳过评审直接开发 | 检查开发时间 vs 评审时间 | ⚠️ 请先完成评审 |
| 签署前未检查待办 | 检查是否有未完成的 Ad-hoc Items | ⚠️ 请先处理待办事项 |
| 独自修改核心模块 | 检查 git log 中的操作者 | ⚠️ 请通知另一个 Agent |
| 多次重复错误 | 检查错误历史 | ⚠️ 参考历史解决方案 |

**检测规则**:

```python
CONFUSION_DETECTION_RULES = {
    "skip_review_before_develop": True,    # 跳过评审直接开发
    "develop_without_signoff": True,       # 未签署就开发
    "modify_without_notification": True,   # 修改未通知
    "repeated_errors": True,               # 重复错误
}
```

**验收标准**:

| 标准 | 验证方式 |
|------|----------|
| 检测到跳过评审行为 | CLI 测试 |
| 检测到未签署开发 | CLI 测试 |
| 提醒消息清晰 | 代码审查 |

---

### 5.3 协作指南 Skill 自动加载

**需求编号**: FR-COGNITIVE-003

**问题背景**:
Agent 不知道 oc-collab 的协作规范，不知道应该遵循什么流程。虽然有 `docs/COLLABORATION_GUIDE.md`，但 Agent 不会主动阅读。

**解决方案**:
将协作指南转换为 Skill，自动加载到 Agent 上下文中。

**实现方式**:

```
skills/
└── oc_collab_collaboration_guide/
    ├── skill.json          # Skill 元数据
    ├── manifest.yaml       # Skill 配置
    └── content.md          # 协作指南内容（从 COLLABORATION_GUIDE.md 提取）
```

**Skill 内容**:

| 章节 | 说明 |
|------|------|
| Agent 角色定义 | Agent 1 vs Agent 2 的职责边界 |
| 工作流程 | 4 个阶段的完整流程 |
| Git 使用规范 | 分支、提交、标签规范 |
| 文件命名规范 | 各类文档的命名约定 |
| 状态文件规则 | project_state.yaml 的更新规则 |
| 流程合规检查 | 启动检查、决策点检查 |
| 任务触发流程 | Agent 2 必须等待任务指派 |
| MEMO 处理流程 | MEMO 到需求的转化 |

**验收标准**:

| 标准 | 验证方式 |
|------|----------|
| Skill 文件结构正确 | 代码审查 |
| Skill 内容完整 | 与 COLLABORATION_GUIDE.md 对比 |
| Skill 可加载 | CLI 测试 |

---

### 5.4 职责边界提醒

**需求编号**: FR-COGNITIVE-004

**问题背景**:
Agent 可能会越界工作：
- Agent 2 主动开始开发，未经任务指派
- Agent 1 独自修改设计，未经评审
- Agent 忘记自己的职责范围

**解决方案**:
在关键操作前，主动提醒 Agent 的职责边界。

**提醒场景**:

| 场景 | Agent 1 | Agent 2 |
|------|---------|---------|
| 开始工作前 | 你是产品经理，负责需求和评审 | 你是开发，负责实现和签署 |
| 提交代码前 | - | 代码是否已完成白盒测试？ |
| 签署前 | 所有 Ad-hoc Items 是否完成？ | 所有 Ad-hoc Items 是否完成？ |
| 越界操作时 | 这是开发的工作，请通知 Agent 2 | 这是产品的工作，请通知 Agent 1 |

**提醒配置** (`config.yaml`):

```yaml
cognitive_immunity:
  enabled: true
  reminders:
    agent_role_reminder: true     # 工作前提醒角色
    test_reminder: true           # 提交代码前提醒测试
    signoff_reminder: true        # 签署前提醒检查
    boundary_reminder: true       # 越界操作时提醒
```

**验收标准**:

| 标准 | 验证方式 |
|------|----------|
| 工作前提醒角色 | CLI 测试 |
| 提交前提醒测试 | CLI 测试 |
| 签署前提醒检查 | CLI 测试 |
| 越界操作提醒 | CLI 测试 |

---

### 5.5 相关 MEMO

| MEMO 编号 | MEMO 名称 | 说明 |
|-----------|-----------|------|
| MEMO-2026-02-003 | oc-collab 核心设计哲学 | 约束分层、决策分配 |
| MEMO-2026-02-004 | AI Agent 软件工程流程 | 会话引导、追溯关联 |

---

## 6. 非功能需求

### 6.1 兼容性

| 要求 | 说明 |
|------|------|
| 向后兼容 | v2.2.0 的签署命令保持不变 |
| `--sync` 选项 | 默认不启用，需要显式指定 |

### 6.2 错误处理

| 场景 | 处理方式 |
|------|----------|
| 签署成功但同步失败 | 显示警告，签署仍有效 |
| 远程仓库冲突 | 提示用户手动解决冲突 |
| 网络错误 | 重试 3 次后报错 |

---

## 7. 里程碑

| 里程碑 | 内容 | 交付物 | 章节 |
|--------|------|--------|------|
| M1 | 签署自动同步功能 | signoff.py + CLI --sync 选项 | FR-SIGNOFF-AUTO-001 |
| M2 | 变更载体明确化 | PRD/RFC 角色分工指南 + 合规检测 | FR-CHANGE-CLARITY-001 |
| M3 | 签署流程改进 | 模板 + 检查清单 + 记录持久化 | FR-SIGNOFF-IMPROVE-001 |
| M4 | 动态 Checklist 机制 | checklist_generator.py + CLI --checklist 选项 | FR-CHECKLIST-001 |
| M5 | 双代理认知免疫系统 | Skill + 检测机制 + 提醒 | FR-COGNITIVE |
| M6 | 测试和签署 | 测试用例 + 签署 | - |

---

## 8. 相关文档

| 文档 | 说明 |
|------|------|
| `docs/bugs/BUG-20260202-001_Combined.md` | Bug 报告整合 |
| `docs/01-requirements/requirements_v2.2.0.md` | v2.2.0 需求 |
| `docs/00-memos/MEMO-2026-02-003.md` | oc-collab 核心设计哲学 |
| `docs/00-memos/MEMO-2026-02-004.md` | AI Agent 软件工程流程 |
| `docs/COLLABORATION_GUIDE.md` | 协作指南 |
| `skills/oc_collab_collaboration_guide/` | 协作指南 Skill |

---

## 附录: 签署确认 (进行中)

### Agent 2 (开发负责人) 评审意见

**评审日期**: 2026-02-05
**评审结果**: ✅ 可行，需细化

**评审意见**:
- FR-STATE-001: ✅ 技术可行，状态机设计清晰
- FR-SIGNOFF-AUTO-001: ✅ 技术可行，直接复用现有 push 方法
- FR-SIGNOFF-IMPROVE-001: ✅ 技术可行
- FR-CHANGE-CLARITY-001: ⚠️ 需细化，冲突检测可能产生误报
- FR-ADHOC-001/002/003: ✅ 技术可行
- FR-CHECKLIST-001: ✅ 可复用上一轮 checklist_generator.py

**开放问题**:
1. ~~PRD 未签署时"阻止开发"的具体实现方式待确认~~ ✅ **已关闭** - 见 2.4.4 违规处理，使用 WARN 而非阻止
2. ~~Ad-hoc Items 批量操作和过期处理待定义~~ ✅ **已关闭** - 见 v2.2.2 FR-ADHOC-004/005（后续版本）

 详细评审见: `requirements_v2.2.1_READY_Review_Agent2.md`

### 二次评审意见 (2026-02-07)

**评审日期**: 2026-02-07
**评审结论**: ✅ 确认通过

**检查项**:
| 检查项 | 状态 | 说明 |
|--------|------|------|
| 2.3.4 签署流程改进验收标准 | ✅ | 存在且完整，包含 4 个验收标准 |
| 2.4.5 变更载体验收标准 | ✅ | 存在且完整，包含 4 个验收标准 |
| 开放问题关闭 | ✅ | 2 个开放问题已关闭 |

**评审意见**:
- 所有验收标准已补充完整
- 开放问题已明确处理方案
- 文档结构清晰，功能需求完整

### 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-07 | ✅ 已签署 |
| 开发负责人 | Agent 2 | 2026-02-05 + 2026-02-07 | ✅ 已签署 |

**签署后状态**: DRAFT → APPROVED

---

**创建人**: Agent 1
**日期**: 2026-02-02
**最后更新**: 2026-02-02
**状态**: DRAFT (草稿)
