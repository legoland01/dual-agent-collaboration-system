# v2.2.2 需求建议书：自动化增强与反思机制

**版本**: v1.2
**日期**: 2026-02-07
**作者**: Agent 1 (产品经理)
**整合来源**:
- Agent2 反思: PROPOSAL_v2.2.1_Lessons_Learned.md
- Agent1 反思: RETROSPECTIVE-v2.2.1-agent1.md
- Agent2 提案: PROPOSAL_v2.2.2_Session_Start_Guide.md
- Agent2 洞察: PROPOSAL_v2.2.2_Reverse_Validation.md
**状态**: 待评审

---

## 1. 概述

### 1.1 背景

v2.2.1 开发过程中发现了多个问题，需要通过自动化机制和流程改进来解决。

### 1.2 问题来源

| 来源 | 核心发现 |
|------|----------|
| Agent2 反思 | **P9: M5 需求遗漏** - 评审流于形式，只"确认"不"质疑" |
| Agent1 反思 | 发布流程不清晰 - Agent2 的发布知识没有文档化 |
| 共同问题 | 任务状态不同步、测试覆盖率不足 |

### 1.3 解决方案总览

| 功能 ID | 功能名称 | 来源 | 优先级 |
|---------|----------|------|--------|
| F-REVIEW-001 | 动态评审 Checklist | Agent2 | P0 |
| F-AUTO-001 | 部署发布自动化 | Agent1 | P0 |
| F-AUTO-002 | 任务状态自动同步 | Agent2 | P0 |
| F-AUTO-003 | 测试覆盖率门禁 | Agent2 | P0 |
| F-AUTO-004 | 文档版本管理 | Agent1 | P1 |
| F-IDENTITY-001 | Agent 身份自动识别 | Agent1 | P0 |

---

## 2. 功能需求

### 2.1 F-REVIEW-001: 动态评审 Checklist（含逆向验证机制）

**核心洞察（Agent2 发现）**:
P9 问题的本质是"上下文混同"而非能力问题。Agent2 与 Agent1 共享过多上下文，失去了独立评审视角。解决方案不是简单的 checklist，而是**逆向验证机制**：强制 Agent 从"批判"角度审视文档，而非"确认"角度。

**需求描述**:
系统应在 Agent 收到评审任务时，自动生成评审 checklist，包含逆向检查项，引导 Agent 进行深度评审。

**问题解决**:
- 解决 Agent2 反思中发现的 P9 问题：评审流于形式，只"确认"不"质疑"
- 本质解决：上下文混同导致的独立视角丧失
- 引导 Agent 提出质疑性问题，而不是简单确认

**验收标准**:
- [ ] 评审需求文档时，自动生成含逆向检查项的 checklist
- [ ] 评审设计文档时，自动生成设计专用 checklist
- [ ] 逆向检查项占比 ≥ 50%（引导批判而非确认）
- [ ] 强制 Agent 回答所有逆向检查项
- [ ] 校验逆向检查项回答质量（必须有实质性质疑内容）
- [ ] 正向检查项作为补充（功能完整性、技术可行性）

**逆向检查项设计（Agent2 贡献）**:
| 序号 | 逆向检查项 | 目的 |
|------|-----------|------|
| 1 | "这份文档是否忽略了什么重要因素？" | 强制寻找遗漏 |
| 2 | "如果你是另一个角色，你会怎么批评这个设计？" | 强制换位思考 |
| 3 | "这个方案的最大风险是什么？如何缓解？" | 强制风险评估 |
| 4 | "有哪些替代方案？为什么当前方案是最好的？" | 强制对比分析 |
| 5 | "这个实现细节是否经得起推敲？" | 强制细节审视 |

**正向检查项设计（补充）**:
| 序号 | 正向检查项 | 目的 |
|------|-----------|------|
| 1 | 功能完整性 | 确保覆盖所有需求 |
| 2 | 技术可行性 | 确保技术方案可行 |
| 3 | 文档规范性 | 确保格式规范 |

**关键区别**:
| 维度 | 传统 Checklist | 逆向验证机制 |
|------|---------------|-------------|
| 视角 | "文档说了什么？" | "文档没说什么？" |
| 思维 | 确认 | 质疑 |
| 输出 | "确认已覆盖" | "发现以下问题..." |
| 效果 | 流于形式 | 真正发现问题 |

**参考**: Agent2 提案 PROPOSAL_v2.2.2_Reverse_Validation.md（上下文混同与逆向验证深入洞察）

---

### 2.2 F-AUTO-001: 部署发布自动化

**需求描述**:
系统应支持用户定义项目的发布命令，并在阶段推进时自动执行。

