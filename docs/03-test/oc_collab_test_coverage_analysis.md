# oc-collab 功能与黑盒测试覆盖分析

**文档ID**: DOC-TEST-COVERAGE-001
**日期**: 2026-02-08
**作者**: Agent 1 (产品经理)
**状态**: DRAFT

---

## 一、oc-collab 全部 CLI 命令清单

### 1.1 核心命令 (22个)

| # | 命令 | 功能描述 | 版本 | 优先级 |
|---|------|----------|------|--------|
| 1 | `oc-collab init` | 初始化协作项目 | v1.0 | P0 |
| 2 | `oc-collab status` | 查看协作状态 | v1.0 | P0 |
| 3 | `oc-collab switch` | 切换 Agent 角色 | v1.0 | P0 |
| 4 | `oc-collab advance` | 推进阶段 | v1.0 | P0 |
| 5 | `oc-collab signoff` | 签署确认 | v1.0 | P0 |
| 6 | `oc-collab signoffs` | 查看签署记录 | v1.0 | P1 |
| 7 | `oc-collab todo` | 待办事项 | v1.0 | P0 |
| 8 | `oc-collab review` | 评审流程 | v1.0 | P0 |
| 9 | `oc-collab sync` | 同步远程变更 | v1.0 | P1 |
| 10 | `oc-collab sync-all` | 同步所有远程 | v1.0 | P1 |
| 11 | `oc-collab push` | 推送代码 | v1.0 | P1 |
| 12 | `oc-collab remote` | 管理远程仓库 | v1.0 | P1 |
| 13 | `oc-collab history` | 查看协作历史 | v1.0 | P2 |
| 14 | `oc-collab docs` | 自动同步文档 | v1.0 | P1 |
| 15 | `oc-collab agent` | Agent 守护进程 | v1.0 | P2 |
| 16 | `oc-collab project` | 项目管理 | v1.0 | P2 |
| 17 | `oc-collab workflow` | 工作流状态 | v1.0 | P2 |
| 18 | `oc-collab work` | 智能工作流引导 | v1.0 | P2 |
| 19 | `oc-collab requirements` | 需求文档管理 | v2.2.2 | P0 |
| 20 | `oc-collab design` | 设计文档管理 | v2.2.2 | P0 |
| 21 | `oc-collab compliance` | 合规检查 | v2.2.2 | P0 |
| 22 | `oc-collab git` | Git 同步工具 | v2.2.2 | P0 |

### 1.2 命令分类

| 分类 | 命令数 | P0命令 |
|------|--------|--------|
| 项目初始化 | 1 | init |
| 状态与切换 | 3 | status, switch, todo |
| 阶段与签署 | 3 | advance, signoff, signoffs |
| 评审流程 | 1 | review |
| 版本控制 | 4 | sync, sync-all, push, remote |
| 文档管理 | 2 | docs, requirements, design |
| 系统运维 | 4 | agent, project, workflow, work |
| 合规检查 | 2 | compliance, git |

---

## 二、黑盒测试用例统计

### 2.1 按版本统计

| 版本 | 测试用例数 | 状态 |
|------|-----------|------|
| v2.2.0 | 83 | 已创建 |
| v2.2.2 | 14 | 已创建 |
| **总计** | **97** | - |

### 2.2 按功能分类统计

| 功能分类 | 命令 | v2.2.0 用例 | v2.2.2 用例 | 合计 |
|---------|------|-------------|-------------|------|
| 项目初始化 | init | 5 | 0 | 5 |
| 状态与切换 | status, switch, todo | 8 | 0 | 8 |
| 阶段与签署 | advance, signoff | 12 | 0 | 12 |
| 评审流程 | review | 10 | 0 | 10 |
| 版本控制 | sync, push, remote | 8 | 0 | 8 |
| 文档管理 | docs | 5 | 0 | 5 |
| 合规检查 | compliance, git | 0 | 14 | 14 |
| 角色边界 | requirements, design | 0 | 5 | 5 |
| Agent 守护 | agent, project | 0 | 0 | 0 |
| 工作流 | workflow, work | 0 | 0 | 0 |

---

## 三、功能-测试覆盖矩阵

### 3.1 P0 核心功能 (必须覆盖)

