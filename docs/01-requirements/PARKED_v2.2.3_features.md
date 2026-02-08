# v2.2.3 推迟功能池

**创建日期**: 2026-02-08
**状态**: 待实现
**来源**: v2.2.3 需求评审

---

## 说明

以下功能从 v2.2.3 推迟到后续版本。记录在此，以便后续版本考虑。

**重要**: 每个推迟的功能都标注了来源文档，便于追溯。

---

## 推迟的功能

### 1. F-REVIEW-001: 动态评审 Checklist（含逆向验证）

| 属性 | 值 |
|------|-----|
| 原功能 ID | F-REVIEW-001 |
| 原工时 | 4-6h |
| 推迟原因 | 太复杂，需要重新设计 |
| 核心洞察 | 评审流于形式，只"确认"不"质疑" |

**来源文档**:
- `requirements_v2.2.2_READY.md` (v2.7) - 逆向检查项设计

**逆向检查项设计**:
| 序号 | 检查项 | 目的 |
|------|--------|------|
| REV-001 | "这份文档是否忽略了什么重要因素？" | 强制寻找遗漏 |
| REV-002 | "如果你是另一个角色，你会怎么批评这个设计？" | 强制换位思考 |
| REV-003 | "这个方案的最大风险是什么？如何缓解？" | 强制风险评估 |
| REV-004 | "有哪些替代方案？为什么当前方案是最好的？" | 强制对比分析 |

**原始验收标准**:
- [ ] 评审时自动生成逆向检查项（≥50%）和正向检查项
- [ ] 强制 Agent 先完成逆向检查项，且必须全部完成
- [ ] 逆向检查项回答长度 ≥ 50 字

**后续建议**:
- 拆分为独立功能
- 先做简单的正向检查项
- 逆向检查项作为 v3.0 考虑

---

### 2. F-AUTO-001: 部署发布自动化

| 属性 | 值 |
|------|-----|
| 原功能 ID | F-AUTO-001 |
| 原工时 | 2-4h |
| 推迟原因 | 需要 deployment.yaml 配置，超出 CLI 范畴 |
| 依赖 | deployment.yaml 规范 |

**来源文档**:
- `PROPOSAL_v2.2.2_Deployment_Automation.md` (v1.0, 2026-02-07)
- `PROPOSAL_v2.2.2_Deployment_Automation_Review_Agent2.md` (APPROVED with comments)

**提案历史**:
| 文档 | 状态 | 日期 |
|------|------|------|
| PROPOSAL_v2.2.2_Deployment_Automation.md | 待评审 | 2026-02-07 |
| PROPOSAL_v2.2.2_Deployment_Automation_Review_Agent2.md | APPROVED | 2026-02-07 |

**原始验收标准**:
- [ ] 支持 `deployment.yaml` 配置文件
- [ ] 支持 `oc-collab deployment configure` 交互式配置
- [ ] `oc-collab phase-advance --deploy` 时自动执行发布命令
- [ ] 发布前显示预览，确认后执行

**后续建议**:
- 先定义 deployment.yaml 规范
- v2.3 或 v3.0 实现

---

### 3. F-AUTO-003: 测试覆盖率门禁

| 属性 | 值 |
|------|-----|
| 原功能 ID | F-AUTO-003 |
| 原工时 | 2-4h |
| 推迟原因 | 属于 CI/CD 范畴，不是 CLI 核心功能 |
| 技术依赖 | coverage.py, pytest-cov |

**来源文档**:
- `requirements_v2.2.1_READY.md` - 质量门禁设计
- `requirements_v2.2.0.md` - 单元测试覆盖率要求 (>=80%)

**相关实现**:
| 文件 | 说明 |
|------|------|
| `state/project_state.yaml` | `test_coverage_threshold: 0.80` |

**原始验收标准**:
- [ ] 新代码的单元测试覆盖率 ≥ 80%
- [ ] 覆盖率不达标时阻止合并
- [ ] 支持自定义阈值

**后续建议**:
- 作为 CI/CD Pipeline 实现
- 不是 CLI 核心功能

---

### 4. F-AUTO-004: 文档版本管理

| 属性 | 值 |
|------|-----|
| 原功能 ID | F-AUTO-004 |
| 原工时 | 2-3h |
| 推迟原因 | 可选功能，优先级低 |

**来源文档**:
- `requirements_v2.2.2_READY.md` - 整合自 v2.2.2 推迟功能

**原始验收标准**:
- [ ] 提供版本索引，显示所有版本的清单和状态
- [ ] 明确标识当前版本（使用 `*` 前缀或 `_CURRENT.md` 命名）
- [ ] 区分 DRAFT / APPROVED / ARCHIVED 状态