**问题解决**:
- 解决 Agent1 反思中发现的问题：不知道如何发布到 PyPI
- Agent2 的发布知识应可配置、可复用

**验收标准**:
- [ ] 支持 `deployment.yaml` 配置文件
- [ ] 支持 `oc-collab deployment configure` 交互式配置
- [ ] `oc-collab phase-advance` 时自动执行发布命令

**参考**: PROPOSAL_v2.2.2_Deployment_Automation.md

---

### 2.3 F-AUTO-002: 任务状态自动同步

**需求描述**:
Agent 执行任务状态变更时，应自动同步到文件。

**问题解决**:
- 解决 Agent2 反思中发现的 P1 问题：todowrite 只更新内存不同步

**验收标准**:
- [ ] `todowrite` / `todoedit` 操作后自动同步到文件
- [ ] 同步时有明确提示

---

### 2.4 F-AUTO-003: 测试覆盖率门禁

**需求描述**:
新代码提交时，应强制检查单元测试覆盖率不低于阈值。

**问题解决**:
- 解决 Agent2 反思中发现的 P6 问题：signoff.py 覆盖率仅 69%

**验收标准**:
- [ ] 新代码的单元测试覆盖率 ≥ 80%
- [ ] 覆盖率不达标时阻止合并

---

### 2.5 F-AUTO-004: 文档版本管理

**需求描述**:
系统应自动管理文档版本，避免版本混乱。

**问题解决**:
- 解决 Agent2 反思中发现的 P8 问题：v2.2.1 存在多个版本 (_DRAFT.md, _READY.md, _PATCH_001.md 等)

**验收标准**:
- [ ] 新版本发布后，旧版本自动标记为过期
- [ ] 避免同一阶段存在多个版本

---

### 2.6 F-IDENTITY-001: Agent 身份自动识别与 Session 启动引导

**需求描述**:
新 OpenCode session 启动时，应自动识别当前 Agent 身份并加载对应规则，无需重复解释 oc-collab 协作规范。同时应自动显示欢迎消息和协作指南摘要。

**问题解决**:
- 解决每次 session 重启或 compaction 后都需要重新解释 oc-collab 规则的问题
- 新 Agent 加入项目时，无法快速了解协作流程和项目状态
- 支持两种启动方式：
  - 手动启动：设置 `OC_AGENT_ID` 环境变量
  - 自动启动：oc-collab 创建 session 时自动注入身份

**验收标准**:
- [ ] 环境变量 `OC_AGENT_ID=agent1` 时，自动加载 Agent1 专用 skill
- [ ] 环境变量 `OC_AGENT_ID=agent2` 时，自动加载 Agent2 专用 skill
- [ ] 未设置环境变量时，加载通用协作规则
- [ ] Agent 进入项目时自动显示欢迎消息
- [ ] 欢迎消息包含：项目名称、当前阶段、Agent 角色、待办任务、下一步建议
- [ ] 显示协作指南摘要，提供完整指南入口
- [ ] `oc-collab start` 命令可用
- [ ] CLI 命令 `oc-collab status` 和 `oc-collab todo` 正常

**功能详情**:

```
Agent 进入项目
    ↓
系统自动显示欢迎消息
    ↓
Agent 立即知道：
- 当前阶段
- 自己的角色
- 待办任务
- 下一步该做什么
- 协作指南入口
```

**触发时机**:
| 时机 | 触发条件 | 动作 |
|------|---------|------|
| Session 启动 | Agent 进入项目目录 | 自动显示欢迎消息 |
| 手动触发 | 运行 `oc-collab start` | 显示欢迎消息 |
| 困惑检测 | Agent 表达困惑 | 加载协作指南 |

**Skill 目录结构**:
```
skills/
├── oc_collab_collaboration_guide/
│   ├── skill.json          # 元数据
│   └── content.md          # 通用协作规范
├── oc_collab_agent1/
│   ├── skill.json
│   └── content.md          # Agent1 专用职责和权限
└── oc_collab_agent2/
    ├── skill.json
    └── content.md          # Agent2 专用职责和权限
```

**启动方式对比**:

| 场景 | 启动命令 | 说明 |
|------|---------|------|
| 手动 | `OC_AGENT_ID=agent1 opencode` | 用户指定身份 |
| 自动 | `oc-collab session start agent1` | oc-collab 自动注入环境变量 |

**参考**: Agent2 提案 PROPOSAL_v2.2.2_Session_Start_Guide.md 中的详细设计

---

## 3. 迭代反思机制

### 3.1 反思收集流程

