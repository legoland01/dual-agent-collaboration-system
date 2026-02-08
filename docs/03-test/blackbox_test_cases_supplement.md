# oc-collab 黑盒测试用例补充 (P0 缺失)

**文档ID**: DOC-TEST-SUPPL-001
**日期**: 2026-02-08
**作者**: Agent 1 (产品经理)
**状态**: DRAFT

---

## Part A: 角色边界测试补充

### TC-PROC-010: Agent1 无法编辑设计文档

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-PROC-010 |
| 用例名称 | Agent1 无法编辑设计文档 |
| 优先级 | P0 |
| 前置条件 | Agent1 身份，已初始化项目 |
| 测试步骤 | 1. 执行 `oc-collab design edit docs/02-design/test.md`<br>2. 观察结果 |
| 预期结果 | 显示权限拒绝错误消息，命令失败 |
| 对应需求 | F-PROC-001.1 |

### TC-PROC-011: Agent2 无法签署自己创建的评审

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-PROC-011 |
| 用例名称 | Agent2 无法签署自己创建的评审 |
| 优先级 | P0 |
| 前置条件 | Agent2 身份，文档为 REVIEW_PENDING 状态 |
| 测试步骤 | 1. 执行 `oc-collab signoff review docs/02-design/test_REVIEW.md`<br>2. 观察结果 |
| 预期结果 | 显示权限拒绝错误消息（利益冲突） |
| 对应需求 | F-PROC-001.1 |

### TC-PROC-012: Agent1 无法编辑已归档文档

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-PROC-012 |
| 用例名称 | Agent1 无法编辑已归档文档 |
| 优先级 | P0 |
| 前置条件 | Agent1 身份，文档状态为 ARCHIVED |
| 测试步骤 | 1. 执行 `oc-collab requirements edit requirements_v1.0.0.md`<br>2. 观察结果 |
| 预期结果 | 显示状态错误，无法编辑 |
| 对应需求 | F-PROC-001.2 |

### TC-PROC-013: Agent2 无法编辑已归档文档

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-PROC-013 |
| 用例名称 | Agent2 无法编辑已归档文档 |
| 优先级 | P0 |
| 前置条件 | Agent2 身份，文档状态为 ARCHIVED |
| 测试步骤 | 1. 执行 `oc-collab design edit docs/02-design/v1.0.0.md`<br>2. 观察结果 |
| 预期结果 | 显示状态错误，无法编辑 |
| 对应需求 | F-PROC-001.2 |

---

## Part B: Todo 命令测试

### TC-TODO-001: 查看待办列表

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-TODO-001 |
| 用例名称 | 查看待办事项列表 |
| 优先级 | P0 |
| 前置条件 | 项目已初始化，有待办任务 |
| 测试步骤 | 1. 执行 `oc-collab todo`<br>2. 观察输出 |
| 预期结果 | 显示待办列表，包含任务编号、描述、优先级 |
| 对应需求 | v1.0 核心功能 |

### TC-TODO-002: 待办任务筛选

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-TODO-002 |
| 用例名称 | 筛选指定 Agent 的待办 |
| 优先级 | P0 |
| 前置条件 | 项目已初始化，有待办任务 |
| 测试步骤 | 1. 执行 `oc-collab todo --agent agent2`<br>2. 观察输出 |
| 预期结果 | 只显示分配给 agent2 的任务 |
| 对应需求 | v1.0 核心功能 |

---

## Part C: Signoffs 命令测试

### TC-SIGNOFFS-001: 查看签署记录

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-SIGNOFFS-001 |
| 用例名称 | 查看签署记录列表 |
| 优先级 | P1 |
| 前置条件 | 项目已初始化，有签署记录 |
| 测试步骤 | 1. 执行 `oc-collab signoffs`<br>2. 观察输出 |
| 预期结果 | 显示所有签署记录 |
| 对应需求 | v1.0 核心功能 |

### TC-SIGNOFFS-002: 筛选签署记录

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-SIGNOFFS-002 |
| 用例名称 | 按阶段筛选签署记录 |
| 优先级 | P1 |
| 前置条件 | 项目已初始化，有多阶段签署记录 |
| 测试步骤 | 1. 执行 `oc-collab signoffs --phase requirements`<br>2. 观察输出 |
| 预期结果 | 只显示 requirements 阶段的签署记录 |
| 对应需求 | v1.0 核心功能 |

---

## Part D: 文档管理测试

### TC-DOCS-001: 自动同步文档

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-DOCS-001 |
| 用例名称 | 自动同步文档到 Git |
| 优先级 | P1 |
| 前置条件 | 项目已初始化，Git 已配置 |
| 测试步骤 | 1. 修改 docs/ 目录下的文档<br>2. 执行 `oc-collab docs sync`<br>3. 检查 Git 状态 |
| 预期结果 | 自动执行 git add → commit |
| 对应需求 | v1.0 核心功能 |

---

## Part E: 远程仓库测试

### TC-REMOTE-001: 查看远程仓库

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-REMOTE-001 |
| 用例名称 | 查看配置的远程仓库 |
| 优先级 | P1 |
| 前置条件 | 项目已初始化，远程已配置 |
| 测试步骤 | 1. 执行 `oc-collab remote list`<br>2. 观察输出 |
| 预期结果 | 显示所有配置的远程仓库 |
| 对应需求 | v1.0 核心功能 |

### TC-REMOTE-002: 添加远程仓库

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-REMOTE-002 |
| 用例名称 | 添加 GitHub 远程仓库 |
| 优先级 | P1 |
| 前置条件 | 项目已初始化 |
| 测试步骤 | 1. 执行 `oc-collab remote add github https://github.com/user/repo.git`<br>2. 观察结果 |
| 预期结果 | 远程仓库添加成功 |
| 对应需求 | v1.0 核心功能 |

---

## Part F: 工作流测试

### TC-WORKFLOW-001: 查看工作流状态

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-WORKFLOW-001 |
| 用例名称 | 查看当前工作流状态 |
| 优先级 | P2 |
| 前置条件 | 项目已初始化 |
| 测试步骤 | 1. 执行 `oc-collab workflow`<br>2. 观察输出 |
| 预期结果 | 显示当前工作流状态和进度 |
| 对应需求 | v1.0 核心功能 |

### TC-WORK-001: 智能工作流引导

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-WORK-001 |
| 用例名称 | 获取下一步工作建议 |
| 优先级 | P2 |
| 前置条件 | 项目已初始化 |
| 测试步骤 | 1. 执行 `oc-collab work`<br>2. 观察输出 |
| 预期结果 | 显示当前阶段的下一步建议 |
| 对值需求 | v1.0 核心功能 |

---

## 测试命令速查

```bash
# 运行所有 P0 缺失测试用例
pytest tests/ -k "TC-PROC-010 or TC-PROC-011 or TC-PROC-012 or TC-TODO-001" -v

# 运行 P1 补充测试用例
pytest tests/ -k "TC-SIGNOFFS or TC-DOCS-001 or TC-REMOTE" -v

# 运行 P2 补充测试用例
pytest tests/ -k "TC-WORKFLOW or TC-WORK" -v
```

---

## Action Items

| ID | 行动 | 负责人 | 优先级 | 状态 |
|----|------|--------|--------|------|
| ACT-001 | 实现 P0 缺失测试用例 | Agent1 | P0 | pending |
| ACT-002 | 执行补充测试用例 | Agent1 | P0 | pending |
| ACT-003 | 修复失败的测试用例 | Agent2 | P0 | pending |

---

**文档版本**: v1
**创建日期**: 2026-02-08
**状态**: DRAFT