**后续建议**:
- v3.0 或后续版本考虑
- 当前可通过文档命名规范解决

---

### 5. F-IDENTITY-001: Agent 身份自动识别

| 属性 | 值 |
|------|-----|
| 原功能 ID | F-IDENTITY-001 |
| 原工时 | 4-8h |
| 推迟原因 | 太复杂，需要 skill 系统配合 |
| 技术依赖 | skill.json, environment variables |

**来源文档**:
- `requirements_infrastructure.md` (DRAFT, 2026-02-07) - 完整基础设施设计
- `requirements_v2.2.2_READY.md` - Agent 身份检测评审意见

**requirements_infrastructure.md 内容**:
| 层级 | 机制 | 用途 | 复杂度 |
|------|------|------|--------|
| L0 极简上下文 | `.a` 文件 | 用户身份、当前阶段 | 低 |
| L1 扩展知识 | Skill 机制 | 复杂项目知识、技能 | 中 |

**原始验收标准**:
- [ ] 环境变量 `OC_AGENT_ID` 正确识别 Agent 身份
- [ ] 自动加载对应 skill 文件
- [ ] `oc-collab start` 命令可用
- [ ] 欢迎消息包含：项目名称、阶段、版本、角色、待办、下一步

**后续建议**:
- 需要 skill 系统重构
- v3.0 考虑

---

### 6. F-PROC-003: Todo 编号唯一性

| 属性 | 值 |
|------|-----|
| 原功能 ID | F-PROC-003 |
| 原工时 | 2h |
| 推迟原因 | 高迁移风险，需要更新 20+ 文档引用 |
| 风险等级 | 🔴 高 |

**来源文档**:
- `requirements_v2.2.2_READY.md` - v2.2.2 推迟功能
- 多个版本中的 TODO 编号规范

**原始设计**:
```
变更: TODO-xxx → {AgentID}-xxx

示例:
  1-001  # Agent1 创建
  2-001  # Agent2 创建
```

**注意事项**:
- 迁移脚本自动更新
- 20+ 文档引用需要更新
- 建议 v2.2.2 完成后实施

**后续建议**:
- v3.0 重大更新时一并处理
- 当前版本不做

---

## 来源文档汇总

| 功能 | 来源文档 | 文档状态 |
|------|---------|---------|
| 逆向验证评审 | requirements_v2.2.2_READY.md | APPROVED |
| 部署自动化 | PROPOSAL_v2.2.2_Deployment_Automation.md | 待评审 |
| 测试覆盖率门禁 | requirements_v2.2.1_READY.md | APPROVED |
| 文档版本管理 | requirements_v2.2.2_READY.md | APPROVED |
| Agent 身份识别 | requirements_infrastructure.md | DRAFT |
| Todo 编号唯一性 | requirements_v2.2.2_READY.md | APPROVED |

---

## 统计

| 状态 | 数量 | 工时 |
|------|------|------|
| 推迟功能 | 6 个 | 16-27h |
| v2.2.3 保留 | 3 个 | 12h |

---

## 处理建议

| 优先级 | 功能 | 建议版本 | 来源文档 |
|--------|------|---------|---------|
| P0 | 测试覆盖率门禁 | CI/CD Pipeline | requirements_v2.2.1_READY.md |
| P1 | 文档版本管理 | v3.0 | requirements_v2.2.2_READY.md |
| P1 | Todo 编号唯一性 | v3.0 (重大更新) | requirements_v2.2.2_READY.md |
| P2 | 部署自动化 | v2.3 (需先定规范) | PROPOSAL_v2.2.2_Deployment_Automation.md |
| P3 | Agent 身份识别 | v3.0 | requirements_infrastructure.md |
| P3 | 逆向验证评审 | v3.0 | requirements_v2.2.2_READY.md |

---

## 相关文档路径

```
docs/01-requirements/
├── requirements_v2.2.2_READY.md          ← 逆向验证、文档版本、Todo编号
├── requirements_v2.2.1_READY.md        ← 测试覆盖率
├── requirements_infrastructure.md      ← Agent身份识别
├── PROPOSAL_v2.2.2_Deployment_Automation.md           ← 部署自动化
├── PROPOSAL_v2.2.2_Deployment_Automation_Review_Agent2.md
└── PARKED_v2.2.3_features.md            ← 本文档
```

---

**文档版本**: v2
**创建日期**: 2026-02-08
**修订日期**: 2026-02-08
**状态**: 待处理