```
版本发布后
    ↓
Agent1 主持反思，收集材料
    ↓
各 Agent 提交 Retrospective（自由形式）
    ↓
Agent1 整合成正式需求建议书
    ↓
Agent2 技术评审
    ↓
根据结论处理（更新指南 / 提新需求）
```

### 3.2 反思存储位置

```
docs/00-retrospective/
├── agent1/
│   └── RETROSPECTIVE-v{version}-agent1.md
├── agent2/
│   └── RETROSPECTIVE-v{version}-agent2.md
└── meetings/
    └── MEETING-{date}.md
```

---

## 4. 实施建议

### 4.1 版本规划

| 版本 | 功能 | 说明 |
|------|------|------|
| v2.2.2 | F-REVIEW-001 + F-AUTO-001 + F-AUTO-002 + F-AUTO-003 + F-IDENTITY-001 | 核心自动化增强 |
| v2.2.3 | F-AUTO-004 | 文档版本管理 |

### 4.2 依赖关系

```
F-REVIEW-001: 动态评审 Checklist
    └── 复用 M4 ExtendedChecklistGenerator 架构

F-AUTO-001: 部署发布自动化
    └── 独立功能

F-AUTO-002: 任务状态自动同步
    └── todowrite 工具改造

F-AUTO-003: 测试覆盖率门禁
    └── CI/CD 流水线集成

F-IDENTITY-001: Agent 身份自动识别
    └── SessionStarter 扩展（参考 Agent2 提案已有详细设计）
```

---

## 5. 评审说明

### 5.1 Agent2 需关注的点

| 关注项 | 说明 |
|--------|------|
| F-REVIEW-001 设计合理性 | 逆向检查项是否有效？回答质量校验是否合理？ |
| F-AUTO-001 技术可行性 | deployment.yaml 方案是否可行？ |
| F-AUTO-002 实现复杂度 | 改造 todowrite 是否有风险？ |
| F-AUTO-003 CI/CD 集成 | GitHub Actions 配置是否正确？ |
| F-IDENTITY-001 设计合理性 | 环境变量方案是否足够？SkillLoader 改造复杂度？ |

### 5.2 各 Agent 关注自己提议

| Agent | 原始提议 | 是否在整合提案中 |
|-------|----------|----------------|
| Agent2 | 动态评审 Checklist | ✅ F-REVIEW-001 |
| Agent2 | 任务状态自动同步 | ✅ F-AUTO-002 |
| Agent2 | 测试覆盖率门禁 | ✅ F-AUTO-003 |
| Agent2 | Session 启动引导 | ✅ F-IDENTITY-001 |
| Agent2 | 代码完整性校验 | ⏳ v2.2.3 |
| Agent2 | 职责边界检测 | ⏳ v2.2.3 |
| Agent1 | 部署发布自动化 | ✅ F-AUTO-001 |
| Agent1 | Agent 身份自动识别 | ✅ F-IDENTITY-001 |
| Agent1 | 跨会话工作追踪 | ⏳ 待讨论 |
| Agent1 | 测试环境标准化 | ⏳ 文档补充 |

---

## 6. 签署

### Agent 1 签署

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-07 | ✅ |

### Agent 2 技术评审

| 评审项 | 结论 | 评审说明 |
|--------|------|----------|
| F-REVIEW-001 设计合理性 | ✅ 通过 | 逆向验证机制设计精妙，直击 P9 问题本质，复用 M4 架构实现成本低 |
| F-AUTO-001 技术可行性 | ✅ 通过 | deployment.yaml 配置方式合理，与现有 phase-advance 机制无缝集成 |
| F-AUTO-002 实现复杂度 | ✅ 通过 | 改造 todowrite 工具，改动小收益大，向后兼容 |
| F-AUTO-003 CI/CD 集成 | ✅ 通过 | pytest-cov + GitHub Actions 实现成熟，覆盖率阈值 80% 合理 |
| F-IDENTITY-001 设计合理性 | ✅ 通过 | 环境变量机制简单可靠，欢迎消息设计全面，需关注 SkillLoader 改造 |

**评审文档**: REVIEW_v2.2.2_Technical_Review.md

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-07 | ✅ |

---

*本文档整合自 v2.2.1 迭代反思成果。*

**文档版本历史**：

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.2 | 2026-02-07 | 整合 Agent2 逆向验证洞察，扩展 F-REVIEW-001（逆向检查项设计） |
| v1.1 | 2026-02-07 | 整合 Agent2 提案 PROPOSAL_v2.2.2_Session_Start_Guide.md，扩展 F-IDENTITY-001 |
| v1 | 2026-02-07 | 初始版本 |