| # | 命令 | 子命令 | v2.2.0 用例 | v2.2.2 用例 | 覆盖状态 |
|---|------|--------|-------------|-------------|----------|
| 1 | init | - | TC-001 | - | ✅ 有 |
| 2 | status | - | TC-002 | - | ✅ 有 |
| 3 | switch | - | TC-003 | - | ✅ 有 |
| 4 | todo | - | - | - | ❌ 无 |
| 5 | advance | - | TC-004 | TC-GIT-001 | ✅ 有 |
| 6 | signoff | - | TC-005 | - | ✅ 有 |
| 7 | review | start | TC-006 | TC-PROC-005 | ✅ 有 |
| 8 | requirements | edit | - | TC-PROC-003 | ⚠️ 待验证 |
| 9 | design | create | - | TC-PROC-001 | ⚠️ 待验证 |
| 10 | compliance | check | - | TC-PROC-009 | ✅ 有 |
| 11 | compliance | status | - | TC-PROC-009 | ✅ 有 |
| 12 | compliance | results | - | TC-PROC-009 | ✅ 有 |
| 13 | git | sync | - | TC-GIT-004 | ✅ 有 |
| 14 | git | status | - | TC-GIT-005 | ✅ 有 |
| 15 | sync | - | TC-006 | - | ✅ 有 |
| 16 | push | - | TC-007 | - | ✅ 有 |

### 3.2 P1 重要功能 (建议覆盖)

| # | 命令 | v2.2.0 用例 | v2.2.2 用例 | 覆盖状态 |
|---|------|-------------|-------------|----------|
| 1 | signoffs | - | - | ❌ 无 |
| 2 | remote | TC-008 | - | ✅ 有 |
| 3 | docs | TC-009 | - | ✅ 有 |
| 4 | sync-all | TC-010 | - | ✅ 有 |

### 3.3 P2 辅助功能 (可选覆盖)

| # | 命令 | v2.2.0 用例 | v2.2.2 用例 | 覆盖状态 |
|---|------|-------------|-------------|----------|
| 1 | history | - | - | ❌ 无 |
| 2 | agent | - | - | ❌ 无 |
| 3 | project | - | - | ❌ 无 |
| 4 | workflow | - | - | ❌ 无 |
| 5 | work | - | - | ❌ 无 |

---

## 四、缺失测试用例清单

### 4.1 P0 缺失用例 (必须补充)

| # | 命令 | 测试场景 | 优先级 |
|---|------|----------|--------|
| 1 | todo | 查看待办列表 | P0 |
| 2 | requirements | Agent2 无法编辑需求 | P0 |
| 3 | design | Agent1 无法创建设计 | P0 |
| 4 | design | Agent1 无法编辑设计 | P0 |
| 5 | review | Agent2 无法评审已评审文档 | P0 |

### 4.2 P1 缺失用例 (建议补充)

| # | 命令 | 测试场景 | 优先级 |
|---|------|----------|--------|
| 1 | signoffs | 查看签署记录 | P1 |
| 2 | history | 查看协作历史 | P1 |
| 3 | project | 项目管理命令 | P1 |

### 4.3 P2 缺失用例 (可选补充)

| # | 命令 | 测试场景 | 优先级 |
|---|------|----------|--------|
| 1 | agent | Agent 守护进程 | P2 |
| 2 | workflow | 工作流状态 | P2 |
| 3 | work | 智能工作流引导 | P2 |

---

## 五、测试覆盖总结

### 5.1 按优先级统计

| 优先级 | 命令数 | 有测试 | 缺失测试 | 覆盖率 |
|--------|--------|--------|----------|--------|
| P0 | 16 | 11 | 5 | 69% |
| P1 | 4 | 3 | 1 | 75% |
| P2 | 5 | 0 | 5 | 0% |
| **总计** | **25** | **14** | **11** | **56%** |

### 5.2 结论

| 指标 | 值 |
|------|-----|
| 总命令数 | 22 |
| P0 命令数 | 16 |
| P0 覆盖率 | 69% |
| 总体覆盖率 | 56% |

**需要优先补充 P0 缺失用例**:

1. `oc-collab todo` - 待办事项查看
2. `oc-collab requirements edit` - Agent2 权限检查
3. `oc-collab design create/edit` - Agent1 权限检查
4. `oc-collab review` - 重复评审检查

---

## 六、Action Items

| ID | 行动 | 负责人 | 优先级 | 状态 |
|----|------|--------|--------|------|
| ACT-001 | 补充 `oc-collab todo` 黑盒测试用例 | Agent1 | P0 | pending |
| ACT-002 | 补充 Agent2 权限边界测试用例 | Agent1 | P0 | pending |
| ACT-003 | 补充 Agent1 权限边界测试用例 | Agent1 | P0 | pending |
| ACT-004 | 补充 `oc-collab signoffs` 测试用例 | Agent1 | P1 | pending |
| ACT-005 | 执行所有黑盒测试用例 | Agent1 | P0 | pending |

---

**文档版本**: v1
**创建日期**: 2026-02-08
**状态**: DRAFT

